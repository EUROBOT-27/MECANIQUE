# Clapets v7: v6 with reworked door units (Seif)

Copy of [clapets v6](../clapets-v6/README.md) (v5 + real horn + real servo wires). v5 and v6 stay untouched. Owner while
in progress: **Seif**. Design = `fc/v7_fc.py` (dimensions in `class G`); never edit the `.FCStd` by hand.

## Regenerate (FreeCAD 1.1), from this folder, one FreeCAD at a time
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v7_fc.py      # parts, STEP/STL/DXF, FCStd, report.txt (~1 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/render_v7.py  # colours + images
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_v7.py  # full-cycle checks (~10 min)
```

## Changes from v6
### 2026-11-01: door unit body (`A_AILE_D/G`) reworked
- **M3 heat-set inserts everywhere, hole Ø4.6 × 6.5** (measured from a part that fits Seif's inserts). This changes
  every M3 insert hole in the design (`INS3_R/D`), not only the door units.
- **Servo fixing:** 3 × M3 × 8 button head through the flange ears into M3 inserts in the post tops. **No more nut
  pockets on the outer face, no strap (`A_BRIDE_SERVO` removed), no upper block over the ears.** The servo still slides
  in from the front (before the rod), its outer ears in a slot of the outer wall. The ±2 mm mesh slots are gone: the
  mesh relies on the printed centre distance (+ the play of the ear holes).
- **Stiffer:** an **outer wall x 146.5..150, full height**, ties the bottom 608 plate to the top on the rod side (v6: open
  between z 36 and the web). Above the gears (z > 104) the unit is a **closed box**: front wall (gothic-arch underside,
  45° sides, ≤ 20 mm bridge), back wall (y 41..45), inner closing wall. Still printed upright with no support.
- Servo cable channel only at the grommet height (v6: from the bottom plate up), so the outer wall keeps its base.
- Solid volume 175 → 239 g per unit (the print is lighter with infill).
- Checks: rest pose 0 interferences, 0 reserve violations. **Full cycle not run yet.**
- Open: M4 back-wall fixing still uses M4 nuts (M4 insert size unknown); the box top is open (could be closed by the cap).
