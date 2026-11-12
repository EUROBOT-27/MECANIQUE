# flip-6cups — stone flip with 6 suction cups (FreeCAD)

Rework of **MECANISME_FLIP_V2** (SolidWorks, four-bar flip of a 3-stone stack + 3 ejector fingers) with **6 cups**
instead of 3. Status: **concept CAD + kinematics**, not reviewed, nothing decided (not in `project/decisions.md`).

![both cases](../simulations/flip_6cups/flip6_cases.gif)

## The two cases

| | Case A: 3 stones, **flip allowed** | Case B: 6 stones, **flip locked** |
|---|---|---|
| Load | 1 quarry stack (3 stones), centred on the plate | 2 stacks end to end (gap 10 mm), 650 mm long |
| Cups | all 6: **2 cups per stone**, at its quarter points (u = ±80 mm) → held **from the middle**, balanced | cups 1-3 (left column) hold the left stack, cups 4-6 (right column) the right stack, each stone held **85 mm off its middle** |
| Motion | flip 90° → stones upright 8.8 mm above the table → valves open (drop) → 3 fingers push 19.5 mm → plate returns | no flip; carried as two 330 mm walls, released stack by stack |
| Vacuum | 6 pumps, one per cup; release = pump off + its vent valve opens (in case A all 6 together) | same; cups 1-3 then 4-6 |

**Flip interlock:** the firmware allows `FLIP` only in the *3-stones-centred* mode (set by the strategy when it grabs
one stack with both cup columns). With 6 stones the 650 mm load would hit the table and the robot when turning.
A sensor check can be added later (e.g. a ToF on the base front edge looking past x = ±170 mm: a stone there = 6-stone
mode → no flip).

## Files

| File | What |
|---|---|
| `fc/flip6_params.py` | All parameters + four-bar kinematics (`pose_at(s)`, s = 0 start → 1 upright). Plain Python |
| `fc/flip6_check.py` | `python flip6_check.py` → `motion_report.txt`: clearance, height, transmission angle, pin crossings, torque |
| `fc/flip6_fc.py` | **`freecad flip6_fc.py`** (GUI, closes itself) → `CAD/flip6.FCStd` and `CAD/flip6.step` with the **same parts**: robot + the 3 stones held in front (50 % transparent), coloured, named (e.g. `Suction_cup_DP-S30_1`) and grouped (Robot_base, Flip_drive, Four_bar, Cup_plate, Suction_cups, Ejectors, Vacuum, Stones_3_in_front), `CAD/parts/*.step`, `collision_report.txt`. `freecadcmd` makes the same files but the FCStd opens with everything hidden (no display data) |
| `fc/flip6_gif.py` | `freecad flip6_gif.py` (GUI, closes itself) → `../simulations/flip_6cups/flip6_cases.gif` + stills |
| `CAD/parts/` | column, crank, rocker, plate (STEP, in their own frame) |

Frame = `base_330`: X = wheel axis, Y = forward (mechanism on the +Y edge), Z = up, origin = robot centre on the
table. The model sits on `../base_330/base_330.step` (plate bottom 13.5 mm above the table).

## Mechanism

- **Column**: 5 mm aluminium, standing on the base front edge (y 125-130), 2 angle brackets.
- **Drive** (2026-11-11): **JGB37-520 DC gear motor with Hall encoder, directly on the crank** (no extra stage).
  Gearbox face bolted to the column back (6 × M3), boss in a Ø13 hole, Ø6 D-shaft → crank hub (M3 set screw on the
  flat). The JGB37 output is 7 mm off its body axis: the body sits above the shaft (bottom 38.9 mm, 20 mm over the
  base). Body + encoder 77 mm deep behind the column (y 48…125), same footprint as the old NEMA + gearbox.
  Homing: an **Ender endstop** on the column front, in the crank layer just past the start angle (crank 0.2 mm from
  the switch body at s = 0, the lever is pressed).
- **Four-bar** (synthesised for this load, see below): crank 91 mm (red, y 133-139), rocker 149.2 mm (blue,
  y 142-148), coupler = the cup plate (pins 104.2 mm apart), ground link 204.1 mm. Ground pivots on the column:
  O1 (−34.8, 50.4), O2 (−97.2, 244.7). Crank travel 120°.
- **Plate**: 3 mm aluminium 230 × 290, R12, 5 lightening pockets, **344 g**. 6 × **DP-S30** cups (Ø30 × 18
  bellows, assumed size, same cup as the clapets suction head) in **printed TPU holders** Ø20 × 17 with a side Ø4
  barb (2 columns × 3 rows at u = ±80, v = −110 / 0 / 110), hoses on the front face. Plate face → stone face stays 35.
- **Ejectors**: 3 × **MG90S** (real size 22.8 × 12.2 × 28.5, ears 32.2) lying on the plate front at the edge that is
  at the bottom when the stones stand (as V2), spline pointing out past the edge, in a printed bracket (foot on the
  plate, 2 × M3; wall under the ears, 2 × M2). Finger 25 mm + Ø8 roller, pushes 19.5 mm. Servo 3.4 mm from the
  stone face, 10 mm from the cups.
- **Joints**: Ø8 pins + 688ZZ (8×16×5). The rocker ground pin is a shaft fixed in the column with an **e-clip**
  on the front: the plate sweeps over it with only 4 mm of gap (no screw head there). Cup lock nuts behind the
  plate are 2.5 mm.
- **Vacuum on the base**: 6 × 12 V mini pumps Ø31.8 × 66 (2 layers of 3, axis along Y) + 6 mini 12 V vent valves on
  top, printed rack: **100 × 74 × 85** (x 23…122, y 50…124, z 20…105). 5 mm from the wheel, 2 mm over the base.
  Hoses Ø4 silicone from the plate to the base: leave a loop for the flip (the plate turns 90° and moves ~60 mm).

## Actuators and parts (2026-11-11, from `parts-library.md`)

📦 in library · 🇹🇳 buy locally · ✈️ import. Sizes marked *assumed* come from datasheets: measure ours.

| Job | Part | Qty | Source | Why this one |
|---|---|---|---|---|
| Flip (crank) | **JGB37-520** 12 V gear motor + Hall encoder, **≥ 10 kg·cm rated (≤ ~35 rpm)** | 1 | 📦 (lab has "a bunch", label not read) / 🇹🇳 every robotics shop | Peak 0.97 N·m at the crank → direct drive, no gearbox to import. Encoder → position control; 0.67 s per flip at 30 rpm |
| Homing | Ender endstop (switch on PCB, with cable) | 1 | 📦 (3) | Zero the encoder at the start pose |
| Crank hub | Ø6 D-bore hub with M3 set screw (or printed hub + nut pocket) | 1 | 🇹🇳 (robot wheel hubs) | Clamp the crank on the motor shaft |
| Ejectors | **MG90S** micro servo | 3 | 📦 (≥ 1, count them) + 🇹🇳 | 7.4 N push at the roller vs a 0.9 N stone |
| Cups | **DP-S30** bellows cup | 6 | planned (same order as the clapets cups) | Same spares as the clapets head. Size *assumed* Ø30 × 18 |
| Cup holders | Printed **TPU** holder + side barb | 6 | print | Plan of Maatoug (2026-10-27) |
| Vacuum | 12 V mini pump Ø31.8 × 66, 6 L/min | 6 | ✈️ Lextronic, already arriving | One pump per cup: a cup that leaks on cardboard does not drain the others |
| Release | Mini 12 V 2-way NC vent valve | 6 | 🇹🇳 to check (Arduino shops), else ✈️ | Opens the cup to air: fast drop. *Size assumed* 27 × 14 × 17 |
| Hoses, Y-fittings | Silicone tube Ø4 (check the barb size) | ~3 m | 🇹🇳 | |
| Pivots | Ø8 pins, 688ZZ (8 × 16 × 5) | 4 | 🇹🇳 688 is rare: 608ZZ (8 × 22 × 7) fits if the bosses grow to Ø30 | unchanged from the concept |
| Drivers | 1 DC driver with current sense (e.g. the drive base's type), 3 servo PWM, 6 MOSFET (pumps) + 6 MOSFET (valves) | | 🇹🇳 | tell Hamza Bjaoui: **12 outputs** for the vacuum |

**Conflict to settle:** the 6 Lextronic pumps are also counted for the clapets v2/v8 suction head
(`concepts/clapets-redesign.md`). If both mechanisms go on the robot, buy more pumps, or run the flip on **2 pumps**
(one per cup column: cups 1-3 and 4-6 are the release groups in case B, and all 6 release together in case A).
That loses the per-cup independence.

**Rejected for the flip drive:** a Two Trees NEMA 17 (📦 ×4, ~0.4 N·m holding) needs ≥ 5:1 (the planetary 5:1 of the
concept is ✈️); a GT2 belt sector from the library (20T + printed sector) needs the sector on the far side of the
pulley, below O1 (z 50): 80T (4:1) leaves too little torque margin, 100T (5:1) reaches the base plate. HS-755HB (📦, ~1.3 N·m) or MG996R (0.9 N·m) direct: no margin, and holding 6 stones
off-centre would heat them.

## Results (`motion_report.txt`, `collision_report.txt`)

| Check | Value |
|---|---|
| Floor clearance during the flip (case A) | **7.2 mm** min (V2: 4.4) |
| Stones upright | 8.8 mm above the table, top at 328.8 mm |
| Transmission angle | **49.2°** min (V2: 44°) |
| Torque at the JGB37-520 (direct) | 0.97 N·m peak during the flip (rated 1.0, stall ~2.5 → ×2.6); 0.65 N·m holding 6 stones |
| Flip time | 0.67 s at 30 rpm |
| Ejector push | 7.4 N (MG90S, 29 mm to the roller) |
| Pin crossings (pins through the other link's layer) | ≥ 79 mm from the other bar: OK |
| Solid overlaps | 0 (case A, 21 poses s = 0…1; case B at rest) |

## Open points / to check

- **Height rule during the flip (GR F.3):** a 320 × 330 stack turned in a vertical plane reaches **470 mm** at
  mid-swing; robot + manipulated objects must stay ≤ 350 mm at all times. Same for V2 (it is geometry, not this
  linkage). Only legal if game elements may exceed the limit in construction zones (rules digest, FAQ Q9) —
  ask, or flip only inside a construction zone.
- The original V2 parts could not be opened (saved in SolidWorks 2026; this PC has 2025): the linkage was
  **re-synthesised** (3-position synthesis + local search) and the parts are simplified with the real catalogue
  dimensions. Compare with the V2 parts once someone with SolidWorks 2026 exports them as STEP.
- Case B: nothing lifts the stones off the table (no lift axis), so the 6-stone load is pushed, not lifted.
- Collision check is done every 5 % of the crank travel; refine before freezing.
- Cups on cardboard: check the hold with the real stones (off-centre case B = 0.075 N·m per cup). DP-S30 is
  smaller than the Ø50 of the concept: test one pump + one DP-S30 on a real stone before freezing (hold > 30 s).
- **Read the JGB37 labels** in the lab: rpm and voltage. Faster than ~35 rpm at 12 V = not enough torque
  (peak = rated); a slower version (more reduction) gives more margin and a slower flip. Measure the shaft offset, boss and
  hole circle and update `JGB_*` in `flip6_params.py`.
- The JGB37 spur gearbox is not self-locking: unpowered, the plate falls back towards the start pose (stones on the
  table: harmless). Keep the PID holding during case B.
- Release time with the vent valves: measure. Without valves (pump off only) the cup leaks through the pump: try
  it first, the valves may not be needed on porous cardboard.
- Plate 3 mm aluminium: check the deflection with 6 stones held off-centre.
