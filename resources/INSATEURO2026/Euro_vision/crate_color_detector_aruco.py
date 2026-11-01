"""
Crate Color Detector — ROBOT CAMERA (ArUco Only)
=================================================
For use with a camera mounted INSIDE the robot.
Detects yellow and blue crates purely by reading their ArUco markers.
The markers are automatically sorted from left-to-right on the screen.

No fixed coordinates needed. No camera calibration needed.

Marker IDs:
  - 36 = Blue Zone ('B')
  - 47 = Yellow Zone ('Y')

Usage:
    python crate_color_detector_aruco.py

Controls:
    c - Capture and classify crates
    d - Toggle debug visualization
    s - Save current annotated frame
    q - Quit
"""

import cv2
import numpy as np
import sys
from typing import List, Dict


# ============================================================================
# CONFIGURATION
# ============================================================================

# Camera index (0 = default, 1 = second camera, 2 = third, etc.)
CAMERA_INDEX: int = 2

# ArUco dictionary and crate marker IDs
ARUCO_DICT_TYPE = cv2.aruco.DICT_4X4_50
BLUE_MARKER_ID = 36
YELLOW_MARKER_ID = 47
ROTTEN_MARKER_ID = 41

# Map IDs to color labels
MARKER_COLORS = {
    BLUE_MARKER_ID: 'B',
    YELLOW_MARKER_ID: 'Y',
    ROTTEN_MARKER_ID: 'R'  # Rotten
}


# ============================================================================
# DETECTION LOGIC
# ============================================================================

def get_aruco_crates(frame: np.ndarray) -> List[Dict]:
    """
    Detect ArUco markers, filter for crates, calculate centers, 
    and sort them from left to right.
    
    Returns:
        List of dictionaries containing crate info, sorted by X coordinate.
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_TYPE)
    aruco_params = cv2.aruco.DetectorParameters()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)
    
    crates = []
    
    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            marker_id = int(marker_id)
            if marker_id in MARKER_COLORS:
                # Calculate center point
                marker_corners = corners[i][0]
                cx = int(np.mean(marker_corners[:, 0]))
                cy = int(np.mean(marker_corners[:, 1]))
                
                color_label = MARKER_COLORS[marker_id]
                
                crates.append({
                    'id': marker_id,
                    'color': color_label,
                    'cx': cx,
                    'cy': cy,
                    'corners': marker_corners
                })
    
    # Sort crates left-to-right based on center X coordinate
    crates.sort(key=lambda c: c['cx'])
    return crates


# ============================================================================
# VISUALIZATION
# ============================================================================

def draw_debug_overlay(frame: np.ndarray, crates: List[Dict]) -> np.ndarray:
    """Draw bounding boxes and labels for each detected crate."""
    vis = frame.copy()
    
    for i, crate in enumerate(crates):
        corners = crate['corners']
        color_label = crate['color']
        cx, cy = crate['cx'], crate['cy']
        
        # Decide box color
        if color_label == 'Y':
            box_color = (0, 255, 255)  # Yellow
        elif color_label == 'B':
            box_color = (255, 0, 0)    # Blue
        elif color_label == 'R':
            box_color = (0, 0, 0)      # Black for rotten
        else:
            box_color = (128, 128, 128)
            
        # Draw bounding box roughly around marker
        rect = cv2.boundingRect(corners)
        x, y, w, h = rect
        padding = 10
        cv2.rectangle(vis, (x - padding, y - padding), 
                     (x + w + padding, y + h + padding), box_color, 3)
                     
        # Draw center crosshair
        cv2.drawMarker(vis, (cx, cy), box_color, cv2.MARKER_CROSS, 20, 2)
        
        # Draw text label
        label = f"#{i}: {color_label} (ID:{crate['id']})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        
        # Label background
        label_y = max(y - padding - 10, text_size[1] + 5)
        cv2.rectangle(vis,
                      (x - padding, label_y - text_size[1] - 5),
                      (x - padding + text_size[0] + 10, label_y + 5),
                      (0, 0, 0), -1)
        cv2.putText(vis, label, (x - padding + 5, label_y), font, font_scale, box_color, thickness)
        
    return vis


def draw_result_banner(frame: np.ndarray, colors_array: List[str]) -> np.ndarray:
    """Draw the final array result at the top of the frame."""
    vis = frame.copy()
    h, w = vis.shape[:2]
    
    cv2.rectangle(vis, (0, 0), (w, 50), (0, 0, 0), -1)
    
    result_str = f"Colors (Left->Right): {colors_array}"
    cv2.putText(vis, result_str, (10, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    return vis


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("  CRATE DETECTOR (ROBOT VIEW / ARUCO ONLY)")
    print("  Dynamically detects markers, sorts left-to-right")
    print("=" * 60)
    print(f"  Camera: {CAMERA_INDEX}")
    print("  Controls:")
    print("    c - Capture & print order")
    print("    d - Toggle debug overlay")
    print("    s - Save frame")
    print("    q - Quit")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=CAMERA_INDEX, help="Camera index")
    args = parser.parse_args()
    
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"\n[ERROR] Could not open camera {args.camera}")
        sys.exit(1)
    
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[OK] Camera opened: {frame_w}x{frame_h}")
    
    show_debug = True
    frame_count = 0
    colors_array = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame")
            break
        
        # Detect and sort crates
        crates = get_aruco_crates(frame)
        colors_array = [c['color'] for c in crates]
        
        # Build display
        if show_debug:
            display = draw_debug_overlay(frame, crates)
        else:
            display = frame.copy()
            
        display = draw_result_banner(display, colors_array)
        
        cv2.imshow('ArUco Crate Detector', display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
            
        elif key == ord('c'):
            print(f"\n{'=' * 40}")
            print(f"  CAPTURE RESULT")
            print(f"  Sequence: {colors_array}")
            for i, c in enumerate(crates):
                print(f"  #{i}: {c['color']} (ID:{c['id']}, X:{c['cx']})")
            print(f"{'=' * 40}\n")
            
        elif key == ord('d'):
            show_debug = not show_debug
            
        elif key == ord('s'):
            filename = f"aruco_crates_{frame_count:04d}.jpg"
            cv2.imwrite(filename, display)
            print(f"[SAVED] {filename}")
            frame_count += 1
            
    cap.release()
    cv2.destroyAllWindows()
    
    # Final output
    print(f"\nFinal color array: {colors_array}")
    return colors_array


if __name__ == "__main__":
    main()
