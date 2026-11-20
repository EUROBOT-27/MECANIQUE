# Grail v2: top grip + 180° flip onto the roof (Flipper and Flipper-S)

> **Where we are (2026-11-20, Seif + Claude)**
> - **Two versions (D-029): Flipper (rack lift, was "B") and Flipper-S (lead-screw lift, was "B2").** Same flip.
>   Electromagnet Ø30 first. **Flipper is the priority: taken all the way to printing.**
> - **Flipper is now built from real parts** (`fc/flipper_fc.py`): Two Trees X carriage (plate + 3 V-wheels + fasteners),
>   real 2020, real NEMA17, Seif's printed rack, new pinion (`fc/flipper_pinion_fc.py`, print files in `print/`).
> - Both pass the checks so far (bounding boxes only, no clash check yet).
> - **Later: a suction-cup version**, also for the **gate lintel** (see below).

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
| Grail bay (layout-v1, T1 back) | x 66–150, y −52…40, z 78–300 (right wheel + drive motor under it) |
| Grail | 70 × 70 × 80, 150 g, steel plate on its top |
| Magnet | 12 V, **Ø30** (same model as `../grail-lift/sw/Magnet 5KG.step`, Ø30 version); height 22 + M4 stud **assumed** (P30/22) 🇹🇳; seat Ø30.3 (Baha's, intentional) |
| Flip head (`common.flip_head`) | MG996R lying, body down, horn on −y; Ø5 shaft into a **625** in a +y cheek joined under the pivot (the arm and the Grail never go there); arm + magnet cup |

## Flipper: rack lift from real parts (`fc/flipper_fc.py`)
Two Trees Bluer V2 **X-axis carriage** on the real **2020**, Seif's **printed rack** (m1, `parts/cremaillere.STL`),
**NEMA17** + **pinion v2**, flip head from `common.flip_head` (MG996R + 625 cheek + arm + Ø30 magnet in a cup).
- **Why it looks like Baha's:** the X plate sits 2 mm from the profile's front face and its wheels ride the two side
  faces, so the rack goes in the **back face's slot**. The NEMA shaft runs along y, and the motor must clear the
  eccentric wheel (5 mm, Seif): hence a **long pinion hub**.
- **Rack slid in from the profile's end** (Seif, 2026-11-20), like a T-nut: wide part in the slot cavity, **V back on
  the cavity's inner faces** (seat computed from the real sections: nose 6.2 below the face, 0.45 play to the lips).
  Its teeth are then 1.2 mm below the face, so the **pinion's 5 mm gear dips 3.2 mm into the slot** (lip 6.35 wide).
  That is exactly why Baha's rack has a 5.7 tooth strip and his pinion 5 mm teeth.
- **Rack cut to the pinion's travel** (z 114–254, 140 long): the back slot stays free at both ends for fixations.
- Placement (robot frame): profile centre y 4, x 110 (or 85, INWARD variant); plate faces the right face (+x); the
  servo mount on the plate's front reaches the flip axis x 152.5. **LZ 58:** pivot 138 → 254 (flip) → 248 (place)
  → 242 (stowed), 122 mm of travel.
- **Motor:** standard 40 mm NEMA17 for now (Seif, 2026-11-20), face 5 mm past the eccentric wheel. Body at y −70…−33:
  **18 mm past the Grail bay** (y −52) toward the back module. A shorter NEMA is a quick fix (motor + pinion hub).

### Column fixation: three variants to choose from (Seif, 2026-11-20)
The 2020's bottom end sits right above the right wheel (x 106–150, top z 74). Run with `FLIPPER_FIX=slot|bridge|inward`
→ `CAD_FC/FLIPPER_<VARIANT>.FCStd` + report. The top fixation is the same in all three: a **2020 cross-member along x**
from the column's back face inward to the core (x 40), z 255–275, joint plate on top (6–7 mm under the arm's path).

| | **SLOT** | **BRIDGE** | **INWARD** |
|---|---|---|---|
| Idea | 2020 corner brackets in the back slot's **free ends** (rack cut to the pinion travel) | a plate **arching over the wheel**, legs to the floor beside it | column **over the drive motor** (x 85), on a saddle above it |
| Bottom | L-bracket (z 78–98) onto a 2020 cross-member along x, z 58–78, above the drive motor (top 55.5) | plate z 76–81, x 96–124, legs at y −45…−40 and 38…42; column bolted through its end hole (M5) | saddle z 57–60, legs at y ±21–25 beside the drive motor; column bolted through its end hole |
| Moves | nothing | everything 3 mm up (column 81–278) | column, carriage, motor 25 mm inward; servo mount reaches **53 mm** to the pivot (28 now) |
| Parts | 2 × 2020 cross-members + 2 corner brackets 📦 | printed / alu arch + top member | printed / alu saddle + top member |
| Fits | all clear; motor 18 mm past the bay (y) | all clear; motor 18 mm past the bay (y) | all clear, but **the NEMA, pinion and motor bracket leave the bay inward (x 46–66)**, toward the back module |
| Checks | same cycle for all: highest point 335.7, the Grail never enters the body, nothing in the Grail's swept zone | | |

### Printed parts so far (`print/`, robot frame at the pick pose)
| Part | What | Fixing |
|---|---|---|
| `FLIPPER_ARM` (12 g) | hub Ø24 + bar 14 × 10 + magnet cup (seat Ø30.3, 18 deep, magnet face 4 mm proud), one solid | round horn's disc in a Ø21.4 pocket + Ø9.8 boss recess, **4 × M2 × 12** from +y into the horn holes (Ø2.5, as the tested T9 pinion); Ø5 steel pin pressed 6 deep from +y; magnet M4 stud + nut in a pocket |
| `FLIPPER_SERVO_MOUNT` (30 g) | base 8 thick on the X plate's front + servo plate under the ears (body cut-out) + 625 cheek joined under the pivot, one solid | **2 × M5×35** replacing the upper wheel screws (nylocs move to the base's front), **2 × M3** into the plate's 2 tapped holes (Ø2.5, 20 apart), recess for the eccentric's nyloc; servo: **2 × M3 × 12 + nuts in pockets**; **625 seat Ø16.2 open on +y**, lip on the arm side |
| `FLIPPER_MOTOR_BRACKET` (15 g) | plate 4.5 thick between the motor face and the eccentric wheel (0.5 mm off it), NEMA17 4 × M3 + Ø23 pilot, 2 bridges to the X plate's back tabs (above / below the wheel) | 4 × M3×25 into the tabs: **drill Ø2.5 + tap M3** (the tabs have no holes) |
| `FLIPPER_RACK_140` | Seif's rack cut to the pinion's travel | slid into the back slot from the profile's end, V back on the cavity's inner faces |
| `FLIPPER_PINION` | below (39 long, 5 mm teeth) | M3 insert K5 + set screw on the shaft flat |

Checks (report): no body part enters the zone the Grail sweeps (radius ≥ 58.5 from the axis, −87…143°); the servo body
stays in the bay (y −50.4).

Fits: ABS values from the clapets v7 coupons (`common.FIT`): bearing seat +0.2, horn pocket Ø21.4, M2 Ø2.5, M3 Ø3.5,
M4 Ø4.6, M5 Ø5.6, nut pockets M3 6.0 × 6.9 × 2.8 / M4 7.4 × 8.4 × 3.6, Ø5 pin press Ø5.0.

### Print orientation (ABS, Bambu X1 Carbon, D-023)
| Part | Bed face | Why |
|---|---|---|
| `FLIPPER_ARM` | the hub's −y face (horn pocket) down, arm plane on the bed | hub axis vertical: horn pocket, M2 holes and pin hole round and coaxial; bar loads along the layers. The cup seat (axis horizontal) needs supports: loose fit (Ø30.3) |
| `FLIPPER_SERVO_MOUNT` | −y down (servo plate side) | 625 seat axis vertical (round); servo plate and cheek flat; the base is a wall, its M5/M3 holes print horizontal (teardrop OK) |
| `FLIPPER_MOTOR_BRACKET` | the motor face (y −33) down | plate flat, motor holes + pilot vertical; bridges grow up from it |
| `FLIPPER_PINION` | the gear face down | axis vertical (teeth, D bore, insert hole horizontal on the hub) |
| `FLIPPER_RACK_197` | as Seif printed it | |
(STEP/STL are in the robot frame at the pick pose: rotate in the slicer.)

### Assembly order
1. Carriage: drill Ø2.5 + tap M3 the X plate's two back tabs (2 holes each, `FLIPPER_report.txt` gives the positions).
2. NEMA17 on `FLIPPER_MOTOR_BRACKET` (4 × M3; the one next to the wheel is a button head in its counterbore). Pinion
   on the shaft (M3 insert + set screw on the flat). Bracket onto the tabs (4 × M3 × 25).
3. `FLIPPER_SERVO_MOUNT` on the X plate's front: the 2 upper wheel screws become M5 × 35 through the base (nylocs on its
   front), 2 × M3 into the plate's tapped holes. MG996R into the servo plate (2 × M3 × 12 + nuts). 625 pressed into its
   seat from +y.
4. Round horn screwed to `FLIPPER_ARM` (4 × M2 × 12 from +y). Arm + horn onto the servo spline (no centre screw: the pin
   holds the arm). Then push the **Ø5 pin through the 625 into the hub** (press).
5. Magnet into the cup (M4 nut in its pocket). Carriage onto the 2020 (eccentric to preload), rack in the back slot.

### Pinion v2 (`fc/flipper_pinion_fc.py` → `print/FLIPPER_PINION.step/.stl`)
Redo of Baha's `parts/el_pignon.STEP` (m1 20T, 5 mm teeth at the end of a Ø10.5 × 29 hub, Ø5.1 bore, radial hole for an
**M3 insert K 5.0** = D-025 read backwards, 2 solids). His geometry was right for a rack inside the slot (5 mm teeth on a
long hub); what was weak was the hub. The new one:
- **involute teeth 5 wide** (they enter the slot: lip 6.35), one solid, **D bore** Ø5.15 / flat 4.6
- **hub Ø16 × 25** (6 mm of wall for the 4 mm insert, 8 mm from the motor end; el pignon had 2.7 mm), then a
  **Ø12 × 9 neck** where it passes the profile's back face; gear centre 37 mm from the motor face (motor 5 mm past the wheel)
- stiffness at 10 N on the teeth: steel shaft ~0.02 mm, hub ~0.3 MPa; teeth ~6 MPa (ABS fine)

## Flipper-S: lead-screw lift (`fc/flipper_s_fc.py`, was B2; on hold, Flipper first)
The Flipper flip on the hardware of Baha's "essai vis ecrou corrigé" (`../Grail_v1/essai vise ecrou corrigé/`).
LZ 50, pivot 130 → 262 (flip) → 256 (place) → 250 (stowed), 138 mm of travel.
- **T8 screw + flange nut**, **2 × Ø8 rods + 4 LM8UU** (2 per rod, carriage 48 tall), **608** in a bottom and a top plate.
  Column in a line along x at **y −28**: rods x 77 / 125, screw x 97. That keeps it behind the arm.
- **Motor not under the screw** (the right wheel and drive motor are there): the NEMA17 **stands on the bottom plate**
  (the bay floor, z 78–88), shaft down. A **GT2 belt 1:1** (pulleys z 64–78, loop ~135) drives the screw, at x ≤ 105:
  off the wheel (x ≥ 106) and above the drive motor.
- Flip head as written before `common.flip_head` existed (same design, own copy: to switch to `flip_head`).

Report `CAD_FC/FLIPPER_S_report.txt` (Ø30 magnet): highest point 338; the Grail never enters the body; 78.5 mm out at
flip 45°; carriage 2 mm under the top plate at the flip; everything inside the bay except the pulleys + belt under its
floor.

## Flipper vs Flipper-S
| | Flipper (rack) | Flipper-S (lead screw) |
|---|---|---|
| Lift drive | NEMA17 rides on the carriage, pinion on a fixed rack | NEMA17 fixed on the bay floor, GT2 belt to a T8 screw |
| Guide | Two Trees X carriage on a 2020 (📦) | 2 × Ø8 rods + 4 LM8UU (rods 📦, LM8UU 🇹🇳 or from the SCS8UU 📦) |
| Power off / e-stop | carriage drops (back-driven) | holds (T8×8 may creep; T8×2 holds but 4× slower) |
| Moving mass | ~0.7 kg (motor rides) | lighter |
| Fits the Grail bay | yes, except the 40 mm NEMA (14 mm past y −52) | yes |
| Tested | rack printed, fits the profile | — |

## Later: suction-cup version, also for the gate lintel (Seif, 2026-11-20)
Same mechanism with a **suction cup instead of the magnet**:
- **Gate lintel:** pick the **2nd stone of a stack from its top (z 220)**, flip it 180° and lift a little past 320.
  It lands upside down **on the two towers**, and the cup ends under it, in the ~100 mm gap between the towers. The
  actuator stays under the stone, so ≤ 350. The stone's long side runs along the flip axis.
- **Grail:** the same cup picks the Grail by its top (no steel plate needed).
Details and numbers once the electromagnet version works. Concept notes: `../concepts/gate-lintel.md`.

## Archived: A, C (not chosen, 2026-11-19) and the B concept (superseded by Flipper)
In `archive/` (script + report).
- **A, pivot:** one servo, no lift, axis fixed at z 193. Arm 121 mm long: **128 mm out** while turning (perimeter +~96),
  and the Grail slides onto the roof sideways.
- **C, rolling:** one NEMA17. A half gear R60 rolls on a fixed rack, so height sets the angle. **The Grail dips 8–35 mm
  below the roof top** while crossing the roof edge (the axle is still low at 110–170°).
- **B concept:** simplified carriage, column at y −70 (outside the bay). Replaced by `fc/flipper_fc.py`.

## Files
| Path | What |
|---|---|
| `fc/common.py` | robot context (layout-v1 numbers), Grail, magnet, MG996R placement, **`flip_head()`**, rack-lift unit, cycle table |
| `fc/flipper_fc.py` | **Flipper** generator (real parts; numbers in `class G`) |
| `fc/flipper_pinion_fc.py` | **pinion v2** → `print/FLIPPER_PINION.step/.stl` |
| `fc/flipper_s_fc.py` | **Flipper-S** generator (numbers in `class G`) |
| `parts/` | inputs: `cremaillere.STL` (Seif's rack, m1, fits the profile), `el_pignon.STEP` (Baha's pinion) |
| `print/` | print files |
| `CAD_FC/FLIPPER_SLOT/BRIDGE/INWARD.FCStd`, `FLIPPER_S.FCStd`, `FLIPPER_PINION.FCStd` | models: pick pose + ghost at the place pose + robot context (body, roof with the slot, right wheel, drive motor, Grail bay) |
| `CAD_FC/*_report.txt` | cycle table + summary + layout envelope + parts (📦 / 🇹🇳 / ✈️) |
| `archive/` | A, C, B concept |
| Real bought parts | `../resources/two-trees-bluer-v2-parts/` (X carriage, profile, NEMA17: see its `SOURCE.md`) |

Run (from this folder):
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_pinion_fc.py     # first: flipper_fc.py reads print/FLIPPER_PINION.step
set FLIPPER_FIX=slot& "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_fc.py     # ~1 min; slot | bridge | inward
set FLIPPER_PRINT=1& ...                                                                         # also write the print files
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_s_fc.py
```
Never edit the `.FCStd` by hand: change the generator and re-run it. Colours are only set when run from the FreeCAD GUI.

## To printing (Flipper)
1. ~~Printed parts drawn for real~~ (2026-11-20): arm + magnet cup, servo mount + 625 cheek, motor bracket, rack 197.
   Still to do on them: ABS fits from the clapets v7 coupons (holes, 625 seat, servo cut-out), print orientation.
2. ~~X plate holes~~ (sliced: Ø7.5 eccentric, 2 × Ø5.4 upper wheels, 2 × Ø2.5 tapped M3 20 apart; the back tabs have
   no holes: drill for the motor bracket).
3. Roof slot (x ~90–151, y ±20) and how the Grail sits on both sides of it; check against layout-v1's roof.
4. Bottom endstop / homing; magnet cable loop around the flip axis; sprung magnet mount (CDC D4).
5. Back-drive of the rack (carriage drops when the NEMA is off): accept, or a brake / self-locking choice.
6. Shorter NEMA once Seif knows what we have (motor length + pinion `HUB_L`).
7. Clash check + motion check before printing (only when Seif asks).
8. STEP / STL / DXF print files + a short assembly sheet.
