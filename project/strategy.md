# Strategy

**Status (2026-10-25):** Seif shared the team's strategy brainstorm (see "Team strategy brainstorm" below).
Partly fixed (2026-10-26): direction = max points, every action, Grail L4 (D-009); build order (D-010).
The rest is still **work in progress**. Once something is chosen, it goes to `project/decisions.md`.

The rules themselves say: *"It is strongly recommended to design simple and reliable systems with a limited
number of actions"* [G C].

## Points available (one team, theoretical)

Zone counts are read from the table drawing (see `project/rules-digest.md` §2) — verify before relying on them.

| Action | How | Max points | Notes |
|---|---|---|---|
| Towers | 4 × (1 stone + 5) | 24 | stone must be stood upright (they start horizontal) |
| Gate | 3 stones + 20 | 23 | one per castle; hardest mechanism (lintel at 320–430 mm, actuator ≤ 350) |
| Walls | ~4 × (3 stones + 5) | ~32 | a quarry stack is already a wall |
| Grail | 5 + 4 levels × 5 | 25 | L4 = on the robot's roof (>300 mm) |
| Return home | completely in throne room | 10 | |
| SIMA moats | 3 moats × 5 | 15 | only from 85 s; SIMA design = Hamza Sammoud |
| SIMA attack | ≥1 SIMA touching an opposing SIMA | 5 | |
| Cannonballs | ≥3 in opposing courtyard | 20 | only from 85 s |
| **Total** | | **~154** | if everything works perfectly |

Extra stones placed in construction zones beyond the buildings also give 1 point each.

## Points per difficulty (first impressions — to discuss)

| Points | Effort | Notes |
|---|---|---|
| Return home (10) | low | needs reliable localisation, which is needed anyway |
| Grail present (5) | maybe zero | if it scores by staying in the throne room (FAQ Q2) |
| Cannonballs (20) | medium | a launcher on the robot; 15 s window; independent of stone handling |
| Walls (8 each) | medium | grab a whole quarry stack? (perimeter FAQ Q1) |
| Grail L4 (+20) | medium | combines with return home; roof > 300 mm |
| Towers (6 each) | medium-high | needs stone tilting to vertical |
| Gate (23) | high | lintel placement under the 350 mm actuator limit |
| SIMA (up to 20) | separate project | Hamza Sammoud |

## Team strategy brainstorm (Seif, 2026-10-25 — work in progress)

### Overall direction
- **Go for max points: build a mechanism for every action.** Walls (pick up), towers (pick up + flip upright),
  gate (incl. the lintel), Grail L4, cannonballs, return home, and SIMAs.
- Several mechanisms are explored as **competing variants that get tested**, and the best one is kept (Grail lift, SIMA types).

### Match plan
1. **Phase 1 (building):** the robot collects and places stones. Code is dynamic: it picks targets from the
   opponent's position and the stones it currently holds (software, out of scope here).
2. **Endgame:** the robot goes home (throne room), picks up the Grail and puts it on its roof (L4), then shoots
   the cannonballs **from the home position** during the attack phase (85–100 s).
3. All actuators off at 100 s, and the Grail resting free on the roof [GR H.3], [G E.2].

### Main robot mechanisms
- **Symmetric stone handling:** pick up walls (quarry stacks) and flip stones.
  - If the flipping mechanism is too bulky: **one face picks up a whole wall** (3-stone stack) and
    **the other face picks up + rotates** (towers, gate uprights).
- **Gate lintel:** a small separate hand with **suction** that extends from the top of the robot. It picks the top stone
  of a stack by its top face. While retracting, it rotates the stone 180° about its long (x) axis, so the cup ends up
  **under** the stone. It then sets the stone gently on the uprights and pulls out through the gap between them.
  **Needs more brainstorming** (Seif, 2026-10-26). Fallback if the flip doesn't work: lift the stone above 350 mm inside the castle (only the stone may go above
  350 mm; the hand must stay ≤ 350 mm [G E.1]).
  - **Variant "side-suction lift" (Seif, 2026-10-26):** a vertical bar with 3 suction cups, one per stone of a
    quarry stack, on a Z-lift. Only the top cup is turned on to take the top stone (bottom at 220 mm), then the
    lift raises it ~110 mm onto the uprights (bottom at ≥ 320 mm). Catch: a cup at the middle of the face sits at
    275 mm and would end at ~385 mm, which is illegal. The cups (and the top of the bar) must sit **at the bottom edge of
    each stone** (e.g. cup centre ~15 mm above the stone's bottom face) so the cup ends at ≤ 350 mm.
    Needs a flat/oval cup (≤ ~20 mm tall) or 2 small cups side by side, and a quick vacuum release.
    **Judged unreliable** (Seif, 2026-10-26): ~20 mm grip band on cardboard, with ±5 mm upright tolerance.
  - **Variant "fork" (Claude, 2026-10-26):** a flat fork ≤ ~90 mm wide carries the lintel from below, enters the gap
    between the uprights, lowers from ~325 to ~315 mm so the lintel rests on them, then pulls out. The actuator stays
    ≤ 325 mm. Needs uprights placed at the right spacing.
  - Both variants hold the lintel above 350 mm while the robot still has it: allowed only inside zones/castle, see FAQ
    Q9 in `rules-digest.md`.
- **Grail lift:** build and test several variants: electromagnet, gripper hand, simple elevator, etc.
- **Cannonball launcher:** shoots from the throne room at the end.

### SIMAs ("PAMI" in the team)
Three versions are built and tested thoroughly. The tests decide which ones go on the table, and how many:
1. **Basic PAMI:** just reaches its target position (opposing moat).
2. **Ejector PAMI:** carries 1 ball and ejects it into the opposing castle. If it works, **make 3** as a backup for the
   robot's launcher (3 balls = 5 + 15 pts).
3. **Attack PAMI:** touches an opposing SIMA.

### Claude's review (2026-10-25)
Rule checks, with references:
- **Lintel hand, height:** actuators ≤ 350 mm at all times [G E.1], [GR F.3]. A quarry stack's top face is at 330 mm,
  so a suction cup on the top face has **≤ 20 mm of headroom** (cup + hand). Tight. Picking the lintel from a lower
  stone, or by its side face, avoids this.
- **Lintel hand, placing:** the lintel ends at 320–430 mm, so the hand can only touch its lowest 30 mm.
  Holding it **by the bottom face** is the better option: if the two uprights stand at the lintel's ends, there is a
  ~100 mm gap between them (320 − 2 × 110). The hand can pull out through that gap at ≤ 320 mm.
  The lintel may only go above 350 mm **inside the construction zone** [G E.1], so carry it low and lift it at the gate.
- **Grail:** L4 requires the Grail to rest on the roof "free of any actuators and any fixing system", and a Grail still
  held by an actuator doesn't count [G E.2]. All actuators turn off at 100 s [GR H.3].
  → An electromagnet is fine only as a lifter that lets go and leaves the Grail resting on the roof. A permanent
  magnet = fixing system = no points. A passive recess on the roof is unclear (FAQ Q7).
- **Grail vs. beacons:** the Grail may exceed the height limit in the castle "without blocking any opposing beacons" [G E.2].
  The opponent's on-board beacon sits on our support at 430 mm. A Grail on the roof whose top passes 430 mm could block it
  (FAQ Q8). Safe design: Grail top ≤ 430 mm, so with the roof at 300 mm the Grail is ≤ 130 mm tall.
- **The Grail's 5 "present" points are free:** the castle courtyard includes the throne room ([G D.4], definitions),
  and the Grail starts there.
- **Shooting from home:** the ball must end with part of its projection in the opposing courtyard [G E.4], so foam balls
  must not bounce out. The opposing robot will also be parked in its throne room, which is part of that courtyard.
  Distances are in "Table measurements" below.
- **Ejector PAMI = double points:** a PAMI that sits in an opposing moat (5) and ejects its ball over a short distance
  into the courtyard scores both. 3 ejector PAMIs in 3 moats = 15 + 20 = 35 pts, more reliable than a long shot.
- **Stable capacity:** 2 stables of 200 × 300 mm (from the drawing). 3+ PAMIs (each > Ø80 mm, ≤ 600 mm perimeter at start)
  must fit, and they need a reach time of < 15 s from the corners to the opposing moats.

Scope concern (project chief): the rules recommend "simple and reliable systems with a limited number of actions" [G C].
Five mechanisms on one robot (gripper ×2 faces, flipper, lintel hand, Grail lift, launcher), plus Grail variants, must
reach CAD freeze on 2026-12-13. The roof is also crowded: Grail (L4), lintel hand, launcher, beacon support
(within Ø200 of the centre), e-stop and LiDAR all want the top of the robot. (2026-10-26: the gate mechanism moved to a
driving face, D-011, which frees roof space.)

### Build order: secure the points first (agreed with Seif, 2026-10-26)
**We do everything, but we secure the easy, big points first, then add the rest.** Later mechanisms get their space
reserved in the CAD from day one (method in `mechanical/design-principles.md`).

| Action | Max points | How hard | Points for the effort | Order |
|---|---|---|---|---|
| Grail in the castle | 5 | nothing to do (it starts there) | free | — |
| Return home | 10 | easy (needed anyway) | very good | **1st** |
| Walls (4 zones × 8) | 32 | medium (a quarry stack is already a wall) | very good | **1st** |
| Grail on the roof (L4) | +20 | medium | very good (35 with return home) | **1st** |
| Towers (4 × 6) | 24 | medium-hard (stone must be flipped upright) | good | **2nd** |
| Gate | 23 | hard (lintel at 320–430 mm) | ok, needs the flipper too | **3rd** |
| Cannonballs from the robot | 20 (≥ 3 balls) | medium (flywheel launcher) | ok, the ejector PAMIs can score the same | **3rd** |
| PAMIs in moats (3 × 5) | 15 | medium, separate team | good | in parallel |
| PAMI attack | 5 | medium, depends on the opponent having SIMAs | low | in parallel |

Extra stones in construction zones: +1 each. 1st order alone ≈ 67 pts; + 2nd ≈ 91; everything ≈ 154.
Decide the robot launcher after the ejector PAMI test. If the test isn't done before the CAD freeze, reserve the space.

## Table measurements (Claude, 2026-10-26)
**Exact values from `Docs/table.svg`** (its units are mm, viewBox 3000 × 2000), checked 2026-10-26.
Origin: the SVG's top-left corner. x along the 3 m side, y along the 2 m side. **Yellow castle at x = 0, blue at x = 3000.**
Written below from yellow's point of view; blue is the mirror image (x → 3000 − x).

| Item | Value (zone centre, or range) |
|---|---|
| Throne room, yellow / blue | x 6–495 / 2505–2995, y 755–1245 → centres (250, 1000) / (2750, 1000) |
| Wall zones (390 × 190 drawn), 5 per castle | yellow: (250, 400), (679, 571) 45°, **(850, 1000) central, facing the bridge**, (679, 1429) 45°, (250, 1600) |
| Tower zones (Ø190 drawn), 4 per castle | yellow: (500, 400), (850, 748), (850, 1246), (503, 1599) |
| Moats (390 × 190 drawn), 3 per castle | around blue: **(1950, 1000) bridge**, (2179, 429) 45°, (2179, 1571) 45° · around yellow: mirror |
| Stables (190 × 290 drawn, 200 × 300 with lines) | yellow: x 5–195, y 5–295 and y 1705–1995 · blue: x 2805–2995 |
| Opposing central rampart (blue) | x 2055–2245, y 805–1195 |
| Opposing courtyard on the centre line | x ≥ 2245 (incl. their throne room from x 2505) |

**Cannonball shot from our throne room:**
- Horizontal distance: **~2.0 m** to the near edge of the opposing courtyard, **~2.75 m** to the far border.
  The landing window on the centre line is ~750 mm deep, but their robot and Grail sit in the back ~500 mm of it.
- In the line of fire: **our own central rampart** at 0.5–0.7 m (a gate there is 430 mm tall) and the **opposing central rampart**
  at 1.8–2.0 m (a wall or gate, up to 430 mm). It has to be a **lob**, not a flat shot.
- Rough launch speed: ~4.7 m/s at 45° without drag for 2.25 m. Light foam balls have a lot of drag, so plan for **~6–8 m/s** and confirm by test.
- **Seif's concept (2026-10-26):** high-rpm motor(s) with discs (flywheel), **fixed angle**, since we always shoot from the
  same spot. Claude's notes:
  - Keep the angle fixed and **tune the range with the motor speed**. Use speed control (encoder or ESC with
    governor), because battery voltage drops during the match and changes the rpm, and so the range.
  - Position error is not a problem: a 2° heading error moves the ball ~80 mm sideways at 2.2 m, and the courtyard is much wider than that.
  - Compressible foam balls grip the discs well. They still need a feeder (hopper + servo gate) for 10 balls.
  - Sourcing: 775/550 DC motors are probably available locally. Small brushless drone motors + ESCs are a good
    option if they can be found locally.

**PAMI reach (stable → opposing moat):** path length ~2.1–2.3 m to the diagonal moats, ~2.4–2.6 m to the bridge moat. Our own
buildings on the ramparts will be in the way at 85 s, so the path goes around them.
At ~12 s of driving (keeping ~3 s for ejection), that's an average of **≥ 0.2 m/s**. Aim for **~0.35–0.4 m/s** cruise to leave margin for avoidance stops.

**Ejector PAMI geometry:** from an opposing moat, the courtyard is just behind the ramparts (~200–400 mm away), but the
opponent's buildings stand on those ramparts (walls 330 mm, towers 320 mm, gate 430 mm). The PAMI (≤ 175 mm) must
**lob the ball over ~350–450 mm** at short range. A spring or servo catapult is enough.

**Seif's fallback, "easy eject" (2026-10-26):** the PAMI opens a front door and the ball rolls into the castle through the gate.
- It fits the geometry: the central wall zone (x 2055–2245) faces the bridge moat (x 1855–2045), and a gate's lintel lies
  along that zone, so **the gate opening faces the bridge moat**. The ball has to roll ~200 mm across the zone to reach the courtyard (x ≥ 2245).
- The gap between the uprights is ≤ 100 mm (320 − 2 × 110, if the uprights stand at the lintel's ends). A 45 mm ball fits, but the PAMI must be aligned with it.
- **It depends on the opponent:** it works if they built a gate there or left the zone empty. A wall there blocks it.
  From the diagonal moats, the path is blocked if they built that diagonal wall.
- A foam ball on grippy vinyl loses speed fast. Release it from a small ramp (~100 mm drop gives ~1.4 m/s), and
  the PAMI can use its deployed size (700 mm perimeter) to extend the ramp closer to the zone.

## What the strategy must answer for the mechanical design (agreed agenda, 2026-10-25)
1. Which actions we target (walls, towers, gate, Grail level, cannonballs, return home).
2. How we take stones: one at a time, or a whole quarry stack of 3 (= a ready wall)?
3. Lying stones only, or standing ones too (towers, gate uprights → a tipping mechanism)?
4. How many stones the robot carries at once, and where it collects them.
5. Grail plan: what level, on our roof (L4)?
6. Cannonballs: launcher on the robot, SIMAs only (1 each), or both?
7. Start configuration: robot + Grail in the 500 × 500 throne room.

## Open strategic questions

- How many stones can we realistically handle in 100 s?
- Grab one stone at a time, or a whole quarry stack (3 stones)?
- Go for the gate or not?
- Cannonball launcher on the main robot: yes / no?
- Which quarries are "ours" in practice (closest, least contested)?
