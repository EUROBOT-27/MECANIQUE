# Map Anchors Module

## 📌 Overview

This module handles the **Map Anchors** system for the Eurobot 2026 vision system. Map anchors are fixed ArUco markers placed at the corners of the playing field that establish the global coordinate system for all vision-based localization.

## 🎯 Objectives

### ✅ Task 1: Place 4 Fixed ArUco Tags on Table Corners (DONE)
- Place 4 ArUco markers at the corners of the table
- Reserved IDs: **0, 1, 2, 3**
- Physical placement considerations:
  - Ensure markers are flat and parallel to the table surface
  - Use high-quality printing (300+ DPI)
  - Laminate markers to prevent wear
  - Ensure proper lighting visibility

### 🔄 Task 2: Compute Camera Extrinsics
- Compute the camera's pose relative to the map coordinate system
- Calculate transformation matrix `T_world_cam`
- Use PnP (Perspective-n-Point) algorithm with known marker positions
- Store calibration results for runtime use

### ✅ Task 3: Validate Camera Pose
- Camera pose should remain stable when the robot is absent
- Implement validation checks:
  - Pose stability test (variance should be minimal)
  - Reprojection error analysis
  - Continuous monitoring during operation

## 📁 Module Structure

```
map_anchors/
├── README.md                 # This file
├── docs/                     # Documentation
│   ├── marker_placement.md   # Guide for physical marker placement
│   ├── extrinsics.md        # Camera extrinsics computation guide
│   ├── validation.md        # Pose validation procedures
│   └── coordinate_system.md # World coordinate system definition
├── config/                   # Configuration files
│   ├── marker_config.yaml   # Marker IDs and physical positions
│   └── camera_config.yaml   # Camera parameters placeholder
├── scripts/                  # Implementation scripts
│   ├── detect_anchors.py    # Detect all 4 map anchors
│   ├── compute_extrinsics.py # Compute camera extrinsics
│   ├── validate_pose.py     # Validate camera pose stability
│   └── visualize_anchors.py # Visualize detected anchors
├── examples/                 # Example usage
│   └── full_pipeline_example.py
└── tests/                    # Test scripts
    └── test_anchor_detection.py
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install opencv-contrib-python numpy pyyaml
```

### Basic Usage

1. **Detect Map Anchors**
```bash
python scripts/detect_anchors.py --camera 0
```

2. **Compute Camera Extrinsics**
```bash
python scripts/compute_extrinsics.py --config config/marker_config.yaml
```

3. **Validate Camera Pose**
```bash
python scripts/validate_pose.py --duration 30
```

## 🔧 Configuration

Edit `config/marker_config.yaml` to define:
- World coordinates of each marker corner (IDs 0-3)
- Marker size in meters
- ArUco dictionary type

## 📊 Coordinate System

The world coordinate system is defined as follows:
- **Origin**: Corner where marker ID=0 is located
- **X-axis**: Along the long edge of the table
- **Y-axis**: Along the short edge of the table
- **Z-axis**: Perpendicular to the table (pointing up)

See `docs/coordinate_system.md` for detailed specifications.

## 🧪 Testing & Validation

Run the test suite:
```bash
python -m pytest tests/
```

Manual validation:
```bash
python scripts/validate_pose.py --visualize
```

## 📚 References

- OpenCV ArUco Detection: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- Camera Calibration: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- PnP Algorithms: https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html

## 🔗 Integration

This module integrates with:
- Camera calibration module (for intrinsic parameters)
- Object detection module (for transforming object coordinates)
- Main vision pipeline (for continuous pose updates)

## ⚠️ Troubleshooting

**Problem**: Markers not detected
- Check lighting conditions
- Verify marker print quality
- Ensure camera focus is correct

**Problem**: Unstable pose estimation
- Verify all 4 markers are visible
- Check for reflections or occlusions
- Recalibrate camera intrinsics

**Problem**: High reprojection error
- Verify marker physical positions in config
- Check marker size specification
- Ensure markers are flat and parallel to table
