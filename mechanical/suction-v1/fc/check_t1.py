# check_t1.py - motion + collision + height + footprint check of T1 through its whole cycle (headless):
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/check_t1.py        (from suction-v1/, ~5-10 min)
#   -> CAD_FC/turn/check_report.txt
# Reads the T1 builds (CAD_FC/turn/T1_S3, T1_S1: grab pose) and clapets v7 (module A, its doors and their kinematics).
# Two mountings: A+B (front, with module A's door units) and B alone (back: module A's lift without door units).
# Cycle (A+B): doors folded -> doors open -> grab -> doors clamp -> carry (lift 15) -> lower -> doors open (cups hold)
#   -> lift-turn 0..90 deg (5 deg steps) -> release -> plate back to 0 -> doors fold.  B alone: same without doors.
import math
import os
import sys

import FreeCAD as App
from FreeCAD import Vector as V

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P
import turn_t1 as T

CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
V7 = os.path.normpath(os.path.join(HERE, "..", "..", "clapets", "clapets-v7", "CAD_FC", "MODULE_CLAPETS_V7.FCStd"))
OUT = os.path.join(CAD, "turn", "check_report.txt")

# clapets v7 door kinematics (motion_v7.py)
A_PX, A_PY, A_SVY, DOOR_RATIO = 131.0, 82.0, 52.0, 28 / 20
A_FOLD, A_APPROACH, A_CLAMP, A_OPEN = 90.0, -30.0, 3.0, -38.0
NOT_ALONE = ("AILE", "CAPOT", "MG996R", "FIL_", "BRAS", "TOLE", "MOUSSE", "PORTE")   # door-unit parts (B alone: none)
B_FIXED = ("T1_BRACKET", "REF_MG996R", "REF_6002", "REF_TUBE_TOP_TO", "REF_TUBE_MID_TO", "REF_TUBE_BOT_TO",
           "FIX_M5", "FIX_NYLOC", "FIX_M3x8_SERVO", "REF_BUTTERFLY_PLATE")
# contacts that are meant to be there
EXPECTED = [("FIX_M5", "REF_ROUES_V"), ("FIX_M5", "REF_ENTRETOISES"), ("FIX_M5", "FIX_VIS_ROUES"), ("FIX_M5", "FIX_ECROU_ROUES"),
            ("FIX_NYLOC", "FIX_VIS_ROUES"), ("FIX_NYLOC", "FIX_ECROU_ROUES"), ("T1_PINION", "REF_MG996R"),
            ("FIX_M5", "REF_RONDELLES"), ("FIX_M5", "REF_PLAQUE_PAPILLON"),
            ("REF_STONE", "REF_MOUSSE_PORTE")]                                    # door foam squeezed on the stack (clamp)
TABLE = P.MODULE_Z                  # table z = module z + 26 (layout-v1: socle on the robot floor)


def cycle(with_doors):
    """[(label, lift, door angle, plate angle, stack: None / (lift, angle))]"""
    s = []
    lt = T.lift_at
    if with_doors:
        s += [("start: doors folded", 0, A_FOLD, 0, None)]
        s += [("doors open %d" % a, 0, a, 0, None) for a in range(80, -31, -10)]
    s += [("grab (cups on the stack)", 0, A_APPROACH if with_doors else None, 0, (0, 0))]
    if with_doors:
        s += [("doors clamp", 0, A_CLAMP, 0, (0, 0))]
    s += [("carry: lift 15", 15, A_CLAMP if with_doors else None, 0, (15, 0)), ("lower in the castle", 0, A_CLAMP if with_doors else None, 0, (0, 0))]
    if with_doors:
        s += [("doors open (cups hold) %d" % a, 0, a, 0, (0, 0)) for a in (-10, -20, -30, A_OPEN)]
    door = A_OPEN if with_doors else None
    s += [("lift-turn %d deg" % t, lt(t), door, t, (lt(t), t)) for t in range(0, 91, 5)]
    s += [("release, robot backs away", lt(90), door, 90, None)]
    s += [("plate back %d deg" % t, 0, door, t, None) for t in range(90, -1, -15)]
    if with_doors:
        s += [("doors fold %d" % a, 0, a, 0, None) for a in range(-30, 91, 10)]
    return s


def rot(axis, ang, c):
    return App.Placement(V(), App.Rotation(axis, ang), c)


def lift(h):
    return App.Placement(V(0, 0, h), App.Rotation())


def b_group(label):
    if label.startswith("REF_STONE"):
        return "stack"
    if label.startswith("T1_PINION"):
        return "b_pinion"
    if label.startswith(B_FIXED):
        return "b_fixed"
    return "b_turn"


def place(grp, h, a, t, stack):
    Y, Z = V(0, 1, 0), V(0, 0, 1)
    if grp == "b_fixed" or grp == "carriage":
        return lift(h)
    if grp == "b_turn":
        return lift(h).multiply(rot(Y, -t, V(0, 0, T.HZ)))
    if grp == "b_pinion":
        return lift(h).multiply(rot(Y, t * T.ZG / T.ZP, V(T.PX, 0, T.PZ)))
    if grp == "stack":
        hs, ts = stack
        return lift(hs).multiply(rot(Y, -ts, V(0, 0, T.HZ)))
    if grp == "fixed":
        return App.Placement()
    s = 1 if grp.endswith("D") else -1
    if grp.startswith("door_"):
        return lift(h).multiply(rot(Z, s * a, V(s * A_PX, A_PY, 0)))
    if grp.startswith("pinion_"):
        return lift(h).multiply(rot(Z, -s * DOOR_RATIO * a, V(s * A_PX, A_SVY, 0)))
    raise ValueError(grp)


def hull_perimeter(pts):
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))
    if len(pts) < 3:
        return 0.0
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(pts[::-1])
    poly = lo[:-1] + up[:-1]
    return sum(math.dist(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def expected(a, b):
    return any((a.startswith(x) and b.startswith(y)) or (b.startswith(x) and a.startswith(y)) for x, y in EXPECTED)


def run(station, with_doors, rep):
    bdoc = App.openDocument(os.path.join(CAD, "turn", "T1_%s" % station, "T1_%s.FCStd" % station))
    objs = []                                                         # (label, group, module, shape)
    for o in bdoc.Objects:
        if o.TypeId == "Part::Feature" and o.Shape.Solids:
            if o.Label == "REF_BUTTERFLY_PLATE":
                continue                                              # module A brings the real one
            objs.append((o.Label, b_group(o.Label), "B" if not o.Label.startswith("REF_STONE") else "S", o.Shape.copy()))
    App.closeDocument(bdoc.Name)
    adoc = App.openDocument(V7)
    for o in adoc.Objects:
        if o.TypeId != "Part::Feature" or getattr(o, "Module", "-") != "A":
            continue
        g = o.MotionGroup
        if not with_doors and (g.startswith(("door_", "pinion_")) or any(k in o.Label for k in NOT_ALONE)):
            continue
        sh = o.Shape.copy()                                           # keeps its placement (= CAD pose, the base)
        objs.append((o.Label, g, "A", sh))
    App.closeDocument(adoc.Name)
    pts = {i: [V(p) for p in (sh.tessellate(2.0)[0] if sh.Faces else [v.Point for v in sh.Vertexes])] for i, (_, _, _, sh) in enumerate(objs)}

    hits, worst_h, worst_stack, foot = {}, (0, ""), (0, ""), []
    steps = cycle(with_doors)
    for label, h, a, t, stack in steps:
        cur = []
        for i, (nm, g, m, sh) in enumerate(objs):
            if g == "stack" and stack is None:
                continue
            pl = place(g, h, a if a is not None else 0, t, stack if stack else (0, 0))
            s = sh.copy(); s.Placement = pl.multiply(sh.Placement)
            cur.append((i, nm, g, m, s, pl))
        # heights + footprint
        zb = max(max(pl.multVec(p).z for p in pts[i]) for i, nm, g, m, s, pl in cur if m == "B") + TABLE
        if zb > worst_h[0]:
            worst_h = (zb, label)
        if stack:
            zs = max(max(pl.multVec(p).z for p in pts[i]) for i, nm, g, m, s, pl in cur if m == "S") + TABLE
            if zs > worst_stack[0]:
                worst_stack = (zs, label)
        xy_a = [(q.x, q.y) for i, nm, g, m, s, pl in cur if m == "A" for q in (pl.multVec(p) for p in pts[i])]
        xy_b = [(q.x, q.y) for i, nm, g, m, s, pl in cur if m == "B" for q in (pl.multVec(p) for p in pts[i])]
        foot.append((label, hull_perimeter(xy_a) if xy_a else 0.0, hull_perimeter(xy_a + xy_b), max(abs(x) for x, y in xy_b), max(y for x, y in xy_b)))
        # collisions between parts that move relative to each other (module A against itself: v7's own check)
        for j in range(len(cur)):
            for k in range(j + 1, len(cur)):
                _, n1, g1, m1, s1, _ = cur[j]
                _, n2, g2, m2, s2, _ = cur[k]
                if g1 == g2 or (m1 == "A" and m2 == "A") or {g1, g2} == {"stack", "b_turn"}:
                    continue
                if not s1.BoundBox.intersect(s2.BoundBox):
                    continue
                vol = s1.common(s2).Volume
                if vol < 0.5:
                    continue
                key = (n1, n2)
                if key not in hits or vol > hits[key][0]:
                    hits[key] = (vol, label, expected(n1, n2))
    mode = "A+B (front, with module A's doors)" if with_doors else "B alone (back, module A's lift without door units)"
    rep.append("=" * 100)
    rep.append("T1 with %s  -  %s  -  %d poses" % (station, mode, len(steps)))
    rep.append("-" * 100)
    rep.append("Highest module B point: %.1f above the table (%s)   limit 350" % worst_h)
    if worst_stack[0]:
        rep.append("Highest stone point:    %.1f (%s)   held stones may pass 350 in the castle only (Q9)" % worst_stack)
    fmax = max(foot, key=lambda f: f[2] - f[1])
    if with_doors:
        rep.append("Footprint: module B adds at most %.1f mm to module A's hull perimeter (%s); B reaches |x| %.1f, y %.1f"
                   % (fmax[2] - fmax[1], fmax[0], max(f[3] for f in foot), max(f[4] for f in foot)))
    else:
        rep.append("Footprint: module B reaches |x| %.1f, y %.1f (layout-v1 body face y %.0f)" % (max(f[3] for f in foot), max(f[4] for f in foot), P.STACK_FACE_Y))
    real = sorted((v for v in hits.items() if not v[1][2]), key=lambda kv: -kv[1][0])
    exp = [v for v in hits.items() if v[1][2]]
    rep.append("Collisions: %d (+ %d expected contacts: bolts through the wheels, pinion on the horn)" % (len(real), len(exp)))
    for (n1, n2), (vol, lab, _) in real:
        rep.append("   %-28s x %-28s %9.1f mm3   worst at: %s" % (n1, n2, vol, lab))
    if with_doors:
        fold_limit(objs, rep)
    rep.append("")


def fold_limit(objs, rep):
    """Largest fold angle each door reaches (opening path from -30 up) before it touches module B (plate at 0, lift 0),
    and what the start perimeter (module A + B hull) becomes at that angle compared with doors fully folded (90)."""
    b = [(nm, g, sh) for nm, g, m, sh in objs if m == "B"]
    for side in ("D", "G"):
        door = [(nm, g, sh) for nm, g, m, sh in objs if m == "A" and g in ("door_" + side, "pinion_" + side)]
        last = None
        for a in range(-30, 91, 2):
            hit = False
            for nm, g, sh in door:
                s1 = sh.copy(); s1.Placement = place(g, 0, a, 0, (0, 0)).multiply(sh.Placement)
                for nb, gb, shb in b:
                    s2 = shb.copy(); s2.Placement = place(gb, 0, 0, 0, (0, 0)).multiply(shb.Placement)
                    if s1.BoundBox.intersect(s2.BoundBox) and s1.common(s2).Volume > 0.5:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                break
            last = a
        rep.append("Door %s (%s side): folds freely up to %s deg (fully folded = 90)" % (side, "+x" if side == "D" else "-x", last))
    def per(a_d, a_g):
        pts = []
        for nm, g, m, sh in objs:
            if m == "S":
                continue
            a = a_d if g.endswith("_D") else a_g
            pl = place(g, 0, a, 0, (0, 0)).multiply(sh.Placement)
            sh2 = sh.copy(); sh2.Placement = pl
            pts += [(v.Point.x, v.Point.y) for v in sh2.Vertexes]
        return hull_perimeter(pts)
    rep.append("Hull perimeter of module A + B: doors folded 90 = %.0f; doors at 60 = %.0f; at 40 = %.0f (layout-v1 start A+B: 1114, limit 1200)"
               % (per(90, 90), per(60, 60), per(40, 40)))


def main():
    rep = ["T1 check (check_t1.py)", "Heights are above the table (module z + %.0f). Poses: see the cycle at the top of the script." % TABLE, ""]
    for st in ("S3", "S1"):
        for doors in (True, False):
            run(st, doors, rep)
            with open(OUT, "w") as f:
                f.write("\n".join(rep) + "\n")
    print("\n".join(rep))


main()
