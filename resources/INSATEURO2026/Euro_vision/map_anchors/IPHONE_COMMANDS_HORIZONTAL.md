# iPhone XR Camera Commands Reference - HORIZONTAL MODE
**Camera Setup**: iPhone XR via Camo, Horizontal (720p), 1280×720, 30 FPS  
**Camera Index**: 2  
**Calibration File**: `camera_calibration_folder/calibration/iphone_xr_720p.json`  
**Calibration Quality**: 0.1987 px reprojection error (EXCELLENT)

⚠️ **IMPORTANT**: Keep your phone in **LANDSCAPE/HORIZONTAL** orientation to match this calibration!

---

## Prerequisites
Always run commands from the `map_anchors/scripts` directory:
```powershell
cd c:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Euro_vision\map_anchors\scripts
```

---

## 📍 1. Detect Anchors (Live Detection)
**Purpose**: Detect and visualize map anchor markers (IDs 20-23) in real-time

```powershell
python detect_anchors.py --camera 2 --config ../config/marker_config.yaml --visualize
```

**What it does**:
- Opens camera feed with live ArUco detection
- Shows detected marker IDs and positions
- Green boxes highlight map anchors (20-23)
- Press 'q' to quit

**Note**: This script doesn't need `--intrinsics` (uses marker_config.yaml only)

**Use when**: Testing marker visibility before extrinsics computation

---

## 🎯 2. Compute Extrinsics (Camera Position)
**Purpose**: Calculate camera's 3D position and orientation relative to the field

```powershell
python compute_extrinsics.py --camera 2 --config ../config/marker_config.yaml --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --visualize
```

**What it does**:
- Requires all 4 map anchors (20-23) visible
- Averages 30 frames for stable results
- Shows live detection during computation
- Saves extrinsics to `calibration/` folder
- Press 'q' to stop early

**Options**:
- `--average 50`: Increase frames for better accuracy (default: 30)
- `--output path/`: Custom output directory
- `--visualize`: Show camera feed (recommended)

**Use when**: Setting up camera or after moving camera position

---

## ✅ 3. Validate Pose (Test Extrinsics)
**Purpose**: Verify computed extrinsics are correct

```powershell
python validate_pose.py --camera 2 --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --extrinsics calibration/ --config ../config/marker_config.yaml
```

**What it does**:
- Loads saved extrinsics
- Projects known world points onto image
- Shows reprojection error
- Displays camera position in world coordinates

**Use when**: After computing extrinsics to verify accuracy

---

## 📊 4. Visualize Anchors (Debug View)
**Purpose**: Advanced visualization with coordinate axes and 3D information

```powershell
python visualize_anchors.py --camera 2 --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --config ../config/marker_config.yaml
```

**What it does**:
- Shows detected markers with IDs
- Draws 3D coordinate axes on markers
- Displays distance estimates
- Real-time pose estimation per marker

**Use when**: Debugging marker detection or checking marker orientations

---

## 🔧 5. Generate Markers (Create New Markers)
**Purpose**: Generate ArUco marker images for printing

```powershell
# Generate single marker
python generate_markers.py --ids 20 --output ../../markers/

# Generate all map anchors
python generate_markers.py --ids 20 21 22 23 --output ../../markers/

# Generate with custom size (300 DPI for high quality)
python generate_markers.py --ids 20 21 22 23 --size 400 --dpi 300 --output ../../markers/
```

**What it does**:
- Creates PNG images of ArUco markers
- Default: 200×200 pixels, 150 DPI
- Adds border and ID label below marker

**Use when**: Need to print new markers or replace damaged ones

---

## 📋 Complete Workflow

### Initial Setup (One-time)
1. **Set Camo to Horizontal mode**:
   - Open Camo on iPhone
   - Select: **Horizontal (720p)**
   - Verify: 1280×720 resolution
   - Frame rate: 30 FPS

2. **Generate markers** (if needed):
   ```powershell
   python generate_markers.py --ids 20 21 22 23 --size 400 --dpi 300 --output ../../markers/
   ```

3. **Test detection**:
   ```powershell
   python detect_anchors.py --camera 2 --config ../config/marker_config.yaml --visualize
   ```
   - Verify all 4 markers (20-23) are detected
   - Adjust lighting, focus, marker placement
   - Keep phone in **horizontal orientation**

4. **Compute extrinsics**:
   ```powershell
   python compute_extrinsics.py --camera 2 --config ../config/marker_config.yaml --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --visualize --average 50
   ```
   - Keep camera steady
   - Ensure all 4 markers visible
   - Wait for 50 frames (~2 seconds)

5. **Validate results**:
   ```powershell
   python validate_pose.py --camera 2 --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --extrinsics calibration/ --config ../config/marker_config.yaml
   ```
   - Check reprojection error < 5 pixels
   - Verify camera position makes sense

### Daily Usage
- **Quick detection check**:
  ```powershell
  python detect_anchors.py --camera 2 --config ../config/marker_config.yaml --visualize
  ```

- **Recompute if camera moved**:
  ```powershell
  python compute_extrinsics.py --camera 2 --config ../config/marker_config.yaml --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --visualize
  ```

---

## 🚨 Troubleshooting

### No markers detected
```powershell
# Quick check (simple detection)
python detect_anchors.py --camera 2 --config ../config/marker_config.yaml --visualize

# Advanced check (with pose estimation)
python visualize_anchors.py --camera 2 --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --config ../config/marker_config.yaml
```
- Ensure markers are printed clearly (300 DPI recommended)
- Check lighting (avoid glare/shadows)
- Verify camera focus (tap screen in Camo)
- **Confirm phone is held horizontally (landscape)**

### Wrong resolution in Camo
- **MUST USE**: Horizontal (720p) = 1280×720 ✅
- **DON'T USE**: Vertical (720p) = 720×1280 ❌ (wrong calibration!)
- **DON'T USE**: 1080p or 4K (doesn't match calibration)

### Extrinsics computation fails
```powershell
# Test with more frames and visualization
python compute_extrinsics.py --camera 2 --config ../config/marker_config.yaml --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --visualize --average 100
```
- All 4 markers must be visible simultaneously
- Keep camera perfectly still during capture
- Check that marker_config.yaml has correct marker positions
- **Ensure phone is in horizontal orientation**

### Camera won't open
```powershell
# List available cameras
python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
```
- Verify Camo is running
- Check camera index (usually 2 for Camo)
- Restart Camo if needed

### Wrong distances/angles (calibration mismatch)
If you accidentally rotated the phone:
- **Solution**: Set Camo back to Horizontal (720p)
- **Or**: Use vertical calibration: `iphone_xr_720p_vertical.json`
- Physical phone orientation MUST match calibration!

---

## 📝 Quick Reference Card

| Script | Command | Purpose |
|--------|---------|---------|
| `detect_anchors.py` | `python detect_anchors.py --camera 2 --config ../config/marker_config.yaml --visualize` | Simple detection test |
| `compute_extrinsics.py` | `python compute_extrinsics.py --camera 2 --config ../config/marker_config.yaml --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --visualize` | Calculate camera pose |
| `validate_pose.py` | `python validate_pose.py --camera 2 --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --extrinsics calibration/ --config ../config/marker_config.yaml` | Verify extrinsics |
| `visualize_anchors.py` | `python visualize_anchors.py --camera 2 --intrinsics ../../camera_calibration_folder/calibration/iphone_xr_720p.json --config ../config/marker_config.yaml` | Advanced debug view |
| `generate_markers.py` | `python generate_markers.py --ids 20 21 22 23 --size 400 --dpi 300 --output ../../markers/` | Create markers |

---

## 💡 Pro Tips

1. **Always use `--visualize`** with compute_extrinsics.py to see what's happening
2. **Increase `--average`** to 50-100 frames for more stable extrinsics
3. **Check resolution** matches calibration (1280×720) - scripts will warn you if wrong
4. **Keep phone horizontal** - rotating phone invalidates calibration!
5. **Keep markers flat** - wrinkled or bent markers reduce accuracy
6. **Good lighting** - even, diffuse light works best (avoid direct sunlight)
7. **Camera stability** - mount phone on tripod for best results
8. **Marker size** - 10cm markers work well from 1-3 meters distance

---

## 📐 Camera Parameters (Reference)

Your calibration details:
```
Resolution: 1280×720 (horizontal/landscape)
Focal lengths: fx=1637.00, fy=1612.92 pixels
Principal point: cx=555.42, cy=367.74 pixels
Reprojection error: 0.1987 pixels (EXCELLENT)
Calibration date: October 13, 2025
```

---

## 🔗 Related Files
- **Calibration**: `camera_calibration_folder/calibration/iphone_xr_720p.json`
- **Marker Config**: `map_anchors/config/marker_config.yaml`
- **Camera Config**: `map_anchors/config/camera_config.yaml`
- **Extrinsics Output**: `map_anchors/scripts/calibration/`

---

## ⚠️ CRITICAL REMINDER

**Phone Orientation = Calibration Orientation**

This calibration is for **HORIZONTAL (landscape)** mode:
- ✅ Phone held horizontally (wider than tall)
- ✅ Camo set to Horizontal (720p)
- ✅ 1280 pixels wide × 720 pixels tall

If you rotate the phone vertically:
- ❌ All measurements will be wrong
- ❌ Need to use vertical calibration instead
- ❌ Or recalibrate in horizontal mode

**When in doubt, check the camera feed dimensions!**

---

*Last Updated: October 14, 2025*  
*Camera: iPhone XR via Camo (Horizontal 720p, 1280×720)*  
*Calibration: 0.1987 px reprojection error (EXCELLENT)*  
*📱 Keep phone horizontal at all times! 📱*
