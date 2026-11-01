# Eurobot 2027 — Project Hub

This folder is the working hub for our Eurobot 2027 robot (theme: **"The Legend of Camelot"**).
Team: **IEEE RAS INSAT** (Tunisia). Not to be confused with Aerobotix INSAT, another INSAT club whose 2026 robot we study.
The main Claude session acts as the **project chief**: it keeps the timeline, rules, decisions and
priorities in view and pushes back when work drifts away from the critical path.

## Who uses this hub

The hub is **shared** by the two tech leads, each with Claude, all year long (D-018):
- **Seif**: overall tech lead, mechanical design + computer vision. Started the hub on 2026-10-25.
- **Mohamed Ali Maatoug**: software lead; also turns mechanical designs into fabrication-ready CAD
  (FreeCAD / SolidWorks prompt-to-CAD scripts).

It is one git repo (GitHub org **EUROBOT-27**, repo `MECANIQUE`); each of them works in their own clone.
**Who you are talking to** comes from the personal memory (`claude-workspace/memory/user-profile.md`, not committed).
If it's missing or unclear, ask before assuming.

Areas and who confirms decisions there:
| Area | Lead |
|---|---|
| Mechanical (`mechanical/`), vision (`vision/`) | Seif |
| Software (`software/`) | Maatoug |
| Fabrication CAD of a mechanism | Maatoug, on a design Seif agrees with |
| SIMAs (`simas/`) | Hamza Sammoud, followed by Seif |

A decision in someone else's area is logged with status `proposed` until that lead confirms it.

## Timeline (absolute dates)

| Milestone | Date | Notes |
|---|---|---|
| Kickoff of this hub | 2026-10-25 | |
| **Mechanical structure + mechanisms built and assembled** | **2026-12-31** | 3D printing, laser cutting, aluminium profiles, rods |
| **National qualifier** | **end of March 2027** (exact date TBD) | |

Detailed internal milestones (design freeze etc.) live in `project/timeline.md`.
Always compute "days left" from today's date — never write relative dates ("next week") into files.

## Team

| Area | People |
|---|---|
| Tech leads | Seif (mechanical + CV, overall tech lead), Maatoug (software lead) |
| CAD (SolidWorks) | Seif, Ayoub, Baha; Maatoug (fabrication CAD: parts ready to print, laser-cut, cut to length) |
| Electrical design | Hamza Bjaoui |
| Software — ROS | Fradi, Loumi |
| Software — navigation | Ben Azza, Nesrine |
| Management (non-technical) + SIMAs | Hamza Sammoud |

In scope: mechanical, fabrication CAD, vision, **software** (`software/`), **SIMAs** (`simas/`).

## Project-wide constraint: hardware sourcing (Tunisia)

Hardware availability in Tunisia is limited, and imports take time (orders from France take a few days to arrive).
- When proposing a component, mention whether it likely needs importing, and suggest a local alternative where possible.
- Prefer designs that tolerate substitutions (e.g. not locked to one exact motor size).
- **Don't track orders or purchases** (decision 2026-10-25). Exception (D-012): parts already
  in hand are listed in `mechanical/parts-library.md` and designs are checked against it.

## How we work (session workflow)

- **`/start`** at the beginning of a session → `git pull`, then briefing from `STATUS.md`, your own `todo/<name>.md`,
  the last logs (yours and the other lead's), timeline.
- **`/wrap`** at the end → write `logs/YYYY-MM-DD-<name>.md`, update your `todo/<name>.md` and `STATUS.md`,
  then **commit and push**.
- **Git:** everyone works on `main`. Pull before you start and before logging a decision; commit + push at wrap
  (and right after logging a decision). Small commits, clear messages. Never force-push.
- **Binary CAD files can't be merged.** One owner per CAD file at a time; say so before editing someone else's file
  (or use `git lfs lock <file>`). Large binaries go through Git LFS (`.gitattributes`).
- **Decisions are logged immediately** in `project/decisions.md` when made — not at wrap time.
  A decision = something the team commits to (concept chosen, dimension fixed, option rejected).
  Ideas and brainstorming go to `project/strategy.md` or the area's notes, not the decision log.
  If unsure whether something was decided or just discussed, ask the user.
- Any rule claim must cite the section (e.g. "General rules F.3"). If the rules are ambiguous, say so
  and add the question to the FAQ list in `project/rules-digest.md` — don't guess.
- For heavy rule verification, delegate to the `rules-checker` agent.
- For design ideas or "how did other teams do X", check `resources/INDEX.md` first and open only the matching
  resources (and their `_notes/` if they exist). Never browse `resources/` blindly.
- Token economy: read PDFs once and save what matters into a markdown file (digest, notes, index), then use
  those files instead of the source.
- Language: **English** for all files. Dates: ISO `YYYY-MM-DD`.
- Paths in committed files are **relative to the hub** — never `C:\Users\...` or `C:\Projects\...` (the clones are
  in different places on each PC).

## File map

| Path | What |
|---|---|
| `STATUS.md` | One page: where the team is right now (shared; updated at each wrap) |
| `todo/seif.md`, `todo/maatoug.md` | Each lead's task list + follow-ups with others |
| `commands.txt` | Cheat sheet of commands |
| `Docs/` | Official documents — **never edit** |
| `project/rules-digest.md` | All constraints that matter, with rule references + open FAQ questions |
| `project/reference/` | UTF-8 text extracts of the rule PDFs (searchable with grep) |
| `project/strategy.md` | Strategy brainstorming and scoring analysis |
| `project/timeline.md` | Detailed timeline and internal milestones |
| `project/decisions.md` | Numbered decision log (shared — pull before adding a number) |
| `mechanical/` | Mechanical design work — has its own `CLAUDE.md` |
| `mechanical/parts-library.md` | Parts we have in hand (Ender 3 V2 teardown + others); designs are checked against it |
| `mechanical/clapets-v5/` | Clapets v5 design (Maatoug), self-contained: FreeCAD scripts in `fc/`, CAD outputs, `docs/` |
| `mechanical/simulations/` | All mechanism animations / motion studies / simulation videos (index: `INDEX.md`) |
| `mechanical/design-principles.md` | Our design + testing standard (from the Aerobotix 2026 study) |
| `software/` | Software work (ROS, navigation, interfaces) — has its own `CLAUDE.md` |
| `vision/` | Computer vision work — has its own `CLAUDE.md` |
| `simas/` | SIMAs (knights) — has its own `CLAUDE.md` |
| `tools/` | Helper scripts for prompt-to-CAD (FreeCAD, SolidWorks API) — see `tools/README.md` |
| `resources/` | Previous teams' material (mechanical + software), committed as snapshots — start at `resources/INDEX.md` |
| `eurobot2027/` | **Not committed.** Local clone of `Simulation-Euro27` (org EUROBOT-27). Clone it yourself: `git clone https://github.com/EUROBOT-27/Simulation-Euro27 eurobot2027/Simulation-Euro27` |
| `logs/` | One file per person per session day: `YYYY-MM-DD-<name>.md` |
| `claude-workspace/` | **Not committed.** Claude's personal scratch space and memory |

## Key rule numbers (quick reference — full list in `project/rules-digest.md`)

- Table 3000 × 2000 mm. Match 100 s. Prep time 3 min. Start area ("throne room") 500 × 500 mm.
- Robot perimeter ≤ 1200 mm at start, ≤ 1400 mm deployed. Height ≤ 350 mm at all times (e-stop may reach 375 mm).
- Beacon support top at 430 ± 5 mm, mandatory. Avoidance system, e-stop and 500 mm start cord mandatory.
- Stone = cardboard box 320 × 110 × 110 mm, ~90 g, ArUco ID 13 on the 4 long faces. 30 stones, 3 per quarry.
- Attack phase (SIMAs, cannonballs) only from 85 s to 100 s.
