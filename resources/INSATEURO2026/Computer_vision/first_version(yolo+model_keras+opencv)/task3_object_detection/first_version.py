#this code will contain simple usage of the yolo model with the local camera with no finetuning or special object annotations

import cv2
from ultralytics import YOLO
"""this model recognizes multiple classes and objects at the same time
When fine tuning this model we need to create a config file that will contain the annotated data which should be structured in a specific format
The config file should include paths to the training and validation datasets, as well as any augmentation or preprocessing steps
additionally, we need to specify the model architecture and hyperparameters for training
Finally, we need to define the training loop and evaluation metrics
Our next versions will include this approach:
    -Using classical image processing techniques for detecting contours and angles
    -evaluating this approach(accuracy+load on the hardware)
    -comparing with YOLOv8 performance(finetuned)
    -
"""
# Load YOLOv8 model (nano version for speed)
model = YOLO("yolov8n.pt")
# Open webcam (0 = default camera)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame)[0]
    if len(results.boxes) > 0:
            # Keep only the highest-confidence detection
            best_box = max(results.boxes.data.tolist(), key=lambda x: x[4])
            x1, y1, x2, y2, score, class_id = best_box
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            label = f"{results.names[int(class_id)]} {score:.2f}"

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show frame
    cv2.imshow("YOLOv8 Webcam", frame)

    # Exit with 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
