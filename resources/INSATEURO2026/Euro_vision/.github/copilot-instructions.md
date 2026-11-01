# Eurobot 2026 Computer Vision System - AI Coding Instructions

## Project Overview
This is a comprehensive computer vision system for Eurobot 2026 competition. The system uses overhead camera + ArUco markers to track game objects (hazelnut crates), enemy robots, and provide real-time strategic decision-making.

**Primary Development Focus**: The `strategy/hybrid_approach/` module is the active decision-making system. It combines static field coordinates (hardcoded in Raspberry Pi) with dynamic computer vision for intelligent supervision. Always consider hybrid approach patterns when generating strategy-related code.

## Critical Architecture Concepts

### ArUco ID Schema (MUST KNOW)
- **Map anchors**: IDs 20-23 (fixed corner references, 10cm markers)
- **Blue team crates**: ArUco ID 36 → Unique IDs 1001, 1002, 1003...
- **Yellow team crates**: ArUco ID 47 → Unique IDs 2001, 2002, 2003...
- **Enemy robots**: IDs 30+
- **Special black rotten crate**: ID 41

**Critical**: All blue crates share ID 36, all yellow share ID 47. The `CrateIDTracker` assigns unique IDs based on spatial position (15cm threshold). Always use `unique_id` field in strategy code, not ArUco `id`.

### Module Organization (Jan 2026 Reorganization)
All major modules follow `utils/` + `main/` structure:
- **`utils/`**: Reusable classes, algorithms, helper functions
- **`main/`**: Execution scripts that import from utils

Import pattern:
```python
# Utilities - shared components
from strategy.utils import StrategyConfig, WorldState, CrateInfo
from kalman_filter.tracker import MultiMarkerTracker

# Main scripts - execution logic
from strategy.main import StrategyManager
```

### Hybrid Strategy Philosophy: "Analyze, Validate, Optimize"

**Communication Flow (ROS2/DDS)**:
1. **Raspberry Pi** → sends destination waypoint via ROS2/DDS
2. **Hybrid Supervisor** → receives waypoint, analyzes threat + feasibility
3. **Decision**:
   - ✅ **ACCEPT**: Compute optimized path (RRT + smoothing), send waypoints back
   - ❌ **REJECT**: Send "REPLAN" flag, wait for new destination from Raspberry Pi
4. **Continuous**: Monitor enemy position/velocity with Kalman filter

**Core Responsibilities**:
- **Enemy Tracking**: Always use Kalman filter for velocity prediction and threat assessment
- **Waypoint Validation**: Check if destination is safe given current enemy state
- **Path Optimization**: Generate collision-free paths using RRT-Connect + smoothing
- **Crate Analysis**: Count crates in pantries for flip decisions
- **Replanning Triggers**: Send flags when threats detected or conditions change

Code in `strategy/hybrid_approach/`:
- `standalone_workspace/` - Visualization/testing without ROS (use for development)
- `ros2_workspace/` - Production-ready with DDS communication placeholders
- Core modules: `crate_flip_manager.py`, `waypoint_validator.py`, `path_optimizer.py`, `enemy_monitor.py`

## Essential Configuration Patterns

### StrategyConfig (`strategy/utils/config.py`)
Single source of truth for all tunable parameters. **Always use `DEFAULT_CONFIG` or pass `config` parameter** - never hardcode field dimensions, scoring rules, or weights.

```python
from strategy.utils.config import StrategyConfig, DEFAULT_CONFIG

# Use default
manager = CrateFlipManager(DEFAULT_CONFIG, team_color="blue")

# Or customize
config = StrategyConfig()
config.set_aggressive_mode()  # Lower safety, higher speed priority
```

Key config sections:
- Field geometry: `field_width`, `field_length`, `robot_radius`
- Scoring (official rules - DO NOT MODIFY): `score_hazelnut_in_nest`, `score_endgame_full`
- Utility weights: `weight_expected_score`, `weight_time_cost`, `weight_safety`
- Zone definitions: `nest_blue`, `pantry_zones`, `endgame_blue`

### WorldState Data Flow
```python
from strategy.utils.world_state import WorldState, CrateInfo, EnemyInfo

# CrateInfo MUST include unique_id (from CrateIDTracker)
crate = CrateInfo(
    unique_id=1001,        # Spatial tracking ID
    id=36,                 # ArUco marker ID
    pos=(1.2, 0.5, 0.0),
    ownership=CrateOwnership.OURS,
    container=CrateContainer.FREE,
    confidence=0.9
)
```

## Critical Workflows

### ROS2/DDS Communication Flow (Production)
```python
# Raspberry Pi → Hybrid Supervisor
# Topic: /navigation/destination
# Message: {x: float, y: float, task_type: string}

# Hybrid Supervisor → Raspberry Pi
# Topic: /navigation/decision
# Message: {status: "ACCEPT"|"REJECT", waypoints: [(x,y)...], reason: string}
```

**Workflow**:
1. Supervisor receives destination from Raspberry Pi
2. Check enemy threat using Kalman-predicted position (3s lookahead)
3. If safe: Compute RRT path + smooth, send waypoints back
4. If unsafe: Send REJECT + reason, wait for new destination
5. Continuous enemy monitoring at 30Hz

### Camera Calibration Pipeline
1. **Intrinsics** (do once per camera): 
   ```bash
   cd camera_calibration_folder
   python calibrate_camera.py --camera 1
   # Output: calibration/camera_calibration.json
   ```
   - Contains: focal length, principal point, distortion coefficients
   - Only redo if camera changes or resolution changes

2. **Extrinsics** (auto-recomputed every run):
   ```bash
   cd full_pipeline/scripts
   python main/main.py --camera 1
   ```
   - System automatically computes when it sees all 4 reference markers (20-23)
   - Uses PnP algorithm, saves to `camera_extrinsics.json`
   - Runtime control: Press SPACE to reset and recompute

**Never manually edit calibration JSON files** - always regenerate using scripts.

### Running the Full Pipeline
```bash
# Standard tracking
cd full_pipeline/scripts
python main/main.py --camera 1

# With custom config
python main/main.py --camera 1 --intrinsics /path/to/intrinsics.json

# Runtime controls
# ESC - quit
# SPACE - reset camera extrinsics
# K - toggle Kalman filter
```

### Testing Hybrid Strategy Features

**Standalone Visualization Workspace** (for development/testing):
```bash
cd strategy/hybrid_approach/standalone_workspace
python main.py  # Full supervisor with CV visualization, no ROS
```
Features: Interactive CV windows, simulated waypoint input, real-time threat display

**ROS2 Integration Workspace** (for production):
```bash
cd strategy/hybrid_approach/ros2_workspace
# ros2 run hybrid_supervisor main.py  # With DDS communication
python main.py  # Test mode with placeholders
```
Features: DDS subscriber/publisher placeholders, production logging

## Code Patterns & Conventions

### Path Planning Integration
**Always use utilities from reorganized structure**:
```python
from path_planning.utils.rrt_connect import rrt_connect_plan
from path_planning.utils.path_smoothing import smooth_path

# RRT parameters from config
path = rrt_connect_plan(
    start, goal, obstacles,
    step_size=config.path_planning_step_size,
    max_iter=config.path_planning_max_iter
)
```

### Kalman Filter Usage (ALWAYS for Enemy Tracking)
```python
from kalman_filter.tracker import MultiMarkerTracker, MarkerType

# Initialize ONCE at startup
tracker = MultiMarkerTracker(
    process_noise=0.01,      # Lower = smoother predictions
    measurement_noise=0.1,   # Higher = trust measurements less
    max_frames_without_detection=30
)

# Per frame update
detections = {30: (1.5, 0.8, 0.3)}  # marker_id: (x, y, theta)
states = tracker.update(detections, dt=1/30)

# Access enemy state with velocity
enemy_state = states[30]
print(f"Pos: ({enemy_state.x}, {enemy_state.y})")
print(f"Vel: ({enemy_state.vx}, {enemy_state.vy})")  # Critical for threat prediction
```

**Enemy tracking is MANDATORY with Kalman** - never use raw detections for decision-making.

### Visualization Pattern
Most scripts support `enable_visualization=True`:
```python
supervisor = HybridSupervisor(
    config=DEFAULT_CONFIG,
    team_color="blue",
    enable_visualization=True  # Shows CV windows
)
```

Visualization windows use consistent naming:
- "ArUco Detection" - raw marker detection
- "Strategy Visualization" - world state + decisions
- "Path Planning" - RRT trees + paths

## Common Pitfalls & Solutions

### ❌ DON'T: Hardcode field coordinates
```python
nest = (0.0, 0.6, 0.0, 0.4)  # BAD - what if field changes?
```
✅ DO:
```python
nest = config.nest_blue if team_color == "blue" else config.nest_yellow
```

### ❌ DON'T: Use ArUco ID for crate tracking
```python
if crate.id == 36:  # BAD - all blue crates have ID 36!
    tasks[crate.id] = new_task  # Overwrites other crates!
```
✅ DO:
```python
if crate.unique_id == 1001:  # Use spatial tracking ID
    tasks[crate.unique_id] = new_task
```

### ❌ DON'T: Import from old flat structure
```python
from strategy import StrategyConfig  # May break
```
✅ DO:
```python
from strategy.utils import StrategyConfig  # Post-reorganization
```

### ❌ DON'T: Modify official scoring rules
```python
config.score_hazelnut_in_nest = 5.0  # NEVER - official is 2.0
```
✅ DO: Only modify utility weights:
```python
config.weight_expected_score = 2.0  # Adjust priorities, not rules
```

## Key Files Reference

**Hybrid Strategy (PRIMARY)**:
- [`strategy/hybrid_approach/README.md`](strategy/hybrid_approach/README.md) - Architecture overview
- [`strategy/hybrid_approach/INTEGRATION_GUIDE.md`](strategy/hybrid_approach/INTEGRATION_GUIDE.md) - How to integrate
- [`strategy/utils/config.py`](strategy/utils/config.py) - All configuration parameters

**Core Systems**:
- [`kalman_filter/UPDATED_TECHNICAL_SUMMARY.md`](kalman_filter/UPDATED_TECHNICAL_SUMMARY.md) - Kalman architecture
- [`full_pipeline/README.md`](full_pipeline/README.md) - Complete tracking pipeline
- [`full_pipeline/STARTUP_GUIDE.md`](full_pipeline/STARTUP_GUIDE.md) - Daily usage workflow

**Quick References**:
- [`Documentation/PROGRESS.md`](Documentation/PROGRESS.md) - Current status, recent fixes
- [`REORGANIZATION.md`](REORGANIZATION.md) - Import path changes, migration guide
- [`Documentation/QUICK_START.md`](Documentation/QUICK_START.md) - Basic usage examples

## Dependencies
Install per-module requirements:
```bash
pip install -r requirements.txt  # Root level
pip install -r full_pipeline/requirements.txt
pip install -r strategy/hybrid_approach/requirements.txt
```

Core: `opencv-contrib-python`, `numpy`, `filterpy` (Kalman), `pyyaml` (configs)

## Testing Philosophy
- **Module-level**: Each file has `if __name__ == "__main__"` with self-test
- **Integration**: `quick_start_example.py` files in each module
- **Stress tests**: `kalman_filter/tests/stress_tests/` for performance validation
- **No formal test framework** - use executable examples instead

Run scripts directly to validate: `python crate_flip_manager.py` tests the module in isolation.
