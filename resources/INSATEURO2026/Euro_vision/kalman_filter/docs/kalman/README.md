# Kalman Filter Implementation for ArUco Tracking

## Overview

This module implements a Kalman filter for tracking ArUco markers in the Eurobot 2026 competition. The filter provides smooth tracking and prediction during frame drops or occlusion.

## Theory

### State Vector

The Kalman filter tracks a 6-dimensional state:

```
x = [x, y, θ, vx, vy, vθ]ᵀ
```

Where:
- `x, y`: Position in meters (world coordinates)
- `θ`: Orientation in radians
- `vx, vy`: Linear velocities in m/s
- `vθ`: Angular velocity in rad/s

### Motion Model

The filter uses a constant velocity motion model:

```
x(k+1) = F * x(k) + w(k)
```

State transition matrix F:
```
F = [1  0  0  dt  0   0 ]
    [0  1  0  0   dt  0 ]
    [0  0  1  0   0   dt]
    [0  0  0  1   0   0 ]
    [0  0  0  0   1   0 ]
    [0  0  0  0   0   1 ]
```

Where `dt` is the time step (typically 1/30 seconds for 30 FPS).

### Measurement Model

We observe position and orientation directly:

```
z = [x, y, θ]ᵀ = H * x + v
```

Measurement matrix H:
```
H = [1  0  0  0  0  0]
    [0  1  0  0  0  0]
    [0  0  1  0  0  0]
```

### Noise Covariances

- **Process noise (Q)**: Models uncertainty in motion
  - Position: σ² = 0.01
  - Velocity: σ² = 0.02 (higher uncertainty)

- **Measurement noise (R)**: Models sensor uncertainty
  - Position: σ² = 0.1 m²
  - Orientation: σ² = 0.1 rad²

## Usage

### Single Marker Tracking

```python
from src.kalman_filter import KalmanTracker, MarkerType

# Create tracker for enemy marker
tracker = KalmanTracker(
    marker_id=30,
    marker_type=MarkerType.ENEMY,
    process_noise=0.01,
    measurement_noise=0.1
)

# Process frames
dt = 1.0 / 30.0  # 30 FPS

# When marker is detected
measurement = (1.5, 0.8, 0.3)  # x, y, theta
state = tracker.update(measurement)
print(f"Position: ({state.x:.2f}, {state.y:.2f}), confidence: {state.confidence:.2f}")

# When marker is not detected (frame drop or occlusion)
state = tracker.predict(dt)
print(f"Predicted position: ({state.x:.2f}, {state.y:.2f}), confidence: {state.confidence:.2f}")
```

### Multi-Marker Tracking

```python
from src.kalman_filter import MultiMarkerTracker

# Create multi-marker tracker
tracker = MultiMarkerTracker(
    process_noise=0.01,
    measurement_noise=0.1,
    max_frames_without_detection=30
)

# Process detections
detections = {
    20: (0.0, 0.0, 0.0),      # Map anchor (Eurobot 2026)
    36: (0.5, 0.5, 0.2),      # Caisse (blue)
    30: (1.5, 0.8, 0.3)       # Enemy marker
}

states = tracker.update(detections, dt=0.033)

# Access tracked markers
for marker_id, state in states.items():
    print(f"Marker {marker_id}: type={state.marker_type.value}, "
          f"pos=({state.x:.2f}, {state.y:.2f})")

# Get markers by type
from src.kalman_filter.tracker import MarkerType
enemy_markers = tracker.get_states_by_type(MarkerType.ENEMY)

# Get tracking summary
summary = tracker.get_tracking_summary()
print(f"Tracking {summary['total_markers']} markers, "
      f"{summary['occluded_markers']} occluded")
```

## Benefits During Frame Drops

The Kalman filter provides several benefits when frames are dropped:

1. **Smooth Prediction**: Uses motion model to predict position
2. **Confidence Tracking**: Confidence decreases with missed detections
3. **Automatic Recovery**: When marker reappears, filter quickly converges
4. **Velocity Estimation**: Tracks velocity for better prediction

### Example: Frame Drop Scenario

```
Frame 1: Detection     → Update filter  → Confidence: 1.00
Frame 2: Detection     → Update filter  → Confidence: 1.00
Frame 3: NO DETECTION  → Predict only   → Confidence: 0.97
Frame 4: NO DETECTION  → Predict only   → Confidence: 0.93
Frame 5: NO DETECTION  → Predict only   → Confidence: 0.90
Frame 6: Detection     → Update filter  → Confidence: 1.00 (recovered)
```

## Marker Classification

Markers are automatically classified by ID (Eurobot 2026):

- Map anchors: IDs 20-23 (fixed corner references)
- Caisse markers: IDs 36 (blue), 47 (yellow), 41 (black/rotten)
- Enemy markers: IDs 30+ (opponent robot)

Different marker types can have different filter parameters:

```python
# Map anchors: fixed position, low process noise
map_tracker = KalmanTracker(20, MarkerType.MAP, process_noise=0.001)

# Enemy markers: fast motion, higher process noise
enemy_tracker = KalmanTracker(30, MarkerType.ENEMY, process_noise=0.05)
```

## Performance Considerations

### Computational Complexity

- **Prediction step**: O(n²) where n=6 (state dimension)
- **Update step**: O(n² * m²) where n=6, m=3 (measurement dimension)
- **Per-frame cost**: ~0.1-0.5 ms on Raspberry Pi 4

### Memory Usage

- Each tracker: ~1KB (state, covariance, matrices)
- For 15 markers: ~15KB total
- Negligible compared to image processing

### Real-time Performance

At 30 FPS (33ms per frame):
- Image capture: ~5ms
- ArUco detection: ~15-20ms
- Kalman filtering (15 markers): ~0.5ms
- **Total budget**: 25-30ms ✓ Sufficient headroom

## Tuning Guidelines

### Process Noise (Q)

Increase if:
- Markers move faster than expected
- Predictions diverge from actual positions
- Markers have unpredictable motion

Decrease if:
- Markers are stationary (map markers)
- Too much smoothing causes lag
- Tracking is too responsive to noise

### Measurement Noise (R)

Increase if:
- Camera detections are noisy
- Lighting conditions are poor
- Markers are far from camera

Decrease if:
- Camera calibration is excellent
- Detections are very accurate
- Over-smoothing is occurring

### Example Tuning

```python
# Stationary map markers
map_tracker = KalmanTracker(
    marker_id=0,
    marker_type=MarkerType.MAP,
    process_noise=0.001,      # Very low - nearly static
    measurement_noise=0.05    # Trust measurements
)

# Fast-moving enemy
enemy_tracker = KalmanTracker(
    marker_id=30,
    marker_type=MarkerType.ENEMY,
    process_noise=0.05,       # Higher - fast motion
    measurement_noise=0.1     # More smoothing
)
```

## Angle Normalization

The filter properly handles angle wraparound (θ ∈ [-π, π]):

```python
# Innovation for angle measurement
y[2] = normalize_angle(z[2] - state[2])
```

This ensures:
- θ = 179° and θ = -179° are treated as close (2° apart)
- No discontinuities at ±180°
- Correct interpolation across wraparound

## Integration with Vision Pipeline

```python
# Typical frame processing loop
def process_frame(frame):
    # 1. Detect ArUco markers
    detections = detect_aruco_markers(frame)
    
    # 2. Transform to world coordinates
    world_detections = {}
    for marker_id, corners in detections.items():
        x, y, theta = estimate_pose(corners, camera_matrix)
        x_world, y_world, theta_world = transform_to_world(x, y, theta)
        world_detections[marker_id] = (x_world, y_world, theta_world)
    
    # 3. Update Kalman filter
    dt = time.time() - last_frame_time
    states = tracker.update(world_detections, dt)
    
    # 4. Send smoothed positions to master controller
    for marker_id, state in states.items():
        if state.marker_type == MarkerType.ENEMY and not state.is_occluded:
            send_enemy_position(state.x, state.y, state.theta)
    
    return states
```

## References

- Kalman, R.E. (1960). "A New Approach to Linear Filtering and Prediction Problems"
- Welch & Bishop (2006). "An Introduction to the Kalman Filter" (UNC-Chapel Hill)
- OpenCV docs: https://docs.opencv.org/4.x/dd/d6a/classcv_1_1KalmanFilter.html
