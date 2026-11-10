# Door unit (`A_AILE` + `A_CAPOT_AILE`) redesign: 4 options

Clapets v7, right door unit (left = mirror). Started 2026-11-10 (Seif + Claude). Status: **Seif prefers B
(spine + cap)**, details to refine before the CAD.

**Seif's answers (2026-11-10):**
- **Option B**, the sturdiest. Keeps the gears (so no direct drive; question 4 is closed).
- **Servo nut windows open on the robot's side** (outer face, x 150).
- **Gears stay open**, easy to see.

**Weight check (B):** the spine + cap come to ~100 g per side (solid PETG) vs 267 g today, so the lift carries
~1.35 kg instead of ~1.7 kg (plate, door units, head, 3 stones at 90 g). The NEMA 17 on the TR8 × 8 (efficiency
~0.5) pushes ~100 N (~10 kg): about 7× margin. The TR8 × 8 does not self-lock: keep the motor powered.

Why: the current body grew fix by fix (walls, fillets, closing walls, windows), so it has no single logic: openings
everywhere, chamfers that start and stop at random, servo nut windows on the wrong faces. We rebuild the door unit
and its cap from scratch. Rod, servo and gears may move; more pieces are fine; any print orientation.

Sketches are rough but to scale, in module mm: **front view** (looking at the butterfly plate from the stack side,
x across, z up from the table) + **top view** (looking down, y toward the stack). Only the right door unit is drawn.
Images: `img/`, made by `make_sketches.py` (`python mechanical/concepts/aile-redesign/make_sketches.py`).

## What every option keeps
| | |
|---|---|
| Plate fixing | 2 × M4 in the plate corner holes, **x 85, z 65 and z 235**. Plate front face y 50.5, plate edge x 95 |
| Bearings | 2 × 608 on the Ø8 door rod (now z 29–36 and 226–233). The top 608 centres whatever holds it, so a cap needs **2 screws on a diagonal**, not 3 |
| Servo | MG996R, 3 ear screws, plain M3 nut under a roof (window face: question 2) |
| Limits | x ≤ 150, height ≤ 350 (now 235), no supports. Arms on the rod at z 39–49 and 212–222 |
| Kept from today | servo cable straight out at the grommet height through one clean slot |

## Shape rules (from the references, apply to every option)
- **3 mm walls everywhere**; thick zones cored out, never solid blocks.
- **Ribs 2 mm** (60–80 % of the wall).
- **One edge rule:** 1 mm chamfer on every outside edge; 45° only where an overhang needs it.
- Bosses: about one hole Ø of wall around each hole. Inserts only where the wall rule fits
  (`../../design-principles.md`), free nuts otherwise, with a straight path for nut, screw and key.

---

## A · Two corner brackets (my pick)
No tall body. A **low bracket** holds the bottom 608, the servo and the gears; a small **high bracket** holds the top
608. Each sits on its own plate corner with one M4 and **hooks over the plate edge (x 95)** so it cannot turn. The rod
and the aluminium plate do the job of the tall body. 2 printed parts / side, both print flat.

![Option A](img/option_A.png)
- Good: fewest and simplest parts, flat prints, lightest, everything open for assembly; both brackets share one look.
- Watch: rod alignment comes from the plate holes (both brackets use x 85, so they line up if the plate is accurate);
  gears and servo exposed; each bracket hangs on one M4 + an edge hook (test that it does not rock).

## B · Spine + cap
One tall part built as a clean **C-channel**: back wall on the plate + outer wall at x 147–150, 3 mm everywhere, tied
by three shelves (bottom 608, servo roof, top), big regular windows to keep it light. A flat **cap with 2 screws**
holds the top 608. 2 printed parts / side; the spine prints on its back (~210 mm).

![Option B](img/option_B.png)
- Good: both bearings in one rigid part (alignment does not depend on the plate); closest to today; clean, uniform.
- Watch: tallest print, most plastic; servo and gears inside the channel (assembly from the open front only); rod
  goes in from the top before the cap.

## C · Brackets, drive on top
Like A, but the **servo hangs upside down in the high bracket** with the gears just under it (z ~168–176, clear of
the top arm). The low bracket shrinks to a small bearing block on the bottom plate corner.

![Option C](img/option_C.png)
- Good: the bottom stays tiny (more room for the chassis floor and the base); servo and gears away from the table.
- Watch: the servo hangs on its ears; longer cable route; gears at z ~170 must clear the arms when the door opens.

## D · Direct drive, no gears
The servo stands **right under the rod, turned 90°**, and drives it through a printed coupler. The 20T, the 28T and
its clamp disappear. The bottom 608 moves above the coupler, so the **low arm moves up to z ~100**.

![Option D](img/option_D.png)
- Good: fewest moving parts (no gears, no 28T clamp, no backlash); slimmest unit; door angle = servo angle.
- Watch: loses the ×1.4 gear, so **about 30 % less squeeze** on the stack (MG996R ~1.1 N·m straight on the rod
  instead of ~1.5); low arm + door sheet holes move up; the coupler carries the servo spline (needs a good fit).

---

## B in detail (v2, rough): spine + cap along the load paths
Seif (2026-11-10): organic shape from the load paths. Chosen method: **design along the load paths by hand, then one
FEM check** (FreeCAD FEM + CalculiX, already installed) and thin out what carries nothing. Topology optimisation
tools (SolidWorks Topology Study, BESO for FreeCAD) were looked at: they ignore FDM rules (overhangs, layer
direction) and assembly access, so their result would have to be redrawn anyway; the loads here are small
(gear force ~90 N, door squeeze a few tens of N), so **stiffness, printability and access** drive the shape.

![Option B detail](img/B_detail.png)

Made by `make_sketch_B.py`. What the sketch shows:
- **C-section spine, 3 mm walls:** a **keel on the plate** (x 66–95, carries both M4s), a **back wall behind the
  servo** (y 38–41, beyond the plate edge) and an **outer wall** (x 147–150). Front open: gears visible, servo slides in.
- **Load paths:** two **curved ribs** (S-curves) in the back wall above the gears tie the bottom pod (bottom 608 +
  servo cradle, one stiff block so the 30 mm gear distance cannot move) to the top pod (top 608). Every window has a
  **pointed-arch top** (45° sides) so it prints upright with no support. The keel gets one long window between its
  two M4s.
- **Bottom shelf** (z 27–36): the bottom 608 boss and the servo floor in one plate. **Top shelf** (z 218–226) + **flat
  cap** (z 226–236, 2 screws on a diagonal) with the top 608. No rib on the cap: a 10 mm cap spanning ~30 mm under
  ~50 N bends ~0.07 mm.
- **Servo: 3 screws** (M3 + nut under a roof). The 2 outer ears have their **nut windows on the outer face** (robot's
  side); the inner ear (y 57) has its nut window **toward the front** (the plate and the keel block the other sides).
  The 4th ear (inner, y 47) sits on the butterfly plate's edge (plate to x 95, y 47.5–50.5): no room for a post, so
  no screw there (same as v5–v7).
- **Cable slot** in the outer wall at the grommet height, open to the front (servo slides in).
- **Keep-out:** no wall near the rod at the two arm heights (z 39–49, 212–222): the arms and their clamps swing there.
- **Print: upright** (Seif asked, 2026-11-10; why upright beats lying on the bed):
  - Both 608 seats and the rod bore are on one vertical axis: upright they print round and coaxial. Lying down they
    become horizontal holes (slightly oval, need a teardrop top): bad for a bearing press fit.
  - The loads are horizontal (gear force ~90 N, door squeeze) and enter in the bottom and top pods, so they run
    **along** the layers. The spine is fixed to the plate at both ends (M4 z 65 next to the bottom bearing, M4 z 235
    level with the top one): little bending along its length, so little load **across** the layers.
  - Protect the layer lines anyway: fillets where walls meet the shelves, 4 perimeters, ~40 % infill.
  - Cost: ABS warps on a ~210 mm tall part: enclosed printer (PLA is fine).
- **Assembly order:** servo (with the 20T on its horn) slides in under the lip → 2 ear screws → 608 bottom → rod down
  through the 28T, the arms and the spacers → top 608 in the cap → cap (2 screws on a diagonal, free nuts under the
  top shelf, reached through the windows).

Seif's answers (2026-11-10): 3–4 servo screws, no lip (→ 3, see above); curved ribs; no cap rib; print upright
(explained above). Next: build B in the FreeCAD generator, then one FEM check (FreeCAD FEM + CalculiX).

## Questions for Seif
1. **Which option, or which mix?** A/B decide the structure, C/D where the drive sits (e.g. A + D).
2. **Servo nut windows:** which face should they open to: outer face (x 150, reachable from the robot's side),
   underneath, or toward the plate?
3. **Gears:** open (easy to see and grease) or under a light guard?
4. **Direct drive (D):** is 30 % less squeeze OK for a 90 g cardboard stack, or keep the gears?

## References used
- Topology optimisation: [BESO for CalculiX/FreeCAD](https://github.com/calculix/beso),
  [FreeCAD forum thread](https://devtalk.freecad.org/t/topology-optimization/13334),
  [SolidWorks Education Premium incl. topology (UCSD listing)](https://blink.ucsd.edu/technology/computers/software-acms/available-software/solidworks.html),
  [nTop: overhang constraint in topology optimisation](https://ntopology.com/blog/topology-optimization-additive-manufacturing-constraints-in-ntop-platform/)
- Enclosure / housing design for 3D printing: [Hubs](https://hubs.com/knowledge-base/enclosure-design-3d-printing-extensive-guide),
  [Sculpteo](https://www.sculpteo.com/blog/2017/06/14/3d-printed-enclosures-learn-the-basic-design-guidelines/),
  [FacFox](https://facfox.com/docs/?p=101808), [Predictable Designs](https://predictabledesigns.com/enclosure-never-mass-produced/)
- Printed servo gearboxes with 608 output bearings: [MakerWorld MG996R planetary](https://makerworld.com/models/2901002),
  [MakerWorld MG996R mount](https://makerworld.com/models/788026), [Instructables printed servo](https://www.instructables.com/3D-Printed-Servo-Motor),
  [CGTrader high-torque servo gearbox](https://www.cgtrader.com/3d-models/industrial/industrial-machine/3d-printable-high-torque-servo-gearbox-version)
- Inserts and nuts: `../../design-principles.md`
