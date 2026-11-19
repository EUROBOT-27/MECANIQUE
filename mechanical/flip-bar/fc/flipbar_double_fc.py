# flipbar_double_fc.py - flip-bar doubled: one unit on the front face (+Y) and the same unit on the rear face (-Y),
# turned 180 deg about Z (Ayoub, 2026-11-19, proposal). Same parts for both units (nothing mirrored).
# Uses Maatoug's flipbar_fc.py unchanged (loaded as a library: its main() does not run, its files are not touched).
#   "D:/FreeCad/bin/freecadcmd.exe" flipbar_double_fc.py      (from mechanical/flip-bar/fc/)
# Writes ../CAD/flipbar_double.FCStd + .step (both units at home, stones on), ../double_report.txt:
#   - front unit x rear unit, over a grid of poses (each unit anywhere in its range, independently)
#   - rear unit x base plate + wheels over its whole range (base_330 is symmetric, so this should match the front)
#   - perimeter (convex hull of the vertical projection, stones out of count, FAQ Q1) at start, upright, and the
#     largest over the range with both units moving together (every mechanism open at once, FAQ Q10) [GR F.3]
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flipbar_params as P  # noqa: E402

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402

_spec = importlib.util.spec_from_file_location("flipbar_fc_lib", os.path.join(HERE, "flipbar_fc.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)          # module name != "flipbar_fc" -> its main() does not run

V = App.Vector
ROOT = os.path.normpath(os.path.join(HERE, ".."))
BASE = ("base_330", "wheels", "table")
TURN = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), 180))
N_GRID = 12                          # poses per unit for front x rear (12 x 12)
N_SWEEP = 84                         # poses for the rear x base sweep and the perimeter (as flipbar_fc.py)


def build_double(doc):
    """front unit = flipbar_fc.build(); rear unit = copy of every non-base object, kind prefixed 'R'"""
    objs = F.build(doc)
    rear = {}
    for n, (o, k) in list(objs.items()):
        if n in BASE:
            continue
        r = doc.addObject("Part::Feature", "R_" + n)
        r.Shape = o.Shape.copy()
        if k == "fixed":
            r.Placement = TURN.multiply(o.Placement)
        rear["R_" + n] = (r, "R" + k)
    objs.update(rear)
    return objs


def pose_double(objs, front, rear):
    if front is not None:
        pl = F.placements(front)
        for n, (o, k) in objs.items():
            if k in pl:
                o.Placement = pl[k]
    if rear is not None:
        pl = F.placements(rear)
        for n, (o, k) in objs.items():
            if k.startswith("R") and k[1:] in pl:
                o.Placement = TURN.multiply(pl[k[1:]])


def vol(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


def side(n, k):
    if n in BASE:
        return "base"
    return "rear" if k.startswith("R") else "front"


def front_x_rear(objs):
    """every front part x every rear part (stones included), worst volume per pair"""
    fr = [(n, o) for n, (o, k) in objs.items() if side(n, k) == "front"]
    rr = [(n, o) for n, (o, k) in objs.items() if side(n, k) == "rear"]
    hits, min_gap = {}, 1e9
    for nf, of in fr:
        for nr, orr in rr:
            v = vol(of.Shape, orr.Shape)
            if v > 1.0:
                hits[(nf, nr)] = max(hits.get((nf, nr), 0.0), v)
    # closest approach along Y between the two units (both bound boxes)
    yf = min(o.Shape.BoundBox.YMin for _, o in fr)
    yr = max(o.Shape.BoundBox.YMax for _, o in rr)
    return hits, yf - yr


def rear_x_base(objs):
    hits = []
    base = [(n, o) for n, (o, k) in objs.items() if n in ("base_330", "wheels")]
    for n, (o, k) in objs.items():
        if not k.startswith("R") or k == "Rfixed":
            continue
        for nb, ob in base:
            v = vol(o.Shape, ob.Shape)
            if v > 1.0:
                hits.append((n, nb, v))
    return hits


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and ((h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0])) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, hi = half(pts), half(pts[::-1])
    return lo[:-1] + hi[:-1]


def perimeter(objs, which=("front", "rear", "base")):
    pts = []
    for n, (o, k) in objs.items():
        if n == "table" or "Stone" in n or side(n, k) not in which:
            continue
        sh = o.Shape
        try:
            vs = sh.tessellate(1.0)[0]
        except Exception:
            vs = [v.Point for v in sh.Vertexes]
        pts += [(round(v.x, 2), round(v.y, 2)) for v in vs]
        pts += [(round(v.Point.x, 2), round(v.Point.y, 2)) for v in sh.Vertexes]
    h = hull(pts)
    per = sum(math.dist(h[i], h[(i + 1) % len(h)]) for i in range(len(h)))
    xs, ys = [p[0] for p in h], [p[1] for p in h]
    return per, (min(xs), max(xs), min(ys), max(ys))


def main():
    doc = App.newDocument("flipbar_double")
    objs = build_double(doc)
    stop = P.STOP_PAST_DEG / math.degrees(abs(P.SWEEP))
    sweep = [it for it in P.sweep_path(-stop, 1 + stop, N_SWEEP) if it[1] is not None]
    grid = [sweep[round(i * (len(sweep) - 1) / (N_GRID - 1))] for i in range(N_GRID)]
    home = min(sweep, key=lambda it: abs(it[0]))
    up = min(sweep, key=lambda it: abs(it[0] - 1))
    L = []

    # 1. front x rear, each unit anywhere in its range
    fr_hits, gap_min = {}, 1e9
    for a in grid:
        for b in grid:
            pose_double(objs, a, b)
            h, gap = front_x_rear(objs)
            gap_min = min(gap_min, gap)
            for k, v in h.items():
                fr_hits[k] = max(fr_hits.get(k, 0.0), v)

    # 2. rear unit x base + wheels over its whole range (front at home)
    rb = {}
    for it in sweep:
        pose_double(objs, home, it)
        for n, nb, v in rear_x_base(objs):
            rb[(n, nb)] = max(rb.get((n, nb), 0.0), v)

    # 3. perimeter (stones out of count, FAQ Q1)
    pose_double(objs, home, home)
    p_start, bb_start = perimeter(objs)
    p_single, bb_single = perimeter(objs, ("front", "base"))
    pose_double(objs, up, up)
    p_up, bb_up = perimeter(objs)
    p_max, s_max = 0.0, 0.0
    for it in sweep[::3] + [sweep[-1]]:
        pose_double(objs, it, it)
        p, _ = perimeter(objs)
        if p > p_max:
            p_max, s_max = p, it[0]

    L.append("flip-bar doubled (front + rear, rear = front turned 180 deg about Z) - flipbar_double_fc.py, Ayoub 2026-11-19, proposal")
    L.append("Base base_330 (330 x 280, symmetric). Each unit = Maatoug's flip-bar unchanged (flipbar_fc.py).")
    L.append("")
    L.append("front unit x rear unit, %d x %d poses (each unit anywhere from its home stop to its upright stop): %d overlap(s)%s"
             % (N_GRID, N_GRID, len(fr_hits), "".join("\n   %s x %s %.0f mm3" % (a, b, v) for (a, b), v in fr_hits.items())))
    L.append("   closest approach along Y between the two units (bound boxes): %.1f mm" % gap_min)
    L.append("rear unit (moving parts) x base_330 + wheels, %d poses: %d overlap(s)%s"
             % (len(sweep), len(rb), "".join("\n   %s x %s %.0f mm3" % (a, b, v) for (a, b), v in rb.items())))
    L.append("height: same as one unit (the turn is about Z): actuators 339.0 mm, see collision_report.txt")
    L.append("")
    L.append("perimeter, convex hull of the vertical projection, stones out of count (FAQ Q1) [GR F.3]:")
    L.append("   one unit (front only), home : %6.0f mm  (x %.0f..%.0f, y %.0f..%.0f)" % ((p_single,) + bb_single))
    L.append("   doubled, both at home (start): %6.0f mm  (x %.0f..%.0f, y %.0f..%.0f)  limit 1200 -> %s"
             % ((p_start,) + bb_start + ("OK" if p_start <= 1200 else "OVER by %.0f" % (p_start - 1200),)))
    L.append("   doubled, both upright        : %6.0f mm  (x %.0f..%.0f, y %.0f..%.0f)" % ((p_up,) + bb_up))
    L.append("   doubled, largest over the range, both moving (FAQ Q10): %.0f mm at s %.3f, limit 1400 -> %s"
             % (p_max, s_max, "OK" if p_max <= 1400 else "OVER by %.0f" % (p_max - 1400)))
    L.append("")
    L.append("Not modelled (as in flipbar_fc.py): base_330 casters (front + back on the Y axis) and odometry units, battery,")
    L.append("electronics, beacon support, Grail lift, launcher.")
    txt = "\n".join(L)
    print(txt)
    open(os.path.join(ROOT, "double_report.txt"), "w", encoding="utf-8").write(txt + "\n")

    # save at home, stones on
    pose_double(objs, home, home)
    doc.removeObject("table")
    keep = {n: (o, k) for n, (o, k) in objs.items() if n != "table"}
    for n, (o, k) in keep.items():
        base_n = n[2:] if n.startswith("R_") else n
        lab = F.LABELS.get(base_n, base_n)
        o.Label = lab if n in BASE else ("Rear_" if n.startswith("R_") else "Front_") + lab
    for unit, pre in (("Front", ""), ("Rear", "R_")):
        top = doc.addObject("App::DocumentObjectGroup", unit + "_unit")
        for gname, members in F.GROUPS:
            if gname == "Robot_base":
                continue
            g = doc.addObject("App::DocumentObjectGroup", unit + "_" + gname)
            top.addObject(g)
            for n, (o, k) in keep.items():
                if (pre and not n.startswith(pre)) or (not pre and n.startswith("R_")) or n in BASE:
                    continue
                bn = n[len(pre):]
                if any(bn == m or (m.endswith("_") and bn.startswith(m)) for m in members):
                    g.addObject(o)
    gb = doc.addObject("App::DocumentObjectGroup", "Robot_base")
    for n in ("base_330", "wheels"):
        gb.addObject(keep[n][0])
    doc.recompute()
    out = os.path.join(ROOT, "CAD")
    Part.makeCompound([o.Shape.copy() for o, k in keep.values()]).exportStep(os.path.join(out, "flipbar_double.step"))
    doc.saveAs(os.path.join(out, "flipbar_double.FCStd"))
    print("->", os.path.join(out, "flipbar_double.FCStd"))


main()
