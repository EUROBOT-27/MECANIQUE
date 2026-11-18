# TODO

Maatoug's tasks, plus follow-ups with other people. Updated at each `/wrap` (Maatoug's sessions).
Tasks for Seif go in `todo/seif.md`.
Format: `- [ ] task — owner — due YYYY-MM-DD (optional)`

## From Seif (2026-11-01)
- [ ] Add the generators that live only on your PC (`C:\Projects\EUROBOT\Mecanique\`: clapets v1/v2/v4/PoC, SolidWorks C# `sw/` scripts, `ANALYSE_mecanisme_*.md`) to the repo under `mechanical/`, with relative paths — Maatoug
- [ ] Check `tools/` (your helpers from `tmp/`, kept as examples) and `mechanical/resources/parts-photos/` (your `tmp/parts-img`) — Maatoug
- [ ] Review the clapets v5 status with Seif: stone gripper choice, D-016/D-017 (see `todo/seif.md`) — Maatoug, Seif
- [ ] Note: Seif owns `mechanical/clapets/clapets-v6/` and `clapets-v7/` for now (v5 untouched). v7 = the version we print (D-020); have a look at its README (fasteners, real printer parts, motor on the floor) — Maatoug
- [ ] Where did you download the Two Trees Bluer V2 model? Add the link to `mechanical/resources/two-trees-bluer-v2-parts/SOURCE.md` if Seif hasn't — Maatoug

## From Ayoub (2026-11-18)
- [ ] **New base `mechanical/base_330_js/` (proposal): laser-cut file `CAD/base_330_js.dxf`** (330 × 280, 5 mm,
  mm, R12, outline + holes on layer 0). Same size as base_330, made for the **JSUMO JS7444** wheels (well cut for
  Ø72–80 since the wheel isn't measured yet), **no MDF lift and no strap slots** (only the 8 hinge holes in the
  middle), and the CDR-2027 **AMT102-V** encoder on a sprung swing arm (4 × M3 per side for its bracket). Printed parts:
  `CAD/base_330_js_print.3mf` (ABS, one X1C plate). Please check the DXF is ready for laser cutting and the
  printed parts for fabrication (fits, inserts). Details: `mechanical/base_330_js/README.md` — Maatoug

## From Seif (2026-11-13)
- [ ] **D-021 confirmed (FYI):** your strike principle is kept. Seif reworks module B himself in a new folder
  `mechanical/suction-v1/` (simpler, reliable, works without the doors, pneumatics designed in; list in
  `project/decisions.md`, D-021). v8 stays as your reference: the v8 tasks below (carry module A in, D-025 holes,
  head servo posts) are no longer needed — Maatoug

## From Seif (2026-11-12)
- [ ] **Insert holes changed (D-025):** the Ø4.6 hole pushed plastic into the insert's thread in the ABS test. New
  reference: `mechanical/design-principles.md` (drawing `mechanical/img/heat_set_insert_hole.png`): our M3 inserts →
  **Ø5.4 × 7, mouth cone Ø6.2 × 1.5**. Clapets v8 still has Ø4.6 × 6.5: please update — Maatoug

## From Seif (2026-11-10)
- [ ] Your commit `a746ea1` added ~470 **software build outputs** (STM32 / micro-ROS `Debug/`, `.elf`, `.hex`, `.map`,
  a 7 MB `libmicroros.a`): build outputs usually stay out of git (`.gitignore`). Can you remove them from the repo? — Maatoug
- [ ] **Module A changed a lot in v7** since your v8 copy (door unit + cap rebuilt as option B, nuts instead of
  inserts, rod clamps, nut support, motor plate: `mechanical/clapets/clapets-v7/README.md`, 2026-11-08 → 11-10). Carry it
  into v8 (v8's module A = v7) — Maatoug
- [ ] Head servo posts (module B, `B_SUPPORT_TETE`): inserts have 0.9 mm walls; use the door unit's nut + roof +
  window fix. Head 20T: only 4.1 mm of face since the horn is 47.4 tall (`mechanical/clapets/clapets-v7/README.md`, 2026-11-09) — Maatoug

## Now (current focus)
- [ ] Add my own current tasks (software + CAD) to this list — Maatoug
- [ ] Count and measure the Ender 3 V2 parts, mark lines `verified` in `mechanical/parts-library.md` — Maatoug
- [ ] Add the other parts in hand to `mechanical/parts-library.md` — Maatoug

## Mechanical (fabrication CAD)
- [ ] Clapets v8 strike (D-021, proposed): show Seif `mechanical/clapets/clapets-v8/` and get it confirmed or folded into v7 — Maatoug, Seif
- [ ] v8: test-print a base bar (Ø8.0 rod press fit) + the carriage bushings (Ø8.3 slide) before the full print — Maatoug
- [ ] v8: tune the strike angle on real stones (press force vs attach reliability) — Maatoug
- [ ] Agree with Seif which mechanisms I turn into fabrication CAD, and the hand-off format (SolidWorks files, DXF, cut lists) — Maatoug, Seif
- [ ] Mechanical built and assembled — team — due 2026-12-31 (CAD freeze 2026-12-13)

## Software
- [ ] Choose the wireless link robot ↔ remote computing device (D-008) — Maatoug + software team
- [ ] CV ↔ software interfaces with Seif (data format, frames, rates) → `software/CLAUDE.md` — Maatoug, Seif

## Follow-ups with others
- [ ] Hamza Sammoud: PAMI size (4 or 6), qualifier/registration/poster dates — Hamza Sammoud
(Seif's open items are in `todo/seif.md`.)

## Backlog

## Done
- [x] Pulled the shared hub (main = origin/main 7979428); `claude-workspace/` kept on disk and now ignored; `core.longpaths` on; personal memory updated for D-018 — 2026-11-02
- [x] Parts library created (Ender 3 V2, unverified) → `mechanical/parts-library.md` (D-012) — 2026-10-27
- [x] Hub handed over to Maatoug, software in scope (D-013) — 2026-10-27 (replaced by the shared hub, D-018, 2026-11-01)
- [x] Git for the hub + how to version CAD files: repo EUROBOT-27/MECANIQUE, Git LFS (D-018, done by Seif) — 2026-11-01

## Grail lift (2026-11-10, Maatoug + Claude)
- [ ] Ask Baha for the 3 SolidWorks parts that stayed on his PC (`profilet 280mm ensi`, `support fixation es7i7`,
  `support en u extension lel bras`, + `Mini V Gantry Set` if used) -> drop them into `mechanical/grail-lift/sw/` - Maatoug
- [ ] Measure the steel U servo bracket (arm length, inner width, thickness) -> `G.L_U`, `G.T_U` in `grail-lift/fc/v2_fc.py`, re-run - Maatoug
- [ ] Show the v2 concept + `docs/CDC.md` (straight lift can't do L4) to Seif and Baha; needs from Seif: roof height, which face carries the lift - Maatoug, Seif
- [ ] Test the Gazebo model `excalibot_fc` (copied into eurobot2027/Simulation-Euro27/src/eb27_description/robots/): `./sim build`,
  set `model: excalibot_fc` in a scenario, command joints on /<ns>/<joint>/cmd. Commit the bridge change in
  `eb27_bringup/robot_config.py` (actuators) in the sim repo if it works - Maatoug
- [x] `python tools/install_hooks.py` done (2026-11-13). Auto-sync is now local only; publish with `python tools/sync_robot.py --push` - Maatoug
- [ ] Tell Seif: the robot auto-sync no longer pushes to Simulation-Euro27 by itself (local copy only, 2026-11-13); after
  pulling, run `python tools/install_hooks.py` once - Maatoug
- [ ] Tell Seif: clapets rails / T8 / top tie reach 381-391 mm in the robot (must be < 350, and < 300 where the Grail lands);
  beacon head (350-430) hits them too - Maatoug, Seif
- [ ] Measure the JSUMO wheels (74 or 77 mm? width 44?) -> robot/fc/layout.py - Maatoug
