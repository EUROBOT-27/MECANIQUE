# 📚 Code Reading Guide - From Beginner to Expert

This guide tells you **exactly what to read** and **in what order** to understand the entire vision system.

**🚨 IMPORTANT UPDATE (November 2025):**
- **Source of Truth**: `full_pipeline/` is now the consolidated active codebase
- **Legacy folders** (`map_anchors/`, `ArUco_detection_folder/`, `caisses_detection/`, `kalman_filter/`) preserved for reference but deprecated
- **Eurobot 2026 Standards**: Map anchors IDs 20-23, ArUco DICT_4X4_50, field 3.0m × 2.0m
- **Camera calibrations preserved**: iPhone XR (Camo) calibrations in `camera_calibration_folder/calibration/`
- **New distance script**: `ArUco_detection_folder/examples/aruco_distance_alert.py` for quick ROS/testing integration

---

## 🎯 Phase 1: Core Concepts (1-2 hours)

### Step 1: Understand ArUco Markers (30 min)

**📁 Read in this order:**

1. **`ArUco_detection_folder/aruco_tools/marker_generator.py`** (15 min)
   - **Focus on**: `generate_marker()` function
   - **Learn**: How markers are created, what IDs mean
   - **Key insight**: Markers are just black/white square patterns with unique IDs

2. **`ArUco_detection_folder/aruco_tools/marker_detector.py`** (15 min)
   - **Focus on**: `detect_markers()` and `estimate_pose()` functions
   - **Learn**: How OpenCV detects markers, corner ordering
   - **Key insight**: Detection returns corners (4 per marker) and IDs

3. **`ArUco_detection_folder/examples/02_detect_webcam.py`** (5 min)
   - **Run it!** See live detection
   - **Learn**: Basic detection loop
   - **Key insight**: Detection is just: read frame → detect → display

**✅ By now you should understand:**
- What ArUco markers are
- How detection works (finds corners)
- Corner order: [top-left, top-right, bottom-right, bottom-left]
- Marker IDs identify different markers

---

### Step 2: Camera Calibration (20 min)

**📁 Read in this order:**

1. **`camera_calibration_folder/calibration/iphone_xr_720p.json`** (5 min)
   - **Look at**: `camera_matrix` and `distortion_coefficients`
   - **Learn**: These correct for lens distortion and enable 3D measurements
   - **Key values**:
     ```json
     fx = 1637 (horizontal focal length in pixels)
     fy = 1613 (vertical focal length in pixels)
     cx = 555 (principal point X - image center)
     cy = 368 (principal point Y - image center)
     ```

2. **`camera_calibration_folder/calibrate_camera.py`** (15 min)
   - **Focus on**: `CameraCalibrator` class, especially `calibrate()` method
   - **Learn**: How chessboard detection computes camera parameters
   - **Key insight**: Calibration corrects lens distortion for accurate 3D measurements

**✅ By now you should understand:**
- Camera intrinsics (fx, fy, cx, cy) - internal camera parameters
- Distortion coefficients - correct barrel/pincushion distortion
- Why calibration matters - enables accurate distance/angle measurements

---

## 🗺️ Phase 2: Full Pipeline System (2-3 hours) ⭐ **ACTIVE CODEBASE**

This is **YOUR MAIN SYSTEM** now! All work consolidated here.

### Step 3: Configuration & Setup (20 min)

**📁 Read in this order:**

1. **`full_pipeline/QUICKSTART.md`** (5 min)
   - Quick installation and first-run instructions
   - PowerShell-friendly commands for Windows
   - Shows minimal example to get started

2. **`full_pipeline/config.yaml`** (10 min)
   ```yaml
   field:
     width: 3.0   # Eurobot 2026: 3 meters
     height: 2.0  # Eurobot 2026: 2 meters
   
   map_anchors:
     marker_ids: [20, 21, 22, 23]  # Eurobot 2026 official IDs
     marker_size: 0.100  # 10 cm markers
     inset: 0.6  # 60 cm from field edges
     # Physical mapping (verified by scanning):
     positions:
       22: [0.600, 0.600, 0.000]  # Bottom-left (ID 22)
       23: [2.400, 0.600, 0.000]  # Bottom-right (ID 23)
       21: [2.400, 1.400, 0.000]  # Top-right (ID 21)
       20: [0.600, 1.400, 0.000]  # Top-left (ID 20)
   
   aruco:
     dictionary: "DICT_4X4_50"  # Eurobot 2026 standard
   ```
   - **Learn**: Field dimensions and anchor positions for Eurobot 2026
   - **Key insight**: Marker positions in meters, Z=0 means on table surface
   - **Important**: All map anchors (20-23) use DICT_4X4_50; caisse markers can use different dictionaries

3. **`full_pipeline/calibration_data/my_camera.json`** (5 min)
   - Camera intrinsics (fx, fy, cx, cy) and distortion coefficients
   - OR use iPhone calibrations from `camera_calibration_folder/calibration/iphone_xr_720p.json`
   - **Key insight**: Intrinsics required for 3D pose estimation

**✅ By now you should understand:**
- Map anchors (IDs 20-23) define the Eurobot 2026 playing field coordinate system
- Physical mapping: ID 22=Bottom-left, ID 23=Bottom-right, ID 21=Top-right, ID 20=Top-left
- Field: 3.0m × 2.0m; anchors at 0.6m inset from edges
- ArUco dictionary DICT_4X4_50 for anchors (standardized across team)
- World coordinates: X (width), Y (depth), Z (height) with origin at field corner

---

### Step 4: Core Detection Modules (READ IN ORDER!) (1.5 hours)

#### A. **`full_pipeline/src/aruco_detector.py`** - ArUco Detection (30 min)

**🎯 Purpose**: Detect map anchors (20-23) and caisse markers (36, 47, 41), compute per-marker poses

**Key class to read:**
```python
class ArucoDetector:
    MAP_IDS = [20, 21, 22, 23]      # Eurobot 2026 map anchors
    CAISSE_IDS = [36, 47, 41]       # Caisse markers
    
    def detect_markers(self, frame):
        # 1. Get ArUco dictionary (DICT_4X4_50)
        # 2. Detect ALL markers in frame
        # 3. Filter for MAP_IDS + CAISSE_IDS
        # 4. Return corners and IDs (2D detection)
    
    def estimate_poses(self, frame, corners, ids):
        # Uses cv2.aruco.estimatePoseSingleMarkers
        # Returns per-marker rvec, tvec (camera-frame poses)
```

**What to understand:**
- ✅ Uses DICT_4X4_50 by default (Eurobot 2026 standard)
- ✅ Detects markers and computes per-marker poses (rvec/tvec) using intrinsics
- ✅ Returns camera-frame coordinates (not yet world coordinates)
- ✅ This is the foundation for all marker-based detection

**Quick test (PowerShell):**
```powershell
cd full_pipeline
python main.py --camera 0 --mode detect
```

**⚠️ IMPORTANT**: This computes per-marker poses. For world coordinates, you also need extrinsics (camera position in world).

---

#### B. **`full_pipeline/src/coordinate_transformer.py`** - World Transform (45 min) ⭐ MOST IMPORTANT

**🎯 Purpose**: Transform camera-frame marker poses into world coordinates using extrinsics

**Key class to read:**

```python
class CoordinateTransformer:
    def __init__(self, anchor_world_coords, camera_matrix, dist_coeffs):
        # anchor_world_coords: IDs 20-23 positions in meters
        # camera_matrix, dist_coeffs: from calibration
    
    def compute_extrinsics(self, anchor_corners_2d):
        # 1. Detect map anchors (20-23) in frame
        # 2. Collect 3D-2D point correspondences
        #    - 3D: world positions from config
        #    - 2D: detected pixel corners
        # 3. Solve PnP (Perspective-n-Point) with RANSAC
        success, rvec, tvec = cv2.solvePnPRansac(...)
        # 4. Build T_world_cam (4×4 transformation matrix)
        return T_world_cam
    
    def camera_to_world(self, camera_coords):
        # Transform point from camera frame to world frame
        # Uses T_world_cam computed from anchors
        return world_coords
```

**Key concepts to understand:**

**What is PnP (Perspective-n-Point)?**
- Mathematical algorithm that computes camera position from point correspondences
- Input: 
  - 3D points in world coordinates (anchor centers from config)
  - 2D points in image (anchor corners from detection)
  - Camera intrinsics (fx, fy, cx, cy, distortion)
- Output:
  - `rvec`: Rotation vector (camera orientation relative to world)
  - `tvec`: Translation vector (camera position in world)

**Transformation flow:**
```
Marker in camera frame (rvec, tvec from estimatePoseSingleMarkers)
         ↓
Apply T_world_cam (from compute_extrinsics)
         ↓
Marker position in world frame (X, Y, Z on field)
```

**Why it might fail:**
- ⚠️ Not enough anchors visible (need at least 3, prefer all 4)
- ⚠️ Marker orientation mismatch (if physical markers rotated vs. config)
- ⚠️ Poor calibration (wrong intrinsics)
- ⚠️ Incorrect anchor positions in config.yaml

**Quick test (PowerShell):**
```powershell
cd full_pipeline
python main.py --camera 0 --mode transform --map-width 3.0 --map-height 2.0
```

**✅ This module REQUIRES camera intrinsics and anchor positions!** It does 3D world transform.

---

#### C. **`full_pipeline/main.py`** - Entry Point & CLI (20 min)

**🎯 Purpose**: Unified CLI runner with multiple modes (detect, transform, full-pipeline)

**Modes:**
```python
--mode detect       # Just detect markers, show IDs and pixel corners
--mode transform    # Detect + compute world coordinates (needs anchors visible)
--mode full         # Full pipeline with visualization (default)
```

**Example runs:**
```powershell
# Detect only (no world transform)
python main.py --camera 0 --mode detect

# Compute world coordinates (requires anchors 20-23 visible)
python main.py --camera 0 --mode transform --map-width 3.0 --map-height 2.0

# Full pipeline with intrinsics
python main.py --camera 0 --intrinsics calibration_data/my_camera.json --mode full
```

**What to understand:**
- Entry point orchestrates ArucoDetector + CoordinateTransformer
- Can run with or without intrinsics (detect mode vs. transform mode)
- CLI accepts camera index, resolution, intrinsics path, map size

---

#### D. **`ArUco_detection_folder/examples/aruco_distance_alert.py`** - Distance Testing (15 min) 🆕

**🎯 Purpose**: Quick distance measurement for ROS integration / threshold testing

**Key features:**
```python
# Detects ArUco marker, computes camera-to-marker distance (Z), prints to stdout
# - Draws 3D axes and 2D arrow overlay on marker
# - Prints per-frame parseable lines: DISTANCE_CM <id> <distance>
# - Prints final JSON on exit: {"last_measured_cm": <value>}
# - Exit code 0 if measurement captured, 2 otherwise
```

**Run it (PowerShell):**
```powershell
cd ArUco_detection_folder\examples
python aruco_distance_alert.py --camera 2 --intrinsics "..\..\camera_calibration_folder\calibration\iphone_xr_720p.json" --threshold-cm 80
```

**What to understand:**
- Uses iPhone (Camo) calibration by default (iphone_xr_720p.json)
- Marker size hardcoded to 0.10 m (10 cm) — accurate absolute distances
- Useful for quick tests: "robot reacts when marker < 80 cm away"
- Stdout lines parseable by ROS or shell scripts

---

## 🔧 Phase 3: Integration & Advanced Topics (1-2 hours)

### Step 5: Camera Calibration Deep Dive (30 min)

**📁 `camera_calibration_folder/calibrate_camera.py`**

**Why calibration matters:**
- Corrects lens distortion (barrel/pincushion)
- Provides intrinsics (fx, fy, cx, cy) needed for accurate 3D measurements
- Required for pose estimation (estimatePoseSingleMarkers, solvePnP)

**Preserved calibrations:**
- `camera_calibration_folder/calibration/iphone_xr_720p.json` (iPhone XR horizontal via Camo)
- `camera_calibration_folder/calibration/iphone_xr_720p_vertical.json` (iPhone XR vertical)
- `full_pipeline/calibration_data/my_camera.json` (default USB webcam)

**How to calibrate a new camera:**
```powershell
cd camera_calibration_folder
python calibrate_camera.py --camera 0 --output calibration/new_camera.json
```

**What to understand:**
- Calibration uses chessboard pattern (9×6 corners)
- Takes ~20-30 images from different angles
- Computes camera_matrix and distortion_coefficients
- Reprojection error < 0.5 pixels = excellent, < 1.0 = good

---

### Step 6: Full Pipeline Workflow (30 min)

**📁 `full_pipeline/IMPLEMENTATION.md` and `full_pipeline/SUMMARY.md`**

**Complete data flow:**
```
1. Camera frame (BGR image)
   ↓
2. ArucoDetector.detect_markers()
   → Returns marker IDs and 2D pixel corners
   ↓
3. ArucoDetector.estimate_poses()
   → Returns per-marker rvec, tvec (camera-frame poses)
   ↓
4. CoordinateTransformer.compute_extrinsics()
   → Uses anchors 20-23 to compute T_world_cam (camera pose in world)
   ↓
5. CoordinateTransformer.camera_to_world()
   → Transforms marker poses from camera frame to world frame
   ↓
6. World coordinates (X, Y, Z in meters on Eurobot field)
```

**Read these docs to understand:**
- How modules connect
- When intrinsics are required (steps 3-5)
- When you can skip extrinsics (if only using camera-frame distances)

---

### Step 7: Legacy Modules (Reference Only)

⚠️ **These folders are deprecated but preserved for reference:**

**📁 `map_anchors/`** - Original extrinsics experiments
- `scripts/compute_extrinsics.py` - Standalone PnP solver
- `scripts/detect_anchors.py` - Basic 2D detection
- `scripts/validate_pose.py` - Reprojection error checking
- **Status**: Superseded by `full_pipeline/src/coordinate_transformer.py`

**📁 `caisses_detection/`** - Standalone caisse detector
- Used markers 36, 47, 41 (DICT_6X6_250 originally)
- **Status**: Now integrated into `full_pipeline/src/aruco_detector.py` with DICT_4X4_50

**📁 `kalman_filter/`** - Trajectory smoothing
- **Status**: Not yet integrated into full_pipeline; can be added when needed

**You don't need to read these unless debugging legacy code.**

---

## 🎓 Learning Checkpoints

After each phase, test yourself:

### ✅ Phase 1 Checkpoint:
- [ ] Can explain what ArUco markers are and how OpenCV detects them
- [ ] Know what camera intrinsics mean (fx, fy, cx, cy) and distortion coefficients
- [ ] Understand why calibration is needed (accurate 3D measurements)

### ✅ Phase 2 Checkpoint:
- [ ] Know the difference between `ArucoDetector` (per-marker poses in camera frame) and `CoordinateTransformer` (world-frame transform)
- [ ] Understand what PnP solver does (computes camera pose from 3D↔2D correspondences)
- [ ] Can explain Eurobot 2026 field coordinate system (3.0m × 2.0m, anchors 20-23 at 0.6m inset)
- [ ] Know which ArUco dictionary to use (DICT_4X4_50 for anchors)

### ✅ Phase 3 Checkpoint:
- [ ] Can describe full pipeline: detection → per-marker poses → extrinsics → world transform
- [ ] Understand when intrinsics are required (any 3D calculation) vs. when not (2D detection only)
- [ ] Know how to use `aruco_distance_alert.py` for quick distance tests
- [ ] Understand the difference between legacy folders and active `full_pipeline/` codebase

---

## 🔍 Common Questions Answered

### Q: When do I need camera intrinsics?

**Answer:**

| Task | Needs Intrinsics? | Why? |
|------|-------------------|------|
| Detect markers (find IDs) | ❌ NO | Just pattern recognition |
| Compute marker pose (rvec, tvec) | ✅ YES | Need to compute 3D angles/distances |
| Compute camera extrinsics | ✅ YES | PnP solver requires intrinsics |
| Validate pose | ✅ YES | Projection requires intrinsics |
| Transform to world coords | ✅ YES | Uses camera pose from PnP |

**Simple rule**: 
- **2D detection only** → No intrinsics needed
- **Any 3D calculation** → Intrinsics required

---

### Q: What's the difference between marker pose and camera pose?

**Marker pose**: Position/orientation of marker relative to camera
- Computed per marker
- Used for individual object tracking
- Example: "Caisse marker 36 is 1.5m away, rotated 30°"

**Camera pose** (extrinsics): Position/orientation of camera relative to world
- Computed from ALL map anchors together
- Used to transform everything to world coordinates
- Example: "Camera is at position [1.2, 0.8, 0.5] looking down at field"

---

### Q: Why might compute_extrinsics fail?

**Most common reasons:**

1. **Corner order mismatch** (⚠️ YOUR LIKELY ISSUE)
   - Config assumes all markers face same direction
   - Physical markers might be rotated
   - Solution: Use marker centers instead of corners, or fix config

2. **Not enough markers detected**
   - Need all 4 markers (20-23) visible
   - Solution: Improve lighting, marker placement

3. **Poor calibration**
   - Intrinsics are wrong
   - Solution: Recalibrate camera

4. **Marker positions wrong in config**
   - Config doesn't match physical setup
   - Solution: Measure and update `marker_config.yaml`

---

## 📊 Data Flow Diagram

```
Camera Frame (1280×720 pixels)
    ↓
[ArUco Detection] (NO intrinsics needed)
    ↓
Marker corners (2D pixel coordinates)
    ↓
    ├→ [Simple Detection] → Display on screen
    │
    └→ [PnP Solver] (NEEDS intrinsics + 3D marker positions)
           ↓
       Camera Pose (rvec, tvec)
           ↓
       [Coordinate Transform]
           ↓
       World Coordinates (meters on field)
```

---

## 🎯 Quick Reference: Which Module/Script Does What?

### Active Codebase (`full_pipeline/`)

| Module/Script | Input | Output | Uses Intrinsics? |
|--------|-------|--------|------------------|
| `src/aruco_detector.py` | Camera frame | Marker IDs, 2D corners, per-marker poses (rvec, tvec) | ✅ YES (for poses) |
| `src/coordinate_transformer.py` | Anchor corners + intrinsics | Camera pose (T_world_cam), world coords | ✅ YES |
| `main.py --mode detect` | Camera frame | Marker IDs, 2D pixel corners (no poses) | ❌ NO |
| `main.py --mode transform` | Camera frame + intrinsics + anchors | Marker world positions (X, Y, Z) | ✅ YES |
| `main.py --mode full` | Camera frame + intrinsics + config | Full visualization + world coords | ✅ YES |

### Quick Testing / ROS Integration

| Script | Input | Output | Uses Intrinsics? |
|--------|-------|--------|------------------|
| `ArUco_detection_folder/examples/aruco_distance_alert.py` | Camera frame + intrinsics | Distance (cm), parseable stdout, final JSON | ✅ YES |

### Legacy (Reference Only)

| Script (deprecated) | Superseded By |
|--------|--------|
| `map_anchors/scripts/detect_anchors.py` | `full_pipeline/main.py --mode detect` |
| `map_anchors/scripts/compute_extrinsics.py` | `full_pipeline/src/coordinate_transformer.py` |
| `caisses_detection/src/caisse_detector.py` | `full_pipeline/src/aruco_detector.py` (integrated) |

---

## 🚀 Hands-On Learning Path (Updated Nov 2025)

**Best way to learn: Read + Run + Modify!**

### Day 1: Basics & Quick Tests (1 hour)
1. Read ArUco basics in `ArUco_detection_folder/aruco_tools/` (20 min)
2. Run quick distance test (10 min):
   ```powershell
   cd ArUco_detection_folder\examples
   python aruco_distance_alert.py --camera 0 --threshold-cm 80
   ```
3. Try detection-only mode in full_pipeline (10 min):
   ```powershell
   cd full_pipeline
   python main.py --camera 0 --mode detect
   ```
4. Read `full_pipeline/QUICKSTART.md` (20 min)

### Day 2: Calibration & Intrinsics (1 hour)
1. Read `camera_calibration_folder/calibrate_camera.py` (20 min)
2. Examine preserved calibrations (10 min):
   - `camera_calibration_folder/calibration/iphone_xr_720p.json`
   - `full_pipeline/calibration_data/my_camera.json`
3. Run calibration test (15 min):
   ```powershell
   cd camera_calibration_folder
   python test_calibration.py
   ```
4. Understand intrinsics vs distortion (15 min)

### Day 3: Full Pipeline & Coordinate Transform (1.5 hours)
1. Read `full_pipeline/config.yaml` (15 min)
2. Read `full_pipeline/src/aruco_detector.py` (30 min)
3. Read `full_pipeline/src/coordinate_transformer.py` (30 min)
4. Run transform mode with your setup (15 min):
   ```powershell
   cd full_pipeline
   python main.py --camera 0 --mode transform --intrinsics calibration_data/my_camera.json
   ```

### Day 4: Integration & Documentation (1 hour)
1. Read `full_pipeline/IMPLEMENTATION.md` (20 min)
2. Read `full_pipeline/SUMMARY.md` (15 min)
3. Trace through complete data flow (25 min)
4. Run full-pipeline mode with visualization (optional)

### Day 5: Raspberry Pi Deployment (if needed)
1. Install OpenCV on Pi (see instructions below)
2. Copy `full_pipeline/` and calibrations to Pi
3. Calibrate Pi Camera or USB webcam on Pi
4. Test distance alert script for ROS integration

---

## 💡 Pro Tips (Updated Nov 2025)

1. **Start simple**: Always test with `main.py --mode detect` before trying world transforms
2. **Use the right calibration**: iPhone (Camo) uses `iphone_xr_720p.json`; USB webcam uses `my_camera.json`
3. **Check marker IDs**: Map anchors are 20-23 (DICT_4X4_50); caisse markers are 36, 47, 41
4. **Verify field dimensions**: Eurobot 2026 is 3.0m × 2.0m (not 2.0m × 3.0m!)
5. **Read config.yaml first**: Most parameters live in `full_pipeline/config.yaml`
6. **One step at a time**: Detection → Poses → Extrinsics → World coords (don't skip steps)
7. **Use distance script for quick tests**: `aruco_distance_alert.py` prints parseable stdout for ROS
8. **Legacy vs. active**: Work in `full_pipeline/`; ignore `map_anchors/`, `caisses_detection/` unless debugging old code
9. **PowerShell-friendly**: All examples use Windows paths with backslashes (e.g., `..\..\calibration\`)
10. **Marker size matters**: Distance accuracy depends linearly on marker_size (default 0.10 m = 10 cm)

---

## 📝 Next Steps

After reading everything:

1. **Document your understanding**: Write your own summary
2. **Identify your specific issue**: Use debug output from `compute_extrinsics.py`
3. **Plan the fix**: Based on error messages, decide on solution
4. **Test incrementally**: Fix one thing, test, repeat

---

## 📋 Recent Updates Summary (November 2025)

### Major Changes Since October:
1. **Repository Consolidation**
   - `full_pipeline/` is now the active codebase
   - Legacy folders (`map_anchors/`, `ArUco_detection_folder/`, `caisses_detection/`, `kalman_filter/`) deprecated but preserved for reference

2. **Eurobot 2026 Standardization**
   - Map anchors: IDs 20-23 (was 0-3 in legacy code)
   - Physical mapping verified: 22=Bottom-left, 23=Bottom-right, 21=Top-right, 20=Top-left
   - ArUco dictionary: DICT_4X4_50 (was DICT_6X6_250 in some old scripts)
   - Field dimensions: 3.0m × 2.0m
   - Anchor inset: 0.6m from edges
   - Marker size: 0.100 m (10 cm)

3. **Calibration Files Preserved**
   - iPhone XR (Camo) calibrations:
     - `camera_calibration_folder/calibration/iphone_xr_720p.json` (horizontal)
     - `camera_calibration_folder/calibration/iphone_xr_720p_vertical.json` (vertical)
   - Default USB webcam: `full_pipeline/calibration_data/my_camera.json`

4. **New Distance Testing Script**
   - `ArUco_detection_folder/examples/aruco_distance_alert.py`
   - Prints parseable distance lines to stdout (DISTANCE_CM <id> <cm>)
   - Final JSON on exit: `{"last_measured_cm": <value>}`
   - Exit codes: 0 (measurement captured), 2 (no measurement)
   - Ready for ROS integration or shell script parsing

5. **Branch Cleanup**
   - Phone branch deleted (calibrations merged to main)
   - All active development on `main` branch

### What to Do After 2-Week Break:
1. ✅ Read this updated guide (you're doing it!)
2. ✅ Physical marker mapping verified: ID 22=Bottom-left, 23=Bottom-right, 21=Top-right, 20=Top-left
3. ✅ Run `full_pipeline/main.py --mode detect` to verify setup
4. ✅ Check `map_anchors/config/marker_config.yaml` for current field/anchor positions
5. ✅ Test distance script if working on ROS integration
6. ✅ Ignore legacy folders unless debugging old experiments

---

*Happy learning! Remember: Understanding the code is more valuable than memorizing it.* 🎓

*Last Updated: November 12, 2025*
