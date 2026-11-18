# base_330_js — 336 × 260 base for the JSUMO JS7444 wheels + AMT102-V odometry (FreeCAD)

> **Status: proposal (Ayoub, 2026-11-18), not reviewed by Seif.** Derived from [`../base_330`](../base_330/README.md)
> (330 × 280 × 5), rebuilt for the **JSUMO JS7444** wheels (D-004). The odometry keeps the **existing wheel of the
> `sysRoueCodeusee` units** (not printed) and reads it with the encoder of the CDR-2027 odometry block,
> **`Poenc1_102-v-2530` = CUI AMT102-V** (`resources/CDR-2027/MCAD/electronical-parts/BlocOdometrie.FCStd`), on a
> sprung swing arm.
> **2026-11-18 rework (Ayoub):** motors **30 mm apart** (were 4), **5 mm** round the drive-wheel envelope (was 3 / 1),
> odometry rebuilt smaller with the **wheel on the outside** (at the edge of the base) and the **encoder on the inside**.
> That stack needs 3 mm more per side, so the plate is **336** wide (was 330).
> **2026-11-18 perimeter rework (Ayoub):** plate **336 × 260** → perimeter **1192 mm ≤ 1200** [GR F.3] (was 336 × 280 =
> 1232). Motors still 30 mm apart, wheels unchanged. **5 mm safety round the JSUMO envelope** now also for the AMT102
> (was 3) and for the inner edge of the wheel well (except the tongue under the hinge foot). The odometry width could
> not shrink with these parts (see section 3), so the base got **shorter** (L 280 → 260), not narrower.
> **The JSUMO wheel is not measured yet**: the plate is cut for an uncertainty envelope and the ride height is set by
> printed shims, so the plate does not have to be cut again when the wheel arrives.
> **2026-11-18 (Ayoub): the 2 casters are replaced by 4 × KSM15-FL ball transfer units, one per corner** (section 1b).

![Assembly](base_330_js_assembly.png)

| File | What |
|---|---|
| `base_330_js.py` | Generator: plate + printed odometry parts + ball-unit holders and shims. Parameters at the top. `freecadcmd base_330_js.py` |
| `base_330_js_assembly.py` | Assembly + checks → `base_330_js_report.txt`. `freecad.exe base_330_js_assembly.py` (GUI, colours, ~4 min, closes itself) or `freecadcmd` |
| `CAD/base_330_js.dxf` / `.step` / `.FCStd` | The plate: laser cut, 5 mm (same material as base_330) |
| `CAD/odo_bracket`, `odo_arm` `.step` / `.stl` | Printed odometry parts (**2 of each**, the same part works on both sides) |
| `CAD/ball_holder.step` / `.stl` | Printed holder for a KSM15-FL ball unit (**4**, one per corner) |
| `CAD/ball_shim.step` / `.stl` / `.dxf` | Shim ring between the ball unit and the holder roof (4), thickness set after measuring the wheel (section 1b) |
| `CAD/base_330_js_print.3mf` | **Everything to print, one plate** (made by `make_3mf.py`): 2 × bracket, 2 × swing beam, 4 × ball holder, 4 × ball shim, already in print orientation. The AMT102 is bought and the wheel already exists, so only the support is printed |
| `CAD/base_330_js_assembly.FCStd` / `.step` | Plate + drive placeholders + uncertainty envelope + both odometry modules + clapets v7 module A |
| `parts/AMT102-V_from_CDR.step` | The encoder model taken out of the CDR assembly (its own frame: shaft = Z) |
| `parts/dead_wheel_sysRoueCodeusee.step` | The existing odometry wheel (rim + O-ring), taken out of `sysRoueCodeusee.SLDPRT` (frame: axis X, hub face x = 0) |
| `base_330_js_report.txt` | Fit checks (see "Checked") |

Frame = base_330: X = wheel axis (336), Y = front/back (260), Z = up, origin at the plate centre. The generator works
in the plate frame (z = 0 at the plate bottom); the assembly puts the floor at z = 0 (nominal Ø74 wheel).

## 1. The JSUMO wheel and the uncertainty margins

What we know: JS7444 = **Ø74** (shop), one page says **77 × 44**, width 44 is only from the name, hub and bore not
known. So the design uses three values for everything:

| | nominal (ride height) | envelope (cut-outs) | why |
|---|---|---|---|
| Diameter | 74 | **72 … 80** | 77 on the other shop page, + 3 mm |
| Width | 44 | **48** | hub boss may stick out |
| Inner face (on the 6 mm D shaft) | x 81 | **79 … 83** | where the hub ends up on the shaft |

- **Motors 30 mm apart** (`MOTOR_GAP`, base_330: 4 mm): the two 37D back ends are at x ±15. Every drive part (hinge,
  motor, wheel) moved out by 13 mm; the hinge holes are now at x ±39.9 / ±63.9. For 40 or 50 mm, change `MOTOR_GAP`
  and regenerate: each +10 mm makes the plate 10 mm wider.
- **Wheel well** x 74…136, y ±45: the Ø80 × 52 envelope (x 79…131) clears it by **5 mm on every side**
  (`WHEEL_CLEAR`), except a **tongue x 74…78, y ±21** under the hinge foot (the hinge sits on the plate there). The tongue
  edge stays 0.3 mm past the hinge motor plate (x 77.7): **3.3 mm to the nominal wheel**, 1 mm to the worst case. That
  last gap is set by the hinge, not the plate: the wheel's own hinge is 1.3 mm from the worst-case envelope too. More room inside means pushing the
  wheel further out on the motor shaft (`WHEEL_IN_NOM`), which leaves less shaft in the hub.
- **Ride height:** no MDF lift any more. The hinge sits on the plate, so the plate top is `D/2 − 20.5` above the floor
  (16.5 for Ø74). A bigger or smaller wheel moves the plate. The **ball units** follow it through a printed shim,
  and the **odometry arm** follows it through its own travel. Nothing has to be cut again.
- **Still unknown, check when the wheels arrive:** the bore (Pololu 37D shaft = Ø6 D) and the hub length. The shaft
  goes 22 mm past the gearbox face (to x 96.5), so with the wheel's inner face at 81 the hub gets ~15 mm of shaft.

## 1b. Ball transfer units (4 × KSM15-FL, one per corner)

Replace the 2 casters (front/back on the centre line). Shop drawing: body **Ø24**, ball **Ø15.875** sticking out
**4 mm**, **21 mm** from the ball top to the body base, **M8 × 18** stud, 40 kg each, 85 g. ✈️ AliExpress (or 🇹🇳 if a
local shop has them).

- **Where:** (±130, ±105). Support rectangle 260 × 210 (the casters were a 220 mm line). 6.2 mm to the odometry
  bracket (rear), 5.2 mm to the corner holes, 8.8 mm to the back-wall profile holes, holder flange 3 mm inside the
  front/back edge and 16 mm inside the sides. 0 clashes with clapets module A.
- **Why through the plate:** the unit is 21 tall but the plate bottom is only 11.5 above the floor (Ø74 wheel), so it
  can't hang under the plate. It goes **ball down through a Ø25 hole** and hangs from a printed **`ball_holder`** on the
  plate top: Ø44 × 4 flange with **3 × M3 × 12** through the plate (washer + nut under it), Ø32 tube round the body
  (bore Ø24.6), 5 mm roof with a Ø8.5 hole. The stud goes up through the roof: **washer + M8 nut** on top.
- **Height = printed `ball_shim`** (Ø24 × Ø8.5 ring) between the body base and the roof. The roof sits for the smallest
  wheel (Ø72), 7.5 above the plate top. Ball 2 mm above the floor (the drive wheels carry the robot, as with the
  casters):

  | measured wheel Ø | 72 | 74 | 77 | 80 |
  |---|---|---|---|---|
  | shim (mm) | none | **1.0** (generated) | 2.5 | 4.0 |

  The stud leaves 4.9 mm for the shim (18 − roof 5 − washer 1.6 − nut 6.5), so every case fits. Measure the wheel,
  set `WHEEL_D_NOM`, re-run `base_330_js.py` + `make_3mf.py` (only the shim changes).
- 4 points + 2 drive wheels is over-constrained: with a 2 mm gap the robot rests on the wheels and at most 1–2 balls
  when it pitches, like the casters before. If a drive wheel loses grip on an uneven table,
  raise the balls with a **thinner shim** (a thicker shim pushes the ball down).

## 2. Odometry: existing wheel + AMT102-V on a sprung swing arm

One module per side, outside the drive wheel, **wheel on the axle line (y = 0) at the very edge of the base, track
329.4 mm** (O-ring contact planes; drive track ~210).

x stack, right side (left = mirror):

| drive envelope | gap | AMT102 body | swing beam (2 × 696ZZ) | shim | existing wheel | gap | plate edge |
|---|---|---|---|---|---|---|---|
| ≤ 131 | **5** | 136.0 … 145.2 | 145.2 … 156.2 | 1 | 157.2 … 167.2 (contact x 164.7) | 0.8 | 168 |

- **Wheel (not printed):** the existing `sysRoueCodeusee` wheel, as modelled in `sysRoueCodeusee.SLDPRT`: Ø58 rim +
  O-ring → **tyre Ø61**, 10 wide, O-ring 6…9 mm from the hub face, **Ø6 bore with an M3 grub screw** in the Ø12 hub
  boss. The hub boss faces the beam, so the grub screw stays reachable in the 1 mm + 5 mm gap. **Check the real
  wheel against the model** (Ø, bore, grub screw) before cutting the shaft.
- **Encoder:** CUI AMT102-V (capacitive, up to 2048 PPR → 8192 counts/rev → 0.023 mm/count on the Ø61 wheel),
  5-pin header (A, B, X, +5 V, GND), **Ø6 sleeve** (in the AMT102 kit). It sits on the **inner** face of the beam, body
  toward the robot centre, **5 mm** from the worst-case drive wheel. Screwed with **2 × M2 × 8 self-tapping** into Ø1.7
  pilot holes (its base holes, 19.05 apart). No heat-set inserts: next to the Ø15 bearing seat an insert would leave
  0.4 mm of wall, a pilot hole leaves 1.2 mm. Connector **up**, so the cable goes up and clears the floor. The shaft
  goes 8 mm past the mounting face (the cap inside is at ~9).
- **Shaft:** **Ø6 × 30 steel** (AMT end 8 mm into the encoder → outer face of the wheel). Held along its axis by an
  **e-clip DIN 6799-5** against the inner bearing (inside the Ø12 lip bore) on the encoder side and by the wheel's
  grub screw + a **6 × 10 × 1 shim** against the outer bearing on the wheel side.
- **Swing beam** (`odo_arm`): **one 11 mm part** (was two 6 mm side plates around the wheel): **2 × 696ZZ** (6 × 15 × 5)
  pressed side by side from the wheel side onto a 1 mm lip, a pivot hub with **2 × F623ZZ** (one from each face,
  flange out), and the spring seat on its top. The wheel is overhung on the outside: 2 bearings 10 mm apart carry it.
  **Why a swing arm and not rods + slide (base_330 / CDR):** the pivot axis is parallel to the drive axle, so the arm
  swings in the Y-Z plane and the **odometry track never changes** with the travel (a 6° swing moves the contact
  0.3 mm along Y only). Also: no Ø8 rods (we have ~6, the clapets need them), no sliding fit that can bind, one spring.
- **Bracket** (`odo_bracket`, the mount): two ears around the beam (x 138.2…144.2 and 157.2…163.2), a back wall and a
  bridge over the spring. Feet: an inner flange (x 132.2…138.2) and a foot between the ears behind the pivot hub, with
  **3 × M3 × 12 through the plate**, washer + nut under it (holes Ø3.4 at (±135.2, −54), (±135.2, −70), (±150.7, −71.3),
  mirrored to the front too, so the module can also go on the front end). Nothing sticks out past the outer ear, so the
  bracket stays inside the plate. Pivot = **M3 × 30 + nyloc** through ear – F623 – beam – F623 – ear.
- **Spring:** one **Ender bed-levelling spring** (📦, 4 in hand; Ø8 × 25) between the bridge and the top of the beam,
  20 mm installed (5 mm preload). Wheel load = spring force × 0.32 (spring 19 mm from the pivot, wheel 60 mm).
  Target ~3–5 N at the wheel (k ≈ 1.9–3.2 N/mm). If the bed spring is too stiff, use a softer one or cut it.
  **M3 × 40** guide screw through the bridge, the spring and the beam. The **nut + washer under the beam is the droop
  stop**, set 1.6 mm below the beam: the wheel hangs at most 5 mm below the floor line when the robot is lifted.

### Assembly order (one module)
1. Press the 2 F623 into the pivot hub (one per face, flanges out) and the 2 696 into the beam (from the wheel side,
   down onto the lip).
2. E-clip on the Ø6 shaft (groove 8 mm + 1 mm from the AMT end, so it sits in the lip bore against the inner race).
   Slide the shaft in from the encoder side through both 696. Shim on the wheel side, then the wheel, hub boss first;
   push it against the shim and tighten the grub screw on a flat filed on the shaft.
3. AMT102: fit the Ø6 sleeve, put the base on the shaft and screw it to the inner face of the beam (2 × M2 × 8
   self-tapping), then the code disc and the cap (CUI procedure, use the centring tool).
4. Bolt the bracket to the plate (3 × M3 × 12). Put the beam between the ears, then the M3 × 30 pivot + nyloc,
   snug and not clamped.
5. Spring on the beam, M3 × 40 from the top through the bridge, spring and beam, then washer + nut underneath, 1.6 mm
   below the beam (droop stop).

## 3. Plate (`base_330_js.dxf`)

| Feature | base_330 | base_330_js |
|---|---|---|
| Size | 330 × 280 × 5 | **336 × 260** × 5 (W computed from the odometry stack + 0.8 mm; L cut for the perimeter) |
| Motors | back ends 4 mm apart | **30 mm apart** (`MOTOR_GAP`), hinge holes at x ±39.9 / ±63.9, y ±15 |
| Wheel well | x 80.8…106.8, y ±50 (Ø90 wheel) | **x 74…136, y ±45** (JSUMO envelope + 5 mm), tongue x 74…78, y ±21 under the hinge foot |
| Encoder | 2 × Ø8 rods per side (x ±134.5) + notch | **notch x 136…168, y ±32.5** (AMT + existing wheel) + **3 × M3 per side** for the bracket (mirrored to the front) |
| Lift | 2 × 3 mm MDF per motor | **none** (hinge on the plate); plate top 16.5 above the floor with Ø74 |
| Strap slots across the motors | 2 × (x ±55.5, y ±27.5, 4 wide) | **removed**: the middle of the plate only has the 8 hinge holes (Ø3.5) |
| Corner holes | (±154, ±129) | **(±157, ±119)**, still 11 mm from the edges |
| Casters | 2 × Ø33 + 2 screws, y ±110 | **removed** → **4 × Ø25 ball-unit holes at (±130, ±105)** + 3 × Ø3.4 per holder (r 19 at 0/120/240°) |
| Back-wall profile holes | (±100, ±130) | **(±100, ±120)** (L/2 − 10: 20 × 20 profile flush with the edge) |
| Clapets v7 module A holes | `CLAP_DY` 23 | **`CLAP_DY` 35**: the socle front must clear the Ø80 envelope (y 40) by 3 mm → stack face 35 mm in front of the plate edge |
| Clapets v7 module A fixing | 4 × Ø4.8 (M4) | **4 × Ø3.4 for M3** (× 2 ends): M3 × 20 + washer under the head (on the socle, whose holes stay Ø4.4) + washer + nut under the plate |

**Perimeter (GR F.3, ≤ 1200 at start): plate 2 × (336 + 260) = 1192 mm, 8 mm margin.** Why the length and not the
width: across X the stack is drive envelope 131 + 5 safety + AMT 9.2 + beam 11 (2 × 696 + 1 mm lip) + shim 1 + wheel 10
= 167.2, so with the motors 30 mm apart and the wheels unchanged the plate can't be narrower than ~336. Keeping L = 280
would need W ≤ 320: no safety gap and no beam at all. More room later, if needed:
- **Thinner bearings in the beam**: 2 × MR126ZZ (6 × 12 × 4) → −2 mm per side, 2 × 676ZZ (6 × 10 × 3) → −4 mm
  (✈️ likely import; the 696 is 🇹🇳). Each mm per side = 4 mm of perimeter.
- **Corner chamfers**: each mm of a 45° chamfer on the 4 corners saves 2.34 mm (move the corner holes in first).
- What counts is the **robot** hull: clapets module A sticks out 45 mm in front of this plate (stack face y 175), so the
  final footprint is still set in `robot/` / `layout-v1/`.

## 3b. Printing (`CAD/base_330_js_print.3mf`)

One 256 × 256 plate (Bambu X1C, **ABS**, D-023), 106.3 cm³ in all, 256 × 142 mm used. Parts already oriented:
- `odo_bracket` lies on its back wall: bridge, ears, inner flange and middle foot stand up, no supports.
- `odo_arm` (swing beam) lies on its encoder face: the 696 seats and the F623 bores are vertical, so they print round;
  the 1 mm lip is on the bed.
- `ball_holder` flange down (the 5 mm roof bridges the Ø24.6 bore, no support needed in ABS); `ball_shim` flat.
  **No odometry wheel any more**: the existing one is reused.

Suggested: 0.2 mm layers, 4 walls, 40 % infill (beam and bracket carry the spring and the pivot), no supports, brim
for ABS. Press-fit holes (696 Ø15, F623 Ø10) and the M2 pilot holes (Ø1.7) are nominal: tune them from the
tolerance coupons first. **Ball shim = 1.0 mm for a Ø74 wheel**: measure the JSUMO wheel first, then re-run
`base_330_js.py` + `make_3mf.py` (section 1).

## 4. Bill of materials (both odometry modules + 4 ball units)

| Part | Qty | Source |
|---|---|---|
| Existing `sysRoueCodeusee` odometry wheel (Ø61 with its O-ring, Ø6 bore, M3 grub screw) | 2 | 📦 from the old encoder units |
| AMT102-V encoder (CDR part `Poenc1_102-v-2530`) with its Ø6 sleeve | 2 | ✈️ import (Mouser/Digikey) unless the CDR team has spares; check the club stock first |
| Printed `odo_bracket` / `odo_arm` (ABS, D-023) | 2 / 2 | 📦 Bambu X1C (~69 cm³ in all) |
| Ball transfer unit **KSM15-FL** (Ø24, ball Ø15.875, M8 × 18 stud) | 4 | ✈️ AliExpress / 🇹🇳 if found locally |
| Printed `ball_holder` / `ball_shim` | 4 / 4 | 📦 Bambu X1C |
| M8 nut + M8 washer (stud) | 4 + 4 | 🇹🇳 |
| M3 × 12 + nut + 2 washers (holders to plate) | 12 | 📦 |
| 696ZZ bearing 6 × 15 × 5 | 4 | 🇹🇳 local (3D-printer / bearing shops) |
| F623ZZ flanged bearing 3 × 10 × 4 | 4 | 📦 lab small bearings (read the codes) / 🇹🇳 |
| Ø6 steel shaft, 30 mm, with an e-clip groove + a flat for the grub screw | 2 | 🇹🇳 Ø6 silver steel or a drill blank, cut + deburr |
| E-clip DIN 6799-5 (shaft 6–8) + M6 shim 6 × 10 × 1 | 2 + 2 | 🇹🇳 |
| Compression spring Ø8 × 25 (Ender bed spring) | 2 | 📦 |
| M2 × 8 self-tapping (AMT to beam) | 4 | 📦 / 🇹🇳 |
| M3 × 30 + nyloc (pivot) | 2 | 📦 |
| M3 × 40 + nut + washer (spring guide / droop stop) | 2 | 📦 |
| M3 × 12 + nut + 2 washers (bracket to plate) | 6 | 📦 |

Electrical (for Hamza Bjaoui): the AMT102 needs **5 V**, and A/B/X are 5 V CMOS outputs, so use level shifting or
dividers on a 3.3 V MCU. 5-wire cable per encoder, routed up from the header.

## 5. Checked (`base_330_js_report.txt`)

- **0 interferences** between all parts in the nominal pose (plate, both odometry modules with the existing wheel,
  bearings, shaft, e-clip + shim, spring, screws, drive placeholders, 4 ball units + holders + shims, clapets v7 module A). The only
  allowed overlaps are the wheel and the AMT sleeve on the shaft, and the e-clip in its (unmodelled) groove.
- **Motor back ends 30.0 mm apart.**
- **Plate perimeter 1192 ≤ 1200** [GR F.3].
- **Wheel envelope Ø80 × 52** to the plate 5.0 everywhere except the hinge tongue (1.0, worst case), AMT **5.0**,
  bracket 7.2, odometry beam 14.2, clapets 12.5 mm (socle). Nominal wheel ↔ plate 3.0 mm, ↔ AMT 11.0 mm.
- **Floor contact** for Ø72 / 74 / 77 / 80: the odometry arm needs +0.95 / 0 / −1.43 / −2.87°, inside its −4.8 … +20° travel.
- **Arm at the droop stop:** no clash. Up to +20°: no clash.
- Everything stays inside the 336 outline (wheel at |x| ≤ 167.2, bracket ≤ 163.2). Lowest parts: AMT 14.9 mm,
  beam 19.2 mm above the floor.
- The clapets v7 NEMA17 STEP gives a **false 0 mm with `distToShape`** (already seen in base_330). The report uses the
  gap between exact bounding boxes for it (≥ 45 mm).

## 6. Not done / to check

- **Measure the JSUMO wheel** (Ø, width, bore, hub length) → set `WHEEL_D_NOM`, regenerate the ball shim.
- Drive motor / hinge / wheel / ball unit are **placeholders** (ball unit from the shop drawing: check one when it arrives). Motor drawn with the gearbox axis 7 mm above the output
  shaft (that is the only way the 37D fits with the hinge on the plate). Check the real hinge.
- Hinge bolts: the base_330 M3 × 20 went through the 6 mm lift. Without the lift, use M3 × 14–16.
- AMT102 shaft length: 8 mm past the mounting face, taken from the CDR model. Check against the CUI datasheet
  before cutting the shafts.
- **Measure one existing odometry wheel** (tyre Ø, width, bore, grub-screw size) against
  `parts/dead_wheel_sysRoueCodeusee.step` (from the SolidWorks part, not measured). If it differs, change `DW_*`
  in `base_330_js.py` and regenerate.
- Print a test beam and measure: the 696 and F623 press fits (tolerance coupons, D-023), the spring force at the
  wheel (target 3–5 N), and the wheel runout (the wheel is overhung on 2 bearings 10 mm apart).
- Clapets: front module checked. A module on the **rear** end would sit next to the odometry brackets
  (door units |x| ≤ 106, inner bracket flange from x 130). Check the door sweep before mounting one there.
- The full-robot model (`robot/fc/layout.py`) still uses its own odometry reserve. Update it if this base is adopted.
