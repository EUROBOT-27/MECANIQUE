# Status

_Last updated: 2026-11-13 (Seif, Ayoub)_

**Phase:** Strategy partly fixed → **clapets v7 module A: CAD passed (2026-11-13), now printing + testing**; module B (suction) reworked by Seif as `suction-v1` (D-021). Hub shared by Seif, Maatoug and Ayoub (D-018, D-024).
**Next deadline:** Strategy chosen (internal), 2026-11-08 (**5 days overdue**) · Concepts chosen + prototypes tested 2026-11-22 (9 days) · CAD freeze 2026-12-13 (30 days) · Mechanical built and assembled, 2026-12-31 (48 days)
**Qualifier:** end of March 2027

## Where we are
- **Strategy direction decided:** max points, every action, Grail at L4 on our roof (D-009). Build order: 1st walls,
  return home, Grail L4 · 2nd flipper (towers) · 3rd gate lintel, robot launcher; PAMIs in parallel (D-010).
- **Gate:** shares a driving face (front/back) with a stone gripper, no side face (D-011). Space to reserve and
  concepts in `mechanical/concepts/gate-lintel.md`. Mechanism not chosen.
- **Stone gripper:** concepts A (side clamp), B (suction), C (both) in `mechanical/concepts/stone-gripper.md` (Seif).
  In parallel, Maatoug designed **clapets v5** (`mechanical/clapets-v5/`, D-014 → D-017): doors + lift + a suction head
  that turns the 3-box stack. **First prototype = clapets v7** (`mechanical/clapets-v7/`, D-019, D-020, **D-022**):
  **ABS tolerance coupons done (2026-11-12)**: fits fixed in the CAD (pinion holes, servo nut recesses, ear openings,
  flat web), cap front tab + insert, teeth that lock the door units on the butterfly plate, nut pockets in the arm tabs,
  insert holes redesigned (D-025: Ø5.4 × 7 + cone); top crossbar without a 608 (lead screw through a Ø15 hole).
  **Module A passed CAD on 2026-11-13: printing in ABS (plates sliced), then assembly + test**; the assembly guide is
  out of date for the new features. Module B: D-021 confirmed 2026-11-13; Seif reworks it in `mechanical/suction-v1/` (simpler, works by
  suction alone without the doors, pneumatics + cables designed in; valves and pump placement still open); Maatoug's v8 stays as reference. A/B/C not dropped; the test decides.
- **Robot layout v1** (`mechanical/layout-v1/`, 2026-11-13, rough first pass): body 300 × 292 around the real v7 module; front = module A+B, back = mirror / Ayoub's flip6 / simple (not chosen), Grail right, launcher left. Start perimeter 1184 / 1172 / 1112, deployed worst 1352 / 1340 / 1282 (never both doors at once: 1491). Seif will refine it.
- Parts in hand added: KSM15-FL ball transfers, VS2-S30 cups, VW7-M5 connectors, 6 × 12 V vacuum pumps. Ayoub: `base_330` (330 × 280 temporary base, perimeter 1220 > 1200: not the final footprint) and `flip-6cups` concept (not reviewed).
- **Ayoub's new idea, not reviewed (2026-11-13):** `mechanical/concepts/central-hub-builder.md`: round Ø300 robot, central hub, 6 suction shafts (3 front, 3 rear) that rotate 90° to the side on elastics + micro-servo latches, then spin the stone upright (walls and towers, ~2 lifts + 6 micro servos). Open: height step, layout vs layout v1 (needs a round body and the robot centre), suction on cardboard, FAQ Q1, gate lintel. Not a decision.
- Parts library from the disassembled Ender 3 V2, lines still unverified (D-012).
- Software: simulation repo (ROS 2 Jazzy + Gazebo), clone separately into `eurobot2027/`. `software/` area exists.
- Earlier decisions: differential drive (D-004), LiDAR + vision (D-007), overhead station on the table (D-008), Aerobotix principles (D-006).

## Biggest risks right now
1. **Real stones not ordered.** Gripper prototypes (concepts due 2026-11-22) can't be tested without them, especially suction on cardboard.
2. **Clapets height margin 2.3 mm** (head at the top of its 75 mm lift) + rails/top tie at 366 mm in the prototype: the
   real-robot mount must keep the mechanism's height above the table and cut the profiles (top tie ≤ 350 mm).
3. **Perimeter budget:** layout v1 leaves 16 mm at start with a mirrored back (88 mm with a simple back) and 48 mm deployed; side-clamp jaws and the gate protrusion compete for it. FAQ Q1 (does a carried stone count?) unconfirmed.

## Waiting on
- Seif: module A print (clapets v7), order stones + foam balls, refine the layout + choose the back option, review Ayoub's flip-6cups and central-hub-builder (concepts due 2026-11-22), refined
  timeline, confirmation of the D-008 location, name of the GROSBOT 2023 club.
- Maatoug: back up personal files before the next pull; push the generators that only exist on his PC; remove the ~470 software build files committed in `a746ea1`. (v8 tasks dropped: Seif reworks module B in suction-v1.)
- Hamza Sammoud: PAMI size choice (4 or 6), qualifier/registration/poster dates.
- FAQ answers (Q1–Q9 not sent yet).
