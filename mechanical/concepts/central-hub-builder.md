# Central hub builder — walls + towers from one mechanism

Status: **idea / concept** (Ayoub, 2026-11-13). Not reviewed by Seif, nothing decided, not in `project/decisions.md`.
To present before the "concepts chosen" milestone (2026-11-22). Alternative to compare with the clapets (v7/v8) and
`flip-6cups`, not a replacement.

Job: build **walls** (carry a quarry stack of 3) and **towers** (stand single stones up) with one mechanism, using
very few actuators. Gate uprights = 2 towers; the gate lintel is **not solved** by this concept.

## Drawings (claude.ai artifacts, private until shared from the page's Share menu)

| Drawing | What it shows |
|---|---|
| [Central hub builder](https://claude.ai/artifact/4nC2krv4sFwRzQjZnz7apr) | Top view of the chosen layout: hub, 90° rotation, sliders for angle / shaft length / robot shape, live checks (clearance, perimeter) |
| [Elastic swing module](https://claude.ai/artifact/JdyeWdhVgQyFQ1K5ufaokK) | Zoom on one shaft: elastic + latch servo, hinge slot, spin. Variants A (helix) and B (off-centre cup) |
| [Three-shaft stone builder](https://claude.ai/artifact/DjMuUc7KWJb29NhzSFCFP2) | Earlier version (rail + pivot at the front), kept for history |

## The idea

- **Round robot, Ø300.** A **cylindrical hub** stands at the robot's centre (vertical axis Z).
- **6 shafts** come out of the hub like spokes: **3 to the front, 3 to the rear**, one per stone of a quarry stack
  (stone centres at 55 / 165 / 275 mm). Each shaft has a **suction cup** at its tip on the stone's long face.
- Each shaft sits on **its own ring** on the hub (stacked turntables), so it rotates on its own.
- **Wall:** all shafts stay home, vacuum on, the base lift raises the stack ~10 mm (330 + lift ≤ 350 → lift ≤ 20 mm
  [GR F.3]), the robot carries it and sets it down.
- **Tower:** one shaft is released and **rotates 90° around the hub**: the front shafts turn to the **left**, the rear
  shafts to the **right** (same module turned 180°, point symmetry, principle of `../design-principles.md`). The stone
  ends lying along the middle of the side. It then goes to the **safe height** and **spins 90°** on the shaft axis: it
  stands up beside the robot. Lower the base, vent the cup: tower.
- **Drive of the rotation:** a stretched **elastic** per ring, held by a **micro servo latch**. The servo only opens the
  latch; the elastic does the swing. One shot per shaft per match, re-armed by hand during prep.
- 2 units × 3 stones = **6 standing stones = 4 towers + 2 gate uprights** (one castle's worth).

## Numbers (computed 2026-11-13, see the drawings)

### Why round, and why 90°
- Turning around the centre, the stone's inner face stays at a fixed radius. A rectangle's corners stick out past it:
  with base_330 (330 × 280) the stone hits the corner **at every angle**. A round Ø300 robot clears it.
- The top stone sits on the middle one. Seen from above it stays over the middle stone until a minimum angle; before
  that it can't go down or stand up without hitting it:

| Stone inner face from the hub axis | Rotation needed |
|---|---|
| **160 mm** (just outside Ø300) | **90°** ← chosen |
| 200 mm | 78° |
| 250 mm | 66° |
| 300 mm | 57° |

- **Chosen: 90° with short shafts (radius 160).** 90° is the exact minimum → set the end stop at **92–95°** for margin.
- After the spin, the stone stands 10–120 mm out from the robot's edge (centre 215 mm from the hub).

### Safe height
A standing stone is 320 tall: its centre must sit between **160 and 190 mm** (bottom ≥ table, top ≤ 350 [GR F.3]).

| Shaft | Stone centre (base +10) | Move to the safe height |
|---|---|---|
| Top | 285 | down 110 |
| Middle | 175 | none |
| Bottom | 65 | up 110 |

Two ways to do it (see the "Elastic swing module" drawing):
- **A — helical groove on the hub.** Must stay flat until the stone is clear of the stack (90°), then drop/climb
  110 mm. A steep step at the end of the rotation: risk of jamming.
- **B — off-centre cup.** Top cup 110 mm off the stone's centre (stone swings **down** when it spins), bottom cup
  110 mm off the other way (swings **up**), middle cup centred. No vertical slide at all. Order: bottom, middle, top.
  Peak height during the top spin: 349 mm with the base lowered first (tight). The bottom spin needs the base at +20.
  Off-centre load on the cup while rotating: 0.9 N × 110 mm (peel risk on cardboard).

### Perimeter [GR F.3]
- Round Ø300 robot alone: **942 mm** at start (limit 1200).
- With both stacks counted at start: **~1720 mm** → the concept depends on **FAQ Q1** (does a carried stone count?),
  like every concept that carries a stack outside the body.

## Actuators and parts

| Per unit (front or rear) | Count | Source |
|---|---|---|
| Base lift (walls, set-down) | 1 motor | NEMA 17 + T8 lead screw + Ø8 rods 📦 (Ender) |
| Latch servo per ring | 3 | MG90S 📦 |
| Spin per shaft | 3 springs + trips (or 3 servos) | torsion spring 🇹🇳 / MG90S 📦 |
| Vacuum per cup | 3 pumps (+ vent valves) | mini pumps 📦 (6 ordered) · 12 V valves 🇹🇳 probably |
| Elastic per ring | 3 | elastic / surgical tubing 🇹🇳 |

**Front + rear: 2 lifts + 6 micro servos + 6 pumps.** For comparison, a motor on every motion was ~14 motors.

## Open questions
1. **Height step:** helix (A) or off-centre cup (B)?
2. **Robot layout:** where do the drive wheels, battery and electronics go with the hub at the centre? Does a round
   Ø300 fit our drive (D-004)?
3. **Swing speed:** an elastic snaps fast; 90 g on the cup hitting a stop can peel it off. Damper or weak elastic?
4. **Release** after the spin without pulling the tower over (vent, then back off).
5. **Re-arming:** 6 rings by hand in the 3-minute prep [GR H.1]. Elastics must be captive (lost part = −20 [GR H.4]).
6. **Suction on cardboard:** untested, same risk as concept B in `stone-gripper.md`.
7. **Gate lintel:** not covered.
8. **Overlap with the plan:** D-010 / D-011 give one face to walls (clapets) and one to pick + rotate. This concept
   does both on both faces → Seif's call.

## First test (before any CAD)
One ring on a plywood board: elastic + MG90S latch + a cup on a short shaft, a home-made stone. Check: the cup holds
through the swing and the stop, the spin stands the stone up, and the stone stays up after venting and pulling away.
Redo on real stones (RAJA BLFA01) when they arrive.
