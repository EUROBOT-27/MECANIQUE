# Central hub option A: connections, actuators, collisions

Status: **proposal** (Ayoub, 2026-11-14). Not reviewed by Seif or Maatoug. Nothing here is in `project/decisions.md`.
Geometry: `fc/hub_a_fc.py` (option A). Collision checks: `hub_a_report.txt` (between the levels) and `hub_a_env_report.txt`
(`fc/check_env_a.py`: fixed parts against each other and the hub against base_330).
Sourcing: 📦 in `../parts-library.md`, 🇹🇳 local, ✈️ import. Printed parts are ABS (D-023). Insert holes follow
`../design-principles.md`: M3 insert hole Ø5.4, mouth Ø6.2, wall ≥ 2 mm. Nuts sit in pockets: M3 6.0 × 6.9 × 2.8, M4 7.4 × 8.4 × 3.6.

## 1. Part breakdown (in the model since 2026-11-14)

`fc/hub_a_fc.py` now draws all of this, with every fastener. FCStd objects: `Hub_S1`…`Hub_S4`, `Cradle_*`,
`TurnServo_*` (with ears), `Fasteners_fixed`, and per level `Level_*` (structure), `Actuators_*` (motors, screws,
couplers, bearings, switches), `Fasteners_*`.

- **The hub is split into 4 printed segments.** The spacers became collars on the segments, and each segment ends
  at the top face of its ring band:
  S1 z 73–100.5 (94 × 94 flange + bottom band) · S2 100.5–150.5 (collar + middle band) · S3 150.5–255.5 (collar +
  top band) · S4 255.5–345 (top collar, the base for the beacon mast). The tallest one is 105 mm, so they print on
  the X1C. Each joint has a 3 mm centring spigot (lip r 38.2–41 on the upper segment, recess in the lower one).
- **Each pinion window is a slot that opens to the top of its segment.** **Each ring's internal gear band opens to
  the ring's top face.** The next segment's collar closes both. Assembly goes: S1, then the bottom ring, then the
  bottom servo + cradle + pinion lowered in (the pinion drops through the slot into the gear), then S2 over the
  servo, and so on up to S4.
- **Each MG996R has its ears.** The outer ear sits in a slot in the hub wall (r 37–44.5, ±10, open to the end the
  servo comes in from). The inner ear bolts to the cradle.
- **Each ring has 2 lugs** at the arm angles, where the ring grows out to r 76 over ±20°. Each arm has a 26 × 8
  pad that sits in a slot in the lug. The lugs stay inside the ring's own z band, so they cannot meet another level.
- **Each arm is printed in one piece** (bar + pad + rail + end caps + N20 clamp + switch shelf): bottom arm, top
  arm, and the middle stepped arm. **Each carriage is printed in one piece** (carriage + nut block + switch tab +
  spin-servo tabs).

## 2. Connections

| # | Joint | Fastener | Qty (whole hub) | Notes |
|---|---|---|---|---|
| J1 | Bridge walls → base plate, bridge top plate → walls | Tab + slot, plus 2 printed L-brackets per wall, M3×12 + nut | 4 brackets, 16 × M3×12, 16 nuts | Laser-cut bridge (concept doc). 📦 |
| J2 | Hub S1 flange → bridge top plate | M4×16 button head (ISO 7380), head in a Ø8.5 × 2.5 counterbore (the bottom ring turns 0.5 mm above it) + nut under the plate | 4 | Holes at (±40, ±40): they clear the motors (\|y\| < 18.5) and the tie rods. 📦 |
| J3 | S1 + S2 + S3 + S4 clamped together | **3 × M4 threaded rods** z 73.5–344, r 44 in the hub wall, polar 135° / 225° / 315° (the pinion windows are at 7–83°). Captive nut in a pocket under S1, nut in a Ø10 × 5 pocket in the top of S4 (nothing above 345) | 3 rods 272 mm, 6 nuts | Plus the centring spigots and a key, so the windows line up. The beacon mast can bolt onto longer rods later (430 ± 5 [GR F.6]). 🇹🇳 |
| J4 | MG996R inner ear → its printed cradle | 2 × M3×12 through the inner ear + nut in a pocket in the cradle (open to the back). The outer ear only sits in its wall slot | 6 + 6 nuts | Servo + cradle are screwed together on the bench, then lowered in. 📦 |
| J5 | Servo cradle → hub segment | 2 × M3×25 countersunk, **radial through the collar** (polar 210° / 240°) into M3 inserts in the cradle (Ø5.4 × 7, mouth Ø6.2 → 5.4 over 1.5; wall 3.4 to the cradle side). The heads sit flush with the collar OD (r 56) | 6 + 6 inserts | Bottom cradle → S2 collar (z 122), middle → S3 collar (z 172), top → S3 collar (z 213). You can unscrew it from outside to pull out a servo. |
| J6 | Pinion → MG996R spline | Round horn (comes with the servo, Ø20) in a 2.2 mm pocket on the servo side of the pinion + 4 × M2×6 self-tapping screws + the servo's centre screw from the far side (head in a pocket) | 3 horns, 12 × M2×6 | The horn keeps the 25T spline. Do not print a spline. 📦 |
| J7 | Ring → hub | **No fastener: plain journal bearing.** Ø50.5 bore on the Ø50 hub (0.25 radial), 0.5 mm axial play to the collars, grease | 3 | With the open gear band the journal is only 10 mm long. The collar faces limit tilt to ~0.5° (≈ 2.5 mm at the stone tip). ABS shrinks: ream the bore. |
| J8 | Arm pad → ring lug | Pad in the lug slot (stops the arm turning) + 2 × M3×20 vertical at r 69, t ±9.5 through lug + pad, head on the top face, nut in a pocket on the lug underside | 6 arms → 12 × M3×20, 12 nuts | Outside the collars (r 56). |
| J9 | Rail, caps, bar | **No fastener:** one printed part per arm | | The rail is an 8 × 10 printed cantilever, 143 mm long: stiffness is open (§5). |
| J10 | N20 → rail end (bottom arm: under the rail; top arm: on top of it) | Printed clamp saddle (part of the arm) + 2 × M2×16 radial through the clamp ears at t 1 / 21 + nut | 4 clamps, 8 × M2×16, 8 nuts | Or 2 × M1.6×4 into the gearbox face if yours is tapped (measure). 📦 / 🇹🇳 |
| J11 | N20 D-shaft 3 mm → M4 lead screw | Coupler Ø8 × 6, 3 → 4, with M3 grub screws | 4 | The library has only 1 brass coupler (3–4 bore): print 3 more, or buy. The nut blocks were shortened 2 mm on the coupler side so they never reach it. 🇹🇳 |
| J12 | Lead screw far end → rail cap | Small ball bearing 4 × 8 × 3 (MR84 class) in the cap, **radial support only** | 4 | The load is ~1.5 N (carriage + servo + stone), so the N20 takes it through the coupler. No lock nut: one above the bottom slide's cap would sit 0.5 mm from the middle arm. Add a collar if a test shows play. "Small ball bearings" 📦 (read the codes). |
| J13 | Carriage → lead screw | M4 nut in a hex pocket in the nut block | 4 | A long coupling nut wears less: option. 📦 |
| J14 | MG90S → carriage / middle-arm post | 2 × M2×8 self-tapping, radial, through the ears into 2 printed tabs (t ±11–17) | 12 | 📦 |
| J15 | Cup adaptor → MG90S horn | ABS adaptor with a Ø16 × 2 flange on the horn: 2 × M2 self-tapping + horn centre screw. VW7-M5 connector into an M5 insert / tapped M5 in the adaptor (PTFE tape). Side hose barb. TPU sleeve holds the VS2-S30 cup | 6 sets | Adaptor flange + 2 M2 drawn; VW7 + TPU sleeve not drawn. The cup turns 90°: leave a hose loop. 📦 |
| J16 | Pumps (+ vent valves) → base | Printed cradle + 2 zip ties per pump. Cradle → base: 2 × M3 + nut | 6 cradles, 12 × M3 | Off the hub, in the free front-right / rear-left quarters. |
| J17 | Cables + hoses (arm → bore) | Printed zip-tie anchors on each arm and collar. Each level needs a **service loop over 90°** that passes into the bore through a slot in the collar above its ring | ~12 anchors | Not modelled yet (§5). |
| J18 | Limit switches (slide zero) | Mini micro-switch 12.8 × 6.5 × 5.8 on a printed shelf beside the rail (t −18…−5), 2 × M2×12 + nut. A tab on the carriage presses it: bottom slide at cz 60 (lowest), top slide at cz 290 (highest) | 4 sw, 8 × M2×12, 8 nuts | In the CAD. Lever not drawn (the tab stops 0.9 mm from the screw heads). |

Fastener count (drawn in the model, J1/J16/J17 are not): M4: 4 bolts + 3 rods + 14 nuts. M3: 6 × 12, 12 × 20,
6 × 25 countersunk, 18 nuts, 6 inserts. M2: 12 × 6, 8 × 12, 8 × 16, 12 × 8, 12 for the cup adaptors, 16 nuts.
Other: 3 servo horns, 4 couplers, 4 bearings, 4 micro-switches. The same list is printed at the end of `hub_a_report.txt`.

## 3. Actuators

| ID | Qty | Part | Where | What it does | Travel | Drive / control | Src |
|---|---|---|---|---|---|---|---|
| TURN-B / -M / -T | 3 (1 per ring) | MG996R | Inside the Ø76 hub bore. Bottom + middle hang upside down above their pinion, top one sits below | Turns its ring, and with it **both** the front arm (stone → robot's left) and the rear arm (→ right) | Servo 180° → ring 90° (pinion pitch r 26 on internal gear r 52, 2:1) | PWM. The ring gets 2 × the servo torque (~18 kg·cm). Load is only inertia (vertical axis) | 📦 |
| SLIDE-TF / -TR | 2 | N20 gear motor + M4 lead screw | Top front + top rear arm, rail r 76–84 | Lowers the top cup from the stack (z 290) to the spin height (175); after the spin the cup vents and the stone drops 15 mm, like the middle one (2026-11-15: the rail used to reach z 146 and passed 2 mm over the middle arm), and back | 115 mm | DC via an H-bridge, home switch | 📦/🇹🇳 |
| SLIDE-BF / -BR | 2 | N20 gear motor + M4 lead screw | Bottom front + bottom rear arm, rail r 104–112 | Raises the bottom cup from the stack (60) to 175, then sets the stone at 160, and back | 115 mm | DC via an H-bridge, home switch | 📦/🇹🇳 |
| SPIN ×6 | 6 (1 per arm) | MG90S | On the carriage (top, bottom) or on the fixed post (middle), output axis radial | Turns cup + stone 90° about the stone's long axis: flat → standing (tower) | 90° | PWM | 📦 |
| VAC ×6 | 6 (1 per cup) | 12 V 370 vacuum pump | Off the hub, hoses down the bore | Holds the stone on its cup | on/off | MOSFET | 📦 |
| VENT ×6 | 6 | 12 V solenoid valve (not modelled) | Next to each pump | Lets air into the cup to drop the stone. A 370 diaphragm pump stays sealed when stopped, so stopping the pump alone may not release the stone | on/off | MOSFET | 🇹🇳 |

Totals: **13 motors** (9 PWM servos + 4 DC with 2 dual H-bridges, e.g. TB6612 🇹🇳), 6 pumps, 6 valves, 4 switches.
Tell Hamza Bjaoui: 9 PWM outputs, 4 DC channels, 12 MOSFET channels, 4 inputs.

Points to check on the actuators:
- **MG996R range:** many sold units turn only ~120–160°, not 180°. With the 2:1 gear that gives a 60–80° ring turn.
  Measure ours before freezing the 2:1 ratio.
- **Slide speed:** an M4 screw (0.7 mm/turn) on a typical 300 rpm N20 gives 3.5 mm/s, so **~33 s for one 115 mm
  stroke**. That is far too slow for a 100 s match. You need a ≥ 1000 rpm N20, or a fast-lead screw (T8 lead 8 📦
  → 40 mm/s), or a rack.
- **Front and rear on one ring always move together:** a stone you don't want to place stays on its cup and comes
  back home.

## 4. Collisions

Model of 2026-11-14 (segments, cradles, servo ears, lugs, every fastener, switches):

- **Hub alone, both units, 167 steps (`hub_a_report.txt`): no clashes.** Checked: every moving part (rings, lugs,
  arms, rails, carriages, servos, cups, switches, moving fasteners) against the other levels, the segments, the
  cradles, the turn servos and the fixed fasteners, plus stones against stones. The highest stone is at 345 and the
  mechanism reaches 328, both within 350 [GR F.3].
- **Fixed parts against each other: no clashes.**
- **Against base_330 (`hub_a_env_report.txt`): only the wheels** (A below).

Tightest gaps:

| Where | Gap |
|---|---|
| Cradle ↔ hub bore wall (all 3) | 0.4 mm |
| Bottom turn servo and bottom cradle ↔ middle pinion | 1.0 mm |
| Middle ↔ bottom level (middle ring turning) | 5.3 mm (was 2.0: fixed 2026-11-15, see below) |
| Middle ↔ top level (middle ring turning) | 6.7 mm (was 2.0) |
| J18 screw heads ↔ carriage tab at the switch point | 0.9 mm |
| Bottom ↔ top level (during the top turn) | 19.9 mm |

**2026-11-15, middle arm vs top + bottom arms (Ayoub):** all 3 arms park at the same angle and the middle arm passed 2 mm under the top rail end and 2 mm over the bottom rail end, which the ring tilt and rail flex would close. Fixed by lengths: top rail shortened (ends at z 161; the top stone now drops 15 mm from the spin height like the middle one), middle crossover raised 199 → 213, top rail moved 4 mm in (r 76–84), bottom rail 2 mm out (r 104–112, bottom spin shaft 2 mm shorter). Re-checked: no clashes, gaps above.

Problems found on 2026-11-14 and what became of them:

| | Collision | Status |
|---|---|---|
| A | **Bottom slide (rail + N20 + clamp, r 99–118, z 22–193) hits both drive wheels** of base_330 (wheels x ±84–104, z 0–90): at 90° the arms point along ±X, right over the wheels. 45 of 167 steps. It would also hit on layout-v1 (wheels x ±106–150, Ø74) | **Open, on purpose:** the wheel will be changed for a smaller one (Ayoub, 2026-11-14). Re-run `fc/check_env_a.py` with the new wheel. |
| B | Bottom stones hit the base_330 plate corner during the bottom turn | **Fixed:** the bottom carriage rises +16 (cz 76) at home before its turn (new sequence step). The levels above are empty by then. |
| C | MG996R ears were not modelled; the outer ear reached ~5 mm into the hub wall | **Fixed:** ears drawn, outer ear in a wall slot, inner ear on the cradle (J4). |
| D | It could not be assembled (pinions inside closed rings) | **Fixed:** split hub, open windows and gear bands (§1). |

**Not checked:** tool access to each fastener (the `fastener_check_v7.py` method from clapets v7 would apply),
cables, hoses and their 90° loops, the switch levers, the VW7 connectors and TPU cup sleeves, the base_330 back wall
(the concept already requires removing it), and the rest of the robot.
The front unit sweeps the front-left quarter and the rear unit sweeps the rear-right quarter, out to r ~280 and up to
350. On layout-v1 that is where the front module, the Grail lift (right) and the launcher (left) sit, so the hub must
be checked against `../layout-v1/` before anyone builds it.

## 5. Review against `../design-principles.md` (2026-11-14)

| Principle | Status |
|---|---|
| Symmetry | ✅ Rear unit = front unit turned 180°. |
| Nuts in pockets (M3 6.0 × 6.9 × 2.8, M4 7.4 × 8.4 × 3.6) | ✅ J3 (S1 underside, S4 top), J4 (cradle, open to the back), J8 (lug underside), J13 (nut block). ❌ **Loose nuts:** J2 (under the bridge, next to the motors), J10 (N20 clamp), J18 (switch shelf). |
| Insert holes (Ø5.4 × 7, mouth cone, wall ≥ 1.6 from the real Ø6) | ✅ J5 after the fix (the first version had 0.35 mm of wall at the cradle side; screws moved from ±20° to ±15°). Wall to the J4 nut pockets: 1.65 mm (just above 1.6). |
| Assembly access: straight path for every key, room for a wrench | ⚠️ **Not checked.** `fastener_check_v7.py` is not run on this model. Known doubts: J2 nuts (wrench between motor and bridge wall, ~6 mm); J8 on the bottom and middle rings (the ring above parks at the same angle, so turn the rings apart to reach the screws). |
| Make every action checkable | ✅ Slides have limit switches (J18). ❌ No feedback on the turn and spin servos; no vacuum sensor. |
| Zip-tie anchors / designed cable path | ❌ Not drawn (J17). |
| Edge rule (1 mm chamfers, inside fillets), windows with rounded corners, one logic per part | ❌ Not applied: the model is still concept boxes. Do it when the parts are made fabrication-ready. |
| Keep-out zones drawn first | ❌ Replaced by the step-by-step clash check. |
| Print orientation, ABS sizes (+0.1–0.2 on holes) | ❌ Not set. Ring bore and hub journal (0.25 radial) need an ABS coupon. |
| Independent modules, one actuator per job | ⚠️ One turn servo drives both the front and the rear arm of a level: if it fails, both towers of that level are lost. |
| Removable subassemblies | ⚠️ The hub comes off with 4 bolts (J2). A turn servo comes out only after the segments above it are removed (tie rods). |

## 6. Open points
1. Bottom slide vs the wheels (A): waiting for the smaller wheel.
2. Rail stiffness: 8 × 10 printed rails, cantilevered 143 mm with a stone at r 225. A guide rod (Ø6 silver steel 🇹🇳
   + bushing in the carriage) would help.
3. Slide speed (lead screw / N20 rpm).
4. The cable + hose service loop for each level (J17), and the hoses down a bore already holding 3 servos (free half
   of the bore: ~Ø38).
5. MG996R real angle range and gear backlash at the cup (backlash × 2 through the 2:1 gear).
