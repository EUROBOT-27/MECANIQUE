---
name: wrap
description: End-of-session wrap-up for the Eurobot 2027 hub — writes the day's log, updates the TODO and STATUS, commits and pushes. Run only when the user types /wrap.
disable-model-invocation: true
model: sonnet
---

# /wrap — end-of-session wrap-up

The user's name (`seif` / `maatoug` / `ayoub`) comes from the personal memory; if unknown, ask.

Go through the whole conversation of this session and collect:
- work done, and files created or changed
- decisions (committed choices) vs. ideas (still open)
- tasks completed, new tasks, changed owners or due dates
- problems, blockers, open questions, things we're waiting on
- new rule findings or interpretations

Keep tool turns to a minimum: batch independent reads in one parallel turn, and don't open files just to check them.

Then do these steps in order:

0. **Pull, then read in one go.** `git pull` (if there is a conflict, stop and explain it). Then, in a single parallel
   turn, read `STATUS.md`, `todo/<name>.md`, today's log if it exists, and run the decisions grep from step 1.
1. **Decisions** — don't read all of `project/decisions.md`. Run `grep -n "^## D-" project/decisions.md` to get the
   titles and the next free D-number, and check this session's decisions against that list. Only open the file's
   template (top 20 lines) if you need to add one. If it's unclear whether something was decided or only discussed,
   ask the user before logging it. A decision in another lead's area gets status `proposed` (see root `CLAUDE.md`); a non-lead's
   (e.g. Ayoub's) decisions are always `proposed` until the area lead confirms.
   Ideas go to `project/strategy.md` or the relevant area folder, not to the decision log.
2. **Log** — write `logs/YYYY-MM-DD-<name>.md` (today's date). If the file already exists, append a `## Session 2`
   (3, …) section instead of overwriting. Sections: `Done`, `Decisions` (D-numbers + titles), `Info gathered`,
   `Problems / blockers`, `Next`. Keep it short and factual.
3. **TODO** — in `todo/<name>.md`: tick finished items and move them to `Done` with today's date; add new tasks with
   owner (and due date if one was given). A task for someone else who has a TODO file goes in their file under `From <name>`.
   If `todo/<name>.md` doesn't exist yet, create it in the same format as the others.
4. **STATUS.md** — shared by all users. Update it: last-updated date + who, phase, next deadline with days left,
   where we are, top 3 risks, waiting on. Keep the other users' still-valid points; don't delete them.
5. **Other files** — only update area files (`project/*.md`, the area `CLAUDE.md` files, `parts-library.md`,
   `design-principles.md`, `simulations/INDEX.md`, `tools/README.md`, `resources/_notes/` + `INDEX.md`) when this
   session produced something that belongs there. Decide from the conversation; don't open a file just to check it.
6. **Commit and push** — one `git status --short`; show the user the list of changed files. Don't commit secrets,
   personal files (`claude-workspace/`), or temporary files. Then `git add <files> && git commit -m "..." && git push`
   as a single command, message `wrap YYYY-MM-DD <name>: <main topics>`. If the push is rejected, `git pull` and push
   again; if that conflicts, stop and explain.
7. **Reply** with at most ~10 lines: what was saved and pushed, and the 1–3 most important things for next session.

Use absolute dates only (never "tomorrow" or "next week") in every file.
