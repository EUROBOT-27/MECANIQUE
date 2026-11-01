"""
ArUco ID Detector
Simple script to detect ArUco markers and display their IDs.
Useful for identifying unknown markers.
"""

import cv2
import argparse


def main():
    parser = argparse.ArgumentParser(description='Detect ArUco marker IDs from camera')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID')
    parser.add_argument('--dict', type=str, default='DICT_4X4_50',
                       help='ArUco dictionary name')
    args = parser.parse_args()
    
    # Setup ArUco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(
        getattr(cv2.aruco, args.dict)
    )
    aruco_params = cv2.aruco.DetectorParameters()
    
    # Open camera
    cap = cv2.VideoCapture(args.camera)
    print(f"=== ArUco ID Detector ===")
    print(f"Dictionary: {args.dict}")
    print("Press 'q' to quit\n")
    
    detected_ids = set()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect markers
        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)
        
        # Draw detected markers
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            for i, marker_id in enumerate(ids.flatten()):
                if marker_id not in detected_ids:
                    detected_ids.add(marker_id)
                    print(f"✓ Detected new marker: ID {marker_id}")
                
                # Draw ID near marker
                corner = corners[i][0]
                center = corner.mean(axis=0).astype(int)
                cv2.putText(frame, f"ID: {marker_id}", 
                           tuple(center - [0, 30]),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # Show summary
        summary = f"Detected IDs: {sorted(detected_ids)}" if detected_ids else "No markers detected"
        cv2.putText(frame, summary, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('ArUco ID Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n=== Summary ===")
    print(f"Total unique markers detected: {len(detected_ids)}")
    print(f"IDs: {sorted(detected_ids)}")


if __name__ == '__main__':
    main()
