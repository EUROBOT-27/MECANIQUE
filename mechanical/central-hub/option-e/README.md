# Central hub option E: one shaft per unit, front + back

Status: **concept + box check, proposal** (Ayoub, 2026-11-19). Nothing in `project/decisions.md`.
Same frame as options A–D: X = wheel axis (robot's left = −X), Y = forward, Z = up, origin = robot centre on the table.
Base = `layout-v1` body **300 × 292, chamfer 30** (Seif), JSUMO wheels, 4 KSM15 casters.
Parts: parts library first, then parts sold in Tunisia, no imports (Ayoub, 2026-11-19).

| File | What |
|---|---|
| `fc/check_e.py` | Doubled design: box check (585 states), perimeter, height, free volumes → `hub_e_report.txt`; `--gif` → `../../simulations/central_hub/option_e_sequence.gif` + `option_e_sheet.png` |
| `fc/hub_e_fc.py` | **FreeCAD model** (`"D:/FreeCad/bin/FreeCAD.exe" fc/hub_e_fc.py`, GUI so the colours are saved, closes itself; `freecadcmd` works without colours): 5 poses `CAD_FC/HUB_E_*.FCStd`, `CAD_FC/HUB_E_HOME.step`, solid clash check → `hub_e_fc_report.txt` |
| `fc/hub_e_gif.py` | **GIF from the FreeCAD solids** (`"D:/FreeCad/bin/FreeCAD.exe" fc/hub_e_gif.py`, GUI, closes itself): same sequence as `check_e.py`, 1 state in 3 (196 frames), fixed 3D (front-left) + top view → `../../simulations/central_hub/option_e_freecad.gif` + 4 stills `option_e_freecad_*.png` |
| `fc/check_e_doors.py` | First study (single unit with clapet doors) → `hub_e_doors_report.txt`, `option_e_doors_sequence.gif` / `_sheet.png` |

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

## The design (per unit; the rear unit is the front one turned 180°)

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

## Results (`python fc/check_e.py`, report `hub_e_report.txt`)

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

## FreeCAD model (`fc/hub_e_fc.py`, 2026-11-19)

All numbers come from `check_e.py`. Printed parts are plain blocks with their holes, bought parts are outer shapes,
gear teeth are trapezoidal, there are no screws.

| File | Pose |
|---|---|
| `CAD_FC/HUB_E_HOME.FCStd` (+ `.step`) | both stacks set down, shaft cups on the top stones, holder cups on the lower ones |
| `CAD_FC/HUB_E_1_FRONT_TOP_TURN45.FCStd` | front top stone lifted 8, turned 45°; rear holds its stack |
| `CAD_FC/HUB_E_2_FRONT_TOP_SPIN.FCStd` | front top stone at 90°, spinning (45°) |
| `CAD_FC/HUB_E_3_REAR_MIDDLE_UP.FCStd` | rear middle stone stood up beside the robot, rear top tower 340 mm behind |
| `CAD_FC/HUB_E_DEPLOYED.FCStd` | both turrets at 90°, cups spun, holders up: perimeter envelope (FAQ Q10) |

Groups in each file: robot base, column + beacon support, per unit turret / carriage / holder / fixed drives, stones,
reserved volumes (transparent). **Solid clash check: no clashes in the 5 poses + 13 extra poses** (carry, each
middle stone at 15/30/60/75°, cup at the bottom stone, bottom stone set down); highest 347.5 mm; perimeter 1176–1182.

What the real shapes changed in the layout (the box model follows):
- **Turn drive:** 60 T gear sector (m 1, pitch r 30) on each turret hub + 30 T pinion on the turn MG996R, shaft 45
  from the axis at polar −35° (front) / 145° (rear), where no riser ever passes. The gears sit above the drive motors.
- **Hubs stacked on the column:** front hub z 66, gear 72–77; rear hub z 80, gear 86–91. Both turrets' arms stay at
  z 59–64 (the carriage must reach the bottom stone), joined to their hub by a web (r 15–34) and a riser at r 34–40.
- **Top:** front hub z 333, rear z 324 with its riser beside the NEMA (t −30..−20). NEMA17 at r 34–76.
- **Rear turn servo on a 3 mm block** (its mounting ears were 1 mm inside the rear riser on a 14 mm block).

## Open points

1. **Not drawn yet:** screws and inserts, the holder lift crank + link, the hard stops (turret, spin), the cup shaft
   bearings (the cup sits on the servo horn in the model), the dovetail of the holder slides, cable and hose loops.
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
