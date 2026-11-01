# This code simulates the first task of the ENSI competition: identifying colors (blue or red)
# The first version of this code uses the computer's camera 

import cv2
import numpy as np

# Define HSV ranges for red and blue
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

lower_blue = np.array([100, 150, 0])
upper_blue = np.array([140, 255, 255])

# Start webcam
webcam_video = cv2.VideoCapture(1)

while True:
    success, video = webcam_video.read()
    if not success:
        break

    hsv = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)

    # Red mask (two parts combined)
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 | mask_red2

    # Blue mask
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Flag to check if any color was detected
    detected_colors = []

    # Find contours for red
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_red:
        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(video, (x, y), (x + w, y + h), (0, 0, 255), 3)
            cv2.putText(video, "Red", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            detected_colors.append("Red")

    # Find contours for blue
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_blue:
        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(video, (x, y), (x + w, y + h), (255, 0, 0), 3)
            cv2.putText(video, "Blue", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            detected_colors.append("Blue")

    
    if detected_colors:
        print("Detected:", ", ".join(detected_colors))

    # Show webcam with bounding boxes
    cv2.imshow("Color Detection", video)

    if cv2.waitKey(1) & 0xFF == ord("q"):  # press q to quit the window
        break

webcam_video.release()
cv2.destroyAllWindows()
