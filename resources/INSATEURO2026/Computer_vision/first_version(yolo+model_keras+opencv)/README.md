# First Version (YOLO + Keras + OpenCV) - Computer Vision System

This directory contains the initial implementation of our computer vision system for the ENSI competition. This version uses a hybrid approach combining multiple technologies for different tasks.

## 📋 Overview

The first version was our initial attempt at solving the competition's three main tasks:
1. **Color Detection** - Identify red and blue objects
2. **Number Recognition** - Detect digits 3, 5, 6, 9
3. **Object Detection** - Identify green cubes and triangles

## 🏗️ Architecture

### Task 1: Color Detection (`task1_color_detection/`)
- **Technology**: Pure OpenCV with HSV color filtering
- **Approach**: Manual HSV range definition for red and blue colors
- **Files**: `color_detection_ver1.py`

### Task 2: Number Detection (`task2_number_detection/`)
- **Technology**: Keras CNN model + OpenCV preprocessing
- **Approach**: Pre-trained MNIST model with custom preprocessing
- **Files**: `run.py`, `final_version.py`, `kadhi/`

### Task 3: Object Detection (`task3_object_detection/`)
- **Technology**: YOLOv8 + OpenCV post-processing
- **Approach**: Custom trained YOLO model with green color filtering
- **Files**: `final_version/run.py`, `test.py`, `training.py`

## ⚠️ Issues & Limitations

### Major Problems Identified:

1. **Task 2 (Number Detection)**:
   - ❌ **Poor accuracy** with Keras MNIST model on real-world data
   - ❌ **Inconsistent preprocessing** pipeline
   - ❌ **Complex contour-based refinement** that often failed
   - ❌ **Multiple detection windows** causing confusion
   - ❌ **Hardcoded thresholds** not robust to lighting changes

2. **Task 3 (Object Detection)**:
   - ❌ **Multiple bounding boxes** shown simultaneously
   - ❌ **Complex post-processing** with clustering and centers
   - ❌ **Inconsistent green color filtering**
   - ❌ **Poor sunlight robustness**

3. **General Issues**:
   - ❌ **No unified inference pipeline**
   - ❌ **Inconsistent camera indices** (0 vs 1)
   - ❌ **Poor code modularity** and reusability
   - ❌ **Multiple preprocessing approaches** for similar tasks

## 🔄 Comparison with Second Version

### What Changed:

| Aspect | First Version | Second Version | Improvement |
|--------|---------------|----------------|-------------|
| **Number Detection** | Keras CNN + OpenCV | Fine-tuned YOLOv8 | ✅ Much better accuracy |
| **Processing** | Multiple inconsistent pipelines | Unified minimal processing | ✅ Simplified & robust |
| **Code Structure** | Script-based, hard to reuse | Function-based, modular | ✅ Better maintainability |
| **Visualization** | Multiple confusing windows | Clean single-window output | ✅ User-friendly |
| **Sunlight Robustness** | Poor, hardcoded thresholds | CLAHE + adaptive processing | ✅ Works outdoors |
| **Color Filtering** | Inconsistent HSV ranges | Unified approach with ratios | ✅ More reliable |
| **Model Performance** | Mixed (YOLO good, Keras poor) | All YOLO-based | ✅ Consistent quality |

### Key Learnings:

1. **YOLO for Everything**: Using YOLOv8 for all detection tasks (including digits) proved much more effective than mixing technologies
2. **Simplify Processing**: Complex post-processing often hurt performance rather than helped
3. **Unified Pipeline**: Having consistent preprocessing across tasks improved reliability
4. **Function-based Design**: Modular functions made the code reusable and easier to debug

## 📁 Directory Structure

```
first_version(yolo+model_keras+opencv)/
├── task1_color_detection/
│   └── color_detection_ver1.py        # HSV-based color detection
├── task2_number_detection/
│   ├── run.py                         # Main digit detection script
│   ├── kadhi/                         # Alternative implementations
│   └── final_version.py               # Final Keras-based version
├── task3_object_detection/
│   ├── first_version.py               # Initial YOLO implementation
│   ├── second_version/                # Improved version
│   └── final_version/                 # Production version
│       ├── run.py                     # Main object detection
│       ├── test.py                    # Testing script
│       ├── training.py                # Model training
│       └── unlabeled_dataset/         # Data collection tools
└── model_converter/                   # ONNX conversion utilities
```

## 🚀 Running the Code

### Prerequisites
```bash
pip install ultralytics opencv-python keras tensorflow numpy
```

### Task 1 - Color Detection
```bash
cd task1_color_detection
python color_detection_ver1.py
```

### Task 2 - Number Detection
```bash
cd task2_number_detection
python run.py
```

### Task 3 - Object Detection
```bash
cd task3_object_detection/final_version
python run.py
```

## 📊 Performance Summary

| Task | Technology | Accuracy | Robustness | Maintainability |
|------|------------|----------|------------|-----------------|
| Color Detection | OpenCV HSV | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Number Detection | Keras CNN | ⭐⭐ | ⭐ | ⭐ |
| Object Detection | YOLOv8 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

## 🎯 Conclusion

This first version served as a valuable learning experience and proof-of-concept. While it had significant issues, particularly with the number detection task, it helped identify the need for:

1. **Unified approach** using YOLOv8 for all detection tasks
2. **Simplified processing** pipelines
3. **Better code organization** and modularity
4. **Improved robustness** to environmental conditions

The lessons learned from this version directly informed the development of the much-improved second version.
