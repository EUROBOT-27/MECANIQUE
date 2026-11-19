# T1: module B v1, the turning plate (D-028, 2026-11-18)

**What it is:** a plate with 3 suction cups (one per stone) on the butterfly plate. A servo turns the plate 90°, so a
lying quarry stack becomes 3 standing stones side by side (towers). Without turning, it is a wall gripper.
**Pumps and valves stay in the robot**: only 3 tubes come to module B.

```
butterfly plate (module A's lift)
  └─ printed bracket (on the 4 wheel bolts) with a bearing housing
       ├─ MG996R servo + round horn + 20T pinion      (fixed)
       └─ 2 × 6002 bearings (15 × 32 × 9)
            └─ HOLLOW shaft: tube Ø15 × 1 (copper plumbing pipe, alu or steel)   (turns)  ← the 3 tubes go through it
                 ├─ rear collar (coupler clamp)
                 └─ printed hub: 33T gear + flange + coupler clamp
                      └─ MDF 6 turning plate + 3 cup stations (S3 or S1, same holes)
```

Generator: `../../fc/turn_t1.py`. Folders: `T1_S3/`, `T1_S1/` = grab pose (lift 0, not turned) with each cup station,
print files in `STEP/`, `STL/`, `DXF/` (as clapets v7);
`T1_S3_a90/`, `T1_S1_a90/` = after the turn (FCStd + report only).
```
cd mechanical/suction-v1
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/turn_t1.py                       # -> T1_S3/
STATION=S1 "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/turn_t1.py            # -> T1_S1/
ANGLE=90 "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/turn_t1.py              # -> T1_S3_a90/
```

## The bearings, simply
- **How a 6002 is held:** its outer ring is pressed into a round seat printed in the bracket's housing (Ø32.1 for a
  32 bearing, same +0.1 as the 608 seats of v7: print an ABS test ring first). Between the two seats the housing has a
  2 mm **shoulder** (a ring that only touches the outer rings). The rear bearing goes in from the back until it
  hits the shoulder, the front one from the front until it hits the other side of the shoulder.
- **Why two bearings:** the plate + stones (~0.8 kg) hang ~60 mm in front of the bearings. That load tries to
  **tilt** the shaft, not just push it down. One ball bearing has play and lets the shaft wobble. Two bearings 11 mm
  apart turn the tilt into two small sideways forces, and the shaft stays straight.
- **What each clamp does:** the shaft must not slide forward or backward in the bearings.
  - **Plate pushed back** (pressing on stones): the hub clamp pushes the front bearing's inner ring back, and its
    outer ring rests on the shoulder.
  - **Plate pulled forward** (lifting the stack, a stone stuck): the **rear collar** pulls the rear bearing's inner
    ring forward, and its outer ring rests on the other side of the shoulder.
  - Without the rear collar, only the bearing press fit would stop the shaft from sliding out forward.
  - So every load ends on the printed shoulder, never on the press fit. The press fit only positions the bearings.

## Tube route (cup → robot)
1. Each cup's elbow → along the front of the plate (22 mm in front of it) → to the plate centre.
2. Into the **hollow shaft**: the 3 tubes run through it together, turning with the plate.
3. Out of the shaft's back end, inside the bearing housing (behind the rear bearing) → they fan out to the right
   through a window in the housing → in Ø6 guide grooves → up the bracket front (x 22 / 38 / 50) → tube clip → to the robot (free loop:
   the lift moves 75 mm).

When the plate turns 90°, the 3 tubes only **twist a quarter turn** between the shaft end and the clip (Ø4 PU, fine).
Nothing swings around. Every bend is **R12** (catalogue minimum for a tube that doesn't move).
To make room for this, the **middle cup sits 70 mm to the right** of the stone's centre (the centre is where the
tubes enter the shaft).

## How the turn works
The lift goes up **while** the plate turns, so the stack's low corner skims the table:
lift = 160 sin t + 165 cos t + 5 − 165 → 5 mm at the start, **70 mm at 44°** (module A's lift goes to 75), back to
0 at 90°. At the end the 3 stones stand on the table (320 tall: legal anywhere). Mid-turn the stack reaches
**465 mm**: **castle only** (FAQ Q9 = yes).

## Key numbers
| | |
|---|---|
| Cups | 3 × DP-S30: top + bottom on the centre line **85 mm** from the middle (table 80 / 250), middle at x +70 (table 165) |
| Why 85 and not 110 | so the turning plate itself stays **≤ 350 during the turn: 343.8 max** (computed on every vertex) |
| Cup station | **S3** (spacer + TPU disc + rigid support ring, same as the flip-bar), see below |
| Drive | MG996R + round horn, 22T → 33T (m1.25): 90° of plate = 135° of servo (22/33 keeps the pinion's horn collar clear of the bearing housing) |
| Pinion | sits on the horn with a plain **collar around the horn disc** (centres it, as the v7 door pinion) |
| Clamps on the shaft | **coupler style** (design principles): round hub, slot on one side, M3 across it inside the outline |
| Bought, new | 2 × 6002-2RS (15 × 32 × 9) 🇹🇳 local; tube Ø15 × 1, 54 long: copper plumbing pipe (any hardware shop) 🇹🇳, or alu / steel |
| Room in the shaft | Ø13 inside for 3 × Ø4 tubes (they need Ø8.6): 2.2 mm all round, easy to push through |
| Turning plate | MDF 6, 154 × 254 (`T1_S3/DXF/`, same plate in both) |
| Printed | S3: ~447 g (bracket 96, hub 36, 3 × S3 = 227 incl. 48 g TPU) · S1: ~295 g |
| Stack face | y 151.4 with S3, 149.9 with S1 (layout-v1: 146) |
| Lowest point | plate 43 above the table at lift 0 → **no notch in the robot floor** |
| Mounting | same part front (A+B, between the door units) and back (B alone) |

## Why S3 and not the other holders
| | Holds the stone how | Tube | On this plate |
|---|---|---|---|
| S1 rigid (25 g) | bellows only: the stone can rock | in front | fits, lightest |
| S2 TPU + pot | TPU spring | **behind** the plate | no: behind the plate is the hub |
| **S3 TPU + ring (76 g)** | TPU spring + **rigid ring the stone sits on** | in front | **fits** |
| S4 spring plunger | spring + stop | in front | 10 mm deeper: stack further out |

When the stack is turned on its side, the cups hold the stones **sideways**. With S1 only the bellows would
carry them, and they sag and rock. S3's ring gives them a rigid seat, which is the same reason the flip-bar uses it.
Cost: 150 g more than S1. **Both are built** (same plate, same holes, just screwed on): try both on the bench.

## Checked (`../../fc/check_t1.py` → `check_report.txt`, 2026-11-19)
Full cycle, S3 and S1, both mountings, 61 poses (A+B) / 30 (B alone):
- doors fold / unfold
- grab, clamp, carry (lift 15), lower
- doors open with the cups holding
- lift-turn 0 → 90° in 5° steps
- release, plate back to 0°

| | A+B (front) | B alone (back) |
|---|---|---|
| Highest module B point | 343.6 (turn 35°) ≤ 350 ✅ | same ✅ |
| Highest stone point | 464.6 (turn 45°): castle only (Q9) | same |
| Grab, clamp, carry, turn, release | **0 collisions** (stack vs open doors too) ✅ | **0 collisions** ✅ |
| Doors folding | ❌ **right door (+x) touches module B past 46° (S3) / 52° (S1)**, left door past 78° / 82° | no doors |

**Why the doors hit:** v7 left module B a pocket of x ±30, y ≤ 140 for the folded doors (its head was 56 wide). T1 is
±42 wide with Ø76 stations, the middle cup at x +70, and its stations reach y 154.

**Start perimeter if the doors fold less** (module A + B hull): folded 90° = 758, 60° = 782 (+24), 40° = 835 (+77).
Right at ~50° + left at ~80° ≈ +35–45 mm on layout-v1's 1114 → ~1150–1160 (limit 1200).

## Assembly order
Before the bracket goes on the butterfly plate:
1. Rear 6002 from the back, front 6002 from the front (the shoulder between them is part of the housing).
2. Shaft from the front through both bearings.
3. Rear collar on from the back. Its M3 × 12 is reached with a key through the side hole.
4. Hub on the front end (put the nuts in its 3 pockets first), M3 × 14 clamp from the left.
5. Push the 3 tubes through the shaft.

Then:
- bracket on the 4 wheel bolts
- servo (M3 × 8 into inserts), pinion on the horn
- plate with its stations onto the hub flange

## Not done yet
- Doors (A+B): checked only in their CAD pose; they must be open while the plate turns.
- Tube clamp on the turning side (near the shaft entry) so the tubes can't be pulled: not modelled yet.
- Tube loop from the bracket to the robot (lift 75 mm) and where the pumps sit in the robot: with the robot layout.
- Servo torque test; real-stone test of the off-centre cups.
