#!/usr/bin/env python3
"""
Full Pipeline - Eurobot 2026 ArUco Tracking System (RRT-Connect)

This script integrates:
- ArUco marker detection and tracking
- Camera intrinsics and extrinsics calibration
- Kalman filtering for enemy robot (ID 13) tracking
- Real-time visualization of all detected markers
- Temporal smoothing for position estimates
- RRT-Connect path planning

Reference markers (IDs 20-23, 10cm):
- M22: (0.600, 0.600, 0.0)m
- M20: (0.600, 1.400, 0.0)m
- M21: (2.400, 1.400, 0.0)m
- M23: (2.400, 0.600, 0.0)m

Usage:
    python main_connect.py --camera 1
"""

import cv2
import numpy as np
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import time
last_print_time = 0
print_interval = 0.2  # seconds

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "kalman_filter" / "src"))
# Ensure repository root on path so sibling packages (e.g., path_planning) can be imported
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kalman_filter.src.kalman_filter.tracker import MultiMarkerTracker, MarkerType, MarkerState
from kalman_filter.src.occlusion_handler.handler import OcclusionHandler, DetectionQuality
from path_planning.rrt_connect import rrt_connect_plan

# ============================================================================
# CONFIGURATION
# ============================================================================

REFERENCE_MARKERS = {
    21: np.array([0.600, 0.600, 0.0]),
    23: np.array([0.600, 1.400, 0.0]),
    22: np.array([2.400, 1.400, 0.0]),
    20: np.array([2.400, 0.600, 0.0]),
}
REFERENCE_MARKER_SIZE = 0.10  # 10cm for reference markers (20-23)
OBJECT_MARKER_SIZE = 0.05     # 5cm for all other markers
ARUCO_DICT = cv2.aruco.DICT_4X4_50
ENEMY_MARKER_ID = 13
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"

# ============================================================================
# FULL PIPELINE TRACKER
# ============================================================================

class FullPipelineTracker:
    def _compute_path_cost(self, path):
        """Compute the cost of a path (total Euclidean length)."""
        if not path or len(path) < 2:
            return float('inf')
        cost = 0.0
        for i in range(len(path) - 1):
            cost += np.linalg.norm(np.array(path[i][:2]) - np.array(path[i+1][:2]))
        return cost
    def _generate_detour_around_enemy(self, start_pos, enemy_pos, enemy_radius, goal_pos):
            """
            Generate waypoints that go around the enemy in a circular arc from start_pos to goal_pos.
            Returns a list of waypoints: [start, tangent1, tangent2, goal]
            """
            # Vector from enemy to start and goal
            start_vec = np.array(start_pos[:2]) - np.array(enemy_pos[:2])
            goal_vec = np.array(goal_pos[:2]) - np.array(enemy_pos[:2])
            # Normalize
            start_dir = start_vec / (np.linalg.norm(start_vec) + 1e-8)
            goal_dir = goal_vec / (np.linalg.norm(goal_vec) + 1e-8)
            # Tangent points (on the circle)
            tangent1 = np.array(enemy_pos[:2]) + start_dir * (enemy_radius + self.robot_radius + 0.05)
            tangent2 = np.array(enemy_pos[:2]) + goal_dir * (enemy_radius + self.robot_radius + 0.05)
            # Add z=0 for 3D compatibility
            tangent1 = np.array([tangent1[0], tangent1[1], 0.0])
            tangent2 = np.array([tangent2[0], tangent2[1], 0.0])
            # Return detour waypoints
            return [start_pos, tangent1, tangent2, goal_pos]
    def _sampled_circle_intersects_obstacle(self, path, obstacle, robot_radius, num_samples=50):
        """
        Check whether any robot-footprint circle placed at sampled points along the path intersects the obstacle circle.
        Returns True if any sampled robot circle intersects the given obstacle.
        """
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
            """
            Project a list of 3D world points to image pixel coordinates using camera extrinsics.
            """
            if not self.extrinsics_valid:
                return []
            pts = np.array(world_points, dtype=np.float32).reshape(-1,3)
            imgpts, _ = cv2.projectPoints(pts, self.rvec_cam, self.tvec_cam, self.camera_matrix, self.dist_coeffs)
            imgpts = imgpts.reshape(-1,2)
            return [(int(p[0]), int(p[1])) for p in imgpts]
    def draw_rrt_path_and_obstacles(self, display_frame, path, obstacles, robot_radius=None):
        """
        Draw the RRT path and obstacles onto the display frame.
        """
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
            cv2.circle(display_frame, center_2d[0], pixel_radius, (255, 100, 0), 2)
        # Draw path
        if path and len(path) > 1:
            path_pixels = self._project_world_to_image(path)
            if path_pixels:
                path_pts = np.array(path_pixels, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(display_frame, [path_pts], isClosed=False, color=(0, 255, 255), thickness=2)
                # Draw orange robot footprint circles at regular intervals along the path
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
                        if robot_radius is not None:
                            edge_pt_world = np.array([wx + robot_radius, wy, 0.0])
                            edge_px = self._project_world_to_image([edge_pt_world])
                            if edge_px:
                                pixel_r = int(np.linalg.norm(np.array(p) - np.array(edge_px[0])))
                                cv2.circle(display_frame, p, pixel_r, (0, 165, 255), 1)
                    except Exception:
                        continue
                # Draw original waypoints as small orange dots and coordinates
                for wp_world, pt in zip(path, path_pixels):
                    try:
                        p = tuple(pt)
                        cv2.circle(display_frame, p, 5, (0, 165, 255), -1)
                        wx = float(wp_world[0])
                        wy = float(wp_world[1])
                        coord_text = f"({wx:.3f},{wy:.3f})"
                        cv2.putText(display_frame, coord_text, (p[0] + 6, p[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (230, 230, 230), 1)
                    except Exception:
                        continue
    def extract_orientation_angle(self, rvec: np.ndarray):
            """
            #this function is still not used to the fullest because the current camera setup and calibration
            is not suitable to extract correct angles and orientation from objects 
            Extract yaw angle (rotation around Z axis) from rotation vector.
            Args:
                rvec: Rotation vector
            Returns:
                Yaw angle in radians
            """
            R, _ = cv2.Rodrigues(rvec)
            # Extract yaw from rotation matrix (assuming ZYX Euler angles)
            yaw = np.arctan2(R[1, 0], R[0, 0])
            return yaw
    def transform_to_world(self, rvec_obj: np.ndarray, tvec_obj: np.ndarray):
            """
            Transform object pose from camera coordinates to world coordinates.
            Args:
                rvec_obj: Object rotation vector in camera frame
                tvec_obj: Object translation vector in camera frame
            Returns:
                (rvec_world, tvec_world) or (None, None) if extrinsics invalid
            """
            if not self.extrinsics_valid:
                return None, None
            R_cam, _ = cv2.Rodrigues(self.rvec_cam)
            R_obj, _ = cv2.Rodrigues(rvec_obj)
            # Transform position: P_world = R_cam^T @ (P_camera - t_cam)
            P_camera = tvec_obj[0].reshape(3, 1)
            R_cam_inv = R_cam.T
            P_world = R_cam_inv @ (P_camera - self.tvec_cam)
            # Transform rotation
            R_obj_world = R_cam_inv @ R_obj
            rvec_world, _ = cv2.Rodrigues(R_obj_world)
            return rvec_world, P_world
    def __init__(self, camera_id: int = 1, intrinsics_file: str = DEFAULT_INTRINSICS,
                 extrinsics_file: str = DEFAULT_EXTRINSICS,
                 enable_kalman: bool = True):
        self.camera_id = camera_id
        self.intrinsics_file = intrinsics_file
        self.extrinsics_file = extrinsics_file
        self.enable_kalman = enable_kalman
        # Load camera intrinsics
        self.load_intrinsics(intrinsics_file)
        # Setup ArUco detector
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        # Camera extrinsics
        self.rvec_cam = None
        self.tvec_cam = None
        self.extrinsics_valid = False
        if Path(extrinsics_file).exists():
            self.load_extrinsics(extrinsics_file)
        # Kalman filter for enemy tracking
        if enable_kalman:
            self.kalman_tracker = MultiMarkerTracker(
                process_noise=0.01,
                measurement_noise=0.1,
                max_frames_without_detection=30
            )
            self.occlusion_handler = OcclusionHandler(
                history_length=30,
                partial_detection_threshold=0.5,
                occlusion_timeout=1.0
            )
        else:
            self.kalman_tracker = None
            self.occlusion_handler = None
        self.position_history = {}
        self.history_size = 5
        self.obstacle_radius_default = 0.12
        self.enemy_obstacle_radius = 0.22
        self.robot_radius = 0.22
        self.obstacle_radius_map = {}
        self._last_planned_path = None
        self._last_plan_time = 0.0
        self._plan_interval = 0.5
        self._last_coord_print_time = 0.0
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
        self.all_candidate_paths = []  # Store all generated candidate paths persistently
    def process_frame(self, frame: np.ndarray):
        """
        Process a single frame: detect markers, compute poses, apply Kalman filter.
        Adapted from main.py, uses rrt_connect_plan for path planning.
        """
        # Detect ArUco markers
        corners, ids, rejected = self.detector.detectMarkers(frame)

        display = frame.copy()
        detections = {}

        if ids is not None:
            ids = ids.flatten()

            # Estimate pose for each marker with correct size
            rvecs = []
            tvecs = []
            for i, marker_id in enumerate(ids):
                marker_size = REFERENCE_MARKER_SIZE if marker_id in REFERENCE_MARKERS else OBJECT_MARKER_SIZE
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [corners[i]], marker_size, self.camera_matrix, self.dist_coeffs
                )
                rvecs.append(rvec[0])
                tvecs.append(tvec[0])

            rvecs = np.array(rvecs)
            tvecs = np.array(tvecs)

            # Compute/update camera extrinsics if needed
            ref_markers = [mid for mid in ids if mid in REFERENCE_MARKERS]
            if len(ref_markers) >= 4 and not self.extrinsics_valid:
                corners_dict = {ids[i]: corners[i] for i in range(len(ids))}
                self.compute_camera_extrinsics(corners_dict, ids)

            # Draw detected markers
            cv2.aruco.drawDetectedMarkers(display, corners, ids)

            # Prepare detections for Kalman filter (2D positions + orientation)
            kalman_detections = {}

            # Process each detected marker
            for i, marker_id in enumerate(ids):
                # Draw axis
                cv2.drawFrameAxes(display, self.camera_matrix, self.dist_coeffs,
                                 rvecs[i], tvecs[i], OBJECT_MARKER_SIZE * 0.5)

                if marker_id in REFERENCE_MARKERS:
                    color = (0, 255, 0)
                    label = f"REF {marker_id}"
                    detections[marker_id] = {
                        'type': 'reference',
                        'camera_pos': tvecs[i][0],
                        'world_pos': REFERENCE_MARKERS[marker_id]
                    }
                else:
                    if self.extrinsics_valid:
                        rvec_world, tvec_world = self.transform_to_world(rvecs[i], tvecs[i])
                        if tvec_world is not None:
                            world_pos = tvec_world.flatten()
                            theta = self.extract_orientation_angle(rvec_world)
                            kalman_detections[marker_id] = (world_pos[0], world_pos[1], theta)
                            detections[marker_id] = {
                                'type': 'enemy' if marker_id == ENEMY_MARKER_ID else 'object',
                                'camera_pos': tvecs[i][0],
                                'world_pos': world_pos,
                                'theta': theta,
                                'raw': True
                            }
                            if marker_id == ENEMY_MARKER_ID:
                                color = (0, 0, 255)
                                label = f"ENEMY {marker_id}"
                            else:
                                color = (255, 0, 255)
                                label = f"OBJ {marker_id}"
                            x, y, z = world_pos
                            label += f" | ({x:.3f}, {y:.3f}, {z:.3f})m"
                    else:
                        color = (128, 128, 128)
                        label = f"OBJ {marker_id} (no extrinsics)"
                corner = corners[i][0][0]
                cv2.putText(display, label, (int(corner[0]), int(corner[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                try:
                    marker_size = REFERENCE_MARKER_SIZE if marker_id in REFERENCE_MARKERS else OBJECT_MARKER_SIZE
                    marker_forward_local = np.array([[[marker_size/2.0, 0.0, 0.0]]], dtype=np.float32)
                    imgpts, _ = cv2.projectPoints(marker_forward_local, rvecs[i], tvecs[i], self.camera_matrix, self.dist_coeffs)
                    pt_forward = (int(imgpts[0][0][0]), int(imgpts[0][0][1]))
                    pt_center = (int(corner[0]), int(corner[1]))
                    cv2.arrowedLine(display, pt_center, pt_forward, (255, 255, 0), 2, tipLength=0.2)
                    theta_deg = None
                    if 'theta' in detections.get(marker_id, {}):
                        theta_deg = np.degrees(detections[marker_id]['theta'])
                    if theta_deg is not None:
                        angle_text = f"{theta_deg:.1f}°"
                        cv2.putText(display, angle_text, (pt_center[0], pt_center[1] + 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                except Exception:
                    pass

            if self.enable_kalman and self.kalman_tracker is not None and kalman_detections:
                dt = 1.0 / max(self.fps, 30.0)
                tracked_states = self.kalman_tracker.update(kalman_detections, dt)
                for marker_id, state in tracked_states.items():
                    if marker_id in detections:
                        detections[marker_id]['kalman_pos'] = (state.x, state.y, 0.0)
                        detections[marker_id]['kalman_theta'] = state.theta
                        detections[marker_id]['confidence'] = state.confidence
                        detections[marker_id]['is_occluded'] = state.is_occluded
                        detections[marker_id]['filtered'] = True
                        if marker_id == ENEMY_MARKER_ID:
                            kf_label = f"ENEMY {marker_id} (KF) | ({state.x:.3f}, {state.y:.3f}) | conf={state.confidence:.2f}"
                            if state.is_occluded:
                                kf_label += " [OCCLUDED]"
                            for j, mid in enumerate(ids):
                                if mid == marker_id:
                                    corner = corners[j][0][0]
                                    cv2.putText(display, kf_label, (int(corner[0]), int(corner[1]) + 20),
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                                    break

        self.frame_count += 1
        if self.frame_count % 30 == 0:
            current_time = time.time()
            elapsed = current_time - self.last_fps_time
            self.fps = 30.0 / elapsed if elapsed > 0 else 30.0
            self.last_fps_time = current_time

        status_y = 30
        ref_count = len([mid for mid in ids if mid in REFERENCE_MARKERS]) if ids is not None else 0
        if self.extrinsics_valid:
            status = f"TRACKING | Refs: {ref_count}/4 | FPS: {self.fps:.1f}"
            status_color = (0, 255, 0)
        else:
            status = f"CALIBRATING | Refs: {ref_count}/4 (need 4)"
            status_color = (0, 165, 255)
        if self.enable_kalman:
            status += " | Kalman: ON"
        cv2.putText(display, status, (10, status_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        if self.enable_kalman and self.kalman_tracker is not None:
            summary = self.kalman_tracker.get_tracking_summary()
            stats_text = f"Tracked: {summary['tracked_markers']} | Enemy: {summary['enemy_markers']} | Occluded: {summary['occluded_markers']}"
            cv2.putText(display, stats_text, (10, status_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return display, detections
    def load_intrinsics(self, intrinsics_file):
        """
        Load camera intrinsics from a JSON file and set camera matrix and distortion coefficients.
        """
        try:
            with open(intrinsics_file, 'r') as f:
                data = json.load(f)
            self.camera_matrix = np.array(data['camera_matrix'])
            # Use 'dist_coeffs' key (not 'dist_coeff')
            self.dist_coeffs = np.array(data['distortion_coefficients'])
            print(f"✓ Loaded camera intrinsics from {intrinsics_file}")
        except Exception as e:
            print(f"✗ Failed to load intrinsics: {e}")
            self.camera_matrix = None
            self.dist_coeffs = None
    def load_extrinsics(self, extrinsics_file):
        """
        Load camera extrinsics from a JSON file and set rvec_cam, tvec_cam, and extrinsics_valid.
        """
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
        """
        Compute camera extrinsics using solvePnP with reference marker corners.
        Args:
            corners_dict: Dictionary mapping marker ID to corner coordinates
            ids_detected: List of detected marker IDs
        Returns:
            True if extrinsics computed successfully
        """
        # Collect 3D world points and 2D image points for all reference markers
        object_points = []
        image_points = []
        for marker_id in ids_detected:
            if marker_id not in REFERENCE_MARKERS:
                continue
            marker_center = REFERENCE_MARKERS[marker_id]
            half_size = REFERENCE_MARKER_SIZE / 2
            # Define 4 corners in world coordinates (270° rotation - working config)
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
        # Solve PnP
        success, rvec, tvec = cv2.solvePnP(
            object_points,
            image_points,
            self.camera_matrix,
            self.dist_coeffs,
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
    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print(f"✗ Cannot open camera {self.camera_id}")
            return
        print(f"\n✓ Camera opened (ID: {self.camera_id})")
        print(f"✓ Kalman filter: {'ENABLED' if self.enable_kalman else 'DISABLED'}")
        print("\nControls:")
        print("  ESC - Quit")
        print("  SPACE - Reset extrinsics")
        print("  'k' - Toggle Kalman filter")
        print("\nWaiting for reference markers (20-23)...\n")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            display, detections = self.process_frame(frame)
            now = time.time()
            # --- Dynamic RRT-Connect Path Planning (Start = ID 36) ---
            if self.extrinsics_valid and now - self._last_plan_time > self._plan_interval:
                ally_marker_id = 36
                start_pos = None
                if ally_marker_id in detections and 'world_pos' in detections[ally_marker_id]:
                    start_pos = np.array(detections[ally_marker_id].get('kalman_pos', detections[ally_marker_id]['world_pos']))
                goal_pos = REFERENCE_MARKERS.get(23)
                if start_pos is not None and goal_pos is not None:
                    obstacles = []
                    enemy_obstacle = None
                    for mid, det in detections.items():
                        if mid == ENEMY_MARKER_ID and 'world_pos' in det:
                            pos = np.array(det.get('kalman_pos', det['world_pos']))
                            radius = self.enemy_obstacle_radius
                            current_obstacle = (pos, radius)
                            obstacles.append(current_obstacle)
                            enemy_obstacle = current_obstacle
                    is_blocked = False
                    if self._last_planned_path and enemy_obstacle:
                        is_blocked = self._sampled_circle_intersects_obstacle(self._last_planned_path, enemy_obstacle, self.robot_radius)
                    if self._last_planned_path is None or is_blocked:
                        if is_blocked:
                            print("! Path blocked by enemy. Replanning...")
                        bounds = (0.0, 3.0, 0.0, 2.0)
                        robot_r = getattr(self, 'robot_radius', 0.22)
                        inflated_obstacles = [(c, r + robot_r) for (c, r) in obstacles]
                        # --- Compute multiple candidate paths ---
                        candidate_paths = []
                        for seed in range(5):
                            np.random.seed(int(time.time() * 1000) % 2**32 + seed)
                            path = rrt_connect_plan(start_pos, goal_pos, inflated_obstacles, bounds)
                            if path:
                                candidate_paths.append(path)
                        # --- Store all candidate paths persistently ---
                        self.all_candidate_paths.extend(candidate_paths)
                        # --- Select shortest path ---
                        best_path = None
                        best_cost = float('inf')
                        for cand_path in candidate_paths:
                            cost = self._compute_path_cost(cand_path)
                            if cost < best_cost:
                                best_cost = cost
                                best_path = cand_path
                        self._last_planned_path = best_path
                        if self._last_planned_path:
                            print(f"✓ Best path found with {len(self._last_planned_path)} waypoints. Cost: {best_cost:.3f}")
                        else:
                            print("✗ RRT-Connect planner failed to find a path.")
                    self._last_plan_time = now
            # Print waypoints only when path changes
            if not hasattr(self, '_last_printed_path'):
                self._last_printed_path = None
            if now - self._last_coord_print_time > 0.2:
                    waypoints = []
                    if self._last_planned_path:
                        # Reverse the waypoints so start is first, goal is last
                        reversed_path = list(reversed(self._last_planned_path))
                        waypoints = [(float(pt[0]), float(pt[1])) for pt in reversed_path]
                        if waypoints != self._last_printed_path:
                            print("WAYPOINTS:", waypoints)
                            self._last_printed_path = waypoints
                    self._last_coord_print_time = now

            obstacles_to_draw = []
            for mid, det in detections.items():
                if 'world_pos' in det and mid not in REFERENCE_MARKERS:
                    pos = det.get('kalman_pos', det['world_pos'])
                    radius = self.enemy_obstacle_radius if mid == ENEMY_MARKER_ID else self.obstacle_radius_default
                    obstacles_to_draw.append((np.array(pos), radius))
            # --- Draw all candidate paths in black ---
            if self.all_candidate_paths:
                for cand_path in self.all_candidate_paths:
                    path_pixels = self._project_world_to_image(cand_path)
                    if path_pixels:
                        path_pts = np.array(path_pixels, dtype=np.int32).reshape((-1, 1, 2))
                        cv2.polylines(display, [path_pts], isClosed=False, color=(0, 0, 0), thickness=1)
            # --- Draw the best path in yellow/orange ---
            if self._last_planned_path:
                self.draw_rrt_path_and_obstacles(display, self._last_planned_path, obstacles_to_draw, robot_radius=self.robot_radius)
            cv2.imshow('Full Pipeline - Eurobot Tracking', display)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == 32:
                self.extrinsics_valid = False
                self.rvec_cam = None
                self.tvec_cam = None
                self.position_history.clear()
                if self.kalman_tracker:
                    self.kalman_tracker.trackers.clear()
                print("\n! Extrinsics reset - recalibrating...\n")
            elif key == ord('k'):
                self.enable_kalman = not self.enable_kalman
                print(f"\n! Kalman filter: {'ENABLED' if self.enable_kalman else 'DISABLED'}\n")
            # --- Waypoint selection: skip waypoints behind or too close to robot ---
            # Only run if we have a valid path and robot position
            if self._last_planned_path and 36 in detections and 'kalman_pos' in detections[36]:
                # Reverse the path so start is first, goal is last
                reversed_path = list(reversed(self._last_planned_path))
                robot_pos = np.array(detections[36]['kalman_pos'][:2])
                # If orientation is available, use it; else, use path direction
                robot_theta = detections[36].get('kalman_theta', None)
                if robot_theta is not None:
                    heading = np.array([np.cos(robot_theta), np.sin(robot_theta)])
                else:
                    # Fallback: direction to next waypoint
                    if len(reversed_path) > 1:
                        heading = np.array(reversed_path[1][:2]) - robot_pos
                        heading = heading / (np.linalg.norm(heading) + 1e-8)
                    else:
                        heading = np.array([1.0, 0.0])
                # Find first waypoint ahead and at a reasonable distance
                min_distance = self.robot_radius * 0.8
                next_waypoint = None
                for wp in reversed_path:
                    wp_vec = np.array(wp[:2]) - robot_pos
                    distance = np.linalg.norm(wp_vec)
                    if distance < min_distance:
                        continue  # Too close
                    dot = np.dot(heading, wp_vec / (distance + 1e-8))
                    if dot > 0.2:  # In front of robot (angle < ~78 deg)
                        next_waypoint = wp
                        break
                if next_waypoint is not None:
                    # Use next_waypoint for control (e.g., send to robot)
                    # For demonstration, print it:
                    print(f"NEXT WAYPOINT: {tuple(float(x) for x in next_waypoint)}")
        cap.release()
        cv2.destroyAllWindows()
def main():
    parser = argparse.ArgumentParser(
        description='Full Pipeline - Eurobot ArUco Tracking with Kalman Filter (RRT-Connect)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--camera', type=int, default=2,
                       help='Camera device ID (default: 1)')
    parser.add_argument('--intrinsics', type=str, default=DEFAULT_INTRINSICS,
                       help='Path to camera intrinsics JSON')
    parser.add_argument('--extrinsics', type=str, default=DEFAULT_EXTRINSICS,
                       help='Path to camera extrinsics JSON')
    parser.add_argument('--no-kalman', action='store_true',
                       help='Disable Kalman filtering')
    args = parser.parse_args()
    if not Path(args.intrinsics).exists():
        print(f"✗ Intrinsics file not found: {args.intrinsics}")
        print("\nPlease run camera calibration first:")
        print("  cd ../camera_calibration_folder")
        print("  python calibrate_camera.py --camera 1")
        return 1
    try:
        tracker = FullPipelineTracker(
            camera_id=args.camera,
            intrinsics_file=args.intrinsics,
            extrinsics_file=args.extrinsics,
            enable_kalman=not args.no_kalman
        )
        tracker.run()
    except KeyboardInterrupt:
        print("\n\n✓ Tracking stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
