# SIMAs (knights) — context

Read the root `CLAUDE.md` and `project/rules-digest.md` §4.4 and §6 for the full picture.

## Ownership
- SIMA lead: Hamza Sammoud.
- Seif tracks SIMAs here as tech lead. Coordinate with mechanical if the main robot launches or carries them.

## Constraints [GR F.7], [G E.4]

| Constraint | Value |
|---|---|
| Size min | larger than a Ø80 mm cylinder, height ≥ 150 mm |
| Perimeter | ≤ 600 mm at start, ≤ 700 mm deployed |
| Height deployed | ≤ 175 mm |
| Weight | ≤ 1.5 kg |
| Sticker | 30 × 30 mm area |
| Safety | same as robots: e-stop, **avoidance system**, laser rules, LiPo bag… |
| Start | own 50 cm pull-cord, or launched by the robot during the match; must move by itself |
| Colour | must work for either team colour |
| Activation | nothing from outside the table |
| No beacon | no beacon mast or support |

## Game role
- Start in the **stable** (200 × 300 mm, 2 per team in the corners — from the drawing). How many SIMAs fit per stable: TBD.
- **Must not leave the stable before 85 s** → removed from the table otherwise.
- Points (only between 85 s and 100 s):
  - 5 per opposing moat occupied (~3 moats per castle — from the drawing, verify)
  - 5 if at least one SIMA touches an opposing SIMA with a **distinctly coloured**, non-damaging actuator
  - SIMAs may each carry **1 cannonball** and launch it into the opposing courtyard (counts toward the cannonball points)
- A SIMA alone can play if the main robot is unavailable (if homologated).

## Naming
The team calls SIMAs **"PAMI"** (the old name). Both mean the same thing in this hub.

## Plan (brainstorm, 2026-10-25 — see `project/strategy.md`)
Three versions get built and tested; the tests decide which ones are used, and how many:
1. **Basic PAMI:** reaches its goal position (opposing moat).
2. **Ejector PAMI:** carries 1 ball and ejects it into the opposing castle. If it works, make 3 (backup for the robot
   launcher; 3 balls = 5 + 15 pts). Ejecting from inside a moat scores the moat points too.
3. **Attack PAMI:** touches an opposing SIMA with a distinctly coloured actuator.

## Size envelope from the stables (Claude, 2026-10-26 — estimate)
Stable = 200 × 300 mm (lines included) [G E.4]; 2 stables per team, in our two corners. Keep ~5 mm placement clearance per side.

| PAMIs per stable | Max footprint each | Perimeter (≤ 600 at start) | Total |
|---|---|---|---|
| 1 | 190 × 290 → **cap to ~150 × 150** by perimeter | 600 | 2 |
| **2 (recommended)** | **~140 × 160 mm** (2 side by side along the 300 mm side) | 600 | **4** |
| 3 | ~90 × 185 mm (narrow, tippy at 150 mm tall) | 550 | 6 |

→ **4 PAMIs of ≤ 140 × 160 mm footprint**, 150–175 mm tall, ≤ 1.5 kg. That fits the plan: 3 ejectors (one per opposing moat)
+ 1 attack/basic. Still to fit inside: e-stop, avoidance sensor, battery, 1 ball, drive.

**5 or 6 PAMIs (Seif asked, 2026-10-26):** they fit at **~90 × 185 mm** each (3 per stable, side by side along the 300 mm side,
long side pointing at the opponent). 5 PAMIs = same size as 6 (one stable holds 3), unless we make two different designs.
- **Points:** 4 PAMIs already reach the max (3 moats + 1 attack + 3 balls). PAMIs 5 and 6 are **spares**, useful
  because PAMIs get blocked, not extra points.
- **Harder build:** 90 mm wide leaves ~45 mm per side for motor + wheel. Two N20 gear motors in line barely fit;
  right-angle motors or motors placed one in front of the other with a small belt are safer. Narrow and 150 mm tall → keep the battery low.
- **Start:** each SIMA needs its own 50 cm cord, or the robot starts them during the match [GR F.7].
  Pulling 6 cords at once with 2 people is impractical → **the robot starts them by radio** (nothing from outside the table).
- **Prep time:** placing 6 PAMIs + loading 6 balls fits in the 3 min [GR H.1], but practise it.
- Suggestion: pick the envelope early, because it drives the whole PAMI design. 4 × 140 × 160 is comfortable; 6 × 90 × 185 gives spares but is harder to build.
Reach: ~2.1–2.6 m in ≤ 15 s → cruise ~0.35–0.4 m/s. Ejector must lob over ~350–450 mm buildings at short range.
Details in `project/strategy.md` → "Table measurements".

## Reference
Our club's 2026 SIMA ("Ninja"): `resources/INSATEURO2026/Pami/`. Its `specification.md` has a step-by-step test
procedure worth reusing (encoder calibration → lifted test → ground test → full run). See `resources/_notes/insateuro2026.md` §4.

## Open points
- Number of SIMAs, design concept, timing (85 s start → ~15 s to reach the opposing moat).
- Sourcing: small motors, batteries, sensors — check local availability early.
- Avoidance: SIMAs need their own avoidance system, and our robot's LiDAR + vision must also detect the **opponent's** SIMAs (D-007).
