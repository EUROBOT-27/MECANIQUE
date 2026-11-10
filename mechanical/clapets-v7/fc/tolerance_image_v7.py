# tolerance_image_v7.py - overview picture of the tolerance coupons (needs the GUI):
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/tolerance_image_v7.py  -> tolerance-tests/coupons.png
import os

import FreeCAD as App
import FreeCADGui as Gui
import Mesh
from PySide import QtCore

D = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tolerance-tests"))


def run():
    doc = App.newDocument("coupons")
    files = sorted((f for f in os.listdir(os.path.join(D, "stl")) if f.endswith(".stl")), key=lambda f: int(f[1:f.index("_")]))
    x, row = 0.0, 0
    for i, f in enumerate(files):
        m = Mesh.Mesh(os.path.join(D, "stl", f))
        bb = m.BoundBox
        if i in (4, 8):                     # 3 rows: T1-T4, T5-T8, T9-T10
            x, row = 0.0, row + 1
        y0 = 95.0 * row
        m.translate(x - bb.XMin, y0 - bb.YMin, -bb.ZMin)
        o = doc.addObject("Mesh::Feature", "m%d" % i)
        o.Mesh = m
        o.ViewObject.ShapeColor = (0.95, 0.55, 0.15)
        lbl = doc.addObject("App::Annotation", "L%d" % i)
        lbl.LabelText = [f.split("_")[0]]
        lbl.Position = App.Vector(x + bb.XLength / 2, y0 - 10, 0)
        lbl.ViewObject.FontSize = 18
        x += bb.XLength + 15
    doc.recompute()
    v = Gui.getDocument(doc.Name).ActiveView
    v.viewIsometric()
    v.fitAll()
    Gui.updateGui()
    v.saveImage(os.path.join(D, "coupons.png"), 1600, 1100, "White")
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(2000, run)
