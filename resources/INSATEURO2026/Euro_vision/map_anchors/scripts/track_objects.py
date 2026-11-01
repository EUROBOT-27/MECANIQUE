#!/usr/bin/env python3
"""
Object Tracking using ArUco Markers - Eurobot 2026

This script tracks objects with ArUco markers on a competition table.
It uses 4 fixed reference markers to compute camera extrinsics, then
reports the position of any detected object in real-world map coordinates.

Fixed reference markers (IDs 20-23) positions in map coordinates (meters):
- Marker 22: (0.600, 0.600, 0.0)
- Marker 20: (0.600, 1.400, 0.0)
- Marker 21: (2.400, 1.400, 0.0)
- Marker 23: (2.400, 0.600, 0.0)

Usage:
    python track_objects.py --camera 1 --calibration ../../camera_calibration_folder/calibration/camera_calibration.json
"""

import cv2
import numpy as np
import json
import argparse
import sys
from pathlib import Path

# Fixed reference markers positions in map coordinates (meters)
REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}

# Marker size in meters
MARKER_SIZE = 0.10  # 10cm (reference markers only)
OBJECT_MARKER_SIZE = 0.05  # 5cm (default for all object markers)

# Marker sizes for specific IDs (in meters)
# Reference markers (20-23) use MARKER_SIZE (10cm)
# All other markers use OBJECT_MARKER_SIZE (5cm) by default
MARKER_SIZES = {
    # Add custom sizes here if needed
}

# ArUco dictionary
ARUCO_DICT = cv2.aruco.DICT_4X4_50


class ObjectTracker:
    def __init__(self, calibration_file, camera_id=1):
        """
        Initialize object tracker.
        
        Args:
            calibration_file: Path to camera calibration JSON file
            camera_id: Camera device ID
        """
        self.camera_id = camera_id
        self.calibration_file = calibration_file
        
        # Load calibration
        self.load_calibration(calibration_file)
        
        # Setup ArUco detector
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # Camera extrinsics (computed from reference markers)
        self.rvec_cam = None
        self.tvec_cam = None
        self.extrinsics_valid = False
        
        # Position smoothing for denoising (temporal filtering)
        self.position_history = {}  # marker_id -> list of recent positions
        self.history_size = 5  # Number of frames to average
        
    def load_calibration(self, calibration_file):
        """Load camera calibration from JSON file."""
        with open(calibration_file, 'r') as f:
            calib = json.load(f)
        
        self.camera_matrix = np.array(calib['camera_matrix'])
        self.dist_coeffs = np.array(calib['distortion_coefficients'])
        
        print(f"✓ Loaded calibration from {calibration_file}")
        print(f"  Camera matrix: fx={self.camera_matrix[0,0]:.1f}, fy={self.camera_matrix[1,1]:.1f}")
        print(f"  Principal point: cx={self.camera_matrix[0,2]:.1f}, cy={self.camera_matrix[1,2]:.1f}")
        print(f"  Distortion: {self.dist_coeffs.ravel()}")
    
    def compute_camera_extrinsics(self, detected_ids, rvecs, tvecs):
        """
        Compute camera extrinsics using detected reference markers.
        
        Args:
            detected_ids: List of detected marker IDs
            rvecs: Rotation vectors from estimatePoseSingleMarkers
            tvecs: Translation vectors from estimatePoseSingleMarkers
            
        Returns:
            bool: True if extrinsics were computed successfully
        """
        # Find which reference markers are detected
        object_points = []
        image_points_3d = []
        
        for i, marker_id in enumerate(detected_ids):
            if marker_id in REFERENCE_MARKERS:
                # World position of this marker
                world_pos = REFERENCE_MARKERS[marker_id]
                object_points.append(world_pos)
                
                # Camera position of this marker (center of the marker)
                # The tvec from estimatePoseSingleMarkers is already the marker center
                image_points_3d.append(tvecs[i][0])
        
        if len(object_points) < 4:
            return False
        
        # Convert to numpy arrays
        object_points = np.array(object_points, dtype=np.float32)
        image_points_3d = np.array(image_points_3d, dtype=np.float32)
        
        # For solvePnP, we need 2D image points, but we already have 3D positions
        # from estimatePoseSingleMarkers. We need to use a different approach.
        # 
        # Actually, we need to use the marker corners for solvePnP!
        # Let me use a different strategy: use the detected markers to compute
        # the transform from camera to world coordinates.
        
        # Alternative: Compute camera position by inverting one marker's pose
        # and adjusting based on known world coordinates
        
        # For now, let's use marker 22 as the primary reference
        if 22 in detected_ids:
            idx = list(detected_ids).index(22)
            
            # This marker's pose in camera frame
            rvec_marker = rvecs[idx]
            tvec_marker = tvecs[idx]
            
            # Convert rotation vector to rotation matrix
            R_marker, _ = cv2.Rodrigues(rvec_marker)
            
            # Marker position in world frame
            marker_world = REFERENCE_MARKERS[22]
            
            # Camera position in marker frame is -R^T * t
            # Then transform to world frame
            R_marker_inv = R_marker.T
            t_cam_in_marker = -R_marker_inv @ tvec_marker[0]
            
            # Transform camera position to world frame
            # World coordinates = marker_world + R_world_marker @ t_cam_in_marker
            # But marker is flat on table, so rotation from marker to world is identity
            # (assuming markers have same orientation as world axes)
            
            # Actually, the marker frame has Z pointing up from marker
            # World frame has Z pointing up from table
            # So we need to account for marker orientation
            
            # Simple approach: Camera position in world = marker_world + offset
            # where offset is computed from tvec_marker
            
            # Let me use a more robust approach with solvePnP
            pass
        
        return False
    
    def compute_camera_extrinsics_robust(self, corners_dict, ids_detected, calibration_file=None):
        """
        Compute camera extrinsics using solvePnP with marker corners.
        
        Args:
            corners_dict: Dictionary mapping marker ID to corners
            ids_detected: List of detected marker IDs
            calibration_file: Path to calibration file (for saving extrinsics)
            
        Returns:
            bool: True if extrinsics computed successfully
        """
        # Collect 3D world points and 2D image points for all reference markers
        object_points = []
        image_points = []
        
        for marker_id in ids_detected:
            if marker_id not in REFERENCE_MARKERS:
                continue
            
            # Get marker center position in world coordinates
            marker_center = REFERENCE_MARKERS[marker_id]
            
            # Define the 4 corners of the marker in world coordinates
            # Assuming marker is axis-aligned with sides parallel to X and Y axes
            half_size = MARKER_SIZE / 2
            
            # OpenCV ArUco corners are ordered: top-left, top-right, bottom-right, bottom-left
            # when looking at the marker with the white square in top-left
            # Our world coords: X increases right, Y increases UP (not down)
            # So we need to match the image corners to world corners correctly
            # 270° rotation (working configuration)
            corners_3d = np.array([
                [marker_center[0] - half_size, marker_center[1] - half_size, 0],  # top-left
                [marker_center[0] + half_size, marker_center[1] - half_size, 0],  # top-right
                [marker_center[0] + half_size, marker_center[1] + half_size, 0],  # bottom-right
                [marker_center[0] - half_size, marker_center[1] + half_size, 0],  # bottom-left
            ], dtype=np.float32)
            
            # Get 2D corners from detection
            corners_2d = corners_dict[marker_id].reshape(-1, 2)
            
            # Add to lists
            object_points.extend(corners_3d)
            image_points.extend(corners_2d)
        
        if len(object_points) < 4:
            return False
        
        # Convert to numpy arrays
        object_points = np.array(object_points, dtype=np.float32)
        image_points = np.array(image_points, dtype=np.float32)
        
        # Solve PnP to get camera extrinsics
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
            
            # Print camera position in world coordinates
            R_cam, _ = cv2.Rodrigues(rvec)
            cam_pos_world = -R_cam.T @ tvec
            
            # Save extrinsics to file (if calibration_file path provided)
            if calibration_file:
                extrinsics_file = Path(calibration_file).parent / "camera_extrinsics.json"
            else:
                extrinsics_file = Path("camera_extrinsics.json")
            extrinsics_data = {
                "rvec": rvec.tolist(),
                "tvec": tvec.tolist(),
                "rotation_matrix": R_cam.tolist(),
                "camera_position_world": {
                    "x": float(cam_pos_world[0,0]),
                    "y": float(cam_pos_world[1,0]),
                    "z": float(cam_pos_world[2,0])
                },
                "reference_markers": {int(k): v.tolist() for k, v in REFERENCE_MARKERS.items()},
                "timestamp": str(Path(__file__).stat().st_mtime)
            }
            
            with open(extrinsics_file, 'w') as f:
                json.dump(extrinsics_data, f, indent=2)
            
            print(f"\n✓ Camera extrinsics computed!")
            print(f"  Camera position in world: X={cam_pos_world[0,0]:.3f}m, Y={cam_pos_world[1,0]:.3f}m, Z={cam_pos_world[2,0]:.3f}m")
            print(f"  Saved to: {extrinsics_file}")
            print(f"  Rotation matrix:\n{R_cam}")
            print(f"  Translation: {tvec.T}")
            
            return True
        
        return False
    
    def transform_to_world(self, rvec_obj, tvec_obj):
        """
        Transform object pose from camera coordinates to world coordinates.
        
        Args:
            rvec_obj: Object rotation vector in camera frame
            tvec_obj: Object translation vector in camera frame
            
        Returns:
            tuple: (rvec_world, tvec_world) or (None, None) if extrinsics not valid
        """
        if not self.extrinsics_valid:
            return None, None
        
        # Convert rotation vectors to matrices
        R_cam, _ = cv2.Rodrigues(self.rvec_cam)
        R_obj, _ = cv2.Rodrigues(rvec_obj)
        
        # The marker's position in camera frame (tvec_obj) is the location of
        # the marker center, regardless of the marker's orientation.
        # We need to transform this 3D point from camera coordinates to world coordinates.
        #
        # Camera extrinsics: P_camera = R_cam @ P_world + t_cam
        # Inverse: P_world = R_cam^T @ (P_camera - t_cam)
        
        # Object position in camera frame (from estimatePoseSingleMarkers)
        # This is already a 3D point in camera coordinates
        P_camera = tvec_obj[0].reshape(3, 1)
        
        # Transform to world frame
        R_cam_inv = R_cam.T
        P_world = R_cam_inv @ (P_camera - self.tvec_cam)
        
        # Object rotation in world frame
        R_obj_world = R_cam_inv @ R_obj
        rvec_world, _ = cv2.Rodrigues(R_obj_world)
        
        return rvec_world, P_world
    
    def smooth_position(self, marker_id, position):
        """
        Apply temporal smoothing to reduce noise in position estimates.
        
        Args:
            marker_id: ID of the marker
            position: Current position as (x, y, z)
            
        Returns:
            Smoothed position as numpy array
        """
        # Initialize history for this marker if needed
        if marker_id not in self.position_history:
            self.position_history[marker_id] = []
        
        # Add current position to history
        self.position_history[marker_id].append(position)
        
        # Keep only recent history
        if len(self.position_history[marker_id]) > self.history_size:
            self.position_history[marker_id].pop(0)
        
        # Return moving average
        return np.mean(self.position_history[marker_id], axis=0)
    
    def run(self):
        """Run the tracking loop."""
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"✗ Cannot open camera {self.camera_id}")
            return
        
        print(f"\n✓ Camera opened (ID: {self.camera_id})")
        print("\nControls:")
        print("  ESC - Quit")
        print("  SPACE - Reset extrinsics")
        print("\nLooking for reference markers (20, 21, 22, 23)...\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect ArUco markers
            corners, ids, rejected = self.detector.detectMarkers(frame)
            
            display = frame.copy()
            
            if ids is not None:
                ids = ids.flatten()
                
                # Estimate pose for each marker with correct size
                rvecs = []
                tvecs = []
                for i, marker_id in enumerate(ids):
                    # Use custom size if specified, otherwise use MARKER_SIZE for reference markers
                    # and OBJECT_MARKER_SIZE for all other markers
                    if marker_id in MARKER_SIZES:
                        marker_size = MARKER_SIZES[marker_id]
                    elif marker_id in REFERENCE_MARKERS:
                        marker_size = MARKER_SIZE
                    else:
                        marker_size = OBJECT_MARKER_SIZE
                    
                    rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                        [corners[i]], marker_size, self.camera_matrix, self.dist_coeffs
                    )
                    rvecs.append(rvec[0])
                    tvecs.append(tvec[0])
                rvecs = np.array(rvecs)
                tvecs = np.array(tvecs)
                
                # Create corners dictionary for extrinsics computation
                corners_dict = {ids[i]: corners[i] for i in range(len(ids))}
                
                # Compute or update camera extrinsics if we see reference markers
                ref_markers_detected = [mid for mid in ids if mid in REFERENCE_MARKERS]
                
                if len(ref_markers_detected) >= 4 and not self.extrinsics_valid:
                    self.compute_camera_extrinsics_robust(corners_dict, ids, self.calibration_file)
                
                # Draw all detected markers
                cv2.aruco.drawDetectedMarkers(display, corners, ids)
                
                # Process each detected marker
                for i, marker_id in enumerate(ids):
                    # Draw axis for visualization
                    cv2.drawFrameAxes(display, self.camera_matrix, self.dist_coeffs,
                                     rvecs[i], tvecs[i], MARKER_SIZE * 0.5)
                    
                    if marker_id in REFERENCE_MARKERS:
                        # This is a reference marker
                        color = (0, 255, 0)  # Green for reference
                        label = f"REF {marker_id}"
                    else:
                        # This is an object marker - compute world position
                        color = (0, 0, 255)  # Red for objects
                        label = f"OBJ {marker_id}"
                        
                        if self.extrinsics_valid:
                            # Transform to world coordinates
                            rvec_world, tvec_world = self.transform_to_world(rvecs[i], tvecs[i])
                            
                            if tvec_world is not None:
                                # Apply temporal smoothing
                                raw_pos = tvec_world.flatten()
                                smoothed_pos = self.smooth_position(marker_id, raw_pos)
                                x, y, z = smoothed_pos
                                
                                label += f" | World: ({x:.3f}, {y:.3f}, {z:.3f})m"
                                
                                # Debug: print camera frame position too
                                tx_cam, ty_cam, tz_cam = tvecs[i][0]
                                print(f"Object ID {marker_id}: Cam=({tx_cam:.3f}, {ty_cam:.3f}, {tz_cam:.3f}) -> World=({x:.3f}, {y:.3f}, {z:.3f})m")
                    
                    # Draw label
                    corner = corners[i][0][0]
                    cv2.putText(display, label, (int(corner[0]), int(corner[1]) - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Display status
                status_y = 30
                if self.extrinsics_valid:
                    status = f"TRACKING MODE | Ref markers: {len(ref_markers_detected)}/4"
                    status_color = (0, 255, 0)
                else:
                    status = f"CALIBRATING | Ref markers: {len(ref_markers_detected)}/4 (need 4)"
                    status_color = (0, 165, 255)
                
                cv2.putText(display, status, (10, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            else:
                # No markers detected
                cv2.putText(display, "No markers detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('Object Tracker', display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                self.extrinsics_valid = False
                self.rvec_cam = None
                self.tvec_cam = None
                self.position_history.clear()  # Clear smoothing history on reset
                print("\n! Extrinsics reset - recalibrating...\n")
        
        cap.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description='Track objects with ArUco markers in real-world coordinates',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera device ID (default: 0)')
    parser.add_argument('--calibration', type=str,
                       default='../../camera_calibration_folder/calibration/camera_calibration.json',
                       help='Path to camera calibration JSON file')
    
    args = parser.parse_args()
    
    # Check if calibration file exists
    if not Path(args.calibration).exists():
        print(f"✗ Calibration file not found: {args.calibration}")
        print("\nPlease run camera calibration first:")
        print("  cd ../../camera_calibration_folder")
        print("  python calibrate_camera.py --camera 0")
        return 1
    
    try:
        tracker = ObjectTracker(args.calibration, args.camera)
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
