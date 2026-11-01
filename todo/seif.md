# TODO

Seif's tasks, plus follow-ups with other people. Updated at each `/wrap` (Seif's sessions).
Tasks for Maatoug go in `todo/maatoug.md` under `From Seif`.
Format: `- [ ] task — owner — due YYYY-MM-DD (optional)`

## Now (current focus)
- [ ] **Fix the rest of the strategy** (gripper layout, launcher yes/no after PAMI test, PAMI count) → `project/decisions.md` — Seif — due 2026-11-08
- [ ] Choose the PAMI size with Hamza Sammoud: 4 × 140 × 160 mm or 6 × 90 × 185 mm (see `simas/CLAUDE.md`) — Seif, Hamza Sammoud
- [ ] Draw the roof layout sketch (beacon support, e-stop, Grail spot, launcher; the gate is on a driving face now, D-011) — Seif
- [ ] Refine the internal milestones in `project/timeline.md` (CAD freeze etc.) — Seif
- [ ] **Order real stones from France** (RAJA BLFA01 or equivalent) — now blocks gripper tests — Seif — ASAP
- [ ] **Order 45 mm compressible foam balls** — Seif — ASAP
- [ ] Get JSUMO wheels — Seif
- [ ] Go through `mechanical/design-principles.md`: keep or drop the ◻ items — Seif
- [ ] Confirm D-008 location: the vision station = remote computing device platform (not a fixed beacon) — Seif

## Mechanical
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

## Follow-ups with others
- [ ] **Review Maatoug's clapets work (D-014 → D-017, `mechanical/clapets-v5/`)**: v5 is a full stack gripper (doors + lift + turning suction head). Accept it as our stone gripper, or keep it `proposed` next to concepts A/B/C (`mechanical/concepts/stone-gripper.md`) — Seif, Maatoug — before 2026-11-22
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
