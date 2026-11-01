# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/INSATEURO2026/Euro_vision.git
cd Euro_vision

# Install dependencies
pip install -r requirements.txt
```

## Running Examples

### Competition Demo
```bash
python examples/competition_tracking_demo.py
```

Simulates a 10-second competition scenario with:
- 4 map markers (fixed)
- 3 caisse markers (moving)
- 1 enemy marker (fast motion)
- Random frame drops and occlusion

### Stress Tests
```bash
python tests/stress_tests/test_multiple_markers.py
```

Tests system with 14 markers (4 map + 8 caisse + 2 enemy) under realistic conditions.

## Basic Usage

### Track Multiple Markers

```python
from src.kalman_filter import MultiMarkerTracker

# Initialize
tracker = MultiMarkerTracker(
    process_noise=0.01,
    measurement_noise=0.1,
    max_frames_without_detection=30
)

# Each frame
detections = {
    0: (0.0, 0.0, 0.0),      # Map marker
    10: (0.5, 0.5, 0.2),     # Caisse
    30: (1.5, 0.8, 0.3)      # Enemy
}

states = tracker.update(detections, dt=1/30)

# Access results
for marker_id, state in states.items():
    print(f"Marker {marker_id}: "
          f"pos=({state.x:.2f}, {state.y:.2f}), "
          f"confidence={state.confidence:.2f}")
```

### Handle Occlusion

```python
from src.occlusion_handler import OcclusionHandler, DetectionQuality
import time

# Initialize
handler = OcclusionHandler(
    history_length=30,
    partial_detection_threshold=0.5,
    occlusion_timeout=1.0
)

# When marker is detected
quality = DetectionQuality(
    marker_id=30,
    detected=True,
    corners_detected=4,
    detection_confidence=0.9,
    is_partial=False,
    timestamp=time.time()
)

pose, confidence = handler.handle_occlusion(
    marker_id=30,
    detection_quality=quality,
    kalman_prediction=None  # Not needed for full detection
)

# Add to history
handler.add_to_history(30, (1.5, 0.8, 0.3))

# Get statistics
stats = handler.get_occlusion_statistics()
print(f"Occluded markers: {stats['occluded_markers']}")
```

## Marker ID Convention

| Type   | ID Range | Usage                    |
|--------|----------|--------------------------|
| Map    | 0-3      | Fixed reference markers  |
| Caisse | 10-20    | Wooden boxes            |
| Enemy  | 30+      | Opponent robot          |

## Configuration Tips

### For Static Markers (Map)
```python
tracker = KalmanTracker(
    marker_id=0,
    marker_type=MarkerType.MAP,
    process_noise=0.001,      # Low - nearly static
    measurement_noise=0.05    # Trust measurements
)
```

### For Fast-Moving Markers (Enemy)
```python
tracker = KalmanTracker(
    marker_id=30,
    marker_type=MarkerType.ENEMY,
    process_noise=0.05,       # High - fast motion
    measurement_noise=0.1     # More smoothing
)
```

## Common Patterns

### Full Pipeline

```python
from src.kalman_filter import MultiMarkerTracker
from src.occlusion_handler import OcclusionHandler

class VisionSystem:
    def __init__(self):
        self.tracker = MultiMarkerTracker()
        self.handler = OcclusionHandler()
    
    def process_frame(self, detections, dt=0.033):
        # Update Kalman filters
        states = self.tracker.update(detections, dt)
        
        # Handle occlusion
        for marker_id, state in states.items():
            if marker_id in detections:
                self.handler.add_to_history(
                    marker_id,
                    detections[marker_id]
                )
        
        return states
```

### Get Tracking Summary

```python
summary = tracker.get_tracking_summary()

print(f"Total markers: {summary['total_markers']}")
print(f"Map: {summary['map_markers']}")
print(f"Caisse: {summary['caisse_markers']}")
print(f"Enemy: {summary['enemy_markers']}")
print(f"Occluded: {summary['occluded_markers']}")
```

### Filter by Type

```python
from src.kalman_filter.tracker import MarkerType

# Get only enemy markers
enemy_states = tracker.get_states_by_type(MarkerType.ENEMY)

for marker_id, state in enemy_states.items():
    print(f"Enemy {marker_id}: ({state.x:.2f}, {state.y:.2f})")
```

## Performance Expectations

- **Processing time**: < 1ms for 15 markers
- **Memory usage**: < 100KB
- **FPS capability**: 30+ on Raspberry Pi 4
- **Tracking accuracy**: 85-95%
- **Occlusion tolerance**: Up to 1 second

## Documentation

- **Kalman Filter**: [`docs/kalman/README.md`](docs/kalman/README.md)
- **Occlusion Handling**: [`docs/occlusion/README.md`](docs/occlusion/README.md)
- **Project Structure**: [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)
- **Stress Tests**: [`tests/stress_tests/README.md`](tests/stress_tests/README.md)
- **Implementation Summary**: [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)

## Troubleshooting

### Problem: Predictions diverge during occlusion
**Solution**: Adjust noise parameters
```python
tracker = MultiMarkerTracker(
    process_noise=0.005,  # Decrease
    measurement_noise=0.15  # Increase
)
```

### Problem: Tracking too slow
**Solution**: Increase smoothing
```python
tracker = MultiMarkerTracker(
    measurement_noise=0.2  # More smoothing
)
```

### Problem: Marker lost too quickly
**Solution**: Increase timeout
```python
tracker = MultiMarkerTracker(
    max_frames_without_detection=60  # 2 seconds at 30 FPS
)
```

## Next Steps

1. Integrate with camera feed
2. Implement ArUco detection
3. Add coordinate transformation to world frame
4. Implement LoRa communication
5. Field test on competition table

## Support

For more information, see the comprehensive documentation in the `docs/` directory.
