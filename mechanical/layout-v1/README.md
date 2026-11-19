# Robot layout v1 (Seif, 2026-11-13)

> **Where we are (2026-11-13, evening):** layout refined. The clapets v7 module now **sits on the robot floor**
> (+26 mm), the body has **chamfered corners** (30 mm by default), there are **4 ball transfers in the corners**, and
> a **"module B only"** version (no door units) is added. Every rule check has been re-run. **Proposal, nothing decided yet.**
> Seif chooses the front (A+B or B only) and the back (mirror / flip6 / simple). Profile and top-tie heights are
> ignored for now (they get trimmed). The moving parts over 350 mm get fixed in Seif's module B rework (`../suction-v1/`).

## Update 2026-11-19: module B = T1 (suction-v1), back = T1 alone (results only, nothing decided)

The script now takes **T1** (`../suction-v1/`, D-027) instead of the v7 suction head, a **back = T1 alone** (module A's
lift without the door units + T1), the **door fold angle at start per side**, a separate **back chamfer**, and the
deployed check follows **FAQ Q10** (every front pose × every back pose, all at once).
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/layout_fc.py                  # default: front A+B, back t1, T1 S3
set LAYOUT_HEAD=T1S1 & "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/layout_fc.py
```
New options: `LAYOUT_HEAD` = `T1S3` (default) | `T1S1` | `V7` (old v7 head, old reports), `LAYOUT_BACK=t1`,
`LAYOUT_FOLD_D` / `LAYOUT_FOLD_G` (door angle at start, 90 = fully folded; default = how far the doors fold before
touching T1, from `../suction-v1/CAD_FC/turn/check_report.txt`), `LAYOUT_CHAMFER_BACK`. Reports `report_AB_t1_T1S3.txt`,
`report_AB_t1_T1S1.txt`, models `CAD/LAYOUT_AB_t1_T1S3.FCStd`, `CAD/LAYOUT_AB_t1_T1S1.FCStd`.

**Front A+B (doors fold less, only as far as T1 lets them) + back T1 alone, chamfer 30:**

| | T1 S3 | T1 S1 | Limit |
|---|---|---|---|
| Doors at start (D / G), stopped by T1 | 46° / 78° | 52° / 82° | |
| **Start perimeter** [GR F.3] | **1142.2** (+57.8) | **1134.9** (+65.1) | 1200 |
| Start with a 4° gap before T1 | 1147.5 (+52.5) | 1139.8 (+60.2) | 1200 |
| Doors fully folded (not possible with T1, reference) | 1122.8 | 1123.2 | |
| One module working | 1322.4 | 1322.9 | 1400 |
| **Fully deployed, everything at once** (FAQ Q10) | **1332.7** (+67.3) | **1329.3** (+70.7) | 1400 |
| Robot + Grail in 500 × 500 | 379 × 347 fits | fits | |

- **Folding less costs only ~19 mm (S3) / ~12 mm (S1)** of start perimeter, not the +35–45 estimated on 2026-11-19.
  Symmetric folds for comparison (S3): 46/46 → 1157.9, 40/40 → 1172.7, 30/30 → 1200.1 (limit), 0/0 → 1283.3.
- **Front A+B + back T1 alone passes Q10**: ~67–71 mm left for the Grail lift, launcher and gate tool at their most
  open, all at the same time.
- **Back chamfer** (no door units at the back), front 30, S3: back 50 → start 1124.6, back 70 → 1109.7. The fully
  deployed perimeter barely moves (1332.7 → 1325.8): the front doors set it.

**Problems found:**
1. **Door sheets + foam reach 360.8 during the lift-turn** (> 350, [GR F.3]): lift-turn 30° 353.9, 45° 360.8, 60° 352.1.
   The doors ride the lift (peak ~70 at 45°), so T1 does not fix the old "366 at lift 75". Fix to study: cut the
   door sheet + foam top ≥ 11 mm lower (~14 with margin; sheet top 292 → ~278 at lift 0, DXF only, printed module A
   unchanged); check the top stone is still gripped.
2. **T1 sticks out 14.4 mm past the body face** (cups), front and back; the stack face is at module y 151.4 (S3) /
   149.9 (S1) = 11.4 / 9.9 mm further out than the v7 head (y 140). Reason: `suction-v1/fc/params.py`
   `STACK_FACE_Y` was 146, but the body face is module y 140 (robot Y 146 = module y 140 + 6). Fixed to 140
   (report text only, no geometry). This is most of the start rise 1114 → 1142.
3. Carried stack centre 93 mm past the front caster line (S3; was ~81 with v7): tipping margin to check.
4. Still open: drive motors overlap the socle by 4 mm (447 mm³ each side), front and back.

Front = clapets v7 module, either **A+B** (lift + doors + suction head) or **B only** (lift + suction head, door units
removed). Back = **mirror** of the front, Ayoub's **flip-6cups**, or a **simple pick** (no turning). Right = **Grail
pickup**. Left = **cannonball launcher**. Drive = 2 × JSUMO JS7444 (Ø74) + Pololu 37D (D-004), axle through the robot
centre.

## Run
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/layout_fc.py        # front A+B, back mirror (~3-5 min)
set LAYOUT_FRONT_MOD=B & set LAYOUT_BACK=simple & "C:/.../freecadcmd.exe" fc/layout_fc.py
```
Options (environment variables): `LAYOUT_FRONT_MOD` = `AB` | `B`, `LAYOUT_BACK` = `mirror` | `flip6` | `simple`,
`LAYOUT_CHAMFER` (default 30), `LAYOUT_CASTERS` = `4` | `2`, `LAYOUT_HALF_W` / `LAYOUT_FRONT` / `LAYOUT_BACK_FACE`
(body size), `LAYOUT_MODULE_Z` (module raise; default puts the socle on the floor top).
Run the variants **one after the other**, not in parallel: each FreeCAD run needs a few GB of RAM.

Outputs: `report_<front>_<back>.txt` (all numbers, including a **chamfer sweep** 0–60), `CAD/LAYOUT_<front>_<back>.FCStd`
(open in FreeCAD: the real v7 parts at start, every reserved volume, the casters, the Grail at start, the start hull),
`envelopes/clapets_v7_AB.json`. Frame: X right, Y forward (front face = stack face), Z up from the table,
origin = drive axle centre.

## Results (chamfer 30, 4 casters, module on the floor)

| | **A+B / mirror** | A+B / flip6 | A+B / simple | **B only / mirror** | B only / simple |
|---|---|---|---|---|---|
| Body (X × Y) | 300 × 292 | 300 × 286 | 300 × 256 | 240 × 325 | 240 × 272.5 |
| **Start perimeter** (≤ 1200) [GR F.3] | **1114.2** (+85.8) | 1102.0 (+98.0) | 1042.0 (+158.0) | **1059.7** (+140.3) | 954.7 (+245.3) |
| **Deployed, one module working** (≤ 1400) | **1318.0** (+82.0) | 1306.4 (+93.6) | 1248.4 (+151.6) | **1062.8** (+337.2) | 957.8 (+442.2) |
| Both modules working at once | 1490.6 → forbidden | — | — | 1066.0 → allowed | — |
| Robot + Grail in 500 × 500 [G D.3, G E.2] | 379 × 292 fits | 379 × 286 fits | 379 × 256 fits | 315 × 325 fits | 315 × 273 fits |
| Moving parts > 350 (not trimmable) | door sheet + foam 366 (lift 75) | same | same | none in the poses checked (346), see below | same |
| Side bays (launcher / Grail) X width | 84 | 84 | 84 | **44** | **44** |

Without a chamfer (v1 numbers): A+B / mirror start 1184.3, deployed 1351.6.

**Chamfer sweep** (start perimeter, A+B / mirror): 0 → 1184.3 · 20 → 1137.5 · 30 → 1114.2 · 40 → 1090.8 ·
50 → 1067.6 · 60 → 1053.2. Every variant gains the full ~2.34 mm per mm of chamfer up to 50: **no module part sits
in the corners**. Only the door servo wire stubs (3.6 mm past the side, x ±153.6) stick out of the body, and the
same as before, routing them inside gives about 7 mm back. The other variants' sweeps are in their reports.

## What changed in this refinement
1. **Module on the floor:** the socle sits on the floor top (z 26), so the whole module is 26 mm higher than in the v7
   CAD (where z 0 = table). This fixes the socle/rail/floor overlaps of v1, and the door sheet bottom is now at z 46
   (no floor cut-out needed).
2. **Chamfers:** 45° chamfers on the 4 body corners. Every reserved box follows the chamfered outline.
3. **4 casters in the corners** (KSM15-FL, we have 4): placed inside the chamfer with 4 mm clearance, at about
   (±124, ±120) for A+B. The support is a rectangle instead of the v1 diamond (2 casters on the axis), which is much more
   stable when the stack hangs in front (stack centre ~81 mm past the front casters in every variant).
   **The catch: 6 contact points.** On an uneven table a drive wheel can lift off and lose grip. Fix: a **sprung drive
   wheel mount** (pivot arm + spring), or as a first test, casters set ~1 mm above the wheel contact line.
4. **Floor cut-out for the lift NEMA:** in the v7 CAD the NEMA hangs 19.5 mm below the socle. On the robot its bottom
   is at **z 6.5 (6.5 mm above the table)**, through a hole in the floor. Check that this is enough over the table joints.

## Problems found (to solve)
1. **Height, moving parts (A+B):** at lift +75 the door sheets and foam pads reach **366** (> 350). Also, the cups
   are now **26 mm above the stone centres** (v7 head: cups at z 85/165/245 above the table by design, see Seif's v8
   analysis sheet). The head has to come down 26 mm relative to the socle, or the lift has to start lower.
   **Seif handles both in the module B rework (`../suction-v1/`).** In the v7 head with lift 75 and the head not
   turned, the head plate would reach ~374. The layout only checks the turned pose (346), so check the
   lift-then-turn order in the rework.
2. **A+B: drive motors touch the socle** (447 mm³ each side): socle at Y 14.5..66.5, z 26..64; motor at Y ±18.5,
   z 18.5..55.5, x 32..100 → 4 mm overlap in Y. Fixes: front face +6 (Y 152, costs ~12 mm of perimeter), or a shorter
   motor (#4742 has no encoder: shorter than the 68 mm assumed, **measure it**), or a notch in the socle.
3. **B only: the width is set by the drive**, 2 × (wheel 44 + gap 6 + motor 68) + 4 = 240. The front face moves forward
   to Y 162.5 so the lift NEMA (through the floor) clears the drive motors. The robot gets longer (325 with a mirrored
   back) but much narrower, and it never goes past 1066 deployed (no doors).
   **The side bays are only 44 mm wide** (x 76..120): too narrow for a 45 mm ball magazine. The launcher would have to
   go in the core (148 × 69 × 214 with a mirrored back, 2.2 L) or a shorter motor would free more width.
4. **B only: the 320 mm stones stick out 40 mm on each side** of a 240 mm body. That's fine if a carried stone doesn't
   count in the perimeter (FAQ Q1), but there is no door to keep the stack from swinging: suction alone has to hold it
   (D-021 requirement 4).
5. **Flip6:** its links and plate (down to z 20) still hit the floor and the back casters: it needs its own floor
   cut-out, and the back casters have to move inward.

## Free volume for the other mechanisms (A+B, chamfer 30)

| Volume | Where | Size (X × Y × Z) | Litres | For |
|---|---|---|---|---|
| Left side bay | X −150..−66, Y ±40, z 78–300 (above the wheel) | 84 × 80 × 222 | 1.49 | cannonball launcher + magazine |
| Right side bay | X 66..150, Y ±40, z 78–300 (above the wheel) | 84 × 80 × 222 | 1.49 | Grail pickup + lift to the roof |
| Core | X ±64, Y ±18, z 86–300 (between the 2 lifts) | 128 × 36 × 214 | 0.99 | battery, electronics, pumps |
| Roof strip | X ±150, Y ±38, z 300–306 | 300 × 76 | — | Grail at L4 (right end), e-stop (left end), beacon support (centre) |
| Beacon support | Ø80, z 350–430, centred, on a bridge over the 2 top ties | | | LiDAR inside it (allowed, see below) |

B-only volumes are in `report_B_mirror.txt` / `report_B_simple.txt` (core 148 × 69, side bays 44 × 137).

## What the layout taught us (constraints for every designer)
1. **Nothing is free above the door units** (A+B). They ride the lift: at +75 mm the caps reach z 343 and the door
   sheets z 366 (module on the floor). The roof (L4, > 300 mm) can only be the strip **between the two lifts**.
2. **Chamfers are free perimeter:** about 2.34 mm per mm of chamfer, because no module part fills the corners. Chamfer
   30 takes A+B / mirror from 15.7 to 85.8 mm of margin at start.
3. **Never open the front and back doors at the same time** with a mirrored A+B back (1490.6 > 1400). Doors at −30°
   (approach) are the worst pose.
4. **The Grail can't come in at floor level on the right:** the right wheel fills the bay bottom (z 0–74, Y ±37). The
   pickup has to reach out over the wheel (side arm) or grab the Grail higher up.
5. **The left bay holds only ~4 balls in a vertical column** (222 / 45). Ten balls need a zigzag magazine or
   storage elsewhere (Barbatronic's 10-ball launcher is 220 × 52 × 260). In B only, the bays are 44 wide: too narrow.
6. **Pumps:** 6 per suction head. With a mirrored back that is 12 pumps (~1 L in boxes) for a core of ~1 L that also takes
   the battery and the electronics. Fewer pumps (one pump + valves per head) or pumps on the head (suction-v1 open
   question) free the core.
7. **Beacon support:** Ø80 centred, between the two lifts. A LiDAR inside it is allowed: the support "can only
   accommodate sensor and telecommunication systems", and for a rotating device the cut must be < 2 cm tall and not
   see-through [GR F.6]. The mast and the sensors in it don't count toward the 350 mm limit [GR F.3]. Barbatronic does this with an LD06.
   Rails, top ties and lead screws must be cut to ≤ 344 so the support bridge sits at 344–350.

## Assumptions to check (measure when the parts arrive)
- JSUMO JS7444 **width 44** (from the name, not confirmed); hub and bore.
- Pololu #4742 length 68 (encoder version figure; #4742 has no encoder, so shorter). It decides problem 2 and the B-only width.
- KSM15-FL body Ø24; the floor height follows the ball transfer (21 mm).
- Grail 70 × 70 × 100; battery and electronics sizes not chosen yet.

## References used
Barbatronic 2027 chassis (`resources/CDR-2027/MCAD/differential-structure.FCStd`) and GROSBOT 2023 (French club)
(`mechanical/resources/2023_GROSBOT.STEP`, local only): notes in `resources/_notes/`. Both: centred mast Ø80–100 at
350–430, battery high and central, boards standing on walls, drive axle through the centre.
