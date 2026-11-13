#!/usr/bin/env python3
"""Install the hub's git hooks (tools/hooks/post-*) into this clone's .git/hooks.
post-commit (after git commit) and post-merge (after git pull): rebuild the full robot if a mechanism changed and
copy it into the LOCAL sim clone. Neither pushes to GitHub (push by hand: tools/sync_robot.py --push). Both run in the background
(tools/hooks/sync_bg.py -> tools/sync_robot.py) and call Git LFS's own hook first, so they replace the LFS stubs.
A hook you wrote yourself is never overwritten. Remove a hook = delete it from .git/hooks (then `git lfs install`
puts the LFS stub back)."""
import os
import shutil
import stat
import subprocess

hub = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
src = os.path.join(hub, "tools", "hooks")
dst = os.path.join(subprocess.check_output(["git", "rev-parse", "--git-path", "hooks"], text=True, cwd=hub).strip())
dst = dst if os.path.isabs(dst) else os.path.join(hub, dst)
os.makedirs(dst, exist_ok=True)


def replaceable(path, ours):
    """Missing, already ours (any version), or the plain Git LFS stub."""
    if not os.path.exists(path):
        return True
    old = open(path, encoding="utf-8", errors="ignore").read()
    if old == ours or "Installed by tools/install_hooks.py" in old:
        return True
    lines = [l.strip() for l in old.splitlines() if l.strip() and not l.startswith("#")]
    return all("git lfs" in l or "git-lfs" in l for l in lines)


for f in sorted(os.listdir(src)):
    if not f.startswith(("post-", "pre-")):
        continue                              # sync_bg.py etc. are run from tools/hooks, not installed
    ours = open(os.path.join(src, f), encoding="utf-8").read()
    t = os.path.join(dst, f)
    if not replaceable(t, ours):
        print("kept your own", t, "(not overwritten) - add a call to tools/hooks/" + f + " in it yourself")
        continue
    shutil.copy(os.path.join(src, f), t)
    os.chmod(t, os.stat(t).st_mode | stat.S_IEXEC)
    print("installed", t)
