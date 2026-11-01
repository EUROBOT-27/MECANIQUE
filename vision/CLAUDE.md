# Computer Vision — context

Read the root `CLAUDE.md` and `project/rules-digest.md` for the full picture. This file holds what matters when
working on CV.

## Ownership
- CV: Seif.
- Consumers of CV output: software team (ROS: Fradi, Loumi · navigation: Ben Azza, Nesrine · lead: Maatoug).
  Interface format (topics, frames, rates) to be agreed later — see TODO backlog.

## ⚠️ Critical responsibility: opponent tracking (D-007)
**LiDAR + vision** together track the opponent and form the **mandatory avoidance system** [GR F.6], which is
checked at homologation. A non-working system costs −30 pts [GR H.4].
- To decide: how the two combine (e.g. LiDAR for close-range distance, vision for identity and the global
  position), and what happens when they disagree.
- **LiDAR height matters:** mounted on the mast (~350–430 mm), it sees beacon supports, not SIMAs (≤ 175 mm).
  SIMAs need vision or a low-mounted sensor.
- Must detect the opposing **robot and its SIMAs** [GR F.6]. SIMAs are short (150–175 mm) and carry **no ArUco marker** [GR F.7].
- Opposing robot: ArUco marker on top at ~430 mm, **IDs 1–5 (blue) / 6–10 (yellow)**, assigned randomly [GR G.6].
- **Decided (D-008):** overhead camera + laptop on the remote computing device at the table edge; wireless link
  to the robot (tech chosen by the software team).
- **Idea (Seif):** put team ArUco tags on **our** SIMAs. Use IDs **> 90** so the same tag works for both colours
  (51–70 blue / 71–90 yellow also allowed) [GR G.6]. Opponent SIMAs: to decide later.
- Vision work (camera choice, accuracy, etc.) starts later. **Mechanical is the priority now.**
- Earlier camera options (for reference):
  - **Overhead camera** on the remote computing device (up to 1.6 m above the table edge) [GR G.4]: sees the whole
    table and every robot marker. It's on the table, so talking to our robot is allowed [GR F.6].
  - **On-board cameras**: no extra hardware off the robot, but blind spots. Covering 360° needs several cameras.
  - Combination: overhead for global tracking + on-board for close range and SIMAs.
- Lesson from Aerobotix 2026: 10 Hz was too slow for an opponent moving at 1 m/s. Aim for a higher detection rate
  and low latency.

## Our club's 2026 vision work — read before building anything
Full study: `resources/_notes/insateuro2026.md` §1. Code: `resources/INSATEURO2026/Euro_vision/`.
- **Working recipe**: calibrate at the runtime resolution → ArUco DICT_4X4_50 → `solvePnP` on all 16 anchor corners
  → `P_world = Rᵀ(P_cam − t)` → moving average / Kalman. Result: 30 FPS, ~35 ms, **~9 cm error**, ±2 mm jitter.
- **Post-mortem**: 14+ failed attempts were caused by wrong input data (marker size, calibration resolution).
  Check the inputs before the maths.
- **Must fix in 2027**:
  1. The compute must be **on the table** (remote computing device platform), not a PC beside it [GR F.6].
  2. One config file for marker IDs, sizes and positions (2026 had conflicting mappings across 4+ files).
  3. Use **known-height plane intersection** for better accuracy.
  4. Proper LiDAR + vision fusion (2026's was a plain average).
- **2027 twist**: stones have tag 13 on the long faces only, so **standing stones show no tag from above**.
  All 30 stones share ID 13, so they need spatial tracking (reuse the 2026 `CrateIDTracker` idea).

## What the rules give us

| Item | Detail | Ref |
|---|---|---|
| Stones | ArUco **ID 13** on each of the 4 large faces | G D.4 |
| Robot markers | 100 mm square, 70 mm ArUco 4×4 on top, at 430 mm (on beacon support). **Blue IDs 1–5, yellow 6–10.** Assigned randomly | GR G.6 |
| Table markers | IDs 11–50 reserved for the playing area; 4 tags visible on the table plan (**exact IDs to read from `Docs/table.svg`**) | GR G.6 |
| Our own tags | **must not use 4×4 IDs 0–50.** Blue 51–70, yellow 71–90, or IDs > 90 / other dictionaries | GR G.6 |
| Overhead camera option | remote computing & observation device on the platform at the table edge: up to **1.6 m above** the platform, 450 × 320 mm footprint, ≤ 5 kg, M8 rod fixing, may vibrate | GR G.4 |
| Fixed beacons | up to 3, 100 × 100 × 1000 mm, ≤ 1.5 kg | GR G.3 |
| Team colours | Blue RAL 5017 (RGB 0,91,140), Yellow RAL 1023 (247,181,0), borders RAL 7032 (181,176,161); hues vary between printed mats | GR J.3 |

## Environment warnings
- Strong, changing ambient light; people, decor and electronics around the table; can't ask anyone to move [GR F.5].
- Recording cameras may be set up on unused table edges [G D.2].
- No communication with anything off the table during matches [GR F.6]. Prefer 5 GHz WiFi [GR F.5].
- Table surface condition varies and degrades [G D.1].

## Other possible CV uses (brainstorm — nothing decided)
- Overhead camera: also localise our own robot (ArUco on top) and stones.
- On-board camera: detect stones (ID 13) for pickup alignment; check quarries are empty.
- Colour detection for team side / cannonballs.

## Working conventions
- Put experiments in `vision/experiments/<date>-<topic>/`, with a short README of what was tried and the result.
- Record the ArUco dictionary and IDs used in every script.
