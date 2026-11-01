# Kalman Filter Tuning Guide

## Quick Start

1. **Run the tuner**:
   ```bash
   python tune_kalman.py --camera 1
   ```

2. **Place enemy marker (ID 13) in camera view**

3. **Wait for calibration**:
   - Need all 4 reference markers (20-23) visible
   - Status will show "TRACKING" when ready

## Controls

### Parameter Adjustment
- **Q/A** - Increase/Decrease Process Noise (Q)
- **W/S** - Increase/Decrease Measurement Noise (R)
- **R** - Reset to default values
- **P** - Plot current statistics
- **SPACE** - Reset extrinsics (recalibrate camera pose)
- **ESC** - Quit

## Understanding the Parameters

### Process Noise (Q)
Controls how much the filter trusts its **prediction model**.

- **Higher Q** (e.g., 0.1):
  - Filter expects more unpredictable movement
  - Responds faster to changes
  - More jittery output
  - Good for: Fast, erratic robot movements
  
- **Lower Q** (e.g., 0.001):
  - Filter expects smooth, predictable motion
  - Slower response to changes
  - Smoother output
  - Good for: Slow, steady robot movements

**Default: 0.01** - balanced for typical robot motion

### Measurement Noise (R)
Controls how much the filter trusts the **sensor measurements**.

- **Higher R** (e.g., 1.0):
  - Filter assumes measurements are noisy
  - Relies more on predictions
  - Very smooth but potentially lagging
  - Good for: Noisy camera/lighting conditions
  
- **Lower R** (e.g., 0.01):
  - Filter trusts measurements more
  - Tracks closer to raw detections
  - Less smoothing
  - Good for: Clean, stable detections

**Default: 0.1** - works well with ArUco markers

## Tuning Workflow

### Step 1: Baseline Test (Stationary)
1. Place enemy marker stationary on table
2. Observe raw vs filtered positions
3. Press **P** to see statistics
4. **Goal**: Filtered position should be very stable (< 5mm std deviation)

If still jittery:
- Increase R (W key) to trust measurements less
- Decrease Q (A key) to expect less motion

### Step 2: Response Test (Moving)
1. Move marker in straight line (slow, constant speed)
2. Observe if filter lags behind
3. **Goal**: Filter should track smoothly without significant lag

If lagging:
- Increase Q (Q key) to allow faster prediction updates
- Decrease R (S key) to trust measurements more

### Step 3: Quick Motion Test
1. Move marker quickly, then stop suddenly
2. Observe settling time
3. **Goal**: Should stabilize within 0.5 seconds

If takes too long to stabilize:
- Decrease R (S key)
- Adjust Q carefully (Q/A keys)

### Step 4: Occlusion Recovery Test
1. Cover marker briefly (1-2 seconds)
2. Uncover and observe recovery
3. **Goal**: Should snap back to correct position within 3-5 frames

If drifts too much:
- Increase Q (Q key) to allow position correction

## Understanding the Statistics

When you press **P**, you'll see:

```
STATISTICS
==========================================================
Raw X std:      18.50 mm       <- Without Kalman filter
Filtered X std: 2.30 mm        <- With Kalman filter
Improvement X:  87.6%          <- Reduction in jitter

Raw Y std:      21.20 mm
Filtered Y std: 2.80 mm
Improvement Y:  86.8%
```

**Good values**:
- Filtered std < 5mm for stationary object
- Improvement > 80%

**If improvement is too high (>95%)**:
- Filter might be over-smoothing
- Test with moving marker to check lag

## Common Tuning Scenarios

### Scenario 1: Robot moves slowly and predictably
```
Recommended: Q = 0.005, R = 0.1
```
- Low Q: smooth motion expected
- Normal R: trust ArUco detection

### Scenario 2: Robot moves quickly and erratically
```
Recommended: Q = 0.05, R = 0.15
```
- High Q: allow quick motion changes
- Higher R: more smoothing during fast motion

### Scenario 3: Poor lighting / noisy camera
```
Recommended: Q = 0.01, R = 0.3
```
- Normal Q: typical motion
- High R: don't trust noisy measurements

### Scenario 4: Need maximum accuracy (stationary)
```
Recommended: Q = 0.001, R = 0.05
```
- Very low Q: minimal expected motion
- Low R: trust clean measurements

## Recording Your Findings

Create a note of optimal values:

```yaml
# Kalman Parameters - Tuned [DATE]
# Conditions: [lighting, distance, motion type]
process_noise: 0.015      # Q value
measurement_noise: 0.12   # R value

# Performance:
# - Stationary std: 2.5mm
# - Tracking lag: minimal
# - Occlusion recovery: good
```

## Tips

1. **Start with defaults** (Q=0.01, R=0.1) and make small adjustments
2. **Test both stationary and moving** scenarios
3. **Real conditions**: Test with actual robot movements, not just hand motions
4. **Lighting matters**: Re-tune if you change lighting significantly
5. **Plot frequently** (P key) to see quantitative improvement
6. **Document optimal values** for your specific setup

## Troubleshooting

### "No markers detected"
- Ensure reference markers (20-23) visible for calibration
- Check lighting - ArUco needs good contrast
- Try moving camera slightly

### "CALIBRATING stuck"
- Need all 4 reference markers (20-23) in view
- Make sure markers are flat on table
- Press SPACE to force reset if needed

### Filter seems to do nothing
- Q or R might be extreme values
- Press 'r' to reset to defaults
- Check that enemy marker (ID 13) is detected

### Values keep resetting
- Make note of good values before closing
- Update `vision_config.yaml` with optimal parameters
- Consider editing default values in script

## Next Steps

Once you find optimal parameters:

1. Update `publisher_ready/config/vision_config.yaml`:
   ```yaml
   kalman:
     process_noise: 0.015     # Your tuned value
     measurement_noise: 0.12   # Your tuned value
   ```

2. Test with actual robot:
   - Run full vision_tracker.py
   - Verify performance in real usage
   - Fine-tune if needed

3. Document in your project:
   - Note the conditions (lighting, distance, speed)
   - Record statistics
   - Share optimal values with team
