# Rules Digest — Eurobot 2027

Sources (in `Docs/`, text extracts in `project/reference/`):
- **Game rules** — *Eurobot and Eurobot Junior 2027 Rules, OFFICIAL 1.0* → cited as **[G x.y]**
- **General rules** — *Eurobot contest general Rules, OFFICIAL 1.4* → cited as **[GR x.y]**
- Table plan `table_FINALE_1.0.pdf`, accessories sheet `accessoire_FINAL_v3.pdf`

> Rules can change during the year. Check www.eurobot.org and the FAQ (www.eurobot.org/faq/) regularly.
> FAQ answers from referees are **official** for refereeing and homologation [G A], [GR A].
> Referee contact: referee@eurobot.org [GR A].
>
> Items marked **(drawing)** were read from the table drawing, not from written rules. Written rules and the
> appendix always win over images [G A].

Last full review: 2026-10-25 (game rules v1.0, general rules v1.4).

---

## 1. Match format

| Item | Value | Ref |
|---|---|---|
| Match duration | 100 s | [GR H.2] |
| Preparation time | max 3 min per team on the table | [GR H.1] |
| Start | pull-cord ≥ 500 mm, cord must not stay attached; no other start system allowed | [GR F.6] |
| End | robots must stop and turn off all actuators at 100 s (dynamic displays may stay on) | [GR H.3] |
| People | max 2 team members backstage/on stage | [GR H] |
| Batteries | must handle 3 matches in a row incl. powered waiting time | [GR F.4.b] |

## 2. Playing area

| Item | Value | Ref |
|---|---|---|
| Table | 3000 × 2000 mm, borders 70 mm high × 22 mm thick | [G D.2] |
| Surface | printed gripping vinyl; joints may be imperfect; condition varies and degrades | [G D.1], [G D.2] |
| Start/finish area ("throne room") | 500 × 500 mm, at the table side, line included | [G D.3] |
| SIMA start area ("stable") | 200 × 300 mm; 2 per team, in the corners on the team's side (yellow x 5–195, y 5–295 and 1705–1995) **(table.svg, 2026-10-26)** | [G D.4] |
| Stone quarries | 10 quarries × 3 stones stacked horizontally = 30 stones; 4 against each long border (stones along x; x 590–910, 1090–1410, 1590–1910, 2090–2410), 2 in the centre (stones along y, x 1445–1555) **(table.svg, 2026-10-26)** | [G D.4] |
| Castle zones per team | 4 circular tower zones (Ø200), **5 rectangular wall zones** (200 × 400): 2 along the edges, 2 diagonal, 1 central facing the bridge **(confirmed in table.svg, 2026-10-26; coordinates in `project/strategy.md`)** | [G D.4] |
| Moats per castle | 3 (2 diagonal + 1 at the bridge) **(confirmed in table.svg, 2026-10-26)** | [G D.4] |
| Tolerances | ≤20: ±1.5 · 20–70: ±2.5 · 70–150: ±4 · >150: ±5 mm. No complaints accepted. | [GR J.2] |
| Colours | Blue RAL 5017 (RGB 0,91,140) · Yellow RAL 1023 (247,181,0) · Borders RAL 7032 (181,176,161) | [GR J.3] |

## 3. Game elements

| Element | Spec | Ref |
|---|---|---|
| Stone | cardboard box 320 × 110 × 110 mm, ~90 g (RAJA BLFA01 or equivalent). **Weight/density varies by country — test several.** ArUco **ID 13** on each of the 4 large faces | [G D.4], [G G.2] |
| Cannonball | 45 mm foam ball ("magician's ball"), compressible; 10 per team in team colour | [G D.4], [G G.2] |
| Grail | made by the team; same construction constraints as a SIMA except min size; must be larger than a 60 mm cube | [G E.2] |
| Knight (SIMA) | made by the team, see §6 | [G D.4] |

## 4. Actions and points

### 4.1 Construction of Camelot [G E.1]
- Stone counts as placed if any part of its vertical projection is in the zone, or it sits on a stone already valid for that zone.
- **Wall** = 3 stones horizontal, stacked → in a rectangular wall zone. Height 330 mm.
- **Tower** = 1 stone vertical → in a circular zone. Height 320 mm.
- **Gate** = 2 stones vertical + 1 horizontal on top → in a rectangular wall zone. Only **one gate per castle**. Top of gate at 430 mm.
- One building per zone. Extra buildings give no construction points, but stones still count.
- A stone can't count for two constructions. Elements still controlled by the robot at the end don't count.
- Up to **3 stones may be stored in the castle courtyard** during the match.
- Stealing stones from the opponent's castle is allowed **only once all quarries are empty**, and without just wrecking it (≥50 pt penalty otherwise).
- Game elements may exceed the height limit **only inside construction zones / castle**. **Actuators must respect 350 mm at all times.**

| Points | |
|---|---|
| 1 | per stone in a construction zone |
| 5 | per wall |
| 5 | per tower |
| 20 | per gate |

### 4.2 I have the real one! (Grail) [G E.2]
- Placed on the **throne room floor** during prep, fully inside the area, **not under robot control**.
- During the match the robot picks it up and places it on a support (stone, construction or robot).
- Score depends on the **lowest point of the Grail** at the end:
  L1 = 1 horizontal stone · L2 = 2 horizontal · L3 = 3 horizontal or 1 vertical · **L4 = on the robot's roof (>300 mm), free of any actuator or fixing system**.
- Grail must stay **fully inside the castle area during the whole match**, otherwise removed.
- Grail may exceed the height limit only in construction zones/castle; actuators still ≤ 350 mm.
- Must not move the opponent's Grail. A Grail still held by an actuator at the end doesn't count.

| Points | |
|---|---|
| 5 | Grail present in the castle |
| 5 | per elevation level (max L4 → 20) |

### 4.3 Return of the King [G E.3]
- At the end, the main robot must be stopped in its throne room. SIMAs excluded.

| Points | |
|---|---|
| 5 | main robot partially in its area |
| 10 | main robot completely in its area |

### 4.4 To the attack! [G E.4]
- **Attack phase = 85 s → 100 s.** Actions outside it don't count.
- SIMAs start in the stable; leaving it **before 85 s** → removed from the table.
- Cannonballs loaded during prep into the robot and SIMAs, **max 1 per SIMA**.
- SIMA scores if any part of its projection is in an opposing moat at the end.
- SIMA "attack" = one of its actuators touches an opposing SIMA at the end. That actuator must have a **distinct colour**, must not damage, and is the only part allowed to touch.
- Cannonball scores if any part of its projection is in the **opposing courtyard** at the end. No height limit during flight. Don't interfere with opposing balls.

| Points | |
|---|---|
| 5 | per opposing moat occupied |
| 5 | if ≥1 SIMA attacks an opposing SIMA |
| 5 | if ≥1 cannonball in opposing castle |
| +15 | if ≥3 cannonballs in opposing castle ("additional" → only if the base 5 is validated [GR H.4]) |

## 5. Main robot constraints

| Constraint | Value | Ref |
|---|---|---|
| Perimeter (convex hull of vertical projection) | **≤ 1200 mm at start**, **≤ 1400 mm deployed**, at all times | [GR F.3] |
| Height | **≤ 350 mm** for robot **and manipulated objects**, at all times. E-stop may reach 375 mm. Excludes beacon mast + sensors under it | [GR F.3] |
| Start position | vertical projection fully inside the 500 × 500 start area at end of setup | [G D.3] |
| Beacon support | top flat & horizontal at **430 ± 5 mm** (adjustable recommended); convex shape ≥ Ø70, ≤ 100 × 100 square; solid, opaque (IR + visible); top fully covered with Velcro (hook); within Ø200 circle around robot centre; full between 350 mm and top (rotating-sensor gap < 20 mm); holds ≥ 400 g without flexing; only sensors/telecom on it | [GR F.6] |
| Sticker space | 100 × 70 mm flat free area on one side face | [GR F.6] |
| Avoidance system | mandatory, checked at homologation; must detect opposing robots **and SIMAs** | [GR F.6] |
| E-stop | red, Ø ≥ 20 mm, on top, visible, hit with a fist, stops immediately | [GR F.4.c] |
| No loose parts | robot must not leave parts on the table (−20 pts) | [GR F.1], [GR H.4] |
| Commercial bases | allowed only if significantly modified | [GR F.2] |
| Originality | robots noticeably similar to other teams' → **disqualification** | [GR H.4] |
| Look | should be aesthetic and on-theme; SIMA/robot visual harmony desired | [GR E], [G D.4] |

## 6. SIMA (knights) [GR F.7]
- Same building and safety rules as robots (e-stop, avoidance, laser, LiPo bag…). Must work for either team colour.
- Start by its own 50 cm cord, or launched by the robot during the match. Must be able to move by itself.
- Bigger than a Ø80 mm cylinder, **min height 150 mm**.
- Perimeter ≤ 600 mm at start, ≤ 700 mm deployed. Deployed height ≤ 175 mm.
- Weight ≤ 1.5 kg. 30 × 30 mm sticker area. No beacon mast/support.
- Cannot be activated from outside the table.
- Homologation of SIMAs is optional, but required to use them.

## 7. Safety & energy [GR F.4]
- Allowed energy: batteries, springs/elastics, compressed air (≤ 4 bar unless unmodified commercial), gravity.
- ≤ 48 V DC. Unmodified batteries only.
- **LiPo**: suitable charger (homologated) + certified fireproof bags at all times. Exceptions: packs with manufacturer BMS and hard case (e.g. power-tool packs), and **LiFePO4**.
- Fuse near the battery strongly advised; size wires properly.
- Lasers: class 1/1M OK; class 2 only if the beam stays in the table and switches off when the robot is lifted; 2M+ forbidden.
- Sound ≤ 80 dBA at 1 m. No dangerous light intensity.

## 8. Beacons, remote device, markers [GR G]
- **Fixed beacons**: up to 3, each within 100 × 100 × 1000 mm, ≤ 1.5 kg, fixed with M8 threaded rod + wing nut on supports around the table.
- **On-board beacon** (placed on the *opponent's* robot): ≤ 100 × 100 × 80 mm, ≤ 300 g, Velcro top and bottom.
- **Remote computing & observation device**: on the shared platform at the table edge on the central axis; within 450 × 320 mm footprint; up to **1.6 m above** the platform top; ≤ 5 kg; M8 rod + wing nut; may vibrate. Can be wired to fixed beacons. Must not act on game elements.
- **Robot ID marker** (provided): 100 mm square, 20 mm thick, ≤ 100 g, 70 mm ArUco 4×4 on top, on the beacon support. **Blue: IDs 1–5, yellow: 6–10.** IDs 11–50 reserved for the playing area.
- **Teams must not use ArUco 4×4 IDs 0–50.** Team-reserved: **51–70 blue, 71–90 yellow**; IDs > 90 or other dictionaries are allowed.
- No communication with anything outside the table during matches [GR F.6]. 5 GHz WiFi recommended [GR F.5].
- Expect strong, changing ambient light and unpredictable things around the table — can't ask people to move [GR F.5].

## 9. Penalties [GR H.4] (warning first, then points; only the highest applies per match)
| Penalty | Points |
|---|---|
| Lost part on the table | −20 |
| Damaging table / game element | −30 |
| Non-functional avoidance | −30 |
| False start · moving after time · excessive prep | −50 |
| Unsportsmanlike | −50 to −100 |

**Forfeit:** no robot and no SIMA leaves the start area · **dimensional limits not respected** · touching anything after prep · entering an opposing exclusive area · moving the table.
**Disqualification:** disabling avoidance on purpose · robot similar to another team's · damaging other robots on purpose.

## 10. Homologation [GR I.3]
- **Static**: referees check compliance; all mechanisms must be easy to show. Accessories checked too.
- **Dynamic**: alone on the table, within 100 s, **robot (and SIMAs) leave the start area and the robot validates at least one action**. Timer and avoidance are checked.
- Significant changes after homologation must be declared → re-homologation.

## 11. Project presentation [GR E]
- **Technical poster mandatory**: ≥ A1, team name, full member names, country + flag, design drawings/strategy; understandable by non-technical public; English version for international finals; PDF ≤ 25 MB. Deadline is in the conditions of participation (**date TBD**).

---

## Derived constraints (our reading — not written rules)

1. **Robot + Grail share the 500 × 500 throne room at start**, and the Grail must not be under robot control. The robot footprint must leave room for the Grail (unless the Grail can sit under the robot — see FAQ Q4).
2. **Gate lintel problem**: the top stone sits at 320–430 mm, but the actuator must stay ≤ 350 mm. Only ~30 mm of the lintel's height is reachable while lowering it onto the uprights.
3. **A quarry stack = a ready-made wall** (3 horizontal stones, 330 mm tall, under the 350 mm limit). Carrying a full stack keeps you under the height limit. Working assumption: carried stones don't count in the
   perimeter (Q1, to confirm).
4. **Grail L4 + full return home** both require the robot to finish in the castle, so they combine: 10 + 5 + 20 = 35 pts. But the Grail must stay inside the castle all match, so the robot can only carry it while staying in the castle.
5. Stone dimensions have ±4/±5 mm tolerance and cardboard deforms → grippers must take up the slack.
6. **Tag 13 is only on the 4 long faces** [G D.4], so a standing stone (tower, gate upright) shows no tag to an
   overhead camera. Lying stones do.
7. **Laptop/computer + camera at the table** must be the remote computing device [GR G.4]. Fixed beacons only allow
   sensors and telecom, within 100 × 100 × 1000 mm and 1.5 kg [GR G.1, G.3].

## Open questions for the FAQ / referees

| # | Question | Why it matters | Status |
|---|---|---|---|
| Q1 | Does a carried game element (stone) count in the robot's perimeter (convex hull)? [GR F.3] only says height includes manipulated objects. | Decides whether we can carry a 320 mm stone / a full quarry stack | **working assumption: does NOT count** (Seif, 2026-10-25). Seif will confirm with the FAQ |
| Q2 | Is the castle courtyard (incl. throne room) "the castle" for the Grail's 5 pts — i.e. does the Grail score 5 pts by just staying where it starts? | Free points / strategy | **likely yes:** the definitions say the castle courtyard "includes the throne room" [G D.4]. Low priority to send |
| Q3 | Which SIMA constraints apply to the Grail exactly? (max perimeter 600? max height 175? weight 1.5 kg? e-stop?) | Grail design | open |
| Q4 | Can the Grail be placed physically under the robot in the throne room if the robot doesn't hold it? | Robot footprint | open |
| Q5 | Is the gate restricted to a specific wall zone (e.g. the central one facing the bridge), or any rectangular wall zone? | Gate strategy | open |
| Q6 | What happens if more than 3 stones are stored in the courtyard? | Stone-buffer strategy | open |
| Q7 | Grail L4 "free of any actuators and fixing system": may the roof have a passive recess or rim to hold the Grail? | Roof design | open |
| Q8 | Grail on the roof (L4) "without blocking any opposing beacons" [G E.2]: is a Grail whose top passes 430 mm, next to our beacon support (where the opponent's on-board beacon sits), considered blocking? Is there a max Grail height on the roof? | Grail height / roof layout | open |
| Q9 | Inside a construction zone / the castle, may a stone **still held by the robot** go above 350 mm (e.g. gate lintel carried on a fork whose top stays ≤ 350 mm)? [GR F.3] says manipulated objects ≤ 350 mm; [G E.1] lets game elements exceed it in zones/castle, actuators still ≤ 350 mm. | Decides if the "fork under the lintel" gate method is legal | open |
