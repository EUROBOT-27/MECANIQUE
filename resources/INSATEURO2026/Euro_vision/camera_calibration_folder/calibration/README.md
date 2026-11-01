# Camera Calibration Guide

This directory contains camera calibration results and tools for the Eurobot 2026 vision system.

## Quick Start

### 1. Generate Chessboard Pattern

```bash
python generate_chessboard.py
```

This creates `chessboard_pattern.png` that you need to print.

**Printing Instructions:**
- Print on A4 or larger paper at actual size (no scaling)
- Glue to a flat, rigid surface (cardboard or foam board)
- Ensure the pattern is completely flat
- Measure a printed square to verify it's 25mm x 25mm

### 2. Calibrate Camera

#### Option A: From Pre-captured Images

Take 15-20 photos of the chessboard pattern from different angles and distances:
- Move the chessboard around
- Tilt it at various angles
- Cover different parts of the camera's field of view
- Ensure good lighting

Then run:
```bash
python calibrate_camera.py --images "path/to/images/*.jpg"
```

#### Option B: Live Calibration from Camera

```bash
python calibrate_camera.py --camera 0
```

- Position the chessboard in the camera view
- Press SPACE when corners are detected to capture
- Capture 15-20 images from different positions/angles
- Press ESC when done

### 3. Test Calibration

```bash
# Check calibration quality
python test_calibration.py

# Test undistortion on an image
python test_calibration.py --test-image sample.jpg

# Test ArUco detection with calibration
python test_calibration.py --test-aruco aruco_test.jpg
```

## Output Files

### camera_calibration.json

Contains:
- `camera_matrix` (K): 3x3 intrinsic camera matrix with focal lengths and principal point
- `distortion_coefficients` (D): Lens distortion parameters (k1, k2, p1, p2, k3)
- `reprojection_error`: Calibration quality metric (lower is better, <0.5 is excellent)
- `image_size`: Resolution used for calibration
- Metadata: date, number of images, chessboard parameters

## Understanding Calibration Parameters

### Camera Matrix (K)
```
[fx  0  cx]
[ 0 fy  cy]
[ 0  0   1]
```
- `fx, fy`: Focal lengths in pixels
- `cx, cy`: Principal point (optical center)

### Distortion Coefficients (D)
```
[k1, k2, p1, p2, k3]
```
- `k1, k2, k3`: Radial distortion
- `p1, p2`: Tangential distortion

## Tips for Good Calibration

1. **Use enough images**: 15-20 minimum, more is better
2. **Vary positions**: Different distances, angles, and orientations
3. **Cover the field of view**: Get corners and center
4. **Good lighting**: Avoid shadows on the chessboard
5. **Keep it flat**: Any warping reduces accuracy
6. **Check reprojection error**: Should be < 1.0 pixel

## Integration with ArUco Detection

Load calibration in your code:

```python
import json
import numpy as np

# Load calibration
with open('camera_calibration.json', 'r') as f:
    cal = json.load(f)

camera_matrix = np.array(cal['camera_matrix'])
dist_coeffs = np.array(cal['distortion_coefficients'])

# Use in ArUco detection
import cv2

# Undistort image
undistorted = cv2.undistort(image, camera_matrix, dist_coeffs)

# Detect markers and estimate pose
corners, ids, rejected = detector.detectMarkers(undistorted)
rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
    corners, marker_size, camera_matrix, dist_coeffs
)
```

## Troubleshooting

### "Corners not found"
- Ensure chessboard is in focus
- Check lighting (avoid shadows)
- Make sure entire pattern is visible
- Try different angles

### High reprojection error (>1.0)
- Pattern might not be flat
- Images might be blurry
- Not enough variation in positions
- Re-calibrate with more/better images

### Poor ArUco pose estimation
- Recalibrate camera
- Verify marker size parameter
- Check if undistortion is applied
- Ensure markers are flat and well-lit
