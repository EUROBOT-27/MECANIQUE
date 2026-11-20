# Grail v1 (Baha): SolidWorks lift + flip arm with an electromagnet

Baha's Grail lift designs, added by Seif on 2026-11-19. **Reference only**: the design continues in
`../Grail_v2/` (Flipper and Flipper-S, D-029). File analysis: [`REVIEW.md`](REVIEW.md).

| Path | What | Status |
|---|---|---|
| `essai mecanisme vis ecrou 1.0.STEP` | lead-screw version (NEMA17 under a T8 screw, carriage on the nut, MG996R flips a U arm) | read in FreeCAD; review findings 1–10 |
| `essai mecanisme cremaillere last version.SLDASM` | rack-and-pinion version, assembly only | can't be opened here (newer SolidWorks than our 2024) |
| `Essai cremaillere/` | the rack version's parts as STLs, already in the assembly's positions | assembled in FreeCAD (below) |
| `essai vise ecrou corrigé/` | corrected lead-screw version: 2 × Ø8 rods + LM8UU, 608 top and bottom, tilting tray on a servo + 625 (STEP at rest + at the 180° place pose) | reviewed; its hardware is reused in Grail v2 **Flipper-S** (was B2) |
| `fc/rack_fc.py` | assembles the rack version from the STLs → `CAD_FC/GRAIL_V1_RACK.FCStd` + `CAD_FC/rack_report.txt` (~2 min) | no clash check (Seif, 2026-11-19) |

Run (from this folder): `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/rack_fc.py`

Main lessons (details in `REVIEW.md`):
1. **The flip turned the Grail back into its own column.** Both versions put the lift column behind the flip plane.
   In Grail v2 the column is inside the body, under the roof, where the Grail never goes.
2. **Too tall** (screw version 360 mm, corrigé 520 mm): the motor under the screw stacks height. In Flipper-S the motor
   stands beside the screw and drives it with a belt.
3. **Couldn't reach a Grail on the floor** with the magnet facing out. Grail v2 grips the Grail by its top.
4. Good ideas kept: arm held on both sides (servo horn + bearing), electromagnet, rods + LM8UU guide, lead screw
   that holds when the power is off, the rack (Seif's test print fits).
