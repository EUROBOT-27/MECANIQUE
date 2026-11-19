# Mechanical design principles

Our reference standard: **review every concept and every CAD against this list.**
Main source: Aerobotix INSAT's 2026 robot (2nd at the European final). Details in
`resources/_notes/aerobotix-2026-robot.md`.

✅ = Seif explicitly wants this · ◻ = proposed by Claude from the study; Seif keeps or drops it

## Architecture
- ✅ **Symmetry.** Aerobotix had identical picking faces front and back, so the robot never turns around to pick.
  For us: make it symmetric wherever that saves a rotation. It also helps us play either team colour.
- ◻ **Drive axle through the robot's centre**, so it turns on the spot without sweeping a big circle.
- ◻ **Low centre of gravity.** Heavy parts (motors, battery, base plates) go on the base plate. Light materials
  higher up (laser-cut MDF box). This matters even more for us: the Grail on the roof (> 300 mm) and stones held high.
- ◻ **Independent modules, one actuator per job.** If one module fails, the robot still scores with the others.
  Fewer shared mechanisms means fewer single points of failure.
- ◻ **Subassemblies that can be removed on their own** (drive, gripper, pneumatics, electronics), so fixes
  between matches take minutes.
- ◻ **Electronics in a top box with a hinged lid; battery in a pull-out drawer.** We need a fast battery swap
  anyway, because the rules require 3 matches in a row [GR F.4.b].

- ✅ **Reserve space for mechanisms that come later** (Seif, 2026-10-26). For each mechanism that isn't designed yet
  (lintel hand, launcher…), add to the top-level SolidWorks assembly:
  1. A **reserved block**: a simple transparent, coloured body with the mechanism's rough size, including the volume it
     sweeps when it moves. Nothing else may enter it. Check with Interference Detection before each CAD review.
  2. **Mounting points on the chassis now**: a 20×20 profile rail, or a hole pattern, where the mechanism will bolt on
     later. Profiles with T-nuts let the exact position change without re-cutting parts.
  3. **A cable path** (zip-tie anchors), plus a share of the **mass** and **power** budget and a spare motor/servo output (tell Hamza Bjaoui).
  The roof gets its own layout sketch: beacon support (within Ø200 of the centre), e-stop, Grail landing spot,
  launcher, lintel hand.

## Details
- ✅ **3D-printed zip-tie anchors designed into the CAD** (Aerobotix had 39). Cable routing is designed, not improvised.
- ◻ **Casters ~2 mm above the floor line**, so the drive wheels always carry the weight and keep grip.
- ◻ **Separate spring-loaded encoder wheels** next to the drive wheels, so position tracking doesn't suffer when the
  drive wheels slip (Aerobotix: 3 mm drift after 100 s).
- ◻ **Bearings as cam followers** wherever a part pushes on another moving part.
- ◻ **Everything mechanical bolts to one base plate**, and the structure goes up from it via 20×20 profiles.
- ✅ **Assembly access** (Seif, 2026-11-10): every nut pocket, screw and hex key needs a straight path to free air
  (no part covering the pocket mouth or the head), room for a 5.5 wrench or pliers where a nut sits free, and screws
  long enough to pass the whole nut. Check it in the CAD before printing (`fc/fastener_check_v7.py`).

## Shape and assembly rules for printed parts
✅ Seif, 2026-11-10, from the clapets v7 door unit rebuild (`concepts/aile-redesign/`). Apply to every printed part.

- **One logic per part.** Build a part from one clear outline (e.g. a C-section), not from patches added fix after fix.
  3 mm walls, 2 mm ribs, thick zones cored out.
- **Edges continue across stacked parts.** When one part sits on another (cap on body, motor plate on socle), they
  share the same outline at the joint, with the same chamfers, so they read as one part. In the generators: one
  outline function used by both parts (`top_loop()` in `v7_fc.py`).
- **One edge rule:** 1 mm chamfer on every outside vertical corner, a small fillet on every inside corner (it also
  protects the layer lines). 45° only where an overhang needs it.
- **Windows with rounded corners**, flat top ≤ 20 mm (it must bridge when printed upright). No triangular tops.
- **Nuts go in pockets** (a simple rectangular indent, it does not have to be hex-shaped), like the rod clamps:
  the nut cannot turn or fall, no wrench needed. Pocket for M3 6.0 × 6.9 × 2.8, M4 7.4 × 8.4 × 3.6; keep any
  adjustment slide (e.g. ±1.5) in the pocket length. A pocket must open to free air with nothing covering its mouth.
- **Hand and tool room around every screw head:** room for fingers to start the screw and for the key (straight, or a
  ball-end key at an angle through a front opening). Check that the head itself does not hit a wall.
- **Don't fix one problem by making a big opening that thins the wall next to it.** Make the opening the size it
  needs and add a rib beside it (door unit inner servo ear: opening + 2.5 mm rib on the web).
- **Holes for cables/parts only as big as the part:** a cable exit the size of the grommet, not a full-width slot
  (a full slot left a 2 mm strip). Thread the connector before assembly if needed.
- **Keep-out zones for moving parts** (arm swing, gear tips) are drawn first; no wall goes in them.
- **Print orientation is chosen from the loads and the precise features:** bearing seats and bores on one axis →
  print with that axis vertical (round, coaxial). Check that the main loads run along the layers; fillets where walls
  meet shelves. ABS: tall parts need an enclosed printer.
- **Size for ABS** (tolerances from ABS test prints, ABS masses), D-023; see "Print materials".

### Lessons from the first assembly (clapets v7 module A)
✅ Seif, 2026-11-18, after printing (ABS) and assembling module A. Everything else assembled well. Apply these to the
**next prints** (any mechanism). Module A itself is not reprinted for them.

- **A nut must be placeable by hand, not just reachable.** The M4 nut that holds the cap to the butterfly plate (the
  one nearest the plate, `m4_plate()` in `clapets-v7/fc/v7_fc.py`) was near impossible to set: it sits in a pocket on
  a face you can't see or hold while the screw comes blind from the other side of the plate. For each nut, check: can
  it go in its pocket **before** the parts are brought together, and does the pocket hold it on its own (drop-in from
  above so gravity keeps it there, or a snug pocket)? If not, swap the sides (nut on the open side), or use a heat-set
  insert there (D-025 holes).
- **Spacers belong to the part they sit on.** A separate spacer between two parts (e.g. `A_ENTRETOISE_608_BAS/HAUT`
  between the door arms and the 608) is one more piece to hold and lose during assembly. Make it a boss on the part
  (here: on `A_BRAS_PORTE`), keeping what the spacer did: touch only the bearing's inner race (Ø12 ring), clear the
  outer race.
- **Rod clamps: coupler style, not a tab.** The split clamps on the Ø8 rods (`split_clamp_z()`) work, but the lug
  that sticks out with the M3 across it feels fragile when the screw is tightened. Design them like a clamp-style
  shaft coupler: a thick round hub (large outer diameter) with the slot through one side, and the screw running
  across the slot **inside** the hub's diameter (head in a counterbore, nut in a pocket, both within the round
  outline). More material around the screw, nothing thin sticking out.

## Print materials (we have PLA and ABS, no PETG)
Seif, 2026-11-10. Our CAD so far assumed PETG; nothing in the geometry depends on it, only tolerances and habits.

| | PLA | ABS |
|---|---|---|
| Use | quick fit checks only (sizes don't carry over to ABS) | **robot parts + their tolerance tests**, on the Bambu X1 Carbon (D-023) |
| Good | stiff, accurate, almost no warping: sizes measured on PLA test pieces carry over well | tougher, takes heat |
| Watch | **creeps** under constant load: rod clamps and nut-under-roof posts loosen, re-tighten after the first runs; brittle on impacts; softens at 55–60 °C (no hot car) | **warps** on big tall parts: print the ~210 mm door unit spine in an **enclosed printer** or it lifts and cracks between layers; **shrinks more**: printed holes come out smaller, plan **+0.1–0.2 mm** on hole sizes |
| Density | 1.24 g/cm³ | ~1.045 g/cm³ (~16 % lighter) |
| Insert iron | ~225 °C | ~245 °C, up to ~265 °C |

Re-check in the material actually used (that is what the tolerance test prints are for): the 608 seats Ø22.2, the
hex nut recesses and the clamp nut pockets (6.0 × 6.9). ABS coupons 2026-11-12: 608 seat Ø22.2 good, servo nut
recess opened to AF 5.9, insert holes changed (next section).

## 3D-printed parts: holes for heat-set inserts
✅ Seif, 2026-11-12: **this drawing is our reference** for every insert hole, in every CAD (FreeCAD scripts and
SolidWorks). It replaces the 2026-11-10 rules (Ø4.6 hole + 0.5 × 45° chamfer): in the ABS coupon (T6) those holes
pushed melted plastic into the insert's threaded bore. The hole was far too small for the knurl, so the extra
plastic had nowhere to go but down and up into the thread.

![Heat-set insert hole: reference drawing](img/heat_set_insert_hole.png)

K = knurl Ø (measure the knurl's outside), L = insert length.

| Feature | Rule | Our M3 insert (straight knurl, K 6.0, L 6.0) |
|---|---|---|
| Hole Ø | **K × 0.9** | **Ø5.4** |
| Mouth | cone from **K + 0.2** at the face down to the hole Ø, **L × 0.25** deep | **Ø6.2 → Ø5.4 over 1.5 mm** |
| Blind hole depth | **L + 1 mm** (room for the plastic, the screw never hits the bottom) | **7.0** |
| Through hole | no extra depth | |

Rules we keep around the hole:

| Rule | Value | Why |
|---|---|---|
| Wall around the insert | **≥ 1.6 mm, aim 2 mm**, measured from the insert's **real** Ø (K = 6.0), not from the hole; at the face the mouth cone (6.2) takes 0.1 more | Thin walls crack or bulge when pressing. The CAD draws the inserts at the hole size, so a wall can look thicker than it is. |
| Boss Ø (round post around an insert) | **≥ 10 mm** (6.0 + 2 × 2), 12 when there is room | Same reason. |
| Slicer | **4 perimeters** around inserts (≥ 1.6 mm with a 0.4 nozzle); infill ≥ 40 % near the insert (modifier) | Knurls held only by sparse infill tear out. |
| Screw hole in the part on top | bigger than the screw, **smaller than the insert's Ø** | The part then presses on the insert's face, so the screw can't pull the insert out. |
| **No room? Use a nut instead** | if a neighbour (servo body, edge) is closer than **K/2 + 1.6 = 4.6 mm** from the hole axis, don't use an insert | e.g. servo ears: the MG996R body is 4.3 mm from its ear hole. Use a plain nut in a hex recess under a thin roof, pushed in through a window (clapets v7 door servo posts, 2026-11-10). |
| Horizontal holes (axis flat while printing) | expect them a bit smaller / oval at the top | Overhang at the top of the hole sags. Set the insert with the part lying so the hole points up. |
| Load direction | avoid a tall thin post pulled along its print axis (Z) | Pulling layers apart is the weakest case. |

**Installation:**
1. Soldering iron with an insert tip, **10..20 °C above the print temperature**: PLA ~225 °C, **ABS ~245..265 °C**.
2. Put the insert in the mouth cone (it centres itself), tip in the thread. **Let it sink mostly under the iron's
   weight**; pushing hard drives plastic into the bore.
3. Stop at ~90 % of the depth, remove the iron, and press the rest flush (0..0.2 mm below the surface) with a flat
   metal tool. Hold a few seconds until the plastic sets (otherwise it creeps back up).
4. Let it cool, then check it's straight with a screw. Plastic in the thread: clear it with an M3 screw or tap.
- Plastic in the bore or a bump around the insert: hole too small. Insert spins or pulls out: hole too big.

**In our FreeCAD scripts:** `ins_hole()` in `mechanical/clapets-v7/fc/v7_fc.py` makes the hole + mouth cone from
`INS3_K`, `INS3_L` in `class G` (it derives `INS3_R`, `INS3_D`, `INS3_MR`, `INS3_MD`). Use it for every new insert
hole. For another insert size, measure K and L and apply the drawing. The fastener check
(`fc/fastener_check_v7.py`) measures walls from the real Ø6.0.

Sources: [CNC Kitchen, tips and tricks](https://www.cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts) ·
[Spirol, hole design for heat inserts](https://www.spirol.com/resources/white-papers/how-to-design-the-proper-hole-for-heat-ultrasonic-inserts/) ·
[takt3d design guide](https://www.takt3d.com/blog/heat-set-inserts-3d-printing-design-guide) ·
[PrintStack3D design guide](https://printstack3d.nl/en/blog/heat-set-threaded-inserts-design-guide) ·
[Sovol, screw bosses](https://www.sovol3d.com/blogs/news/3d-printing-with-heat-set-inserts-design-strong-screw-bosses-that-last)

## Process and testing
✅ Seif: *"their methodology of testing to reach a reliable goal"*.

1. **Several concepts per mechanism.** Compare them on simplicity, ease of manufacture, reliability and number of actuators.
   Write down why each rejected concept was rejected (Aerobotix rejected A–C for clear reasons).
2. **Cheap prototypes first** (MDF, 3D prints), tested on **real game elements**, before the final design.
3. **Choose the simplest concept that works.** Fewer actuators means fewer failures.
4. **Focused CAD of the whole robot** once the concepts are chosen (Aerobotix: about 1 week).
5. **Build step by step, testing each step:** chassis → motors → power wiring → sensors and boards.
   Don't move on until the current step works.
6. **Measurable unit tests with targets** (see the table below). "It works" is not a result; "19 out of 20" is.
7. **Full match runs**, aiming to finish our actions **with time to spare** (Aerobotix: ~60 s out of 100).
8. ◻ **Make every action checkable.** Their software only moved on once the actuator confirmed the action was done.
   Mechanically, that means planning where a sensor goes (limit switch, vacuum sensor, encoder) for each action.

## Test targets (fill in as mechanisms are defined)

| Test | Target | Latest result | Date |
|---|---|---|---|
| _e.g. pick a stone from a quarry stack_ | _≥ 19/20_ | | |
| _e.g. drive 2 m and return, position error_ | _≤ 5 mm_ | | |
