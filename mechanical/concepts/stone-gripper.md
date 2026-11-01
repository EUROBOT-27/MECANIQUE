# Stone gripper (wall pick-up) — concepts

Status: **brainstorm** (Seif, 2026-10-26). Order: 1st (see `project/strategy.md` → Build order).
Job: take a full quarry stack (3 horizontal stones = a ready wall) and put it down in a wall zone.
Per the design principles: several concepts, cheap prototypes, tested on **real stones**, simplest reliable one wins.
Suction and non-suction concepts are both explored, in case suction turns out unreliable.

## Where the stacks are (from `Docs/table.svg`, mm)
- **8 quarries against the long borders**, stones along x: x 590–910, 1090–1410, 1590–1910, 2090–2410, at y 0–110 and y 1890–2000.
  One long face touches the border → reachable: the front long face, the two end faces (110 × 110 per stone),
  and the top. Gap between neighbouring quarries: 180 mm.
- **2 quarries in the centre**, stones along y: x 1445–1555, y 340–660 and 1340–1660. Free on all sides.
- Wall zones (drawn 390 × 190) are larger than a stone (320 × 110): about ±35 mm of slack along, ±40 mm across.

## Concepts

### A — Side clamp, no suction
The robot drives at the stack with its front face. A jaw on the left and on the right grips the stack by its end faces.
The robot then drags the wall to its zone without lifting it.
- A1: one jaw plate per side (2 actuators).
- A2: one servo per stone per side (6 servos per face), so each stone is gripped on its own.

### B — Suction on the front face
3 suction cups, one at the centre of each stone's front face (heights ~55 / 165 / 275 mm). Lift the stack a little
so it doesn't drag.

### C — A + B combined
For example, suction for holding and alignment, plus side jaws for carrying. Or suction alone for single-stone jobs and jaws for walls.

## Claude's notes (2026-10-26)
- **Stone tolerance (±5 mm on 320) vs. rigid jaws (A1):** a rigid plate only grips the longest stone, and the other two
  hang loose. A1 needs compliant pads (~10 mm foam or spring fingers). A2 solves this by design, at the cost of 12 servos for 2 faces.
- **A sets the robot width:** the jaws open past 320 + tolerance + clearance ≈ 340 mm inside, ~370–380 mm outside.
  Perimeter limits: ≤ 1200 mm at start, ≤ 1400 mm deployed [GR F.3]. Example that fits: jaws closed inward at start
  (body 300 × 300 = 1200), opening to 380 → 380 × 300 = 1360. If the stack is pulled into a **front pocket** inside
  the body, it sits inside the hull, and FAQ Q1 (does a carried stone count in the perimeter?) no longer matters.
  Two pockets (symmetric robot) leave little depth for the drive and battery → check in a layout sketch.
  If instead the jaws reach 110 mm forward outside the body, the hull grows by 110 mm in depth.
- **B doesn't constrain the width** (cups on a ~110 mm wide column), but the stack sits in front of the body → relies on the Q1 working assumption.
- **Cardboard is porous** (corrugated) → suction may leak. The ArUco sticker is smoother and may seal better.
  Test cup type (bellows vs. flat, foam lip) and pump flow on **real stones** early. Add a vacuum sensor so the
  robot knows it holds the stone (principle 8).
- **Lift height:** stack 330 mm + lift must stay ≤ 350 mm [GR F.3] → **lift ≤ 20 mm**. 5–10 mm is enough.
- **Dragging (A):** vinyl joints are imperfect [G D.1], so the bottom stone's edge can catch on a seam and tip the stack.
  Lifting 5–10 mm avoids it, also helps when turning with the stack. Worth testing both.
  With suction, dragging mostly loads the cups lightly (the floor carries the weight); pulling backwards puts them in tension.
- **Edge quarries:** for A, the jaws go into the 180 mm gaps between quarries, fine. For B, the robot only needs the front face.
- **Messy stacks:** stacks may be slightly offset or skewed, and the opponent may have taken stones (1–2 left).
  Both concepts should handle 1–3 stones and a few mm of misalignment. Funnel-shaped jaw entries help.

## Test plan (draft — fill targets in `design-principles.md`)
| Test | Target |
|---|---|
| Grip a full stack from an edge quarry, robot misaligned ±20 mm / ±5° | ≥ 19/20 |
| Carry 2 m incl. turns (drag vs. lift 5–10 mm), stack still aligned | ≥ 19/20 |
| Release in a wall zone, all 3 stones valid | ≥ 19/20 |
| Suction only: hold time on real cardboard, leak check | holds > 30 s |
| Partial stack (1 and 2 stones) | works |

## Open questions
- Which concept gets the robot's other face (pick + rotate for towers)? Do A and the flipper share hardware?
- Robot width from the drive layout (Pololu 4742 + JSUMO wheels) → do 380 mm jaws fit?
