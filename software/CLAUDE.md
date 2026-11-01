# Software — context

Read the root `CLAUDE.md` and `project/rules-digest.md` for the full picture. This file holds what matters when
working on software. In scope since 2026-10-27 (D-013).

## Team
- Lead: Maatoug.
- ROS: Fradi, Loumi. Navigation: Ben Azza, Nesrine.
- CV: Seif (vision station, opponent tracking). Electrical: Hamza Bjaoui. SIMAs/PAMIs: Hamza Sammoud.

## Code
- Simulation: `eurobot2027/Simulation-Euro27` (ROS 2 Jazzy + Gazebo, from the GitHub org **EUROBOT-27**).
  Start with its `README.md`, `SETUP.md`, `PLAN.md`; team code lives in `team/`. `git pull` to refresh.
- Our robot model there: `src/eb27_description/robots/excalibot/` (robot.yaml + CAD mesh). New CAD exports go
  through `tools/import_cad.sh`, so fabrication CAD and the sim model should stay in sync.

## Decisions that drive software
- Differential drive, 2 × Pololu 4742 (D-004).
- Opponent tracking = LiDAR + vision (D-007). LiDAR mounting height decides what it sees (SIMAs ≤ 175 mm are below a mast LiDAR).
- Overhead camera + laptop on the **remote computing device** at the table edge, wireless link to the robot;
  the software team chooses the wireless technology (D-008).
- Strategy and build order: D-009, D-010 (`project/strategy.md`).

## Rules that are software's job (details + references in `project/rules-digest.md`)
- Match 100 s; start by pulling the 500 mm cord; robot must stop by itself at the end.
- Avoidance system mandatory.
- Attack phase (SIMAs, cannonballs) only from 85 s to 100 s.

## Working conventions
- Notes and designs for a software topic: `software/<topic>.md`. Choices go to `project/decisions.md`.
- Interfaces with CV and electrical (message formats, frames, rates, wireless link) are written down here once agreed.
