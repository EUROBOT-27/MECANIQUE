import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Open webcam (0 = default camera)
import sys
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit(1)
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Load trained model
print("printing model input shape: heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeere\n")
model = load_model(r'C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Computer_vision\task2_number_detection\digits.h5')
# Print input and output shapes
print("Input shape:", model.inputs[0].shape)
print("Output shape:", model.outputs[0].shape)
print(model.summary())
# Allowed digits
ALLOWED_DIGITS = {3, 5, 6, 9}

def prediction(image, model):
    # Preprocess: resize, blur, threshold, normalize, reshape
    img = cv2.resize(image, (28, 28))
    img = cv2.GaussianBlur(img, (3, 3), 0)
    _, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)
    img = img / 255.0
    img = img.reshape(1, 28, 28, 1)

    # Predict
    predict = model.predict(img, verbose=0)

    # Restrict predictions to allowed digits only
    restricted_probs = np.full_like(predict, -np.inf)  # initialize with -inf
    for d in ALLOWED_DIGITS:
        restricted_probs[0][d] = predict[0][d]

    result = int(np.argmax(restricted_probs))
    prob = float(predict[0][result])

    # Apply confidence threshold
    if result not in ALLOWED_DIGITS or prob < 0.75:
        result = -1  # uncertain or not allowed
        prob = 0.0
    return result, prob

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_copy = frame.copy()

    # Define ROI (Region of Interest)
    bbox_size = (100, 100)
    x1 = int(WIDTH // 2 - bbox_size[0] // 2)
    y1 = int(HEIGHT // 2 - bbox_size[1] // 2)
    x2 = int(WIDTH // 2 + bbox_size[0] // 2)
    y2 = int(HEIGHT // 2 + bbox_size[1] // 2)

    # Draw ROI rectangle
    cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(frame_copy, "Draw digit here", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


    # Crop and convert to grayscale
    img_cropped = frame[y1:y2, x1:x2]
    if img_cropped.shape[0] == 0 or img_cropped.shape[1] == 0:
        img_gray = np.zeros((100, 100), dtype=np.uint8)
        digit, prob = -1, 0.0
    else:
        img_gray = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
        digit, prob = prediction(img_gray, model)

    # Display prediction
    if digit == -1:
        text = "Prediction: ?"
    else:
        text = f"Prediction: {digit} ({prob*100:.1f}%)"

    cv2.putText(frame_copy, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (36, 255, 12), 2)
               

    # Show windows
    cv2.imshow("Input", frame_copy)
    cv2.imshow("Cropped (gray)", cv2.resize(img_gray, (200, 200)))

    # Exit on ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()