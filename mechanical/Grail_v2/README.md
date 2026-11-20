# Grail v2: top grip + 180° flip onto the roof (Flipper and Flipper-S)

> **Where we are (2026-11-20, Seif + Claude)**
> - **Now placed on Ayoub's `base_330_js`** (Seif: "take base 330 js as reference"): `CAD_FC/FLIPPER_B330.FCStd` =
>   **the Flipper alone** (colours, everything visible, numbered groups) + `FLIPPER_B330_report.txt` (fit checked against
>   the real base parts). With the base around it: `set FLIPPER_CONTEXT=1` → `FLIPPER_B330_IN_BASE.FCStd`.
>   The column stands on a printed **saddle** over the drive wheel + motor (section "On base_330_js").
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
  servo mount on the plate's front reaches the flip axis x 152.5. **LZ 80** (was 58): pivot 160 → 232 (flip) → 226 (place)
  → 220 (stowed), 78 mm of travel.
- **Motor:** standard 40 mm NEMA17 for now (Seif, 2026-11-20), face 5 mm past the eccentric wheel. Body at y −70…−33:
  **18 mm past the Grail bay** (y −52) toward the back module. A shorter NEMA is a quick fix (motor + pinion hub).

### On base_330_js: the SADDLE (Seif, 2026-11-20)
Placed on Ayoub's `../base_330_js` (336 × 260 plate, JSUMO wheels, odometry outside the wheel), read straight from its
assembly (`../base_330_js/CAD/base_330_js_assembly.FCStd`, same frame: X = wheel axis, Y = front (clapets) / back, z 0 =
table). Right face = plate edge **x 168**: flip axis x 170.5, Grail picked at x 178–248, placed at x 93–163, y ±35,
between the front clapets and the future **back module** (Seif: it goes in the back-right corner).

**`FLIPPER_SADDLE_SOCLE`** (printed ABS, one part, **167 g** at 60 % after 12 lightening pockets, was 198, `print/`): a deck over the drive wheel, the drive motor
and the odometry module, on **4 legs on the free plate zones of Seif's sketch**:
| | |
|---|---|
| Legs | beside the wheel well: x 80–128, y −60…−47 and 47…60 (odometry bracket from x 132, clapets door unit from y 69); beside the drive motor: x 25–74, y −42…−24 and x 25–66, y 24…40 (hinge \|y\| ≤ 20, clapets socle from y 43.5) |
| Deck | x 25–141, y ±60 (±55 where x < 70: clapets rails at y 58), underside z 67 (drive motor top 62.5) and z 70 over the odometry module (bracket 61.2, screws 64.2), **tunnel R45 around the worst-case wheel Ø80** (5 mm): crown 82, deck top 85 |
| Column | **blind socket** (Seif): 3.5 deep pocket 20.4 × 20.4 (profile end at z 84.5, 2.5 floor over the wheel tunnel's crown) + 3 mm collar to z 88.5 (the carriage passes 1 mm above at the pick); a **heel on its back face** (x 106–118, to z 112) with **2 × M5 into T-nuts** in the back slot's free bottom (z 96, 106); top: 2020 cross-member inward (z 260–280) + corner bracket in the back slot's top end |
| Ribs | back and front edges (7 tall, under the NEMA / outside the carriage) |
| Lightening | pockets **open at the bottom inside the 4 legs** (3 mm walls round the screw channels, 7 mm cap under the deck) + a grid **under the deck over the drive motor** (4 mm top skin, 3 mm ribs). The crown over the wheel, the pad, the heel and the ribs are untouched |
| Floor | **8 × M4 × 16** from the top through Ø9 channels, nut under the plate. **Plate holes not added yet** (Seif confirms first): Ø4.4 at (88, −53.5), (120, −53.5), (88, 53.5), (120, 53.5), (33, −33), (66, −33), (33, 32), (58, 32) |
| Clearances (real distances) | clapets rails 3.0, hinge 4.0, odometry bracket 4.2, drive motor 4.5, worst-case wheel 5.0 (nominal 7.0), X plate at the pick 4.5, carriage wheels 5.1 |

Same flip and cycle as before: highest point 335.7, the Grail never enters the body, nothing in its swept zone; start
16.8 mm past the face (perimeter 1192 + ~2), 84 mm out at flip 45° (+~50, budget 1400).
**Polish (2026-11-20):** magnet wire hole Ø3.8 through the cup's top (beside the M4 stud); zip-tie anchor (2 slots) on
the servo mount's base for the servo + magnet cables.
**Finish (2026-11-20, Seif: chamfers, ribs, form fits, screws in their holes):**
- **Chamfers 1 mm** on the printed parts' convex straight edges (design-principles edge rule), computed on the finished
  solids: saddle 137/152, motor bracket 32/44, servo mount 29/67 (edges the kernel refuses stay sharp; count in the report).
- **Ribs:** gusset behind the column heel; 2 stiffening flanges on the motor bracket (top and bottom, away from the
  wheel); 2 gussets where the servo plate's web meets the servo mount's base; the saddle's edge ribs.
- **Form fits (guidage par forme):** the saddle's 2 tongues drop into the plate's wheel well (centre it in y); a key on
  the heel enters the column's back slot below the rack; the servo mount's lip hooks the X plate's lower edge; the motor
  bracket's bridges have steps that butt on the X plate tabs' ends; the arm sits on the horn's disc pocket.
- **Every fastener modelled in its hole** (groups `8a/8b/8c_SCREWS_…`, moving with their part): saddle 8 × M4 × 16 +
  nuts under the plate; heel 2 × M5 × 12 + T-nuts; top bracket 2 × M5 × 10 + T-nuts; upper wheel screws M5 × 35 (eccentric
  M5 × 25 kept) + nylocs on the servo mount; 2 × M3 × 12 into the X plate; servo 2 × M3 × 10 + nuts; NEMA 4 × M3 × 8 button
  heads; tabs 4 × M3 × 20 (tip 3.5 mm off the column); horn 4 × M2 × 12; magnet M4 nut; pinion M3 insert + M3 × 6 set screw.
**Top cross-member anchor:** a centre column, or rings on the front / back modules' profiles carrying floors for the
electronics (Seif's idea, `../concepts/electronics-column.md`).

**Static collision check (2026-11-20): 0 clashes** (`fc/flipper_static_check.py` → `CAD_FC/FLIPPER_static_check.txt`).
Real overlap volumes between every pair of solids, pick pose (as built) and place pose (ghosts), with the real base plate,
the Grail deck (z 314–320, arm slot) and a 1 mm sheet at z 350–351 for the height limit, plus the base_330_js parts.
Fixed on the way: the top cross-member and its bracket were inside each other (cross-member now lies **on** the column's
top, M5 × 30 into the column's tapped end + inside corner bracket; profile 168.5), T-nuts resized to the real slot
(8 wide, 2.5 deep), heel M5 holes through the key, the saddle tongues 0.2 into the plate (now 0.2 off the wheel well's
edge, joined to the legs above the plate), the magnet nut turned 30°. Overlaps listed as expected: threads, pressed parts,
the gear mesh (tooth phase not set in a static model), holes still to drill (base plate × 8, X plate tabs × 2).
**Not the Flipper:** in `base_330_js`, the clapets v7 module A reaches z 372.5–379.5 (3 parts), over the 350 limit.

**Grail deck at 320 (Seif, 2026-11-20):** the Grail lands on a **landing deck at z 320** (L4 needs > 300); the rest of
the robot's top can be at 350 (different top heights). Earlier numbers here used 306 (layout-v1's roof strip, carried over
without asking). The Flipper's highest point is ~ deck + 24 (the arm swings above the place height), so the deck can't
go above ~324. With 320 and LZ 80: travel 80 + 12 = **92** (pivot 160 → 246 flip → 240 place → 234 stowed), **2020 profile
168.5** (z 84.5–253, in the saddle's socket), **rack 110** (z 119–229, `print/FLIPPER_RACK_110`), top cross-member **on** the column's top, z 253–273 (21 mm under the arm's lowest edge),
**highest point 344** (limit 350), roof slot x 108–169, y ±20. Env `GRAIL_ROOF` changes the deck height.

**Fixes after Seif's review (2026-11-20):**
- **The arm's cup hit the column at the place / stowed pose.** The Grail's roof spot is right above the column, and the
  magnet + cup hang 26 mm under the roof top (z 280 at the place, 274 after the 6 mm release); the column top was 280.
  **LZ 58 → 80**: the pivot sits higher above the Grail at the pick and lower under the roof at the place, the travel
  shrinks 122 → 78 and the **column top drops to 237** (arm's lowest edge above it 280+). LZ 70 was not enough (0.7 mm).
  Cost: 100 mm out while flipping (perimeter ~1261), flip torque 2.6 kg·cm (3.6×); highest point 330.
- Saddle: **edge ribs removed**; the gusset behind the heel (it blocked the heel's screws) → **2 gussets on the heel's sides**.
- **Motor bracket wraps around the X plate** (its shape follows the plate, which it hit at a small bent tab); its bridges
  moved off the NEMA's screw heads (one was buried under a bridge, behind a tab), tab screws at zc+29 / zc−25, flanges past
  the heads. Real check: 0 overlap with the plate, wheel, NEMA and every screw.
- **Motor bracket redrawn explicitly (no wall under 2.5 mm)**, Seif: thin faces / edges unprintable. The automatic "wrap" cut
  against the X plate left slivers (~0.6 mm next to the small bent tab), and the upper bridge was joined by only 2.6 mm.
  Now: plate zc ±34 (backs both bridges fully), flanges 3 × 6.5 on its top / bottom edges, upper bridge butts on the
  plate's small bent tab, lower bridge wraps the tab's end with a 2.7 step, **one M3 × 20 per bridge** (centred:
  counterbore walls ≥ 3; two did not fit). 0 overlap with the plate (0.03 gap at the bolted faces), wheel 0.5, NEMA + screws 0.
- **Why the travel is 78 now:** lift travel = roof 306 − Grail 80 − 2 × LZ (+ 6 over + 6 release): the 180° turn lifts the
  Grail by twice the arm's vertical reach, the lift does the rest. LZ 80 → 66 + 12. Getting LZ 58 (122) back needs the
  column out of the area under the Grail's roof spot (e.g. beside the flip plane in y).
- The report now checks the arm (cup included) against the column, its fixation and the carriage at the place and stowed
  poses with real distances.

**For the back module:** the Flipper's NEMA rides at x 89–131, y −70…−11, z 110–272 (column x 118–138, y −6…14) and its
roof spot is x 93–163, y ±35.

Run in the **GUI** (colours, ~3 min, closes itself): `"C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/flipper_fc.py`
(`set FLIPPER_PRINT=1` first to rewrite the print files). `freecadcmd` gives the same file without colours.

### Column fixation on layout-v1: BRIDGE (Seif, 2026-11-20; superseded by the SADDLE on base_330_js)
The 2020's bottom end sits right above the right wheel (x 106–150, top z 74). Three variants were built
(`FLIPPER_FIX=slot|bridge|inward` → `CAD_FC/FLIPPER_<VARIANT>.FCStd` + report); Seif chose **BRIDGE** ("it could help a
lot"). SLOT (corner brackets in the back slot onto a cross-member above the drive motor) and INWARD (column over the drive
motor, motor leaving the bay inward) stay as records.

**`FLIPPER_BRIDGE_SOCLE`** (printed ABS, one part, 89 g at 60 %, `print/`), drawn like the clapets socle but stiffer:
| | |
|---|---|
| Shape | block x 80–148, y −52…38, z 26 (floor plate top) … 83, with a **tunnel R43 around the wheel** (wheel R37: 6 mm all round), from x 101 (5 mm inside the wheel's inner face) to past the right face |
| Over the wheel | deck underside z 80 (wheel top 74), deck top 83; **pad** to z 86 under the column only |
| Back | full wall, 9 thick, y −52…−43 (the back module's butterfly plate is at y −53) |
| Front | the support is the **inner block above the drive motor** (x 80–101): the front module's door unit starts at y 40 (z ≥ 53), so no leg beside the wheel there |
| Drive motor | cut-out x < 104, \|y\| < 22, z < 60: 3.5 mm clear |
| Ribs on the deck | along y beside the column (4 tall), along the back wall's top (12), front edge (4), front corner (12): heights set by what the carriage brings down at the pick (steel plate 87.5, wheels 88, motor bracket 91, servo mount 92 / 97) |
| Column | M5 × 12 button head from under the deck into its end (head counterbored) + a 2020 corner bracket in the back slot's free bottom (z 86–106), M5 down through the deck into a nut in a side pocket |
| Floor | 5 × M4 through the full height (57) into the floor plate, heads counterbored flush with the deck, at (90, −48), (118, −48), (144, −48), (88, 30), (86, 0) |
| Clearances (real distances, pick pose) | wheel 5–6, drive motor 3.5, X plate 3.8, wheels 3.1, motor bracket 4.0, servo mount 3.2 |
| Top of the column | 2020 cross-member along x to the core (x 40–100, z 260–280) + corner bracket in the back slot's top end; 5.4 mm under the arm's path |

Knock-on of BRIDGE: the column stands at z 86–280; the carriage's lowest plate centre is z 125 (wheels 2 mm above the
column's end, steel plate 4.5 mm above the deck), pivot 13 above it; the pinion sits 4 mm above the plate centre (its top
clears the top cross-member); the rack is at z 117–257. Cycle checks unchanged: highest point 335.7, the Grail never enters
the body, nothing in its swept zone.

### Printed parts so far (`print/`, robot frame at the pick pose)
| Part | What | Fixing |
|---|---|---|
| `FLIPPER_ARM` (12 g) | hub Ø24 + bar 14 × 10 + magnet cup (seat Ø30.3, 18 deep, magnet face 4 mm proud), one solid | round horn's disc in a Ø21.4 pocket + Ø9.8 boss recess, **4 × M2 × 12** from +y into the horn holes (Ø2.5, as the tested T9 pinion); Ø5 steel pin pressed 6 deep from +y; magnet M4 stud + nut in a pocket |
| `FLIPPER_SERVO_MOUNT` (30 g) | base 8 thick on the X plate's front + servo plate under the ears (body cut-out) + 625 cheek joined under the pivot, one solid | **2 × M5×35** replacing the upper wheel screws (nylocs move to the base's front), **2 × M3** into the plate's 2 tapped holes (Ø2.5, 20 apart), recess for the eccentric's nyloc; servo: **2 × M3 × 12 + nuts in pockets**; **625 seat Ø16.2 open on +y**, lip on the arm side |
| `FLIPPER_MOTOR_BRACKET` (13 g) | plate 4.5 thick between the motor face and the eccentric wheel (0.5 mm off it), NEMA17 4 × M3 + Ø23 pilot, 2 bridges to the X plate's back tabs (above / below the wheel) | 4 × M3×25 into the tabs: **drill Ø2.5 + tap M3** (the tabs have no holes) |
| `FLIPPER_RACK_140` | Seif's rack cut to the pinion's travel (z 117–257) | slid into the back slot from the profile's end, V back on the cavity's inner faces |
| `FLIPPER_BRIDGE_SOCLE` (89 g) | the socle over the wheel (above) | 5 × M4 to the floor plate; column: M5 into its end + corner bracket |
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
| `FLIPPER_BRIDGE_SOCLE` | the floor face (z 26) down | tunnel = an arch over the bed (bridges up to 86 wide: support inside the tunnel); screw holes vertical; ribs on top |
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
set FLIPPER_FIX=bridge& "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_fc.py   # ~1 min; bridge (chosen) | slot | inward
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
7. **Next (Seif, 2026-11-20): Seif validates the polished model → static collision check → motion check → GIF render
   (with colours).**
8. STEP / STL / DXF print files + a short assembly sheet.
