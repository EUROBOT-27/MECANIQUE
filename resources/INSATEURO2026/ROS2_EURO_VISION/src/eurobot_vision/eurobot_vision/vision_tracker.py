#!/usr/bin/env python3
"""
Full Pipeline - Eurobot 2026 ArUco Tracking System

This script integrates:
- ArUco marker detection and tracking
- Camera intrinsics and extrinsics calibration
- Kalman filtering for enemy robot (ID 13) tracking
- Real-time visualization of all detected markers
- Temporal smoothing for position estimates

Reference markers (IDs 20-23, 10cm):
- M22: (0.600, 0.600, 0.0)m
- M20: (0.600, 1.400, 0.0)m
- M21: (2.400, 1.400, 0.0)m
- M23: (2.400, 0.600, 0.0)m

Usage:
    python main.py --camera 1
"""

import cv2
import numpy as np
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import time

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from kalman_filter.tracker import MultiMarkerTracker, MarkerType, MarkerState
from occlusion_handler.handler import OcclusionHandler, DetectionQuality

# ============================================================================
# CONFIGURATION
# ============================================================================

# Fixed reference markers positions in map coordinates (meters)
REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}

# Marker sizes (meters)
REFERENCE_MARKER_SIZE = 0.10  # 10cm for reference markers (20-23)
OBJECT_MARKER_SIZE = 0.05     # 5cm for all other markers

# ArUco dictionary
ARUCO_DICT = cv2.aruco.DICT_4X4_50

# Enemy marker ID
ENEMY_MARKER_ID = 47

# Default calibration paths (relative to this file)
DEFAULT_INTRINSICS = "../config/camera_calibration.json"
DEFAULT_EXTRINSICS = "../config/camera_extrinsics.json"


# ============================================================================
# FULL PIPELINE TRACKER
# ============================================================================

class FullPipelineTracker:
    """
    Complete tracking system integrating ArUco detection, extrinsics calibration,
    and Kalman filtering for smooth enemy tracking.
    """
    
    def __init__(self, camera_id: int = 1, intrinsics_file: str = DEFAULT_INTRINSICS,
                 extrinsics_file: str = DEFAULT_EXTRINSICS,
                 enable_kalman: bool = True,
                 force_recompute_extrinsics: bool = False):
        """
        Initialize the full tracking pipeline.
        
        Args:
            camera_id: Camera device ID
            intrinsics_file: Path to camera intrinsics JSON
            extrinsics_file: Path to camera extrinsics JSON (optional)
            enable_kalman: Enable Kalman filtering for enemy tracking
            force_recompute_extrinsics: If True, ignore saved extrinsics and recompute
        """
        self.camera_id = camera_id
        self.intrinsics_file = intrinsics_file
        self.extrinsics_file = extrinsics_file
        self.enable_kalman = enable_kalman

        self.force_recompute_extrinsics = force_recompute_extrinsics
        
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
        
        # Try to load existing extrinsics (unless forced to recompute)
        if not force_recompute_extrinsics and Path(extrinsics_file).exists():
            self.load_extrinsics(extrinsics_file)
        elif force_recompute_extrinsics:
            print("! Force recompute enabled - will recalibrate extrinsics from reference markers")
        
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
        
        # Position smoothing for non-Kalman markers (temporal filtering)
        self.position_history: Dict[int, List[np.ndarray]] = {}
        self.history_size = 5
        
        # Statistics
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
    
    def load_intrinsics(self, intrinsics_file: str):
        """Load camera intrinsics from JSON file."""
        with open(intrinsics_file, 'r') as f:
            calib = json.load(f)
        
        self.camera_matrix = np.array(calib['camera_matrix'])
        self.dist_coeffs = np.array(calib['distortion_coefficients'])
        
        print(f"✓ Loaded intrinsics from {intrinsics_file}")
        print(f"  fx={self.camera_matrix[0,0]:.2f}, fy={self.camera_matrix[1,1]:.2f}")
        print(f"  cx={self.camera_matrix[0,2]:.2f}, cy={self.camera_matrix[1,2]:.2f}")
    
    def load_extrinsics(self, extrinsics_file: str):
        """Load camera extrinsics from JSON file."""
        try:
            with open(extrinsics_file, 'r') as f:
                extr = json.load(f)
            
            self.rvec_cam = np.array(extr['rvec'])
            self.tvec_cam = np.array(extr['tvec'])
            self.extrinsics_valid = True
            
            cam_pos = extr['camera_position_world']
            print(f"✓ Loaded extrinsics from {extrinsics_file}")
            print(f"  Camera position: ({cam_pos['x']:.3f}, {cam_pos['y']:.3f}, {cam_pos['z']:.3f})m")
        except Exception as e:
            print(f"! Could not load extrinsics: {e}")
            self.extrinsics_valid = False
    
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
    
    def compute_camera_extrinsics(self, corners_dict: Dict[int, np.ndarray], 
                                  ids_detected: List[int]) -> bool:
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
    
    def transform_to_world(self, rvec_obj: np.ndarray, 
                          tvec_obj: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
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
    
    def smooth_position(self, marker_id: int, position: np.ndarray) -> np.ndarray:
        """
        Apply temporal smoothing to reduce noise (for non-Kalman markers).
        
        Args:
            marker_id: Marker ID
            position: Current position (x, y, z)
            
        Returns:
            Smoothed position
        """
        if marker_id not in self.position_history:
            self.position_history[marker_id] = []
        
        self.position_history[marker_id].append(position)
        
        if len(self.position_history[marker_id]) > self.history_size:
            self.position_history[marker_id].pop(0)
        
        return np.mean(self.position_history[marker_id], axis=0)
    
    def extract_orientation_angle(self, rvec: np.ndarray) -> float:
        """
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
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[int, Dict]]:
        """
        Process a single frame: detect markers, compute poses, apply Kalman filter.
        
        Args:
            frame: Input frame
            
        Returns:
            (annotated_frame, detections_dict) where detections_dict maps marker_id to pose info
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
                    # Reference marker
                    color = (0, 255, 0)  # Green
                    label = f"REF {marker_id}"
                    
                    detections[marker_id] = {
                        'type': 'reference',
                        'camera_pos': tvecs[i][0],
                        'world_pos': REFERENCE_MARKERS[marker_id]
                    }
                else:
                    # Object marker - transform to world coordinates
                    if self.extrinsics_valid:
                        rvec_world, tvec_world = self.transform_to_world(rvecs[i], tvecs[i])
                        
                        if tvec_world is not None:
                            # Extract position and orientation
                            world_pos = tvec_world.flatten()
                            theta = self.extract_orientation_angle(rvec_world)
                            
                            # Add to Kalman filter detections (x, y, theta in 2D)
                            kalman_detections[marker_id] = (world_pos[0], world_pos[1], theta)
                            
                            # Store detection info
                            detections[marker_id] = {
                                'type': 'enemy' if marker_id == ENEMY_MARKER_ID else 'object',
                                'camera_pos': tvecs[i][0],
                                'world_pos': world_pos,
                                'theta': theta,
                                'raw': True  # Raw detection (not filtered)
                            }
                            
                            if marker_id == ENEMY_MARKER_ID:
                                color = (0, 0, 255)  # Red for enemy
                                label = f"ENEMY {marker_id}"
                            else:
                                color = (255, 0, 255)  # Magenta for other objects
                                label = f"OBJ {marker_id}"
                            
                            # Add position to label (will be updated with Kalman if enabled)
                            x, y, z = world_pos
                            label += f" | ({x:.3f}, {y:.3f}, {z:.3f})m"
                    else:
                        color = (128, 128, 128)  # Gray if no extrinsics
                        label = f"OBJ {marker_id} (no extrinsics)"
                
                # Draw label
                corner = corners[i][0][0]
                cv2.putText(display, label, (int(corner[0]), int(corner[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Update Kalman filter with all detections
            if self.enable_kalman and self.kalman_tracker is not None and kalman_detections:
                dt = 1.0 / max(self.fps, 30.0)  # Use measured FPS or default to 30
                tracked_states = self.kalman_tracker.update(kalman_detections, dt)
                
                # Update detection info with Kalman-filtered positions
                for marker_id, state in tracked_states.items():
                    if marker_id in detections:
                        detections[marker_id]['kalman_pos'] = (state.x, state.y, 0.0)  # 2D to 3D
                        detections[marker_id]['kalman_theta'] = state.theta
                        detections[marker_id]['confidence'] = state.confidence
                        detections[marker_id]['is_occluded'] = state.is_occluded
                        detections[marker_id]['filtered'] = True
                        
                        # Display Kalman position for enemy
                        if marker_id == ENEMY_MARKER_ID:
                            kf_label = f"ENEMY {marker_id} (KF) | ({state.x:.3f}, {state.y:.3f}) | conf={state.confidence:.2f}"
                            if state.is_occluded:
                                kf_label += " [OCCLUDED]"
                            
                            # Find corner position for display
                            for j, mid in enumerate(ids):
                                if mid == marker_id:
                                    corner = corners[j][0][0]
                                    cv2.putText(display, kf_label, (int(corner[0]), int(corner[1]) + 20),
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)  # Yellow for KF
                                    break
        
        # Update FPS
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            current_time = time.time()
            elapsed = current_time - self.last_fps_time
            self.fps = 30.0 / elapsed if elapsed > 0 else 30.0
            self.last_fps_time = current_time
        
        # Display status
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
        
        # Display Kalman filter statistics
        if self.enable_kalman and self.kalman_tracker is not None:
            summary = self.kalman_tracker.get_tracking_summary()
            stats_text = f"Tracked: {summary['tracked_markers']} | Enemy: {summary['enemy_markers']} | Occluded: {summary['occluded_markers']}"
            cv2.putText(display, stats_text, (10, status_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return display, detections
    
    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"✗ Cannot open camera {self.camera_id}")
            return
        
        # Set resolution to 1280x720
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Verify the resolution was set
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"\n✓ Camera opened (ID: {self.camera_id})")
        print(f"✓ Resolution: {actual_width}x{actual_height}")
        print(f"✓ Kalman filter: {'ENABLED' if self.enable_kalman else 'DISABLED'}")
        print("\nControls:")
        print("  ESC - Quit")
        print("  SPACE - Reset and recompute extrinsics")
        print("  'k' - Toggle Kalman filter")
        print("  'r' - Force recompute extrinsics now")
        print("\nWaiting for reference markers (20-23)...\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            display, detections = self.process_frame(frame)
            
            # Display
            cv2.imshow('Full Pipeline - Eurobot Tracking', display)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32 or key == ord('r'):  # SPACE or 'r' - Reset extrinsics
                self.extrinsics_valid = False
                self.rvec_cam = None
                self.tvec_cam = None
                self.position_history.clear()
                if self.kalman_tracker:
                    self.kalman_tracker.trackers.clear()
                print("\n! Extrinsics reset - recalibrating from reference markers...\n")
            elif key == ord('k'):  # Toggle Kalman
                self.enable_kalman = not self.enable_kalman
                print(f"\n! Kalman filter: {'ENABLED' if self.enable_kalman else 'DISABLED'}\n")
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(
        description='Full Pipeline - Eurobot ArUco Tracking with Kalman Filter',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--camera', type=int, default=1,
                       help='Camera device ID (default: 1)')
    parser.add_argument('--intrinsics', type=str, default=DEFAULT_INTRINSICS,
                       help='Path to camera intrinsics JSON')
    parser.add_argument('--extrinsics', type=str, default=DEFAULT_EXTRINSICS,
                       help='Path to camera extrinsics JSON')
    parser.add_argument('--no-kalman', action='store_true',
                       help='Disable Kalman filtering')
    parser.add_argument('--force-recompute', action='store_true',
                       help='Force recompute extrinsics (ignore saved file - use when camera moved)')
    
    args = parser.parse_args()
    
    # Check intrinsics file
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
            enable_kalman=not args.no_kalman,
            force_recompute_extrinsics=args.force_recompute
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
