# Clapets v6: v5 refined for the first real print (Seif)

Copy of [clapets v5](../clapets-v5/README.md) (Maatoug), made so v5 stays untouched (D-019). Goal: print it, build it
and test it on real stones. Owner while in progress: **Seif**.

- Design = `fc/v6_fc.py` (all dimensions in `class G`). Never edit the `.FCStd` by hand; it is regenerated.
- The servo model is shared with v5: `../clapets-v5/resources/mg996r/`.
- `docs/` are copies of v5's docs; update them as v6 changes.

## Regenerate (FreeCAD 1.1), from this folder, one FreeCAD at a time
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v6_fc.py      # parts, STEP/STL/DXF, FCStd, report.txt (~1 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/render_v6.py  # colours + images
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_v6.py  # full-cycle checks (~10 min)
```

## Changes from v5
- (none yet)
