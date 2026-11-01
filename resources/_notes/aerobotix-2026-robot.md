# Aerobotix INSAT — Eurobot 2026 robot (study notes)

Sources (both fully read 2026-10-25):
- **[TD]** `Aero Euro/Robot-CAD-Teardown.pdf`, 18 p. Analysis of the STEP file "Slide final CAD" (SolidWorks 2026, 196 unique parts / 415 placed). Materials are *inferred*.
- **[PPP]** `Aero Euro/ppp_eurobot2026_EN.pdf`, 48 p. Academic report by the team (Bensaid, Hmadi, Sellini, Khalsi; supervisor A. Chatti; defended 2026-06-02).
- Related code: `Aero Euro/ROS2-WS-EURO`, `LIDAR_EUROBOT`, `System_code_ESP32_*`, `PCBs`, `NINJA_MECANIQUE` (not studied yet).

## 1. Context and result
- 2026 game "Winter is Coming": **hazelnut crates 50 × 30 × 150 mm** taken from 4-crate batches and flipped to show the team colour; nest, pantries, thermometer, PAMIs. 100 s match.
- **1st at the Tunisian national qualifier, 2nd overall at the international final** (La Roche-sur-Yon, France: 615 pts cumulative vs. 637 for DIT Robotics) [PPP 4.5, fig 4.7]. Club record: national 1st in 2022/23/25/26, 2nd in 2024.
- Another INSAT team, "IEEE RAS INSAT", finished 20th at the same final.
- Its strategy completed all actions in **~60 s**, leaving 40 s spare [PPP 4.5].

## 2. Robot at a glance [TD 2, 8]
- Body **~300 × 300 mm**, top of box at 342 mm, **~426–435 mm with the LiDAR mast**. That's roughly a 1200 mm perimeter (the start limit), with the arms deploying outside it.
- **Symmetric front/back**: two identical picking faces, so it never turns around to pick. The drive axle is at the exact centre, so it turns on the spot.

| Level | Height | Contents |
|---|---|---|
| Base | 0–8 mm | Al base plate 290 × 300 × 4 + 2 plates 238 × 204 × 4, drive motors, 2 MGN12 rails, 8 solenoid valves |
| Middle | 8–219 mm | 8 picking modules (4 per face), spacing servos, 4 × 20×20 columns (219 mm) |
| Top box | 219–342 mm | all electronics, LiPo drawer, power bank, 2 vacuum pumps |
| Mast | 342–426 mm | 2-part printed tower with the LD19 LiDAR; e-stop on the lid |

## 3. Drivetrain and odometry [TD 4], [PPP 2.2]
- **Differential drive.** Chosen mainly because the existing software stack was built for differential drive; switching to omni would have meant new control, tuning and validation [PPP 2.2.1].
- Motors: **Pololu 4742** (37D metal gearmotor, 12 V, 300 rpm) in **JGB37-520 L-brackets**, mounted back to back across the centre, **direct drive** (no belt).
- Wheels: **JSUMO JS7444** (Ø72–74 mm, ~41 mm wide, high-grip silicone), track width ~180 mm.
- Casters: 4 × **Omnitrack 9100** ball transfer units (Ø20 ball) in milled Al corner blocks, set **2 mm above the floor** so the drive wheels always carry the weight.
- **Odometry: separate Ø57 mm encoder wheels**, coaxial with and just outside each drive wheel, on blocks sliding on 2 × 65 mm guide screws, **spring-loaded** (2 mm preload in the CAD). Optical encoders, 3000 ticks/rev.
- Measured accuracy: **3 mm final error after 100 s of linear driving; 0.02° error on a 90° turn** [PPP 4.4].

## 4. Picking system (Concept D) [TD 5–7], [PPP 2.2.1–2.2.2]
- 8 identical modules ("zo7li9a"), 4 per face. Each one is a 3D-printed triangular chute, 51–55 mm wide, leaning ~45° toward the centre.
- Each module has its own **N20 gearmotor** (150 rpm, with encoder) → Ø30 pulley → **timing belt** down the slope → pulley at the arm pivot. The arm is ~107 mm long, with a **Ø28 bellows suction cup** on a 90° fitting.
- **Pick-and-flip sequence**: the cup lands on the centre of the crate → vacuum → the arm swings up (crate held against the chute) → to flip, the arm rotates **~160°** to put the crate over a **30° incline**, releases the vacuum, and **gravity flips the crate** into the right orientation. This is the "double action" the teardown couldn't explain.
- The bellows cup tolerates small misalignment.
- **Sliding ("glider") mechanism**: each module is on its own **MGN12C carriage** on a 240 mm **MGN12** rail (1 rail per face).
  - A **9 kg servo (S0900M)** in the middle drives two 72 mm "separation arms" that push the outer modules apart. Bearings act as cam followers (5 × 13.8 mm).
  - **30 kg servos (TIANKONGRC)** at each rail end swing "organiser" levers that push the modules back together. In the PPP these are the servo-actuated **centering guides** that align crates before suction.
  - **Folding 3-link chains** between modules probably set equal maximum gaps.
  - Pitch: ~54 mm packed, 56–63 mm spread, max ~69 mm.
  - Purpose: centre and align before picking, and keep neighbouring crates apart when releasing them.
- 6 servos position 8 modules.

## 5. Concept history — what they rejected and why [PPP 2.2.1]
| Concept | Idea | Why rejected |
|---|---|---|
| A | Articulated front collector; crates pressed against a servo disc + passive disc for orientation | Simple and fast, but the drive wheels ended up off-centre → bad weight distribution, unstable |
| B | Two-stage: screw-and-nut lift of the whole batch, then 4 grippers rotate crates | Worked, but too many actuators and high torque → complex, less reliable |
| C | Gripper on a ~120° rotating hinge, two discs orient each crate | Cheap, but mechanically complex with many moving parts |
| **D** | One printed suction module per crate + gravity flip | **Chosen**: simplest, easy to make, reliable, symmetric, fewer actuators |

Lesson: they prototyped several concepts (MDF + 3D prints) before committing [PPP 4.2]. **CAD of the final robot took ~1 week of continuous work** [PPP 2.2.1].

## 6. Pneumatics [TD 7]
- 2 × **CK501-1BPM 12 V vacuum pumps** (one per face, in the top box) → **1-into-4 manifolds**, 4 mm tube (plus a 6→8 mm adapter).
- 8 × **Fa0520F 12 V solenoid valves**, one per cup, mounted low near the arms → each cup grabs and releases on its own.
- Switched by a custom MOSFET board.

## 7. Frame, materials, manufacturing [TD 8], [PPP 2.2]
- Base: **three stacked 4 mm aluminium plates**, **CNC-machined** from 2D drawings [PPP]. (TD guessed the 2 lower plates were steel; the PPP says aluminium.) Heavy parts sit low: motors, plates, battery.
- 4 × 20×20 extrusion columns (219 mm) → 5 mm middle plate → 4 × 20×20 columns (110 mm) for the top box.
- Top box walls: **laser-cut MDF** [PPP] (TD guessed acrylic/PVC), painted black. MDF was chosen to avoid a top-heavy robot.
- Top lid 288 × 288 × 8.6 mm, **hinged** (2 hinges + lift tab), carrying the LiDAR mast and e-stop → fast access to the electronics.
- **LiPo in a pull-out side drawer** with a voltage checker → quick battery swap.
- Printed parts: **FDM PLA+** on a Bambu Lab X1C and an Ender 3 V2 Neo. Teal on one face, white on the other. 39 zip-tie anchors are designed into the CAD.
- Assembly order: base plate with everything mounted → columns → middle plate → box → hinged lid. Each subsystem can be removed on its own.

## 8. Electronics and power [TD 9], [PPP 2.3]
- **Raspberry Pi 5 (8 GB)**, Ubuntu 24.04, ROS 2 Jazzy: strategy, planning, vision.
- **STM32F446RE Nucleo** + custom shield: real-time PID and odometry.
- **3 × ESP32**: actuators and pneumatics, over micro-ROS.
- Drive drivers: IBT-4 [PPP] / 2 × IBT-2 BTS7960 [TD] (the two sources differ).
- N20 drivers: TB6612FNG on 2 custom "ESP motors 2.0" boards (4 N20 + 3 servos per board).
- Custom boards: 2 motor boards, 1 pneumatic MOSFET board (10 N-MOSFETs), 2 servo boards, 1 STM32 shield. The early versions were **home-etched single-sided**; the final ones are green manufactured PCBs.
- Power: **4S LiPo 5000–5200 mAh** for motors and pumps, plus a **separate 20 000 mAh power bank for the Pi 5** so motor current spikes can't reset the logic. 5 × **XL4016** buck converters isolate the rails. Fan and USB hub.
- Start-cord jack. E-stop on the lid.

## 9. Software and vision (brief — software is out of scope for this hub)
- Architecture: RPi5 (ROS 2: strategy state machine, **Hybrid A\*** in Python with occupancy grid and ~30 cm safety margin, ~80 ms per 1.5 m path) ↔ micro-ROS ↔ STM32 (cascaded velocity + position PID) and ESP32s.
- Strategy is a **task scheduler** that scores each task by distance, opponent's likely target, obstacles, enemy proximity, distance to the nest, remaining time and which face is loaded.
- LiDAR LD19 (360°, 10 Hz) with clustering, map validation and EMA smoothing of obstacles. **Limitation: 10 Hz is too slow at 1 m/s** to track the opponent well [PPP 4.6].
- **Vision (relevant to Seif)**:
  - **2 × Raspberry Pi Camera v3**, OpenCV + **ArUco**, chosen over colour detection for robustness to lighting and occlusion.
  - Pipeline: calibration → marker detection → relative pose, fused with odometry. A **`set_position` service** resets odometry when a tag is seen at the front or back.
  - Colour detection confirms grasps.
  - "Pickability" AI: an OpenVINO classifier on a 33-feature vector per batch (centre, orientation, member poses, batch ID, team side). It labels a batch pickable or not (threshold 0.72) and falls back to rules if the model fails to load.
- Tools: a web dashboard via rosbridge (`Eurobot_Dashboard`) and RViz2 simulation without Gazebo.

## 10. Bill of materials (proven parts) [PPP table 2.3], [TD 3]
Raspberry Pi 5 8 GB · STM32F446RE Nucleo · 3 × ESP32 DevKit · LD19 LiDAR · 2 × RPi Camera v3 · 2 × optical encoders (3000 ticks/rev) · 2 × Pololu 4742 · 2 × JSUMO JS7444 · IBT-4/IBT-2 · 8 × N20 150 rpm with encoders · 4 × 30 kg servos + 2 × 9 kg servos · 2 × TB6612FNG · 2 × CK501-1BPM pumps · 8 × Fa0520F valves · 10 × N-MOSFETs · LiPo 4S 5000 mAh · 20 000 mAh power bank · 5 × XL4016 · MGN12 rails + MGN12C carriages · Omnitrack 9100 ball transfers · Ø28 bellows suction cups · 20×20 Al extrusion.
**Where they bought each part is not documented.** Ask them (see §13), because it's the fastest way to know what can be found in Tunisia.

## 11. Differences between the two documents
| Topic | [TD] | [PPP] | Trust |
|---|---|---|---|
| STM32 | F401/F411 | F446RE | PPP (written by the team) |
| Drive driver | 2 × IBT-2 (BTS7960) | IBT-4 (×1 in BOM) | ask |
| Lower base plates | steel weight plates (inferred) | 3 × 4 mm aluminium | PPP |
| Box walls | acrylic/PVC (inferred) | MDF | PPP |
| Battery | 4S 5200 mAh | 5000 mAh | minor |
| Regulators | 5 × XL4016 | 5 (6 DC-DC in the integration list) | minor |
| What the N20 drives | arm via belt | "linear slides with spring-assisted mechanism" | TD (from CAD); PPP wording is loose |

## 12. Lessons for our 2027 robot
**Directly transferable:**
1. **Chassis architecture**: heavy low base plate + 20×20 columns + top electronics box + hinged lid + LiDAR mast under the beacon support. Proven at the European final, and it matches our manufacturing methods (profiles, laser cutting, printing). Their CNC plates could be laser-cut in our process.
2. **Drivetrain package**: Pololu 37D + JSUMO wheels, direct drive, centred axle, casters 2 mm high, **spring-loaded separate encoder wheels**. 3 mm drift over 100 s is excellent.
3. **Differential drive**: we chose it too (D-004). Their numbers (3 mm drift after 100 s) are the benchmark to beat.
4. **Electronics layout**: separate logic power (power bank) from motor power, battery drawer, hinged lid, fan.
5. **Design process**: several concepts → cheap prototypes (MDF/printed) → pick the simplest. One week of focused CAD for the final robot.
6. **Symmetric two-face design** saves turning time.
7. **Suction + one valve per cup**: independent grip and release; the bellows cup tolerates misalignment. Smooth cardboard (and the ArUco stickers on stone faces) should suit suction, **but test on real stones**.

**Doesn't transfer directly (2027 is a different game):**
- 2026 crates were 50 × 30 × 150 mm. **2027 stones are 320 × 110 × 110 mm (~90 g)**: over 2× longer, and needing **vertical placement and stacking** (walls, towers, gate) rather than flipping on the floor. A single Ø28 cup at the centre of a 320 mm box gives a long lever arm, so the stone will swing. Consider 2 cups per stone or a cup plus a mechanical support.
- Their **300 mm body is shorter than a 320 mm stone**. Carrying stones lengthwise changes the outline, so the perimeter question (FAQ Q1) matters.
- Same 350 mm height envelope (their box top is at 342 mm). A 2027 robot with the Grail on its roof (L4, > 300 mm) and stacking up to 330 mm must fit lifts in the same envelope.
- 10 Hz LiDAR was their main limitation. Consider a faster LiDAR or vision fusion for avoidance (this affects the CV plan).

## 13. Things the documents don't say
Aerobotix is another club (we're IEEE RAS INSAT). These would only come from talking to them, if that's ever possible:
- Do the folding chains really work as end stops? What N20 gear ratio and belt type?
- Did suction fail on dusty or worn crates? Any reliability issues during the matches?
- Who did their CNC machining and PCBs?
