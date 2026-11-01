# Camera Configuration Files

This folder contains camera configuration files for the Map Anchors module.

## 📁 Files

### `camera_config.yaml` ✅ **UPDATED**
**Primary configuration file** used by most scripts.
- **Format**: YAML (human-readable, supports comments)
- **Status**: ✅ Populated with intrinsics from camera calibration
- **Use**: Default config file for all map_anchors scripts

### `camera_config.json` ✅ **UPDATED**
**Alternative JSON format** for scripts that prefer JSON.
- **Format**: JSON (machine-readable, standard format)
- **Status**: ✅ Synced with YAML file
- **Use**: Optional, for scripts preferring JSON over YAML

### `marker_config.yaml`
**Map anchor marker definitions** (world coordinates, sizes, IDs).
- Contains positions of the 4 corner markers
- Defines world coordinate system origin

## 📊 Configuration Status

### ✅ Intrinsics (Calibrated)
Camera intrinsics have been populated from `camera_calibration_folder/calibration/camera_calibration.json`:

- **Focal Length**: fx=662.18, fy=658.50 pixels
- **Principal Point**: cx=315.63, cy=239.77 pixels
- **Image Size**: 640×480 pixels
- **Distortion**: 5 coefficients (k1, k2, p1, p2, k3)
- **Calibration Date**: 2025-10-01
- **Reprojection Error**: 0.096 pixels ✅ **EXCELLENT** (< 0.1 px)

### ⏸️ Extrinsics (Not Computed)
Camera pose relative to world frame - **needs to be computed**:

**To compute extrinsics:**
1. Place 4 map anchor markers at table corners
2. Run: `python map_anchors/scripts/compute_extrinsics.py --camera 0`
3. Extrinsics will be saved to config files

### ⏸️ Validation (Pending)
Camera pose validation - **needs to be performed**:

**To validate:**
```bash
python map_anchors/scripts/validate_pose.py --camera 0 --duration 30
```

## 🔄 Syncing Configuration

### Automatic Sync Script

Use the `sync_camera_config.py` utility to update both YAML and JSON files:

```bash
# Update both config files from calibration JSON
python map_anchors/scripts/sync_camera_config.py

# Show current configuration status
python map_anchors/scripts/sync_camera_config.py --show
```

### Manual Sync

If you update camera calibration, run:
```bash
cd map_anchors/scripts
python sync_camera_config.py
```

This will:
- ✅ Read `camera_calibration_folder/calibration/camera_calibration.json`
- ✅ Update `camera_config.yaml` with intrinsics
- ✅ Update `camera_config.json` with intrinsics
- ✅ Preserve existing extrinsics and validation data

## 📖 Using Configuration Files

### In Python Scripts

**Load YAML config:**
```python
import yaml

with open('map_anchors/config/camera_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

fx = config['intrinsics']['camera_matrix']['fx']
fy = config['intrinsics']['camera_matrix']['fy']
```

**Load JSON config:**
```python
import json

with open('map_anchors/config/camera_config.json', 'r') as f:
    config = json.load(f)

camera_matrix = config['intrinsics']['camera_matrix_3x3']
dist_coeffs = config['intrinsics']['distortion_coefficients_array']
```

**Load as NumPy arrays (for OpenCV):**
```python
import numpy as np
import yaml

with open('map_anchors/config/camera_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Build camera matrix
camera_matrix = np.array([
    [config['intrinsics']['camera_matrix']['fx'], 0, config['intrinsics']['camera_matrix']['cx']],
    [0, config['intrinsics']['camera_matrix']['fy'], config['intrinsics']['camera_matrix']['cy']],
    [0, 0, 1]
], dtype=np.float32)

# Build distortion coefficients
dist_coeffs = np.array([
    config['intrinsics']['distortion_coefficients']['k1'],
    config['intrinsics']['distortion_coefficients']['k2'],
    config['intrinsics']['distortion_coefficients']['p1'],
    config['intrinsics']['distortion_coefficients']['p2'],
    config['intrinsics']['distortion_coefficients']['k3']
], dtype=np.float32)
```

## 🔧 Configuration Fields

### Camera Info
- `name`: Camera identifier
- `model`: Camera model/type
- `mount_height`: Physical height above table (measured during setup)

### Intrinsics (from calibration)
- `camera_matrix`: Focal lengths (fx, fy) and principal point (cx, cy)
- `distortion_coefficients`: k1, k2, k3 (radial), p1, p2 (tangential)
- `image_size`: Image dimensions in pixels
- `calibration_date`: When calibration was performed
- `reprojection_error`: Calibration quality metric

### Extrinsics (from map anchors)
- `rvec`: Rotation vector (world to camera transform)
- `tvec`: Translation vector (camera position)
- `camera_position_world`: Computed camera position (x, y, z)
- `camera_orientation_world`: Euler angles (roll, pitch, yaw)

### Validation (from validation tests)
- `validated`: Overall validation status
- `stability`: Pose stability test results
- `reprojection`: Reprojection error test results
- `detection`: Marker detection consistency results

## ⚠️ Important Notes

1. **Don't edit intrinsics manually** - always update from calibration
2. **Use sync script** to keep YAML and JSON in sync
3. **Preserve extrinsics** - they take time to compute correctly
4. **Re-validate after changes** - run validation if you move the camera

## 📚 Next Steps

1. ✅ Intrinsics calibrated
2. ⏸️ **TODO**: Compute extrinsics (place markers, run compute_extrinsics.py)
3. ⏸️ **TODO**: Validate pose (run validate_pose.py)
4. ⏸️ **TODO**: Use in production pipeline

## 🔗 Related Documentation

- **Camera Calibration**: `camera_calibration_folder/README.md`
- **Map Anchors Setup**: `map_anchors/README.md`
- **Extrinsics Computation**: `map_anchors/docs/extrinsics.md`
- **Validation Guide**: `map_anchors/docs/validation.md`
- **Quick Summary**: `map_anchors/docs/SUMMARY.md`
