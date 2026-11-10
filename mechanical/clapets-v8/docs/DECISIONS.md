# Decisions behind this design

Copied from the project decision log (`Eurobot 2027-ALL/project/decisions.md`, 2026-10-30). Paths like
`Mecanique/module_clapets_v5/` refer to the working folder this repo was made from. Earlier team decisions referenced here:
D-002 (manufacturing: printing, laser cutting, profiles, rods), D-004 (differential drive base), D-006 (design standard),
D-010 (build order: secure points first, reserve CAD space for later mechanisms).

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
