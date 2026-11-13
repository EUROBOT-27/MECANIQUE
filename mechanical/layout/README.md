# Robot layout v1 (Seif, 2026-11-13)

> **Where we are (2026-11-13):** first full layout of the robot around the real clapets v7 module, with every rule
> check computed (perimeter, height, start area) and the free volume left for each mechanism. **Proposal, nothing
> decided yet. Rough first pass (reserved boxes only); Seif will refine it.** The back of the robot has 3 options (below); Seif chooses.

Front = clapets v7 **module A + B** (same space with or without module B). Back = **mirror** of the front, or
Ayoub's **flip-6cups**, or a **simple pick** (no turning). Right = **Grail pickup**. Left = **cannonball launcher**.
Drive = 2 × JSUMO JS7444 (Ø74) + Pololu 37D (D-004), axle through the robot centre; 2 KSM15-FL ball transfers.

## Run
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/layout_fc.py                    # back = mirror (~3-8 min)
set LAYOUT_BACK=flip6 & "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/layout_fc.py   # or simple
set LAYOUT_BACK_FACE=130 & ...                                                          # move the back face
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/module_envelope.py              # v7 footprint per pose (seconds)
```
Outputs: `report_<back>.txt` (all numbers), `CAD/LAYOUT_<back>.FCStd` (open in FreeCAD: the real v7 parts doors
folded, every reserved volume as a box, the Grail at start, the start hull), `envelopes/clapets_v7_AB.json`.
All sizes are parameters at the top of `fc/layout_fc.py` (class `P`). Frame: X right, Y forward (front face = stack
face), Z up from the table, origin = drive axle centre.

## The shape (top view, back = mirror)
```
                         FRONT  (stack face, Y +146)
 X  -150         -66                0                 +66          +150
     +-----------+-----------------------------------+-------------+
     | door unit |      module A + B (front)          |  door unit  |  Y +40 .. +146
     |   (left)  |   lift rails at Y +29..+49         |   (right)   |  (rises 75 mm with the lift)
     +-----------+-----------------------------------+-------------+
     | SHOOTER   |  CORE  Y ±18, z 60-300            |  GRAIL      |  Y -40 .. +40
     | bay       |  battery + electronics + pumps     |  bay        |  roof strip on top (z 300-306)
     | wheel L   |  drive motors below (z 18-56)      |  wheel R    |  beacon support at the centre
     | below     |                                    |  below      |
     +-----------+-----------------------------------+-------------+
     | door unit |      module A + B (back, mirror)   |  door unit  |  Y -146 .. -40
     +-----------+-----------------------------------+-------------+
                         BACK  (Y -146)
```
- Body **300 × 292** (X × Y). The width is fixed by the v7 door units (x ±150). The depth is fixed by the drive:
  the Ø74 wheels at the centre must clear the door units, which start 106 mm behind the front face → front face
  at Y +146.
- Floor plate z 21–26 (KSM15-FL: 21 mm from the ball bottom to the body top), cut-outs for the wheels + motors.
- Drive motors (37 × 68) fit between the lift motors (NEMA, |x| ≤ 21) and the wheels: x 32–100. No clash found.

## Numbers (from the reports)

| | back = **mirror** | back = **flip6** (Ayoub) | back = **simple** (70 deep) |
|---|---|---|---|
| Body (X × Y) | 300 × 292 | 300 × 286 | 300 × 256 |
| **Start perimeter** (limit 1200) [GR F.3] | **1184.3** (margin 15.7) | 1172.2 (27.8) | 1112.2 (87.8) |
| **Deployed, one mechanism working** (limit 1400) | **1351.6** (48.4), doors at −30° | 1339.9 (60.1) | 1281.5 (118.5) |
| Front + back doors working at the same time | **1490.6 → forbidden** (software interlock) | — | — |
| Robot + Grail (70) on the floor at the right, start area 500 × 500 [G D.3, G E.2] | 379 × 292: fits | 379 × 286: fits | 379 × 256: fits |
| Height, moving parts [GR F.3] | 340.0 (door sheet, lift 75) | same | same |
| Pumps to place (one per cup) | 12 | 6 + Ayoub's 6 | 6 + ? |

The carried stack is not counted in the perimeter (assumption, FAQ Q1). The servo wire stubs of the door units stick
out to x ±153.6: they cost 7 mm of perimeter; routing them inside gives the margin back.

## Free volume for the other mechanisms (same in the 3 options)

| Volume | Where | Size (X × Y × Z) | Litres | For |
|---|---|---|---|---|
| Left side bay | X −150..−66, Y ±40, z 78–300 (above the wheel) | 84 × 80 × 222 | 1.49 | cannonball launcher + magazine |
| Right side bay | X 66..150, Y ±40, z 78–300 (above the wheel) | 84 × 80 × 222 | 1.49 | Grail pickup + lift to the roof |
| Core | X ±64, Y ±18, z 60–300 (between the 2 lifts) | 128 × 36 × 240 | 1.11 | battery, electronics, pumps |
| Roof strip | X ±150, Y ±38, z 300–306 | 300 × 76 | — | Grail at L4 (right end), e-stop (left end), beacon support (centre) |
| Beacon support | Ø80, z 350–430, centred, on a bridge over the 2 top ties | | | LiDAR inside it (allowed, see below) |

## What the layout taught us (constraints for every designer)
1. **Nothing is free above the door units.** They ride the lift: at +75 mm the caps reach z 317 and the door sheets
   z 340. The roof (L4, > 300 mm) can only be the strip **between the two lifts** (|Y| < 38).
2. **The perimeter at start has 15.7 mm left with a mirrored back.** Anything that sticks out (bumpers, sensors,
   cables, a screw head) eats it. Flip6 leaves 27.8 mm, the simple back 87.8 mm.
3. **Never open the front and back doors at the same time** (1490 > 1400). Doors at −30° (approach) are the worst
   pose; −38° (release) is almost the same.
4. **The Grail can't come in at floor level on the right**: the right wheel fills the bay bottom (z 0–74, Y ±37). The
   pickup must reach out over the wheel (side arm) or grab higher on the Grail. Its deployed part counts in the
   perimeter (budget ~216 mm while the doors stay folded).
5. **The left bay holds only ~4 balls in a vertical column** (222 mm / 45). Ten balls need a zigzag magazine or
   storage elsewhere (Barbatronic's 10-ball launcher is 220 × 52 × 260).
6. **Pumps:** 6 per suction head. With a mirrored back that is 12 pumps (~1 L in boxes) for a core of 1.11 L that
   also takes the battery and the electronics. Fewer pumps (one pump + valves per head) or pumps on the head
   (suction-v1 open question) free the core.
7. **Module A on the real robot:** its socle, rails and lift motor move up onto the floor (z 26); the door sheet
   bottom (z 20) and the door units (z 27, 1 mm above the floor top) need a floor cut-out; rails, top tie and lead
   screw cut to ≤ 344 so the beacon support bridge sits at 344–350 (today 366).
8. **Beacon support:** Ø80 centred, between the two lifts (fits: the rail corners are 39 mm from the centre). A LiDAR
   inside it is allowed: the support "can only accommodate sensor and telecommunication systems", and for a
   rotating device the cut must be < 2 cm tall and not see-through [GR F.6]. The mast and the sensors in it are
   outside the 350 mm limit [GR F.3]. Barbatronic does this with an LD06.
9. **Flip6 at the back:** its links and plate go down to z 20, so the floor and the back ball transfer must move
   (reported overlaps); its stones reach 470 mm during the flip (Ayoub's README, GR F.3 question).

## Assumptions to check (measure when the parts arrive)
- JSUMO JS7444 **width 44** (from the name, not confirmed); hub and bore.
- Pololu #4742 length 68 (encoder version figure; #4742 has no encoder, so shorter).
- KSM15-FL body Ø24; the floor height follows the ball transfer (21 mm).
- Grail 70 × 70 × 100; battery and electronics sizes not chosen yet.

## References used
Barbatronic 2027 chassis (`resources/CDR-2027/MCAD/differential-structure.FCStd`) and Aerobotix 2023 GROSBOT
(`mechanical/resources/2023_GROSBOT.STEP`, local only): notes in `resources/_notes/`. Both: centred mast Ø80–100 at
350–430, battery high and central, boards standing on walls, drive axle through the centre.
