# ArUco Detection Examples

This directory contains example scripts demonstrating the ArUco marker detection system for Eurobot 2026.

## 📋 Examples Overview

| Script | Description | Usage |
|--------|-------------|-------|
| `01_generate_markers.py` | Generate all ArUco markers for the project | `python examples/01_generate_markers.py` |
| `02_detect_webcam.py` | Real-time marker detection from webcam | `python examples/02_detect_webcam.py` |
| `03_detect_from_image.py` | Detect markers in static images | `python examples/03_detect_from_image.py image.jpg` |
| `04_complete_demo.py` | Complete pipeline demonstration | `python examples/04_complete_demo.py` |

## 🚀 Quick Start

### 1. Generate Markers

First, generate all markers for the project:

```bash
python examples/01_generate_markers.py
```

This creates:
- Individual marker images in `markers/` directory
- Printable marker sheets ready for printing
- Markers organized by type (MAP, CAISSE, ENEMY)

**Output:**
- `markers/map_markers/` - Corner markers (IDs 0-3)
- `markers/caisse_markers/` - Wooden box markers (IDs 10-20)
- `markers/enemy_markers/` - Enemy robot markers (IDs 30-35)
- `markers/printable_*.png` - Ready-to-print sheets

### 2. Test Detection

#### Option A: Webcam (Real-time)

```bash
python examples/02_detect_webcam.py
```

**Features:**
- Real-time marker detection
- Live pose estimation (position and orientation)
- 3D axis visualization on markers
- Marker type classification
- Frame capture capability

**Controls:**
- `q` - Quit
- `s` - Save current frame
- `p` - Toggle pose information display

#### Option B: From Image

```bash
python examples/03_detect_from_image.py path/to/image.jpg
```

**Features:**
- Detect markers in any image file
- Display detailed pose information
- Save annotated output image
- Print detection results to console

#### Option C: Complete Demo

```bash
python examples/04_complete_demo.py
```

**Features:**
- Generates test markers on screen
- Uses webcam to detect them
- Demonstrates the complete pipeline
- No printing required for testing

**Perfect for:**
- Testing without physical markers
- Demonstrating the system
- Quick validation of setup

## 📖 Detailed Usage

### Example 1: Generate Markers

```python
from aruco_tools import MarkerGenerator
import cv2

# Create generator
generator = MarkerGenerator(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_size=200
)

# Generate single marker
generator.generate_marker(marker_id=0, output_path="marker_0.png")

# Generate batch of markers
generator.generate_markers_batch(
    marker_ids=[0, 1, 2, 3],
    output_dir="my_markers"
)

# Generate printable sheet
generator.generate_marker_sheet(
    marker_ids=[0, 1, 2, 3],
    output_path="sheet.png",
    cols=2
)
```

### Example 2: Detect from Webcam

```python
from aruco_tools import MarkerDetector
import cv2

# Initialize detector
detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_length=0.05  # 5cm markers
)

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    # Process frame
    processed_frame, pose_info = detector.process_frame(
        frame,
        draw_markers=True,
        draw_axis=True
    )
    
    # Display results
    if pose_info:
        for info in pose_info:
            print(f"Marker {info['id']}: "
                  f"pos=({info['position']['x']:.3f}, "
                  f"{info['position']['y']:.3f}, "
                  f"{info['position']['z']:.3f})")
    
    cv2.imshow('Detection', processed_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Example 3: Detect from Image

```python
from aruco_tools import MarkerDetector
import cv2

# Initialize detector
detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_length=0.05
)

# Load image
image = cv2.imread("test_image.jpg")

# Detect markers
processed_image, pose_info = detector.process_frame(image)

# Print results
for info in pose_info:
    marker_type = detector.classify_marker(info['id'])
    print(f"[{marker_type}] Marker ID: {info['id']}")
    print(f"  Position: {info['position']}")
    print(f"  Yaw: {info['yaw_deg']:.2f}°")

# Save result
cv2.imwrite("output.jpg", processed_image)
```

## 🔧 Configuration

### Marker Dictionary

The examples use `DICT_4X4_50` by default, which is suitable for the Eurobot project. Other options include:

- `DICT_4X4_50` - 4x4 markers, 50 IDs (recommended)
- `DICT_4X4_100` - 4x4 markers, 100 IDs
- `DICT_5X5_50` - 5x5 markers, 50 IDs
- `DICT_6X6_50` - 6x6 markers, 50 IDs

### Marker Size

Physical marker size affects pose estimation accuracy. Measure your printed markers and set:

```python
detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    marker_length=0.05  # 5cm = 0.05m
)
```

### Camera Calibration

For better pose estimation, calibrate your camera:

```python
import numpy as np

camera_matrix = np.array([
    [fx, 0, cx],
    [0, fy, cy],
    [0, 0, 1]
], dtype=np.float32)

dist_coeffs = np.array([k1, k2, p1, p2, k3])

detector = MarkerDetector(
    dictionary_type=cv2.aruco.DICT_4X4_50,
    camera_matrix=camera_matrix,
    dist_coeffs=dist_coeffs,
    marker_length=0.05
)
```

## 🎯 Marker ID Ranges

As per the Eurobot 2026 specification:

| Type | ID Range | Purpose |
|------|----------|---------|
| MAP | 0-3 | Fixed corner markers (global coordinate system) |
| CAISSE | 10-20 | Wooden box markers |
| ENEMY | 30+ | Enemy robot markers |

## 📝 Output Format

### Pose Information

Each detected marker returns:

```python
{
    'id': 0,                                    # Marker ID
    'rvec': [rx, ry, rz],                      # Rotation vector
    'tvec': [tx, ty, tz],                      # Translation vector
    'position': {
        'x': 0.05,                             # X position in meters
        'y': -0.03,                            # Y position in meters
        'z': 0.25                              # Z position (distance) in meters
    },
    'yaw_rad': 1.57,                           # Yaw angle in radians
    'yaw_deg': 90.0                            # Yaw angle in degrees
}
```

## 🐛 Troubleshooting

### No markers detected

1. Check lighting - ensure good, even lighting
2. Check focus - camera must be focused on markers
3. Check distance - try different distances
4. Check marker print quality - must be clear and high contrast

### Inaccurate pose estimation

1. Calibrate camera for better accuracy
2. Verify marker size is correct in code
3. Ensure markers are on flat surface
4. Check for lens distortion

### Poor performance

1. Reduce camera resolution if needed
2. Adjust detection parameters if necessary
3. Use larger markers for easier detection
4. Improve lighting conditions

## 🔗 Related Documentation

- [ArUco Implementation Guide](../ARUCO_GUIDE.md) - Complete API reference
- [Main README](../README.md) - Project overview
- [OpenCV ArUco Tutorial](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)

## 💡 Tips

1. **Print markers on matte paper** to avoid glare
2. **Maintain good lighting** without harsh shadows
3. **Keep markers flat** for accurate pose estimation
4. **Measure marker size accurately** for correct scale
5. **Test at different distances** to find optimal range
6. **Use printable sheets** for easy marker organization
