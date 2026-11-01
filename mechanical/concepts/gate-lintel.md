# Gate lintel — space reservation and concepts

Status: **mechanism not chosen** (gate is 3rd in the build order, D-010). Shares a driving face with a stone gripper, no side face (D-011). This file fixes the space to reserve in the
robot layout so the gate stays possible later. Brainstorm history: `project/strategy.md` → "Gate lintel".

## The problem
The lintel ends at 320–430 mm (uprights 320 ± 5 mm). Actuators must stay ≤ 350 mm at all times [G E.1], [GR F.3].
Anything gripping the lintel's sides only has the bottom ~30 mm band (320–350). Grip-based methods are fragile there,
so the preferred direction is **gravity-held**: the lintel rests on a support (fork/shelf) and is set down, not released
from a grip.

## Space to reserve (any concept) — Claude, 2026-10-26

| Item | Size | Why |
|---|---|---|
| Lintel envelope | 320 × 110 × 110 mm, long side parallel to a robot face | |
| Vertical travel | ~100–110 mm (lintel bottom from ~220–240 to ~325–330) | Outside zones the stone's top must stay ≤ 350 mm, so carry low, lift at the gate |
| Support under the lintel | ~8–10 mm plate or one fork tine ≤ 90 mm wide | Gap between uprights ≈ 100 mm (320 − 2 × 110) |
| Lift guide + drive | 1–2 columns ~40 × 40 mm, up to 350 mm tall | 8 mm rods + LM8UU + belt/lead screw: local (3D-printer parts). MGN12 rails: likely import |
| Horizontal reach | lintel ends ~110–120 mm **outside** the robot edge | The uprights stand on the floor in front of the robot |

**Reserve on one face: a slot ≈ 340 wide × 130 deep × full height (to 350 mm), plus the lift columns at the sides.**
This is nearly the same envelope as the stack-gripper bay (`stone-gripper.md`). Either share that face (saves space,
must be designed together) or use a separate face (simpler, costs a whole face).

### Perimeter budget (the hidden cost)
Start ≤ 1200 mm, deployed ≤ 1400 mm [GR F.3] → **200 mm** of extra perimeter shared by all deployed parts.
On a 300 × 300 base:
- Full-width tray (320 wide) sticking out 120 mm → about **+240 mm**. Over budget.
- One central tine (80 wide) sticking out 120 mm → about **+105 mm**. Fits, assuming the carried stone does not count (FAQ Q1).

→ **What sticks out at the gate must be narrow.**

## Concepts

| Concept | Idea | Status |
|---|---|---|
| Flip hand (Seif) | Suction on the top face, flip 180° so the cup ends under the stone, set down, pull out through the gap | Needs brainstorming; see `project/strategy.md` |
| Side-suction lift (Seif) | 3 cups on a Z-bar, top cup takes the top stone and lifts it ~110 mm | **Judged unreliable** (Seif, 2026-10-26): ~20 mm grip band on cardboard, ±5 mm uprights |
| Fork from below (Claude) | Lintel on a fork, fork enters the gap between uprights, lowers until the lintel rests, pulls out. Fork top ≤ ~330 mm | Open. Unsolved: how the lintel gets onto the fork |
| Shelf + pusher (Claude) | Lintel on a shelf level with the upright tops; robot docks, pusher slides it across (touches at 325–345 mm) | Open. Same loading problem as the fork |

## Open points
- **Loading** the lintel onto a fork/shelf from a quarry stack (side jaws lift the top stone, support slides under = an extra axis?).
- FAQ **Q9** (`project/rules-digest.md`): may a stone still held by the robot go above 350 mm inside a zone?
- Cheap hand test before any CAD: 3 stones + scrap plywood: does a lintel set from a fork/shelf land straight on the uprights?
