#!/usr/bin/env python3
"""
digit_live_onnx.py
Live webcam digit recognition using an ONNX MNIST classifier + contour-based ROI extraction.
Requirements:
    pip install opencv-python numpy onnxruntime

Usage:
    python digit_live_onnx.py --model best.onnx --camera 0 --min_area 500
"""

import cv2
import numpy as np
import onnxruntime as ort
import argparse
import time
from datetime import datetime

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="Path to ONNX model (MNIST classifier expecting 1x1x28x28 input).")
    p.add_argument("--camera", type=int, default=1, help="Camera index (default 0).")
    p.add_argument("--min_area", type=int, default=400, help="Minimum contour area to consider as a digit (px).")
    p.add_argument("--confidence_th", type=float, default=0.4, help="Min confidence to display prediction.")
    return p.parse_args()

def load_onnx_session(path):
    sess = ort.InferenceSession(path, providers=['CPUExecutionProvider'])
    # Get model input name for session.run
    input_name = sess.get_inputs()[0].name
    return sess, input_name

def preprocess_mnist(crop):
    """
    crop: grayscale image ROI (numpy array)
    Returns: float32 numpy array shaped (1,1,28,28), normalized [0,1]
    """
    # Resize to 28x28 while preserving aspect via padding
    h, w = crop.shape
    # Resize keeping aspect ratio
    if h > w:
        new_h = 20
        new_w = int(round((w * 20) / h))
    else:
        new_w = 20
        new_h = int(round((h * 20) / w))
    if new_h == 0: new_h = 1
    if new_w == 0: new_w = 1
    resized = cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create 28x28 canvas and place resized in center
    canvas = np.zeros((28, 28), dtype=np.uint8)
    x_off = (28 - new_w) // 2
    y_off = (28 - new_h) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized

    # In MNIST white digit on black background; ensure that
    # If background appears white (mean>127), invert.
    if np.mean(canvas) > 127:
        canvas = 255 - canvas

    # Normalize to [0,1]
    arr = canvas.astype(np.float32) / 255.0
    # Optionally apply simple centering (subtract mean)
    # arr = (arr - arr.mean()) / (arr.std() + 1e-8)

    # Reshape to 1x1x28x28
    arr = arr[np.newaxis, np.newaxis, :, :].astype(np.float32)
    return arr

def main():
    args = parse_args()
    sess, input_name = load_onnx_session(args.model)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("ERROR: Cannot open camera index", args.camera)
        return

    print("Model loaded:", args.model)
    print("Press ESC or q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera.")
            break

        # Resize frame for speed (optional)
        frame_disp = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Preprocessing pipeline (adaptive to lighting):
        # 1) Gaussian blur -> 2) adaptive threshold -> 3) morphological open to remove noise
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        opened = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        predictions = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < args.min_area:
                continue
            x,y,w,h = cv2.boundingRect(cnt)
            # expand bbox slightly
            pad = 4
            x1 = max(0, x-pad); y1 = max(0, y-pad)
            x2 = min(frame.shape[1], x+w+pad); y2 = min(frame.shape[0], y+h+pad)
            roi = gray[y1:y2, x1:x2]

            # further threshold the ROI to enhance digit
            _, roi_bin = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            mnist_in = preprocess_mnist(roi_bin)

            # Run ONNX inference
            try:
                out = sess.run(None, {input_name: mnist_in})
                logits = out[0]  # shape (1,10) expected
                probs = softmax(logits[0])
                label = int(np.argmax(probs))
                conf = float(probs[label])
            except Exception as e:
                # fallback: skip if model input mismatch
                # print("Inference error:", e)
                continue

            if conf < args.confidence_th:
                # skip low-confidence predictions (optional)
                continue

            # Draw bbox and label
            cv2.rectangle(frame_disp, (x1,y1), (x2,y2), (0,255,0), 2)
            text = f"{label} ({conf:.2f})"
            cv2.putText(frame_disp, text, (x1, y1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # Log prediction with timestamp
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[{ts}] bbox=({x1},{y1},{x2},{y2}) label={label} conf={conf:.4f}")
            predictions.append((label, conf, (x1,y1,x2,y2)))

        # show a small window with thresholded image for debugging
        cv2.imshow("thresh", opened)
        cv2.imshow("Digit Recognition", frame_disp)

        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):  # ESC or q
            break

    cap.release()
    cv2.destroyAllWindows()

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / (e_x.sum() + 1e-8)

if __name__ == "__main__":
    main()