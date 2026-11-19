# Central hub option D: one transfer actuator per stone

Status: **concept + FreeCAD model, proposal** (Ayoub, 2026-11-18). Not reviewed by Seif. Nothing in `project/decisions.md`.
Robot: **base_330_js**. Same frame as options A–C: X = wheel axis (robot's left = −X), Y = forward, Z = up, origin =
robot centre on the table.

> **2026-11-19: bottom level simplified to a fixed holder** (Ayoub's request, proposal). The bottom stone no longer
> moves: no ring, N20, spin servo, parallelogram, roller or cam sleeve. It is carried with the stack (walls) and left
> lying when tower mode starts, so **each unit builds 2 towers (middle + top), 4 in all = the 4 tower zones per team
> [G D.4]**. Motors **13 → 9**. Switch back with `BOTTOM_FIXED = False` in `fc/check_d.py` (the old bottom code is kept).
> See "Bottom level: fixed holder" below.

| File | What |
|---|---|
| `fc/check_d.py` | Box check (plain Python), both units, 814 states (1210 with the moving bottom) → `hub_d_report.txt`, `../../simulations/central_hub/option_d_sheet.png`, `option_d_sequence.gif` (`--gif`) |
| `fc/hub_d_fc.py` | FreeCAD model (`freecadcmd fc/hub_d_fc.py`) → `CAD_FC/HUB_D_*.FCStd` (5 poses; `HUB_D_2_FRONT_TOP_SPIN` replaced `HUB_D_2_FRONT_BOTTOM_SPIN`), `CAD_FC/HUB_D_HOME.step`, `hub_d_fc_report.txt` (solid clash check) |
| `fc/hub_d_gif.py` | GIF rendered from the FreeCAD solids (`FreeCAD.exe fc/hub_d_gif.py`, GUI, closes itself): run B sequence, 3D + top view → `../../simulations/central_hub/option_d_freecad.gif` + 4 stills |
| `fc/hub_d_zoom_gif.py` | Zoomed GIF of the height guide (top: drag link; with the fixed bottom there is no bottom guide any more), front unit only (`FreeCAD.exe fc/hub_d_zoom_gif.py`) → `../../simulations/central_hub/option_d_guides_zoom.gif` + 2 stills |
| `fc/hub_d_levels_gif.py` | Zoomed GIF of the front unit's 3 levels doing the build sequence (bottom left lying, then middle → top), one colour per level (`FreeCAD.exe fc/hub_d_levels_gif.py`) → `../../simulations/central_hub/option_d_levels.gif` + 3 stills |

Both scripts take the arm geometry, the guides, the robot and the stones from option C (`../fc/check_c.py`), so the two
options are checked the same way.

## The idea

Ayoub's brief: **one actuator moves one stone** from its place in the stack (in front of the robot) along one arc to the
spin-safe position beside the robot. There the cup servo stands it up, as before.

- **Each of the 6 stones has its own ring** on the hub axis, turned −3 → 90° by **its own N20 gear motor**. The front
  and rear units are now independent (option C: one ring per level drove both).
- **The height comes from a fixed passive guide**, so the same motor makes the whole move (unchanged from option C):

| Level | Stone centre (stack → side) | Guide |
|---|---|---|
| Top | 275 → 160 | parallelogram arm + **drag link** (rod 157 mm, 2 ball links) to a fixed anchor on the spine |
| Middle | 165 → 165 (cup 5 mm below the centre, ends at 160) | none, rigid arm |
| Bottom | **55, fixed** (2026-11-19) | **none: fixed holder**, the stone is not transferred (before: parallelogram arm + 623ZZ roller under a fixed ramp / in a grooved sleeve, steepest 34°) |

- **Drive:** each ring (r 35–48, 10 mm band) has **72 internal teeth** (m 1). The N20 stands inside the **hollow
  spine** (r 30/34, around the mast). Its 22 T pinion goes through a window in the spine wall: ratio 3.27, 314° of
  motor shaft for the whole turn. Position comes from the motor encoder, with **hard stops** on the ring at −3° and 90°.
  The motors are 60° apart, so no pinion meets another motor (4 motors left with the fixed bottom: polar 120 / 180 / 240 / 300).
- **Ring bands** (hub frame): middle 151–161 / 161–171, top 174.5–184.5 / 184.5–194.5 (front / rear). The old bottom
  bands 131–151 are now free; the other rings were not moved.
- Spin (MG90S on a bearing shaft + hard stops) and **hub lift** (MG996R + crank, 0–20 mm) as option C.

### Why the stone moves on a guided arc, not a pure hinge arc

A rigid arm on **one fixed hinge** (a true circular arc, no guide) was tried first (2026-11-18). The stone's face must
turn from +Y to −X and end horizontal, so the spin can stand it up. To end where option C puts it (cup face r 176, so
the tower stands 8 mm off the plate), the hinge would have to be **450–550 mm away** from the stone, which is off the
robot. With the hinge on the hub, the axis tilts ~27° and the turn is 130–140°. But the towers then end **70–150 mm
further out**, and the deployed perimeter becomes **≥ 1477 mm counting only the cups** (> 1400, [GR F.3], FAQ Q10). So
the swing axis stays vertical through the hub. A 90° heading change with the face at r 176 at both ends only works
with the axis exactly on the hub centre, and the guide adds the height.

### Why the motors are inside the spine

A first layout put 270° servos **outside** the spine, with the pinion on the ring's outer teeth. A placement search
(every polar angle, above/below, shaft extensions) found **no layout**. The only space no arm sweeps is 2 slots of
~20° (polar 124–144 / 304–324, front frame), and each slot would have to hold 3 servos + Ø36 pinions in z 87–238.

## Bottom level: fixed holder (2026-11-19)

**Why:** the bottom level was the most complex part of the hub (parallelogram with 4 pins, cam lever, 623ZZ roller,
a grooved cam sleeve with a 3D groove, its own ring + N20 + spin servo) for the stone that has to rise the most
(55 → 160). Only **4 tower zones per team** score [G D.4], and the 2 units already give 4 towers with the middle and
top stones. So the bottom stone is held, not moved.

**What it is** (per unit, both bolted to one collar):

| Part | Size / place |
|---|---|
| Collar, printed ABS, clamped on the spine (shared by both units) | r 34–42, z 86–102 (hub frame), moves with the hub lift |
| Bracket beam, from the collar out | r 42 → 137.5, z 88–100, 24 wide (15 mm over the bridge plate) |
| Bracket drop, down to the cup | r 126.5–137.5, z 42–88, 32 wide |
| Fixed cup mount (no spin servo) + VS2-S30 cup | cup face r 176, cup at z 55: where the old bottom arm held it at turn 0 |

**New sequence for towers** (walls unchanged: all 3 cups hold, hub to 12, carry, set down, vent):
1. Hub at 0, stack on the table: **the bottom cup vents, the bottom stone stays lying on the table**.
2. Unpinch: the top ring turns back to −3° (top stone rises 3.4).
3. Hub to 14: the middle stone now has **14 mm under it** (before, the bottom ring dipped 3 mm), and later the top stone
   can drop to 160 without touching the bottom stone.
4. Middle: transfer, spin, set down, vent, ring back (as before). The robot drives on (≥ 0.34 m); the bottom stone stays
   behind, lying.
5. Top: as before.

Keeping the bottom stone in its cup during the tower build does **not** work: the top stone drops 275 → 160 and hits it
(box check, 7 states around turn 45–60°). That is why it is left at step 1.

**Counts:** 4 rings + 4 N20 + 4 pinions (was 6), 4 spin MG90S (was 6), 1 hub lift → **9 motors** (option C: 10, D before: 13).
Removed: 2 parallelogram arms (4 links, 8 pins), 2 cam levers, 2 623ZZ rollers, the grooved cam sleeve, 2 rings, 2 N20, 2 MG90S.
Still 6 cups and pumps (the bottom cups are needed for walls).

**What we lose:** the bottom stone of a tower run is not stood up. It is left lying where the stack was picked up: 1 point
if that is inside a construction zone [G E.1], otherwise it has to be fetched again (open point 9).

## New parts compared with option C

What changes is only the **transfer drive** (how each arm is turned). Everything else is option C's.

| Part | Option C | Option D | In the GIF (`option_d_freecad.gif`) |
|---|---|---|---|
| Transfer rings | 3 (one per level, front + rear arms on the same ring) | **6** (one per stone), 10 mm bands stacked on the spine | blue = front unit, orange = rear unit |
| Ring teeth | outer gear Ø~112 driven by a servo | **72 T internal, m 1** (teeth on the inside of the ring) | inside the ring, hidden by the spine |
| Transfer actuator | 3 × MG996R (outside) | **6 × N20 gear motor with encoder**, standing **inside** the hollow spine | black cylinders inside the spine |
| Pinion | servo gear | **22 T pinion (m 1)** on each N20, through a window in the spine wall (ratio 3.27) | yellow |
| Spine | lifting spine, plain | **hollow spine r 30/34 with 6 pinion windows** (motors 60° apart) | dark grey tube |
| End positions | servo angle | **hard stops on each ring at −3° and 90°** + encoder homing on the stops | — |
| Electronics | 3 PWM channels | **6 DC motor driver channels + 6 encoders** (open point 3) | — |

**Unchanged from option C:** parallelogram arms, top drag link (rod 157 + 2 ball links) and its spine anchor, bottom
623ZZ roller + fixed ramp (dark grey), middle rigid arm, 6 cups on bearing shafts with MG90S spin servos (dark grey
at the arm tips), hub lift MG996R + crank, the mast. Stones are tan, stones already standing as towers are darker tan.

**Removed:** the 3 MG996R ring servos of option C and their outer gears.

## Sequence (each unit on its own, or both together)

1. **Pick:** hub at 0, every ring at 0, drive the cups onto the stack faces, vacuum on. **Wall:** hub to 12, carry, set down, vent.
2. **Towers:** hub at 0, the bottom cup vents (bottom stone left lying). **Unpinch:** the top ring turns back to −3°
   (the top stone rises 3.4). Hub to 14.
3. **Middle:** its ring 0 → 90, top ring back to 0, spin 90°, hub to 0 (the tower stands on the table), vent, ring back.
4. **Top**: same. The robot drives ≥ 0.34 m between levels.

(Before 2026-11-19: unpinch moved the top and bottom rings, and the order was middle → bottom → top.)

**New with option D:** the front unit can build its towers **while the rear unit keeps its 3-stone stack in its cups**
(and the reverse). The hub lift is shared, so the held stack goes down to the table with each set-down and back up.
Checked as run B.

## Results

With the fixed bottom (2026-11-19, `BOTTOM_FIXED = True`):

| Check | Result |
|---|---|
| Box check, run A (both units together, 272 states) | **no clashes**, height 0 … 347.4 (top stone at the unpinch, hub at 14) [GR F.3] |
| Box check, run B (front alone while rear holds, then rear alone, 542 states) | **no clashes**, same heights |
| FreeCAD solids: home, front top at 45°, front top spinning (bottom left lying), rear middle stood up + every moving arm alone at 15/30/60/75° (in build order) | **no clashes**, highest 344.0 |
| Perimeter [GR F.3] | start **1249** (> 1200, unchanged: plate 1232 + cups 36 mm front and back); deployed **1250** (≤ 1400; the bottom holders stay at the front / back) |
| Drag link | worst transmission angle 31° (keep > 30) |

Before (moving bottom, 2026-11-18): same results with 1210 states, deployed 1233, steepest bottom ramp 34°.

`HUB_D_DEPLOYED.FCStd` puts every moving arm at 90° at once for the perimeter rule (FAQ Q10). It can never happen,
because the arms of a unit end on the same spot. So it is saved as an envelope and not clash-checked.

## Parts (concept level, fixed bottom)

| Part | Qty | Source |
|---|---|---|
| N20 gear motor **with encoder** (~50–100 rpm, 6 or 12 V) + motor driver channel | 4 | 🇹🇳 likely / ✈️ |
| Ring, 72 T internal m 1, r 35–48 × 10 (printed ABS, D-023) + 22 T pinion | 4 + 4 | printed |
| Hollow spine r 30/34 with 4 windows, sliding on the mast | 1 | printed ABS |
| Spin servo MG90S + cup shaft on 2 small bearings + VS2-S30 cup + 12 V pump | 4 | 📦 / 🇹🇳, cups ordered (Seif) |
| Bottom holder: collar (shared) + 2 brackets + 2 fixed cup mounts, printed ABS; VS2-S30 cup + 12 V pump each | 1 + 2 + 2 | printed / 📦 |
| Drag rod M3 157 mm + 2 ball links (top) | 2 | 🇹🇳 RC shops |
| Parallelogram pins M3 (4 per arm, top arms) | 8 | 📦 / 🇹🇳 |
| Hub lift MG996R + crank (shared) | 1 | 📦 / 🇹🇳 |

Motors: **4 transfer + 4 spin + 1 lift = 9**, against 10 for option C (13 for D with the moving bottom).

## Open points

1. **Ring friction:** the 4 ring bands are stacked with no gap (box check: every lug ≤ 3 mm from the neighbouring ring).
   Turning one ring would drag its neighbour. Put a PTFE washer or a 1 mm printed shoulder on the spine between
   bands, or shrink the rings to 9 mm. (The free bottom bands 131–151 leave room to spread them out.)
2. **N20 torque and speed:** the worst load was the bottom ramp (~3 kg·cm at the ring, gone with the fixed bottom). Now
   the top stone goes down and the middle one stays level, so the load is lower: still pick the gearbox (≈ 50–100 rpm → 96°
   in ~1 s) and test it with a real arm + stone.
3. **Electronics:** 4 DC motor channels with encoders (instead of PWM servos). Check with Hamza Bjaoui. Homing
   on the hard stops at start-up.
4. **Pinion window and gear strength:** m 1 printed teeth at 10 mm wide; check after a print test (tolerance coupons, D-023).
5. **Start perimeter 1249 > 1200**, as option C: the final footprint (`layout-v1` / `robot/`) must take the hub into account.
6. Stack height with worst-case stones (115 mm), cable loops for the spin servos and hoses (90° per ring), lift guide:
   as option C open points 1, 6.
7. Strategy: 4 tower zones per team [G D.4]: with the fixed bottom the hub builds exactly 4 towers (2 per unit).
8. Gate lintel: not covered.
9. **Where the bottom stone goes** (fixed bottom): it is left lying where the stack was picked up for a tower run.
   Pick tower runs so that spot is inside a construction zone (1 point per stone [G E.1]), or plan to collect it
   again for a wall. The robot also has to back away from it (it lies in front of the unit).
