#!/usr/bin/env python3
"""
Interactive Kalman Filter Tuning Tool

Test different parameter combinations and visualize results in real-time.
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "map_anchors" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import tracker from map_anchors (working tracking system)
from track_objects import ObjectTracker
from kalman_filter.tracker import MultiMarkerTracker
import matplotlib.pyplot as plt
from collections import deque

# Constants
ENEMY_MARKER_ID = 13
REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}


class KalmanTuner:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.process_noise = 0.01
        self.measurement_noise = 0.1
        self.tracker = None
        self.kalman_tracker = None
        
        # Data logging
        self.raw_positions = deque(maxlen=300)  # 10 seconds at 30fps
        self.filtered_positions = deque(maxlen=300)
        self.timestamps = deque(maxlen=300)
        
        # Visualization
        self.setup_plot()
    
    def setup_plot(self):
        plt.ion()
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.suptitle('Kalman Filter Tuning')
    
    def update_tracker(self):
        """Reinitialize tracker with new parameters."""
        # Initialize base tracker
        calibration_file = str(Path(__file__).parent.parent.parent / 
                              "camera_calibration_folder" / "calibration" / "camera_calibration.json")
        self.tracker = ObjectTracker(calibration_file, self.camera_id)
        
        # Initialize Kalman filter with new parameters
        self.kalman_tracker = MultiMarkerTracker(
            process_noise=self.process_noise,
            measurement_noise=self.measurement_noise,
            max_frames_without_detection=30
        )
    
    def run(self):
        self.update_tracker()
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"❌ Cannot open camera {self.camera_id}")
            return
        
        print("\n" + "="*60)
        print("KALMAN FILTER TUNER")
        print("="*60)
        print("\nControls:")
        print("  'q'/'a' - Increase/Decrease Process Noise (Q)")
        print("  'w'/'s' - Increase/Decrease Measurement Noise (R)")
        print("  'r'     - Reset to defaults")
        print("  'p'     - Plot results")
        print("  SPACE   - Reset extrinsics")
        print("  ESC     - Quit")
        print("\nCurrent parameters:")
        self.print_params()
        print("\nPlace enemy marker (ID 13) in view...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Detect markers
            corners, ids, rejected = self.tracker.detector.detectMarkers(frame)
            display = frame.copy()
            
            if ids is None:
                cv2.putText(display, "No markers detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Kalman Tuner', display)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                continue
            
            ids = ids.flatten()
            
            # Estimate poses
            rvecs = []
            tvecs = []
            for i, marker_id in enumerate(ids):
                if marker_id in REFERENCE_MARKERS:
                    size = 0.10
                else:
                    size = 0.05
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [corners[i]], size, self.tracker.camera_matrix, self.tracker.dist_coeffs
                )
                rvecs.append(rvec[0])
                tvecs.append(tvec[0])
            rvecs = np.array(rvecs)
            tvecs = np.array(tvecs)
            
            # Compute/update extrinsics
            corners_dict = {ids[i]: corners[i] for i in range(len(ids))}
            ref_markers = [mid for mid in ids if mid in REFERENCE_MARKERS]
            if len(ref_markers) >= 4 and not self.tracker.extrinsics_valid:
                self.tracker.compute_camera_extrinsics_robust(corners_dict, ids)
            
            # Draw markers
            cv2.aruco.drawDetectedMarkers(display, corners, ids)
            
            # Prepare Kalman detections
            kalman_detections = {}
            detections = {}
            
            # Process each marker
            for i, marker_id in enumerate(ids):
                if self.tracker.extrinsics_valid and marker_id not in REFERENCE_MARKERS:
                    # Transform to world coordinates
                    rvec_world, tvec_world = self.tracker.transform_to_world(rvecs[i], tvecs[i])
                    
                    if tvec_world is not None:
                        world_pos = tvec_world.flatten()
                        
                        # Extract yaw angle
                        R_world, _ = cv2.Rodrigues(rvec_world)
                        theta = np.arctan2(R_world[1, 0], R_world[0, 0])
                        
                        # Add to Kalman detections
                        kalman_detections[marker_id] = (world_pos[0], world_pos[1], theta)
                        
                        # Store raw detection
                        detections[marker_id] = {
                            'world_pos': world_pos,
                            'theta': theta,
                            'raw': True
                        }
            
            # Update Kalman filter
            if self.tracker.extrinsics_valid:
                dt = 1.0 / 30.0
                tracked_states = self.kalman_tracker.update(kalman_detections, dt)
                
                # Update detections with Kalman data (including predicted-only states)
                for marker_id, state in tracked_states.items():
                    if marker_id in detections:
                        # Marker detected - update with filtered position
                        detections[marker_id]['kalman_pos'] = (state.x, state.y, 0.0)
                        detections[marker_id]['kalman_theta'] = state.theta
                        detections[marker_id]['confidence'] = state.confidence
                        detections[marker_id]['filtered'] = True
                    else:
                        # Marker not detected but Kalman has prediction
                        detections[marker_id] = {
                            'world_pos': np.array([state.x, state.y, 0.0]),
                            'theta': state.theta,
                            'raw': False,
                            'kalman_pos': (state.x, state.y, 0.0),
                            'kalman_theta': state.theta,
                            'confidence': state.confidence,
                            'filtered': True,
                            'prediction_only': True
                        }
            
            # Log data if enemy detected or predicted
            if ENEMY_MARKER_ID in detections:
                enemy = detections[ENEMY_MARKER_ID]
                is_prediction_only = enemy.get('prediction_only', False)
                
                # Raw position
                raw_x, raw_y = enemy['world_pos'][:2]
                raw_theta = enemy['theta']
                
                # Convert world coordinates to pixel coordinates for visualization
                # Assuming table is ~3m x 2m, scale to frame
                scale_x = display.shape[1] / 3.0  # pixels per meter
                scale_y = display.shape[0] / 2.0
                
                # Get marker center in pixel coordinates (if detected)
                if not is_prediction_only and ENEMY_MARKER_ID in ids:
                    marker_idx = np.where(ids == ENEMY_MARKER_ID)[0][0]
                    marker_corners = corners[marker_idx].reshape(4, 2)
                    marker_center = marker_corners.mean(axis=0).astype(int)
                    marker_cx, marker_cy = marker_center
                else:
                    # Use predicted position as marker center when not detected
                    marker_cx = int(raw_x * scale_x)
                    marker_cy = int((2.0 - raw_y) * scale_y)
                
                # Raw measurement visualization (GREEN) - only if actually detected
                if not is_prediction_only:
                    raw_px = int(raw_x * scale_x)
                    raw_py = int((2.0 - raw_y) * scale_y)  # Flip Y axis
                    
                    # Draw raw measurement position (green circle)
                    cv2.circle(display, (raw_px, raw_py), 8, (0, 255, 0), 2)
                    
                    # Draw raw orientation arrow from marker center (green)
                    arrow_len = 40
                    raw_end_x = int(marker_cx + arrow_len * np.cos(raw_theta))
                    raw_end_y = int(marker_cy - arrow_len * np.sin(raw_theta))
                    cv2.arrowedLine(display, (marker_cx, marker_cy), (raw_end_x, raw_end_y),
                                   (0, 255, 0), 2, tipLength=0.3)
                else:
                    # Draw prediction-only indicator (orange circle)
                    arrow_len = 40
                    cv2.circle(display, (marker_cx, marker_cy), 12, (0, 165, 255), 2)
                    cv2.putText(display, "PREDICTED", (marker_cx + 15, marker_cy),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
                
                # Filtered position (if available)
                if enemy.get('filtered', False):
                    filt_x, filt_y = enemy['kalman_pos'][:2]
                    filt_theta = enemy['kalman_theta']
                    
                    # Get velocity from Kalman state
                    if ENEMY_MARKER_ID in self.kalman_tracker.trackers:
                        tracker = self.kalman_tracker.trackers[ENEMY_MARKER_ID]
                        vx = tracker.state[3]  # vx is at index 3
                        vy = tracker.state[4]  # vy is at index 4
                        speed = np.sqrt(vx**2 + vy**2)
                    else:
                        vx, vy, speed = 0, 0, 0
                    
                    self.raw_positions.append((raw_x, raw_y))
                    self.filtered_positions.append((filt_x, filt_y))
                    self.timestamps.append(len(self.timestamps) / 30.0)
                    
                    # Print values to terminal
                    if not is_prediction_only:
                        print(f"\rRaw: ({raw_x:.4f}, {raw_y:.4f}, {np.degrees(raw_theta):.1f}°) | "
                              f"Kalman: ({filt_x:.4f}, {filt_y:.4f}, {np.degrees(filt_theta):.1f}°) | "
                              f"Vel: ({vx:.3f}, {vy:.3f}) m/s | Speed: {speed:.3f} m/s | "
                              f"Conf: {enemy['confidence']:.2f}", end='')
                    else:
                        print(f"\r[PREDICTION] Kalman: ({filt_x:.4f}, {filt_y:.4f}, {np.degrees(filt_theta):.1f}°) | "
                              f"Vel: ({vx:.3f}, {vy:.3f}) m/s | Speed: {speed:.3f} m/s | "
                              f"Conf: {enemy['confidence']:.2f} ", end='')
                    
                    # Predicted position visualization (RED)
                    pred_px = int(filt_x * scale_x)
                    pred_py = int((2.0 - filt_y) * scale_y)
                    
                    # Draw predicted position (red circle)
                    cv2.circle(display, (pred_px, pred_py), 8, (0, 0, 255), 2)
                    
                    # Draw predicted orientation arrow from marker center (red)
                    pred_end_x = int(marker_cx + arrow_len * np.cos(filt_theta))
                    pred_end_y = int(marker_cy - arrow_len * np.sin(filt_theta))
                    cv2.arrowedLine(display, (marker_cx, marker_cy), (pred_end_x, pred_end_y),
                                   (0, 0, 255), 2, tipLength=0.3)
                    
                    # Draw velocity vector from marker center (BLUE) - scaled by speed
                    if speed > 0.01:  # Only draw if moving
                        vel_scale = 100  # scale factor for visibility
                        vel_end_x = int(marker_cx + vx * vel_scale)
                        vel_end_y = int(marker_cy - vy * vel_scale)
                        cv2.arrowedLine(display, (marker_cx, marker_cy), (vel_end_x, vel_end_y),
                                       (255, 0, 0), 2, tipLength=0.3)
                    
                    # Draw line connecting raw and predicted positions (only if detected)
                    if not is_prediction_only:
                        cv2.line(display, (raw_px, raw_py), (pred_px, pred_py),
                                (255, 255, 0), 1, cv2.LINE_AA)
                    
                    # Display info
                    status_text = "PREDICTION ONLY" if is_prediction_only else "TRACKING"
                    status_color = (0, 165, 255) if is_prediction_only else (255, 255, 255)
                    label = f"Enemy {ENEMY_MARKER_ID} | {status_text} | Speed: {speed:.3f} m/s"
                    cv2.putText(display, label, (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                    
                    if not is_prediction_only:
                        cv2.putText(display, f"Raw (GREEN): ({raw_x:.3f}, {raw_y:.3f})m", (10, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.putText(display, f"Pred (RED): ({filt_x:.3f}, {filt_y:.3f})m", (10, 115),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    cv2.putText(display, f"Velocity (BLUE): ({vx:.3f}, {vy:.3f}) m/s", (10, 140),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                    cv2.putText(display, f"Confidence: {enemy['confidence']:.2f}", (10, 165),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display status
            status_y = 30
            if self.tracker.extrinsics_valid:
                status = f"TRACKING | Refs: {len(ref_markers)}/4"
                status_color = (0, 255, 0)
            else:
                status = f"CALIBRATING | Refs: {len(ref_markers)}/4"
                status_color = (0, 165, 255)
            cv2.putText(display, status, (10, status_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Display parameters on frame
            cv2.putText(display, f"Process Noise: {self.process_noise:.4f}", 
                       (10, display.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(display, f"Measurement Noise: {self.measurement_noise:.4f}", 
                       (10, display.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            cv2.imshow('Kalman Tuner', display)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE - reset extrinsics
                self.tracker.extrinsics_valid = False
                self.tracker.rvec_cam = None
                self.tracker.tvec_cam = None
                self.kalman_tracker.trackers.clear()
                print("\n! Extrinsics reset - recalibrating...")
            elif key == ord('q'):
                self.process_noise *= 1.5
                if self.kalman_tracker:
                    self.kalman_tracker.process_noise = self.process_noise
                print(f"\nProcess noise increased: {self.process_noise:.4f}")
            elif key == ord('a'):
                self.process_noise /= 1.5
                if self.kalman_tracker:
                    self.kalman_tracker.process_noise = self.process_noise
                print(f"\nProcess noise decreased: {self.process_noise:.4f}")
            elif key == ord('w'):
                self.measurement_noise *= 1.5
                if self.kalman_tracker:
                    self.kalman_tracker.measurement_noise = self.measurement_noise
                print(f"\nMeasurement noise increased: {self.measurement_noise:.4f}")
            elif key == ord('s'):
                self.measurement_noise /= 1.5
                if self.kalman_tracker:
                    self.kalman_tracker.measurement_noise = self.measurement_noise
                print(f"\nMeasurement noise decreased: {self.measurement_noise:.4f}")
            elif key == ord('r'):
                self.process_noise = 0.01
                self.measurement_noise = 0.1
                if self.kalman_tracker:
                    self.kalman_tracker.process_noise = self.process_noise
                    self.kalman_tracker.measurement_noise = self.measurement_noise
                    self.kalman_tracker.trackers.clear()
                print("\nReset to defaults")
                print(f"Process Noise: {self.process_noise:.4f}")
                print(f"Measurement Noise: {self.measurement_noise:.4f}")
            elif key == ord('p'):
                self.plot_results()
        
        cap.release()
        cv2.destroyAllWindows()
    
    def print_params(self):
        print(f"  Process Noise (Q):     {self.process_noise:.4f}")
        print(f"  Measurement Noise (R): {self.measurement_noise:.4f}")
    
    def plot_results(self):
        if len(self.raw_positions) < 10:
            print("\nNot enough data to plot (need at least 10 samples)")
            return
        
        raw_arr = np.array(self.raw_positions)
        filt_arr = np.array(self.filtered_positions)
        times = np.array(self.timestamps)
        
        # Plot X and Y positions
        self.ax1.clear()
        self.ax1.plot(times, raw_arr[:, 0], 'b-', alpha=0.5, label='Raw X')
        self.ax1.plot(times, filt_arr[:, 0], 'r-', linewidth=2, label='Filtered X')
        self.ax1.set_ylabel('X Position (m)')
        self.ax1.legend()
        self.ax1.grid(True)
        self.ax1.set_title(f'Q={self.process_noise:.4f}, R={self.measurement_noise:.4f}')
        
        self.ax2.clear()
        self.ax2.plot(times, raw_arr[:, 1], 'b-', alpha=0.5, label='Raw Y')
        self.ax2.plot(times, filt_arr[:, 1], 'r-', linewidth=2, label='Filtered Y')
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Y Position (m)')
        self.ax2.legend()
        self.ax2.grid(True)
        
        plt.draw()
        plt.pause(0.001)
        
        # Compute statistics
        raw_std_x = np.std(raw_arr[:, 0])
        raw_std_y = np.std(raw_arr[:, 1])
        filt_std_x = np.std(filt_arr[:, 0])
        filt_std_y = np.std(filt_arr[:, 1])
        
        print("\n" + "="*60)
        print("STATISTICS")
        print("="*60)
        print(f"Raw X std:      {raw_std_x*1000:.2f} mm")
        print(f"Filtered X std: {filt_std_x*1000:.2f} mm")
        print(f"Improvement X:  {(1 - filt_std_x/raw_std_x)*100:.1f}%")
        print(f"\nRaw Y std:      {raw_std_y*1000:.2f} mm")
        print(f"Filtered Y std: {filt_std_y*1000:.2f} mm")
        print(f"Improvement Y:  {(1 - filt_std_y/raw_std_y)*100:.1f}%")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera', type=int, default=1)
    args = parser.parse_args()
    
    tuner = KalmanTuner(camera_id=args.camera)
    tuner.run()