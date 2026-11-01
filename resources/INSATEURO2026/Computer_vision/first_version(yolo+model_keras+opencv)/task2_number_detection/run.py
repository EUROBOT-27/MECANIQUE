import keras
import cv2
import numpy as np
from keras.models import load_model
import sys
import os

# ---------------- CONFIGURATION ----------------
# Set True if running on the Pi (headless mode)
RUNNING_ON_PI = False  # <-- Change to True on Pi

if RUNNING_ON_PI:
    # Headless mode to avoid Qt/xcb errors
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
# ------------------------------------------------

# Open webcam (0 = default camera, try 1 if you have multiple)
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit(1)

WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# assuming you already have: model = load_model(...)
# and a predict(model, image) function defined

frame_count = 0
threshold = 50  # adjust based on lighting

# create a black background for overlay
background = np.zeros((480, 640), dtype=np.uint8)

# Load the saved Keras model
model = load_model(
    r"C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Computer_vision\task2_number_detection\model_mnist_0.keras"
)

ALLOWED_DIGITS = {3, 5, 6, 9}

def prediction(image, model):
    """Preprocess image, predict digit, restrict to allowed digits, apply confidence threshold."""
    img = cv2.resize(image, (28, 28))
    img = cv2.GaussianBlur(img, (3, 3), 0)
    _, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)
    img = img / 255.0
    img = img.reshape(1, 28, 28, 1)

    predict = model.predict(img, verbose=0)

    # Restrict predictions to allowed digits only
    restricted_probs = np.full_like(predict, -np.inf)
    for d in ALLOWED_DIGITS:
        restricted_probs[0][d] = predict[0][d]

    result = int(np.argmax(restricted_probs))
    prob = float(predict[0][result])

    # Confidence check
    if result not in ALLOWED_DIGITS or prob < 0.75:
        result = -1
        prob = 0.0
    return result, prob


while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    # Convert to gray for contour detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 255, 50, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Pick the largest contour (assume it’s the digit)
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)

        # Add some margin so box isn’t too tight
        margin = 20
        x1, y1 = max(x - margin, 0), max(y - margin, 0)
        x2, y2 = min(x + w + margin, WIDTH), min(y + h + margin, HEIGHT)

        img_cropped = frame[y1:y2, x1:x2]

        if img_cropped.shape[0] > 0 and img_cropped.shape[1] > 0:
            img_gray = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
            digit, prob = prediction(img_gray, model)
        else:
            img_gray = np.zeros((100, 100), dtype=np.uint8)
            digit, prob = -1, 0.0
    else:
        # No contour found
        x1, y1, x2, y2 = 0, 0, 0, 0
        img_gray = np.zeros((100, 100), dtype=np.uint8)
        digit, prob = -1, 0.0

    # Show prediction
    if digit == -1:
        text = f"Frame {frame_count}: Prediction uncertain or not allowed"
    else:
        text = f"Frame {frame_count}: Predicted {digit} ({prob*100:.1f}%)"

    # ------------------ DISPLAY ------------------
    if not RUNNING_ON_PI:
        frame_copy = frame.copy()
        if x2 > x1 and y2 > y1:
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_copy, "Digit ROI", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame_copy, text, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (36, 255, 12), 2)

        cv2.imshow("Input", frame_copy)
        cv2.imshow("Cropped (gray)", cv2.resize(img_gray, (200, 200)))

        # Exit on ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break
    else:
        print(text)
    # ---------------------------------------------

cap.release()
cv2.destroyAllWindows()
