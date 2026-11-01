import cv2
import numpy as np

# ---------- Shape detection helpers ----------
def calculate_angle(pt1, pt2, pt3):
    """Calculate angle (in degrees) between three points with pt2 as vertex."""
    a = np.array(pt1)
    b = np.array(pt2)
    c = np.array(pt3)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def detect_shape(approx):
    num_vertices = len(approx)

    # ---------- Triangle ----------
    if num_vertices == 3:
        pts = approx.reshape(-1, 2)
        angles = []
        for i in range(3):
            ang = calculate_angle(pts[i], pts[(i+1) % 3], pts[(i+2) % 3])
            angles.append(ang)
        if all(50 <= ang <= 80 or 100 <= ang <= 130 for ang in angles):
            return "Triangle"

    # ---------- Square (front view of Cube) ----------
    elif num_vertices == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)
        pts = approx.reshape(-1, 2)
        angles = []
        for i in range(4):
            ang = calculate_angle(pts[i], pts[(i+1) % 4], pts[(i+2) % 4])
            angles.append(ang)
        # Check ~90° angles (square/rectangle)
        if all(70 <= ang <= 110 for ang in angles) and 0.9 <= aspect_ratio <= 1.1:
            return "Cube"   # <-- now treat square as Cube

    return "Other"


# ---------- Webcam ----------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edged = cv2.Canny(blurred, 50, 150)

    # Morphological cleanup
    kernel = np.ones((5, 5), np.uint8)
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 1500:
            continue

        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if not cv2.isContourConvex(approx):
            continue

        shape = detect_shape(approx)

        if shape != "Other":
            cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
            M = cv2.moments(approx)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.putText(frame, shape, (cX - 20, cY - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    cv2.imshow("ENSI Shape Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
