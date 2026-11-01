from ultralytics import YOLO
import cv2
import numpy as np  # Import numpy for numerical operations

# Load your trained model
model = YOLO("runs/detect/train2/weights/best.pt")

# Open the webcam (0 = default camera)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Cannot open webcam")
    exit()

PIXELS_PER_CM = 20  # TODO: Calibrate for your camera
MIN_SIDE_CM = 11
MAX_SIDE_CM = 12
MIN_SIDE_PX = MIN_SIDE_CM * PIXELS_PER_CM
MAX_SIDE_PX = MAX_SIDE_CM * PIXELS_PER_CM

# Define HSV range for green
LOWER_GREEN = (35, 40, 40)
UPPER_GREEN = (85, 255, 255)
GREEN_RATIO_THRESHOLD = 0.2  # At least 20% of ROI pixels must be green

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO inference
    results = model(frame)

    # Get detections from the first result
    detections = results[0].boxes

    # Counters
    num_triangles = 0
    num_cubes = 0

    # Loop through detections
    for box in detections:
        cls_id = int(box.cls[0])   # class index
        cls_name = model.names[cls_id]  # class name (from training)

        # Get bounding box coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w = x2 - x1
        h = y2 - y1

        # Check if bounding box sides are within range
        if MIN_SIDE_PX <= w <= MAX_SIDE_PX and MIN_SIDE_PX <= h <= MAX_SIDE_PX:
            # Extract ROI and check for green color
            roi = frame[y1:y2, x1:x2]
            if roi.size > 0:
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                mask_green = cv2.inRange(hsv_roi, LOWER_GREEN, UPPER_GREEN)
                green_ratio = np.sum(mask_green > 0) / (roi.shape[0] * roi.shape[1])
                if green_ratio >= GREEN_RATIO_THRESHOLD:
                    if cls_name.lower() == "triangle":
                        num_triangles += 1
                    elif cls_name.lower() == "cube":
                        num_cubes += 1

    # Find the highest confidence detection
    best_conf = -1
    best_box = None
    best_cls_name = None
    for box in detections:
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w = x2 - x1
        h = y2 - y1
        roi = frame[y1:y2, x1:x2]
        is_green = False
        if roi.size > 0:
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask_green = cv2.inRange(hsv_roi, LOWER_GREEN, UPPER_GREEN)
            green_ratio = np.sum(mask_green > 0) / (roi.shape[0] * roi.shape[1])
            if green_ratio >= GREEN_RATIO_THRESHOLD:
                is_green = True
        if conf > best_conf and MIN_SIDE_PX <= w <= MAX_SIDE_PX and MIN_SIDE_PX <= h <= MAX_SIDE_PX and is_green:
            best_conf = conf
            best_box = (x1, y1, x2, y2)
            best_cls_name = cls_name

    # Print/log results
    print(f"Triangles: {num_triangles}, Cubes: {num_cubes}")

    # Show all predictions (YOLO-annotated frame)
    annotated_frame = results[0].plot()
    cv2.imshow("All Predictions", annotated_frame)

    # Show only the best detection
    best_frame = frame.copy()
    if best_box is not None and best_cls_name is not None:
        x1, y1, x2, y2 = best_box
        cv2.rectangle(best_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(best_frame, f"{best_cls_name} {best_conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Best Detection Only", best_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
