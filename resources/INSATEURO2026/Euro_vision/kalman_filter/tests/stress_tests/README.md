# Stress Tests Documentation

## Overview

This directory contains stress tests for the Eurobot 2026 vision system, specifically testing the performance under heavy load with multiple ArUco markers present simultaneously.

## Test Scenarios

### 1. Light Load
- 4 map markers (IDs 20-23)
- 2 caisse markers (IDs 36, 47)
- 1 enemy marker (ID 30)
- **Total: 7 markers**
- Frame drop rate: 5%
- Occlusion rate: 10%

### 2. Medium Load
- 4 map markers (IDs 20-23)
- 3 caisse markers (IDs 36, 47, 41)
- 2 enemy markers (IDs 30-31)
- **Total: 11 markers**
- Frame drop rate: 10%
- Occlusion rate: 15%

- 4 map markers (IDs 20-23)
- 3 caisse markers (IDs 36, 47, 41)
- 3 enemy markers (IDs 30-32)
- **Total: 15 markers**
- Frame drop rate: 15%
- Occlusion rate: 20%

- 4 map markers (IDs 20-23)
- 3 caisse markers (IDs 36, 47, 41)
- 4 enemy markers (IDs 30-33)
- **Total: 18 markers**
- Frame drop rate: 20%
- Occlusion rate: 25%

## Running Tests

### Single Test

```bash
cd /home/runner/work/Euro_vision/Euro_vision
python tests/stress_tests/test_multiple_markers.py
```

This will run the default stress test configuration and print results.

### All Scenarios

Edit `test_multiple_markers.py` and uncomment the line at the bottom:

```python
if __name__ == "__main__":
    run_multiple_stress_tests()  # Uncomment this
```

Then run:

```bash
python tests/stress_tests/test_multiple_markers.py
```

## Expected Performance

On a Raspberry Pi 4:
- **Processing time**: < 1ms per frame
- **Tracking accuracy**: > 90% for all scenarios
- **FPS capability**: 30+ FPS
- **Memory usage**: < 100KB

The vision system should maintain real-time performance (>= 30 FPS) even under extreme load.

## Test Results Format

Results are saved to `/tmp/stress_test_results.json`:

```json
{
  "Light Load": {
    "config": {
      "num_map_markers": 4,
      "num_caisse_markers": 2,
      "num_enemy_markers": 1,
      ...
    },
    "total_frames": 300,
    "frames_processed": 285,
    "frames_dropped": 15,
    "average_processing_time_ms": 0.45,
    "tracking_accuracy": 0.95,
    ...
  },
  ...
}
```

## Interpreting Results

### Success Criteria

✓ **Good**: 
- Tracking accuracy > 90%
- Average processing time < 2ms
- Lost tracks < 10%

⚠️ **Acceptable**:
- Tracking accuracy 80-90%
- Average processing time 2-5ms
- Lost tracks 10-20%

✗ **Poor**:
- Tracking accuracy < 80%
- Average processing time > 5ms
- Lost tracks > 20%

### Common Issues

**High processing time**:
- Too many markers being tracked
- Inefficient matrix operations
- Solution: Optimize Kalman filter implementation

**Low tracking accuracy**:
- Process/measurement noise poorly tuned
- Frame drop rate too high
- Solution: Adjust Kalman filter parameters

**Many lost tracks**:
- `max_frames_without_detection` too low
- Occlusion duration exceeds timeout
- Solution: Increase timeout or improve prediction

## Custom Stress Tests

Create your own test configuration:

```python
from tests.stress_tests.test_multiple_markers import StressTestConfig, run_stress_test

# Custom configuration
config = StressTestConfig(
    num_map_markers=4,
    num_caisse_markers=12,  # More caisses
    num_enemy_markers=2,
    test_duration_frames=600,  # 20 seconds
    frame_drop_probability=0.2,
    occlusion_probability=0.3,
    fps=30
)

# Run test
results = run_stress_test(config)
results.print_summary()
```

## Benchmarking

To benchmark different Kalman filter configurations:

```python
# Test different noise parameters
for process_noise in [0.001, 0.01, 0.05, 0.1]:
    tracker = MultiMarkerTracker(process_noise=process_noise)
    # Run test with this tracker
    # Compare results
```

## Competition Simulation

The stress tests simulate realistic competition conditions:

1. **Map markers**: Fixed at corners (slight detection noise)
2. **Caisse markers**: Slow random motion (boxes being moved)
3. **Enemy markers**: Fast motion with direction changes
4. **Frame drops**: Simulates camera processing delays
5. **Occlusion**: Random occlusion events

This mimics the actual competition environment where:
- Multiple robots compete simultaneously
- Game elements (caisses) are moved around
- Markers may be temporarily occluded
- Camera may drop frames under load

## Next Steps

After stress testing:

1. **Profile performance**: Identify bottlenecks
2. **Tune parameters**: Optimize for your specific setup
3. **Test with real camera**: Validate with actual ArUco detection
4. **Integration test**: Test full pipeline with LoRa communication
5. **Field test**: Test on actual competition table

## See Also

- [Kalman Filter Documentation](../docs/kalman/README.md)
- [Occlusion Handling Documentation](../docs/occlusion/README.md)
- [Competition Demo Example](../examples/competition_tracking_demo.py)
