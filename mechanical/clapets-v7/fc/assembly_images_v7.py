# assembly_images_v7.py - images for the module A assembly guide (needs the GUI):
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/assembly_images_v7.py
# Reads assembly/steps.py; writes assembly/img/step_NN_exploded.png, step_NN_detail.png, cover.png and
# assembly/img/views.json (balloon + arrow positions in pixels, detail scale). Then: python assembly/make_guide.py
import importlib.util
import json
import math
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
ASM = os.path.join(ROOT, "assembly")
IMG = os.path.join(ASM, "img")
os.makedirs(IMG, exist_ok=True)
FCSTD = os.path.join(ROOT, "CAD_FC", "MODULE_CLAPETS_V7.FCStd")
spec = importlib.util.spec_from_file_location("steps", os.path.join(ASM, "steps.py"))
steps_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(steps_mod)
STEPS = steps_mod.STEPS

W, H = 1600, 1100          # exploded view (landscape)
WD, HD = 1100, 800         # detail view (landscape)
GREY = (0.86, 0.87, 0.88)


def log(msg):
    with open(os.path.join(IMG, "progress.log"), "a") as f:
        f.write(msg + "\n")


def colour(label):
    if label.startswith("A_"):
        return (0.95, 0.55, 0.15)
    if label.startswith("FIX_VIS"):
        return (0.80, 0.12, 0.12)
    if label.startswith("FIX_"):
        return (0.92, 0.76, 0.18)
    if label.startswith("REF_TOLE") or label.startswith("A_TOLE"):
        return (0.72, 0.58, 0.40)
    return (0.45, 0.60, 0.80)


def collect(doc, name, filt):
    wild = name.endswith("*")
    p = name.rstrip("*")
    out = []
    for o in doc.Objects:
        if o.TypeId != "Part::Feature":
            continue
        base = o.Label.rsplit("-", 1)[0]
        if not (base == p or (wild and base.startswith(p))):
            continue
        subs = o.Shape.childShapes() if o.Label.startswith("FIX_") else (o.Shape.Solids or [o.Shape])
        for s in subs:
            c = s.BoundBox.Center
            if filt and not all(a0 <= getattr(c, ax) <= a1 for ax, (a0, a1) in filt.items()):
                continue
            out.append((o.Label, s.copy()))
    return out


def frame(d, up=Vector(0, 0, 1)):
    d = Vector(*d)
    d.normalize()
    y = up - d * up.dot(d)
    if y.Length < 1e-6:
        y = Vector(0, 1, 0) - d * d.y
    y.normalize()
    x = y.cross(d)
    x.normalize()
    return x, y, d


def show(tdoc, items, ctx_items):
    for lab, sh in ctx_items:
        o = tdoc.addObject("Part::Feature", "c")
        o.Shape = sh
        o.ViewObject.ShapeColor = GREY
        o.ViewObject.LineColor = (0.55, 0.56, 0.58)
    for lab, sh in items:
        o = tdoc.addObject("Part::Feature", "n")
        o.Shape = sh
        o.ViewObject.ShapeColor = colour(lab)
        o.ViewObject.LineColor = (0.15, 0.15, 0.15)
    tdoc.recompute()


def shoot(tdoc, d, path, w, h, up=Vector(0, 0, 1), margin=1.08):
    from pivy import coin  # noqa: F401
    view = Gui.getDocument(tdoc.Name).ActiveView
    view.setCameraType("Orthographic")
    x, y, z = frame(d, up)
    rot = App.Rotation(App.Matrix(x.x, y.x, z.x, 0, x.y, y.y, z.y, 0, x.z, y.z, z.z, 0, 0, 0, 0, 1))
    for _ in range(2):
        view.getCameraNode().orientation.setValue(*rot.Q)
        view.fitAll()
        Gui.updateGui()
    cam = view.getCameraNode()
    # fit the projected bounding box to the image aspect ourselves (fitAll used the window's aspect)
    pts = []
    for o in tdoc.Objects:
        bb = o.Shape.BoundBox
        for cx in (bb.XMin, bb.XMax):
            for cy in (bb.YMin, bb.YMax):
                for cz in (bb.ZMin, bb.ZMax):
                    pts.append(Vector(cx, cy, cz))
    us = [p.dot(x) for p in pts]
    vs = [p.dot(y) for p in pts]
    ws = [p.dot(z) for p in pts]
    a = w / float(h)
    hgt = max((max(vs) - min(vs)), (max(us) - min(us)) / a) * margin
    centre = x * ((max(us) + min(us)) / 2) + y * ((max(vs) + min(vs)) / 2) + z * (max(ws) + 500)
    cam.position.setValue(centre.x, centre.y, centre.z)
    cam.height.setValue(hgt)
    cam.nearDistance.setValue(1)
    cam.farDistance.setValue(max(ws) - min(ws) + 2000)
    Gui.updateGui()
    view.saveImage(path, w, h, "White")

    def proj(p):
        q = Vector(*p) - centre
        return ((q.dot(x) / (hgt * a)) + 0.5) * w, (0.5 - q.dot(y) / hgt) * h
    return proj, hgt / h


def exploded(src, st):
    tdoc = App.newDocument("E%d" % st["id"])
    Gui.updateGui()
    ctx = []
    for name in st["context"]:
        ctx += collect(src, name, None if name in ("A_AILE_D", "A_CAPOT_AILE_D") else {"x": (-1e9, 1e9)})
    # right side only for the parts that exist on both sides (filters in steps.py); context: drop the left door parts
    ctx = [(l, s) for l, s in ctx if not (s.BoundBox.Center.x < -60 and not l.startswith(("REF_RAILS", "A_SOCLE", "A_PLATINE", "A_TRAVERSE", "REF_PLAQUE", "REF_ROUES", "REF_NEMA", "REF_ENTRETOISES", "REF_RONDELLES", "FIX_")))]
    items, balloons = [], []
    for name, filt, ex, txt in st["new"]:
        got = collect(src, name, filt)
        if not got:
            log("step %d: nothing for %s %s" % (st["id"], name, filt))
            continue
        arrows = []
        for lab, sh in got:
            c0 = sh.BoundBox.Center
            arrows.append(((c0.x, c0.y, c0.z), (c0.x + ex[0], c0.y + ex[1], c0.z + ex[2])))
            sh.translate(Vector(*ex))
            items.append((lab, sh))
        moved = (abs(ex[0]) + abs(ex[1]) + abs(ex[2])) > 0.1
        if txt:     # balloon on the first part of the group; one arrow per part (max 6)
            balloons.append(dict(text=txt, p0=arrows[0][0], p1=arrows[0][1], moved=moved, arrows=arrows[:6] if moved else []))
    show(tdoc, items, ctx)
    path = os.path.join(IMG, "step_%02d_exploded.png" % st["id"])
    proj, mmpx = shoot(tdoc, st["view"], path, W, H)
    for b in balloons:
        b["px0"], b["px1"] = proj(b["p0"]), proj(b["p1"])
        b["arrows_px"] = [(proj(p0), proj(p1)) for p0, p1 in b["arrows"]]
    App.closeDocument(tdoc.Name)
    return dict(exploded=os.path.basename(path), balloons=balloons, mm_per_px=mmpx)


def detail(src, st):
    dt = st["detail"]
    tdoc = App.newDocument("D%d" % st["id"])
    Gui.updateGui()
    x0, x1, y0, y1, z0, z1 = dt["box"]
    crop = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))
    ax = dt["axis"]
    if dt.get("section"):
        px, py, pz = dt["section"]
        big = 5000
        if ax == "x":
            crop = crop.common(Part.makeBox(big, 2 * big, 2 * big, Vector(px - big, -big, -big)))
        elif ax == "y":
            crop = crop.common(Part.makeBox(2 * big, big, 2 * big, Vector(-big, py - big, -big)))
        else:
            crop = crop.common(Part.makeBox(2 * big, 2 * big, big, Vector(-big, -big, pz - big)))
    items = []
    for name in dt["labels"]:
        for lab, sh in collect(src, name, None):
            if not sh.BoundBox.intersect(crop.BoundBox):
                continue
            try:
                c = sh.common(crop)
            except Exception:
                continue
            if c.isNull() or c.Volume < 1e-3:
                continue
            items.append((lab, c))
    show(tdoc, items, [])
    d = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[ax]
    up = Vector(0, 1, 0) if ax == "z" else Vector(0, 0, 1)
    path = os.path.join(IMG, "step_%02d_detail.png" % st["id"])
    proj, mmpx = shoot(tdoc, d, path, WD, HD, up=up, margin=1.15)
    App.closeDocument(tdoc.Name)
    return dict(detail=os.path.basename(path), detail_mm_per_px=mmpx)


def cover(src):
    tdoc = App.newDocument("COVER")
    Gui.updateGui()
    skip = ("B_", "RES_", "REF_PILE", "REF_VENTOUSE", "REF_MG996R_TETE", "REF_AXE_TETE", "REF_608ZZ_TETE", "REF_FIL_",
            "FIX_VIS_TETE", "FIX_VIS_STATION", "FIX_ECROU_STATION", "FIX_INSERT_TETE", "FIX_ECROU_TETE", "FIX_VIS_ROUES",
            "FIX_ECROU_ROUES", "B_")
    items = [(o.Label, o.Shape.copy()) for o in src.Objects if o.TypeId == "Part::Feature" and not o.Label.startswith(skip)]
    show(tdoc, items, [])
    shoot(tdoc, (1.0, 1.6, 0.8), os.path.join(IMG, "cover.png"), W, H, margin=1.04)
    App.closeDocument(tdoc.Name)


def run():
    try:
        open(os.path.join(IMG, "progress.log"), "w").close()
        src = App.openDocument(FCSTD)
        Gui.updateGui()
        views = {}
        cover(src)
        log("cover")
        for st in STEPS:
            try:
                v = exploded(src, st)
                v.update(detail(src, st))
                views[str(st["id"])] = v
                log("step %d ok" % st["id"])
            except Exception:
                log("step %d FAILED %s" % (st["id"], traceback.format_exc()))
        with open(os.path.join(IMG, "views.json"), "w") as f:
            json.dump(views, f, indent=1)
        App.closeDocument(src.Name)
        log("done")
    except Exception:
        log("CRASH " + traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(2500, run)
