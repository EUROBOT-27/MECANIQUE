# grail2: Baha's lead-screw Grail lift ("essai mecanisme vis ecrou 1.0")

> **Where we are (2026-11-19, Maatoug + Claude)**
> - The SolidWorks assembly from Baha is rebuilt in FreeCAD: `CAD_FC/GRAIL2.FCStd`. Run `fc/grail2_fc.py` to regenerate
>   it; it also writes the motion check (`CAD_FC/grail2_report.txt`). Slider study: `fc/sliders_fc.py`.
> - **2026-11-20: translation guide added** (`ADD_*` parts, our addition, not in Baha's file): 1 Ø8 rod behind the
>   screw + 2 SCS8UU blocks on a printed plate + a printed top plate with a 608 bearing on the screw top. Fixes
>   problems 2 and 3 below. Lift travel now **207 mm** (−44 … +163: the blocks meet the top plate), flip unchanged.
> - The motion works: **flip −44° … +156°**. **The 180° flip is blocked**: the magnet hits the lead screw from +158°.
> - Still open (details below): taller than 350 mm whatever the mounting; the coupling has Ø5 bores for an Ø8 screw;
>   lead 8 not self-locking; 1 mm walls on the nut mount.
> - The Grail and the robot around the mechanism are not modelled yet.
> - **Not a decision.** Mechanical is Seif's area; this is one Grail-lift variant among others (see `../grail-lift/`).

## What it is
- A NEMA17 stands under a 3 mm plate (`support fixation stepper`) and drives a vertical **T8 screw (300 mm, lead 8)**
  through a CXJH D25 clamp coupling.
- A T8 brass nut is screwed under `piece de fixation sur l ecrou` (the nut mount). The **Ø5 × 60 pin**
  (`tige articulation vis ecrou`) joins the nut mount to the **`bloc de rotation 180`**: an open box with a floor,
  a back wall, a small lid, and a tall +x wall that carries the pivot.
- An MG996R lies in the bloc, held by a "multipurpose bracket". It turns a **U bracket** (`support en u`) through a
  round horn. The U carries a **5 kg electromagnet** (Ø25 × 20). On the other side of the U, a Ø6 pin turns in the
  bloc's Ø6.3 hole.
- At flip 0 the magnet points out horizontally, 110 mm from the screw axis. That suggests a side grip on the Grail.

## Files
| Path | What |
|---|---|
| `sw/` | Baha's SolidWorks files as received: the assembly + 6 parts. `essai mecanisme vis ecroue 1.0.SLDPRT` is only a sketch and is not used |
| `CAD_FC/STEP/sw_export/` | Export done by `tools/solidworks/dump_asm.cs`: STEP files of every part + the assembly, and `sw_dump.json` (component transforms, all 24 mates with their geometry, part masses and dimensions) |
| `fc/g2_common.py` | Frame, paths, joints (lift / flip / screw turn) |
| `fc/grail2_fc.py` | **Generator + headless motion check** → `CAD_FC/GRAIL2.FCStd`, `joints_grail2.json`, `grail2_report.txt`, `STEP/GRAIL2.step` (~3 min) |
| `fc/sliders_fc.py` | Slider panel in the FreeCAD GUI: lift, flip, a planned sequence + Play, collision check at the current pose |

Run (FreeCAD 1.1, from this folder):
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/grail2_fc.py
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/sliders_fc.py
```
Never edit the `.FCStd` by hand: change the generator and re-run it.

**Frame:** x = along the flip axis, y = the side the magnet points to (0 on the screw axis), z up.
**z 0 = bottom of the NEMA17**, because the assembly does not say how the mechanism is mounted in the robot.

### What is exact and what is not
| Prefix | Source |
|---|---|
| `SW_*` | Baha's parts, exact (bloc, nut mount, stepper support, screw, pin) |
| `REAL_*` | Bought-part models that were in the assembly (coupling, magnet, a 4-pad servo arm) |
| `REF_*` | Files missing from the assembly (they were in Baha's Downloads folder). Replaced by our models (NEMA17, T8 nut from clapets-v5; MG996R from grail-lift) and placed with the mate geometry stored in the assembly |
| `APPROX_*` | Missing, and we have no model, so rebuilt to fit the mates. **Shape assumed:** U bracket (2.5 mm sheet, 36 wide, base 40 mm from the axis), round horn, servo bracket (2 posts) |
| `ADD_*` | **Our addition (2026-11-20): the translation guide** (see below). Lab parts at catalogue size + printed parts |

### Translation guide (added 2026-11-20)
| Part | What | Where (grail2 frame) |
|---|---|---|
| `ADD_GUIDE_ROD_D8` | Ø8 smooth rod (lab, ~6 in stock), **cut 319 mm** | behind the screw, y −32, z 47 … 365.6 |
| `ADD_SCS8UU_x2` | 2 × SCS8UU linear blocks (lab has 3), vendor model `../resources/linear-motion/vendor/SCS8UU.step` (from Maatoug's SCS8UU.SLDPRT: 34 × 22 × 30, 4 × M4 on 24 × 16, holes face on the plate) | on the guide plate, one above the other (60 mm of guiding) |
| `ADD_GUIDE_PLATE_printed` | printed plate 30 × 10 × 60, between the bloc's ears (bolted to them and to the back of the nut mount) | y −21 … −11, moves with the carriage |
| `ADD_SK8_rod_foot` + `ADD_SK8_BRACKET_printed` | **SK8** from the lab (vendor model `../resources/linear-motion/vendor/SoporteVertical_SK8.step`, from the Inventor file) holding the rod bottom, bolted (2 × M5) to a printed L bracket that stands on the stepper support | z 43 … 61, behind the rod (y −58 … −19) |
| `ADD_TOP_PLATE_608_printed` | printed top plate: rod top + a **608 bearing on the screw top** (the screw is no longer held only by the coupling) | z 357.6 … 365.6 |

One rod is enough because the screw itself is the second line: rod + screw stop the turning, and the two SCS8UU
(60 mm apart in length) take the tilting load of the magnet arm. The 3rd SCS8UU stays spare. If the screw rubs in the
nut, add a 2nd rod on the other side of the screw (same parts, the 3rd block).

To make the model exact, ask Baha for: `support en u`, `multipurpose bracket (1)`, the servo horn `[3879]…`, and his
`Nema 17`, `T8 nut`, `Tower Pro MG 996R` files.

## Motion check (from `CAD_FC/grail2_report.txt`)
| | |
|---|---|
| Lift travel | −44.0 … +163.0 mm from the model pose = **207 mm = 26 screw turns** (bottom: nut on the coupling; top: the SCS8UU blocks meet the top plate). Without the guide it was 275 mm (nut at the end of the thread) |
| Flip free arc | **−44° … +156°** (0 = magnet out, +90 = up). At +158° the magnet hits the screw. At 180° it also overlaps the bloc lid / nut-mount top by 0.5 mm. The −44° stop is between two APPROX parts (U base vs servo bracket), so it is not reliable |
| Height | screw top z 365.6; carriage top z 204.1 at the model pose, up to z 240.8 when the magnet points up |
| Sequence | model pose → bottom → lift +109 (the highest pose under 350 with the motor on the table) → flip +156 → −44 → back. Replayed with collision checks: **no collision** |
| Clashes at rest | coupling × stepper support 7.5 mm³ (see 4 below); everything else touches only where parts are fastened |

## Problems found (for Baha / Seif)
1. **Over 350 mm whatever the mounting** [GR F.3]. From the motor bottom to the screw top is 365.6 mm. Even with the
   motor standing on the table, the fixed screw is 15.6 mm too tall. The robot's floor clearance makes it worse. Fix:
   a screw ≤ ~280 mm, or put the motor next to the screw (belt) or above it.
2. ✅ *Fixed by the added guide (2026-11-20).* **Nothing stops the carriage from turning with the screw.** The assembly has no rail, rod or slot to guide the
   bloc, and the SW "Parallel1" mate does that job only virtually. On the real robot the nut + bloc would spin
   instead of rising. A guide is needed: a 2020 column + slider shoes as in grail-lift v3, or a Ø8 rod + bushing.
3. ✅ *Fixed by the added top plate + 608 (2026-11-20).* **The screw is held only by the coupling.** No 608 bearing at the top, and 300 mm sticks out. The magnet (+ Grail)
   pulls 60–110 mm off the screw axis, so the screw bends and wobbles. A guide (2) that takes the moment + a top bearing.
4. **Coupling `CXJH-C-D25-d5-e5` has Ø5 bores on both sides.** The Ø8 screw does not fit (SW let a concentric mate
   join r 2.5 to r 4). Use a **5 → 8 coupler** (we have 2 from the Ender 📦). The coupling also sits 0.5 mm down
   inside the Ø25.3 hole of the support plate. Its clamp screws (Ø26.3) rub there: raise it 1 mm or open the hole to Ø28.
5. **Lead 8 mm/turn is not self-locking.** When the stepper is not powered (e-stop, end of match), the carriage
   slides down. Use a lead-2 screw (also 4× the force, 4× slower) or keep the motor powered. With an e-stop it will
   drop anyway.
6. **The 180° flip is not possible as drawn** (Motion check above). Once a Grail hangs on the magnet, the back half of
   the arc is blocked much earlier: the Grail would be where the screw is. To decide once we know how the Grail
   must end up (L4 on our roof, CDC in `../grail-lift/docs/CDC.md`).
7. **The nut mount has 1 mm walls** (Shell 1 mm). The whole carriage hangs on a Ø5 pin through 1 mm walls and 4 M3
   in a 1 mm floor. Too thin in ABS [D-023]: use ≥ 3 mm walls.
8. The **4-pad servo arm** (`mg996_arm_4pad`) has no mate: it floats 3.2 mm off the servo axis, outside the U, and
   touches nothing. It looks like a leftover (magenta in the model, left out of the checks).
9. The SW assembly opens with errors because of the 6 missing files, so their mates are stale. For example, the U's
   pin face is drawn 0.3 mm inside the bloc wall.

Not checked yet: the Grail itself, where the mechanism sits on the robot (`../robot/fc/layout.py`), perimeter, the
wiring of the magnet through the flip.
