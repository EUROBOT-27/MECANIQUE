# Central hub option D: one transfer actuator per stone

Status: **concept + FreeCAD model, proposal** (Ayoub, 2026-11-18). Not reviewed by Seif. Nothing in `project/decisions.md`.
Robot: **base_330_js**. Same frame as options A–C: X = wheel axis (robot's left = −X), Y = forward, Z = up, origin =
robot centre on the table.

| File | What |
|---|---|
| `fc/check_d.py` | Box check (plain Python), both units, 1210 states → `hub_d_report.txt`, `../../simulations/central_hub/option_d_sheet.png`, `option_d_sequence.gif` (`--gif`) |
| `fc/hub_d_fc.py` | FreeCAD model (`freecadcmd fc/hub_d_fc.py`) → `CAD_FC/HUB_D_*.FCStd` (5 poses), `CAD_FC/HUB_D_HOME.step`, `hub_d_fc_report.txt` (solid clash check) |

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
| Bottom | 55 → 160 | parallelogram arm + **623ZZ roller under a fixed ramp** (steepest 34°) |

- **Drive:** each ring (r 35–48, 10 mm band) has **72 internal teeth** (m 1). The N20 stands inside the **hollow
  spine** (r 30/34, around the mast). Its 22 T pinion goes through a window in the spine wall: ratio 3.27, 314° of
  motor shaft for the whole turn. Position comes from the motor encoder, with **hard stops** on the ring at −3° and 90°.
  The 6 motors are 60° apart, so no pinion meets another motor.
- **Ring bands** (hub frame): front/rear bottom 131–141 / 141–151, middle 151–161 / 161–171, top 174.5–184.5 / 184.5–194.5.
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

## Sequence (each unit on its own, or both together)

1. **Pick:** hub at 0, every ring at 0, drive the cups onto the stack faces, vacuum on. **Wall:** hub to 12, carry, set down, vent.
2. Hub to 14. **Unpinch:** the unit's top and bottom rings turn back to −3° (the top stone rises 3.4, the bottom one dips 3).
3. **Middle:** its ring 0 → 90, top + bottom rings back to 0, spin 90°, hub to 0 (the tower stands on the table), vent, ring back.
4. **Bottom**, then **top**: same. The robot drives ≥ 0.34 m between levels.

**New with option D:** the front unit can build its towers **while the rear unit keeps its 3-stone stack in its cups**
(and the reverse). The hub lift is shared, so the held stack goes down to the table with each set-down and back up.
Checked as run B.

## Results

| Check | Result |
|---|---|
| Box check, run A (both units together, 404 states) | **no clashes**, height −3.0 … 347.4 (top stone at the unpinch, hub at 14) [GR F.3] |
| Box check, run B (front alone while rear holds, then rear alone, 806 states) | **no clashes**, same heights |
| FreeCAD solids: home, front top at 45°, front bottom spinning, rear middle stood up + every arm alone at 15/30/60/75° (in build order) | **no clashes**, highest 344.0 |
| Perimeter [GR F.3] | start **1249** (> 1200, as option C: plate 1232 + cups 36 mm front and back); deployed **1233** (≤ 1400) |
| Drag link / ramp | worst transmission angle 31° (keep > 30); steepest ramp 34° |

`HUB_D_DEPLOYED.FCStd` puts every arm at 90° at once for the perimeter rule (FAQ Q10). It can never happen, because the
3 arms of a unit end on the same spot. So it is saved as an envelope and not clash-checked.

## Parts (concept level)

| Part | Qty | Source |
|---|---|---|
| N20 gear motor **with encoder** (~50–100 rpm, 6 or 12 V) + motor driver channel | 6 | 🇹🇳 likely / ✈️ |
| Ring, 72 T internal m 1, r 35–48 × 10 (printed ABS, D-023) + 22 T pinion | 6 + 6 | printed |
| Hollow spine r 30/34 with 6 windows, sliding on the mast | 1 | printed ABS |
| Spin servo MG90S + cup shaft on 2 small bearings + VS2-S30 cup + 12 V pump | 6 | 📦 / 🇹🇳, cups ordered (Seif) |
| Drag rod M3 157 mm + 2 ball links (top) | 2 | 🇹🇳 RC shops |
| 623ZZ roller + M3 pin, ramp (bottom) | 2 | 📦 / 🇹🇳 |
| Parallelogram pins M3 (4 per arm, top + bottom arms) | 16 | 📦 / 🇹🇳 |
| Hub lift MG996R + crank (shared) | 1 | 📦 / 🇹🇳 |

Motors: **6 transfer + 6 spin + 1 lift = 13**, against 10 for option C. The 3 extra buy independent front/rear units
and half the load per motor.

## Open points

1. **Ring friction:** the 6 ring bands are stacked with no gap (box check: every lug ≤ 3 mm from the neighbouring ring).
   Turning one ring would drag its neighbour. Put a PTFE washer or a 1 mm printed shoulder on the spine between
   bands, or shrink the rings to 9 mm.
2. **N20 torque and speed:** the bottom stone's ramp needs ~3 kg·cm peak at the ring, ~0.9 kg·cm at the N20 (÷ 3.27).
   Pick the gearbox (≈ 50–100 rpm → 96° in ~1 s) and test it with a real arm + stone.
3. **Electronics:** 6 more DC motor channels with encoders (instead of PWM servos). Check with Hamza Bjaoui. Homing
   on the hard stops at start-up.
4. **Pinion window and gear strength:** m 1 printed teeth at 10 mm wide; check after a print test (tolerance coupons, D-023).
5. **Start perimeter 1249 > 1200**, as option C: the final footprint (`layout-v1` / `robot/`) must take the hub into account.
6. Stack height with worst-case stones (115 mm), cable loops for the spin servos and hoses (90° per ring), lift guide:
   as option C open points 1, 6.
7. Strategy: 4 tower zones per team [G D.4], so 6 towers is more than can score (option B/C open point).
8. Gate lintel: not covered.
