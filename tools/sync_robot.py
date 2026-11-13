#!/usr/bin/env python3
"""sync_robot.py - keep the full robot model (mechanical/robot) and its Gazebo export up to date.

    python tools/sync_robot.py            rebuild if a source changed, then copy the Gazebo model into the LOCAL sim clone
    python tools/sync_robot.py --push     same, then commit + push the model to Simulation-Euro27 on GitHub (push()).
                                          BY HAND ONLY: no hook ever passes --push (2026-11-13).
    python tools/sync_robot.py --check    only say if the robot is stale (exit code 1 = stale)
    python tools/sync_robot.py --force    rebuild even if nothing changed
    options: --no-copy, --quiet, --sim <path to Simulation-Euro27>, --freecad <path to freecadcmd>

Sources = mechanical/robot/fc/{layout.py, build_robot.py, robot.urdf.xacro} + the mechanism models the layout names
(clapets FCStd, Grail-lift FCStd + joints json). A mechanism generator writes its FCStd -> this sees the change.
Which VERSION of a mechanism the robot uses is set in layout.py (e.g. L.CLAPETS = "clapets-v8"), never guessed.
Triggered automatically (tools/hooks/sync_bg.py) WITHOUT --push: at the end of each Claude turn (.claude/settings.json
Stop hook), after git commit (post-commit) and after git pull (post-merge): rebuild + copy into the local sim clone.
One run at a time (lock file); a mechanism changed during a build -> rebuilt again. A failed build (or no FreeCAD) is
remembered (.sync.failed) and not retried until a source changes.
Plain Python 3, no FreeCAD needed to check; the rebuild calls FreeCAD's freecadcmd.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HUB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MECH = os.path.join(HUB, "mechanical")
RFC = os.path.join(MECH, "robot", "fc")
CAD = os.path.join(MECH, "robot", "CAD_FC")
NAME = "excalibot_fc"
EXPORT = os.path.join(MECH, "robot", "sim", NAME)
SIM_REL = "src/eb27_description/robots/" + NAME          # where the model lives in Simulation-Euro27
DEFAULT_SIM = os.path.join(HUB, "eurobot2027", "Simulation-Euro27")
LOCK = os.path.join(CAD, ".sync.lock")                    # a sync is running (not committed)
FAILED = os.path.join(CAD, ".sync.failed")                # signature of the sources whose build failed (not committed)
NOTIFIED = os.path.join(CAD, ".sync.notified")            # failed signature already reported in the Claude UI (not committed)
LOG = os.path.join(CAD, "sync.log")                       # background runs write here (*.log: not committed)
LOCK_MAX_AGE = 1800                                       # s; an older lock = a crashed run
FREECAD_CANDIDATES = [os.environ.get("FREECADCMD", ""), r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe",
                      r"C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe", "/usr/bin/freecadcmd", "/usr/bin/FreeCADCmd",
                      "freecadcmd", "FreeCADCmd"]


def layout():
    sys.path.insert(0, RFC)
    import layout as lay                      # plain python, no FreeCAD
    return lay.L


def sources():
    L = layout()
    out = [os.path.join(RFC, f) for f in ("layout.py", "build_robot.py", "robot.urdf.xacro")]
    out.append(os.path.join(MECH, "clapets", L.CLAPETS, "CAD_FC", "MODULE_%s.FCStd" % L.CLAPETS.upper().replace("-", "_")))
    g = os.path.join(MECH, "grail-lift", "CAD_FC")
    out.append(os.path.join(g, "GRAIL_LIFT_%s.FCStd" % L.GRAIL_LIFT.upper()))
    out.append(os.path.join(g, "joints_%s.json" % L.GRAIL_LIFT))
    return out


def file_hash(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:12]


def signature():
    """One string for the current state of every source (to remember which state failed to build)."""
    return ";".join("%s=%s" % (os.path.basename(p), file_hash(p) if os.path.isfile(p) else "-") for p in sources())


def stale():
    man_p = os.path.join(EXPORT, "manifest.json")
    if not os.path.isfile(man_p):
        return ["no export yet"]
    man = json.load(open(man_p, encoding="utf-8"))["built_from"]
    why = []
    for p in sources():
        key = os.path.relpath(p, MECH).replace("\\", "/")
        if not os.path.isfile(p):
            why.append("missing source " + key)
        elif man.get(key) != file_hash(p):
            why.append("changed: " + key)
    return why


def last_failed():
    """True if the last build failed and the sources have not changed since (no point retrying)."""
    try:
        return open(FAILED, encoding="utf-8").read().strip() == signature()
    except OSError:
        return False


def locked():
    try:
        return time.time() - os.path.getmtime(LOCK) < LOCK_MAX_AGE
    except OSError:
        return False


def acquire_lock(wait):
    """Take the lock. wait=True: wait for a running sync to finish (up to LOCK_MAX_AGE)."""
    os.makedirs(CAD, exist_ok=True)
    t0 = time.time()
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            if not locked():                  # crashed run left it behind
                try:
                    os.remove(LOCK)
                except OSError:
                    pass
                continue
            if not wait or time.time() - t0 > LOCK_MAX_AGE:
                return False
            time.sleep(5)


def release_lock():
    try:
        os.remove(LOCK)
    except OSError:
        pass


def freecad(cli):
    for c in [cli] + FREECAD_CANDIDATES:
        if c and (os.path.isfile(c) or shutil.which(c)):
            return c
    return None


def git(repo, *args, **kw):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")   # background run: never wait for a password prompt
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, env=env, timeout=180, **kw)


def copy_export(sim):
    dst = os.path.join(sim, *SIM_REL.split("/"))
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(EXPORT, dst)
    return dst


def push(sim, why):
    """Copy the model into the sim clone, commit it there and push it to GitHub.
    SIM_REL is 100 % generated, so the clone's copy is thrown away, the clone is pulled, and the export is copied
    again on top: no merge conflicts on the binary meshes when both hub clones push. Only SIM_REL is committed,
    never other changes in the sim clone. Refuses if the sim clone is not on main or holds unpushed commits of its own
    (those are yours). If the hub has uncommitted robot sources, the commit message says so."""
    branch = git(sim, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != "main":
        print("NOT pushed: the sim clone is on branch '%s', not main" % branch)
        return False
    rel_sources = [os.path.relpath(p, HUB).replace("\\", "/") for p in sources()]
    dirty = [l[3:] for l in git(HUB, "status", "--porcelain", "--", *rel_sources).stdout.splitlines() if l.strip()]
    hub_sha = git(HUB, "rev-parse", "--short", "HEAD").stdout.strip()
    for attempt in range(2):
        r = git(sim, "fetch", "--quiet")
        if r.returncode != 0:
            print("NOT pushed: git fetch failed (offline?):\n" + r.stderr)
            return False
        mine = git(sim, "log", "@{u}..HEAD", "--format=", "--name-only").stdout.split()
        if any(not f.startswith(SIM_REL + "/") for f in mine):
            print("NOT pushed: the sim clone has unpushed commits of its own (push or drop them first)")
            return False
        if mine:                              # our own earlier robot commits that never got out: superseded below
            git(sim, "reset", "--mixed", "--quiet", "@{u}")
        git(sim, "checkout", "--", SIM_REL)
        git(sim, "clean", "-fdq", "--", SIM_REL)
        r = git(sim, "pull", "--rebase", "--autostash", "--quiet")
        if r.returncode != 0:
            git(sim, "rebase", "--abort")
            print("NOT pushed: git pull failed in the sim clone:\n" + r.stdout + r.stderr)
            return False
        copy_export(sim)
        if not git(sim, "status", "--porcelain", "--", SIM_REL).stdout.strip():
            print("sim repo already has this robot")
            return True
        git(sim, "add", "-A", "--", SIM_REL)
        msg = "%s: rebuilt from MECANIQUE %s%s\n\n%s\n%s\nGenerated by tools/sync_robot.py in the MECANIQUE hub, do not edit by hand." % (
            NAME, hub_sha, " + local changes" if dirty else "", "\n".join(why) or "export refresh",
            ("Uncommitted in the hub at build time: " + ", ".join(dirty) + "\n") if dirty else "")
        r = git(sim, "commit", "--quiet", "-m", msg, "--", SIM_REL)
        if r.returncode != 0:
            print("NOT pushed: commit failed in the sim clone:\n" + r.stdout + r.stderr)
            return False
        r = git(sim, "push", "--quiet")
        if r.returncode == 0:
            print("pushed %s to Simulation-Euro27 (%s)" % (NAME, git(sim, "rev-parse", "--short", "HEAD").stdout.strip()))
            return True
        print("push rejected (attempt %d):\n%s" % (attempt + 1, r.stderr))
    print("NOT pushed after 2 attempts (commit kept locally, retried at the next sync)")
    return False


def build(cli, quiet, force):
    """Rebuild until the export matches the sources (a mechanism may change during a build). Returns the reasons."""
    done = []
    for i in range(3):
        why = stale()
        if not why and not (force and i == 0):
            return done
        print("rebuilding the robot (%s) ..." % ("; ".join(why) or "forced"), flush=True)
        sig = signature()
        fc = freecad(cli)
        if not fc:                            # remembered like a failed build: the hooks don't retry every turn
            open(FAILED, "w", encoding="utf-8").write(sig)
            sys.exit("freecadcmd not found: install FreeCAD 1.1, or pass --freecad / set FREECADCMD")
        r = subprocess.run([fc, os.path.join(RFC, "build_robot.py")], cwd=os.path.join(MECH, "robot"),
                           capture_output=quiet)
        if r.returncode != 0 or (stale() and signature() == sig):
            open(FAILED, "w", encoding="utf-8").write(sig)
            sys.exit("robot build FAILED (see mechanical/robot/CAD_FC/robot_report.txt / the FreeCAD output)")
        done += [w for w in (why or ["forced rebuild"]) if w not in done]
    if stale():
        sys.exit("robot still stale after 3 builds (sources keep changing?) - run tools/sync_robot.py again")
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-copy", action="store_true")
    ap.add_argument("--push", action="store_true", help="commit + push the model in Simulation-Euro27")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--sim", default=DEFAULT_SIM)
    ap.add_argument("--freecad", default="")
    a = ap.parse_args()
    if a.check:
        why = stale()
        print("robot is %s" % ("STALE: " + "; ".join(why) if why else "up to date"))
        sys.exit(1 if why else 0)
    print("[%s] sync_robot %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), " ".join(sys.argv[1:])), flush=True)
    if not acquire_lock(wait=True):
        sys.exit("another sync has been running for too long; delete %s if it crashed" % LOCK)
    try:
        why = build(a.freecad, a.quiet, a.force)
        for p in (FAILED, NOTIFIED):
            try:
                os.remove(p)
            except OSError:
                pass
        if not why:
            print("robot up to date")
        if a.no_copy:
            return
        if not os.path.isdir(os.path.join(a.sim, "src", "eb27_description")):
            print("sim clone not found at %s (pass --sim); export is in %s" % (a.sim, EXPORT))
            return
        if a.push:
            if not push(a.sim, why):
                sys.exit("NOT pushed (see the reason above); the local hub export is up to date")
        else:
            print("copied to", copy_export(a.sim))
        print("-> in the sim: ./sim build, robot model", NAME)
    finally:
        release_lock()


if __name__ == "__main__":
    main()
