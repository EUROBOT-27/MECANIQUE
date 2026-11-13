# Status

_Last updated: 2026-11-13 (Seif)_

**Phase:** Strategy partly fixed → **clapets v7 module A: CAD passed (2026-11-13), now printing + testing**; module B (suction) reworked by Maatoug in v8. Hub shared by Seif, Maatoug and Ayoub (D-018, D-024).
**Next deadline:** Strategy chosen (internal), 2026-11-08 (**4 days overdue**) · Concepts chosen + prototypes tested 2026-11-22 (10 days) · CAD freeze 2026-12-13 (31 days) · Mechanical built and assembled, 2026-12-31 (49 days)
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
  out of date for the new features. Module B: Maatoug's **v8** (D-021, confirmed 2026-11-13 with a rework: simpler, standalone, pneumatics designed in),
  which must take v7's module A. A/B/C not dropped; the test decides.
- Parts library from the disassembled Ender 3 V2, lines still unverified (D-012).
- Software: simulation repo (ROS 2 Jazzy + Gazebo), clone separately into `eurobot2027/`. `software/` area exists.
- Earlier decisions: differential drive (D-004), LiDAR + vision (D-007), overhead station on the table (D-008), Aerobotix principles (D-006).

## Biggest risks right now
1. **Real stones not ordered.** Gripper prototypes (concepts due 2026-11-22) can't be tested without them, especially suction on cardboard.
2. **Clapets height margin 2.3 mm** (head at the top of its 75 mm lift) + rails/top tie at 366 mm in the prototype: the
   real-robot mount must keep the mechanism's height above the table and cut the profiles (top tie ≤ 350 mm).
3. **Perimeter budget:** only 200 mm of extra perimeter for all deployed parts; side-clamp jaws (~380 mm open) and the
   gate protrusion compete for it. Full robot layout not checked yet; FAQ Q1 (does a carried stone count?) unconfirmed.

## Waiting on
- Seif: module A print (clapets v7), order stones + foam balls, robot and roof layout sketches, refined
  timeline, confirmation of the D-008 location.
- Maatoug: back up personal files before the next pull; push the generators that only exist on his PC; carry v7's
  module A into v8; remove the ~470 software build files committed in `a746ea1`; fix the head servo posts; update v8's insert holes to D-025.
- Hamza Sammoud: PAMI size choice (4 or 6), qualifier/registration/poster dates.
- FAQ answers (Q1–Q9 not sent yet).
