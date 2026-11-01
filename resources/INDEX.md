# Resources index

Reference material from previous Eurobot teams (mechanical + software). **Read this index first**, then open only
the resources that match the task. Never browse this folder blindly: it's large and reading it costs tokens.

How it works:
- Seif drops material into `mechanical/` or `software/` (any format: PDFs, CAD, repos, images, links).
- When asked to "index the new resources", Claude skims each new item **once** and adds one row below.
- When a resource gets studied in depth, Claude writes the findings to `_notes/<resource-name>.md`, so it never
  has to be re-read from scratch. The Notes column links to it.
- **Everything here is committed to git as a snapshot** (D-018): cloned repos are copied without their `.git` folder
  and without build output / caches. To refresh one, clone the source again outside the hub and copy it over.
  Stored in normal git, not LFS (`resources/.gitattributes`).

Tags: `drive` `gripper` `lift` `stacking` `launcher` `chassis` `beacon` `sima` `electronics` `localisation`
`vision` `aruco` `ros` `navigation` `strategy` `poster` (add more as needed)

## Aero Euro — Aerobotix INSAT, Eurobot 2026 (`Aero Euro/`)

Source: github.com/Eurobot-2026-Aerobotix, shallow clones taken 2026-10-25, committed as a snapshot 2026-11-01.
Descriptions below come from GitHub; rows marked *not skimmed* haven't been opened yet. Note: 2026 called SIMAs "PAMI".

| Resource | What it is | Useful for | Tags | Notes |
|---|---|---|---|---|
| `NINJA_MECANIQUE/` | "conception ninja version finale" — final robot mechanical design | mechanical reference (chassis, mechanisms) | `chassis` `drive` | *not skimmed* |
| `Robot-CAD-Teardown.pdf` | 18-p teardown of the final 2026 robot CAD: drivetrain, 8 suction modules on MGN12 rails, pneumatics, frame, electronics | chassis architecture, drivetrain, odometry, suction picking | `chassis` `drive` `gripper` `electronics` | [studied](_notes/aerobotix-2026-robot.md) |
| `ppp_eurobot2026_EN.pdf` | 48-p academic report on the 2026 robot (2nd at European final): concepts A–D, design, BOM, ROS 2 architecture, vision/ArUco, tests | design process, BOM, vision, results | `chassis` `gripper` `vision` `aruco` `ros` `strategy` | [studied](_notes/aerobotix-2026-robot.md) |
| `Pickaboo/` | no description | ? | | *not skimmed* |
| `D-MAX-t-l-guid-/` | no description (tiny) | ? | | *not skimmed* |
| `PCBs/` | all PCB schematics | electronics reference for Hamza Bjaoui | `electronics` | *not skimmed* |
| `System_code_ESP32_front/` | ESP32: position control for 4 N20 motors + 3 servos | actuator control | `electronics` | *not skimmed* |
| `System_code_ESP32_back/` | ESP32 back-side system code | actuator control | `electronics` | *not skimmed* |
| `System_Code_ESP32_pneumatic/` | ESP32: 8 electrovalves + 2 pumps | suction/pneumatic grippers | `gripper` `electronics` | *not skimmed* |
| `PAMI_ESP32_code/` | ESP32 navigation + communication for the PAMI (SIMA) | SIMAs | `sima` | *not skimmed* |
| `ROS2-WS-EURO/` | ROS 2 workspace: strategy, Hybrid A*, perception, micro-ROS | software, perception | `ros` `navigation` `vision` `strategy` | *not skimmed* |
| `Navigation_MicroROS_2026/` | navigation with micro-ROS | software | `navigation` `ros` | *not skimmed* |
| `LIDAR_EUROBOT/` | obstacle detection with LD19 lidar | avoidance system (mandatory) | `localisation` | *not skimmed* |
| `Eurobot_Dashboard/` | dashboard: strategy selection, system tests, navigation visualisation | testing tools | `strategy` | *not skimmed* |
| `Serial_plotter/` | no description (tiny) | debugging tool | | *not skimmed* |
| `.github/` | org profile page | — | | |

## INSATEURO2026 — IEEE RAS INSAT previous team, Eurobot 2026 + ENSI 2025 (`INSATEURO2026/`)

Our own club's handed-down material: 17 repos, shallow clones taken 2026-10-25 (snapshot committed 2026-11-01). **All studied →
[notes](_notes/insateuro2026.md)** (repo-by-repo table, vision post-mortem, lessons). 2026 result: 20th at the final.

| Resource | What it is | Useful for | Tags |
|---|---|---|---|
| `Euro_vision/` (+ `full_pipeline/POST_MORTEM.md`) | Overhead ArUco vision system, Kalman, extrinsics, strategy | **vision** | `vision` `aruco` `localisation` `strategy` |
| `ROS2_EURO_VISION/` | ROS 2 vision node + LiDAR/vision fusion + YDLidar | vision, avoidance | `vision` `ros` `localisation` |
| `Navigation/` (docs/) | STM32 navigation, odometry calibration | software team | `navigation` `drive` |
| `Mecanisme_Euro/` | 2026 mechanism firmware (rail + 2 arms + storage + suction) | mechanical lessons | `gripper` `electronics` |
| `Pami/`, `PAMI_COPILOT/` | SIMA firmware, test procedure, telemetry dashboard | SIMAs | `sima` |
| `Electrique/` | KiCad boards (JLCPCB) | electrical team | `electronics` |
| `EURO_ROS2/`, `Ros2_Vision/`, `Lidar/` | ROS 2 workspace, early vision, YDLidar X2 | software team | `ros` |
| `HARDWARE-CAD/`, `Computer_vision/`, `ROS1-Ensi/`, `ros2-ensi/`, `Simulation/` | **ENSI 2025**, not Eurobot | low | |

## Mechanical

| Resource | From (team, year) | What it is | Useful for | Tags | Notes |
|---|---|---|---|---|---|

## Software

| Resource | From (team, year) | What it is | Useful for | Tags | Notes |
|---|---|---|---|---|---|

## CDR-2027 — Barbatronic / Karibous, Coupe de France 2027 (`CDR-2027/`)

Source: github.com/Barbatronic/CDR-2027, commit `91f057e` (2026-10-28), committed as a snapshot 2026-11-01. FreeCAD CAD + Jekyll journal + firmware.

| Resource | What it is | Useful for | Tags | Notes |
|---|---|---|---|---|
| `MCAD/actuator-parts/suction-cup-prototype.FCStd` | 1 cup per box, 3 drop-in stations at 110 mm pitch, TPU spiral-spring disc + clamp ring + M5 adapter | suction head design | `gripper` | [studied](_notes/cdr-2027-barbatronic.md) |
| `MCAD/actuator-parts/box-manipulator.FCStd` (+ 3mf, laser svg) | servo arm with a roller on the box | — | `gripper` | [studied](_notes/cdr-2027-barbatronic.md) |
| `MCAD/` (other) | differential chassis, launchers, electronics supports | chassis / launcher reference | `chassis` `launcher` | *not skimmed* |
| `DOCS/_posts/` | journal: game elements, gate/tower tests, ball launchers | game-element behaviour | `stacking` `launcher` | [studied](_notes/cdr-2027-barbatronic.md) (posts to 2026-09-29) |
| `FRW/Differential-Robot-Firmware/` | robot firmware (PlatformIO) + FreeCAD simulator macro | software reference | `navigation` | *not skimmed* |
