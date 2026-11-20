# Two Trees Bluer V2 parts (real geometry)

Extracted 2026-11-01 (Seif + Claude) from the GrabCAD model **"3D Printer Two Trees Bluer V2"**
(`3d-printer-two-trees-bluer-v2-1.snapshot.4`, GrabCAD download; author/licence: see the GrabCAD page, add the link here).
The full download (.stp/.3dm/.igs/.obj + named STLs, ~2 GB) is **not committed** (`.gitignore`); it lives in
`mechanical/resources/3d-printer-two-trees-bluer-v2-1.snapshot.4/` on Seif's PC.

How: the `.stp` has generic names; the "Brazilian portuguese" folder has one named STL per part, in the same
coordinates. Each part = the `.stp` solids inside its STL's box, checked by volume (ratio ≈ 1.00), extra solids filtered
out. All files are in **printer coordinates** (mm); `fc/v7_fc.py` places them in the module.

| File | Part (Portuguese name) | Source |
|---|---|---|
| `rails_2020_Y.step` | 2 × 2020 profiles, 350 mm, 80.9 apart (Perfil de Alumínio eixo Y) | .stp |
| `v_wheels_Y.step` | 4 V-wheels with bearings (Roldana Eixo Y) | .stp |
| `m5x35_wheel_screws_Y.step` | 4 wheel screws (Parafuso Allen M5x35 Roldana) | .stp |
| `m5_nyloc_nuts_Y.step` | 4 M5 nyloc nuts (Porca Autotravante M5) | .stp |
| `m5_spacers_Y.step` | 2 plain M5 spacers (Espaçadores Parafuso M5) | .stp |
| `bronze_washers_Y.step` | 2 bronze washers of the eccentric spacers | .stp |
| `eccentric_spacers_Y.step` | 2 eccentric hex spacers (Espaçador Excêntrico Sextavado) | **modelled** from the STL size (hex 10 × 8.4 from the bronze washer + Ø7.4 spigot into the plate); the STL mesh is open |
| `butterfly_plate.step` | heatbed base, 190 × 190 × 3 (Base da Mesa Aquecida) | .stp, **B-spline only (no true holes): not used**, the CAD keeps the exact plate from `fc/plaque_papillon_reelle.json` |
| `nema17.step` | NEMA 17 of the Z axis, body ~38 mm, shaft Ø5 (Motor Nema 17 Eixo Z), without its mounting screws | .stp |
| `coupler_5x8.step` | 5 → 8 coupler (Acoplador Motor Nema 17) | .stp |
| `lead_nut_TR8x8.step` | TR8x8 brass nut, flange 1.5 mm from one end (Porca Trapezoidal TR8x8-4) | converted from the STL |

Not taken: the lead screw (TR8x8, 400 mm in the printer) is a plain Ø8 cylinder in our CAD, cut to length.

## Belt-axis parts (Maatoug + Claude, 2026-11-20), for the Grail lift v4 (`mechanical/grail-lift/fc/v4_fc.py`)
Same download, unzipped on Maatoug's PC into `mechanical/resources/3d-printer-two-trees-bluer-v2-1.snapshot.4/` (only the
`.stp` + the X / Y / heatbed named STLs; not committed). These are the parts on the bench: the belt, the knob tensioner,
the belt bracket. **Mesh** = solid made from the named STL (triangulated faces, exact size, no true cylinders).

| File | Part (Portuguese name) | Source |
|---|---|---|
| `tensioner_X_plate.step` | X tensioner: mounting plate 60 × 3 × 20 (Peça 1 Conj. Tensor Eixo X) | mesh |
| `tensioner_X_body.step` | X tensioner: blue body (Peça 2) | mesh |
| `tensioner_X_slider.step` | X tensioner: sliding block holding the idler (Peça 3) | mesh |
| `tensioner_X_knob_screw.step` | X tensioner: knob + M5x20 screw (Parafuso M5x20 Tensor Eixo X) | mesh |
| `tensioner_Y_body.step`, `tensioner_Y_slider.step`, `tensioner_Y_cover.step` | Y tensioner (Peça 1, Peça 2, Chapa Proteção) | mesh |
| `belt_Y_GT2.step` | Y belt as mounted in the printer, GT2 6 mm (Correia do Eixo Y) | .stp (volume ratio 1.01) |
| `belt_X_GT2.step` | X belt as mounted (Correia do Eixo X) | mesh |
| `pulley_X_motor_GT2.step` | GT2 20T motor pulley (Polia Sincronizadora GT2 Motor de Passo Eixo X) | mesh |
| `carriage_plate_X.step` | blue X carriage plate, 3 V-wheels (Chapa Roldanas do Eixo X no Hot End) | mesh |
| `belt_clamp_bracket_Y.step` | black bent bracket holding both Y belt ends, 28 × 20 × 13 (União Correia Eixo Y Sob a Base da Mesa) | mesh |

Not converted: the 20T idlers (`Polia GT2 Tensora 20T ID5 OD18 W6`) and the Y motor pulley: 100 MB as mesh STEP. The
generators use measured stand-ins instead (idler: Ø17 flanges, Ø12.2 teeth x 6, bore 5, 8.6 wide; motor pulley: Ø15.5,
16 long, bore 5).
