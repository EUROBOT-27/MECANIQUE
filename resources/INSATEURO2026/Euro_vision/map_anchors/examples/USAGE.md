# Real-World Object Localization - Usage Guide

## Overview

The `full_pipeline_example.py` script uses **YOUR calibrated camera parameters** to detect ArUco markers and return their real-world coordinates.

### What It Does
- ✅ Uses **iPhone XR intrinsics** from `camera_calibration_folder/calibration/`
- ✅ Uses **computed extrinsics** from `map_anchors/scripts/calibration_pnp_fixed/`
- ✅ Detects and localizes objects in **real-world coordinates** (meters)
- ✅ Supports two modes: **live extrinsics** or **pre-computed extrinsics**

### Detected Objects
- 📦 **Boxes (Caisses)**: IDs 36 (Blue), 47 (Yellow), 41 (Black)
- 🔴 **Enemy Robots**: IDs 30+
- 🟢 **Map Anchors**: IDs 20-23 (used for extrinsics computation)

---

## Quick Start

### Method 1: Using Pre-Computed Extrinsics (Recommended)

This method uses the extrinsics you already computed and validated:

```bash
cd map_anchors/examples
python full_pipeline_example.py --camera 1 --use-extrinsics
```

**Advantages**:
- No need to see all 4 map markers
- More stable (uses validated calibration)
- Faster (no live computation)

### Method 2: Live Extrinsics Computation

This method computes extrinsics in real-time from map markers:

```bash
cd map_anchors/examples
python full_pipeline_example.py --camera 1
```

**Requirements**:
- All 4 map markers (20, 21, 22, 23) must be visible
- Markers must be in their calibrated positions

---

## Output Format

### Console Output

The script prints detected objects to console:

```
📦 Box 36: x=1.234m, y=0.856m, z=0.045m, yaw=45.2°
🔴 Enemy 30: x=2.100m, y=1.500m, z=0.120m, yaw=-15.8°
```

### Visual Overlay

The video feed shows:
- **Green circles**: Map anchors (IDs 20-23)
- **Orange circles**: Boxes (IDs 36, 47, 41)
- **Red circles**: Enemy robots (ID 30+)
- **Text labels**: World coordinates (x, y, z, yaw)

---

## Understanding the Coordinates

### Coordinate System
- **Origin (0, 0, 0)**: Bottom-left corner of field (marker 22 position)
- **X-axis**: Right (0 to 3.0m)
- **Y-axis**: Forward (0 to 2.0m)
- **Z-axis**: Up from table surface (0 = table level)
- **Yaw**: Rotation around Z-axis (0° = facing +X direction)

### Example Output
```
📦 Box 36: x=1.234m, y=0.856m, z=0.045m, yaw=45.2°
```
This means:
- Box is 1.234m to the right of origin
- Box is 0.856m forward from origin
- Box is 4.5cm above table surface
- Box is rotated 45.2° counterclockwise

---

## Calibration Files Used

### 1. Camera Intrinsics (iPhone XR)
**File**: `camera_calibration_folder/calibration/camera_calibration.json`

```json
{
  "camera_matrix": [[662.175, 0, 315.633], [0, 658.500, 239.767], [0, 0, 1]],
  "distortion_coefficients": [[0.156, -1.383, -0.0004, -0.003, 2.793]],
  "image_size": [640, 480]
}
```

### 2. Camera Extrinsics
**File**: `map_anchors/scripts/calibration_pnp_fixed/extrinsics_metadata.yaml`

```yaml
camera_position_world:
  x: 0.777
  y: 2.768
  z: 2.429
rvec: [0.098, -2.775, 0.788]
tvec: [1.665, -1.085, 3.197]
```

Camera is positioned at (0.777m, 2.768m, 2.429m) in world coordinates.

### 3. Marker Configuration
**File**: `map_anchors/config/marker_config.yaml`

Defines physical positions of map markers 20-23.

---

## Command-Line Options

```bash
python full_pipeline_example.py [OPTIONS]

Options:
  --camera INT           Camera index (default: 1 for iPhone XR via Camo)
  --use-extrinsics       Use pre-computed extrinsics (recommended)
```

### Examples

```bash
# Use camera 0 with live extrinsics
python full_pipeline_example.py --camera 0

# Use camera 1 (iPhone XR) with pre-computed extrinsics
python full_pipeline_example.py --camera 1 --use-extrinsics

# Use camera 2 with live extrinsics
python full_pipeline_example.py --camera 2
```

---

## Troubleshooting

### Camera Not Found
```
❌ Error: Could not open camera 1
```
**Solution**: Check camera index. Try `--camera 0` or different index.

### Calibration Files Not Found
```
❌ Error: Camera calibration not found
```
**Solution**: Ensure you're running from project root or the calibration exists at:
- `camera_calibration_folder/calibration/camera_calibration.json`

### Insufficient Map Markers
```
✗ Insufficient markers (2/4)
```
**Solution**: 
- Ensure all 4 map markers (20-23) are visible in frame
- OR use `--use-extrinsics` flag to skip live computation

### Poor Detection
- **Low light**: Increase camera brightness/exposure
- **Motion blur**: Reduce camera movement
- **Small markers**: Move camera closer or use larger markers
- **Occlusion**: Ensure markers are not covered

---

## Integration Example

To integrate object detection into your robot control system:

```python
from full_pipeline_example import (
    load_camera_intrinsics,
    load_extrinsics,
    detect_and_classify_markers,
    estimate_marker_pose,
    transform_to_world
)

# Load calibration once
camera_matrix, dist_coeffs = load_camera_intrinsics(calib_path)
T_world_cam, T_cam_world, camera_pos = load_extrinsics(extrinsics_path)

# In your main loop
while True:
    frame = capture_frame()
    map_markers, box_markers, enemy_markers = detect_and_classify_markers(frame, aruco_dict)
    
    for marker_id, corners in box_markers.items():
        ok, rvec, tvec = estimate_marker_pose(corners, marker_size, camera_matrix, dist_coeffs)
        if ok:
            position, yaw = transform_to_world(T_world_cam, rvec, tvec)
            print(f"Box {marker_id} at ({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f})")
            
            # Send to robot via WiFi
            send_to_robot(marker_id, position, yaw)
```

---

## Next Steps

Now that you have real-world object localization working:

1. ✅ **Test with physical markers** - Print markers 36, 47, 41 and verify coordinates
2. ⏳ **Implement WiFi communication** - Send coordinates to Raspberry Pi
3. ⏳ **Add Kalman filtering** - Smooth enemy robot tracking
4. ⏳ **Optimize performance** - Reduce latency, handle occlusions
5. ⏳ **Field testing** - Test under competition conditions

---

## Technical Details

### Transformation Pipeline

```
Object Marker (camera frame)
    ↓ [rvec, tvec from solvePnP]
Camera Frame
    ↓ [T_world_cam from extrinsics]
World Frame (x, y, z, yaw)
```

### Accuracy
- **Position accuracy**: ~2mm std dev (from 60-frame validation)
- **Rotation accuracy**: ~0.001-0.002 rad std dev
- **Reprojection error**: ~16 pixels (acceptable for 4-point method)

### Performance
- **Detection rate**: ~20-30 FPS (depends on camera resolution)
- **Latency**: ~30-50ms per frame

---

## Support

For issues or questions:
1. Check error messages in console
2. Verify calibration files exist and are correct
3. Test with known marker positions
4. Review [map_anchors/README.md](../README.md) for detailed documentation
