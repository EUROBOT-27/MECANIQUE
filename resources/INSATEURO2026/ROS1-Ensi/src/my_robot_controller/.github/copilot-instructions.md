# Copilot Instructions for my_robot_controller

## Project Overview
This package implements a ROS2-based robot controller using a state machine (SMACH) to manage a competition workflow. The robot performs a sequence of tasks: number detection, color reading, cube/triangle detection, can pushing, bar pushing, and a fingerprint task. The main loc is in `my_first_node.py`.

## Key Files
- `my_first_node.py`: Main entry point. Contains all state machine logic, task handlers, and ROS publishers/services.
- `__init__.py`: Empty, used for Python package structure.

## Architecture & Data Flow
- **State Machine**: Uses `smach` and `smach_ros` to define states (`Idle`, `Init`, `WaitForSignal`, `MoveOn`, `WaitToReach`, `BlockageDetected`, `DestinationReached`, `Finished`). Transitions are explicit and outcomes are named as `Go to: <State>`.
- **Task Management**: Tasks are managed via the `TaskType` enum and a global `target_counter`. The `task_handler` method updates the current task based on the counter.
- **Navigation**: Navigation targets are generated from a `coordinates_list` and published as `master_navigationMessage`.
- **ROS Integration**: Uses publishers for navigation and acknowledgments, and a service for color detection. Parameters are set and read via `rospy.set_param`/`get_param`.

## Developer Workflows
- **Run Node**: Launch with `rosrun` or as part of a ROS2 launch file. The main node is `hafnaoui`.
- **Edit Task Sequence**: Update `coordinates_list` and `TaskType.task_handler` for new task orders or positions.
- **Debugging**: Use ROS logging (`rospy.loginfo`, `rospy.logerr`) and introspection server (`smach_ros.IntrospectionServer`) for state machine visualization.
- **Timers**: The game timer is managed in a background thread (commented out by default).

## Project-Specific Conventions
- **State Outcomes**: All state transitions use the pattern `Go to: <State>` for clarity.
- **Global Variables**: State and task management rely on global variables (e.g., `target_counter`, `current_task`).
- **Parameter Usage**: Robot state is tracked via ROS parameters (e.g., `nav_currentX`, `current_playing_time`).
- **Service/Topic Names**: Follows the pattern `/ros_can_interface/<topic>` for CAN interface messages.

## Integration Points
- **External Messages**: Relies on custom message types from `ros_can_interface` and `ensi1` packages.
- **Color Detection**: Calls the `detect_color` service from `ensi1`.

## Examples
- To add a new navigation target, append to `coordinates_list` and update `task_handler` logic.
- To add a new state, subclass `smach.State` and register it in the state machine in `main()`.

---
For more details, see `my_first_node.py`. Update this file if you add new states, tasks, or integration points.
