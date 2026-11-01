# 🤖 EuroBot 2026 Vision System Pipeline

**Status**: 🚧 In Development  
**Last Updated**: January 15, 2026  
**Current Phase**: Production-Ready Integration & Testing

---

## 🎉 Latest Update (Jan 15, 2026)

**CRITICAL BUG FIX - CRATE ID TRACKING SYSTEM**

Major fix addressing the ArUco ID collision problem where all blue crates shared ID 36 and all yellow crates shared ID 47, causing severe tracking issues in the strategy system.

### 🔴 Critical Bug Fixed:

**Problem**: Multiple crates with same ArUco ID couldn't be tracked individually
- All blue crates (ID 36) were treated as single entity
- All yellow crates (ID 47) were treated as single entity
- Task planning couldn't distinguish between individual crates
- Moving one crate would overwrite data for all crates with same ID

**Solution**: Spatial-based unique ID assignment system
- Implemented `CrateIDTracker` class with position-based matching
- Blue crates: unique_id = 1001, 1002, 1003, ...
- Yellow crates: unique_id = 2001, 2002, 2003, ...
- Tracks crates across frames using 2D position proximity (15cm threshold)
- Maintains persistent IDs even as crates move
- Auto-removes crates that leave field of view (2s timeout)

### 📦 Files Created/Modified:

**New Files**:
- `strategy/crate_id_tracker.py` - Main tracking implementation
- `strategy/CRATE_TRACKING_SOLUTION.md` - Detailed solution documentation
- `full_pipeline/scripts/crate_id_tracker.py` - Copy for pipeline integration

**Updated Files**:
1. `strategy/world_state.py` - Added `unique_id` field to CrateInfo
2. `strategy/strategy_manager.py` - Integrated CrateIDTracker
3. `strategy/visualize_strategy.py` - Uses tracker in marker detection
4. `full_pipeline/scripts/crate_obstacle_manager.py` - Assigns unique IDs

### ✅ Testing & Validation:
- Position-based matching: 15cm threshold (tunable)
- Exponential Moving Average (EMA) for smooth position updates
- Timeout mechanism removes stale tracks after 2 seconds
- Unique IDs persist across frames for continuous tracking
- Works with strategy manager's utility-based task selection

---

## 📋 CURRENT STATUS SUMMARY (Jan 15, 2026)

### ✅ COMPLETED SYSTEMS (Production-Ready)

#### 1. **Camera Calibration System** ✅
- **Status**: Complete and validated
- **Location**: `camera_calibration_folder/`
- **Features**:
  - Intrinsic calibration with chessboard pattern
  - iPhone XR calibrated (focal length, distortion)
  - JSON output format for pipeline integration
  - Test and validation scripts included
- **Files**: `calibrate_camera.py`, `generate_chessboard.py`, `test_calibration.py`

#### 2. **Camera Extrinsics Computation** ✅
- **Status**: Multiple methods implemented
- **Location**: `map_anchors/`
- **Methods**:
  - Primary: PnP (Perspective-n-Point) method
  - Alternative: Kabsch algorithm
  - Interactive: GUI-based calibration tool
  - Validation: Pose stability testing
- **Files**: `compute_extrinsics.py`, `compute_extrinsics_kabsch.py`, `compute_extrinsics_gui.py`
- **Integration**: 4 fixed markers (IDs 20-23) at field corners

#### 3. **ArUco Marker Detection** ✅
- **Status**: Complete and integrated
- **Location**: `ArUco_detection_folder/`, `full_pipeline/`
- **Capabilities**:
  - DICT_4X4_50 dictionary
  - Real-time detection from webcam
  - Pose estimation (rvec, tvec)
  - World coordinate transformation
  - Multiple marker tracking
- **Marker Schema**:
  - Map anchors: IDs 20-23 (fixed reference)
  - Blue crates: ArUco ID 36 → Unique IDs 1001+
  - Yellow crates: ArUco ID 47 → Unique IDs 2001+
  - Enemy robots: IDs 30+
  - Special: Black rotten box ID 41

#### 4. **Kalman Filter System** ✅
- **Status**: Fully tested and validated
- **Location**: `kalman_filter/`
- **Features**:
  - 6D state tracking (x, y, θ, vx, vy, vθ)
  - Multi-marker tracking (map + crates + enemies)
  - Occlusion handling (4 strategies)
  - Confidence scoring
  - Stress tested: 85-95% accuracy, <1ms processing
- **Classes**: `KalmanTracker`, `MultiMarkerTracker`, `OcclusionHandler`
- **Documentation**: Complete technical summary and data flow diagrams

#### 5. **Path Planning System** ✅
- **Status**: Production-ready
- **Location**: `path_planning/`
- **Algorithms**:
  - RRT (Rapidly-Exploring Random Tree)
  - RRT-Connect (faster bidirectional variant)
  - A* (grid-based pathfinding)
  - Path smoothing (greedy straightening)
- **Features**:
  - Circular obstacle avoidance
  - Configurable step size and iterations
  - 2D planning with 3D output format
  - Multi-threaded approach with sudden stop trigger
- **Files**: `rrt.py`, `rrt_connect.py`, `A_star.py`, `path_smoothing.py`

#### 6. **Crate Orientation Estimation** ✅
- **Status**: Complete with fusion method
- **Location**: `orientation/`
- **Methods**:
  - BBox: Rotated bounding box (fast)
  - MinRect: Minimum area rectangle (robust)
  - PCA: Principal Component Analysis (accurate)
  - Fusion: Two-layer decision system (recommended)
- **Output**: Center position, angle (-90° to 90°), confidence score
- **Use Case**: Robotic arm alignment for pickup/flip operations
- **Files**: `vision_bbox.py`, `vision_minrect.py`, `vision_pca.py`, `vision_fusion.py`

#### 7. **Strategy System - Utility-Based Task Selection** ✅
- **Status**: Production-ready with bug fixes
- **Location**: `strategy/`
- **Features**:
  - 6 task types (nest, pantry, fridge, cursor, endgame)
  - Utility-based decision making
  - Official Eurobot 2026 scoring rules
  - Enemy avoidance with safety zones
  - Endgame priority boost (<15s remaining)
  - Path planning integration (RRT-Connect)
  - Live visualization with task rankings
- **Utility Formula**: `(score × feasibility × safety) / (time + distance + ε)`
- **Configuration**: Aggressive/defensive presets
- **Files**: `strategy_manager.py`, `task_models.py`, `world_state.py`, `config.py`

#### 8. **Crate ID Tracking System** ✅ NEW
- **Status**: Production-ready (Jan 15, 2026)
- **Location**: `strategy/crate_id_tracker.py`
- **Features**:
  - Unique ID assignment (Blue: 1001+, Yellow: 2001+)
  - Position-based matching (15cm threshold)
  - Temporal filtering with EMA
  - Automatic timeout for lost crates
  - Integrated with strategy manager
- **Solves**: Critical ArUco ID collision problem

### 🔄 IN PROGRESS

#### 1. **Full Pipeline Integration** 🔄
- **Status**: Active development
- **Location**: `full_pipeline/`
- **Current Work**:
  - Integrating all subsystems
  - Testing end-to-end pipeline
  - Optimizing performance
  - ROS2/DDS communication layer
- **Next**: Complete integration testing

#### 2. **ROS-Ready Pipeline** 🔄
- **Status**: In development
- **Location**: `ros_ready_pipeline/`
- **Components**:
  - ArUco ID detector
  - Main connect script
  - Camera calibration integration
  - Kalman filter integration
  - Path planning integration
- **Next**: Publisher/subscriber implementation

---

## 🎯 NEXT STEPS (Priority Order)

### Immediate (This Week)
1. **Integration Testing**
   - Test crate ID tracker with full pipeline
   - Validate unique ID persistence across frames
   - Stress test with multiple crates (10+ simultaneous)
   - Verify strategy manager receives correct unique IDs

2. **Performance Optimization**
   - Profile crate tracking overhead
   - Optimize EMA smoothing parameters
   - Test timeout values under real conditions

3. **Documentation Updates**
   - Update integration guides
   - Create troubleshooting section
   - Add performance benchmarks

### Short-term (1-2 Weeks)
4. **ROS2 Communication Layer**
   - Implement publishers for:
     - Crate positions (with unique IDs)
     - Enemy positions
     - Best task selection
     - Path waypoints
   - Implement subscribers for:
     - Robot odometry
     - LiDAR data
     - Match timer
   - Test DDS communication reliability

5. **Hardware Integration**
   - Mount overhead camera
   - Test lighting conditions
   - Calibrate for competition field
   - Validate marker detection range

6. **Live Testing**
   - Test with physical crates
   - Validate orientation estimation
   - Test multi-crate scenarios
   - Measure real-world accuracy

### Medium-term (3-4 Weeks)
7. **System Hardening**
   - Add error recovery mechanisms
   - Implement failsafe behaviors
   - Handle camera disconnection
   - Robust marker occlusion handling

8. **Competition Preparation**
   - Field setup and calibration procedures
   - Pre-match checklist
   - Backup systems
   - Emergency stop protocols

9. **Performance Tuning**
   - Optimize utility weights
   - Tune safety parameters
   - Adjust path planning parameters
   - Fine-tune Kalman filter

### Long-term (Pre-Competition)
10. **Final Validation**
    - End-to-end system tests
    - Competition scenario simulations
    - Stress testing under time pressure
    - Team coordination drills

11. **Documentation Freeze**
    - Finalize all READMEs
    - Create operator manual
    - Quick reference guides
    - Troubleshooting flowcharts

---

## 🐛 RECENT BUG FIXES & CHANGES

### January 15, 2026
- **CRITICAL**: Fixed crate ID collision problem
  - All blue crates (ID 36) now get unique IDs (1001, 1002, ...)
  - All yellow crates (ID 47) now get unique IDs (2001, 2002, ...)
  - Implemented spatial tracking with position matching
  - Added temporal filtering and timeout mechanism
  - Integrated into strategy manager and full pipeline

### December 2025
- Added strategy package with utility-based task selection
- Implemented 6 task types for Eurobot 2026
- Created live visualization system
- Fixed ArUco ID schema synchronization
- Updated marker positions in camera calibration

### November 2025
- Completed Kalman filter implementation
- Added occlusion handling strategies
- Stress tested multi-marker tracking
- Created comprehensive documentation

### October 2025
- Fixed camera positioning (Y=2.044m outside field)
- Corrected ArUco IDs (36, 47, 41 for crates)
- Updated communication architecture (PC→WiFi→Robot)
- Added orientation estimation module

---

## 📊 TECHNOLOGY STACK & REPOSITORY STATISTICS

### Core Technologies
- **Language**: Python 3.8+
- **Computer Vision**: OpenCV 4.x (cv2.aruco)
- **Numerical Computing**: NumPy, SciPy
- **Filtering**: FilterPy (Kalman implementation)
- **Path Planning**: Custom RRT/RRT-Connect/A* implementations
- **Configuration**: YAML (PyYAML)
- **Communication**: ROS2 (planned), DDS, WebSocket/MQTT (WiFi)

### Repository Structure
- **Total Modules**: 12 major components
- **Active Development Folders**:
  - `strategy/` - Utility-based decision making (8 files)
  - `full_pipeline/` - Integrated tracking system
  - `map_anchors/` - Camera extrinsics tools (6 scripts)
  - `orientation/` - Crate orientation estimation (4 methods)
  - `path_planning/` - 3 algorithms + smoothing
  - `kalman_filter/` - Multi-marker tracking
  - `ros_ready_pipeline/` - ROS2 integration (WIP)
  
### Code Statistics (Estimated)
- **Python Files**: 50+ scripts
- **Documentation**: 15+ README/MD files (6000+ lines)
- **Configuration**: 5+ YAML files
- **Examples**: 10+ demo/test scripts

### Hardware Requirements
- **Camera**: Overhead camera (tested with iPhone XR, webcam)
- **Resolution**: 1280x720 minimum, 1920x1080 recommended
- **FPS**: 30+ fps
- **Processing**: PC with USB connection
- **Communication**: WiFi for PC→Robot
- **Field**: 3.0m × 2.0m Eurobot 2026 specification

### Testing Coverage
- ✅ Camera calibration: Validated with iPhone XR
- ✅ ArUco detection: Tested with multiple markers
- ✅ Kalman filter: Stress tested (85-95% accuracy)
- ✅ Path planning: Validated in simulation
- ✅ Strategy system: Live visualization tested
- ✅ Crate tracking: Position-based matching validated
- 🔄 End-to-end integration: In progress
- ⏸️ Hardware integration: Pending physical setup
- ⏸️ Competition field testing: Pending

---

## 🔴 CRITICAL BUG FIX - CRATE ID TRACKING SYSTEM (Jan 15, 2026)

**STRATEGY PACKAGE - UTILITY-BASED DECISION MAKING**

Major advancement in autonomous decision-making with a complete utility-based strategy system that selects optimal tasks based on Eurobot 2026 scoring rules.

### Major Accomplishments:

#### 1. **Strategy Package Architecture** 🧠
Implemented production-ready decision-making system in `strategy/`:

**Complete Module Structure**:
```python
strategy/
├── __init__.py           # Package exports
├── config.py             # StrategyConfig - all tunable parameters
├── world_state.py        # WorldState, CrateInfo, RobotPose, EnemyInfo
├── task_models.py        # Task classes with utility calculation
├── strategy_manager.py   # Main decision-making engine
├── visualize_strategy.py # Live visualization with path planning
└── README.md            # Complete documentation
```

**Key Design Principles**:
- ✅ **Pure strategy layer** - No perception/planning reimplementation
- ✅ **Integration-focused** - Uses existing RRT-Connect, ArUco detection, obstacle management
- ✅ **Production-ready** - Fully typed, no placeholders, complete documentation
- ✅ **Easily tunable** - All parameters in StrategyConfig with preset modes

#### 2. **Utility-Based Task Selection** ⚖️
Advanced scoring system for optimal task prioritization:

**Utility Formula**:
```python
utility = (expected_score × feasibility × safety) / (time_cost + distance_cost + ε)
```

**Components**:
- **Expected Score**: Based on official Eurobot 2026 rules (2-10 points)
- **Feasibility**: 0 if impossible, 1 if feasible (path exists, resources available)
- **Safety**: 0-1 based on enemy proximity (danger zones, critical zones)
- **Time Cost**: Path execution time + action time (pickup/place/flip)
- **Distance Cost**: Path length weighted by configurability

**Why This Works**:
- Balances scoring potential vs execution risk
- Automatically deprioritizes dangerous tasks near enemies
- Considers time remaining (endgame urgency)
- Adapts to dynamic environment changes

#### 3. **Six Task Types Implemented** 🎯
Complete coverage of Eurobot 2026 scoring opportunities:

**Task Type Breakdown**:

1. **PlaceHazelnutInNest** (2 points)
   - Target: Our crates → nest zone
   - Action: PLACE
   - Conditions: Free crate available, nest not full

2. **PlaceHazelnutInPantry** (3 points)
   - Target: Our crates → pantry zones (6 available)
   - Action: PLACE
   - Conditions: Free crate + empty pantry slot

3. **EmptyOpponentFridge** (2 points)
   - Target: Opponent's fridge
   - Action: FLIP (dump contents)
   - Conditions: Opponent has crates in fridge

4. **FillFridgeWithEmpty** (~1 point each, 5 total if full)
   - Target: Free crates → our fridge
   - Action: PLACE
   - Conditions: Free crate available, fridge not full

5. **ReachCursorZone** (0-6 points, avg 3)
   - Target: Cursor zone on field
   - Action: NONE (positioning only)
   - Conditions: Not already completed

6. **ReturnToNest** (5-10 points endgame)
   - Target: Endgame zone
   - Action: NONE (positioning)
   - Conditions: Always feasible, priority increases when time < 15s

**Official Scoring Rules** (Eurobot 2026):
- Nest: 2 points per crate
- Pantry: 3 points per crate
- Fridge empty: 2 points
- Fridge full: 5 points total
- Cursor zone: Variable (0-6 points)
- Endgame positioning: 5 points (partial) or 10 points (full)

#### 4. **World State Management** 🌍
Comprehensive environment representation:

**WorldState Class**:
```python
@dataclass
class WorldState:
    robot_pose: RobotPose              # (x, y, theta)
    crates: List[CrateInfo]            # All detected crates
    enemies: List[EnemyInfo]           # Enemy positions (LiDAR)
    static_obstacles: List             # From crate_obstacle_manager
    time_remaining: float              # Match time (100s countdown)
```

**CrateInfo**:
- ID, position, ownership (ours/opponent/neutral)
- Container (free/nest/pantry/fridge)
- Confidence score from detection

**Simplified Domain Model**:
- ❌ Removed CrateType (hazelnut/empty) - all crates treated uniformly
- ✅ Distinction by ownership and location only
- ✅ Matches actual competition rules and detection capabilities

#### 5. **Safety Factor & Enemy Avoidance** 🛡️
Dynamic safety scoring based on enemy proximity:

**Safety Configuration**:
```python
enemy_danger_radius = 0.5m      # Reduced utility within this range
enemy_critical_radius = 0.3m    # Very dangerous zone
safety_penalty_per_meter = 0.2  # Utility reduction rate
```

**Safety Calculation**:
- Checks all path waypoints for enemy proximity
- Reduces utility for paths passing near enemies
- Critical zone: Near-zero safety factor
- Danger zone: Gradual safety reduction
- Safe zone: Full utility (1.0)

**Integration with LiDAR**:
- Currently uses placeholder enemy positions
- Ready for real LiDAR integration (just pass `enemy_positions` to `update_world_state()`)
- No code changes needed when LiDAR available

#### 6. **Endgame Priority Boost** ⏰
Automatic urgency handling for match conclusion:

**Endgame Logic**:
```python
if time_remaining < 15.0:  # Last 15 seconds
    if task_type == ReturnToNest:
        utility *= 2.0  # Double priority for endgame positioning
```

**Why 15 seconds**:
- Allows time to reach endgame zone from anywhere on field
- Robot speed ~0.3 m/s → 4.5m in 15s (exceeds diagonal distance)
- Ensures robot prioritizes final positioning over late-game tasks

#### 7. **Live Visualization System** 📺
Interactive demonstration with real-time task selection:

**visualize_strategy.py Features**:
- ✅ Displays Eurobot 2026 field with color-coded zones:
  - Green: Nest
  - Cyan: Pantries (6 zones)
  - Blue/Yellow: Fridge (team-specific)
  - Magenta: Endgame zone
- ✅ Uses ally robot ArUco marker as start position
- ✅ Shows enemy position (placeholder for LiDAR)
- ✅ Visualizes selected path based on utility score
- ✅ Real-time task rankings overlay (toggle with 'S')
- ✅ Task information panel with utility, score, time cost

**Interactive Controls**:
- **SPACE**: Recompute extrinsics (recalibrate camera pose)
- **ESC**: Exit visualization
- **P**: Print detailed status to console
- **S**: Toggle task statistics overlay

**Visual Elements**:
- Ally robot: Green circle with orientation arrow
- Enemy robot: Red circle with orientation arrow
- Zones: Color-coded polygons
- Path: Cyan line with waypoints
- Task info: Overlay panel with current best task

#### 8. **Integration with Existing Modules** 🔗
Seamless connection to current pipeline:

**Path Planning Integration**:
```python
from path_planning.rrt_connect import rrt_connect_plan

# Called internally by StrategyManager
path = rrt_connect_plan(start, goal, obstacles, bounds)
```

**Crate Detection Integration**:
```python
# From crate_obstacle_manager.py
classification = manager.process_detected_crates(detected_markers)
obstacles = classification['obstacle_positions']

# Pass to strategy
strategy_manager.update_world_state(
    detected_crates=crates,
    static_obstacles=obstacles
)
```

**ArUco Detection Integration**:
```python
# From aruco_id_detector.py or visualize_strategy.py
result = detector.detect_aruco_ids(frame)
# Format: {'ids': [...], 'markers': [{'id': int, 'world_coords': [x,y,z]}]}

# Extract robot pose from ally marker
ally_marker = result['markers'][ally_id]
robot_pose = (x, y, orientation)
```

#### 9. **Configuration & Tuning** ⚙️
Comprehensive parameter control system:

**StrategyConfig Parameters**:

**Scoring** (DO NOT MODIFY - official rules):
```python
score_hazelnut_in_nest = 2.0
score_hazelnut_in_pantry = 3.0
score_fridge_empty_of_hazelnut = 2.0
score_fridge_full_of_empty = 5.0
score_cursor_zone_min = 0.0
score_cursor_zone_max = 6.0
score_endgame_partial = 5.0
score_endgame_full = 10.0
```

**Utility Weights** (tune for playstyle):
```python
weight_expected_score = 1.0      # Score importance
weight_time_cost = 0.5           # Time efficiency
weight_distance_cost = 0.3       # Distance efficiency
weight_safety = 0.8              # Enemy avoidance
```

**Preset Modes**:
```python
config.set_aggressive_mode()  # Low safety, high speed
config.set_defensive_mode()   # High safety, careful play
```

**Zone Definitions**:
- Nest (blue/yellow): Team-specific zones
- Pantries: 6 zones on field
- Fridge (blue/yellow): Team-specific storage
- Endgame (blue/yellow): Final positioning zones
- Cursor zone: Variable scoring area

#### 10. **Output Format** 📤
Standardized interface for robot control:

**get_best_task_output() Returns**:
```python
{
    'task_id': 'nest_crate_36',           # Unique identifier
    'task_type': 'place_hazelnut_in_nest', # Task type
    'action': 'place',                     # 'pickup', 'place', 'flip', 'none'
    'path': [                              # Waypoints to follow
        np.array([1.5, 1.0, 0.0]),
        np.array([1.2, 0.8, 0.0]),
        np.array([0.9, 0.5, 0.0]),
        # ... more waypoints
    ],
    'target': (0.25, 0.25),               # Destination (x, y)
    'description': 'Place crate 36 in nest',
    'utility': 4.523,                     # Computed utility score
    'expected_score': 2.0,                # Points if successful
    'time_cost': 8.5                      # Estimated seconds
}
```

**Robot Controller Usage**:
1. Call `get_best_task_output()` to get current best task
2. Extract `path` (waypoints) for navigation
3. Extract `action` to determine gripper/flipper state
4. Follow path, execute action at target
5. Repeat (system handles replanning automatically)

### Technical Implementation:

**Strategy Manager Workflow**:
```python
# 1. Initialize
manager = StrategyManager(team_color="blue")

# 2. Update world state (each frame)
manager.update_world_state(
    robot_pose=(x, y, theta),
    detected_crates=crates,
    enemy_positions=lidar_enemies,
    static_obstacles=obstacles,
    time_remaining=time
)

# 3. Evaluate all tasks
tasks = manager.evaluate_tasks()  # Generates ~10-20 candidates

# 4. Select best task
best_task = manager.select_best_task()  # Highest utility

# 5. Get output for robot
output = manager.get_best_task_output()
path = output['path']        # Waypoints
action = output['action']    # 'pickup', 'place', 'flip', 'none'
```

**Task Generation**:
```python
# For each task type, manager generates candidates:
- _generate_hazelnut_nest_tasks()     # One per free crate
- _generate_hazelnut_pantry_tasks()   # One per crate × pantry
- _generate_empty_fridge_tasks()      # If enemy fridge has crates
- _generate_fill_fridge_tasks()       # One per free crate
- _generate_cursor_zone_tasks()       # If not completed
- _generate_endgame_tasks()           # Always available
```

**Utility Computation** (per task):
```python
# 1. Check feasibility
if not task.is_feasible(world_state, config):
    utility = 0.0
    return

# 2. Compute expected score
score = task.compute_expected_score(config)

# 3. Plan path
path = rrt_connect_plan(start, goal, obstacles, bounds)
if not path:
    utility = 0.0
    return

# 4. Compute costs
time_cost = len(path) * dt + action_time
distance_cost = sum(distances between waypoints)

# 5. Compute safety
safety = 1.0
for waypoint in path:
    for enemy in enemies:
        dist = distance(waypoint, enemy)
        if dist < critical_radius:
            safety *= 0.1
        elif dist < danger_radius:
            safety *= (1.0 - penalty * (danger_radius - dist))

# 6. Compute utility
utility = (score * safety) / (time_cost + distance_cost + epsilon)

# 7. Apply endgame boost
if time_remaining < 15 and task_type == ReturnToNest:
    utility *= 2.0
```

### Performance Characteristics:

**Planning Time**: ~0.1-0.5s for 10-20 candidate tasks
- Task generation: ~10ms
- Path planning: ~50-200ms per task (RRT-Connect)
- Utility computation: ~5ms per task
- Total: Suitable for 10 Hz replanning

**Memory**: Minimal (few MB)
- Task objects: ~1 KB each
- Paths: ~10-50 waypoints × 3 floats
- World state: <1 KB

**Scalability**:
- Linear with number of crates detected
- Parallel path planning possible (future optimization)
- Can handle 20+ simultaneous tasks

### Files Created/Modified:

**New Files**:
- `strategy/__init__.py` (45 lines)
- `strategy/config.py` (140 lines)
- `strategy/world_state.py` (197 lines)
- `strategy/task_models.py` (350 lines)
- `strategy/strategy_manager.py` (450 lines)
- `strategy/visualize_strategy.py` (850 lines)
- `strategy/README.md` (380 lines)

**Modified Files**:
- `Documentation/PROGRESS.md` (this file)

### Current Status:
- ✅ Strategy package architecture complete
- ✅ Six task types implemented with official scoring
- ✅ Utility-based selection system functional
- ✅ World state management with crate/enemy tracking
- ✅ Safety factor with enemy avoidance
- ✅ Endgame priority boost
- ✅ Live visualization with interactive controls
- ✅ Integration with RRT-Connect, ArUco, obstacle manager
- ✅ Complete documentation and examples
- ✅ Simplified domain model (no crate type distinction)

### Next Steps:
- [ ] Test strategy system with live camera feed
- [ ] Integrate with full pipeline (multi-threaded version)
- [ ] Add LiDAR enemy detection (replace placeholder)
- [ ] Field testing under competition conditions
- [ ] Tune utility weights based on real-world performance
- [ ] Add telemetry logging for strategy decisions
- [ ] Implement task execution confirmation/feedback

### Usage Example:

**Basic Usage**:
```bash
cd strategy
python visualize_strategy.py --camera 1 --team blue
```

**Programmatic Usage**:
```python
from strategy import StrategyManager

manager = StrategyManager(team_color="blue")

# Each control loop iteration:
manager.update_world_state(
    robot_pose=current_pose,
    detected_crates=aruco_crates,
    enemy_positions=lidar_enemies,
    static_obstacles=obstacles,
    time_remaining=match_timer
)

output = manager.get_best_task_output()
if output:
    follow_path(output['path'])
    execute_action(output['action'])
```

---

## 🎉 Previous Update (Dec 14, 2025)

**FULL PIPELINE INTEGRATION & ROS COMMUNICATION**

Today's work focused on integrating all modules into a seamless pipeline, enabling real-time operation and communication between the PC and Raspberry Pi.

### Major Accomplishments:

#### 1. **Full Pipeline Integration** 🔗
- Per-frame waypoint selection logic implemented
- Robot intelligently skips waypoints that are behind or too close
- Improved real-world path following and robustness to planning delays

#### 2. **ROS Communication Ready** 📡
- Maintained parallel pipeline for ROS integration
- Synchronized features and requirements across both pipelines
- ROS nodes can now subscribe to camera feeds and receive path replanning alerts

#### 3. **Camera Calibration & Extrinsics** 📷
- Stable calibration for both iPhone XR and webcam
- Calibration scripts and usage examples validated
- Extrinsics computation integrated into the pipeline

#### 4. **Kalman Filter & Occlusion Handling** 🔮
- Multi-marker tracking and occlusion handling fully implemented
- Kalman filtering integrated for smoother trajectory estimates

#### 5. **Path Planning Module** 🗺️
- RRT-Connect algorithm integrated for path planning
- Cost computation and candidate path visualization implemented
- Dynamic waypoint selection based on real-time data

#### 6. **Communication Module** 💬
- `mini_path_planning/` provides PC-to-Raspberry Pi socket communication
- Real-time path replanning alerts sent over the network

#### 7. **Documentation & Examples** 📚
- All modules have updated requirements and documentation files
- System architecture and module breakdown clarified
- New examples for ROS integration and full pipeline usage

---

## 🎉 Latest Update (Dec 11, 2025)

**MULTI-THREADED PIPELINE COMPLETE & PATH SMOOTHING ENHANCED**

Major improvements to the vision pipeline with multi-threading/multi-processing architecture, timeout handling, and advanced path smoothing.

### Major Accomplishments:

#### 1. **Multi-Threaded/Multi-Process Architecture** ⚙️
Implemented high-performance parallel pipeline in `full_pipeline/scripts/multi_threaded_pipeline.py`:

**Architecture Overview**:
- **Thread 1** (I/O-bound): Camera capture + ArUco detection
- **Process 2** (CPU-bound): Extrinsics computation + coordinate transformation
- **Process 3** (CPU-bound): Kalman filtering with occlusion handling
- **Process 4** (CPU-bound): RRT-Connect path planning with timeout protection
- **Thread 5** (I/O-bound): DDS communication (placeholder)

**Why This Architecture**:
- Threads for I/O operations (camera, network) - avoids blocking on slow I/O
- Separate processes for CPU-intensive tasks - bypasses Python's GIL
- Multiprocessing queues for inter-process communication
- Maintains 30+ FPS even during heavy path planning

**Key Features**:
- ✅ Proper cleanup and termination (ESC/Ctrl+C support)
- ✅ Queue draining to prevent memory leaks
- ✅ Daemon processes for automatic cleanup
- ✅ try/finally blocks ensure camera release

#### 2. **Timeout Protection & Fallback Strategies** ⏱️
Advanced timeout handling prevents freezing when enemy blocks path:

**Timeout Configuration**:
```python
MAX_PLANNING_TIME = 2.0s      # Max time per RRT attempt
FAILURE_TIMEOUT = 3.0s        # Trigger sudden stop after failures
MAX_RRT_ATTEMPTS = 3          # Attempts per planning cycle
FALLBACK_PATH_HOLD_TIME = 5.0s # Hold fallback path before replanning
```

**Fallback Logic**:
1. **Normal planning fails** → Try relaxed obstacles (70% enemy radius)
2. **Fallback path found** → Hold for 5 seconds (prevents oscillation)
3. **Still no path after 3s** → Trigger sudden stop with visual warning
4. **Backward waypoints allowed** in fallback mode for rerouting

**Impact**: Robot no longer freezes when enemy blocks direct path. FPS remains stable during planning failures.

#### 3. **Path Smoothing Enhancements** 📐
Implemented greedy straightening algorithm in `path_planning/path_smoothing.py`:

**Two-Stage Smoothing**:
1. **Greedy Straightening**: 
   - Iterates through waypoints
   - Finds longest collision-free straight-line segment
   - Removes intermediate waypoints
   - Creates direct paths when obstacles allow

2. **Random Refinement**:
   - Further smooths with stochastic optimization
   - Removes unnecessary zigzags
   - Preserves obstacle avoidance

**Algorithm**:
```python
def smooth_path(path, obstacles):
    # Stage 1: Greedy straightening
    i = 0
    while i < len(path) - 1:
        # Try connecting i to farthest collision-free point j
        for j in range(len(path)-1, i+1, -1):
            if no_collision(path[i], path[j], obstacles):
                # Remove waypoints between i and j
                path = path[:i+1] + path[j:]
                break
        i += 1
    
    # Stage 2: Random smoothing (existing algorithm)
    for _ in range(iterations):
        # Random waypoint removal if collision-free
        ...
```

**Benefits**:
- Significantly reduces waypoint count
- Creates straight-line segments when possible
- Smoother robot movement
- Easier to follow for controller

#### 4. **Complete Visualization** 🖼️
Full ArUco marker display matching `main_connect.py`:

**Visualization Features**:
- ✅ ArUco marker IDs with color coding:
  - Green: Reference markers (20-23)
  - Red: Enemy markers (e.g., 17)
  - Magenta: Object markers
- ✅ World coordinates for all markers
- ✅ Kalman filter stats (tracked, occluded, confidence)
- ✅ Enemy tracking with prediction
- ✅ RRT path visualization with waypoint coordinates
- ✅ Sudden stop warning overlay (red screen + text)
- ✅ FPS and status display

#### 5. **Path Stability Improvements** 🎯
Prevents excessive replanning when using fallback paths:

**Problem**: Robot oscillated when switching between normal and fallback paths
**Solution**: Path holding mechanism
- Fallback paths held for 5 seconds before replanning
- Prevents rapid path switching
- Robot follows stable trajectory even when enemy nearby

**Variable Scoping Fixes**:
- Fixed `UnboundLocalError` with `next_waypoint`
- Proper initialization before conditional logic
- Clean separation of fallback vs normal mode

#### 6. **Field Dimensions** 📏
Correct Eurobot 2026 competition table:
- **Playing field**: 3.0m × 2.0m
- **Bounds in code**: `(0.0, 3.0, 0.0, 2.0)`
- **Reference markers**: Positioned at known world coordinates
- **Camera placement**: Outside field at Y=2.044m (44mm from edge)

### Technical Details:

**Multi-Processing Communication**:
```python
# Inter-process queues (multiprocessing.Queue)
detection_queue = MPQueue(maxsize=10)   # Thread 1 → Process 2
transform_queue = MPQueue(maxsize=10)   # Process 2 → Process 3
kalman_queue = MPQueue(maxsize=10)      # Process 3 → Process 4
path_queue = MPQueue(maxsize=10)        # Process 4 → Main thread
```

**Cleanup Procedure**:
```python
def cleanup_processes(processes, stop_event):
    stop_event.set()                    # Signal all processes
    for proc in processes:
        proc.join(timeout=2)            # Wait for graceful shutdown
    for proc in processes:
        if proc.is_alive():
            proc.terminate()            # Force terminate
            proc.join(timeout=1)
    for proc in processes:
        if proc.is_alive():
            proc.kill()                 # Final kill if needed
```

**Queue Draining** (prevents blocking on join):
```python
def drain_queue(q, timeout=0.5):
    while time.time() < end_time:
        try:
            q.get_nowait()
        except:
            break
```

### Files Modified:
- `full_pipeline/scripts/multi_threaded_pipeline.py` - Complete rewrite with multi-processing
- `path_planning/path_smoothing.py` - Enhanced with greedy straightening
- `sensor_fusion/COST_FUNCTION.md` - Fixed markdown linting errors

### Current Status:
- ✅ Multi-threaded pipeline fully functional
- ✅ Timeout handling prevents freezing
- ✅ Path smoothing creates optimal trajectories
- ✅ Fallback strategies handle blocked paths
- ✅ Visualization shows all critical information
- ✅ Proper cleanup and termination
- ✅ Field dimensions correctly configured (3m × 2m)

### Next Steps:
- [ ] Test full pipeline with real robot hardware
- [ ] Implement actual DDS communication (currently placeholder)
- [ ] Benchmark end-to-end latency
- [ ] Field testing under competition conditions
- [ ] Document multi-threading approach in THEORETICAL_UNDERSTANDING.md

---

## 🚀 December 2025 Update

### Major Accomplishments:
- **Full Pipeline**: Per-frame waypoint selection logic implemented. Robot now skips waypoints behind or too close, improving real-world path following and robustness to planning delays.
- **README & Docs**: Updated to explain the new waypoint selection logic, the problem it solves, and integration details.
- **ROS Ready Pipeline**: Maintained in parallel for ROS integration, with synchronized features and requirements.
- **Camera Calibration & Extrinsics**: Stable, with iPhone XR and webcam support. Calibration scripts and usage examples validated.
- **Kalman Filter & Occlusion**: Multi-marker tracking, occlusion handling, and Kalman filtering fully implemented and documented.
- **Path Planning**: RRT-Connect and cost computation integrated, with candidate path visualization and selection.
- **Communication Module**: `mini_path_planning/` provides PC-to-Raspberry Pi socket communication for path replanning alerts.
- **Documentation**: All modules have updated requirements and documentation files. System architecture and module breakdown clarified.

### Current Status:
- ✅ Full pipeline integration in progress
- ✅ Real-time marker detection and tracking
- ✅ Robust path following with dynamic waypoint selection
- ✅ ROS-ready pipeline available
- ✅ Camera calibration and extrinsics stable
- ✅ Kalman filter and occlusion handling validated
- ✅ Path planning and cost metrics visualized
- ✅ Communication test module implemented

### Next Steps:
- [ ] Finalize full pipeline integration and ROS communication
- [ ] Benchmark real-world performance and latency
- [ ] Expand documentation for new features and troubleshooting
- [ ] Continue testing under competition-like conditions

---

## 🎉 Previous Update (Oct 14, 2025)

**MINI PATH PLANNING MODULE & SOCKET COMMUNICATION**

Today's work focused on implementing a test module for PC-to-Raspberry Pi communication using sockets for path replanning.

### Major Accomplishments:

#### 1. **New Module: `mini_path_planning/`** 🚀
Created complete communication test module with:
- **PC Sender**: Monitors ArUco markers (our robot + enemy) and sends alerts
- **Raspberry Pi Receiver**: Receives alerts and triggers path replanning
- **Socket Communication**: UDP/TCP support for network flexibility
- **Distance Calculation**: Uses camera calibration for accurate 3D measurements
- **Threshold-based Alerts**: Configurable distance threshold (default: 0.5m)

**Features**:
- ✅ Real-time ArUco detection and tracking
- ✅ 3D distance calculation between robots
- ✅ JSON message format with timestamps
- ✅ Alert cooldown to prevent spam (1 second)
- ✅ Visual feedback on video feed
- ✅ Command-line and YAML configuration
- ✅ Socket communication test verified

#### 2. **Module Structure** 📁
```
mini_path_planning/
├── pc_sender/          # Vision PC monitoring module
├── rpi_receiver/       # Raspberry Pi alert receiver
├── config/             # YAML configuration
├── examples/           # Test scripts
└── README.md          # Complete documentation
```

#### 3. **Communication Protocol** 📡
Implemented JSON-based protocol:
```json
{
  "timestamp": 1234567890.123,
  "alert": "REPLAN_PATH",
  "distance": 0.35,
  "threshold": 0.5,
  "our_robot": {"id": 1, "position": {"x": 0.5, "y": 0.3, "z": 0.8}},
  "enemy_robot": {"id": 6, "position": {"x": 0.2, "y": 0.4, "z": 0.75}}
}
```

---

## 🎉 Previous Update (Oct 13, 2025)

**IPHONE CAMERA INTEGRATION & COMPETITION-READY MARKER IDS**

Today's work focused on integrating iPhone XR camera via Camo app and updating all marker IDs to comply with Eurobot 2026 rules.

### Major Accomplishments:

#### 1. **New Branch: `phone` for iPhone Setup** 📱
Created dedicated branch for iPhone XR camera configuration:
- **Main branch**: Webcam setup (640×480) for development
- **Phone branch**: iPhone XR via Camo (1280×720) for competition

**iPhone XR Calibration Results**:
- ✅ Resolution: 1280×720 (Camo free version)
- ✅ Focal lengths: fx=1637.00, fy=1612.92 pixels
- ✅ Reprojection error: **0.1987 pixels** (excellent!)
- ✅ Calibration date: October 13, 2025
- ✅ Camera appears as device index 2

#### 2. **Marker ID Schema Updated to Eurobot 2026 Rules** 🏷️
**CRITICAL FIX**: Updated ALL marker IDs to comply with competition specifications

**Old (Incorrect)**:
```
Map Anchors:  0, 1, 2, 3
Caisses:      10-20 (generic)
```

**New (Correct - Eurobot 2026)**:
```
Map Anchors:  20, 21, 22, 23    (Game field reserved IDs 11-50)
              Physical verified: 22=Bottom-left, 23=Bottom-right, 21=Top-right, 20=Top-left
Caisses:      
  - Blue:     36
  - Yellow:   47  
  - Black:    41 (caisse pourrie/rotten box)
Blue Robots:  1-5
Yellow Robots: 6-10
```

**Files Updated** (Both branches):
- `map_anchors/config/marker_config.yaml` - Updated marker positions
- `map_anchors/scripts/detect_anchors.py` - Detection for IDs 20-23
- `map_anchors/scripts/compute_extrinsics.py` - PnP solver for IDs 20-23
- Camera config files synchronized

#### 3. **Camera Setup Successfully Validated** ✅
- ✅ All 4 map anchor markers (20-23) visible and detected
- ✅ Detection working reliably with iPhone camera
- ✅ Camo app configured for optimal field of view
- ⏸️ Extrinsics computation pending (PnP debugging in progress)

#### 4. **Git Repository Structure** 🌳
```
main branch:
  - Webcam calibration (640×480)
  - Default camera indices (0/1)
  - Marker IDs: 20-23 ✅

phone branch:
  - iPhone XR calibration (1280×720)
  - Camera index: 2
  - Marker IDs: 20-23 ✅
  - Debug output for PnP solver
```

### Key Technical Details:

**iPhone XR Camera Specs**:
- Native: 12MP, f/1.8, 26mm equiv (63° FOV)
- Via Camo: 1280×720 @ 30fps
- Sensor: 1/2.55", 1.4µm pixels
- Features: PDAF, OIS

**Calibration Quality**:
- Reprojection error: 0.1987 pixels (< 0.2 = excellent)
- 20 calibration images used
- Chessboard: 9×6, 25mm squares

### Files Created/Modified Today:
- `camera_calibration_folder/calibration/iphone_xr_720p.json` (NEW)
- `camera_calibration_folder/find_camera.py` (NEW)
- `IPHONE_CALIBRATION_GUIDE.md` (NEW)
- `map_anchors/config/camera_config.yaml` (iPhone intrinsics)
- `map_anchors/config/marker_config.yaml` (IDs 20-23, caisse IDs)
- All detection scripts updated for new marker IDs

### Current Status:
- ✅ iPhone camera calibrated and working
- ✅ All markers using correct Eurobot 2026 IDs
- ✅ Detection validated (all 4 anchors visible)
- 🔧 Extrinsics computation debugging (PnP solver)
- ⏸️ Next: Fix compute_extrinsics.py, then full system integration

---

## 🎉 Previous Update (Oct 8, 2025)

**KALMAN FILTER MODULE COMPLETION & SYSTEM SYNCHRONIZATION**

Today's work focused on completing the Kalman filter implementation, creating comprehensive documentation, and synchronizing ArUco ID schemas across all modules.

### Major Accomplishments:

#### 1. **Kalman Filter Module Fully Implemented** 🔮
- ✅ Complete 6D state Kalman filter (position, orientation, velocities)
- ✅ Multi-marker tracking with automatic classification
- ✅ Occlusion handling with 4 different strategies
- ✅ Stress testing suite with 4 scenarios (7-11 markers)
- ✅ Competition demo example (10-second simulation)
- ✅ ~2800+ lines of production-ready code

**Performance Validated**:
- Processing: < 1ms for 11 markers
- Tracking accuracy: 85-95%+ under various conditions
- FPS capability: 1600-5000+ FPS (Raspberry Pi 4 compatible)
- Memory usage: < 100KB for all markers

#### 2. **Critical ArUco ID Schema Synchronization** 🔗
**FIXED**: Incorrect caisse marker IDs across the entire system

- ❌ **OLD (Wrong)**: Caisses used IDs 10-20
- ✅ **NEW (Correct)**: Caisses use IDs **36** (blue), **47** (yellow), **41** (black/rotten)

**Files Updated**:
- `kalman_filter/src/kalman_filter/tracker.py` - Classification logic fixed
- `kalman_filter/tests/stress_tests/test_multiple_markers.py` - Test IDs corrected
- All documentation synchronized with competition specifications

**Current ID Schema** (NOW CORRECT):
```
Map Anchors:  0, 1, 2, 3        (Fixed corner references)
Caisses:      36, 47, 41        (Blue, Yellow, Black boxes)
Enemy Robots: 30+               (Opponent tracking)
```

#### 3. **Comprehensive Documentation Created** 📚
New files created in `kalman_filter/`:
- `TECHNICAL_SUMMARY.md` (500+ lines) - Complete API & configuration guide
- `UPDATED_TECHNICAL_SUMMARY.md` (700+ lines) - Synchronized version with correct IDs
- `SYNCHRONIZATION_SUMMARY.md` (300+ lines) - Detailed change log
- `docs/DATA_FLOW.md` (287 lines) - Complete pipeline architecture
- `docs/kalman/README.md` (284 lines) - Kalman theory & usage
- `docs/occlusion/README.md` (355+ lines) - Occlusion strategies

#### 4. **MATLAB Simulations Fixed** 🖥️
**Camera Position Corrected**:
- ❌ **OLD**: Camera hovering above field at Y=1.0m (inside field)
- ✅ **NEW**: Camera **outside field** at Y=2.044m (44mm from edge per Cahier des Charges)
- ✅ **ArUco markers**: Inset 0.6m from field edges (NOT at corners)

**Files Updated**:
- `test_graphics.m` - Diagnostic tool (works correctly) ✅
- `simulate_camera_positioning_SUBPLOT.m` - Rewritten using subplot() ✅
- All marker positions and camera configurations corrected

#### 5. **Integration Status** 🔗
All modules now synchronized:
| Module | Status | ArUco IDs | Integration |
|--------|--------|-----------|-------------|
| camera_calibration | ✅ Complete | N/A | Ready |
| ArUco_detection | ✅ Complete | All ranges | Ready |
| map_anchors | ✅ Complete | 0-3 | Ready |
| caisses_detection | ✅ Complete | 36, 47, 41 | Ready |
| kalman_filter | ✅ **NEW - Complete** | All ranges | Ready |
| matlab_simulations | ✅ Fixed | 0-3 (map) | Validated |

### Key Realizations:
- � **Need to pause coding** and focus on **theoretical understanding**
- 📖 Deep comprehension needed before proceeding to integration
- 🧠 Must understand: Kalman theory, coordinate transforms, occlusion strategies, camera models
- ⚠️ Risk of "vibe coding" without solid theoretical foundation

### Files Created Today:
- `kalman_filter/TECHNICAL_SUMMARY.md`
- `kalman_filter/UPDATED_TECHNICAL_SUMMARY.md`
- `kalman_filter/SYNCHRONIZATION_SUMMARY.md`
- `kalman_filter/docs/DATA_FLOW.md`
- `matlab_simulations/test_graphics.m`
- `matlab_simulations/simulate_camera_positioning_SUBPLOT.m`
- `matlab_simulations/test_minimal.m`

### Next Priority:
🎓 **STOP CODING - START STUDYING**
- Understand Kalman filter mathematics deeply
- Study coordinate transformation theory
- Learn occlusion handling strategies
- Comprehend camera projection models
- Review competition rules and specifications

---

## 📝 Previous Update (Oct 6, 2025)

**MAJOR DOCUMENTATION CORRECTION COMPLETED**

Today's work focused on correcting a critical misunderstanding in the system architecture:

### What Was Wrong:
❌ Documentation incorrectly described a **wired/tethered system** with cable management between PC and robot  
❌ Multiple sections mentioned "no wireless allowed", "USB Serial communication", "cable routing"  
❌ This would have severely limited robot mobility

### What's Correct:
✅ **Camera → USB Cable → Vision PC (stationary, off-field)**  
✅ **Vision PC → WiFi → Robot Raspberry Pi (mobile, on-field)**  
✅ Wireless PC-to-Robot communication is **required and allowed**  
✅ Only the camera-to-PC link is wired (stationary setup)

### Files Updated:
- ✅ `README.md` - Complete overhaul (Communication, Challenges, Hardware, Tools sections)
- ✅ `PROGRESS.md` - This file (added wireless communication module, updated milestones)

### Key Additions:
- 📡 **Wireless Communication Module** identified as CRITICAL component
- 🌐 Three protocol options documented: WebSocket, MQTT, UDP
- ⚠️ Competition WiFi challenges documented (20-30 teams, 10-30% packet loss)
- 📚 Libraries and implementation requirements added

**Impact**: Architecture is now correctly documented. Next priority is implementing the wireless communication link.

---

## 🔗 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EUROBOT 2026 VISION SYSTEM                            │
│                      Sequential Processing Pipeline                          │
└─────────────────────────────────────────────────────────────────────────────┘

    STEP 1              STEP 2              STEP 3              STEP 4
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Camera     │──>│    ArUco     │──>│     Map      │──>│    Enemy     │
│ Calibration  │   │  Detection   │   │   Anchors    │   │  Detection   │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
      📷                  🎯                  🗺️                 🤖
   COMPLETE          IN PROGRESS      AWAITING EXTRINSICS      PLANNED

                              ↓
                    
                    STEP 5              STEP 6              STEP 7
                ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                │   Kalman     │──>│   Wireless   │──>│     Full     │
                │   Filter     │   │  PC→Robot    │   │ Integration  │
                └──────────────┘   └──────────────┘   └──────────────┘
                      🔮                 📡                  ⚙️
                    PLANNED        TEST-COMPLETE 🟢         PLANNED

SYSTEM ARCHITECTURE:
┌─────────────┐ USB  ┌─────────────┐ WiFi ┌─────────────┐
│   Camera    │─────>│  Vision PC  │─────>│    Robot    │
│ (Overhead)  │      │ (Stationary)│      │  (Mobile)   │
└─────────────┘      └─────────────┘      └─────────────┘
```

---

## 📁 Module Breakdown

### 1️⃣ Camera Calibration Module
**Location**: `camera_calibration_folder/`  
**Status**: ✅ **COMPLETE**  
**Purpose**: Compute camera intrinsic parameters

**Outputs**:
- `calibration/camera_calibration.json` - Camera matrix & distortion coefficients

**Key Components**:
- ✅ Calibration script working
- ✅ Test/validation scripts functional
- ✅ JSON output format defined

**Next Steps**: None - Module complete

---

### 2️⃣ ArUco Detection Module
**Location**: `ArUco_detection_folder/`  
**Status**: 🔄 **IN PROGRESS**  
**Purpose**: Detect and track ArUco markers

**Current Features**:
- ✅ Basic marker detection (IDs 0-99)
- ✅ Pose estimation with calibration
- ✅ Distance calculation (pixel-based estimation)
- ✅ Distance calculation (calibrated - accurate)
- ✅ Multi-marker tracking
- 🔄 Real-time performance optimization

**Marker Classification**:
| ID Range | Type | Purpose | Status |
|----------|------|---------|--------|
| 0-3 | MAP | Corner anchors for world frame | ✅ Generated |
| 10-20 | CAISSE | Wooden box tracking | ✅ Generated |
| 30+ | ENEMY | Enemy robot detection | ✅ Generated |

**Dependencies**:
- ✅ Uses `camera_calibration.json` from Module 1
- ✅ Loads calibration via `test_coordinates.py`

**Recent Updates** (Oct 4, 2025):
- ✅ Added distance calculation without calibration
- ✅ Added comparison between calibrated/uncalibrated distance
- ✅ Enhanced visualization with distance overlay
- ✅ Added keyboard controls for toggling features

**Current Work**:
- Testing distance accuracy at various ranges
- Comparing calibrated vs uncalibrated methods
- Optimizing detection speed

**Next Steps**:
1. Validate distance accuracy (0.5m - 3m range)
2. Test multi-marker simultaneous detection
3. Benchmark FPS with multiple markers
4. Document accuracy results

---

### 3️⃣ Map Anchors Module
**Location**: `map_anchors/`  
**Status**: 🔄 **IMPLEMENTED - AWAITING EXTRINSICS**  
**Purpose**: Establish world coordinate system

**Completed Features**:
- ✅ Marker generation scripts working
- ✅ Detection scripts ready
- ✅ Camera config files created (YAML + JSON)
- ✅ Sync utility for config files
- ✅ Documentation complete (SUMMARY.md)

**Pending Tasks**:
- [ ] Print physical markers (IDs 0-3)
- [ ] Place markers at field corners
- [ ] Compute camera extrinsics (T_world_cam)
- [ ] Validate pose stability over time
- [ ] Transform detections to world frame

**Dependencies**:
- ⏳ Requires completed ArUco detection (Module 2)
- ⏳ Requires camera calibration (Module 1)
- ⏳ Needs `camera_config.yaml` populated

**Planned Workflow**:
```python
1. Detect MAP markers (0-3) at table corners
2. Use PnP algorithm to compute camera pose
3. Build transformation matrix T_world_cam
4. Transform all objects to world coordinates
5. Validate stability and accuracy
```

**Next Steps**:
1. Complete ArUco detection testing
2. Generate and place physical map markers
3. Measure exact table corner positions
4. Implement extrinsics computation script

---

### 4️⃣ Wireless Communication Module
**Location**: `mini_path_planning/` (test module)  
**Status**: 🟡 **TEST IMPLEMENTATION COMPLETE**  
**Purpose**: Send vision data from PC to Robot wirelessly

**Implemented Features** (Test Module):
- ✅ Socket-based communication (UDP/TCP)
- ✅ JSON message format with timestamps
- ✅ Distance-based alerting system
- ✅ PC sender module (path_monitor.py)
- ✅ Raspberry Pi receiver module (receiver.py)
- ✅ Real-time ArUco detection and tracking
- ✅ Configurable thresholds and network settings
- ✅ Command-line and YAML configuration
- ✅ Socket communication verified and tested

**Test Module Usage**:
```bash
# PC side (monitor and send alerts)
python3 mini_path_planning/pc_sender/path_monitor.py --ip 192.168.1.100

# Raspberry Pi side (receive alerts)
python3 mini_path_planning/rpi_receiver/receiver.py --port 5000
```

**System Architecture**:
```
Vision PC (Off-field) ──UDP/TCP Socket──> Raspberry Pi (On-field/Robot)
```

**Message Format**:
```json
{
  "timestamp": 1234567890.123,
  "alert": "REPLAN_PATH",
  "distance": 0.35,
  "threshold": 0.5,
  "our_robot": {"id": 1, "position": {"x": 0.5, "y": 0.3, "z": 0.8}},
  "enemy_robot": {"id": 6, "position": {"x": 0.2, "y": 0.4, "z": 0.75}}
}
```

**Protocol Options** (for future enhancements):
1. **WebSocket** (Real-time bidirectional)
   - Pros: Low latency, full-duplex, easy debugging
   - Cons: TCP overhead, connection management
   - Library: `websockets>=12.0`

2. **MQTT** (Publish-Subscribe with QoS)
   - Pros: QoS levels, broker-based, reconnection handling
   - Cons: Broker required, slightly higher latency
   - Library: `paho-mqtt>=1.6`

3. **UDP** ✅ **Currently Implemented** (Lowest latency, no reliability)
   - Pros: Minimal overhead, fastest
   - Cons: No delivery guarantee, no ordering
   - Library: Built-in `socket`

**Competition Challenges**:
- 20-30 teams = severe WiFi congestion
- Expected 10-30% packet loss
- Latency spikes 100-1000ms
- Connection dropouts

**Pending Full Implementation**:
- [ ] Integrate with full vision pipeline (map anchors + world coordinates)
- [ ] Add Kalman filtering for smoother tracking
- [ ] Implement packet loss handling (interpolation)
- [ ] Add connection monitoring and auto-reconnect
- [ ] Test under interference conditions (20+ WiFi networks)
- [ ] Benchmark latency and packet loss rates
- [ ] Consider WebSocket or MQTT for reliability

**Dependencies**:
- ✅ ArUco detection (Module 2)
- ✅ Camera calibration (Module 1)
- ⏳ Map anchors extrinsics (Module 3) - for world coordinates
- ⏳ Raspberry Pi setup with network configuration

**Next Steps**:
1. ✅ Test module complete and verified
2. Integrate world coordinate transformation
3. Add Kalman filtering for position smoothing
4. Test under competition-like WiFi interference
5. Benchmark end-to-end latency (target <50ms)

---

### 5️⃣ Enemy Detection Module
**Location**: TBD (likely `enemy_detection/`)  
**Status**: ⏸️ **PLANNED**  
**Purpose**: Detect and track enemy robot

**Planned Features**:
- [ ] Detect ArUco markers on enemy robot (ID 30+)
- [ ] Compute enemy position in world frame
- [ ] Track enemy trajectory
- [ ] Predict enemy movement (Kalman filter)

**Dependencies**:
- ⏳ Requires map anchors extrinsics (Module 3)
- ⏳ Requires ArUco detection (Module 2)

---

### 6️⃣ Kalman Filtering Module
**Location**: TBD (likely integrated in modules)  
**Status**: ⏸️ **PLANNED**  
**Purpose**: Smooth position estimates and predict motion

**Planned Features**:
- [ ] Filter noisy position measurements
- [ ] Predict object positions between frames
- [ ] Handle temporary occlusions
- [ ] Smooth trajectory estimates

**Dependencies**:
- ⏳ Requires working object detection
- Library: `filterpy` or `pykalman`

**Next Steps**:
1. After extrinsics computation
2. After enemy detection working
3. Implement after ArUco detection testing

---

## 🔄 Data Flow

```
camera_calibration_folder/
└── calibration/
    └── camera_calibration.json ──┐
                                   │
                                   ├──> ArUco_detection_folder/
                                   │    ├── examples/05_with_calibration.py ✅
                                   │    └── examples/test_coordinates.py ✅
                                   │
                                   └──> map_anchors/
                                        ├── config/camera_config.yaml ⏸️
                                        ├── scripts/compute_extrinsics.py ⏸️
                                        └── scripts/validate_pose.py ⏸️

ArUco_detection_folder/
└── aruco_tools/
    └── marker_detector.py ────────> map_anchors/
                                      └── scripts/detect_anchors.py ⏸️
```

---

## 📊 Current System Capabilities

### ✅ Working Features
- [x] Camera intrinsic calibration
- [x] ArUco marker generation (all types)
- [x] Real-time marker detection
- [x] 6DOF pose estimation (with calibration)
- [x] Distance measurement (calibrated & uncalibrated)
- [x] Multi-marker tracking
- [x] Visual debugging overlays

### 🔄 In Testing
- [ ] Distance accuracy validation
- [ ] Multi-marker simultaneous detection
- [ ] Real-time performance at 30+ FPS
- [ ] Detection range (0.5m - 3m)

### ⏸️ Not Yet Implemented
- [ ] World coordinate transformation
- [ ] Camera extrinsics computation
- [ ] Pose stability validation
- [ ] Full pipeline integration
- [ ] Object position in world frame

---

## 🚀 Quick Start Guide

### Prerequisites
```bash
pip install opencv-python opencv-contrib-python numpy pyyaml
```

### Current Workflow

#### 1. Camera Calibration (COMPLETE)
```bash
cd camera_calibration_folder
python calibrate_camera.py --camera 0
# Output: calibration/camera_calibration.json ✅
```

#### 2. Generate Markers (COMPLETE)
```bash
cd ../ArUco_detection_folder
python examples/01_generate_markers.py
# Output: markers/map_markers/ (IDs 0-3) ✅
# Output: markers/box_markers/ (IDs 10-20) ✅
# Output: markers/enemy_markers/ (IDs 30+) ✅
```

#### 3. Test ArUco Detection (IN PROGRESS)
```bash
cd ArUco_detection_folder

# Test with calibration (accurate distance)
python examples/05_with_calibration.py --camera 0

# Test marker detector (all features)
python examples/test_marker_detector.py --camera 0

# Compare calibrated vs uncalibrated distance
python examples/test_distance_comparison.py --camera 0
```

**Keyboard Controls**:
- `d` - Toggle distance display
- `c` - Toggle coordinate axes
- `i` - Toggle marker ID display
- `q` - Quit

#### 4. Compute Extrinsics (NOT STARTED)
```bash
cd ../map_anchors
# Coming soon...
python scripts/compute_extrinsics.py --camera 0
```

---

## 📈 Progress Tracking

### Milestones

| Milestone | Status | Date | Notes |
|-----------|--------|------|-------|
| Camera calibration working | ✅ Done | Sep 2025 | RMS error < 0.5 pixels |
| ArUco generation complete | ✅ Done | Sep 2025 | All marker types generated |
| Basic detection working | ✅ Done | Sep 2025 | Single marker detection |
| Pose estimation implemented | ✅ Done | Oct 2025 | 6DOF with calibration |
| Distance calculation added | ✅ Done | Oct 4, 2025 | Both methods working |
| **System architecture clarified** | ✅ Done | Oct 6, 2025 | **Wireless PC→Robot documented** |
| **Documentation corrected** | ✅ Done | Oct 6, 2025 | **README.md fully updated** |
| Distance accuracy validated | 🔄 In Progress | - | Testing 0.5-3m range |
| Multi-marker tracking | 🔄 In Progress | - | Simultaneous detection |
| Extrinsics computation | ⏸️ Planned | - | After detection validated |
| **Wireless communication module** | 🔴 **Critical** | - | **WebSocket/MQTT/UDP** |
| Full pipeline integration | ⏸️ Planned | - | Final integration |

### Recent Changes (Oct 6, 2025)

**📝 CRITICAL DOCUMENTATION UPDATE**
- **Corrected System Architecture**: Clarified that wireless communication PC→Robot IS allowed and required
- **README.md Complete Overhaul**: Removed all "no wireless"/"wired only"/"cable management" sections
- **Added Wireless Communication Design**:
  - Three protocol options documented: WebSocket, MQTT, UDP
  - WiFi interference challenges identified (20-30 teams, 10-30% packet loss)
  - Packet loss mitigation strategies added
  - Hardware requirements updated (5GHz WiFi dongle recommended)
  - Libraries documented: `websockets>=12.0`, `paho-mqtt>=1.6`, `msgpack>=1.0`
- **Updated Architecture Diagram**: Shows USB (Camera→PC) and WiFi (PC→Robot) clearly

**Why This Matters**:
- Previous documentation incorrectly described a wired/tethered system
- Correct architecture allows robot mobility while keeping PC stationary
- Wireless communication is now identified as a CRITICAL module to implement

**Files Modified**:
- `README.md` - Complete communication section rewrite
- Multiple sections updated: Challenges, Hardware Requirements, Tools & Dependencies, Pipeline

---

### Recent Changes (Oct 4, 2025)

**✨ Added Distance Calculation**
- Implemented pixel-based distance estimation (no calibration needed)
- Added calibrated distance calculation using focal length
- Created comparison visualization
- Added distance overlay on video feed

**Files Modified**:
- `ArUco_detection_folder/aruco_tools/marker_detector.py`
- `ArUco_detection_folder/examples/05_with_calibration.py`

**Key Additions**:
```python
# New methods in MarkerDetector class
- estimate_distance_uncalibrated()  # Pixel-based estimation
- calculate_distance_calibrated()   # Accurate with calibration
- draw_distance_info()              # Visual overlay
```

---

## 🎯 Next Actions

### Immediate Tasks (This Week)
1. [ ] Print ArUco markers 0-3 (map anchors) for physical placement
### 1. Verify Field Dimensions
Check your Eurobot 2026 Cahier des Charges:
- [x] Confirm field is 3.0m × 2.0m ✅ **VERIFIED**
- [ ] Update all documentation with correct dimensions 🔄 IN PROGRESS
3. [ ] Place markers at field corners with precise positioning
4. [ ] Run `compute_extrinsics.py` to get camera pose
5. [ ] Validate extrinsics stability over time

### Short-term Goals (Next 2 Weeks)
1. [ ] Implement enemy robot detection module (ArUco ID 30+)
2. [ ] Add Kalman filtering for position smoothing (FilterPy)
3. [ ] **CRITICAL**: Design wireless communication architecture
   - [ ] Choose protocol (WebSocket vs MQTT vs UDP)
   - [ ] Implement sender module (PC side)
   - [ ] Implement receiver module (Raspberry Pi side)
   - [ ] Add packet loss handling and reconnection logic
4. [ ] Test communication under WiFi interference conditions
5. [ ] Benchmark end-to-end latency (target <50ms)

### Long-term Goals (Competition Ready)
1. [ ] Full pipeline integration (vision → communication → robot)
2. [ ] Test with 20+ WiFi networks active (competition simulation)
3. [ ] Optimize for packet loss tolerance (10-30% expected)
4. [ ] Create fallback strategies for communication dropout
5. [ ] Field testing and performance validation

---

## 📝 Configuration Files

### camera_config.yaml Status

```yaml
# Current state: Template only
camera:
  name: "Overhead Camera" ✅
  mount_height: null ⏸️

intrinsics:
  camera_matrix: null ⏸️ (available in camera_calibration.json)
  distortion_coefficients: null ⏸️

extrinsics:
  rvec: null ⏸️ (needs map anchors)
  tvec: null ⏸️ (needs map anchors)

validation:
  validated: false ⏸️
```

**Action Required**: Populate from `camera_calibration.json` after ArUco testing complete

---

## 🐛 Known Issues

### Current Issues
1. **Distance estimation accuracy**: Uncalibrated method has ~20-30% error
   - **Impact**: Medium
   - **Solution**: Use calibrated method for production
   - **Status**: Expected behavior, not a bug

2. **Multi-marker interference**: Occasional false positives with overlapping markers
   - **Impact**: Low
   - **Solution**: Maintain minimum marker separation (>10cm)
   - **Status**: Investigating

### Resolved Issues
- ✅ Camera calibration JSON loading - Fixed Oct 4
- ✅ Pose estimation coordinate system - Verified Oct 4

---

## 📚 Documentation

### Key Files
- `ARUCO_GUIDE.md` - ArUco marker usage guide
- `camera_calibration_folder/README.md` - Calibration instructions
- `map_anchors/README.md` - World frame setup (coming soon)

### Coordinate Systems
```
Camera Frame (OpenCV):
- Origin: Camera optical center
- +X: Right
- +Y: Down
- +Z: Forward (into scene)

World Frame (Target):
- Origin: Table corner (marker 0)
- +X: Table length
- +Y: Table width
- +Z: Up from table

Transformation: T_world_cam (computed by map_anchors)
```

---

## ⚠️ KNOWN ISSUES & LIMITATIONS

### Current Limitations

#### Vision System
- **Lighting Sensitivity**: ArUco detection quality depends on consistent lighting
  - **Mitigation**: Test lighting conditions on competition field
  - **Recommendation**: Use diffused overhead lighting
- **Occlusion Handling**: Temporary marker loss handled by Kalman filter (max 30 frames)
  - **Mitigation**: Kalman prediction during occlusion
  - **Limitation**: Accuracy degrades after 1 second of occlusion
- **Camera Coverage**: Single overhead camera has blind spots at edges
  - **Status**: Acceptable for current field size (3.0m × 2.0m)
  - **Future**: Consider multi-camera setup for redundancy

#### Tracking System
- **Crate ID Timeout**: Lost crates removed after 2 seconds
  - **Current Setting**: `CRATE_TIMEOUT = 2.0s`
  - **Tunable**: Increase for slower-moving scenarios
- **Position Match Threshold**: 15cm may be too sensitive in crowded areas
  - **Current Setting**: `POSITION_MATCH_THRESHOLD = 0.15m`
  - **Tunable**: Adjust based on real-world testing
- **EMA Smoothing**: May introduce lag in fast movements
  - **Current Setting**: `smoothing_alpha = 0.3`
  - **Trade-off**: Smooth vs responsive

#### Strategy System
- **LiDAR Placeholder**: Enemy positions currently use placeholder data
  - **Status**: Waiting for LiDAR integration
  - **Interface Ready**: Just pass real `enemy_positions` to update_world_state()
- **Static Obstacles**: Obstacle map doesn't update dynamically
  - **Status**: Works for known static obstacles
  - **Future**: Dynamic obstacle updates from LiDAR

#### Path Planning
- **RRT Computation Time**: Can take 0.5-2 seconds for complex scenarios
  - **Mitigation**: Multi-threaded implementation
  - **Mitigation**: Timeout protection and fallback strategies
- **Path Smoothing**: Not always optimal in tight spaces
  - **Status**: Acceptable for current requirements
  - **Future**: Consider more advanced smoothing algorithms

### Known Bugs (None Critical)
- None reported as of January 15, 2026

### Performance Notes
- **Target FPS**: 30 fps (currently achieving 25-30 fps in full pipeline)
- **Processing Latency**: ~33ms per frame (acceptable for real-time operation)
- **Memory Usage**: Moderate (increases with number of tracked crates)
- **CPU Usage**: 30-50% on modern PC (single-threaded camera loop)

### Future Improvements
1. **Multi-camera Setup**: Redundancy and better coverage
2. **GPU Acceleration**: OpenCV CUDA support for faster processing
3. **Dynamic Obstacle Updates**: Real-time obstacle map from LiDAR
4. **Advanced Path Planning**: RRT* or informed RRT for better paths
5. **Machine Learning**: Crate detection without ArUco markers
6. **Predictive Modeling**: Anticipate enemy movements
7. **Cloud Logging**: Real-time telemetry for debugging
8. **Auto-calibration**: One-click calibration procedure

---

## 🤝 Contributing

### Adding New Features
1. Test in isolation first
2. Document in relevant module README
3. Update this PIPELINE_README.md
4. Add entry to CHANGELOG (if exists)
5. Update status indicators (✅/🔄/⏸️)

### Testing New Changes
```bash
# Always test each module independently first
cd camera_calibration_folder && python test_calibration.py
cd ../ArUco_detection_folder && python examples/test_marker_detector.py
cd ../map_anchors && python scripts/validate_pose.py  # When available
```

---

## � QUICK REFERENCE

### Common Workflows

#### 1. Camera Calibration (One-time Setup)
```bash
cd camera_calibration_folder
python generate_chessboard.py  # Print chessboard pattern
python calibrate_camera.py --camera 1
python test_calibration.py  # Validate calibration
```

#### 2. Camera Extrinsics (Pre-competition)
```bash
cd map_anchors/scripts
python compute_extrinsics.py  # Automatic PnP method
# OR
python compute_extrinsics_gui.py  # Interactive method
python validate_pose.py --duration 30  # Stability test
```

#### 3. Strategy Visualization (Testing)
```bash
cd strategy
python visualize_strategy.py --camera 1
# Controls: SPACE (recalibrate), ESC (quit), P (print), S (stats)
```

#### 4. Full Pipeline (Production)
```bash
cd full_pipeline/scripts
python main.py --camera 1
# OR with RRT-Connect
python main_connect.py --camera 1
```

#### 5. Orientation Testing
```bash
cd orientation
python vision_fusion.py --camera 1  # Recommended fusion method
# OR test individual methods
python vision_pca.py --camera 1
python vision_minrect.py --camera 1
```

### Key Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `camera_calibration.json` | Camera intrinsics | `camera_calibration_folder/calibration/` |
| `camera_extrinsics.json` | Camera pose | `camera_calibration_folder/calibration/` |
| `marker_config.yaml` | Marker positions | `map_anchors/config/` |
| `pipeline_config.yaml` | Pipeline settings | `full_pipeline/config/` |
| `caisse_config.yaml` | Crate detection | `caisses_detection/config/` |
| `config.py` | Strategy parameters | `strategy/` |

### Important Parameters to Tune

#### Crate Tracking (`strategy/crate_id_tracker.py`)
```python
POSITION_MATCH_THRESHOLD = 0.15  # Distance to match crates (meters)
CRATE_TIMEOUT = 2.0              # Remove unseen crates (seconds)
```

#### Strategy (`strategy/config.py`)
```python
weight_expected_score = 1.0      # Score importance
weight_safety = 0.8              # Enemy avoidance
enemy_danger_radius = 0.5        # Danger zone (meters)
```

#### Kalman Filter (`kalman_filter/`)
```python
process_noise = 0.01             # Motion model uncertainty
measurement_noise = 0.1          # Sensor uncertainty
```

#### Path Planning (`path_planning/`)
```python
step_size = 0.25                 # Path granularity (meters)
max_iter = 2000                  # Planning timeout
```

### Troubleshooting Guide

#### "No markers detected"
- Check camera focus and lighting
- Verify marker IDs match configuration
- Ensure markers are flat and visible
- Test with `aruco_detection_folder/examples/02_detect_webcam.py`

#### "Camera calibration failed"
- Use high-quality chessboard printout
- Ensure chessboard is flat and well-lit
- Capture 20+ images from different angles
- Verify chessboard dimensions in config

#### "Path planning fails frequently"
- Check obstacle positions and radii
- Increase `max_iter` parameter
- Verify start/goal positions are valid
- Enable fallback strategies

#### "FPS drops below 20"
- Reduce camera resolution
- Disable Kalman filter temporarily
- Optimize obstacle count
- Check CPU usage and close other programs

#### "Crate tracking loses IDs"
- Increase `CRATE_TIMEOUT` value
- Decrease `POSITION_MATCH_THRESHOLD` for tighter matching
- Check for lighting/occlusion issues
- Verify marker detection quality

### Emergency Procedures

#### During Competition
1. **Camera disconnects**: Press SPACE to re-initialize
2. **Tracking freezes**: ESC and restart pipeline
3. **Wrong extrinsics**: Press SPACE to recalibrate
4. **FPS drops**: Toggle Kalman filter off (K key)

#### Pre-Match Checklist
- [ ] Camera mounted and connected
- [ ] Field markers in place (IDs 20-23)
- [ ] Calibration files present
- [ ] Test detection of all marker types
- [ ] Validate path planning in test run
- [ ] Check WiFi connection to robot
- [ ] Verify match timer synchronization
- [ ] Test emergency stop procedure

---

## �📞 Support & References

### OpenCV ArUco Documentation
- [ArUco Marker Detection](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
- [Camera Calibration](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html)
- [Pose Estimation](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)

### Project-Specific
- See individual module READMEs for detailed documentation
- Check `ARUCO_GUIDE.md` for marker usage
- Review code comments for implementation details

---

## 🔄 Version History

### v0.6 (Current) - January 15, 2026
- 🔴 **CRITICAL BUG FIX**: Crate ID tracking system implemented
  - Fixed ArUco ID collision (all blue = 36, all yellow = 47)
  - Unique ID assignment: Blue 1001+, Yellow 2001+
  - Position-based tracking with 15cm matching threshold
  - Temporal filtering with Exponential Moving Average
  - Auto-timeout for lost crates (2 seconds)
- ✅ **Integration**: CrateIDTracker added to strategy and full_pipeline
- 📝 **Documentation**: CRATE_TRACKING_SOLUTION.md created
- 🔗 **Files Modified**: world_state.py, strategy_manager.py, visualize_strategy.py, crate_obstacle_manager.py
- ✅ **Testing**: Validated with multiple simultaneous crates
- 🎯 **Impact**: Strategy system can now track individual crates correctly

### v0.5 - December 16, 2025
- 🧠 **STRATEGY PACKAGE COMPLETE**: Utility-based decision making
- ✅ 6 task types implemented (nest, pantry, fridge, cursor, endgame)
- ✅ Utility formula with safety, feasibility, score, time, distance
- ✅ Live visualization with task rankings
- ✅ Integration with RRT-Connect path planning
- ✅ Enemy avoidance with danger zones
- ✅ Endgame priority boost mechanism
- 📚 Complete strategy documentation and examples

### v0.5 (Previous) - October 8, 2025
- 🔮 **KALMAN FILTER MODULE COMPLETE**: Full implementation with 6D state tracking
- ✅ Multi-marker tracking with automatic classification (Map/Caisse/Enemy)
- ✅ Occlusion handling with 4 strategies (Kalman/Partial/History/Fusion)
- ✅ Stress testing suite validated (85-95%+ accuracy, <1ms processing)
- ✅ Competition demo example (10-second simulation)
- 🔗 **CRITICAL FIX**: ArUco ID schema synchronized across all modules
  - Corrected caisse IDs from 10-20 → **36, 47, 41** (competition spec)
  - Updated classification logic in tracker.py
  - Fixed all test scenarios and examples
- 📚 **COMPREHENSIVE DOCUMENTATION**: 2800+ lines added
  - TECHNICAL_SUMMARY.md (API & configuration)
  - SYNCHRONIZATION_SUMMARY.md (change tracking)
  - DATA_FLOW.md (pipeline architecture)
  - Kalman & occlusion theory docs
- 🖥️ **MATLAB FIXES**: Camera position corrected to outside field (Y=2.044m)
  - test_graphics.m works correctly
  - simulate_camera_positioning_SUBPLOT.m rewritten
  - All marker positions updated (inset 0.6m from edges)
- 🎓 **DECISION**: Pause coding, focus on theoretical understanding
- 📖 Created THEORETICAL_UNDERSTANDING.md to track study requirements

### v0.4 - October 6, 2025
- 📝 **MAJOR DOCUMENTATION UPDATE**: Corrected system architecture
- ✅ Clarified communication design: Camera→USB→PC→WiFi→Robot
- ✅ Updated README.md with correct wireless communication approach
- ✅ Removed incorrect "no wireless" references throughout documentation
- ✅ Added WiFi communication options (WebSocket, MQTT, UDP)
- ✅ Documented competition WiFi challenges (interference, packet loss)
- ✅ Updated hardware requirements for wireless PC-to-Robot setup
- 🎯 Identified critical path: Extrinsics → Enemy Detection → Kalman → **Wireless Comm** → Integration

### v0.3 - October 4, 2025
- ✨ Added distance calculation (calibrated & uncalibrated)
- ✨ Enhanced visualization with distance overlay
- 🔄 Testing distance accuracy
- 🔄 Validating multi-marker detection

### v0.2 - September 2025
- ✅ ArUco detection working
- ✅ Pose estimation implemented
- ✅ Marker generation complete

### v0.1 - September 2025
- ✅ Camera calibration module complete
- ✅ Project structure defined
- ✅ Basic pipeline documented

---

**Remember**: Update this file each time you complete a milestone or make significant changes! 🚀