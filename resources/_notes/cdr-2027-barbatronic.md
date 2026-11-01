# Barbatronic — CDR-2027 (Coupe de France 2027), notes

Source: `resources/CDR-2027/` (clone of github.com/Barbatronic/CDR-2027, team "Karibous", differential robot),
studied 2026-10-28 for the suction head. CAD is FreeCAD (`MCAD/`), docs are a Jekyll journal (`DOCS/`).

## Suction-cup module (`MCAD/actuator-parts/suction-cup-prototype.FCStd`) — the part we copy the idea of
- **One cup per box, 3 stations on one carrier ("Arm")**: 8 mm plate, 306 mm long, stations every **113.9 mm along an
  S/zigzag at 15°** → **110 mm vertical pitch** (= one box) with a ±29.5 mm sideways stagger. Only the middle station is
  populated in the file; the other two are bare Ø48 holes: **identical drop-in stations**.
- **Each station (modular, bolts into a Ø48 hole):**
  - `Corps` = **TPU spring disc Ø60**, 8 mm overall, **3 spiral arms** (polar pattern 120°, spiral slots ~70°), hex
    centre holding the cup adapter. Lets the cup move in/out and tilt to seat on bent cardboard.
  - `Corps002` = **3 mm clamp ring**, Ø48 bore / ~Ø73 outer, M3 screws (Ø3.2): sandwiches the TPU disc rim on the carrier.
  - `Corps001` = Ø66 × 28 pot under the carrier (3 lugs, slot for the tube): protects the cup / sets its stand-off.
  - `Adaptator-suction-cup-M5-VM` (12 mm, M5 thread for the cup), `Tube-connector-M5-ID5mm`, washer.
- Mount: end bracket with an R44 lobe + a toothed vertical clip (`Corps003/004/005`), M4 (Ø4.15) holes.

## Other
- `box-manipulator.FCStd` (+ `MCAD/3d-print/*.3mf`, `MCAD/laser-cutting/box-manipulator_laser-cut-5mm.svg`): a servo
  arm with a **roller** pressing on the box (5 mm laser-cut parts). Not a gripper we need.
- Journal (`DOCS/_posts/`): game-element tests (gate built ≈ 439 mm high because the cardboard bulges; towers less stable
  than walls), ball launchers. No written doc of the suction module.

## What we take for our head (clapets module)
1 cup per box at 110 mm pitch, identical drop-in cup stations, TPU spiral-spring disc clamped by a ring, M5 cup adapter.
