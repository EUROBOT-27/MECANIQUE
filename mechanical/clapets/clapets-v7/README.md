# Clapets v7: v6 with reworked door units (Seif)

> **Where we are (2026-11-13): module A has PASSED CAD → printing + testing phase.**
> - **Module A (lift + doors) CAD: closed for the first prototype.** Door unit + cap rebuilt (option B, D-022), every
>   fastener checked, ABS tolerance coupons done and fed back (2026-11-12), insert holes per D-025.
> - **Now: printing module A in ABS** on the Bambu X1 Carbon: sliced plates in `CAD_FC/STL/PRINT.3mf`
>   (`PRINT_plate_1/2.gcode.3mf`). Then assemble and test. CAD changes from here on come only from what the test shows.
> - Assembly guide PDF is out of date for the cap tab, the plate teeth, the arm nut pockets and the top crossbar.
> - Done before: ABS tolerance tests → [`tolerance-tests/README.md`](tolerance-tests/README.md) (D-023).
> - **In parallel:** module B (suction head) with Maatoug in `../clapets-v8/`; it must take module A from here.
> - **Assembly guide (v1):** [`assembly/clapets_v7_moduleA_assembly.pdf`](assembly/clapets_v7_moduleA_assembly.pdf),
>   15 A4 sheets, made from the CAD. Regenerate after the tolerance tests (see `assembly/README.md`).
> - Concept history of the door unit: [`../../concepts/aile-redesign/README.md`](../../concepts/aile-redesign/README.md).

## Effort to reach "CAD passed" (estimate, 2026-11-13)
Rough figure from commit and log timestamps: time at the PC, not focused work time. Printer and FreeCAD run time
are not counted. Baseline for planning the next modules.

| Who / what | When | Hours |
|---|---|---|
| Maatoug: clapets v1 → v5 design (base of v6/v7), mostly on his PC before the hub | up to 2026-10-29 | ~15–25 (guess, to confirm with Maatoug) |
| Seif: v6 + v7 (real horn, wires, Two Trees parts, every fastener + BOM, motion check) | 2026-11-01 | ~8–9 |
| Seif: caliper values, door unit rebuilt (4 concepts, option B), tolerance coupons, assembly PDF, door sweep + GIFs | 2026-11-09 → 11-10 | ~10–14 |
| Seif: switch to ABS (D-023), print + measure the coupons | 2026-11-10 → 11-12 | ~2–3 |
| Seif: fixes from the coupons, insert holes (D-025), top crossbar without 608, slicing | 2026-11-12 → 11-13 | ~10–12 |
| **Total** | | **~45–65 person-hours** (Seif ~30–38 h) |

Copy of [clapets v6](../clapets-v6/README.md) (v5 + real horn + real servo wires). v5 and v6 stay untouched. Owner while
in progress: **Seif**. Design = `fc/v7_fc.py` (dimensions in `class G`); never edit the `.FCStd` by hand.

## Regenerate (FreeCAD 1.1), from this folder, one FreeCAD at a time
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v7_fc.py      # parts, STEP/STL/DXF, FCStd, report.txt (~1 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/render_v7.py  # colours + images
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_v7.py  # full-cycle checks (~10 min, only when asked)
set V4_MODE=doors & "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_v7.py  # FAST door sweep (~2.5 min)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/door_gif_v7.py  # door module GIF, top + 3D split view (~1 min) -> CAD_FC/motion/doors.gif
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/cycle_gif_v7.py # module A cycle GIF (no module B), side + 3D (~1 min) -> CAD_FC/motion/cycle_moduleA.gif
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/fastener_check_v7.py  # every screw/nut/insert: numbers + cut views (~15 min)
```
**Fast door sweep (`V4_MODE=doors`, 2026-11-10):** right door only (the left is its mirror), carriage down, no stack.
Only the door's moving parts (arms, door sheet, 28T, pinion, their screws) move, checked only against the parts that
come inside their swing; the real travel (open −38 … fold +90) + 5° margin in 2° steps, refined to 0.25° at each
contact. Report: `CAD_FC/motion/door_sweep_report.txt`. Last run: **no contact over the travel**; the folded door
sheet meets the head's MDF carrier only past +93.25° (3.25° margin beyond the +90° fold).

`fastener_check_v7.py` writes `CAD_FC/fastener_check/report.txt` (thread length in the nut/insert, hole gaps, head
seat, key access, wall around each nut/insert) and a cut view through each screw (`s_NN_*.png`). Its "nothing to screw
into" for the horn screws and "key blocked" / "head bears on nothing" next to the motor and V-wheels are false alarms
(those bought-part models confuse the inside test).

**Material (D-023, 2026-11-10):** coupons and real parts in **ABS on the Bambu X1 Carbon** (enclosed). The generator
still uses PLA density for every printed part (`RHO_PRINT` = 1.24 g/cm³), so its reported masses are ~16 % high;
the figures below are converted to ABS (≈ 1.045 g/cm³). Fits come from the ABS coupons (ABS shrinks more than PLA).
See `../design-principles.md`, "Print materials".

## Printing module A (2026-11-10)
- **Tolerance tests first:** `tolerance-tests/README.md` (10 coupons, ~127 g ABS at 20 % infill). Report the best variants, the CAD is
  updated, then the real parts.
- **Filament for module A** (both sides, ABS, from the CAD solids with 4 perimeters): **~465 g at 40 % infill**
  (415 g at 20 %, 605 g solid), about 184 m of 1.75 mm. Plan **~510 g** with skirts, brims and a failed start; one
  1 kg spool covers module A + the tests. Biggest parts: door unit body ×2 (~101 g each), socle (~55 g),
  top crossbar (~35 g), nut support (~31 g). Brim on the door unit bodies (tall, ABS warps).

## Changes from v6
### 2026-11-12 (late): top crossbar without a 608 (Seif)
- **Top crossbar (`A_TRAVERSE_HAUT`):** no 608 at the top any more. The lead screw passes through a plain **Ø15 hole**
  (free top end). The 608 seat and its 2.8 mm roof are gone; the part is
  solid there (61.4 → 65.8 g, PLA density). BOM: one 608ZZ less.
- Print plates sliced for the Bambu X1 Carbon: `CAD_FC/STL/PRINT.3mf`, `PRINT_plate_1.gcode.3mf`, `PRINT_plate_2.gcode.3mf`.

### 2026-11-12: fixes after the ABS coupons (T8, T9) + plate form lock (Seif)
- **Insert holes (D-025):** the ABS coupon T6 pushed plastic into the insert's thread. Every M3 insert hole now follows
  the reference drawing in `../design-principles.md`: **Ø5.4 × 7, mouth cone Ø6.2 × 1.5** (was Ø4.6 × 7 + 0.5 × 45°).
  Socle ×4, cap tabs ×2 (and the head bracket ×4, module B). No new coupon.
- **Coupon results (ABS, Seif):** T1 608 seat: Ø22.2 (variant 2) good. T2, T4, T5, T7, T10: good, no change. T3 / T8 /
  T9: the changes below. T6: see above.
- **Pinion (`A_PIGNON_PORTE_20T`):** M2 horn screw holes Ø2.2 → **Ø2.5** (`HORN_SCR_R`): too tight in T9.
- **Servo ear nuts (3 posts):** hex recess AF 5.7 → **5.9** (`POST_HEX`) = 0.2 per side on the 5.5 nut (was 0.1). The
  wall between the recess and the servo pocket goes 0.95 → 0.85 mm.
  The 2 outer-ear nut windows are now **one window** (y 43.7–60.3): the 3.4 mm wall between them is gone; its ceiling is a
  16.6 mm bridge (was 2 × 6.6).
- **Inner ear (3rd servo screw):** key opening above the ear 15 → **33 mm** tall (`EAR_IN_H`); the keel window is
  narrower (x 71–91 → **71–87**), so 5.5 mm of keel stays between them (was 1.5).
- **Outer ear opening:** the strip in front of it was 2 mm. The outer wall now comes forward to y 69 (`OWB_Y1` 66 → 69,
  28T still 3.2 mm away), so the strip is **5 mm**. The ear tip goes 1 mm into the wall (x 148), so a 3 mm groove at ear
  height lets the servo still slide in from the front.
- **Arms, door sheet screws:** the nut now sits in a **pocket in the arm tab's inner face** (6.0 × 6.9 × 2.8, same as the
  28T clamp pockets: it can't turn), walls 1.75 / 1.55 mm; screws **M3 × 12** (were M3 × 16 with the nut in free air).
- **Web:** the local rib beside the inner ear (z 57–107, with steps at its ends) now runs the **full height**: the web's
  inner face is one flat face (x 100.5).
- **Cap → body, 3rd screw from the front:** a tab on the cap's front face (x 67.5–78, z 210–242: full cap height, sunk
  0.5 into the cap so it is one solid; chamfers only on its 2 outer edges) hangs down over the keel's front face (below z 226,
  4.2 thick); **M3 × 10 button head** through it into an **M3 insert set horizontally** in the keel front face
  (x 72.75, z 218; walls 3.75 to the side, 4.0 to the plate face). Set the insert with the body lying on its back.
- **Form lock on the butterfly plate:** 2 flat teeth in the plate's plane (y 47.8–50.5), x 67–76, **0.3 mm** from the two
  diagonal edges of the plate's wing: the bottom tooth on the body (below the lower edge, from the bed), the top tooth
  on the cap (above the upper edge). The wing sits between them, so the door clamp reaction (outward) and the stack
  weight (down) bear on the plate's edges instead of only on the M4s' grip. Edges fitted on the real plate outline
  (`plate_diag()`; the outer edge between the lobes is a concave arc, not used).
  **Mounting is unchanged:** the teeth sit outside the plate outline, so the unit still goes onto the plate straight
  from the front, and the cap still comes down from above. Then **push the unit outward in its M4 slots until the
  teeth touch** and tighten the 2 M4.
- Masses (PLA figures from the generator): body 146 → 157 g, cap 42 → 43 g (ABS ≈ ×0.84).
- Rest check: 0 interferences, 0 reserve violations. Fast door sweep clean after the outer wall change (run before the
  tab and teeth, which are far from the doors). Not re-run: full motion check, fastener check, images,
  assembly guide (the guide's cap and plate steps are now out of date).

### 2026-11-10 (4): no M4 inserts, no motor pad (Seif)
- **Nut support (`A_SUPPORT_ECROU`): M4 nuts instead of M4 inserts** (none in stock). Wall 8 → 5 mm (`SUP_WALL`),
  nut pockets in the wall's back face (7.4 × 8.4 × 3.4). The 2 screws are **the printer's own M4 × 8** (they held
  the Y belt clamp under this same plate): plate 3 + skin 1.6 + nut 3.2 = full thread. M4 × 10 also fits.
- **No pad under the motor** (none in stock): the motor hangs from the clamp plate by its 4 screws, 1 mm air gap
  under it (`MOT_PAD` stays 1.0 as that gap). `REF_PATIN_MOTEUR` removed.
- Module A now has **only 4 heat-set inserts** (M3, socle). Tolerance coupon T6 is M3-only.
- Assembly guide: steps 1, 2, 5 updated; layout reduced to title, content and page number.
- Rest pose: 0 interferences, 0 reserve violations.

### 2026-11-10 (3): door unit + cap rebuilt as option B (Seif)
Concept, sketches and reasons: `../../concepts/aile-redesign/README.md`. `aile()` and `capot_aile()` rewritten from scratch
(the old box, closing walls, arch walls, cap bosses and nut slides are gone). Kept: plate holes, both 608 seats, servo place.
- **Spine (`A_AILE`), C-section, 3 mm walls, printed upright, no support:** keel on the plate (x 66–98, y 50.5–60.5,
  carries the bottom plate M4), web (x 95.2–98) to a **back wall behind the servo** (y 34–37: the 20T tips reach y 38.25),
  **outer wall** (x 147–150, y 34–66), bottom shelf (z 27–36: bottom 608 + servo floor), top shelf (z 218–226, y ≤ 63:
  the top arm swings in front of it). Front open: gears visible, servo slides in from the front.
- **Windows with rounded corners** (flat top ≤ 20 mm bridge): keel (between the M4 rows), back wall and outer wall
  (z 112–212). No ribs.
- **Servo: 3 screws** M3 × 8 + nut in a hex recess under a 1.6 mm roof. Outer 2 nut windows open on the **robot's side**
  (x 150), inner 1 toward the **front**. Ear slots 6.6 tall, open to the front: room for the button heads and a
  **ball-end hex key from the front at an angle** (straight from above is blocked by the top shelf / keel). Cable slot
  as before.
- **Cap (`A_CAPOT_AILE`) z 226–242:** holds the top 608 and **the top plate M4** (z 235, now fully covered), so the top
  bearing goes to the plate by the shortest path. 2 × M3 × 16 on a diagonal into the top shelf, nuts in pockets under
  the shelf. Pocket from below (3 mm skins), printed upside down.
- **Plate M4s:** M4 × 16 from behind the plate, ±1.5 slot (door centering), nut in a pocket in the keel / cap front
  face (the pocket keeps the ±1.5 slide).
- **Servo screw access:** each ear has an opening from the ear up to just under the gears (z 77–95.4), open to the
  front, and for the 2 outer ears on the robot's side too: fingers to start the screws, a hex key at an angle. Inner
  ear: 4.5 mm flange entry + an opening 15 mm tall around the screw, open to the front; behind it the web stays whole
  and gets a **rib** (2.5 mm thicker, x 99–100.5, z 57–107) that ties the keel to the back wall around the opening.
- **One outline, edges continue into the cap:** the walls are one C-section outline (`spine_loop`), 1 mm chamfer on
  every outside corner, small fillet on the inside ones. The top shelf and the cap share one outline (`top_loop`), so
  the cap's edges and chamfers continue the body's (as for the socle and the motor plate). The web moved to x 96.2 so
  its inside fillet stays clear of the plate edge; keel to x 99.
- **Cable exit:** the channel inside the posts stays open to the front (the servo slides in), but the hole through
  the outer wall is grommet-size (9 mm wide): the wall keeps ~10 mm at the front instead of 2 mm. Thread the connector
  through the hole before sliding the servo in.
- **No inserts left in the door unit.** Mass (solid PLA): spine 146 g + cap 42 g = 188 g per side (was 267 g).
- Rest pose: 0 interferences, 0 reserve violations. Motion check and FEM not run yet.

### 2026-11-10 (2): nut support, motor plate, arm ↔ door sheet, rod clamps (Seif)
- **`A_SUPPORT_ECROU` symmetric:** the locating pin in the butterfly plate's 3rd hole (x 25.8) and the 4.5 mm of wall that
  carried it are gone (from v5; the 2 M4 screws already fix the part). `PIN_X` is no longer used.
- **`A_PLATINE_MOTEUR` flush with the socle's rail blocks:** same outline and square edges as the blocks under it
  (y 19..55, x ±56.45), plus the motor's 42 mm square face in the middle (its 4 screws). It no longer sticks out at
  the back. The socle is unchanged.
- **Arm ↔ door sheet: M3 × 16 + plain nut** (no inserts). One screw 7 mm under and one 7 mm over each arm (`ARM_SC`),
  so the nut sits in free air on the tab's inner face with room for a 5.5 wrench or pliers. Tabs 8 deep (`TAB_D`),
  `FL1` (27, 61), `FL2` (200, 234). Door sheet holes (±1.5 slots) follow: **new DXF**.
- **Parts clamped on the rods:**
  - Arms: the hub covered the mouth of the clamp's nut pocket (the nut could not go in): the pocket now runs 8 mm out
    to free air (`nut_ext`). Clamp screw M3 × 12 (the × 10 ended inside the nut). Key path: 20 mm counterbore (11-08).
  - 28T gear: its 2 nut pockets overlapped (screws 6 apart in a 14 mm hub): hub **22** tall (`HUB28_H`), screws
    **11** apart (`hub28_screws_z`): 2.2 mm of plastic above the gear, 4.1 between the pockets, 2.2 at the top. M3 × 12.
    Nut pockets run 4 mm out through the Ø20 hub (it bulged past the lug face over the pocket mouth); the screw-head
    holes run 6 mm out the same way (`cb_ext`). Head holes on both rod clamps Ø6.6 (was 6.0) for the Ø5.5 head.
  - Clamp nut pockets (arms + 28T) roomier: 6.0 × 6.9 for the 5.5 × 6.35 nut (`CLAMP_NUT_W/L`; printed holes come
    out small). Other pockets unchanged.
  - Head hub (module B): not changed (Maatoug's v8).
- Rest pose: 0 interferences, 0 reserve violations. Motion check not re-run.
- BOM now: 14 M3 inserts, 32 M3 nuts (see `CAD_FC/report.txt`).

### 2026-11-10: insert walls ≥ 1.8 from the real insert Ø6.0 (Seif)
Measured from the insert's real Ø6.0 (not the hole), the walls were 0.6..1.1. Fixes in `v7_fc.py`:
- **Door servo posts (3 per door unit): inserts → M3 nuts.** The servo body is 4.3 mm from the ear hole, so an
  insert could never get more than ~1.1 mm there. Now: a 1.6 mm **roof** under the ear, a **hex recess** under it
  (AF 5.7, snug, flats facing the servo), and a **window below, open to the front**: push the nut up into its recess,
  slide the servo in, M3 × 8 from the top. The nut clamps the ear on the roof; the plastic only stops it turning
  (`POST_ROOF`, `POST_HEX`, `POST_HEX_D`, `POST_WIN`). Inner post 1 mm wider on its free side.
- **Cap screws (3):** the first moved into the corner of the side wall and the front wall (71, 61) (was (70, 69),
  0.5 mm wall); the two in the 8 mm front wall moved 1 mm into the box (y 60) with a boss behind them inside the box
  (`cap_bosses`, 45° underside). The cap is 3 mm longer at the back over the box (x ≥ 95) so the counterbores keep a
  full edge. Walls **2.0**.
- **Arm tabs (door sheet screws):** `TAB_SC` 4.0 → 4.8, lower tab `FL1` (37, 53) → (36, 54) (both 18 tall),
  `TAB_Y0` 128 → 127 (tab 9.5 thick). Walls **1.8**, 2.4 between the two inserts. Door sheet DXF follows.
- Not changed: head servo posts (module B, 0.9 mm: same problem, the same nut + roof fix applies → Maatoug's v8).
- Rest pose: 0 interferences, 0 reserve violations. Motion check not re-run (arm tabs: +1 mm in z and y, they sweep
  at ≥ 51 mm from the rod, the door unit body reaches ≤ 45).
- Pictures of every insert in its hole: `fc/insert_views_v7.py` → `CAD_FC/fastener_check/inserts/`.

### 2026-11-09: caliper values (Seif)
- **Servo horn disc top: 47.4 mm** above the servo bottom (measured twice; the GrabCAD model said 45.7, `SV_HORN`).
  Door gears (pinion + 28T) move up 1.7 together: full 8 mm mesh kept. **Head pinion** (module B): it sits on the horn
  inside the gear plane (y 94.5..102.5), so its face width drops from 5.8 to **4.1 mm** against the 8 mm 30T. To get
  it back, the gear plane must move forward (e.g. thinner cup-station flange); module B, Maatoug's v8.
- **Motor body 37.0 mm** (`MOT_L`, was 38): the motor is the printer's own Z motor, taken from its model (back face to
  front face 37.0, boss Ø22 × 1.9, shaft 21.9 from the front face). The clamp plate now sits on the motor face (z 38).
  The shaft tip stays at z 59.9, 0.1 mm under the lead screw (z 60) in the coupler: unchanged.
- **M3 inserts: outer Ø5.6..6.0 × 6.** Hole Ø stays 4.6 (proven on a print). The fastener check now measures
  the insert walls from Ø6.0 (they were measured from the hole, ~0.7 mm too optimistic).
- Confirmed as in the CAD: horn disc Ø × thickness, servo body + ears + grommet, TR8 nut, 2020 profiles, butterfly
  plate, lead screw Ø8 lead 8, coupler, 608ZZ, Ø8 rods, door sheet 3 mm. Foam pads: none in hand, 8 mm kept.
- **Insert holes (all 28 M3 + 2 M4): 0.5 × 45° lead-in chamfer** at the mouth (mouth Ø5.6 = the insert's narrow end,
  so it starts square) and **blind depth 7.0** (= insert 6 + 1 for melted plastic). One helper, `ins_hole()`, makes
  every insert hole (`INS_CH`). Checked: no hole breaks through a wall. Rules + sources: `../design-principles.md`.
- Rest pose: 0 interferences, 0 reserve violations. Motion check not re-run.

### 2026-11-08: fastener check, fixes (Seif)
Found with `fc/fastener_check_v7.py`, fixed in `v7_fc.py`:
- **Arm clamp screws** (4): the arm hub covered half of the head, so the screw could not go in and no key could reach
  it. The head counterbore now runs 20 mm out through the hub (`split_clamp_z(cb_ext=20)`).
- **Arm ↔ door sheet** (8): nut pockets had 0.2–0.5 mm walls → **M3 inserts** set from the tab's outer face, screws
  **M3 × 12** (were × 16), 4 mm from the tab edges (`TAB_SC`, was 3.5; the door sheet holes follow). Walls 1.7.
- **Head servo** (4): side-entry nut pockets had 0.5–0.8 mm walls → **M3 inserts** in the post tops, **M3 × 8** (were
  × 12 + nut). The ±1.5 mesh slots are gone, like the door units. Post edge chamfer 1.5 → 0.5 (it ate the insert wall).
  This is in `B_SUPPORT_TETE` (module B): Maatoug should carry it into v8.
- Result: rest pose 0 interferences, 0 reserve violations; insert walls ≥ 1.4 mm (thinnest: one door-unit cap insert;
  the new ones 1.7). Still thin, not changed: 28T clamp nut 0.9 mm, middle station nuts 0.9 mm (module B). Motion check not re-run (only
  holes, inserts and screw lengths changed; Seif's call).
- **Door unit corners** (4): M4 × 8 ended inside the nut (2.6 of 3.2 mm) → **M4 × 10**; notch in the cap for the top
  one's tip.
- **TR8 nut support** (4): the M3 inserts left ~0.2 mm of plastic next to the nut-body hole (Ø11) → **Ø2.5 pilot
  holes**, **M3 × 10** cut their own thread (wall 1.25). They only locate the nut: the lift pushes plastic on brass.
- **Not changed (module B, Maatoug is reworking it in v8):** wheel bolts M5 × 35 are ~10 mm too short (tip stops
  inside the head bracket, never reaches the nyloc → **M5 × 45**); the middle cup station's M3 × 16 stops on its nuts
  and the nut pockets face the 30T gear 0.5 mm away (can't be inserted) → inserts in the flange front face.
- Assembly order this check showed: door pinion onto the horn **before** the servo goes into the door unit; head
  pinion **before** the 30T hub; plate → nut-support M4 screws **before** the head bracket.

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
| M3 heat-set insert | outer Ø × length (hole is Ø4.6 × 7.0 + 0.5 chamfer) | **measured Ø5.6..6.0 × 6** (hole kept) |
| M4 insert (if used) | outer Ø × length | not used yet |
| MG996R + round horn | servo bottom → top of the horn disc | **measured 47.4** |
| | horn disc Ø × thickness; boss Ø; screw holes radius | Ø20.8 × 2.5; Ø9.2; r 7.2 |
| | body L × W × H; flange height above the bottom; ear hole spacing | 40.4 × 20.4 × 38; 28; ±24.5 from centre, y ±5 |
| | cable grommet: height above the bottom, how far it sticks out | 3.7–8.3; 5.8 |
| NEMA 17 | body length; shaft length; centring boss Ø; depth of the M3 holes | **37.0; 21.9; Ø22 × 1.9** (printer's model); ≥ 4.5 (M3 × 10 goes 4 in) |
| M5 T-nut (2020 slot) | thickness (the M5 × 8 rail screws get ~2 mm in a 3 mm model) | 3 |
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
  (2026-11-08: the fastener check found the middle station gets 0 mm and the corner M4 is fixed; see above.)
- Still nuts (pockets) rather than inserts: arm and gear split clamps, door sheet screws, head servo, hub clamp, stations.
  The door-unit nut pockets are gone (inserts).
- Checks: rest pose 0 interferences, 0 reserve violations. Full cycle not run yet.

Bill of materials as of 2026-11-08 (after the fastener fixes; source of truth: end of `CAD_FC/report.txt`):

| Qty | Fastener (whole module) |
|---|---|
| 22 | M3 heat-set insert … (**out of date**: since 2026-11-10 module A has only 4 M3 inserts (socle) and no M4 insert; current list: end of `CAD_FC/report.txt`) |
| 10 | M3 × 8 button head · 18 M3 × 12 button head · 9 M3 × 16 button head |
| 4 | M3 × 10 button head into Ø2.5 pilot holes (TR8 nut flange, cut their own thread) |
| 12 | M3 × 10 socket head · 1 M3 × 12 socket head |
| 24 | M3 nut |
| 4 | M4 × 10 button head (door unit corners) · 2 M4 × 8 button head (nut support) · 4 M4 nut · 4 M4 × (6 + chassis) to the robot base |
| 4 | M5 × 35 socket head (wheel bolts; **should be M5 × 45**, module B, not changed yet) · 4 M5 nyloc · 4 M5 × 8 button head + 4 M5 T-nuts (rails) |
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
- Motor body length: 37.0 from the printer's model (2026-11-09); the blocks are 37 mm + pad (`MOT_L`, `MOT_PAD`).

## Mounting on the real robot (after the proof of concept)
- The mechanism is referenced to the **table** (door pads, cups on the middle box at z 165): keep every moving part at
  the same height above the table; only the bottom changes (socle on the chassis floor, motor on that floor, lead screw
  length).
- **Cut the profiles:** today rails + top tie reach **366 mm** (the motion check exempts them). Robot: top tie ≈ 328–350,
  rails ending ≈ 328. Clear of the carriage (wheels ≈ 275 at full lift; the plate, 320, is in front of the top tie).
- The **347.7 mm** maximum (head at the top of the 75 mm lift) does not change with the profile length: 2.3 mm margin.
- The chassis floor must stay below the lowest moving part: door units' bottom, z 27 above the table.
