# Castle building: ideas from other competitions (research 2026-11-18, Ayoub + Claude)

Ideas only, not decisions. Interactive page with an animation per idea (private, Ayoub):
https://claude.ai/artifact/BZsiKzudYLZN2ptLftoSg8

Searched: Google, YouTube, GitHub, VEX Forum, Robot Maker. No 2027 team has published a stone mechanism yet
(rules are beta 0.4; Bidulab, MechaKnights, ARC Lille, CDFR-2027 simulator repos hold software only).

| # | Idea | Builds | Seen in | Height check | Open point |
|---|---|---|---|---|---|
| 1 | **Tray tilter**: stone on a floor tray, tray turns 90° about a hinge at table level, stone stands up | towers, gate uprights | VEX Tower Takeover tray bots | corner peaks at 340 mm (√(320² + 116²)) | loading the stone onto the tray; tray 330 long vs 300 robot |
| 2 | **Bottom stacker**: end clamps lift the stack one stone high, next stone slides under | walls from loose stones | FRC 2015 Recycle Rush (Anastasia, 254) | max 335 mm | clamp force on cardboard end faces |
| 3 | **End clamps + 10 mm lift**: paddles squeeze the whole stack on its end faces, lift 10 mm, drive | walls | Eurobot 2025 (Mars Attacks! elevators), FRC stackers | 340 mm | middle stone held by friction; paddles add ~30 mm per side to the face width |
| 4 | **Fork under the lintel**: 20 mm fork raises the lintel to 324, tine passes in the 100 mm gap between the uprights, fork drops, lintel rests at 320 | gate | Eurobot 2025 rule: elements to 430 in construction zones, actuators ≤ 350 | fork ≤ 324; held stone top 434 | **FAQ Q9** (`project/rules-digest.md`) decides if it is legal |

Idea 3 answers the off-centre holder cup problem of central hub option B (`../central-hub/OPTION_B.md`, open point 8):
each stone is held through its centre line.

Set aside: several stacks in rows (needs a deeper robot than layout v1), virtual four-bar arm (350 mm limit; flip-bar
already covers four-bars), cone-righting device (not needed). Kept detail: closed HTD M5 belts with printed pulleys and
current-based homing (Mars Attacks!), brake pads on lift rails (FRC 449 Totedile).

Sources: listed at the bottom of the page above.
