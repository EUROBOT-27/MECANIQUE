# Camera Extrinsics Implementation Guide

**Complete guide for adding camera extrinsics computation with SPACE key trigger to strategy main.py**

Date: February 7, 2026  
System: Eurobot 2026 Computer Vision

---

## Overview

This document provides all necessary code components to implement automatic camera extrinsics computation using ArUco map anchors (IDs 20-23) with live SPACE-key-triggered recalibration.

**Key Features:**
- Automatic extrinsics computation when all 4 reference markers are visible
- SPACE key to reset and recompute extrinsics on-the-fly
- 16-point PnP algorithm for robust camera pose estimation (4 corners × 4 markers)
- Camera-to-world coordinate transformation for all detected objects
- JSON persistence for cross-session calibration reuse

---

## 1. Required Imports

```python
import cv2
import numpy as np
import json
import time
from pathlib import Path
```

---

## 2. Configuration Constants

```python
# ArUco Configuration
ARUCO_DICT = cv2.aruco.DICT_4X4_50

# Map Anchor Reference Markers (IDs 20-23) - Fixed World Coordinates
# These are the 4 corner markers that define the absolute coordinate system
REFERENCE_MARKERS = {
    20: np.array([2.400, 0.600, 0.0]),  # Bottom-right corner
    21: np.array([0.600, 0.600, 0.0]),  # Bottom-left corner
    22: np.array([2.400, 1.400, 0.0]),  # Top-right corner
    23: np.array([0.600, 1.400, 0.0])   # Top-left corner
}

# Marker Sizes (meters)
REFERENCE_MARKER_SIZE = 0.10  # 10cm for map anchors (IDs 20-23)
OBJECT_MARKER_SIZE = 0.05     # 5cm for robots/objects
CRATE_MARKER_SIZE = 0.03      # 3cm for crates (IDs 36, 47)

# Calibration File Paths (adjust relative to your main.py location)
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"
```

**Important Notes:**
- Map anchor coordinates are in meters on the 3.0m × 2.0m Eurobot field
- Reference markers use larger 10cm ArUco markers for better detection at distance
- Coordinate system: Right-handed, Z-up, origin at reference marker alignment

---

## 3. Class Initialization

Add these attributes to your `__init__` method:

```python
def __init__(self):
    # ArUco detector setup
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    aruco_params = cv2.aruco.DetectorParameters()
    self.detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Camera calibration data
    self.camera_matrix = None      # Intrinsic matrix (3x3)
    self.dist_coeffs = None         # Distortion coefficients (1x5 or 1x8)
    self.rvec_cam = None            # Camera rotation vector in world frame (3x1)
    self.tvec_cam = None            # Camera translation vector in world frame (3x1)
    
    # Extrinsics validity flag
    self.extrinsics_valid = False   # True when camera pose is computed
    
    # Load camera intrinsics (must exist before starting)
    self.load_intrinsics(DEFAULT_INTRINSICS)
```

**Prerequisites:**
- Camera intrinsics must be calibrated first using the camera calibration module
- Run `camera_calibration_folder/calibrate_camera.py` to generate `camera_calibration.json`
- Intrinsics only need to be computed once per camera/resolution setup

---

## 4. Required Methods

### 4.1 Load Camera Intrinsics

```python
def load_intrinsics(self, path: str):
    """
    Load camera intrinsic parameters from calibration JSON file.
    
    Intrinsics include:
    - camera_matrix: Focal length and principal point (3x3)
    - dist_coeffs: Radial and tangential distortion coefficients
    
    Args:
        path: Absolute or relative path to camera_calibration.json
    
    Returns:
        bool: True if loaded successfully, False otherwise
    """
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        self.camera_matrix = np.array(data['camera_matrix'])
        self.dist_coeffs = np.array(data['dist_coeffs'])
        print(f"✓ Loaded camera intrinsics from {path}")
        return True
    except Exception as e:
        print(f"✗ Failed to load intrinsics: {e}")
        return False
```

---

### 4.2 Compute Extrinsics from Reference Markers (PnP Algorithm)

```python
def compute_extrinsics_from_reference(self, corners, ids) -> bool:
    """
    Compute camera extrinsics using all 4 reference markers (IDs 20-23).
    Uses 16 point correspondences (4 corners × 4 markers) for robust PnP.
    
    Algorithm:
    1. Check that all 4 reference markers (20-23) are visible
    2. For each marker, compute 3D world positions of its 4 corners
    3. Match with detected 2D pixel positions (16 correspondences total)
    4. Solve PnP: Finds camera rotation (rvec) and translation (tvec) in world frame
    5. Save to extrinsics file for persistence
    
    Args:
        corners: Detected marker corners from cv2.aruco.detectMarkers
        ids: Detected marker IDs (flattened numpy array)
    
    Returns:
        bool: True if extrinsics successfully computed, False otherwise
    """
    # Build dictionary for quick lookup
    corners_dict = {ids[i]: corners[i] for i in range(len(ids))}
    
    # Check if all 4 reference markers are visible
    ref_ids = [20, 21, 22, 23]
    if not all(rid in ids for rid in ref_ids):
        missing = [rid for rid in ref_ids if rid not in ids]
        print(f"! Missing reference markers: {missing}")
        return False
    
    # Collect 3D-2D correspondences (4 corners per marker = 16 points total)
    object_points = []  # 3D world coordinates
    image_points = []   # 2D image pixel coordinates
    
    for marker_id in ref_ids:
        marker_corners = corners_dict[marker_id][0]  # Shape: (4, 2)
        world_pos = REFERENCE_MARKERS[marker_id]     # Center position in world frame
        
        # Compute 4 corner positions in world frame
        # ArUco markers: corners ordered clockwise from top-left
        half_size = REFERENCE_MARKER_SIZE / 2.0
        corners_3d = np.array([
            world_pos + [-half_size, +half_size, 0],  # Top-left
            world_pos + [+half_size, +half_size, 0],  # Top-right
            world_pos + [+half_size, -half_size, 0],  # Bottom-right
            world_pos + [-half_size, -half_size, 0]   # Bottom-left
        ], dtype=np.float32)
        
        object_points.extend(corners_3d)
        image_points.extend(marker_corners)
    
    object_points = np.array(object_points, dtype=np.float32)
    image_points = np.array(image_points, dtype=np.float32)
    
    # Solve PnP to get camera pose in world frame
    success, rvec, tvec = cv2.solvePnP(
        object_points,
        image_points,
        self.camera_matrix,
        self.dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )
    
    if not success:
        print("✗ PnP solver failed")
        return False
    
    # Store camera extrinsics
    self.rvec_cam = rvec
    self.tvec_cam = tvec
    self.extrinsics_valid = True
    
    # Save to file for persistence
    self.save_extrinsics(DEFAULT_EXTRINSICS)
    
    print("✓ Camera extrinsics computed from reference markers")
    return True
```

**Technical Details:**
- **PnP** = Perspective-n-Point algorithm, estimates 3D camera pose from 2D-3D correspondences
- **16 points** = More robust than using only marker centers (4 points)
- **SOLVEPNP_ITERATIVE** = Levenberg-Marquardt optimization, good balance of speed/accuracy
- **Output**: `rvec_cam` and `tvec_cam` represent camera pose in world coordinate system

---

### 4.3 Transform Camera Coordinates to World Coordinates

```python
def transform_to_world(self, rvec_obj, tvec_obj):
    """
    Transform object pose from camera frame to world frame.
    
    Mathematical formula:
        P_world = R_cam^T @ (P_camera - t_cam)
    
    Where:
    - R_cam: Camera rotation matrix (3x3) derived from rvec_cam
    - t_cam: Camera translation vector (3x1), i.e., tvec_cam
    - P_camera: Object position in camera frame (from ArUco detection)
    - P_world: Object position in world frame (returned)
    
    Args:
        rvec_obj: Object rotation vector in camera frame (3x1)
        tvec_obj: Object translation vector in camera frame (3x1)
    
    Returns:
        tuple: (world_pos, world_rvec)
            - world_pos: Object position in world frame (3,) array
            - world_rvec: Object orientation in world frame (3,) array
            - Returns (None, None) if extrinsics not valid
    """
    if not self.extrinsics_valid:
        return None, None
    
    # Convert camera rotation vector to matrix
    R_cam, _ = cv2.Rodrigues(self.rvec_cam)
    t_cam = self.tvec_cam.reshape(3, 1)
    
    # Transform object position to world frame
    t_obj = tvec_obj.reshape(3, 1)
    world_pos = R_cam.T @ (t_obj - t_cam)
    
    # Transform object orientation to world frame
    R_obj, _ = cv2.Rodrigues(rvec_obj)
    world_R = R_cam.T @ R_obj
    world_rvec, _ = cv2.Rodrigues(world_R)
    
    return world_pos.flatten(), world_rvec.flatten()
```

**Use Case:**
```python
# After detecting a marker in camera frame
rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(...)

# Transform to absolute world coordinates
world_pos, world_rvec = self.transform_to_world(rvec[0], tvec[0])

# Now world_pos contains (x, y, z) in meters on the game field
# Use for path planning, collision detection, strategy decisions
```

---

### 4.4 Save/Load Extrinsics

```python
def save_extrinsics(self, path: str):
    """
    Save computed camera extrinsics to JSON file.
    
    Saves:
    - rvec: Camera rotation vector (3,)
    - tvec: Camera translation vector (3,)
    - rotation_matrix: Camera rotation matrix (3x3) - for debugging
    - camera_position_world: Camera XYZ position in world frame - for debugging
    
    Args:
        path: Path to save camera_extrinsics.json
    """
    if self.rvec_cam is None or self.tvec_cam is None:
        print("! No extrinsics to save")
        return
    
    # Compute rotation matrix and camera position for easier interpretation
    R_cam, _ = cv2.Rodrigues(self.rvec_cam)
    cam_position = -R_cam.T @ self.tvec_cam.flatten()
    
    data = {
        'rvec': self.rvec_cam.flatten().tolist(),
        'tvec': self.tvec_cam.flatten().tolist(),
        'rotation_matrix': R_cam.tolist(),
        'camera_position_world': cam_position.tolist()
    }
    
    # Ensure directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Extrinsics saved to {path}")


def load_extrinsics(self, path: str) -> bool:
    """
    Load camera extrinsics from JSON file.
    
    Useful for:
    - Reusing calibration across sessions
    - Starting up faster (no need to see all 4 reference markers initially)
    - Still allows SPACE key recalibration if camera moves
    
    Args:
        path: Path to camera_extrinsics.json
    
    Returns:
        bool: True if loaded successfully, False otherwise
    """
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        self.rvec_cam = np.array(data['rvec'])
        self.tvec_cam = np.array(data['tvec'])
        self.extrinsics_valid = True
        print(f"✓ Loaded camera extrinsics from {path}")
        return True
    except FileNotFoundError:
        print(f"! No existing extrinsics file at {path}")
        return False
    except Exception as e:
        print(f"✗ Failed to load extrinsics: {e}")
        return False
```

---

## 5. Main Loop with SPACE Key Trigger

```python
def run(self):
    """
    Main tracking loop with live extrinsics recomputation.
    
    Workflow:
    1. Detect ArUco markers in each frame
    2. If all 4 reference markers visible and extrinsics invalid → compute extrinsics
    3. If extrinsics valid → transform all detected objects to world coordinates
    4. SPACE key → reset extrinsics_valid flag, forces recomputation
    5. ESC key → quit
    
    Real-time Controls:
    - SPACE: Reset and recompute camera extrinsics (useful if camera moves)
    - ESC: Exit program
    """
    cap = cv2.VideoCapture(0)  # Or your camera index/RTSP URL
    
    print("=" * 60)
    print("EUROBOT STRATEGY - CAMERA EXTRINSICS SYSTEM")
    print("=" * 60)
    print("\nControls:")
    print("  ESC - Quit")
    print("  SPACE - Reset and recompute camera extrinsics")
    print("\nWaiting for reference markers (20-23)...\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect ArUco markers
        corners, ids, rejected = self.detector.detectMarkers(frame)
        display = frame.copy()
        
        if ids is not None:
            ids = ids.flatten()
            
            # Estimate pose for each detected marker
            for i, marker_id in enumerate(ids):
                # Use correct marker size based on ID
                marker_size = (REFERENCE_MARKER_SIZE if marker_id in REFERENCE_MARKERS
                              else OBJECT_MARKER_SIZE)
                
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [corners[i]], marker_size, self.camera_matrix, self.dist_coeffs
                )
                
                # Transform to world coordinates if extrinsics valid
                if self.extrinsics_valid:
                    world_pos, world_rvec = self.transform_to_world(rvec[0], tvec[0])
                    if world_pos is not None:
                        # *** USE world_pos FOR STRATEGY DECISIONS ***
                        # Example: Store in detections dict, send to path planner, etc.
                        x, y, z = world_pos
                        # print(f"Marker {marker_id}: ({x:.3f}, {y:.3f}, {z:.3f})")
            
            # Auto-compute extrinsics if not yet valid and all reference markers visible
            ref_markers = [mid for mid in ids if mid in REFERENCE_MARKERS]
            if len(ref_markers) >= 4 and not self.extrinsics_valid:
                self.compute_extrinsics_from_reference(corners, ids)
            
            # Draw detected markers on display
            cv2.aruco.drawDetectedMarkers(display, corners, ids)
        
        # Display extrinsics status on screen
        status_text = "Extrinsics: VALID" if self.extrinsics_valid else "Extrinsics: INVALID"
        status_color = (0, 255, 0) if self.extrinsics_valid else (0, 0, 255)
        cv2.putText(display, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 2)
        
        cv2.imshow('Strategy - Extrinsics Tracker', display)
        
        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            # Reset extrinsics and force recomputation
            self.extrinsics_valid = False
            self.rvec_cam = None
            self.tvec_cam = None
            print("\n! Extrinsics reset - recalibrating...\n")
    
    cap.release()
    cv2.destroyAllWindows()
```

**Runtime Behavior:**
- **Automatic calibration**: System auto-computes extrinsics when it first sees all 4 reference markers
- **SPACE key**: Instantly invalidates current calibration, waits for next detection of all 4 markers to recalibrate
- **Persistence**: Extrinsics saved to JSON on every computation, loaded on startup if available

---

## 6. Complete Minimal Example

```python
import cv2
import numpy as np
import json
from pathlib import Path

# Configuration
ARUCO_DICT = cv2.aruco.DICT_4X4_50
REFERENCE_MARKERS = {
    20: np.array([2.400, 0.600, 0.0]),
    21: np.array([0.600, 0.600, 0.0]),
    22: np.array([2.400, 1.400, 0.0]),
    23: np.array([0.600, 1.400, 0.0])
}
REFERENCE_MARKER_SIZE = 0.10
OBJECT_MARKER_SIZE = 0.05
DEFAULT_INTRINSICS = "../../camera_calibration_folder/calibration/camera_calibration.json"
DEFAULT_EXTRINSICS = "../../camera_calibration_folder/calibration/camera_extrinsics.json"

class ExtrinsicsTracker:
    def __init__(self):
        aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rvec_cam = None
        self.tvec_cam = None
        self.extrinsics_valid = False
        self.load_intrinsics(DEFAULT_INTRINSICS)
    
    def load_intrinsics(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
        self.camera_matrix = np.array(data['camera_matrix'])
        self.dist_coeffs = np.array(data['dist_coeffs'])
        print(f"✓ Loaded intrinsics")
    
    def compute_extrinsics_from_reference(self, corners, ids) -> bool:
        corners_dict = {ids[i]: corners[i] for i in range(len(ids))}
        ref_ids = [20, 21, 22, 23]
        if not all(rid in ids for rid in ref_ids):
            return False
        
        object_points = []
        image_points = []
        for marker_id in ref_ids:
            marker_corners = corners_dict[marker_id][0]
            world_pos = REFERENCE_MARKERS[marker_id]
            half_size = REFERENCE_MARKER_SIZE / 2.0
            corners_3d = np.array([
                world_pos + [-half_size, +half_size, 0],
                world_pos + [+half_size, +half_size, 0],
                world_pos + [+half_size, -half_size, 0],
                world_pos + [-half_size, -half_size, 0]
            ], dtype=np.float32)
            object_points.extend(corners_3d)
            image_points.extend(marker_corners)
        
        object_points = np.array(object_points, dtype=np.float32)
        image_points = np.array(image_points, dtype=np.float32)
        
        success, rvec, tvec = cv2.solvePnP(
            object_points, image_points,
            self.camera_matrix, self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if success:
            self.rvec_cam = rvec
            self.tvec_cam = tvec
            self.extrinsics_valid = True
            print("✓ Extrinsics computed")
            return True
        return False
    
    def transform_to_world(self, rvec_obj, tvec_obj):
        if not self.extrinsics_valid:
            return None, None
        R_cam, _ = cv2.Rodrigues(self.rvec_cam)
        t_cam = self.tvec_cam.reshape(3, 1)
        t_obj = tvec_obj.reshape(3, 1)
        world_pos = R_cam.T @ (t_obj - t_cam)
        return world_pos.flatten(), None
    
    def run(self):
        cap = cv2.VideoCapture(0)
        print("Press SPACE to reset extrinsics, ESC to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            corners, ids, _ = self.detector.detectMarkers(frame)
            display = frame.copy()
            
            if ids is not None:
                ids = ids.flatten()
                for i, marker_id in enumerate(ids):
                    marker_size = REFERENCE_MARKER_SIZE if marker_id in REFERENCE_MARKERS else OBJECT_MARKER_SIZE
                    rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                        [corners[i]], marker_size, self.camera_matrix, self.dist_coeffs
                    )
                    if self.extrinsics_valid:
                        world_pos, _ = self.transform_to_world(rvec[0], tvec[0])
                
                ref_markers = [mid for mid in ids if mid in REFERENCE_MARKERS]
                if len(ref_markers) >= 4 and not self.extrinsics_valid:
                    self.compute_extrinsics_from_reference(corners, ids)
                
                cv2.aruco.drawDetectedMarkers(display, corners, ids)
            
            status = "VALID" if self.extrinsics_valid else "INVALID"
            cv2.putText(display, f"Extrinsics: {status}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                       (0, 255, 0) if self.extrinsics_valid else (0, 0, 255), 2)
            
            cv2.imshow('Extrinsics Tracker', display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == 32:
                self.extrinsics_valid = False
                print("! Extrinsics reset")
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = ExtrinsicsTracker()
    tracker.run()
```

---

## 7. Integration Checklist

- [ ] **Camera intrinsics calibrated**: Run `camera_calibration_folder/calibrate_camera.py`
- [ ] **Map anchor markers printed**: IDs 20-23, 10cm size, DICT_4X4_50 dictionary
- [ ] **Markers positioned**: Place at exact world coordinates defined in `REFERENCE_MARKERS`
- [ ] **Imports added**: cv2, numpy, json, pathlib
- [ ] **Constants defined**: REFERENCE_MARKERS dict, marker sizes, file paths
- [ ] **Attributes initialized**: detector, camera_matrix, rvec_cam, tvec_cam, extrinsics_valid
- [ ] **Methods implemented**: load_intrinsics, compute_extrinsics_from_reference, transform_to_world, save/load_extrinsics
- [ ] **Main loop updated**: SPACE key handler, auto-calibration logic, world coordinate transformation
- [ ] **Tested**: Verify all 4 markers detected, SPACE key resets extrinsics, world coordinates are correct

---

## 8. Troubleshooting

### Problem: "Missing reference markers: [20, 21, 22, 23]"
**Solution**: Ensure all 4 map anchor markers are visible in camera frame. Print markers using `ArUco_detection_folder/aruco_tools/marker_generator.py` with DICT_4X4_50 dictionary.

### Problem: "PnP solver failed"
**Solution**: Check that:
- Camera intrinsics are loaded correctly
- Marker corners are detected accurately (good lighting, no motion blur)
- REFERENCE_MARKERS coordinates match physical placement

### Problem: World coordinates are incorrect (e.g., negative X when should be positive)
**Solution**: 
- Verify marker ID-to-position mapping in REFERENCE_MARKERS
- Check marker placement matches defined world coordinates
- Ensure marker size constant matches physical marker size

### Problem: Extrinsics drift over time / SPACE key doesn't help
**Solution**:
- Camera may be moving physically - mount it rigidly
- Reference markers may be moving - secure them to fixed surface
- Lighting changes affect detection - use consistent lighting

### Problem: "Failed to load intrinsics"
**Solution**: Run camera calibration first:
```bash
cd camera_calibration_folder
python calibrate_camera.py --camera 0
```

---

## 9. Theory: How It Works

### 9.1 Camera Calibration Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: INTRINSICS (Done once per camera)                  │
├─────────────────────────────────────────────────────────────┤
│ Input:  Chessboard images from multiple angles             │
│ Output: Camera matrix (focal length, principal point)      │
│         Distortion coefficients (radial, tangential)        │
│ Tool:   camera_calibration_folder/calibrate_camera.py      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: EXTRINSICS (Recomputed when camera/markers move)   │
├─────────────────────────────────────────────────────────────┤
│ Input:  4 reference markers (IDs 20-23) in camera view     │
│         Known 3D world positions of marker corners          │
│ Output: Camera rotation (rvec) and translation (tvec)      │
│         in world coordinate system                          │
│ Tool:   cv2.solvePnP (Perspective-n-Point algorithm)       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: WORLD TRANSFORMATION (Every frame)                 │
├─────────────────────────────────────────────────────────────┤
│ Input:  Object pose in camera frame (from ArUco detection) │
│         Camera extrinsics (rvec_cam, tvec_cam)             │
│ Output: Object pose in world frame                         │
│ Formula: P_world = R_cam^T @ (P_camera - t_cam)           │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Why 16 Points Instead of 4?

**Using only marker centers (4 points):**
- Less robust to detection noise
- Single marker detection error has large impact
- Harder to constrain camera orientation

**Using all marker corners (16 points):**
- 4× more constraints for PnP solver
- Averaging effect reduces noise
- Better conditioning for rotation estimation
- More resistant to individual marker detection errors

### 9.3 Coordinate Systems

```
World Frame (Eurobot field):
    Y (North)
    ↑
    |
    └──→ X (East)
   /
  Z (Up)
  
Camera Frame:
    Z (Optical axis, forward)
    ↗
   /
  └──→ X (Right)
  |
  ↓
  Y (Down)

Transformation:
    P_world = R_cam^T @ (P_camera - t_cam)
    
Where:
- R_cam^T: Inverse rotation (world → camera becomes camera → world)
- t_cam: Camera position expressed in world frame
- P_camera: Object position in camera frame
```

---

## 10. References

**Related Documentation:**
- [Camera Calibration Guide](../../../camera_calibration_folder/USAGE_EXAMPLES.md)
- [ArUco Detection System](../../../ArUco_detection_folder/ARUCO_GUIDE.md)
- [Map Anchors Configuration](../../../map_anchors/README.md)
- [Full Pipeline Startup Guide](../../../full_pipeline/STARTUP_GUIDE.md)

**External Resources:**
- OpenCV PnP Tutorial: https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html
- ArUco Marker Detection: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html

---

**Last Updated**: February 7, 2026  
**Version**: 1.0  
**Author**: Eurobot 2026 Computer Vision Team
