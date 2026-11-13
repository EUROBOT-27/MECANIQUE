#!/usr/bin/env python3
"""Start tools/sync_robot.py in the background (output -> mechanical/robot/CAD_FC/sync.log) and return at once.

    python tools/hooks/sync_bg.py --claude     Claude Code Stop hook (.claude/settings.json): at the end of each turn,
                                               if a mechanism changed -> rebuild the robot and copy it into the LOCAL
                                               sim clone. Says so in the Claude UI (a failed build: said once).
    python tools/hooks/sync_bg.py              git hooks (post-commit, post-merge): same, in the background.
Local only: no hook pushes to GitHub (2026-11-13). Push by hand: python tools/sync_robot.py --push
Never fails (exit 0): a hook must not block a commit or a Claude turn.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import sync_robot as s  # noqa: E402


def spawn(args):
    os.makedirs(s.CAD, exist_ok=True)
    log = open(s.LOG, "a", encoding="utf-8")
    cmd = [sys.executable, os.path.join(s.HUB, "tools", "sync_robot.py"), "--quiet"] + args
    kw = dict(stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, cwd=s.HUB, close_fds=True)
    if os.name == "nt":
        # no console window (freecadcmd is a console app), own process group, survive the hook's job if allowed
        flags = 0x08000000 | 0x00000200        # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
        try:
            subprocess.Popen(cmd, creationflags=flags | 0x01000000, **kw)   # + CREATE_BREAKAWAY_FROM_JOB
        except OSError:
            subprocess.Popen(cmd, creationflags=flags, **kw)
    else:
        subprocess.Popen(cmd, start_new_session=True, **kw)


def claude_stop():
    why = s.stale()
    if not why or s.locked():
        return None                           # up to date, or the running sync re-checks the sources when its build ends
    what = "; ".join(w.replace("changed: ", "") for w in why)
    if s.last_failed():                       # same sources as the failed build: don't rebuild, say it once
        sig = s.signature()
        try:
            if open(s.NOTIFIED, encoding="utf-8").read().strip() == sig:
                return None
        except OSError:
            pass
        open(s.NOTIFIED, "w", encoding="utf-8").write(sig)
        return ("Robot rebuild FAILED for the current mechanism files (%s). See mechanical/robot/CAD_FC/sync.log. "
                "It retries by itself when a mechanism file changes again, or run: python tools/sync_robot.py" % what)
    spawn([])
    return ("Mechanism changed (%s) -> rebuilding the full robot + Gazebo model in the background (~3 min) and "
            "copying it into the local sim clone (not pushed to GitHub). Log: mechanical/robot/CAD_FC/sync.log" % what)


def main():
    try:
        if sys.argv[1:2] == ["--claude"]:
            msg = claude_stop()
            if msg:
                print(json.dumps({"systemMessage": msg}))
        else:
            spawn(sys.argv[1:])
    except Exception as e:          # never break the caller
        print("sync_bg: %s" % e, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
