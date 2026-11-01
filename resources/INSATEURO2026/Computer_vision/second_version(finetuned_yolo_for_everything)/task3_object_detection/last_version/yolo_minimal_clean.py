import cv2
import numpy as np
import os
from ultralytics import YOLO
import time
from collections import Counter

def is_green_cube(frame, x1, y1, x2, y2, min_green_ratio=0.10):
    """
    Check if the detected cube is predominantly green.
    Simplified version for LED-lit environment.
    """
    # Extract the region of interest
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return False
    
    # Convert to HSV for color detection
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Define green color ranges (for well-lit environment with LED)
    # Range 1: Main green range
    lower_green1 = np.array([45, 50, 50])
    upper_green1 = np.array([80, 255, 255])
    
    # Range 2: Light green range  
    lower_green2 = np.array([35, 40, 40])
    upper_green2 = np.array([45, 255, 255])
    
    # Create masks for green ranges
    mask1 = cv2.inRange(hsv_roi, lower_green1, upper_green1)
    mask2 = cv2.inRange(hsv_roi, lower_green2, upper_green2)
    
    # Combine green masks
    green_mask = cv2.bitwise_or(mask1, mask2)
    
    # Basic morphological operations to clean up noise
    kernel = np.ones((3,3), np.uint8)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    
    # Calculate green ratio
    total_pixels = roi.shape[0] * roi.shape[1]
    green_pixels = cv2.countNonZero(green_mask)
    green_ratio = green_pixels / total_pixels
    
    # Debug info
    if green_ratio > 0.05:
        print(f"    Green cube analysis: ratio={green_ratio:.3f}, threshold={min_green_ratio}")
    
    return green_ratio >= min_green_ratio

def detect_object_from_camera(show_window=True):
    """
    Detects objects using YOLOv8 from the webcam and returns the detected object continuously.
    - All triangles are accepted (any color)
    - Only green cubes are accepted
    Optimized for LED-lit environment.
    Camera stays open for continuous detection - controlled externally by ROS.
    """
    
    RUNNING_ON_PI = False
    if RUNNING_ON_PI:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    # Path to YOLO model
    model_path = "/home/ubuntu/ensi_workspace/models/200epoch.pt" if RUNNING_ON_PI else r"C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Computer_vision\second_version(finetuned_yolo_for_everything)\task3_object_detection\last_version\200epoch.onnx"
    model = YOLO(model_path)
    
    # Define expected class names
    class_names = {0: 'cube', 1: 'triangle'}
    
    print(f"Model loaded: {model_path}")
    print(f"Expected classes: {list(class_names.values())}")
    print("Starting continuous detection...")
    print("Detection rules: ALL triangles, GREEN cubes only")
    
    cap = cv2.VideoCapture(0 if RUNNING_ON_PI else 1)
    if not cap.isOpened():
        print("Cannot open camera")
        return None

    # Continuous detection - no time limit
    last_detected_object = None
    frame_count = 0

    while True:  # Run continuously
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            continue
        
        frame_count += 1

        # Run YOLO inference
        results = model.predict(frame, conf=0.3, verbose=False)
        boxes = results[0].boxes

        # Find best detection for this frame
        if len(boxes) > 0:
            # Find the best detection (highest confidence)
            best_box = max(boxes, key=lambda box: float(box.conf[0]))
            cls_id = int(best_box.cls[0])
            conf = float(best_box.conf[0])
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            
            # Check if detected class is in our expected classes
            if cls_id in class_names:
                class_value = class_names[cls_id]
                
                if class_value == 'triangle':
                    # Accept ALL triangles regardless of color
                    last_detected_object = class_value
                    print(f"Frame {frame_count}: {class_value} ACCEPTED (conf: {conf:.2f})")
                    
                    if show_window and not RUNNING_ON_PI:
                        detection_frame = frame.copy()
                        cv2.rectangle(detection_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(detection_frame, f"{class_value} {conf:.2f}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.imshow("YOLO Object Detection", detection_frame)
                        
                elif class_value == 'cube':
                    # Only accept GREEN cubes
                    if is_green_cube(frame, x1, y1, x2, y2):
                        last_detected_object = class_value
                        print(f"Frame {frame_count}: GREEN {class_value} ACCEPTED (conf: {conf:.2f})")
                        
                        if show_window and not RUNNING_ON_PI:
                            detection_frame = frame.copy()
                            cv2.rectangle(detection_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(detection_frame, f"GREEN {class_value} {conf:.2f}", (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            cv2.imshow("YOLO Object Detection", detection_frame)
                    else:
                        # Cube detected but not green - reject
                        print(f"Frame {frame_count}: {class_value} REJECTED - not green (conf: {conf:.2f})")
                        if show_window and not RUNNING_ON_PI:
                            detection_frame = frame.copy()
                            cv2.rectangle(detection_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.putText(detection_frame, f"NOT GREEN {class_value}", (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            cv2.imshow("YOLO Object Detection", detection_frame)
            else:
                # Invalid detection - not a cube or triangle
                print(f"Frame {frame_count}: Unknown class_id={cls_id}, conf={conf:.2f}")
                if show_window and not RUNNING_ON_PI:
                    cv2.imshow("YOLO Object Detection", frame)
        else:
            print(f"Frame {frame_count}: No detections")
            if show_window and not RUNNING_ON_PI:
                cv2.imshow("YOLO Object Detection", frame)

        if show_window and not RUNNING_ON_PI:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    return last_detected_object

# Example usage:
if __name__ == "__main__":
    obj = detect_object_from_camera(show_window=True)
    print("Last detected object:", obj)