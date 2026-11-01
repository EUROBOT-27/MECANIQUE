import cv2
import math
import numpy as np
from ultralytics import YOLO

# ================================
# Distortion + Math Utils
# ================================
def abs_to_cam_cartesian(x, y):
    return x - 320, 480 - y

def cam_cartesian_to_abs(new_x, new_y):
    return new_x + 320, 480 - new_y

def cartesian_to_polar(x, y, coef):
    r = math.sqrt(x**2 + y**2) * coef
    theta_rad = math.atan2(y, x)
    theta_deg = math.degrees(theta_rad)
    return r, theta_deg

def polar_to_cartesian(r, theta_deg):
    theta_rad = math.radians(theta_deg)
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return round(x), round(y)

def treat_camera_distorsion(x, y, coef=1):
    xcam, ycam = abs_to_cam_cartesian(x, y)
    r, theta = cartesian_to_polar(xcam, ycam, coef)
    new_xcam, new_ycam = polar_to_cartesian(r, theta)
    return cam_cartesian_to_abs(new_xcam, new_ycam)

def distance(center1, center2):
    return ((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)**0.5

# ================================
# YOLO Detection + Processing
# ================================
LOWER_GREEN = (35, 40, 40)
UPPER_GREEN = (85, 255, 255)
GREEN_RATIO_THRESHOLD = 0.19  # At least 20% of ROI pixels must be green

def perform_detection(model, image, radius_correction_factor, threshold=0.5):
    results = model.predict(image, verbose=False)

    best_center = None
    best_conf = -1
    best_class_name = None
    best_box = None

    for result in results:
        for i in range(len(result.boxes)):
            box = result.boxes.data[i]
            x1, y1, x2, y2 = map(int, box[:4])
            confidence, class_id = box[4].item(), int(box[5])
            roi = image[y1:y2, x1:x2]

            # Green filter
            is_green = False
            if roi.size > 0:
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                mask_green = cv2.inRange(hsv_roi, LOWER_GREEN, UPPER_GREEN)
                green_ratio = np.sum(mask_green > 0) / (roi.shape[0] * roi.shape[1])
                if green_ratio >= GREEN_RATIO_THRESHOLD:
                    is_green = True

            if confidence > threshold and confidence > best_conf and is_green:
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                corrected_x, corrected_y = treat_camera_distorsion(
                    center_x, center_y, radius_correction_factor
                )
                best_center = ((int(corrected_x), int(corrected_y)), confidence, result.names[class_id])
                best_conf = confidence
                best_class_name = result.names[class_id]
                best_box = (x1, y1, x2, y2)

    return best_center, best_box, best_class_name, best_conf


def draw_best_detection(image, best_box=None, best_class_name=None, best_conf=None):
    image_out = image.copy()
    if best_box is not None and best_class_name is not None and best_conf is not None:
        x1, y1, x2, y2 = best_box
        cv2.rectangle(image_out, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(image_out, f'{best_class_name} {best_conf:.2f}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    return image_out


def process_and_visualize_image(image, model, radius_correction_factor):
    best_center, best_box, best_class_name, best_conf = perform_detection(
        model, image, radius_correction_factor
    )
    processed_image = draw_best_detection(image, best_box, best_class_name, best_conf)
    return processed_image, best_center


# ================================
# Main Loop
# ================================
if __name__ == "__main__":
    model = YOLO("runs/detect/train2/weights/best.pt")
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Cannot open webcam")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_image, best_center = process_and_visualize_image(
            frame, model, radius_correction_factor=1.0
        )

        if best_center:
            _, conf, cls = best_center
            print(f"Best detection: {cls} ({conf:.2f})")
        else:
            print("No valid detection.")

        cv2.imshow("Processed YOLO (Best Only)", processed_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
