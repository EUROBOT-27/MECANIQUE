# pose_v8.py - move the clapets v8 by hand in FreeCAD: a panel with sliders for the lift, the doors, the head turn and
# the strike. Every part follows its own rule (same rules as motion_v8.py), so gears, crank, carriage and stack move
# together. "Check collisions" tests the current pose. "Rest pose" puts everything back.
#
# Use: open CAD_FC/MODULE_CLAPETS_V8.FCStd in FreeCAD 1.1, then Macro > Macros... > browse to this fc/ folder >
# pose_v8.py > Execute. (Or in the Python console: exec(open(r"<path>/fc/pose_v8.py", encoding="utf-8").read()) )
# Don't save the document in a moved pose: the generator rebuilds it anyway, but the panel takes the CURRENT placements
# as the rest pose the first time it runs on a document.
import math

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
from PySide import QtCore, QtGui
try:
    from PySide import QtWidgets
except ImportError:
    QtWidgets = QtGui

# = v8_fc.py class G
PX, PY, SVY, HZ = 131.0, 82.0, 52.0, 165.0
HGC, HS_ANG = 31.25, 25.0
HS_X = -HGC * math.sin(math.radians(HS_ANG))
HS_Z = HZ - HGC * math.cos(math.radians(HS_ANG))
HEAD_RATIO, DOOR_RATIO = 30 / 20, 28 / 20
SS_Y, SS_Z, CR_R = 70.2, 128.0, 8.0                       # strike servo shaft (y, z), crank pin radius
B_FIXED = ("B_BASE_TETE", "REF_TIGE_GUIDE", "FIX_VIS_ROUES", "FIX_ECROU_ROUES")
CRANK = ("B_MANIVELLE_FRAPPE", "FIX_VIS_MANIVELLE")
EXPECTED = (("REF_ECROU_T8", "REF_VIS_T8"), ("REF_RAILS_2020", "REF_ROUES_V"), ("FIX_VIS_PIGNON_PORTE", "REF_MG996R"),
            ("FIX_VIS_TETE_PIGNON", "REF_MG996R_TETE"), ("FIX_VIS_MANIVELLE", "REF_MG996R_FRAPPE"),
            ("A_SOCLE", "REF_RAILS_2020"), ("REF_COUPLEUR_5x8", "REF_VIS_T8"), ("FIX_VIS_MOTEUR", "REF_NEMA17"),
            ("REF_ECROU_T8", "FIX_VIS_SUPPORT_ECROU"), ("FIX_TNUT_RAILS", "REF_RAILS_2020"), ("FIX_VIS_RAILS", "REF_RAILS_2020"))
SLIDERS = (("lift", "Lift (mm)", 0, 75, 0), ("doors", "Doors (deg, 0 = on the stack, 90 = folded, -38 = open)", -38, 90, 0), ("head", "Head turn (deg)", 0, 90, 0),
           ("strike", "Strike servo (deg)", 0, 90, 0))


def _rot(axis, deg, centre):
    return App.Placement(Vector(), App.Rotation(Vector(*axis), deg), Vector(*centre))


def _lift(h):
    return App.Placement(Vector(0, 0, h), App.Rotation())


class PosePanel:
    def __init__(self, doc):
        self.doc = doc
        self.objs = [o for o in doc.Objects if o.TypeId == "Part::Feature" and hasattr(o, "MotionGroup")]
        store = getattr(App, "_clapets_v8_rest", {})
        App._clapets_v8_rest = store
        if doc.Name not in store:
            store[doc.Name] = {o.Name: App.Placement(o.Placement) for o in self.objs}
        self.base = store[doc.Name]
        self.v = {k: d for k, _, _, _, d in SLIDERS}
        self.carry = False
        self.build_ui()
        self.apply()

    # ------------------------------------------------------------------ pose rules
    def placement(self, o):
        base = self.base[o.Name]
        grp, mod, lab = o.MotionGroup, getattr(o, "Module", "-"), o.Label
        h, a, ph, st = self.v["lift"], self.v["doors"], self.v["head"], self.v["strike"]
        dy = CR_R * math.sin(math.radians(st))                         # scotch yoke: carriage travel
        strike = App.Placement(Vector(0, dy, 0), App.Rotation())
        moves_b = mod == "B" and not lab.startswith(B_FIXED)
        if grp == "fixed":
            return base
        if grp == "stack":
            if not self.carry:
                return base
            return _lift(h).multiply(_rot((0, 1, 0), ph, (0, 0, HZ))).multiply(base)
        if grp == "reserve":
            return _lift(h).multiply(base)
        if grp.startswith("door_"):
            s = 1 if grp.endswith("D") else -1
            return _lift(h).multiply(_rot((0, 0, 1), s * a, (s * PX, PY, 0))).multiply(base)
        if grp.startswith("pinion_"):
            s = 1 if grp.endswith("D") else -1
            return _lift(h).multiply(_rot((0, 0, 1), -s * DOOR_RATIO * a, (s * PX, SVY, 0))).multiply(base)
        if grp == "hpinion":
            return _lift(h).multiply(strike).multiply(_rot((0, 1, 0), -HEAD_RATIO * ph, (HS_X, 0, HS_Z))).multiply(base)
        if grp == "head":
            return _lift(h).multiply(strike).multiply(_rot((0, 1, 0), ph, (0, 0, HZ))).multiply(base)
        # "carriage": moves with the lift; module B's carriage parts also strike; the crank also turns
        pl = base
        if lab.startswith(CRANK):
            pl = _rot((1, 0, 0), st, (0, SS_Y, SS_Z)).multiply(pl)
        if moves_b:
            pl = strike.multiply(pl)
        return _lift(h).multiply(pl)

    def apply(self):
        for o in self.objs:
            o.Placement = self.placement(o)
        self.doc.recompute()
        dy = CR_R * math.sin(math.radians(self.v["strike"]))
        self.info.setText("carriage forward %.1f mm (cups %.1f mm into the stack face)" % (dy, dy))

    # ------------------------------------------------------------------ collisions in the current pose
    @staticmethod
    def body(o):
        grp, lab = o.MotionGroup, o.Label
        if grp in ("head", "hpinion"):
            return grp
        if lab.startswith(CRANK):
            return "crank"
        if grp == "carriage" and getattr(o, "Module", "-") == "B" and not lab.startswith(B_FIXED):
            return "b_slide"
        return grp

    def check(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            objs = [o for o in self.objs if o.MotionGroup != "reserve" and o.ViewObject.Visibility]
            hits = []
            for i in range(len(objs)):
                for j in range(i + 1, len(objs)):
                    oi, oj = objs[i], objs[j]
                    if self.body(oi) == self.body(oj):              # same rigid body: they never move relative to each other
                        continue
                    if not oi.Shape.BoundBox.intersect(oj.Shape.BoundBox):
                        continue
                    v = oi.Shape.common(oj.Shape).Volume
                    if v <= 0.05:
                        continue
                    pair = (oi.Label.rsplit("-", 1)[0], oj.Label.rsplit("-", 1)[0])
                    if any((pair[0].startswith(x) and pair[1].startswith(y)) or (pair[1].startswith(x) and pair[0].startswith(y))
                           for x, y in EXPECTED):
                        continue
                    if any(p.startswith("REF_PILE") for p in pair) and any(p.startswith(("REF_VENTOUSE", "REF_MOUSSE")) for p in pair):
                        continue                                    # cups / door foam pressing on the stack: wanted
                    hits.append("%8.1f mm3  %s / %s" % (v, oi.Label, oj.Label))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        txt = "No collision in this pose." if not hits else "%d collision(s):\n" % len(hits) + "\n".join(hits)
        App.Console.PrintMessage("[pose_v8] " + txt + "\n")
        self.result.setPlainText(txt)

    # ------------------------------------------------------------------ UI
    def build_ui(self):
        mw = Gui.getMainWindow()
        old = mw.findChild(QtWidgets.QDockWidget, "ClapetsV8Pose")
        if old:
            old.close()
            old.deleteLater()
        dock = QtWidgets.QDockWidget("Clapets v8 - pose", mw)
        dock.setObjectName("ClapetsV8Pose")
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        self.sliders = {}
        for key, text, lo, hi, d in SLIDERS:
            lab = QtWidgets.QLabel("%s: %d" % (text, d))
            sl = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            sl.setRange(lo, hi)
            sl.setValue(d)
            sl.valueChanged.connect(lambda val, k=key, l=lab, t=text: self.on_slide(k, val, l, t))
            lay.addWidget(lab)
            lay.addWidget(sl)
            self.sliders[key] = sl
        cb = QtWidgets.QCheckBox("Stack follows the lift and the head (carried)")
        cb.stateChanged.connect(self.on_carry)
        lay.addWidget(cb)
        self.info = QtWidgets.QLabel("")
        lay.addWidget(self.info)
        row = QtWidgets.QHBoxLayout()
        b1 = QtWidgets.QPushButton("Check collisions")
        b1.clicked.connect(self.check)
        b2 = QtWidgets.QPushButton("Rest pose")
        b2.clicked.connect(self.reset)
        row.addWidget(b1)
        row.addWidget(b2)
        lay.addLayout(row)
        self.result = QtWidgets.QPlainTextEdit()
        self.result.setReadOnly(True)
        lay.addWidget(self.result)
        dock.setWidget(w)
        mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.dock = dock

    def on_slide(self, key, val, lab, text):
        self.v[key] = val
        lab.setText("%s: %d" % (text, val))
        self.apply()

    def on_carry(self, state):
        self.carry = bool(state)
        self.apply()

    def reset(self):
        for key, _, _, _, d in SLIDERS:
            self.sliders[key].setValue(d)
        self.result.setPlainText("")


_doc = App.ActiveDocument
if _doc is None or not _doc.Name.startswith("MODULE_CLAPETS_V8"):
    App.Console.PrintError("[pose_v8] open CAD_FC/MODULE_CLAPETS_V8.FCStd first (and make it the active document)\n")
else:
    App._clapets_v8_panel = PosePanel(_doc)
