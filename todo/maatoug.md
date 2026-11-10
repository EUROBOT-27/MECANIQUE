# TODO

Maatoug's tasks, plus follow-ups with other people. Updated at each `/wrap` (Maatoug's sessions).
Tasks for Seif go in `todo/seif.md`.
Format: `- [ ] task — owner — due YYYY-MM-DD (optional)`

## From Seif (2026-11-01)
- [ ] **Before your next pull:** back up your `claude-workspace/memory/` and `claude-workspace/tmp/` folders. They are no longer tracked (personal files, D-018), so the pull deletes them from your disk. Put them back after the pull; git ignores them from now on — Maatoug
- [ ] Before the pull, also run `git config --global core.longpaths true` (some resources paths are too long for Windows' default limit). If git complains during the pull, a fresh clone is simpler — Maatoug
- [ ] After the pull, update your personal memory: you share the hub with Seif (D-018); your TODO is `todo/maatoug.md`, logs are `logs/YYYY-MM-DD-maatoug.md` — Maatoug
- [ ] Add the generators that live only on your PC (`C:\Projects\EUROBOT\Mecanique\`: clapets v1/v2/v4/PoC, SolidWorks C# `sw/` scripts, `ANALYSE_mecanisme_*.md`) to the repo under `mechanical/`, with relative paths — Maatoug
- [ ] Check `tools/` (your helpers from `tmp/`, kept as examples) and `mechanical/resources/parts-photos/` (your `tmp/parts-img`) — Maatoug
- [ ] Review the clapets v5 status with Seif: stone gripper choice, D-016/D-017 (see `todo/seif.md`) — Maatoug, Seif
- [ ] Note: Seif owns `mechanical/clapets-v6/` and `clapets-v7/` for now (v5 untouched). v7 = the version we print (D-020); have a look at its README (fasteners, real printer parts, motor on the floor) — Maatoug
- [ ] Where did you download the Two Trees Bluer V2 model? Add the link to `mechanical/resources/two-trees-bluer-v2-parts/SOURCE.md` if Seif hasn't — Maatoug

## From Seif (2026-11-10)
- [ ] Your commit `a746ea1` added ~470 **software build outputs** (STM32 / micro-ROS `Debug/`, `.elf`, `.hex`, `.map`,
  a 7 MB `libmicroros.a`): build outputs usually stay out of git (`.gitignore`). Can you remove them from the repo? — Maatoug
- [ ] **Module A changed a lot in v7** since your v8 copy (door unit + cap rebuilt as option B, nuts instead of
  inserts, rod clamps, nut support, motor plate: `mechanical/clapets-v7/README.md`, 2026-11-08 → 11-10). Carry it
  into v8 (v8's module A = v7) — Maatoug
- [ ] Head servo posts (module B, `B_SUPPORT_TETE`): inserts have 0.9 mm walls; use the door unit's nut + roof +
  window fix. Head 20T: only 4.1 mm of face since the horn is 47.4 tall (`mechanical/clapets-v7/README.md`, 2026-11-09) — Maatoug

## Now (current focus)
- [ ] Add my own current tasks (software + CAD) to this list — Maatoug
- [ ] Count and measure the Ender 3 V2 parts, mark lines `verified` in `mechanical/parts-library.md` — Maatoug
- [ ] Add the other parts in hand to `mechanical/parts-library.md` — Maatoug

## Mechanical (fabrication CAD)
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
- [x] Parts library created (Ender 3 V2, unverified) → `mechanical/parts-library.md` (D-012) — 2026-10-27
- [x] Hub handed over to Maatoug, software in scope (D-013) — 2026-10-27 (replaced by the shared hub, D-018, 2026-11-01)
- [x] Git for the hub + how to version CAD files: repo EUROBOT-27/MECANIQUE, Git LFS (D-018, done by Seif) — 2026-11-01
