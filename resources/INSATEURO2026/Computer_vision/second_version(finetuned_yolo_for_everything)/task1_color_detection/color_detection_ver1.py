# This code simulates the first task of the ENSI competition: identifying colors (blue or red)
# The first version of this code uses the computer's camera 


import cv2
import numpy as np
import os

# Detect if running on Pi
RUNNING_ON_PI = False
if RUNNING_ON_PI:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Define HSV ranges for red and blue
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

lower_blue = np.array([100, 150, 0])
upper_blue = np.array([140, 255, 255])

# Minimum bounding box size in centimeters
MIN_SIZE_CM = 12
PIXELS_PER_CM = 10 #: Calibrate this value for your camera
MIN_SIZE_PX = MIN_SIZE_CM * PIXELS_PER_CM

def detect_color_from_camera(show_window=True):
    """
    Detects red or blue color from the webcam continuously.
    Returns: last_detected_color (str or None)
    Camera stays open for continuous detection - controlled externally by ROS.
    """
    
    print("Starting continuous color detection...")
    print("Expected colors: Red, Blue")
    
    webcam_video = cv2.VideoCapture(0 if RUNNING_ON_PI else 1)
    if not webcam_video.isOpened():
        print("Cannot open camera")
        return None
    
    # Continuous detection - no time limit
    last_detected_color = None
    frame_count = 0
    
    while True:  # Run continuously
        success, video = webcam_video.read()
        if not success:
            print("Failed to grab frame")
            continue
        
        frame_count += 1

        hsv = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)

        # Red mask (two parts combined)
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = mask_red1 | mask_red2

        # Blue mask
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        frame_detections = []
        detection_areas = []

        # Find contours for red
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                if w >= MIN_SIZE_PX and h >= MIN_SIZE_PX:
                    frame_detections.append("Red")
                    detection_areas.append(("Red", area, (x, y, w, h)))
                    if show_window and not RUNNING_ON_PI:
                        cv2.rectangle(video, (x, y), (x + w, y + h), (0, 0, 255), 3)
                        cv2.putText(video, "Red", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Find contours for blue
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                if w >= MIN_SIZE_PX and h >= MIN_SIZE_PX:
                    frame_detections.append("Blue")
                    detection_areas.append(("Blue", area, (x, y, w, h)))
                    if show_window and not RUNNING_ON_PI:
                        cv2.rectangle(video, (x, y), (x + w, y + h), (255, 0, 0), 3)
                        cv2.putText(video, "Blue", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Find the best detection (largest area) for this frame
        if detection_areas:
            # Sort by area (largest first) and take the best one
            best_detection = max(detection_areas, key=lambda x: x[1])
            best_color = best_detection[0]
            best_area = best_detection[1]
            last_detected_color = best_color
            
            print(f"Frame {frame_count}: {best_color} (area: {best_area:.0f})")
        else:
            print(f"Frame {frame_count}: No valid colors detected")

        # Show webcam with bounding boxes
        if show_window and not RUNNING_ON_PI:
            cv2.imshow("Color Detection", video)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    webcam_video.release()
    cv2.destroyAllWindows()
    return last_detected_color

# Example usage:
if __name__ == "__main__":
    color = detect_color_from_camera(show_window=True)
    print("Last detected color:", color)
