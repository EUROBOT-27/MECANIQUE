# base_330_js — 330 × 280 base for the JSUMO JS7444 wheels + AMT102-V odometry (FreeCAD)

> **Status: proposal (Ayoub, 2026-11-18), not reviewed by Seif.** Same plate size as [`../base_330`](../base_330/README.md)
> (330 × 280 × 5), rebuilt for the **JSUMO JS7444** wheels (D-004). The `sysRoueCodeusee` encoder units are
> replaced by the encoder of the CDR-2027 odometry block, **`Poenc1_102-v-2530` = CUI AMT102-V**
> (`resources/CDR-2027/MCAD/electronical-parts/BlocOdometrie.FCStd`), on a new sprung swing arm.
> **The JSUMO wheel is not measured yet**: the plate is cut for an uncertainty envelope and the ride height is set by
> a printed spacer, so the plate does not have to be cut again when the wheel arrives.

![Assembly](base_330_js_assembly.png)

| File | What |
|---|---|
| `base_330_js.py` | Generator: plate + printed odometry parts + caster spacer. Parameters at the top. `freecadcmd base_330_js.py` |
| `base_330_js_assembly.py` | Assembly + checks → `base_330_js_report.txt`. `freecad.exe base_330_js_assembly.py` (GUI, colours, ~4 min, closes itself) or `freecadcmd` |
| `CAD/base_330_js.dxf` / `.step` / `.FCStd` | The plate: laser cut, 5 mm (same material as base_330) |
| `CAD/odo_bracket`, `odo_arm`, `odo_wheel` `.step` / `.stl` | Printed odometry parts (**2 of each**, the same part works on both sides) |
| `CAD/caster_spacer.step` / `.stl` / `.dxf` | Caster spacer (2 of them), thickness set after measuring the wheel (see below) |
| `CAD/base_330_js_print.3mf` | **Everything to print, one plate** (made by `make_3mf.py`): 2 × bracket, 2 × arm, 2 × odometry wheel, 2 × caster spacer, already in print orientation. The AMT102 is bought, so only its support is printed |
| `CAD/base_330_js_assembly.FCStd` / `.step` | Plate + drive placeholders + uncertainty envelope + both odometry modules + clapets v7 module A |
| `parts/AMT102-V_from_CDR.step` | The encoder model taken out of the CDR assembly (its own frame: shaft = Z) |
| `base_330_js_report.txt` | Fit checks (see "Checked") |

Frame = base_330: X = wheel axis (330), Y = front/back (280), Z = up, origin at the plate centre. The generator works
in the plate frame (z = 0 at the plate bottom); the assembly puts the floor at z = 0 (nominal Ø74 wheel).

## 1. The JSUMO wheel and the uncertainty margins

What we know: JS7444 = **Ø74** (shop), one page says **77 × 44**, width 44 is only from the name, hub and bore not
known. So the design uses three values for everything:

| | nominal (ride height) | envelope (cut-outs) | why |
|---|---|---|---|
| Diameter | 74 | **72 … 80** | 77 on the other shop page, + 3 mm |
| Width | 44 | **48** | hub boss may stick out |
| Inner face (on the 6 mm D shaft) | x 68 | **66 … 70** | where the hub ends up on the shaft |

- **Wheel well** x 65…121, y ±45: the Ø80 × 52 envelope (x 66…118) clears it by **1 mm inside** (the hinge motor plate is
  at 64.7, so the wheel can't go further in anyway), **3 mm outside**, **5 mm front/back**. The nominal wheel has 3 mm.
- **Ride height:** no MDF lift any more. The hinge sits on the plate, so the plate top is `D/2 − 20.5` above the floor
  (16.5 for Ø74). A bigger or smaller wheel moves the plate. The **casters** follow it through a printed spacer,
  and the **odometry arm** follows it through its own travel. Nothing has to be cut again.
- **Caster spacer** (under each caster flange, `caster_spacer.stl`), thickness = `2 + 16.5 − (D/2 − 20.5)`
  → caster 2 mm above the floor:

  | measured wheel Ø | 72 | 74 | 77 | 80 |
  |---|---|---|---|---|
  | spacer (mm) | 3.0 | **2.0** (generated) | 0.5 | none: caster already 3 mm up, accept it or add a 3 mm MDF lift under the hinges |

  Measure the wheel, set `WHEEL_D_NOM`, re-run `base_330_js.py` (only the spacer changes).
- **Still unknown, check when the wheels arrive:** the bore (Pololu 37D shaft = Ø6 D) and the hub length. The shaft
  goes 22 mm past the gearbox face (to x 83.5), so with the wheel's inner face at 68 the hub gets ~15 mm of shaft.

## 2. Odometry: AMT102-V on a sprung swing arm

![Odometry module](base_330_js_odometry.png)

One module per side, outside the drive wheel, **wheel on the axle line (y = 0), track 272 mm** (drive track ~180).

- **Encoder:** CUI AMT102-V (capacitive, up to 2048 PPR → 8192 counts/rev → 0.020 mm/count on the Ø53 wheel),
  5-pin header (A, B, X, +5 V, GND), Ø5 sleeve (the one fitted in the CDR model). It is screwed to the outer arm plate
  with **2 × M2 × 6 into M2 heat-set inserts** (its base holes, 19.05 mm apart). The connector points **up**, so the cable
  goes up and clears the floor. The shaft goes 8 mm past the mounting face (the cap inside is at ~9).
- **Wheel:** printed hub Ø50 × 8 with an O-ring groove (Ø46 bottom) + **NBR O-ring 46 × 3.5** → tyre Ø53. It is pressed
  on a **Ø5 × 29 steel shaft** (bore printed Ø4.9, add retaining compound). The two 1 mm bosses bear on the
  625 inner races, so they locate the shaft along its axis.
- **Arm** (`odo_arm`): two 6 mm side plates with a **625ZZ** in each (5 × 16 × 5, pressed from the wheel side, 1 mm lip
  outside), a pivot tube with **2 × F623ZZ** (one per end, flange out), and a crossbar that seats the spring.
  **Why a swing arm and not rods + slide (base_330 / CDR):** the pivot axis is parallel to the drive axle, so the arm
  swings in the Y-Z plane and the **odometry track never changes** with the travel (a 6° swing moves the contact
  0.3 mm along Y only). Also: no Ø8 rods (we have ~6, the clapets need them), no sliding fit that can bind, one spring.
- **Bracket** (`odo_bracket`, the mount): two ears around the arm, a back wall and a bridge over the spring.
  Two foot flanges with **4 × M3 × 12 through the plate**, washer + nut under it (holes Ø3.4 at x ±114 / ±158,
  y ±55 / ±69). The holes are mirrored to the front too, so the module can also go on the front end.
  Pivot = **M3 × 40 + nyloc** through ear – F623 – F623 – ear.
- **Spring:** one **Ender bed-levelling spring** (📦, 4 in hand; Ø8 × 25) between the bridge and the crossbar, 20 mm
  installed (5 mm preload). Wheel load = spring force × 0.32 (crossbar 19 mm from the pivot, wheel 60 mm).
  Target ~3–5 N at the wheel. If the bed spring is too stiff, use a softer one or cut it. **M3 × 35** guide screw
  through the bridge, the spring and the crossbar. The **nut + washer under the crossbar is the droop stop**: set it so
  the wheel hangs at most 5 mm below the floor line when the robot is lifted.
- **Travel (checked):** the floor sits between −3 mm (Ø80 wheel) and +1 mm (Ø72) from the nominal arm position, inside
  a range of −5 (droop stop) … +20 mm (no clash up to 20°). The spring length changes by less than 1 mm over the
  whole wheel range, so the odometry load hardly depends on the JSUMO size.

![Odometry side view](base_330_js_odometry_side.png)

### Assembly order (one module)
1. Melt the 2 M2 inserts into the outer arm plate, press the 2 F623 into the pivot tube (flanges out) and the 2 625 into
   the side plates (from the wheel side).
2. Fit the O-ring on the wheel. Slide the shaft through the inner 625, the wheel and the outer 625, with the shaft end
   8 mm past the outer face. Glue the wheel with the bosses touching both inner races.
3. AMT102: fit the Ø5 sleeve, put the base on the shaft and screw it down (M2 × 6), then the code disc and the cap
   (CUI procedure, use the centring tool).
4. Bolt the bracket to the plate (4 × M3 × 12). Put the arm between the ears, then the M3 × 40 pivot + nyloc,
   snug and not clamped.
5. Spring on the crossbar, M3 × 35 from the top through the bridge, spring, crossbar, then washer + nut underneath (droop stop).

## 3. Plate (`base_330_js.dxf`)

![Plate](base_330_js_drive.png)

| Feature | base_330 | base_330_js |
|---|---|---|
| Size | 330 × 280 × 5 | **same** |
| Wheel well | x 80.8…106.8, y ±50 (Ø90 wheel) | **x 65…121, y ±45** (JSUMO envelope) |
| Encoder | 2 × Ø8 rods per side (x ±134.5) + notch | **notch x 121…165, y ±30** (odometry wheel + AMT) + **4 × M3 per side** for the bracket (mirrored to the front) |
| Lift | 2 × 3 mm MDF per motor | **none** (hinge on the plate); plate top 16.5 above the floor with Ø74 |
| Strap slots across the motors | 2 × (x ±55.5, y ±27.5, 4 wide) | **removed**: the middle of the plate only has the 8 hinge holes (Ø3.5) |
| Hinge holes, corner holes, casters, back-wall profile holes | | **unchanged** |
| Clapets v7 module A holes | `CLAP_DY` 23 | **`CLAP_DY` 35**: the socle front must clear the Ø80 envelope (y 40) by 3 mm → stack face 35 mm in front of the plate edge |

Plate perimeter 1220 mm (> 1200): like base_330, this is a **test base**, not the final footprint.

## 3b. Printing (`CAD/base_330_js_print.3mf`)

One 256 × 256 plate (Bambu X1C, **ABS**, D-023), 108.8 cm³ in all, 256 × 148 mm used. Parts already oriented:
- `odo_bracket` lies on its back wall: bridge, ears and flanges stand up, no supports.
- `odo_arm` lies on its inner side plate: the 625 seats and the F623 bores are vertical, so they print round.
  The outer 625 seat has a 3.5 mm lip bridge on top.
- `odo_wheel` and `caster_spacer` lie flat.

Suggested: 0.2 mm layers, 4 walls, 40 % infill (arm and bracket carry the spring and the pivot), no supports, brim
for ABS. Press-fit holes (625 Ø16, F623 Ø10, wheel bore Ø4.9, M2 inserts Ø3.2) are nominal: tune them from the
tolerance coupons first. **Caster spacer = 2.0 mm for a Ø74 wheel**: measure the JSUMO wheel first, then re-run
`base_330_js.py` + `make_3mf.py` (section 1).

## 4. Bill of materials (both modules)

| Part | Qty | Source |
|---|---|---|
| AMT102-V encoder (CDR part `Poenc1_102-v-2530`) | 2 | ✈️ import (Mouser/Digikey) unless the CDR team has spares; check the club stock first |
| Printed `odo_bracket` / `odo_arm` / `odo_wheel` (ABS, D-023) | 2 / 2 / 2 | 📦 Bambu X1C (~105 cm³ in all) |
| Printed `caster_spacer` | 2 | 📦 |
| 625ZZ bearing 5 × 16 × 5 | 4 | 📦 Ender V-wheels / 🇹🇳 local (3D-printer shops) |
| F623ZZ flanged bearing 3 × 10 × 4 | 4 | 📦 lab small bearings (read the codes) / 🇹🇳 |
| Ø5 steel shaft, 29 mm | 2 | 🇹🇳 Ø5 silver steel or a drill blank, cut + deburr |
| NBR O-ring 46 × 3.5 (any 44–48 ID × 3–3.5 CS; groove is a parameter) | 2 | 🇹🇳 hydraulics shop |
| Compression spring Ø8 × 25 (Ender bed spring) | 2 | 📦 |
| M2 heat-set insert + M2 × 6 | 4 + 4 | 📦 |
| M3 × 40 + nyloc (pivot) | 2 | 📦 |
| M3 × 35 + nut + washer (spring guide / droop stop) | 2 | 📦 |
| M3 × 12 + nut + 2 washers (bracket to plate) | 8 | 📦 |

Electrical (for Hamza Bjaoui): the AMT102 needs **5 V**, and A/B/X are 5 V CMOS outputs, so use level shifting or
dividers on a 3.3 V MCU. 5-wire cable per encoder, routed up from the header.

## 5. Checked (`base_330_js_report.txt`)

- **0 interferences** between all parts in the nominal pose (plate, both odometry modules with bearings, shaft,
  O-ring, spring, screws, drive placeholders, casters + spacers, clapets v7 module A). The only allowed overlaps are the
  wheel on the shaft (press fit) and the AMT sleeve on the shaft.
- **Wheel envelope Ø80 × 52** to the plate 1.0 (inside, against the hinge side), bracket 6.0, odometry arm 7.0,
  AMT 29, clapets 5.9 mm (socle). Nominal wheel ↔ plate 3.0 mm.
- **Floor contact** for Ø72 / 74 / 77 / 80: the odometry arm needs +0.95 / 0 / −1.43 / −2.87°, inside its −4.8 … +20° travel.
- **Arm at the droop stop:** no clash. Up to +20°: no clash.
- Everything stays inside the 330 outline (AMT at |x| ≤ 156.2, bracket ≤ 162). Lowest parts: odometry hub flange
  1.2 mm, AMT 10.9 mm, arm 15.2 mm above the floor.
- The clapets v7 NEMA17 STEP gives a **false 0 mm with `distToShape`** (already seen in base_330). The report uses the
  gap between exact bounding boxes for it (≥ 45 mm).

## 6. Not done / to check

- **Measure the JSUMO wheel** (Ø, width, bore, hub length) → set `WHEEL_D_NOM`, regenerate the spacer.
- Drive motor / hinge / wheel / caster are **placeholders**. Motor drawn with the gearbox axis 7 mm above the output
  shaft (that is the only way the 37D fits with the hinge on the plate). Check the real hinge.
- Hinge bolts: the base_330 M3 × 20 went through the 6 mm lift. Without the lift, use M3 × 14–16.
- AMT102 shaft length: 8 mm past the mounting face, taken from the CDR model. Check against the CUI datasheet
  before cutting the shafts.
- Print a test arm and measure: the 625 and F623 press fits (tolerance coupons, D-023), the spring force at the
  wheel (target 3–5 N), and the wheel runout.
- Clapets: front module checked. A module on the **rear** end would sit next to the odometry brackets
  (door units |x| ≤ 106, inner bracket flange from x 110). Check the door sweep before mounting one there.
- The full-robot model (`robot/fc/layout.py`) still uses its own odometry reserve. Update it if this base is adopted.
