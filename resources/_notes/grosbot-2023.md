# GROSBOT — 2023 main robot of a French club (STEP), notes

Source: `mechanical/resources/2023_GROSBOT.STEP` (246 MB, **local only, not committed**: ask Seif for the file).
Eurobot 2023 (cakes + cherries). **From a French club, not Aerobotix** (club name to add; Seif, 2026-11-13). Read with FreeCAD 1.1 on 2026-11-13 (loads in ~3 min, ~2100 solids). The STEP is
**Y up**: below, "height" = STEP y, footprint = STEP x × z.

## Overall
- **Structure 290 × 250 mm footprint** (x ±145, z ±125) → plain-box perimeter 1080 mm. **350 mm tall**; whole robot
  incl. side protections x ±146–157.
- **Mast (beacon support) Ø100 from 350 to 430 mm** (x ±50), on top of the structure, centred.
- **E-stop** (LANBOO 22 mm, 2NO2NC) on the roof corner, top at 367 mm (≤ 375 allowed).

## Where things sit
| Block | Position | Notes |
|---|---|---|
| Drive (`CO_MOTORIZATION`) | bottom layer, height 0–73, x ±116, centred | wheel axle through the robot centre; Faulhaber 3242CR motors (Ø32) |
| Odometry (`CO_ODOMETRY`) | bottom layer, x ±144 (outside the drive wheels) | separate encoder wheels at the sides |
| Battery | **high, centred**: 90 × 55 × 150 safety bag at height 192–252, quick-holder under it | easy swap from the top; keeps the bottom free for mechanisms |
| Electronics | boards **standing on the inner side walls**: io board x −143..−104, motor/servo boards x 106..145, height 80–320 | boards use the walls, not the floor |
| Raspberry Pi + touchscreen | top, height 194–333 | |
| Mechanisms | elevator in the middle (height 7–259, x ±117), flippers on both faces (front + back, mirrored), aspirator at the top (249–341), cherry dispenser | front/back mirrored mechanisms like our plan |
| Side protections | thin walls x ±135–146, full height | |

## What we take for our layout (2026-11-13)
- A centred mast Ø100 from 350 to 430 on a full-height structure is the proven way to get the beacon support.
- Battery high and central, reachable from the top; boards vertical on side walls: both free the floor for mechanisms.
- Mirrored front/back mechanisms + a centred axle (same as our D-004 / layout v1).
