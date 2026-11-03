# TODO

Maatoug's tasks, plus follow-ups with other people. Updated at each `/wrap` (Maatoug's sessions).
Tasks for Seif go in `todo/seif.md`.
Format: `- [ ] task — owner — due YYYY-MM-DD (optional)`

## From Seif (2026-11-01)
- [ ] Add the generators that live only on your PC (`C:\Projects\EUROBOT\Mecanique\`: clapets v1/v2/v4/PoC, SolidWorks C# `sw/` scripts, `ANALYSE_mecanisme_*.md`) to the repo under `mechanical/`, with relative paths — Maatoug
- [ ] Check `tools/` (your helpers from `tmp/`, kept as examples) and `mechanical/resources/parts-photos/` (your `tmp/parts-img`) — Maatoug
- [ ] Review the clapets v5 status with Seif: stone gripper choice, D-016/D-017 (see `todo/seif.md`) — Maatoug, Seif
- [ ] Note: Seif owns `mechanical/clapets-v6/` and `clapets-v7/` for now (v5 untouched). v7 = the version we print (D-020); have a look at its README (fasteners, real printer parts, motor on the floor) — Maatoug
- [ ] Where did you download the Two Trees Bluer V2 model? Add the link to `mechanical/resources/two-trees-bluer-v2-parts/SOURCE.md` if Seif hasn't — Maatoug

## Now (current focus)
- [ ] Add my own current tasks (software + CAD) to this list — Maatoug
- [ ] Count and measure the Ender 3 V2 parts, mark lines `verified` in `mechanical/parts-library.md` — Maatoug
- [ ] Add the other parts in hand to `mechanical/parts-library.md` — Maatoug

## Mechanical (fabrication CAD)
- [ ] Clapets v8 strike (D-021, proposed): show Seif `mechanical/clapets-v8/` and get it confirmed or folded into v7 — Maatoug, Seif
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
