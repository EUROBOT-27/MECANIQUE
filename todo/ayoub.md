# TODO

Ayoub's tasks (CAD team, SolidWorks), plus follow-ups with other people. Updated at each `/wrap` (Ayoub's sessions).
Tasks for Seif go in `todo/seif.md`, for Maatoug in `todo/maatoug.md`.
Format: `- [ ] task — owner — due YYYY-MM-DD (optional)`

## From Seif (copied from `todo/seif.md`)
- [ ] Prototype and test stone gripper concepts A (side clamp) and B (suction) → `mechanical/concepts/stone-gripper.md` — Seif, Ayoub, Baha — due 2026-11-22
- [ ] Concepts for the second face: single-stone pick + flip (towers, gate uprights) — Seif, Ayoub, Baha (my candidates: `flip-6cups`, `central-hub-builder`)
- [ ] List candidate concepts for Grail lift (electromagnet, hand, elevator…) and the flywheel launcher — Seif, Ayoub, Baha

## Now (current focus)
- [ ] Plywood test of one ring (elastic + MG90S latch + cup + home-made stone): holds through swing and stop? stone stands after venting? — Ayoub — due 2026-11-22
- [ ] Review `mechanical/central-hub/CONNECTIONS.md` + option A CAD + `OPTION_B.md` (option A clashes fixed 2026-11-15; reports clean) — Ayoub — due 2026-11-22
- [ ] Central hub: **option C** (`central-hub/OPTION_C.md`) and **option D** (`central-hub/option-d/`, FreeCAD model + `option_d_freecad.gif`) solve the holder-cup problem of B. Option E (doubled, `central-hub/option-e/`, start perimeter 1176 OK) is the newest. Pick B / C / D / E — Ayoub — due 2026-11-22
- [ ] Option D, if kept: ring spacing (rings touch, add washer / 1 mm shoulder), choose the N20 gearbox + test torque, agree 6 DC channels with encoders with Hamza Bjaoui, print test of ring + pinion in ABS — Ayoub
- [ ] Add FAQ question "may the robot drag a quarry stack on the table?" to `project/rules-digest.md` — Ayoub
- [ ] Check the hub against `mechanical/layout-v1/` (round Ø300 body, wheels, battery, electronics around the hub) — Ayoub
- [ ] Decide the height step: helix groove (A) or off-centre cups (B) — Ayoub
- [ ] Gate lintel: still no mechanism (not covered by the hub) — Ayoub, Seif, Baha

- [ ] Ask Seif / Hamza Sammoud to send FAQ questions (Q1 first: does a carried stone count in the perimeter?) — Ayoub

## Done
- [x] Central hub option E (doubled): box check, FreeCAD model + poses, `option_e_freecad.gif`, pushed — 2026-11-19
- [x] Option D GIF rendered from the FreeCAD solids (`option-d/fc/hub_d_gif.py` → `simulations/central_hub/option_d_freecad.gif`) — 2026-11-19
- [x] Central hub option C (box check) and option D (one N20 + ring per stone, motors inside a hollow spine): `option-d/` with box check, FreeCAD poses, report, README, sheet + gif — 2026-11-18
- [x] Central hub: option A clash fix + new animation + PDF brief; option B concept + box check; Idea 1 / Idea 2 studied; interactive comparison page — 2026-11-15/18
- [x] Central hub option A: FreeCAD model (4 segments, arms, servos, all fasteners), `CONNECTIONS.md`, collision reports, sequence gif — 2026-11-14/15
- [x] Wrote the central hub builder concept (`mechanical/concepts/central-hub-builder.md`) — 2026-11-13
- [x] `base_330` back wall + assembly, `flip-6cups` concept CAD + kinematics — 2026-11-12
