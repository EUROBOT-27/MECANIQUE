# Central hub builder — walls + towers from one mechanism

Status: **idea / concept** (Ayoub, 2026-11-13). Not reviewed by Seif, nothing decided, not in `project/decisions.md`.
To present before the "concepts chosen" milestone (2026-11-22). Alternative to compare with the clapets (v7) and
`flip-6cups`, not a replacement. Current version: **grooved hub on base_330** (below); the earlier round-robot study is
kept at the end for history.

Job: build **walls** (carry a quarry stack of 3) and **towers** (stand single stones up) with one mechanism and few
actuators. Gate uprights = 2 towers; the gate lintel is **not solved** by this concept.

## Drawings

| Drawing | What it shows |
|---|---|
| `../simulations/central_hub/hub_base330.gif` (script `../central-hub/hub_gif.py`) | Front + side view of the current version, both units, full sequence |
| [Hub on base_330](https://claude.ai/artifact/EP6EdH9eDqLXeaE7nQkgG6) (interactive, private until shared) | Same, step by step, live collision checks, "top first" order to see the failure |
| [Central hub builder](https://claude.ai/artifact/4nC2krv4sFwRzQjZnz7apr), [Elastic swing module](https://claude.ai/artifact/JdyeWdhVgQyFQ1K5ufaokK), [Three-shaft builder](https://claude.ai/artifact/DjMuUc7KWJb29NhzSFCFP2) | Earlier steps (round robot, elastic + latch, rail version) |

## Current version: grooved hub on base_330

Frame: X = wheel axis (robot's left = −X), Y = forward, Z = up, origin = robot centre on the table. mm. Base heights
include the 10 mm base lift (stack off the table).

- **Hub:** Ø100 vertical column at the robot centre. It stands on a **bridge** over the drive motors (base_330 has
  the 2 Pololu 37D back to back at the centre, x ±61.5, z 26.5–63.5): top plate 140 × 110 × 5 at z 68–73 on two walls
  at y ±50–55 (x ±70). 4.5 mm above the motors; clears the lift spacers (y ±24), strap slots (y ±25.5–29.5), couplers
  and wheels (wheels from x 84). Laser-cut.
- **6 shafts:** 3 to the front, 3 to the rear (one per stone of a quarry stack). Suction cup at the tip, stone face
  170 mm from the hub axis (a standing stone then clears the plate's side edge at x 165).
- **Grooves:** each shaft's **partial sleeve** (≤ a quarter of the hub) rides its own groove cut in the hub. Turning
  90° and reaching the height where the stone can spin is **one movement** (Ayoub's sketch). Then the shaft **spins the
  stone 90°** on its own axis: it stands up beside the robot. Lower the base, vent the cup: tower.
- **Rear unit = front unit turned 180°.** Front stones go to the robot's **left**, rear stones to its **right**. Front
  grooves use the hub from 0° to 90°, rear grooves from 180° to 270°: the two units' sleeves stay ≥ 90° apart.
- **Wall:** all shafts at home, vacuum on, base +10 mm (330 + 10 ≤ 350 [GR F.3]), carry, set down.

### Grooves (stone centre, base at +10)

| Groove | Stone centre | Shape over the 90° | Sleeve vs cup |
|---|---|---|---|
| Top | 285 → 180 | down 105, fast at the start, then level | sleeve 40 below the cup |
| Middle | 175 → 175 | level (plain rotation) | same height |
| Bottom | 65 → 170 | up 105, fast at the start (~25 mm in the first 7°) | sleeve 40 above the cup (clears the bridge) |

- **Spin-safe height:** while a stone spins on its centre, its corner sweeps √(160² + 55²) = **169 mm**. Its centre
  must be between **169 and 181 mm** during the spin (table ≤ bottom, top ≤ 350). The grooves end at 170 / 175 / 180.
  Standing heights 10–340 mm; peak 349 during the top spin (legal, tight).
- **Arm step:** each arm steps 40 mm at radius 100 (outside the bridge corners at r 89), so the 3 sleeves end 35 mm apart
  (210 / 175 / 140) and pass each other ≥ 47° apart.

### Firing order (inside each unit): middle → top → bottom
- **Middle first:** only turns, never changes height.
- **Top second:** the middle layer is empty, it goes down and stops 5 mm above the bottom stone.
- **Bottom last:** nothing above it; it rises fast so it is above the plate (z 18.5) before it reaches the plate corner.
- **Top first fails:** the top stone sits on the middle one and its groove goes down at once → it presses into the
  middle stone until ~86°.
- Checked every 2° for both units (stones vs stones, plate, bridge, arms; 350 limit): **no collisions**, without the
  base_330 back wall.

### What it needs from the robot
- **No back wall at the rear:** base_330's electronics back wall (MDF x ±130 at y −115…−120 + 2 profiles) belonged to
  another design. With it, all 3 rear arms and stones hit it.
- The front unit sweeps the **front-left** quarter, the rear unit the **rear-right** quarter, out to ~280 mm from the
  centre and up to 350: nothing else may stand there. The **front-right** and **rear-left** quarters stay free inside
  the robot (outside the wheels): electronics + LiPo can go there (two small boards).
- The hub top can continue up as the **beacon support** (top 430 ± 5, within Ø200 of the centre, Ø100 fits ≤ 100 × 100
  [GR F.6]).

### Possible bonus (to check with the rules-checker)
A front stone stands 225 mm left of the centre and a rear stone 225 mm right: 450 mm apart. Tower zones (850, 748) and
(850, 1246) are ~500 mm apart, and a stone counts if any part of its projection is in the zone [G E.1] → maybe 2 towers
in one stop.

## Option A (2026-11-14): rings + slides, no grooves, no elastics

Elastics dropped (Ayoub, 2026-11-14): a one-shot spring can't come back, so every move must be driven both ways.
The grooved hub was modelled first (`../central-hub/fc/hub_fc.py`, `hub_report.txt`) and **fails**: the top and bottom
grooves start at 77° (no single actuator can drive them: a turn jams on the steep start, a push on the flat end), and
the 3 sleeves of a unit collide where the grooves cross (118 clashes in the step check).

**Option A** (`../central-hub/fc/hub_a_fc.py` → `CAD_FC/HUB_A_*.FCStd`, `hub_a_report.txt`; views
`../simulations/central_hub/option_a_sheet.png`, animation `hub_option_a_sequence.gif` via `fc/anim_a.py`):
- **3 full rings** on the Ø100 hub (z 105 / 140 / 245), one per stack level, each in its own band: they only turn.
- **Each ring carries a front and a rear arm** (180° apart): one 90° turn places a front stone on the left and a rear
  stone on the right (2 towers per stop). Turn = 1 servo per ring, fixed in the free front-right quarter, pinion Ø63
  on the ring gear (180° servo → 90°).
- **Height:** top and bottom arms carry a vertical slide (rail + carriage, lead screw + N20 placeholder, 115 mm travel);
  the middle arm is fixed. Heights change only once the arm is turned out (alone at the side).
- **Spin:** one MG90S per arm on the carriage, radial axis, turns cup + stone 90°.
- **Layout rule found:** the 3 levels park at the same angle and turn the same way, so **seen from the side (radius ×
  height) their parts must never overlap** (whichever moves second would sweep into the other). Hence: top rail r 80–88,
  bottom rail r 102–110, middle arm goes out under the top rail, up between the rails, over the bottom rail (z 199).
- **Sequence:** unpinch (top +5, bottom −5, so the middle stone slides out freely) → middle: turn, spin, place, spin
  back, turn back → top: turn, down to 175, spin, place, back → bottom: turn, up to 175, spin, place, back.
- **Set-down:** the top and bottom slides lower their standing stone onto the table (centre 160) before venting; the
  middle arm has no slide, so its stone drops ~15 mm (needs the base lift or a short slide).
- **Check (167 steps, both units, every part):** no clashes; stones 0–345 mm, mechanism ≤ 329 mm [GR F.3].
- **Actuators (modelled 2026-11-14):** 3 turn MG996R 📦 **inside the hub bore** (one per ring; the pinion pokes through a
  window in the hub wall and meshes an internal gear cut in the ring bore, pitch r 26 / 52 → 180° servo = 90° ring;
  bottom + middle servos hang upside down above their pinion, top one below; rings now at z 90 / 140 / 245);
  4 slides = N20 gear motor 🇹🇳 + M4 lead screw 🇹🇳 beside each rail, nut block in the carriage; 6 spin MG90S 📦;
  6 pumps 📦 off the hub, hoses + wires down the Ø76 bore. 13 motors + 6 pumps, all reversible. The front-right
  quarter is free again (no outside turn drives).

**Connections, actuator table, collisions:** `../central-hub/CONNECTIONS.md` (2026-11-14, proposal). The model now
has the hub in 4 segments + 3 M4 tie rods, open windows and gear bands (assembly order), MG996R ears + printed cradles,
ring lugs, N20 clamps, couplers, bearings, limit switches and every fastener. No clashes in 167 steps. Against base_330
(`../central-hub/fc/check_env_a.py`) only the bottom slide hits the wheels: left open, a smaller wheel is planned.
The bottom carriage now rises +16 before its turn (its stones cleared the plate corner).

Open on option A: robot around it (base_330 wheels at x ±84–104 and the bottom slide motors at z 21–46 are in the
swept quarters; nothing may stand at r 56–170 in the front-left and rear-right quarters); front and rear of a level
always turn together (a stone not to place stays on its cup and comes back); rails are cantilevered (stiffness);
slide drive choice (N20 + M3/M4 screw 🇹🇳, or 360° servo + rack); hose routing through the Ø76 bore; turn gear detail.

## Option B (2026-11-17): one lift + one turret (paused 2026-11-18: holder cups grip off-centre, see OPTION_B.md)

Option A simplified (Ayoub asked for fewer actuators and a safer arm turn + spin): the 3 levels never work at once, so
**one carriage** on a fixed column (2 × Ø8 rods + T8, NEMA17) visits them in turn; **one turret** on it (MG996R, hard
stops, V-wheels) carries the front and rear arms; each arm spins its cup on a **bearing shaft** with an MG996R and hard
stops; **fixed holder cups** keep the stack. 4 motors instead of 13, every stone set on the table (no drop). Box check
`../central-hub/fc/check_b.py`: no clashes, ≤ 343 mm. Details, A vs B table, open points: `../central-hub/OPTION_B.md`.

## Actuators and parts

Not fixed yet. What moves: per shaft, the turn along the groove (1 actuator, or an elastic + latch servo, see the
"Elastic swing module" drawing) and the spin (servo, or spring + trip); per unit, the vacuum (1 pump per cup); one
base lift (lead screw) for the whole hub. Parts in hand: MG90S / MG996R 📦, 6 mini pumps 📦, VS2-S30 cups 📦,
T8 lead screw + NEMA 17 + Ø8 rods 📦; elastics, torsion springs 🇹🇳; 12 V valves 🇹🇳 probably.

## Open questions
1. **Drive of each shaft's turn:** motor, or elastic + latch (one shot per match, re-armed by hand in prep [GR H.1])?
2. **Sleeve + groove detail:** pin in a groove cut in a Ø100 printed or turned hub; partial sleeves stacked on one
   column; how much play before the cup misses the stone?
3. **Perimeter [GR F.3]:** base_330 is already 1220 at start (> 1200, temporary base); both stacks carried front and
   back → depends on FAQ Q1 (does a carried stone count?).
4. **Release** after the spin without pulling the tower over.
5. **Suction on cardboard:** untested (real stones not ordered yet).
6. **Gate lintel:** not covered.
7. **Overlap with the plan:** D-010 / D-011 give one face to walls (clapets) and one to pick + rotate; this does both
   on both faces → Seif's call.

## First test (before any CAD)
One shaft on a printed hub segment with its groove, a cup, a home-made stone: does the pin run smoothly along the
groove, does the cup hold through the turn and the spin, does the stone stay up after venting? Redo on real stones.

---

## History: round-robot version (earlier the same day)
Round Ø300 robot, hub at the centre, 6 shafts turning 90° on elastics + latch servos. Findings that still hold: turning
around the centre, a rectangle's corners stick out past the stones (on base_330 only the low plate corners matter,
handled by the bottom groove rising fast); the top stone stays over the middle one until ~90° at short radius
(160 → 90°, 200 → 78°, 250 → 66°, 300 → 57°); a straight helix starting at 0° collides unless the layer below is empty.
