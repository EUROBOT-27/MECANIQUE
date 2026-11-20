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
- Status: superseded by D-018 (the hub is shared, not handed over; "software in scope" stands)
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

## D-018 — One shared hub in git for Seif and Maatoug
- Date: 2026-11-01
- Area: project
- Decided by: Seif
- Status: active (supersedes D-013; updates D-001)
- Decision: Seif's hub and Maatoug's copy are merged into **one hub**, versioned in the git repo **EUROBOT-27/MECANIQUE**
  (name kept for now). Both leads work in their own clone, on `main`: `/start` pulls, `/wrap` commits and pushes.
  `CLAUDE.md` describes both users; each person's identity and Claude memory stay personal (`claude-workspace/`, not
  committed). Per-person files: `todo/<name>.md`, `logs/YYYY-MM-DD-<name>.md`; `STATUS.md` and `project/decisions.md`
  are shared. **Everything in `resources/` is committed** (other teams' repos as plain snapshots, no nested `.git`, no
  build output). Git LFS for our own binaries (CAD, images, videos, zip); `resources/` stays in normal git.
  Area leads confirm decisions in their area (mechanical + vision: Seif; software: Maatoug); decisions made in
  someone else's area are logged `proposed` until confirmed.
- Alternatives considered: two separate hubs synced by hand (they drift; D-numbers clash: D-012 to D-017 were made in
  Maatoug's copy only); one shared `TODO.md` (conflicts at every wrap); resources kept out of git (Seif wants them kept).
- Why: one decision log and one status for the team, without losing either lead's work.
- Consequences: D-014 to D-017 (clapets, Maatoug) were logged before this rule and still need Seif's review as
  mechanical lead. Binary CAD files have one owner at a time (`git lfs lock` if needed). Committed files use paths
  relative to the hub only.

## D-019 — Clapets v6: print and test v5 first, in its own folder
- Date: 2026-11-01
- Area: mechanical
- Decided by: Seif
- Status: active
- Decision: The first stone gripper we print and test on real stones is **clapets v5**, refined for printing by Seif
  as **clapets v6** in `mechanical/clapets/clapets-v6/` (scripts copied from v5, renamed v6; outputs go to `clapets-v6/CAD_FC/`).
  v5 stays as Maatoug left it. Concepts A/B/C (`mechanical/concepts/stone-gripper.md`) are **not dropped**; the real
  test decides.
- Alternatives considered: editing v5 in place (would overwrite Maatoug's reference outputs); prototyping A/B first.
- Why: v5 is the most complete design (CAD-checked full cycle); a real print + test answers more than more concept work.
- Consequences: D-014 → D-017 stay active as the base of v6. Maatoug is told that Seif owns `clapets-v6/` for now.

## D-020 — Clapets v7 is the version we print and test
- Date: 2026-11-01
- Area: mechanical
- Decided by: Seif
- Status: active (updates D-019: v7 replaces v6 as the print target; v5 and v6 stay as references)
- Decision: The proof of concept is printed from `mechanical/clapets/clapets-v7/`. Choices made in it:
  - **M3 heat-set inserts, hole Ø4.6 × 6.5** (sized from a part that fits Seif's inserts) instead of nut pockets in the
    door units; **nuts are kept** in split clamps, door sheet screws, head servo, hub clamp and cup stations.
  - **Door unit reworked:** full-height outer wall + closed box above the gears, servo held by 3 screws into inserts
    (no strap), one continuous bottom plate.
  - **Real parts in the CAD:** MG996R horn + wires (GrabCAD), Two Trees Bluer V2 profiles, wheels, spacers, NEMA 17,
    coupler, TR8 nut (`mechanical/resources/two-trees-bluer-v2-parts/`); every screw, nut and insert modelled, with a BOM.
  - **Motor on the floor** on a 1 mm rubber/cork pad, clamped by a separate plate on the motor and the rail blocks (the
    v5 socle could not be assembled).
  - **Lift travel stays 75 mm** (needed to turn the stack). **Profiles not cut** for the proof of concept; they will be
    cut when mounted on the real chassis (top tie ≤ 350 mm).
- Alternatives considered: printing v6 (nut pockets, open door unit frame, impossible motor mount).
- Why: make the first print match the real parts in hand, with nothing left to guess.
- Consequences: before printing: tolerance check of every fastener, door sheet + foam redesign, suction carrier with real
  tube sizes, printability check, caliper measurements (`mechanical/clapets/clapets-v7/README.md`). Full-cycle check not run yet.

## D-021 — Clapets v8: the suction head strikes forward on its own
- Date: 2026-11-03
- Area: mechanical
- Decided by: Maatoug
- Status: **confirmed by Seif on 2026-11-13, with a rework of module B (below)**
- Confirmation (Seif, 2026-11-13): the principle is kept (the cups press onto the stack by a forward movement inside
  module B, while the doors hold it). **The rework is done by Seif in a new folder `mechanical/suction-v1/`** (not a
  clapets version; v8 stays as Maatoug's reference, no Maatoug review needed). Seif's requirements for the module B rework:
  1. **Simpler:** fewer parts and fewer special parts; nothing that needs fine tuning to work.
  2. **Reliable:** no binding guides, no fragile press fits, no loads that depend on print tolerances.
  3. **Buildable in real life:** every part printable or in hand / local, every fastener reachable with a tool, an
     assembly order that works (same standard as v7 module A, `mechanical/design-principles.md`).
  4. **Works without the doors:** module B is still mounted on module A's butterfly plate (rides the lift), but it must
     hold, lift and turn the stack **by suction alone** if the doors are removed (fallback if the perimeter budget
     forces them out). Own frame, bench-testable, one simple interface to the butterfly plate.
  5. **Pneumatics, cables and fixings designed in, not left open:** pumps and valves placed and fixed, tube routing to
     the cups through the head's rotation and the strike travel, servo cables with strain relief, zip-tie anchors.
     Open for now (Seif): valves or pump-off release; pumps on the turning head or fixed with tubes through the rotation.
  6. Takes the current v7 module A (2026-11-12 state), insert holes per D-025, height margin re-checked with the 3rd
     servo and the carriage, strike force tuned on real stones.
- Decision: The cups must press firmly onto the boxes to attach reliably, with a forward movement inside module B only,
  while the doors hold the stack. In `mechanical/clapets/clapets-v8/` (copy of v7, owned by Maatoug), module B is split into a
  **fixed base** (2 bars on the 4 wheel bolts, each holding a Ø8 guide rod) and a **sliding carriage** (bearing tube,
  head servo, gears, carrier, cups). A **3rd MG996R** on the carriage turns a crank whose pin runs in a slot of the base
  (scotch yoke): +90° → the carriage goes **8 mm forward**, at dead centre so it holds. Rest pose = v7 (cups touching
  the stack face); at strike the cups press 8 mm in (bellows + TPU discs take it). Module A is unchanged.
- Alternatives considered: passive longer-travel springs under the cups (no actuator, but the force comes from the doors);
  sliding only the head shaft in LM8UU with a long pinion and a fork (more parts).
- Why: simplest active option: the rotation drive rides on the carriage, so the gear mesh and the turning cycle don't
  change; only printed parts + an MG996R + Ø8 rod.
- Consequences: +1 servo (wiring, a PWM channel), 2 × 47 mm Ø8 rods, 4 more M3 inserts. The strike force is set by the
  servo angle (TPU + bellows compression), so it must be tuned on real stones. No room to retract the cups behind the
  stack face: the strike is a press from contact, not a blow from a gap.

## D-022 — Clapets v7: door unit rebuilt as option B, nuts instead of inserts, sized for PLA
- Date: 2026-11-10
- Area: mechanical
- Decided by: Seif
- Status: active (updates D-020: door unit, inserts, motor pad)
- Decision: In `mechanical/clapets/clapets-v7/`, the door unit (`A_AILE`) and its cap are rebuilt from scratch as **option B**
  (`mechanical/concepts/aile-redesign/README.md`): a **C-section spine** (keel on the plate, back wall behind the servo,
  outer wall, bottom + top shelves, 3 mm walls, rounded windows, one outline whose chamfers continue into the cap) and a
  **cap to z 242** that carries the top 608 and the top plate M4. Print upright. Servo: **3 screws**, plain M3 nut under a
  roof, nut windows on the robot's side (+ one to the front). With it:
  - **Nuts in pockets instead of heat-set inserts** wherever an insert can't get 1.6 mm of wall; **no M4 inserts** (none
    in stock): the nut support uses the printer's own M4 × 8 (Y belt clamp screws) into nut pockets. Only 4 M3 inserts
    left (socle).
  - **No motor pad** (none in stock): the motor hangs from the clamp plate, 1 mm air gap.
  - **Everything sized for PLA** (tests + prototype); ABS (or PETG) later for robot parts.
- Alternatives considered: A (two corner brackets), C (drive on top), D (direct drive, −30 % squeeze); curved ribs,
  cap rib, a lip instead of the 3rd servo screw (all dropped by Seif).
- Why: the old door unit grew fix by fix (thin walls around inserts, openings everywhere); B is the sturdiest and keeps
  both bearings in one part; we print in PLA and have no M4 inserts / pad.
- Consequences: tolerance coupons first (`tolerance-tests/`, 10 coupons, ~150 g), then module A (~600 g PLA);
  assembly guide `assembly/clapets_v7_moduleA_assembly.pdf`. FEM check of B not run yet. Module A of v8 (D-021) must
  take these changes.

## D-023 — Printed parts in ABS on the Bambu X1 Carbon, tolerance coupons included
- Date: 2026-11-10
- Area: mechanical
- Decided by: Seif
- Status: active (updates D-022: "sized for PLA")
- Decision: The robot's printed parts are printed in **ABS** on a **Bambu X1 Carbon** (enclosed, door and lid closed,
  AMS). The clapets v7 **tolerance coupons are printed in ABS too**, on the same printer and filament, so the fits they
  give carry over to the real parts. Coupon settings: 0.2 mm layers, 4 walls, 15–20 % infill, as the STL lies, no
  supports. Real parts: 4 walls, 40 % infill, brim on tall parts.
- Alternatives considered: PLA coupons + PLA prototype, ABS later (the earlier plan): fits measured on PLA don't carry
  over to ABS (ABS shrinks more, holes come out smaller). PETG: not available.
- Why: an enclosed printer is available, so ABS warping on tall parts (~210 mm door unit spine) is manageable; ABS is
  tougher, takes heat and doesn't creep like PLA under the rod clamps and nut posts.
- Consequences: masses ~16 % lower than the PLA figures (ABS ≈ 1.04–1.05 g/cm³): coupons ~127 g, module A ~510 g with
  margin. Heat-set inserts (T6, socle) at ~245–265 °C. The generator `clapets-v7/fc/v7_fc.py` still uses
  `RHO_PRINT` = 1.24 (PLA), so its reported masses are high until changed.

## D-024 — Ayoub joins the hub as a user (beyond the two leads)
- Date: 2026-11-12
- Area: project
- Decided by: Ayoub; confirmed by Seif 2026-11-12
- Status: active (extends D-018)
- Decision: The shared hub is no longer limited to the two tech leads. **Ayoub** (CAD team, SolidWorks) uses it in their
  own clone with Claude, with the same workflow: `/start` pulls and briefs, `/wrap` logs, commits and pushes. Name key
  `ayoub` → `todo/ayoub.md`, `logs/YYYY-MM-DD-ayoub.md`. As a non-lead, Ayoub's decisions are always logged as
  `proposed` until the area lead confirms.
- Alternatives considered: keep the hub to the two leads and have Ayoub's work go through Seif (slower, and their CAD
  work and tasks would not be tracked in the hub).
- Why: Ayoub has CAD tasks for the 2026-12-31 mechanical milestone (stone gripper concepts, second face, Grail lift);
  tracking them in the hub keeps STATUS, TODOs and logs complete.
- Consequences: root `CLAUDE.md` ("Who uses this hub", file map), `/start` and `/wrap` skills updated for more than
  two users; `todo/ayoub.md` created. Other team members (e.g. Baha) can join the same way.

## D-025 — Heat-set insert holes: K × 0.9, mouth cone, L + 1 (new reference drawing)
- Date: 2026-11-12
- Area: mechanical
- Decided by: Seif
- Status: active (replaces the insert-hole rules of 2026-11-10 in `mechanical/design-principles.md`)
- Decision: every heat-set insert hole follows the reference drawing `mechanical/img/heat_set_insert_hole.png`:
  hole **K × 0.9**, mouth cone from **K + 0.2** down to the hole over **L × 0.25**, blind depth **L + 1** (K = knurl Ø,
  L = insert length). Our M3 inserts are straight, K 6.0, L 6.0: **Ø5.4 × 7, cone Ø6.2 × 1.5**.
- Alternatives considered: the old Ø4.6 × 7 + 0.5 × 45° chamfer: the ABS coupon (T6, Ø4.4 / 4.6 / 4.8) pushed melted
  plastic into the insert's bore. No new coupon printed (Seif): the drawing is applied directly.
- Why: the hole was far too small for a 6.0 knurl; the extra plastic had nowhere to go but into the thread.
- Consequences: `ins_hole()` in `clapets-v7/fc/v7_fc.py` (`INS3_K`, `INS3_L`) regenerated, all M3 insert holes changed
  (socle ×4, cap tabs ×2, head bracket ×4). Clapets v8 (Maatoug) still uses Ø4.6 × 6.5: to update.

## D-026 — Overhead camera: Raspberry Pi Camera Module 3 Wide, frames sent to the laptop by Ethernet
- Date: 2026-11-14
- Area: vision
- Decided by: Seif
- Status: active
- Decision: buy the **Raspberry Pi Camera Module 3 Wide (SC0874)** for the overhead station (2BTrading, 275 TND).
  The camera goes on a Raspberry Pi (4 or 5) that only grabs frames and sends them to the laptop over a **wired
  Ethernet cable** (JPEG per frame); **all processing runs on the laptop**.
- Alternatives considered: Arducam B0433 12MP USB 110° (better balance of sharpness and speed, but must be imported);
  ArduCam 64MP (sold locally, but too narrow: sees ~65–75 % of the table and needs a Pi); IMX219 120°/160° (too few
  pixels at speed); 4K webcams (too narrow, ≤ 90° D); WiFi from the Pi to the laptop (too slow).
- Why: the only camera sold in Tunisia that covers the whole table from the station (102° × 67°) at a usable rate
  (2304×1296 @ 56 fps). Comparison in `vision/camera-choice.md`.
- Consequences: D-008 stays (camera + laptop on the station) with a Pi added between them. Pi 4 or Pi 5 still to
  choose (Pi 5 needs its own camera cable). Lock the autofocus and calibrate at the runtime resolution. First test:
  70 mm marker in the far corners (~24 × 12 px at 56 fps, borderline).

## D-027 — Module B: one design for the front (on module A) and the back (alone on a butterfly plate); walls + towers
- Date: 2026-11-18
- Area: mechanical
- Decided by: Seif
- Status: active (updates D-021: module B is a fresh design, no longer a rework of the v8 strike head)
- Decision: module B (suction) is designed from a blank sheet in `mechanical/suction-v1/`, as **one design used
  twice**: at the **front** it mounts on clapets module A (rides its lift, doors around it); at the **back** it is
  mounted **alone on its own butterfly plate** (own lift, **no doors**). It must build **walls** (grab, carry, set down
  a quarry stack) **and towers** (stand single stones upright). Robot layout follows perimeter option 2: **front
  A+B, back B only**. Cups, holders (TPU spring stations if needed), tubes, fittings and cable/tube bending are
  designed in from the start. FreeCAD generator by Claude; many variations studied before choosing.
- Alternatives considered: rework of Maatoug's v8 strike head (D-021 plan of 2026-11-13); A+B front and mirrored A+B
  back (out: 1493 mm with both open, FAQ Q10); flip the whole stack in the castle (depends on FAQ Q9, open).
- Why: doors on both faces break the 1400 mm deployed perimeter (`mechanical/layout-v1/perimeter-study/`), so the
  back module must work by suction alone; one design for both faces halves the CAD and the spares.
- Consequences: the back of layout v1 = module B on a butterfly plate + lift (no mirror, no flip6). The back's
  deployed outline must stay inside the 82 mm left at 1318 mm. Flip-bar, central hub and v8 stay as references.
  Brief and driving numbers: `mechanical/suction-v1/README.md`.

## D-028 — Module B v1 turns the whole stack (3 stones at once); one stone at a time comes later
- Date: 2026-11-18
- Area: mechanical
- Decided by: Seif
- Status: active (narrows D-027 for the first version)
- Decision: module B v1 = a **turning plate with 3 cups** (one per stone) on the butterfly plate. It grabs a quarry
  stack and **turns the whole stack 90°** so the 3 stones end up standing side by side (towers), using module A's
  lift during the turn. Turning **one stone at a time** is a later version.
- Alternatives considered: one stone at a time first (M1 tower unit: own carriage + belt, much bigger, built
  2026-11-18 as a study only).
- Why: simplest mechanism that does walls and towers; Seif reports FAQ Q9 answered **yes** (a held stone may pass
  350 mm inside the castle), so the ~460 mm mid-turn height is legal there.
- Consequences: the turn happens in the castle only. The cups are pitched 85 mm (not 110) so the turning plate
  itself stays under 350 mm during the lift-turn. Generator: `mechanical/suction-v1/fc/turn_t1.py`.
- Update 2026-11-18 (Seif): **pumps and valves stay in the robot**, not on module B (too heavy, too complex);
  the 3 cup tubes go through a hollow shaft at the turning axis.

## D-029 — Grail lift: top grip + 180° flip onto the roof, two versions (B rack, B2 lead screw); suction version later for the gate lintel
- Date: 2026-11-20
- Area: mechanical
- Decided by: Seif
- Status: active (the Grail lift direction; `mechanical/grail-lift/` v1–v3 stay as reference)
- Decision: the Grail lift grips the Grail **by its top** and **flips it 180°** about an axis along the right face, so
  it lands **upside down on the roof** and the gripper ends under it in a roof slot. Two versions are developed in
  parallel in `mechanical/Grail_v2/`: **B** = rack lift (2020 + V-wheel carriage + NEMA17 pinion on an m1 rack,
  Baha's rack) and **B2** = lead-screw lift (T8 + 2 × Ø8 rods / LM8UU, NEMA17 by GT2 belt, from Baha's "corrigé").
  Both flip with an MG996R. **Electromagnet first**; a **suction-cup version** comes later and is meant for the
  **gate lintel** too (pick the 2nd stone of a stack from its top at z 220, flip, set it on the two towers at ≥ 320,
  the cup ending in the gap between them).
- Alternatives considered: A pivot (one servo, no lift: arm 128 mm out while turning, perimeter +~96); C rolling (one
  NEMA17, half gear on a fixed rack: the Grail dips below the roof top at the edge); Baha's Grail v1 screw and rack
  versions and the corrigé (flip into their own column, 360–520 mm tall); grail-lift v2/v3 (Maatoug).
- Why: only B/B2 pass every check so far (actuators ≤ 340, the Grail never enters the body, magnet leaves straight
  down); a top grip needs the flip to end under 350; one mechanism can serve the Grail and the gate lintel.
- Consequences: the right side bay (x 66–150, y ±40, z 78–300) holds the lift; roof slot about x 95–151, y ±15 at the
  Grail spot. B must move its column into the bay (as B2). Gate lintel stays 3rd in the build order (D-010); its
  stone passes 350 mid-flip (FAQ Q9 yes, castle only: check where the gate is built). Files and checks:
  `mechanical/Grail_v2/README.md`.
- Update 2026-11-20 (Seif): version B is named **Flipper** (rack lift, now placed on base_330_js on a printed saddle over
  the right drive wheel) and B2 **Flipper-S**. The **Grail lands on a deck at z 320** (L4 > 300); the rest of the robot's
  top can be at 350 (different top heights). The Flipper can't place higher than ~324 (its arm swings above the place
  height, actuators ≤ 350).
