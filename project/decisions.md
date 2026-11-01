# Decision Log

One entry per decision the team commits to. Newest at the bottom. Never delete an entry: if a decision is
reversed, add a new entry that supersedes it and mark the old one `Superseded by D-xxx`.

Template:

```
## D-000 — Title
- Date: YYYY-MM-DD
- Area: mechanical | vision | electrical | strategy | project
- Decided by: who
- Status: active | superseded by D-xxx
- Decision: what we chose
- Alternatives considered: what we didn't choose, and why
- Why: the reasoning
- Consequences: what this constrains or requires next
```

---

## D-001 — Project hub organisation
- Date: 2026-10-25
- Area: project
- Decided by: Seif
- Status: active
- Decision: Use this folder as the year-long hub. The main Claude session acts as project chief; memory lives in
  files (`CLAUDE.md`, `STATUS.md`, `TODO.md`, `logs/`, this log). Per-area context is kept in `mechanical/` and `vision/` with
  their own `CLAUDE.md`. Subagents only for one-off heavy jobs (e.g. `rules-checker`). Daily routine: `/start` and `/wrap`.
- Alternatives considered: one persistent agent per area (mechanical, vision, organiser, chief). Rejected because
  subagents start fresh every time and can't remember. Organiser and chief merged because they need the same information.
- Why: Files survive between sessions; the main session keeps back-and-forth design discussions in one place.
- Consequences: Decisions must be written down when made; `/wrap` must run at the end of each session.

## D-002 — Manufacturing methods
- Date: 2026-10-25
- Area: mechanical
- Decided by: Seif
- Status: active
- Decision: Build with 3D printing, laser cutting, aluminium profiles and rods.
- Alternatives considered: —
- Why: Available to the team and fast to produce.
- Consequences: Design for these processes (printable parts, flat laser-cut plates, profile-based frame).

## D-003 — CAD tool and file language
- Date: 2026-10-25
- Area: project
- Decided by: Seif
- Status: active
- Decision: SolidWorks for all CAD (Seif, Ayoub, Baha). All project files in English.
- Alternatives considered: —
- Why: Team's existing tool and skills.
- Consequences: CAD files are binary; they need a storage/versioning plan (see TODO backlog: git).

## D-004 — Differential drive
- Date: 2026-10-25
- Area: mechanical
- Decided by: team (reported by Seif)
- Status: active
- Decision: Differential drive with 2 × Pololu 4742 (37D gearmotor, ordered from Lextronic) and JSUMO wheels (to buy).
- Alternatives considered: omniwheels. The team explored them and decided against.
- Why: The team's own exploration. It's also the setup Aerobotix 2026 used successfully (3 mm drift after 100 s).
- Consequences: The robot has to rotate to face its targets, so symmetry and a centred axle matter (see
  `mechanical/design-principles.md`). Separate spring-loaded encoder wheels recommended.

## D-005 — Opponent tracking by vision
- Date: 2026-10-25
- Area: vision
- Decided by: Seif
- Status: superseded by D-007
- Decision: Vision tracks the opponent. The team's LiDAR is not reliable enough.
- Alternatives considered: LiDAR-based tracking (Aerobotix's approach). Their 10 Hz LD19 was also their main limitation.
- Why: LiDAR unreliable.
- Consequences: CV becomes part of the **mandatory avoidance system** [GR F.6], which is checked at homologation.
  A non-working system costs −30 pts; disabling it on purpose means disqualification [GR H.4]. It must detect
  opposing robots **and SIMAs**. CV is now on the critical path.

## D-006 — Aerobotix 2026 design principles as our reference
- Date: 2026-10-25
- Area: mechanical
- Decided by: Seif
- Status: active
- Decision: Use the principles in `mechanical/design-principles.md` as the standard for reviewing designs: symmetry,
  printed zip-tie anchors, a testing method aimed at measurable reliability, and more.
- Alternatives considered: —
- Why: Seif studied the Aerobotix 2026 robot (2nd at the European final) and liked many of its decisions.
- Consequences: Every concept and CAD review checks against that file.

## D-007 — Opponent tracking and avoidance: LiDAR + vision
- Date: 2026-10-25
- Area: vision
- Decided by: Seif
- Status: active (supersedes D-005)
- Decision: Combine LiDAR and vision to track the opponent and for the mandatory avoidance system.
- Alternatives considered: vision only (D-005), rejected the same day. LiDAR only: our LiDAR isn't reliable on its own,
  and Aerobotix 2026 found 10 Hz LiDAR too slow at 1 m/s.
- Why: Each covers the other's weaknesses (LiDAR: direct range, independent of lighting; vision: identity via ArUco,
  wider coverage, helps when the LiDAR is unreliable).
- Consequences: The avoidance system [GR F.6] relies on both, so design how they combine. **The LiDAR mounting height
  decides what it sees.** A LiDAR on the mast (~350–430 mm) scans above the opposing SIMAs (≤ 175 mm tall) and most
  robot bodies, so it mainly sees beacon supports. SIMA detection must come from vision or a low-mounted sensor.

## D-008 — Overhead vision station on the table
- Date: 2026-10-25
- Area: vision
- Decided by: Seif
- Status: active
- Decision: An overhead camera **and the laptop** sit on a station at the table edge (Seif's "balise fixe") and talk to
  the robot wirelessly. The software team chooses the wireless technology.
- Alternatives considered: 2026 setup with the PC beside the table (not allowed [GR F.6]).
- Why: Whole-table view for opponent tracking (D-007); compute must be on the table.
- Consequences: By the rules this has to be the **remote computing and observation device**, not a fixed beacon:
  fixed beacons are limited to 100 × 100 × 1000 mm and may only hold sensors and telecom [GR G.1, G.3]. The remote
  device allows a 450 × 320 mm footprint, up to 1.6 m above the platform and < 5 kg total, fixed with an M8 rod + wing
  nut, and nothing may be able to fall off [GR G.4]. Laptop + mast + camera must fit in 5 kg.

## D-009 — Strategy direction: max points
- Date: 2026-10-26
- Area: strategy
- Decided by: Seif (with the team)
- Status: active (direction only; the detailed plan in `project/strategy.md` is still a brainstorm)
- Decision: Aim for maximum points by targeting every scoring action: walls, towers, gate, Grail, return home,
  SIMA moats, SIMA attack, cannonballs. Each action is handled on its own merits, which often means its own mechanism,
  but shortcuts that cover several actions are welcome. The Grail ends at **L4 on our robot's roof**. SIMAs ("PAMI"):
  three versions (basic, ejector, attack) are built and tested, and the tests decide which ones are used and how many.
- Alternatives considered: a reduced action set focused on reliability (the rules recommend "simple and reliable
  systems" [G C]). Not chosen; the scope risk is handled by prioritising (tiers in `project/strategy.md`) instead.
- Why: Each action scores independently and in different ways; the team wants to compete for the top.
- Consequences: Many mechanisms compete for the 2026-12-13 CAD freeze and for space on the roof. Grail variants must
  release the Grail before 100 s and leave it resting free on the roof [G E.2], [GR H.3].

## D-010 — Build order: secure the sure points first
- Date: 2026-10-26
- Area: strategy
- Decided by: Seif
- Status: active
- Decision: Every action stays in the plan (D-009), but mechanisms get design time, prototypes and the best chassis
  space in this order: **1st** walls, return home, Grail L4 · **2nd** flipper (towers) · **3rd** gate lintel hand,
  robot launcher. PAMIs run in parallel (separate team). Later mechanisms get **reserved space** in the CAD from the
  start (reserved block + mounts + cable path + mass/power share, see `mechanical/design-principles.md`).
- Alternatives considered: developing all mechanisms in parallel with equal priority (risk: all at 80% on the
  2026-12-13 CAD freeze, none finished).
- Why: Points per effort (`project/strategy.md` → Build order); the flipper also serves the gate; the robot launcher
  has a backup in the ejector PAMIs.
- Consequences: Launcher decided after the ejector PAMI test. A roof layout sketch is needed early.

## D-011 — Gate mechanism shares a driving face
- Date: 2026-10-26
- Area: mechanical
- Decided by: Seif
- Status: active (which face, A or B, still open)
- Decision: The gate lintel mechanism sits on a **driving face** (front or back) and shares it with a stone gripper
  (face A = stack pick-up, or face B = pick-up + rotate). **No gate on a side face.** Space to reserve:
  `mechanical/concepts/gate-lintel.md`.
- Alternatives considered: gate on a side face, with a ~120 mm sideways slide to bring the lintel over the uprights.
  Rejected: extra axis (motor + rail), and with differential drive (D-004) the sideways position can't be corrected
  without driving away and coming back.
- Why: Differential drive only moves forward/backward, so driving straight at the uprights brings the lintel over them
  with no extra axis.
- Consequences: The gate and the stone gripper on that face must be designed together (shared slot ~340 × 130 mm,
  narrow protrusion for the perimeter budget). Face A vs B is decided once the stack gripper concept is chosen
  (`mechanical/concepts/stone-gripper.md`).

## D-012 — Keep a library of parts in hand
- Date: 2026-10-27
- Area: mechanical
- Decided by: Seif
- Status: active
- Decision: Keep `mechanical/parts-library.md`, a list of parts the team physically has (first source: the
  disassembled Ender 3 V2). Claude checks every design against it and flags missing parts.
- Alternatives considered: no inventory at all (the 2026-10-25 rule).
- Why: Designing around parts already in hand avoids imports from France and their delays.
- Consequences: Narrows the 2026-10-25 rule: orders and purchases are still not tracked. Only `verified` lines
  (counted + measured) are trusted for design.
- Update 2026-10-27 (Maatoug): the library is a preference, not a limit. Any part available in Tunisia may be
  used; only imports are flagged.

## D-013 — Hub handed over to Maatoug; software in scope
- Date: 2026-10-27
- Area: project
- Decided by: Maatoug
- Status: active
- Decision: This copy of the hub belongs to Mohamed Ali Maatoug (software lead + fabrication CAD). Software is in
  scope (`software/`). Seif's old session logs were deleted; his decisions above stay as the team record.
- Alternatives considered: keep software out of scope (the 2026-10-25 choice, made for Seif's hub).
- Why: Maatoug's work is software plus turning mechanical designs into fabrication-ready CAD.
- Consequences: `TODO.md`/`STATUS.md` rewritten for Maatoug; Seif's open items are follow-ups.

## D-014 — Clapets proof of concept: build choices
- Date: 2026-10-27
- Area: mechanical
- Decided by: Maatoug
- Status: active
- Decision: Build a **functional proof of concept** of the clapets module now (`mechanical/concepts/clapets-redesign.md`).
  For the PoC: the lift reuses the **Ender 2040 upright + V-wheel carriage** + NEMA17 + coupler + T8 screw (fallback:
  Ø8 rods if the rail makes it complicated); door hinges on **608ZZ** (Claude's pick, Maatoug had no preference);
  **captive steel M3 nuts** in printed pockets, as in v1. Rule limits on **height may be exceeded on the PoC**
  (e.g. profile tops); it only has to work.
- Alternatives considered: rods + LM8UU + integrated-screw NEMA17 (v1 as drawn, needs parts we don't own); 688ZZ;
  heat-set inserts.
- Why: Use what we own and see the mechanism work quickly; rule fitting comes in the competition version.
- Consequences: The competition version must be rechecked against every rule (height, perimeter, Q1, Q9). The Ender
  screw (lead 8, not self-locking) is held by keeping the stepper powered.

## D-015 — FreeCAD for the clapets proof of concept
- Date: 2026-10-28
- Area: mechanical
- Decided by: Maatoug
- Status: active
- Decision: The clapets PoC CAD is generated with **FreeCAD 1.1** (Python script `Mecanique/module_clapets_poc/fc/poc_fc.py`)
  instead of the SOLIDWORKS API generator. Every part and the assembly are exported as STEP, so the SolidWorks CAD team
  can open them. Narrow exception to the "SolidWorks for all CAD" decision; it does not change it for the robot.
- Alternatives considered: keep the SOLIDWORKS generator (needs SOLIDWORKS running; ~15 min per run; failed for lack of
  memory on Maatoug's PC).
- Why: lighter (runs headless in ~30 s), no SOLIDWORKS session needed.
- Consequences: the SOLIDWORKS generator `sw/swpoc.cs` is kept but not maintained. Competition CAD stays in SolidWorks
  unless the team decides otherwise.

## D-016 — Clapets module v4: final concept for the real build
- Date: 2026-10-28
- Area: mechanical
- Decided by: Maatoug
- Status: active
- Decision: Redesign the clapets module (`Mecanique/module_clapets_v4/`, FreeCAD scripts) for the real build:
  **short doors** (v1-style, grip the front ~30 mm of the box ends) that **fold inward flat across the front** at
  start, open ~48° to clear the turning stack; **MG996R** door servos; **suction head turns the whole stack 90°, one
  cup per box** (3 cups), modular TPU spring stations inspired by Barbatronic CDR-2027; the head's cups/rings are the
  anti-tip backstop; the head's lift is the **main lift** (no second lift motor). Printed parts ≤ 250 mm (Bambu X1C),
  only printed / laser-cut MDF / Two Trees printer parts. Lead-8 screw kept; 350 mm rails kept (their height is
  ignored for now). Perimeter checked against a **300 × 300 mm base** (start ≤ 1200, deployed ≤ 1400).
- Alternatives considered: long doors gripping at the box centre of mass (needs > 180° door travel and breaks the
  deployed perimeter); 2 cups per box (v2); a separate head lift.
- Why: smallest footprint, lowest torque, rigid, buildable from parts we own.
- Consequences: head axis at z 175 (clears the lift-nut screw), cups at z 90/135/240, lift 72 mm to turn the stack.

## D-017 — Clapets v5: two modules with a reserved interface for the suction head
- Date: 2026-10-29
- Area: mechanical
- Decided by: Maatoug
- Status: active (replaces the layout of D-016; the concept choices of D-016 stand)
- Decision: Split the mechanism into **module A** (lift + doors) and **module B** (suction head), and design A around a
  **reserved space** for B: head fixed zone (y 50–108, ±62), cable passage, rest envelope (cups vertical, x ±36) and a
  turning disc of **R 140** (B needs R 126). To make room: lift moved **25 mm back**, door rods moved back to y 82 so the
  door units stay behind the turning disc; door gears 20T→28T (×1.4), doors open to −35°. Module B bolts on the plate
  front (4 wheel bolts), drives its shaft with a 20T→30T gear pair from an MG996R in its fixed zone (no belt), 2× 608
  35 mm apart, 3 TPU cup stations (one per box), tube holes + zip-tie slots + reserved tube passage.
- Alternatives considered: v4 (head packed tight: 2 mm clearance to the door units, belt drive below the head).
- Why: Maatoug wants module B to integrate easily, with room to rotate and enough depth in front of the plate.
- Consequences: `Mecanique/module_clapets_v5/` is the reference design; v4 kept for comparison.
- Update 2026-10-29 (Maatoug): **middle cup on the head axis** (axis z 165 = middle box centre, cups 85/165/245; the
  hub flange is the middle station's mount), **doors +7 mm** (pads 37 mm; the maximum, folded tips stop at x 30),
  doors open −38°, turning lift 75 mm, printed **strap** over each door servo. Full cycle re-checked: 0 collisions,
  start 1200 mm, deployed ≤ 1367 mm, height ≤ 347.7 mm.
- Update 2026-10-29, finalizing pass (Maatoug): **real butterfly plate** in the CAD (read from the Two Trees .3dm: 3.0 mm
  aluminium, centre holes M4, a 3rd hole at x 25.8); **nut support** on 3 points (2× M4 into heat-set inserts + a pin in the
  3rd hole), T8 flange moved under the shelf; **door unit = body + bolt-on top cap**, both printed without support (45°
  rear web, fillets, chamfers); **servo cable channels** (connector passes) + zip-tie anchors; fabrication tolerances
  (608 seats Ø22.2 + lead-in, clamp bores Ø8.2, nut pockets +0.3); adjustment slots (door units ±1.5 x, door sheet tabs
  ±1.5 y, strap ±1 x). Re-checked: 0 interferences, full cycle 0 collisions, 1200 / ≤ 1367 / ≤ 347.7 mm.
- Update 2026-10-29 (Maatoug, servo photo): MG996R cable exits a long side face at the bottom, at the shaft end. Cable
  slots redone (door D front, door G back, head underside → slot down the bracket); printed bearing spacers added
  (`A_ENTRETOISE_608_BAS/HAUT` on the door rods' inner races, `B_ENTRETOISE_TETE` sleeve between the head's 608s); 12 heat-set
  inserts listed in the README. Re-checked: 0 interferences (cable stubs included), full cycle 0 collisions.
- Correction 2026-10-29 (Maatoug, photos + real model `mechanical/resources/mg996r-servo-3.snapshot.9`): the MG996R cable
  leaves the **short end face on the output-shaft side**, centred, 3.7–8.3 mm above the bottom. The real STEP is now the
  servo reference in the CAD (flange 28 above the bottom, body 40.4 × 20.4 × 38). Cable channels redone on that face
  (doors: through the outer post and down through the bottom plate; head: window extended + L slot down the bracket);
  posts clear the ear rib, strap pocketed for the label pad. Re-checked: 0 interferences, full cycle 0 collisions.
