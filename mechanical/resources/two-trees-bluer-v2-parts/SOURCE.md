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
