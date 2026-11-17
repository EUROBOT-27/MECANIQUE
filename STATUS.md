# Status

_Last updated: 2026-11-15 (Ayoub; Seif's 2026-11-14 content kept)_

**Phase:** Strategy partly fixed → **clapets v7 module A: CAD passed (2026-11-13), now printing + testing**; module B (suction) reworked by Seif as `suction-v1` (D-021). Hub shared by Seif, Maatoug and Ayoub (D-018, D-024).
**Next deadline:** Strategy chosen (internal), 2026-11-08 (**7 days overdue**) · Concepts chosen + prototypes tested 2026-11-22 (7 days) · CAD freeze 2026-12-13 (28 days) · Mechanical built and assembled, 2026-12-31 (46 days)
**Qualifier:** end of March 2027

## Where we are
- **Strategy direction decided:** max points, every action, Grail at L4 on our roof (D-009). Build order: 1st walls,
  return home, Grail L4 · 2nd flipper (towers) · 3rd gate lintel, robot launcher; PAMIs in parallel (D-010).
- **Gate:** shares a driving face (front/back) with a stone gripper, no side face (D-011). Space to reserve and
  concepts in `mechanical/concepts/gate-lintel.md`. Mechanism not chosen.
- **Stone gripper:** concepts A (side clamp), B (suction), C (both) in `mechanical/concepts/stone-gripper.md` (Seif).
  In parallel, Maatoug designed **clapets v5** (`mechanical/clapets/clapets-v5/`, D-014 → D-017): doors + lift + a suction head
  that turns the 3-box stack. **First prototype = clapets v7** (`mechanical/clapets/clapets-v7/`, D-019, D-020, **D-022**):
  **module A (lift + doors) is ready to print**: door unit + cap rebuilt (option B, C-section spine), nuts in pockets
  instead of inserts (only 4 M3 inserts left), sized for PLA, rest check + fast door sweep clean. **Next: print the
  tolerance coupons** (`tolerance-tests/`, ~150 g), update the fits, then module A (~600 g PLA) with the assembly guide
  (`assembly/clapets_v7_moduleA_assembly.pdf`). Module B: Maatoug's **v8** (D-021, proposed: cups strike 8 mm forward),
  which must take v7's module A. A/B/C not dropped; the test decides.
  In parallel, Maatoug designed **clapets v5** (`mechanical/clapets-v5/`, D-014 → D-017): doors + lift + a suction head
  that turns the 3-box stack. **First prototype = clapets v7** (`mechanical/clapets-v7/`, D-019, D-020, **D-022**):
  **ABS tolerance coupons done (2026-11-12)**: fits fixed in the CAD (pinion holes, servo nut recesses, ear openings,
  flat web), cap front tab + insert, teeth that lock the door units on the butterfly plate, nut pockets in the arm tabs,
  insert holes redesigned (D-025: Ø5.4 × 7 + cone); top crossbar without a 608 (lead screw through a Ø15 hole).
  **Module A passed CAD on 2026-11-13: printing in ABS (plates sliced), then assembly + test**; the assembly guide is
  out of date for the new features. Module B: D-021 confirmed 2026-11-13; Seif reworks it in `mechanical/suction-v1/` (simpler, works by
  suction alone without the doors, pneumatics + cables designed in; valves and pump placement still open); Maatoug's v8 stays as reference. A/B/C not dropped; the test decides.
- **Robot layout v1 refined** (`mechanical/layout-v1/`, 2026-11-13, proposal): v7 module on the floor (+26), 30 mm chamfers, 4 corner casters, front A+B or B only, back mirror / flip6 / simple. Start / deployed perimeter: A+B mirror 1114 / 1318, A+B simple 1042 / 1248, B only mirror 1060 / 1063. Open: choose front + back; A+B motors clash the socle by 4 mm; B only has 44 mm side bays; door sheets 366 at lift 75 and cups 26 mm too high go to the module B rework (Seif).
- Parts in hand added: KSM15-FL ball transfers, VS2-S30 cups, VW7-M5 connectors, 6 × 12 V vacuum pumps. Ayoub: `base_330` (330 × 280 temporary base, perimeter 1220 > 1200: not the final footprint) and `flip-6cups` concept (not reviewed).
- **Ayoub's new idea, not reviewed (2026-11-13):** `mechanical/concepts/central-hub-builder.md`: round Ø300 robot, central hub, 6 suction shafts (3 front, 3 rear) that rotate 90° to the side on elastics + micro-servo latches, then spin the stone upright (walls and towers, ~2 lifts + 6 micro servos). Open: height step, layout vs layout v1 (needs a round body and the robot centre), suction on cardboard, FAQ Q1, gate lintel. Not a decision.
  **2026-11-15: option A modelled in FreeCAD** (`mechanical/central-hub/`, proposal): hub in 4 printed segments S1–S4 on 3 × M4 tie rods, MG996R turn servos in cradles, one-piece arms + carriages, every fastener; joints and parts in `CONNECTIONS.md`, clash reports `hub_a_report.txt` / `hub_a_env_report.txt`, gif in `simulations/central_hub/`. The grooved-hub variant was dropped from the model (helix up to 77°, 118 clashes).
- Parts library from the disassembled Ender 3 V2, lines still unverified (D-012).
- Software: simulation repo (ROS 2 Jazzy + Gazebo), clone separately into `eurobot2027/`. `software/` area exists.
- Earlier decisions: differential drive (D-004), LiDAR + vision (D-007), overhead station on the table (D-008), **overhead camera = Pi Camera Module 3 Wide on a Pi, Ethernet to the laptop (D-026, `vision/camera-choice.md`)**, Aerobotix principles (D-006).

## Biggest risks right now
1. **Real stones not ordered.** Gripper prototypes (concepts due 2026-11-22) can't be tested without them, especially suction on cardboard.
2. **Clapets height margin 2.3 mm** (head at the top of its 75 mm lift) + rails/top tie at 366 mm in the prototype: the
   real-robot mount must keep the mechanism's height above the table and cut the profiles (top tie ≤ 350 mm).
3. **Perimeter budget:** layout v1 leaves 16 mm at start with a mirrored back (88 mm with a simple back) and 48 mm deployed; side-clamp jaws and the gate protrusion compete for it. FAQ Q1 (does a carried stone count?) unconfirmed.

## Waiting on
- Seif: buy the camera (D-026), module A print (clapets v7), order stones + foam balls, choose front/back of the refined layout, review Ayoub's flip-6cups and central-hub-builder + option A CAD (`mechanical/central-hub/CONNECTIONS.md`) (concepts due 2026-11-22), refined
  timeline, confirmation of the D-008 location, name of the GROSBOT 2023 club.
- Maatoug: back up personal files before the next pull; push the generators that only exist on his PC; remove the ~470 software build files committed in `a746ea1`. (v8 tasks dropped: Seif reworks module B in suction-v1.)
- Hamza Sammoud: PAMI size choice (4 or 6), qualifier/registration/poster dates.
- FAQ answers (Q1–Q9 not sent yet).
