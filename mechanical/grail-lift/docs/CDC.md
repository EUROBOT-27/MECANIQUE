# Grail lift: requirements (CDC)

What the mechanism must do, taken from the rules, plus the constraints we derived from them. Every Grail-lift
variant (v1 = Baha's essai mecanisme 1, v2 = concept here, and any other variant) is checked against this page.
Rule references: `project/rules-digest.md`.

## 1. From the rules

| # | Requirement | Ref |
|---|---|---|
| R1 | The Grail starts **on the throne-room floor**, fully inside it, **not under robot control**. Robot + Grail must both fit in the 500 × 500 throne room at the start. | G E.2, G D.3 |
| R2 | It must stay **inside the castle area the whole match**, so we only pick it up at the end, in our castle. | G E.2 |
| R3 | **L4 = the Grail's lowest point on our robot's roof, roof > 300 mm**, worth 5 + 4 × 5 = 25 pts. | G E.2 |
| R4 | At the end it must rest **free of any actuator or fixing system**. A Grail still held does not count. All actuators stop at 100 s. | G E.2, GR H.3 |
| R5 | **Robot and actuators ≤ 350 mm at all times.** Only the Grail itself may go higher, in the castle. | GR F.3, G E.1, G E.2 |
| R6 | Deployed perimeter ≤ 1400 mm (start ≤ 1200). The lift shares the ~200 mm deployed budget with the other mechanisms. | GR F.3 |
| R7 | The Grail is ours: > 60 mm cube envelope, SIMA-like limits (which ones exactly = FAQ Q3). | G E.2 |
| R8 | Must not block the opponent's beacon. Safe if the Grail top stays ≤ 430 mm on the roof (FAQ Q8). | G E.2 |
| R9 | Nothing may fall off the robot. | GR H.4 |

## 2. What we want (team)

| # | Requirement |
|---|---|
| F1 | Endgame (D-009): go home, pick the Grail, put it on the roof (L4) + return home = 35 pts, then shoot cannonballs from home (85–100 s). The whole Grail cycle should take **≤ 15 s**. |
| F2 | Pick-up tolerant to robot positioning: ± 10 mm along the face, ± 5 mm in distance (the magnet only needs to reach the plate). |
| F3 | Folded inside the robot outline during the match (no perimeter cost while driving). |
| F4 | Parts from `parts-library.md` first (📦), then local (🇹🇳), import (✈️) last. PLA/ABS printed parts only. |
| F5 | Safe at e-stop / power off: nothing falls onto the Grail or a hand. |

## 3. Derived constraints (the hard part)

**D1: a straight lift cannot do L4.** Say everything that rides up with the Grail (carriage, motor, servo, magnet)
spans a height *H* around the grip point:
- at pick-up it must stay above the table;
- at the end the Grail's bottom is above 300 mm, and the top of that block must stay ≤ 350 mm.

That gives **H ≤ 350 − 300 − ~1 ≈ 49 mm** (≈ 42 mm with the roof at 305 and a 2 mm margin), whatever the grip
height and the mounting. A carriage on V-wheels with a motor is 60–70 mm tall. So a design that only translates
**must change the grip-to-carriage offset during the lift** (a 2nd motion), or use a 2-stage hand-off.

**D2: the grip must sit low on the Grail at the end.** For the magnet (Ø 27) to stay ≤ 350 mm with the Grail's
bottom > 300 mm, its centre must be **≤ ~35 mm above the Grail's lowest point** at release.

**D3: a horizontal move over the roof edge is needed.** The Grail starts outside the robot and ends over the roof.
A straight inclined path fails: the Grail would hit the roof edge before it is above it.

**D4: clean release.** After the magnet switches off, the arm has to leave without dragging the Grail. A pure
rotation always pushes one edge of the magnet slightly into the plate. Keep it to < 1 mm and absorb it with a
sprung magnet mount.

**D5: the Grail can end upside down.** It's our object, so we make it symmetric, with a steel plate near each end of
one face. v2 relies on this (D1 → the flip inverts it).

## 4. Interfaces / assumptions to confirm

| Item | Assumed | Who |
|---|---|---|
| Roof top height | 305 mm (plate 300–305) | Seif (roof layout) |
| Face carrying the lift | a **driving face**, so the robot drives straight into the Grail (F2). Competes with the clapets and the gate slot (D-011). | Seif |
| Lift bay inside the robot | v2 needs ~115 × 150 mm through the full height + 2 roof openings | Seif / layout |
| Grail | 80 mm cube, ≤ 150 g, mild-steel plate (or a big fender washer 📦) on one face, symmetric | team |
| Electronics | 12 V electromagnet (~3–4 W) on a MOSFET + flyback diode, reverse pulse to release; 1 stepper driver; servo 5–6 V | Hamza Bjaoui |
| FAQ | Q3 (Grail limits), Q7 (passive recess on the roof?), Q8 (Grail height on the roof) | Hamza Sammoud sends the FAQ |
