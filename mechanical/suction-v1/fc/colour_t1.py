# colour_t1.py - colours every module B build (needs the GUI: freecadcmd can't store colours):
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/colour_t1.py      (from suction-v1/; opens, colours, saves, closes)
# Colours every FCStd under CAD_FC/turn/ and CAD_FC/stations/ by part name. Re-run after each generator run.
import glob
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
LOG = os.path.join(CAD, "colour_log.txt")

# (name prefix or part of the name, RGB, transparency %), first match wins
RULES = [
    ("REF_STONE", (0.80, 0.64, 0.42), 70),        # cardboard, see-through
    ("REF_BUTTERFLY_PLATE", (0.12, 0.12, 0.13), 0),
    ("REF_MG996R", (0.10, 0.12, 0.30), 0),         # servo (dark blue) + horn
    ("REF_6002", (0.75, 0.77, 0.80), 0),           # bearings: steel
    ("REF_SHAFT", (0.78, 0.47, 0.25), 0),          # copper pipe
    ("REF_TUBE", (0.15, 0.55, 0.95), 0),           # PU tubes: blue
    ("REF_CUP", (0.08, 0.08, 0.08), 0),            # cups: black rubber
    ("REF_ELBOW", (0.85, 0.85, 0.88), 0),          # fittings: nickel
    ("FIX_", (0.30, 0.30, 0.32), 0),               # screws, nuts
    ("TURN_PLATE", (0.82, 0.66, 0.45), 0),         # MDF
    ("T1_BRACKET", (0.20, 0.45, 0.80), 0),         # ABS parts: one colour per part
    ("T1_HUB", (0.95, 0.55, 0.15), 0),
    ("T1_PINION", (0.98, 0.82, 0.20), 0),
    ("T1_REAR_COLLAR", (0.95, 0.55, 0.15), 0),
    ("TPU_DISC", (0.75, 0.15, 0.15), 0),           # TPU: red
    ("S3_SPACER", (0.20, 0.65, 0.55), 0),          # stations: teal
    ("S3_SUPPORT_RING", (0.55, 0.85, 0.75), 0),
    ("S1_HOLDER", (0.20, 0.65, 0.55), 0),
    ("REF_", (0.60, 0.60, 0.60), 0),
]


def rule(name):
    for key, rgb, tr in RULES:
        if name.startswith(key) or key in name:
            return rgb, tr
    return (0.70, 0.70, 0.70), 0


def run():
    lines = []
    try:
        files = sorted(glob.glob(os.path.join(CAD, "turn", "*", "*.FCStd")) + glob.glob(os.path.join(CAD, "stations", "*", "*.FCStd")))
        for path in files:
            doc = App.openDocument(path)
            Gui.updateGui()
            n = 0
            for o in doc.Objects:
                if o.TypeId != "Part::Feature":
                    continue
                rgb, tr = rule(o.Label)
                o.ViewObject.ShapeColor = rgb
                o.ViewObject.LineColor = (0.15, 0.15, 0.15)
                o.ViewObject.Transparency = tr
                n += 1
            doc.save()
            App.closeDocument(doc.Name)
            lines.append("%s: %d parts coloured" % (os.path.relpath(path, CAD), n))
        lines.append("done")
    except Exception:
        lines.append("CRASH " + traceback.format_exc())
    with open(LOG, "w") as f:
        f.write("\n".join(lines) + "\n")
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(2500, run)
