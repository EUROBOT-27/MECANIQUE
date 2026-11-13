# Design history: how we got to clapets v5

From 2026-10-27 to 2026-10-29, Mohamed Ali Maatoug (fabrication CAD) designed this with Claude, starting from Seif's
clapets v1 and v2. This file explains what was tried, what was rejected and why, so nobody has to re-learn it. The
decisions are quoted in [DECISIONS.md](DECISIONS.md).

## 0. Starting point: Seif's v1 and v2 (SolidWorks)
- **v1**: two servo doors with foam pads clamp a quarry stack (3 boxes 320 × 110 × 110) by its ends. A backstop plate
  stops it tipping. A NEMA17 with an integrated TR8×2 screw, guided by 2 Ø8 rods + 4 LM8UU, lifts the door block
  **15 mm** (rule: a carried wall may be lifted ≤ 20 mm). MG995 servos, 688ZZ hinges, D-flat shafts.
- **v2**: v1 + a **suction head** (6 DP-S30 cups on a TPU membrane) with its own second lift and a third servo. It turns
  the stack 90° to stand the 3 boxes up as towers.
- Both were drawn for the omni-wheel base (set aside since; our base is differential, D-004).

## 1. Build it from what we own (2026-10-27)
- We disassembled a printer and started a **library of parts in hand** (D-012). The printer turned out to be a
  **Two Trees Bluer V2**, not an Ender 3 V2. The library is a preference, not a limit: anything sold in Tunisia is fine;
  imports from France take days, so they are flagged.
- The redesign proposal swapped v1's parts for ours: the printer's own axis as the lift, 608ZZ instead of 688ZZ (608 is
  everywhere locally), MG996R instead of MG995 (same body, more torque), captive M3 nuts.
- **Lead-8 screw instead of TR8×2:** not self-locking, so the stepper stays powered during the match (a 15 mm drop at the
  end is harmless).

## 2. Proof of concept 1: wiped
First attempt: one 2040 rail with the motor on a crossbar, generated in SolidWorks by a C# API script. Rejected in review:
- the shafts had a **D-flat that we don't have**;
- the **stepper was floating** on a cantilevered crossbar (vibrations); it should stand on the ground;
- the **backstop was unnecessary**, and the whole thing used too much space;
- the lift screw sat **in the centre, exactly where the rotating suction head must go**. Lesson (design principle):
  **reserve space for the next mechanism from the start**, design for modularity.

## 3. Proof of concept 2: the printer's Y axis stood on end
- **Lift:** the Two Trees **Y axis on end**. Its 2 rails become uprights, and the **butterfly bed plate with its own 4
  V-wheels** becomes the carriage. NEMA17 standing in a printed base, coupler, T8 screw up the middle *behind* the plate,
  608 at the top. Nothing floats, and the front of the plate is free for the head.
- **Door hinge, iterated with Maatoug:**
  1. Fixed shaft + a hub with the gear printed on it, turning on 608s. Question: is the pinion → hub link reliable?
  2. Servo driving the door directly: considered, but the servo would carry the door's whole bending load.
  3. Back to **2 gears**, v1 layout: servo on the top plate, gear on the rod top, **the rod turns** in 2× 608.
  4. **Plain Ø8 rod, no flat** → the gear and the arms grip it with **printed split clamps** (slotted hub + M3 + nut).
- **Real printer geometry:** the Two Trees model (.3dm, 181 MB) imported into SolidWorks, but the plate itself ("Product
  298") did not, so its holes were deduced from the screws and wheel bolts passing through it.
- **SolidWorks ran out of memory** on Maatoug's PC (about 15 min per run) → the generator moved to **FreeCAD 1.1** scripts
  (headless, ~1 min), exporting STEP for the SolidWorks team (D-015).
- **Motion studies:** clamp / lift 15 mm / release cycle with collision checks, and the full door range without the
  stack (free from −47° to +94°).

## 4. Perfecting brief (2026-10-28) → v4
Maatoug's requirements: rigid, not wobbly; **minimal footprint** but reliable; parts **≤ 250 mm** for the Bambu X1C;
only printed / laser-cut MDF / printer parts; doors **fold flat at start** without entering the cups' space, and **open a
bit more than needed** for tolerance; the TPU suction plate must turn 90° freely.
Choices (asked and answered):
- doors **fold inward, across the front**;
- the head **turns the whole stack 90° with one cup per box**, after **Barbatronic's CDR-2027** TPU spring stations
  (their repo was studied, notes in the hub `resources/_notes/cdr-2027-barbatronic.md`);
- the head is lifted by the **main lift** (no second motor);
- **short doors + head** (long doors gripping at the centre of mass need > 180° of door travel and break the deployed
  perimeter);
- 300 × 300 base for the perimeter checks; MG996R everywhere; rail height ignored for now (they won't be cut).

**v4** (D-016): short doors gripping the front ~30 mm of the box ends, fold +90° / clamp +3° / open −48°, 20T→24T gears.
Head with 3 TPU stations, driven by the printer's GT2 belt from below. Results: start 1200 mm, deployed 1333 mm,
height 340 mm. Problem: **the head was packed tight** (2 mm from the door units), so changing it meant changing everything.

## 5. v5: two modules with a reserved interface (2026-10-29, D-017)
Maatoug's request: make the clapets **modular**, so the turning suction head integrates easily, with room to rotate and
enough depth in front of the plate. So the design was turned around:
1. Define the **space reserved for module B** first: fixed zone, tube passage, rest envelope, turning disc R 140.
2. Design **module A around it**: lift 25 mm further back, door rods moved back to y 82 (every door-unit part stays
   behind the turning disc), 20T→28T gears (×1.4) for longer arms, doors open −35°.
3. Then design **module B inside it**: direct 20T→30T gear pair (no belt), 2× 608 on the head shaft, 3 TPU stations.
4. Check automatically: module A never enters the reserve, at rest and over the whole cycle.

### Refinements, same day
- **Doors 7 mm longer** (pads 37 mm). That is the maximum: folded at start, the door tips must stop at x 30, in front of
  the head's rest envelope.
- **Middle cup on the head axis** (asked by Maatoug, with the turning gear still working): head axis moved to z 165 = the
  middle box's centre, cups at 85 / 165 / 245. The hub part became clamp hub + 30T gear + a **Ø56 flange that is the
  middle station's mount**. The head now sweeps only R 108.
- Doors open −38° (179° of the servo's 180°), turning lift 75 mm, printed **strap** over each door servo.
- "How are the servos fixed?" → documented: flange screws in slotted posts + the strap; head servo on 2 posts.

### Finalizing pass
- **Real butterfly plate.** The .3dm was read directly with `rhino3dm`. The plate is a 3.0 mm aluminium extrusion,
  not 3.5. The centre holes are **M4**, not M3, and there is a **3rd hole** at x 25.8 that we didn't know about. The
  outline and holes are in `fc/plaque_papillon_reelle.json`.
- **Nut support**, rechecked for real assembly. It moved to 3 points: 2× M4 into heat-set inserts plus a pin in the 3rd
  hole. The T8 flange is now **under** the shelf, so lifting presses plastic on brass instead of pulling on screws.
- **Door unit ("aile") redesigned:** the old one looked odd and printed badly. It is now a body + a bolt-on cap, both
  printing without supports, with a 45° rear web that closes the frame into a box, fillets and chamfers. With the cap
  off, the rod, arms and gear drop in from the top.
- **Tolerances** for FDM, plus **adjustment slots** (lumières) where they help assembly.
- **Bearing spacers** on the inner races only, so nothing rubs the outer races.
- **Heat-set inserts**: 12 in total, listed in the build sheet.
- **Rod clamp check:** about 2 N·m of grip against about 0.5 N·m needed. It is marginal only at full servo stall, and
  the upgrade path is written down.

### The servo cable, three tries
1. Guessed: cable out of the end face **opposite** the shaft → wrong.
2. From one photo: a long side face, at the shaft end → wrong (the photo angle was misleading).
3. From three photos, then Maatoug's **real MG996R STEP model** (`resources/mg996r/`): the cable leaves the
   **short end face on the shaft side**, centred, 3.7–8.3 mm above the bottom. The real model became the servo
   reference, with a cable stub that the collision check must pass. It also revealed that the flange sits 28 mm above
   the bottom (not 26.6), that the ears have a rib, and that the case has a 1.1 mm label pad. All three are now cleared.

## Lessons
- **Use real models of bought parts as early as possible.** Each guess (plate thickness and holes, servo flange height,
  cable exit) cost a redesign later.
- **Reserve space for the next mechanism before designing the current one.**
- **Script the CAD and the checks.** Every change re-runs the interference check, the reserve check and a full-cycle
  check (perimeter, height, collisions) in minutes. That is what made the many iterations possible.
- **Think about the real assembly:** screw access, the order of operations, where inserts go, where cables go, how
  bearings are retained, and print orientation.

## Versions kept for comparison (not in this repo)
`Mecanique/module_clapets` (v1), `module_clapets_v2` (v2), `module_clapets_poc` (PoC 2, plus the SolidWorks
generator `sw/swpoc.cs`), `module_clapets_v4`. Ask Maatoug if you need them.
