# Changelog

All notable changes to the Eurobot 2026 Vision System project will be documented in this file.

## [Unreleased]

### Updated (2025-10-08)

#### ArUco ID Schema Synchronization
- **CRITICAL**: Updated caisse marker IDs to match competition specifications
- ❌ OLD: Caisse IDs 10-20
- ✅ NEW: Caisse IDs 36 (blue), 47 (yellow), 41 (black/rotten)
- Updated `classify_marker()` function in `tracker.py`
- Synchronized with `caisses_detection` module configuration
- Updated all documentation and examples

### Added (2025-01-XX)

#### Kalman Filter Module
- Implemented `KalmanTracker` class for single marker tracking with 6D state vector (position, orientation, velocities)
- Implemented `MultiMarkerTracker` for managing multiple ArUco markers simultaneously
- Added automatic marker classification by ID (map: 0-3, caisse: 36/47/41, enemy: 30+)
- Added confidence scoring based on detection history
- Added prediction capability during frame drops and occlusion
- Proper angle normalization handling (±180° wraparound)
- Configurable process and measurement noise parameters
- Maximum 30 frames without detection timeout

#### Occlusion Handler Module
- Implemented `OcclusionHandler` class with multiple strategies
- Added full occlusion handling using Kalman filter prediction
- Added partial occlusion support (when only some corners are visible)
- Added history-based estimation for stationary markers
- Implemented `ConfidenceFusion` for combining multiple estimates
- Added per-marker occlusion state tracking
- Configurable timeout and quality thresholds
- Comprehensive occlusion statistics

#### Stress Testing Suite
- Created comprehensive stress test scenarios (light, medium, heavy, extreme)
- Implemented `MarkerSimulator` for realistic marker behavior simulation
- Added performance benchmarking (processing time, tracking accuracy, FPS)
- Support for testing frame drops and occlusion
- Automated result reporting with JSON export
- Multiple test scenarios with increasing difficulty

#### Examples and Demos
- Created `competition_tracking_demo.py` with full pipeline demonstration
- 10-second competition scenario simulation
- Occlusion recovery demonstration
- Real-time performance monitoring
- Detailed marker state visualization

#### Documentation
- Comprehensive Kalman filter documentation (`docs/kalman/README.md`)
  - Mathematical theory and motion model
  - Usage examples and API documentation
  - Tuning guidelines for different marker types
  - Performance considerations
  - Integration examples
- Occlusion handling documentation (`docs/occlusion/README.md`)
  - Types of occlusion (full, partial, intermittent)
  - Strategy descriptions and when to use each
  - Practical recommendations per marker type
  - Integration examples
  - Troubleshooting guide
- Project structure documentation (`docs/PROJECT_STRUCTURE.md`)
  - Complete directory layout
  - Module overview and responsibilities
  - Data flow diagrams
  - Development workflow
- Stress test documentation (`tests/stress_tests/README.md`)
  - Test scenarios and configurations
  - Running instructions
  - Expected performance metrics
  - Result interpretation guide

#### Project Infrastructure
- Created modular source code structure
- Added `requirements.txt` for dependency management
- Set up proper Python package structure with `__init__.py` files
- Created placeholder directories for future development

### Changed
- Updated main `README.md` with implementation status
- Added comprehensive usage examples to README
- Added performance metrics table to README
- Updated next steps checklist with completed items

## Future Work

### To Be Implemented
- ArUco marker detection module (`src/aruco_detection/`)
- Camera calibration utilities
- LoRa communication module (`src/communication/`)
- Real camera integration
- Field calibration tools
- Competition mode implementation

### Planned Improvements
- Adaptive Kalman filter parameters based on marker behavior
- Extended Kalman Filter (EKF) for non-linear motion
- Multi-hypothesis tracking for ambiguous situations
- Performance optimization for Raspberry Pi
- Additional visualization tools
- Unit tests for individual components
- Integration tests with mock camera data
- Continuous integration setup

---

## Version History Notes

This project follows semantic versioning. Version numbers are assigned as:
- MAJOR: Incompatible API changes
- MINOR: New functionality in a backward-compatible manner
- PATCH: Backward-compatible bug fixes

## References

- Eurobot 2026 Official Rules: [Cahier des Charges]
- OpenCV Documentation: https://docs.opencv.org/
- Kalman Filter Theory: Welch & Bishop (UNC-Chapel Hill)
