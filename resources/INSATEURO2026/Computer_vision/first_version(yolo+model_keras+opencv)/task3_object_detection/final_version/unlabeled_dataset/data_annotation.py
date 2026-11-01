import cv2
import os

# Save path (portable relative to script)
save_path = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(save_path, exist_ok=True)

# Start numbering from the last saved image
existing_files = [f for f in os.listdir(save_path) if f.startswith("img_") and f.endswith(".jpg")]
if existing_files:
    numbers = [int(f.split("_")[1].split(".")[0]) for f in existing_files]
    img_count = max(numbers) + 1
else:
    img_count = 0

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera Feed - Press 's' to Save", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Press 's' to save image
        filename = os.path.join(save_path, f"img_{img_count}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")
        img_count += 1
    elif key == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()
