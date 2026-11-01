# Occlusion Handling Strategies

## Overview

This module provides comprehensive strategies for handling marker occlusion in the Eurobot 2026 vision system. Occlusion occurs when markers are partially or fully hidden by obstacles, other robots, or game elements.

## Types of Occlusion

### 1. Full Occlusion
Marker is completely hidden. No corners are visible.

**Symptoms:**
- Zero ArUco detections for the marker
- Sudden loss of tracking
- No corner points detected

**Strategy:**
- Use Kalman filter prediction
- Maintain confidence scoring
- Timeout after extended occlusion

### 2. Partial Occlusion
Part of the marker is visible (1-3 corners).

**Symptoms:**
- ArUco detection fails standard threshold
- Only 1-3 corners visible (need all 4 for standard detection)
- Higher detection noise

**Strategy:**
- Attempt partial marker reconstruction
- Use reduced-confidence detection
- Fusion with Kalman prediction

### 3. Intermittent Occlusion
Marker appears and disappears rapidly.

**Symptoms:**
- Detection success rate < 50%
- Alternating detection/no-detection frames
- Position jumps between detections

**Strategy:**
- Heavy Kalman filtering
- Temporal smoothing
- Outlier rejection

## Implementation

### Detection Quality Assessment

```python
from src.occlusion_handler import OcclusionHandler, DetectionQuality

handler = OcclusionHandler(
    history_length=30,
    partial_detection_threshold=0.5,
    occlusion_timeout=1.0  # seconds
)

# Assess detection quality
quality = DetectionQuality(
    marker_id=30,
    detected=True,
    corners_detected=3,  # Only 3 of 4 corners visible
    detection_confidence=0.6,
    is_partial=True,
    timestamp=time.time()
)

# Handle occlusion
estimated_pose, confidence = handler.handle_occlusion(
    marker_id=30,
    detection_quality=quality,
    kalman_prediction=(1.5, 0.8, 0.3)  # From Kalman filter
)
```

### Confidence Scoring

The system provides confidence scores (0.0 to 1.0) based on:

1. **Detection quality**: Number of corners detected
2. **Occlusion duration**: Confidence decreases over time
3. **Historical accuracy**: Past detection reliability

```python
# Full detection
confidence = 1.0

# Partial detection (3/4 corners)
confidence = 0.75 * detection_quality

# Kalman prediction (no detection)
confidence = max(0.0, 1.0 - occlusion_duration / 30)
```

## Strategies

### Strategy 1: Kalman Prediction

Best for: Full occlusion, short duration (< 1 second)

```python
# When marker is fully occluded
if not detection_quality.detected:
    # Predict using Kalman filter
    predicted_state = kalman_tracker.predict(dt)
    
    # Confidence decreases with prediction duration
    confidence = 1.0 - (frames_without_detection / 30.0)
    
    # Use prediction if confidence > threshold
    if confidence > 0.5:
        return predicted_state, confidence
```

**Advantages:**
- Smooth prediction based on motion model
- Works well for moving markers
- No additional complexity

**Limitations:**
- Accuracy degrades over time
- Assumes constant velocity
- Cannot handle sudden direction changes

### Strategy 2: Partial Detection

Best for: Partial occlusion (1-3 corners visible)

```python
# Attempt partial marker detection
if 1 <= corners_detected < 4:
    # Use available corners to estimate pose
    # (requires custom ArUco detection code)
    
    # Reduce confidence based on missing corners
    corner_confidence = corners_detected / 4.0
    
    # Fuse with Kalman prediction
    fused_pose = fuse_estimates([
        (partial_pose, corner_confidence),
        (kalman_pose, 0.7)
    ])
```

**Advantages:**
- Uses available visual information
- Better than pure prediction
- Can handle stationary occlusion

**Limitations:**
- Requires modified ArUco detector
- Higher computational cost
- Less accurate than full detection

### Strategy 3: History-Based Estimation

Best for: Stationary or slow-moving markers

```python
# Estimate from detection history
def estimate_from_history(marker_id):
    history = get_detection_history(marker_id, last_n=5)
    
    # Weighted average (recent detections weighted more)
    weights = np.exp(np.linspace(-1, 0, len(history)))
    weights /= weights.sum()
    
    x = sum(h[0] * w for h, w in zip(history, weights))
    y = sum(h[1] * w for h, w in zip(history, weights))
    theta = circular_mean([h[2] for h in history], weights)
    
    return (x, y, theta)
```

**Advantages:**
- Robust for stationary markers
- Smooths noisy detections
- Simple to implement

**Limitations:**
- Lags behind moving markers
- Requires sufficient history
- Not suitable for fast motion

### Strategy 4: Confidence Fusion

Best for: Combining multiple estimates

```python
from src.occlusion_handler.handler import ConfidenceFusion

# Multiple estimates with different confidence levels
estimates = [
    ((1.5, 0.8, 0.3), 0.6),  # Partial detection
    ((1.52, 0.81, 0.29), 0.7),  # Kalman prediction
    ((1.49, 0.79, 0.31), 0.4)   # History-based
]

# Fuse with confidence weighting
fused_pose, fused_confidence = ConfidenceFusion.fuse_estimates(estimates)
```

**Advantages:**
- Combines multiple information sources
- Weighted by confidence
- Robust to single-source failures

**Limitations:**
- More complex
- May over-smooth
- Requires tuning

## Practical Recommendations

### For Map Anchors (IDs 20-23)
- **Expected behavior**: Stationary
- **Recommended strategy**: History-based + Kalman
- **Timeout**: Long (5-10 seconds) - should rarely be occluded
- **Action on loss**: Re-calibrate world frame

```python
# Map marker configuration
map_handler = OcclusionHandler(
    history_length=50,
    partial_detection_threshold=0.7,
    occlusion_timeout=5.0
)
```

### For Caisse Markers (IDs 36, 47, 41)
- **Expected behavior**: Slow motion or stationary
- **Recommended strategy**: Partial detection + Kalman
- **Timeout**: Medium (2-3 seconds)
- **Action on loss**: Mark as moved/removed

```python
# Caisse marker configuration
caisse_handler = OcclusionHandler(
    history_length=30,
    partial_detection_threshold=0.6,
    occlusion_timeout=2.0
)
```

### For Enemy Markers (IDs 30+)
- **Expected behavior**: Fast motion, frequent occlusion
- **Recommended strategy**: Kalman + Confidence fusion
- **Timeout**: Short (0.5-1 second)
- **Action on loss**: Continue prediction, high priority re-acquisition

```python
# Enemy marker configuration
enemy_handler = OcclusionHandler(
    history_length=20,
    partial_detection_threshold=0.5,
    occlusion_timeout=0.5
)
```

## Integration Example

```python
class VisionPipeline:
    def __init__(self):
        self.tracker = MultiMarkerTracker()
        self.occlusion_handler = OcclusionHandler()
    
    def process_frame(self, detections):
        # Get all tracked states (includes predictions)
        states = self.tracker.update(detections, dt=0.033)
        
        # Handle occlusion for each tracked marker
        final_estimates = {}
        
        for marker_id, state in states.items():
            if marker_id in detections:
                # Good detection - add to history
                self.occlusion_handler.add_to_history(
                    marker_id,
                    detections[marker_id]
                )
                final_estimates[marker_id] = (state, 1.0)
            
            else:
                # Marker is occluded - use strategies
                quality = DetectionQuality(
                    marker_id=marker_id,
                    detected=False,
                    corners_detected=0,
                    detection_confidence=0.0,
                    is_partial=False,
                    timestamp=time.time()
                )
                
                estimated_pose, confidence = self.occlusion_handler.handle_occlusion(
                    marker_id=marker_id,
                    detection_quality=quality,
                    kalman_prediction=(state.x, state.y, state.theta)
                )
                
                if estimated_pose and confidence > 0.5:
                    final_estimates[marker_id] = (estimated_pose, confidence)
        
        return final_estimates
```

## Performance Metrics

Track these metrics to evaluate occlusion handling:

```python
stats = occlusion_handler.get_occlusion_statistics()

print(f"Markers tracked: {stats['total_markers']}")
print(f"Currently occluded: {stats['occluded_markers']}")
print(f"Partial detections: {stats['partial_detections']}")
print(f"Full occlusions: {stats['full_occlusions']}")
print(f"Avg occlusion duration: {stats['avg_occlusion_duration']:.1f} frames")
```

## Testing Occlusion Handling

```python
# Simulate occlusion scenario
def test_occlusion():
    # 1. Track marker for 1 second (good detections)
    for i in range(30):
        detection = (1.0 + i*0.01, 0.5, 0.0)
        state = tracker.update({30: detection})
    
    # 2. Occlude marker for 0.5 seconds (15 frames)
    for i in range(15):
        state = tracker.predict(dt=0.033)
        print(f"Predicted: ({state.x:.2f}, {state.y:.2f}), "
              f"confidence: {state.confidence:.2f}")
    
    # 3. Re-detect marker
    detection = (1.45, 0.5, 0.0)  # Should be close to prediction
    state = tracker.update({30: detection})
    print(f"Recovered: ({state.x:.2f}, {state.y:.2f})")
```

## Troubleshooting

### Problem: Predictions diverge during occlusion
**Solution**: Increase measurement noise (R), decrease process noise (Q)

### Problem: Marker marked as lost too quickly
**Solution**: Increase `occlusion_timeout` parameter

### Problem: Partial detections too noisy
**Solution**: Increase `partial_detection_threshold` to reject low-quality detections

### Problem: System too slow with many markers
**Solution**: Disable partial detection, use Kalman prediction only

## References

- Bar-Shalom et al. "Tracking and Data Association" (2001)
- OpenCV ArUco documentation: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- Eurobot 2026 competition rules
