# Marker Placement Guide

## 🎯 Objective

This guide describes the physical placement of 4 ArUco markers at the corners of the Eurobot playing field to establish a global coordinate reference system.

## 📏 Marker Specifications

### Marker IDs
- **ID 0**: Bottom-left corner (origin)
- **ID 1**: Bottom-right corner
- **ID 2**: Top-right corner
- **ID 3**: Top-left corner

### Physical Specifications
- **ArUco Dictionary**: `DICT_4X4_50` or `DICT_6X6_250`
- **Marker Size**: 100mm × 100mm (outer black border included)
- **Print Quality**: Minimum 300 DPI
- **Material**: Matte paper or cardstock (avoid glossy to reduce reflections)

## 🖨️ Printing Instructions

### 1. Generate ArUco Markers

Use OpenCV to generate markers:
```python
import cv2
import numpy as np

# Select dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Generate and save each marker
for marker_id in range(4):
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, 200)
    cv2.imwrite(f'marker_{marker_id}.png', marker_image)
```

### 2. Print Settings
- **Resolution**: 300 DPI minimum
- **Size**: 100mm × 100mm
- **Color Mode**: Black and white (no grayscale)
- **Paper**: Matte white cardstock
- **Margins**: Include white border around marker

### 3. Post-Processing
- Laminate markers to protect from wear
- Ensure lamination is perfectly flat (no bubbles)
- Cut precisely to size with white border

## 📍 Physical Placement

### Table Dimensions (Example)
- **Length**: 2000mm (X-axis)
- **Width**: 3000mm (Y-axis)
- Adjust according to actual Eurobot 2026 specifications

### Placement Procedure

1. **Clean the Surface**
   - Ensure corners are clean and flat
   - Remove any debris or dust

2. **Measure and Mark**
   - Mark exact corner positions
   - Use a ruler and level to ensure accuracy
   - Markers should be placed **outside** the playing area if possible

3. **Apply Markers**
   - Use double-sided tape or mounting squares
   - Ensure marker is perfectly flat (no wrinkles or bubbles)
   - Verify marker is parallel to table surface
   - Check that marker faces upward (visible to overhead camera)

4. **Verify Placement**
   - All 4 markers should be in the same plane
   - Markers should form a perfect rectangle
   - Measure diagonals to verify squareness

### Marker Orientation
- All markers should have the same orientation (top edge aligned)
- The white border should be clearly visible
- Markers should not be rotated relative to table edges

## 📐 World Coordinate Definition

Once placed, the markers define the world coordinate system:

```
         Y (3000mm)
         ↑
         |
    [3] -+- [2]
         |
         |
         |
    [0] -+- [1] → X (2000mm)
      Origin
```

- **Origin (0,0,0)**: Center of Marker ID=0
- **X-axis**: Points from Marker 0 to Marker 1
- **Y-axis**: Points from Marker 0 to Marker 3
- **Z-axis**: Points upward (perpendicular to table)

### Example Coordinates (in meters)

| Marker ID | X (m) | Y (m) | Z (m) |
|-----------|-------|-------|-------|
| 0         | 0.0   | 0.0   | 0.0   |
| 1         | 3.0   | 0.0   | 0.0   |
| 2         | 3.0   | 2.0   | 0.0   |
| 3         | 0.0   | 2.0   | 0.0   |

**Note**: These coordinates are based on Eurobot 2026 field dimensions (3.0m × 2.0m).

## ✅ Verification Checklist

Before proceeding to calibration:

- [ ] All 4 markers printed at correct size and quality
- [ ] Markers are laminated and flat
- [ ] Markers placed at exact corner positions
- [ ] All markers are in the same plane (parallel to table)
- [ ] Markers are visible from overhead camera position
- [ ] No glare or reflections on markers
- [ ] Marker IDs are correct (0, 1, 2, 3)
- [ ] Coordinate measurements recorded in config file
- [ ] Table is level and stable

## 🔧 Maintenance

- Inspect markers weekly for damage
- Clean with dry cloth (no liquids)
- Replace markers if:
  - Print quality degrades
  - Lamination becomes cloudy
  - Markers become detached or curled
  - Detection reliability drops

## 📸 Testing Visibility

After placement, test detection:
```bash
python scripts/detect_anchors.py --camera 0 --visualize
```

Expected result: All 4 markers should be detected in every frame when robot is absent.

## ⚠️ Common Issues

**Issue**: Markers not detected
- **Cause**: Poor lighting, glare, or incorrect print quality
- **Solution**: Adjust lighting, replace markers, use matte lamination

**Issue**: Inconsistent detection
- **Cause**: Markers not flat or parallel to table
- **Solution**: Re-apply markers ensuring flatness

**Issue**: Wrong marker pose
- **Cause**: Incorrect marker size in configuration
- **Solution**: Measure actual marker size and update config

## 📚 References

- Eurobot 2026 Rules: [Official Website]
- ArUco Marker Properties: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- Marker Generation Tool: `scripts/generate_markers.py`
