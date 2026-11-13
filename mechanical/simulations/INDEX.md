# Simulations and videos

All mechanism animations, motion studies and simulation videos are kept here (copies; the scripts that make them
live with each design in `C:\Projects\EUROBOT\Mecanique\`). New ones go in a subfolder per study.

| Folder | Files | What | Source (scripts / originals) |
|---|---|---|---|
| `clapets_poc/` | `clapets_poc_motion.mp4`, `.gif`, `motion_report.txt` | Clapets PoC 2 (Two Trees lift, v1-layout doors, ×2 gears): doors open −21° → clamp +2.8° → lift 15 mm with the stack → lower → release. Report = collision check over the 91 frames. 2026-10-28 | `Mecanique/module_clapets_poc/fc/motion_fc.py` |
| `clapets_poc/` | `clapets_poc_door_range.mp4`, `.gif`, `door_range_report.txt` | Full door range, **no stack**: rest → fully open (−47°) → fully folded (+94°) → rest; pinion turns −2×. Report = limits found by a 1° collision sweep. 2026-10-28 | `Mecanique/module_clapets_poc/fc/door_range_fc.py` |
| `clapets_v5/` | `clapets_v5_motion.mp4/.gif`, `motion_report.txt`, `v5_*.png` | **Clapets v5 (reference design, D-017)**: module A (lift + doors) + module B (suction head). Full match cycle: doors unfold → clamp → carry → cups hold, doors open −38° → lift 75 → turn the stack 90° → set down → release → fold. Report: 0 collisions, module A never in the head's turning disc, start 1200 mm / deployed ≤ 1367 mm / height ≤ 347.7 mm. Close-ups: `v5_aile_D*.png` (door unit body + cap), `v5_support_ecrou.png`, `v5_support_tete.png` (on the real plate). 2026-10-29 (finalizing pass) | `Mecanique/module_clapets_v5/fc/motion_v5.py` |
| `clapets_v7/` | `cycle_moduleA.gif`, `doors.gif`, `door_sweep_report.txt` | **Clapets v7, module A only** (D-022 door unit, no module B). `cycle_moduleA.gif`: folded → doors open → stack appears → grab → lift 75 mm → lower → release (side + 3D split view). `doors.gif`: doors only, fold → open −38° → clamp +3° → fold (top + 3D). Report: fast door sweep, no contact over the travel, folded door sheet meets the head carrier only past +93.25°. 2026-11-10 | `mechanical/clapets-v7/fc/cycle_gif_v7.py`, `door_gif_v7.py`, `motion_v7.py` (`V4_MODE=doors`) |
| `flip_6cups/` | `flip6_cases.gif`, `flip6_*.png` | **6-cup flip** (rework of MECANISME_FLIP_V2): case A, 3 stones held from the middle → four-bar flip 90° → drop 8.8 → fingers push 19.5 → return; case B, 6 stones (2 stacks) held off-centre, flip locked. 3D + front view. 2026-11-10; real actuators (JGB37-520, MG90S, DP-S30, 6 pumps + valves) 2026-11-11 | `mechanical/flip-6cups/fc/flip6_gif.py` |
| `levage_rotation_flip/` | `V2_FINAL.mp4/.gif`, `A2_up.mp4/.gif`, `A2_down.gif`, `FLIP.mp4/.gif` | Stone lift + rotation (flip) mechanism studies, earlier work | `Mecanique/simulation/levage_rotation/` |
| `mecanisme_sammoud/` | `GATE_*.gif` (5 variants), `TOUR_H160.gif`, `TOUR_H172.gif`, `sammoud_robot_B.mp4` | Gate and tower variants of the "Sammoud" mechanism, earlier work | `Mecanique/simulation/mecanisme sammoud/`, notes in `Mecanique/ANALYSE_mecanisme_sammoud.md` |
| `simulation_general/` | `anim_*.gif` (3), `sw_actuel.gif`, `sw_v2.gif` | Earlier sequencing / SolidWorks animations (current vs v2) | `Mecanique/simulation/out/` |

The earlier studies (all but `clapets_poc/`) were copied as they are and have not been reviewed in this hub yet.
