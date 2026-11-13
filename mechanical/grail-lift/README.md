# Grail lift: put our Grail on the roof (L4)

> **Where we are (2026-11-11, Maatoug + Claude)**
> - **v3 = the compact one, mounted in the full robot** (`../robot/`): on the left side face, in the 88 mm band
>   between the front and back clapets' door units, above the drive wheel. Picks the Grail **by its top** (park with
>   the Grail under the arm, +-25 mm), flips it 180 deg over the side edge, sets it down through a roof slot, and the
>   arm drops under the roof: Grail free (L4). Planned path feasible over the whole flip, worst margin 2.4 mm
>   (`CAD_FC/v3_report.txt`). The motion check (`fc/motion_fc.py`) has not been run on v3 yet.
> - **v2** (lift + flip, side grip) works but needs a whole driving face, which the clapets take (front + back).
> - **v1** = Baha's SolidWorks "essai mecanisme 1" (`sw/`), rebuilt in FreeCAD. It can't reach L4 (`docs/REVIEW_v1.md`).
> - **Not a decision**: mechanical is Seif's area; the Grail lift is meant to be tested against other variants.
> - **Needs from others:** clapets rails / top tie must stop below the roof (300) where the Grail lands (they reach
>   381-391 now, CDC + robot report); roof at 305 and the left side for the lift (Seif's roof layout); real U-bracket
>   dimensions; the 3 missing v1 SLDPRT from Baha.

## v3 (compact) in short
| | |
|---|---|
| Where | left side face, robot X -44 .. 44 (between the door units), above the left wheel; moving parts stay in y -43.5 .. 38 of the lift frame |
| Lift | 2020 column (z 76 .. 346) + carriage on printed slider shoes in the column slots; **T8 lead screw + NEMA17** (library) — motor standing on the roof (robot X -57..-15, Y 56..98), screw through a roof hole, 608 block low, brass nut on an arm under the carriage. Self-locking: no drop at 100 s / e-stop. Travel axis 116 .. 283 |
| Arm | MG996R lying in the steel U bracket; magnet on an L plate, 20 mm below the arm line at the pick pose (keeps the Grail outside the face at mid-flip) |
| Grail | 80 x 80 x 86, ~150 g, steel plate on the **top** face; ends upside down on the roof at robot X -10 .. 70, Y 27.5 .. 107.5 |
| Roof | slot for the arm + magnet, bay for the column/carriage, 12 mm notch at the edge where the Grail's corner passes; the Grail rests on the roof on two sides of the slot |
| Cycle | ~11 s (sequence in `CAD_FC/joints_v3.json`), servo load 1.3 kg.cm |
| Generator | `fc/v3_fc.py` (numbers in `class G`, robot context from `../robot/fc/layout.py`) |

Requirements every variant is checked against: [`docs/CDC.md`](docs/CDC.md).
Key result (CDC D1): **a straight lift can't do L4 under the 350 mm rule.** Whatever travels with the Grail would
have to fit in a ~45 mm tall band. A 2nd motion is needed.

## Files

| Path | What |
|---|---|
| `sw/` | Baha's SolidWorks assembly + the parts sent with it. `servo-duplicates/` = copies of files already in `../resources/mg996r-servo-3.snapshot.9/` (not needed). |
| `CAD_FC/STEP/v1_sw_export/` | The v1 assembly exported from SolidWorks (resolved parts only), NEMA17 and coupling as STEP |
| `fc/grail_common.py` | Shared helpers (frame, simple parts, joints file, sequence replay) |
| `fc/v1_fc.py` | v1 rebuilt → `CAD_FC/GRAIL_LIFT_V1.FCStd`, `joints_v1.json`, `v1_report.txt` |
| `fc/v2_fc.py` | **v2 generator** (dimensions in `class G`) + motion planner → `GRAIL_LIFT_V2.FCStd`, `joints_v2.json`, `v2_report.txt`, STEP |
| `fc/sliders_fc.py` | **Slider motion study** in the FreeCAD GUI (v1 and v2) |
| `fc/motion_fc.py` | Plays the planned cycle: checks (headless) + GIF (GUI) → `CAD_FC/motion/`, copied to `../simulations/grail_lift/` |
| `docs/` | `CDC.md` (requirements), `REVIEW_v1.md` (v1 review + parts check), v1 preview image |

## Run (FreeCAD 1.1, from this folder)
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v1_fc.py        # v1 rebuild (~20 s)
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v2_fc.py        # v2 model + planned path (~4 min)
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v3_fc.py        # v3 (compact) + planned path (~6 min); then python tools/sync_robot.py
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/sliders_fc.py   # sliders (or Macro > Macros... > Execute)
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_fc.py    # full-cycle checks (~7 min)
set GRAIL_GIF_ONLY=1 & "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/motion_fc.py   # GIF only (~10 min)
```
`set GRAIL_V=v1` runs the motion check / GIF on v1. Never edit the `.FCStd` by hand: change the generator and re-run it.

### The slider panel
- **Lift**: v2 = height of the flip axis (55 = magnet facing the Grail on the table … 334.5 = top).
- **Flip**: 0° = arm pointing out of the robot, 180° = over the roof. On v1 this is the servo tilt.
- **Grail approach**: the robot driving in; moves a free Grail along x.
- **Magnet ON**: the Grail follows the arm from where it is. OFF: it stays where it is (no gravity: read "Grail bottom").
- **Sequence + Play**: the planned cycle; the other sliders follow it.
- Live readouts: highest actuator point (≤ 350), the **planned lift band for this flip angle** (outside it you hit
  the roof or pass 350), Grail bottom / over the roof, protrusion. **Check collisions**: real solid intersections at
  this pose. The gear mesh, wheels in the slot and pin in its cap touch by design and are ignored.

## v2 concept

How it works (one stepper + one servo + one magnet, ~13 s):

![cycle](../simulations/grail_lift/grail_lift_v2.gif)

1. **During the match** the arm is folded over the roof (flip 180°): no perimeter cost.
2. **Unfold** over the edge, lift coordinated with the flip (planned path), then **lower** to the Grail (axis at 55 mm).
3. The robot **drives in** until the magnet touches the Grail's steel plate. The lift is meant for a driving face.
   **Magnet ON.**
4. **Lift**, then **flip 180° over the roof edge** while the lift follows the planned path: about 278 mm at 90°,
   330 mm at the end. The Grail turns upside down (CDC D5) and passes over the edge.
5. **Lower** until the Grail sits on the roof, **magnet OFF** (reverse pulse), arm swings back to 140°: **Grail
   free on the roof (L4)**, nothing touching it (nearest part 2.8 mm).

Key numbers (`CAD_FC/v2_report.txt`, `CAD_FC/motion/motion_report_v2.txt`):

| | |
|---|---|
| Highest actuator point over the cycle | 348.2 mm (limit 350; planner keeps 2 mm) |
| Worst height margin with the Grail held | 4.4 mm (flip 180°, place pose) |
| Collisions of moving parts | none |
| Release | magnet edge presses ≤ ~0.5 mm into the plate as the arm swings back → **spring-mounted magnet** (2 mm float) |
| Grail on the roof | bottom 305.5 → rests at 305, x −164 … −82.5 (fully on solid roof) |
| Servo load | 2.0 kg·cm with the Grail horizontal (MG996R ~9.4) |
| Protrusion | 52.5 mm beyond the face while picking; 0 when folded |
| Carriage | 64 mm tall, 4 V-wheels 38 mm apart on a 2020 column |

### Parts (📦 library · 🇹🇳 local · ✈️ import)
| Part | Qty | Status |
|---|---|---|
| 2020 profile, ~342 mm (column) | 1 | 📦 Ender, cut |
| V-wheels + eccentric spacers | 4 | 📦 Ender (count them) |
| NEMA17, shaft **cut to ~14 mm** (a stock 24 mm shaft hits the column) | 1 | 📦 Ender |
| Rack M1 ~320 mm (2 printed pieces, lying in the front slot) + 20T M1 pinion (D-bore + set screw) | 1 + 1 | print PLA/ABS (or 🇹🇳) |
| MG996R + round horn | 1 | 📦 |
| **Steel U servo bracket** (photo) | 1 | 📦 (measure: arm length, inner width; `G.L_U`, `G.T_U`) |
| Electromagnet 12 V 5 kg, Ø27 × 20 (KK-P25/20 type) | 1 | 🇹🇳 (to confirm) |
| Printed carriage plate + servo cradle (rear pivot cap) | 1 + 1 | print PLA/ABS |
| M3 pivot screw/pin, M3/M4 screws, T-nuts | – | 📦 |
| Grail steel plate: 1–1.5 mm mild steel, or a big fender washer | 1–2 | 📦 |
| Magnet float: 2 × M3 shoulder screw + small springs | 2 | 📦 / 🇹🇳 |

### Rigidity and layout notes
- **Arm:** held on both sides of the servo by the U bracket (horn + pivot pin). The servo spline only gives the
  torque, not the bending.
- **Carriage:** 4 V-wheels, 38 mm apart vertically (the height budget allows no more). Moment from the Grail
  ≈ 0.2 N·m → ~6 N per wheel. Preload with the eccentric spacers.
- **Servo cradle:** printed L from the carriage plate to the servo, ~70 mm long. The weakest link: ribs, ABS,
  test it.
- **Column:** bolt it along its back (≥ 3 T-nuts) to a robot frame member, not only at the base (corner bracket
  70×70×40 in `sw/`).
- **Rack and pinion can be back-driven:** at 100 s / e-stop the carriage drops. After the release the arm parks
  at 140°. Estimate (not simulated): the magnet then comes down ~15 mm beside the Grail, onto the roof edge, not
  onto it. Check this on the real roof, or park the carriage on a stop before 100 s.

### Robot layout it needs (for Seif's roof sketch)
- The lift on a **driving face** (the robot drives straight into the Grail). Bay inside the robot:
  x −113 … 0 × y −109 … 41 (frame of this model), full height. Two roof openings (A: column + carriage, B: servo +
  arm swing) and a 60 mm slot in the face skin for the bracket.
- Roof top at **305 mm** assumed. Every height margin depends on it (change `G.ROOF` and re-run).
- The Grail lands next to the lift, ~80–165 mm in from the face. Keep that roof area free (beacon support, e-stop,
  launcher elsewhere).

### Open points
1. Real U-bracket dimensions (assumed: arm 45 mm, inner width 51.4, 2.5 thick).
2. The 3 missing v1 parts (only matters for judging v1 exactly; v2 doesn't use them).
3. Grail design: symmetric 80 cube, ≤ 150 g, steel plate on one face at 25 mm from both ends (FAQ Q3).
4. Pick-up tolerance (F2): test how far off the magnet can still grab (target ± 5 mm in distance).
5. Magnet supply: 12 V MOSFET + diode, reverse pulse (Hamza Bjaoui).
