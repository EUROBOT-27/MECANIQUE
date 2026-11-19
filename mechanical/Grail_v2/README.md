# Grail v2: top grip + 180° flip onto the roof (options B and B2)

> **Where we are (2026-11-20, Seif + Claude)**
> - **Two versions developed in parallel (D-029): B (rack lift) and B2 (lead-screw lift).** Same flip, same arm,
>   different lift. Electromagnet first.
> - Both pass every check so far (bounding boxes only, no clash check yet): actuators ≤ 340, the Grail never enters
>   the body, the magnet leaves the Grail straight down.
> - **Later: a suction-cup version** of the same mechanism, also meant for the **gate lintel** (see below).
> - Next: perfect B and B2 (list at the bottom).

Fresh start after Baha's Grail v1 (`../Grail_v1/`). Earlier Grail lift work (Maatoug, v1–v3): `../grail-lift/`
(reference). Requirements: `../grail-lift/docs/CDC.md`.

## How it works
1. The magnet comes down onto the Grail's **top** (Grail on the floor, 10 mm from the right face).
2. **Lift** with the arm pointing down-outward.
3. Near the top, the servo **flips the arm 180°** about an axis along the right face. The Grail swings out, over the
   top, and comes down **upside down** above the roof.
4. **Lower** until the Grail sits on the roof. **Magnet off.**
5. **Lower 6 mm more**: the magnet leaves the Grail straight down, into a **slot in the roof**. This is also the
   stowed pose at the start.

Why a flip: a top grip can't end above the Grail. With the Grail on the roof (bottom ≥ 301), a magnet on its top would
be at about 386 > 350 [GR F.3]. Turned over, the gripper ends **under** the Grail.

Why the flip axis is at x 152.5 (2.5 mm past the face): a 180° turn maps the pick pose onto the place pose only if the
axis is halfway between them (Grail centre x 195 on the floor, x 110 on the roof).

| Common numbers (`fc/common.py`, from layout-v1) | |
|---|---|
| Right face | x 150 |
| Roof | top 306 (plate 300–306), strip y ±38 |
| Right side bay (Grail) | x 66–150, y ±40, z 78–300 (right wheel + drive motor under it) |
| Grail | 70 × 70 × 80, 150 g, steel plate on its top |
| Magnet | 12 V 5 kg, Ø25 × 20 (KK-P25/20 type) 🇹🇳 |

## B: rack lift (`fc/b_lift_flip_fc.py`)
2020 column + Ender-style carriage (3 V-wheels) + **m1 rack + 20T pinion on a NEMA17** (Baha's rack, Seif's test print
fits) + MG996R flip. The arm is 45 mm under the pivot at the pick (LZ 45). Pivot 125 → 269 (flip) → 261 (place).

Report `CAD_FC/B_LIFT_FLIP_report.txt`:
- highest actuator point 340; the Grail never enters the body; 73 mm out at flip 45° (perimeter +~35)
- flip 1.7 kg·cm (5.5× on the MG996R); the rack can be back-driven (carriage drops at 100 s, Grail already released)

**Known problem: the column is at y −70, outside the right bay** (the back module is there). B2 shows how to fit a
column in the bay; B has to follow.

## B2: lead-screw lift (`fc/b2_screw_fc.py`)
Option B with the hardware of Baha's "essai vis ecrou corrigé" (`../Grail_v1/essai vise ecrou corrigé/`). LZ 50,
pivot 130 → 262 (flip) → 256 (place) → 250 (stowed), 138 mm of travel.
- **T8 screw + flange nut**, **2 × Ø8 rods + 4 LM8UU** (2 per rod, carriage 48 tall), **608** in a bottom and a top plate.
  Column in a line along x at **y −28**: rods x 77 / 125, screw x 97. That keeps it behind the arm, which crosses the
  roof at |y| ≤ 16.
- **Motor not under the screw** (the right wheel and drive motor are there): the NEMA17 **stands on the bottom plate**
  (the bay floor, z 78–88), shaft down. A **GT2 belt 1:1** (pulleys z 64–78, loop ~135) drives the screw, at x ≤ 105:
  off the wheel (x ≥ 106) and above the drive motor (z 55.5).
- **Arm held on both sides** (as the corrigé): MG996R horn (−y) + Ø5 shaft into a **625** in a +y cheek. The cheek joins
  the servo bracket under the pivot, a zone the arm and the Grail never reach. Servo body pointing down.

Report `CAD_FC/B2_SCREW_report.txt`:
- highest actuator point 336; the Grail never enters the body; start 14.5 mm past the face; 77 mm out at flip 45°
  (perimeter +~38, budget ~67)
- carriage 2 mm under the top plate at the flip; nut 16.5 mm above the bottom plate at the pick
- servo reaches 38 mm, cheek 46 mm from the axis; the Grail's nearest point is 51 mm away
- flip 1.8 kg·cm (5.2×); screw 0.014 N·m
- **everything inside the right bay**, except the pulleys + belt under its floor

## B vs B2
| | B (rack) | B2 (lead screw) |
|---|---|---|
| Lift drive | NEMA17 rides on the carriage, pinion on a fixed rack | NEMA17 fixed on the bay floor, GT2 belt to a T8 screw |
| Guide | 2020 + 3 V-wheels (Ender carriage 📦) | 2 × Ø8 rods + 4 LM8UU (rods 📦, LM8UU 🇹🇳 or from the SCS8UU 📦) |
| Power off / e-stop | carriage drops (back-driven) | holds (T8×8 may creep; T8×2 holds but 4× slower) |
| Moving mass | + motor (~280 g) | lighter (no motor on the carriage) |
| Fits the right bay | not yet (column at y −70) | yes |
| Tested | rack + pinion printed, fits | — |

## Later: suction-cup version, also for the gate lintel (Seif, 2026-11-20)
Same mechanism with a **suction cup instead of the magnet**:
- **Gate lintel:** pick the **2nd stone of a stack from its top (z 220)**, flip it 180° and lift a little past 320.
  It lands upside down **on the two towers**, and the cup ends under it, in the ~100 mm gap between the towers. The
  actuator stays under the stone, so ≤ 350. The stone's long side runs along the flip axis.
- **Grail:** the same cup picks the Grail by its top (no steel plate needed).
Details and numbers to do once the electromagnet version works. Concept notes: `../concepts/gate-lintel.md`.

## Archived (not chosen, 2026-11-19): A and C
In `archive/` (script + report).
- **A, pivot:** one servo, no lift, axis fixed at z 193. Arm 121 mm long: **128 mm out** while turning (perimeter +~96),
  and the Grail slides onto the roof sideways.
- **C, rolling:** one NEMA17. A half gear R60 rolls on a fixed rack, so height sets the angle. **The Grail dips 8–35 mm
  below the roof top** while crossing the roof edge (the axle is still low at 110–170°).

## Files
| Path | What |
|---|---|
| `fc/common.py` | robot context (layout-v1 numbers), Grail, magnet, MG996R placement, rack-lift unit, cycle table |
| `fc/b_lift_flip_fc.py` | **B** generator (numbers in `class G`) |
| `fc/b2_screw_fc.py` | **B2** generator (numbers in `class G`), with the layout-envelope check |
| `CAD_FC/B_LIFT_FLIP.FCStd`, `CAD_FC/B2_SCREW.FCStd` | pick pose + ghost at the place pose + robot context (body ghost, roof with the slot, right wheel, drive motor) |
| `CAD_FC/*_report.txt` | cycle table (heights, protrusion, Grail vs body) + summary + parts (📦 / 🇹🇳 / ✈️) |
| `archive/` | variants A and C |

Run (from this folder, a few seconds each, they can run in parallel):
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/b_lift_flip_fc.py
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/b2_screw_fc.py
```
Never edit the `.FCStd` by hand: change the generator and re-run it. Colours are only set when run from the FreeCAD GUI.

## To perfect (next)
1. **B:** move the column into the right bay (as B2), check the motor-on-carriage fits.
2. Real carriage (B2: LM8UU clamps, nut screws; B: Ender plate holes), servo bracket + 625 cheek as one printed part.
3. Roof slot (x ~95–151, y ±15) and how the Grail sits on both sides of it; check against layout-v1's roof (e-stop,
   beacon support).
4. Bottom endstop / homing; belt tension (B2, slotted motor holes); T8 lead choice (B2).
5. Magnet mount (sprung, CDC D4), wiring of the magnet through the flip (cable loop around the axis).
6. Real Grail design (size, mass, steel plate), FAQ Q3.
7. Clash check and motion check once the design settles (only when Seif asks).
