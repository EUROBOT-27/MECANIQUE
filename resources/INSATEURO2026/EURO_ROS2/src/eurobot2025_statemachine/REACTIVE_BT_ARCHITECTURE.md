# Reactive Behavior Tree Architecture Guide

## Overview
This document explains the reactive behavior tree architecture for Eurobot 2025 and how it integrates with the strategy package for dynamic task management.

---

## Tree Structure Visualization

```
ReactiveRoot (Sequence)
│
├─── Initialization (Sequence)
│    ├─── WaitForJack
│    └─── CheckNavigatorReady
│
├─── MainMatchLoop (Decorator: FailureIsRunning) ← Makes tree loop continuously
│    │
│    └─── TaskWithReplanning (Selector) ← Tries normal execution, falls back to replan
│         │
│         ├─── NormalTaskExecution (Sequence)
│         │    │
│         │    ├─── RequestNextTask ← Queries strategy for best current task
│         │    │
│         │    └─── MonitoredNavigation (Parallel) ← KEY REACTIVE COMPONENT
│         │         │
│         │         ├─── ConditionMonitor (Sequence) ← Runs simultaneously with nav
│         │         │    │
│         │         │    ├─── IsTaskStillValid ← Re-queries strategy
│         │         │    ├─── IsEnemyThreat ← Checks enemy_conflict flag
│         │         │    └─── IsObstaclePresent ← Checks LIDAR/stuck
│         │         │
│         │         └─── ExecuteNavigation (Sequence)
│         │              │
│         │              ├─── SendNavigationOrder
│         │              ├─── WaitForDestination
│         │              └─── AcknowledgeDestination
│         │
│         └─── ReplanAndRetry (Sequence) ← Executed if NormalTaskExecution fails
│              │
│              ├─── AbortCurrentNavigation ← Sends stop signal to STM32
│              └─── RequestNextTask ← Gets fresh task from strategy
│
└─── FinishMatch
```

---

## How Reactivity Works

### 1. **Parallel Node Behavior**

The `MonitoredNavigation` uses a **Parallel** composite with `SuccessOnOne` policy:

```python
Parallel(
    name="MonitoredNavigation",
    policy=py_trees.common.ParallelPolicy.SuccessOnOne(synchronise=False)
)
```

**What this means:**
- Both `ConditionMonitor` and `ExecuteNavigation` run **at the same time**
- Every tick (10 Hz by default), both branches are evaluated
- If `ConditionMonitor` returns `FAILURE`, the entire Parallel returns `FAILURE`
- This **interrupts** the navigation sequence immediately

**Example Timeline:**
```
Tick 1: ConditionMonitor=SUCCESS, ExecuteNavigation=RUNNING → Parallel=RUNNING
Tick 2: ConditionMonitor=SUCCESS, ExecuteNavigation=RUNNING → Parallel=RUNNING
Tick 3: ConditionMonitor=FAILURE (enemy detected!), ExecuteNavigation=RUNNING → Parallel=FAILURE
Result: Navigation interrupted, falls through to ReplanAndRetry
```

---

### 2. **Condition Checking (Every Tick)**

#### **IsTaskStillValid**
```python
def update(self):
    if get_next_task():  # Query strategy
        if next_task.id != current_task.id:
            return Status.FAILURE  # Different task returned!
    return Status.SUCCESS
```

**When it triggers:**
- Strategy discovers a higher-priority task
- Strategy determines current task is no longer optimal
- Enemy takes the current task (strategy updates internally)

#### **IsEnemyThreat**
```python
def update(self):
    if enemy_conflict:  # Set by enemy position subscriber
        return Status.FAILURE
    return Status.SUCCESS
```

**When it triggers:**
- Enemy position subscriber detects enemy within 200mm of target
- `enemy_conflict` flag is set to `True`

#### **IsObstaclePresent**
```python
def update(self):
    if lidar_obstacle_detected or robot_stuck or current_navigator_state in [9, 10]:
        return Status.FAILURE
    return Status.SUCCESS
```

**When it triggers:**
- LIDAR detects obstacle in path
- Robot gets stuck (position not changing)
- STM32 navigator reports blockage

---

### 3. **Replanning Flow**

When any condition fails:

```
1. MonitoredNavigation returns FAILURE
   ↓
2. NormalTaskExecution returns FAILURE (Sequence fails if child fails)
   ↓
3. TaskWithReplanning Selector tries next child: ReplanAndRetry
   ↓
4. AbortCurrentNavigation sends stop to STM32
   ↓
5. RequestNextTask gets NEW best task from strategy
   ↓
6. Loop continues: MainMatchLoop decorator makes tree restart
   ↓
7. Back to TaskWithReplanning, tries NormalTaskExecution with new task
```

---

## Integration with Strategy Package

### Strategy Package Responsibilities

The `static_task_generator.py` maintains:
- **`available_tasks`**: Current list of tasks to perform
- **`obstacle_positions`**: Dynamic obstacles (including enemies)
- **Task scoring**: Priority based on:
  - Distance to robot
  - Task value/score
  - Enemy proximity
  - Already completed tasks

### Communication Flow

```
Behavior Tree                    Strategy Package
     │                                │
     ├─ get_next_task_point() ──────►│
     │                                ├─ Evaluate all tasks
     │                                ├─ Check enemy positions
     │                                ├─ Score and rank tasks
     │                                └─ Return best task
     │◄─────────────────────────────┤
     │                                │
     ├─ (Enemy moves near task)      │
     │                                │
     ├─ IsTaskStillValid()           │
     ├─ get_next_task_point() ──────►│
     │                                ├─ Enemy now near old task
     │                                ├─ Returns DIFFERENT task
     │                                └─ (higher priority now)
     │◄─────────────────────────────┤
     │                                │
     ├─ Comparison: new ≠ old        │
     └─ Return FAILURE (trigger replan)
```

---

## Example Scenarios

### Scenario 1: Enemy Interference

```
Initial state:
- Robot navigating to Task A (Building Pickup at position X,Y)
- Enemy robot detected moving toward same position

Timeline:
Tick 50: Robot halfway to Task A
         ConditionMonitor checks:
         - IsTaskStillValid: Strategy still says Task A is best → SUCCESS
         - IsEnemyThreat: Enemy 300mm away → SUCCESS (outside threshold)
         - IsObstaclePresent: Path clear → SUCCESS
         Result: Continue navigation

Tick 75: Robot 3/4 way to Task A
         Enemy position subscriber callback fires:
         - Enemy now 150mm from Task A
         - Sets enemy_conflict = True
         
         ConditionMonitor checks:
         - IsTaskStillValid: Task A still valid → SUCCESS
         - IsEnemyThreat: enemy_conflict = True → FAILURE ⚠️
         Result: MonitoredNavigation returns FAILURE

Action: AbortCurrentNavigation sends stop signal
        RequestNextTask queries strategy
        Strategy returns Task B (different location)
        Navigation restarts toward Task B
```

### Scenario 2: Better Task Discovered

```
Initial state:
- Robot navigating to Task C (low priority, far away)
- Strategy detects Task D became available (high priority, closer)

Timeline:
Tick 100: Robot navigating to Task C
          IsTaskStillValid queries strategy:
          - Strategy now returns Task D (higher priority)
          - next_task.id (D) != current_task.id (C)
          - Returns FAILURE ⚠️

Action: Navigation aborted
        New navigation to Task D started
        Robot adapts to better opportunity
```

### Scenario 3: Obstacle Detection

```
Initial state:
- Robot navigating to Task E
- Unexpected obstacle appears in path

Timeline:
Tick 120: LIDAR detects obstacle
          lidar_obstacle_detected = True
          
          IsObstaclePresent checks:
          - lidar_obstacle_detected = True → FAILURE ⚠️

Action: Navigation aborted
        Strategy consulted for alternative
        May return same task (obstacle temporary) or different task
```

---

## Advantages of This Architecture

### 1. **True Reactivity**
- Responds within one tick cycle (100ms at 10 Hz)
- No need to complete current action before adapting

### 2. **Separation of Concerns**
- Behavior Tree: Handles execution flow and interruption
- Strategy Package: Handles decision-making and task prioritization

### 3. **Easy to Extend**
Add new conditions by:
```python
class IsNewCondition(Behaviour):
    def update(self):
        if some_check():
            return Status.FAILURE
        return Status.SUCCESS

# Add to monitor:
monitor_sequence.add_child(IsNewCondition())
```

### 4. **Testable**
- Each condition node can be unit tested
- Strategy package can be tested independently
- Tree structure is explicit and visualizable

---

## Configuration Parameters

### Tick Rate
```python
tick_rate = 10.0  # Hz (in main() function)
```
- Higher = More responsive but more CPU
- Lower = Less CPU but slower reaction
- Recommended: 10-20 Hz

### Enemy Conflict Threshold
```python
CONFLICT_THRESHOLD = 200.0  # mm (in enemy_pos_callback)
```
- Distance at which enemy is considered a threat
- Adjust based on robot size and field dimensions

---

## Strategy Package Requirements

For this reactive BT to work optimally, your strategy package should:

1. **Always return best current task** when queried
   - Don't cache responses
   - Re-evaluate all tasks on each request

2. **Consider enemy positions** in task scoring
   - Tasks with enemies nearby should have lower priority

3. **Update dynamically** when enemy crosses tasks
   - Remove tasks from available_tasks when enemy takes them
   - Or significantly reduce their priority

4. **Provide task validation**
   - Return consistent task IDs
   - Support querying "is task X still valid?"

---

## Future Enhancements

### 1. Add Subtask Monitoring
```python
# Monitor during complex tasks (pickup/dropdown)
subtask_parallel = Parallel("MonitoredSubtask")
subtask_parallel.add_children([
    SubtaskConditionMonitor(),
    ExecuteSubtasks()
])
```

### 2. Add Mechanism Integration
```python
class ExecuteMechanismAction(Behaviour):
    def update(self):
        from mecanisme.mechanism_servo import move_servo
        move_servo(channel, position)
        return Status.SUCCESS
```

### 3. Add Match Time Awareness
```python
class IsTimeToReturn(Behaviour):
    def update(self):
        if time_remaining < 10.0:  # 10 seconds left
            return Status.FAILURE  # Trigger return to start
        return Status.SUCCESS
```

---

## Debugging Tips

### 1. Enable Tree Visualization
```python
# In main()
tree = create_behavior_tree()
py_trees.display.render_dot_tree(tree, name='eurobot_tree')
# Generates eurobot_tree.png showing structure
```

### 2. Add Logging
```python
class IsTaskStillValid(Behaviour):
    def update(self):
        if get_next_task():
            if next_task.id != current_task.id:
                print(f"Task changed: {current_task.id} → {next_task.id}")
                return Status.FAILURE
        return Status.SUCCESS
```

### 3. Monitor Tick Rate
```python
# In main()
import time
last_tick = time.time()
while rclpy.ok():
    tree.tick()
    now = time.time()
    print(f"Tick rate: {1.0/(now-last_tick):.1f} Hz")
    last_tick = now
    time.sleep(1.0 / tick_rate)
```

---

## Summary

This reactive behavior tree provides:
✅ **Instant reaction** to environmental changes
✅ **Dynamic task reprioritization** via strategy package
✅ **Graceful interruption and replanning**
✅ **Modular and extensible** architecture
✅ **Clear separation** between execution (BT) and decision-making (strategy)

The key insight: **Use Parallel nodes for monitoring + Selectors for replanning = Reactive system**
