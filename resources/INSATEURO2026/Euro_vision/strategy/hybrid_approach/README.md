# Hybrid Strategy Supervisor System

**Eurobot 2026 - Vision-Based Decision Making**

A sophisticated hybrid approach combining static field coordinates with dynamic computer vision perception for intelligent waypoint validation and path optimization.

---

## 🎯 Architecture Overview

### Philosophy: "Analyze, Validate, Optimize"

The hybrid supervisor receives destination waypoints from the Raspberry Pi (via ROS2/DDS) and makes intelligent decisions based on real-time computer vision:

**Workflow**:
1. 📍 **Receive** destination from Raspberry Pi (ROS2/DDS)
2. 👁️ **Analyze** enemy threat using Kalman predictions (3s lookahead)
3. ✅ **Decision**:
   - **ACCEPT**: Compute optimized path (RRT + smoothing) → send waypoints
   - **REJECT**: Send "REPLAN" flag + reason → wait for new destination
4. 🔄 **Monitor** enemy continuously at 30Hz

---

## 📁 Workspace Structure

```
strategy/hybrid_approach/
├── src/                          # Core modules (reusable)
│   ├── crate_flip_manager.py     # Count crates, decide flip targets
│   ├── dynamic_return_to_nest.py # RRT path planning (legacy)
│   ├── task_replanner.py         # Threat assessment (legacy)
│   └── hybrid_supervisor.py      # Legacy full supervisor
│
├── standalone_workspace/         # 🧪 Testing & Visualization
│   └── main.py                   # Run WITHOUT ROS2 - visual testing
│
├── ros2_workspace/               # 🚀 Production Integration
│   └── main.py                   # ROS2/DDS integration with placeholders
│
├── README.md                     # This file
└── requirements.txt              # Dependencies
```

---

## 🚀 Quick Start

### For Development & Testing (No ROS2 Required)

```bash
cd strategy/hybrid_approach/standalone_workspace

# Mock mode - simulated scenarios
python main.py --mock

# Camera mode - live CV (requires full_pipeline integration)
python main.py --camera 1
```

**Features**:
- ✅ Interactive visualization
- ✅ Simulated waypoint input
- ✅ Real-time threat assessment
- ✅ Path planning visualization
- ✅ No ROS dependencies

---

### For Production Integration (ROS2)

```bash
cd strategy/hybrid_approach/ros2_workspace

# Test mode (without ROS2)
python main.py --test

# Production mode (when ROS2 is configured)
ros2 run hybrid_supervisor main.py --team blue
```

**ROS2 Topics**:
- **Subscribe**: `/navigation/destination` - Receives waypoints from Raspberry Pi
- **Publish**: `/navigation/decision` - Sends ACCEPT/REJECT + reason
- **Publish**: `/navigation/waypoints` - Sends optimized path waypoints

---

## 🧩 Core Features

### 1. Waypoint Validation
Analyzes destination safety based on:
- Enemy position (Kalman-filtered)
- Enemy velocity (3-second prediction)
- Threat zones (configurable radius)
- Path feasibility

### 2. Path Optimization
When waypoint is ACCEPTED:
- RRT-Connect path planning
- Obstacle avoidance (predicted enemy position)
- Path smoothing for efficient navigation
- Waypoint sequence generation

### 3. Enemy Monitoring
Continuous tracking with Kalman filter:
- 6D state: position (x,y,θ) + velocity (vx,vy,vθ)
- Velocity-based prediction
- Confidence scoring
- Occlusion handling

### 4. Crate Analysis (Bonus Feature)
Vision-based crate counting:
- Pantry occupancy detection
- Ownership classification
- Flip target prioritization

---

## ⚙️ Configuration

All parameters in `strategy/utils/config.py`:

```python
from strategy.utils.config import StrategyConfig, DEFAULT_CONFIG

# Use defaults
supervisor = HybridSupervisor(DEFAULT_CONFIG, team_color="blue")

# Or customize
config = StrategyConfig()
config.enemy_danger_radius = 0.7  # Increase threat zone
config.path_planning_max_iter = 3000  # More RRT iterations
```

**Key Parameters**:
- `enemy_danger_radius`: Threat zone around enemy (default: 0.5m)
- `enemy_critical_radius`: Very dangerous zone (default: 0.3m)
- `path_planning_step_size`: RRT step size (default: 0.5m)
- `path_planning_max_iter`: Max RRT iterations (default: 2000)

---

## 🔌 Integration Guide

### Standalone Testing (No ROS2)

```python
from standalone_workspace.main import StandaloneHybridSupervisor

supervisor = StandaloneHybridSupervisor(team_color="blue", use_mock_data=True)
supervisor.run()
```

### ROS2 Production

```python
from ros2_workspace.main import ROS2HybridSupervisor

# Initialize with ROS2
supervisor = ROS2HybridSupervisor(team_color="blue", test_mode=False)

# Update vision at 30Hz
while running:
    detections = vision_system.get_detections()
    supervisor.update_vision(detections)

# ROS2 callbacks handle destinations automatically
supervisor.run()  # Spin ROS2 node
```

---

## 📊 Decision Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Raspberry Pi                             │
│                   (Static Waypoints)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ROS2/DDS: Destination (x, y)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               Hybrid Supervisor                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ 1. Get Enemy State (Kalman Filter)                 │     │
│  │    - Current position (x, y, θ)                    │     │
│  │    - Velocity (vx, vy, vθ)                         │     │
│  │    - Predict position in 3 seconds                 │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │ 2. Assess Threat                                   │     │
│  │    - Distance to predicted enemy position          │     │
│  │    - Compare to danger radius                      │     │
│  │    - Classify: NONE/LOW/MODERATE/HIGH/CRITICAL     │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │ 3. Decision                                        │     │
│  │    IF threat_distance < danger_radius:            │     │
│  │       → REJECT, send flag, wait for new dest      │     │
│  │    ELSE:                                          │     │
│  │       → ACCEPT, compute RRT path, send waypoints  │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ROS2/DDS: Decision + Waypoints
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Raspberry Pi                             │
│             (Execute or Request Replan)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Scenarios

### Standalone Mode Test Cases

```bash
python standalone_workspace/main.py --mock
```

**Scenario 1**: Safe waypoint - no enemy
- Destination: (1.5, 1.0)
- Expected: ACCEPT with direct path

**Scenario 2**: Threatened waypoint - enemy nearby
- Destination: (1.2, 0.8)
- Enemy at: (1.3, 0.9) moving toward
- Expected: REJECT with threat warning

**Scenario 3**: Safe waypoint - enemy far
- Destination: (2.5, 1.5)
- Enemy at: (0.5, 0.5) stationary
- Expected: ACCEPT with direct path

---

## 📝 Implementation Notes

### DO Use:
- ✅ `DEFAULT_CONFIG` for parameters
- ✅ Kalman filter for enemy tracking (mandatory)
- ✅ `unique_id` from `CrateIDTracker` (not ArUco `id`)
- ✅ RRT-Connect for path planning
- ✅ Path smoothing for efficiency

### DON'T:
- ❌ Raw enemy detections (always use Kalman)
- ❌ Hardcoded field coordinates (use config)
- ❌ ArUco IDs for crate tracking (use unique IDs)
- ❌ Blocking operations in ROS2 callbacks
- ❌ Modify official scoring rules in config

---

## 🔗 Dependencies

```bash
pip install -r requirements.txt
```

**Core**:
- `opencv-contrib-python` - ArUco detection
- `numpy` - Numerical operations
- `filterpy` - Kalman filtering

**Optional (for ROS2)**:
- `rclpy` - ROS2 Python client
- `geometry_msgs` - ROS2 message types
- `nav_msgs` - Path messages

---

## 📚 Related Documentation

- [Strategy Config](../utils/config.py) - All tunable parameters
- [World State](../utils/world_state.py) - Data structures
- [Kalman Filter](../../kalman_filter/UPDATED_TECHNICAL_SUMMARY.md) - Tracking system
- [Path Planning](../../path_planning/README.md) - RRT algorithms
- [Full Pipeline](../../full_pipeline/README.md) - CV integration

---

## 🎯 Next Steps

1. **Test standalone mode**: Verify visualization and decision logic
2. **Integrate with full_pipeline**: Connect to live camera feed
3. **Configure ROS2**: Set up DDS communication with Raspberry Pi
4. **Tune parameters**: Adjust threat radii, RRT settings for competition
5. **Field testing**: Validate with actual robot and enemy

---

**Questions?** See [.github/copilot-instructions.md](../../.github/copilot-instructions.md) for AI agent guidance.
flip_counts = flip_manager.analyze_all_pantries(world_state)

# 3. Assess current task threat
threat = task_replanner.assess_threat_to_task(current_task, world_state)

# 4. Make decision
if endgame:
    command = "RETURN_TO_NEST"
elif threat.should_abort:
    command = "EMERGENCY_RETURN"
elif threat.should_defer:
    command = "SWITCH_TASK"
else:
    command = "CONTINUE"

# 5. Send command to robot
send_to_robot(command, flip_counts, waypoint)
```

### Command Output Structure

```python
@dataclass
class SupervisorCommand:
    command_type: str           # "CONTINUE", "SWITCH_TASK", "RETURN_TO_NEST", "ABORT"
    target_task_id: str         # Which task to execute
    flip_counts: Dict[str, int] # Pantry flip decisions
    waypoint: Tuple[float, float]  # Next navigation target
    threat_level: str           # Current threat assessment
    confidence: float           # Decision confidence (0-1)
    reason: str                 # Human-readable explanation
```

---

## 🚀 Usage

### Basic Integration

```python
from hybrid_supervisor import HybridSupervisor
from config import DEFAULT_CONFIG

# Initialize
supervisor = HybridSupervisor(
    config=DEFAULT_CONFIG,
    team_color="blue",
    enable_visualization=True
)

# Set mission context
supervisor.set_current_task(your_current_task)
supervisor.set_available_tasks(list_of_tasks)

# Main loop
while game_running:
    # Get detections from vision system
    detections = vision_system.get_detections()
    
    # Run supervision cycle
    command = supervisor.run_supervision_cycle(
        detections=detections,
        camera_frame=camera_frame  # Optional for visualization
    )
    
    # Execute command
    if command.command_type == "SWITCH_TASK":
        robot.switch_to_task(command.target_task_id)
    elif command.command_type == "RETURN_TO_NEST":
        robot.navigate_to(command.waypoint)
    elif command.command_type == "ABORT":
        robot.emergency_stop()
    
    # Use flip counts
    if robot.at_pantry(pantry_id):
        num_flips = command.flip_counts[pantry_id]
        robot.flip_crates(num_flips)
```

### Detection Format

The supervisor expects detections in this format:

```python
detections = {
    'robot': {
        'pos': (x, y),
        'theta': orientation_radians
    },
    'enemies': [
        {
            'id': 13,
            'pos': (x, y, z),
            'theta': orientation,
            'velocity': (vx, vy),  # From Kalman filter
            'confidence': 0.95
        }
    ],
    'crates': [
        {
            'aruco_id': 36,  # or 47
            'pos': (x, y, z),
            'ownership': 'ours' or 'opponent',
            'container': 'free', 'pantry', 'nest', etc.
        }
    ],
    'time_remaining': 85.0  # seconds
}
```

---

## 📊 Visualization

When `enable_visualization=True`, the supervisor provides real-time display:

- **Field Map**: Top-down view with pantries, nests, and zones
- **Robot Position**: Green circle with orientation arrow
- **Enemies**: Red circles with blue velocity arrows
- **Crates**: Blue (ours) / Orange (enemy) dots
- **Current Task**: Yellow star marker
- **Waypoint**: Cyan circle
- **Info Panel**: State, command, threat level, time remaining
- **Flip Counts**: Displayed on each pantry

---

## 🔧 Configuration

All parameters tunable via `StrategyConfig`:

```python
from config import StrategyConfig

config = StrategyConfig()

# Pantry zones (auto-loaded from config)
config.pantry_zones = {
    'pantry1': (1.150, 1.350, 0.450, 0.650),
    # ... more pantries
}

# Safety parameters
config.enemy_danger_radius = 0.5  # meters
config.robot_flip_capacity = 4

# Path planning
config.path_planning_max_iter = 2000
config.rrt_step_size = 0.5

# Speeds
config.robot_linear_speed = 0.3  # m/s
```

---

## 🧪 Testing

Each module includes standalone tests:

### Test Flip Manager
```bash
cd strategy/hybrid_approach/src
python crate_flip_manager.py
```

### Test Return Planner
```bash
python dynamic_return_to_nest.py
```

### Test Task Replanner
```bash
python task_replanner.py
```

### Test Full Supervisor
```bash
python hybrid_supervisor.py
```

---

## 📈 Performance Characteristics

| Feature | Performance | Notes |
|---------|-------------|-------|
| Flip Analysis | < 1ms per pantry | Real-time capable |
| Path Planning (RRT) | 50-200ms | Depends on complexity |
| Threat Assessment | < 5ms | Kalman predictions cached |
| Full Supervision Cycle | 100-300ms | Suitable for 3-10 Hz loop |

---

## 🎯 Design Principles

1. **Separation of Concerns**: Each feature is independent and testable
2. **Confidence Scoring**: Every decision includes confidence metric
3. **Fail-Safe Defaults**: System degrades gracefully (no vision → static mode)
4. **Human-Readable**: All decisions include textual reasoning
5. **Visualization First**: See what the system is thinking
6. **Configuration-Driven**: Easy to tune without code changes

---

## 🔄 Integration with Existing Systems

### With ROS Pipeline
```python
# In your ROS node
from hybrid_supervisor import HybridSupervisor

supervisor = HybridSupervisor(team_color="blue")

def vision_callback(msg):
    detections = parse_ros_message(msg)
    command = supervisor.run_supervision_cycle(detections)
    
    # Publish command flags
    flip_pub.publish(command.flip_counts)
    waypoint_pub.publish(command.waypoint)
    threat_pub.publish(command.threat_level)
```

### With Serial Communication
```python
import serial

supervisor = HybridSupervisor(team_color="blue")
ser = serial.Serial('/dev/ttyUSB0', 115200)

while True:
    detections = get_detections_from_vision()
    command = supervisor.run_supervision_cycle(detections)
    
    # Send flags over serial
    msg = f"CMD:{command.command_type}|FLIP:{command.flip_counts}|WP:{command.waypoint}\n"
    ser.write(msg.encode())
```

---

## 🛠️ Advanced Features

### Custom Threat Zones

```python
replanner.threat_zone_radius[TaskType.FLIP_ENEMY_CRATE_IN_PANTRY] = 0.8  # Larger zone
```

### Force Replanning

```python
path = planner.plan_return_to_nest(world_state, force_replan=True)
```

### Get Detailed Reports

```python
print(flip_manager.get_summary_report())
print(replanner.get_threat_report(tasks, world_state))
print(supervisor.get_status_report())
```

---

## 📚 Dependencies

- `numpy`: Numerical operations
- `opencv-python`: Visualization
- Existing modules:
  - `strategy/utils/config.py`
  - `strategy/utils/world_state.py`
  - `strategy/utils/task_models.py`
  - `strategy/utils/crate_id_tracker.py`
  - `kalman_filter/src/kalman_filter/tracker.py`

---

## 🤝 Contributing

This is a **senior engineering** implementation with:
- ✅ Clear documentation
- ✅ Modular architecture
- ✅ Testable components
- ✅ Type hints
- ✅ Comprehensive examples
- ✅ Performance considerations

Follow these patterns when extending!

---

## 📄 License

Part of Eurobot 2026 Computer Vision System

---

## 👥 Authors

**Eurobot 2026 Vision Team**

*"From static paths to intelligent perception - the evolution of robot autonomy."*

---

**Last Updated**: January 23, 2026
