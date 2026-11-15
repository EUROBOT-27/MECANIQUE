# flip-bar: single-bar stone flip (Maatoug, 2026-11-14)

> **Status: concept CAD + range-of-motion study, proposal, nothing decided.** Derived from Ayoub's
> [`flip-6cups`](../flip-6cups/README.md) (same four-bar). Ayoub / Seif to review.
> Revision of 2026-11-14 (evening): smooth bar outline, cups in the clapets-v8 **TPU spring stations** with a
> Barbatronic-style **support ring** around each cup (replaces the cup blocks + seat pads).

Flips one quarry stack (3 stones) from lying to standing, **inside the castle only** (the stones reach 470 mm on
the way; game elements may pass 350 mm only in construction zones and the castle). Each stone has its own cup, so
the robot then drops **one tower at a time** by venting one cup.

![range of motion](../simulations/flip_bar/range_of_motion.png)

## What changed from flip-6cups, and why

| | flip-6cups | **flip-bar** | Why |
|---|---|---|---|
| Cup holder | Al plate 230 × 290, 6 cups (2 per stone, quarter points) | **one smooth Al bar** (5 mm, CNC / laser cut): a lobe around each cup station, an arm to the crank pin, filleted, lightening slot | the plate corner and one cup reached **387 mm** during the flip; actuators must stay ≤ 350 even in the castle (game rules, stone constraints, before E.1.c). Bar: **339.0 mm** |
| Grip | 2 bellows cups per stone | 1 DP-S30 per stone in the **clapets-v8 TPU spring station** (`B_STATION_TPU`, same part), under a printed **Ø62 support ring** (after Barbatronic's cup pot): the bellows pulls the stone onto the ring rim | the stone sits on a rigid ring: no sag, no sway; the TPU spring lets the cup tilt to seat on bent cardboard; one station design for the head and the flip |
| Drive | JGB37-520 direct on the crank | **17HS4401S** (our Ender steppers) + **2-stage printed spur gears 15T/45T × 2 = 9:1** | user choice: our stepper, gears (no belts, no worm); reversible and back-drivable |
| Frame | one 5 mm column, crank on the motor shaft | **column + rear plate** (5 mm Al) tied by 4 standoffs; crank on its own Ø8 shaft, one 608 in each plate | the gear mesh force must not sit on the motor's bearings; stiff against the stones' overhang |
| Joints | one 688ZZ per joint | **two 608ZZ per moving joint** (crank pin, rocker at O2 and P2); crank and rocker blended at the hubs, lightening slot | the stones' weight sits 106 mm in front of the links: 0.39 N·m of twist |
| Ends of travel | home endstop | home + upright endstops, **rubber hard stops 3° past each end** | unpowered, the bar falls back (first half) or forward (second half) onto a stop |
| Vacuum | 6 pumps + 6 valves | **3 + 3** | one per cup; frees 3 of the 6 pumps for the clapets head |
| Ejectors | 3 × MG90S fingers | none | release = vent valve of that cup |
| 6 stones (case B) | yes | **no** (the centre cups would land in the gap between 2 stacks) | strategy to confirm |

## Cup station (× 3, identical, drop-in)

![station](../simulations/flip_bar/flipbar_3d_station.png)

From the bar outwards (bar front face y 164 → stone face y 196), held by **3 × M3 tapped in the bar** (bolt circle
r 24 at 90 / 210 / 330°, turned 60° from v8 so no bolt sits next to the P2 pin):
1. **Spacer** (ABS, Ø62 × 10, bore Ø40): room behind the TPU hub for the cup's **M5 elbow fitting**; a slot towards
   the bar edge lets the Ø4 tube out. It also covers the end of the P2 pin (keeps it from sliding forward).
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
| Stones | top 470 mm mid-flip (castle only); 7.2 mm over the table during the flip; upright 8.8 mm above it. Moving parts ≥ 18.9 mm above the table |
| Collisions | **0** between moving parts and the frame over 85 poses, hard stop to hard stop; **0** between fixed parts |
| Masses (CAD) | bar assembly 323 g (bar 179, 3 stations × 38: spacer 13, TPU 7, ring 10, cup 8; pins 32), crank 76 g, rocker 93 g (with bearings) |
| Crank torque (3 stones) | lift peak +0.66 N·m (crank 25°), **brake** peak −0.82 N·m (upright); reverses at crank 64° |
| Motor torque (9:1, η 0.81) | flip in **1.0 s: peak 0.118 N·m → ×1.70 margin** (1.5 s: ×1.98; 0.6 s: ×1.01, too tight). Holding: 0.090 N·m (45 %) |
| Gear teeth (ABS, m1, 9 mm) | stage 2 pinion 19.0 MPa (×2.1), stage 1 6.3 MPa (×6.3) |
| Backlash at the crank | ~0.34° (0.10 mm per mesh): slow the move around crank 55–75° where the torque reverses |
| Resolution | 16 microsteps → 0.0125° of crank per microstep |
| Joints | pin forces ≤ 8 N; twist 0.39 N·m → 11 N per bearing on the crank shaft, 55 N per bearing in the hubs (608 static 1370 N); friction negligible |

Assumptions to check: 17HS4401S = 0.40 N·m holding at 1.7 A (**read our labels**), usable 0.20 N·m at ~1 A up to
300 rpm (raise the driver current for more margin); DP-S30 size; real stones.

## Parts

📦 in library · 🇹🇳 buy locally · ✈️ import · 🖨️ print (ABS, D-023; TPU 95A for the spring discs)

| Part | Qty | Source |
|---|---|---|
| Stepper 17HS4401S (Ender) | 1 | 📦 (read the label) |
| 608ZZ (8 × 22 × 7) | 10 (4 frame, 2 crank pin, 4 rocker) | 🇹🇳 |
| Ø8 rod: crank shaft 49, intermediate 35, rocker ground shaft 72, bar pins 31 + 22 | 5 pieces | 📦 smooth rods, cut |
| Gears m1: 15T × 2, 45T × 2, 9 mm wide | 4 | 🖨️ 100 % infill |
| Double bearing housings (rear plate, column) | 2 | 🖨️ |
| Column (x −137..52), rear plate, 5 mm aluminium | 2 | 🇹🇳 (cut + drill) |
| **Bar, 5 mm aluminium, smooth outline** (DXF from `CAD/parts/Cup_bar_alu_5mm.step`) | 1 | 🇹🇳 laser / waterjet / CNC (the curves can't be hand-cut well; a printed drilling template + jigsaw is the fallback) |
| Crank, rocker 6 mm aluminium (blended hubs, slot) | 2 | 🇹🇳 same cutter as the bar |
| Standoffs Ø10 × 35 + M5, angle brackets | 4 + 4 | 🇹🇳 |
| Ender endstops | 2 | 📦 (3 in hand) |
| Rubber bumpers Ø10 | 2 | 🇹🇳 |
| Station spacers, support rings | 3 + 3 | 🖨️ ABS |
| TPU spring discs (`B_STATION_TPU`, clapets-v8 STL) | 3 | 🖨️ TPU 95A |
| M3 × 20 (stations, tapped M3 in the bar) | 9 | 🇹🇳 |
| DP-S30 cups + M5 elbow fittings (Ø4 tube) | 3 + 3 | planned (same as the clapets head) |
| 12 V mini pumps + vent valves | 3 + 3 | 📦 pumps (arriving), 🇹🇳/✈️ valves |

## Run
```
cd mechanical/flip-bar/fc
"C:/Program Files/FreeCAD 1.1/bin/python.exe" flipbar_check.py    # range of motion, torque, gears -> motion_report.txt + plots/GIF (~10 s)
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" flipbar_fc.py   # CAD + collision/height sweep -> CAD/, collision_report.txt (~5 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe" flipbar_render.py  # 3D pictures (opens FreeCAD, closes itself, ~1 min)
```
All numbers live in `fc/flipbar_params.py`. The bar and link outlines are computed there too (smooth union of
circles and capsules, `bar_outline()` / `link_outline()`), so the 2D check and the CAD use the same shape; change
`LOBE_R`, `SPINE_R`, `ARM_R`, `BLEND` to reshape the bar, then rerun the three scripts (height + collisions).
Pictures and the GIF: `../simulations/flip_bar/`.
Frame = base_330 (X wheel axis, Y forward with the mechanism on the +Y edge, Z up, origin = robot centre on the table).

## Open points
1. **Read the stepper labels** (holding torque, current) and set the driver current; the 1 s flip margin depends on it.
2. **Print one 15T/45T pair first** and measure the backlash at 30.0 mm centres; the housings set the centre distance.
3. **Suction test on real stones:** one station (spacer + TPU disc + support ring + DP-S30) per stone, hold > 30 s,
   and during the flip; also with the top cup 25 mm off its stone's centre.
4. Switch levers are not modelled: set them so they trip at the end of the travel (bodies are 5 mm clear of the crank).
5. Hoses (Ø4): M5 elbow behind each TPU hub, out through the spacer slot, along the bar edge to the bottom, then a
   loop for the 90° turn; not modelled.
6. Where it goes on the robot: modelled on base_330 like flip-6cups. On layout-v1 it would be the back option instead
   of flip6 (not checked against layout-v1 yet, nor its perimeter at full deployment, FAQ Q10).
7. Strategy: no 6-stone carry (case B) with a centre-line bar.
