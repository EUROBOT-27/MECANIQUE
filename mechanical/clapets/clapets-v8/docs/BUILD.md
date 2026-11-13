# Build sheet: clapets v5 (module A lift + doors, module B suction head)

Everything needed to print, cut, buy and assemble the module. Numbers come from `fc/v5_fc.py` (`class G`); if you
change the script, regenerate (see the [README](../README.md)) and update this sheet.

Two separate modules with a clean interface. **Module A** is designed around **space reserved for module B**, so the
suction head can be added, removed or redesigned without touching the doors or the lift.

- **Module A, clapets:** the Two Trees printer's Y axis on end lifts a carriage (butterfly plate) carrying two short
  doors that clamp a quarry stack and carry it (lift 15 mm).
- **Module B, suction head:** bolts on the plate front. One cup per box (3 cups) on TPU spring stations; in the castle it
  holds the stack, the doors open, the lift raises 75 mm and the head **turns the whole stack 90°** to stand the boxes
  as towers.

Open **`CAD_FC/MODULE_CLAPETS_V5.FCStd`** in FreeCAD: tree folders A (lift + doors), B (head), R (reserved space,
hidden; show it with Space), S (stack). STEP: `CAD_FC/STEP/` (every part + `MODULE_A_CLAPETS.step`, `MODULE_B_TETE.step`,
`MODULE_CLAPETS_V5.step`), printable STL: `CAD_FC/STL/`, laser DXF: `CAD_FC/DXF/`.

![](../CAD_FC/images/v5_iso_parts.png)

## The interface: space reserved for module B (carriage frame, mm)
| Volume | Where | Who must keep it free |
|---|---|---|
| Fixed zone | x ±62, y 50.5 (plate front) → 108, z 100–200 | module A, always |
| Tube passage | x ±62, y 50.5 → 108, z 200–230 (slack loop for the 90° turn + lift) | module A, always |
| Rest envelope | x ±30, y 108 → 140, z 57–273 (cups vertical) | module A, always (folded door tips stop at x 30) |
| Turning disc | Ø280 (R 140) around the axis x 0, **z 165**, y 108 → 140 | module A, whenever the head turns (doors open) |

Module B needs **R 108** to turn: 32 mm of margin. Mounting: the 4 wheel bolts of the butterfly plate (longer M5) through
the head bracket. Module A's 2 M4 button heads (nut support) sit in pockets behind the bracket.

## Module A: lift + doors
- **Lift:** rails, plate, wheels, NEMA17, coupler, T8 lead-8 screw (cut to 292 mm), 608 at the top. **25 mm further
  back than v4**, to give module B depth. Travel 0–15 mm (carry), 0–75 mm (turn).
- **Butterfly plate = the real part.** `REF_PLAQUE_PAPILLON` is now the Two Trees heatbed base read from the printer's
  .3dm (`fc/plaque_papillon_reelle.json`): 190 × 190 × **3.0** mm aluminium, 4× M4 corner holes (±85, ±85), 4 wheel
  holes 120 × 75 (2× Ø5.3, 2× Ø7.5 for the eccentric spacers), **2 centre holes Ø4.3 (M4, ±10)** and a **3rd hole Ø4.2
  at x 25.8**. Mounted with that 3rd hole on +x (away from the head servo); the eccentric wheels are then on +x.
- **Nut support (`A_SUPPORT_ECROU`), 3 points on the plate:** 2× M4 × 8 button head (the printer's own screws) through
  the centre holes into **M4 heat-set inserts** in an 8 mm wall, + a **printed Ø3.9 pin in the 3rd hole** (locates it and
  stops rotation). The **T8 nut flange is under the shelf** and its body goes up through it: lifting pushes the shelf on
  the brass flange directly; the 4× M3 (into M3 inserts, from below) only hold it. The flange holes are Ø3.5 for M3, so
  the nut can find the screw's axis before you tighten them. Print with the shelf on the bed.
- **Door units ×2: body `A_AILE_D/G` + top cap `A_CAPOT_AILE_D/G`.** Plain Ø8 rod turning in 2× 608ZZ, **at y 82 so
  the whole unit stays behind the head's turning disc**.
  - Body, printed upright with **no support**: 9 mm flat bottom plate (bottom 608 seat, servo bay), an L spine (back
    wall bolted to the plate's corners with 2× M4 + inner side wall), and a **rear web with a 45° underside** that closes
    the frame into a box behind the rod. The arms only ever swing in front of it, and the web stays above the 28T gear.
    45° fillets at the joints, chamfered edges.
  - Cap, printed upside down (flat 9 mm plate): top 608 seat, 3× M3 into inserts in the body, back edge against the
    back wall. **With the cap off, the rod, both arms and the 28T drop in from the top.**
  On the rod: 2 arms and a 28T gear, all with printed split clamps (no flat needed). MG996R standing on the bottom plate,
  20T pinion, **×1.4**; servo posts slotted ±2 mm to set the mesh.
- **Doors:** 3 mm MDF, 3 pads (one per box) **37 mm long**, grip the front of the box ends (y 145–182). Folded **+90°**
  (start, inside the 300 × 300 base, tips stop at x 30 in front of the head's rest envelope: that is what limits the
  door length) · clamp **+3°** · open **−38°** (all of the door behind the box face, so the turning stack clears it).
  Servo travel (90 + 38) × 1.4 = 179° of its 180°.

## Module B: suction head
- **Bracket** (`B_SUPPORT_TETE`): on the plate front with the 4 wheel bolts; a Ø34 bearing tube with **2× 608 25 mm
  apart** (stiff against the stack's weight); a window for the servo body; posts for the servo flange.
- **Drive:** MG996R inside the fixed zone, axis along y, 25° down-left of the head axis; **20T → 30T gear pair**
  (`B_PIGNON_TETE_20T` on the horn, `B_MOYEU_TETE_30T` = gear + flange, split clamp on the Ø8 shaft). ×1.5: head 90° =
  servo 135°. No belt.
- **Middle cup on the axis.** The head axis is at **z 165 = the middle box's centre** and the cups are at
  **z 85 / 165 / 245** (one per box). The hub part (`B_MOYEU_TETE_30T`) is, from the back: a split-clamp hub on the shaft,
  the 30T gear, and a **Ø56 flange that is the mount of the middle cup station**: the station's 3 M3 go through its
  clamp ring, the TPU rim and the carrier **into nuts in the flange**, so they also hold the carrier on the hub. A Ø20
  recess in the flange front leaves the middle TPU hub room to move back. The gear and the shaft clamp are behind it, so
  the drive is unchanged.
- **Carrier** (`B_PLATEAU_TETE`, 6 mm MDF, laser): the 3 station holes, and a **tube notch** from each station hole to the
  +x edge inside the carrier's thickness: each cup's tube leaves sideways, then goes back into the tube passage.
- **Cup station ×3 (drop-in, 3 screws each):** `B_STATION_TPU` (TPU 95A: clamped rim, 3 spiral springs, hub with an M5
  stem + nut pocket) + `B_BAGUE_STATION` (PETG clamp ring) + DP-S30 bellows cup. The rings are also the backstop that
  keeps the boxes from tipping while the doors only grip their front.

## How each servo is held
- **Door servos (×2), `REF_MG996R_D/G`.** Each stands upright on the bottom plate of its door unit.
  1. **Flange screws:** M3 × 12 go down through the servo's flange ears into **2 printed posts** (nuts slid into side
     pockets). The outer post takes 2 screws, the inner post 1 (the plate's corner lobe is where the 4th would go).
     The holes are **slotted ±2 mm** along the gear line: slide the servo to set the pinion/gear mesh, then tighten.
  2. **Strap (`A_BRIDE_SERVO_D/G`):** both posts continue above the flange up to the top of the servo body; a printed
     strap lies across the body top and screws onto them (2× M3, nuts in the posts), with a ring around the output
     shaft. The servo is clamped between the strap and its flange screws: it cannot tilt or lift.
- **Head servo, `REF_MG996R_TETE`.** Lies with its output along y, inside the head bracket. Its body passes through a
  window in the bracket plate; its two flange ears are screwed (4× M3, nuts in side pockets) onto **2 posts** that come
  forward from the bracket. Slotted ±1.5 mm sideways to set the 20T/30T mesh.

## Gear and arms on the plain Ø8 rods (split clamps): is it enough?
- Needed: gripping a stack takes about **0.3–0.5 N·m** on the rod (a few N at the pads, ~85 mm from the rod).
- Worst case: the MG996R at stall (~1.1 N·m at 6 V) × 1.4 = **~1.5 N·m** on the rod.
- Holds: a printed split clamp on a steel rod grips about μ·2F·r ≈ 0.25 × 2 × 500 N × 4 mm ≈ **1 N·m per M3**. The 28T has
  2 screws (~2 N·m) and each arm has 1, but the 2 arms share the load (~2 N·m).
- Verdict: **enough for normal use, marginal at full stall**, and PETG creeps, so the preload drops with time. Retighten
  after the first runs, and never command the servo far past contact.
- If it slips: the upgrade is a **steel Ø8 shaft collar** (set-screw "bague d'arrêt", sold for 3D printers) under the 28T,
  bolted to it (2× M3), with a **0.5 mm spot flat** ground with a Dremel under its set screw. Steel on steel does not
  creep, and the flat makes it positive.

## Servo cables
**The servo in the CAD is now the real MG996R model** (`resources/mg996r/mg996R_v2.step`). Its cable grommet comes out of the **short end face on the output-shaft side, centred across the width,
3.7–8.3 mm above the bottom, sticking out 5.8 mm**, just under the ear. Each servo carries a cable stub routed as below, and
the collision check proves the grommet and the stub pass. Other sizes taken from that model: body 40.4 × 20.4 × 38,
flange 28 above the bottom (2.4 thick, with a centre rib to +3.5), ear holes Ø4 at ±24.5 from the body centre (y ±5),
a label pad 1.1 mm proud on the case top (the strap has a pocket for it).

| Servo | Cable leaves | Route in the CAD |
|---|---|---|
| Door D and G | the **outer** end face (shaft end, x ±141), right against the outer post | channel in the post's inner face (open to the front, so the grommet slides in with the servo) → down into the 13 mm under the servo → out through a **~11 × 10 slot** in the bottom plate (the Dupont connector passes) → zip tie through the 2 holes beside the slot |
| Head | its **+x end face** (shaft end, x −3), next to the plate | the servo window is extended past that end, then an L slot runs down to the bracket's bottom edge (lay the cable in from the front) → zip tie through the 2 holes beside it, around the back through the plate's centre notch |

All carriage cables (3 servos) and the 3 tubes then go to the robot in one service loop (lift travel 75 mm).

## Bearings (7× 608ZZ, 8 × 22 × 7): how each one goes in
The seats are Ø22.2 with a 0.6 mm chamfer at the mouth: the bearing goes in **by hand or with a light tap** (a socket on the
outer race, or squeeze it in a vise between two flat pieces). Push only on the **outer race**. If a seat is loose, a drop
of CA glue; if too tight, warm the plastic with a heat gun for a few seconds.

| Where | How it goes in | What holds the shaft |
|---|---|---|
| Lift top (`A_TRAVERSE_HAUT`), 1× | from **below**, up against the 2.8 mm roof, before the top tie goes on the rails | the T8 screw's top end just turns in it (radial support; the coupler holds the screw at the bottom) |
| Door unit bottom (`A_AILE`), 1× per door | from the **top**, into the seat in the bottom plate (stops on a 1.8 mm floor with a Ø10 hole) | rod passes through |
| Door unit top (`A_CAPOT_AILE`), 1× per door | from **below** into the cap, before the cap goes on | rod passes through |
| Head bracket (`B_SUPPORT_TETE`), 2× | both from the **front**: bearing 1 to the bottom of the tube (shoulder at y 54), then the printed sleeve **`B_ENTRETOISE_TETE`**, then bearing 2 flush with the tube front | Ø8 head shaft through both |

**Door rod in its bearings:** the rod slides through both inner races. Two printed spacers bear on the inner races only:
**`A_ENTRETOISE_608_BAS`** (3 mm) between the bottom 608 and arm BAS, and **`A_ENTRETOISE_608_HAUT`** (4 mm) between
arm HAUT and the top 608. Tighten the arm clamps with the spacers touching. The rod is then held up and down by the arms
and turns on the inner races only; nothing rubs the outer races or the plastic.
**Head shaft:** the hub clamp (`B_MOYEU_TETE_30T`) has a small Ø12 boss that bears on the front 608's inner race: pushing
the cups onto the boxes loads it there. Against pulling forward, put **a drop of Loctite 641 (or CA) between the shaft and
the rear 608's inner race**.

## Heat-set inserts: where exactly (12 in total)
Push them in with the soldering iron (~220 °C for PETG), straight, until flush. Everything else uses nuts in pockets,
because those holes are slotted to adjust or must clamp (split clamps).

| Part | Inserts | Hole | For |
|---|---|---|---|
| `A_SUPPORT_ECROU` | **2× M4**, front face of the wall (z 140, z 160) | Ø5.6 × 7 | the 2 M4 × 8 button heads through the plate's centre holes |
| `A_SUPPORT_ECROU` | **4× M3**, underside of the shelf, around the nut hole | Ø4.0 × 6 | the T8 nut flange (M3 × 10 from below; 2 diagonal ones are enough) |
| `A_AILE_D` | **3× M3**, top faces of the inner side wall and the rear web | Ø4.0 × 6 | the cap `A_CAPOT_AILE_D` (M3 × 10) |
| `A_AILE_G` | **3× M3**, same | Ø4.0 × 6 | the cap `A_CAPOT_AILE_G` |

Check your inserts against these holes (`class G` INS3 / INS4) before printing.

## Fabrication: tolerances, inserts, adjustment slots
| What | Value in the CAD | Why |
|---|---|---|
| 608 seats (6×) | Ø22.2 × 7.2, 0.6 × 45° lead-in at the mouth | FDM holes print ~0.1 small: light press by hand |
| Ø8 rod through printed walls | Ø10 | the rod only touches the 608 inner races |
| Clamp bores (arms, 28T, head hub) | Ø8.2, slot 1.2 | slides on, the M3 closes it |
| M3 / M4 / M5 clearance | Ø3.4 / Ø4.5 / Ø5.5 | |
| M3 nut pockets | 5.8 × 6.6 × 2.8 | nut 5.5 AF × 2.4 |
| Heat-set inserts | M3: Ø4.0 × 6 · M4: Ø5.6 × 7 | **check against your insert box** (`class G` INS3/INS4) |
| Rail pockets (socle, top tie) | 20.4 × 20.4 | |
| Gears | backlash 0.15, centre distance set by the servo slots | |

**Adjustment slots (lumières)**, so the parts can be set in place at assembly:
| Where | Slot | Sets |
|---|---|---|
| Door unit → plate corners (2× M4 each) | ±1.5 in x (nut slides in its pocket) | doors centred on the stack |
| Door servo flange (3× M3) | ±2 along the gear line | pinion/28T mesh |
| Door servo strap (2× M3) | ±1 in x | strap lines up with the posts |
| Door sheet tabs (MDF, 4× M3 per door) | ±1.5 in y | pad position against the box face |
| Head servo flange (4× M3) | ±1.5 in x | 20T/30T mesh |
| T8 nut flange (M3 in Ø3.5) | float ±0.25 | nut follows the screw axis, no binding |

**Assembly order (door unit):** inserts in the body → bottom 608 in its seat → servo slides in from the front (pinion off,
cable down through its slot), flange screws, strap → rod with spacer BAS, arm BAS, 28T, arm HAUT, spacer HAUT dropped in
from the top → top 608 in the cap, cap on (3× M3) → pinion on the
horn, set the mesh with the slots → clamps tightened with the doors at 0° → bolt the unit to the plate.

## Rules check (300 × 300 base, stack not counted: FAQ Q1). Full table: [`CAD_FC/motion/motion_report.txt`](../CAD_FC/motion/motion_report.txt), details in [RULES.md](RULES.md)
- Start: perimeter 1200 mm, nothing outside the base.
- Deployed: worst ≈ 1367 mm ≤ 1400.
- Height: highest actuator 347.7 ≤ 350 (head carrier while turning, lift 75: only 2.3 mm margin). Rails/top tie ignored for now.
- The stack goes above 350 mm while turning in the castle: FAQ **Q9**, still open.

## Parts
**PETG** (4 walls, 40 % gyroid, gears 100 %), all ≤ 250 mm: `A_SOCLE`, `A_TRAVERSE_HAUT`, `A_SUPPORT_ECROU`, `A_AILE_D`,
`A_AILE_G`, `A_CAPOT_AILE_D`, `A_CAPOT_AILE_G`, `A_BRIDE_SERVO_D/G`, `A_BRAS_PORTE_D_BAS/_HAUT`, `A_BRAS_PORTE_G_BAS/_HAUT`, `A_ROUE_PORTE_28T` ×2, `A_PIGNON_PORTE_20T` ×2,
`A_ENTRETOISE_608_BAS` ×2, `A_ENTRETOISE_608_HAUT` ×2, `B_ENTRETOISE_TETE`, `B_SUPPORT_TETE`, `B_MOYEU_TETE_30T`, `B_PIGNON_TETE_20T`, `B_BAGUE_STATION` ×3. **TPU 95A:** `B_STATION_TPU` ×3.
**MDF (DXF):** `A_TOLE_PORTE` ×2 (3 mm), `B_PLATEAU_TETE` (6 mm).

| Qty | Part | Source |
|---|---|---|
| 2 + 1 + 4 | Y rails 2020 × 350, butterfly plate, V-wheels | 📦 printer |
| 1 + 1 + 1 + 1 | NEMA17, 5→8 coupler, T8 screw (cut to 292), brass nut | 📦 printer |
| 7 | 608ZZ (4 door units, 2 head, 1 screw top) | 🇹🇳 |
| 2 + 1 | plain Ø8 rod: 203 mm (doors) + 58 mm (head shaft) | 📦 lab rods |
| 3 | MG996R + round horn (2 doors, 1 head) | 📦 |
| 3 + 3 + 3 | DP-S30 cups + 12 V pumps (Lextronic) + 12 V vent valves; Ø4 silicone tube | planned / 🇹🇳 |
| 6 | EVA/foam pad 30 × 40 × 8 | 🇹🇳 |
| | M3 screws + nuts (in printed pockets), 4× M4 + nuts (door units), 2× M4 × 8 button head (nut support, the printer's own), 4× longer M5 (wheel bolts through the head bracket) | 📦 |
| 10 + 2 | brass heat-set inserts M3 (4 T8 nut, 6 caps) + M4 (nut support) | 📦 |

## Check on the real parts before printing (values in `class G`)
Already taken from real models: the butterfly plate (from the printer's CAD) and the MG996R (`resources/mg996r/`).
Still assumed: horn Ø21 × 2 (`HORN_R/T`), DP-S30 height 18 mm, T8 lead 8 mm, heat-set insert holes (`INS3/INS4`).
See [OPEN_POINTS.md](OPEN_POINTS.md).
