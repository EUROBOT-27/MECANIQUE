# Central hub option B: one lift + one turret (simplified option A)

Status: **concept, proposal, PAUSED 2026-11-18** (Ayoub). Not reviewed by Seif. Nothing in `project/decisions.md`.
Paused because the fixed holder cups grip each stone 100 mm off its centre, and a stone must be held from the middle
(open point 8). Restart from there. Interactive comparison of B with two simplified variants (3 and 2 motors) + 3D wall/tower
sequences: https://claude.ai/artifact/U8UQDkDet7VDkMRGUdMCQC (private, Ayoub).
Check: `fc/check_b.py` → `hub_b_report.txt` + `../simulations/central_hub/option_b_sheet.png` (plain Python, boxes,
not a FreeCAD model yet). Same frame, stack, stone heights and base_330 parts as option A (`CONNECTIONS.md`).

## Why

Option A has **13 motors** (3 turn MG996R, 6 spin MG90S, 4 N20 slides) + 6 pumps, and the turn is not robust:
- the rings turn on a 10 mm plain ABS journal (0.5° tilt ≈ 2.5 mm at the stone), driven through a 2:1 internal gear
  (servo backlash × 2 at the cup) by servos hidden inside the hub (a servo comes out only after the segments above it);
- the slides are 8 × 10 printed rails cantilevered 143 mm, with N20 + M4 screws (~33 s per stroke at 300 rpm);
- each cup spins on a bare MG90S spline (the servo's plastic bushing carries the stone), with no hard stop, and the
  spin height comes from an N20 + switch on a flexing rail, where the margin is 6 mm to the table and 6 mm to 350.

The 3 levels never work at the same time anyway (order middle → top → bottom), so 3 sets of actuators are not
needed: **one set of actuators can visit the 3 levels in turn.**

## The idea

- **Fixed column** at the hub axis: 2 × Ø8 steel rods + T8 lead screw, bridge (z 73) to a top plate (z 345–350,
  base for the beacon mast). The rods are clamped at both ends, so nothing is cantilevered from a printed part.
- **One carriage** on the rods (LM8UU / SCS8UU), driven by **one NEMA17 + T8** (all 📦). The motor stands on the base
  plate in the free front-right quarter (x 19–61, y 64–106), direct coupled; the nut is on a carriage ear. Homed
  with one endstop, so every height (pick, unpinch, spin, set) is a step count, not a switch on a printed rail.
- **One turret** on the carriage, turning 0 → 90° about the column, carries **both arms** (front + rear, 180° apart,
  same as one ring of option A). Turret on 3 V-wheels (📦 Ender, eccentric spacers take up the play) in a V-groove
  on the carriage. Driven by **one MG996R** through a ~1.33:1 spur pair, so the servo only needs ~120° (the MG996R
  range doubt of option A goes away). **Hard stops at 0° and 90°**, a switch at 90°.
- **Spin, made safe:** per arm one MG996R (stronger than the MG90S), but the cup sits on its own short shaft in **2 ball
  bearings** in the arm tip; the servo only gives torque through its horn. Pin + 90° slot = hard stops. Spin is only
  allowed at turret 90° (switch) and at the lift's spin height (step count). The arms are rigid L-shaped parts on the turret.
- **Fixed holder cups (no motor):** a vertical bar per unit with 3 cups at x = +100 (off-centre on the stone face; the
  arm cup is at the centre). They hold the stack while driving and pull it out of the quarry. **A wall needs no motor
  at all:** hold, carry, vent.

### Sequence (both units together, like option A)
Top, then middle, then bottom. For each level:
1. Turret at 20° (cup rim 5 mm off the stack face), lift to the level.
2. Turret 20 → 0°: the cup slides onto the stone face (bellows cup), vacuum on; vent that level's holder cup.
3. Unpinch: lift +3 (top, middle) or +40 (bottom: its arm then clears the wheel top and the stone clears the plate).
4. Turret 0 → 90°.
5. Lift to z 173, spin 90°: the stone stands up.
6. Lift down 13 mm: the stone stands **on the table** (no 15 mm drop for any level, option A had one on middle + top).
7. Vent, turret back to 20°. The robot drives ≥ 0.34 m before the next level (Gazebo, option A).

## Result of `fc/check_b.py` (345 steps, both units)

| | |
|---|---|
| Clashes | **none** (vs plate, drive motors, wheels, bridge, lift motor, top plate, holder bars + cups, stack stones, other unit) |
| Under 3 mm | the bottom stone leaving the middle holder cup (its top edge slides past, moving away) |
| Lift stroke | 223 mm, carriage block z 76–339 (bridge top 73, top plate 345) |
| Height | everything ≤ 343 (stones included) [GR F.3] |
| Spin at 173 | nominal stone: lowest corner 3.8, highest 342.2; worst stone 324 × 115: 1.1 / 344.9 |

**The spin margin is physics:** standing up a 320 × 110 stone needs 320 sin a + 110 cos a = **338 mm** of height
at a = 71°, out of 350, whatever the mechanism. What B changes is that the height is set by a homed stepper on steel
rods and the stone sits on a bearing shaft with hard stops, so the 6 mm on each side is not eaten by rail flex or a
switch.

## A vs B

| | Option A | Option B |
|---|---|---|
| Motors | 13: 3 MG996R + 6 MG90S + 4 N20 | **4: 1 NEMA17 + 3 MG996R** |
| Driver channels | 9 PWM + 4 DC (2 H-bridges) | 3 PWM + 1 stepper driver |
| Limit switches | 4 | 2 (lift home, turret 90°) |
| Pumps / vent valves | 6 / 6 | 8 / 8 (6 holder cups + 2 arm cups) |
| Turn support | 3 plain ABS journals, 10 mm long | 1 turret on 3 V-wheels, adjustable |
| Height axis | 4 printed rails, cantilevered | 2 steel rods, both ends held |
| Spin | MG90S spline carries the stone, no stop | bearing shaft, hard stops, interlocked |
| Servo service | take the hub segments apart | everything on the outside of the carriage |
| Walls | 6 cups (shafts at home) | 6 fixed holder cups, no motor |
| Failure | a level's servo dies → 2 towers lost | lift or turret dies → all towers lost (walls still work) |
| Speed | 33 s for 6 towers (Gazebo, 40 mm/s slides) | similar: 3 lift moves of ≤ 220 mm at ≥ 40 mm/s, not simulated |

## Open points
1. **Engaging the next stone:** the cup reaches the face sideways (turret 20 → 0°), not straight on. Test that the
   VS2-S30 bellows takes it on cardboard (holder cups keep the stone still).
2. **Release** after venting: the cup still rubs the tower when the turret turns back (same as option A, seen in Gazebo).
3. **Pneumatics:** 8 cups. One pump per cup (12 in hand: 6 × 370 + 6 mini). Sharing a pump needs 3/2 valves.
4. **Strategy:** a team has **4 tower zones** [G D.4] and one building per zone, so 6 towers is more than can score.
   If 4 towers are enough, drop the bottom level from the tower job (it stays a wall/holder stone): stroke 110 mm,
   no unpinch +40, the arms never go near the wheels.
5. Cable + hose loop: one moving carriage (220 mm + 90°) instead of 3 rings, run in the free front-right quarter.
6. Not checked: base_330 encoder wheel units, layout-v1 modules, tool access, cables.
8. **Holder cups off-centre (blocking, Ayoub 2026-11-18):** each holder cup sits at x = ±100, 100 mm from the stone's
   centre, so the stone can twist or peel off; a stone must be held from the middle. But the middle of the inner face is
   where the arm cup engages. To solve before restarting: e.g. hold from the middle on another face, 2 cups per stone
   (x = ±100), or a different stack holder. Variants studied before the pause: one servo for both spins (3 motors),
   turret also drives the spin through a fixed bevel sector (2 motors).
9. Next step if Seif agrees: FreeCAD model `fc/hub_b_fc.py` with real parts (LM8UU, V-wheels, MG996R, bearings,
   fasteners), then the Gazebo sim.
