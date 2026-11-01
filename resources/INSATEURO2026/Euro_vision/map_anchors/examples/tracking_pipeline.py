#!/usr/bin/env python3
"""
Real-World Object Tracking Pipeline with Kalman Filtering

This script integrates the existing Kalman filter module with the ArUco detection
pipeline to provide smooth tracking of enemy robots, boxes, and other objects.

Features:
- Uses YOUR calibrated camera parameters
- Integrates kalman_filter module for smooth tracking
- Tracks ANY moving marker ID (enemies, boxes, etc.)
- Predicts positions during occlusion
- Velocity estimation with arrow visualization

Usage:
    python tracking_pipeline.py --camera 1 --use-extrinsics
    python tracking_pipeline.py --camera 1 --use-extrinsics --track-all
"""

import cv2
import numpy as np
import yaml
import json
import argparse
from pathlib import Path
import sys

# Add kalman_filter module to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir / 'kalman_filter'))

from src.kalman_filter.tracker import MultiMarkerTracker, MarkerType, MarkerState


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
    """Detect all ArUco markers and return with corners."""
    parameters = cv2.aruco.DetectorParameters()
    corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    
    detections = {}
    corners_dict = {}
    
    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            detections[marker_id] = corners[i][0]
            corners_dict[marker_id] = corners[i][0]
    
    return detections, corners_dict


def compute_camera_extrinsics(map_markers, marker_config, camera_matrix, dist_coeffs):
    """Compute camera extrinsics from map anchor markers."""
    if len(map_markers) < 4:
        return False, None, None
    
    object_points = []
    image_points = []
    
    for marker_id, corners in map_markers.items():
        if marker_id not in marker_config['markers']:
            continue
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
    
    return True, T_world_cam, T_cam_world


def estimate_marker_pose(corners, marker_size, camera_matrix, dist_coeffs):
    """Estimate pose of a single marker."""
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
    R_marker, _ = cv2.Rodrigues(rvec_marker)
    T_cam_marker = np.eye(4)
    T_cam_marker[:3, :3] = R_marker
    T_cam_marker[:3, 3] = tvec_marker.flatten()
    
    T_world_marker = T_world_cam @ T_cam_marker
    
    position = T_world_marker[:3, 3]
    
    # Extract yaw angle
    R = T_world_marker[:3, :3]
    yaw = np.arctan2(R[1, 0], R[0, 0])
    
    return position, yaw


def draw_tracked_marker(frame, marker_id, state, corners, color):
    """Draw tracked marker with Kalman state information."""
    if corners is not None:
        center = corners.mean(axis=0).astype(int)
    else:
        # No visual detection, skip drawing on frame
        return
    
    # Determine marker type symbol
    if state.marker_type == MarkerType.MAP:
        symbol = "🗺️"
        label = f"MAP {marker_id}"
    elif state.marker_type == MarkerType.CAISSE:
        symbol = "📦"
        label = f"Box {marker_id}"
    elif state.marker_type == MarkerType.ENEMY:
        symbol = "🔴"
        label = f"Enemy {marker_id}"
    else:
        symbol = "❓"
        label = f"ID {marker_id}"
    
    # Draw marker center
    if state.is_occluded:
        # Predicted position (dashed circle)
        cv2.circle(frame, tuple(center), 8, color, 1)
        cv2.circle(frame, tuple(center), 4, color, -1)
        label += " [PRED]"
    else:
        # Detected position (solid circle)
        cv2.circle(frame, tuple(center), 5, color, -1)
    
    # Draw position and confidence
    cv2.putText(
        frame, label,
        (center[0] + 10, center[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
    )
    
    # Draw world coordinates
    coord_text = f"({state.x:.2f}, {state.y:.2f})"
    cv2.putText(
        frame, coord_text,
        (center[0] + 10, center[1] + 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
    )
    
    # Calculate and draw velocity vector
    # Get velocity from state (vx, vy from Kalman filter)
    # Note: We need to access the tracker's internal state for velocities
    # For now, we'll estimate velocity from position changes
    
    # Draw orientation arrow
    arrow_length = 30
    end_x = int(center[0] + arrow_length * np.cos(state.theta))
    end_y = int(center[1] + arrow_length * np.sin(state.theta))
    cv2.arrowedLine(frame, tuple(center), (end_x, end_y), color, 2, tipLength=0.3)


def main():
    parser = argparse.ArgumentParser(description='Real-world object tracking with Kalman filtering')
    parser.add_argument('--camera', type=int, default=1, help='Camera index')
    parser.add_argument('--use-extrinsics', action='store_true', help='Use pre-computed extrinsics')
    parser.add_argument('--extrinsics-path', type=str, default=None, help='Path to extrinsics folder')
    parser.add_argument('--track-all', action='store_true', help='Track ALL detected markers (not just enemies)')
    args = parser.parse_args()
    
    # Paths
    root_dir = Path(__file__).parent.parent.parent
    config_path = root_dir / 'map_anchors' / 'config' / 'marker_config.yaml'
    calib_path = root_dir / 'camera_calibration_folder' / 'calibration' / 'iphone_xr_720p.json'
    
    # Determine extrinsics path
    if args.extrinsics_path:
        extrinsics_dir = Path(args.extrinsics_path)
        if not extrinsics_dir.is_absolute():
            extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / extrinsics_dir
    else:
        extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / 'calibration_pnp_fixed'
        if not (extrinsics_dir / 'extrinsics_metadata.yaml').exists():
            extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / 'calibration_pnp'
            if not (extrinsics_dir / 'extrinsics_metadata.yaml').exists():
                extrinsics_dir = root_dir / 'map_anchors' / 'scripts' / 'calibration_kabsch'
    
    extrinsics_path = extrinsics_dir / 'extrinsics_metadata.yaml'
    
    # Load configuration
    config = load_config(config_path)
    camera_matrix, dist_coeffs = load_camera_intrinsics(calib_path)
    
    print("📷 Loading iPhone XR camera intrinsics...")
    print(f"   fx={camera_matrix[0,0]:.1f}, fy={camera_matrix[1,1]:.1f}")
    
    # Load pre-computed extrinsics if available
    use_precomputed = False
    if args.use_extrinsics and extrinsics_path.exists():
        print(f"🎯 Loading extrinsics from {extrinsics_dir.name}/...")
        T_world_cam_fixed, T_cam_world_fixed, camera_pos = load_extrinsics(extrinsics_path)
        print(f"   Camera: ({camera_pos['x']:.3f}, {camera_pos['y']:.3f}, {camera_pos['z']:.3f}) m")
        use_precomputed = True
    else:
        T_world_cam_fixed = None
        print("⚠️  Will compute extrinsics live from map markers")
    
    # Initialize Kalman tracker
    print("🔮 Initializing Kalman filter tracker...")
    tracker = MultiMarkerTracker(
        process_noise=0.01,
        measurement_noise=0.1,
        max_frames_without_detection=30
    )
    
    # ArUco dictionary
    aruco_dict = get_aruco_dict(config['aruco']['dictionary'])
    
    # Open camera
    print(f"📹 Opening camera {args.camera}...")
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"❌ Error: Could not open camera {args.camera}")
        return
    
    print("\n" + "="*70)
    print("🎯 REAL-WORLD OBJECT TRACKING WITH KALMAN FILTERING")
    print("="*70)
    print("Tracking mode:", "ALL MARKERS" if args.track_all else "ENEMIES & BOXES ONLY")
    print("\nFeatures:")
    print("  • Kalman filter smoothing for position/velocity estimation")
    print("  • Prediction during occlusion (up to 30 frames)")
    print("  • Multi-object tracking with ID persistence")
    print("\nControls:")
    print("  • Press 'q' to quit")
    print("  • Press 'r' to reset all tracks")
    print("  • Press 's' to show tracking summary")
    print("="*70)
    print()
    
    import time
    last_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Calculate dt
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Detect markers
        all_detections, corners_dict = detect_and_classify_markers(frame, aruco_dict)
        
        # Separate map markers for extrinsics
        map_markers = {mid: corners for mid, corners in all_detections.items() if 20 <= mid <= 23}
        
        # Determine extrinsics
        if use_precomputed:
            T_world_cam = T_world_cam_fixed
            success = True
            extrinsics_source = "Pre-computed"
        elif len(map_markers) == 4:
            success, T_world_cam, _ = compute_camera_extrinsics(
                map_markers, config, camera_matrix, dist_coeffs
            )
            extrinsics_source = "Live (4/4)" if success else "Failed"
        else:
            success = False
            extrinsics_source = f"Insufficient ({len(map_markers)}/4)"
        
        if success:
            # Convert detections to world coordinates
            world_detections = {}
            marker_size = config['aruco']['marker_size']
            
            for marker_id, corners in all_detections.items():
                # Skip map markers if not tracking all
                if not args.track_all and marker_id in [20, 21, 22, 23]:
                    continue
                
                ok, rvec, tvec = estimate_marker_pose(corners, marker_size, camera_matrix, dist_coeffs)
                if ok:
                    position, yaw = transform_to_world(T_world_cam, rvec, tvec)
                    # Store as (x, y, theta) for Kalman filter
                    world_detections[marker_id] = (position[0], position[1], yaw)
            
            # Update Kalman tracker
            tracked_states = tracker.update(world_detections, dt)
            
            # Draw map markers (for reference)
            for marker_id, corners in map_markers.items():
                center = corners.mean(axis=0).astype(int)
                cv2.circle(frame, tuple(center), 4, (0, 255, 0), -1)
                cv2.putText(frame, f"MAP {marker_id}", (center[0] + 8, center[1]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Draw tracked markers
            for marker_id, state in tracked_states.items():
                # Get color based on marker type
                if state.marker_type == MarkerType.MAP:
                    color = (0, 255, 0)  # Green
                elif state.marker_type == MarkerType.CAISSE:
                    color = (0, 165, 255)  # Orange
                elif state.marker_type == MarkerType.ENEMY:
                    color = (0, 0, 255)  # Red
                else:
                    color = (128, 128, 128)  # Gray
                
                # Get corners if marker was detected this frame
                corners = corners_dict.get(marker_id)
                
                draw_tracked_marker(frame, marker_id, state, corners, color)
                
                # Print state to console
                status = "PREDICTED" if state.is_occluded else "TRACKED"
                print(f"  {state.marker_type.value.upper()} {marker_id}: "
                      f"x={state.x:.3f}m, y={state.y:.3f}m, θ={np.degrees(state.theta):.1f}°, "
                      f"conf={state.confidence:.2f}, {status}")
            
            # Status overlay
            status_text = f"✓ {extrinsics_source} | Tracked: {len(tracked_states)}"
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            status_text = f"✗ {extrinsics_source}"
            cv2.putText(frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # FPS overlay
        fps_text = f"FPS: {1/dt:.1f}" if dt > 0 else "FPS: --"
        cv2.putText(frame, fps_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow('Kalman Filter Tracking Pipeline', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            tracker = MultiMarkerTracker(
                process_noise=0.01,
                measurement_noise=0.1,
                max_frames_without_detection=30
            )
            print("\n🔄 Reset all tracks\n")
        elif key == ord('s'):
            summary = tracker.get_tracking_summary()
            print("\n" + "="*50)
            print("📊 TRACKING SUMMARY")
            print("="*50)
            for key, value in summary.items():
                print(f"  {key}: {value}")
            print("="*50 + "\n")
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Final summary
    print("\n" + "="*70)
    print("📊 FINAL TRACKING SUMMARY")
    print("="*70)
    summary = tracker.get_tracking_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print("="*70)


if __name__ == '__main__':
    main()
