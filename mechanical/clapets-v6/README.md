# Clapets v6: v5 refined for the first real print (Seif)

Copy of [clapets v5](../clapets-v5/README.md) (Maatoug), made so v5 stays untouched (D-019). Goal: print it, build it
and test it on real stones. Owner while in progress: **Seif**.

- Design = `fc/v6_fc.py` (all dimensions in `class G`). Never edit the `.FCStd` by hand; it is regenerated.
- The servo and horn models are read from `../resources/mg996r-servo-3.snapshot.9/` (real GrabCAD model).
- `docs/` are copies of v5's docs; update them as v6 changes.

## Regenerate (FreeCAD 1.1), from this folder, one FreeCAD at a time
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v6_fc.py      # parts, STEP/STL/DXF, FCStd, report.txt (~1 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/render_v6.py  # colours + images
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_v6.py  # full-cycle checks (~10 min)
```

## Changes from v5
### 2026-11-01: real MG996R horn
- The **real round horn** (`mg996_arm_round.step`) is now on all 3 servos in the assembly, seated on the spline
  (hub 0.2 mm above the body). v5 assumed a Ø21 × 2 disc with its top 43.5 mm above the servo bottom; the real one is
  **Ø20.8 × 2.5 with its top at 45.7 mm**, a Ø9.2 × 0.8 centre boss, and screw holes on **r 7.2** (v5: r 7.5).
- **Door pinions + 28T gears 2.2 mm higher** (they follow the horn). Pocket fits the real disc (+0.3), recess for the boss,
  screw holes on r 7.2.
- **Head pinion:** the servo body can't move back (plate), so the real horn now sits inside the gear plane. The 20T is
  shorter (y 96.7 → 102.5, **5.8 mm face** instead of 8) and sits directly on the horn disc, centred by the boss; no
  collar (it would hit the 30T). The 30T keeps its full 8 mm. Horn disc to 30T tips ≈ 0.85 mm.
- Checks: rest pose 0 interferences, 0 reserve violations.
