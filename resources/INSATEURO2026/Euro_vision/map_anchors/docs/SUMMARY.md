# Map Anchors Module - Documentation Summary

**Quick reference guide for the Map Anchors system**  
Last Updated: October 6, 2025

---

## 📋 Overview

The Map Anchors module establishes a **global coordinate system** for the Eurobot 2026 vision pipeline using 4 ArUco markers placed at the corners of the playing field.

**Purpose**: Transform all detected objects (caisses, enemy robot) from camera coordinates to a consistent world reference frame.

---

## 🎯 Quick Start Workflow

1. **Print & Place Markers** → See [Marker Placement](#marker-placement)
2. **Compute Camera Extrinsics** → See [Extrinsics Computation](#extrinsics-computation)
3. **Validate Camera Pose** → See [Validation](#validation)
4. **Use in Production** → Transform all detections to world coordinates

---

## 📐 Coordinate System

### World Frame Definition

```
                Y-axis (3.0m - table length)
                    ↑
                    |
         [3]--------+--------[2]
          |         |         |
          |    PLAYING FIELD  |
          |         |         |
         [0]--------+--------[1] → X-axis (2.0m - table width)
        Origin    (0,0,0)
         
         Z-axis: ⊙ (upward, perpendicular to table)
```

### Key Definitions

- **Origin (0,0,0)**: Center of ArUco marker ID=0 (bottom-left corner)
- **X-axis**: Points from marker 0 → 1 (table width - 3.0m)
- **Y-axis**: Points from marker 0 → 3 (table length - 2.0m)
- **Z-axis**: Points upward (perpendicular to table surface)
- **Handedness**: Right-handed coordinate system (X × Y = Z)
- **Units**: Meters (m) for distance, radians/degrees for angles

### Map Anchor Positions

| Marker ID | Position (X, Y, Z) [meters] | Corner |
|-----------|------------------------------|--------|
| 0 | (0.0, 0.0, 0.0) | Origin (bottom-left) |
| 1 | (3.0, 0.0, 0.0) | Bottom-right |
| 2 | (3.0, 2.0, 0.0) | Top-right |
| 3 | (0.0, 2.0, 0.0) | Top-left |

### Robot Orientation Convention

```
θ = 0°:   Robot facing +X direction (→)
θ = 90°:  Robot facing +Y direction (↑)
θ = 180°: Robot facing -X direction (←)
θ = 270°: Robot facing -Y direction (↓)
```

---

## 📍 Marker Placement

### Physical Specifications

- **ArUco Dictionary**: `DICT_6X6_250` (or `DICT_4X4_50`)
- **Marker Size**: 100mm × 100mm (10cm)
- **Print Quality**: Minimum 300 DPI
- **Material**: Matte paper/cardstock (avoid glossy to reduce glare)
- **Protection**: Laminate markers (flat, no bubbles)

### Placement Procedure

1. **Print Markers**
   ```python
   # Generate markers using:
   python map_anchors/scripts/generate_markers.py --output markers/ --size 200
   ```
   - Print at 300 DPI on matte cardstock
   - Include white border around marker
   - Laminate for protection

2. **Physical Installation**
   - Clean corner surfaces
   - Mark exact corner positions
   - Apply with double-sided tape
   - Ensure markers are perfectly flat and parallel to table
   - All markers must be in the same plane

3. **Verification**
   - Measure distances to verify rectangle
   - Check diagonals for squareness
   - All markers should have same orientation
   - Test visibility from camera:
     ```bash
     python map_anchors/scripts/detect_anchors.py --camera 0 --visualize
     ```

### ✅ Placement Checklist

- [ ] All 4 markers printed at 100mm × 100mm
- [ ] Markers laminated and flat (no bubbles/wrinkles)
- [ ] Placed at exact corner positions
- [ ] All markers parallel to table surface
- [ ] No glare or reflections
- [ ] Markers visible from overhead camera
- [ ] Correct IDs: 0 (bottom-left), 1 (bottom-right), 2 (top-right), 3 (top-left)

---

## 🔧 Extrinsics Computation

### What Are Extrinsics?

Camera extrinsics define the camera's position and orientation in world coordinates:
- **rvec**: Rotation vector (Rodrigues format)
- **tvec**: Translation vector (camera position)
- **T_world_cam**: 4×4 transformation matrix (camera to world)

### Computation Process

**Prerequisites**:
- ✅ Camera intrinsics calibrated (focal length, distortion coefficients)
- ✅ All 4 map anchors placed and visible
- ✅ Camera mounted (will not move after calibration)

**Algorithm**:
1. Detect all 4 markers in camera view
2. Build 3D-2D correspondences (16 points: 4 markers × 4 corners)
3. Solve PnP (Perspective-n-Point) problem using `cv2.solvePnP`
4. Build transformation matrix T_world_cam

**Implementation**:
```bash
# Compute extrinsics from live camera
python map_anchors/scripts/compute_extrinsics.py --camera 0 --config config/marker_config.yaml

# Multi-frame averaging (more robust)
python map_anchors/scripts/compute_extrinsics.py --camera 0 --frames 30
```

**Expected Output**:
```
calibration/
├── camera_extrinsics_rvec.npy     # Rotation vector
├── camera_extrinsics_tvec.npy     # Translation vector
└── T_world_cam.npy                # 4×4 transformation matrix
```

### Quality Metrics

**Reprojection Error**: Measure accuracy of computed pose
- **Good**: Mean < 1.0 pixel, Max < 2.0 pixels
- **Acceptable**: Mean < 2.0 pixels, Max < 3.0 pixels
- **Poor**: Mean > 2.0 pixels → Re-calibrate intrinsics or check marker placement

---

## ✅ Validation

### Why Validate?

Validation ensures:
- Camera pose is **stable** (doesn't drift over time)
- Pose estimation is **accurate** (low reprojection error)
- All markers are **consistently detected** (>95% detection rate)

### Validation Tests

**Test 1: Pose Stability Over Time**
```bash
python map_anchors/scripts/validate_pose.py --camera 0 --duration 30
```

**Success Criteria**:
- Position variance < 1mm in X, Y, Z
- Rotation variance < 0.1° in all axes

**Test 2: Reprojection Error**
- Mean error < 1.0 pixel ✅
- Max error < 2.0 pixels ✅
- 95th percentile < 1.5 pixels ✅

**Test 3: Detection Consistency**
- All 4 markers detected in >95% of frames ✅
- No extended detection gaps (max 5 consecutive frames)

### Running Validation

```bash
# Run full validation suite
python map_anchors/scripts/validate_pose.py --camera 0 --duration 30 --visualize

# Expected output:
# ✓ Pose stability: PASS (variance < 1mm)
# ✓ Reprojection error: PASS (mean < 1px)
# ✓ Detection consistency: PASS (>95% detection)
# ✓ Overall: VALIDATED - Ready for production
```

### Troubleshooting Validation Failures

| Issue | Cause | Solution |
|-------|-------|----------|
| High pose variance | Camera moved/vibrating | Re-mount camera securely |
| High reprojection error | Bad intrinsics calibration | Re-calibrate camera intrinsics |
| Low detection rate | Lighting/glare issues | Adjust lighting, check marker quality |
| Markers not detected | Wrong dictionary or size | Verify config matches physical markers |

---

## 🔄 Coordinate Transformations

### Camera to World Transform

```python
# Point detected in camera frame
P_cam = np.array([x_cam, y_cam, z_cam, 1])  # Homogeneous coordinates

# Load transformation matrix
T_world_cam = np.load('calibration/T_world_cam.npy')

# Transform to world frame
P_world = T_world_cam @ P_cam
x_world, y_world, z_world = P_world[:3]
```

### Object Detection Pipeline

```python
# 1. Detect marker in camera frame
corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict)
rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, K, D)

# 2. Build object pose in camera frame
R_obj, _ = cv2.Rodrigues(rvecs[0])
T_cam_obj = np.eye(4)
T_cam_obj[:3, :3] = R_obj
T_cam_obj[:3, 3] = tvecs[0].flatten()

# 3. Transform to world frame
T_world_obj = T_world_cam @ T_cam_obj

# 4. Extract world position
object_position_world = T_world_obj[:3, 3]  # (x, y, z) in meters
```

---

## 📁 Configuration Files

### marker_config.yaml

Located at: `map_anchors/config/marker_config.yaml`

```yaml
# ArUco dictionary
aruco:
  dictionary: "DICT_6X6_250"
  marker_size: 0.100  # 10cm

# Map anchor positions
markers:
  0:
    center: [0.000, 0.000, 0.000]
    size: 0.100
  1:
    center: [3.000, 0.000, 0.000]
    size: 0.100
  2:
    center: [3.000, 2.000, 0.000]
    size: 0.100
  3:
    center: [0.000, 2.000, 0.000]
    size: 0.100

# Field dimensions
field:
  width: 3.000   # X-axis (meters)
  length: 2.000  # Y-axis (meters)
```

---

## 📊 Sanity Checks

### Range Validation

When processing detections, verify coordinates are valid:

```python
def validate_world_coordinates(x, y, z):
    """Check if coordinates are physically plausible."""
    valid = True
    
    # Within table boundaries
    if not (0 <= x <= 2.0):
        print(f"⚠️ X coordinate {x:.3f} outside field [0, 2.0]m")
        valid = False
    
    if not (0 <= y <= 3.0):
        print(f"⚠️ Y coordinate {y:.3f} outside field [0, 3.0]m")
        valid = False
    
    # Objects on table surface
    if not (-0.05 <= z <= 0.5):
        print(f"⚠️ Z coordinate {z:.3f} unusual (expected ~0m for table objects)")
        valid = False
    
    return valid
```

### Expected Values

- **Map anchors**: Should be at exact positions (0,0,0), (3,0,0), (3,2,0), (0,2,0)
- **Caisses**: X ∈ [0, 3.0], Y ∈ [0, 2.0], Z ≈ 0.015m (half box height)
- **Enemy robot**: X ∈ [0, 3.0], Y ∈ [0, 2.0], Z ≈ 0.1-0.3m (robot height)

---

## 🛠️ Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `generate_markers.py` | Generate ArUco markers for printing | `--output markers/ --size 200` |
| `detect_anchors.py` | Test marker detection | `--camera 0 --visualize` |
| `compute_extrinsics.py` | Compute camera pose | `--camera 0 --config config.yaml` |
| `validate_pose.py` | Validate camera calibration | `--camera 0 --duration 30` |
| `visualize_anchors.py` | Visualize coordinate system | `--camera 0 --show-axes` |

---

## ⚠️ Common Issues

### Issue: Markers Not Detected
- **Cause**: Poor lighting, glare, wrong dictionary
- **Solution**: 
  - Improve lighting (diffuse, avoid direct glare)
  - Use matte lamination
  - Verify ArUco dictionary matches config

### Issue: High Reprojection Error (>2 pixels)
- **Cause**: Bad camera intrinsics or marker placement error
- **Solution**:
  - Re-calibrate camera intrinsics
  - Verify marker physical dimensions
  - Check marker corners are at correct world positions

### Issue: Pose Unstable (Drifting)
- **Cause**: Camera moving or vibrating
- **Solution**:
  - Mount camera more securely
  - Check for vibration sources
  - Use heavier camera mount

### Issue: Intermittent Detection Failures
- **Cause**: Markers partially occluded or at extreme angles
- **Solution**:
  - Ensure all markers visible from camera
  - Adjust camera position/angle
  - Increase marker size if too far from camera

---

## 📚 Detailed Documentation

For more in-depth information, see individual documentation files:

- **`coordinate_system.md`**: Complete coordinate system specification, transformations, and conventions
- **`marker_placement.md`**: Detailed marker printing and placement instructions
- **`extrinsics.md`**: Mathematical details of camera pose computation
- **`validation.md`**: Comprehensive validation procedures and quality metrics

---

## 🎯 Production Checklist

Before using the system in competition:

- [ ] All 4 markers printed, laminated, and placed
- [ ] Camera intrinsics calibrated
- [ ] Camera extrinsics computed and saved
- [ ] Validation passed (stability, accuracy, consistency)
- [ ] Coordinate transformations tested
- [ ] Sanity checks implemented
- [ ] Backup markers available (in case of damage)

---

## 📞 Support

**Issues**: Check troubleshooting sections in each document  
**Configuration**: `map_anchors/config/marker_config.yaml`  
**Examples**: `map_anchors/examples/full_pipeline_example.py`

**OpenCV Documentation**:
- ArUco Detection: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- Camera Calibration: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- Pose Estimation: https://docs.opencv.org/4.x/d7/d53/tutorial_py_pose.html

---

**Status**: ✅ Module fully documented and ready for use  
**Last Validation**: Pending - Run validation before competition  
**Next Steps**: Integrate with main vision pipeline, test with full system
