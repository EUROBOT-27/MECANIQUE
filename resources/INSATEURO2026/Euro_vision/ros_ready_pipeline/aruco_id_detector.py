#!/usr/bin/env python3

"""ArUco ID Detector - ArUco marker detection with positions

This script detects ArUco markers in camera frames and returns their IDs,
corner positions, and center coordinates.
Uses camera calibration parameters for undistortion.

Usage:
    python aruco_id_detector.py --camera 1
"""

import cv2
import numpy as np
import json
import argparse
import sys
from pathlib import Path
from typing import List, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

ARUCO_DICT = cv2.aruco.DICT_4X4_50
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"
MARKER_SIZE = 0.10  # ArUco marker size in meters (10cm)

# ============================================================================
# ARUCO ID DETECTOR
# ============================================================================

class ArucoIDDetector:
    """ArUco marker detector that returns IDs with real-world coordinates."""
    
    def __init__(self, camera_id: int = 1, intrinsics_file: str = DEFAULT_INTRINSICS,
                 extrinsics_file: str = DEFAULT_EXTRINSICS, marker_size: float = MARKER_SIZE):
        """
        Initialize the ArUco ID detector.
        
        Args:
            camera_id: Camera device ID
            intrinsics_file: Path to camera intrinsics JSON file
            extrinsics_file: Path to camera extrinsics JSON file
            marker_size: Physical size of ArUco markers in meters
        """
        self.camera_id = camera_id
        self.intrinsics_file = intrinsics_file
        self.extrinsics_file = extrinsics_file
        self.marker_size = marker_size
        
        # Load camera intrinsics
        self.camera_matrix = None
        self.dist_coeffs = None
        self.load_intrinsics(intrinsics_file)
        
        # Load camera extrinsics
        self.rvec_cam = None
        self.tvec_cam = None
        self.extrinsics_valid = False
        self.load_extrinsics(extrinsics_file)
        
        # Setup ArUco detector
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
    
    def load_intrinsics(self, intrinsics_file: str) -> bool:
        """
        Load camera intrinsics from JSON file.
        
        Args:
            intrinsics_file: Path to camera intrinsics JSON
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(intrinsics_file, 'r') as f:
                data = json.load(f)
            self.camera_matrix = np.array(data['camera_matrix'])
            self.dist_coeffs = np.array(data['distortion_coefficients'])
            print(f"✓ Loaded camera intrinsics from {intrinsics_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to load intrinsics: {e}")
            self.camera_matrix = None
            self.dist_coeffs = None
            return False
    
    def load_extrinsics(self, extrinsics_file: str) -> bool:
        """
        Load camera extrinsics from JSON file.
        
        Args:
            extrinsics_file: Path to camera extrinsics JSON
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(extrinsics_file, 'r') as f:
                data = json.load(f)
            self.rvec_cam = np.array(data['rvec'])
            self.tvec_cam = np.array(data['tvec'])
            self.extrinsics_valid = True
            print(f"✓ Loaded camera extrinsics from {extrinsics_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to load extrinsics: {e}")
            print(f"  World coordinates will not be available")
            self.rvec_cam = None
            self.tvec_cam = None
            self.extrinsics_valid = False
            return False
    
    def transform_to_world(self, rvec_obj: np.ndarray, tvec_obj: np.ndarray) -> Optional[np.ndarray]:
        """
        Transform object pose from camera coordinates to world coordinates.
        
        Args:
            rvec_obj: Object rotation vector in camera frame
            tvec_obj: Object translation vector in camera frame
            
        Returns:
            World position (x, y, z) as numpy array, or None if extrinsics invalid
        """
        if not self.extrinsics_valid:
            return None
        
        # Convert rotation vectors to matrices
        R_cam, _ = cv2.Rodrigues(self.rvec_cam)
        
        # Transform position: P_world = R_cam^T @ (P_camera - t_cam)
        P_camera = tvec_obj[0].reshape(3, 1)
        R_cam_inv = R_cam.T
        P_world = R_cam_inv @ (P_camera - self.tvec_cam)
        
        return P_world.flatten()
    
    def detect_aruco_ids(self, frame: np.ndarray) -> dict:
        """
        Detect ArUco markers in frame and return their IDs with real-world coordinates.
        
        Args:
            frame: Input image frame
            
        Returns:
            Dictionary with marker data:
            {
                'ids': [list of marker IDs],
                'markers': [
                    {
                        'id': marker_id,
                        'world_coords': [x, y, z]  # meters, None if extrinsics unavailable
                    },
                    ...
                ]
            }
        """
        # Undistort frame if calibration is available
        if self.camera_matrix is not None and self.dist_coeffs is not None:
            frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs)
        
        # Detect ArUco markers
        corners, ids, rejected = self.detector.detectMarkers(frame)
        
        result = {
            'ids': [],
            'markers': []
        }
        
        # Process detected markers
        if ids is not None:
            result['ids'] = ids.flatten().tolist()
            
            # Estimate pose for each marker
            if self.camera_matrix is not None:
                # Define 3D marker corners in marker coordinate system
                half_size = self.marker_size / 2.0
                obj_points = np.array([
                    [-half_size, half_size, 0],
                    [half_size, half_size, 0],
                    [half_size, -half_size, 0],
                    [-half_size, -half_size, 0]
                ], dtype=np.float32)
                
                for i, marker_id in enumerate(result['ids']):
                    # Solve PnP to get marker pose in camera frame
                    success, rvec, tvec = cv2.solvePnP(
                        obj_points,
                        corners[i][0],
                        self.camera_matrix,
                        self.dist_coeffs,
                        flags=cv2.SOLVEPNP_IPPE_SQUARE
                    )
                    
                    world_coords = None
                    if success and self.extrinsics_valid:
                        # Transform to world coordinates
                        world_pos = self.transform_to_world(rvec, tvec)
                        if world_pos is not None:
                            world_coords = [float(world_pos[0]), float(world_pos[1]), float(world_pos[2])]
                    
                    marker_data = {
                        'id': int(marker_id),
                        'world_coords': world_coords
                    }
                    result['markers'].append(marker_data)
            else:
                # No intrinsics, can't compute world coordinates
                for marker_id in result['ids']:
                    marker_data = {
                        'id': int(marker_id),
                        'world_coords': None
                    }
                    result['markers'].append(marker_data)
        
        return result
    
    def detect_and_visualize(self, frame: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Detect ArUco markers and draw them on the frame with world coordinates.
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (annotated frame, marker data dict)
        """
        # Undistort frame if calibration is available
        if self.camera_matrix is not None and self.dist_coeffs is not None:
            frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs)
        
        # Detect ArUco markers
        corners, ids, rejected = self.detector.detectMarkers(frame)
        
        # Draw detected markers
        display = frame.copy()
        
        result = {
            'ids': [],
            'markers': []
        }
        
        if ids is not None:
            result['ids'] = ids.flatten().tolist()
            cv2.aruco.drawDetectedMarkers(display, corners, ids)
            
            # Estimate pose for each marker
            if self.camera_matrix is not None:
                # Define 3D marker corners
                half_size = self.marker_size / 2.0
                obj_points = np.array([
                    [-half_size, half_size, 0],
                    [half_size, half_size, 0],
                    [half_size, -half_size, 0],
                    [-half_size, -half_size, 0]
                ], dtype=np.float32)
                
                for i, marker_id in enumerate(result['ids']):
                    # Get pixel coordinates
                    corner_points = corners[i][0]
                    center_x = float(np.mean(corner_points[:, 0]))
                    center_y = float(np.mean(corner_points[:, 1]))
                    
                    # Solve PnP to get marker pose in camera frame
                    success, rvec, tvec = cv2.solvePnP(
                        obj_points,
                        corner_points,
                        self.camera_matrix,
                        self.dist_coeffs,
                        flags=cv2.SOLVEPNP_IPPE_SQUARE
                    )
                    
                    world_coords = None
                    if success and self.extrinsics_valid:
                        # Transform to world coordinates
                        world_pos = self.transform_to_world(rvec, tvec)
                        if world_pos is not None:
                            world_coords = [float(world_pos[0]), float(world_pos[1]), float(world_pos[2])]
                    
                    marker_data = {
                        'id': int(marker_id),
                        'world_coords': world_coords
                    }
                    result['markers'].append(marker_data)
                    
                    # Draw ID label
                    corner = corner_points[0]
                    cv2.putText(display, f"ID: {marker_id}", 
                               (int(corner[0]), int(corner[1]) - 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Draw center point
                    cv2.circle(display, (int(center_x), int(center_y)), 5, (0, 0, 255), -1)
                    
                    # Draw world coordinates if available
                    if world_coords is not None:
                        coord_text = f"World: ({world_coords[0]:.3f}, {world_coords[1]:.3f}, {world_coords[2]:.3f})"
                        cv2.putText(display, coord_text, 
                                   (int(center_x) + 10, int(center_y)),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                    else:
                        # Show pixel coordinates instead
                        cv2.putText(display, f"Pixel: ({center_x:.1f}, {center_y:.1f})", 
                                   (int(center_x) + 10, int(center_y)),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            else:
                # No intrinsics, can't compute coordinates
                for marker_id in result['ids']:
                    result['markers'].append({
                        'id': int(marker_id),
                        'world_coords': None
                    })
        
        # Display count and calibration status
        cv2.putText(display, f"Detected: {len(result['ids'])} markers", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        status_color = (0, 255, 0) if self.extrinsics_valid else (0, 0, 255)
        status_text = "World Coords: OK" if self.extrinsics_valid else "World Coords: N/A"
        cv2.putText(display, status_text, 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        return display, result
    
    def run(self):
        """Run the detector in continuous mode with live video feed."""
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print(f"✗ Cannot open camera {self.camera_id}")
            return
        
        print(f"\n✓ Camera opened (ID: {self.camera_id})")
        print("\nControls:")
        print("  ESC - Quit")
        print("  's' - Save current frame")
        print("\nDetecting ArUco markers...\n")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect and visualize
            display, marker_data = self.detect_and_visualize(frame)
            
            # Print detected marker data
            if frame_count % 30 == 0:  # Print every 30 frames
                print(f"\n=== Frame {frame_count} ===")
                print(f"Detected IDs: {marker_data['ids']}")
                for marker in marker_data['markers']:
                    if marker['world_coords'] is not None:
                        wx, wy, wz = marker['world_coords']
                        print(f"  ID {marker['id']}: World=({wx:.3f}, {wy:.3f}, {wz:.3f}) m")
                    else:
                        print(f"  ID {marker['id']}: World coords unavailable")
            
            frame_count += 1
            
            # Show frame
            cv2.imshow('ArUco ID Detector', display)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord('s'):
                filename = f"aruco_detection_{frame_count}.jpg"
                cv2.imwrite(filename, display)
                print(f"✓ Saved frame to {filename}")
        
        cap.release()
        cv2.destroyAllWindows()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='ArUco ID Detector - Detect ArUco markers and return world coordinates',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--camera', type=int, default=1,
                       help='Camera device ID (default: 1)')
    parser.add_argument('--intrinsics', type=str, default=DEFAULT_INTRINSICS,
                       help='Path to camera intrinsics JSON')
    parser.add_argument('--extrinsics', type=str, default=DEFAULT_EXTRINSICS,
                       help='Path to camera extrinsics JSON')
    parser.add_argument('--marker-size', type=float, default=MARKER_SIZE,
                       help='Physical size of ArUco markers in meters (default: 0.10)')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not Path(args.intrinsics).exists():
        print(f"⚠ Warning: Intrinsics file not found: {args.intrinsics}")
        print("  Detector will work without undistortion.")
    
    if not Path(args.extrinsics).exists():
        print(f"⚠ Warning: Extrinsics file not found: {args.extrinsics}")
        print("  World coordinates will not be available.")
    
    try:
        detector = ArucoIDDetector(
            camera_id=args.camera,
            intrinsics_file=args.intrinsics,
            extrinsics_file=args.extrinsics,
            marker_size=args.marker_size
        )
        detector.run()
    except KeyboardInterrupt:
        print("\n\n✓ Detection stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
