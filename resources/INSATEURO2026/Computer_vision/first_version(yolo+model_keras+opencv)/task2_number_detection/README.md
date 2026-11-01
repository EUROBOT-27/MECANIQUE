# Eurobot Number Detection System

This repository contains the number detection system development for our Eurobot robot.  
The first version uses **a pre-trained model (e.g., YOLO or custom CNN)** to detect numbers locally on the camera feed.  



## 🔹 Current Version (v0.1 - Baseline)

- Runs the number detection model on the local camera.  
- Detects **one number at a time** to match the Eurobot competition environment.  
- Uses pre-trained weights with no fine-tuning on competition-specific numbers yet.  
- No custom dataset prepared yet.

### ▶️ Usage
```bash
pip install ultralytics opencv-python
python baseline_number_detection.py