#!/usr/bin/env python3

"""Crate Obstacle Manager - Classify crates as obstacles or interactable objects

This module manages crate detection and classification for path planning.
Coordinate system matches main_connect.py:
- Field dimensions: 3.0m (width) x 2.0m (length)
- Origin: Bottom-left corner (0, 0)
- X-axis: Along field width (left to right)
- Y-axis: Along field length (bottom to top)
- Units: meters

Classification Rules:
- Crates of our color inside pantries = OBSTACLES (already doing their job)
- Crates of our color outside pantries = INTERACTABLE (can be picked up)
- Enemy crates anywhere = INTERACTABLE (can be stolen/blocked)

ArUco IDs:
- 36: Blue crate
- 47: Yellow crate

Reference Markers (from main_connect.py):
- M22: (0.600, 0.600, 0.0)m - Bottom-left
- M20: (0.600, 1.400, 0.0)m - Top-left
- M21: (2.400, 1.400, 0.0)m - Top-right
- M23: (2.400, 0.600, 0.0)m - Bottom-right
"""

import numpy as np
import cv2
import json
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from enum import Enum

# Add path for path_planning import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from path_planning.rrt_connect import rrt_connect_plan

# Import crate ID tracker
try:
    from crate_id_tracker import CrateIDTracker
except ImportError:
    # If not in same folder, try from strategy
    sys.path.insert(0, str(Path(__file__).parent.parent / "strategy"))
    from crate_id_tracker import CrateIDTracker

# Import crate ID tracker
try:
    from crate_id_tracker import CrateIDTracker
except ImportError:
    # If not in same folder, try from strategy
    sys.path.insert(0, str(Path(__file__).parent.parent / "strategy"))
    from crate_id_tracker import CrateIDTracker


class TeamColor(Enum):
    """Team color enumeration."""
    BLUE = "blue"
    YELLOW = "yellow"


class CrateType(Enum):
    """Crate classification."""
    OBSTACLE = "obstacle"  # Our color in pantry
    INTERACTABLE = "interactable"  # Our color outside pantry or enemy anywhere


# ============================================================================
# CONFIGURATION (Matches main_connect.py)
# ============================================================================

# Field dimensions (from main_connect.py)
FIELD_WIDTH = 3.0   # meters (X-axis)
FIELD_LENGTH = 2.0  # meters (Y-axis)

# Camera calibration files (from main_connect.py)
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"

# ArUco detection parameters
ARUCO_DICT = cv2.aruco.DICT_4X4_50
CRATE_MARKER_SIZE = 0.05  # 5cm crate markers

# Pantry regions in WORLD coordinates (meters) - (xmin, xmax, ymin, ymax)
# Coordinate system: Origin at bottom-left, X right, Y up
PANTRIES_WORLD = {
    'pantry1': (0.700, 0.900, 0.000, 0.200),   # Bottom-left area
    'pantry2': (1.400, 1.600, 0.000, 0.200),   # Bottom-center area
    'pantry3': (2.200, 2.400, 0.000, 0.200),   # Bottom-right area
    'pantry4': (2.100, 2.300, 0.700, 0.900),   # Right-side area
    'build5': (1.100, 1.350, 1.350, 1.550),    # Top-center-left build zone
    'build6': (1.650, 1.850, 1.350, 1.550),    # Top-center-right build zone
}

# ArUco marker IDs
BLUE_CRATE_ID = 36
YELLOW_CRATE_ID = 47
START_MARKER_ID = 20  # Reference marker for start position
REFERENCE_MARKER_SIZE = 0.10  # 10cm for reference markers

# Reference markers world positions (from main_connect.py)
REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}

# Path planning parameters (from main_connect.py)
ROBOT_RADIUS = 0.22        # Robot footprint radius in meters
OBSTACLE_RADIUS = 0.01     # 5cm radius around obstacle crates
OBSTACLE_MOVEMENT_THRESHOLD = 0.05  # 5cm - ignore movement below this (noise filtering)
FIELD_BOUNDS = (0.0, FIELD_WIDTH, 0.0, FIELD_LENGTH)  # (xmin, xmax, ymin, ymax)

# Placeholder destination goal (will come from mission planner file later)
# For now, use reference marker M23 position from main_connect.py
DEFAULT_GOAL_POSITION = (2.400, 0.600, 0.0)  # Marker M23 position


# ============================================================================
# CRATE OBSTACLE MANAGER
# ============================================================================

class CrateObstacleManager:
    """Manage crate detection and classification for path planning."""
    
    def __init__(self, team_color: TeamColor, goal_position: Optional[Tuple[float, float, float]] = None):
        """
        Initialize the crate obstacle manager.
        
        Args:
            team_color: Our team color (BLUE or YELLOW)
            goal_position: Destination goal coordinates (x, y, z) in meters.
                          If None, uses DEFAULT_GOAL_POSITION placeholder.
                          This will come from mission planner file later.
        """
        self.team_color = team_color
        self.pantries = PANTRIES_WORLD
        self.goal_position = goal_position if goal_position is not None else DEFAULT_GOAL_POSITION
        
        # Set our crate ID and enemy crate ID
        if team_color == TeamColor.BLUE:
            self.our_crate_id = BLUE_CRATE_ID
            self.enemy_crate_id = YELLOW_CRATE_ID
        else:
            self.our_crate_id = YELLOW_CRATE_ID
            self.enemy_crate_id = BLUE_CRATE_ID
        
        # Initialize crate ID tracker (handles multiple crates with same ArUco ID)
        self.crate_tracker = CrateIDTracker()
        
        # Camera calibration
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rvec_cam = None
        self.tvec_cam = None
        self.extrinsics_valid = False
        
        # Path planning state (from main_connect.py)
        self._last_planned_path = None
        self._last_plan_time = 0.0
        self._plan_interval = 0.5  # Plan every 0.5 seconds
        self._last_obstacle_positions = None  # Track obstacle movement
        
        print(f"✓ Crate Obstacle Manager initialized")
        print(f"  Team: {team_color.value.upper()}")
        print(f"  Our crate ID: {self.our_crate_id}")
        print(f"  Enemy crate ID: {self.enemy_crate_id}")
        print(f"  Field bounds: {FIELD_BOUNDS}")
        print(f"  Goal position: {self.goal_position}")
        print(f"  Pantries defined: {list(self.pantries.keys())}")
    
    def load_intrinsics(self, intrinsics_file: str) -> bool:
        """Load camera intrinsics from JSON file."""
        try:
            with open(intrinsics_file, 'r') as f:
                data = json.load(f)
            self.camera_matrix = np.array(data['camera_matrix'])
            self.dist_coeffs = np.array(data['distortion_coefficients'])
            print(f"✓ Loaded camera intrinsics")
            return True
        except Exception as e:
            print(f"✗ Failed to load intrinsics: {e}")
            return False
    
    def load_extrinsics(self, extrinsics_file: str) -> bool:
        """Load camera extrinsics from JSON file."""
        try:
            with open(extrinsics_file, 'r') as f:
                data = json.load(f)
            self.rvec_cam = np.array(data['rvec'])
            self.tvec_cam = np.array(data['tvec'])
            self.extrinsics_valid = True
            print(f"✓ Loaded camera extrinsics")
            return True
        except Exception as e:
            print(f"✗ Failed to load extrinsics: {e}")
            self.extrinsics_valid = False
            return False
    
    def project_world_to_image(self, world_points: np.ndarray) -> Optional[np.ndarray]:
        """Project 3D world points to image pixel coordinates."""
        if not self.extrinsics_valid:
            return None
        pts = np.array(world_points, dtype=np.float32).reshape(-1, 3)
        imgpts, _ = cv2.projectPoints(pts, self.rvec_cam, self.tvec_cam, 
                                     self.camera_matrix, self.dist_coeffs)
        return imgpts.reshape(-1, 2)
    
    def _sampled_circle_intersects_obstacle(self, path, obstacle, robot_radius, num_samples=50):
        """Check if path intersects obstacle (from main_connect.py)."""
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
    
    def is_point_in_pantry(self, x: float, y: float) -> Tuple[bool, Optional[str]]:
        """
        Check if a point is inside any pantry region.
        
        Args:
            x: X coordinate (meters or pixels)
            y: Y coordinate (meters or pixels)
            
        Returns:
            Tuple of (is_in_pantry, pantry_name)
        """
        for pantry_name, (xmin, xmax, ymin, ymax) in self.pantries.items():
            if xmin <= x <= xmax and ymin <= y <= ymax:
                return True, pantry_name
        return False, None
    
    def classify_crate(self, crate_id: int, x: float, y: float) -> Tuple[CrateType, str]:
        """
        Classify a crate as obstacle or interactable.
        
        Args:
            crate_id: ArUco marker ID of the crate
            x: X coordinate of crate center
            y: Y coordinate of crate center
            
        Returns:
            Tuple of (CrateType, reason_string)
        """
        is_our_crate = (crate_id == self.our_crate_id)
        is_in_pantry, pantry_name = self.is_point_in_pantry(x, y)
        
        if is_our_crate and is_in_pantry:
            # Our crate in pantry = OBSTACLE (already doing its job)
            reason = f"Our crate in {pantry_name}"
            return CrateType.OBSTACLE, reason
        elif is_our_crate and not is_in_pantry:
            # Our crate outside pantry = INTERACTABLE (can be picked up)
            reason = "Our crate outside pantry"
            return CrateType.INTERACTABLE, reason
        else:
            # Enemy crate anywhere = INTERACTABLE (can be stolen/blocked)
            location = f"in {pantry_name}" if is_in_pantry else "outside pantry"
            reason = f"Enemy crate {location}"
            return CrateType.INTERACTABLE, reason
    
    def process_detected_crates(self, detected_markers: Dict) -> Dict:
        """
        Process detected ArUco markers and classify crates.
        
        Args:
            detected_markers: Dictionary from ArUco detector with format:
                {
                    'ids': [list of marker IDs],
                    'markers': [
                        {'id': marker_id, 'world_coords': [x, y, z]},
                        ...
                    ]
                }
                
        Returns:
            Dictionary with classified crates:
            {
                'obstacles': [
                    {'unique_id': unique_id, 'aruco_id': aruco_id, 'pos': (x, y, z), 'pantry': pantry_name},
                    ...
                ],
                'interactable': [
                    {'unique_id': unique_id, 'aruco_id': aruco_id, 'pos': (x, y, z), 'reason': reason_string},
                    ...
                ],
                'obstacle_positions': [(x, y), ...]  # For path planning
            }
        """
        obstacles = []
        interactable = []
        obstacle_positions = []
        
        if 'markers' not in detected_markers:
            return {
                'obstacles': obstacles,
                'interactable': interactable,
                'obstacle_positions': obstacle_positions
            }
        
        # Prepare crates for ID tracking
        crate_detections = []
        for marker in detected_markers['markers']:
            marker_id = marker['id']
            
            # Check if this is a crate marker
            if marker_id not in [BLUE_CRATE_ID, YELLOW_CRATE_ID]:
                continue
            
            # Get position
            coords = marker.get('world_coords')
            if coords is None:
                continue  # Skip if no coordinates available
            
            crate_detections.append({
                'id': marker_id,
                'aruco_id': marker_id,
                'pos': coords,
                'ownership': 'ours' if marker_id == self.our_crate_id else 'opponent',
                'container': 'free',
                'confidence': 1.0
            })
        
        # Assign unique IDs to crates
        crates_with_ids = self.crate_tracker.assign_unique_ids(crate_detections)
        
        # Classify each crate
        for crate in crates_with_ids:
            x, y, z = crate['pos']
            
            # Classify the crate
            crate_type, reason = self.classify_crate(crate['aruco_id'], x, y)
            
            if crate_type == CrateType.OBSTACLE:
                # Add to obstacles list
                _, pantry_name = self.is_point_in_pantry(x, y)
                obstacles.append({
                    'unique_id': crate['unique_id'],
                    'aruco_id': crate['aruco_id'],
                    'pos': (x, y, z),
                    'pantry': pantry_name
                })
                obstacle_positions.append((x, y))
            else:
                # Add to interactable list
                interactable.append({
                    'unique_id': crate['unique_id'],
                    'aruco_id': crate['aruco_id'],
                    'pos': (x, y, z),
                    'reason': reason
                })
        
        return {
            'obstacles': obstacles,
            'interactable': interactable,
            'obstacle_positions': obstacle_positions
        }
    
    def get_obstacle_circles(self, obstacle_positions: List[Tuple[float, float]], 
                            radius: float = OBSTACLE_RADIUS) -> List[Tuple[float, float, float]]:
        """
        Convert obstacle positions to circles for path planning.
        
        Args:
            obstacle_positions: List of (x, y) positions
            radius: Radius around each obstacle in meters
            
        Returns:
            List of (x, y, radius) tuples for circular obstacles
        """
        return [(x, y, radius) for x, y in obstacle_positions]
    
    def get_goal_position(self) -> Tuple[float, float, float]:
        """
        Get the current goal position for path planning.
        
        Returns:
            Goal position as (x, y, z) tuple in meters
            
        Note:
            This is currently a placeholder. In the future, this will be
            provided by a mission planner file that determines the next
            objective (e.g., crate pickup location, delivery zone, etc.)
        """
        return self.goal_position
    
    def set_goal_position(self, x: float, y: float, z: float = 0.0):
        """
        Update the goal position for path planning.
        
        Args:
            x: X coordinate in meters
            y: Y coordinate in meters
            z: Z coordinate in meters (default: 0.0)
            
        Note:
            This will be called by the mission planner in the future.
        """
        self.goal_position = (x, y, z)
        print(f"✓ Goal position updated: {self.goal_position}")
    
    def draw_path_on_frame(self, display_frame: np.ndarray, path: List, obstacles: List):
        """
        Draw the RRT path and obstacles onto the display frame (from main_connect.py).
        """
        if not self.extrinsics_valid:
            return
        
        # Draw obstacles
        for center, radius in obstacles:
            center_2d = self.project_world_to_image([center])
            if center_2d is None or len(center_2d) == 0:
                continue
            center_2d = (int(center_2d[0, 0]), int(center_2d[0, 1]))
            
            edge_point_3d = center + np.array([radius, 0, 0])
            edge_point_2d = self.project_world_to_image([edge_point_3d])
            if edge_point_2d is None or len(edge_point_2d) == 0:
                continue
            edge_2d = (int(edge_point_2d[0, 0]), int(edge_point_2d[0, 1]))
            
            pixel_radius = int(np.linalg.norm(np.array(center_2d) - np.array(edge_2d)))
            cv2.circle(display_frame, center_2d, pixel_radius, (255, 100, 0), 2)
        
        # Draw path
        if path and len(path) > 1:
            path_pixels = self.project_world_to_image(path)
            if path_pixels is not None and len(path_pixels) > 0:
                path_pts = path_pixels.astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(display_frame, [path_pts], isClosed=False, color=(0, 255, 255), thickness=2)
                
                # Draw robot footprint circles at intervals
                num_samples = max(10, len(path) * 5)
                sampled_points = []
                for i in range(len(path) - 1):
                    p0 = np.array(path[i])
                    p1 = np.array(path[i + 1])
                    for t in np.linspace(0, 1, num_samples // (len(path) - 1)):
                        pt_world = p0 * (1 - t) + p1 * t
                        sampled_points.append(pt_world)
                
                sampled_pixels = self.project_world_to_image(sampled_points)
                if sampled_pixels is not None:
                    for pt_world, pt_pixel in zip(sampled_points, sampled_pixels):
                        try:
                            p = (int(pt_pixel[0]), int(pt_pixel[1]))
                            wx = float(pt_world[0])
                            wy = float(pt_world[1])
                            
                            # Draw robot radius circle
                            edge_pt_world = np.array([wx + ROBOT_RADIUS, wy, 0.0])
                            edge_px = self.project_world_to_image([edge_pt_world])
                            if edge_px is not None and len(edge_px) > 0:
                                pixel_r = int(np.linalg.norm(np.array(p) - np.array([int(edge_px[0, 0]), int(edge_px[0, 1])])))
                                cv2.circle(display_frame, p, pixel_r, (0, 165, 255), 1)
                        except Exception:
                            continue
                
                # Draw waypoints
                for wp_world, pt in zip(path, path_pixels):
                    try:
                        p = (int(pt[0]), int(pt[1]))
                        cv2.circle(display_frame, p, 5, (0, 165, 255), -1)
                        wx = float(wp_world[0])
                        wy = float(wp_world[1])
                        coord_text = f"({wx:.3f},{wy:.3f})"
                        cv2.putText(display_frame, coord_text, (p[0] + 6, p[1] - 6), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (230, 230, 230), 1)
                    except Exception:
                        continue
    
    def visualize_on_frame(self, frame: np.ndarray, classification_result: Dict) -> np.ndarray:
        """
        Draw pantries, crates, and goal position on camera frame.
        
        Args:
            frame: Camera frame to draw on
            classification_result: Result from process_detected_crates()
            
        Returns:
            Annotated frame
        """
        display = frame.copy()
        
        if not self.extrinsics_valid:
            cv2.putText(display, "EXTRINSICS NOT LOADED - NO VISUALIZATION", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return display
        
        # Draw pantry regions
        for pantry_name, (xmin, xmax, ymin, ymax) in self.pantries.items():
            # Define pantry corners in world coordinates
            corners_world = np.array([
                [xmin, ymin, 0.0],
                [xmax, ymin, 0.0],
                [xmax, ymax, 0.0],
                [xmin, ymax, 0.0]
            ], dtype=np.float32)
            
            # Project to image
            corners_img = self.project_world_to_image(corners_world)
            if corners_img is not None:
                pts = corners_img.astype(np.int32).reshape((-1, 1, 2))
                # Draw pantry rectangle in cyan
                cv2.polylines(display, [pts], True, (255, 255, 0), 2)
                
                # Draw pantry label
                center_x = int(np.mean(corners_img[:, 0]))
                center_y = int(np.mean(corners_img[:, 1]))
                cv2.putText(display, pantry_name, (center_x - 40, center_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Draw obstacle crates (RED)
        for obs in classification_result['obstacles']:
            x, y, z = obs['pos']
            world_pt = np.array([[x, y, z]], dtype=np.float32)
            img_pt = self.project_world_to_image(world_pt)
            
            if img_pt is not None:
                px, py = int(img_pt[0, 0]), int(img_pt[0, 1])
                # Draw red circle for obstacle
                cv2.circle(display, (px, py), 15, (0, 0, 255), -1)
                cv2.circle(display, (px, py), int(OBSTACLE_RADIUS * 100), (0, 0, 255), 2)
                # Draw ID and coordinates
                cv2.putText(display, f"ID {obs['id']} OBSTACLE", 
                           (px + 20, py - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(display, f"({x:.2f}, {y:.2f})", 
                           (px + 20, py),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(display, obs['pantry'], 
                           (px + 20, py + 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # Draw interactable crates (GREEN)
        for obj in classification_result['interactable']:
            x, y, z = obj['pos']
            world_pt = np.array([[x, y, z]], dtype=np.float32)
            img_pt = self.project_world_to_image(world_pt)
            
            if img_pt is not None:
                px, py = int(img_pt[0, 0]), int(img_pt[0, 1])
                # Draw green circle for interactable
                cv2.circle(display, (px, py), 12, (0, 255, 0), -1)
                cv2.circle(display, (px, py), 18, (0, 255, 0), 2)
                # Draw ID and coordinates
                cv2.putText(display, f"ID {obj['id']} INTERACTABLE", 
                           (px + 20, py - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(display, f"({x:.2f}, {y:.2f})", 
                           (px + 20, py),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(display, obj['reason'], 
                           (px + 20, py + 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # Draw goal position (MAGENTA)
        goal_world = np.array([self.goal_position], dtype=np.float32)
        goal_img = self.project_world_to_image(goal_world)
        if goal_img is not None:
            gx, gy = int(goal_img[0, 0]), int(goal_img[0, 1])
            # Draw magenta star/cross for goal
            cv2.drawMarker(display, (gx, gy), (255, 0, 255), 
                          cv2.MARKER_STAR, 30, 3)
            cv2.putText(display, "GOAL", (gx + 20, gy - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(display, f"({self.goal_position[0]:.2f}, {self.goal_position[1]:.2f})", 
                       (gx + 20, gy),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw status info
        y_offset = 30
        team_color_bgr = (255, 0, 0) if self.team_color == TeamColor.BLUE else (0, 200, 200)
        cv2.putText(display, f"Team: {self.team_color.value.upper()}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, team_color_bgr, 2)
        y_offset += 30
        cv2.putText(display, f"Obstacles: {len(classification_result['obstacles'])} (RED)", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        y_offset += 25
        cv2.putText(display, f"Interactable: {len(classification_result['interactable'])} (GREEN)", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += 25
        cv2.putText(display, f"Pantries: {len(self.pantries)} (CYAN)", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return display
    
    def print_status(self, classification_result: Dict):
        """
        Print current crate classification status.
        
        Args:
            classification_result: Result from process_detected_crates()
        """
        print("\n" + "="*60)
        print("CRATE CLASSIFICATION STATUS")
        print("="*60)
        
        print(f"\nOBSTACLES (Our crates in pantries): {len(classification_result['obstacles'])}")
        for obs in classification_result['obstacles']:
            x, y, z = obs['pos']
            print(f"  • ID {obs['id']} @ ({x:.3f}, {y:.3f}, {z:.3f}) in {obs['pantry']}")
        
        print(f"\nINTERACTABLE (Available for tasks): {len(classification_result['interactable'])}")
        for obj in classification_result['interactable']:
            x, y, z = obj['pos']
            print(f"  • ID {obj['id']} @ ({x:.3f}, {y:.3f}, {z:.3f}) - {obj['reason']}")
        
        print("="*60 + "\n")
    
    def run_visualization(self, camera_id: int = 1, 
                         intrinsics_file: str = DEFAULT_INTRINSICS,
                         extrinsics_file: str = DEFAULT_EXTRINSICS):
        """
        Run live camera visualization with crate detection and classification.
        
        Args:
            camera_id: Camera device ID
            intrinsics_file: Path to camera intrinsics JSON
            extrinsics_file: Path to camera extrinsics JSON
        """
        # Load calibration
        self.load_intrinsics(intrinsics_file)
        self.load_extrinsics(extrinsics_file)
        
        # Setup ArUco detector
        aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        aruco_params = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        
        # Open camera
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"✗ Cannot open camera {camera_id}")
            return
        
        print(f"\n✓ Camera opened (ID: {camera_id})")
        print("\nControls:")
        print("  ESC - Quit")
        print("  'p' - Print status to console")
        print("  'g' - Change goal position")
        print(f"\nPath Planning:")
        print(f"  Start: ArUco ID {START_MARKER_ID} (Reference marker)")
        print(f"  Goal: {self.goal_position}")
        print("\nDetecting crates and planning path...\n")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect ArUco markers (no undistortion, same as main_connect.py)
            corners, ids, rejected = detector.detectMarkers(frame)

            # Build detected_markers dict and track all markers
            detected_markers = {'ids': [], 'markers': []}
            all_detections = {}  # Track all markers including start marker
            
            if ids is not None:
                detected_markers['ids'] = ids.flatten().tolist()
                
                # Estimate pose for each marker using estimatePoseSingleMarkers (same as main_connect.py)
                for i, marker_id in enumerate(detected_markers['ids']):
                    # Determine marker size
                    marker_size = REFERENCE_MARKER_SIZE if marker_id in REFERENCE_MARKERS else CRATE_MARKER_SIZE
                    
                    # Estimate pose
                    rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                        [corners[i]], marker_size,
                        self.camera_matrix, self.dist_coeffs
                    )
                    
                    # Transform to world coordinates
                    world_pos = None
                    if self.extrinsics_valid:
                        R_cam, _ = cv2.Rodrigues(self.rvec_cam)
                        P_camera = tvec[0][0].reshape(3, 1)
                        R_cam_inv = R_cam.T
                        P_world = R_cam_inv @ (P_camera - self.tvec_cam)
                        world_pos = np.array([P_world[0, 0], P_world[1, 0], P_world[2, 0]])
                    
                    # Store in all_detections
                    all_detections[marker_id] = {
                        'world_pos': world_pos
                    }
                    
                    # For crate markers, continue processing
                    if marker_id not in [BLUE_CRATE_ID, YELLOW_CRATE_ID]:
                        continue
                        
                    # Original crate detection code
                    marker_id_int = marker_id
                    world_coords = None
                    if world_pos is not None:
                        world_coords = [float(world_pos[0]), float(world_pos[1]), float(world_pos[2])]
                    
                    detected_markers['markers'].append({
                        'id': marker_id_int,
                        'world_coords': world_coords
                    })
            
            # Classify crates
            classification = self.process_detected_crates(detected_markers)
            
            # --- Path Planning (from main_connect.py) ---
            now = time.time()
            if self.extrinsics_valid and now - self._last_plan_time > self._plan_interval:
                # Get start position from marker ID 20
                start_pos = None
                if START_MARKER_ID in all_detections and all_detections[START_MARKER_ID]['world_pos'] is not None:
                    start_pos = all_detections[START_MARKER_ID]['world_pos']
                
                goal_pos = np.array(self.goal_position)
                
                if start_pos is not None:
                    # Build obstacles list from classified crates
                    obstacle_circles = self.get_obstacle_circles(classification['obstacle_positions'])
                    
                    # Check if obstacles have moved significantly (beyond noise threshold)
                    obstacles_moved = False
                    if self._last_obstacle_positions is not None:
                        current_positions = classification['obstacle_positions']
                        
                        # Check if number of obstacles changed
                        if len(current_positions) != len(self._last_obstacle_positions):
                            obstacles_moved = True
                        else:
                            # Check if any obstacle moved beyond threshold
                            for curr_pos in current_positions:
                                curr_x, curr_y = curr_pos
                                # Find closest previous obstacle
                                min_dist = float('inf')
                                for prev_pos in self._last_obstacle_positions:
                                    prev_x, prev_y = prev_pos
                                    dist = np.sqrt((curr_x - prev_x)**2 + (curr_y - prev_y)**2)
                                    min_dist = min(min_dist, dist)
                                
                                # If moved beyond threshold, consider it as moved
                                if min_dist > OBSTACLE_MOVEMENT_THRESHOLD:
                                    obstacles_moved = True
                                    break
                    
                    # Check if current path is blocked
                    is_blocked = False
                    if self._last_planned_path and len(obstacle_circles) > 0:
                        for x, y, r in obstacle_circles:
                            obs_center = np.array([x, y, 0.0])
                            obs = (obs_center, r)
                            if self._sampled_circle_intersects_obstacle(self._last_planned_path, obs, ROBOT_RADIUS):
                                is_blocked = True
                                break
                    
                    # Replan if no path, path is blocked, or obstacles moved
                    if self._last_planned_path is None or is_blocked or obstacles_moved:
                        if is_blocked:
                            print("! Path blocked by obstacle crate. Replanning...")
                        elif obstacles_moved:
                            print("! Obstacles moved. Replanning...")
                        
                        # Inflate obstacles with robot radius
                        inflated_obstacles = [(np.array([x, y, 0.0]), r + ROBOT_RADIUS) 
                                             for x, y, r in obstacle_circles]
                        
                        # Plan path
                        path = rrt_connect_plan(start_pos, goal_pos, inflated_obstacles, FIELD_BOUNDS)
                        
                        if path:
                            self._last_planned_path = path
                            # Update obstacle tracking
                            self._last_obstacle_positions = classification['obstacle_positions'].copy()
                            print(f"✓ Path planned: {len(path)} waypoints")
                        else:
                            print("✗ Path planning failed")
                            self._last_planned_path = None
                        
                        self._last_plan_time = now
                    else:
                        # Path is still valid
                        if frame_count % 60 == 0:
                            print("Path still valid - keeping it")
            
            # Visualize everything
            display = self.visualize_on_frame(frame, classification)
            
            # Draw path if available
            if self._last_planned_path:
                obstacle_circles = self.get_obstacle_circles(classification['obstacle_positions'])
                obstacles_for_viz = [(np.array([x, y, 0.0]), r + ROBOT_RADIUS) 
                                    for x, y, r in obstacle_circles]
                self.draw_path_on_frame(display, self._last_planned_path, obstacles_for_viz)
            
            # Draw detected markers
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(display, corners, ids)
            
            # Show frame
            cv2.imshow('Crate Obstacle Manager', display)
            
            # Print status periodically
            if frame_count % 60 == 0:
                print(f"\nFrame {frame_count}: Detected {len(all_detections)} markers")
                print(f"  Obstacles: {len(classification['obstacles'])}")
                print(f"  Interactable: {len(classification['interactable'])}")
                start_detected = "YES" if START_MARKER_ID in all_detections else "NO"
                print(f"  Start marker (ID {START_MARKER_ID}): {start_detected}")
                path_status = f"{len(self._last_planned_path)} waypoints" if self._last_planned_path else "No path"
                print(f"  Path: {path_status}")
            
            frame_count += 1
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord('p'):
                self.print_status(classification)
            elif key == ord('g'):
                print("\nEnter new goal coordinates (x y):")
                try:
                    x, y = map(float, input().split())
                    self.set_goal_position(x, y, 0.0)
                except:
                    print("Invalid input. Use format: x y (e.g., 1.5 1.0)")
        
        cap.release()
        cv2.destroyAllWindows()


# ============================================================================
# MAIN VISUALIZATION
# ============================================================================

def main():
    """Run crate obstacle manager with live camera visualization."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Crate Obstacle Manager - Visualize and classify crates for path planning'
    )
    parser.add_argument('--camera', type=int, default=1,
                       help='Camera device ID (default: 1)')
    parser.add_argument('--team', type=str, default='blue', choices=['blue', 'yellow'],
                       help='Team color (default: blue)')
    parser.add_argument('--intrinsics', type=str, default=DEFAULT_INTRINSICS,
                       help='Path to camera intrinsics JSON')
    parser.add_argument('--extrinsics', type=str, default=DEFAULT_EXTRINSICS,
                       help='Path to camera extrinsics JSON')
    parser.add_argument('--test', action='store_true',
                       help='Run test example instead of live camera')
    
    args = parser.parse_args()
    
    # Select team
    team = TeamColor.BLUE if args.team == 'blue' else TeamColor.YELLOW
    
    if args.test:
        # Run test example
        print("\n" + "="*60)
        print("CRATE OBSTACLE MANAGER - TEST EXAMPLE")
        print("="*60 + "\n")
        
        manager = CrateObstacleManager(team)
        
        # Simulate detected markers
        detected_markers = {
            'ids': [36, 36, 47, 47, 36],
            'markers': [
                {'id': 36, 'world_coords': [0.800, 0.100, 0.050]},  # Blue in pantry1
                {'id': 36, 'world_coords': [1.500, 0.100, 0.050]},  # Blue in pantry2
                {'id': 47, 'world_coords': [2.300, 0.100, 0.050]},  # Yellow in pantry3
                {'id': 47, 'world_coords': [1.200, 0.500, 0.050]},  # Yellow outside
                {'id': 36, 'world_coords': [0.500, 0.500, 0.050]},  # Blue outside
            ]
        }
        
        result = manager.process_detected_crates(detected_markers)
        manager.print_status(result)
        
        obstacle_circles = manager.get_obstacle_circles(result['obstacle_positions'])
        print("\nOBSTACLE CIRCLES FOR PATH PLANNING:")
        for x, y, r in obstacle_circles:
            print(f"  Circle @ ({x:.3f}, {y:.3f}) with radius {r:.3f}m")
        
        goal_pos = manager.get_goal_position()
        print(f"\nGOAL POSITION: ({goal_pos[0]:.3f}, {goal_pos[1]:.3f}, {goal_pos[2]:.3f})")
        print("\n✓ Test complete\n")
    else:
        # Run live visualization
        print("\n" + "="*60)
        print("CRATE OBSTACLE MANAGER - LIVE VISUALIZATION")
        print("="*60 + "\n")
        
        manager = CrateObstacleManager(team)
        
        try:
            manager.run_visualization(
                camera_id=args.camera,
                intrinsics_file=args.intrinsics,
                extrinsics_file=args.extrinsics
            )
        except KeyboardInterrupt:
            print("\n\n✓ Visualization stopped by user")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
