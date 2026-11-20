# flipper_motion_check.py - motion collision check of the Flipper on base_330_js (Seif 2026-11-20, after the static check).
# Sweeps the whole cycle in small steps and, at every pose, computes REAL overlap volumes (Part common) between:
#   - the moving parts (carriage, arm, Grail) and the fixed ones (column, rack, saddle, top fixation and their screws,
#     base plate, Grail deck, the 350 limit sheet) + the base_330_js parts (wheel, drive motor, hinge, odometry, clapets A)
#   - the arm and the carriage (they move relative to each other during the flip)
#   - the Grail and every actuator part (it hangs on the magnet until it is let go)
# plus the closest approach (real distance) of every moving part to everything it comes within 5 mm of.
# The cycle (same kinematics as fc/flipper_fc.py, numbers read from its report):
#   lift 0 -> top every 4 mm (flip 0) / flip 0 -> 180 every 5 deg at the top / lower OVER (place) / magnet off, lower REL.
#   The way back (stowed -> pick, without the Grail) runs through the same arm + carriage poses.
#   Run (from mechanical/Grail_v2, after fc/flipper_fc.py): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_motion_check.py
#   -> CAD_FC/FLIPPER_motion_check.txt
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App

import common as C
from check_common import MIN_VOL, expected, load_base

NEAR = 5.0                      # mm: closest approaches under this are listed
LIFT_STEP, FLIP_STEP, LOW_STEP = 4.0, 5.0, 2.0
SEGMENT = os.environ.get("FLIPPER_MOTION", "all")   # "back": only the way back (drop + turn back)
RUNNING = (("V_WHEELS", "PROFILE_2020"), ("PINION_v2", "RACK_m1"))   # running contacts by design (rolling, meshing)
GROUPS_ARM = ("_3_ARM_pick_pose", "_8c_SCREWS_arm")
GROUPS_LIFT = ("_2_CARRIAGE_pick_pose", "_8b_SCREWS_carriage")
GROUPS_GRAIL = ("_4_GRAIL_pick",)
GROUPS_FIXED = ("_1_COLUMN_fixed", "_1b_FIXATION_saddle", "_8a_SCREWS_column", "_6_ROBOT_CONTEXT")


def running(a, b):
    return any((a.startswith(x) and b.startswith(y)) or (b.startswith(x) and a.startswith(y)) for x, y in RUNNING)


def kinematics():
    rep = open(os.path.join(C.CAD, "FLIPPER_B330_report.txt"), encoding="utf-8", errors="replace").read()
    m = re.search(r"Flip axis x ([\d.]+); LZ ([\d.]+); pivot z ([\d.]+) \(pick\) -> ([\d.]+) \(flip\) -> ([\d.]+) \(place\)"
                  r" -> ([\d.]+) \(stowed\)", rep)
    px, lz_, z_pick, z_flip, z_place, z_stow = (float(v) for v in m.groups())
    b = re.search(r"turn back at pivot z ([\d.]+)", rep)
    return px, z_pick, z_flip - z_pick, z_flip - z_place, z_place - z_stow, float(b.group(1)) - z_pick


def poses(px, z_pick, top, over, rel, back):
    P = (px, z_pick)
    out = []
    if SEGMENT == "back":                     # the way back only: the rest is the forward cycle, already checked
        lz0 = top - over - rel
        n = max(1, int(round((lz0 - back) / LOW_STEP)))
        for i in range(1, n + 1):
            out.append(("back: lower %.1f after the release" % ((lz0 - back) * i / n), lz0 - (lz0 - back) * i / n, 180.0, False))
        for a in range(180 - int(FLIP_STEP), -1, -int(FLIP_STEP)):
            out.append(("back: turn to %3d at pivot %.0f" % (a, z_pick + back), back, float(a), False))
    n = max(1, int(round(top / LIFT_STEP)))
    for i in range(n + 1 if SEGMENT != "back" else 0):
        out.append(("lift %5.1f, flip 0" % (top * i / n), top * i / n, 0.0, True))
    if SEGMENT != "back":
        for a in range(int(FLIP_STEP), 181, int(FLIP_STEP)):
            out.append(("flip %3d at the top" % a, top, float(a), True))
        n = max(1, int(round(over / LOW_STEP)))
        for i in range(1, n + 1):
            out.append(("lower %.1f to place" % (over * i / n), top - over * i / n, 180.0, True))
        n = max(1, int(round(rel / LOW_STEP)))
        for i in range(1, n + 1):
            out.append(("magnet off, lower %.1f" % (rel * i / n), top - over - rel * i / n, 180.0, False))
    res = []
    for label, lz, a, held in out:
        res.append(dict(label=label, arm=C.rot_pl(P, a, lz), lift=App.Placement(App.Vector(0, 0, lz), App.Rotation()),
                        grail=C.rot_pl(P, a, lz) if held else C.rot_pl(P, 180.0, top - over), held=held))
    return res


def main():
    t0 = time.time()
    doc = App.openDocument(os.path.join(C.CAD, "FLIPPER_B330.FCStd"))

    def group(names):
        d = {}
        for g in names:
            grp = doc.getObject(g)
            for o in (grp.Group if grp else []):
                if o.TypeId == "Part::Feature" and not o.Shape.isNull():
                    d[o.Name] = o.Shape
        return d

    arm, lift, grail, fixed = group(GROUPS_ARM), group(GROUPS_LIFT), group(GROUPS_GRAIL), group(GROUPS_FIXED)
    fixed.update(load_base(C))
    px, z_pick, top, over, rel, back = kinematics()
    P = poses(px, z_pick, top, over, rel, back)
    clashes, exp, near, contacts = {}, {}, {}, {}

    def test(na, a, nb, b, label, grail_pair=False, held=True):
        free = grail_pair and not held               # Grail let go: the magnet touching it is NOT expected any more
        exp_ = None if free else expected(na, nb)
        bba, bbb = a.BoundBox, b.BoundBox
        big = App.BoundBox(bba)
        big.enlarge(NEAR)
        if not big.intersect(bbb):
            return
        key = tuple(sorted((na, nb)))
        ov = 0.0
        if bba.intersect(bbb):
            try:
                ov = a.common(b).Volume
            except Exception:
                ov = 0.0
        if ov > MIN_VOL:
            why = exp_ or ("running contact by design" if running(na, nb) else None)
            if grail_pair and held and not why and "MAGNET_D30" in key:
                why = "the Grail hangs on the magnet"
            if why:
                exp.setdefault(key, [why, 0.0, label])
                if ov > exp[key][1]:
                    exp[key][1:] = [ov, label]
            else:
                clashes.setdefault(key, [0.0, label, 0])
                clashes[key][2] += 1
                if ov > clashes[key][0]:
                    clashes[key][:2] = [ov, label]
            return
        if exp_ or running(na, nb):
            return
        try:
            d = a.distToShape(b)[0]
        except Exception:
            return
        if d < 0.01:
            contacts.setdefault(key, label)          # touching, no overlap (or a false 0 on an imported STEP)
        elif d < NEAR and (key not in near or d < near[key][0]):
            near[key] = (d, label)

    for st in P:
        m_arm = {n: C.moved(s, st["arm"]) for n, s in arm.items()}
        m_lift = {n: C.moved(s, st["lift"]) for n, s in lift.items()}
        m_gr = {n: C.moved(s, st["grail"]) for n, s in grail.items()}
        moving = dict(m_arm)
        if SEGMENT != "back":                 # way back: the carriage heights vs the fixed parts are all in the lift
            moving.update(m_lift)
        for na, a in moving.items():
            for nb, b in fixed.items():
                if na.startswith("B330_") and nb.startswith("B330_"):
                    continue
                if nb == "CTX_LIMIT_350":
                    if a.BoundBox.ZMax > 350.0:
                        clashes.setdefault((na, nb), [a.BoundBox.ZMax - 350.0, st["label"], 0])[2] += 1
                    continue
                test(na, a, nb, b, st["label"])
        for na, a in (m_arm.items() if SEGMENT != "back" else ()):   # way back: same angles as the forward flip
            for nb, b in m_lift.items():
                test(na, a, nb, b, st["label"])
        for ng, g in m_gr.items():
            for nb, b in list(moving.items()) + list(fixed.items()):
                if nb == "CTX_LIMIT_350":
                    continue                          # the Grail may pass 350 [G E.2]
                if nb == "CTX_GRAIL_DECK" and not st["held"]:
                    continue                          # landed on it
                test(ng, g, nb, b, st["label"], grail_pair=True, held=st["held"])

    L = ["FLIPPER motion collision check - fc/flipper_motion_check.py (%.0f s)%s" % (
        time.time() - t0, ", WAY BACK ONLY (FLIPPER_MOTION=back): drop after the release, turn back 180 -> 0" if SEGMENT == "back" else ""),
         "cycle: %d poses: lift 0..%.0f every %.0f (flip 0), flip 0..180 every %.0f deg at the top, lower %.0f to place, "
         "magnet off + lower %.0f (pivot x %.1f, z %.1f at the pick). Way back: FLIPPER_MOTION=back."
         % (len(P), top, LIFT_STEP, FLIP_STEP, over, rel, px, z_pick),
         "pairs: moving (carriage + arm + their screws) vs fixed (column, rack, saddle, top fixation, base plate, Grail deck, "
         "350 limit, base_330_js parts); arm vs carriage; Grail vs everything. Overlaps > %.1f mm3 are clashes." % MIN_VOL, ""]
    L.append("CLASHES: %d" % len(clashes))
    for (na, nb), (v, lab, k) in sorted(clashes.items(), key=lambda kv: -kv[1][0]):
        unit = "mm over 350" if "CTX_LIMIT_350" in (na, nb) else "mm3"
        L.append("  %-26s x %-26s max %.1f %s at '%s' (%d poses)" % (na, nb, v, unit, lab, k))
    L.append("")
    L.append("closest approaches under %.0f mm (real distance, smallest over the cycle):" % NEAR)
    for (na, nb), (d, lab) in sorted(near.items(), key=lambda kv: kv[1][0]):
        L.append("  %5.2f mm  %-26s - %-26s at '%s'" % (d, na, nb, lab))
    L.append("")
    L.append("touching without overlap (distance 0, overlap < %.1f mm3; a few are false zeros on imported STEPs):" % MIN_VOL)
    for (na, nb), lab in sorted(contacts.items()):
        L.append("  %-26s - %-26s first at '%s'" % (na, nb, lab))
    L.append("")
    L.append("expected overlaps seen during the cycle (largest):")
    for (na, nb), (why, v, lab) in sorted(exp.items(), key=lambda kv: -kv[1][1]):
        L.append("  %8.1f mm3  %-26s x %-26s %s" % (v, na, nb, why))
    with open(os.path.join(C.CAD, "FLIPPER_motion_check%s.txt" % ("_back" if SEGMENT == "back" else "")), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


main()
