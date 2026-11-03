# Rules check (Eurobot 2027, "The Legend of Camelot")

The rules that shape this mechanism, and how v5 is checked against them. References are to the General Rules (GR) and
the game rules (G).

## Constraints used
| Constraint | Value | Ref |
|---|---|---|
| Perimeter at start | ≤ 1200 mm (convex hull of the vertical projection) | GR F.3 |
| Perimeter deployed | ≤ 1400 mm, at all times | GR F.3 |
| Height | ≤ 350 mm for the robot **and manipulated objects**, at all times | GR F.3 |
| Stone | cardboard box 320 × 110 × 110 mm, ~90 g, ±4/±5 mm, deforms; quarries hold stacks of 3 lying stones | G |
| Tower | 1 stone standing (320 mm) | G |

**Base assumed: 300 × 300 mm** (x ±150, y −160 … 140, the stack face at y 140). The rails and the top tie are ignored in
the height check for now: they will be cut, or the lift rearranged, for the competition robot.

## Results (full match cycle, `fc/motion_v5.py`, 88 frames)
| Step | Perimeter | Outside the base | Highest part |
|---|---|---|---|
| Start: doors folded | **1200.0 mm** | **0.0 mm** | 273.0 (head carrier) |
| Doors open | 1367.3 | 66.1 | 273.0 |
| Clamp the stack | 1364.8 | 57.8 | 273.0 |
| Carry: lift 15 mm | 1322.6 | 45.0 | 288.0 |
| Cups hold, doors open −38° | 1367.0 | 70.5 | 273.0 |
| Lift 75 mm with the stack | 1365.4 | 74.7 | 344.2 |
| **Turn the stack 90°** | 1365.4 | 74.7 | **347.7** (head carrier) |
| Lower, release, back away, fold | ≤ 1365.4 | ≤ 74.7 | ≤ 335.0 |

Plus **0 unexpected collisions** over the cycle, and module A never inside the head's turning disc while it turns. Full
table: [`CAD_FC/motion/motion_report.txt`](../CAD_FC/motion/motion_report.txt).

**Watch:** the height margin is only **2.3 mm** (head carrier while turning at lift 75). Don't raise the head axis or the
turning lift without re-checking.

## Open rule questions (FAQ, not answered yet)
- **Q1: does a carried stone count in the perimeter?** Working assumption: **no**. The whole design depends on it: a carried
  320 mm stack would break the 1400 mm limit.
- **Q9: may a stone still held by the robot go above 350 mm inside a construction zone / the castle?** GR F.3 says
  manipulated objects ≤ 350 mm; G E.1 lets game elements exceed it in zones, actuators still ≤ 350 mm. While turning, the
  stack goes above 350 mm (the actuators stay ≤ 347.7). **Turning the stack in the castle is only legal if Q9 is "yes".**
  If it is "no", module B must turn the stack at a lower lift, or lay the boxes down differently.
