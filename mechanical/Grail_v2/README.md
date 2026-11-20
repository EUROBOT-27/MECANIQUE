# Grail v2: top grip + 180° flip onto the roof (Flipper and Flipper-S)

> **Where we are (2026-11-20, Seif + Claude)**
> - **Two versions (D-029): Flipper** (rack lift, was "B") and **Flipper-S** (lead-screw lift, was "B2"), same flip,
>   Ø30 electromagnet first. **Flipper is the priority, on Ayoub's `base_330_js`.**
> - Flipper: real parts (Two Trees X carriage, 2020, NEMA17), printed saddle, rack, pinion, motor bracket, servo mount,
>   arm, top cap. **Static and motion collision checks: 0 clashes** (forward cycle + way back). GIF and views in `sim/`.
> - **Waiting on Seif:** the 8 saddle holes in the base plate (positions below), then printing.
> - **Later:** a suction-cup version, also for the **gate lintel**.

Fresh start after Baha's Grail v1 (`../Grail_v1/`). Earlier Grail lift work (Maatoug, v1–v3): `../grail-lift/`
(reference). Requirements: `../grail-lift/docs/CDC.md`.

## How it works
1. The magnet comes down onto the Grail's **top** (Grail on the floor, 10 mm from the right face).
2. **Lift** with the arm pointing down-outward.
3. At the top, the servo **flips the arm 180°** about an axis along the right face. The Grail swings out, over the
   top, and comes down **upside down** onto the Grail deck.
4. **Lower 6** until the Grail sits on the deck. **Magnet off.**
5. **Lower 6 more** (the magnet leaves the Grail straight down, into the deck's slot) and **14 more**, then **turn the arm
   back** 180 → 0 and lower to the pick height (Seif: "put, go down, then rotate").

Why a flip: a top grip can't end above the Grail. With the Grail on the roof (bottom > 300), a magnet on its top would
be above 350 [GR F.3]. Turned over, the gripper ends **under** the Grail.

## Flipper on base_330_js (`fc/flipper_fc.py` → `CAD_FC/FLIPPER_B330.FCStd` + `_report.txt`)
Robot frame = `../base_330_js` (`CAD/base_330_js_assembly.FCStd`): X = wheel axis, +Y = front (clapets), z 0 = table,
right face = plate edge **x 168**. The Flipper sits over the right drive wheel, between the front clapets and the future
back module (back-right corner).

| Key numbers | |
|---|---|
| Grail | 70 × 70 × 80, steel plate on its top; picked at x 178–248, placed upside down at x 93–163, y ±35 |
| Grail deck | **top z 320** (6 mm plate, slot for the arm x 108–169, y ±20); the rest of the robot's top can be at 350. Placeholder: supports not designed. Env `GRAIL_ROOF` |
| Flip | axis along y at **x 170.5** (halfway between pick and place); **LZ 80** (pivot above the Grail's top at the pick) |
| Pivot height | 160 (pick) → 246 (flip) → 240 (place) → 234 (magnet off) → **220 (turn back)** → 160 |
| Lift | **86 up** (+ 6 + 6 + 14 down after the flip); travel = deck 320 − Grail 80 − 2 × LZ + 6 |
| Height | highest actuator point **344** (flip 150°), limit 350; the deck can't go above ~324 (the arm swings ~24 above the place height) |
| Perimeter | start (stowed) 16.8 mm past the face (~+2); **100.5 out at flip 60°** (~+69, deployed budget 1400) |
| Flip torque | 2.6 kg·cm at 65° (MG996R ~9.4: 3.6×) |
| Magnet | 12 V, **Ø30** × 22 + M4 stud (**height and stud assumed**, P30/22: to measure); seat Ø30.3 (intentional) |

**Lift:** Two Trees Bluer V2 **X carriage** (steel plate + 3 V-wheels) on a real **2020 cut to 168.5** (z 84.5–253),
Seif's **printed m1 rack** cut to **110** (z 119–229), **slid in from the profile's end** like a T-nut (V back on the slot
cavity's inner faces). **NEMA17** (standard 40 mm for now; shorter = quick fix) rides on the carriage, **pinion v2**
(5 mm teeth dip 3.2 into the slot). The rack back-drives when the NEMA is off.

**Column fixation:**
- **Bottom: printed saddle** (`FLIPPER_SADDLE_SOCLE`, 169 g ABS) over the drive wheel + motor + odometry, on 4 legs on the
  free plate zones (Seif's sketch). Tunnel R45 around the worst-case wheel Ø80 (crown 82, deck top 85). The column stands
  in a **blind socket** (3.5 deep + 3 mm collar), a **heel** on its back face (2 × M5 into T-nuts, key in the slot, 2 side
  gussets), **2 tongues** in the plate's wheel well (centre it in y). **Floor: 8 × M4 × 16 + nuts under the plate.**
- **Top:** 2020 cross-member (x 40–118, z 233–253) **beside** the column, tops flush: **blind joint** (M5 head slid into
  the column's back slot from the open top) + printed **TOP_CAP** (4 thick: countersunk M5 into the column's end, M5 into a
  T-nut in the cross-member). Where the cross-member goes next: a centre column, or rings on the front / back modules'
  profiles carrying floors for the electronics (`../concepts/electronics-column.md`).

**Way back window:** the cup turns on a circle (r ~91 around the pivot) that rises ~10 mm above its release height early
in the turn back. With less than 12 mm of drop after the release it hits the placed Grail; with more than 14 the arm's bar
meets the column's top. Hence the drop of 14, the **4 × 45° chamfer filed on the column's +x top edge**, the cap stopping
4 short of that face (3 × 45° edge) and its **countersunk** column screw.

**Clearances (real distances):** saddle ↔ base parts: clapets rails 3.0, hinge 4.0, odometry bracket 4.2, drive motor
4.5, worst-case wheel 5.0; saddle ↔ carriage at the pick: X plate 3.3, wheels 3.9, motor bracket 4.1. Motion: see Checks.

**For the back module:** the NEMA rides at x 89–131, y −70…−11, z 110–272 (column x 118–138, y −6…14); Grail spot
x 93–163, y ±35.

### Printed parts (`print/`, ABS on the Bambu X1 Carbon, D-023; STEP/STL in the robot frame at the pick pose: rotate in the slicer)
| Part | What | Fixing | Bed face |
|---|---|---|---|
| `FLIPPER_ARM` (~14 g) | hub Ø24 + bar 14 × 10 + magnet cup (seat Ø30.3, wire hole Ø3.8) | round horn's disc in a Ø21.4 pocket, **4 × M2 × 12** into the horn; Ø5 pin pressed 6 deep (last, through the 625); magnet M4 nut in a pocket | hub's −y face (horn pocket) down; the cup needs supports (loose fit) |
| `FLIPPER_SERVO_MOUNT` (30 g) | base on the X plate's front + servo plate + 625 cheek joined under the pivot; zip-tie slots; lip on the X plate's lower edge | **2 × M5 × 35** replacing the upper wheel screws (nylocs on its front), **2 × M3 × 12** into the plate's tapped holes; servo **2 × M3 × 10 + nuts**; **625** seat Ø16.2 | −y (servo plate side) down |
| `FLIPPER_MOTOR_BRACKET` (14 g) | plate 4.5 between the motor face and the eccentric wheel (0.5 off it), flanges, 2 bridges to the X plate's bottom tabs (form fits); no wall < 2.5 | NEMA **4 × M3 × 8** (button heads; one counterbored next to the wheel); **2 × M3 × 20** into the tabs: **drill Ø2.5 + tap M3** (no holes there) | motor face (y −33) down |
| `FLIPPER_PINION` | m1 20T, 5 mm involute teeth, hub Ø16, Ø12 neck, D bore Ø5.15 / 4.6 (`fc/flipper_pinion_fc.py`) | **M3 insert K5** + M3 × 6 set screw on the shaft's flat | gear face down |
| `FLIPPER_RACK_110` | Seif's rack (`parts/cremaillere.STL`) cut to 110 | slid into the back slot from the column's top end | as Seif printed it |
| `FLIPPER_SADDLE_SOCLE` (169 g) | see "Column fixation"; 12 lightening pockets (201 g without) | 8 × M4 × 16 to the base plate (Ø9 channels from the top); heel 2 × M5 × 12 + T-nuts | floor face (z 16.5) down; supports inside the tunnel |
| `FLIPPER_TOP_CAP` (~3 g) | 4 thick over the column + cross-member tops | **countersunk M5 × 12** into the column's end (flush), M5 × 8 button into a T-nut | bottom down |

Fits: ABS values from the clapets v7 coupons (`common.FIT`): bearing seat +0.2, horn pocket Ø21.4, M2 Ø2.5, M3 Ø3.5,
M4 Ø4.6, M5 Ø5.6, nut pockets M3 6.0 × 6.9 × 2.8 / M4 7.4 × 8.4 × 3.6, Ø5 pin press Ø5.0. Chamfers 1 mm on the convex
straight edges (count per part in the report; the kernel refuses some). Every fastener is modelled in its hole
(groups `8a/8b/8c_SCREWS_…`).

### Workshop operations (not printed)
1. **2020 column:** cut to **168.5**; tap M5 its top end hole; **Ø5 access hole** through the +x face at z 243 (blind
   joint); **file a 4 × 45° chamfer on the +x top edge**.
2. **2020 cross-member:** cut (x 40–118); tap M5 its column-side end hole (blind joint).
3. **X plate:** drill Ø2.5 + tap M3 in the 2 bottom tabs (positions in the report, "FLIPPER_MOTOR_BRACKET").
4. **Base plate:** 8 × Ø4.4 at (88, −53.5), (120, −53.5), (88, 53.5), (120, 53.5), (33, −33), (66, −33), (33, 32),
   (58, 32) — **not in the plate model yet: Seif confirms first.**

### Assembly order
1. Saddle onto the base plate (8 × M4 × 16 + nuts). Column into its socket, heel screws into the T-nuts.
2. NEMA17 on the motor bracket (4 × M3 × 8), pinion on the shaft (insert + set screw on the flat). Bracket onto the X
   plate's tabs (2 × M3 × 20).
3. Servo mount on the X plate's front (2 × M5 × 35 for the upper wheels, 2 × M3 × 12). MG996R into it (2 × M3 × 10 +
   nuts). 625 pressed into its seat from +y.
4. Round horn screwed to the arm (4 × M2 × 12). Arm + horn onto the servo spline, then the **Ø5 pin through the 625 into
   the hub** (press). Magnet into the cup (M4 nut).
5. Carriage onto the column from the top (eccentric to preload), rack slid into the back slot, then the cross-member:
   blind-joint screw head into the back slot from the top, tighten through the access hole; top cap (countersunk M5 +
   M5 × 8 into the T-nut).

### Checks (all on base_330_js, real solids)
| Check | Script → result | Result |
|---|---|---|
| Fit + cycle table | `fc/flipper_fc.py` → `CAD_FC/FLIPPER_B330_report.txt` | highest 344, Grail never inside the body, arm vs column / carriage at place + stowed |
| Static collision | `fc/flipper_static_check.py` → `CAD_FC/FLIPPER_static_check.txt` (~2 min) | **0 clashes**: pick pose + place pose vs base plate, deck, 350 sheet, base_330_js parts. Expected overlaps listed (threads, pressed parts, gear mesh, holes still to drill) |
| Motion, forward | `fc/flipper_motion_check.py` → `CAD_FC/FLIPPER_motion_check.txt` (~25 min) | **0 clashes** over 65 poses; tightest: pinion ↔ column 0.6 (bottom), horn screws ↔ servo mount 1.5 (flip 70°), Grail ↔ deck 1.5, arm ↔ deck 2.0 (flip 160°) |
| Motion, way back | `FLIPPER_MOTION=back` → `CAD_FC/FLIPPER_motion_check_back.txt` (~3 min) | **0 clashes** over 43 poses; arm ↔ cap screw 2.6, arm ↔ column 3.1, magnet ↔ placed Grail 3.2 |

Shared lists of expected overlaps: `fc/check_common.py`. All printed parts are checked as valid single solids before
export (a chamfer step had left the saddle invalid on 2026-11-20; fixed in `common.chamfer_outer`).
**Not the Flipper:** in `base_330_js`, the clapets v7 module A reaches z 372.5–379.5, over the 350 limit.

### Pictures (`sim/`)
- `sim/flipper_cycle.gif` (+ stills): full cycle and the way back; 3D, side view (red line = 350 mechanism limit),
  close view of the pinion on the rack. Magnet red = ON. `freecad.exe fc/flipper_gif.py` (~2 min).
- `sim/views/`: 7 views at the pick pose + `flipper_all_views.png`. `freecad.exe fc/flipper_views.py` (< 1 min).

### To do (Flipper)
1. **Seif:** confirm the 8 base-plate holes → add them to the plate.
2. Grail deck supports and the roof around it (the deck is a placeholder); cross-member anchor (centre column / rings).
3. Measure the magnet (height 22 + M4 stud assumed).
4. Bottom endstop / homing; magnet cable loop around the flip axis; sprung magnet mount (CDC D4).
5. Rack back-drive when the NEMA is off: accept, or a brake.
6. Shorter NEMA once Seif knows what we have (motor length + pinion `HUB_L`).

## Flipper-S: lead-screw lift (`fc/flipper_s_fc.py`, was B2; on hold, Flipper first)
The Flipper flip on the hardware of Baha's "essai vis ecrou corrigé" (`../Grail_v1/essai vise ecrou corrigé/`).
**Still on layout-v1** (right face x 150, roof 306): to move to base_330_js like the Flipper.
LZ 50, pivot 130 → 262 (flip) → 256 (place) → 250 (stowed), 138 mm of travel.
- **T8 screw + flange nut**, **2 × Ø8 rods + 4 LM8UU** (2 per rod, carriage 48 tall), **608** in a bottom and a top plate.
  Column in a line along x at **y −28**: rods x 77 / 125, screw x 97. That keeps it behind the arm.
- **Motor not under the screw** (the right wheel and drive motor are there): the NEMA17 **stands on the bottom plate**
  (the bay floor, z 78–88), shaft down. A **GT2 belt 1:1** (pulleys z 64–78, loop ~135) drives the screw, at x ≤ 105.
- Flip head as written before `common.flip_head` existed (own copy: to switch to `flip_head`).

Report `CAD_FC/FLIPPER_S_report.txt`: highest point 338; the Grail never enters the body; 78.5 mm out at flip 45°.

## Flipper vs Flipper-S
| | Flipper (rack) | Flipper-S (lead screw) |
|---|---|---|
| Lift drive | NEMA17 rides on the carriage, pinion on a fixed rack | NEMA17 fixed on the bay floor, GT2 belt to a T8 screw |
| Guide | Two Trees X carriage on a 2020 (📦) | 2 × Ø8 rods + 4 LM8UU (rods 📦, LM8UU 🇹🇳 or from the SCS8UU 📦) |
| Power off / e-stop | carriage drops (back-driven) | holds (T8×8 may creep; T8×2 holds but 4× slower) |
| Moving mass | ~0.7 kg (motor rides) | lighter |
| Tested | rack printed, fits the profile | — |
| State | on base_330_js, checked, print files | layout-v1 |

## Later: suction-cup version, also for the gate lintel (Seif, 2026-11-20)
Same mechanism with a **suction cup instead of the magnet**:
- **Gate lintel:** pick the **2nd stone of a stack from its top (z 220)**, flip it 180° and lift a little past 320.
  It lands upside down **on the two towers**, and the cup ends under it, in the ~100 mm gap between the towers. The
  actuator stays under the stone, so ≤ 350. The stone's long side runs along the flip axis.
- **Grail:** the same cup picks the Grail by its top (no steel plate needed).
Details and numbers once the electromagnet version works. Concept notes: `../concepts/gate-lintel.md`.

## History (2026-11-19 → 11-20, short)
- A (pivot), B (lift + flip), C (rolling) generated in parallel; B chosen and rebuilt from real parts as the Flipper.
  A / C / the B concept: `archive/` (A: 128 mm out while turning; C: the Grail dips below the roof top at the edge).
- On **layout-v1** three column fixations were built (`archive/layout_v1/FLIPPER_SLOT/BRIDGE/INWARD`, older code state);
  Seif chose BRIDGE, then moved the Flipper to **base_330_js** (saddle).
- **LZ 58 → 80:** the cup hit the column at the place pose (the Grail's spot is right above the column); the longer arm
  shortens the lift (each mm of LZ takes 2 mm of lift).
- **Grail deck 306 → 320** (Seif): 306 came from layout-v1's roof strip, carried over without asking.
- Seif's reviews: motor bracket wrapped round the X plate, then redrawn with no wall < 2.5; saddle edge ribs removed, heel
  gussets on its sides; blind socket under the column; the top cross-member moved beside the column after the motion
  check found the arm in its corner; the way back changed to "down, then turn back".

## Files
| Path | What |
|---|---|
| `fc/common.py` | Grail, magnet, MG996R, **`flip_head()`**, fasteners, `chamfer_outer`, base selection (`GRAIL_BASE`, default b330), deck height, cycle table |
| `fc/flipper_fc.py` | **Flipper** generator (numbers in `class G`, saddle in `class SB`); GUI run sets the colours |
| `fc/flipper_pinion_fc.py` | **pinion v2** → `print/FLIPPER_PINION.step/.stl` (run first: the Flipper reads it) |
| `fc/flipper_static_check.py`, `fc/flipper_motion_check.py`, `fc/check_common.py` | collision checks |
| `fc/flipper_gif.py`, `fc/flipper_views.py` | pictures (`sim/`) |
| `fc/flipper_s_fc.py` | **Flipper-S** generator (layout-v1) |
| `CAD_FC/FLIPPER_B330.FCStd` + `_report.txt` | **the Flipper** (colours, numbered groups, ghost at the place pose, base plate, deck, 350 sheet). `FLIPPER_CONTEXT=1` adds the whole base → `FLIPPER_B330_IN_BASE.FCStd` |
| `CAD_FC/FLIPPER_S.FCStd`, `FLIPPER_PINION.FCStd` | Flipper-S, pinion |
| `print/` | print files (7 parts) |
| `sim/` | GIF, stills, views |
| `parts/` | inputs: `cremaillere.STL` (Seif's rack), `el_pignon.STEP` (Baha's pinion) |
| `archive/` | A, C, B concept; `layout_v1/` fixation variants |
| Real bought parts | `../resources/two-trees-bluer-v2-parts/` (X carriage, profile, NEMA17: see its `SOURCE.md`) |

Run (from this folder; never edit the `.FCStd` by hand):
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_pinion_fc.py
set FLIPPER_PRINT=1& "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/flipper_fc.py        # GUI: colours, ~3 min, closes itself
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_static_check.py
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_motion_check.py                 # set FLIPPER_MOTION=back for the way back only
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/flipper_gif.py
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/flipper_views.py
```
