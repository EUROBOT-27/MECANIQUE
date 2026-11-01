# Camera Calibration - Quick Usage Examples

## Complete Workflow Example

### Step 1: Print the Chessboard Pattern

```bash
# Generate the pattern (already done, but you can regenerate if needed)
python generate_chessboard.py

# This creates: calibration/chessboard_pattern.png
# Print it on A4 paper and glue to a flat surface
```

### Step 2: Live Camera Calibration (Recommended)

```bash
# Start live calibration with default camera
python calibrate_camera.py --camera 0

# Instructions:
# 1. Position the chessboard so green text appears
# 2. Press SPACE to capture (20 images needed)
# 3. Move the board to different positions/angles:
#    - Close and far
#    - Left, right, center
#    - Tilted at various angles
# 4. Press ESC when done (minimum 3 images required)
```

### Step 3: Verify Calibration Quality

```bash
# Check calibration quality and parameters
python test_calibration.py

# Expected output:
# - Reprojection error < 1.0 pixels (good)
# - Camera matrix (K) with focal lengths
# - Distortion coefficients (D)
```

## Alternative: Calibration from Images

If you prefer to collect images first, then calibrate:

```bash
# 1. Take 15-20 photos of the chessboard pattern
#    Save them to a directory (e.g., my_calibration_images/)

# 2. Run calibration on those images
python calibrate_camera.py --images "my_calibration_images/*.jpg"

# 3. Test the calibration
python test_calibration.py
```

## Advanced Usage

### Custom Number of Calibration Images

```bash
# Capture more images for better accuracy
python calibrate_camera.py --camera 0 --num-images 30
```

### Custom Output Location

```bash
# Save calibration to a specific file
python calibrate_camera.py --camera 0 --output my_calibration.json
```

### Test Undistortion on Your Images

```bash
# Test undistortion effect on a sample image
python test_calibration.py --test-image path/to/test_image.jpg
```

### Test ArUco Detection with Calibration

```bash
# Test ArUco marker detection with calibration
python test_calibration.py --test-aruco path/to/aruco_image.jpg --marker-size 0.05
```

## Using Calibration in Your Code

```python
import cv2
import numpy as np
import json

# Load calibration
with open('calibration/camera_calibration.json', 'r') as f:
    cal = json.load(f)

camera_matrix = np.array(cal['camera_matrix'])
dist_coeffs = np.array(cal['distortion_coefficients'])

# Capture image
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Undistort image
undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs)

# Detect ArUco markers
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

corners, ids, rejected = detector.detectMarkers(undistorted)

# Estimate pose for each marker
if ids is not None:
    marker_size = 0.05  # 5cm markers
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
        corners, marker_size, camera_matrix, dist_coeffs
    )
    
    for i in range(len(ids)):
        print(f"Marker {ids[i][0]}: pos={tvecs[i].ravel()}, rot={rvecs[i].ravel()}")
```

## Calibration Quality Guidelines

| Reprojection Error | Quality | Action |
|-------------------|---------|--------|
| < 0.5 pixels | Excellent | Ready to use |
| 0.5 - 1.0 pixels | Good | Ready to use |
| 1.0 - 2.0 pixels | Acceptable | Consider recalibrating |
| > 2.0 pixels | Poor | Recalibrate with more/better images |

## Troubleshooting

### Problem: "Corners not found"
**Solution:**
- Ensure the entire chessboard is visible
- Check focus (board should be sharp)
- Improve lighting (avoid shadows)
- Hold board steadier

### Problem: High reprojection error
**Solution:**
- Verify the chessboard is completely flat
- Ensure images are not blurry
- Use more images (20-30 instead of minimum)
- Cover more of the camera's field of view

### Problem: Camera not opening
**Solution:**
- Check camera ID (try 0, 1, 2)
- Ensure no other program is using the camera
- Check camera permissions

### Problem: Module import errors
**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

## Running Tests

```bash
# Run integration tests to verify everything works
python test_integration.py

# Expected: 6/6 tests passed
```

## Camera Position Changes - What You Need to Know

### Does Camera Position (x, y, z) Matter?

**Short Answer:** Yes and No - it depends on what changes.

#### What DOESN'T Change When You Move the Camera:
- ✅ **Intrinsic Parameters** (camera matrix K, distortion coefficients)
  - Focal lengths (fx, fy)
  - Principal point (cx, cy)
  - Lens distortion coefficients
  - **These are properties of the camera itself and remain constant**

#### What DOES Change When You Move the Camera:
- ⚠️ **Extrinsic Parameters** (camera pose in world frame)
  - Translation vector (tvec) - where the camera is
  - Rotation vector (rvec) - how the camera is oriented
  - Transformation matrices (T_cam_world, T_world_cam)

### When You Reposition the Camera

#### Scenario 1: Camera Moved to New Location (x, y, z changed)

```
Example: Camera moved from (0.5, 0.0, 1.0) to (1.0, 0.5, 0.8)
```

**What happens:**
- Intrinsic calibration remains valid ✅
- Extrinsic calibration needs to be recomputed 🔄
- ArUco marker detection still works normally
- Object positions in camera frame are still accurate
- Object positions in world frame will be WRONG until extrinsics are updated

**What you need to do:**
1. Keep the same intrinsic calibration file (camera_calibration.json)
2. Re-run extrinsic calibration with ArUco markers at known world positions
3. Update the extrinsic parameters (camera_extrinsics.json)
4. No other configuration changes needed

**Configuration changes required:**
```
❌ No need to change: camera_calibration.json
✅ Must recalibrate: camera_extrinsics.json (rvec, tvec)
❌ No need to change: marker sizes, ArUco dictionary
❌ No need to change: pipeline code or algorithms
```

#### Scenario 2: Camera Orientation Changed

```
Example: Camera tilted, panned, or rotated
```

**What happens:**
- Same as Scenario 1
- Only the rotation component (rvec) of extrinsics changes
- Translation (tvec) might stay the same if camera center didn't move

**What you need to do:**
- Same as Scenario 1: recalibrate extrinsics only

#### Scenario 3: Camera Replaced or Lens Changed

```
Example: Different camera model or different lens
```

**What happens:**
- Intrinsic parameters are now completely different ⚠️
- Extrinsic parameters also need recalibration

**What you need to do:**
1. ❌ Discard old camera_calibration.json
2. ✅ Run full intrinsic calibration with chessboard
3. ✅ Run full extrinsic calibration with ArUco markers

### The Beauty of Proper Calibration

Because your system correctly separates intrinsics and extrinsics:

```python
# Your pipeline does this automatically:
1. Load intrinsics (K, dist_coeffs) - constant for this camera
2. Detect markers and estimate pose - uses intrinsics
3. Compute/load extrinsics (T_world_cam) - specific to camera placement
4. Transform to world coordinates - uses both

# Result: Objects are always correctly localized in world frame
```

**This means:**
- ✅ You can move the camera anywhere
- ✅ System will compute new extrinsics automatically (if you have markers at known positions)
- ✅ World-frame coordinates remain accurate
- ✅ No code changes needed
- ✅ No algorithm changes needed

### Practical Workflow for Camera Repositioning

```bash
# Step 1: Camera moved to new position
# (Your intrinsic calibration is still valid)

# Step 2: Place ArUco markers at known world positions
# (Same as original setup - markers at corners of field, etc.)

# Step 3: Run extrinsic calibration
python calibrate_extrinsics.py  # or your equivalent script

# Step 4: Verify
python test_world_coordinates.py

# Done! System now works at new camera position
```

### Summary Table

| Change | Intrinsics Affected? | Extrinsics Affected? | Action Required |
|--------|---------------------|---------------------|-----------------|
| Camera moved (x, y, z) | ❌ No | ✅ Yes | Recalibrate extrinsics only |
| Camera rotated/tilted | ❌ No | ✅ Yes | Recalibrate extrinsics only |
| Zoom/focus adjusted | ⚠️ Maybe | ✅ Yes | Recalibrate both (if zoom changed) |
| Camera replaced | ✅ Yes | ✅ Yes | Recalibrate both |
| Lens replaced | ✅ Yes | ✅ Yes | Recalibrate both |
| Arena/markers moved | ❌ No | ⚠️ Depends | Update marker positions or extrinsics |

### Key Insight

Your algorithms for estimating position and computing real-world coordinates are **position-independent** because they:
1. Use intrinsics to undistort and measure angles correctly (camera-specific)
2. Use extrinsics to transform to world frame (position-specific)
3. Separate these concerns properly

So yes, you can put your camera anywhere - just recalibrate the extrinsics!

**Be careful**:
-if the map or marker positions change, you may need to update those as well.
-the marker positions in world coordinates must remain consistent.
-the marker configurations (sizes, dictionary) are found in the pipeline config yaml file.


## Next Steps After Calibration

Once calibration is complete:
1. Use the calibration parameters for ArUco marker detection
2. Implement extrinsic calibration (world coordinates)
3. Build the transform pipeline for enemy/object tracking
4. Integrate with the robot's vision system
