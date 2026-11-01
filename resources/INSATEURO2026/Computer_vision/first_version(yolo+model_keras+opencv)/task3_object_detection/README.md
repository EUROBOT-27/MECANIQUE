# Eurobot Vision System

This repository contains the vision system development for our Eurobot robot.  
The first version uses **YOLOv8 (nano model)** with a webcam to perform object detection locally.  

---

## 🔹First Version (v1 - Baseline)

- Runs YOLOv8 on the local camera.
- Detects objects using the pre-trained COCO dataset.
- Only **one object (highest confidence)** is kept at a time to match the Eurobot competition environment.
- No fine-tuning or custom dataset yet.

### ▶️ Usage
```bash
pip install ultralytics opencv-python
cd task3_object_detection
python first_version.py
---

### Second Version (v2)
-   uses opencv to detect contours and calculate angles to detect objects
### ▶️ Usage
```bash
pip install  opencv-python
cd task3_object_detection
python first_version.py


### Final version(v3)
-   Uses "FINE-TUNED" yolov8n model
-   Used roboflow for data annotation (read Robflow annotation file)
-   Data collected by  REDDRAGON GW600 USB webcam
-   Model trained locally for 50 epochs
-   Model exported as tflite for the best model performance 
-   Model exported as ONNX for the last model training performance
###usage
```bash
pip install ultralytics cv2
cd  task3_object_detection
cd final_version
python training.py (for training the model this command is only ran once not in every usage)
python run.py


🔮 Planned Versions

v0.2 - Multi-object (testing only)

Keep all detected objects (for debugging outside competition).

v0.3 - Dataset Preparation

Create annotation guide.

Collect and label competition-specific objects.

v0.4 - Fine-tuned YOLO

Train YOLOv8 on our custom Eurobot dataset.

Detect competition-specific objects (e.g., pucks, zones, markers).

v0.5 - Robot Integration

Connect detection output to robot decision-making.

Provide bounding box + class info over serial/ROS.

v0.6 - Optimized Deployment

Deploy lightweight YOLO model on Raspberry Pi / Jetson.

Optimize for real-time FPS with quantization/pruning.

v1.0 - Competition-ready

Robust, fine-tuned model.

Stable integration with navigation & manipulation systems.

Tested on official competition environment.