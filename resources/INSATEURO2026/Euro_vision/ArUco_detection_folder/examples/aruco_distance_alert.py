#!/usr/bin/env python3
"""
ArUco distance alert

Detect an ArUco marker and compute the camera-to-marker distance using intrinsics (Camo iPhone JSON by default).
The script displays a live OpenCV window, prints per-frame distance lines to stdout (parseable), and prints a final
JSON object with the last measured distance on exit.

Usage example (PowerShell):
    python aruco_distance_alert.py --camera 2 --intrinsics "..\..\camera_calibration_folder\calibration\iphone_xr_720p.json" --marker-id 30 --threshold-cm 80

"""

import argparse
import json
import os
import time
import math

import cv2
import numpy as np


def load_intrinsics(path_candidates):
    for p in path_candidates:
        if p and os.path.exists(p):
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                # Accept both formats: camera_matrix/dist_coeffs or camera_matrix/distortion_coefficients
                if 'camera_matrix' in data:
                    K = np.array(data['camera_matrix'], dtype=np.float32)
                elif 'camera_matrix' in data.get('intrinsics', {}):
                    K = np.array(data['intrinsics']['camera_matrix'], dtype=np.float32)
                else:
                    continue

                if 'dist_coeffs' in data:
                    dist = np.array(data['dist_coeffs'], dtype=np.float32)
                elif 'distortion_coefficients' in data:
                    # Some files have a nested array
                    dist = np.array(data['distortion_coefficients'], dtype=np.float32)
                    if dist.ndim > 1:
                        dist = dist.flatten()
                else:
                    dist = np.zeros(5, dtype=np.float32)

                return K, dist
            except Exception:
                continue

    return None, None


# ROS support removed: distances are printed to stdout for external integration.


def main():
    parser = argparse.ArgumentParser(description='ArUco distance alert (phone intrinsics friendly)')
    parser.add_argument('--camera', type=int, default=1, help='Camera device index (Camo often at 2)')
    parser.add_argument('--intrinsics', type=str,
                        default=os.path.join('..', '..', 'camera_calibration_folder', 'calibration', 'iphone_xr_720p.json'),
                        help='Path to camera intrinsics JSON')
    parser.add_argument('--marker-id', type=int, default=None, help='Marker ID to watch (if omitted, any marker)')
    parser.add_argument('--threshold-cm', type=float, default=80.0, help='Alert threshold in cm')
    # (ROS support removed) -- this script prints distances to stdout for external integration
    parser.add_argument('--camera-width', type=int, default=None, help='Optional force width')
    parser.add_argument('--camera-height', type=int, default=None, help='Optional force height')
    args = parser.parse_args()

    # Load intrinsics
    intr_candidates = [args.intrinsics,
                       os.path.join('full_pipeline', 'calibration_data', 'my_camera.json'),
                       os.path.join('camera_calibration_folder', 'calibration', 'camera_calibration.json')]

    K, dist = load_intrinsics(intr_candidates)
    if K is None:
        print('❌ Could not find valid intrinsics. Provide --intrinsics path to JSON.')
        return

    print('Loaded intrinsics:')
    print(K)
    print('dist coeffs:', dist)

    # ROS support removed; distances are printed to stdout.

    # Setup ArUco
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"❌ Cannot open camera {args.camera}")
        return

    if args.camera_width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.camera_width)
    if args.camera_height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.camera_height)

    last_alert_time = 0
    alert_cooldown = 1.0  # seconds between printed alerts
    last_measured_cm = None

    print('Starting detection loop. Press q to quit.')

    while True:
        ret, frame = cap.read()
        if not ret:
            print('Frame grab failed')
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        measured_cm = None
        if ids is not None and len(ids) > 0:
            # Estimate pose for all detected markers
            # markerLength is unknown here; pose Z scales with marker size. If you know marker size (m), set marker_length_m
            marker_length_m = 0.10  # default 7 cm; change if your marker differs
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length_m, K, dist)

            # Find the marker to watch
            target_idx = None
            if args.marker_id is None:
                # choose the closest marker (smallest z)
                zs = [t[0][2] for t in tvecs]
                target_idx = int(np.argmin(zs))
            else:
                for i, mid in enumerate(ids.flatten()):
                    if int(mid) == int(args.marker_id):
                        target_idx = i
                        break

            if target_idx is not None:
                t = tvecs[target_idx][0]
                z_m = float(t[2])
                measured_cm = z_m * 100.0
                last_measured_cm = measured_cm

                # Draw axis and marker outline
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                cv2.drawFrameAxes(frame, K, dist, rvecs[target_idx], tvecs[target_idx], marker_length_m * 0.5)

                # Project marker translation vector (camera frame) into image to draw a 2D arrow.
                # We'll draw the vector from the marker center projected point to an offset using tvec.
                # Compute marker center in image space using the average of its corner pixels
                c = corners[target_idx][0]
                center_px = np.mean(c, axis=0)

                # Project a point in camera frame offset by the translation vector
                # We'll choose an offset along the X and Y camera axes proportional to the translation
                # Create a 3D point in camera coordinates: origin at marker translation, plus small scale on x,y
                arrow_scale = 0.03  # meters for visible arrow length
                arrow_cam_point = np.array([[t[0] + arrow_scale, t[1], t[2]]], dtype=np.float32)
                # Project
                proj, _ = cv2.projectPoints(arrow_cam_point, np.zeros(3), np.zeros(3), K, dist)
                proj_pt = proj[0][0]
                start_pt = (int(center_px[0]), int(center_px[1]))
                end_pt = (int(proj_pt[0]), int(proj_pt[1]))
                cv2.arrowedLine(frame, start_pt, end_pt, (255, 0, 0), 2, tipLength=0.2)

                # Overlay distance text and ID near the marker
                label = f"ID:{int(ids.flatten()[target_idx])} Dist: {measured_cm:.1f} cm"
                cv2.putText(frame, label, (start_pt[0] - 50, start_pt[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Always print the latest measured distance to stdout in a simple line for parsing
                print(f"DISTANCE_CM {int(ids.flatten()[target_idx])} {measured_cm:.2f}")

                # Alert logic
                now = time.time()
                if measured_cm <= args.threshold_cm and (now - last_alert_time) > alert_cooldown:
                    print(f"🔔 ALERT: marker {ids.flatten()[target_idx]} within threshold: {measured_cm:.1f} cm <= {args.threshold_cm} cm")
                    last_alert_time = now
                    # No ROS: just continue. External systems can parse the printed "DISTANCE_CM" lines.

        else:
            cv2.putText(frame, "No marker detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Show threshold line/status
        if measured_cm is not None:
            status = 'SAFE'
            color = (0, 255, 0)
            if measured_cm <= args.threshold_cm:
                status = 'ALERT'
                color = (0, 0, 255)
            cv2.putText(frame, f"Threshold: {args.threshold_cm:.1f} cm  Status: {status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow('ArUco Distance Alert', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    finally:
        # On exit, print a final JSON object with last measured distance if available.
        # We attempt to read last_measured_cm from globals (set inside main). If not present, return null.
        lm = None
        try:
            lm = globals().get('last_measured_cm', None)
        except Exception:
            lm = None

        out = {'last_measured_cm': None}
        if lm is not None:
            out['last_measured_cm'] = float(lm)
            print(json.dumps(out))
            # exit code 0 indicates success with a measurement
            os._exit(0)
        else:
            print(json.dumps(out))
            # non-zero exit to indicate no measurement captured
            os._exit(2)
