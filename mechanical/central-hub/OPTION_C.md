# Central hub option C: one transfer servo per level + one spin servo per cup

Status: **concept, proposal** (Ayoub, 2026-11-18). Not reviewed by Seif. Nothing in `project/decisions.md`.
Check: `fc/check_c.py` → `hub_c_report.txt` + `../simulations/central_hub/option_c_sheet.png` and
`option_c_sequence.gif` (plain Python, boxes + cylinders, not a FreeCAD model yet). Robot: **base_330_js**.
Same frame as options A/B: X = wheel axis (robot's left = −X), Y = forward, Z = up, origin = robot centre on the table.

## The idea

Back to the first sketch: **one movement takes a stone from the stack to the spin-safe position beside the robot**,
then **a servo on the cup stands it up**. One actuator does the transfer and one does the spin. What failed before was
how the transfer was made (a steep groove, crossing sleeves, slides, off-centre holder cups), so option C changes that:

- **Each level has a ring** on the hub, turned 0 → 90° by **one MG996R** (transfer servo). Like option A, each ring
  carries the **front and the rear arm** (180° apart), so one turn places a front stone on the robot's left and a rear
  stone on its right.
- **The arm is a parallelogram** (2 links of 81.3 mm, 30 mm apart), so the cup and the stone stay level all the way.
  **The link angle is tied to the ring turn**, so the same servo also moves the stone up or down, along one arc:

| Level | Stone centre (stack → side) | What ties the height to the turn |
|---|---|---|
| Top | 275 → 160 (down 115) | **Drag link**: a rod with 2 ball links, from a stud on the lower link (50 from the root pivot, 30 to the side) to a fixed stud on a spine bracket (polar 80°, r 70, z 320). Rod 157 mm. |
| Middle | 165 → 165 (the cup holds it 5 mm below its centre, at 160) | Nothing: rigid arm, plain turn |
| Bottom | 55 → 160 (up 105) | **Ramp cam**: a 22 mm lever behind the lower root pivot carries a roller (623ZZ) that rolls **under** a fixed ramp on the spine (r 40–54). The weight of arm + stone presses it up onto the ramp; a lip under it is only a safety. Steepest ramp 34°. |

A drag link does not fit the bottom level. The rod would need an anchor below the bottom arm (that is the bridge
over the drive motors), or it would climb through the top arm. The ramp keeps all of the bottom level inside its own
band.

- **Cups end at z 160** (hub frame) at turn 90, **cup faces at r 176** at both ends of the turn.
- **Spin, as option B:** each cup sits on its own short shaft in 2 ball bearings, the servo (MG90S, or MG996R if
  the test says so) only gives torque through its horn, and a pin in a 90° slot gives hard stops.
- **Hub lift:** the spine with the 3 rings (and the anchor + ramps) slides 0–20 mm on the fixed mast, raised by **one
  MG996R + crank** under the bridge plate. Pick at 0, carry walls at 12, transfer + spin at 14 (cup 174), set down at 0.

## Sequence (both units together)

1. **Pick:** hub at 0, every arm at turn 0, drive the cups onto the stack faces, vacuum on. **Wall:** hub to 12, carry,
   set down at 0, vent. No transfer needed.
2. Hub to 14. **Unpinch:** top and bottom rings turn back to −3°. The top stone goes up 3.4 (drag link) and the bottom
   one down 3 (ramp dip), so the middle stone leaves without rubbing.
3. **Middle:** turn 0 → 90, then top and bottom rings back to 0. Spin 90°, hub to 0 (the tower stands on the table),
   vent, turn back.
4. **Bottom:** hub to 14, turn 0 → 90 (rises fast first: +32 mm by 15°, over the plate corner), spin, hub to 0, vent,
   turn back.
5. **Top:** same (it goes down only once the bottom stone has left, so it never comes down onto it).
6. The robot drives ≥ 0.34 m between levels (Gazebo, option A).

## What it fixes

| Problem found before | Where | Option C |
|---|---|---|
| Groove 77° steep at the start: a turn jams | grooved hub | Top: no groove (rod). Bottom: the lever makes the roller travel only 2 × 22 sin 40° = 28 mm over the turn, so the ramp is at most **34°** (rule of thumb < 45°) |
| The 3 sleeves collide where the grooves cross (118 clashes) | grooved hub | One ring per level, each in its own band (bottom 131–141, middle 146–156, top 184.5–194.5), only one level turns at a time: **0 clashes** |
| 4 printed slides cantilevered 143 mm, N20 + M4 screws (~33 s a stroke), 13 motors | option A | No slides: the height comes from the turn. **10 motors** (3 transfer + 6 spin + 1 lift) |
| Middle stone dropped 15 mm | option A | Every cup ends at 160; the hub lowers 14 and every tower is **set on the table** |
| Holder cups grip 100 mm off the stone centre (blocking) | option B | No holder cups: **each stone stays on its own arm cup at the middle of its face** from pick to set-down (the middle cup is 5 mm low, inside the ±5 stone tolerance) |
| MG90S spline carries the stone, no stop | option A | Cup on a bearing shaft, hard stops (from B) |
| Bottom slide hits the wheels | option A on base_330 | Checked on base_330_js (wheels Ø80 envelope, odometry modules, bridge): clear |
| "Top first" presses the top stone into the middle one | grooved hub | Order middle → bottom → top + 3° unpinch |
| Cup pushes the tower when the arm turns back | A, B | Both transfers **dwell** at the end: the first 10° of the return move the cup only 1.1 mm toward the tower |
| Tower 2 mm from the plate edge | first run of C | Cup face at r 176 → tower 8 mm off the base_330_js plate (x 168) |

## Result of `fc/check_c.py` (404 states, both units)

| | |
|---|---|
| Clashes | **none**, and nothing closer than 3 mm (arms, rods, ramps, rings, servos, spine, stones, towers, plate, bridge, drive motors, wheels, odometry, lift servo) |
| Height | everything ≤ **347.4** (the top stone during the unpinch, hub at 14) [GR F.3] |
| Spin at cup 174 | nominal stone 4.8 … 343.2; worst 324 × 115: 2.1 … 345.9; middle (cup 5 low) worst 3.7 … 347.6 |
| Top drag link | links +45 → −45°, worst transmission angle **31°** (keep > 30) |
| Bottom ramp | steepest 34°; end dwell 1.2° of link over the last 10° of turn |
| Perimeter [GR F.3] | start **1249** (> 1200: the base_330_js plate alone is 1232, and the cups stick out 36 mm front and back); deployed 1233 (≤ 1400) |

## Parts (concept level)

| Part | Qty | Source |
|---|---|---|
| MG996R: transfer (one per ring) + hub lift | 3 + 1 | 📦 (count them, library says ≥ 1) / 🇹🇳 |
| Spin servo MG90S (MG996R if too weak) | 6 | 📦 ≥ 1 / 🇹🇳 |
| Spin shaft: 2 small bearings per cup (MR/623 class) | 12 | 📦 lab small bearings (~8) / 🇹🇳 |
| Parallelogram pivots: M3 shoulder screws or M3 + bushes, 4 per arm | 16 | 📦 / 🇹🇳 |
| Ball links M3 (RC car type) + M3 rod 157 mm, top level | 2 rods, 4 links | 🇹🇳 RC shops |
| 623ZZ roller + M3 pin, bottom level | 2 | 📦 / 🇹🇳 |
| Rings (gear Ø~112) on the spine: printed races + 6 mm steel balls, or a thin bearing | 3 | 🇹🇳 (thin-section bearing likely ✈️) |
| Fixed mast + lifting spine, ramps, arm parts, brackets | | printed ABS (D-023) |
| VS2-S30 cups + 12 V pumps (one per cup) | 6 + 6 | 📦 ordered (Seif, 2026-11-13) |

## Open points

1. **Stack height with worst-case stones [GR F.3].** Each stone is held at its nominal height, but a stack of three
   115 mm stones is 345 tall: lifted 14 + unpinch, the top stone would reach ~362. Measure the real stones (RAJA,
   ordered). If they are tall, carry at ≤ 5 mm and spin with the cups lower.
2. **Start perimeter 1249 > 1200:** the cups stick out of base_330_js front and back (face r 176). The final footprint
   (layout-v1 / robot/) must take the hub into account.
3. Top drag link at **31°** worst transmission angle: OK on paper, check the force in the rod and the ball links once
   the arm mass is known.
4. **Release:** the dwell removes the push, but the cup still slides 30–40 mm along the tower face when the arm turns
   back (same as A and B). Test on real stones.
5. Engaging the stack: the robot drives the cups onto the faces (front unit forward, rear unit backward into a second
   stack). Bellows cups take ±5 mm.
6. Ring bearing, spine-on-mast guide, lift crank, cable + hose loops (3 rings × 90° + the spin), servo gears:
   not modelled.
7. Strategy (from option B): a team has 4 tower zones [G D.4], so 6 towers is more than can score. If 4 are
   enough, the bottom level can stay a holder only (no transfer, no ramp, no spin): 2 servos fewer.
8. Gate lintel: not covered (as A and B).
9. Next step if Seif agrees: FreeCAD model `fc/hub_c_fc.py` with real parts (MG996R/MG90S, bearings, ball links,
   fasteners), then the Gazebo sim.
