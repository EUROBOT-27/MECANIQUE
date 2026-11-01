# INSATEURO2026 — IEEE RAS INSAT's previous team (Eurobot 2026 + ENSI 2025)

Source: github.com/INSATEURO2026, 17 repos cloned 2026-10-25 into `INSATEURO2026/`. Studied the same day.
Our own club's material, handed down from the previous team. Result at the 2026 European final: **20th, 134 pts**
(from the ranking table in the Aerobotix PPP).

## 0. What is in the org

The org mixes **two competitions**. Only the Eurobot ones matter for us.

| Repo | Competition | What it is | Value for 2027 |
|---|---|---|---|
| **`Euro_vision/`** | Eurobot 2026 | Overhead-camera vision system, ~24k lines of Python, 100+ commits Nov 2025 → Mar 2026. Has a **post-mortem** | ⭐⭐⭐ vision |
| `ROS2_EURO_VISION/` | Eurobot 2026 | ROS 2 version of the vision tracker + **LiDAR + vision fusion node** + YDLidar driver + CAN interface | ⭐⭐ vision, D-007 |
| `Ros2_Vision/` | Eurobot 2026 | Earlier ROS 2 vision package (camera node + tracker) | ⭐ superseded |
| `Navigation/` | Eurobot 2026 | STM32F407 navigation board: odometry, trapezoid profile, polar PD, CAN; **excellent docs** (final Aug 2026) | ⭐⭐⭐ for the software team |
| `Mecanisme_Euro/` | Eurobot 2026 | ESP32 firmware for the main robot's mechanism, plus standalone test firmwares | ⭐⭐ mechanical lessons |
| `Pami/` | Eurobot 2026 | "Ninja" SIMA firmware (ESP32) + **step-by-step test procedure** | ⭐⭐ SIMAs |
| `PAMI_COPILOT/` | Eurobot 2026 | ESP32 SIMA firmware + web telemetry dashboard (Bluetooth/WiFi) | ⭐ debug tooling |
| `Electrique/` | Eurobot 2026 (+ENSI) | KiCad boards: actuators, power ("Puissance IEEE INSAT"), STM32 shield, solenoid valve controller, SIMA boards; final boards ordered from **JLCPCB**; HTML mechanism debug remote | ⭐⭐ for Hamza Bjaoui |
| `EURO_ROS2/` | Eurobot 2026 | ROS 2 workspace: behaviour-tree strategy (py_trees), SMACH state machine (from 2025), CAN interface, custom msgs, LiDAR, mechanism nodes | ⭐ software team |
| `Lidar/` | Eurobot 2026 | **YDLidar X2** docs + test scripts (triangulation, 5–10 Hz) | ⭐ explains "LiDAR unreliable" |
| `HARDWARE-CAD/` | **ENSI 2025** | SolidWorks of the ENSI robot (pendulum, pusher, LifeCam). **Not Eurobot** | low |
| `Computer_vision/` | **ENSI 2025** | YOLOv8 colour/number/shape detection, CLAHE for sunlight | low (shows YOLO know-how) |
| `ROS1-Ensi/`, `ros2-ensi/`, `Simulation/` | **ENSI 2025** | ROS bits, pygame path simulator (1.8 × 1.2 m table) | low |
| `Overview_EURO26/`, `demo-repository/` | — | Org overview template, GitHub demo | none |

⚠️ **There is no CAD of the Eurobot 2026 main robot in the org.** Ask the previous members whether a STEP/SolidWorks file exists.

---

## 1. Vision (Euro_vision) — the important part

### 1.1 Architecture they built
- **Overhead camera** above the field (planned on the edge platform at ~1.6 m), seeing the whole 3 × 2 m table.
- Prototyped with an **iPhone XR via the Camo app** (1280×720 @ 30 fps), later another phone (Feb 2026, fx ≈ 939 px →
  horizontal FOV ≈ 69°). There's no sign in the repos that a dedicated competition camera was chosen.
- Pipeline: **capture → ArUco detection (DICT_4X4_50) → pose per marker → camera extrinsics from 4 fixed table
  anchors → transform to world → smoothing (moving average) / Kalman (enemy) → strategy + path planning → send to robot.**
- Planned link: **camera → USB → vision PC → WiFi → robot Raspberry Pi** (sockets / ROS 2 DDS). They documented
  competition WiFi issues (20–30 teams, 10–30% packet loss).
- Grew into a **"hybrid supervisor"**: the RPi proposes a destination, and the vision PC accepts it (returns an RRT-Connect
  path) or rejects it based on the Kalman-predicted enemy position (3 s lookahead).
- Multi-threaded version: capture thread + separate processes for extrinsics, Kalman and RRT → kept 30 FPS during planning.
- On-board camera (Mar 2026, `crate_color_detector_aruco.py`): reads crate tags and sorts them left → right to get the
  colour order. No calibration needed. Simple and useful.

### 1.2 The post-mortem (`full_pipeline/POST_MORTEM.md`) — read this before writing any CV code
**14+ failed attempts, 400–4000 px reprojection errors.** The causes were all **wrong input data**, not the maths:
1. **Marker size mismatch**: all markers were assumed 10 cm, but object markers were 5 cm → objects appeared at 2× the distance.
   Fix: size per marker ID.
2. **Calibration resolution mismatch**: 640×480 intrinsics used on 1280×720 video. Fix: recalibrate at the runtime
   resolution → **0.05–0.16 px** reprojection error.
3. **Over-engineering**: custom PnP, averaging rotation matrices (invalid), chained transforms, quaternions… all
   replaced by standard OpenCV: `solvePnP` on **all 16 anchor corners** (4 markers × 4) → `P_world = Rᵀ(P_cam − t)`.

**Measured results (final working version):** 28–30 FPS · ~35 ms latency · **~9 cm XY error** at 1.6 m (5 cm
marker) · jitter ±2 cm raw → ±5 mm moving average → ±2 mm Kalman · 1 s occlusion → ~3 cm error, re-converges in < 0.5 s.

Their lessons: trust standard libraries · check input data first · calibrate at the runtime resolution · keep it
simple · validate step by step (calibration → detection → extrinsics → known positions) · Kalman only where needed.

### 1.3 Other technical details
- **Kalman**: constant velocity, state [x, y, θ, vx, vy, vθ], Q = 0.01, R = 0.1, lost after 30 frames.
  Occlusion handler with 4 strategies (prediction, partial corners, history, confidence fusion).
- **Same-ID objects**: all blue crates shared one ID, so they built `CrateIDTracker`: spatial matching (15 cm gate), EMA,
  2 s timeout, unique IDs 1001+/2001+. **Directly relevant: in 2027 all 30 stones carry ID 13.**
- Orientation from bbox / min-rect / PCA was tried and **removed ("approach did not work")** (Jan 2026).
- Path planning: RRT, RRT-Connect (used), A*, greedy path smoothing; fallback with relaxed enemy radius, then sudden stop.
- Strategy: utility = (score × feasibility × safety) / (time + distance), endgame boost below 15 s.

### 1.4 LiDAR + vision fusion they tried (`ROS2_EURO_VISION/src/lidar_scripts`)
- LiDAR: **YDLidar X2** (triangulation, 5–10 Hz). Script takes the **closest point inside the table** as "the enemy" and
  raises an obstacle flag if it's 0.15–0.45 m away.
- Fusion: **plain average** of the last vision and LiDAR positions. No timestamps, no gating, no handling of one
  sensor dropping out, no distinction between the opponent, game elements and our own SIMAs.

### 1.5 Problems we must not repeat (my reading)
1. ⚠️ **Rules: the vision PC was off the table.** [GR F.6]: *all systems must be on the table and may not communicate
   with systems outside it during matches.* The camera **and the computer** must be on the remote computing
   device platform (≤ 5 kg, 450 × 320 mm footprint, ≤ 1.6 m) [GR G.4]. A laptop beside the table isn't allowed.
2. **ArUco ID chaos**: "enemy" was 13 in one file, 30+ in another, 47 in the ROS node. By the rules, robot markers are
   **1–5 / 6–10, assigned randomly** [GR G.6]. The anchor ID ↔ position mapping differs across **at least 4 files**.
   → One config file must be the single source of truth.
3. **Accuracy left on the table**: they took depth from the pose of a single small marker. Because heights are known
   (robot marker top ≈ 450 mm, table 0 mm, stone faces at known heights), **intersecting the pixel ray with the known
   height plane** should give ~1–2 cm instead of ~9 cm. Worth testing first.
4. Phone-as-camera was never replaced by a dedicated camera in the repos. Choose and mount the real camera early.
5. README pinouts don't match the code (e.g. CAN pins in `Mecanisme_Euro`). Docs drifted from the code.

### 1.6 2027-specific consequences (new)
- **Stones: ArUco ID 13 on the 4 long faces only, none on the 110 × 110 ends** [G D.4]. From above, a **lying
  stone shows a tag**, but a **standing stone (tower, gate upright) shows no tag**. The overhead tag tracker can't see
  built towers. Use another cue (shape/colour/depth) or don't track them.
- 30 identical IDs → reuse the `CrateIDTracker` idea (spatial matching).
- 2027 table anchor tags sit at the **same positions as 2026** (≈ (0.6, 0.6), (0.6, 1.4), (2.4, 0.6), (2.4, 1.4) m,
  read from the table plan). **IDs to read from `Docs/table.svg`.** Their 16-corner PnP method transfers directly.
- Stone tag size isn't stated in the rules. Measure it on the real stones.

---

## 2. Mechanical (Mecanisme_Euro) — main robot 2026
- **Linear rail on a stepper** (AccelStepper, limit-switch homing, 2 pickup positions) carrying **two 3-DOF servo arms**
  (shoulder/elbow/wrist = 6 servos) + **2 rotating internal storage bays** (servo, 180°) + 2 cursor servos.
- **Suction**: 1 pump + 4 solenoid valves (2 on the arms, 2 holding stored crates), via an MCP23017 I/O expander.
- "Hybrid buffer": 2 crates stored inside + 2 held by the arms = 4 carried.
- Control: ESP32 + **Pololu Mini Maestro** (servos, with speed/accel per frame) + CAN node (TWAI) to the RPi + Bluetooth debug.
- Hard-coded multi-servo "frames" for each pose (pick, store, flip…).
- **Lesson**: about 10 servos + rail + pneumatics for 4 crates is far more complex than Aerobotix's one-motor-per-module
  design (2nd place vs our 20th). This supports the "fewest actuators" rule in `mechanical/design-principles.md`.
- **Good practice worth keeping**: a **standalone test firmware per subsystem** (servos only, rail only, pneumatics only,
  full system with and without CAN) and an **HTML manual debug remote** (`Electrique/Mecanisme Manual Debug tool`).

## 3. Navigation (for the software team — Maatoug)
- STM32F407, differential drive, odometry from encoder wheels, **trapezoidal profile + polar PD**, CAN command interface
  to the RPi, 4-level state machine (rotate → forward → rotate-after).
- Docs cover STM32 config, PID tuning, **odometry calibration (after PID tuning)**, quirks (positive angles only;
  target angle 655 = "don't rotate after"), and an **improvement list** (curvilinear trajectories, S-curves, simpler
  state machine, float + FPU).
- Recommended reading inside: Cubot "atelier asservissement", the VRAC "maxi liste ressources eurobot".

## 4. SIMAs (Pami, PAMI_COPILOT) — for Hamza Sammoud
- "Ninja" SIMA: ESP32, 4× quadrature encoders, waypoint state machine (rotate → forward → checkpoint), trapezoid, PID,
  stepper + pump at a waypoint.
- **`Pami/specification.md` has an excellent test procedure**: encoder tuning with braked motors, push 1 m to
  calibrate distance, spin 360° to calibrate rotation, 1 m square test → lifted single waypoint → on the ground →
  full sequence → actuators.
- PAMI_COPILOT: web dashboard with live telemetry over Bluetooth/WiFi. Fine for testing only; it can't be used
  during matches [GR F.6].

## 5. Electrical (Electrique) — for Hamza Bjaoui
KiCad projects: actuator board (V1/V2), power board ("GERBER Puissance IEEE INSAT"), STM32 shield, solenoid valve
controller, SIMA boards (N20 V2, stepper, Ninja), "AKRIVEIA" actuator version. Final boards were made by **JLCPCB** (imported).

## 6. Questions for the previous team
- Did the overhead vision actually run in 2026 matches? With which camera and computer, and where was it mounted?
- Is there a CAD (SolidWorks/STEP) of the 2026 main robot?
- What went wrong at the final (20th)? Their own list of top problems would be very valuable.
