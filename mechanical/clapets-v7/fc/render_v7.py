# render_v7.py - colours + visibility saved into ../CAD_FC/MODULE_CLAPETS_V7.FCStd, still images in ../CAD_FC/images.
# Run after v7_fc.py:  "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" render_v7.py
# Module A = blue / orange, module B = green / orange / MDF, reserved head space = transparent purple.
import os
import shutil

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
IMG = os.path.join(CAD, "images")
os.makedirs(IMG, exist_ok=True)
HUB_SIM = os.environ.get("CLAPETS_COPY_DIR", "")              # optional: also copy videos/reports/images there

COLOURS = [   # (label prefix, rgb, transparency %)
    ("RES_TETE_ROTATION", (0.55, 0.30, 0.85), 88), ("RES_", (0.55, 0.30, 0.85), 75),
    ("A_AILE", (0.20, 0.45, 0.85), 0), ("A_CAPOT", (0.20, 0.45, 0.85), 0),("A_ROUE", (0.20, 0.45, 0.85), 0), ("A_PIGNON", (0.20, 0.45, 0.85), 0),
    ("A_TOLE", (0.72, 0.58, 0.40), 0), ("A_", (0.95, 0.45, 0.10), 0),
    ("B_STATION_TPU", (0.15, 0.75, 0.30), 0), ("B_PLATEAU", (0.72, 0.58, 0.40), 0), ("B_MOYEU", (0.10, 0.60, 0.55), 0),
    ("B_PIGNON", (0.10, 0.60, 0.55), 0), ("B_", (0.95, 0.75, 0.15), 0),
    ("REF_FIL_BRUN", (0.40, 0.22, 0.10), 0), ("REF_FIL_ROUGE", (0.85, 0.10, 0.10), 0), ("REF_FIL_ORANGE", (1.00, 0.60, 0.05), 0),
    ("REF_MOUSSE", (0.25, 0.65, 0.35), 0), ("REF_VENTOUSE", (0.30, 0.30, 0.32), 0),
    ("REF_RAIL", (0.13, 0.13, 0.15), 0), ("REF_PLAQUE", (0.25, 0.25, 0.28), 0), ("REF_ROUE", (0.05, 0.05, 0.05), 0),
    ("REF_NEMA", (0.13, 0.13, 0.15), 0), ("REF_ECROU", (0.80, 0.62, 0.25), 0), ("REF_MG996R", (0.10, 0.10, 0.12), 0),
    ("A_BRIDE", (0.95, 0.45, 0.10), 0), ("REF_PILE", (0.85, 0.72, 0.48), 60), ("REF_", (0.62, 0.63, 0.66), 0),
]


def shot(view, name, fn, w=1600, h=1100):
    fn()
    view.fitAll()
    Gui.updateGui()
    view.saveImage(os.path.join(IMG, name + ".png"), w, h, "White")


def run():
    doc = App.openDocument(os.path.join(CAD, "MODULE_CLAPETS_V7.FCStd"))
    Gui.ActiveDocument = Gui.getDocument(doc.Name)
    Gui.updateGui()
    for o in doc.Objects:
        o.ViewObject.Visibility = True
    for o in doc.Objects:
        for prefix, rgb, tr in COLOURS:
            if o.Label.startswith(prefix):
                o.ViewObject.ShapeColor = rgb
                o.ViewObject.Transparency = tr
                break
    view = Gui.ActiveDocument.ActiveView
    hide = lambda pre, on: [setattr(o.ViewObject, "Visibility", on) for o in doc.Objects if o.Label.startswith(pre)]
    hide("REF_PILE", False)
    shot(view, "v7_iso", view.viewIsometric)
    shot(view, "v7_front", view.viewRear)
    shot(view, "v7_top", view.viewTop)
    shot(view, "v7_side", view.viewRight)
    hide("RES_", False)                                  # without the reserve: the real parts
    shot(view, "v7_iso_parts", view.viewIsometric)
    shot(view, "v7_front_parts", view.viewRear)
    for o in doc.Objects:                                # module B alone
        if getattr(o, "Module", "") == "A" or o.Label.startswith(("REF_RAIL", "REF_PLAQUE", "REF_ROUE", "REF_NEMA", "REF_COUP", "REF_VIS", "REF_ECROU")):
            o.ViewObject.Visibility = False
    shot(view, "v7_module_B", view.viewIsometric)
    for o in doc.Objects:                                # module A + reserve, without B
        o.ViewObject.Visibility = getattr(o, "Module", "-") != "B" and not o.Label.startswith("REF_PILE")
    hide("RES_", True)
    shot(view, "v7_module_A_reserve", view.viewIsometric)
    def only(prefixes):
        for o in doc.Objects:
            o.ViewObject.Visibility = o.Label.startswith(prefixes)
    only(("A_AILE_D", "A_CAPOT_AILE_D", "A_BRIDE_SERVO_D", "REF_MG996R_D", "A_PIGNON_PORTE_20T-1", "A_ROUE_PORTE_28T-1"))
    shot(view, "v7_aile_D", view.viewIsometric)
    only(("A_AILE_D", "REF_MG996R_D"))
    shot(view, "v7_cable_servo_porte", view.viewRight)
    shot(view, "v7_aile_D_back", lambda: (view.viewIsometric(), view.setCameraOrientation(App.Rotation(App.Vector(0, 0, 1), 180).multiply(view.getCameraOrientation()))))
    only(("A_SUPPORT_ECROU", "REF_ECROU_T8", "REF_VIS_T8", "REF_PLAQUE_PAPILLON", "REF_RAIL_2020"))
    shot(view, "v7_support_ecrou", view.viewIsometric)
    only(("B_SUPPORT_TETE", "REF_MG996R_TETE", "REF_PLAQUE_PAPILLON", "REF_608ZZ_TETE"))
    shot(view, "v7_support_tete", view.viewRear)
    for o in doc.Objects:                                # saved state: everything but the reserve and the stack visible
        o.ViewObject.Visibility = True
    hide("RES_", False)
    view.viewIsometric()
    view.fitAll()
    doc.save()
    App.closeDocument(doc.Name)
    for f in ("v7_iso.png", "v7_iso_parts.png", "v7_module_B.png", "v7_module_A_reserve.png", "v7_front_parts.png",
              "v7_aile_D.png", "v7_aile_D_back.png", "v7_support_ecrou.png", "v7_support_tete.png", "v7_cable_servo_porte.png"):
        if HUB_SIM:
            os.makedirs(HUB_SIM, exist_ok=True)
            shutil.copy(os.path.join(IMG, f), os.path.join(HUB_SIM, f))
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(4000, run)
