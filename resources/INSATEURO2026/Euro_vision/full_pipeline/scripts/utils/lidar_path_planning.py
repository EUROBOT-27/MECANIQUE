#!/usr/bin/env python3
"""
LiDAR-Based Path Planning - Eurobot 2026 (Vision + LiDAR Fusion)

This script integrates:
- ArUco marker detection for robot localization (our robot ID 36)
- Camera intrinsics and extrinsics calibration
- LiDAR-based enemy detection (more accurate than vision)
- RRT-Connect path planning with LiDAR obstacles
- Real-time visualization

Key Difference from main_connect.py:
- Enemy detection: LiDAR data instead of ArUco vision
- Enemy position: Placeholder coordinates (waiting for ROS/DDS subscriber)
- More accurate obstacle avoidance with LiDAR precision

Reference markers (IDs 20-23, 10cm):
- M22: (0.600, 0.600, 0.0)m
- M20: (0.600, 1.400, 0.0)m
- M21: (2.400, 1.400, 0.0)m
- M23: (2.400, 0.600, 0.0)m

Usage:
    python lidar_path_planning.py --camera 1
"""

import cv2
import numpy as np
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import time

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "kalman_filter" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kalman_filter.src.kalman_filter.tracker import MultiMarkerTracker, MarkerType, MarkerState
from kalman_filter.src.occlusion_handler.handler import OcclusionHandler, DetectionQuality
from path_planning.rrt_connect import rrt_connect_plan

# ============================================================================
# CONFIGURATION
# ============================================================================

REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}
REFERENCE_MARKER_SIZE = 0.10  # 10cm for reference markers (20-23)
ALLY_MARKER_SIZE = 0.05       # 5cm for ally robot marker (ID 36)
ARUCO_DICT = cv2.aruco.DICT_4X4_50
ALLY_ROBOT_ID = 36  # Our robot (tracked via ArUco)
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"

# ============================================================================
# LIDAR-BASED PATH PLANNER
# ============================================================================

class LidarPathPlanner:
    """
    Path planning system that uses:
    - Vision (ArUco) for ally robot localization
    - LiDAR for enemy detection (more accurate than vision)
    - RRT-Connect for path planning
    """
    
    def __init__(self, camera_id: int = 1, intrinsics_file: str = DEFAULT_INTRINSICS,
                 extrinsics_file: str = DEFAULT_EXTRINSICS):
        self.camera_id = camera_id
        self.intrinsics_file = intrinsics_file
        self.extrinsics_file = extrinsics_file
        
        # Load camera intrinsics
        self.load_intrinsics(intrinsics_file)
        
        # Setup ArUco detector (for ally robot + reference markers only)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # Camera extrinsics
        self.rvec_cam = None
        self.tvec_cam = None
        self.extrinsics_valid = False
        if Path(extrinsics_file).exists():
            self.load_extrinsics(extrinsics_file)
        
        # LiDAR enemy data (PLACEHOLDER - will come from ROS/DDS subscriber)
        self.enemy_position_lidar = np.array([1.5, 1.0, 0.0])  # PLACEHOLDER: (x, y, z) in world frame
        self.enemy_radius = 0.22  # Enemy robot radius (meters)
        self.lidar_data_valid = True  # PLACEHOLDER: Set to True when LiDAR data available
        
        # Robot parameters
        self.robot_radius = 0.22
        self.obstacle_radius_default = 0.12
        
        # Path planning state
        self._last_planned_path = None
        self._last_plan_time = 0.0
        self._plan_interval = 0.5  # Replan every 0.5 seconds
        self._last_coord_print_time = 0.0
        self.all_candidate_paths = []
        
        # Performance tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
    
    # ========================================================================
    # LiDAR DATA HANDLING (PLACEHOLDER FOR FUTURE ROS/DDS INTEGRATION)
    # ========================================================================
    
    def update_enemy_position_from_lidar(self, x: float, y: float, z: float = 0.0):
        """
        Update enemy position from LiDAR data.
        
        This method will be called by the ROS/DDS subscriber when LiDAR data arrives.
        
        Args:
            x, y, z: Enemy position in world frame (meters)
        """
        self.enemy_position_lidar = np.array([x, y, z])
        self.lidar_data_valid = True
    
    def get_enemy_obstacle(self) -> Optional[Tuple[np.ndarray, float]]:
        """
        Get enemy obstacle from LiDAR data.
        
        Returns:
            (position, radius) tuple or None if no valid LiDAR data
        """
        if not self.lidar_data_valid:
            return None
        return (self.enemy_position_lidar, self.enemy_radius)
    
    # ========================================================================
    # CAMERA CALIBRATION & COORDINATE TRANSFORMS
    # ========================================================================
    
    def load_intrinsics(self, intrinsics_file):
        """Load camera intrinsics from JSON file."""
        try:
            with open(intrinsics_file, 'r') as f:
                data = json.load(f)
            self.camera_matrix = np.array(data['camera_matrix'])
            self.dist_coeffs = np.array(data['distortion_coefficients'])
            print(f"✓ Loaded camera intrinsics from {intrinsics_file}")
        except Exception as e:
            print(f"✗ Failed to load intrinsics: {e}")
            self.camera_matrix = None
            self.dist_coeffs = None
    
    def load_extrinsics(self, extrinsics_file):
        """Load camera extrinsics from JSON file."""
        try:
            with open(extrinsics_file, 'r') as f:
                data = json.load(f)
            self.rvec_cam = np.array(data['rvec'])
            self.tvec_cam = np.array(data['tvec'])
            self.extrinsics_valid = True
            print(f"✓ Loaded camera extrinsics from {extrinsics_file}")
        except Exception as e:
            print(f"✗ Failed to load extrinsics: {e}")
            self.rvec_cam = None
            self.tvec_cam = None
            self.extrinsics_valid = False
    
    def compute_camera_extrinsics(self, corners_dict, ids_detected):
        """Compute camera extrinsics using solvePnP with reference markers."""
        object_points = []
        image_points = []
        
        for marker_id in ids_detected:
            if marker_id not in REFERENCE_MARKERS:
                continue
            
            marker_center = REFERENCE_MARKERS[marker_id]
            half_size = REFERENCE_MARKER_SIZE / 2
            
            corners_3d = np.array([
                [marker_center[0] - half_size, marker_center[1] - half_size, 0],
                [marker_center[0] + half_size, marker_center[1] - half_size, 0],
                [marker_center[0] + half_size, marker_center[1] + half_size, 0],
                [marker_center[0] - half_size, marker_center[1] + half_size, 0],
            ], dtype=np.float32)
            
            corners_2d = corners_dict[marker_id].reshape(-1, 2)
            object_points.extend(corners_3d)
            image_points.extend(corners_2d)
        
        if len(object_points) < 4:
            return False
        
        object_points = np.array(object_points, dtype=np.float32)
        image_points = np.array(image_points, dtype=np.float32)
        
        success, rvec, tvec = cv2.solvePnP(
            object_points, image_points, self.camera_matrix, self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if success:
            self.rvec_cam = rvec
            self.tvec_cam = tvec
            self.extrinsics_valid = True
            
            R_cam, _ = cv2.Rodrigues(rvec)
            cam_pos_world = -R_cam.T @ tvec
            print(f"\n✓ Camera extrinsics computed!")
            print(f"  Camera position: ({cam_pos_world[0,0]:.3f}, {cam_pos_world[1,0]:.3f}, {cam_pos_world[2,0]:.3f})m")
            
            self.save_extrinsics()
            return True
        
        return False
    
    def save_extrinsics(self):
        """Save computed extrinsics to JSON file."""
        if not self.extrinsics_valid:
            return
        
        R_cam, _ = cv2.Rodrigues(self.rvec_cam)
        cam_pos_world = -R_cam.T @ self.tvec_cam
        
        extrinsics_data = {
            "rvec": self.rvec_cam.tolist(),
            "tvec": self.tvec_cam.tolist(),
            "rotation_matrix": R_cam.tolist(),
            "camera_position_world": {
                "x": float(cam_pos_world[0,0]),
                "y": float(cam_pos_world[1,0]),
                "z": float(cam_pos_world[2,0])
            },
            "reference_markers": {int(k): v.tolist() for k, v in REFERENCE_MARKERS.items()},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        extrinsics_path = Path(self.extrinsics_file)
        extrinsics_path.parent.mkdir(parents=True, exist_ok=True)
        with open(extrinsics_path, 'w') as f:
            json.dump(extrinsics_data, f, indent=2)
        print(f"✓ Saved extrinsics to {extrinsics_path}")
    
    def transform_to_world(self, rvec_obj: np.ndarray, tvec_obj: np.ndarray):
        """Transform object pose from camera to world coordinates."""
        if not self.extrinsics_valid:
            return None, None
        
        R_cam, _ = cv2.Rodrigues(self.rvec_cam)
        R_obj, _ = cv2.Rodrigues(rvec_obj)
        
        P_camera = tvec_obj[0].reshape(3, 1)
        R_cam_inv = R_cam.T
        P_world = R_cam_inv @ (P_camera - self.tvec_cam)
        
        R_obj_world = R_cam_inv @ R_obj
        rvec_world, _ = cv2.Rodrigues(R_obj_world)
        
        return rvec_world, P_world
    
    # ========================================================================
    # PATH PLANNING & VISUALIZATION
    # ========================================================================
    
    def _compute_path_cost(self, path):
        """Compute total Euclidean length of path."""
        if not path or len(path) < 2:
            return float('inf')
        cost = 0.0
        for i in range(len(path) - 1):
            cost += np.linalg.norm(np.array(path[i][:2]) - np.array(path[i+1][:2]))
        return cost
    
    def _sampled_circle_intersects_obstacle(self, path, obstacle, robot_radius, num_samples=50):
        """Check if path intersects with obstacle using sampled robot footprints."""
        if not path or obstacle is None:
            return False
        
        center_obs, radius_obs = obstacle
        center_obs = np.array(center_obs)
        
        sampled_points = []
        for i in range(len(path) - 1):
            p0 = np.array(path[i])
            p1 = np.array(path[i + 1])
            for t in np.linspace(0, 1, num_samples // max(1, (len(path) - 1))):
                pt = p0 * (1 - t) + p1 * t
                sampled_points.append(pt)
        
        for pt in sampled_points:
            pt_xy = np.array(pt[:2])
            dist = np.linalg.norm(pt_xy - center_obs[:2])
            if dist <= (robot_radius + float(radius_obs)):
                return True
        
        return False
    
    def _project_world_to_image(self, world_points):
        """Project 3D world points to 2D image coordinates."""
        if not self.extrinsics_valid:
            return []
        
        pts = np.array(world_points, dtype=np.float32).reshape(-1, 3)
        imgpts, _ = cv2.projectPoints(pts, self.rvec_cam, self.tvec_cam, 
                                     self.camera_matrix, self.dist_coeffs)
        imgpts = imgpts.reshape(-1, 2)
        return [(int(p[0]), int(p[1])) for p in imgpts]
    
    def draw_rrt_path_and_obstacles(self, display_frame, path, obstacles, robot_radius=None):
        """Draw RRT path and obstacles on the display frame."""
        if not self.extrinsics_valid:
            return
        
        # Draw obstacles
        for center, radius in obstacles:
            center_2d = self._project_world_to_image([center])
            if not center_2d:
                continue
            
            edge_point_3d = center + np.array([radius, 0, 0])
            edge_point_2d = self._project_world_to_image([edge_point_3d])
            if not edge_point_2d:
                continue
            
            pixel_radius = int(np.linalg.norm(np.array(center_2d[0]) - np.array(edge_point_2d[0])))
            
            # Draw LiDAR enemy in RED (different from vision-based)
            cv2.circle(display_frame, center_2d[0], pixel_radius, (0, 0, 255), 3)
            
            # Label: LiDAR ENEMY
            label = f"LiDAR ENEMY ({center[0]:.2f}, {center[1]:.2f})"
            cv2.putText(display_frame, label, (center_2d[0][0] - 50, center_2d[0][1] - pixel_radius - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Draw path
        if path and len(path) > 1:
            path_pixels = self._project_world_to_image(path)
            if path_pixels:
                path_pts = np.array(path_pixels, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(display_frame, [path_pts], isClosed=False, color=(0, 255, 255), thickness=2)
                
                # Draw robot footprint circles along path
                if robot_radius:
                    num_samples = max(10, len(path) * 5)
                    sampled_points = []
                    for i in range(len(path) - 1):
                        p0 = np.array(path[i])
                        p1 = np.array(path[i + 1])
                        for t in np.linspace(0, 1, num_samples // (len(path) - 1)):
                            pt_world = p0 * (1 - t) + p1 * t
                            sampled_points.append(pt_world)
                    
                    sampled_pixels = self._project_world_to_image(sampled_points)
                    for pt_world, pt_pixel in zip(sampled_points, sampled_pixels):
                        try:
                            p = tuple(pt_pixel)
                            wx = float(pt_world[0])
                            wy = float(pt_world[1])
                            edge_pt_world = np.array([wx + robot_radius, wy, 0.0])
                            edge_px = self._project_world_to_image([edge_pt_world])
                            if edge_px:
                                pixel_r = int(np.linalg.norm(np.array(p) - np.array(edge_px[0])))
                                cv2.circle(display_frame, p, pixel_r, (0, 165, 255), 1)
                        except Exception:
                            continue
                
                # Draw waypoint coordinates
                for wp_world, pt in zip(path, path_pixels):
                    try:
                        p = tuple(pt)
                        cv2.circle(display_frame, p, 5, (0, 165, 255), -1)
                        wx, wy = float(wp_world[0]), float(wp_world[1])
                        coord_text = f"({wx:.3f},{wy:.3f})"
                        cv2.putText(display_frame, coord_text, (p[0] + 6, p[1] - 6),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (230, 230, 230), 1)
                    except Exception:
                        continue
    
    # ========================================================================
    # FRAME PROCESSING
    # ========================================================================
    
    def process_frame(self, frame: np.ndarray):
        """
        Process a single frame:
        - Detect ArUco markers for ally robot (ID 36) and references (20-23)
        - Use LiDAR data for enemy detection
        - Update extrinsics if needed
        """
        # Detect ArUco markers
        corners, ids, rejected = self.detector.detectMarkers(frame)
        
        display = frame.copy()
        detections = {}
        
        if ids is not None:
            ids = ids.flatten()
            
            # Estimate pose for each marker
            rvecs = []
            tvecs = []
            for i, marker_id in enumerate(ids):
                if marker_id in REFERENCE_MARKERS:
                    marker_size = REFERENCE_MARKER_SIZE
                elif marker_id == ALLY_ROBOT_ID:
                    marker_size = ALLY_MARKER_SIZE
                else:
                    continue  # Skip unknown markers
                
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [corners[i]], marker_size, self.camera_matrix, self.dist_coeffs
                )
                rvecs.append(rvec[0])
                tvecs.append(tvec[0])
            
            rvecs = np.array(rvecs) if rvecs else np.array([])
            tvecs = np.array(tvecs) if tvecs else np.array([])
            
            # Compute extrinsics if needed
            ref_markers = [mid for mid in ids if mid in REFERENCE_MARKERS]
            if len(ref_markers) >= 4 and not self.extrinsics_valid:
                corners_dict = {ids[i]: corners[i] for i in range(len(ids))}
                self.compute_camera_extrinsics(corners_dict, ids)
            
            # Draw detected markers
            cv2.aruco.drawDetectedMarkers(display, corners, ids)
            
            # Process each detected marker
            for i, marker_id in enumerate(ids):
                if marker_id in REFERENCE_MARKERS:
                    # Reference marker
                    color = (0, 255, 0)
                    label = f"REF {marker_id}"
                    detections[marker_id] = {
                        'type': 'reference',
                        'world_pos': REFERENCE_MARKERS[marker_id]
                    }
                elif marker_id == ALLY_ROBOT_ID:
                    # Ally robot - transform to world coordinates
                    if self.extrinsics_valid and i < len(rvecs):
                        rvec_world, tvec_world = self.transform_to_world(rvecs[i], tvecs[i])
                        if tvec_world is not None:
                            world_pos = tvec_world.flatten()
                            detections[marker_id] = {
                                'type': 'ally',
                                'world_pos': world_pos,
                            }
                            color = (255, 0, 255)
                            x, y, z = world_pos
                            label = f"ALLY {marker_id} | ({x:.3f}, {y:.3f}, {z:.3f})m"
                    else:
                        color = (128, 128, 128)
                        label = f"ALLY {marker_id} (no extrinsics)"
                else:
                    continue
                
                # Draw label
                corner = corners[i][0][0]
                cv2.putText(display, label, (int(corner[0]), int(corner[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Update FPS
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            current_time = time.time()
            elapsed = current_time - self.last_fps_time
            self.fps = 30.0 / elapsed if elapsed > 0 else 30.0
            self.last_fps_time = current_time
        
        # Draw status
        status_y = 30
        ref_count = len([mid for mid in ids if mid in REFERENCE_MARKERS]) if ids is not None else 0
        if self.extrinsics_valid:
            status = f"TRACKING | Refs: {ref_count}/4 | FPS: {self.fps:.1f} | LiDAR: {'ON' if self.lidar_data_valid else 'OFF'}"
            status_color = (0, 255, 0)
        else:
            status = f"CALIBRATING | Refs: {ref_count}/4 (need 4)"
            status_color = (0, 165, 255)
        
        cv2.putText(display, status, (10, status_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Draw LiDAR status
        if self.lidar_data_valid:
            lidar_text = f"LiDAR Enemy: ({self.enemy_position_lidar[0]:.2f}, {self.enemy_position_lidar[1]:.2f}) [PLACEHOLDER]"
            cv2.putText(display, lidar_text, (10, status_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return display, detections
    
    # ========================================================================
    # MAIN LOOP
    # ========================================================================
    
    def run(self):
        """Main execution loop."""
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print(f"✗ Cannot open camera {self.camera_id}")
            return
        
        print(f"\n✓ Camera opened (ID: {self.camera_id})")
        print(f"✓ LiDAR enemy detection: ENABLED (placeholder mode)")
        print("\nControls:")
        print("  ESC - Quit")
        print("  SPACE - Reset extrinsics")
        print("\nWaiting for reference markers (20-23) and ally robot (36)...\n")
        print("\n⚠️  PLACEHOLDER MODE: Enemy position hardcoded to (1.5, 1.0)")
        print("    TODO: Integrate ROS/DDS subscriber for real LiDAR data\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            display, detections = self.process_frame(frame)
            now = time.time()
            
            # === PATH PLANNING ===
            if self.extrinsics_valid and now - self._last_plan_time > self._plan_interval:
                # Get ally robot position
                start_pos = None
                if ALLY_ROBOT_ID in detections and 'world_pos' in detections[ALLY_ROBOT_ID]:
                    start_pos = np.array(detections[ALLY_ROBOT_ID]['world_pos'])
                
                # Goal: Reference marker 23
                goal_pos = REFERENCE_MARKERS.get(23)
                
                if start_pos is not None and goal_pos is not None:
                    # Build obstacles list (enemy from LiDAR)
                    obstacles = []
                    enemy_obstacle = self.get_enemy_obstacle()
                    if enemy_obstacle:
                        obstacles.append(enemy_obstacle)
                    
                    # Check if current path is blocked
                    is_blocked = False
                    if self._last_planned_path and enemy_obstacle:
                        is_blocked = self._sampled_circle_intersects_obstacle(
                            self._last_planned_path, enemy_obstacle, self.robot_radius
                        )
                    
                    # Replan if no path or blocked
                    if self._last_planned_path is None or is_blocked:
                        if is_blocked:
                            print("! Path blocked by LiDAR enemy. Replanning...")
                        
                        bounds = (0.0, 3.0, 0.0, 2.0)
                        inflated_obstacles = [(c, r + self.robot_radius) for (c, r) in obstacles]
                        
                        # Generate multiple candidate paths
                        candidate_paths = []
                        for seed in range(5):
                            np.random.seed(int(time.time() * 1000) % 2**32 + seed)
                            path = rrt_connect_plan(start_pos, goal_pos, inflated_obstacles, bounds)
                            if path:
                                candidate_paths.append(path)
                        
                        # Store all candidate paths
                        self.all_candidate_paths.extend(candidate_paths)
                        
                        # Select shortest path
                        best_path = None
                        best_cost = float('inf')
                        for cand_path in candidate_paths:
                            cost = self._compute_path_cost(cand_path)
                            if cost < best_cost:
                                best_cost = cost
                                best_path = cand_path
                        
                        self._last_planned_path = best_path
                        
                        if self._last_planned_path:
                            print(f"✓ Path found with {len(self._last_planned_path)} waypoints. Cost: {best_cost:.3f}")
                        else:
                            print("✗ RRT-Connect planner failed to find a path.")
                    
                    self._last_plan_time = now
            
            # Print waypoints periodically
            if now - self._last_coord_print_time > 0.2:
                if self._last_planned_path:
                    waypoints = [(float(pt[0]), float(pt[1])) for pt in self._last_planned_path]
                    print("WAYPOINTS:", waypoints)
                self._last_coord_print_time = now
            
            # Prepare obstacles for visualization
            obstacles_to_draw = []
            enemy_obstacle = self.get_enemy_obstacle()
            if enemy_obstacle:
                obstacles_to_draw.append(enemy_obstacle)
            
            # Draw all candidate paths in black
            if self.all_candidate_paths:
                for cand_path in self.all_candidate_paths:
                    path_pixels = self._project_world_to_image(cand_path)
                    if path_pixels:
                        path_pts = np.array(path_pixels, dtype=np.int32).reshape((-1, 1, 2))
                        cv2.polylines(display, [path_pts], isClosed=False, color=(0, 0, 0), thickness=1)
            
            # Draw best path in yellow/orange
            if self._last_planned_path:
                self.draw_rrt_path_and_obstacles(display, self._last_planned_path, 
                                                 obstacles_to_draw, robot_radius=self.robot_radius)
            
            # Waypoint selection for robot control
            if self._last_planned_path and ALLY_ROBOT_ID in detections and 'world_pos' in detections[ALLY_ROBOT_ID]:
                robot_pos = np.array(detections[ALLY_ROBOT_ID]['world_pos'][:2])
                
                # Find first waypoint ahead and at reasonable distance
                min_distance = self.robot_radius * 0.8
                next_waypoint = None
                
                for wp in self._last_planned_path:
                    wp_vec = np.array(wp[:2]) - robot_pos
                    distance = np.linalg.norm(wp_vec)
                    if distance < min_distance:
                        continue
                    
                    # Simple forward check (no orientation needed)
                    next_waypoint = wp
                    break
                
                if next_waypoint is not None:
                    print(f"NEXT WAYPOINT: {tuple(float(x) for x in next_waypoint)}")
            
            # Display
            cv2.imshow('LiDAR Path Planning - Eurobot Tracking', display)
            
            # Keyboard controls
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE - reset extrinsics
                self.extrinsics_valid = False
                self.rvec_cam = None
                self.tvec_cam = None
                print("\n! Extrinsics reset - recalibrating...\n")
        
        cap.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description='LiDAR-Based Path Planning - Eurobot Vision + LiDAR Fusion',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--camera', type=int, default=2,
                       help='Camera device ID (default: 2)')
    parser.add_argument('--intrinsics', type=str, default=DEFAULT_INTRINSICS,
                       help='Path to camera intrinsics JSON')
    parser.add_argument('--extrinsics', type=str, default=DEFAULT_EXTRINSICS,
                       help='Path to camera extrinsics JSON')
    
    args = parser.parse_args()
    
    if not Path(args.intrinsics).exists():
        print(f"✗ Intrinsics file not found: {args.intrinsics}")
        print("\nPlease run camera calibration first:")
        print("  cd ../../camera_calibration_folder")
        print("  python calibrate_camera.py --camera 1")
        return 1
    
    try:
        planner = LidarPathPlanner(
            camera_id=args.camera,
            intrinsics_file=args.intrinsics,
            extrinsics_file=args.extrinsics
        )
        planner.run()
    except KeyboardInterrupt:
        print("\n\n✓ Planning stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
