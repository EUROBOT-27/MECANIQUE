# Status

_Last updated: 2026-11-10 (Seif)_

**Phase:** Strategy partly fixed → **clapets v7 module A ready to print** (tolerance tests first); module B (suction) reworked by Maatoug in v8. Hub shared by Seif and Maatoug (D-018).
**Next deadline:** Strategy chosen (internal), 2026-11-08 (**2 days overdue**) · Concepts chosen + prototypes tested 2026-11-22 (12 days) · CAD freeze 2026-12-13 (33 days) · Mechanical built and assembled, 2026-12-31 (51 days)
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
- Seif: tolerance coupon results (clapets v7), order stones + foam balls, robot and roof layout sketches, refined
  timeline, confirmation of the D-008 location, confirm/reject D-021.
- Maatoug: back up personal files before the next pull; push the generators that only exist on his PC; carry v7's
  module A into v8; remove the ~470 software build files committed in `a746ea1`; fix the head servo posts.
- Hamza Sammoud: PAMI size choice (4 or 6), qualifier/registration/poster dates.
- FAQ answers (Q1–Q9 not sent yet).
