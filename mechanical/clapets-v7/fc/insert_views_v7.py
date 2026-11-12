# insert_views_v7.py - zoomed pictures of every heat-set insert in its hole (clapets v7).
# Run after v7_fc.py (needs the GUI):
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/insert_views_v7.py
# Output: ../CAD_FC/fastener_check/inserts/  NN_<insert>_side.png, NN_<insert>_top.png, README.md (table + real walls)
# Each insert is drawn at its REAL size (M3: Ø6.0 x 6, see design-principles.md), see-through, so the hole, its chamfer
# and the plastic around it stay visible. Side view: cut along the axis, through the thinnest wall. Top view: a 1 mm
# slice across the insert at mid depth, seen from the mouth. Read-only on the model (the .FCStd is never saved).
import math
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector
from PySide import QtCore, QtGui

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
OUT = os.path.join(CAD, "fastener_check", "inserts")
os.makedirs(OUT, exist_ok=True)
REAL = {3: (6.0, 6.0, 3.0), 4: (5.6, 6.0, 4.0)}     # outer Ø, length, thread Ø (M4: real size unknown, hole size)
HOLE_D = {3: 7.0, 4: 7.0}                           # blind hole depth in v7_fc.py (INS3_D, INS4_D)
WALL_MIN = 1.6                                      # design-principles.md
R_VIEW = 9.0                                        # half-width of the zoomed region


def log(msg):
    with open(os.path.join(OUT, "progress.log"), "a") as f:
        f.write(msg + "\n")


def perp(u):
    a = Vector(1, 0, 0) if abs(u.x) < 0.9 else Vector(0, 1, 0)
    p = u.cross(a)
    p.normalize()
    q = u.cross(p)
    q.normalize()
    return p, q


def inside(o, pt):
    sh = o.Shape
    return sh.BoundBox.isInside(pt) and any(s.BoundBox.isInside(pt) and s.isInside(pt, 1e-4, True) for s in sh.Solids)


def placed_box(origin, ex, ey, ez, lx, ly, lz):    # box with its edges along ex, ey, ez from origin
    b = Part.makeBox(lx, ly, lz)
    m = App.Matrix(ex.x, ey.x, ez.x, 0, ex.y, ey.y, ez.y, 0, ex.z, ey.z, ez.z, 0, 0, 0, 0, 1)
    b.Placement = App.Placement(origin, App.Rotation(m))
    return b


def caption(path, lines, bad):
    img = QtGui.QImage(path)
    out = QtGui.QImage(img.width(), img.height() + 22 * len(lines) + 10, QtGui.QImage.Format_RGB32)
    out.fill(QtGui.QColor("white"))
    p = QtGui.QPainter(out)
    p.drawImage(0, 22 * len(lines) + 10, img)
    f = QtGui.QFont("Arial", 12)
    for i, t in enumerate(lines):
        f.setBold(i == 0)
        p.setFont(f)
        p.setPen(QtGui.QColor("#b00020") if (bad and i == 1) else QtGui.QColor("#222222"))
        p.drawText(12, 22 * (i + 1), t)
    p.end()
    out.save(path)


def shoot(sdoc, view, items, X, up, fname):
    for o in list(sdoc.Objects):
        sdoc.removeObject(o.Name)
    for sh, rgb, transp in items:
        if sh is None or sh.isNull() or not sh.Solids:
            continue
        o = sdoc.addObject("Part::Feature", "c")
        o.Shape = sh
        o.ViewObject.ShapeColor = rgb
        o.ViewObject.LineColor = (0.15, 0.15, 0.15)
        o.ViewObject.Transparency = transp
    sdoc.recompute()
    n = X.cross(up)
    rot = App.Rotation(App.Matrix(X.x, up.x, n.x, 0, X.y, up.y, n.y, 0, X.z, up.z, n.z, 0, 0, 0, 0, 1))
    from pivy import coin  # noqa: F401
    view.setCameraType("Orthographic")
    for _ in range(2):
        view.getCameraNode().orientation.setValue(*rot.Q)
        view.fitAll()
        Gui.updateGui()
    path = os.path.join(OUT, fname)
    view.saveImage(path, 800, 650, "White")
    return path


def run():
    rows = []
    try:
        for f in os.listdir(OUT):
            if f.endswith(".png") or f == "progress.log":
                os.remove(os.path.join(OUT, f))
        doc = App.openDocument(os.path.join(CAD, "MODULE_CLAPETS_V7.FCStd"))
        objs = [o for o in doc.Objects if o.TypeId == "Part::Feature" and hasattr(o, "Shape") and o.Shape.Solids]
        prints = [o for o in objs if o.Label[:2] in ("A_", "B_")]
        screws = [o for o in objs if o.Label.startswith("FIX_VIS")]
        sdoc = App.newDocument("INSERTS")
        Gui.updateGui()
        view = Gui.getDocument(sdoc.Name).ActiveView
        k = 0
        for o in objs:
            if not o.Label.startswith("FIX_INSERT"):
                continue
            if o.Label.rsplit("-", 1)[0].endswith("_G"):      # left side = mirror of the right (_D): no pictures
                continue
            for j, so in enumerate(o.Shape.Solids, 1):
                k += 1
                name = "%s_%d" % (o.Label.replace("FIX_INSERT_", "").rsplit("-", 1)[0], j)
                log("%d %s" % (k, name))
                try:
                    cyl = [f for f in so.Faces if f.Surface.__class__.__name__ == "Cylinder"]
                    rin = min(f.Surface.Radius for f in cyl)
                    d = 3 if rin < 1.8 else 4
                    od, L, td = REAL[d]
                    rh = 2.7 if d == 3 else 2.8            # hole radius (INS3_R / INS4_R); M3 Ø5.4 since 2026-11-12
                    ax = Vector(cyl[0].Surface.Axis)
                    ax.normalize()
                    c = so.CenterOfMass
                    ts = [(v.Point - c).dot(ax) for v in so.Vertexes]
                    mid = c
                    p0, q0 = perp(ax)
                    # host = the printed part right outside the hole at mid depth
                    host = None
                    for pr in prints:
                        if sum(inside(pr, mid + (p0 * math.cos(a) + q0 * math.sin(a)) * (rh + 0.4)) for a in (0, 1.6, 3.1, 4.7)) >= 2:
                            host = pr
                            break
                    if host is None:
                        log("  no host")
                        continue
                    ends = [(c + ax * min(ts), ax), (c + ax * max(ts), ax * -1)]   # (end, direction into the hole)
                    empty = []
                    for e, u in ends:
                        p, q = perp(u)
                        empty.append(sum(not inside(host, e - u * 0.3 + (p * math.cos(a) + q * math.sin(a)) * (rh + 0.3))
                                         for a in [2 * math.pi * i / 12 for i in range(12)]))
                    mouth, u = ends[0] if empty[0] >= empty[1] else ends[1]
                    p, q = perp(u)
                    # real wall: from the insert's real outer radius outwards, in the host only
                    best = (99.0, p)
                    for z in (1.0, L / 2, L - 1.0):
                        for i in range(24):
                            a = 2 * math.pi * i / 24
                            dv = p * math.cos(a) + q * math.sin(a)
                            t = od / 2 + 0.05
                            if not inside(host, mouth + u * z + dv * t):
                                continue          # open side (e.g. the mouth face of a horizontal hole): not a wall
                            while t < od / 2 + 12 and inside(host, mouth + u * z + dv * t):
                                t += 0.1
                            if t - od / 2 < best[0]:
                                best = (t - od / 2, dv)
                    wall, dmin = best
                    # shapes: real insert (tube), host and its neighbours, screws
                    ins = Part.makeCylinder(od / 2, L, mouth, u).cut(Part.makeCylinder(td / 2, L + 2, mouth - u, u))
                    region = placed_box(mouth - u * 3 - p * R_VIEW - q * R_VIEW, p, q, u, 2 * R_VIEW, 2 * R_VIEW, HOLE_D[d] + 6)
                    near = [pr for pr in prints if pr.Shape.BoundBox.intersect(region.BoundBox)]
                    near_s = [s for s in screws if s.Shape.BoundBox.intersect(region.BoundBox)]
                    # --- side view: keep the half behind the plane through the axis and the thinnest wall
                    n = u.cross(dmin)
                    n.normalize()
                    half = placed_box(mouth - u * 3 - dmin * R_VIEW - n * R_VIEW, dmin, n, u, 2 * R_VIEW, R_VIEW, HOLE_D[d] + 6)
                    items = []
                    for pr in near:
                        sh = pr.Shape.common(half)
                        items.append((sh, (0.55, 0.7, 0.85) if pr is host else (0.75, 0.75, 0.75), 0 if pr is host else 50))
                    for s in near_s:
                        items.append((s.Shape.common(half), (0.85, 0.1, 0.1), 0))
                    items.append((ins.common(half), (0.85, 0.65, 0.2), 45))
                    up = u * -1
                    side = shoot(sdoc, view, items, up.cross(n), up, "%02d_%s_side.png" % (k, name))
                    # --- top view: 1 mm slice across the insert at mid depth, seen from the mouth
                    sl = placed_box(mouth + u * (L / 2 - 0.5) - p * R_VIEW - q * R_VIEW, p, q, u, 2 * R_VIEW, 2 * R_VIEW, 1.0)
                    items = []
                    for pr in near:
                        items.append((pr.Shape.common(sl), (0.55, 0.7, 0.85) if pr is host else (0.75, 0.75, 0.75), 0 if pr is host else 50))
                    items.append((ins.common(sl), (0.85, 0.65, 0.2), 30))
                    top = shoot(sdoc, view, items, q, p, "%02d_%s_top.png" % (k, name))
                    bad = wall < WALL_MIN
                    lines = ["%s  (M%d insert in %s)" % (name, d, host.Label.rsplit("-", 1)[0]),
                             "real wall min %.1f mm %s" % (wall, "-> under %.1f" % WALL_MIN if bad else "OK"),
                             "blue = the part, brass = insert at real size Ø%.1f x %.1f (see-through), red = screw, grey = other parts" % (od, L)]
                    caption(side, lines + ["cut along the axis, through the thinnest wall"], bad)
                    caption(top, lines + ["slice across the insert at mid depth, seen from the mouth"], bad)
                    rows.append((k, name, d, host.Label.rsplit("-", 1)[0], wall, os.path.basename(side), os.path.basename(top)))
                except Exception:
                    log("  FAILED " + traceback.format_exc())
        App.closeDocument(sdoc.Name)
        App.closeDocument(doc.Name)
        md = ["# Clapets v7: inserts in their holes",
              "",
              "Generated by `fc/insert_views_v7.py` (not committed: `CAD_FC/` is generated output). Inserts drawn at their",
              "**real** size (M3 Ø6.0 × 6), holes Ø5.4 × 7 + mouth cone Ø6.2 × 1.5 (since 2026-11-12). Left parts (`_G`) = mirror of the right (`_D`): not shown. Wall rule: ≥ %.1f mm (`mechanical/design-principles.md`)." % WALL_MIN,
              "",
              "| # | Insert | In part | Real wall min | Side | Top |",
              "|---|---|---|---|---|---|"]
        for k, name, d, hl, wall, s, t in rows:
            md.append("| %d | %s (M%d) | %s | %s | [side](%s) | [top](%s) |" % (
                k, name, d, hl, ("**%.1f**" % wall) if wall < WALL_MIN else "%.1f" % wall, s, t))
        with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(md) + "\n")
        log("done")
    except Exception:
        log("CRASH " + traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, run)
