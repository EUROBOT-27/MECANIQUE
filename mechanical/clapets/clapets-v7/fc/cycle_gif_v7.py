# cycle_gif_v7.py - GIF of the module A cycle (lift + doors, NO module B), split view: side (left) + 3D (right).
# Closed (folded) -> doors open -> the stack appears -> doors grab it -> lift 75 mm -> lower -> release.
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/cycle_gif_v7.py   -> CAD_FC/motion/cycle_moduleA.gif (~2 min)
import os

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
OUT = os.path.join(CAD, "motion")
PX, PY, SVY, RATIO = 131.0, 82.0, 52.0, 28 / 20       # = v7_fc.py class G
FOLD, OPEN, CLAMP, LIFT = 90.0, -38.0, 3.0, 75.0
W, H = 640, 520


def timeline():
    """frames of (lift h, door angle a, stack shown, stack held)"""
    f = []
    def seg(h0, h1, a0, a1, n, show, held):
        f.extend((h0 + (h1 - h0) * k / n, a0 + (a1 - a0) * k / n, show, held) for k in range(n))
    seg(0, 0, FOLD, FOLD, 3, False, False)        # closed
    seg(0, 0, FOLD, OPEN, 12, False, False)       # doors open
    seg(0, 0, OPEN, OPEN, 4, True, False)         # the stack appears
    seg(0, 0, OPEN, CLAMP, 8, True, False)        # grab
    seg(0, 0, CLAMP, CLAMP, 2, True, True)
    seg(0, LIFT, CLAMP, CLAMP, 10, True, True)    # lift
    seg(LIFT, LIFT, CLAMP, CLAMP, 3, True, True)
    seg(LIFT, 0, CLAMP, CLAMP, 8, True, True)     # lower
    seg(0, 0, CLAMP, OPEN, 6, True, False)        # release
    seg(0, 0, OPEN, OPEN, 4, True, False)
    return f


def place(base, grp, h, a, hs):
    lift = App.Placement(Vector(0, 0, h), App.Rotation())
    if grp == "carriage":
        return lift.multiply(base)
    if grp.startswith("door_"):
        s = 1 if grp.endswith("D") else -1
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), s * a), Vector(s * PX, PY, 0))).multiply(base)
    if grp.startswith("pinion_"):
        s = 1 if grp.endswith("D") else -1
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), -s * RATIO * a), Vector(s * PX, SVY, 0))).multiply(base)
    if grp == "stack":
        return App.Placement(Vector(0, 0, hs), App.Rotation()).multiply(base)
    return base


def run():
    from PIL import Image
    doc = App.openDocument(os.path.join(CAD, "MODULE_CLAPETS_V7.FCStd"))
    gd = Gui.getDocument(doc.Name)
    objs = []
    for o in doc.Objects:
        if o.TypeId != "Part::Feature":
            continue
        grp = getattr(o, "MotionGroup", "fixed")
        b_side = getattr(o, "Module", "-") == "B" or grp in ("head", "hpinion", "reserve") or o.Label.startswith("RES_")
        gd.getObject(o.Name).Visibility = not b_side
        if not b_side:
            objs.append((o, o.Placement, grp))
        if grp == "stack":
            gd.getObject(o.Name).Transparency = 45
    v = gd.ActiveView
    v.setCameraType("Orthographic")
    # frame both views once, at the highest pose with the stack shown (largest extent)
    for o, base, grp in objs:
        o.Placement = place(base, grp, LIFT, OPEN, LIFT)
    Gui.updateGui()
    cams = {}
    for name, setv in (("side", v.viewRight), ("iso", v.viewIsometric)):
        setv()
        v.fitAll()
        Gui.updateGui()
        cams[name] = v.getCamera()
    imgs, hs = [], 0.0
    for h, a, show, held in timeline():
        if held:
            hs = h
        for o, base, grp in objs:
            o.Placement = place(base, grp, h, a, hs)
            if grp == "stack":
                gd.getObject(o.Name).Visibility = show
        Gui.updateGui()
        pair = []
        for name in ("side", "iso"):
            v.setCamera(cams[name])
            Gui.updateGui()
            p = os.path.join(OUT, "_frame_%s.png" % name)
            v.saveImage(p, W, H, "White")
            pair.append(Image.open(p).convert("RGB"))
        im = Image.new("RGB", (2 * W, H), "white")
        im.paste(pair[0], (0, 0))
        im.paste(pair[1], (W, 0))
        imgs.append(im.convert("P", palette=Image.ADAPTIVE, colors=96))
    imgs[0].save(os.path.join(OUT, "cycle_moduleA.gif"), save_all=True, append_images=imgs[1:], duration=100, loop=0, optimize=True)
    for name in ("side", "iso"):
        os.remove(os.path.join(OUT, "_frame_%s.png" % name))
    App.closeDocument(doc.Name)
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(2500, run)
