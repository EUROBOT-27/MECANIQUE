"""Example Usage of Strategy Manager with Visualization

This script demonstrates how to use the strategy package for
utility-based task selection in Eurobot 2026 with live camera visualization.

Features:
- Live camera feed with ArUco detection
- Pantry and zone visualization
- ArUco ID significations (our crates, enemy crates, robots)
- Score-based task selection with rankings
- Path visualization with waypoints
- Action instructions (pickup, place, flip)
- Real-time task information overlay
"""

import sys
from pathlib import Path
import numpy as np
import cv2
import json
import time
from typing import Optional, Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from capacity_aware_strategy import CapacityAwareStrategyManager
from utils.config import StrategyConfig
from utils.world_state import WorldState, CrateInfo, CrateOwnership, CrateContainer
from utils.crate_id_tracker import CrateIDTracker
from strategy_manager import StrategyManager
# Camera calibration paths
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"

# ArUco parameters
ARUCO_DICT = cv2.aruco.DICT_4X4_50
CRATE_MARKER_SIZE = 0.03  # 3cm (black ArUco square only, not including vinyl border)
ROBOT_MARKER_SIZE = 0.05  # 5cm
REFERENCE_MARKER_SIZE = 0.10  # 10cm

# Marker IDs
BLUE_CRATE_ID = 36
YELLOW_CRATE_ID = 47
ALLY_ROBOT_ID = 17
REFERENCE_MARKER_IDS = [20, 21, 22, 23]

# Reference marker positions
REFERENCE_MARKERS = {
    21: np.array([0.600, 0.600, 0.0]),
    23: np.array([0.600, 1.400, 0.0]),
    22: np.array([2.400, 1.400, 0.0]),
    20: np.array([2.400, 0.600, 0.0]),
}

# Field parameters
FIELD_WIDTH = 3.0   # meters
FIELD_LENGTH = 2.0  # meters
ROBOT_RADIUS = 0.22  # meters


class StrategyVisualizer:
    """Visual demonstration of strategy system with live camera."""
    
    def __init__(self, team_color: str = "blue"):
        """Initialize visualizer."""
        self.team_color = team_color.lower()
        self.our_crate_id = BLUE_CRATE_ID if team_color == "blue" else YELLOW_CRATE_ID
        self.enemy_crate_id = YELLOW_CRATE_ID if team_color == "blue" else BLUE_CRATE_ID
        
        # Capacity-aware strategy manager
        self.manager = CapacityAwareStrategyManager(team_color=team_color)
        
        # Crate tracker for unique IDs
        self.crate_tracker = CrateIDTracker()
        
        # Camera calibration
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rvec = None
        self.tvec = None
        self.extrinsics_valid = False
        
        # ArUco detector
        aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        
        # Position tracking for teleportation filter
        self.marker_history = {}  # {marker_id: (x, y, z)}
        self.teleport_threshold = 0.5  # meters - ignore jumps larger than this
        
        # Visualization state
        self.ally_robot_pos = None
        self.show_debug = True
    
    def load_calibration(self, intrinsics_file: str, extrinsics_file: str):
        """Load camera calibration."""
        try:
            with open(intrinsics_file, 'r') as f:
                calib = json.load(f)
                self.camera_matrix = np.array(calib['camera_matrix'])
                self.dist_coeffs = np.array(calib['distortion_coefficients'])
            
            with open(extrinsics_file, 'r') as f:
                ext = json.load(f)
                self.rvec = np.array(ext['rvec'])
                self.tvec = np.array(ext['tvec'])
                self.extrinsics_valid = True
        except FileNotFoundError as e:
            self.extrinsics_valid = False
    
    def compute_extrinsics_from_reference(self, corners, ids) -> bool:
        """Compute camera extrinsics from reference markers using all 4 corners."""
        if ids is None or self.camera_matrix is None:
            return False
        
        # Collect 3D world points and 2D image points for all reference markers
        object_points = []
        image_points = []
        
        for i, marker_id in enumerate(ids.flatten()):
            if marker_id in REFERENCE_MARKERS:
                # Get world position of this reference marker center
                marker_center = REFERENCE_MARKERS[marker_id]
                half_size = REFERENCE_MARKER_SIZE / 2
                
                # Define 4 corners in world coordinates (standard ArUco corner order)
                corners_3d = np.array([
                    [marker_center[0] - half_size, marker_center[1] - half_size, 0],
                    [marker_center[0] + half_size, marker_center[1] - half_size, 0],
                    [marker_center[0] + half_size, marker_center[1] + half_size, 0],
                    [marker_center[0] - half_size, marker_center[1] + half_size, 0],
                ], dtype=np.float32)
                
                # Get detected corners in image (already in correct order)
                corners_2d = corners[i][0]
                
                object_points.extend(corners_3d)
                image_points.extend(corners_2d)
        
        if len(object_points) < 16:  # Need all 4 corners of at least 4 markers
            return False
        
        # Solve PnP with all corner points
        object_points = np.array(object_points, dtype=np.float32)
        image_points = np.array(image_points, dtype=np.float32)
        
        success, rvec, tvec = cv2.solvePnP(
            object_points,
            image_points,
            self.camera_matrix,
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if success:
            self.rvec = rvec
            self.tvec = tvec
            self.extrinsics_valid = True
            num_markers = len(object_points) // 4
            
            # Save to file
            try:
                extrinsics_data = {
                    'rvec': rvec.tolist(),
                    'tvec': tvec.tolist(),
                    'timestamp': time.time(),
                    'num_markers': num_markers
                }
                with open(DEFAULT_EXTRINSICS, 'w') as f:
                    json.dump(extrinsics_data, f, indent=2)
            except Exception as e:
                pass
            
            return True
        else:
            return False
    
    def transform_to_world(self, rvec_obj: np.ndarray, tvec_obj: np.ndarray):
        """Transform object pose from camera coordinates to world coordinates."""
        if not self.extrinsics_valid:
            return None, None
        
        R_cam, _ = cv2.Rodrigues(self.rvec)
        R_obj, _ = cv2.Rodrigues(rvec_obj)
        
        # Transform position: P_world = R_cam^T @ (P_camera - t_cam)
        P_camera = tvec_obj.reshape(3, 1)
        R_cam_inv = R_cam.T
        P_world = R_cam_inv @ (P_camera - self.tvec)
        
        # Transform rotation
        R_obj_world = R_cam_inv @ R_obj
        rvec_world, _ = cv2.Rodrigues(R_obj_world)
        
        return rvec_world, P_world
    
    def extract_orientation_angle(self, rvec: np.ndarray):
        """Extract yaw angle (rotation around Z axis) from rotation vector."""
        R, _ = cv2.Rodrigues(rvec)
        # Extract yaw from rotation matrix (assuming ZYX Euler angles)
        yaw = np.arctan2(R[1, 0], R[0, 0])
        return yaw
    
    def get_camera_pose(self) -> Optional[Tuple[np.ndarray, float]]:
        """Get camera position and orientation in world coordinates."""
        if not self.extrinsics_valid:
            return None
        
        # Camera position: -R^T @ t
        R_cam, _ = cv2.Rodrigues(self.rvec)
        camera_pos = -R_cam.T @ self.tvec
        
        # Camera orientation (yaw)
        camera_yaw = self.extract_orientation_angle(self.rvec)
        
        return camera_pos.flatten(), camera_yaw
    
    def project_to_image(self, world_points: np.ndarray) -> Optional[np.ndarray]:
        """Project 3D world points to 2D image."""
        if not self.extrinsics_valid:
            return None
        
        world_points = np.array(world_points, dtype=np.float32)
        if world_points.ndim == 1:
            world_points = world_points.reshape(1, -1)
        
        image_points, _ = cv2.projectPoints(
            world_points, self.rvec, self.tvec,
            self.camera_matrix, self.dist_coeffs
        )
        return image_points.reshape(-1, 2)
    
    def draw_camera_pose_on_field(self, display: np.ndarray):
        """Draw camera position and orientation on the field."""
        if not self.extrinsics_valid:
            return
        
        camera_pose = self.get_camera_pose()
        if camera_pose is None:
            return
        
        cam_pos, cam_yaw = camera_pose
        
        # Project camera position to image
        cam_world = np.array([cam_pos[0], cam_pos[1], 0.0])  # Project to ground plane
        cam_img = self.project_to_image(cam_world)
        
        if cam_img is not None:
            cx, cy = int(cam_img[0, 0]), int(cam_img[0, 1])
            
            # Draw camera position marker
            cv2.circle(display, (cx, cy), 12, (255, 100, 255), 2)
            cv2.circle(display, (cx, cy), 3, (255, 100, 255), -1)
            
            # Draw orientation arrow
            arrow_length = 60
            end_x = int(cx + arrow_length * np.cos(cam_yaw))
            end_y = int(cy + arrow_length * np.sin(cam_yaw))
            cv2.arrowedLine(display, (cx, cy), (end_x, end_y), 
                          (255, 150, 255), 2, tipLength=0.3)
            
            # Label
            cv2.putText(display, "CAMERA", (cx - 30, cy - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 255), 2)
    
    def determine_container(self, x: float, y: float) -> str:
        """Determine which container a crate is in based on position."""
        config = self.manager.config
        
        # Check pantries
        for pantry_name, bounds in config.pantry_zones.items():
            xmin, xmax, ymin, ymax = bounds
            if xmin <= x <= xmax and ymin <= y <= ymax:
                return 'pantry'
        
        # Check nests
        if self.team_color == 'blue':
            our_nest = config.nest_blue
            enemy_nest = config.nest_yellow
        else:
            our_nest = config.nest_yellow
            enemy_nest = config.nest_blue
        
        # Check our nest
        if our_nest[0] <= x <= our_nest[1] and our_nest[2] <= y <= our_nest[3]:
            return 'nest'
        
        # Check enemy nest
        if enemy_nest[0] <= x <= enemy_nest[1] and enemy_nest[2] <= y <= enemy_nest[3]:
            return 'nest'
        
        # Check fridges
        if config.fridge_blue[0] <= x <= config.fridge_blue[1] and config.fridge_blue[2] <= y <= config.fridge_blue[3]:
            return 'fridge'
        if config.fridge_yellow[0] <= x <= config.fridge_yellow[1] and config.fridge_yellow[2] <= y <= config.fridge_yellow[3]:
            return 'fridge'
        
        # Default: free on field
        return 'free'
    
    def draw_zones(self, display: np.ndarray):
        """Draw pantry zones, nests, and endgame area."""
        if not self.extrinsics_valid:
            return
        
        config = self.manager.config
        pantries = config.pantry_zones
        
        def draw_zone(xmin, xmax, ymin, ymax, color, label, score_text=""):
            corners = np.array([
                [xmin, ymin, 0.0],
                [xmax, ymin, 0.0],
                [xmax, ymax, 0.0],
                [xmin, ymax, 0.0]
            ], dtype=np.float32)
            
            corners_img = self.project_to_image(corners)
            if corners_img is not None:
                pts = corners_img.astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(display, [pts], True, color, 2)
                
                # Label with score
                center_x = int(np.mean(corners_img[:, 0]))
                center_y = int(np.mean(corners_img[:, 1]))
                cv2.putText(display, label, (center_x - 40, center_y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                if score_text:
                    cv2.putText(display, score_text, (center_x - 40, center_y + 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Draw nests (green for ours, red for enemy) - 2 pts per crate
        if self.team_color == "blue":
            draw_zone(*config.nest_blue, (0, 200, 0), "OUR NEST", "2pts")
            draw_zone(*config.nest_yellow, (0, 0, 200), "ENEMY NEST", "")
        else:
            draw_zone(*config.nest_yellow, (0, 200, 0), "OUR NEST", "2pts")
            draw_zone(*config.nest_blue, (0, 0, 200), "ENEMY NEST", "")
        
        # Draw all pantries (cyan) - 3 pts per crate
        if pantries:
            for i, (name, bounds) in enumerate(pantries.items()):
                xmin, xmax, ymin, ymax = bounds
                draw_zone(xmin, xmax, ymin, ymax, (255, 255, 0), name.upper(), "3pts")
        
        # Draw endgame area (opponent's side only) - 10 pts
        if self.team_color == "blue":
            draw_zone(*config.endgame_yellow, (255, 165, 0), "ENEMY ENDGAME", "")
        else:
            draw_zone(*config.endgame_blue, (255, 165, 0), "ENEMY ENDGAME", "")
    
    def draw_aruco_info(self, display: np.ndarray, detections: Dict):
        """Draw ArUco markers with ID significations and world coordinates."""
        corners = detections['corners']
        ids = detections['ids']
        
        if ids is None:
            return
        
        cv2.aruco.drawDetectedMarkers(display, corners, ids)
        
        # Create lookup dict for crate unique IDs
        crate_unique_ids = {}
        for crate in detections.get('crates', []):
            aruco_id = crate.get('aruco_id', crate.get('id'))
            unique_id = crate.get('unique_id')
            pos = crate.get('pos')
            if unique_id and pos:
                # Store by position (rounded to avoid floating point issues)
                key = (aruco_id, round(pos[0], 2), round(pos[1], 2))
                crate_unique_ids[key] = unique_id
        
        # Draw world coordinates for all markers
        for marker_info in detections.get('all_markers', []):
            marker_id = marker_info['id']
            marker_corners = marker_info['corners']
            world_pos = marker_info['world_pos']
            center = marker_corners.mean(axis=0).astype(int)
            
            # Determine marker type and color
            if marker_id == self.our_crate_id:
                label = "OUR CRATE"
                color = (0, 255, 0)
            elif marker_id == self.enemy_crate_id:
                label = "ENEMY CRATE"
                color = (0, 0, 255)
            elif marker_id in REFERENCE_MARKER_IDS:
                label = f"REF M{marker_id}"
                color = (128, 128, 128)
            else:
                label = "ROBOT"
                color = (255, 0, 255)
            
            # Get unique ID if this is a crate
            unique_id = None
            if marker_id in [self.our_crate_id, self.enemy_crate_id]:
                key = (marker_id, round(world_pos[0], 2), round(world_pos[1], 2))
                unique_id = crate_unique_ids.get(key)
            
            # Draw label with world coordinates and unique ID
            x, y, z = world_pos
            if unique_id:
                coord_text = f"{label} #{unique_id} | ({x:.3f}, {y:.3f})m"
            else:
                coord_text = f"{label} | ({x:.3f}, {y:.3f})m"
            cv2.putText(display, coord_text, (center[0] + 15, center[1] - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
    
    def draw_path(self, display: np.ndarray, path: List[np.ndarray]):
        """Draw planned path with waypoints."""
        if not self.extrinsics_valid or not path or len(path) < 2:
            return
        
        path_world = np.array(path, dtype=np.float32)
        path_img = self.project_to_image(path_world)
        
        if path_img is None:
            return
        
        # Draw path line
        path_pts = path_img.astype(np.int32).reshape((-1, 1, 2))
        cv2.polylines(display, [path_pts], False, (0, 255, 255), 3)
        
        # Draw waypoints with numbers
        for i, (wp_world, wp_img) in enumerate(zip(path, path_img)):
            px, py = int(wp_img[0]), int(wp_img[1])
            cv2.circle(display, (px, py), 6, (0, 165, 255), -1)
            
            # Draw waypoint number
            cv2.putText(display, str(i), (px + 10, py - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # First and last waypoint labels
            if i == 0:
                cv2.putText(display, "START", (px - 20, py - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            elif i == len(path) - 1:
                cv2.putText(display, "GOAL", (px - 20, py - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
    
    def draw_task_info(self, display: np.ndarray, task_output: Optional[Dict]):
        """Draw task information overlay with capacity status."""
        # Create semi-transparent overlay panel
        overlay = display.copy()
        h, w = display.shape[:2]
        
        # Panel dimensions (increased for capacity info)
        panel_height = 240
        cv2.rectangle(overlay, (0, 0), (w, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, display, 0.4, 0, display)
        
        if task_output is None:
            cv2.putText(display, "NO FEASIBLE TASK", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return
        
        # Task information
        y_offset = 25
        line_height = 22
        
        # Title
        cv2.putText(display, "SELECTED TASK:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        y_offset += line_height + 5
        
        # Get capacity status
        capacity_status = self.manager.get_capacity_status()
        
        # Task details
        info_lines = [
            f"Type: {task_output['task_type'].replace('_', ' ').upper()}",
            f"Action: {task_output['action'].upper()} - {self._get_action_description(task_output['action'])}",
            f"Target: ({task_output['target'][0]:.2f}m, {task_output['target'][1]:.2f}m)",
            f"Score: {task_output['expected_score']:.0f} points | Utility: {task_output['utility']:.3f}",
            f"Time: {task_output['time_cost']:.1f}s | Waypoints: {len(task_output['path'])}",
            f"",  # Blank line
            f"CAPACITY: Batch {capacity_status['batch_size']} tasks | "
            f"Pickup {capacity_status['pickup_capacity_used']} | "
            f"Flip {capacity_status['flip_capacity_used']}",
        ]
        
        for line in info_lines:
            if line:  # Skip blank lines
                cv2.putText(display, line, (15, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += line_height
        
        # Description
        desc = task_output['description'][:60]
        cv2.putText(display, f"Description: {desc}", (15, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    
    def draw_game_timer(self, display: np.ndarray, time_remaining: float):
        """Draw game timer at the top of the screen."""
        # Calculate minutes and seconds
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        
        # Format timer string
        timer_text = f"TIME: {minutes:02d}:{seconds:02d}"
        
        # Choose color based on time remaining
        if time_remaining > 60:
            color = (0, 255, 0)  # Green
        elif time_remaining > 30:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 0, 255)  # Red
        
        # Get text size for centering
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        (text_width, text_height), baseline = cv2.getTextSize(timer_text, font, font_scale, thickness)
        
        # Draw background rectangle
        padding = 10
        bg_x1 = (display.shape[1] - text_width) // 2 - padding
        bg_y1 = 5
        bg_x2 = bg_x1 + text_width + 2 * padding
        bg_y2 = bg_y1 + text_height + 2 * padding
        cv2.rectangle(display, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        cv2.rectangle(display, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 2)
        
        # Draw timer text centered at top
        text_x = (display.shape[1] - text_width) // 2
        text_y = bg_y1 + text_height + padding
        cv2.putText(display, timer_text, (text_x, text_y), font, font_scale, color, thickness)
    
    def draw_arm_reach_circles(self, display: np.ndarray, task_output: Optional[Dict]):
        """Draw arm reach circles around crates and pantries with approach visualization."""
        if not self.extrinsics_valid or task_output is None:
            return
        
        # Get arm reach distance from config
        arm_reach = self.manager.config.arm_reach_distance
        pantry_reach = self.manager.config.pantry_placement_distance
        
        # Draw circle around crate with perpendicular approach visualization
        if 'associated_crate' in task_output and task_output.get('action') in ['place', 'flip']:
            # Get crate position from task
            if hasattr(self.manager.best_task, 'associated_crate') and self.manager.best_task.associated_crate:
                crate_pos = self.manager.best_task.associated_crate.position
                crate_world = np.array([[crate_pos[0], crate_pos[1], 0.0]], dtype=np.float32)
                crate_img = self.project_to_image(crate_world)
                
                if crate_img is not None:
                    cx, cy = int(crate_img[0, 0]), int(crate_img[0, 1])
                    
                    # Calculate radius in pixels
                    edge_world = np.array([[crate_pos[0] + arm_reach, crate_pos[1], 0.0]], dtype=np.float32)
                    edge_img = self.project_to_image(edge_world)
                    
                    if edge_img is not None:
                        radius = int(np.linalg.norm(crate_img[0] - edge_img[0]))
                        # Draw arm reach circle
                        cv2.circle(display, (cx, cy), radius, (255, 255, 0), 2)
                        cv2.putText(display, "ARM REACH", (cx - 40, cy - radius - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                        
                        # Use stored perpendicular points from task if available
                        if hasattr(self.manager.best_task, 'perpendicular_point1') and hasattr(self.manager.best_task, 'perpendicular_point2'):
                            point1 = self.manager.best_task.perpendicular_point1
                            point2 = self.manager.best_task.perpendicular_point2
                            chosen = self.manager.best_task.chosen_approach_point
                            
                            point1_world = np.array([[point1[0], point1[1], 0.0]], dtype=np.float32)
                            point2_world = np.array([[point2[0], point2[1], 0.0]], dtype=np.float32)
                            chosen_world = np.array([[chosen[0], chosen[1], 0.0]], dtype=np.float32)
                            
                            p1_img = self.project_to_image(point1_world)
                            p2_img = self.project_to_image(point2_world)
                            chosen_img = self.project_to_image(chosen_world)
                            
                            if p1_img is not None and p2_img is not None:
                                p1 = tuple(p1_img[0].astype(int))
                                p2 = tuple(p2_img[0].astype(int))
                                
                                # Draw vertical line (perpendicular to X-axis)
                                cv2.line(display, p1, p2, (0, 255, 0), 3)
                                cv2.putText(display, "PERP to X", (p1[0] + 15, p1[1] - 25),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                                
                                # Draw intersection points
                                cv2.circle(display, p1, 8, (0, 255, 0), -1)
                                cv2.circle(display, p2, 8, (0, 255, 0), -1)
                                cv2.putText(display, "P1", (p1[0] + 10, p1[1] - 10),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                cv2.putText(display, "P2", (p2[0] + 10, p2[1] + 20),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                
                                # Highlight chosen point
                                if chosen_img is not None:
                                    chosen_px = tuple(chosen_img[0].astype(int))
                                    cv2.circle(display, chosen_px, 12, (255, 0, 255), 4)
                                    cv2.putText(display, "CHOSEN", (chosen_px[0] - 35, chosen_px[1] - 20),
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        
        # Draw circle around pantry with placement visualization
        if task_output.get('action') == 'place':
            # Get pantry center from path (last waypoint or target)
            if task_output['path'] and len(task_output['path']) > 0:
                # Find pantry center - it's the actual target before adjustment
                task_type = task_output.get('task_type', '')
                if 'pantry' in task_type.lower():
                    # Get original pantry center from config
                    for pantry_name, bounds in self.manager.config.pantry_zones.items():
                        pantry_center = (
                            (bounds[0] + bounds[1]) / 2.0,
                            (bounds[2] + bounds[3]) / 2.0
                        )
                        # Check if target is near this pantry
                        target_pos = task_output['target']
                        dist = np.linalg.norm(np.array(target_pos) - np.array(pantry_center))
                        if dist < 0.3:  # Within 30cm means this is our pantry
                            pantry_world = np.array([[pantry_center[0], pantry_center[1], 0.0]], dtype=np.float32)
                            pantry_img = self.project_to_image(pantry_world)
                            
                            if pantry_img is not None:
                                px, py = int(pantry_img[0, 0]), int(pantry_img[0, 1])
                                
                                # Calculate radius in pixels
                                edge_world = np.array([[pantry_center[0] + pantry_reach, pantry_center[1], 0.0]], dtype=np.float32)
                                edge_img = self.project_to_image(edge_world)
                                
                                if edge_img is not None:
                                    radius = int(np.linalg.norm(pantry_img[0] - edge_img[0]))
                                    cv2.circle(display, (px, py), radius, (0, 255, 255), 2)
                                    cv2.putText(display, "PLACE ZONE", (px - 45, py - radius - 5),
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                                    
                                    # Draw line from pantry center to placement point
                                    target_world = np.array([[target_pos[0], target_pos[1], 0.0]], dtype=np.float32)
                                    target_img = self.project_to_image(target_world)
                                    if target_img is not None:
                                        tx, ty = int(target_img[0, 0]), int(target_img[0, 1])
                                        cv2.line(display, (px, py), (tx, ty), (0, 255, 255), 2)
                                        cv2.circle(display, (tx, ty), 8, (255, 0, 255), -1)
                            break
    
    def _get_action_description(self, action: str) -> str:
        """Get human-readable action description."""
        descriptions = {
            'pickup': 'Pick up crate from ground',
            'place': 'Place/displace crate to zone',
            'flip': 'Flip crate to convert to our team',
            'none': 'Navigate to position'
        }
        return descriptions.get(action, 'Unknown action')
    
    def draw_task_rankings(self, display: np.ndarray, tasks: List):
        """Draw task rankings sidebar."""
        if not tasks:
            return
        
        h, w = display.shape[:2]
        
        # Sort tasks by utility
        sorted_tasks = sorted(
            [t for t in tasks if t.utility > 0],
            key=lambda t: t.utility,
            reverse=True
        )[:5]
        
        if not sorted_tasks:
            return
        
        # Panel dimensions
        panel_width = 350
        panel_x = w - panel_width
        
        # Semi-transparent panel
        overlay = display.copy()
        cv2.rectangle(overlay, (panel_x, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, display, 0.4, 0, display)
        
        # Title
        cv2.putText(display, "TASK RANKINGS", (panel_x + 10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Rankings
        y_offset = 55
        for i, task in enumerate(sorted_tasks, 1):
            # Rank number
            rank_color = (0, 255, 0) if i == 1 else (255, 255, 255)
            cv2.putText(display, f"#{i}", (panel_x + 10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, rank_color, 2)
            
            # Task type
            task_name = task.task_type.value.replace('_', ' ')[:25]
            cv2.putText(display, task_name, (panel_x + 45, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Utility score
            cv2.putText(display, f"U:{task.utility:.2f}", (panel_x + 45, y_offset + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
            
            # Score
            cv2.putText(display, f"S:{task.expected_score:.0f}pts", (panel_x + 120, y_offset + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 0), 1)
            
            # Action
            action_color = {
                'pickup': (100, 255, 100),
                'place': (255, 200, 100),
                'flip': (255, 100, 100),
                'none': (200, 200, 200)
            }.get(task.action.value, (255, 255, 255))
            
            cv2.putText(display, task.action.value.upper(), (panel_x + 220, y_offset + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, action_color, 1)
            
            y_offset += 45
    
    def _validate_crate_color(self, frame: np.ndarray, corners: np.ndarray, marker_id: int) -> float:
        """
        Validate crate color to improve detection confidence.
        
        Args:
            frame: Input image
            corners: Marker corner points
            marker_id: ArUco marker ID (36=blue, 47=yellow)
            
        Returns:
            Confidence multiplier (0.5-1.5) based on color match
        """
        # Extract region around marker
        x_coords = corners[:, 0].astype(int)
        y_coords = corners[:, 1].astype(int)
        
        # Expand region slightly to get crate color (not just marker)
        margin = 5
        x_min = max(0, x_coords.min() - margin)
        x_max = min(frame.shape[1], x_coords.max() + margin)
        y_min = max(0, y_coords.min() - margin)
        y_max = min(frame.shape[0], y_coords.max() + margin)
        
        roi = frame[y_min:y_max, x_min:x_max]
        
        if roi.size == 0:
            return 1.0  # Neutral if can't extract ROI
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Define color ranges in HSV
        # Blue: Hue 100-130 (opencv uses 0-180 for hue)
        blue_lower = np.array([100, 50, 50])
        blue_upper = np.array([130, 255, 255])
        
        # Yellow: Hue 20-35
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([35, 255, 255])
        
        # Create masks
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        # Count pixels
        blue_pixels = np.count_nonzero(blue_mask)
        yellow_pixels = np.count_nonzero(yellow_mask)
        total_pixels = roi.shape[0] * roi.shape[1]
        
        blue_ratio = blue_pixels / total_pixels
        yellow_ratio = yellow_pixels / total_pixels
        
        # Validate based on expected marker color
        if marker_id == BLUE_CRATE_ID:  # 36
            # Expect blue crate
            if blue_ratio > 0.15:  # At least 15% blue pixels
                return 1.2  # Boost confidence
            elif yellow_ratio > 0.15:  # Conflicting color
                return 0.6  # Reduce confidence (might be wrong detection)
        elif marker_id == YELLOW_CRATE_ID:  # 47
            # Expect yellow crate
            if yellow_ratio > 0.15:  # At least 15% yellow pixels
                return 1.2  # Boost confidence
            elif blue_ratio > 0.15:  # Conflicting color
                return 0.6  # Reduce confidence (might be wrong detection)
        
        return 1.0  # Neutral if uncertain
    
    def detect_markers(self, frame: np.ndarray) -> Dict:
        """Detect ArUco markers and classify them with world coordinates."""
        corners, ids, _ = self.detector.detectMarkers(frame)
        
        result = {
            'ally_robot': None,
            'crates': [],
            'corners': corners,
            'ids': ids,
            'all_markers': []  # All detected markers with world coordinates
        }
        
        if ids is None:
            return result
        
        ids = ids.flatten()
        
        for i, marker_id in enumerate(ids):
            marker_corners = corners[i][0]
            
            # Estimate pose with correct marker size
            if marker_id in REFERENCE_MARKER_IDS:
                marker_size = REFERENCE_MARKER_SIZE
            elif marker_id in [BLUE_CRATE_ID, YELLOW_CRATE_ID]:
                marker_size = CRATE_MARKER_SIZE
            else:
                marker_size = ROBOT_MARKER_SIZE
            
            obj_points = np.array([
                [-marker_size/2, marker_size/2, 0],
                [marker_size/2, marker_size/2, 0],
                [marker_size/2, -marker_size/2, 0],
                [-marker_size/2, -marker_size/2, 0]
            ], dtype=np.float32)
            
            success, rvec, tvec = cv2.solvePnP(
                obj_points, marker_corners,
                self.camera_matrix, self.dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
            
            if not success:
                continue
            
            # Transform to world coordinates if extrinsics valid
            if self.extrinsics_valid:
                rvec_world, tvec_world = self.transform_to_world(rvec, tvec)
                
                if tvec_world is not None:
                    world_pos = tvec_world.flatten()
                    theta = self.extract_orientation_angle(rvec_world)
                    
                    # Teleportation filter: ONLY for robot and reference markers (not crates)
                    # Crates can have multiple instances, so don't filter by marker_id
                    if marker_id not in [BLUE_CRATE_ID, YELLOW_CRATE_ID]:
                        if marker_id in self.marker_history:
                            prev_pos = self.marker_history[marker_id]
                            distance = np.linalg.norm(world_pos - prev_pos)
                            
                            # Ignore if movement is unrealistically large (teleportation)
                            if distance > self.teleport_threshold:
                                # Keep previous position instead of updating
                                world_pos = prev_pos
                                # Optional: print warning for debugging
                                # print(f"[FILTER] Ignored teleport for ID {marker_id}: {distance:.2f}m jump")
                        
                        # Update position history for non-crate markers
                        self.marker_history[marker_id] = world_pos.copy()
                    
                    # Store marker info with world coordinates
                    marker_info = {
                        'id': marker_id,
                        'camera_pos': tvec.flatten(),
                        'world_pos': world_pos,
                        'theta': theta,
                        'corners': marker_corners
                    }
                    result['all_markers'].append(marker_info)
                    
                    # Classify marker
                    if marker_id == ALLY_ROBOT_ID:
                        # ArUco ID 17 is our ally robot
                        result['ally_robot'] = {
                            'id': marker_id,
                            'pos': tuple(world_pos),
                            'orientation': theta
                        }
                    elif marker_id in [BLUE_CRATE_ID, YELLOW_CRATE_ID]:
                        ownership = 'ours' if marker_id == self.our_crate_id else 'opponent'
                        
                        # Validate color to improve confidence
                        color_confidence = self._validate_crate_color(frame, marker_corners, marker_id)
                        base_confidence = 1.0
                        final_confidence = base_confidence * color_confidence
                        
                        # Only add detection if confidence is reasonable
                        if final_confidence >= 0.5:  # Filter out low-confidence detections
                            # Determine container based on position
                            container = self.determine_container(world_pos[0], world_pos[1])
                            
                            result['crates'].append({
                                'aruco_id': marker_id,  # Use aruco_id key for tracker
                                'pos': tuple(world_pos),
                                'ownership': ownership,
                                'container': container,
                                'confidence': final_confidence
                            })
        
        # Assign unique IDs to crates (handles multiple crates with same ArUco marker)
        if result['crates']:
            result['crates'] = self.crate_tracker.assign_unique_ids(result['crates'])
        
        return result
    
    def run(self, camera_id: int = 1):
        """Run live visualization."""
        # Load calibration
        self.load_calibration(DEFAULT_INTRINSICS, DEFAULT_EXTRINSICS)
        
        # Open camera
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"[ERROR] Failed to open camera {camera_id}")
            return
        
        print(f"\n[OK] Camera {camera_id} opened")
        print("Controls: ESC=Exit | SPACE=Recompute extrinsics | D=Toggle debug | P=Print task\n")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            display = frame.copy()
            
            # Detect markers
            detections = self.detect_markers(frame)
            
            # Draw zones
            self.draw_zones(display)
            
            # Draw camera pose on field
            self.draw_camera_pose_on_field(display)
            
            # Draw ArUco markers with significations and world coordinates
            self.draw_aruco_info(display, detections)
            
            # Draw enemies if any detected
            if detections.get('enemy_robot'):
                enemy_pos = detections['enemy_robot']['pos']
                enemy_world = np.array([[enemy_pos[0], enemy_pos[1], 0.0]], dtype=np.float32)
                enemy_img = self.project_to_image(enemy_world)
                if enemy_img is not None:
                    ex, ey = int(enemy_img[0, 0]), int(enemy_img[0, 1])
                    # Draw enemy with red circle and danger zone
                    cv2.circle(display, (ex, ey), 20, (0, 0, 255), 3)
                    cv2.circle(display, (ex, ey), 5, (0, 0, 255), -1)
                    # Draw danger radius (0.15m obstacle radius from path planning)
                    edge_world = np.array([[enemy_pos[0] + 0.15, enemy_pos[1], 0.0]], dtype=np.float32)
                    edge_img = self.project_to_image(edge_world)
                    if edge_img is not None:
                        danger_radius = int(np.linalg.norm(enemy_img[0] - edge_img[0]))
                        cv2.circle(display, (ex, ey), danger_radius, (0, 0, 255), 2)
                    cv2.putText(display, "ENEMY", (ex - 30, ey - 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Update strategy if ally robot detected
            if detections['ally_robot'] is not None:
                ally_pos = detections['ally_robot']['pos']
                ally_orientation = detections['ally_robot']['orientation']
                robot_pose = (ally_pos[0], ally_pos[1], ally_orientation)
                
                # Enemy positions from detections
                enemy_positions = []
                if detections.get('enemy_robot'):
                    enemy = detections['enemy_robot']
                    enemy_positions.append((enemy['pos'][0], enemy['pos'][1], enemy.get('orientation', 0.0)))
                
                # Update strategy
                time_elapsed = time.time() - start_time
                time_remaining = max(0, 100.0 - time_elapsed)
                
                self.manager.update_world_state(
                    robot_pose=robot_pose,
                    detected_crates=detections['crates'],
                    enemy_positions=enemy_positions,
                    static_obstacles=[],
                    time_remaining=time_remaining
                )
                
                # Evaluate tasks
                tasks = self.manager.evaluate_tasks()
                best_task = self.manager.select_best_task()
                
                # Get output
                if best_task:
                    output = self.manager.get_best_task_output()
                    
                    # Draw path FIRST (works for all task types)
                    if output and output['path']:
                        self.draw_path(display, output['path'])
                        
                        # Draw arm reach circles for visualization
                        self.draw_arm_reach_circles(display, output)
                        
                        # Draw circle around target (highest utility task)
                        target_world = np.array([output['target'][0], output['target'][1], 0.0])
                        target_img = self.project_to_image(target_world)
                        if target_img is not None:
                            target_px = tuple(target_img[0].astype(int))
                            # Draw pulsing circle around target
                            radius = int(30 + 10 * np.sin(time.time() * 3))
                            cv2.circle(display, target_px, radius, (0, 255, 0), 3)
                            cv2.circle(display, target_px, 8, (0, 255, 0), -1)
                            # Draw score text
                            cv2.putText(display, f"{output['expected_score']:.0f}pts", 
                                      (target_px[0] - 25, target_px[1] - radius - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Highlight source and destination for place tasks (ADDITIONAL OVERLAY)
                    if output and 'hazelnut' in output['task_type'].lower() and 'pantry' in output['task_type'].lower():
                        # Find the crate being moved
                        for crate in detections['crates']:
                            crate_pos = np.array([crate['pos'][0], crate['pos'][1], 0.0])
                            # Check if this crate is near the start of the path
                            if output['path'] and len(output['path']) > 0:
                                start_pos = np.array(output['path'][0][:2])
                                if np.linalg.norm(crate_pos[:2] - start_pos) < 0.3:  # Within 30cm
                                    # Highlight source crate
                                    crate_img = self.project_to_image(crate_pos)
                                    if crate_img is not None:
                                        cx, cy = tuple(crate_img[0].astype(int))
                                        cv2.circle(display, (cx, cy), 40, (0, 255, 255), 3)
                                        cv2.putText(display, "SOURCE", (cx - 35, cy - 50),
                                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                        
                        # Highlight target pantry zone
                        target_world = np.array([output['target'][0], output['target'][1], 0.0])
                        # Find which pantry contains this target
                        for pantry_name, bounds in self.manager.config.pantry_zones.items():
                            xmin, xmax, ymin, ymax = bounds
                            if (xmin <= output['target'][0] <= xmax and 
                                ymin <= output['target'][1] <= ymax):
                                # Draw highlighted pantry border
                                corners = np.array([
                                    [xmin, ymin, 0.0], [xmax, ymin, 0.0],
                                    [xmax, ymax, 0.0], [xmin, ymax, 0.0]
                                ], dtype=np.float32)
                                corners_img = self.project_to_image(corners)
                                if corners_img is not None:
                                    pts = corners_img.astype(np.int32).reshape((-1, 1, 2))
                                    cv2.polylines(display, [pts], True, (0, 255, 0), 4)
                                    # Add "DESTINATION" label
                                    center_x = int(np.mean(corners_img[:, 0]))
                                    center_y = int(np.mean(corners_img[:, 1]))
                                    cv2.putText(display, "DESTINATION", (center_x - 60, center_y - 30),
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                break
                    
                    # Draw game timer
                    self.draw_game_timer(display, time_remaining)
                    
                    # Draw task info
                    self.draw_task_info(display, output)
                    
                    # Draw rankings
                    if self.show_debug:
                        self.draw_task_rankings(display, tasks)
            else:
                # No robot detected
                cv2.putText(display, "Waiting for ally robot...", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            
            # Status info
            fps = frame_count / (time.time() - start_time + 0.001)
            h, w = display.shape[:2]
            cv2.putText(display, f"FPS: {fps:.1f}", (10, h - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Camera pose info (bottom right)
            if self.extrinsics_valid:
                camera_pose = self.get_camera_pose()
                if camera_pose:
                    cam_pos, cam_yaw = camera_pose
                    pose_text = [
                        f"Camera Pose:",
                        f"X: {cam_pos[0]:.3f}m",
                        f"Y: {cam_pos[1]:.3f}m",
                        f"Z: {cam_pos[2]:.3f}m",
                        f"Yaw: {np.degrees(cam_yaw):.1f}deg"
                    ]
                    y_start = h - 120
                    for i, text in enumerate(pose_text):
                        cv2.putText(display, text, (w - 200, y_start + i * 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 255, 100), 1)
            
            cv2.imshow('Strategy Manager - Example Usage', display)
            
            frame_count += 1
            
            # Keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord(' '):  # SPACE - Recompute extrinsics
                print("\n[SPACE] Recomputing extrinsics from reference markers...")
                if self.compute_extrinsics_from_reference(detections['corners'], detections['ids']):
                    print("[OK] Extrinsics updated successfully")
                else:
                    print("[ERROR] Failed to update extrinsics")
            elif key == ord('d'):  # Toggle debug
                self.show_debug = not self.show_debug
            elif key == ord('p'):  # Print details
                if detections['ally_robot']:
                    print("\n" + "="*70)
                    print("CURRENT TASK DETAILS")
                    print("="*70)
                    self.manager.print_task_rankings(top_n=3)
                    output = self.manager.get_best_task_output()
                    if output:
                        print(f"\nPath: {len(output['path'])} waypoints")
                        for i, wp in enumerate(output['path'][:5]):
                            print(f"  {i}: ({wp[0]:.3f}, {wp[1]:.3f}, {wp[2]:.3f})")
        
        cap.release()
        cv2.destroyAllWindows()


def create_sample_world_state():
    """Create sample world state for demonstration."""
    
    # Sample robot pose
    robot_pose = (1.5, 1.0, 0.0)  # (x, y, theta) in meters
    
    # Sample detected crates
    detected_crates = [
        # Our crates (free)
        {
            'id': 36,
            'pos': (0.8, 0.5, 0.05),
            'ownership': 'ours',
            'container': 'free',
            'confidence': 1.0
        },
        {
            'id': 36,
            'pos': (1.2, 0.7, 0.05),
            'ownership': 'ours',
            'container': 'free',
            'confidence': 1.0
        },
        
        # Our crate already in pantry (becomes obstacle)
        {
            'id': 36,
            'pos': (0.8, 0.1, 0.05),
            'ownership': 'ours',
            'container': 'pantry',
            'confidence': 1.0
        },
        
        # Opponent crate in their fridge (target for emptying)
        {
            'id': 47,
            'pos': (2.7, 1.1, 0.05),
            'ownership': 'opponent',
            'container': 'fridge',
            'confidence': 1.0
        },
        
        # Free crates (for filling our fridge)
        {
            'id': 47,
            'pos': (1.8, 1.3, 0.05),
            'ownership': 'opponent',
            'container': 'free',
            'confidence': 1.0
        },
    ]
    
    # Enemy positions from detection or LiDAR
    enemy_positions = []
    
    # Static obstacles (empty - detected crates become obstacles automatically)
    static_obstacles = []
    
    # Time remaining
    time_remaining = 85.0  # seconds
    
    return robot_pose, detected_crates, enemy_positions, static_obstacles, time_remaining


def example_basic_usage():
    """Example 1: Basic usage with default configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 1: BASIC USAGE")
    print("="*70 + "\n")
    
    # Initialize strategy manager
    manager = StrategyManager(team_color="blue")
    
    # Get sample world state
    robot_pose, crates, enemies, obstacles, time_left = create_sample_world_state()
    
    # Update world state
    manager.update_world_state(
        robot_pose=robot_pose,
        detected_crates=crates,
        enemy_positions=enemies,
        static_obstacles=obstacles,
        time_remaining=time_left
    )
    
    # Evaluate all tasks
    print("Evaluating tasks...")
    tasks = manager.evaluate_tasks()
    print(f"Generated {len(tasks)} candidate tasks")
    print(f"Feasible tasks: {len([t for t in tasks if t.utility > 0])}")
    print(f"Planning time: {manager.last_planning_time:.3f}s")
    
    # Print task rankings
    manager.print_task_rankings(top_n=5)
    
    # Select best task
    best_task = manager.select_best_task()
    
    # Get actionable output
    output = manager.get_best_task_output()
    
    if output:
        print("\n" + "-"*70)
        print("ACTIONABLE OUTPUT:")
        print("-"*70)
        print(f"Task ID: {output['task_id']}")
        print(f"Task Type: {output['task_type']}")
        print(f"Action: {output['action'].upper()}")
        print(f"Target: ({output['target'][0]:.2f}, {output['target'][1]:.2f})")
        print(f"Expected Score: {output['expected_score']:.1f} points")
        print(f"Estimated Time: {output['time_cost']:.1f} seconds")
        print(f"Path Length: {len(output['path'])} waypoints")
        
        print("\nPath waypoints:")
        for i, waypoint in enumerate(output['path'][:5]):  # Show first 5
            print(f"  {i+1}. ({waypoint[0]:.3f}, {waypoint[1]:.3f})")
        if len(output['path']) > 5:
            print(f"  ... ({len(output['path']) - 5} more waypoints)")
        
        print("\n" + "-"*70)


def example_custom_configuration():
    """Example 2: Using custom configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 2: CUSTOM CONFIGURATION (AGGRESSIVE MODE)")
    print("="*70 + "\n")
    
    # Create custom configuration
    config = StrategyConfig()
    config.set_aggressive_mode()  # Lower safety priority, higher speed
    
    # Override specific parameters
    config.weight_time_cost = 1.2  # Prefer very fast tasks
    config.enemy_danger_radius = 0.3  # Smaller danger zone
    
    # Initialize with custom config
    manager = StrategyManager(team_color="blue", config=config)
    
    # Update world state
    robot_pose, crates, enemies, obstacles, time_left = create_sample_world_state()
    manager.update_world_state(
        robot_pose=robot_pose,
        detected_crates=crates,
        enemy_positions=enemies,
        static_obstacles=obstacles,
        time_remaining=time_left
    )
    
    # Evaluate and select
    tasks = manager.evaluate_tasks()
    best_task = manager.select_best_task()
    
    print(f"\nAggressive mode selected: {best_task.description}")
    print(f"Utility: {best_task.utility:.3f} (compare with defensive mode)")


def example_endgame_scenario():
    """Example 3: Endgame scenario."""
    print("\n" + "="*70)
    print("EXAMPLE 3: ENDGAME SCENARIO")
    print("="*70 + "\n")
    
    manager = StrategyManager(team_color="blue")
    
    # Endgame state (only 12 seconds left!)
    robot_pose, crates, enemies, obstacles, _ = create_sample_world_state()
    
    manager.update_world_state(
        robot_pose=robot_pose,
        detected_crates=crates,
        enemy_positions=enemies,
        static_obstacles=obstacles,
        time_remaining=12.0  # Endgame!
    )
    
    # Evaluate tasks
    tasks = manager.evaluate_tasks()
    
    print("World state:")
    print(f"  Phase: {manager.world_state.match_phase}")
    print(f"  Time remaining: {manager.world_state.time_remaining}s")
    print(f"  Endgame: {manager.world_state.is_in_endgame()}")
    
    # Print rankings
    manager.print_task_rankings(top_n=3)
    
    best_task = manager.select_best_task()
    
    print("\n➜ In endgame, return-to-nest tasks get priority boost!")


def example_statistics():
    """Example 4: Getting statistics."""
    print("\n" + "="*70)
    print("EXAMPLE 4: STATISTICS AND MONITORING")
    print("="*70 + "\n")
    
    manager = StrategyManager(team_color="yellow")  # Yellow team
    
    robot_pose, crates, enemies, obstacles, time_left = create_sample_world_state()
    manager.update_world_state(
        robot_pose=robot_pose,
        detected_crates=crates,
        enemy_positions=enemies,
        static_obstacles=obstacles,
        time_remaining=time_left
    )
    
    tasks = manager.evaluate_tasks()
    best_task = manager.select_best_task()
    
    # Get statistics
    stats = manager.get_statistics()
    
    print("System Statistics:")
    print(f"  Team: YELLOW")
    print(f"  Candidate tasks: {stats['num_candidate_tasks']}")
    print(f"  Feasible tasks: {stats['num_feasible_tasks']}")
    print(f"  Planning time: {stats['last_planning_time']:.3f}s")
    print(f"  Planning count: {stats['planning_count']}")
    
    print("\nWorld State:")
    ws = stats['world_state']
    print(f"  Robot: ({ws['robot_pose']['x']:.2f}, {ws['robot_pose']['y']:.2f})")
    print(f"  Crates: {ws['num_crates']}")
    print(f"  Enemies: {ws['num_enemies']}")
    print(f"  Phase: {ws['phase']}")
    print(f"  Time: {ws['time_remaining']:.1f}s")


def example_task_details():
    """Example 5: Inspecting task details."""
    print("\n" + "="*70)
    print("EXAMPLE 5: TASK DETAILS INSPECTION")
    print("="*70 + "\n")
    
    manager = StrategyManager(team_color="blue")
    
    robot_pose, crates, enemies, obstacles, time_left = create_sample_world_state()
    manager.update_world_state(
        robot_pose=robot_pose,
        detected_crates=crates,
        enemy_positions=enemies,
        static_obstacles=obstacles,
        time_remaining=time_left
    )
    
    tasks = manager.evaluate_tasks()
    
    # Inspect top 3 tasks in detail
    print("Detailed Task Inspection:\n")
    
    for i, task in enumerate(tasks[:3], 1):
        print(f"{i}. {task.description}")
        task_dict = task.to_dict()
        
        print(f"   Task Type: {task_dict['task_type']}")
        print(f"   Action: {task_dict['action']}")
        print(f"   Target: ({task_dict['target'][0]:.2f}, {task_dict['target'][1]:.2f})")
        print(f"   Utility Components:")
        print(f"     • Expected Score: {task_dict['expected_score']:.1f} points")
        print(f"     • Feasibility: {task_dict['feasibility']:.2f}")
        print(f"     • Safety: {task_dict['safety_factor']:.2f}")
        print(f"     • Time Cost: {task_dict['time_cost']:.1f}s")
        print(f"     • Distance Cost: {task_dict['distance_cost']:.2f}m")
        print(f"   ═══ Final Utility: {task_dict['utility']:.3f} ═══\n")


def main():
    """Run visual example with camera."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Strategy Manager - Visual Example with Camera'
    )
    parser.add_argument('--camera', type=int, default=1,
                       help='Camera device ID (default: 1)')
    parser.add_argument('--team', type=str, default='blue', choices=['blue', 'yellow'],
                       help='Team color (default: blue)')
    parser.add_argument('--text-only', action='store_true',
                       help='Run text-only examples without camera')
    
    args = parser.parse_args()
    
    if args.text_only:
        # Run original text examples
        print("\n" + "#"*70)
        print("# STRATEGY MANAGER - TEXT EXAMPLES")
        print("#"*70)
        
        example_basic_usage()
        example_custom_configuration()
        example_endgame_scenario()
        example_statistics()
        example_task_details()
        
        print("\n" + "#"*70)
        print("# ALL EXAMPLES COMPLETED")
        print("#"*70 + "\n")
    else:
        # Run visual example
        print("\n" + "#"*70)
        print("# STRATEGY MANAGER - VISUAL EXAMPLE")
        print("#"*70 + "\n")
        
        visualizer = StrategyVisualizer(team_color=args.team)
        
        try:
            visualizer.run(camera_id=args.camera)
        except KeyboardInterrupt:
            print("\n[OK] Visualization stopped")
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n[OK] Strategy package example completed!")
    print("\nWhat you saw:")
    print("  • Live camera feed with ArUco detection")
    print("  • Zone visualization (nest, pantries, fridge, endgame)")
    print("  • ArUco ID significations (our crates, enemy crates)")
    print("  • Score-based task selection with utilities")
    print("  • Path visualization with waypoints")
    print("  • Action instructions (pickup, place, flip, none)")
    print("  • Real-time task rankings")
    print("\nNext steps:")
    print("  1. Integrate with your main pipeline")
    print("  2. Connect real LiDAR for enemy positions")
    print("  3. Tune StrategyConfig weights for your robot")
    print("  4. Execute paths with your motion controller\n")


if __name__ == "__main__":
    main()
