# TODO

Seif's tasks, plus follow-ups with other people. Updated at each `/wrap` (Seif's sessions).
Tasks for Maatoug go in `todo/maatoug.md` under `From Seif`.
Format: `- [ ] task — owner — due YYYY-MM-DD (optional)`

## Now (current focus)
- [ ] **Fix the rest of the strategy** (gripper layout, launcher yes/no after PAMI test, PAMI count) → `project/decisions.md` — Seif — due 2026-11-08
- [ ] Choose the PAMI size with Hamza Sammoud: 4 × 140 × 160 mm or 6 × 90 × 185 mm (see `simas/CLAUDE.md`) — Seif, Hamza Sammoud
- [ ] Roof layout: first version in `mechanical/layout-v1/` (strip between the lifts, L4 Grail right end); refine — Seif
- [ ] Refine the internal milestones in `project/timeline.md` (CAD freeze etc.) — Seif
- [ ] **Order real stones from France** (RAJA BLFA01 or equivalent) — now blocks gripper tests — Seif — ASAP
- [ ] **Order 45 mm compressible foam balls** — Seif — ASAP
- [ ] Get JSUMO wheels — Seif
- [ ] Go through `mechanical/design-principles.md`: keep or drop the ◻ items — Seif
- [ ] Add the name of the French club behind GROSBOT 2023 to `resources/_notes/grosbot-2023.md` — Seif
- [ ] **suction-v1 concept** (`mechanical/suction-v1/`): decide valves vs pump-off, pumps on head vs fixed — Seif
- [ ] Review Ayoub's `flip-6cups` and `base_330` (base perimeter 1220 > 1200) — Seif
- [ ] Confirm D-008 location: the vision station = remote computing device platform (not a fixed beacon) — Seif

## Mechanical
- [ ] **Refine the robot layout** (`mechanical/layout-v1/`, v1 2026-11-13 = first rough pass: boxes around the real v7 module, Seif finds it too primitive); choose the back option (mirror / flip6 / simple) — Seif
- [ ] **Clapets v7 module A: print and test** — CAD passed 2026-11-13, now printing (plates sliced in `CAD_FC/STL/PRINT.3mf`) (`mechanical/clapets-v7/`, D-022; module B in parallel in Maatoug's v8) — Seif
  2. Print module A in **ABS** (~510 g, 40 % infill, parts regenerated 2026-11-12), assemble, test. The assembly guide
     is out of date for the cap tab, the plate teeth and the arm nut pockets: regenerate it (ask Claude) or follow the README
     - Set the inserts with the new holes (D-025): let them sink under the iron's weight
     - Mount each door unit: push it outward in its M4 slots until the plate teeth touch, then tighten
  3. Door sheet foam pads: none in hand (CAD keeps 8 mm); get some or decide another pad
  4. Optional: FEM check of the new door unit (gear force ~90 N + door squeeze)
- [ ] Decide: "PLA for tests / prototype, ABS (or PETG) for robot parts" → log it as a decision or not — Seif
- [ ] Add the GrabCAD link of the Two Trees Bluer V2 model to `mechanical/resources/two-trees-bluer-v2-parts/SOURCE.md` — Seif
- [ ] Robot layout: chassis floor height vs the module (z 0 = table in the clapets CAD; floor must stay < z 27; cut profiles, top tie ≤ 350) — Seif
- [ ] Prototype and test stone gripper concepts A (side clamp) and B (suction) → `mechanical/concepts/stone-gripper.md` — Seif, Ayoub, Baha — due 2026-11-22
- [ ] Robot layout sketch: drive base vs. ~380 mm open jaws (concept A), pockets, perimeter at start / deployed, **shared gate slot on face A or B** (D-011, `mechanical/concepts/gate-lintel.md`) — Seif
- [ ] Concepts for the second face: single-stone pick + flip (towers, gate uprights) — Seif, Ayoub, Baha
- [ ] List candidate concepts for Grail lift (electromagnet, hand, elevator…) and the flywheel launcher — Seif, Ayoub, Baha
- [ ] Gate lintel: low priority (3rd, D-010). Open point: how the lintel gets onto a fork/shelf → `mechanical/concepts/gate-lintel.md` — Seif
- [ ] Hand test of the fork / shelf lintel placement with 3 real stones + scrap plywood (after real stones arrive) — Seif
- [ ] Sketch the start configuration: robot + Grail inside 500 × 500 mm — Seif
- [ ] Define the test targets (table in `design-principles.md`) once the mechanisms are known — Seif

## Vision (parked until vision tasks start — mechanical first)
- [ ] Opponent tracking concept, LiDAR + vision (D-007, D-008): camera choice, how LiDAR and vision combine, LiDAR mounting height, opponent SIMAs — Seif
- [ ] Read the table ArUco IDs from `Docs/table.svg` → `vision/CLAUDE.md` — Seif

## SIMAs
- [ ] Get Hamza Sammoud's current SIMA ideas and plan → `simas/CLAUDE.md` — Seif
- [ ] Plan the 3 PAMI versions (basic, ejector, attack) and their tests with Hamza Sammoud. Ejector result needed before CAD freeze 2026-12-13 — Seif, Hamza Sammoud
- [ ] Decide ArUco tags on our SIMAs (IDs > 90 suggested) — Seif, Hamza Sammoud

## From Ayoub
- [ ] **Review Ayoub's new idea: grooved central hub on base_330** (walls + towers from one mechanism, 6 suction shafts, front stones → left, rear → right). Concept: `mechanical/concepts/central-hub-builder.md`; GIF: `mechanical/simulations/central_hub/hub_base330.gif`. Keep / drop / test? It competes with clapets v7 for the faces (D-010, D-011) and needs base_330's back wall gone — Seif — before 2026-11-22

## Follow-ups with others
- [x] Confirmed D-021 with a module B rework (simpler, standalone, pneumatics designed in) — 2026-11-13
- [ ] **Review Maatoug's clapets work (D-014 → D-017)**: v5 is being printed and tested as v7 (D-019, D-020); A/B/C not dropped, the real test decides. Close this after the test — Seif, Maatoug — before 2026-11-22
- [ ] Confirm D-012 (parts library, logged as "Decided by: Seif" on 2026-10-27) — Seif
- [ ] Tell Maatoug about the shared hub (D-018) and the steps before his next pull (see `todo/maatoug.md`) — Seif — 2026-11-01
- [ ] Send the open FAQ questions (Q1–Q9 in `project/rules-digest.md`) to the Eurobot FAQ / referees. Q1 (perimeter) first — Seif
- [ ] Ask Hamza Sammoud for the exact qualifier date, registration deadline and poster deadline — Seif
- [ ] Tell Hamza Bjaoui the battery rules (LiPo bag vs. LiFePO4 / BMS packs) before the battery is chosen — Seif
- [ ] Ask the previous IEEE team: did overhead vision run in the 2026 matches (camera, computer, mount)? Is there a CAD of the 2026 main robot? What were their top problems at the final? — Seif
- [ ] Point Maatoug to `INSATEURO2026/Navigation/docs`, Hamza Bjaoui to `Electrique/`, Hamza Sammoud to `Pami/specification.md` — Seif

## Backlog
- [ ] Discuss CV ↔ software interfaces with Maatoug (data format, frames, rates, wireless link) — Seif
- [ ] Add a `/weekly` review command once the daily routine is working — Seif

## Done
- [x] Clapets v7 module A CAD passed (README, STATUS), effort estimate ~45–65 h logged — 2026-11-13
- [x] D-021 confirmed with rework; `mechanical/suction-v1/` created — 2026-11-13
- [x] Parts photos + library (KSM15-FL, VS2-S30, VW7-M5, vacuum pumps); Barbatronic chassis + GROSBOT 2023 notes — 2026-11-13
- [x] Robot layout v1 (rough) `mechanical/layout-v1/` — 2026-11-13
- [x] Confirmed D-024 (Ayoub joins the hub) — 2026-11-12
- [x] ABS tolerance coupons printed + checked; clapets v7 fixes (pinion holes, servo nut recess, ear openings, flat web, cap front tab + insert, plate form-lock teeth, arm nut pockets); insert holes redesigned (D-025) — 2026-11-12
- [x] Clapets v7 module A ready to print: caliper values, insert holes + walls, nuts instead of inserts, rod clamps, door unit + cap rebuilt (option B, D-022), PLA sizing, no M4 inserts / no pad, tolerance coupons, assembly guide PDF, fast door sweep + GIFs — 2026-11-10
- [x] Tolerance check of every nut / screw / insert (fastener check + insert views) — 2026-11-10
- [x] Motion video of v7 → `mechanical/simulations/clapets_v7/` (door GIF + module A cycle GIF) — 2026-11-10
- [x] Full-cycle check of clapets v7: no real collision, deployed ≤ 1367.3 mm — 2026-11-01
- [x] Clapets v6 (real horn + wires) and v7 (door units reworked, real Two Trees parts, all fasteners + BOM, motor on the floor) → `mechanical/clapets/clapets-v6/`, `mechanical/clapets/clapets-v7/` (D-019, D-020) — 2026-11-01
- [x] Real Two Trees Bluer V2 parts extracted → `mechanical/resources/two-trees-bluer-v2-parts/` — 2026-11-01
- [x] Claude removed from GitHub contributors; attribution off in `.claude/settings.json` — 2026-11-01
- [x] Shared hub: merged Seif's and Maatoug's copies into the git repo EUROBOT-27/MECANIQUE, Git LFS for CAD/images, per-person TODO and logs (D-018) — 2026-11-01
- [x] Gate space reservation + concepts → `mechanical/concepts/gate-lintel.md`; gate shares a driving face (D-011) — 2026-10-26
- [x] Table zones measured from `table.svg` (shot distance, PAMI paths, quarries) → `project/strategy.md` — 2026-10-26
- [x] PAMI size envelope (4 × 140 × 160 or 6 × 90 × 185 mm) → `simas/CLAUDE.md` — 2026-10-26
- [x] Stone gripper concepts listed → `mechanical/concepts/stone-gripper.md` — 2026-10-26
- [x] Strategy direction logged (D-009) and build order agreed (D-010) — 2026-10-26
- [x] Shared the team's strategy brainstorm → `project/strategy.md` — 2026-10-25
- [x] Project hub set up: structure, rules digest, `/start` + `/wrap` — 2026-10-25
- [x] Cloned the Aerobotix 2026 repos; studied their teardown + PPP → `resources/_notes/aerobotix-2026-robot.md` — 2026-10-25
- [x] Drive decided: differential, Pololu 4742 + JSUMO (D-004) — 2026-10-25
- [x] Lextronic order placed (7" display, 6 mini air pumps, 2 × Pololu 4742), arriving ~2026-10-28 — 2026-10-25
- [x] First resources added and indexed (Aerobotix 2026, INSATEURO2026) — 2026-10-25
- [x] Cloned + studied all 17 INSATEURO2026 repos → `resources/_notes/insateuro2026.md` — 2026-10-25
- [x] Opponent tracking decided: LiDAR + vision (D-007); overhead station on the table (D-008) — 2026-10-25
