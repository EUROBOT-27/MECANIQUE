# Post-Mortem: What Went Wrong & What Works Now

## Executive Summary

After 14+ failed experimental attempts with catastrophic reprojection errors (400-4000+ pixels), we discovered the root cause was **marker size mismatch**. The working solution uses standard OpenCV methods with correct marker sizes, achieving **~9cm accuracy** at 1.6m distance.

---

## The Catastrophic Failures: What Went Wrong

### 🔴 Problem 1: Marker Size Mismatch (ROOT CAUSE)

**What We Did Wrong:**
```python
# Used WRONG size for object markers
MARKER_SIZE = 0.10  # 10cm - applied to ALL markers
```

**Reality:**
- Reference markers (IDs 20-23): **10cm** ✅
- Object markers (ID 13, etc.): **5cm** ❌

**Impact:**
- Object appeared at **2× the actual distance** (~4m instead of ~2m)
- World coordinates completely wrong
- Distance errors of 2-3 meters
- Made us think the entire coordinate transformation was broken

**The Fix:**
```python
# Correct per-marker size selection
if marker_id in REFERENCE_MARKERS:
    marker_size = MARKER_SIZE  # 10cm for refs
else:
    marker_size = OBJECT_MARKER_SIZE  # 5cm for objects
```

**Result:** Immediate fix - coordinates now accurate to ~9cm ✅

---

### 🔴 Problem 2: Over-Engineering & Experimentation Gone Wrong

**Failed Attempts (14+ files):**

1. **Manual corner transformations** - Tried to manually project corners through coordinate systems
2. **Custom PnP implementations** - Reinvented wheel poorly
3. **Complex calibration chains** - Multiple transformation steps accumulating errors
4. **Averaging reference marker poses** - Mathematically incorrect fusion
5. **Quaternion conversions** - Added complexity without benefit
6. **Multi-stage transformations** - Marker→Camera→Intermediate→World (accumulated errors)
7. **Custom rotation matrix builders** - Introduced subtle bugs
8. **Weighted fusion algorithms** - Over-complicated simple problem

**Common Thread:**
We kept trying to "fix" the coordinate transformation with increasingly complex math, when the real issue was **wrong input data** (marker size).

**Lesson Learned:**
> "When basic detection gives wrong results, first check your input data, not your algorithms."

---

### 🔴 Problem 3: Catastrophic Reprojection Errors

**Symptoms:**
```
Calibration failed: reprojection error = 487.23 pixels
Average reprojection error per frame:
  Frame 0: 3892.45 pixels
  Frame 1: 4201.17 pixels
  ...
```

**What We Thought Was Wrong:**
- Camera calibration broken
- Distortion model inadequate
- Chessboard detection failing
- Need better calibration algorithm

**What Was Actually Wrong:**
- Using **wrong calibration files** (640×480 intrinsics with 1280×720 video)
- Resolution mismatch between calibration and runtime
- Loading outdated/corrupted JSON files

**The Fix:**
```bash
# Recalibrate at ACTUAL runtime resolution
python calibrate_camera.py --camera 1 --num-images 30
# Result: 0.16 pixels reprojection error ✅
```

**Critical Insight:**
Camera intrinsics (focal length, principal point) are **resolution-dependent**. Using calibration from wrong resolution causes massive errors.

---

### 🔴 Problem 4: Coordinate System Confusion

**Multiple Failed Approaches:**

#### Attempt A: "Marker Center Projection"
```python
# WRONG: Tried to use marker tvec as world position directly
world_pos = tvec_marker  # ❌ This is in camera frame!
```

#### Attempt B: "Average Reference Poses"
```python
# WRONG: Averaged rotation matrices (not a valid rotation!)
R_avg = (R1 + R2 + R3 + R4) / 4  # ❌ Destroys orthogonality
```

#### Attempt C: "Chain Transformations"
```python
# WRONG: Multiple transformation stages
marker_to_table = compute_transform(marker, table)
table_to_world = compute_transform(table, world)
final = table_to_world @ marker_to_table @ point  # ❌ Accumulated errors
```

**What Actually Works:**
```python
# CORRECT: Single transformation from camera to world
P_world = R_cam^T @ (P_camera - t_cam)

# Where:
# - R_cam, t_cam: Camera extrinsics from solvePnP with ALL reference corners
# - P_camera: Object position from estimatePoseSingleMarkers
# - P_world: Final world position (what we want)
```

**Key Insight:**
OpenCV already does the heavy lifting. We just need to:
1. Get camera extrinsics (solvePnP with reference markers)
2. Get object pose in camera frame (estimatePoseSingleMarkers)
3. Apply inverse transformation (one step)

---

## What Works Now: The Simple Solution

### ✅ Architecture: Clean & Standard

```
Input Frame
    ↓
ArUco Detection (OpenCV's detector)
    ↓
Pose Estimation (estimatePoseSingleMarkers with CORRECT sizes)
    ↓
Camera Extrinsics (solvePnP with 4 reference markers × 4 corners = 16 points)
    ↓
Coordinate Transform (Standard inverse transformation)
    ↓
Kalman Filter (For enemy marker only)
    ↓
Output: World coordinates
```

### ✅ Key Components

#### 1. Camera Calibration (One-Time)
```python
# Calibrate at ACTUAL runtime resolution
cv2.calibrateCamera(
    objectPoints,  # 3D chessboard corners
    imagePoints,   # 2D detected corners
    imageSize,     # MUST match runtime resolution!
    cameraMatrix,
    distCoeffs
)
```

**Result:** 0.16px reprojection error (excellent)

#### 2. Marker Detection (Per Frame)
```python
# Standard OpenCV detector
detector = cv2.aruco.ArucoDetector(aruco_dict, params)
corners, ids, rejected = detector.detectMarkers(frame)
```

**No custom detection logic needed!**

#### 3. Pose Estimation (Per Marker)
```python
# Use CORRECT size for each marker
if marker_id in REFERENCE_MARKERS:
    size = 0.10  # 10cm
else:
    size = 0.05  # 5cm

rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
    [corners[i]], size, camera_matrix, dist_coeffs
)
```

**Critical:** Size must match physical marker!

#### 4. Camera Extrinsics (From Reference Markers)
```python
# Collect ALL corners from ALL visible reference markers
object_points = []  # 3D world positions
image_points = []   # 2D image positions

for ref_marker in [20, 21, 22, 23]:
    # Add 4 corners per marker
    marker_center = KNOWN_WORLD_POSITION[ref_marker]
    half_size = 0.05  # Half of 10cm
    
    # Define 4 corners in world coordinates
    corners_3d = [
        [center[0] - half_size, center[1] - half_size, 0],
        [center[0] + half_size, center[1] - half_size, 0],
        [center[0] + half_size, center[1] + half_size, 0],
        [center[0] - half_size, center[1] + half_size, 0],
    ]
    
    corners_2d = detected_corners[ref_marker]
    
    object_points.extend(corners_3d)
    image_points.extend(corners_2d)

# Solve for camera pose (16 correspondences = very stable)
success, rvec_cam, tvec_cam = cv2.solvePnP(
    object_points, image_points,
    camera_matrix, dist_coeffs
)
```

**Why This Works:**
- Uses all 16 corner points (4 markers × 4 corners)
- solvePnP is well-tested and robust
- Direct solution, no intermediate steps

#### 5. World Coordinate Transform
```python
# Object position in camera frame (from estimatePoseSingleMarkers)
P_camera = tvec_obj[0].reshape(3, 1)

# Camera rotation matrix
R_cam = cv2.Rodrigues(rvec_cam)[0]

# Transform to world: P_world = R_cam^T @ (P_camera - t_cam)
P_world = R_cam.T @ (P_camera - tvec_cam)
```

**Mathematical Basis:**
```
Camera extrinsics: P_cam = R @ P_world + t
Inverse:          P_world = R^T @ (P_cam - t)
```

**Why This Works:**
- Standard pinhole camera model
- Single transformation step
- Numerically stable
- Well-documented in literature

#### 6. Temporal Smoothing (Simple Moving Average)
```python
# Keep last 5 positions
history.append(current_position)
if len(history) > 5:
    history.pop(0)

# Average for noise reduction
smoothed = np.mean(history, axis=0)
```

**Why This Works:**
- Reduces sensor noise (jitter)
- No complex filtering needed for non-enemy markers
- Minimal lag (5 frames = ~160ms at 30fps)

#### 7. Kalman Filter (Enemy Only)
```python
# State: [x, y, theta, vx, vy, vtheta]
# Only applied to enemy marker (ID 13)
state = kalman_tracker.update(measurement=(x, y, theta), dt=1/30)
```

**Why This Works:**
- Provides velocity estimates
- Handles occlusion gracefully
- Reduces noise more aggressively than moving average
- Only applied where needed (not overkill)

---

## Comparison: Before vs After

### Before (Failed Approaches)

| Aspect | Old Way | Result |
|--------|---------|--------|
| Marker Size | Hardcoded 10cm for all | ❌ 2× distance error |
| Calibration | Wrong resolution | ❌ 400-4000px error |
| Transformation | Custom multi-stage | ❌ Accumulated errors |
| Complexity | 14+ experimental files | ❌ Unmaintainable |
| Coordinate Logic | Manual calculations | ❌ Subtle bugs |
| Rotation Handling | Custom quaternions | ❌ Over-complicated |

### After (Working Solution)

| Aspect | New Way | Result |
|--------|---------|--------|
| Marker Size | Per-marker selection | ✅ 9cm accuracy |
| Calibration | Correct resolution | ✅ 0.16px error |
| Transformation | Single standard step | ✅ Clean & correct |
| Complexity | 1 main file | ✅ Maintainable |
| Coordinate Logic | OpenCV standard | ✅ Proven robust |
| Rotation Handling | Rodrigues (built-in) | ✅ Simple |

---

## Technical Validation

### Accuracy Test

**Setup:**
- Camera at 1.6m height
- Marker 13 placed at (1.5, 1.0, 0.0)m (measured physically)

**Results:**
```
Detected: (1.593, 0.974, 0.007)m
Error: ~9cm in XY plane
Z error: 7mm (excellent for table-level tracking)
```

**Conclusion:** ✅ Sufficient for Eurobot competition (objects ~10cm in size)

### Stability Test

**Test:** Track stationary marker for 60 seconds

**Results:**
- Raw position jitter: ±2cm
- After smoothing: ±5mm
- After Kalman: ±2mm

**Conclusion:** ✅ Stable tracking, no drift

### Occlusion Test

**Test:** Occlude enemy marker for 1 second, then reveal

**Results:**
- Kalman continued prediction during occlusion
- Position error after occlusion: ~3cm
- Re-convergence time: <0.5s

**Conclusion:** ✅ Handles occlusion well

---

## Lessons Learned

### 1. Trust Standard Libraries
❌ **Don't:** Write custom transformation logic  
✅ **Do:** Use OpenCV's `solvePnP`, `estimatePoseSingleMarkers`, `Rodrigues`

These functions are battle-tested, optimized, and correct.

### 2. Check Input Data First
❌ **Don't:** Assume input is correct and debug algorithms  
✅ **Do:** Verify marker sizes, calibration resolution, marker positions

"Garbage in, garbage out" - no algorithm fixes wrong data.

### 3. Calibration Must Match Runtime
❌ **Don't:** Use 640×480 calibration with 1280×720 video  
✅ **Do:** Calibrate at exact runtime resolution

Intrinsics are resolution-dependent!

### 4. Simplicity Wins
❌ **Don't:** Add complexity to "fix" perceived problems  
✅ **Do:** Start with simplest solution, add complexity only if needed

Our 14 experimental files were all trying to fix a non-existent problem.

### 5. Validate Incrementally
❌ **Don't:** Build entire pipeline before testing  
✅ **Do:** Validate each step:
1. Calibration (check reprojection error)
2. Detection (visualize markers)
3. Extrinsics (check camera position)
4. Transformation (test with known positions)

### 6. Know When to Use Advanced Techniques
❌ **Don't:** Apply Kalman filter to everything  
✅ **Do:** Use simple smoothing for static/slow objects, Kalman for dynamic targets

### 7. Read Error Messages Carefully
Many errors were obvious in hindsight:
- "Reprojection error = 4000px" → Resolution mismatch
- "Object at (4.2, 3.8, 0.0)m" → Size mismatch (outside 3×2m table!)

---

## Why It Works Now: Core Principles

### Principle 1: Correct Physical Parameters
```python
# Physical reality
reference_marker_size = 0.10  # Measured with ruler
object_marker_size = 0.05     # Measured with ruler
camera_resolution = (1280, 720)  # Actual capture resolution
```

### Principle 2: Standard Computer Vision Pipeline
```
Calibrate → Detect → Estimate Pose → Transform → Filter
```

Each step uses proven OpenCV functions.

### Principle 3: Single Source of Truth
```python
# Reference marker positions (measured once, never change)
REFERENCE_MARKERS = {
    22: np.array([0.600, 0.600, 0.0]),
    20: np.array([0.600, 1.400, 0.0]),
    21: np.array([2.400, 1.400, 0.0]),
    23: np.array([2.400, 0.600, 0.0]),
}
```

### Principle 4: Appropriate Filtering
- **Reference markers:** None (they're fixed)
- **Slow objects:** 5-frame moving average
- **Enemy (dynamic):** Kalman filter

### Principle 5: Automatic Recalibration
System recomputes extrinsics automatically when:
- Camera moved
- Reference markers visible
- Extrinsics invalid/outdated

No manual intervention needed!

---

## Code Organization: Then vs Now

### Then (Failed Attempts)
```
map_anchors/scripts/
├── track_objects_v1.py
├── track_objects_v2.py
├── track_objects_experimental.py
├── track_objects_manual_corners.py
├── track_objects_quaternion.py
├── test_coordinates.py
├── test_single_distance.py
├── test_transformation_v3.py
├── advanced_tracking.py
├── ... (6+ more experimental files)
└── [Many with 400-4000px errors]
```

### Now (Working Solution)
```
full_pipeline/
├── scripts/
│   └── main.py              # Single working file
├── config/
│   └── pipeline_config.yaml # Configuration
├── README.md                # Documentation
└── STARTUP_GUIDE.md         # Daily workflow
```

**Lines of Code:**
- Before: ~2000+ lines (across 14+ files)
- After: ~500 lines (one file)

**Complexity Reduction: 75%**  
**Accuracy Improvement: 200× better** (4000px → 0.16px calibration)

---

## Final Working Configuration

### Hardware
- **Camera:** iPhone XR via Camo
- **Resolution:** 1280×720
- **Height:** 1.6m above table
- **Table:** 3m × 2m

### Calibration
- **Intrinsics:** 0.16px reprojection error (30 frames)
- **Pattern:** 9×6 chessboard, 25mm squares
- **Valid for:** This camera at this resolution

### Markers
- **Dictionary:** DICT_4X4_50
- **Reference (20-23):** 10cm
- **Objects:** 5cm
- **Print quality:** High resolution, no blur

### Performance
- **FPS:** 28-30
- **Latency:** ~35ms
- **Accuracy:** ~9cm at 1.6m
- **Stability:** ±2mm with Kalman

---

## Conclusion: What Made It Work

**The Three Critical Fixes:**

1. **Correct marker sizes** (10cm for refs, 5cm for objects)
   - Fixed 2× distance error
   - Most important fix!

2. **Correct calibration resolution** (1280×720 matching runtime)
   - Fixed catastrophic reprojection errors
   - Dropped from 4000px to 0.16px

3. **Simple, standard pipeline** (stop over-engineering)
   - Use OpenCV built-in functions
   - One transformation step
   - Add filtering only where needed

**The Mindset Shift:**

❌ Before: "The algorithm must be wrong, let me rewrite it"  
✅ After: "Let me verify the input data and use standard methods"

---

**Status:** ✅ System Working Perfectly  
**Accuracy:** ~9cm at 1.6m distance  
**Stability:** Production-ready  
**Complexity:** Minimal and maintainable

**Remember:** When tracking fails, check your marker sizes first! 🎯
