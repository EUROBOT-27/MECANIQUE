# render_any.py - open FreeCAD files in the GUI and save iso/front/top/right views of each (all objects visible).
import os

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

ROOT = r"C:/Projects/EUROBOT/Eurobot 2027-ALL/resources/CDR-2027/MCAD"
FILES = [("actuator-parts/suction-cup-prototype.FCStd", "suction"), ("actuator-parts/box-manipulator.FCStd", "boxmanip")]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cdr_img")
os.makedirs(OUT, exist_ok=True)


def run():
    for rel, tag in FILES:
        doc = App.openDocument(os.path.join(ROOT, rel))
        Gui.updateGui()
        view = Gui.getDocument(doc.Name).ActiveView
        for name, fn in (("iso", view.viewIsometric), ("front", view.viewFront), ("top", view.viewTop), ("right", view.viewRight)):
            fn()
            view.fitAll()
            Gui.updateGui()
            view.saveImage(os.path.join(OUT, "%s_%s.png" % (tag, name)), 1400, 1000, "White")
        App.closeDocument(doc.Name)
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(4000, run)
