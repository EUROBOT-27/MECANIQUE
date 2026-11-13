# Clapets v5: quarry-stack gripper with a turning suction head

**IEEE RAS INSAT · Eurobot 2027 ("The Legend of Camelot")** · Mohamed Ali Maatoug (fabrication CAD), with Claude.
Status: **design complete, verified in CAD, not built yet** (2026-10-30).

The robot drives up to a quarry (3 stacked boxes, 320 × 110 × 110 mm each). Two short doors clamp the stack and a lift
raises it 15 mm to carry it. In the castle, a suction head (one cup per box) holds the stack, the doors open, the lift
raises 75 mm, and the head **turns the whole stack 90°** to stand the boxes up as towers.

![](CAD_FC/images/v5_iso_parts.png)

▶ **Video of a full match cycle:** [`CAD_FC/motion/motion.mp4`](CAD_FC/motion/motion.mp4) (GIF: `motion.gif`)

## Two modules, one interface
- **Module A, clapets (lift + doors).** The lift is the Y axis of a Two Trees Bluer V2 printer stood on end: 2 rails,
  the butterfly bed plate on its 4 V-wheels, NEMA17 + T8 screw. Two door units (MG996R + gears, plain Ø8 rod on 608s)
  carry MDF doors with foam pads. The doors fold flat inside the base at start.
- **Module B, suction head.** It bolts on the plate front with the 4 wheel bolts. An MG996R turns a Ø8 shaft on 2× 608
  through a 20T → 30T gear pair. An MDF carrier holds 3 TPU spring stations with DP-S30 cups, the middle one on the axis.
- **Module A is designed around space reserved for module B.** A script checks that A never enters it, so the head can be
  redesigned without touching the doors or the lift.

| Check (automatic) | Result |
|---|---|
| Interferences at rest (real servo and plate models, cable stubs included) | **0** |
| Collisions over the full cycle (88 frames) | **0** |
| Perimeter at start / deployed (300 × 300 base) | **1200.0 mm** / ≤ 1367 mm (limits 1200 / 1400) |
| Highest actuator | **347.7 mm** (limit 350; only 2.3 mm margin) |

## What's in this repo
| Path | What |
|---|---|
| [`docs/BUILD.md`](docs/BUILD.md) | **Build sheet:** how it works, servo fixing, cables, bearings, heat-set inserts, tolerances, adjustment slots, assembly order, parts list |
| [`docs/DESIGN_HISTORY.md`](docs/DESIGN_HISTORY.md) | How we got here: v1/v2 → PoC 1 (wiped) → PoC 2 → v4 → v5, what was rejected and why, lessons |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | The decisions behind it (D-012 to D-017) |
| [`docs/RULES.md`](docs/RULES.md) | Rules used, full-cycle results, open FAQ questions (Q1, Q9) |
| [`docs/OPEN_POINTS.md`](docs/OPEN_POINTS.md) | What to measure and print-test before the build, known limits, what's not designed yet |
| `fc/v5_fc.py` | **The design**: every part is generated from the numbers in `class G`. Also runs the interference and reserve checks |
| `fc/motion_v5.py` | Full match cycle: collisions, reserve, perimeter, height per step; in the GUI, records the video |
| `fc/render_v5.py` | Colours, pictures, and saves the display into the `.FCStd` |
| `fc/plaque_papillon_reelle.json` | Real butterfly plate outline + holes, read from the printer's CAD |
| `resources/mg996r/` | Real MG996R model, used as the servo reference |
| `CAD_FC/MODULE_CLAPETS_V5.FCStd` | The assembly: open in FreeCAD |
| `CAD_FC/STEP/` | Every part + `MODULE_A_CLAPETS.step`, `MODULE_B_TETE.step`, `MODULE_CLAPETS_V5.step` (open in SolidWorks) |
| `CAD_FC/STL/` | Printable parts (`printed_parts.txt` lists them) |
| `CAD_FC/DXF/` | Laser-cut MDF: door sheet (3 mm), head carrier (6 mm) |
| `CAD_FC/report.txt`, `CAD_FC/motion/motion_report.txt` | Masses, sizes, check results |
| `CAD_FC/images/` | Renders, including close-ups of the door unit, nut support, head bracket and servo cable |

Part names: `A_` module A, `B_` module B, `REF_` bought parts (not to print), `RES_` reserved space. French names are
kept from the original CAD: *aile* = door unit, *capot* = cap, *bras* = arm, *roue* = gear, *pignon* = pinion,
*tôle* = sheet, *socle* = base, *traverse haute* = top tie, *support écrou* = nut support, *bride* = strap,
*entretoise* = spacer, *tête* = head, *moyeu* = hub, *plateau* = carrier, *bague* = ring, *pile de pierres* = stone stack.

## Regenerate (FreeCAD 1.1)
Run from this folder, **one FreeCAD at a time** (memory). `FC="C:/Program Files/FreeCAD 1.1/bin"`:
```
"$FC/freecadcmd.exe" fc/v5_fc.py       # parts, STEP/STL/DXF, FCStd, report.txt          (~1 min)
"$FC/freecad.exe"    fc/render_v5.py   # colours + images (opens and closes the GUI)
"$FC/freecadcmd.exe" fc/motion_v5.py   # full-cycle checks -> CAD_FC/motion/motion_report.txt (~10 min)
"$FC/freecad.exe"    fc/motion_v5.py   # same cycle as a video -> CAD_FC/motion/motion.mp4 (needs ffmpeg on PATH for the mp4)
```
Optional: set `CLAPETS_COPY_DIR` to also copy reports, images and videos to another folder.
Change a dimension → edit `class G` in `fc/v5_fc.py` → run all four → check that `report.txt` and `motion_report.txt` still
say 0 → update `docs/BUILD.md`.

## Coordinates
Millimetres. x to the right, y towards the stack, z up; z 0 = the table. Base x ±150, y −160 … 140; the stack face is
at y 140. Door unit D is at +x, G at −x.
