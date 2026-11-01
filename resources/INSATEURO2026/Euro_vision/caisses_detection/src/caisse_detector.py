"""
Caisse de Noisettes Detector
Detects and localizes wooden boxes using ArUco markers on vinyl bands.
"""

import cv2
import numpy as np
import yaml
from typing import List, Dict, Tuple, Optional


class CaisseDetector:
    """Detects caisses de noisettes using ArUco markers (IDs 36, 47)."""
    
    def __init__(self, config_path: str, camera_matrix: np.ndarray, dist_coeffs: np.ndarray):
        """
        Initialize detector with configuration and camera calibration.
        
        Args:
            config_path: Path to caisse_config.yaml
            camera_matrix: Camera intrinsic matrix K
            dist_coeffs: Distortion coefficients D
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        
        # ArUco setup
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            getattr(cv2.aruco, self.config['aruco_detection']['dictionary'])
        )
        self.aruco_params = cv2.aruco.DetectorParameters()
        self._configure_aruco_params()
        
        # Marker specifications
        self.blue_marker_id = self.config['vinyl_band']['blue_zone']['aruco_id']
        self.yellow_marker_id = self.config['vinyl_band']['yellow_zone']['aruco_id']
        self.marker_size = self.config['vinyl_band']['blue_zone']['marker_size_mm'] / 1000.0  # Convert to meters
        
        # Box dimensions (in meters)
        self.box_length = self.config['box_specifications']['dimensions']['length_mm'] / 1000.0
        self.box_width = self.config['box_specifications']['dimensions']['width_mm'] / 1000.0
        self.box_height = self.config['box_specifications']['dimensions']['height_mm'] / 1000.0
        
        # Color ranges
        self._setup_color_ranges()
    
    def _configure_aruco_params(self):
        """Configure ArUco detection parameters from config."""
        params = self.config['aruco_detection']['detection_parameters']
        self.aruco_params.adaptiveThreshConstant = params['adaptiveThreshConstant']
        self.aruco_params.adaptiveThreshWinSizeMin = params['adaptiveThreshWinSizeMin']
        self.aruco_params.adaptiveThreshWinSizeMax = params['adaptiveThreshWinSizeMax']
        self.aruco_params.minMarkerPerimeterRate = params['minMarkerPerimeterRate']
        self.aruco_params.maxMarkerPerimeterRate = params['maxMarkerPerimeterRate']
    
    def _setup_color_ranges(self):
        """Setup HSV color ranges for team identification."""
        blue_cfg = self.config['color_detection']['blue_team']
        yellow_cfg = self.config['color_detection']['yellow_team']
        
        self.blue_lower = np.array([blue_cfg['h_min'], blue_cfg['s_min'], blue_cfg['v_min']])
        self.blue_upper = np.array([blue_cfg['h_max'], blue_cfg['s_max'], blue_cfg['v_max']])
        
        self.yellow_lower = np.array([yellow_cfg['h_min'], yellow_cfg['s_min'], yellow_cfg['v_min']])
        self.yellow_upper = np.array([yellow_cfg['h_max'], yellow_cfg['s_max'], yellow_cfg['v_max']])
    
    def detect_caisses(self, frame: np.ndarray, T_world_cam: np.ndarray) -> List[Dict]:
        """
        Detect all caisses in frame and return their world coordinates.
        
        Args:
            frame: Input image
            T_world_cam: 4x4 transform from camera to world frame
            
        Returns:
            List of detected caisses with position, orientation, and team
        """
        # Detect ArUco markers
        corners, ids, _ = cv2.aruco.detectMarkers(
            frame, self.aruco_dict, parameters=self.aruco_params
        )
        
        if ids is None:
            return []
        
        caisses = []
        ids = ids.flatten()
        
        for i, marker_id in enumerate(ids):
            # Only process caisse markers (36, 47)
            if marker_id not in [self.blue_marker_id, self.yellow_marker_id]:
                continue
            
            # Estimate pose
            rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                [corners[i]], self.marker_size, self.camera_matrix, self.dist_coeffs
            )
            
            # Transform to world coordinates
            world_position, world_orientation = self._transform_to_world(
                rvec[0][0], tvec[0][0], T_world_cam
            )
            
            # Determine team based on marker ID
            team = "BLUE" if marker_id == self.blue_marker_id else "YELLOW"
            
            # Detect visible face color for validation
            visible_color = self._detect_face_color(frame, corners[i][0])
            
            caisse = {
                'aruco_id': int(marker_id),
                'team': team,
                'position': {
                    'x': float(world_position[0]),
                    'y': float(world_position[1]),
                    'z': float(world_position[2]),
                    'theta': float(world_orientation)
                },
                'visible_face': visible_color,
                'confidence': self._calculate_confidence(corners[i][0]),
                'corners': corners[i][0].tolist()
            }
            
            caisses.append(caisse)
        
        return caisses
    
    def _transform_to_world(self, rvec: np.ndarray, tvec: np.ndarray, 
                           T_world_cam: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Transform marker pose from camera frame to world frame.
        
        Args:
            rvec: Rotation vector
            tvec: Translation vector
            T_world_cam: Camera to world transform
            
        Returns:
            (position, orientation) in world frame
        """
        # Convert rvec to rotation matrix
        R_cam_marker, _ = cv2.Rodrigues(rvec)
        
        # Build 4x4 transform
        T_cam_marker = np.eye(4)
        T_cam_marker[:3, :3] = R_cam_marker
        T_cam_marker[:3, 3] = tvec.flatten()
        
        # Transform to world
        T_world_marker = T_world_cam @ T_cam_marker
        
        # Extract position
        position = T_world_marker[:3, 3]
        
        # Extract yaw angle
        orientation = np.arctan2(T_world_marker[1, 0], T_world_marker[0, 0])
        
        return position, orientation
    
    def _detect_face_color(self, frame: np.ndarray, corners: np.ndarray) -> str:
        """
        Detect which colored face is visible (blue or yellow).
        
        Args:
            frame: Input image
            corners: Marker corners
            
        Returns:
            'blue', 'yellow', or 'unknown'
        """
        # Create mask around marker
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        corners_int = corners.astype(np.int32)
        
        # Expand region around marker
        expanded_corners = self._expand_region(corners_int, expansion=50)
        cv2.fillPoly(mask, [expanded_corners], 255)
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Apply mask
        hsv_masked = cv2.bitwise_and(hsv, hsv, mask=mask)
        
        # Detect blue and yellow
        blue_mask = cv2.inRange(hsv_masked, self.blue_lower, self.blue_upper)
        yellow_mask = cv2.inRange(hsv_masked, self.yellow_lower, self.yellow_upper)
        
        blue_area = cv2.countNonZero(blue_mask)
        yellow_area = cv2.countNonZero(yellow_mask)
        
        min_area = self.config['color_detection']['min_color_area']
        
        if blue_area > yellow_area and blue_area > min_area:
            return 'blue'
        elif yellow_area > blue_area and yellow_area > min_area:
            return 'yellow'
        else:
            return 'unknown'
    
    def _expand_region(self, corners: np.ndarray, expansion: int) -> np.ndarray:
        """Expand region around marker corners."""
        center = corners.mean(axis=0)
        expanded = []
        for corner in corners:
            direction = corner - center
            direction = direction / np.linalg.norm(direction)
            expanded.append(corner + direction * expansion)
        return np.array(expanded, dtype=np.int32)
    
    def _calculate_confidence(self, corners: np.ndarray) -> float:
        """
        Calculate detection confidence based on marker geometry.
        
        Args:
            corners: Marker corners
            
        Returns:
            Confidence score [0, 1]
        """
        # Check if corners form a square
        side_lengths = []
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            length = np.linalg.norm(p2 - p1)
            side_lengths.append(length)
        
        # Calculate variance in side lengths (should be low for square)
        mean_length = np.mean(side_lengths)
        variance = np.var(side_lengths)
        
        # Normalize confidence (lower variance = higher confidence)
        confidence = np.exp(-variance / (mean_length ** 2))
        
        return min(confidence, 1.0)
    
    def visualize_detections(self, frame: np.ndarray, caisses: List[Dict]) -> np.ndarray:
        """
        Draw detected caisses on frame.
        
        Args:
            frame: Input image
            caisses: List of detected caisses
            
        Returns:
            Annotated frame
        """
        vis_frame = frame.copy()
        
        for caisse in caisses:
            # Draw marker corners
            corners = np.array(caisse['corners'], dtype=np.int32)
            cv2.polylines(vis_frame, [corners], True, (0, 255, 0), 2)
            
            # Draw team color
            color = (255, 0, 0) if caisse['team'] == 'BLUE' else (0, 255, 255)
            center = corners.mean(axis=0).astype(int)
            cv2.circle(vis_frame, tuple(center), 5, color, -1)
            
            # Add text
            text = f"{caisse['team']} ID:{caisse['aruco_id']}"
            cv2.putText(vis_frame, text, tuple(center + [0, -20]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Add position
            pos_text = f"({caisse['position']['x']:.2f}, {caisse['position']['y']:.2f})"
            cv2.putText(vis_frame, pos_text, tuple(center + [0, 20]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return vis_frame
