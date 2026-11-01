from ultralytics import YOLO
import cv2
import numpy as np
import os

def detect_number_from_camera(show_window=True):
    """
    Detects numbers using YOLOv8 from the webcam continuously.
    Returns: last_detected_number (str or None)
    Camera stays open for continuous detection - controlled externally by ROS.
    """
    
    RUNNING_ON_PI = False
    if RUNNING_ON_PI:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    # Path to YOLO .pt model (update as needed)
    model_path = "/home/ubuntu/ensi_workspace/models/best_3.pt" if RUNNING_ON_PI else r"C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Computer_vision\second_version(finetuned_yolo_for_everything)\second_task_number_detection\models\best_2.pt"
    model = YOLO(model_path)

    # Define class names (update these based on your model)
    class_names = {0: '3', 1: '5', 2: '6', 3: '9'}  # Update according to your classes

    print(f"Model loaded: {model_path}")
    print(f"Expected classes: {list(class_names.values())}")
    print("Starting continuous number detection...")

    cap = cv2.VideoCapture(0 if RUNNING_ON_PI else 1)
    if not cap.isOpened():
        print("Cannot open camera")
        return None

    # Continuous detection - no time limit
    last_detected_number = None
    frame_count = 0

    while True:  # Run continuously
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            continue
        
        frame_count += 1

        # Minimal processing: Gaussian blur and CLAHE
        blurred = cv2.GaussianBlur(frame, (3, 3), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)
        processed = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)

        # Run YOLO inference
        results = model.predict(processed, conf=0.3, verbose=False)
        boxes = results[0].boxes

        # Process YOLO detections
        frame_detection = None
        if len(boxes) > 0:
            # Find the best detection (highest confidence)
            best_box = max(boxes, key=lambda box: float(box.conf[0]))
            cls_id = int(best_box.cls[0])
            conf = float(best_box.conf[0])
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            
            # Check if detected class is in our expected classes (3, 5, 6, 9)
            if cls_id in class_names:
                # Valid detection - this is a number we're looking for
                class_value = class_names[cls_id]
                last_detected_number = class_value
                
                print(f"Frame {frame_count}: {class_value} (conf: {conf:.2f})")

                if show_window and not RUNNING_ON_PI:
                    # Draw bounding box and label
                    yolo_frame = frame.copy()
                    cv2.rectangle(yolo_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(yolo_frame, f"YOLO: {class_value} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    cv2.imshow("YOLO Number Detection", yolo_frame)
            else:
                # Invalid detection - not a number we're looking for (3, 5, 6, 9)
                print(f"Frame {frame_count}: Invalid class_id={cls_id}, conf={conf:.2f}")
                if show_window and not RUNNING_ON_PI:
                    cv2.imshow("YOLO Number Detection", frame)
        else:
            print(f"Frame {frame_count}: No detections")
            if show_window and not RUNNING_ON_PI:
                cv2.imshow("YOLO Number Detection", frame)

        if show_window and not RUNNING_ON_PI:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    return last_detected_number

# Example usage:
if __name__ == "__main__":
    number = detect_number_from_camera(show_window=True)
    print("Last detected number:", number)