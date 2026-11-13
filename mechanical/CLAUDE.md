# Mechanical — context

Read the root `CLAUDE.md` and `project/rules-digest.md` for the full picture. This file holds what matters when
working on mechanical design.

## Team and tools
- CAD: Seif (lead), Ayoub, Baha, and Maatoug (fabrication CAD). **SolidWorks.**
- Maatoug's role here: take a mechanism design and make it **ready to fabricate**: printable parts (orientation, tolerances, inserts), laser-cut DXFs, profile cut lists, hole and fastener choices from `parts-library.md`.
- Manufacturing: 3D printing, laser cutting, aluminium profiles, rods (D-002). Fast turnaround.
- **Print materials available: PLA and ABS only, no PETG** (Seif, 2026-11-10). The clapets CAD so far assumes PETG
  (densities, insert temperatures); the geometry does not depend on it. Plan (not a decision yet): PLA for tolerance
  tests + first prototype, ABS (or PETG if we get some) for robot parts. Details: `design-principles.md`, "Print materials".
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
- `concepts/aile-redesign/README.md`: clapets v7 door unit + cap rebuilt from scratch, 4 options (2026-11-10), not chosen yet.
- `concepts/clapets-redesign.md`: rethink of the clapets modules v1/v2 (quarry-stack grip + 15 mm lift, v2 adds a turning suction head) around our parts library. Proposal, 2026-10-27.

## Simulations and videos
**Every mechanism animation, motion study or simulation video is saved in `mechanical/simulations/`** (one
subfolder per study, listed in `simulations/INDEX.md`), even when the script that makes it lives elsewhere.

## Folder layout (2026-11-10)
One folder per mechanism: `clapets/` (all clapets versions, index in its README), `grail-lift/` (Grail lift),
`concepts/` (ideas not yet a mechanism), `simulations/` (all videos/GIFs), `resources/` (bought-part models, photos).
Nothing goes loose in `mechanical/` itself: a new SolidWorks file goes into its mechanism's `sw/` folder.

## Full robot (2026-11-10)
- `robot/`: the whole robot assembled by `fc/build_robot.py` from the current mechanism files; **all placement numbers in
  `robot/fc/layout.py`** (CDR-2027 style: drive in the middle, clapets front + back, Grail lift on a side). Writes
  `CAD_FC/ROBOT.FCStd`, `robot_report.txt` (perimeter, height, clashes between modules) and the Gazebo model
  `sim/excalibot_fc/`. Sync is automatic and **local only** (2026-11-13): at the end of each Claude turn where a mechanism
  file changed, a Stop hook rebuilds the robot and copies the model into the local sim clone (git post-commit and
  post-merge hooks do the same, `python tools/install_hooks.py` once per clone). **Nothing is pushed to GitHub
  automatically**: publish to Simulation-Euro27 with `python tools/sync_robot.py --push`. The robot uses the mechanism
  version named in `layout.py`; a generator change counts only once its FCStd is rewritten. Details: `robot/README.md`.
- A mechanism that needs the robot around it (e.g. Grail lift v3) reads `layout.py` too.

## Grail lift (2026-11-10)
- `grail-lift/`: **v1** = Baha's "essai mecanisme 1" (SolidWorks rack + pinion lift + servo-tilted electromagnet), files in
  `sw/` (3 custom parts still on Baha's PC → rebuilt approximately in FreeCAD); **v2** = concept that keeps the idea and
  makes L4 possible (coordinated lift + 180° flip over the roof edge, club steel U servo bracket, 4 V-wheels, NEMA17).
  Requirements: `grail-lift/docs/CDC.md` (key result: a straight lift cannot do L4 under 350 mm, CDC D1).
  Review of v1: `grail-lift/docs/REVIEW_v1.md`. Slider motion study: `grail-lift/fc/sliders_fc.py`. Not a decision yet.
- **v3 (2026-11-11) = the compact variant used in the full robot**: side face above the wheel, top grip, flip over the
  side edge, Grail set down through a roof slot (`grail-lift/fc/v3_fc.py`, reads `robot/fc/layout.py`).

## Clapets (Maatoug's stack gripper, D-014 → D-017)
- **Clapets v5 = Maatoug's reference design (D-017); Seif is prototyping it as v7 (D-019, D-020), concepts A/B/C kept until the test.**
  Self-contained folder `mechanical/clapets/clapets-v5/`: FreeCAD generator scripts in `fc/` (relative paths), real servo model,
  CAD outputs in `CAD_FC/` (STEP, STL, DXF, FCStd), docs (build sheet, design history, decisions, rules, open points).
  Edit the design there.
- Earlier versions and other generators are still **only on Maatoug's PC** (`Mecanique/` folder: `module_clapets` v1,
  `module_clapets_v2`, `module_clapets_v4`, `module_clapets_poc`, SolidWorks C# API scripts in each `sw/` folder,
  `ANALYSE_mecanisme_*.md`, `simulation/`, `mecanisme1/`). To be added to the repo (`todo/maatoug.md`).
- `module_clapets_v3`, `base omniwheel 4/CAD/V2_280` (omni base): set aside (Maatoug, 2026-10-27).
- **Clapets v6 / v7 (Seif, D-019, D-020, D-022):** `mechanical/clapets/clapets-v6/` (v5 + real horn and servo wires), `mechanical/clapets/clapets-v7/` (**the version we print**: door unit + cap rebuilt as option B (C-section spine, D-022), nuts in pockets instead of inserts except 4 M3 in the socle, real Two Trees parts, every fastener + BOM, sized for PLA; tolerance coupons in `tolerance-tests/`, assembly guide PDF in `assembly/`, status box at the top of its README). Same workflow as v5 (`fc/v7_fc.py`, README). Real printer parts: `mechanical/resources/two-trees-bluer-v2-parts/` (the 2 GB download is local only, gitignored).
- **Clapets v8 (Maatoug, D-021, proposed):** `mechanical/clapets/clapets-v8/` = v7 + a suction head that strikes 8 mm forward on its own (fixed base bars + sliding carriage on 2 Ø8 rods, 3rd MG996R, scotch yoke). Module A = v7 (v7's module A changed a lot on 2026-11-08 → 11-10: to be carried into v8).
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
