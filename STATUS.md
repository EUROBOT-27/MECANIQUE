# Status

_Last updated: 2026-11-01, evening (Seif)_

**Phase:** Strategy partly fixed → mechanical concepts + first gripper prototype (clapets v7) being finalised for printing. Hub shared by Seif and Maatoug (D-018).
**Next deadline:** Strategy chosen (internal), 2026-11-08 (7 days) · Concepts chosen + prototypes tested 2026-11-22 (21 days) · CAD freeze 2026-12-13 (42 days) · Mechanical built and assembled, 2026-12-31 (60 days)
**Qualifier:** end of March 2027

## Where we are
- **Strategy direction decided:** max points, every action, Grail at L4 on our roof (D-009). Build order: 1st walls,
  return home, Grail L4 · 2nd flipper (towers) · 3rd gate lintel, robot launcher; PAMIs in parallel (D-010).
- **Gate:** shares a driving face (front/back) with a stone gripper, no side face (D-011). Space to reserve and
  concepts in `mechanical/concepts/gate-lintel.md`. Mechanism not chosen.
- **Stone gripper:** concepts A (side clamp), B (suction), C (both) in `mechanical/concepts/stone-gripper.md` (Seif).
  In parallel, Maatoug designed **clapets v5** (`mechanical/clapets-v5/`, D-014 → D-017): doors + lift + a suction head
  that turns the 3-box stack. **Seif is turning it into the first prototype: clapets v7** (`mechanical/clapets-v7/`,
  D-019, D-020): real horn/servo/printer parts, door units reworked with M3 inserts, every fastener + BOM, motor on the
  floor. Rest pose clean; full cycle not re-run. Next: fastener tolerances, door sheet + foam, suction carrier with real
  tubes, printability, caliper check, print + test. A/B/C not dropped; the test decides.
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
- Seif: order stones + foam balls, robot and roof layout sketches, refined timeline, confirmation of the D-008 location,
  full-cycle check of clapets v7.
- Maatoug: back up personal files before the next pull; push the generators that only exist on his PC.
- Hamza Sammoud: PAMI size choice (4 or 6), qualifier/registration/poster dates.
- FAQ answers (Q1–Q9 not sent yet).
