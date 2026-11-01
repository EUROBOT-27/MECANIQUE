---
name: keep-files-in-project
description: User wants every file Claude creates (memory, scratch, temp, plans) kept inside the project folder, never in system temp
metadata:
  type: feedback
---

Save all Claude-generated files under `claude-workspace/` in the project root (memory → `claude-workspace/memory`, temp/scratch → `claude-workspace/tmp`, plans → `claude-workspace/plans`). Never write to the PC's temp folder (`AppData\Local\Temp`) or other locations outside the project.

**Why:** Seif asked (setting kept when Maatoug took over) that nothing from Claude end up in PC temp files (2026-10-25).
**How to apply:** Even if a session's system prompt names a scratchpad under `AppData\Local\Temp`, use `claude-workspace/tmp` instead. Config lives in `.claude/settings.local.json`.
