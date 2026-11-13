# Open points before and during the build

## Check on the real parts (then update `class G` in `fc/v5_fc.py` and regenerate)
- [ ] **Heat-set inserts:** measure ours; the holes are M3 Ø4.0 × 6 and M4 Ø5.6 × 7 (`INS3_*`, `INS4_*`).
- [ ] **Servo horn:** round horn assumed Ø21 × 2 mm (`HORN_R`, `HORN_T`); the pinions have a pocket for it.
- [ ] **DP-S30 cup height:** 18 mm assumed (cup face at y 140 = the box face).
- [ ] **T8 screw lead:** 8 mm assumed (not self-locking: keep the stepper powered).
- [ ] **Ø8 rods:** check they are Ø8.0 and straight; whether they are hardened matters only for the clamp upgrade below.
- [ ] **Print test pieces first:** one 608 seat, one clamp bore, one nut pocket, one insert hole. Adjust `BRG_R`, `ROD_R`,
      `NUT_*`, `INS*` if needed.

## Known limits
- **Height margin 2.3 mm** while turning (see [RULES.md](RULES.md)).
- **Door length is at its maximum** (folded tips stop at x 30, in front of the head's rest space).
- **Door servo travel:** 179° of 180° is used (fold +90° … open −38°, ×1.4). Set the servo end points carefully.
- **Split clamps on plain rods:** fine for normal use, marginal at full servo stall. Upgrade if they slip: a steel Ø8
  shaft collar bolted under the 28T, with a 0.5 mm spot flat under its set screw (see [BUILD.md](BUILD.md)).

## Not designed yet
- Tubes (DP-S30 → pumps → vent valves): only the passage and the carrier notches are reserved.
- The service loop for the 3 servo cables + 3 tubes (lift travel 75 mm).
- Mounting the module on the robot's base, and the competition lift height (the rails are 350 mm, uncut).
- Endstop (lift homing) and stack-present switch.

## Rules
- FAQ **Q1** (stack in the perimeter) and **Q9** (stack above 350 mm in the castle) are still open.
