# Camera Extrinsics Computation

## 🎯 Objective

Compute the camera's **extrinsic parameters** (position and orientation) relative to the world coordinate system defined by the 4 map anchor markers.

## 📖 Background

### What are Extrinsics?

Camera extrinsics define the camera's pose in the world coordinate system:
- **Translation vector (tvec)**: Camera position (x, y, z) in world coordinates
- **Rotation vector (rvec)**: Camera orientation as Rodriguez rotation vector
- **Transformation matrix (T_world_cam)**: 4×4 homogeneous transformation from camera to world frame

### Why Do We Need This?

Once we know the camera's extrinsics:
1. We can transform detected objects from camera frame to world frame
2. All detected positions become consistent with the map coordinate system
3. Multiple cameras can be registered to the same world frame

## 🔧 Prerequisites

Before computing extrinsics, ensure:
- ✅ Camera intrinsics are calibrated (focal length, principal point, distortion)
- ✅ 4 map anchors are placed and their world coordinates are known
- ✅ Camera is mounted and will not move

## 📐 Mathematical Approach

### Step 1: Detect All 4 Markers

For each marker, we get:
- `corners`: 4 corner positions in image (pixel coordinates)
- `id`: Marker ID (0, 1, 2, or 3)

### Step 2: Prepare 3D-2D Correspondences

For each detected marker corner, we have:
- **3D point**: Known world coordinate of marker corner (from config)
- **2D point**: Detected corner position in image

This gives us 16 correspondences (4 markers × 4 corners each).

### Step 3: Solve PnP (Perspective-n-Point)

Use OpenCV's `solvePnP` or `solvePnPRansac`:

```python
success, rvec, tvec = cv2.solvePnP(
    objectPoints=world_points_3d,    # Known 3D coordinates
    imagePoints=image_points_2d,     # Detected 2D coordinates
    cameraMatrix=camera_matrix,      # From intrinsic calibration
    distCoeffs=dist_coeffs,          # From intrinsic calibration
    flags=cv2.SOLVEPNP_ITERATIVE     # Or SOLVEPNP_SQPNP
)
```

Result:
- `rvec`: Rotation from world to camera frame
- `tvec`: Translation from world to camera frame

### Step 4: Build Transformation Matrix

Convert rvec and tvec to 4×4 transformation matrix:

```python
R, _ = cv2.Rodrigues(rvec)
T_cam_world = np.eye(4)
T_cam_world[:3, :3] = R
T_cam_world[:3, 3] = tvec.flatten()

# Invert to get world to camera transform
T_world_cam = np.linalg.inv(T_cam_world)
```

## 🔬 Implementation

### Basic Algorithm

```python
import cv2
import numpy as np
import yaml

def compute_camera_extrinsics(image, camera_matrix, dist_coeffs, marker_config):
    """
    Compute camera extrinsics from detected map anchors.
    
    Args:
        image: Input image from camera
        camera_matrix: 3x3 intrinsic camera matrix
        dist_coeffs: Distortion coefficients
        marker_config: Dict with marker IDs and world positions
    
    Returns:
        success: True if extrinsics computed successfully
        rvec: Rotation vector (world to camera)
        tvec: Translation vector (world to camera)
        T_world_cam: 4x4 transformation matrix
    """
    
    # Load ArUco dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    
    # Detect markers
    corners, ids, _ = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)
    
    if ids is None or len(ids) < 4:
        return False, None, None, None
    
    # Collect 3D-2D correspondences
    object_points = []
    image_points = []
    
    for i, marker_id in enumerate(ids.flatten()):
        if marker_id not in [0, 1, 2, 3]:
            continue
        
        # Get marker's world coordinates from config
        marker_world_corners = marker_config['markers'][marker_id]['corners']
        
        # Add all 4 corners
        for j in range(4):
            object_points.append(marker_world_corners[j])
            image_points.append(corners[i][0][j])
    
    if len(object_points) < 16:  # Need all 4 markers
        return False, None, None, None
    
    # Solve PnP
    object_points = np.array(object_points, dtype=np.float32)
    image_points = np.array(image_points, dtype=np.float32)
    
    success, rvec, tvec = cv2.solvePnPRansac(
        object_points,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )
    
    if not success:
        return False, None, None, None
    
    # Build transformation matrix
    R, _ = cv2.Rodrigues(rvec)
    T_cam_world = np.eye(4)
    T_cam_world[:3, :3] = R
    T_cam_world[:3, 3] = tvec.flatten()
    
    # Invert to get world to camera
    T_world_cam = np.linalg.inv(T_cam_world)
    
    return True, rvec, tvec, T_world_cam
```

### Usage Example

```python
# Load camera intrinsics
camera_matrix = np.load('calibration/camera_matrix.npy')
dist_coeffs = np.load('calibration/dist_coeffs.npy')

# Load marker configuration
with open('config/marker_config.yaml', 'r') as f:
    marker_config = yaml.safe_load(f)

# Capture image
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Compute extrinsics
success, rvec, tvec, T_world_cam = compute_camera_extrinsics(
    frame, camera_matrix, dist_coeffs, marker_config
)

if success:
    print("Camera extrinsics computed successfully!")
    print(f"Translation: {tvec.flatten()}")
    print(f"Rotation: {rvec.flatten()}")
    
    # Save for runtime use
    np.save('calibration/camera_extrinsics_rvec.npy', rvec)
    np.save('calibration/camera_extrinsics_tvec.npy', tvec)
    np.save('calibration/T_world_cam.npy', T_world_cam)
else:
    print("Failed to compute extrinsics. Ensure all 4 markers are visible.")
```

## 📊 Quality Metrics

### Reprojection Error

Measure how well the computed extrinsics explain the observations:

```python
def compute_reprojection_error(object_points, image_points, rvec, tvec, camera_matrix, dist_coeffs):
    """Compute mean reprojection error in pixels."""
    projected_points, _ = cv2.projectPoints(
        object_points, rvec, tvec, camera_matrix, dist_coeffs
    )
    projected_points = projected_points.reshape(-1, 2)
    error = np.linalg.norm(image_points - projected_points, axis=1)
    return np.mean(error), np.std(error)

mean_error, std_error = compute_reprojection_error(
    object_points, image_points, rvec, tvec, camera_matrix, dist_coeffs
)

print(f"Reprojection error: {mean_error:.2f} ± {std_error:.2f} pixels")
```

**Acceptance criteria**: Mean error < 2 pixels, std < 1 pixel

## 🔄 Continuous Calibration

For a fixed camera, compute extrinsics once and save. However, you can:

1. **Re-compute periodically** to detect camera movement
2. **Average multiple frames** to reduce noise
3. **Use outlier rejection** (RANSAC) for robustness

### Multi-Frame Averaging

```python
def compute_extrinsics_averaged(video_source, n_frames=30):
    """Compute extrinsics by averaging over multiple frames."""
    rvecs = []
    tvecs = []
    
    cap = cv2.VideoCapture(video_source)
    
    for _ in range(n_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        success, rvec, tvec, _ = compute_camera_extrinsics(
            frame, camera_matrix, dist_coeffs, marker_config
        )
        
        if success:
            rvecs.append(rvec)
            tvecs.append(tvec)
    
    cap.release()
    
    # Average rotation and translation
    rvec_mean = np.mean(rvecs, axis=0)
    tvec_mean = np.mean(tvecs, axis=0)
    
    return rvec_mean, tvec_mean
```

## 📁 Output Files

After computing extrinsics, save:

```
calibration/
├── camera_extrinsics_rvec.npy    # Rotation vector
├── camera_extrinsics_tvec.npy    # Translation vector
├── T_world_cam.npy                # 4x4 transformation matrix
└── extrinsics_metadata.yaml      # Calibration info (date, reprojection error, etc.)
```

## ⚠️ Troubleshooting

**Problem**: PnP fails or returns incorrect results
- Ensure all 4 markers are visible and properly detected
- Verify marker world coordinates in config are correct
- Check camera intrinsics are valid

**Problem**: High reprojection error
- Re-calibrate camera intrinsics
- Verify physical marker placement matches config
- Check for lens distortion correction

**Problem**: Extrinsics change between frames
- Camera may have moved (check mounting)
- Use multi-frame averaging
- Consider robust estimation (RANSAC)

## 🔗 Next Steps

After computing extrinsics:
1. Proceed to **validation** (see `validation.md`)
2. Use extrinsics in main vision pipeline
3. Transform all detected objects to world coordinates

## 📚 References

- OpenCV solvePnP: https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html
- Rotation Representations: https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
- Camera Pose Estimation: https://docs.opencv.org/4.x/d7/d53/tutorial_py_pose.html
