# ENSI Computer Vision System - Eurobot 2025

## Overview

This repository contains our complete **Computer Vision system** for the ENSI Eurobot 2025 competition. The system successfully implements vision-based solutions for all three competition tasks:

* **Task 1: Color Detection** - Identify red and blue objects with size filtering
* **Task 2: Number Recognition** - Detect digits 3, 5, 6, 9 using fine-tuned YOLO
* **Task 3: Object Detection** - Identify green cubes and triangles with verification

The system evolved through two major versions, with the final implementation using a **unified YOLOv8-based approach** that achieved competition-winning performance.

---

## Repository Structure

```
Computer_vision/
├── README.md                           <- Project documentation
├── requirements.txt                    <- Python dependencies
├── resources.md                        <- Computer vision resources and tutorials
├── first_version(yolo+model_keras+opencv)/
│   ├── README.md                       <- Detailed first version analysis
│   ├── task1_color_detection/          <- HSV-based color detection
│   ├── task2_number_detection/         <- Keras CNN + OpenCV approach
│   └── task3_object_detection/         <- YOLO + complex post-processing
└── second_version(finetuned_yolo_for_everything)/
    ├── README.md                       <- Production system documentation
    ├── computer_vision_service.py      <- ROS service integration
    ├── task1_color_detection/          <- Improved color detection
    ├── second_task_number_detection/   <- Fine-tuned YOLO for digits
    └── task3_object_detection/         <- Optimized object detection
```

---

## 🏆 System Versions

### First Version (Hybrid Approach)
- **Location**: `first_version(yolo+model_keras+opencv)/`
- **Approach**: Mixed technologies (OpenCV + Keras + YOLO)
- **Issues**: Poor number detection accuracy (~60%), complex pipelines, multiple windows
- **Status**: ❌ Learning prototype with identified limitations

### Second Version (Unified YOLO) 
- **Location**: `second_version(finetuned_yolo_for_everything)/`
- **Approach**: Fine-tuned YOLOv8 for all tasks
- **Performance**: Excellent accuracy (~95% for numbers), robust outdoor operation
- **Status**: ✅ **Competition-ready production system**

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install ultralytics opencv-python numpy rospy
```

### Running the Production System (Second Version)

#### Individual Tasks
```bash
# Color Detection
cd second_version(finetuned_yolo_for_everything)/task1_color_detection
python color_detection_ver1.py

# Number Detection  
cd second_version(finetuned_yolo_for_everything)/second_task_number_detection
python yolo_only.py

# Object Detection
cd second_version(finetuned_yolo_for_everything)/task3_object_detection/last_version  
python yolo_minimal.py
```

#### ROS Service Integration
```bash
# Start computer vision services
cd second_version(finetuned_yolo_for_everything)
python computer_vision_service.py

# Call services from robot
rosservice call /service1  # Color detection
rosservice call /service2  # Number detection  
rosservice call /service3  # Object detection
```

---

## 🛠️ Technology Stack

### Core Technologies
* **YOLOv8 (Ultralytics)** – Primary detection engine for all tasks
* **OpenCV** – Image preprocessing, color filtering, camera interface
* **ONNX Runtime** – Optimized model inference for edge deployment
* **ROS** – Robot communication and service integration

### Processing Pipeline
* **CLAHE** – Adaptive contrast enhancement for sunlight robustness
* **Gaussian Blur** – Noise reduction preprocessing
* **HSV Color Filtering** – Object color verification
* **Confidence Thresholding** – Best detection selection

---

## 📊 Performance Achievements

| Task | First Version | Second Version | Improvement |
|------|---------------|----------------|-------------|
| **Color Detection** | HSV filtering | HSV + size constraints | ✅ Better reliability |
| **Number Recognition** | ~60% (Keras CNN) | ~95% (Fine-tuned YOLO) | ✅ +35% accuracy |
| **Object Detection** | Complex post-processing | Clean single detection | ✅ 2x faster |
| **Sunlight Robustness** | Poor | Excellent | ✅ Outdoor ready |
| **Code Maintainability** | Mixed technologies | Unified YOLO | ✅ Much simpler |

---

## 🏁 Competition Results

✅ **Successfully implemented** all three required computer vision tasks  
✅ **Robust outdoor performance** with CLAHE preprocessing  
✅ **Real-time detection** suitable for competition constraints  
✅ **ROS integration** for seamless robot communication  
✅ **Production deployment** ready for competition environment  

---

## 📚 Documentation

- **[First Version README](first_version(yolo+model_keras+opencv)/README.md)** - Detailed analysis of initial approach and lessons learned
- **[Second Version README](second_version(finetuned_yolo_for_everything)/README.md)** - Production system documentation and technical details
- **[Resources](resources.md)** - Computer vision learning materials and references

---

## 🤝 Development Team

**INSAT Eurobot 2025 Team - Computer Vision Module**

For questions or contributions, please contact the development team or create an issue in this repository.

---

## 📄 License

This repository is for **Eurobot 2025 INSAT Team use only**. External usage requires explicit permission.

