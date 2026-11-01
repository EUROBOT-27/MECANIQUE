---
name: wrap
description: End-of-session wrap-up for the Eurobot 2027 hub — writes the day's log, updates the TODO and STATUS, commits and pushes. Run only when the user types /wrap.
disable-model-invocation: true
---

# /wrap — end-of-session wrap-up

The user's name (`seif` / `maatoug`) comes from the personal memory; if unknown, ask.

Go through the whole conversation of this session and collect:
- work done, and files created or changed
- decisions (committed choices) vs. ideas (still open)
- tasks completed, new tasks, changed owners or due dates
- problems, blockers, open questions, things we're waiting on
- new rule findings or interpretations

Then do these steps in order:

0. **Pull first** (`git pull`) so the files below are up to date. If there is a conflict, stop and explain it.
1. **Decisions** — check that every decision from this session is in `project/decisions.md` (use its template, next
   free D-number after the pull). If it's unclear whether something was decided or only discussed, ask the user before
   logging it. A decision in the other lead's area gets status `proposed` (see root `CLAUDE.md`).
   Ideas go to `project/strategy.md` or the relevant area folder, not to the decision log.
2. **Log** — write `logs/YYYY-MM-DD-<name>.md` (today's date). If the file already exists, append a `## Session 2`
   (3, …) section instead of overwriting. Sections: `Done`, `Decisions` (D-numbers + titles), `Info gathered`,
   `Problems / blockers`, `Next`. Keep it short and factual.
3. **TODO** — in `todo/<name>.md`: tick finished items and move them to `Done` with today's date; add new tasks with
   owner (and due date if one was given). A task for the other lead goes in their file under `From <name>`.
4. **STATUS.md** — shared by both leads. Update it: last-updated date + who, phase, next deadline with days left,
   where we are, top 3 risks, waiting on. Keep the other lead's still-valid points; don't delete them.
5. **Other files** — if this session changed them, update `project/rules-digest.md` (new findings, FAQ answers),
   `project/timeline.md`, `project/strategy.md`, `mechanical/CLAUDE.md`, `mechanical/parts-library.md`,
   `mechanical/design-principles.md` (new principles or test results), `mechanical/simulations/INDEX.md`,
   `software/CLAUDE.md`, `vision/CLAUDE.md`, `simas/CLAUDE.md`, `tools/README.md`.
6. **Resources** — if a resource was studied in depth this session, save the findings to
   `resources/_notes/<resource-name>.md` and link them in `resources/INDEX.md`.
7. **Commit and push** — `git status` first; show the user the list of changed files. Don't commit secrets, personal
   files (`claude-workspace/`), or temporary files. Commit with a short message
   (`wrap YYYY-MM-DD <name>: <main topics>`), then `git push`. If the push is rejected, `git pull` and push again;
   if that conflicts, stop and explain.
8. **Reply** with at most ~10 lines: what was saved and pushed, and the 1–3 most important things for next session.

Use absolute dates only (never "tomorrow" or "next week") in every file.
