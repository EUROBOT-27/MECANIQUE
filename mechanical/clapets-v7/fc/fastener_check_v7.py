# fastener_check_v7.py - check every screw, nut and insert of clapets v7 (numbers + a cut view through each screw).
# Run after v7_fc.py and render_v7.py (needs the GUI for the pictures):
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/fastener_check_v7.py
# Output: ../CAD_FC/fastener_check/  report.txt, s_NN_<screw>.png (cut through the screw axis), g_<group>.png (where it is)
# Read-only on the model: the .FCStd is opened, never saved.
import math
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
OUT = os.path.join(CAD, "fastener_check")
os.makedirs(OUT, exist_ok=True)
SHOTS = os.environ.get("FC_SHOTS", "1") == "1"
import time
T0 = time.time()


def log(msg):
    with open(os.path.join(OUT, "progress.log"), "a") as f:
        f.write("%6.0fs  %s\n" % (time.time() - T0, msg))

ENGAGE = ("nut", "insert", "tnut")
TOOL_R = {2: 1.5, 3: 2.0, 4: 2.5, 5: 3.0}      # radius of the key / driver shaft that has to reach the head
INS3_OD = 6.0   # 2026-11-09: real M3 insert outer Ø (5.6..6.0); the CAD models inserts at the hole size (Ø5.4 since 2026-11-12)


def kind(label):
    if label.startswith("FIX_VIS"):
        return "screw"
    if label.startswith("FIX_ECROU"):
        return "nut"
    if label.startswith("FIX_INSERT"):
        return "insert"
    if label.startswith("FIX_TNUT"):
        return "tnut"
    if label.startswith(("RES_", "REF_PILE")):
        return None
    if label.startswith(("A_TOLE", "B_PLATEAU")):
        return "mdf"
    if label.startswith(("A_", "B_")):
        return "print"
    if label.startswith("REF_"):
        return "ref"
    return None


def frame(d):
    a = Vector(1, 0, 0) if abs(d.x) < 0.9 else Vector(0, 1, 0)
    u = d.cross(a)
    u.normalize()
    w = d.cross(u)
    w.normalize()
    return u, w


def ring(c, d, r, n=8):
    u, w = frame(d)
    return [c + u * (r * math.cos(2 * math.pi * k / n)) + w * (r * math.sin(2 * math.pi * k / n)) for k in range(n)]


class Ent:
    def __init__(self, label, k, shape, obj):
        self.label, self.kind, self.shape, self.obj = label, k, shape, obj
        self.solids = shape.Solids
        self.bb = shape.BoundBox

    def inside(self, p):
        if not self.bb.isInside(p):
            return False
        for s in self.solids:
            if s.BoundBox.isInside(p) and s.isInside(p, 1e-4, True):
                return True
        return False


def entities(doc):
    ents = []
    for o in doc.Objects:
        if not hasattr(o, "Shape") or o.TypeId != "Part::Feature":
            continue
        k = kind(o.Label)
        if k is None:
            continue
        if k == "screw":
            for i, ch in enumerate(o.Shape.childShapes()):
                ents.append(Ent("%s#%d" % (o.Label, i + 1), k, ch, o))
        elif k in ENGAGE:
            for i, s in enumerate(o.Shape.Solids):
                ents.append(Ent("%s#%d" % (o.Label, i + 1), k, s, o))
        else:
            ents.append(Ent(o.Label, k, o.Shape, o))
    return ents


def parse_screw(sh):
    best = None
    for s in sh.Solids:
        for f in s.Faces:
            if f.Surface.__class__.__name__ == "Cylinder" and (best is None or f.Surface.Radius < best[1].Surface.Radius - 1e-6):
                best = (s, f)
    shank, f = best
    r = f.Surface.Radius
    ax = Vector(f.Surface.Axis)
    ax.normalize()
    c = Vector(f.Surface.Center)
    ts = [(v.Point - c).dot(ax) for v in shank.Vertexes]
    tmin, tmax = min(ts), max(ts)
    head = []
    for s in sh.Solids:
        rad = max(((v.Point - c) - ax * (v.Point - c).dot(ax)).Length for v in s.Vertexes)
        if rad > r + 0.3:
            head.append(s)
    ht = sum((v.Point - c).dot(ax) for s in head for v in s.Vertexes) / max(1, sum(len(s.Vertexes) for s in head))
    if ht < (tmin + tmax) / 2:
        d, p = ax, c + ax * tmin
    else:
        d, p = -ax, c + ax * tmax
    L = max((v.Point - p).dot(d) for s in sh.Solids if s not in head for v in s.Vertexes)
    dk = 2 * max(((v.Point - p) - d * (v.Point - p).dot(d)).Length for s in head for v in s.Vertexes)
    k = max(-(v.Point - p).dot(d) for s in head for v in s.Vertexes)
    return dict(p=p, d=d, r=r, dn=int(round(2 * r + 0.1)), L=L, dk=dk, k=k, shank=shank, head=Part.makeCompound(head))


def near(ents, bb, skip=None):
    return [e for e in ents if e is not skip and e.bb.intersect(bb)]


def check_screw(e, ents):
    s = parse_screw(e.shape)
    p, d, L, dn = s["p"], s["d"], s["L"], s["dn"]
    bb = e.shape.BoundBox
    bb.enlarge(3)
    cands = near(ents, bb, e)
    step = 0.3
    occ, axis_hit = {}, {}
    eng_t = []
    t = 0.1
    while t < L - 0.35:
        c = p + d * t
        pts = ring(c, d, dn / 2 + 0.6)
        engaged = False
        for x in cands:
            if x.kind == "screw":
                continue
            n_in = sum(1 for q in pts if x.inside(q))
            if n_in >= 3 or (x.kind == "tnut" and n_in >= 1):
                occ[x.label] = occ.get(x.label, 0) + step
                if x.kind in ENGAGE:
                    engaged = True
            if x.inside(c):
                axis_hit[x.label] = axis_hit.get(x.label, 0) + step
                if x.kind == "ref":
                    engaged = True
        if engaged:
            eng_t.append(t)
        t += step
    eng_len = len(eng_t) * step
    beyond = (L - (max(eng_t) + step / 2)) if eng_t else None       # thread length past the end of the nut / insert
    # tip: room to the next solid along the axis (blind holes)
    tip_room = None
    t = L
    while t < L + 4:
        if any(x.inside(p + d * t) for x in cands if x.kind != "screw"):
            tip_room = t - L
            break
        t += 0.25
    # radial gap in the holes of printed / MDF parts
    gaps = {}
    for x in cands:
        if x.kind in ("print", "mdf") and occ.get(x.label, 0) > 0 and x.label not in axis_hit:
            gaps[x.label] = s["shank"].distToShape(x.shape)[0]
    # head seat (what the head bears on) and side room
    seat = None
    for z in (0.15, 0.4, 0.8, 1.5):
        pts = ring(p + d * z, d, (dn / 2 + 0.6 + s["dk"] / 2) / 2, 12)
        for x in cands:
            if sum(1 for q in pts if x.inside(q)) >= 4:
                seat = (x.label, z - 0.15)
                break
        if seat:
            break
    side = None
    for gr in (0.2, 0.5, 1.0, 2.0):
        hits = set()
        for z in (-0.25, -s["k"] / 2, -s["k"] + 0.2):
            for q in ring(p + d * z, d, s["dk"] / 2 + gr, 8):
                for x in cands:
                    if x.inside(q):
                        hits.add(x.label)
        if hits:
            side = (gr, sorted(hits))
            break
    # tool access: straight line out of the head (axis + a ring the size of the key shaft)
    access = None
    bbt = Part.makeLine(p, p - d * 60).BoundBox
    bbt.enlarge(4)
    tcands = near(ents, bbt, e)
    t = s["k"] + 0.3
    while t < 60:
        c = p - d * t
        pts = [c] + ring(c, d, TOOL_R.get(dn, 2.0), 4)
        hit = [x.label for x in tcands if any(x.inside(q) for q in pts)]
        if hit:
            access = (t - s["k"], hit[0])
            break
        t += 1.0
    return dict(s=s, occ=occ, axis_hit=axis_hit, eng_len=eng_len, beyond=beyond, tip_room=tip_room, gaps=gaps,
                seat=seat, side=side, access=access)


def walls(x, centre, axis, r0, heights, ents, n=12):
    """Wall of printed material around a cylinder / hex of radius r0: min over directions; 'open' directions counted."""
    host = [h for h in ents if h.kind in ("print", "mdf") and h.bb.intersect(x.bb)]
    res, opened, hosts = [], 0, set()
    u, w = frame(axis)
    for z in heights:
        for k in range(n):
            a = 2 * math.pi * k / n
            dv = u * math.cos(a) + w * math.sin(a)
            first = centre + axis * z + dv * (r0 + 0.25)
            hh = [h for h in host if h.inside(first)]
            if not hh:
                opened += 1
                continue
            hosts.add(hh[0].label)
            t = r0 + 0.25
            while t < r0 + 10 and hh[0].inside(centre + axis * z + dv * t):
                t += 0.3
            res.append(t - r0)
    return (min(res) if res else None), opened, n * len(heights), sorted(hosts)


def check_nut(x, ents):
    sol = x.solids[0]
    cyl = [f for f in sol.Faces if f.Surface.__class__.__name__ == "Cylinder"][0]
    ax = Vector(cyl.Surface.Axis)
    ax.normalize()
    c = sol.CenterOfMass
    ts = [(v.Point - c).dot(ax) for v in sol.Vertexes]
    h = max(ts) - min(ts)
    rc = max(((v.Point - c) - ax * (v.Point - c).dot(ax)).Length for v in sol.Vertexes)
    rin = cyl.Surface.Radius
    if x.kind == "insert":
        rin = min(f.Surface.Radius for f in sol.Faces if f.Surface.__class__.__name__ == "Cylinder")   # thread bore
        if rin < 1.8:                                   # M3: wall from the real knurl, not the hole
            rc = max(rc, INS3_OD / 2)
        return dict(walls=walls(x, c, ax, rc, (-h / 3, 0, h / 3), ents), h=h, od=2 * rc, d=2 * rin)
    return dict(walls=walls(x, c, ax, rc, (0,), ents), h=h, af=rc * math.sqrt(3), d=2 * rin)


def verdict_screw(r, ents_by):
    s = r["s"]
    dn = s["dn"]
    flags = []
    eng_kinds = [ents_by[l].kind for l in r["occ"] if ents_by[l].kind in ENGAGE] + \
                [ents_by[l].kind for l in r["axis_hit"] if ents_by[l].kind == "ref"]
    printed_hits = [l for l in r["axis_hit"] if ents_by[l].kind in ("print", "mdf")]
    if printed_hits:
        flags.append("BAD: screw goes into solid plastic (%s)" % ", ".join(printed_hits))
    if not eng_kinds:
        flags.append("BAD: nothing to screw into (no nut / insert / threaded part found)")
    elif "nut" in eng_kinds:
        if r["eng_len"] < 0.75 * dn:
            flags.append("BAD: only %.1f mm in the nut" % r["eng_len"])
        if r["beyond"] is not None and r["beyond"] < 0.3:
            flags.append("WARN: tip ends inside the nut (%.1f mm past it)" % r["beyond"])
    elif "insert" in eng_kinds:
        if r["eng_len"] < 1.0 * dn:
            flags.append("BAD: only %.1f mm in the insert" % r["eng_len"])
        elif r["eng_len"] < 1.5 * dn:
            flags.append("WARN: %.1f mm in the insert (want >= %.1f)" % (r["eng_len"], 1.5 * dn))
    elif "tnut" in eng_kinds and r["beyond"] is not None and r["beyond"] > 1.5:
        flags.append("WARN: %.1f mm past the T-nut (check it doesn't hit the slot bottom)" % r["beyond"])
    if r["tip_room"] is not None and r["tip_room"] < 0.3 and "ref" not in eng_kinds:
        flags.append("WARN: tip %.1f mm from the bottom of the hole" % r["tip_room"])
    for l, g in r["gaps"].items():
        if g < 0.1:
            flags.append("WARN: hole in %s tight (%.2f mm per side)" % (l, g))
    if r["seat"] is None:
        flags.append("BAD: head bears on nothing")
    elif r["seat"][1] > 0.1:
        flags.append("WARN: head %.1f mm off its seat" % r["seat"][1])
    if r["side"] and r["side"][0] <= 0.2:
        flags.append("WARN: head side room < 0.2 mm (%s)" % ", ".join(r["side"][1]))
    if r["access"] and r["access"][0] < 15:
        flags.append("WARN: key blocked %.0f mm above the head by %s" % r["access"])
    return flags


def fmt_screw(i, e, r, flags):
    s = r["s"]
    occ = ", ".join("%s %.1f" % (l, v) for l, v in sorted(r["occ"].items(), key=lambda kv: -kv[1]))
    lines = ["[%02d] %s   M%d x %.0f  head %.1f x %.1f   at (%.1f, %.1f, %.1f) dir (%.0f, %.0f, %.0f)" % (
        i, e.label, s["dn"], s["L"], s["dk"], s["k"], s["p"].x, s["p"].y, s["p"].z, s["d"].x, s["d"].y, s["d"].z),
        "     passes through: %s" % (occ or "-"),
        "     thread engaged %.1f mm, past it %s, tip room %s" % (
            r["eng_len"], "-" if r["beyond"] is None else "%.1f" % r["beyond"], "free" if r["tip_room"] is None else "%.1f" % r["tip_room"]),
        "     hole gap per side: %s" % (", ".join("%s %.2f" % kv for kv in r["gaps"].items()) or "-"),
        "     head on: %s   side room: %s   key access: %s" % (
            "-" if r["seat"] is None else "%s (gap %.1f)" % r["seat"],
            ">= 2" if r["side"] is None else "< %.1f (%s)" % (r["side"][0], ", ".join(r["side"][1])),
            "free (60)" if r["access"] is None else "%.0f mm (%s)" % r["access"])]
    if r["axis_hit"]:
        lines.append("     axis inside (threaded into / expected): %s" % ", ".join("%s %.1f" % kv for kv in r["axis_hit"].items()))
    lines += ["     -> " + f for f in flags] or []
    lines.append("     -> OK" if not flags else "")
    return lines


# ------------------------------------------------------------------ pictures
def colour_of(e):
    try:
        return tuple(e.obj.ViewObject.ShapeColor[:3])
    except Exception:
        return (0.7, 0.7, 0.7)


def cut_view(sdoc, view, e, r, ents, fname):
    s = r["s"]
    p, d = s["p"], s["d"]
    n = Vector(0, 1, 0) if abs(d.y) < 0.9 else Vector(0, 0, 1)
    if os.environ.get("FC_N") == "z" and abs(d.z) < 0.9:      # second cut plane (horizontal), for a second look
        n = Vector(0, 0, 1)
    n = n - d * n.dot(d)
    n.normalize()
    e3 = d.cross(n)
    e3.normalize()
    R = max(10.0, s["dk"] * 2 + 2)
    a0, a1 = -s["k"] - 5, s["L"] + 6
    m = App.Matrix(d.x, n.x, e3.x, 0, d.y, n.y, e3.y, 0, d.z, n.z, e3.z, 0, 0, 0, 0, 1)
    box = Part.makeBox(a1 - a0, R, 2 * R)
    box.Placement = App.Placement(p + d * a0 - n * R - e3 * R, App.Rotation(m))
    for o in list(sdoc.Objects):
        sdoc.removeObject(o.Name)
    for x in near(ents, box.BoundBox):
        whole = False
        try:
            sh = e.shape.copy() if x is e else x.shape.common(box)
            bad = sh.isNull() or (x is not e and sh.Volume < 1e-3)
        except Exception:
            bad = True
        if bad:
            # bought parts from the printer / GrabCAD models often do not cut: show them whole, see-through, if small
            b = x.bb
            if x.kind != "ref" or max(b.XLength, b.YLength, b.ZLength) > 80:
                continue
            sh, whole = x.shape.copy(), True
        o = sdoc.addObject("Part::Feature", "c")
        o.Shape = sh
        o.ViewObject.ShapeColor = (0.9, 0.1, 0.1) if x is e else colour_of(x)
        o.ViewObject.LineColor = (0.2, 0.2, 0.2)
        if whole:
            o.ViewObject.Transparency = 65
    sdoc.recompute()
    up = -d
    X = up.cross(n)
    rot = App.Rotation(App.Matrix(X.x, up.x, n.x, 0, X.y, up.y, n.y, 0, X.z, up.z, n.z, 0, 0, 0, 0, 1))
    from pivy import coin  # noqa: F401  (loads the SWIG wrapper getCameraNode needs)
    view.setCameraType("Orthographic")
    view.getCameraNode().orientation.setValue(*rot.Q)     # direct, no animation (setCameraOrientation animates)
    view.fitAll()
    Gui.updateGui()
    view.getCameraNode().orientation.setValue(*rot.Q)
    view.fitAll()
    Gui.updateGui()
    view.saveImage(os.path.join(OUT, fname), 900, 700, "White")


def context_shots(doc, view, groups):
    objs = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    keep = {o.Name: (o.ViewObject.ShapeColor, o.ViewObject.Transparency, o.ViewObject.Visibility) for o in objs}
    for o in objs:
        o.ViewObject.Visibility = not o.Label.startswith(("RES_", "REF_PILE"))
    for g in groups:                                   # the group in red + the parts within 25 mm, see-through
        mine = [o for o in objs if o.Label.startswith(g)]
        bb = mine[0].Shape.BoundBox
        for o in mine[1:]:
            bb.add(o.Shape.BoundBox)
        bb.enlarge(25)
        for o in objs:
            if o.Label.startswith(g):
                o.ViewObject.ShapeColor = (0.9, 0.05, 0.05)
                o.ViewObject.Transparency = 0
                o.ViewObject.Visibility = True
            else:
                o.ViewObject.ShapeColor = keep[o.Name][0]
                o.ViewObject.Transparency = 70
                o.ViewObject.Visibility = (not o.Label.startswith(("RES_", "REF_PILE"))) and o.Shape.BoundBox.intersect(bb)
        view.viewIsometric()
        view.fitAll()
        Gui.updateGui()
        view.saveImage(os.path.join(OUT, "g_%s.png" % g), 1000, 800, "White")
    for o in objs:
        o.ViewObject.ShapeColor, o.ViewObject.Transparency, o.ViewObject.Visibility = keep[o.Name]


# ------------------------------------------------------------------ main
def run():
    rep = []
    try:
        doc = App.openDocument(os.path.join(CAD, "MODULE_CLAPETS_V7.FCStd"))
        Gui.updateGui()
        ents = entities(doc)
        by = {e.label: e for e in ents}
        screws = [e for e in ents if e.kind == "screw"]
        only = os.environ.get("FC_ONLY", "")
        if only:                                       # pictures only, for these screw numbers (the numbers stay in report.txt)
            want = {int(v) for v in only.split(",")}
            sdoc = App.newDocument("SECTION")
            Gui.updateGui()
            sv = Gui.getDocument(sdoc.Name).ActiveView
            for i, e in enumerate(screws, 1):
                if i in want:
                    log("picture %d" % i)
                    try:
                        cut_view(sdoc, sv, e, {"s": parse_screw(e.shape)}, ents, "s_%02d_%s%s.png" % (i, e.label.replace("#", "_"), "_z" if os.environ.get("FC_N") == "z" else ""))
                    except Exception:
                        log("picture %d failed %s" % (i, traceback.format_exc()))
            if os.environ.get("FC_GROUPS", "1") == "1":
                gv = Gui.getDocument(doc.Name).ActiveView
                context_shots(doc, gv, sorted({e.obj.Label.rsplit("-", 1)[0] for e in ents if e.kind in ("screw", "nut", "insert", "tnut")}))
            App.closeDocument(sdoc.Name)
            App.closeDocument(doc.Name)
            log("done")
            Gui.getMainWindow().close()
            return
        rep += ["Clapets v7 fastener check (rest pose). Lengths in mm.", ""]
        results = []
        n_bad = n_warn = 0
        log("%d entities, %d screws" % (len(ents), len(screws)))
        for i, e in enumerate(screws, 1):
            log("screw %d %s" % (i, e.label))
            try:
                r = check_screw(e, ents)
                fl = verdict_screw(r, by)
            except Exception:
                rep += ["[%02d] %s  ERROR" % (i, e.label), traceback.format_exc()]
                continue
            n_bad += any(f.startswith("BAD") for f in fl)
            n_warn += any(f.startswith("WARN") for f in fl) and not any(f.startswith("BAD") for f in fl)
            results.append((i, e, r, fl))
            rep += fmt_screw(i, e, r, fl)
        rep += ["", "Nuts and inserts: wall of plastic around them (min over the closed directions; 'open' = no plastic "
                    "right next to it in that direction, normal on the insertion side of a nut pocket)"]
        for x in ents:
            if x.kind not in ("nut", "insert"):
                continue
            log("nut/insert " + x.label)
            try:
                q = check_nut(x, ents)
            except Exception:
                rep += ["  %s ERROR %s" % (x.label, traceback.format_exc())]
                continue
            wmin, op, tot, hosts = q["walls"]
            fl = ""
            if wmin is not None and wmin < (1.2 if x.kind == "insert" else 1.0):
                fl = "  -> BAD: thin wall"
            elif wmin is not None and wmin < (2.0 if x.kind == "insert" else 1.5):
                fl = "  -> WARN: wall under %s mm" % ("2" if x.kind == "insert" else "1.5")
            if x.kind == "insert" and op > tot / 3:
                fl += "  -> WARN: insert not surrounded (%d/%d open)" % (op, tot)
            rep.append("  %-28s %-6s in %-22s min wall %s   open %d/%d%s" % (
                x.label, x.kind, ", ".join(hosts) or "-", "-" if wmin is None else "%.1f" % wmin, op, tot, fl))
        rep.insert(2, "Screws: %d checked, %d with a BAD point, %d with only warnings." % (len(results), n_bad, n_warn))
        with open(os.path.join(OUT, "report.txt"), "w") as f:
            f.write("\n".join(rep) + "\n")
        if SHOTS:
            gv = Gui.getDocument(doc.Name).ActiveView
            groups = sorted({e.obj.Label.rsplit("-", 1)[0] for e in ents if e.kind in ("screw", "nut", "insert", "tnut")})
            context_shots(doc, gv, groups)
            sdoc = App.newDocument("SECTION")
            Gui.updateGui()
            sv = Gui.getDocument(sdoc.Name).ActiveView
            for i, e, r, fl in results:
                log("picture %d" % i)
                try:
                    cut_view(sdoc, sv, e, r, ents, "s_%02d_%s.png" % (i, e.label.replace("#", "_")))
                except Exception:
                    with open(os.path.join(OUT, "report.txt"), "a") as f:
                        f.write("picture %d failed\n%s\n" % (i, traceback.format_exc()))
            App.closeDocument(sdoc.Name)
        App.closeDocument(doc.Name)
        log("done")
    except Exception:
        log("CRASH " + traceback.format_exc())
        with open(os.path.join(OUT, "report.txt"), "a") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, run)
