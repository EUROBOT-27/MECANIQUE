# 🤖 Eurobot 2026 – Autonomous Strategy & Behavior Tree Architecture

## 🧠 Project Overview

This repository contains the **autonomous strategy system** for the main robot participating in **Eurobot 2026**.  
The goal is to make the robot **dynamic, reactive, and intelligent**, capable of adapting to game changes in real time instead of following a static preplanned task list.

The strategy layer is implemented using a **Behavior Tree (BT)** integrated with **ROS 2**.  
The BT acts as the **high-level decision-making system**, while lower layers (STM32 / Navigation FSM) handle low-level control.

---

## 🎯 Objectives

1. Replace the old **Finite State Machine (FSM)-only** approach with a **Behavior Tree** for dynamic decision-making.
2. Maintain modularity by keeping navigation and mechanism control handled by STM32.
3. Allow the robot to:
   - React to **dynamic crate positions** detected by computer vision.
   - Prioritize tasks in real time based on **distance**, **availability**, and **score value**.
   - Transition smoothly between initialization and main phases of the match.

---

## ⚙️ System Architecture

### High-Level Structure

+------------------------------------------------------+
| STRATEGY LAYER |
| (Behavior Tree implemented in ROS 2) |
| |
| +--------------------+ +------------------------+ |
| | INIT PHASE | | DYNAMIC PHASE | |
| | (Fill nest, cursor)| | (Vision + Crate logic)| |
| +--------------------+ +------------------------+ |
+------------------------------------------------------+
│
▼
+------------------------------------------------------+
| NAVIGATION / ACTION LAYER (FSM) |
| - Receives nav orders or mechanism commands |
| - Runs on STM32 / ROS 2 action servers |
+------------------------------------------------------+
│
▼
+------------------------------------------------------+
| HARDWARE LAYER |
| - Sensors (Lidar, Camera, Encoders) |
| - Actuators (Motors, Servos, Gripper) |
+------------------------------------------------------+

yaml
Copy code

---

## 🌳 Behavior Tree Overview

### Root Behavior Tree

Root
├── InitPhase (Sequence)
│ ├── FillNest
│ ├── MoveCursor
│ └── SetFlag(init_done=True)
└── MainPhase (Selector)
├── Check(init_done == False) → Run InitPhase
└── DynamicCrateLoop (Sequence)
├── DetectAndFilterCrates
├── SelectNearestCrate
├── MoveToCrate
├── PickCrate
├── MoveToNearestPantry
├── DropCrate
└── RepeatUntil(NoCratesLeft)

markdown
Copy code

---

## 🧩 Behavior Tree Components

| Node | Description |
|------|--------------|
| **FillNest** | Navigate to the nest and place 6 initial crates (static tasks). |
| **MoveCursor** | Move the “cursor” actuator to score early points. |
| **DetectAndFilterCrates** | Receive crate positions from the computer vision node (e.g. via ArUco detection). Filters crates already in nest or pantry. |
| **SelectNearestCrate** | Compute the Euclidean distance between the robot and each valid crate. Select the closest one and store it in the blackboard. |
| **MoveToCrate** | Send navigation goal (to STM32 or Nav2). Wait until success or failure. |
| **PickCrate** | Trigger the gripper/arm sequence to pick the crate. |
| **MoveToNearestPantry** | Navigate to the nearest free pantry location. |
| **DropCrate** | Execute drop action. |
| **RepeatUntil(NoCratesLeft)** | Loop dynamic crate phase until all crates have been moved or time expires. |

---

## 🧠 Blackboard Variables

| Variable | Type | Description |
|-----------|------|-------------|
| `init_done` | bool | Whether initialization phase is complete. |
| `crates_list` | list of Pose2D | Raw crates detected from computer vision. |
| `valid_crates` | list of Pose2D | Filtered list of movable crates. |
| `target_crate` | Pose2D | Currently selected crate target. |
| `target_pantry` | Pose2D | Chosen pantry destination. |
| `robot_pose` | Pose2D | Robot’s current position (from odometry or Nav). |

---

## 🔄 Runtime Logic

1. On match start → BT begins in `InitPhase`.
2. Once nest and cursor actions succeed → `init_done` flag is set.
3. The main selector switches to the `DynamicCrateLoop`.
4. Each tick:
   - The robot queries the vision system for crate positions.
   - Filters invalid crates.
   - Chooses the nearest valid crate.
   - Sends motion commands to STM32 / Nav2.
   - Picks and places the crate.
   - Repeats the loop until no crates remain or match ends.
5. If at any moment an action fails (e.g., crate missing, obstacle), BT re-evaluates and selects a new target automatically.

---

## 🧩 Implementation Details

- **Library:** [`py_trees_ros`](https://github.com/splintered-reality/py_trees_ros)
- **Language:** Python 3 (ROS 2 Humble / Iron compatible)
- **Tick Rate:** ~10 Hz
- **Integration:**  
  - BT nodes communicate with ROS 2 services and actions.  
  - The STM32 microcontroller executes low-level FSM-based navigation and control.
- **Computer Vision Input:** Crate coordinates via a custom ROS 2 topic or service (using ArUco markers).

---

## 🧭 Roadmap

| Milestone | Description |
|------------|-------------|
| ✅ Week 1 | Study Behavior Trees and install `py_trees_ros`. |
| ✅ Week 2 | Implement simple BT for InitPhase and test locally. |
| 🟨 Week 3 | Integrate crate detection node (mock data first). |
| 🟨 Week 4 | Implement DynamicCrateLoop with navigation and pickup logic. |
| ⏳ Week 5 | Connect BT with STM32 navigation FSM and test on real robot. |
| ⏳ Week 6 | Optimize crate prioritization and failure recovery. |

---

## 📚 References

- [Behavior Trees in Robotics and AI – Michele Colledanchise (Book)](https://link.springer.com/book/10.1007/978-3-319-93405-7)
- [py_trees Documentation](https://py-trees.readthedocs.io/)
- [BehaviorTree.CPP Documentation](https://www.behaviortree.dev/)
- [ROS 2 Navigation (Nav2) Behavior Tree Architecture](https://navigation.ros.org/concepts/behavior_trees.html)
- [Groot 2 Visualization Tool](https://github.com/BehaviorTree/Groot2)

---

## 🧩 Notes for Copilot and Future Contributors

- The project’s **main goal** is to implement a **hybrid BT–FSM architecture**, where:
  - The **BT** handles high-level decision logic and task selection.
  - The **FSM** (running on STM32) executes physical navigation and manipulation tasks.
- Code contributions should follow modular design:
  - Each BT node = one logical action or condition.
  - All communication via ROS 2 topics, services, or actions.
- The repository will later include:
  - `/bt_nodes/` → Python BT node implementations.
  - `/launch/` → launch files for BT runtime.
  - `/config/` → blackboard and task parameters.
  - `/docs/` → diagrams and explanations.

---
The code architecture is not definite and can be changed
