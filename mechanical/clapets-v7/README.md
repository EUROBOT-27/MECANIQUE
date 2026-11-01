# Clapets v7: v6 with reworked door units (Seif)

Copy of [clapets v6](../clapets-v6/README.md) (v5 + real horn + real servo wires). v5 and v6 stay untouched. Owner while
in progress: **Seif**. Design = `fc/v7_fc.py` (dimensions in `class G`); never edit the `.FCStd` by hand.

## Regenerate (FreeCAD 1.1), from this folder, one FreeCAD at a time
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v7_fc.py      # parts, STEP/STL/DXF, FCStd, report.txt (~1 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/render_v7.py  # colours + images
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_v7.py  # full-cycle checks (~10 min)
```

## Changes from v6
### 2026-11-01: door unit body (`A_AILE_D/G`) reworked
- **M3 heat-set inserts everywhere, hole Ø4.6 × 6.5** (measured from a part that fits Seif's inserts). This changes
  every M3 insert hole in the design (`INS3_R/D`), not only the door units.
- **Servo fixing:** 3 × M3 × 8 button head through the flange ears into M3 inserts in the post tops. **No more nut
  pockets on the outer face, no strap (`A_BRIDE_SERVO` removed), no upper block over the ears.** The servo still slides
  in from the front (before the rod), its outer ears in a slot of the outer wall. The ±2 mm mesh slots are gone: the
  mesh relies on the printed centre distance (+ the play of the ear holes).
- **Stiffer:** an **outer wall x 146.5..150, full height**, ties the bottom 608 plate to the top on the rod side (v6: open
  between z 36 and the web). Above the gears (z > 104) the unit is a **closed box**: front wall (gothic-arch underside,
  45° sides, ≤ 20 mm bridge), back wall (y 41..45), inner closing wall. Still printed upright with no support.
- Servo cable channel only at the grommet height (v6: from the bottom plate up), so the outer wall keeps its base.
- Solid volume 175 → 239 g per unit (the print is lighter with infill).
- Checks: rest pose 0 interferences, 0 reserve violations. **Full cycle not run yet.**
- Open: M4 back-wall fixing still uses M4 nuts (M4 insert size unknown); the box top is open (could be closed by the cap).

### 2026-11-01: real Two Trees Bluer V2 parts
- From the GrabCAD printer model (see `../resources/two-trees-bluer-v2-parts/SOURCE.md`): **2020 profiles, V-wheels,
  plain + eccentric spacers, bronze washers, NEMA 17 (body ~38 mm, shaft Ø5), 5×8 coupler, TR8x8 nut** replace the
  boxes/cylinders. The plate stays the exact one from `fc/plaque_papillon_reelle.json` (the STEP plate is B-spline only).
- Real plate gap: **4.5 mm** from the rail face (v5: 4.0) → rails moved 0.5 mm back (`RAIL_YC`); nothing in front of the
  plate moves.
- TR8 nut: its flange is 1.5 mm from one end; flipped so the long body goes up through the shelf.
- Not used: the printer's M5 wheel screws + nyloc nuts (ours are longer, through the head bracket: fasteners step);
  the lead screw stays a plain Ø8 cylinder (cut to length).
- Rest check: 0 interferences; real contacts listed apart ("expected": wheels in the V-slot, screw in the nut / coupler,
  rails seated on the socle).
- **Open question (Seif):** lift travel. The cycle still uses **75 mm** to turn the stack (its corners sweep R ≈ 230 mm
  around the head axis at z 165); Seif mentioned < 20 mm of travel. Decide before cutting the lead screw.

## Check with calipers before the final print
Every number the CAD assumes about a bought part. Measure, then update `class G` (or tell Claude) and regenerate.

| Part | Check | CAD value |
|---|---|---|
| M3 heat-set insert | outer Ø × length (hole is Ø4.6 × 6.5) | fits Ø4.6 × 6.5 |
| M4 insert (if used) | outer Ø × length | not used yet |
| MG996R + round horn | servo bottom → top of the horn disc | 45.7 |
| | horn disc Ø × thickness; boss Ø; screw holes radius | Ø20.8 × 2.5; Ø9.2; r 7.2 |
| | body L × W × H; flange height above the bottom; ear hole spacing | 40.4 × 20.4 × 38; 28; ±24.5 from centre, y ±5 |
| | cable grommet: height above the bottom, how far it sticks out | 3.7–8.3; 5.8 |
| NEMA 17 | body length; shaft length; centring boss Ø | ~38; ~19; Ø22 |
| 2020 profiles | length; centre-to-centre spacing on the printer frame | 350; 80.9 |
| Butterfly plate | thickness; gap rail face → plate | 3.0; 4.5 |
| V-wheel stack | eccentric spacer hex + height; plain spacer length | hex 10, 8.1 + 1.6 spigot; 9 |
| TR8x8 nut | flange Ø × thickness; body Ø; flange hole pattern | Ø22 × 3.9; Ø10 |
| Lead screw | diameter, lead | Ø8, lead 8 |
| Coupler 5×8 | length × Ø | 25 × 20 |
| 608ZZ | Ø × width | 22 × 7 (seats Ø22.2) |
| Ø8 rods | diameter, straightness | 8.0 |
| DP-S30 cup | height (cup face = box face) | 18 |

### 2026-11-01: every screw, nut and insert in the CAD
- Generated in `v7_fc.py` (`fasteners()`), ISO sizes, no threads: parts `FIX_VIS_*` (screws, dark grey), `FIX_ECROU_*`
  (nuts, silver), `FIX_INSERT_*` (inserts, brass, modelled at the hole size), `FIX_TNUT_*`. They are in the interference
  check, so a screw too long or a head with no room shows up. **Bill of materials: end of `CAD_FC/report.txt`.**
- Fixes found by placing them: real **TR8 nut holes at 0/90/180/270°** on r 8 (v5: 45°) → nut-support inserts moved;
  horn-screw holes in both pinions Ø2.2 (were pilot size) + counterbores in the head pinion (the hub flange is 0.5 mm in
  front of it); door unit corner screws **M4 × 8** (× 10 reached into the cap); deeper counterbore for the hub clamp
  screw; wheel bolts on the real wheel axes; eccentric spacer bore centred.
- Expected contacts (listed apart, not counted): horn screws self-tapping into the horns, motor screws into the motor.
- Thin spots to know: middle cup station nuts get ~2 mm of thread (M3 × 16 ends in the nut); corner M4 nuts ~2.6 mm.
- Still nuts (pockets) rather than inserts: arm and gear split clamps, door sheet screws, head servo, hub clamp, stations.
  The door-unit nut pockets are gone (inserts).
- Checks: rest pose 0 interferences, 0 reserve violations. Full cycle not run yet.

| Qty | Fastener (whole module) |
|---|---|
| 16 | M3 heat-set insert (hole Ø4.6 × 6.5) · 2 M4 insert (hole Ø5.6 × 7) |
| 10 | M3 × 8 button head · 10 M3 × 12 button head · 17 M3 × 16 button head |
| 12 | M3 × 10 socket head · 1 M3 × 12 socket head |
| 30 | M3 nut |
| 6 | M4 × 8 button head · 4 M4 nut · 4 M4 × (6 + chassis) to the robot base |
| 4 | M5 × 35 socket head (wheel bolts) · 4 M5 nyloc · 4 M5 × 8 button head + 4 M5 T-nuts (rails) |
| 12 | M2 self-tapping pan head for the horns: 8 × 10 mm (door pinions), 4 × 6 mm (head pinion) |

### 2026-11-01: motor on the floor (the v5 socle could not be assembled)
- v5/v6: the motor hung under a shelf that was part of the socle, with its shaft through the shelf: **impossible to put
  in** (shelf above, base below, shaft in the hole).
- v7: the **motor stands on the floor** on a **1 mm rubber/cork pad** (`REF_PATIN_MOTEUR`, damping + length tolerance) in
  a notch of the socle base (open at the back for the connector). A separate **clamp plate `A_PLATINE_MOTEUR`** sits on
  the motor's top face (4× M3 × 10 into the motor) and on both rail blocks (4× M3 × 12 into inserts); the rails pass
  through it, so it also braces them. Rail blocks bigger (inserts), floor screws moved outside the blocks.
- Assembly: socle → pad + motor → clamp plate → rails down through the plate into the socle → carriage → top tie.
- Coupler and lead screw 11 mm lower: **lead screw 303 mm** (60 → 363). Motor shaft in the coupler: ~13 mm.
- Measure the motor body length before printing: the blocks are 38 mm + pad (`MOT_L`, `MOT_PAD`).
