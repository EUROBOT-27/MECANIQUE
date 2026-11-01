#!/usr/bin/env python3
"""
Single Marker Distance Validation
Test the accuracy of Z-distance (depth) measurements by moving a marker
to known distances from the camera.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aruco_tools.marker_detector import MarkerDetector
import cv2
import numpy as np

def test_single_marker_distance():
    """
    Test Z-distance accuracy by moving marker to known distances.
    
    Instructions:
    1. Place one ArUco marker on a ruler or measuring tape
    2. Move it to exact distances: 30cm, 50cm, 70cm, 1m
    3. Compare detected vs actual distance
    """
    
    print("=" * 70)
    print("SINGLE MARKER DISTANCE TEST")
    print("=" * 70)
    print("\n📏 Instructions:")
    print("1. Place one ArUco marker on a measuring surface")
    print("2. Move it to these distances from camera:")
    print("   • 30 cm - Press '1' to record")
    print("   • 50 cm - Press '2' to record") 
    print("   • 70 cm - Press '3' to record")
    print("   • 100 cm - Press '4' to record")
    print("3. Press 'q' to quit and see results")
    print("=" * 70)
    
    # Load calibration
    calibration_path = r"C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Euro_vision\camera_calibration_folder\calibration\camera_calibration.json"
    try:
        with open(calibration_path, 'r') as f:
            cal_data = json.load(f)
        camera_matrix = np.array(cal_data['camera_matrix'])
        dist_coeffs = np.array(cal_data['distortion_coefficients'])
    except:
        print("❌ Could not load calibration!")
        return
    
    # Initialize detector
    detector = MarkerDetector(
        dictionary_type=cv2.aruco.DICT_4X4_50,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        marker_length=0.07
    )
    
    # Open camera
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        return
    
    width, height = cal_data['image_size']
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # Storage for measurements
    measurements = {
        30: [],   # 30cm measurements
        50: [],   # 50cm measurements  
        70: [],   # 70cm measurements
        100: []   # 100cm measurements
    }
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.undistort(frame, camera_matrix, dist_coeffs)
        corners, ids, rejected = detector.detect_markers(frame)
        
        if ids is not None and len(ids) > 0:
            detector.draw_detected_markers(frame, corners, ids)
            rvecs, tvecs = detector.estimate_pose(corners)
            frame = detector.draw_axis(frame, rvecs, tvecs)
            
            pose_info = detector.get_pose_info(rvecs, tvecs, ids)[0]
            distance_m = pose_info['position']['z']
            distance_cm = distance_m * 100
            
            # Display current distance
            cv2.putText(frame, f"Distance: {distance_cm:.1f} cm", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Show instructions
            cv2.putText(frame, "Press: 1=30cm, 2=50cm, 3=70cm, 4=100cm", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "No marker detected", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Show current measurements count
        y_pos = 100
        for distance, measures in measurements.items():
            if measures:
                avg = np.mean(measures)
                cv2.putText(frame, f"{distance}cm: {len(measures)} measures (avg: {avg:.1f}cm)", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y_pos += 25
        
        cv2.imshow('Distance Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key in [ord('1'), ord('2'), ord('3'), ord('4')] and ids is not None:
            distance_map = {ord('1'): 30, ord('2'): 50, ord('3'): 70, ord('4'): 100}
            expected_distance = distance_map[key]
            
            pose_info = detector.get_pose_info(rvecs, tvecs, ids)[0]
            measured_distance = pose_info['position']['z'] * 100
            measurements[expected_distance].append(measured_distance)
            
            print(f"📏 {expected_distance}cm measurement: {measured_distance:.1f}cm (error: {abs(measured_distance - expected_distance):.1f}cm)")
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Analysis
    print("\n" + "=" * 60)
    print("DISTANCE ACCURACY RESULTS")
    print("=" * 60)
    
    for expected, measures in measurements.items():
        if measures:
            avg = np.mean(measures)
            std = np.std(measures)
            error = abs(avg - expected)
            error_percent = (error / expected) * 100
            
            print(f"\n{expected}cm measurements:")
            print(f"  Count: {len(measures)}")
            print(f"  Average: {avg:.2f}cm")
            print(f"  Std dev: {std:.2f}cm")
            print(f"  Error: {error:.2f}cm ({error_percent:.1f}%)")
            print(f"  Accuracy: {'✅ GOOD' if error < 2 else '⚠️ FAIR' if error < 5 else '❌ POOR'}")

if __name__ == "__main__":
    test_single_marker_distance()