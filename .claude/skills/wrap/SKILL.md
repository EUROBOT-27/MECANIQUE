---
name: wrap
description: End-of-session wrap-up for the Eurobot 2027 hub — writes the day's log and updates TODO and STATUS. Run only when the user types /wrap.
disable-model-invocation: true
---

# /wrap — end-of-session wrap-up

Go through the whole conversation of this session and collect:
- work done, and files created or changed
- decisions (committed choices) vs. ideas (still open)
- tasks completed, new tasks, changed owners or due dates
- problems, blockers, open questions, things we're waiting on
- new rule findings or interpretations

Then do these steps in order:

1. **Decisions** — check that every decision from this session is in `project/decisions.md` (use its template, next
   free D-number). If it's unclear whether something was decided or only discussed, ask Maatoug before logging it.
   Ideas go to `project/strategy.md` or the relevant area folder, not to the decision log.
2. **Log** — write `logs/YYYY-MM-DD.md` (today's date). If the file already exists, append a `## Session 2` (3, …)
   section instead of overwriting. Sections: `Done`, `Decisions` (D-numbers + titles), `Info gathered`,
   `Problems / blockers`, `Next`. Keep it short and factual.
3. **TODO.md** — tick finished items and move them to `Done` with today's date; add new tasks with owner (and due
   date if one was given); move items between sections if the priority changed.
4. **STATUS.md** — rewrite it completely: last-updated date, phase, next deadline with days left, where we are,
   top 3 risks, waiting on.
5. **Other files** — if this session changed them, update `project/rules-digest.md` (new findings, FAQ answers),
   `project/timeline.md`, `project/strategy.md`, `mechanical/CLAUDE.md`, `mechanical/parts-library.md`, `mechanical/design-principles.md`
   (new principles or test results), `software/CLAUDE.md`, `vision/CLAUDE.md`, `simas/CLAUDE.md`.
6. **Resources** — if a resource was studied in depth this session, save the findings to
   `resources/_notes/<resource-name>.md` and link them in `resources/INDEX.md`.
7. **Reply** with at most ~10 lines: what was saved, and the 1–3 most important things for next session.

Use absolute dates only (never "tomorrow" or "next week") in every file.
