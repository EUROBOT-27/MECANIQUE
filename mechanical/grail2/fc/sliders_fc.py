# sliders_fc.py - interactive motion study of grail2 in the FreeCAD GUI: one slider per movement.
#   Open:  "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/sliders_fc.py      (from mechanical/grail2)
#          or in FreeCAD: Macro > Macros... > browse to this file > Execute.
#   Needs CAD_FC/GRAIL2.FCStd + CAD_FC/joints_grail2.json (fc/grail2_fc.py).
# Panel (right dock):
#   * Lift (mm from the model pose): carriage on the T8 nut; the screw + coupling turn with it (lead 8 mm / turn)
#   * Flip (deg): U + horn + magnet about the servo axis; 0 = magnet pointing out (+y), +90 = up
#   * Sequence slider + Play: the cycle planned in joints_grail2.json (the other sliders follow it)
#   * Readouts: screw turns, highest point vs 350, inside the free flip arc or not.
#     "Check collisions" = real solid intersections at this pose (threaded screw replaced by a plain Ø8).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector

import g2_common as C

try:
    from PySide import QtCore, QtWidgets
except ImportError:
    from PySide import QtCore
    from PySide import QtGui as QtWidgets


class Study:
    def __init__(self):
        self.J = C.load_joints()
        path = os.path.join(C.CAD, self.J["fcstd"])
        self.doc = None
        for d in App.listDocuments().values():
            if os.path.normcase(d.FileName) == os.path.normcase(path):
                self.doc = d
        if self.doc is None:
            self.doc = App.openDocument(path)
        App.setActiveDocument(self.doc.Name)
        Gui.ActiveDocument = Gui.getDocument(self.doc.Name)
        self.base = {o.Name: App.Placement(o.Placement) for o in self.doc.Objects if hasattr(o, "Placement")}
        for o in self.doc.Objects:
            vo = getattr(o, "ViewObject", None)
            if vo is None:
                continue
            vo.Visibility = True
            if o.Name in self.J["colors"]:
                vo.ShapeColor = tuple(self.J["colors"][o.Name])
        sb = self.doc.getObject("SW_SCREW_T8_L300_lead8").Shape.BoundBox
        self.proxy = Part.makeCylinder(4.0, sb.ZLength, Vector(0, 0, sb.ZMin), Vector(0, 0, 1))
        self.lift, self.ang = self.J["sequence"][0][1], self.J["sequence"][0][2]
        self.apply()
        Gui.getDocument(self.doc.Name).activeView().viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")

    def apply(self):
        for n, pl in C.placements(self.J, self.lift, self.ang).items():
            o = self.doc.getObject(n)
            if o is not None:
                o.Placement = pl.multiply(self.base[n])
        self.doc.recompute()

    def from_sequence(self, t):
        self.lift, self.ang, label = C.simulate(self.J, t)
        self.apply()
        return label

    def readouts(self):
        J = self.J
        top = max(self.doc.getObject(n).Shape.BoundBox.ZMax for n in J["lift"]["objects"])
        screw_top = self.proxy.BoundBox.ZMax
        lo, hi = J["flip"]["free"]
        return "\n".join([
            "Screw turns from the model pose: %.2f" % (self.lift / C.LEAD),
            "Highest carriage point z %.1f  (%s 350 if the motor bottom is on the table)" % (top, "under" if top <= 350 else "OVER"),
            "Fixed screw top z %.1f (%s)" % (screw_top, "OVER 350" if screw_top > 350 else "ok"),
            "Flip %.1f deg: %s (free arc %.0f .. %.0f)" % (self.ang, "inside" if lo <= self.ang <= hi else "OUTSIDE", lo, hi),
        ])

    def collisions(self):
        J = self.J
        exp = {frozenset(p) for p in J["expected"]}
        ign = set(J["ignore"])
        shapes = {o.Name: o.Shape for o in self.doc.Objects if o.Name not in ign and hasattr(o, "Shape")}
        p = self.proxy.copy()
        p.Placement = C.screw_pl(self.lift).multiply(p.Placement)
        shapes["SCREW_PROXY"] = p
        moving = set(J["lift"]["objects"]) | set(J["flip"]["objects"])
        names = sorted(shapes)
        out = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if frozenset((a, b)) in exp or (a not in moving and b not in moving):
                    continue
                sa, sb = shapes[a], shapes[b]
                if not sa.BoundBox.intersect(sb.BoundBox):
                    continue
                try:
                    v = sa.common(sb).Volume
                except Exception:
                    v = -1
                if v > 0.5:
                    out.append("%s x %s : %.1f mm3" % (a, b, v))
        return "\n".join(out) if out else "No collision at this pose."


class Panel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.st = Study()
        J = self.st.J
        self.T = C.seq_duration(J)
        self.cfg = {"lift": (J["lift"]["min"], J["lift"]["max"], 0.5, J["lift"]["label"]),
                    "flip": (J["flip"]["min"], J["flip"]["max"], 0.5, J["flip"]["label"]),
                    "seq": (0.0, self.T, 0.05, "Sequence time (s)")}
        lay = QtWidgets.QVBoxLayout(self)
        self.sl = {}
        for key, (lo, hi, step, _) in self.cfg.items():
            lab = QtWidgets.QLabel()
            s = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            s.setRange(int(round(lo / step)), int(round(hi / step)))
            s.valueChanged.connect(lambda val, k=key: self.moved(k, val))
            lay.addWidget(lab)
            lay.addWidget(s)
            self.sl[key] = (s, lab)
        row = QtWidgets.QHBoxLayout()
        self.play = QtWidgets.QPushButton("Play sequence")
        self.play.clicked.connect(self.toggle_play)
        cb = QtWidgets.QPushButton("Check collisions at this pose")
        cb.clicked.connect(self.check)
        row.addWidget(self.play)
        row.addWidget(cb)
        lay.addLayout(row)
        self.info = QtWidgets.QLabel()
        self.info.setWordWrap(True)
        lay.addWidget(self.info)
        self.coll = QtWidgets.QPlainTextEdit()
        self.coll.setReadOnly(True)
        self.coll.setMaximumHeight(140)
        lay.addWidget(self.coll)
        lay.addStretch(1)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.sync()
        self.refresh()

    def sync(self):
        for k, val in (("lift", self.st.lift), ("flip", self.st.ang)):
            s, _ = self.sl[k]
            s.blockSignals(True)
            s.setValue(int(round(val / self.cfg[k][2])))
            s.blockSignals(False)

    def refresh(self, label=""):
        vals = {"lift": self.st.lift, "flip": self.st.ang, "seq": self.sl["seq"][0].value() * self.cfg["seq"][2]}
        for k, (s, lab) in self.sl.items():
            lab.setText("%s: %.1f" % (self.cfg[k][3], vals[k]))
        if label:
            self.sl["seq"][1].setText("%s: %.2f  -  %s" % (self.cfg["seq"][3], vals["seq"], label))
        self.info.setText(self.st.readouts())

    def moved(self, k, val):
        x = val * self.cfg[k][2]
        if k == "seq":
            label = self.st.from_sequence(x)
            self.sync()
            self.refresh(label)
            return
        if k == "lift":
            self.st.lift = x
        else:
            self.st.ang = x
        self.st.apply()
        self.refresh()

    def check(self):
        self.coll.setPlainText("checking...")
        QtWidgets.QApplication.processEvents()
        self.coll.setPlainText(self.st.collisions())

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play.setText("Play sequence")
        else:
            s, _ = self.sl["seq"]
            if s.value() >= s.maximum():
                s.setValue(0)
            self.timer.start(50)
            self.play.setText("Pause")

    def tick(self):
        s, _ = self.sl["seq"]
        if s.value() >= s.maximum():
            self.toggle_play()
            return
        s.setValue(s.value() + 1)


def show():
    mw = Gui.getMainWindow()
    for d in mw.findChildren(QtWidgets.QDockWidget):
        if d.objectName() == "Grail2Sliders":
            d.close()
            d.deleteLater()
    dock = QtWidgets.QDockWidget("grail2 - motion study", mw)
    dock.setObjectName("Grail2Sliders")
    dock.setWidget(Panel())
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    dock.show()
    return dock


_dock = show()
