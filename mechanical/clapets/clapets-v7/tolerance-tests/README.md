# Clapets v7 (module A): tolerance test prints

Print these **in ABS before the real parts** (D-023: the real parts are ABS, so the coupons must be too), check each fit, and report back which variant fits best. The CAD gets
updated before the final print. Made by `../fc/tolerance_tests_v7.py` (STLs in `stl/`). 2026-11-10.

![Coupons](coupons.png)

**Print settings:** ABS on the Bambu X1 Carbon (Bambu/Generic ABS profile, door and lid closed, bed warmed ~10 min
first, textured PEI or engineering plate + glue), 0.2 mm layers, **4 perimeters** (same as the real parts: the perimeters set the hole sizes),
**15–20 % infill is enough** (the coupons are almost all perimeters; infill changes neither the fits nor the weight
much), **as the STL lies (z up)**: every coupon repeats the real part's print orientation. No supports. Same printer
and same filament as the real parts. Keep elephant-foot and X-Y hole compensation at the same values for the coupons
and the real parts (defaults are fine). No brim needed on the coupons.

**Variant marks:** 1, 2 or 3 small grooves next to each feature: **1 = smaller, 2 = the CAD value, 3 = bigger.**

| # | File | Tests (real part) | CAD value | Variants (1 / 2 / 3) | How to check |
|---|---|---|---|---|---|
| T1 | `T1_608_seat_22.0_22.2_22.4` | 608 bearing seats, axis vertical (door unit bottom, cap top) | Ø22.2 × 7.2 + 0.6 lead-in | Ø22.0 / 22.2 / 22.4 | Press a 608 in by hand or with a vice: it should go in firmly and not fall out. Not loose, not cracking |
| T2 | `T2_rod_clamp_8.1_8.2_8.3` | Split clamp on the Ø8 rod (door arms, 28T hub): bore, M3 × 12 + nut in its pocket, head hole | bore Ø8.2, nut pocket 6.0 × 6.9 × 2.8, head hole Ø6.6 | bore Ø8.1 / 8.2 / 8.3 | The rod slides in freely when loose and locks when you tighten the screw. The nut drops into its pocket from the side and doesn't turn. A key reaches the head |
| T3 | `T3_servo_post_hex_5.6_5.7_5.8` | Servo ear posts: M3 nut pushed up into a hex recess under a 1.6 mm roof, window below | hex AF 5.7, 2.5 deep | AF 5.6 / 5.7 / 5.8 | Push a nut up through the window: it should stay up there on its own (snug) and not turn when you screw an M3 × 8 from the top |
| T4 | `T4_M4_pocket_7.2_7.4_7.6` | M4 nut pocket in an upright face (keel and cap front faces with the ±1.5 mm slide; same nut in the nut support's back face) | 11.4 × 7.4 × 3.6 deep | height 7.2 / 7.4 / 7.6 | The M4 nut slides in, can move ±1.5 mm sideways, doesn't turn. An M4 passes the slot |
| T5 | `T5_shelf_nut_pocket_5.8_6.0_6.2` | M3 nut pocket under a shelf (cap screws), opening downward, printed as a bridge | 6.0 × 6.9 × 2.8 | width 5.8 / 6.0 / 6.2 | The nut pushes up into the pocket and stays, doesn't turn. Check that the pocket's ceiling printed clean |
| T6 | `T6_insert_holes_M3_4.4_4.6_4.8` | M3 heat-set insert holes, vertical (socle, 4 inserts; the only inserts left in module A) | Ø4.6 × 7, 0.5 × 45° lead-in | Ø4.4 / 4.6 / 4.8 | Set an insert at ~245 °C (ABS; go up to ~265 °C if it won't sink). Good = goes in straight with light pressure, flush, no plastic pushed out the back, doesn't spin |
| T7 | `T7_2020_passage_20.2_20.4_20.6` | 2020 profile passages (socle rail blocks, motor plate) | 20.4 square | 20.2 / 20.4 / 20.6 | A 2020 profile end slides through without forcing, little play |
| T8 | `T8_servo_cradle_from_A_AILE_D` | **Cut from the real door unit:** bottom 608 seat, the 3 servo posts (nut + roof + windows), ear entries, screw-head openings, cable exit | as in the CAD | one copy | Slide the MG996R in (connector threaded through the cable hole first), push the 3 nuts in, screw the 3 M3 × 8, check finger + key room. Put a 608 in the seat, a rod, **T9 on the servo horn and T10 on the rod**: check the gear mesh (not tight, little backlash) |
| T9 | `T9_pinion_20T` | **The real 20T pinion** (`A_PIGNON_PORTE_20T`): horn pocket, M2 holes, teeth | as in the CAD | one copy | Fits on the MG996R round horn (pocket Ø21.4, boss pocket), 4 M2 × 10 go in. Then the mesh with T10 in T8 |
| T10 | `T10_gear_28T` | **The real 28T gear** (`A_ROUE_PORTE_28T`): rod bore, split clamp with its 2 nut pockets, teeth | as in the CAD | one copy | Slides on the Ø8 rod, locks with the 2 M3 × 12 + nuts; meshes with T9 at 30 mm centre distance (in T8) |

T9 and T10 are the real gears (the same as in `../CAD_FC/STL/`): if they fit, keep them for the final build.

**Filament for the tests: ~127 g of ABS** at 20 % infill (~139 g at 40 %). T8 is ~39 g, the two gears ~15 g; the 7
small coupons alone take ~73 g. Volumes per coupon: `volumes.txt`. (ABS ≈ 1.045 g/cm³, ~16 % lighter than PLA.)

## Results (2026-11-12, ABS, Seif)
- **T1** 608 seat: **Ø22.2** (variant 2) good, no change.
- **T2, T4, T5, T7, T10:** good, no change.
- **T3** servo nut recess: opened to **AF 5.9** (0.2 per side).
- **T6** insert holes: **all bad**, plastic pushed into the insert's thread. Holes redesigned from a reference drawing
  (D-025, `../../design-principles.md`): **Ø5.4 × 7 + mouth cone Ø6.2 × 1.5**. Not re-tested.
- **T8** cradle: inner ear key opening taller, 5 mm strip in front of the outer ears, one window for the 2 outer nuts.
- **T9** pinion: M2 holes **Ø2.5** (were Ø2.2, too tight).
The coupon files here are kept as printed (old values). Details: `../README.md`, "2026-11-12".

## What to report back
For each test: the variant number that fits best (1, 2 or 3), or "all too tight" / "all too loose". Example:
`T1: 2 · T2: 3 (8.1 and 8.2 too tight) · T3: 2 · T4: 2 · T5: 1 · T6: 2 · T7: 2 · T8: ok · T9/T10: mesh a bit tight`.
Then the CAD values in `../fc/v7_fc.py` (`class G`) get updated and the real parts regenerated.
