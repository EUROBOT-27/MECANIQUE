# World Coordinate System Definition

## 🎯 Purpose

This document defines the **world coordinate system** used throughout the Eurobot 2026 vision pipeline. All object positions, robot coordinates, and navigation waypoints are expressed in this reference frame.

## 📐 Coordinate Frame Definition

### Origin and Axes

The world coordinate system is a **right-handed Cartesian coordinate system** defined by the 4 map anchor markers.

```
                Y-axis (long edge)
                    ↑
                    |
         [3]--------+--------[2]
          |         |         |
          |         |         |
          |         |         |
          |         |         |
          |    PLAYING FIELD  |
          |         |         |
          |         |         |
          |         |         |
         [0]--------+--------[1] → X-axis (short edge)
        Origin    (0,0,0)
         
         Z-axis: ⊙ (pointing out of the page, upward)
```

### Coordinate Definitions

- **Origin (0, 0, 0)**: Center of ArUco marker ID=0 (bottom-left corner)
- **X-axis**: Points from marker 0 to marker 1 (along table width - 3.0m)
- **Y-axis**: Points from marker 0 to marker 3 (along table length - 2.0m)
- **Z-axis**: Points perpendicular to the table surface (upward)
- **Handedness**: Right-handed (X × Y = Z)

### Units

- **Distance**: Meters (m)
- **Angles**: Radians (rad) or degrees (°) as specified
- **Time**: Seconds (s)

## 📏 Playing Field Dimensions

### Eurobot 2026 Standard Table

According to Eurobot 2026 rules:
- **Width (X-axis)**: 3.000 m
- **Length (Y-axis)**: 2.000 m
- **Border height**: ~0.022 m (22 mm wooden borders)

### Map Anchor Positions

The 4 ArUco markers are placed at the corners:

| Marker ID | Position (X, Y, Z) [meters] | Description |
|-----------|------------------------------|-------------|
| 0         | (0.000, 0.000, 0.000)        | Origin (bottom-left) |
| 1         | (3.000, 0.000, 0.000)        | Bottom-right |
| 2         | (3.000, 2.000, 0.000)        | Top-right |
| 3         | (0.000, 2.000, 0.000)        | Top-left |

**Note**: These are the coordinates of the marker **centers**. If markers are placed on the border edges, adjust accordingly.

### Marker Corner Coordinates

Each marker has 4 corners. For a marker of size `S` (e.g., 0.100 m for 10cm marker):

For **Marker ID=0** (at origin):
```
Corner 0: (0 - S/2, 0 - S/2, 0)  →  (-0.050, -0.050, 0)
Corner 1: (0 + S/2, 0 - S/2, 0)  →  ( 0.050, -0.050, 0)
Corner 2: (0 + S/2, 0 + S/2, 0)  →  ( 0.050,  0.050, 0)
Corner 3: (0 - S/2, 0 + S/2, 0)  →  (-0.050,  0.050, 0)
```

**Corner numbering**: ArUco convention (top-left, top-right, bottom-right, bottom-left when viewed from above).

## 🧭 Orientation Convention

### Rotation Representation

Orientations are represented as:
- **Rotation Matrix (R)**: 3×3 orthonormal matrix
- **Rotation Vector (rvec)**: 3×1 Rodrigues rotation vector (axis-angle)
- **Euler Angles**: (roll, pitch, yaw) in radians or degrees
- **Quaternion**: (w, x, y, z) for some applications

### Euler Angles Convention

- **Roll (φ)**: Rotation around X-axis
- **Pitch (θ)**: Rotation around Y-axis  
- **Yaw (ψ)**: Rotation around Z-axis
- **Order**: XYZ (intrinsic rotations)

### Yaw Angle (θ) for Robot Heading

For a robot on the table (planar motion):
```
    Y
    ↑
    |
    +--→ X

θ = 0°:   Robot facing +X direction (→)
θ = 90°:  Robot facing +Y direction (↑)
θ = 180°: Robot facing -X direction (←)
θ = -90° or 270°: Robot facing -Y direction (↓)
```

## 🔄 Coordinate Transformations

### Camera to World Transform

Given camera extrinsics `T_world_cam`, transform a point from camera frame to world frame:

```python
# Point in camera frame
P_cam = np.array([x_cam, y_cam, z_cam, 1])  # Homogeneous coordinates

# Transform to world frame
P_world = T_world_cam @ P_cam

# Extract 3D coordinates
x_world, y_world, z_world = P_world[:3]
```

### World to Camera Transform

```python
# Point in world frame
P_world = np.array([x_world, y_world, z_world, 1])

# Transform to camera frame
T_cam_world = np.linalg.inv(T_world_cam)
P_cam = T_cam_world @ P_world
```

### Marker to World Transform

Each detected marker has its own pose `(rvec_marker, tvec_marker)` in camera frame. To get marker position in world frame:

```python
# Build marker transform in camera frame
R_marker, _ = cv2.Rodrigues(rvec_marker)
T_cam_marker = np.eye(4)
T_cam_marker[:3, :3] = R_marker
T_cam_marker[:3, 3] = tvec_marker.flatten()

# Transform to world frame
T_world_marker = T_world_cam @ T_cam_marker

# Extract position and orientation
marker_position_world = T_world_marker[:3, 3]
marker_rotation_world = T_world_marker[:3, :3]
```

## 📊 Coordinate Validation

### Sanity Checks

When validating coordinates, ensure:

1. **Range checks**:
   - X ∈ [0, 2.0] meters (within table width)
   - Y ∈ [0, 3.0] meters (within table length)
   - Z ≈ 0 for objects on table (±0.1 m tolerance)

2. **Marker positions**:
   - Map anchors (ID 0-3) should be at known fixed positions
   - Deviation from expected position indicates calibration error

3. **Physics constraints**:
   - Objects cannot be outside playing field
   - Objects cannot have Z < -0.05 (below table)
   - Robot height should be reasonable (0.1 - 0.3 m typically)

### Visual Verification

Project coordinate system axes onto image for visualization:

```python
def draw_coordinate_axes(image, camera_matrix, dist_coeffs, rvec, tvec, length=0.5):
    """
    Draw world coordinate axes on image.
    
    Args:
        length: Length of axes in meters
    """
    # Define axis endpoints in world frame
    axes = np.float32([
        [0, 0, 0],           # Origin
        [length, 0, 0],      # X-axis (red)
        [0, length, 0],      # Y-axis (green)
        [0, 0, length]       # Z-axis (blue)
    ])
    
    # Project to image
    img_points, _ = cv2.projectPoints(
        axes, rvec, tvec, camera_matrix, dist_coeffs
    )
    img_points = img_points.reshape(-1, 2).astype(int)
    
    # Draw axes
    origin = tuple(img_points[0])
    cv2.line(image, origin, tuple(img_points[1]), (0, 0, 255), 3)    # X: red
    cv2.line(image, origin, tuple(img_points[2]), (0, 255, 0), 3)    # Y: green
    cv2.line(image, origin, tuple(img_points[3]), (255, 0, 0), 3)    # Z: blue
    
    return image
```

## 🗺️ Field Regions and Zones

### Playing Field Zones (Example)

Define named regions for strategic planning:

```yaml
zones:
  start_zone_blue:
    x_min: 0.0
    x_max: 0.4
    y_min: 0.0
    y_max: 0.5
    
  start_zone_yellow:
    x_min: 1.6
    x_max: 2.0
    y_min: 2.5
    y_max: 3.0
    
  center_zone:
    x_min: 0.8
    x_max: 1.2
    y_min: 1.3
    y_max: 1.7
```

### Obstacle and No-Go Zones

Define regions where the robot should not enter:

```yaml
obstacles:
  - type: "circular"
    center: [1.0, 1.5]
    radius: 0.2
    
  - type: "rectangular"
    x_min: 0.5
    x_max: 0.7
    y_min: 1.0
    y_max: 1.2
```

## 🔄 Reference Frame Transformations Summary

Key transformations in the system:

```
World Frame (W)
    ↕ T_world_cam
Camera Frame (C)
    ↕ T_cam_marker
Marker Frame (M)
    ↕ T_marker_object
Object Frame (O)
```

**Chain rule**: To transform from object frame to world frame:
```python
T_world_object = T_world_cam @ T_cam_marker @ T_marker_object
```

## 📁 Configuration File Format

Store world coordinate definitions in `config/marker_config.yaml`:

```yaml
# World coordinate system definition
coordinate_system:
  origin: "Marker ID 0 center"
  handedness: "right-handed"
  units: "meters"
  
# Map anchor positions
markers:
  0:
    center: [0.000, 0.000, 0.000]
    corners:
      - [-0.050, -0.050, 0.000]  # Top-left
      - [ 0.050, -0.050, 0.000]  # Top-right
      - [ 0.050,  0.050, 0.000]  # Bottom-right
      - [-0.050,  0.050, 0.000]  # Bottom-left
    size: 0.100  # 10cm marker
    
  1:
    center: [3.000, 0.000, 0.000]
    corners:
      - [2.950, -0.050, 0.000]
      - [3.050, -0.050, 0.000]
      - [3.050,  0.050, 0.000]
      - [2.950,  0.050, 0.000]
    size: 0.100
    
  2:
    center: [3.000, 2.000, 0.000]
    corners:
      - [2.950, 1.950, 0.000]
      - [3.050, 1.950, 0.000]
      - [3.050, 2.050, 0.000]
      - [2.950, 2.050, 0.000]
    size: 0.100
    
  3:
    center: [0.000, 2.000, 0.000]
    corners:
      - [-0.050, 1.950, 0.000]
      - [ 0.050, 1.950, 0.000]
      - [ 0.050, 2.050, 0.000]
      - [-0.050, 2.050, 0.000]
    corners:
      - [-0.050, 2.950, 0.000]
      - [ 0.050, 2.950, 0.000]
      - [ 0.050, 3.050, 0.000]
      - [-0.050, 3.050, 0.000]
    size: 0.100

# Playing field dimensions
field:
  width: 2.000   # X-axis
  length: 3.000  # Y-axis
  border_height: 0.022

# ArUco dictionary
aruco:
  dictionary: "DICT_6X6_250"
  marker_ids_map: [0, 1, 2, 3]
  marker_ids_boxes: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
  marker_ids_enemy: [30, 31, 32, 33, 34, 35]
```

## 📚 References

- Right-handed coordinate systems: https://en.wikipedia.org/wiki/Right-hand_rule
- Homogeneous transformations: https://en.wikipedia.org/wiki/Transformation_matrix
- Rodrigues rotation: https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
- Eurobot rules: [Official Cahier des Charges]

## ⚡ Quick Reference

**Origin**: Marker 0 center  
**X-axis**: Marker 0 → Marker 1 (table width, 2m)  
**Y-axis**: Marker 0 → Marker 3 (table length, 3m)  
**Z-axis**: Upward (perpendicular to table)  
**Units**: Meters for distance, radians for angles  
**Marker IDs**: 0-3 for map anchors
