#!/usr/bin/env python3
"""
Full Pipeline Example - Real-World Object Localization

This script uses YOUR calibrated camera parameters to detect ArUco markers
and return their real-world coordinates.

Features:
- Uses iPhone XR intrinsics from camera_calibration_folder/calibration/
- Uses computed extrinsics from map_anchors/scripts/calibration_pnp/ (latest)
- Detects and localizes: boxes (IDs 36,47,41), enemy robots (ID 30+)
- Returns world coordinates (x, y, z, yaw) in meters

Usage:
    python full_pipeline_example.py --camera 1 --use-extrinsics
    python full_pipeline_example.py --camera 1 --extrinsics-path ../scripts/calibration_pnp/
"""

import cv2
import numpy as np
import yaml
import json
import argparse
from pathlib import Path


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_camera_intrinsics(calib_path):
    """Load camera intrinsics from calibration JSON."""
    with open(calib_path, 'r') as f:
        calib = json.load(f)
    
    camera_matrix = np.array(calib['camera_matrix'], dtype=np.float32)
    dist_coeffs = np.array(calib['distortion_coefficients'][0], dtype=np.float32)
    
    return camera_matrix, dist_coeffs


def load_extrinsics(extrinsics_path):
    """Load pre-computed camera extrinsics."""
    with open(extrinsics_path, 'r') as f:
        extrinsics = yaml.safe_load(f)
    
    rvec = np.array(extrinsics['rvec'], dtype=np.float64).reshape(3, 1)
    tvec = np.array(extrinsics['tvec'], dtype=np.float64).reshape(3, 1)
    
    # Build transformation matrices
    R_world_cam, _ = cv2.Rodrigues(rvec)
    T_world_cam = np.eye(4)
    T_world_cam[:3, :3] = R_world_cam
    T_world_cam[:3, 3] = tvec.flatten()
    T_cam_world = np.linalg.inv(T_world_cam)
    
    camera_pos = extrinsics['camera_position_world']
    
    return T_world_cam, T_cam_world, camera_pos


def get_aruco_dict(dict_name):
    """Get ArUco dictionary from string name."""
    dict_map = {
        'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
        'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
        'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
        'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
    }
    return cv2.aruco.getPredefinedDictionary(dict_map.get(dict_name, cv2.aruco.DICT_4X4_50))


def detect_and_classify_markers(frame, aruco_dict):
    """
    Detect all ArUco markers and classify them.
    
    Returns:
        map_markers: Dict of map anchor markers (IDs 20-23)
        box_markers: Dict of box markers (IDs 36, 47, 41)
        enemy_markers: Dict of enemy robot markers (IDs 30+)
        other_markers: Dict of unknown/other markers
    """
    parameters = cv2.aruco.DetectorParameters()
    corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    
    map_markers = {}
    box_markers = {}
    enemy_markers = {}
    other_markers = {}
    
    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            if marker_id in [20, 21, 22, 23]:  # Eurobot 2026 map anchors
                map_markers[marker_id] = corners[i][0]
            elif marker_id in [36, 47, 41]:  # Caisses: blue, yellow, black
                box_markers[marker_id] = corners[i][0]
            elif marker_id >= 30:  # Enemy robots
                enemy_markers[marker_id] = corners[i][0]
            else:  # Unknown/other objects
                other_markers[marker_id] = corners[i][0]
    
    return map_markers, box_markers, enemy_markers, other_markers


def compute_camera_extrinsics(map_markers, marker_config, camera_matrix, dist_coeffs):
    """Compute camera extrinsics from map anchor markers."""
    if len(map_markers) < 4:
        return False, None, None
    
    object_points = []
    image_points = []
    for marker_id, corners in map_markers.items():
        marker_corners = marker_config['markers'][marker_id]['corners']
        for j in range(4):
            object_points.append(marker_corners[j])
            image_points.append(corners[j])
    
    object_points = np.array(object_points, dtype=np.float32)
    image_points = np.array(image_points, dtype=np.float32)
    
    success, rvec, tvec = cv2.solvePnP(
        object_points, image_points, camera_matrix, dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )
    
    if not success:
        return False, None, None
    
    # Build transformation matrix
    R, _ = cv2.Rodrigues(rvec)
    T_cam_world = np.eye(4)
    T_cam_world[:3, :3] = R
    T_cam_world[:3, 3] = tvec.flatten()
    T_world_cam = np.linalg.inv(T_cam_world)
    
    return True, rvec, tvec


def estimate_marker_pose(corners, marker_size, camera_matrix, dist_coeffs):
    """Estimate pose of a single marker."""
    # Define marker corners in marker's local frame
    half_size = marker_size / 2
    obj_points = np.array([
        [-half_size, -half_size, 0],
        [ half_size, -half_size, 0],
        [ half_size,  half_size, 0],
        [-half_size,  half_size, 0]
    ], dtype=np.float32)
    
    success, rvec, tvec = cv2.solvePnP(
        obj_points, corners, camera_matrix, dist_coeffs
    )
    
    return success, rvec, tvec


def transform_to_world(T_world_cam, rvec_marker, tvec_marker):
    """Transform marker pose from camera frame to world frame."""
    # Build marker transform in camera frame
    R_marker, _ = cv2.Rodrigues(rvec_marker)
    T_cam_marker = np.eye(4)
    T_cam_marker[:3, :3] = R_marker
    T_cam_marker[:3, 3] = tvec_marker.flatten()
    
    # Transform to world frame
    T_world_marker = T_world_cam @ T_cam_marker
    
    # Extract position and yaw
    position = T_world_marker[:3, 3]
    
    # Extract yaw angle (rotation around Z-axis)
    R = T_world_marker[:3, :3]
    yaw = np.arctan2(R[1, 0], R[0, 0])
    
    return position, yaw


def draw_world_coordinates(frame, text, position, color=(0, 255, 0)):
    """Draw world coordinates on frame."""
    cv2.putText(
        frame, text, position,
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
    )


def main():
    parser = argparse.ArgumentParser(description='Real-world object localization using calibrated camera')
    parser.add_argument('--camera', type=int, default=1, help='Camera index (default: 1 for iPhone XR via Camo)')
    parser.add_argument('--use-extrinsics', action='store_true', help='Use pre-computed extrinsics instead of live computation')
    parser.add_argument('--extrinsics-path', type=str, default=None, help='Path to extrinsics folder (default: calibration_pnp)')
    args = parser.parse_args()
    
    # Paths
    root_dir = Path(__file__).parent.parent.parent
    config_path = root_dir / 'map_anchors' / 'config' / 'marker_config.yaml'
    calib_path = root_dir / 'camera_calibration_folder' / 'calibration' / 'iphone_xr_720p.json'
    
    # Determine extrinsics path (default to Kabsch calibration)
    if args.extrinsics_path:
        extrinsics_dir = Path(args.extrinsics_path)
        if not extrinsics_dir.is_absolute():
            extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / extrinsics_dir
    else:
        # Try calibration_kabsch first, then fallback to calibration_pnp, then calibration_pnp_fixed
        extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / 'calibration_kabsch'
        if not (extrinsics_dir / 'extrinsics_metadata.yaml').exists():
            extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / 'calibration_pnp'
            if not (extrinsics_dir / 'extrinsics_metadata.yaml').exists():
                extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / 'calibration_pnp_fixed'
    
    extrinsics_path = extrinsics_dir / 'extrinsics_metadata.yaml'
    
    # Check files exist
    if not config_path.exists():
        print(f"❌ Error: Configuration file not found: {config_path}")
        return
    if not calib_path.exists():
        print(f"❌ Error: Camera calibration not found: {calib_path}")
        return
    
    # Load configuration
    config = load_config(config_path)
    
    # Load YOUR calibrated camera intrinsics (iPhone XR)
    print("📷 Loading iPhone XR camera intrinsics...")
    camera_matrix, dist_coeffs = load_camera_intrinsics(calib_path)
    print(f"   fx={camera_matrix[0,0]:.1f}, fy={camera_matrix[1,1]:.1f}, cx={camera_matrix[0,2]:.1f}, cy={camera_matrix[1,2]:.1f}")
    
    # Load pre-computed extrinsics if available and requested
    use_precomputed = False
    if args.use_extrinsics and extrinsics_path.exists():
        print(f"🎯 Loading pre-computed camera extrinsics from {extrinsics_dir.name}/...")
        T_world_cam_fixed, T_cam_world_fixed, camera_pos = load_extrinsics(extrinsics_path)
        print(f"   Camera position: ({camera_pos['x']:.3f}, {camera_pos['y']:.3f}, {camera_pos['z']:.3f}) m")
        use_precomputed = True
    elif args.use_extrinsics:
        print(f"⚠️  Extrinsics file not found: {extrinsics_path}")
        print("   Will compute extrinsics live from map markers")
        T_world_cam_fixed = None
    else:
        print("⚠️  Will compute extrinsics live from map markers")
        T_world_cam_fixed = None
    
    # ArUco dictionary
    aruco_dict = get_aruco_dict(config['aruco']['dictionary'])
    
    # Open camera
    print(f"📹 Opening camera {args.camera}...")
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"❌ Error: Could not open camera {args.camera}")
        return
    
    print("\n" + "="*60)
    print("🎯 REAL-WORLD OBJECT LOCALIZATION")
    print("="*60)
    print("Using YOUR calibrated camera parameters:")
    print(f"  • Camera: iPhone XR (index {args.camera})")
    print(f"  • Intrinsics: fx={camera_matrix[0,0]:.1f}, fy={camera_matrix[1,1]:.1f}")
    if use_precomputed:
        print(f"  • Extrinsics: Pre-computed (camera at {camera_pos['x']:.2f}, {camera_pos['y']:.2f}, {camera_pos['z']:.2f})")
    else:
        print(f"  • Extrinsics: Computed live from map markers 20-23")
    print("\nDetecting:")
    print("  🟦 Boxes (Blue=36, Yellow=47, Black=41)")
    print("  🔴 Enemy robots (ID 30+)")
    print("\nPress 'q' to quit")
    print("="*60)
    print()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect and classify markers
        map_markers, box_markers, enemy_markers, other_markers = detect_and_classify_markers(frame, aruco_dict)
        
        # Decide which extrinsics to use
        if use_precomputed:
            # Use pre-computed extrinsics
            T_world_cam = T_world_cam_fixed
            success = True
            extrinsics_source = "Pre-computed"
        elif len(map_markers) == 4:
            # Compute extrinsics live from map anchors
            success, rvec_cam, tvec_cam = compute_camera_extrinsics(
                map_markers, config, camera_matrix, dist_coeffs
            )
            
            if success:
                # Build world-to-camera transform
                R, _ = cv2.Rodrigues(rvec_cam)
                T_cam_world = np.eye(4)
                T_cam_world[:3, :3] = R
                T_cam_world[:3, 3] = tvec_cam.flatten()
                T_world_cam = np.linalg.inv(T_cam_world)
                extrinsics_source = "Live (4/4 markers)"
            else:
                extrinsics_source = "Failed"
        else:
            success = False
            extrinsics_source = f"Insufficient markers ({len(map_markers)}/4)"
        
        if success:
            # Draw map anchors (always show them for reference)
            for marker_id, corners in map_markers.items():
                center = corners.mean(axis=0).astype(int)
                cv2.circle(frame, tuple(center), 5, (0, 255, 0), -1)
                cv2.putText(
                    frame, f"MAP {marker_id}",
                    (center[0] + 10, center[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
                )
            
            # Process box markers
            for marker_id, corners in box_markers.items():
                # Estimate marker pose in camera frame
                marker_size = config['aruco']['marker_size']
                ok, rvec_box, tvec_box = estimate_marker_pose(
                    corners, marker_size, camera_matrix, dist_coeffs
                )
                
                if ok:
                    # Transform to world coordinates
                    position_world, yaw = transform_to_world(
                        T_world_cam, rvec_box, tvec_box
                    )
                    
                    # Print to console for logging
                    print(f"📦 Box {marker_id}: x={position_world[0]:.3f}m, y={position_world[1]:.3f}m, z={position_world[2]:.3f}m, yaw={np.degrees(yaw):.1f}°")
                    
                    # Draw on frame
                    center = corners.mean(axis=0).astype(int)
                    cv2.circle(frame, tuple(center), 5, (0, 165, 255), -1)
                    
                    text = f"Box {marker_id}: ({position_world[0]:.2f}, {position_world[1]:.2f}, {position_world[2]:.2f}m)"
                    draw_world_coordinates(frame, text, (center[0] + 10, center[1]), (0, 165, 255))
            
            # Process enemy markers
            for marker_id, corners in enemy_markers.items():
                # Estimate marker pose in camera frame
                marker_size = config['aruco']['marker_size']
                ok, rvec_enemy, tvec_enemy = estimate_marker_pose(
                    corners, marker_size, camera_matrix, dist_coeffs
                )
                
                if ok:
                    # Transform to world coordinates
                    position_world, yaw = transform_to_world(
                        T_world_cam, rvec_enemy, tvec_enemy
                    )
                    
                    # Print to console for logging
                    print(f"🔴 Enemy {marker_id}: x={position_world[0]:.3f}m, y={position_world[1]:.3f}m, z={position_world[2]:.3f}m, yaw={np.degrees(yaw):.1f}°")
                    
                    # Draw on frame
                    center = corners.mean(axis=0).astype(int)
                    cv2.circle(frame, tuple(center), 5, (0, 0, 255), -1)
                    
                    text = f"Enemy {marker_id}: ({position_world[0]:.2f}, {position_world[1]:.2f}, {np.degrees(yaw):.0f}°)"
                    draw_world_coordinates(frame, text, (center[0] + 10, center[1]), (0, 0, 255))
            
            # Process other/unknown markers
            for marker_id, corners in other_markers.items():
                # Estimate marker pose in camera frame
                marker_size = config['aruco']['marker_size']
                ok, rvec_other, tvec_other = estimate_marker_pose(
                    corners, marker_size, camera_matrix, dist_coeffs
                )
                
                if ok:
                    # Transform to world coordinates
                    position_world, yaw = transform_to_world(
                        T_world_cam, rvec_other, tvec_other
                    )
                    
                    # Print to console for logging
                    print(f"❓ Other {marker_id}: x={position_world[0]:.3f}m, y={position_world[1]:.3f}m, z={position_world[2]:.3f}m, yaw={np.degrees(yaw):.1f}°")
                    
                    # Draw on frame
                    center = corners.mean(axis=0).astype(int)
                    cv2.circle(frame, tuple(center), 5, (128, 128, 128), -1)
                    
                    text = f"Other {marker_id}: ({position_world[0]:.2f}, {position_world[1]:.2f})"
                    draw_world_coordinates(frame, text, (center[0] + 10, center[1]), (128, 128, 128))
            
            # Display status
            status = f"✓ {extrinsics_source}"
            color = (0, 255, 0)
        else:
            status = f"✗ {extrinsics_source}"
            color = (0, 0, 255)
        
        # Draw status
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw detection summary
        summary = f"Boxes: {len(box_markers)} | Enemy: {len(enemy_markers)} | Other: {len(other_markers)}"
        cv2.putText(frame, summary, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw camera info
        info = f"Camera: iPhone XR | Extrinsics: {extrinsics_source if success else 'N/A'}"
        cv2.putText(frame, info, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Show frame
        cv2.imshow('Real-World Object Localization', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
