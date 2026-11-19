# Grail v1 (Baha, 2026-11-19): file analysis

Two versions of the Grail lift made by Baha in SolidWorks. Both use a **lift + an MG996R that flips a U arm
carrying an electromagnet**. Analysed by Seif + Claude on 2026-11-19, before the FreeCAD rebuild.
Requirements: `../grail-lift/docs/CDC.md`. Earlier work on the same idea: `../grail-lift/` (v1 = Baha's
"essai mecanisme 1", v2 / v3 = Maatoug's rebuilds).

Seif's input (2026-11-19): the idea has potential; a small lever arm is OK; **the internal size limits set before
(CDC bay, band between the door units, etc.) may be overridden**. The rule limits (350 mm height, perimeter) still hold.
The printed rack was test-fitted and fits well.

| File | Version | Status |
|---|---|---|
| `essai mecanisme cremaillere last version.SLDASM` | rack and pinion | can't be read here (newer SolidWorks than ours, 2024). Its parts came as STLs in `Essai cremaillere/` (assembly coordinates) → **assembled in FreeCAD**, see "Rack version" below. |
| `essai mecanisme vis ecrou 1.0.STEP` | lead screw + nut | analysed below |

## Lead screw version: what is in the file

Axes as exported from SolidWorks: **Y = up** (lift axis), servo axis along X, the magnet points along −Z at rest.

| Part | Size (mm) | Role |
|---|---|---|
| NEMA 17 | 42 × 42 × 57 | at the **bottom**, shaft up |
| `support fixation stepper` | 42 × 37 × 80 | motor bracket: NEMA17 pattern 31 mm (M3), Ø25.3 bore, 4 × M4 to the robot |
| Coupling `CXJH-C-D25-d5-e5` | Ø25 × 32 | motor → screw |
| `vis 300mm` | T8 × 301 | lead screw, free at the top |
| T8 nut + `piece de fixation sur l ecrou` | 22 × 40 × 22 | nut holder, pinned to the carriage (Ø5 cross pin + M3) |
| `bloc de rotation 180` | 75 × 62 × 102 | carriage: holds the servo + a Ø6.3 pivot hole on the servo axis |
| MG996R + horn + multipurpose bracket | | servo axis horizontal, **57 mm in front of the screw** |
| `support en u` | 81 × 42 × 64 | U arm: horn on one cheek, Ø6 pivot on the other (two-sided, good), Ø30.3 seat for the magnet in its base, 44 mm from the axis |
| Magnet 5 kg | Ø25 × 20 | **not placed**: floating ~110 mm away from its seat |

Overall: 160 × **360 tall** × 244.

## Findings

| # | Finding | Severity |
|---|---|---|
| 1 | **The flip turns the Grail into its own lift.** The magnet points away from the screw at rest. At 180° it points back at the screw and the carriage (axis 57 mm in front of the screw). The U arm alone already hits `bloc de rotation 180` at 180° (346 mm³) and at −90° (245 mm³); it swings freely 0 → 135°. A Grail held at 180° would sit where the screw and the carriage are. **The lift column must be out of the flip plane** (offset sideways), or the Grail must be put down before 135°. | blocking |
| 2 | **Too tall: 359.5 mm from the motor's bottom to the screw top**, even with the motor on the table (rule: ≤ 350 [GR F.3]). The motor under the screw adds ~70 mm (motor + coupling) to the stack. | blocking |
| 3 | **Can't reach a Grail on the floor.** Lowest servo axis = 125 mm above the motor's bottom (the nut stops at the coupling). Magnet facing sideways: centre ≥ ~127 mm up, but a Grail plate is ~25–40 mm up. Magnet facing down (−90°): its face is ~75 mm up, only just above an 80 mm Grail if the motor sits on the table, and −90° hits the carriage (finding 1). | blocking |
| 4 | **No guide for the carriage.** It hangs on the T8 nut only, with nothing to stop it turning with the screw. The ~0.3 N·m from the arm + Grail (~0.35 kg at ~80 mm) bends the screw and binds the nut. Needs rods + bushings or a 2020 + V-wheels (as in grail-lift v2/v3). | blocking |
| 5 | **Wrong coupling bore:** `d5-e5` = 5 mm on both sides, the T8 screw is 8 mm (229 mm³ overlap in the model). Use a 5 → 8 coupling (🇹🇳, common for 3D printers). | major |
| 6 | **300 mm screw free at the top.** Add a top bearing (608 or KFL08) or keep the screw short. | major |
| 7 | **Nut holder bore too small:** Ø8.2 (screw size), but the T8 nut's spigot is Ø10.2 × 10 mm and goes into it (28 mm³). Bore ≥ Ø10.5. | minor |
| 8 | **Magnet seat Ø30.3 for a Ø25 magnet** (2.6 mm gap all round). Size it for the real magnet (Ø25 + 0.3), or for a sprung mount (CDC D4). | minor |
| 9 | Servo vs horn and servo vs bracket overlaps (≤ 20 mm³) come from the bought-part models: ignore. | — |
| 10 | Good choices to keep: **U arm held on both sides** (horn + Ø6 pivot), the review of v1 asked for this. Lead screw is **self-locking** (no drop at 100 s / e-stop), unlike the rack (CDC F5). Electromagnet. NEMA17 + T8 are in the library (Ender). | — |

## Height budget at the place pose (CDC D1, with this arm)
Around the servo axis, the U cheeks reach ±20 mm whatever the angle, the servo + carriage +10 mm above the axis.
With the Grail held by its side face at 180°, the magnet centre is at the axis height:
- top of the actuators = axis + 20 ≤ 348 → **axis ≤ 328**
- Grail bottom = axis − (height of the steel plate above the Grail's bottom, after the flip) ≥ 302 →
  **plate centre ≤ 26 mm from the Grail's end**. Feasible with the plate low on the Grail (CDC D5: 25 mm), tight.

## For the rebuild (to discuss)
- Rack version: get the STEP first; Seif's printed rack fits.
- Lift column beside the flip plane (finding 1), motor not under the column (findings 2, 3): motor on top, or
  beside the column with a belt / rack.
- Guide (finding 4) and the lift's ability to reach the floor drive the column height.

Analysis scripts (not committed): `claude-workspace/tmp/grail_v1/` (`dump_step.py`, `holes.py`, `pose.py`, `swasm.cs`).

## Rack version (from the STLs)

**Model:** `fc/rack_fc.py` → `CAD_FC/GRAIL_V1_RACK.FCStd` + `CAD_FC/rack_report.txt` (~2 min). Run from this folder:
`"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/rack_fc.py`
- The STLs are already in place (SolidWorks wrote them in the assembly's coordinates). The script stands the profile
  up (it leaned 1.0° in the assembly) and uses the grail-lift frame: x = outward (servo / magnet side), y = along the
  face, z = up. **Profile bottom assumed at z = 5.**
- Parts are faceted solids made from the meshes: good for sizes and placement, not for fine fits. Only one instance
  of each repeated part was exported (3 V-wheels = the whole Ender X carriage, fine).
- **No clash check** until the mechanism is fixed (Seif, 2026-11-19).

What it is: 2020 profile 316 + printed rack 310 lying **in the profile's front slot**; the **Ender X carriage**
(plate + 3 V-wheels) runs on the profile; `support fixation es7i7` (171 × 80 × 104) bolts to the carriage and carries
the NEMA17 (shaft along x, pinion on it) and, at its far end, the MG996R. **Servo axis along y**: the U arm flips in
the x-z plane (outward ↔ back over the column).

| Item | Value (rack_report.txt) |
|---|---|
| Fixed column (profile + rack) | z 5 → 321 |
| Moving block (without the magnet) | 109 mm tall: `support fixation` bottom 89 mm under the servo axis → U top 20 mm over it |
| Model pose | **top of the travel** (+2.7 mm left) |
| Travel | 242 mm (the wheels leave the profile at the bottom); servo axis **89 → 331** |
| Highest actuator point at the top | U 348.6 + 2.7 = **351.3 > 350** |
| Lever arm | servo axis **122 mm out** from the profile centre (OK for Seif) |
| Magnet | **not placed again**: floating 75 mm from the servo axis, top at 380 |

Findings (rack version):
1. **Same flip problem as the screw version.** The U base sits ~44 mm outward of the servo axis. At 180° it is
   ~78 mm from the column centre, and the Grail beyond it spans about x −22 … 58: over the column and its own
   carriage (plate top ~320, Grail at the axis height ± 40). The Grail can't pass 180° unless the column is beside
   the flip plane, or the arm is longer than the axis-to-column distance + the Grail.
2. **1.3 mm over 350 at the top of the travel** (U top). Easy: stop the travel 2–4 mm lower (the column is not the limit).
3. **Lowest servo axis 89 mm** (the bracket under the servo hits the table first). Magnet facing out → its centre at
   ~89 at best; a Grail plate is ~25–40 mm up. The pick has to be magnet down (−90°) or the bracket must not hang
   under the servo.
4. **Pinion maybe ~0.6 mm too deep** in the model (centre 8.4 mm from the rack tips; 20T m1 needs 9.0). Seif's printed
   rack + pinion fit, so check it on the print, not in the CAD.
5. The rack can be back-driven: at 100 s / e-stop the carriage drops (known from v1).
6. Good: **real guide** (Ender carriage + V-wheels on the 2020, the screw version had none); rack in the profile slot
   (no extra width); NEMA17 + carriage + wheels from the library 📦.

Open question for the redesign: **how did Baha plan the cycle?** (magnet facing out or down at the pick; what angle at
the place; which side the roof is on).

## "essai vise ecrou corrigé" (2026-11-19, two STEP poses: REPOS + DEPOT_haut_180deg)
A clean redo of the screw version, Z up: NEMA17 under a base plate, 5×8 coupling, **T8 screw 453**, **2 × Ø8 rods
478 + 4 LM8UU**, 608 bearings in a bottom and a top plate, flange nut in a carriage (86 × 81 × 100). On the carriage,
a **tilting tray** (`bac_basculant` 75 × 56 × 40) turns on an MG996R horn on one side and a **625 bearing on the
other** (held on both sides). DEPOT = carriage +300 mm, tray turned 180°.
- Good, kept for Grail v2 option B: the guide (rods + LM8UU), the screw (holds when the power is off), 608 at both
  ends, the arm held on both sides (servo + 625).
- Doesn't fit the robot: 520 mm tall (screw 453, rods 478) and the tray at z 385–425 at the DEPOT (> 350 [GR F.3]).
  The motor under the screw has no room in layout-v1 (right wheel + drive motor under the bay). The tray is not a top
  grip, and there is no Grail or magnet in the model.
→ Rebuilt as **Grail v2 option B2** (`../Grail_v2/fc/b2_screw_fc.py`).
