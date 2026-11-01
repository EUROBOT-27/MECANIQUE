# Project Structure

## Directory Layout

```
Euro_vision/
├── README.md                          # Main project documentation
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
│
├── src/                              # Source code
│   ├── kalman_filter/                # Kalman filtering module
│   │   ├── __init__.py              # Module exports
│   │   └── tracker.py               # Kalman tracker implementations
│   │
│   ├── occlusion_handler/           # Occlusion handling module
│   │   ├── __init__.py              # Module exports
│   │   └── handler.py               # Occlusion strategies
│   │
│   └── aruco_detection/             # ArUco detection (to be implemented)
│       └── (future: camera integration, pose estimation)
│
├── tests/                            # Test suites
│   └── stress_tests/                # Stress testing
│       ├── README.md                # Stress test documentation
│       └── test_multiple_markers.py # Multi-marker stress tests
│
├── examples/                         # Example implementations
│   └── competition_tracking_demo.py # Competition scenario demo
│
├── docs/                             # Documentation
│   ├── kalman/                      # Kalman filter docs
│   │   └── README.md                # Theory, usage, tuning
│   │
│   └── occlusion/                   # Occlusion handling docs
│       └── README.md                # Strategies, integration
│
└── config/                          # Configuration files
    └── (future: camera calibration, marker IDs)
```

## Module Overview

### `src/kalman_filter/`

Implements Kalman filtering for smooth ArUco marker tracking.

**Key classes:**
- `KalmanTracker`: Single marker tracking with 6D state
- `MultiMarkerTracker`: Manages multiple trackers simultaneously
- `MarkerState`: Data class for marker state representation
- `MarkerType`: Enum for marker classification

**Key features:**
- Constant velocity motion model
- Automatic velocity estimation
- Prediction during frame drops
- Confidence scoring
- Angle normalization

**When to use:**
- Smoothing noisy detections
- Predicting during occlusion
- Tracking moving objects (enemy, caisses)

### `src/occlusion_handler/`

Handles marker occlusion with multiple strategies.

**Key classes:**
- `OcclusionHandler`: Main occlusion management
- `DetectionQuality`: Quality assessment for detections
- `OcclusionState`: Per-marker occlusion tracking
- `ConfidenceFusion`: Fuses multiple estimates

**Key features:**
- Full occlusion handling (Kalman prediction)
- Partial occlusion support
- History-based estimation
- Confidence-weighted fusion
- Per-marker timeout management

**When to use:**
- Marker is partially visible
- Marker temporarily disappears
- Need to fuse multiple estimates
- Track occlusion statistics

### `tests/stress_tests/`

Comprehensive stress testing for multi-marker scenarios.

**Key components:**
- `StressTestConfig`: Test configuration
- `StressTestResults`: Results with metrics
- `MarkerSimulator`: Simulates marker detections
- `run_stress_test()`: Executes test scenarios

**Test scenarios:**
- Light, Medium, Heavy, Extreme load
- Configurable frame drops and occlusion
- Performance benchmarking
- JSON result export

**When to use:**
- Validate system performance
- Test scalability (many markers)
- Benchmark different configurations
- Simulate competition conditions

### `examples/`

Demonstration code showing complete usage.

**Key demos:**
- `competition_tracking_demo.py`: Full competition simulation
  - Multi-marker tracking
  - Occlusion handling
  - Performance monitoring
  - 10-second scenario

**When to use:**
- Learn how to integrate modules
- Understand complete pipeline
- Test configuration changes
- Visualize tracking behavior

### `docs/`

Comprehensive documentation for each module.

**Documentation includes:**
- **Theory**: Mathematical foundations
- **Usage**: Code examples and patterns
- **Tuning**: Parameter guidelines
- **Integration**: How to combine modules
- **Troubleshooting**: Common issues and solutions

## Data Flow

```
┌─────────────────┐
│  Camera Frame   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  ArUco Detection        │  (to be implemented)
│  - Detect markers       │
│  - Estimate pose        │
│  - Transform to world   │
└────────┬────────────────┘
         │
         │ detections: {id: (x, y, θ)}
         ▼
┌─────────────────────────┐
│  MultiMarkerTracker     │
│  - Update Kalman filter │
│  - Predict if missing   │
│  - Classify markers     │
└────────┬────────────────┘
         │
         │ states: {id: MarkerState}
         ▼
┌─────────────────────────┐
│  OcclusionHandler       │
│  - Assess quality       │
│  - Apply strategies     │
│  - Fuse estimates       │
└────────┬────────────────┘
         │
         │ final_estimates: {id: (pose, confidence)}
         ▼
┌─────────────────────────┐
│  LoRa Communication     │  (to be implemented)
│  - Format message       │
│  - Send to master       │
└─────────────────────────┘
```

## Marker ID Convention

As defined in the main README:

| Marker Type | ID Range | Quantity | Behavior | Tracking Priority |
|-------------|----------|----------|----------|-------------------|
| Map         | 0-3      | 4        | Fixed    | Critical          |
| Caisse      | 10-20    | 1-10     | Slow     | Medium            |
| Enemy       | 30+      | 1-4      | Fast     | High              |

## Configuration Files

### `requirements.txt`

Python dependencies for the project.

**Currently required:**
- `numpy>=1.24.0`: Core numerical computations

**Future dependencies:**
- OpenCV: Camera and ArUco detection
- FilterPy: Alternative Kalman implementation (optional)
- PySerial: LoRa communication
- Matplotlib: Visualization (optional)

### Future: `config/camera_calibration.yaml`

Will contain:
- Camera intrinsic parameters
- Distortion coefficients
- Extrinsic calibration (world frame)

### Future: `config/marker_ids.yaml`

Will contain:
- Marker ID assignments
- Marker types and sizes
- World coordinates for map markers

## Development Workflow

### 1. Development
```bash
# Clone repository
git clone https://github.com/INSATEURO2026/Euro_vision.git
cd Euro_vision

# Install dependencies
pip install -r requirements.txt

# Run examples
python examples/competition_tracking_demo.py
```

### 2. Testing
```bash
# Run stress tests
python tests/stress_tests/test_multiple_markers.py

# View results
cat /tmp/stress_test_results.json
```

### 3. Integration
```python
# In your vision pipeline
from src.kalman_filter import MultiMarkerTracker
from src.occlusion_handler import OcclusionHandler

tracker = MultiMarkerTracker()
handler = OcclusionHandler()

# Process each frame
def process_frame(detections):
    states = tracker.update(detections, dt=0.033)
    # ... handle occlusion ...
    return states
```

## Next Implementation Steps

### 1. ArUco Detection (`src/aruco_detection/`)
- Camera interface
- ArUco marker detection
- Pose estimation (rvec, tvec)
- Coordinate transformation to world frame

### 2. Camera Calibration
- Intrinsic calibration script
- Extrinsic calibration (world frame)
- Calibration data storage

### 3. Communication (`src/communication/`)
- LoRa interface
- Message formatting
- Data transmission protocol
- Error handling

### 4. Complete Integration
- End-to-end pipeline
- Real camera testing
- Field calibration tools
- Competition mode

## Best Practices

### Code Style
- Follow PEP 8
- Use type hints
- Document public APIs
- Include docstrings

### Testing
- Test edge cases (no detections, all occluded)
- Benchmark performance
- Validate accuracy
- Test on real hardware

### Performance
- Profile critical sections
- Optimize hot paths
- Monitor memory usage
- Target 30+ FPS

### Documentation
- Keep docs synchronized with code
- Include usage examples
- Document assumptions
- Explain design decisions

## See Also

- [Main README](../README.md): Project overview and getting started
- [Kalman Filter Docs](kalman/README.md): Theory and usage
- [Occlusion Docs](occlusion/README.md): Strategies and integration
- [Stress Test Docs](../tests/stress_tests/README.md): Testing guide
