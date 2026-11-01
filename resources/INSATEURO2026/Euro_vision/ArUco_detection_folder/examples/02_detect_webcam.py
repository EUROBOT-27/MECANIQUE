"""
Example: Detect ArUco Markers from Webcam
This script demonstrates real-time ArUco marker detection with pose estimation.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aruco_tools import MarkerDetector
import cv2
import numpy as np


def main():
    print("=" * 70)
    print("ArUco Marker Detector - Webcam Mode")
    print("=" * 70)
    
    # Initialize detector
    detector = MarkerDetector(
        dictionary_type=cv2.aruco.DICT_4X4_50,
        marker_length=0.05  # 5cm physical size (adjust based on your markers)
    )
    
    # Open webcam
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam!")
        print("\nAlternatively, run detection on an image:")
        print("  python examples/03_detect_from_image.py path/to/image.jpg")
        return
    
    # Set camera resolution (optional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\nCamera opened successfully!")
    print("\nControls:")
    print("  • Press 'q' to quit")
    print("  • Press 's' to save current frame")
    print("  • Press 'p' to toggle pose display")
    print("=" * 70)
    
    frame_count = 0
    show_pose = True
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("ERROR: Could not read frame from camera")
            break
        
        # Process frame
        processed_frame, pose_info = detector.process_frame(
            frame,
            draw_markers=True,
            draw_axis=True
        )
        
        # Display detection information
        info_y = 30
        if pose_info:
            for info in pose_info:
                marker_type = detector.classify_marker(info['id'])
                
                # Display on frame
                text = f"[{marker_type}] ID:{info['id']} | Pos:({info['position']['x']:.3f}, {info['position']['y']:.3f}, {info['position']['z']:.3f})m"
                cv2.putText(processed_frame, text, (10, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                info_y += 25
                
                # Print to console if pose display is enabled
                if show_pose:
                    print(f"\r[{marker_type}] ID:{info['id']:2d} | "
                          f"x:{info['position']['x']:6.3f}m y:{info['position']['y']:6.3f}m z:{info['position']['z']:6.3f}m | "
                          f"yaw:{info['yaw_deg']:6.1f}°", end='')
        else:
            cv2.putText(processed_frame, "No markers detected", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            if show_pose:
                print("\rNo markers detected", end=' ' * 50)
        
        # Display frame
        cv2.imshow('ArUco Detection - Press Q to quit', processed_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n\nQuitting...")
            break
        elif key == ord('s'):
            os.makedirs('output', exist_ok=True)
            filename = f"output/detected_frame_{frame_count:04d}.jpg"
            cv2.imwrite(filename, processed_frame)
            print(f"\n[SAVED] Frame saved to: {filename}")
            frame_count += 1
        elif key == ord('p'):
            show_pose = not show_pose
            status = "ON" if show_pose else "OFF"
            print(f"\n[INFO] Pose display: {status}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\nCamera closed. Goodbye!")


if __name__ == "__main__":
    main()
