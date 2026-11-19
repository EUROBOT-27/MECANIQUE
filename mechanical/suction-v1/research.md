# Module B: research (2026-11-18)

Inputs for the fresh start (D-027). What other teams did, what our own CAD already has, and what "professional
pneumatics" means for us. Then how the variations are organised.

## 1. References

### Barbatronic / Karibous, CDR 2027 (`resources/CDR-2027/MCAD/actuator-parts/suction-cup-prototype.FCStd`)
Read with FreeCAD on 2026-11-18 (notes: `resources/_notes/cdr-2027-barbatronic.md`). Same game, same stones.

| Part | Geometry (from the file) | Role |
|---|---|---|
| Carrier "Arm" | plate **8 mm**, 306 long, 3 stations on a **15° zigzag**: 113.9 mm between stations = **110 mm vertical pitch** (one stone) with ±29.5 mm side stagger | one cup per stone; the zigzag gives room for the big stations at a 110 pitch |
| Station hole | **Ø48** + 3 × M3 (Ø3.2) holes | identical drop-in stations |
| `Corps` = **TPU spring disc** | **Ø60 × 8**, centre hub with a hex for the cup adapter, **3 spiral slots** (polar pattern 120°), 2 mm rim pocket | lets the cup move back and tilt to seat on bent cardboard |
| `Corps002` = clamp ring | **3 mm**, Ø48 bore, 3 lugs to ~Ø73, M3 | clamps the TPU rim on the carrier |
| `Corps001` = pot | **Ø66 × 28**, 3 lugs, slot for the tube | sets the cup's stand-off, protects the cup, the stone lands on its rim |
| `Adaptator-suction-cup-M5` | 12 AF hex × 21 long, M5 inside | cup → station |
| `Tube-connector-M5-ID5mm` | 90° elbow, ~15 long | tube leaves sideways, flat against the carrier |
| `Corps003/004/005` | bracket + upright 5 mm with 5 slots at 8 mm pitch (z −61 … 27) | carrier mount, height adjustable by slot |

Lessons: one cup per stone at 110 pitch; the stone is pulled onto a **rigid rim** (no sag); the cup floats on a
**TPU spring**; the **tube leaves through a 90° elbow sideways**; every station is the same part.

### Aerobotix INSAT 2026 (`resources/Aero Euro/Robot-CAD-Teardown.pdf` pp. 5–13, notes `aerobotix-2026-robot.md`)
- 8 identical picking modules (one per crate), each with its own N20 + belt arm and a Ø28 bellows cup on a **90°
  fitting**. Modules slide on an MGN12 rail to match the crate spacing.
- **Pneumatics:** 1 pump per face (CK501) → **1-into-4 manifold**, 4 mm tube → **one 12 V solenoid valve per cup
  (Fa0520F), mounted low near the arms under printed covers**. Each cup grabs and lets go on its own.
- Pumps high in the top box, valves low near the cups (short line from valve to cup = fast grip and release).
- Not documented: dust, worn crates, failure rate. 2026 crates were 150 mm; our stones are 320 mm (lever arm).

### Our own CAD
- **Clapets v7 `tete_station_tpu()` / `tete_bague()`** (`../clapets/clapets-v7/fc/v7_fc.py`): Barbatronic-style TPU
  disc (3 spiral slots 200°, hub with M5 + nut pocket) + clamp ring, on an MDF 6 carrier with **tube notches**.
  Already parametric: the starting code for our station.
- **Flip-bar station** (`../flip-bar/README.md`, Maatoug): v8 TPU disc + ABS spacer (room for the **M5 elbow**,
  tube slot) + **Ø62 support ring** with 3 windows; cup lip 3 mm proud of the ring when free; vacuum pulls the stone
  onto the ring. 38 g per station. 3 × M3 tapped in the bar.
- **Central hub option B** point 8 (Ayoub): a cup 100 mm off the stone's centre lets the stone twist. **Grip on the
  stone's centre line.**

## 2. Pneumatics: what "designed in" means

| Topic | Practice | For us |
|---|---|---|
| Tube | 4 mm OD PU, min bend radius **8–12 mm** (catalogue, static) | design every bend at **R ≥ 20 mm** (moving tube), never a kink at a fitting: leave 15 mm straight after each push-in |
| Line length | keep the valve and the vacuum source close to the cup; long lines = slow grip and release | pump or valve within ~150 mm of its cup |
| Release | pump-off alone is slow (the pump's own check valve holds the vacuum); industrial grippers use a vent / quick-exhaust valve, plus a push-off if the part sticks | **one small 12 V vent valve per cup** (2/2 NC on a tee, opens to air), or a 3/2 valve. Add a push-off if tests show cardboard sticking |
| Grip check | vacuum switch / sensor: check the vacuum before moving | **optional pressure sensor per cup** (e.g. XGZP6847A, −100…0 kPa, 0.5–4.5 V analog): tells software the stone is held. Reserve a tee + space now |
| Rotating cup | rotary feedthroughs exist (industrial, costly); swivel elbows turn on their thread axis | our turns are **≤ 90°, not continuous**: use a **swivel push-in elbow (M5 × 4 mm)** on the cup + a slack loop around the turn axis (R ≥ 25), no rotary union |
| Lift travel | drag chain, or a guided slack loop | small cable/tube chain (10 × 10) or a printed guide for the loop, tube and servo cable together |
| Dust | cardboard dust into the pump | inline filter optional; test first |
| Force | Ø30 bellows ≈ Ø25 effective → 4.9 cm²; at −40 kPa (leaky cardboard) ≈ 20 N per cup | a stone is 0.9 N: margin is huge; **the real question is leakage through cardboard and tag stickers → test on real stones** |

**Test (Seif, 2026-11-18): suction through the ArUco tag sticker holds well.** One pump per cup (Seif, 2026-11-18).

Parts in hand: 6 × 12 V 370 vacuum pumps (−60 kPa), 6 mini pumps, 10 × DP-S30 cups, 10 × VW7-M5. **Not in hand:
vent valves, swivel elbows, pressure sensors, tube, tees** (to check locally: 12 V mini air valves of the
blood-pressure-monitor type and PL4-M5 elbows are common; otherwise ✈️).

## 3. How the variations are organised
The module splits into three layers. Each layer gets its variants; they combine.

1. **Cup station** (common to every concept, designed first): how the cup is held, sprung, protected, plumbed.
   - S1: rigid holder (cup on a printed boss), simplest
   - S2: Barbatronic TPU spiral disc + clamp ring + pot (proven, same game)
   - S3: TPU disc + support ring (flip-bar): stone pulled onto a rigid Ø62 rim
   - S4: guided plunger + compression spring (cup on a sliding tube, no TPU)
   Each one with: cup, M5 connector, swivel elbow, tube exit, bend radius, M3 fixing, print orientation.
2. **Carrier + pneumatics**: one or two cups per stone, 110 pitch (straight or zigzag), where pumps and valves sit
   (on the moving part or fixed), tube and cable routing to the lift.
3. **Mechanism** (walls + towers, D-027): concepts A / B / C in `README.md` and new ones from the research; checked
   for height ≤ 350 in every pose, perimeter, and the two mountings (on module A; alone on a butterfly plate).

## Sources (web, 2026-11-18)
- Tube bend radius: [Pisco PU tubing](https://cdn.shopify.com/s/files/1/0590/7857/4280/files/Pisco_Polyurethane_Tubing.pdf),
  [RS 4 × 2.5 PU datasheet](https://docs.rs-online.com/5ed7/A700000015906483.pdf),
  [Freelin-Wade 4 mm 95A](https://www.jhf.com/parts/4mm-od-freelin-wade-free-thane-95a-tubing/1c-156-37)
- Swivel fittings / rotary feedthroughs: [Festo LJK](https://ftp.festo.com/Public/PNEUMATIC/SOFTWARE_SERVICE/Documentation/2023/EN/LJK_EN.PDF),
  [Jung swivel rotary modules](https://www.industrial-production.de/handling-technology/jung--freedom-of-rotation-for-the-grippers.htm?thema=actuators)
- Pressure sensor: [XGZP6847A (DigiKey)](https://www.digikey.de/en/products/detail/cfsensor/XGZP6847A100KPGN/22530765),
  [Arduino forum example](https://forum.arduino.cc/t/xgzp6847a-pressure-sensor-modul/995497)
- Gripper practice (release, check vacuum, short lines, bellows on cardboard):
  [UR10 vacuum gripper guide](https://industrialmonitordirect.com/blogs/knowledgebase/ur10-vacuum-gripper-design-components-force-calc-suction-cup-selection),
  [Mech-Mind suction cup design](https://community.mech-mind.com/t/topic/1976)
