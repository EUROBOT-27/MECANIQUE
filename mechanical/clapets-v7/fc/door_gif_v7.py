# door_gif_v7.py - quick GIF of the door module only (both door units + doors, plate, stack when clamped), split view:
# top view (left) + 3D view (right). Cycle: folded -> open -38 -> clamp +3 on the stack -> open -> folded.
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/door_gif_v7.py   -> CAD_FC/motion/doors.gif (~2 min)
import os

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
OUT = os.path.join(CAD, "motion")
PX, PY, SVY, RATIO = 131.0, 82.0, 52.0, 28 / 20
KEEP = ("A_AILE", "A_CAPOT", "REF_MG996R_D", "REF_MG996R_G", "REF_PLAQUE_PAPILLON", "REF_PILE")
W, H = 640, 480


def angles():
    seq = []
    def seg(a0, a1, n):
        seq.extend(a0 + (a1 - a0) * k / n for k in range(n))
    seg(90, -38, 14)
    seq.extend([-38] * 3)
    seg(-38, 3, 8)
    seq.extend([3] * 5)
    seg(3, -38, 6)
    seg(-38, 90, 12)
    seq.extend([90] * 3)
    return seq


def run():
    from PIL import Image
    doc = App.openDocument(os.path.join(CAD, "MODULE_CLAPETS_V7.FCStd"))
    gd = Gui.getDocument(doc.Name)
    moving, stack = [], []
    for o in doc.Objects:
        if o.TypeId != "Part::Feature":
            continue
        grp = getattr(o, "MotionGroup", "")
        show = grp.startswith(("door_", "pinion_")) or o.Label.startswith(KEEP)
        if o.Label.startswith("FIX_") and not grp.startswith(("door_", "pinion_")):
            show = o.Label.startswith(("FIX_VIS_AILE", "FIX_ECROU_AILE"))
        gd.getObject(o.Name).Visibility = show
        if grp.startswith(("door_", "pinion_")):
            moving.append((o, o.Placement, grp))
        if o.Label.startswith("REF_PILE"):
            stack.append(o)
            gd.getObject(o.Name).Transparency = 60
    v = gd.ActiveView
    v.setCameraType("Orthographic")
    for o in stack:                                       # frame each view ONCE (stack visible = largest extent)
        gd.getObject(o.Name).Visibility = True
    cams = {}
    for name, setv in (("top", v.viewTop), ("iso", v.viewIsometric)):
        setv()
        v.fitAll()
        Gui.updateGui()
        cams[name] = v.getCamera()
    imgs = []
    for k, a in enumerate(angles()):
        for o, base, grp in moving:
            s = 1 if grp.endswith("D") else -1
            if grp.startswith("door_"):
                rot = App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), s * a), Vector(s * PX, PY, 0))
            else:
                rot = App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), -s * RATIO * a), Vector(s * PX, SVY, 0))
            o.Placement = rot.multiply(base)
        for o in stack:                                   # the stack is there only while the doors are near it
            gd.getObject(o.Name).Visibility = a < 30
        Gui.updateGui()
        pair = []
        for name in ("top", "iso"):
            v.setCamera(cams[name])
            Gui.updateGui()
            p = os.path.join(OUT, "_frame_%s.png" % name)          # overwritten every frame, removed at the end
            v.saveImage(p, W, H, "White")
            pair.append(Image.open(p).convert("RGB"))
        im = Image.new("RGB", (2 * W, H), "white")
        im.paste(pair[0], (0, 0))
        im.paste(pair[1], (W, 0))
        imgs.append(im.convert("P", palette=Image.ADAPTIVE, colors=96))
    imgs[0].save(os.path.join(OUT, "doors.gif"), save_all=True, append_images=imgs[1:], duration=90, loop=0, optimize=True)
    for name in ("top", "iso"):
        os.remove(os.path.join(OUT, "_frame_%s.png" % name))
    App.closeDocument(doc.Name)
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(2500, run)
