---
name: start
description: Start-of-session briefing for the Eurobot 2027 hub. Run only when the user types /start.
disable-model-invocation: true
---

# /start — session briefing

1. Read these files:
   - `STATUS.md`
   - `TODO.md`
   - `project/timeline.md`
   - the most recent file in `logs/` (highest `YYYY-MM-DD` filename)
2. Take today's date from the environment. Compute the days left to each upcoming milestone in `project/timeline.md`
   (fixed and internal).
3. Check for:
   - TODO items with a due date that has passed   - "Waiting on" items in `STATUS.md` that have been open a long time
   - FAQ questions in `project/rules-digest.md` that are still `open`
   - whether the last session was wrapped: if `STATUS.md`'s "Last updated" date is older than the newest log, say so
4. Give the briefing in **this format, max ~20 lines**:

```
📅 <today> — <N> days to <next milestone> · <M> days to qualifier

Last session (<date>): <2–3 bullets>

Overdue / at risk: <items, or "nothing">
Waiting on: <items>

Suggested focus today:
1. <most important thing for the next milestone>
2. ...
```

5. Base the suggested focus on the critical path to the next milestone, not on what's easiest.
6. End by asking what Maatoug wants to work on today. Don't start working before the answer.
