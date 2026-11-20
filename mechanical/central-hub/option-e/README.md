# Central hub option E: one shaft per unit, front + back

Status: **concept + box check, proposal** (Ayoub, 2026-11-19). Nothing in `project/decisions.md`.
Same frame as options A–D: X = wheel axis (robot's left = −X), Y = forward, Z = up, origin = robot centre on the table.
**Base since 2026-11-20 = [`base_330_js`](../../base_330_js/README.md), unchanged** (Ayoub: "we can't change the base,
the mechanism should fit the base"): plate 336 × 260, 37D motors on hinges, JSUMO wheels (worst-case envelope Ø80),
the 2 odometry modules (AMT102 + swing arm), 4 KSM15 ball units. The scripts load the real base parts from
`base_330_js/CAD/base_330_js_assembly.FCStd`. **Perimeter limits are ignored in this version** (Ayoub, 2026-11-20):
start perimeter 1248 > 1200, see "On base_330_js" below.
The first version (on `layout-v1`, 300 × 292, perimeter 1176 / 1182) is kept as a snapshot in `CAD_FC/layout-v1/`
(FCStd + STEP + both reports); the sections below marked *(layout-v1)* describe it.
Parts: parts library first, then parts sold in Tunisia, no imports (Ayoub, 2026-11-19).

| File | What |
|---|---|
| `fc/check_e.py` | Doubled design: box check (585 states), perimeter, height, free volumes → `hub_e_report.txt`; `--gif` → `../../simulations/central_hub/option_e_sequence.gif` + `option_e_sheet.png` |
| `fc/hub_e_fc.py` | **FreeCAD model** (`"D:/FreeCad/bin/FreeCAD.exe" fc/hub_e_fc.py`, GUI so the colours are saved, closes itself; `freecadcmd` works without colours): 5 poses `CAD_FC/HUB_E_*.FCStd`, `CAD_FC/HUB_E_HOME.step`, solid clash check → `hub_e_fc_report.txt` |
| `fc/hub_e_hw.py` | Fasteners, loaded by `hub_e_fc.py`: adds them to every pose and cuts their holes; their FreeCAD folders end in `_fasteners` |
| `fc/hub_e_gif.py` | **GIF from the FreeCAD solids** (`"D:/FreeCad/bin/FreeCAD.exe" fc/hub_e_gif.py`, GUI, closes itself): same sequence as `check_e.py`, 1 state in 3 (196 frames), fixed 3D (front-left) + top view → `../../simulations/central_hub/option_e_freecad.gif` + 4 stills `option_e_freecad_*.png` |
| `fc/check_e_doors.py` | First study (single unit with clapet doors) → `hub_e_doors_report.txt`, `option_e_doors_sequence.gif` / `_sheet.png` |

## On base_330_js (2026-11-20, proposal)

What the base forced, all inside the mechanism (the base is untouched):

| Change | Why (base_330_js) |
|---|---|
| **Stack face r 168 → 171** (shaft cup, holder frame + cups, spin servo, horn moved out 3) | the plate edge is at x ±168: a tower set down beside the robot needs 3 mm. Still ≥ 163, so a stone lying at the side clears the other unit's stack |
| **Turret lower arm z 59 → 65.5** (front hub at arm level, no front riser) | the 37D motors reach z 62.5 at x 15–74.5: the arm turns over them at 90° (3.0 mm) |
| **T8 screw circle r 88 → 66**, guide rod at (r 56, t −28.3), bottom pad kept **within r 76 of the axis** | the JSUMO worst-case envelope starts at x 79 (z −3…77): the pad turns over it |
| **NEMA17 beside the screw** at (r 70, t +45) instead of inboard | no room inboard of r 66; at r 70 it stays 3 mm clear of the other unit's carriage when that one is at the side |
| **Carriage block** r 46–80, t −45…12.5, **16.5 above the cup axis, 27.5 tall**; lowest 10 mm only to t 6.5; spin servo + cup hang under it on the drop plate | the cup still reaches the bottom stone (zc 55, block 1 mm over the pad) and the carry pose (zc 290, block 1 mm under the top plate) |
| **Top plate z 333 → 335**, pulleys + belt up to 349.5 | room for the lift above |
| **Turn servos: polar −35 / 145 → −40 / 140**, on the plate (z 16.5); pinion phase now computed (`pinion_rot()`) | the carriage at the bottom stone passed 0.1 mm from its own pinion |
| **Holder slide posts at \|t\| 84–100** (were 92–108), **MG90S + cradle at t 50–73** (were 115–138) | the KSM15 ball-unit holders at (±130, ±105) |
| Column foot sleeve up to the front hub (z 65.5) instead of a bottom collar; cross bolt along Y | a collar there would sit in the motors' back ends (x ±15) |
| Rod: **e-clip DIN 6799-6** under the bottom pad instead of the DIN 705 collar | the collar would turn over the motor |

Results:

| Check | Result |
|---|---|
| Box check, 585 states, 3 mm margin (`hub_e_report.txt`) | **0 clashes**, base parts included (plate, motors, hinges, JSUMO envelope, odometry, ball units) |
| Solid check, 5 poses + 13 extra (`hub_e_fc_report.txt`), with all fasteners and the real base solids | **no clashes** |
| Highest point | **350.0** (top hub clamp collar 340–350; pulleys 349.5) |
| Lowest stone corner during the spin | 4.8 mm |
| Perimeter at start / deployed | **1248 / 1248** (limits 1200 / 1400): **ignored in this version**. The holder frames + cups stick out 41 mm front and back of the 260-long plate; the plate alone is 1192 |
| Free volumes (Grail lift, launcher, pumps) | not checked: they were `layout-v1` reservations |

To pass the start perimeter later, the holders would have to start inside the plate and move out after the start
(sliding or folding), with the turrets parked at the sides; or the base changes (not ours to decide).

## The idea (Ayoub)

The stack is held in front of the robot. **One shaft** goes up and down and turns around the hub. Its suction cup
takes **one stone at a time** to the side, spins 90° and the stone stands up as a tower. Order **top → middle →
bottom**, so every stone of a quarry stack becomes a tower or a gate upright, and none is left lying.

## Why no clapet doors

The first study held the stack with the clapet doors (`check_e_doors.py`). It works for one unit with short doors,
z ≤ 195, each stone lifted above the door tops before it turns. But the doors grip the stone ends, outside the
320 mm stones, so **doubled they break the deployed perimeter** [GR F.3, FAQ Q10]:

| How the stacks are held (300-wide base) | Deployed perimeter |
|---|---|
| Doors front + back, 30 mm grip | 1512 ❌ |
| Doors front + back, 16 mm grip | 1456 ❌ |
| **2 holder cups per lower stone (x = ±100) + the shaft cup on the top stone** | **1182** ✅ (this design) |
| Doors front, holder cups back | 1346 ✅ |
| Front unit only, doors | 1315 ✅ |

The holder cups come in **pairs, symmetric about the stone centre**. That is the fix for option B's blocker, where a
single off-centre cup let the stone twist.

## The design (per unit; the rear unit is the front one turned 180°) *(layout-v1)*

| Part | What / where | Source |
|---|---|---|
| **Column** (shared) | 20 mm aluminium tube on the floor, z 26–350; the **beacon support** (80 × 80, top 430) sits on top [GR F.6] | 🇹🇳 |
| **Turret** | bottom + top plate turning on the column (printed bushings): hub, spoke, pad. Front plates z 59–64 / 333–338; rear hubs stepped (68–73 / 324–329) with a riser to the same arm level | printed ABS (D-023) |
| Turn drive | **MG996R** + printed 2:1 gear pair (180° servo → 90° turret), hard stops at 0° / 90°. Front: robot's left; rear: robot's right | 📦 / 🇹🇳 |
| Lift | **T8 lead screw** at r 88 + **8 mm guide rod** at r 88, t +30; **NEMA17** inboard (r 32–74) under the top plate, **GT2 belt 1:1** over the top plate (z ≤ 347); endstop for homing | 📦 (screw, nut, rod, NEMA, belt, endstop), 🇹🇳 (8 mm bore pulley, LM8UU) |
| Carriage | printed block on the brass nut + LM8UU (r 76–106), holds the spin servo | printed ABS |
| Spin | **MG996R** (r 106–144), cup shaft on 2 small bearings, hard stops at 0° / 90° | 📦 / 🇹🇳 |
| Shaft cup | **VS2-S30** + VW7-M5, face at r 168 | 📦 |
| **Holder frame** | 2 printed columns at x = ±100 on a crossbar, **one VS2-S30 per lower stone on each column** (4 cups), lifted 15 mm by an **MG90S** + crank to carry the stack | printed / 📦 |
| Pumps | 3 per unit: 1 for the shaft cup, 1 per holder pair (both cups of a stone vent together) + a 12 V vent valve each | 📦 (6 pumps) / valves 🇹🇳 (check) |

**Motors: 2 NEMA17 + 4 MG996R + 2 MG90S = 8**, plus 6 pumps. Cups: 10 = the pack of 10 we have.
Guide rods: 2 (lift). Holder slides: printed (we have ~6 rods, keep them for the lifts).

**Why these numbers:**
- **Stack face r 168:** a stone lying beside the robot (y ±160) must clear the other unit's stack (y −168…).
  On a 300-wide body the tower stands 18 mm off the side.
- **Screw circle r 88:** with the turret at the side, the bottom pad (r ≤ 98) clears the wheel (x 102).
- **NEMA inboard:** beside the screw, it swung into the launcher / Grail space at the end of the turn.
- **Stones turn at z 250** (top stone at 283): bottom face 195, above the holder cups (top 180). Below that, the
  stone's near face turns into the holder cups of its own unit.

## Sequence (one unit; the other holds its stack meanwhile)

1. Carry: holder cups on the 2 lower stones, shaft cup on the top one, holders + carriage up 15 mm.
2. Set down. **Top**: lift 8 mm, turn 90°, down to 174, spin 90° (stands up), down to 160 (on the table), vent.
3. Cup spins back and rises along the tower face to 250, turret turns back (the cup slides off the face).
4. Cup down to the next stone, its 2 holder cups vent, lift to 250, same as 2–3. Then the bottom stone.
5. The robot drives on (≥ 0.34 m) between towers, holders up 15 mm.

## Results *(layout-v1; now `CAD_FC/layout-v1/hub_e_report.txt`)*

| Check | Result |
|---|---|
| Box check, 585 states (front builds 3 towers while the rear holds, then the rear), 3 mm margin | **no clashes** |
| Highest point, robot + held stone (the column is the beacon mast [GR F.3]) | **347.0 mm** (≤ 350) |
| Perimeter at start | **1176 mm** (≤ 1200) |
| Perimeter deployed (both turrets out, holders up) | **1182 mm** (≤ 1400) |
| Lowest stone corner during the spin | 4.8 mm |
| Grail lift / launcher volumes | **never entered** by any part or stone |

**Free volumes** (`option_e_sheet.png`, yellow / red / grey):

| Volume | Where | Size |
|---|---|---|
| Grail lift (front-right), above the right wheel | x 82..146, y 22..110, z 78..330 | 64 × 88 × 252 (1.42 L; `layout-v1` side bay: 84 × 80 × 222) |
| L4 roof pad | x 76..150, y 26..122, z 330–335 | 74 × 96 (Grail 70 × 70) [G E.2] |
| Launcher (rear-left), above the left wheel | x −146..−82, y −110..−22, z 78..330 | 64 × 88 × 252 (1.42 L) |
| Pumps, 3 per unit | x ∓146..∓112, z 78..113, beside the swept quarters | 34 × 90 × 35 |

The other two quarters (front-left, rear-right) are swept by the turrets above z 59. Battery and electronics have to
go low in the body (under z 59 between the drive motors) or in the core near the column; **not checked yet**.

## FreeCAD model (`fc/hub_e_fc.py`, 2026-11-19) *(layout-v1 numbers)*

All numbers come from `check_e.py`. Printed parts are plain blocks with their holes, **drawn blue**, bought parts are
outer shapes, gear teeth are trapezoidal. **Every screw, nut, washer, insert and collar is drawn** (`fc/hub_e_hw.py`,
2026-11-20), with its holes, counterbores and nut pockets cut into the parts; see "Fasteners" below.

| File | Pose |
|---|---|
| `CAD_FC/HUB_E_HOME.FCStd` (+ `.step`) | both stacks set down, shaft cups on the top stones, holder cups on the lower ones |
| `CAD_FC/HUB_E_1_FRONT_TOP_TURN45.FCStd` | front top stone lifted 8, turned 45°; rear holds its stack |
| `CAD_FC/HUB_E_2_FRONT_TOP_SPIN.FCStd` | front top stone at 90°, spinning (45°) |
| `CAD_FC/HUB_E_3_REAR_MIDDLE_UP.FCStd` | rear middle stone stood up beside the robot, rear top tower 340 mm behind |
| `CAD_FC/HUB_E_DEPLOYED.FCStd` | both turrets at 90°, cups spun, holders up: perimeter envelope (FAQ Q10) |

Groups in each file: robot base, column + beacon support, per unit turret / carriage / holder / fixed drives, stones,
reserved volumes (transparent). **Solid clash check: no clashes in the 5 poses + 13 extra poses** (carry, each
middle stone at 15/30/60/75°, cup at the bottom stone, bottom stone set down); highest 348.0 mm since the fasteners (the top hub clamp collar, z 338–348); perimeter 1176–1182.

What the real shapes changed in the layout (the box model follows):
- **Turn drive:** 60 T gear sector (m 1, pitch r 30) on each turret hub + 30 T pinion on the turn MG996R, shaft 45
  from the axis at polar −35° (front) / 145° (rear), where no riser ever passes. The gears sit above the drive motors.
- **Hubs stacked on the column:** front hub z 66, gear 72–77; rear hub z 80, gear 86–91. Both turrets' arms stay at
  z 59–64 (the carriage must reach the bottom stone), joined to their hub by a web (r 15–34) and a riser at r 34–40.
- **Top:** front hub z 333, rear z 324 with its riser beside the NEMA (t −30..−20). NEMA17 at r 34–76.
- **Rear turn servo on the floor** like the front one (2026-11-20; it was on a 3 mm block, before that 14 mm, where its ears were 1 mm inside the rear riser). On the 3 mm block its ear screw heads hit the rear arm.

## Fasteners (`fc/hub_e_hw.py`, 2026-11-20, proposal)

Rules from `mechanical/design-principles.md`: M3 heat-set inserts K6 L6 (hole Ø5.4, blind 7, wall ≥ 1.6), nut pockets
6.0 × 6.9 × 2.8 open to free air, servo ears on nuts under a 1.6 roof, clamps coupler style, spacers as bosses on a part.

| Joint | Fasteners | Notes |
|---|---|---|
| Column → base plate | printed **column foot** (flange r 24 + sleeve r 13.5 up to the front hub, z 65.5): 4 × M4×20 + washers + nyloc under the plate; **M4×40 cross bolt along Y** through sleeve + tube (drill Ø4.4) + nyloc | the column can't turn or lift |
| Turret hubs on the column | the foot sleeve under the front bottom hub; 1 printed **clamp collar** (Ø40 × 10, slot + M3×16 across it, nut in a pocket) over the front top hub (z 340–350) | spacers are **bosses**: rear bottom hub (z 77–80) on the front gear, front top hub (z 332–335) 1 mm over the rear top hub |
| Beacon support → column | printed plug in the tube top + M4 insert, M4×12 down through the support's base disc | |
| NEMA17 → top plate | 4 × M3×10 + washers (31 mm square) | rear top spoke now starts at r 31 (its riser) so the inner screws have plate under them |
| Guide rod | **DIN 705 collar Ø8** (D16 × 8, M4 set screw) over the top pad + **e-clip DIN 6799-6** under the bottom pad (groove in the rod) | |
| T8 brass nut → carriage | 2 × M3×18 down through the flange (PCD 16) + M3 nuts in pockets near the block bottom, open to the −r / +r faces | inserts don't fit: the flange holes are 8 from the screw axis. Nut modelled at its real 15 mm |
| LM8UU → carriage | bearing on a ledge, **clamp**: slot to the −t face, M3×20 across along r, nut pocket open to −t | |
| Spin MG996R → carriage drop plate | 4 × M3×12 + washers + nuts | |
| Turn MG996R → floor | 2 printed **posts** under the ears, 4 × M3×8 + nuts under a 1.6 roof; each post 1 × M3×12 from under the floor into an insert | **rear servo now on the floor too** (no 3 mm block): on the block its ear screw heads hit the rear arm at z 59 |
| Turn pinion | servo horn → printed pinion hub with the 2 M2 self-tapping screws of the servo kit (from under the horn, before it goes on the spline), then M3×25 (front) / M3×40 (rear) + washer down the pinion bore into the spline | the steel shaft of the first model is gone |
| Holder slide posts → floor | each post has a foot inboard; 2 × M3×12 from under the floor into inserts | |
| Holder MG90S | printed **cradle** (2 × M3×12 from under the floor into inserts), ears on 2 × M2×8 + M2 nuts under a 1.6 roof | |
| Holder cups → frame | VW7-M5 hex in a Ø15 counterbore, M5 nut in a pocket open to the column's side face | |

**Count (both units, base_330_js):** 155 parts, all metric standard (📦 / 🇹🇳); the list by size is at the end of
`hub_e_fc_report.txt`. Clash check with all of them: see that report.

## Open points

1. **Not drawn yet:** the holder lift crank + link, the hard stops (turret, spin), the cup shaft bearings and the shaft
   cup's fixing (the cup sits on the servo horn in the model), the dovetail of the holder slides, cable and hose
   loops, the pulley set screws, the T8 screw's lower end (it hangs from the 608 + pulley).
2. **Worst-case stones (324 × 115 × 115):** a stack is 345 tall, so lifting the top stone 8 mm makes 353 > 350.
   Lift it only 3 mm (unpinch), then turn. Re-run the check with the worst size.
3. **The cup slides off the tower face** when the turret turns back (vacuum off). Test that a 90 g tower doesn't
   move. If it does, add a few mm of radial retract on the cup.
4. **The rising stone slides past its vented holder cups** (bellows cups touch the face). Check the cup lip doesn't snag.
5. **Vent valves:** 6 × 12 V. Check they can be bought in Tunisia, otherwise use the pump-off + bleed hole.
6. **Battery, electronics, pumps:** place them for real (`layout-v1`, `robot/`).
7. **Changes Seif's layout:** the Grail lift and the launcher move from the side bays to the front-right / rear-left
   quarters, and there is no clapets module (no doors).
8. **Time:** about 5 s per stone + a drive between towers; both units can work at the same time if two tower zones
   are on either side of the robot.
9. **FAQ:** may the holder cups drag a stack? (Here the holders lift 15 mm, so no dragging.)
