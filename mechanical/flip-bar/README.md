# flip-bar: single-bar stone flip (Maatoug, 2026-11-14)

> **Status: concept CAD + range-of-motion study, proposal, nothing decided.** Derived from Ayoub's
> [`flip-6cups`](../flip-6cups/README.md) (same four-bar). Ayoub / Seif to review.
> Revision of 2026-11-14 (evening): smooth bar outline, cups in the clapets-v8 **TPU spring stations** with a
> Barbatronic-style **support ring** around each cup (replaces the cup blocks + seat pads). Then: **one gear pair**
> (15T pinion → 100T sector, m 0.8, 6.67:1) instead of the 2-stage 9:1 train.
> Revision of 2026-11-17: checked against `../design-principles.md` (section below): fasteners drawn and swept,
> housings and gears fixed the v7 way, printed fits sized for ABS, zip-tie anchors (4 points were left open).
> Revision of 2026-11-18: those 4 points are designed and swept: flat laser-cut links with printed bolted hubs, a
> clamp hub on the crank, M8 bolts as axles, every small fixing, the hoses on the bar. Swapping the stepper for an
> MG995 / MG996R was checked and **not** done (section "Drive: why the stepper stays").

Flips one quarry stack (3 stones) from lying to standing, **inside the castle only** (the stones reach 470 mm on
the way; game elements may pass 350 mm only in construction zones and the castle). Each stone has its own cup, so
the robot then drops **one tower at a time** by venting one cup.

![range of motion](../simulations/flip_bar/range_of_motion.png)

## What changed from flip-6cups, and why

| | flip-6cups | **flip-bar** | Why |
|---|---|---|---|
| Cup holder | Al plate 230 × 290, 6 cups (2 per stone, quarter points) | **one smooth Al bar** (5 mm, CNC / laser cut): a lobe around each cup station, an arm to the crank pin, filleted, lightening slot | the plate corner and one cup reached **387 mm** during the flip; actuators must stay ≤ 350 even in the castle (game rules, stone constraints, before E.1.c). Bar: **339.0 mm** |
| Grip | 2 bellows cups per stone | 1 DP-S30 per stone in the **clapets-v8 TPU spring station** (`B_STATION_TPU`, same part), under a printed **Ø62 support ring** (after Barbatronic's cup pot): the bellows pulls the stone onto the ring rim | the stone sits on a rigid ring: no sag, no sway; the TPU spring lets the cup tilt to seat on bent cardboard; one station design for the head and the flip |
| Drive | JGB37-520 direct on the crank | **17HS4401S** (our Ender steppers) + **one printed spur pair: 15T pinion → 100T sector gear on the crank shaft, module 0.8 = 6.67:1** | user choice: our stepper, 2 gears only (no belts, no worm); reversible and back-drivable. A **sector** because the crank only swings 126° stop to stop and a full wheel that size would hit the base plate |
| Frame | one 5 mm column, crank on the motor shaft | **column + rear plate** (5 mm Al) tied by 4 standoffs; crank on its own Ø8 shaft, one 608 in each plate | the gear mesh force must not sit on the motor's bearings; stiff against the stones' overhang |
| Joints | one 688ZZ per joint | **two 608ZZ per moving joint** (crank pin, rocker at O2 and P2), in a printed hub bolted on a flat link; M8 bolts as pins | the stones' weight sits 106 mm in front of the links: 0.39 N·m of twist |
| Ends of travel | home endstop | home + upright endstops, **rubber hard stops 3° past each end** | unpowered, the bar falls back (first half) or forward (second half) onto a stop |
| Vacuum | 6 pumps + 6 valves | **3 + 3** | one per cup; frees 3 of the 6 pumps for the clapets head |
| Ejectors | 3 × MG90S fingers | none | release = vent valve of that cup |
| 6 stones (case B) | yes | **no** (the centre cups would land in the gap between 2 stacks) | strategy to confirm |

## Cup station (× 3, identical, drop-in)

![station](../simulations/flip_bar/flipbar_3d_station.png)

From the bar outwards (bar front face y 164 → stone face y 196), held by **3 × M3 tapped in the bar** (bolt circle
r 24 at 90 / 210 / 330°, turned 60° from v8 so no bolt sits next to the P2 pin):
1. **Spacer** (ABS, Ø62 × 10, bore Ø40): room behind the TPU hub for the cup's **M5 elbow fitting**; a slot towards
   the bar edge lets the Ø4 tube out. The middle spacer also has a notch, open at its rim, for the head of the P2 bolt.
2. **TPU spring disc** (TPU 95A): **the clapets-v8 `B_STATION_TPU` unchanged**: rim Ø50 clamped, 3 spiral arms, hub
   Ø16 with the cup's M5 thread + nut pocket; the hub can move 3 mm back into the spacer bore.
3. **Support ring** (ABS): a 3 mm flange clamps the TPU rim, then a Ø62 / Ø56 wall up to the stone face, with
   3 round-ended windows (see the cup, lighter). The bolt heads sit inside the wall (hex key from the front).
4. **DP-S30**: lip 3 mm proud of the ring rim when free; the vacuum pulls the stone onto the ring.

The bar has a Ø30 hole under each station (lighter; the spacer bears on r 15–31).

## Results (`motion_report.txt`, `collision_report.txt`)

| Check | Value |
|---|---|
| Four-bar | crank 91.0, rocker 149.2, coupler (bar) 104.2, ground 204.1. Non-Grashof: the crank swings 120° between two toggle positions |
| Range of motion | crank 0 → 120° = bar 0 → 90°. Toggles (linkage locks) 87° before the start and 18.2° past upright; hard stops at 3° past each end (84° / 15.2° from the toggles) |
| Transmission angle | min **49.2°** (≥ 40 good); 59.5° / 46.0° at the stops |
| **Actuators highest point** | **339.0 mm** (exact solids) at crank 49°, bar 33°: **11 mm margin**. It is the top support ring, so the **top cup sits at v 85**, 25 mm below its stone's centre (at the centre it would reach 353.7) |
| Stones | top 470 mm mid-flip (castle only); 7.2 mm over the table during the flip; upright 8.8 mm above it. Moving parts ≥ 17.9 mm above the table (bottom support ring, at the home stop) |
| Collisions | **0** between moving parts and the frame over 85 poses, hard stop to hard stop; **0** between fixed parts. Every screw, nut, sleeve, hub, anchor and the hoses on the bar are in the sweep (2026-11-18) |
| Masses (CAD) | bar assembly 358 g (bar 180, 3 stations × 38: spacer 13, TPU 7, ring 10, cup 8; M8 pins + nuts 44; bolts + anchors 20; hoses 4), crank 81 g, rocker 93 g (with bearings and hubs) |
| Crank torque (3 stones) | lift peak +0.69 N·m (crank 25°), **brake** peak −0.86 N·m (upright); reverses at crank 64° |
| Motor torque (6.67:1, η 0.90) | flip in **1.5 s: peak 0.130 N·m → ×1.54 margin**; 1.0 s: ×1.33 (tight); 0.6 s: ×0.92, too weak. Holding: 0.117 N·m (58 %). Less margin than the old 9:1 (×1.70 at 1.0 s): the price of 2 gears; raise the driver current if the 1 s flip is wanted |
| Gear pair (ABS, m 0.8, 10 mm wide) | pinion root 12.7 MPa (×3.1). Sector: 140° of teeth (39 teeth of a 100T wheel, 2 spare past each hard stop), tip r 40.8; lowest tooth tip **4.0 mm above the base plate** over the whole travel. Teeth never overlap (0.05 mm gap, stop to stop) |
| Backlash at the crank | ~0.14° (0.10 mm): slow the move around crank 55–75° where the torque reverses |
| Resolution | 16 microsteps → 0.0169° of crank per microstep |
| Joints | pin forces ≤ 8 N; twist 0.39 N·m → 11 N per bearing on the crank shaft, 57 N per bearing in the hubs (608 static 1370 N); friction negligible |

Assumptions to check: 17HS4401S = 0.40 N·m holding at 1.7 A (**read our labels**), usable 0.20 N·m at ~1 A up to
300 rpm (raise the driver current for more margin); DP-S30 size; real stones.

## Parts

📦 in library · 🇹🇳 buy locally · ✈️ import · 🖨️ print (ABS, D-023; TPU 95A for the spring discs)

| Part | Qty | Source |
|---|---|---|
| Stepper 17HS4401S (Ender) | 1 | 📦 (read the label) |
| 608ZZ (8 × 22 × 7) | 8 (2 crank shaft, 2 crank pin, 4 rocker) | 🇹🇳 |
| Ø8 rod: crank shaft, 59 mm | 1 piece | 📦 smooth rod, cut |
| M8 × 80 hex bolt, part thread (DIN 931) + M8 washer + M8 nyloc nut: rocker axle at O2 | 1 + 1 + 1 | 🇹🇳 |
| M8 × 30 hex bolt: bar pins P1, P2; M8 thin nut (P1), M8 nut (P2) | 2 + 1 + 1 | 🇹🇳 |
| Gears m 0.8, 10 mm wide: 15T pinion (Ø20 hub, set screw on the shaft's flat), 100T **sector** (split clamp on the crank shaft) | 2 | 🖨️ 100 % infill (0.4 nozzle OK; print the pair first) |
| Bearing housings (rear plate, column): 608 seat Ø22.2, 2 ears with nut pockets | 2 | 🖨️ ABS, seat axis vertical |
| **Link hub** (2 × 608 in a Ø22.2 seat, lip, tongue with 2 screws): crank P1, rocker O2 and P2, one part | 3 | 🖨️ ABS, seat axis vertical, lip on the bed |
| **Crank clamp hub** (split clamp on the Ø8 shaft + tongue bolted on the crank) | 1 | 🖨️ ABS 100 % |
| Sleeves Ø11.5 × Ø8.2: 10 and 8 long (crank shaft), 6 long × 2 (O2 bolt, P1 bolt); tube Ø14 × Ø8.4 × 35 (O2 bolt, between the plates) | 4 + 1 | 🖨️ ABS 100 % |
| Zip-tie anchors 18 × 8 × 6 (3 on the bar's +u tabs for the hoses, 2 on the rear plate back for the cables) | 5 | 🖨️ ABS |
| Column (x −137..52), rear plate, 5 mm aluminium | 2 | 🇹🇳 (cut + drill) |
| **Bar, 5 mm aluminium, smooth outline** (DXF from `CAD/parts/Cup_bar_alu_5mm.step`) | 1 | 🇹🇳 laser / waterjet / CNC (the curves can't be hand-cut well; a printed drilling template + jigsaw is the fallback) |
| Crank, rocker 6 mm aluminium: **flat plates, holes only** (Ø20 under each hub, M3 tapped for the hubs) | 2 | 🇹🇳 same cutter as the bar |
| Standoffs Ø10 × 35 (plain tube, Ø5.5 bore), angle brackets | 4 + 4 | 🇹🇳 |
| Ender endstops | 2 | 📦 (3 in hand) |
| Rubber sleeves Ø10 × Ø4 bore, 8 long (hard stops, on an M4 × 16) | 2 | 🇹🇳 (hose or grommet) |
| Station spacers (the middle one with the P2 notch), support rings | 3 + 3 | 🖨️ ABS |
| TPU spring discs (`B_STATION_TPU`, clapets-v8 STL) | 3 | 🖨️ TPU 95A |
| M3 × 20 socket head (stations, tapped M3 in the bar) | 9 | 🇹🇳 |
| M3 × 12 button head + M3 nut (housings, head on the plate's outer face) | 4 + 4 | 🇹🇳 |
| M3 × 12 socket head + M3 nut (sector clamp, crank clamp) | 2 + 2 | 🇹🇳 |
| M3 × 10 socket head (link hubs 6, crank clamp hub 2; tapped M3 in the links) | 8 | 🇹🇳 |
| M3 × 6 button head (endstops, tapped M3 in the column) | 4 | 🇹🇳 |
| M3 × 8 set screw + M3 nut (pinion) | 1 + 1 | 🇹🇳 |
| M3 × 8 button head (motor, from the rear plate's front face) | 4 | 🇹🇳 |
| M3 × 8 socket head (anchors, tapped M3 in the bar and the rear plate) | 5 | 🇹🇳 |
| M4 × 16 button head + M4 nut (brackets 8: head on the plate front / under the base; hard stops 2) | 10 + 10 | 🇹🇳 |
| M5 × 55 button head + M5 nut (through the standoffs, head on the column front) | 4 + 4 | 🇹🇳 |
| DP-S30 cups + M5 elbow fittings (Ø4 tube) | 3 + 3 | planned (same as the clapets head) |
| 12 V mini pumps + vent valves | 3 + 3 | 📦 pumps (arriving), 🇹🇳/✈️ valves |

## Checked against the design principles (2026-11-17, completed 2026-11-18)

`../design-principles.md` is the standard for every CAD (D-006). The first flip-bar CAD skipped most of its fastener
and printed-part rules. State now:

| Rule | First CAD (2026-11-14) | Now |
|---|---|---|
| Every screw and nut drawn, swept, counted | none drawn | 54 screws and bolts, 24 nuts, 5 anchors drawn and in the collision sweep (0 hits); list at the end of `collision_report.txt`. Not drawn: pump and valve clamps, cables, the free hose loop |
| Nuts go in pockets (6.0 × 6.9 × 2.8), mouth open to free air | no nuts at all; housings had no fixing | housings: pocket in each ear, open at the ear tip. Sector and crank clamps: pocket cut out to the hub's rim. Pinion: slot open on the hub's motor-side face. M4 and M8 nuts are in the open, wrench or socket on them |
| Screws pass the whole nut | - | housings M3 × 12 (5 + 2.2 + 2.4 = 9.6); clamps M3 × 12; brackets M4 × 16 (5 + 4 + 3.2 = 12.2); standoffs M5 × 55 (45 + 4.7); O2 M8 × 80 (65 + 1.6 washer + 8 nyloc = 74.6); P1 M8 × 30 (5 + 6 + 14 + 4 = 29) |
| Torque parts clamped like the v7 rod clamps | "clamped" in the text, nothing in the CAD | sector: split clamp, bore Ø8.2, M3 × 12 at r 9. **Crank: printed clamp hub (same clamp) bolted on the crank by 2 × M3 × 10.** Pinion: Ø20 hub, M3 set screw on the shaft's flat + captive nut |
| Parts that can be made | crank and rocker hubs 14 mm deep in one piece with a 6 mm plate | **links are flat plates with holes only**; the two 608 of each joint sit in one printed hub (3 identical) screwed on the link |
| Nothing slides along a shaft | no collar, clip or spacer anywhere | crank shaft: sector boss + 2 sleeves fill it between the two 608, the plates stop the outer races. O2: one M8 bolt clamps head, 608s, sleeve, column, tube, rear plate. P1: bolt + sleeve + thin nut clamp the inner races; lip and link close the hub. P2 floats on purpose (a third stop would fight the other two) |
| Sized for ABS (D-023): 608 seat Ø22.2 + 0.6 lead-in, holes + 0.1–0.2 | seats Ø22.0, bores Ø8.0 and Ø5.0 | all 5 seats Ø22.2 + lead-in at the open mouth; clamp bores and sleeves Ø8.2, pinion bore Ø5.2; M3 clearance Ø3.4, M4 Ø4.5 |
| 608 touched on the right race only | plate hole Ø12 = the inner race's outer Ø (rubs) | frame plates Ø15 and link holes Ø20 hold the outer race; sleeves Ø11.5 touch the inner race only |
| Printed zip-tie anchors, cables and hoses in the CAD | not routed | hoses drawn on the bar: out of each spacer slot, onto an anchor on a bar tab just under it, side by side down the +u flank, off the bar under the bottom anchor. 2 anchors on the rear plate back for the motor and switch cables (cables not drawn) |
| 1 mm chamfer on outside corners, rounded windows, 3 mm walls | ring windows already round-ended, ring wall 3 mm | hubs: 3.1 mm wall around the seat, tongue corners chamfered 1 mm; housings rounded; anchors chamfered |
| Heat-set inserts (D-025) | none used | none used: nuts, and M3 tapped in the 5 and 6 mm aluminium |
| Print orientation from the precise features | not stated | housings, link hubs, clamp hub, sleeves, spacers, rings, gears, anchors: all flat, seat / bore axis vertical, no support (link hub: lip on the bed, seat opens upwards) |
| Key and finger access to every screw | not checked | see below |

### How the 4 open points were closed (2026-11-18)

Checked first with the pivots' swept clearances: the rocker never comes within 90 mm of O1, the crank never within
85 mm of P2 or 113 mm of O2, and the bar never covers O2. So no Y layer had to move.

| Point | Design | Y (mm) |
|---|---|---|
| Crank on its shaft | **clamp hub** on the crank's front face: Ø26 boss, split clamp (M3 × 12 + nut) with the slit on the side away from P1, a tongue towards P1 with 2 × M3 × 10 (heads sunk 6 mm) into M3 tapped in the crank. The tongue is on the clamp's hinge side, so the clamp still closes | 139–149 |
| Link hubs | **one printed hub, 3 times**: Ø28.4 body, two 608 in a Ø22.2 seat that opens on the link, 2 mm lip at the far end, tongue 20 × 36 × 4 along the link with 2 × M3 × 10. Crank P1: on the crank's front face. Rocker O2 and P2: on its back face. The link's Ø20 hole closes the seat and lets a 13 mm socket in. The link outlines did not change, so the stops and switches stay where they were; the crank lost its slot (the screws took its place) | crank 139–155, rocker 134–150 |
| Shafts held along Y | crank shaft: see the table above. **O2 = M8 × 80 hex bolt** from the front, head inside the rocker's hole, nyloc behind the rear plate. **P1, P2 = M8 × 30 hex bolts**, head on the bar's front face (P2's under the middle spacer, in a notch). P1 clamped by a thin nut inside the crank's hole; P2 locked on the bar by a full nut, free to slide in the rocker's bearings | - |
| Small fixings | brackets: 1 × M4 × 16 + nut per leg (4 holes Ø4.5 to drill in base_330). Endstops: 2 × M3 × 6 button head, tapped in the column, on the side away from the crank. Hard stops: rubber sleeve on an M4 × 16 from the column's back, locked by a nut on the front. Hoses: 3 anchors on 3 small tabs added to the bar outline | - |

Access and assembly order (checked by hand from the layers, not by a script: `fastener_check_v7.py` only knows v7):
1. **Rear plate:** motor first (4 heads on the plate's front face, under the gear layer), then the pinion: nut in
   the hub slot, pinion on the shaft, set screw from the side.
2. **Column, on the bench:** hard stops (M4 from the back face, nut + rubber on the front), endstops, housing.
3. **Frame:** standoffs (M5 heads on the column front, nuts on the rear plate back), brackets (M4 heads on the
   plates' front faces and under the base, nuts on the brackets). While closing it, thread the crank shaft stack:
   rear 608, sector (boss towards that bearing), sleeve 10, column 608, sleeve 8 through the column.
4. **Links, on the bench:** press two 608 into each hub from its open side, screw the hub on its link (heads on the
   tongue). Crank: add the clamp hub.
5. **Bar, on the bench:** P2 bolt + full nut, tight on the bar, *before* the middle station (its spacer covers the
   head). P1 bolt through the bar, sleeve, the crank's hub; thin nut inside the crank's Ø20 hole with a 13 mm socket,
   the head held on the bar's front. Then the stations, the anchors, the hoses.
6. **Linkage on the frame:** crank over the shaft end, clamp screw from the side (10 mm of room between the crank
   and the bar). Rocker's P2 hub over the P2 bolt. O2 bolt from the front through the rocker's hole, sleeve, column,
   tube, rear plate; washer + nyloc at the back: **snug, not hard** (a printed sleeve and tube are in that stack).
7. Sector clamp: between the two plates from the +X edge. Station bolts: straight from the stone side.

**Still to prove on the bench (tests, not drawings):**
1. **Clamp grip:** the sector clamp and the crank clamp each pass up to ~1.2 N·m through one M3 on a smooth Ø8
   shaft (estimate ~2 N·m before slip). Paint-mark the shaft and both hubs, run 50 flips with stones, look for a
   shift. Fallback: drill the shaft and put an M3 cross screw through each hub.
2. **Endstop PCB:** the 2 screw positions are assumed (`SWITCH_SCREW_X`, `SWITCH_SCREW_Z`); measure a real Ender
   endstop and correct them.
3. **Hose loop:** from the bottom anchor to the valves the straight distance goes from 106 to 186 mm over the flip:
   cut 240 mm free and check it never reaches the crank (it hangs on the +X side, where the crank comes at upright).
4. The M8 × 30 bolts are fully threaded: the P1 and P2 bearings ride on the thread (9 N load, fine); if the play
   shows, use bolts with a plain shank or a Ø8 sleeve.
5. Pump and valve clamps are not drawn; the motor and switch cables are not drawn.

## Drive: why the stepper stays (MG995 / MG996R checked, 2026-11-18)

The crank needs **+0.69 N·m to lift, −0.86 N·m to brake** at upright, and 0.78 N·m at the peak of a 1.5 s flip.
Datasheet stall torque: MG996R 0.92 N·m at 4.8 V, 1.08 N·m at 6 V; MG995 0.83 / 0.98 N·m. Travel ~180°.

| | 17HS4401S + 6.67:1 (kept) | MG996R direct on the crank | MG996R + 1.4:1 gear |
|---|---|---|---|
| Travel | any | 126° of 180°: fits | 176° of 180°: the biggest ratio the servo's travel allows, nothing left to trim |
| Torque at the motor, 1.5 s flip | 0.130 N·m | 0.78 N·m | 0.62 N·m |
| Share of what it can give | 65 % of the usable torque (33 % of holding) | **72 % of stall at 6 V**, 85 % at 4.8 V | **57 % at 6 V**, 67 % at 4.8 V |
| Braking at upright | 58 % of usable | 80 % of stall | 51 % of stall |
| If overloaded | loses steps, re-home | stalls at ~2.5 A and burns | same |

A hobby servo should work at about a third of its stall torque; clones often give less than the datasheet. An
MG996R can't get there because its 180° of travel caps the gear ratio at 1.4:1. The MG995 is weaker still.

What a servo would bring: no driver, no homing, no endstops, 55 g instead of 280 g, one Ender stepper freed. That is
worth having, but with a stronger servo in the same 40 × 20 case: a **20–25 kg·cm, 270° servo (DS3218 / DS3225
class)** allows a 2:1 gear and works at ~20 % of stall. Likely an import (check the local shops first). The lab's
HS-755HB (13 kg·cm class, 1 seen) is only 20 % stronger than an MG996R: not enough. A later swap means a new rear
plate and gear pair, nothing else.

## Run
```
cd mechanical/flip-bar/fc
"C:/Program Files/FreeCAD 1.1/bin/python.exe" flipbar_check.py    # range of motion, torque, gears -> motion_report.txt + plots/GIF (~10 s)
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" flipbar_fc.py   # CAD + collision/height sweep -> CAD/, collision_report.txt (~12 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe" flipbar_render.py  # 3D pictures (opens FreeCAD, closes itself, ~1 min)
```
All numbers live in `fc/flipbar_params.py`. The bar and link outlines are computed there too (smooth union of
circles and capsules, `bar_outline()` / `link_outline()`), so the 2D check and the CAD use the same shape; change
`LOBE_R`, `SPINE_R`, `ARM_R`, `BLEND`, `ANCHOR_TAB_R` to reshape the bar, then rerun the three scripts (height + collisions).
Pictures and the GIF: `../simulations/flip_bar/`.
Angle brackets: the column's on its inner face, the rear plate's on its back face (the sector sweeps the space
between the plates). The low right standoff sits straight under the crank shaft, where the sector never goes.
Frame = base_330 (X wheel axis, Y forward with the mechanism on the +Y edge, Z up, origin = robot centre on the table).

## Open points
1. **Read the stepper labels** (holding torque, current) and set the driver current; the 1 s flip margin depends on it.
2. **Print the 15T + sector pair first** and check the mesh at 46.0 mm centres (the motor holes in the rear plate
   and the crank housing set it); m 0.8 teeth are small: ABS, 100 %, check the pinion's grip on the Ø5 motor shaft.
3. **Suction test on real stones:** one station (spacer + TPU disc + support ring + DP-S30) per stone, hold > 30 s,
   and during the flip; also with the top cup 25 mm off its stone's centre.
4. Switch levers are not modelled: set them so they trip at the end of the travel (bodies are 5 mm clear of the crank).
5. Hoses (Ø4): drawn on the bar (3 anchors); the 240 mm free loop to the valves is not modelled, try it for real.
6. Where it goes on the robot: modelled on base_330 like flip-6cups. On layout-v1 it would be the back option instead
   of flip6 (not checked against layout-v1 yet, nor its perimeter at full deployment, FAQ Q10).
7. Strategy: no 6-stone carry (case B) with a centre-line bar.
8. The 5 bench tests under "Still to prove on the bench" above (clamp grip first).
