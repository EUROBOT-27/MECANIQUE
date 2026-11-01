# Mechanical — context

Read the root `CLAUDE.md` and `project/rules-digest.md` for the full picture. This file holds what matters when
working on mechanical design.

## Team and tools
- CAD: Seif (lead), Ayoub, Baha, and Maatoug (fabrication CAD). **SolidWorks.**
- Maatoug's role here: take a mechanism design and make it **ready to fabricate**: printable parts (orientation, tolerances, inserts), laser-cut DXFs, profile cut lists, hole and fastener choices from `parts-library.md`.
- Manufacturing: 3D printing, laser cutting, aluminium profiles, rods (D-002). Fast turnaround.
- Electrical design: Hamza Bjaoui. Coordinate on battery, e-stop, wiring routes and board space early.
- SIMAs (knights): Hamza Sammoud — see `simas/CLAUDE.md`. Coordinate if the robot launches or carries them.

## Design standard
**Review every concept and CAD against `mechanical/design-principles.md`** (symmetry, printed zip-tie anchors,
the testing method, …) (D-006).

## Decided so far
- Differential drive, 2 × Pololu 4742 (37D) + JSUMO wheels (D-004). Omniwheels were rejected.
- Working assumption: a carried stone does **not** count in the robot perimeter (FAQ Q1, to confirm).
- Strategy: target every action, Grail at L4 on our roof (D-009). Build order: secure the sure points first, reserve CAD space for later mechanisms (D-010).

## Concepts in progress
- `concepts/stone-gripper.md`: wall pick-up, concepts A (side clamp), B (3 suction cups), C (both). Brainstorm 2026-10-26.
- `concepts/gate-lintel.md`: space to reserve for the gate (slot on a driving face shared with a stone gripper, D-011 + narrow protrusion for the perimeter budget), concepts compared. Mechanism not chosen.
- Launcher (flywheel, fixed angle), Grail lift variants: brainstorm in `project/strategy.md`.
- `concepts/clapets-redesign.md`: rethink of the clapets modules v1/v2 (quarry-stack grip + 15 mm lift, v2 adds a turning suction head) around our parts library. Proposal, 2026-10-27.

## Simulations and videos
**Every mechanism animation, motion study or simulation video is saved in `mechanical/simulations/`** (one
subfolder per study, listed in `simulations/INDEX.md`), even when the script that makes it lives elsewhere.

## Clapets (Maatoug's stack gripper, D-014 → D-017)
- **Clapets v5 = Maatoug's reference design (D-017); Seif is prototyping it as v7 (D-019, D-020), concepts A/B/C kept until the test.**
  Self-contained folder `mechanical/clapets-v5/`: FreeCAD generator scripts in `fc/` (relative paths), real servo model,
  CAD outputs in `CAD_FC/` (STEP, STL, DXF, FCStd), docs (build sheet, design history, decisions, rules, open points).
  Edit the design there.
- Earlier versions and other generators are still **only on Maatoug's PC** (`Mecanique/` folder: `module_clapets` v1,
  `module_clapets_v2`, `module_clapets_v4`, `module_clapets_poc`, SolidWorks C# API scripts in each `sw/` folder,
  `ANALYSE_mecanisme_*.md`, `simulation/`, `mecanisme1/`). To be added to the repo (`todo/maatoug.md`).
- `module_clapets_v3`, `base omniwheel 4/CAD/V2_280` (omni base): set aside (Maatoug, 2026-10-27).
- **Clapets v6 / v7 (Seif, D-019, D-020):** `mechanical/clapets-v6/` (v5 + real horn and servo wires), `mechanical/clapets-v7/` (**the version we print**: door units with M3 inserts Ø4.6 × 6.5, real Two Trees parts, every fastener + BOM, motor on the floor). Same workflow as v5 (`fc/v7_fc.py`, README). Real printer parts: `mechanical/resources/two-trees-bluer-v2-parts/` (the 2 GB download is local only, gitignored).
- Prompt-to-CAD helpers: `tools/` (FreeCAD + SolidWorks API).

## Sourcing (Tunisia)
Hardware is limited locally and imports take time. Design so parts can be swapped for what's available.
**Parts in hand: `mechanical/parts-library.md`** (D-012). Use what we own first, but the library is not a limit:
any part available in Tunisia is fine. For each part in a design, mark 📦 in library / 🇹🇳 local / ✈️ import.
Orders and purchases are still not tracked.
- Suction gripper plan (Maatoug, 2026-10-27): DP S30 cups in **TPU printed holders**, 12 V mini pumps (6 L/min).

## Test stones
The team's current test stones are **home-made and not exact**. Real ones (RAJA BLFA01 or equivalent) are being
bought from France, and shipping takes time. Until they arrive, design with clearance, and **re-test every stone
mechanism on real stones** once they arrive (size, stiffness and weight may differ).

## Deadline
**Built and assembled by 2026-12-31.** Proposed CAD freeze 2026-12-13 (see `project/timeline.md`).

## Hard constraints (check every design against these)

| Constraint | Value | Ref |
|---|---|---|
| Perimeter at start | ≤ 1200 mm (convex hull of vertical projection) | GR F.3 |
| Perimeter deployed | ≤ 1400 mm, at all times | GR F.3 |
| Height (robot + carried objects) | ≤ 350 mm at all times; e-stop ≤ 375 mm | GR F.3 |
| Start area | fit fully in 500 × 500 mm, **and leave room for the Grail** on the floor | G D.3, G E.2 |
| Beacon support | top at 430 ± 5 mm (make adjustable), within Ø200 of robot centre, ≥ Ø70 / ≤ 100 × 100, solid, opaque, Velcro hook top, holds 400 g, full between 350 mm and top | GR F.6 |
| Sticker area | 100 × 70 mm flat on one side face | GR F.6 |
| E-stop | red, Ø ≥ 20 mm, on top, reachable by a fist | GR F.4.c |
| Grail L4 | roof > 300 mm, with no actuator/fixing holding the Grail | G E.2 |
| Batteries | easy to swap (3 matches in a row + spares); LiPo needs fireproof bag → LiFePO4 or BMS packs are simpler | GR F.4.b |
| No loose parts | nothing may fall off | GR H.4 |

## Game elements to handle
- **Stone**: cardboard box 320 × 110 × 110 mm, ~90 g, tolerance ±4/±5 mm, deforms. Starts in quarries as stacks of 3 horizontal stones.
  - Wall = 3 horizontal (330 mm tall) · Tower = 1 vertical (320 mm) · Gate = 2 vertical + 1 horizontal on top (430 mm).
- **Grail**: our own object, > 60 mm cube, SIMA-like limits (FAQ Q3 open).
- **Cannonball**: 45 mm compressible foam ball, 10 per team.

## Known hard problems
1. **Gate lintel**: placing a stone on top of two 320 mm uprights while the actuator stays ≤ 350 mm.
2. **Carrying a 320 mm stone or a full quarry stack.** Assumed not to count in the perimeter (FAQ Q1), but it
   is still long and must be held securely. A single central suction cup will let it swing (see the Aerobotix note).
3. **Standing a stone upright** for towers and gate uprights.
4. **Robot + Grail in 500 × 500** at start.

## Working conventions
- Concepts and trade-offs: write them in this folder (e.g. `mechanical/concepts/<mechanism>.md`).
  Once chosen, log the choice in `project/decisions.md`.
- Before calling a design "done", run a rules check (perimeter at start/deployed, height in every pose, start-area fit, beacon support).
- Always use real dimensions from the rules; design with clearance for stone tolerances.
