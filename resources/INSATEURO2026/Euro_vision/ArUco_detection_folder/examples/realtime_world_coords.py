#!/usr/bin/env python3
"""
Simple Real-World Coordinate Detection
Uses current intrinsics and computes extrinsics on-demand.
Press SPACE to compute/reset extrinsics when all 4 reference markers are visible.

Uses the same PnP algorithm as full_pipeline/scripts/main/main.py
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, Optional, Tuple

# ArUco detection setup
ARUCO_DICT = cv2.aruco.DICT_4X4_50
aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

# Reference markers (map anchors) - EXACT positions from main.py
REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}

# Marker sizes (meters) - matching main.py
REFERENCE_MARKER_SIZE = 0.10  # 10cm for reference markers (20-23)
OBJECT_MARKER_SIZE = 0.05     # 5cm for all other markers


def load_camera_calibration(calib_file):
    """Load camera intrinsics from JSON file."""
    if not os.path.exists(calib_file):
        raise FileNotFoundError(f"Calibration file not found: {calib_file}")
    
    with open(calib_file, 'r') as f:
        data = json.load(f)
    
    camera_matrix = np.array(data['camera_matrix'])
    dist_coeffs = np.array(data['distortion_coefficients'])
    
    return camera_matrix, dist_coeffs


def compute_extrinsics(corners_dict, ids_list, camera_matrix, dist_coeffs):
    """
    Compute camera extrinsics using solvePnP with reference marker corners.
    Uses EXACT same algorithm as full_pipeline/scripts/main/main.py
    
    Args:
        corners_dict: Dictionary {marker_id: corners}
        ids_list: List of detected marker IDs
        camera_matrix: Camera intrinsic matrix
        dist_coeffs: Distortion coefficients
    
    Returns:
        tuple: (rvec, tvec, detected_refs) or (None, None, detected_refs) if failed
    """
    # Collect 3D world points and 2D image points for all reference markers
    object_points = []
    image_points = []
    detected_refs = []
    
    for marker_id in ids_list:
        if marker_id not in REFERENCE_MARKERS:
            continue
        
        detected_refs.append(marker_id)
        marker_center = REFERENCE_MARKERS[marker_id]
        half_size = REFERENCE_MARKER_SIZE / 2
        
        # Define 4 corners in world coordinates (270° rotation - working config from main.py)
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
        return None, None, detected_refs
    
    object_points = np.array(object_points, dtype=np.float32)
    image_points = np.array(image_points, dtype=np.float32)
    
    # Solve PnP - EXACT flags from main.py
    success, rvec, tvec = cv2.solvePnP(
        object_points,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )
    
    if success:
        return rvec, tvec, detected_refs
    
    return None, None, detected_refs


def transform_to_world(rvec_obj: np.ndarray, tvec_obj: np.ndarray, 
                      rvec_cam: np.ndarray, tvec_cam: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Transform object pose from camera coordinates to world coordinates.
    EXACT implementation from full_pipeline/scripts/main/main.py
    
    Args:
        rvec_obj: Object rotation vector in camera frame
        tvec_obj: Object translation vector in camera frame
        rvec_cam: Camera rotation vector (extrinsics)
        tvec_cam: Camera translation vector (extrinsics)
        
    Returns:
        (rvec_world, tvec_world) - object pose in world frame
    """
    R_cam, _ = cv2.Rodrigues(rvec_cam)
    R_obj, _ = cv2.Rodrigues(rvec_obj)
    
    # Transform position: P_world = R_cam^T @ (P_camera - t_cam)
    P_camera = tvec_obj[0].reshape(3, 1)
    R_cam_inv = R_cam.T
    P_world = R_cam_inv @ (P_camera - tvec_cam)
    
    # Transform rotation
    R_obj_world = R_cam_inv @ R_obj
    rvec_world, _ = cv2.Rodrigues(R_obj_world)
    
    return rvec_world, P_world


def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    calib_file = os.path.join(script_dir, '..', '..', 'camera_calibration_folder', 
                              'calibration', 'camera_calibration.json')
    
    # Load calibration
    print("Loading camera calibration...")
    try:
        camera_matrix, dist_coeffs = load_camera_calibration(calib_file)
        print(f"✓ Loaded: {calib_file}")
    except Exception as e:
        print(f"✗ Error loading calibration: {e}")
        return
    
    # Open camera
    print("\nOpening camera...")
    cap = cv2.VideoCapture(1, cv2.CAP_MSMF)
    
    if not cap.isOpened():
        print("Trying DSHOW backend...")
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("✗ Failed to open camera!")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Warm up camera
    print("Warming up camera...")
    for _ in range(30):
        cap.read()
    
    print("\n" + "="*60)
    print("REAL-TIME WORLD COORDINATE DETECTION")
    print("="*60)
    print("Controls:")
    print("  SPACE - Compute/reset extrinsics (need ref markers 20,21,22,23)")
    print("  ESC   - Quit")
    print("\nReference markers (10cm):")
    print("  M22: (0.600, 0.600)m")
    print("  M20: (0.600, 1.400)m")
    print("  M21: (2.400, 1.400)m")
    print("  M23: (2.400, 0.600)m")
    print("="*60 + "\n")
    
    extrinsics_computed = False
    rvec_cam = None
    tvec_cam = None
    
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        
        # Detect markers
        corners, ids, _ = detector.detectMarkers(frame)
        
        if ids is not None:
            ids_flat = ids.flatten()
            ids_list = ids_flat.tolist()
            corners_dict = {ids_list[i]: corners[i] for i in range(len(ids_list))}
            
            # Draw all detected markers
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            # Estimate pose for each marker with correct size (matching main.py)
            rvecs = []
            tvecs = []
            for i, marker_id in enumerate(ids_list):
                marker_size = REFERENCE_MARKER_SIZE if marker_id in REFERENCE_MARKERS else OBJECT_MARKER_SIZE
                
                # Use estimatePoseSingleMarkers - EXACT method from main.py
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [corners[i]], marker_size, camera_matrix, dist_coeffs
                )
                rvecs.append(rvec[0])
                tvecs.append(tvec[0])
            
            rvecs = np.array(rvecs)
            tvecs = np.array(tvecs)
            
            # Display info for each marker
            y_offset = 30
            for i, marker_id in enumerate(ids_list):
                # Draw axis for this marker
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs,
                                rvecs[i], tvecs[i], OBJECT_MARKER_SIZE * 0.5)
                
                # Camera frame coordinates
                cam_x, cam_y, cam_z = tvecs[i][0]
                
                info_text = f"ID {marker_id}: Cam({cam_x:.2f}, {cam_y:.2f}, {cam_z:.2f})"
                
                # If extrinsics available, show world coordinates
                if extrinsics_computed and rvec_cam is not None:
                    rvec_world, tvec_world = transform_to_world(rvecs[i], tvecs[i], rvec_cam, tvec_cam)
                    wx, wy, wz = tvec_world.flatten()
                    info_text += f" | World({wx:.2f}, {wy:.2f}, {wz:.2f})m"
                    
                    # Draw world coordinates on frame near marker
                    marker_corners = corners[i]
                    center = marker_corners[0].mean(axis=0).astype(int)
                    
                    # Color code: green for reference, blue for objects
                    color = (0, 255, 0) if marker_id in REFERENCE_MARKERS else (255, 0, 0)
                    cv2.putText(frame, f"({wx:.2f}, {wy:.2f})m", 
                               tuple(center), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                cv2.putText(frame, info_text, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 25
        
        # Status display
        status_y = frame.shape[0] - 60
        if extrinsics_computed:
            cv2.putText(frame, "Extrinsics: COMPUTED (World coords active)", 
                       (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Extrinsics: NOT SET (Press SPACE with ref markers 20,21,22,23)", 
                       (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show detected reference markers
        if ids is not None:
            ref_detected = [id for id in [20, 21, 22, 23] if id in ids_list]
            ref_text = f"Ref markers: {len(ref_detected)}/4 - {sorted(ref_detected)}"
            cv2.putText(frame, ref_text, (10, status_y + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.imshow('Real-World Coordinates', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            if ids is not None:
                rvec_cam, tvec_cam, detected = compute_extrinsics(
                    corners_dict, ids_list, camera_matrix, dist_coeffs
                )
                
                if rvec_cam is not None:
                    extrinsics_computed = True
                    
                    # Compute camera position in world frame (same as main.py)
                    R_cam, _ = cv2.Rodrigues(rvec_cam)
                    cam_pos_world = -R_cam.T @ tvec_cam
                    
                    print(f"\n✓ Extrinsics computed using markers: {sorted(detected)}")
                    print(f"  Camera position: ({cam_pos_world[0,0]:.3f}, {cam_pos_world[1,0]:.3f}, {cam_pos_world[2,0]:.3f})m")
                else:
                    print(f"\n✗ Failed to compute extrinsics. Detected ref markers: {sorted(detected)}")
                    print(f"   Need at least 4 points. Try showing all 4 markers: 20, 21, 22, 23")
            else:
                print("\n✗ No markers detected!")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nDone!")


if __name__ == "__main__":
    main()
