#!/usr/bin/env python3
"""
Multi-Threaded/Multi-Process Pipeline - Eurobot 2026 ArUco Tracking System

High-performance pipeline that distributes tasks across threads and processes:
- Thread 1 (I/O): Camera capture + ArUco detection
- Process 1 (CPU): Extrinsics computation + coordinate transformation
- Process 2 (CPU): Kalman filtering
- Process 3 (CPU): RRT-Connect path planning
- Thread 2 (I/O): DDS communication (placeholder)

This architecture maximizes CPU utilization while avoiding GIL bottlenecks.

Usage:
    python multi_threaded_pipeline.py --camera 1
"""

import cv2
import numpy as np
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import time
import threading
import multiprocessing as mp
from queue import Queue, Empty, Full
from multiprocessing import Queue as MPQueue

# Fix imports for local modules (works when run from 'scripts' directory)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Kalman filter and occlusion handler
from kalman_filter.src.kalman_filter.tracker import MultiMarkerTracker, MarkerType, MarkerState
from kalman_filter.src.occlusion_handler.handler import OcclusionHandler, DetectionQuality

# Path planning (import as package)
from path_planning.rrt_connect import rrt_connect_plan

# ============================================================================
# CONFIGURATION
# ============================================================================

REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}
REFERENCE_MARKER_SIZE = 0.10
OBJECT_MARKER_SIZE = 0.05
ARUCO_DICT = cv2.aruco.DICT_4X4_50
ENEMY_MARKER_ID = 17
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"

# Queue sizes for flow control
QUEUE_MAXSIZE = 10

# ============================================================================
# TASK 1: CAMERA CAPTURE + ARUCO DETECTION (Thread - I/O Bound)
# ============================================================================

def camera_capture_and_detection(camera_id: int, intrinsics_file: str, 
                                  detection_queue: MPQueue, stop_event: threading.Event):
    """
    Thread Task 1: Capture frames and detect ArUco markers.
    
    This is I/O-bound (waiting for camera frames), so it runs in a thread.
    Outputs: (frame, corners, ids, timestamp)
    
    Args:
        camera_id: Camera device ID
        intrinsics_file: Path to camera calibration
        detection_queue: Multiprocessing queue to send detections to next stage
        stop_event: Event to signal thread termination
    """
    print("[THREAD 1] Starting camera capture and ArUco detection...")
    
    # Load camera intrinsics
    try:
        with open(intrinsics_file, 'r') as f:
            data = json.load(f)
        camera_matrix = np.array(data['camera_matrix'])
        dist_coeffs = np.array(data['distortion_coefficients'])
        print(f"[THREAD 1] ✓ Loaded camera intrinsics")
    except Exception as e:
        print(f"[THREAD 1] ✗ Failed to load intrinsics: {e}")
        return
    
    # Setup ArUco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Open camera
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"[THREAD 1] ✗ Cannot open camera {camera_id}")
        return
    
    print(f"[THREAD 1] ✓ Camera opened (ID: {camera_id})")
    frame_count = 0
    
    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("[THREAD 1] Failed to read frame")
                break
            
            # Detect ArUco markers
            corners, ids, rejected = detector.detectMarkers(frame)
            
            # Package detection data
            detection_data = {
                'frame': frame,
                'corners': corners,
                'ids': ids.flatten().tolist() if ids is not None else [],
                'corners_raw': corners,
                'timestamp': time.time(),
                'frame_count': frame_count,
                'camera_matrix': camera_matrix,
                'dist_coeffs': dist_coeffs
            }
            
            # Send to next stage (non-blocking with timeout)
            try:
                detection_queue.put(detection_data, timeout=0.1)
                frame_count += 1
            except Full:
                # Queue full - skip this frame to maintain real-time performance
                pass
    finally:
        cap.release()
        print("[THREAD 1] Camera capture stopped")

# ============================================================================
# TASK 2: EXTRINSICS + COORDINATE TRANSFORMATION (Process - CPU Bound)
# ============================================================================

def compute_extrinsics_and_transform(detection_queue: MPQueue, transform_queue: MPQueue, 
                                     extrinsics_file: str, stop_event: mp.Event):
    """
    Process Task 2: Compute camera extrinsics and transform coordinates to world frame.
    
    This is CPU-bound (matrix operations, PnP solving), so it runs in a separate process.
    Outputs: (detections_dict, extrinsics_valid, rvec_cam, tvec_cam, timestamp)
    
    Args:
        detection_queue: Input from Task 1
        transform_queue: Output to Task 3
        extrinsics_file: Path to save/load extrinsics
        stop_event: Event to signal process termination
    """
    print("[PROCESS 2] Starting extrinsics computation and transformation...")
    
    # Load extrinsics if available
    rvec_cam = None
    tvec_cam = None
    extrinsics_valid = False
    
    if Path(extrinsics_file).exists():
        try:
            with open(extrinsics_file, 'r') as f:
                data = json.load(f)
            rvec_cam = np.array(data['rvec'])
            tvec_cam = np.array(data['tvec'])
            extrinsics_valid = True
            print(f"[PROCESS 2] ✓ Loaded extrinsics from {extrinsics_file}")
        except Exception as e:
            print(f"[PROCESS 2] ✗ Failed to load extrinsics: {e}")
    
    def extract_orientation_angle(rvec: np.ndarray):
        """Extract yaw angle from rotation vector."""
        R, _ = cv2.Rodrigues(rvec)
        yaw = np.arctan2(R[1, 0], R[0, 0])
        return yaw
    
    def transform_to_world(rvec_obj: np.ndarray, tvec_obj: np.ndarray):
        """Transform object pose from camera to world coordinates."""
        if not extrinsics_valid:
            return None, None
        
        R_cam, _ = cv2.Rodrigues(rvec_cam)
        R_obj, _ = cv2.Rodrigues(rvec_obj)
        
        P_camera = tvec_obj[0].reshape(3, 1)
        R_cam_inv = R_cam.T
        P_world = R_cam_inv @ (P_camera - tvec_cam)
        
        R_obj_world = R_cam_inv @ R_obj
        rvec_world, _ = cv2.Rodrigues(R_obj_world)
        
        return rvec_world, P_world
    
    def compute_camera_extrinsics(corners_dict, ids_detected, camera_matrix, dist_coeffs):
        """Compute camera extrinsics using solvePnP."""
        object_points = []
        image_points = []
        
        for marker_id in ids_detected:
            if marker_id not in REFERENCE_MARKERS:
                continue
            
            marker_center = REFERENCE_MARKERS[marker_id]
            half_size = REFERENCE_MARKER_SIZE / 2
            
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
            return False, None, None
        
        object_points = np.array(object_points, dtype=np.float32)
        image_points = np.array(image_points, dtype=np.float32)
        
        success, rvec, tvec = cv2.solvePnP(
            object_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if success:
            R_cam, _ = cv2.Rodrigues(rvec)
            cam_pos_world = -R_cam.T @ tvec
            print(f"[PROCESS 2] ✓ Extrinsics computed! Camera at: ({cam_pos_world[0,0]:.3f}, {cam_pos_world[1,0]:.3f}, {cam_pos_world[2,0]:.3f})m")
            
            # Save extrinsics
            extrinsics_data = {
                "rvec": rvec.tolist(),
                "tvec": tvec.tolist(),
                "rotation_matrix": R_cam.tolist(),
                "camera_position_world": {
                    "x": float(cam_pos_world[0,0]),
                    "y": float(cam_pos_world[1,0]),
                    "z": float(cam_pos_world[2,0])
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            Path(extrinsics_file).parent.mkdir(parents=True, exist_ok=True)
            with open(extrinsics_file, 'w') as f:
                json.dump(extrinsics_data, f, indent=2)
            
            return True, rvec, tvec
        
        return False, None, None
    
    while not stop_event.is_set():
        try:
            # Get detection data from Task 1
            detection_data = detection_queue.get(timeout=0.1)
        except:
            continue
        
        frame = detection_data['frame']
        corners_raw = detection_data['corners_raw']
        ids = detection_data['ids']
        camera_matrix = detection_data['camera_matrix']
        dist_coeffs = detection_data['dist_coeffs']
        timestamp = detection_data['timestamp']
        
        detections = {}
        
        if len(ids) > 0:
            # Estimate pose for each marker
            rvecs = []
            tvecs = []
            for i, marker_id in enumerate(ids):
                marker_size = REFERENCE_MARKER_SIZE if marker_id in REFERENCE_MARKERS else OBJECT_MARKER_SIZE
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [corners_raw[i]], marker_size, camera_matrix, dist_coeffs
                )
                rvecs.append(rvec[0])
                tvecs.append(tvec[0])
            
            rvecs = np.array(rvecs)
            tvecs = np.array(tvecs)
            
            # Compute extrinsics if not valid and enough reference markers detected
            ref_markers = [mid for mid in ids if mid in REFERENCE_MARKERS]
            if len(ref_markers) >= 4 and not extrinsics_valid:
                corners_dict = {ids[i]: corners_raw[i] for i in range(len(ids))}
                success, rvec_new, tvec_new = compute_camera_extrinsics(
                    corners_dict, ids, camera_matrix, dist_coeffs
                )
                if success:
                    rvec_cam = rvec_new
                    tvec_cam = tvec_new
                    extrinsics_valid = True
            
            # Transform coordinates to world frame
            for i, marker_id in enumerate(ids):
                if marker_id in REFERENCE_MARKERS:
                    detections[marker_id] = {
                        'type': 'reference',
                        'world_pos': REFERENCE_MARKERS[marker_id]
                    }
                else:
                    if extrinsics_valid:
                        rvec_world, tvec_world = transform_to_world(rvecs[i], tvecs[i])
                        if tvec_world is not None:
                            world_pos = tvec_world.flatten()
                            theta = extract_orientation_angle(rvec_world)
                            
                            detections[marker_id] = {
                                'type': 'enemy' if marker_id == ENEMY_MARKER_ID else 'object',
                                'world_pos': world_pos,
                                'theta': theta,
                                'raw': True
                            }
        
        # Send to Task 3 (Kalman filtering)
        transform_data = {
            'detections': detections,
            'corners': corners_raw,
            'ids': ids,
            'extrinsics_valid': extrinsics_valid,
            'rvec_cam': rvec_cam,
            'tvec_cam': tvec_cam,
            'camera_matrix': camera_matrix,
            'dist_coeffs': dist_coeffs,
            'frame': frame,
            'timestamp': timestamp
        }
        
        try:
            transform_queue.put(transform_data, timeout=0.1)
        except Full:
            pass
    
    print("[PROCESS 2] Extrinsics computation stopped")

# ============================================================================
# TASK 3: KALMAN FILTERING (Process - CPU Bound)
# ============================================================================

def kalman_filtering(transform_queue: MPQueue, kalman_queue: MPQueue, stop_event: mp.Event):
    """
    Process Task 3: Apply Kalman filtering to tracked objects.
    
    This is CPU-bound (matrix operations for Kalman filter), so it runs in a separate process.
    Outputs: (filtered_detections, timestamp)
    
    Args:
        transform_queue: Input from Task 2
        kalman_queue: Output to Task 4
        stop_event: Event to signal process termination
    """
    print("[PROCESS 3] Starting Kalman filtering...")
    
    # Initialize Kalman tracker
    kalman_tracker = MultiMarkerTracker(
        process_noise=0.01,
        measurement_noise=0.1,
        max_frames_without_detection=30
    )
    
    frame_count = 0
    last_fps_time = time.time()
    fps = 30.0
    
    while not stop_event.is_set():
        try:
            transform_data = transform_queue.get(timeout=0.1)
        except:
            continue
        
        detections = transform_data['detections']
        timestamp = transform_data['timestamp']
        
        # Prepare Kalman detections
        kalman_detections = {}
        for marker_id, det in detections.items():
            if det['type'] in ['enemy', 'object'] and 'world_pos' in det:
                world_pos = det['world_pos']
                theta = det.get('theta', 0.0)
                kalman_detections[marker_id] = (world_pos[0], world_pos[1], theta)
        
        # Update Kalman filter
        dt = 1.0 / max(fps, 30.0)
        tracked_states = kalman_tracker.update(kalman_detections, dt)
        
        # Merge Kalman results with detections
        for marker_id, state in tracked_states.items():
            if marker_id in detections:
                detections[marker_id]['kalman_pos'] = (state.x, state.y, 0.0)
                detections[marker_id]['kalman_theta'] = state.theta
                detections[marker_id]['confidence'] = state.confidence
                detections[marker_id]['is_occluded'] = state.is_occluded
                detections[marker_id]['filtered'] = True
        
        # Update FPS
        frame_count += 1
        if frame_count % 30 == 0:
            current_time = time.time()
            elapsed = current_time - last_fps_time
            fps = 30.0 / elapsed if elapsed > 0 else 30.0
            last_fps_time = current_time
        
        # Get Kalman tracking summary
        kalman_summary = {}
        if kalman_tracker is not None:
            kalman_summary = kalman_tracker.get_tracking_summary()
        
        # Send to Task 4 (Path planning)
        kalman_data = {
            'detections': detections,
            'corners': transform_data.get('corners', []),
            'ids': transform_data.get('ids', []),
            'kalman_summary': kalman_summary,
            'extrinsics_valid': transform_data['extrinsics_valid'],
            'rvec_cam': transform_data['rvec_cam'],
            'tvec_cam': transform_data['tvec_cam'],
            'camera_matrix': transform_data['camera_matrix'],
            'dist_coeffs': transform_data['dist_coeffs'],
            'frame': transform_data['frame'],
            'timestamp': timestamp,
            'fps': fps
        }
        
        try:
            kalman_queue.put(kalman_data, timeout=0.1)
        except Full:
            pass
    
    print("[PROCESS 3] Kalman filtering stopped")

# ============================================================================
# TASK 4: PATH PLANNING (Process - CPU Bound)
# ============================================================================

def path_planning(kalman_queue: MPQueue, path_queue: MPQueue, stop_event: mp.Event):
    """
    Process Task 4: Compute paths using RRT-Connect.
    
    This is CPU-bound (RRT algorithm, path cost computation), so it runs in a separate process.
    Outputs: (path, waypoints, detections, visualization_data, timestamp)
    
    Args:
        kalman_queue: Input from Task 3
        path_queue: Output to Task 5
        stop_event: Event to signal process termination
    """
    print("[PROCESS 4] Starting path planning...")
    
    # Path planning state
    _last_planned_path = None
    _last_plan_time = 0.0
    _plan_interval = 0.5
    _last_successful_plan_time = 0.0
    _planning_failure_start = None
    _sudden_stop_triggered = False
    _using_fallback_path = False  # Track if currently using a fallback path
    all_candidate_paths = []
    robot_radius = 0.22
    enemy_obstacle_radius = 0.22
    obstacle_radius_default = 0.12
    
    # Timeout and fallback settings
    MAX_PLANNING_TIME = 2.0  # Max time to spend on single RRT attempt
    FAILURE_TIMEOUT = 3.0    # Trigger sudden stop after 3 seconds of failures
    MAX_RRT_ATTEMPTS = 3     # Max attempts per planning cycle (reduced from 5 for speed)
    FALLBACK_PATH_HOLD_TIME = 5.0  # Hold fallback path for 5 seconds before replanning
    
    def compute_path_cost(path):
        """Compute total Euclidean length of path."""
        if not path or len(path) < 2:
            return float('inf')
        cost = 0.0
        for i in range(len(path) - 1):
            cost += np.linalg.norm(np.array(path[i][:2]) - np.array(path[i+1][:2]))
        return cost
    
    def sampled_circle_intersects_obstacle(path, obstacle, robot_radius, num_samples=50):
        """Check if path intersects with obstacle."""
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
    
    while not stop_event.is_set():
        try:
            kalman_data = kalman_queue.get(timeout=0.1)
        except:
            continue
        
        detections = kalman_data['detections']
        extrinsics_valid = kalman_data['extrinsics_valid']
        timestamp = kalman_data['timestamp']
        now = time.time()
        
        # Path planning (RRT-Connect)
        if extrinsics_valid and now - _last_plan_time > _plan_interval:
            ally_marker_id = 36
            start_pos = None
            
            if ally_marker_id in detections and 'world_pos' in detections[ally_marker_id]:
                start_pos = np.array(detections[ally_marker_id].get('kalman_pos', detections[ally_marker_id]['world_pos']))
            
            goal_pos = REFERENCE_MARKERS.get(23)
            
            if start_pos is not None and goal_pos is not None:
                # Collect obstacles
                obstacles = []
                enemy_obstacle = None
                
                for mid, det in detections.items():
                    if mid == ENEMY_MARKER_ID and 'world_pos' in det:
                        pos = np.array(det.get('kalman_pos', det['world_pos']))
                        radius = enemy_obstacle_radius
                        current_obstacle = (pos, radius)
                        obstacles.append(current_obstacle)
                        enemy_obstacle = current_obstacle
                
                # Check if current path is blocked
                is_blocked = False
                if _last_planned_path and enemy_obstacle:
                    is_blocked = sampled_circle_intersects_obstacle(_last_planned_path, enemy_obstacle, robot_radius)
                
                # If using a fallback path, hold it for a while before replanning
                if _using_fallback_path and _last_planned_path:
                    time_since_fallback = now - _last_successful_plan_time
                    if time_since_fallback < FALLBACK_PATH_HOLD_TIME:
                        # Keep using fallback path, don't replan yet
                        if not is_blocked:
                            # Path is clear now, can exit fallback mode
                            _using_fallback_path = False
                            print("[PROCESS 4] ✓ Fallback path clear, exiting fallback mode")
                        # Skip replanning
                        _last_plan_time = now
                        continue
                
                # Replan if needed
                if _last_planned_path is None or is_blocked:
                    if is_blocked:
                        print("[PROCESS 4] ! Path blocked by enemy. Replanning...")
                    
                    bounds = (0.0, 3.0, 0.0, 2.0)
                    inflated_obstacles = [(c, r + robot_radius) for (c, r) in obstacles]
                    
                    # Compute multiple candidate paths with timeout
                    candidate_paths = []
                    planning_start = time.time()
                    
                    for seed in range(MAX_RRT_ATTEMPTS):
                        # Check timeout
                        if time.time() - planning_start > MAX_PLANNING_TIME:
                            print(f"[PROCESS 4] ⚠ Planning timeout after {time.time() - planning_start:.2f}s")
                            break
                        
                        np.random.seed(int(time.time() * 1000) % 2**32 + seed)
                        path = rrt_connect_plan(start_pos, goal_pos, inflated_obstacles, bounds)
                        if path:
                            candidate_paths.append(path)
                    
                    # If no paths found, try fallback: allow backward waypoints
                    if not candidate_paths:
                        print("[PROCESS 4] ⚠ No forward path found. Trying fallback with backward waypoints...")
                        
                        for seed in range(MAX_RRT_ATTEMPTS):
                            if time.time() - planning_start > MAX_PLANNING_TIME:
                                break
                            
                            # Try with relaxed obstacles (reduce enemy radius)
                            relaxed_obstacles = [(c, max(0.05, r * 0.7 + robot_radius)) for (c, r) in obstacles]
                            np.random.seed(int(time.time() * 1000) % 2**32 + seed + 100)
                            path = rrt_connect_plan(start_pos, goal_pos, relaxed_obstacles, bounds)
                            if path:
                                candidate_paths.append(path)
                                print("[PROCESS 4] ✓ Fallback path found - ACCEPTING FIRST AND HOLDING")
                                # ACCEPT FIRST FALLBACK PATH - stop generating more
                                _using_fallback_path = True
                                break
                    
                    # Store all candidate paths
                    all_candidate_paths.extend(candidate_paths)
                    
                    # Select path: if fallback, use first one; if normal, use shortest
                    best_path = None
                    best_cost = float('inf')
                    
                    if _using_fallback_path and candidate_paths:
                        # Fallback mode: just take the first valid path
                        best_path = candidate_paths[0]
                        best_cost = compute_path_cost(best_path)
                    else:
                        # Normal mode: select shortest path
                        for cand_path in candidate_paths:
                            cost = compute_path_cost(cand_path)
                            if cost < best_cost:
                                best_cost = cost
                                best_path = cand_path
                    
                    _last_planned_path = best_path
                    
                    if _last_planned_path:
                        fallback_str = " (FALLBACK - HOLDING FOR 2s)" if _using_fallback_path else ""
                        print(f"[PROCESS 4] ✓ Path found with {len(_last_planned_path)} waypoints. Cost: {best_cost:.3f}{fallback_str}")
                        _last_successful_plan_time = now
                        _planning_failure_start = None
                        _sudden_stop_triggered = False
                    else:
                        print("[PROCESS 4] ✗ RRT-Connect planner failed to find a path.")
                        
                        # Track failure duration
                        if _planning_failure_start is None:
                            _planning_failure_start = now
                        
                        failure_duration = now - _planning_failure_start
                        
                        # Trigger sudden stop if failures exceed timeout
                        if failure_duration > FAILURE_TIMEOUT:
                            if not _sudden_stop_triggered:
                                print(f"[PROCESS 4] 🛑 SUDDEN STOP TRIGGERED - No path for {failure_duration:.1f}s")
                                _sudden_stop_triggered = True
                            _last_planned_path = None  # Clear path to stop robot
                
                _last_plan_time = now
        
        # Prepare waypoints (reversed so start is first, goal is last)
        waypoints = []
        if _last_planned_path:
            reversed_path = list(reversed(_last_planned_path))
            waypoints = [(float(pt[0]), float(pt[1])) for pt in reversed_path]
        
        # Waypoint selection: skip waypoints behind or too close to robot
        # In fallback mode (sudden stop not triggered but no forward path), allow backward waypoints
        next_waypoint = None
        if _last_planned_path and 36 in detections and 'kalman_pos' in detections[36]:
            reversed_path = list(reversed(_last_planned_path))
            robot_pos = np.array(detections[36]['kalman_pos'][:2])
            robot_theta = detections[36].get('kalman_theta', None)
            
            if robot_theta is not None:
                heading = np.array([np.cos(robot_theta), np.sin(robot_theta)])
            else:
                if len(reversed_path) > 1:
                    heading = np.array(reversed_path[1][:2]) - robot_pos
                    heading = heading / (np.linalg.norm(heading) + 1e-8)
                else:
                    heading = np.array([1.0, 0.0])
            
            min_distance = robot_radius * 0.8
            
            # Use different thresholds based on planning state
            if _planning_failure_start is not None and not _sudden_stop_triggered:
                # Fallback mode: allow backward waypoints (more lenient angle check)
                angle_threshold = -0.5  # Allow waypoints up to ~120° behind
                print("[PROCESS 4] 🔄 Fallback mode: Allowing backward waypoints for rerouting")
            else:
                # Normal mode: only forward waypoints
                angle_threshold = 0.2  # Only waypoints < 78° ahead
            
            for wp in reversed_path:
                wp_vec = np.array(wp[:2]) - robot_pos
                distance = np.linalg.norm(wp_vec)
                if distance < min_distance:
                    continue
                dot = np.dot(heading, wp_vec / (distance + 1e-8))
                if dot > angle_threshold:
                    next_waypoint = wp
                    break
        
        # Print waypoints periodically (console output)
        if waypoints and now - _last_plan_time < 0.1:  # Print when path updates
            print(f"[PROCESS 4] WAYPOINTS: {waypoints}")
        
        if next_waypoint is not None and now - _last_plan_time < 0.1:
            print(f"[PROCESS 4] NEXT WAYPOINT: {tuple(float(x) for x in next_waypoint)}")
        
        # Prepare obstacles for drawing
        obstacles_to_draw = []
        for mid, det in detections.items():
            if 'world_pos' in det and mid not in REFERENCE_MARKERS:
                pos = det.get('kalman_pos', det['world_pos'])
                radius = enemy_obstacle_radius if mid == ENEMY_MARKER_ID else obstacle_radius_default
                obstacles_to_draw.append((np.array(pos), radius))
        
        # Send to visualization (and DDS placeholder)
        path_data = {
            'path': _last_planned_path,
            'waypoints': waypoints,
            'next_waypoint': next_waypoint,
            'all_candidate_paths': all_candidate_paths,
            'obstacles': obstacles_to_draw,
            'detections': detections,
            'corners': kalman_data.get('corners', []),
            'ids': kalman_data.get('ids', []),
            'kalman_summary': kalman_data.get('kalman_summary', {}),
            'sudden_stop': _sudden_stop_triggered,
            'planning_failure_duration': (now - _planning_failure_start) if _planning_failure_start else 0.0,
            'extrinsics_valid': extrinsics_valid,
            'rvec_cam': kalman_data['rvec_cam'],
            'tvec_cam': kalman_data['tvec_cam'],
            'camera_matrix': kalman_data['camera_matrix'],
            'dist_coeffs': kalman_data['dist_coeffs'],
            'frame': kalman_data['frame'],
            'fps': kalman_data['fps'],
            'timestamp': timestamp
        }
        
        try:
            path_queue.put(path_data, timeout=0.1)
        except Full:
            pass
    
    print("[PROCESS 4] Path planning stopped")

# ============================================================================
# TASK 5: DDS COMMUNICATION (Thread - I/O Bound)
# ============================================================================

def dds_communication(path_queue: MPQueue, stop_event: threading.Event):
    """
    Thread Task 5: DDS Communication (PLACEHOLDER - disabled for now).
    
    This is I/O-bound (network communication), so it runs in a thread.
    Currently just a placeholder - communication removed.
    
    Args:
        path_queue: Queue to receive path planning results
        stop_event: Event to signal thread termination
    """
    print("[THREAD 5] DDS communication placeholder (disabled)")
    
    # Placeholder - DDS communication removed for now
    # Just wait for stop signal
    
    while not stop_event.is_set():
        time.sleep(0.1)
    
    print("[THREAD 5] DDS communication stopped")

# ============================================================================
# VISUALIZATION TASK (Main Thread - for debugging/monitoring)
# ============================================================================

def visualization_task(path_queue: MPQueue, stop_event: threading.Event):
    """
    Main thread visualization: Display processed frames with paths and markers.
    Shows ArUco marker IDs, enemy markers, reference markers, and Kalman tracking.
    
    Args:
        path_queue: Shared queue with path planning results
        stop_event: Event to signal termination
    """
    print("[MAIN THREAD] Starting visualization...")
    
    def project_world_to_image(world_points, rvec_cam, tvec_cam, camera_matrix, dist_coeffs):
        """Project 3D world points to 2D image coordinates."""
        if rvec_cam is None or tvec_cam is None:
            return []
        pts = np.array(world_points, dtype=np.float32).reshape(-1, 3)
        imgpts, _ = cv2.projectPoints(pts, rvec_cam, tvec_cam, camera_matrix, dist_coeffs)
        imgpts = imgpts.reshape(-1, 2)
        return [(int(p[0]), int(p[1])) for p in imgpts]
    
    def draw_path_and_obstacles(display_frame, path, obstacles, rvec_cam, tvec_cam, 
                                camera_matrix, dist_coeffs, robot_radius=None):
        """Draw RRT path and obstacles on frame."""
        if rvec_cam is None or tvec_cam is None:
            return
        
        # Draw obstacles
        for center, radius in obstacles:
            center_2d = project_world_to_image([center], rvec_cam, tvec_cam, camera_matrix, dist_coeffs)
            if not center_2d:
                continue
            edge_point_3d = center + np.array([radius, 0, 0])
            edge_point_2d = project_world_to_image([edge_point_3d], rvec_cam, tvec_cam, camera_matrix, dist_coeffs)
            if not edge_point_2d:
                continue
            pixel_radius = int(np.linalg.norm(np.array(center_2d[0]) - np.array(edge_point_2d[0])))
            cv2.circle(display_frame, center_2d[0], pixel_radius, (255, 100, 0), 2)
        
        # Draw path
        if path and len(path) > 1:
            path_pixels = project_world_to_image(path, rvec_cam, tvec_cam, camera_matrix, dist_coeffs)
            if path_pixels:
                path_pts = np.array(path_pixels, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(display_frame, [path_pts], isClosed=False, color=(0, 255, 255), thickness=2)
                
                # Draw robot footprint circles along path
                if robot_radius:
                    num_samples = max(10, len(path) * 5)
                    sampled_points = []
                    for i in range(len(path) - 1):
                        p0 = np.array(path[i])
                        p1 = np.array(path[i + 1])
                        for t in np.linspace(0, 1, num_samples // (len(path) - 1)):
                            pt_world = p0 * (1 - t) + p1 * t
                            sampled_points.append(pt_world)
                    
                    sampled_pixels = project_world_to_image(sampled_points, rvec_cam, tvec_cam, camera_matrix, dist_coeffs)
                    for pt_world, pt_pixel in zip(sampled_points, sampled_pixels):
                        try:
                            wx = float(pt_world[0])
                            wy = float(pt_world[1])
                            edge_pt_world = np.array([wx + robot_radius, wy, 0.0])
                            edge_px = project_world_to_image([edge_pt_world], rvec_cam, tvec_cam, camera_matrix, dist_coeffs)
                            if edge_px:
                                pixel_r = int(np.linalg.norm(np.array(pt_pixel) - np.array(edge_px[0])))
                                cv2.circle(display_frame, tuple(pt_pixel), pixel_r, (0, 165, 255), 1)
                        except Exception:
                            continue
                
                # Draw waypoint coordinates
                for wp_world, pt in zip(path, path_pixels):
                    try:
                        p = tuple(pt)
                        cv2.circle(display_frame, p, 5, (0, 165, 255), -1)
                        wx, wy = float(wp_world[0]), float(wp_world[1])
                        coord_text = f"({wx:.3f},{wy:.3f})"
                        cv2.putText(display_frame, coord_text, (p[0] + 6, p[1] - 6),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (230, 230, 230), 1)
                    except Exception:
                        continue
    
    while not stop_event.is_set():
        try:
            path_data = path_queue.get(timeout=0.1)
        except:
            continue
        
        # Extract data from queue
        frame = path_data['frame']
        corners = path_data.get('corners', [])
        ids = path_data.get('ids', [])
        detections = path_data.get('detections', {})
        path = path_data['path']
        all_candidate_paths = path_data['all_candidate_paths']
        obstacles = path_data['obstacles']
        extrinsics_valid = path_data['extrinsics_valid']
        rvec_cam = path_data['rvec_cam']
        tvec_cam = path_data['tvec_cam']
        camera_matrix = path_data['camera_matrix']
        dist_coeffs = path_data['dist_coeffs']
        fps = path_data['fps']
        kalman_summary = path_data.get('kalman_summary', {})
        sudden_stop = path_data.get('sudden_stop', False)
        failure_duration = path_data.get('planning_failure_duration', 0.0)
        
        display = frame.copy()
        
        # Draw detected ArUco markers
        if len(corners) > 0 and len(ids) > 0:
            cv2.aruco.drawDetectedMarkers(display, corners, np.array(ids).reshape(-1, 1))
            
            # Draw labels for each marker
            for i, marker_id in enumerate(ids):
                corner = corners[i][0][0]
                
                # Determine marker type and color
                if marker_id in REFERENCE_MARKERS:
                    color = (0, 255, 0)  # Green for reference
                    label = f"REF {marker_id}"
                elif marker_id == ENEMY_MARKER_ID:
                    color = (0, 0, 255)  # Red for enemy
                    label = f"ENEMY {marker_id}"
                else:
                    color = (255, 0, 255)  # Magenta for objects
                    label = f"OBJ {marker_id}"
                
                # Add world coordinates if available
                if marker_id in detections and 'world_pos' in detections[marker_id]:
                    world_pos = detections[marker_id]['world_pos']
                    x, y, z = world_pos
                    label += f" | ({x:.3f}, {y:.3f}, {z:.3f})m"
                
                # Draw main label
                cv2.putText(display, label, (int(corner[0]), int(corner[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Draw Kalman filter info for enemy
                if marker_id == ENEMY_MARKER_ID and marker_id in detections:
                    if detections[marker_id].get('filtered', False):
                        kf_pos = detections[marker_id].get('kalman_pos', (0, 0, 0))
                        confidence = detections[marker_id].get('confidence', 0)
                        is_occluded = detections[marker_id].get('is_occluded', False)
                        
                        kf_label = f"ENEMY {marker_id} (KF) | ({kf_pos[0]:.3f}, {kf_pos[1]:.3f}) | conf={confidence:.2f}"
                        if is_occluded:
                            kf_label += " [OCCLUDED]"
                        
                        cv2.putText(display, kf_label, (int(corner[0]), int(corner[1]) + 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Draw status
        status_y = 30
        ref_count = sum(1 for mid in ids if mid in REFERENCE_MARKERS)
        if extrinsics_valid:
            status = f"TRACKING | Refs: {ref_count}/4 | FPS: {fps:.1f}"
            status_color = (0, 255, 0)
        else:
            status = f"CALIBRATING | Refs: {ref_count}/4 (need 4)"
            status_color = (0, 165, 255)
        
        # Add Kalman status if available
        if kalman_summary:
            status += f" | Kalman: ON"
            cv2.putText(display, status, (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Draw Kalman stats
            stats_text = f"Tracked: {kalman_summary.get('tracked_markers', 0)} | Enemy: {kalman_summary.get('enemy_markers', 0)} | Occluded: {kalman_summary.get('occluded_markers', 0)}"
            cv2.putText(display, stats_text, (10, status_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            cv2.putText(display, status, (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Draw SUDDEN STOP warning if triggered
        if sudden_stop:
            # Big red warning overlay
            overlay = display.copy()
            cv2.rectangle(overlay, (0, 0), (display.shape[1], 100), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.3, display, 0.7, 0, display)
            
            # Warning text
            warning_text = "🛑 SUDDEN STOP TRIGGERED 🛑"
            cv2.putText(display, warning_text, (display.shape[1]//2 - 300, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            cv2.putText(display, f"No path found for {failure_duration:.1f}s", 
                       (display.shape[1]//2 - 200, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        elif failure_duration > 0:
            # Show warning before sudden stop triggers
            warning_text = f"⚠ Path planning failed ({failure_duration:.1f}s)"
            cv2.putText(display, warning_text, (10, status_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        # Draw all candidate paths in black
        if all_candidate_paths and extrinsics_valid:
            for cand_path in all_candidate_paths:
                path_pixels = project_world_to_image(cand_path, rvec_cam, tvec_cam, camera_matrix, dist_coeffs)
                if path_pixels:
                    path_pts = np.array(path_pixels, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(display, [path_pts], isClosed=False, color=(0, 0, 0), thickness=1)
        
        # Draw best path in yellow/orange
        if path and extrinsics_valid:
            draw_path_and_obstacles(display, path, obstacles, rvec_cam, tvec_cam, 
                                   camera_matrix, dist_coeffs, robot_radius=0.22)
        
        cv2.imshow('Multi-Threaded Pipeline - Eurobot Tracking', display)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            stop_event.set()
            break
    
    cv2.destroyAllWindows()
    
    print("[MAIN THREAD] Visualization stopped")

# ============================================================================
# CLEANUP UTILITIES
# ============================================================================

def drain_queue(q: MPQueue, timeout=0.5):
    """Drain a queue to prevent blocking on join."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            q.get_nowait()
        except:
            break

def cleanup_processes(processes: List, stop_event: mp.Event, timeout=2.0):
    """Clean up processes with proper termination."""
    # Signal all processes to stop
    stop_event.set()
    
    # Wait for graceful shutdown
    for proc in processes:
        proc.join(timeout=timeout)
    
    # Force terminate any remaining processes
    for proc in processes:
        if proc.is_alive():
            print(f"[CLEANUP] Force terminating process {proc.pid}...")
            proc.terminate()
            proc.join(timeout=1)
            
    # Final kill if still alive
    for proc in processes:
        if proc.is_alive():
            print(f"[CLEANUP] Force killing process {proc.pid}...")
            proc.kill()

# ============================================================================
# MAIN PIPELINE ORCHESTRATION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Multi-Threaded/Multi-Process Pipeline - Eurobot Tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--camera', type=int, default=2, help='Camera device ID')
    parser.add_argument('--intrinsics', type=str, default=DEFAULT_INTRINSICS, help='Camera intrinsics JSON')
    parser.add_argument('--extrinsics', type=str, default=DEFAULT_EXTRINSICS, help='Camera extrinsics JSON')
    parser.add_argument('--no-viz', action='store_true', help='Disable visualization')
    
    args = parser.parse_args()
    
    if not Path(args.intrinsics).exists():
        print(f"✗ Intrinsics file not found: {args.intrinsics}")
        return 1
    
    print("\n" + "="*70)
    print("MULTI-THREADED/MULTI-PROCESS PIPELINE")
    print("="*70)
    print("Architecture:")
    print("  Thread 1  → Camera capture + ArUco detection (I/O-bound)")
    print("  Process 2 → Extrinsics + coordinate transformation (CPU-bound)")
    print("  Process 3 → Kalman filtering (CPU-bound)")
    print("  Process 4 → RRT-Connect path planning (CPU-bound)")
    print("  Thread 5  → DDS communication (I/O-bound)")
    print("="*70 + "\n")
    
    # Create inter-process queues
    detection_queue = MPQueue(maxsize=QUEUE_MAXSIZE)
    transform_queue = MPQueue(maxsize=QUEUE_MAXSIZE)
    kalman_queue = MPQueue(maxsize=QUEUE_MAXSIZE)
    path_queue = MPQueue(maxsize=QUEUE_MAXSIZE)
    
    # Create stop events
    thread_stop_event = threading.Event()
    process_stop_event = mp.Event()
    
    # Start processes
    process2 = mp.Process(target=compute_extrinsics_and_transform, 
                         args=(detection_queue, transform_queue, args.extrinsics, process_stop_event),
                         daemon=True)
    process3 = mp.Process(target=kalman_filtering, 
                         args=(transform_queue, kalman_queue, process_stop_event),
                         daemon=True)
    process4 = mp.Process(target=path_planning, 
                         args=(kalman_queue, path_queue, process_stop_event),
                         daemon=True)
    
    process2.start()
    process3.start()
    process4.start()
    
    # Start threads
    thread1 = threading.Thread(target=camera_capture_and_detection, 
                               args=(args.camera, args.intrinsics, detection_queue, thread_stop_event),
                               daemon=True)
    thread5 = threading.Thread(target=dds_communication, 
                               args=(path_queue, thread_stop_event),
                               daemon=True)
    
    thread1.start()
    thread5.start()
    
    try:
        if not args.no_viz:
            # Run visualization in main thread
            visualization_task(path_queue, thread_stop_event)
        else:
            # Just wait for termination
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✓ Pipeline stopped by user")
    finally:
        # Cleanup
        print("\nStopping pipeline...")
        thread_stop_event.set()
        
        # Give threads time to finish
        thread1.join(timeout=2)
        thread5.join(timeout=2)
        
        # Drain queues to unblock processes
        print("[CLEANUP] Draining queues...")
        drain_queue(detection_queue)
        drain_queue(transform_queue)
        drain_queue(kalman_queue)
        drain_queue(path_queue)
        
        # Clean up processes
        cleanup_processes([process2, process3, process4], process_stop_event, timeout=2)
        
        # Ensure all OpenCV windows are destroyed
        cv2.destroyAllWindows()
        
        print("✓ All tasks stopped")
    
    return 0


if __name__ == "__main__":
    # Required for Windows multiprocessing
    mp.freeze_support()
    sys.exit(main())
