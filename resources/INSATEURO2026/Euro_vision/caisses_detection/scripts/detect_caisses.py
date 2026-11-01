"""
Real-time Caisse Detection Script
Detects caisses de noisettes from camera feed and displays results.
"""

import cv2
import numpy as np
import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from caisses_detection.src.caisse_detector import CaisseDetector


def load_camera_calibration(calib_path: str):
    """Load camera calibration parameters."""
    with open(calib_path, 'r') as f:
        calib = json.load(f)
    K = np.array(calib['camera_matrix'])
    D = np.array(calib['dist_coeffs'])
    return K, D


def load_extrinsics(extrinsics_path: str):
    """Load camera extrinsics (world to camera transform)."""
    with open(extrinsics_path, 'r') as f:
        extrinsics = json.load(f)
    T_world_cam = np.array(extrinsics['T_world_cam'])
    return T_world_cam


def main():
    parser = argparse.ArgumentParser(description='Detect caisses de noisettes in real-time')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID')
    parser.add_argument('--config', type=str, 
                       default='caisses_detection/config/caisse_config.yaml',
                       help='Path to caisse configuration')
    parser.add_argument('--calibration', type=str,
                       default='calibration/camera_calibration.json',
                       help='Path to camera calibration')
    parser.add_argument('--extrinsics', type=str,
                       default='map_anchors/config/camera_extrinsics.json',
                       help='Path to camera extrinsics')
    parser.add_argument('--visualize', action='store_true',
                       help='Show visualization window')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video file path')
    args = parser.parse_args()
    
    # Load calibration
    print("Loading camera calibration...")
    K, D = load_camera_calibration(args.calibration)
    
    # Load extrinsics
    print("Loading camera extrinsics...")
    T_world_cam = load_extrinsics(args.extrinsics)
    
    # Initialize detector
    print("Initializing caisse detector...")
    detector = CaisseDetector(args.config, K, D)
    
    # Open camera
    print(f"Opening camera {args.camera}...")
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Error: Cannot open camera {args.camera}")
        return
    
    # Video writer
    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
    
    print("\n=== Caisse Detection Started ===")
    print("Press 'q' to quit\n")
    
    frame_count = 0
    total_detected = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect caisses
            caisses = detector.detect_caisses(frame, T_world_cam)
            total_detected += len(caisses)
            
            # Print detection info
            if frame_count % 30 == 0:  # Every second at 30fps
                print(f"Frame {frame_count}: Detected {len(caisses)} caisses")
                for caisse in caisses:
                    print(f"  {caisse['team']} (ID {caisse['aruco_id']}): "
                          f"x={caisse['position']['x']:.3f}, "
                          f"y={caisse['position']['y']:.3f}, "
                          f"θ={caisse['position']['theta']:.2f}")
            
            # Visualize
            if args.visualize or args.output:
                vis_frame = detector.visualize_detections(frame, caisses)
                
                # Add stats
                stats_text = f"Frame: {frame_count} | Detected: {len(caisses)}/48"
                cv2.putText(vis_frame, stats_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if args.visualize:
                    cv2.imshow('Caisse Detection', vis_frame)
                
                if writer:
                    writer.write(vis_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Summary
        print("\n=== Detection Summary ===")
        print(f"Total frames: {frame_count}")
        print(f"Average caisses per frame: {total_detected / max(frame_count, 1):.2f}")
        print(f"Expected: 48 caisses")


if __name__ == '__main__':
    main()
