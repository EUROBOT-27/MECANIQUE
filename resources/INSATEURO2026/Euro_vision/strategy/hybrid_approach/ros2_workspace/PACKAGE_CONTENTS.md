# Hybrid Approach ROS2 Package - Complete File List

## 📦 Package Structure for ROS Team

This document lists ALL files needed to run the hybrid approach on ROS2.

---

## Required Files

### 1. Main ROS2 Integration
```
ros2_workspace/
├── main.py                    # ROS2 supervisor with DDS communication
└── README.md                  # ROS2 integration guide
```

### 2. Core Strategy Modules
```
strategy/hybrid_approach/src/
└── crate_flip_manager.py      # Crate counting and flip decision logic
```

### 3. Strategy Utilities (from strategy/utils/)
```
strategy/utils/
├── __init__.py                # Package initialization
├── config.py                  # StrategyConfig, DEFAULT_CONFIG - all tunable parameters
├── world_state.py             # WorldState, CrateInfo, EnemyInfo, RobotPose data classes
├── crate_id_tracker.py        # Spatial tracking for ArUco crates (unique ID assignment)
└── task_models.py             # Task definitions (optional - not used in main.py)
```

### 4. Kalman Filter System
```
kalman_filter/src/kalman_filter/
├── __init__.py                # Package initialization
└── tracker.py                 # MultiMarkerTracker - Kalman filter for enemy tracking
```

### 5. Path Planning Utilities
```
path_planning/utils/
├── __init__.py                # Package exports
├── rrt_connect.py             # RRT-Connect algorithm for path planning
└── path_smoothing.py          # Bezier curve smoothing for paths
```

### 6. Configuration & Documentation
```
strategy/hybrid_approach/
├── requirements.txt           # Python dependencies
├── README.md                  # Architecture overview
└── INTEGRATION_GUIDE.md       # How to integrate with ROS2
```

---

## 📋 Complete File Checklist

Copy these files to your ROS2 package:

- [ ] `strategy/hybrid_approach/ros2_workspace/main.py`
- [ ] `strategy/hybrid_approach/src/crate_flip_manager.py`
- [ ] `strategy/utils/__init__.py`
- [ ] `strategy/utils/config.py`
- [ ] `strategy/utils/world_state.py`
- [ ] `strategy/utils/crate_id_tracker.py`
- [ ] `kalman_filter/src/kalman_filter/__init__.py`
- [ ] `kalman_filter/src/kalman_filter/tracker.py`
- [ ] `path_planning/utils/__init__.py`
- [ ] `path_planning/utils/rrt_connect.py`
- [ ] `path_planning/utils/path_smoothing.py`
- [ ] `strategy/hybrid_approach/requirements.txt`
- [ ] `strategy/hybrid_approach/README.md`
- [ ] `strategy/hybrid_approach/INTEGRATION_GUIDE.md` (if exists)

---

## 📂 Suggested ROS2 Package Structure

```
hybrid_supervisor_ros2/
├── setup.py                          # ROS2 package setup
├── package.xml                       # ROS2 package manifest
├── requirements.txt                  # Python dependencies
├── README.md                         # Package documentation
│
├── hybrid_supervisor/                # Main package directory
│   ├── __init__.py
│   ├── main.py                       # ROS2 supervisor node (from ros2_workspace/main.py)
│   │
│   ├── strategy/                     # Strategy modules
│   │   ├── __init__.py
│   │   ├── crate_flip_manager.py
│   │   └── utils/                    # Strategy utilities
│   │       ├── __init__.py
│   │       ├── config.py
│   │       ├── world_state.py
│   │       └── crate_id_tracker.py
│   │
│   ├── kalman_filter/                # Kalman tracking
│   │   ├── __init__.py
│   │   └── tracker.py
│   │
│   └── path_planning/                # Path planning algorithms
│       ├── __init__.py
│       ├── rrt_connect.py
│       └── path_smoothing.py
│
├── msg/                              # Custom ROS2 messages
│   └── NavigationDecision.msg
│
├── launch/                           # Launch files
│   └── hybrid_supervisor.launch.py
│
└── config/                           # Configuration files
    └── supervisor_params.yaml
```

---

## 🔧 Python Dependencies

From `requirements.txt`:
```
numpy>=1.24.0
filterpy>=1.4.5  # For Kalman filter (if used, check tracker.py)
```

**Standard library only** (no external CV dependencies in core logic):
- `typing`
- `dataclasses`
- `pathlib`
- `time`
- `json`

---

## 🚀 Integration Steps

1. **Copy Files**: Transfer all files from checklist above
2. **Adjust Imports**: Change relative imports to match ROS2 package structure
3. **Implement ROS2 Hooks**: Replace placeholders in `main.py`:
   - `_init_ros2()` - Initialize node, subscribers, publishers
   - `destination_callback()` - Handle incoming destinations
   - `_publish_decision()` - Publish decisions back
4. **Add ROS2 Messages**: Define `NavigationDecision.msg` custom message
5. **Test**: Run in test mode first (`python main.py --test`)
6. **Deploy**: Integrate with ROS2 launch system

---

## 📡 ROS2 Topics & Messages

### Subscriptions
- **Topic**: `/navigation/destination`
- **Type**: `geometry_msgs/Point` (or custom message with task type)
- **Purpose**: Receive destination waypoints from Raspberry Pi

### Publications
- **Topic**: `/navigation/decision`
- **Type**: Custom `NavigationDecision` message
  ```
  std_msgs/Header header
  string status          # "ACCEPT" or "REJECT"
  string reason          # Human-readable explanation
  string threat_level    # "NONE", "LOW", "MODERATE", "HIGH", "CRITICAL"
  float32 confidence     # 0.0 to 1.0
  geometry_msgs/Point[] waypoints
  string[] flip_positions  # Crate flip targets
  ```

- **Topic**: `/navigation/waypoints` (optional, can merge with decision)
- **Type**: `nav_msgs/Path`
- **Purpose**: Optimized path waypoints for robot to follow

### Vision Data Input
The supervisor needs vision data updates at ~30Hz. This should come from:
- **Topic**: `/vision/aruco_detections` (or similar)
- **Type**: Custom message with ArUco marker detections
- **Data**: `{marker_id: (x, y, theta), ...}`

Call `supervisor.update_vision(detections)` on each frame.

---

## 🧪 Testing Without ROS2

```bash
cd ros2_workspace
python main.py --test --team blue
```

This runs the full logic with simulated data, no ROS2 required.

---

## ⚠️ Important Notes

### Import Path Adjustments Needed
The current code uses relative imports assuming it runs from the project root:
```python
from strategy.utils.config import StrategyConfig
from kalman_filter.src.kalman_filter.tracker import MultiMarkerTracker
```

In a ROS2 package, you may need to adjust to:
```python
from hybrid_supervisor.strategy.utils.config import StrategyConfig
from hybrid_supervisor.kalman_filter.tracker import MultiMarkerTracker
```

### Kalman Filter Dependency
The `tracker.py` uses standard NumPy-based Kalman implementation. Check if it requires `filterpy` library or is self-contained.

### Configuration Tuning
All parameters are in `strategy/utils/config.py`:
- Field dimensions
- Scoring rules (DO NOT MODIFY - official Eurobot rules)
- Utility weights (TUNABLE for strategy preferences)
- Safety thresholds (enemy danger radius, etc.)

Use `config.set_aggressive_mode()` or create custom config for different behaviors.

---

## 📞 Contact & Support

For integration questions:
1. Read `README.md` for architecture overview
2. Check `INTEGRATION_GUIDE.md` for detailed setup
3. Run test mode to verify all dependencies work
4. Check import paths match your ROS2 package structure

---

## 📊 File Size Summary

Total files: ~13 Python files
Total lines: ~3000-4000 LOC
External dependencies: numpy, (optional: filterpy)
ROS2 dependencies: rclpy, geometry_msgs, nav_msgs, std_msgs
