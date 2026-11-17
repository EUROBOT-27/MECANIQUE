# flipbar_render.py - 3D pictures of the single-bar flip at 3 poses (GUI: opens FreeCAD, saves, closes itself).
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" flipbar_render.py      (from mechanical/flip-bar/fc/, ~1-2 min)
# -> ../../simulations/flip_bar/flipbar_3d_{start,mid,upright,linkage,station,gears}.png
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import FreeCAD as App  # noqa: E402
import FreeCADGui as Gui  # noqa: E402
from PySide import QtCore  # noqa: E402

SIM = os.path.normpath(os.path.join(HERE, "..", "..", "simulations", "flip_bar"))
ALU, ALU_D = (0.80, 0.82, 0.86), (0.66, 0.69, 0.74)
NAVY, RED, BLUE = (0.17, 0.31, 0.55), (0.75, 0.22, 0.17), (0.16, 0.38, 0.83)
ABS_D, TPU, BLACK = (0.22, 0.22, 0.25), (0.18, 0.64, 0.31), (0.07, 0.07, 0.08)
COL = {"base_330": (0.87, 0.78, 0.60), "wheels": (0.15, 0.15, 0.15), "column": ALU, "rear_plate": ALU_D,
       "standoffs": (0.55, 0.55, 0.58), "housings": ABS_D, "bearings_fixed": (0.85, 0.85, 0.88), "shaft_": (0.60, 0.60, 0.62),
       "brackets": ALU_D, "motor": (0.20, 0.20, 0.22), "switch_": (0.15, 0.55, 0.25), "stop_": BLACK,
       "pumps": (0.35, 0.35, 0.35), "valves": (0.85, 0.85, 0.80), "Crank": RED, "Crank_bearings": (0.85, 0.85, 0.88),
       "Rocker": BLUE, "Rocker_bearings": (0.85, 0.85, 0.88), "Bar": NAVY, "Bar_pins": (0.70, 0.70, 0.72),
       "Station_spacer": ABS_D, "Station_TPU": TPU, "Support_ring": ABS_D, "DPS30": BLACK,
       "Stone": (0.82, 0.70, 0.52), "Gear_": (0.95, 0.75, 0.15), "Motor_shaft": (0.6, 0.6, 0.62)}


def colour(o):
    best = None
    for k, c in COL.items():
        if o.Name.startswith(k) and (best is None or len(k) > len(best[0])):
            best = (k, c)
    return best[1] if best else (0.7, 0.7, 0.7)


def run():
    try:
        import flipbar_fc as F
        import flipbar_params as P
        App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations", False)
        doc = App.newDocument("flipbar_render")
        objs = F.build(doc)
        doc.removeObject("table")
        objs.pop("table")
        doc.recompute()
        for n, (o, k) in objs.items():
            o.ViewObject.ShapeColor = colour(o)
            o.ViewObject.LineColor = (0.15, 0.15, 0.18)
            o.ViewObject.LineWidth = 1.0
            if n.startswith("Stone"):
                o.ViewObject.Transparency = 60
        os.makedirs(SIM, exist_ok=True)
        gdoc = Gui.getDocument(doc.Name)
        view = gdoc.activeView()
        for s, name in ((0.0, "start"), (0.40, "mid"), (1.0, "upright")):
            F.pose(objs, (s,) + P.pose_at(s))
            doc.recompute()
            view.viewIsometric()
            view.fitAll()
            Gui.updateGui()
            view.saveImage(os.path.join(SIM, "flipbar_3d_%s.png" % name), 1600, 1200, "White")
        # close-up of the middle cup station: same isometric camera, mid-flip, frame hidden
        F.pose(objs, (0.40,) + P.pose_at(0.40))
        doc.recompute()
        hide = [o for n, (o, k) in objs.items() if n.startswith(("column", "rear_plate", "standoffs", "brackets", "motor",
                                                                  "housings", "Stone"))]
        for o in hide:
            o.ViewObject.Visibility = False
        Gui.Selection.clearSelection()
        for n in ("Station_spacer_2", "Support_ring_2", "Station_TPU_2", "DPS30_2"):
            Gui.Selection.addSelection(objs[n][0])
        Gui.SendMsgToActiveView("ViewSelection")
        Gui.Selection.clearSelection()
        Gui.updateGui()
        view.saveImage(os.path.join(SIM, "flipbar_3d_station.png"), 1600, 1200, "White")
        for o in hide:
            o.ViewObject.Visibility = True
        F.pose(objs, (0.40,) + P.pose_at(0.40))
        for n, (o, k) in objs.items():          # view from the stone side: the linkage + bar
            if n.startswith(("Stone", "base_330", "pumps", "valves", "wheels")):
                o.ViewObject.Visibility = False
        view.viewRear()
        view.fitAll()
        Gui.updateGui()
        view.saveImage(os.path.join(SIM, "flipbar_3d_linkage.png"), 1600, 1200, "White")
        # gear pair: seen from behind, rear plate / motor / housings hidden
        for n, (o, k) in objs.items():
            if n.startswith(("rear_plate", "motor", "housings", "bearings_fixed", "brackets", "standoffs")):
                o.ViewObject.Visibility = False
        view.viewFront()
        view.fitAll()
        Gui.updateGui()
        view.saveImage(os.path.join(SIM, "flipbar_3d_gears.png"), 1600, 1200, "White")
    except Exception:
        import traceback
        open(os.path.join(SIM, "render_error.txt"), "w").write(traceback.format_exc())
    for d in list(App.listDocuments()):        # close without the "save changes?" prompt, then quit
        if d.startswith("flipbar_render"):
            App.closeDocument(d)
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(1500, run)
