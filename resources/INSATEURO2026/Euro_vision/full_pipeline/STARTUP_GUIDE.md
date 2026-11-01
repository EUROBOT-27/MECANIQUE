# Daily Startup Guide - Eurobot Tracking System

## Quick Start (Camera Position Changed)

When you mount the camera again (even slightly different position), follow this workflow:

### Option 1: Automatic Recalibration (Recommended)

```bash
cd full_pipeline/scripts
python main.py --camera 1
```

**What happens:**
1. System loads saved **intrinsics** (camera internal parameters - these stay the same)
2. System tries to load saved **extrinsics** (camera position - this is outdated)
3. When it detects all 4 reference markers (20-23), it **automatically recomputes extrinsics**
4. New extrinsics are saved to `camera_extrinsics.json`
5. Tracking begins immediately

**Steps:**
1. Launch the script
2. Point camera at table so all 4 reference markers are visible
3. Wait 1-2 seconds - status changes from "CALIBRATING" → "TRACKING"
4. Done! System is tracking in world coordinates

---

### Option 2: Manual Reset (If Auto-Recompute Doesn't Work)

If the system loads old extrinsics and tracking looks wrong:

**Runtime Controls:**
- Press **SPACE** during runtime to reset extrinsics
- System goes back to "CALIBRATING" mode
- Point at all 4 reference markers
- Extrinsics recompute automatically

---

## What You DON'T Need to Redo

### ✅ Camera Intrinsics (Keep Using)

**Location:** `camera_calibration_folder/calibration/camera_calibration.json`

**These stay valid because:**
- Intrinsics are properties of the camera lens itself (focal length, distortion)
- They don't change unless you change the camera or zoom level
- Your iPhone XR intrinsics are already perfect (0.16px error)

**Only recalibrate intrinsics if:**
- You switch to a different camera
- You change resolution (e.g., 1280×720 → 1920×1080)
- You're getting obviously distorted tracking (very rare)

---

## What You DO Need to Redo

### 🔄 Camera Extrinsics (Recompute Every Time)

**Location:** `camera_calibration_folder/calibration/camera_extrinsics.json`

**These change because:**
- Extrinsics = camera position and orientation in world space
- Even slight camera movement changes these values
- If you use old extrinsics with new camera position, coordinates will be wrong

**Automatic recomputation:**
- Full pipeline does this automatically when it sees 4 reference markers
- Takes ~0.5 seconds
- No user intervention needed

---

## Daily Workflow

### Morning Setup

```bash
# 1. Mount camera above table
# 2. Ensure all 4 reference markers (20-23) are visible and in correct positions
# 3. Run the pipeline
cd full_pipeline/scripts
python main.py --camera 1
```

### Expected Output

```
✓ Loaded intrinsics from ../../camera_calibration_folder/calibration/camera_calibration.json
  fx=970.58, fy=959.96
  cx=618.43, cy=302.32
! Could not load extrinsics: [error message]  ← This is OK!
✓ Camera opened (ID: 1)
✓ Kalman filter: ENABLED

Controls:
  ESC - Quit
  SPACE - Reset extrinsics
  'k' - Toggle Kalman filter

Waiting for reference markers (20-23)...

✓ Camera extrinsics computed!
  Camera position: (1.343, 2.084, 1.645)m
  Saved to: ../../camera_calibration_folder/calibration/camera_extrinsics.json
```

### Verify Tracking

Once status shows "TRACKING":
1. Place enemy marker (ID 13) at a known position
2. Check displayed coordinates match expected position
3. If coordinates are off by more than ~10cm, press SPACE to recalibrate

---

## Troubleshooting

### "CALIBRATING" Never Changes to "TRACKING"

**Problem:** Not all 4 reference markers detected

**Solutions:**
- Ensure markers 20, 21, 22, 23 are all visible
- Improve lighting (no glare on markers)
- Move camera back to see all 4 markers
- Check markers are printed at correct size (10cm)

### Coordinates Look Wrong (Off by Meters)

**Problem:** Old extrinsics loaded, camera is in different position

**Solution:**
- Press **SPACE** during runtime
- Point at all 4 reference markers
- Wait for automatic recalibration

### Coordinates Jittering/Noisy

**Problem:** Normal sensor noise

**Solutions:**
- Kalman filter handles this for enemy (ID 13) automatically
- 5-frame smoothing applied to other markers
- Increase smoothing in config if needed

### Camera Index Wrong

**Problem:** `Cannot open camera 1`

**Solution:**
```bash
# Find correct camera index
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

# Use correct index
python main.py --camera 0  # or 2, 3, etc.
```

---

## File Reference

### Files That Stay the Same (Commit to Git)

```
camera_calibration_folder/calibration/
├── camera_calibration.json       ✅ Keep (intrinsics)
├── chessboard_pattern.png        ✅ Keep (calibration pattern)
```

### Files That Change Daily (Don't Commit / Use .gitignore)

```
camera_calibration_folder/calibration/
├── camera_extrinsics.json        🔄 Recomputed daily
```

### Add to .gitignore

```
# Camera extrinsics (changes with camera position)
**/camera_extrinsics.json
```

---

## Advanced: Manual Extrinsics Computation

If you want to compute extrinsics separately before running the full pipeline:

### Option A: Use track_objects.py

```bash
cd map_anchors/scripts
python track_objects.py --camera 1
```

This will:
- Compute and save extrinsics to `camera_extrinsics.json`
- Start basic tracking without Kalman filter
- Useful for testing camera position

### Option B: Use Full Pipeline

Just run `main.py` - it does everything automatically!

---

## Summary: What to Run Each Day

### ☀️ Morning (Camera Remounted)

```bash
cd full_pipeline/scripts
python main.py --camera 1
```

**That's it!** System automatically:
1. Loads intrinsics (saved)
2. Recomputes extrinsics (automatic when 4 markers visible)
3. Starts tracking with Kalman filter

### 🔧 If Something's Wrong

1. Press **SPACE** to reset extrinsics
2. Point at all 4 reference markers
3. Wait for auto-recalibration

### 🔄 When to Recalibrate Intrinsics (Rare)

```bash
cd camera_calibration_folder
python calibrate_camera.py --camera 1 --num-images 30
```

**Only needed if:**
- Switching cameras
- Changing resolution
- Tracking accuracy is poor (<20cm error)

---

## Camera Positioning Tips

### Optimal Setup

- **Height:** 1.5-1.8m above table
- **Angle:** Looking straight down (perpendicular to table)
- **Coverage:** All 4 corners visible with some margin
- **Lighting:** Diffuse, no direct glare on markers

### Reference Marker Positions (Physical Setup)

Ensure these markers are at exactly these positions:

| ID | Position (m) | Location |
|----|--------------|----------|
| 22 | (0.600, 0.600, 0.0) | Bottom-left |
| 20 | (0.600, 1.400, 0.0) | Top-left |
| 21 | (2.400, 1.400, 0.0) | Top-right |
| 23 | (2.400, 0.600, 0.0) | Bottom-right |

**Critical:** If you move these markers, update positions in `config/pipeline_config.yaml`

---

## Performance Checklist

✅ All 4 reference markers visible  
✅ Camera stable (not moving/vibrating)  
✅ Good lighting (no shadows on markers)  
✅ Intrinsics loaded successfully  
✅ Extrinsics recomputed (status = "TRACKING")  
✅ Test object (ID 13) shows correct position  
✅ FPS > 25  

**Ready to track!** 🎯

---

## Questions?

**Q: Do I run calibrate_camera.py every day?**  
A: No! Only run it once or when changing cameras/resolution.

**Q: Do I need to delete camera_extrinsics.json?**  
A: No! The system automatically recomputes when it detects markers.

**Q: What if reference markers aren't visible during competition?**  
A: Once extrinsics are computed, you can move camera view away from reference markers. Extrinsics stay valid as long as camera doesn't move.

**Q: Can I save multiple extrinsics for different camera positions?**  
A: Yes! Copy `camera_extrinsics.json` to `camera_extrinsics_position1.json` etc., then use `--extrinsics` flag:
```bash
python main.py --camera 1 --extrinsics path/to/camera_extrinsics_position1.json
```

---

**Last Updated:** 2025-01-21  
**System Status:** ✅ Production Ready  
**Tested With:** iPhone XR, 1280×720, 4 reference markers
