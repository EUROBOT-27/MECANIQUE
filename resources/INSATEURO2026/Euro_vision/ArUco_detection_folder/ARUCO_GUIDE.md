# ArUco Marker Detection - Implementation Guide

This directory contains a complete implementation of ArUco marker detection for the Eurobot 2026 project.

## 📁 Project Structure

```
Euro_vision/
├── aruco_tools/              # Core ArUco detection library
│   ├── __init__.py          # Package initialization
│   ├── marker_generator.py  # Generate ArUco markers
│   └── marker_detector.py   # Detect markers and estimate pose
├── examples/                 # Example scripts
│   ├── 01_generate_markers.py      # Generate all project markers
│   ├── 02_detect_webcam.py         # Real-time webcam detection
│   ├── 03_detect_from_image.py     # Detect markers in images
│   └── 04_complete_demo.py         # Complete pipeline demo
├── markers/                  # Generated marker images (created by scripts)
├── output/                   # Output images and results (created by scripts)
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `opencv-contrib-python` - For ArUco marker detection
- `numpy` - For numerical operations

### 2. Generate Markers

Generate all ArUco markers for the project:

```bash
python examples/01_generate_markers.py
```

This creates:
- **Map markers** (IDs 0-3): Fixed corner markers for global coordinate system
- **Caisse markers** (IDs 10-20): Markers for wooden boxes
- **Enemy markers** (IDs 30-35): Markers for enemy robot
- **Printable sheets**: Ready-to-print marker sheets

Output is saved to `markers/` directory.

### 3. Test Detection

#### Option A: Webcam Detection (Real-time)

```bash
python examples/02_detect_webcam.py
```

Controls:
- Press `q` to quit
- Press `s` to save current frame
- Press `p` to toggle pose information display

#### Option B: Image Detection

```bash
python examples/03_detect_from_image.py path/to/image.jpg
```

#### Option C: Complete Demo

```bash
python examples/04_complete_demo.py
```

This demo:
1. Creates test markers on screen
2. Opens webcam to detect them
3. Shows real-time pose estimation
4. Visualizes 3D axis on markers

## 📚 Features Implemented

### ✅ Task 1: Generate Dictionary + Print Markers

**File**: `aruco_tools/marker_generator.py`

- Generate individual markers with specific IDs
- Create printable sheets with multiple markers
- Support multiple ArUco dictionary types
- Configurable marker sizes and spacing
- Automatic labeling with marker IDs

**Example**:
```python
from aruco_tools import MarkerGenerator
import cv2

generator = MarkerGenerator(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_size=200
)

# Generate single marker
generator.generate_marker(marker_id=0, output_path="marker_0.png")

# Generate batch
generator.generate_markers_batch(
    marker_ids=[0, 1, 2, 3],
    output_dir="my_markers"
)

# Generate printable sheet
generator.generate_marker_sheet(
    marker_ids=[0, 1, 2, 3],
    output_path="marker_sheet.png",
    cols=2
)
```

### ✅ Task 2: Detect ArUco + Draw Bounding Box + Display ID

**File**: `aruco_tools/marker_detector.py`

- Detect ArUco markers in images and video streams
- Draw bounding boxes around detected markers
- Display marker IDs at center
- Classify markers by type (MAP, CAISSE, ENEMY)

**Example**:
```python
from aruco_tools import MarkerDetector
import cv2

detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_length=0.05  # 5cm physical size
)

# Detect from image
image = cv2.imread("test.jpg")
corners, ids, rejected = detector.detect_markers(image)

# Draw detected markers
result = detector.draw_detected_markers(image, corners, ids)
cv2.imshow("Detection", result)
cv2.waitKey(0)
```

### ✅ Task 3: Estimate Pose (Rvec, Tvec) Relative to Camera

**File**: `aruco_tools/marker_detector.py`

- Estimate 6DOF pose (rotation and translation vectors)
- Calculate position in 3D space (x, y, z)
- Compute orientation (yaw angle)
- Handle multiple markers simultaneously

**Example**:
```python
from aruco_tools import MarkerDetector
import cv2

detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_length=0.05  # Physical marker size in meters
)

image = cv2.imread("test.jpg")
processed_image, pose_info = detector.process_frame(image)

# Access pose information
for info in pose_info:
    print(f"Marker ID: {info['id']}")
    print(f"Position: {info['position']}")  # x, y, z in meters
    print(f"Rotation (rvec): {info['rvec']}")
    print(f"Translation (tvec): {info['tvec']}")
    print(f"Yaw angle: {info['yaw_deg']}°")
```

### ✅ Task 4: Visualize Axis on Marker to Confirm

**File**: `aruco_tools/marker_detector.py`

- Draw 3D coordinate axes on each detected marker
- X-axis: Red, Y-axis: Green, Z-axis: Blue
- Confirms correct pose estimation
- Visual verification of marker orientation

**Example**:
```python
from aruco_tools import MarkerDetector
import cv2

detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_length=0.05
)

image = cv2.imread("test.jpg")

# Process with axis visualization
processed_image, pose_info = detector.process_frame(
    image,
    draw_markers=True,  # Draw bounding boxes and IDs
    draw_axis=True      # Draw 3D axes
)

cv2.imshow("With Axes", processed_image)
cv2.waitKey(0)
```

## 🎯 Marker ID Ranges

As defined in the project README:

| Type | ID Range | Purpose |
|------|----------|---------|
| **MAP** | 0-3 | Fixed corner markers for global coordinate system |
| **CAISSE** | 10-20 | Wooden box markers |
| **ENEMY** | 30+ | Enemy robot markers |

## 🔧 Configuration

### Camera Calibration

For accurate pose estimation, you should calibrate your camera. The detector uses default camera parameters if none are provided, but real calibration improves accuracy.

```python
from aruco_tools import MarkerDetector
import numpy as np

# Your calibrated camera parameters
camera_matrix = np.array([
    [fx, 0, cx],
    [0, fy, cy],
    [0, 0, 1]
], dtype=np.float32)

dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)

detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    camera_matrix=camera_matrix,
    dist_coeffs=dist_coeffs,
    marker_length=0.05
)
```

### Marker Physical Size

The `marker_length` parameter is crucial for accurate pose estimation. It represents the physical size of the marker (black square only, not including white border) in meters.

Example:
- If your printed marker's black square is 5cm, use `marker_length=0.05`
- If it's 10cm, use `marker_length=0.10`

## 📖 API Reference

### MarkerGenerator

**Constructor:**
```python
MarkerGenerator(dictionary_type=cv2.aruco.DICT_4X4_50, marker_size=200)
```

**Methods:**
- `generate_marker(marker_id, output_path=None, border_bits=1)` - Generate single marker
- `generate_markers_batch(marker_ids, output_dir, border_bits=1)` - Generate multiple markers
- `generate_marker_sheet(marker_ids, output_path, cols=4, spacing=20)` - Generate printable sheet

### MarkerDetector

**Constructor:**
```python
MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    camera_matrix=None,
    dist_coeffs=None,
    marker_length=0.05
)
```

**Methods:**
- `detect_markers(image)` - Detect markers, returns (corners, ids, rejected)
- `estimate_pose(corners)` - Estimate pose, returns (rvecs, tvecs)
- `draw_detected_markers(image, corners, ids, border_color=(0,255,0))` - Draw markers
- `draw_axis(image, rvecs, tvecs, length=0.03)` - Draw 3D axes
- `process_frame(image, draw_markers=True, draw_axis=True)` - Complete processing pipeline
- `get_pose_info(rvecs, tvecs, ids)` - Get structured pose information
- `classify_marker(marker_id)` - Classify marker type

## 🧪 Testing

### Print and Test Markers

1. Generate markers:
   ```bash
   python examples/01_generate_markers.py
   ```

2. Print the generated sheets from `markers/printable_*.png`

3. Test detection:
   ```bash
   python examples/02_detect_webcam.py
   ```

4. Point your webcam at the printed markers

### Test Without Printing

Use the complete demo to test without printing:

```bash
python examples/04_complete_demo.py
```

This creates markers on screen and uses your webcam to detect them.

## 🔍 Troubleshooting

### No markers detected

1. **Check lighting**: Ensure good, even lighting
2. **Check focus**: Ensure camera is focused on markers
3. **Check distance**: Try different distances from camera
4. **Check dictionary**: Ensure using correct dictionary (DICT_4X4_50)
5. **Check print quality**: Ensure markers are printed clearly with good contrast

### Inaccurate pose estimation

1. **Calibrate camera**: Use OpenCV camera calibration
2. **Measure marker size**: Ensure `marker_length` is accurate
3. **Check marker flatness**: Markers should be on flat surface
4. **Reduce lens distortion**: Use calibrated distortion coefficients

### Poor detection performance

1. **Adjust detection parameters**: Modify `DetectorParameters` if needed
2. **Improve image quality**: Use higher resolution camera
3. **Optimize lighting**: Avoid glare and shadows
4. **Use larger markers**: Larger markers are easier to detect

## 🚀 Next Steps

1. **Camera Calibration**: Calibrate your overhead camera for accurate measurements
2. **Transform Pipeline**: Implement world coordinate transformation
3. **Enemy Tracking**: Add Kalman filter for smooth tracking
4. **Communication**: Integrate LoRa communication module
5. **Integration**: Combine with robot control system

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is part of the INSATEURO2026 Eurobot project. For questions or contributions, please refer to the main project repository.
