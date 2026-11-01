---
name: start
description: Start-of-session briefing for the Eurobot 2027 hub. Run only when the user types /start.
disable-model-invocation: true
---

# /start — session briefing

0. **Who and sync.** The user's name comes from the personal memory (`user-profile`); if unknown, ask (Seif or
   Maatoug). Then run `git pull` in the hub folder.
   - If there are uncommitted local changes, tell the user and ask before pulling (suggest commit first).
   - If the pull hits a conflict, stop and explain it in plain words; don't resolve it without the user.
   - Summarise in 1–3 bullets what the other lead pushed since the user's last session (`git log` since the user's
     last log date, other authors).
1. Read these files:
   - `STATUS.md`
   - `todo/<name>.md` (the user's own list)
   - `project/timeline.md`
   - the user's most recent log in `logs/` (`YYYY-MM-DD-<name>.md`) and the other lead's most recent log
2. Take today's date from the environment. Compute the days left to each upcoming milestone in `project/timeline.md`
   (fixed and internal).
3. Check for:
   - TODO items with a due date that has passed
   - "Waiting on" items in `STATUS.md` that have been open a long time
   - FAQ questions in `project/rules-digest.md` that are still `open`
   - decisions with status `proposed` in `project/decisions.md` that wait for this user to confirm
   - whether the user's last session was wrapped (log exists, committed and pushed)
4. Give the briefing in **this format, max ~20 lines**:

```
📅 <today> — <N> days to <next milestone> · <M> days to qualifier

Pulled: <what the other lead pushed, or "nothing new">
Last session (<date>): <2–3 bullets>

Overdue / at risk: <items, or "nothing">
Waiting on: <items>
To confirm: <proposed decisions in your area, or "nothing">

Suggested focus today:
1. <most important thing for the next milestone>
2. ...
```

5. Base the suggested focus on the critical path to the next milestone, not on what's easiest.
6. End by asking what the user wants to work on today. Don't start working before the answer.
