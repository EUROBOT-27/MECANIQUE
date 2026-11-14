# Perimeter study: clapets modules open (Maatoug, 2026-11-14)

Follow-up to the layout v1 result "both modules working at once = 1490.6 > 1400" (A+B front / mirror back, chamfer 30).
Pictures and checks of that case, plus options to keep the clapets and stay ≤ 1400. **Analysis only, nothing decided.**

## Run
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/perimeter_study_fc.py    # ~10-15 min, from mechanical/layout-v1/
"C:/Program Files/FreeCAD 1.1/bin/python.exe" fc/perimeter_plot.py             # pictures, a few seconds
```
`perimeter_study_fc.py` runs `layout_fc.py`'s own definitions (same poses, body, blocks, hull code), so its numbers
match the layout report. It only fixes the v7 path: `layout_fc.py` still reads `../clapets-v7/`, which moved to
`../clapets/clapets-v7/` (layout_fc.py can't run until that line is fixed).

## Pictures
- `topview_sheet.png`: start / one module open / both open at −30 (approach) / both fully open at −38 (release)
- `topview_both_approach.png`, `topview_both_release.png`, `topview_both_lift_turn.png`: one large view each
- `topview_ab_front_b_back.png`: option 2 below (front A+B, back B only, everything working)
- `door_angle_map.png`: perimeter for every front / back door angle pair (lift 0), the black line = 1400

## Is the perimeter measured correctly? Yes
[GR F.3]: "the perimeter of the convex shell of its vertical projection on the ground". The script projects every part
and every reserved volume onto XY, takes one convex hull and adds up its sides: that is the rule. Curved edges are
cut into 16 segments; with 64 the result changes by < 0.1 mm (1490.6 → 1490.6). The Grail at start and the carried
stones are not in the hull (Grail is a separate object; stones: FAQ Q1 working assumption).

What the study missed: it only tried 4 door angles. The full sweep (every 2°) gives:
| Case | Study | Sweep |
|---|---|---|
| One module working, other folded | 1318.0 (−30) | **1318.2 (−32)** |
| Both working, same angle | 1490.6 (−30) | **1492.9 (−24)** |
| **Both clamping a stack (+3)** | not checked | **1427 → over 1400** |
| Back clamping (+3), front opening | not checked | front may go only to **+14** (1400.0) |

The last two matter most: with A+B front and back, **the robot can't hold two stacks clamped at the same time**, and
it can't approach a second stack while the back holds one. At the clamp the 4 door tips sit at (±166, ±191): the
hull is a 331 × 382 rectangle no matter how the body is chamfered.

## FAQ answers (2026-11-14, see `project/rules-digest.md`)
- **Q1: carried stones do NOT count** in the perimeter. (For reference, if they did: one stack in front 1391.3,
  two stacks front + back 1665.7.)
- **Q10: "fully deployed" = every mechanism open at the same time**, as shown at homologation. A software interlock
  (never open both modules together) does not make the robot legal. The number to check is the hull with **all**
  mechanisms at their most open position (and ≤ 1400 at every moment of the travel).

Consequence: **A+B front + A+B mirrored back is not legal**, whatever the software does: both fully open 1477.8,
worst over the travel 1492.9, and even both clamped (+3) is 1427. Layout README lesson 3 ("never open the front and
back doors at the same time") no longer works as a rule.

## Options (perimeter with chamfer 30)
| # | Option | Start | All mechanisms open | Keeps | Cost |
|---|---|---|---|---|---|
| 1 | ~~Software interlock~~ | 1114 | 1493 | — | **out (Q10)** |
| 2 | **Front A+B + back B only** (back keeps lift + suction head, no doors) | 1114 | **1318** (82 mm left for the other mechanisms) | front unchanged; back = suction-v1 (D-021) | back stack held by suction alone |
| 3 | Shorter doors + small opening on both modules (v9 door units) | ~1114 | must be ≤ 1400 with both at max opening | both modules with doors | full door unit redesign; both clamped alone needs the tips at Y ≤ ±177 (~1371), the approach needs far less opening than −30 |
| 4 | ~~Smaller opening limited by the other module's pose~~ | | | | **out (Q10)**: only the fixed maximum opening counts |

The 82 mm left with option 2 is for **every other mechanism at its most open position at the same time**: Grail
lift (v3 flips over the side edge), launcher, gate tool. Each one's deployed outline has to go into this check.
Ayoub's flip6 back is not modelled deployed here (reserved box only): its plate turning out at the back has to be
added to the front's 1318 before it can be compared.

## Are the modules pushed in as far as they can go? Yes, already 4 mm too far
`fc/inward_gap_fc.py` (bounding boxes of every v7 part over all poses, against the drive and the other module):

| What stops the front module moving toward the centre | Gap in Y |
|---|---|
| Socle (Y 14.5, z 26–64) vs the drive motors (Y ±18.5, z 18.5–55.5) | **−4.0 (overlap now)** |
| Door units (Y 40, from z 53) vs the wheels (Y ±37, up to z 74) | 3.0 |
| Rail screws vs the drive motors | 3.8 |
| Front lift NEMA vs back lift NEMA (both hang through the floor, Y ±4) | 7.9 (4 per module) |

- The body doesn't add to the footprint: front face = stack face (Y 146), sides = door unit outer faces (X ±150); only
  the door servo wire stubs stick out (3.6 mm).
- The drive already sits partly under the modules (motors under the socle, wheels beside the door units). Even with a
  socle notch over the motors, the next stops are 3–4 mm away: ~8 mm shorter robot, ~16 mm of perimeter.
- Needed to pass with both modules working: both clamped needs each module ~7 mm further in (zero margin), both at
  the approach angle ~23 mm. That only comes from a shallower module (lift motor not hanging behind the socle), a
  drive that sits fully under the modules (smaller wheels, motors outside the socle's Y band), or shorter doors.

Notes:
- Chamfers don't help here: the door tips set the hull corners, not the body.
- Sliding jaws in X instead of swinging doors don't solve it alone: to clamp the stone ends they still reach Y ±191,
  and the hull of 2 clamped stacks stays ≥ 2 × (330 + 382). What matters is how far the grip reaches past the body face.
