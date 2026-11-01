# Parts library — what we have in hand

Parts the team physically has (D-012), so designs **make use of everything we already own**. Not a shopping
list or order tracker.

## How Claude uses this file
- **The library is a preference, not a limit.** First reach for a part listed here. If nothing fits, any part
  **available in Tunisia** is fine. Only flag a part as a problem if it has to be imported (then suggest a local
  alternative, root `CLAUDE.md` → sourcing).
- In every design, list the parts and mark each one: 📦 in library · 🇹🇳 buy locally · ✈️ import.
- `verified` lines (counted + measured) are facts. `seen` = visible in a photo, size/count estimated from the
  photo. `planned` = chosen for a design but not in hand. Treat sizes on `seen` lines as assumptions and say so.
- Photos: `mechanical/resources/` (files named by the first 8 characters below, e.g. `a45eb9fd…jfif`).
- When a part gets committed to a mechanism, write it in "Used in".

Status: `verified` · `seen` · `planned` · `used` · `broken`
Source: **Ender** = the disassembled printer. **Correction 2026-10-27: it is a Two Trees (Bluer family?, model to confirm on its label), not an Ender 3 V2.** "Ender" is kept as a short tag. Its parts are Ender-3-like but sizes are NOT guaranteed to match Ender drawings. **Its CAD: `mechanical/resources/3D Printer Two Trees Bluer V2.3dm`** (Rhino; the model is a Bluer V2) · **Lab** = club stock

---

## 1. Structure — aluminium profiles and brackets

| Part | Spec | Qty | Source | Status | Photo | Used in | Notes |
|---|---|---|---|---|---|---|---|
| Profile 20-series, black | 2040 and/or 2020, lengths ? | several | Ender | seen | c5f6b2e7, fd140e84, 83f4534a | | Ender frame: Z uprights, top bar, X beam, base. Measure each length; check slot width (6 mm?) and tapped ends (M5?) |
| Profile 2020, silver, short offcuts | 20 × 20, centre bore tapped | 2 | Lab | seen | 314f82e3, a45eb9fd | | ~60 mm and ~150 mm. Good for brackets/test rigs |
| Inner corner connector (L, hidden) | for 20-series slot, set screws | 2 | Lab | seen | 5b45988a, c4f8640e | | Joins two profiles at 90° inside the slot, invisible joint |
| T-nuts / hammer nuts | 20-series slot, thread M4 or M5 ? | ≥ 5 | Ender/Lab | seen | b6e9494c | | Check thread size |
| Bed carriage plate (Y), "butterfly" | black steel plate, 4 V-wheels, bed spring holes; rides on the 2 Y rails | 1 | Ender | seen | fd140e84 | | Flat rigid plate with V-wheel mounts → ready-made carriage on a 40-wide profile |
| Ender X carriage plate | blue steel, 3 V-wheels | 1 | Ender | seen | c5f6b2e7 | | Ready-made carriage on 20-series profile (lift!) |
| Ender Z carriages (L + R) | steel plates with V-wheels | 2 | Ender | unverified | | | Check they're there |
| Bent steel bracket, black, Z-nut holder | U-shape, T8 nut mounted, extra holes | 1 | Ender | seen | c349f2d1 | | Holds the T8 nut on the X gantry → reuse as lift nut bracket |
| Bent steel bracket, blue, slotted | flat strip with 2 bent tabs, 2 countersunk holes + 1 centre hole | 1 | Ender | seen | 5a5d6677 | | Belt/tensioner or display part; light bracket |
| Bent steel bracket, black, long L/Z | ~150 mm strip, bent ends, 2 screws | 1 | Ender | seen | 83f4534a | | Probably spool holder / display mount; makes a light arm or hook |
| Aluminium U-bracket | ~2 mm, central hole + 4-hole pattern on 2 faces | 1 | Lab | seen | c2979d5a | | Looks like a small motor/servo mount bracket |
| Aluminium flat links | 3 pieces: long link (~150 mm), short link (~60 mm), cross hub plate; big end holes + small holes | 3 | Lab | seen | chat photo 2026-10-27 | | Robot-kit links: arms, levers, linkages |

## 2. Linear motion

| Part | Spec | Qty | Source | Status | Photo | Used in | Notes |
|---|---|---|---|---|---|---|---|
| Lead screw T8 | Tr8, lead ? (8 mm on the Ender) | ~3 | Ender + Lab | seen | 314f82e3, 71b33ca8, a45eb9fd, 3a536510, c29d0350 | | Measure each length and lead (mm per turn). For lifts: Grail, gate (~110 mm Z) |
| T8 brass flange nut | 4-hole flange | ~4 | Ender + Lab | seen | 3a536510, c29d0350, c349f2d1 | | |
| Smooth rod (linear shaft) | Ø8 mm ? | ~6 | Lab | seen | 71b33ca8, a45eb9fd | | Check Ø (8?) and that they're hardened/straight; some have turned/threaded ends |
| Linear bearing block SCS8UU ? | aluminium housing, 4 holes, for Ø8 rod | 3 | Lab | seen | a45eb9fd | | Pair with the Ø8 rods for a guided slide |
| Shaft support SK8 ? | aluminium, clamp, 2 holes | 1–2 | Lab | seen | 71b33ca8, a45eb9fd | | Holds rod ends |
| V-wheels (POM, with bearings) | for V-slot, 625ZZ? | ≥ 5 + those on carriages | Ender | seen | c5f6b2e7, a45eb9fd, b6e9494c | | Count total |
| Eccentric spacers / plain spacers | for V-wheels | ? | Ender | unverified | | | |
| GT2 belt | 6 mm wide | 2+ pieces | Ender | seen | c5f6b2e7, fd140e84 | | Measure lengths |
| GT2 pulley 20 T + idlers | 5 mm bore | ~2 + 2 | Ender | seen (background) | 74235cea | | |
| Belt tensioners (X, Y) | Ender knob tensioners | 2 | Ender | seen | fd140e84 | | |

## 3. Rotation — bearings, shafts, couplers

| Part | Spec | Qty | Source | Status | Photo | Used in | Notes |
|---|---|---|---|---|---|---|---|
| Pillow block bearing KP08 ? | 2-bolt foot, Ø8 bore | 2 | Lab | seen | a45eb9fd | | Shaft support on a flat base |
| Flange bearing KFL08 ? | 2-bolt oval flange, Ø8 bore | 1 | Lab | seen (on a shaft) | 314f82e3, 71b33ca8 | | Lead-screw end support |
| Small ball bearings | ~Ø10–13 mm OD, plain + flanged (MR/623/F623 ?) | ~8 | Lab | seen | b6e9494c, a45eb9fd | | Read the codes on the shields |
| Larger ball bearings | 2RS, ~Ø22–35 mm OD (608 / 6000 / 6201 ?) | 2 | Lab | seen | a45eb9fd | | Read codes |
| Rod + pressed bearing | Ø8 rod with a ~Ø22 bearing on the end | 1 | Lab | seen | fb47ae7a | | Ready idler / roller |
| Flexible coupler (beam/slotted) | 5 → 8 mm ? | 2 | Ender + Lab | seen | a45eb9fd, c4f8640e | | Motor → lead screw |
| Brass hex coupler | small, set screw, ~3–4 mm bore | 1 | Lab | seen | b6e9494c | | For N20 motor shafts (wheels/arms) |
| Home-made shaft clamp blocks | aluminium blocks + shaft + set screw | 2 | Lab | seen | a45eb9fd | | Old mechanism parts: hub/arm clamps |

## 4. Motors and actuators

| Part | Spec | Qty | Source | Status | Photo | Used in | Notes |
|---|---|---|---|---|---|---|---|
| Stepper NEMA 17 | 42 × 42, length ? | 4 | Ender | unverified | | | Read labels (current, length). Lifts, rotating stages |
| DC gear motors **JGB** | model ? (JGB37-520 ?), voltage ?, rpm ? | "a bunch" | Lab | unverified (no photo) | | | Read the label: voltage, rpm, encoder yes/no. Good for arms, flippers, flywheel? (check rpm) |
| N20 micro gear motor | 12 mm, metal gearbox, D shaft 3 mm, ratio ? | ≥ 1 | Lab | seen | 8c208708 | | Small light actuators, PAMIs |
| Servo TowerPro **MG996R** | standard size, metal gears, ~10 kg·cm class | ≥ 1 | Lab | seen | 3fe67375 | | Count them |
| Servo TowerPro **MG90S** | micro, metal gears, ~2 kg·cm class | ≥ 1 | Lab | seen | 3fe67375 | | |
| Servo Hitec **HS-755HB** | quarter scale (large), ~13 kg·cm class | ≥ 1 | Lab | seen | 3fe67375 | | Big servo for heavy flips (stone flipper?) |

## 5. Pneumatics (suction)

| Part | Spec | Qty | Source | Status | Photo | Used in | Notes |
|---|---|---|---|---|---|---|---|
| Mini air pump | 9.6–14.4 V (12 V typ.), air, 6.0 L/min, Ø31.8 × 66 mm | 6 | Lextronic order (2026-10) | planned (arriving) | | Stone gripper B (suction) | Vacuum level not given → test on real cardboard stones |
| Suction cup **DP S30** | size ? | ? | to source | planned | | Stone gripper B | Holder printed in **TPU** (decision of Maatoug, 2026-10-27). Note cup Ø and thread when they arrive |
| Push-in elbow fitting | blue collar, threaded body + swivel | ≥ 1 | Lab | seen | d5063d8b | | Check tube Ø (4 or 6 mm) and thread |

## 6. Fasteners

"Various nuts and screws of a lot of types" — no need to count every screw. Design with standard metric sizes;
the lines below just say which types we have.

| Part | Sizes seen | Source | Status | Photo | Notes |
|---|---|---|---|---|---|
| Socket head cap screws (DIN 912) | M3, M4, M5, M6 ? (stainless + 8.8 steel) | Ender + Lab | seen | 314f82e3, 5b45988a, c4f8640e | |
| Button head screws (ISO 7380) | M4/M5 | Ender | seen | c4f8640e | |
| Mushroom/truss head combi screws (Phillips + slot) | M5/M6, ~25 and ~45 mm | Lab | seen | 14c30a6e, 74235cea | |
| Flanged / carriage bolt | M8 ? | Lab | seen | 314f82e3, c4f8640e | |
| Hex bolts (8.8) | M8–M10 ? | Lab | seen | eedad378 | |
| Countersunk wood screws | ~4 × 40 | Lab | seen | b6e9494c | For wood/MDF test rigs only |
| Hex nuts | M5–M10 | Lab | seen | b6e9494c, cb3708fe, a45eb9fd | |
| Washers (incl. large fender washers) | M8/M10 | Lab | seen | a45eb9fd | |
| Threaded rods (zinc + black) | M8 / M10 ?, ~300–450 mm | Lab | seen | 71b33ca8, a45eb9fd | Cheap rigid ties, adjustable beacon mast? |
| **Brass heat-set inserts** | M2/M3/M4 (several compartments) | Lab | seen | 17a7e359 | **Use in every printed part that gets screwed** (D-006 style) |
| Brass hex standoffs (M-F, F-F) | M2/M3, several lengths | Lab | seen | 17a7e359 | PCB / board mounting |

## 7. Electronics (from the Ender, bench use)

| Part | Spec | Qty | Status | Notes |
|---|---|---|---|---|
| Mainboard Creality 4.2.2 / 4.2.7 | 32-bit, 4 stepper drivers | 1 | unverified | Test benches for steppers |
| Display 4.3" + knob | | 1 | unverified | |
| Endstops (mechanical switches) | | 3 | unverified | Homing a lift |
| Power supply 24 V | mains input | 1 | unverified | **Bench only, never on the robot** |
| Fans 24 V (4010 axial, blower) | | ~3–4 | unverified | |
| Heated bed + glass, hotend, extruder, bed springs | | 1 set | unverified | Low value; springs and glass can be reused |

---

## Committed: clapets proof of concept (D-014, one module)
PoC 2: 2 Y rails + butterfly plate with its 4 V-wheels · 4 × M5 + T-nut · 1 × NEMA17 ·
1 × 5→8 coupler · 1 × T8 screw + brass nut · 2 × Ø8 rod 166 mm (door rods, turning, split clamps) · 2 × MG996R · 1–2 endstops.
Details: `C:\Projects\EUROBOT\Mecanique\module_clapets_poc\README.md`.

## Still to do
- Measure: profile lengths, lead screw lengths + lead, rod Ø, bearing codes, JGB motor labels, servo counts.
- Photos `3fe67375`, `5a5d6677`, `cb3708fe` exist twice in `mechanical/images/` (identical files).
