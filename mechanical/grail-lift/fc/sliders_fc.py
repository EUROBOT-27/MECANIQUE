# sliders_fc.py - interactive motion study of the Grail lift in the FreeCAD GUI: one slider per movement.
#   Open:  "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/sliders_fc.py      (from mechanical/grail-lift)
#          or in FreeCAD: Macro > Macros... > browse to this file > Execute.
#   Needs CAD_FC/GRAIL_LIFT_V2.FCStd + joints_v2.json (fc/v2_fc.py) and/or GRAIL_LIFT_V1.FCStd + joints_v1.json (fc/v1_fc.py).
# Panel (right dock):
#   * Version v1 (Baha's essai mecanisme 1, rebuilt) / v2 (concept)
#   * Lift, Flip (v1: tilt), Grail approach (the robot driving in, moves the free Grail along x) sliders
#   * Magnet ON: the Grail follows the arm from where it is; OFF: it stays where it is (no gravity: watch "Grail bottom")
#   * Sequence slider + Play: the planned cycle (joints_*.json) - the other sliders follow it
#   * Live readouts: highest actuator point vs 350, allowed lift band at this flip angle (v2 plan), Grail bottom /
#     over the roof, protrusion beyond the face. "Check collisions" = real solid intersections at this pose.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector

import grail_common as C

try:
    from PySide import QtCore, QtWidgets
except ImportError:                                   # older FreeCAD shim
    from PySide import QtCore
    from PySide import QtGui as QtWidgets

EXPECTED = {frozenset(p) for p in (("CAR_PINION_20T", "RACK_M1"), ("CAR_VWHEELS", "COL_2020"), ("CAR_SLIDERS", "COL_2020"), ("SCREW_T8", "NUT_T8_brass"), ("SCREW_T8", "BEARING_608_BLOCK"), ("SCREW_T8", "COUPLER_5x8"), ("COUPLER_5x8", "NEMA17_LIFT"), ("CAR_SPACERS", "CAR_VWHEELS"),
                                   ("CAR_SPACERS", "CAR_PLATE"), ("PIVOT_PIN_M3", "CRADLE_printed"),
                                   ("SERVO_HORN_ROUND", "SERVO_MG996R"), ("PIVOT_PIN_M3", "U_BRACKET_steel"),
                                   ("SERVO_HORN_ROUND", "U_BRACKET_steel"), ("REAL_RACK_1M_280", "REAL_PINION_20T_1M"),
                                   ("REAL_NEMA14_SHAFT", "REAL_COUPLING_liaison"), ("REAL_PINION_20T_1M", "REAL_COUPLING_liaison"))}


class Study:
    def __init__(self, version):
        self.J = C.load_joints(os.path.join(C.CAD, "joints_%s.json" % version))
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
            vo.Visibility = True                           # FCStd written by freecadcmd has no view data
            if o.Name in self.J.get("colors", {}):
                vo.ShapeColor = tuple(self.J["colors"][o.Name])
            if o.Name in self.J.get("transparent", {}):
                vo.Transparency = self.J["transparent"][o.Name]
        s0 = self.J["sequence"][0]
        self.lift, self.ang, self.app = s0[1], s0[2], s0[4]
        self.on, self.rel = False, None
        self.grail = self.grail_free(self.app)
        self.apply()                                       # show the sequence's start pose
        Gui.getDocument(self.doc.Name).activeView().viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")

    def grail_free(self, app):
        o = Vector(*self.J["grail"]["start_offset"])
        return App.Placement(o + Vector(*self.J["grail"].get("approach_dir", [1, 0, 0])) * app, App.Rotation())

    def apply(self):
        J = self.J
        lp, fp = C.lift_pl(J, self.lift), C.flip_pl(J, self.lift, self.ang)
        if self.on and self.rel is not None:
            self.grail = fp.multiply(self.rel)
        for n in J["lift"]["objects"]:
            self.set(n, lp)
        for n in J["flip"]["objects"]:
            self.set(n, fp)
        for n in J["grail"]["objects"]:
            self.set(n, self.grail)
        self.doc.recompute()

    def set(self, name, pl):
        o = self.doc.getObject(name)
        if o is not None:
            o.Placement = pl.multiply(self.base[name])

    def magnet(self, on):
        if on and not self.on:
            self.rel = C.flip_pl(self.J, self.lift, self.ang).inverse().multiply(self.grail)
            self.on = True
        elif not on and self.on:
            self.on = False
        self.apply()

    def reset_grail(self):
        self.on, self.rel = False, None
        self.app = self.J["sequence"][0][4]
        self.grail = self.grail_free(self.app)
        self.apply()

    def approach(self, x):
        """The robot drives: a free Grail moves along x by the slider change."""
        d, self.app = x - self.app, x
        if not self.on:
            ad = Vector(*self.J["grail"].get("approach_dir", [1, 0, 0]))
            self.grail = App.Placement(self.grail.Base + ad * d, self.grail.Rotation)
        self.apply()

    def from_sequence(self, t):
        lift, ang, on, g, label = C.simulate(self.J, t)
        self.lift, self.ang, self.grail, self.on = lift, ang, g, on
        self.rel = C.flip_pl(self.J, lift, ang).inverse().multiply(g) if on else None
        seq, t0, self.app = self.J["sequence"], 0.0, self.J["sequence"][0][4]
        for k in range(1, len(seq)):                      # approach value at t (for the slider)
            d = seq[k][0]
            if t < t0 + d:
                self.app = seq[k - 1][4] + (seq[k][4] - seq[k - 1][4]) * ((t - t0) / d if d else 1)
                break
            self.app, t0 = seq[k][4], t0 + d
        self.apply()
        return label

    def readouts(self):
        J, lim = self.J, self.J["limits"]
        objs = [self.doc.getObject(n) for n in J["actuators"]]
        top = max(o.Shape.BoundBox.ZMax for o in objs if o)
        xmax = max(o.Shape.BoundBox.XMax for o in objs if o)
        txt = ["Highest actuator point: %.1f mm  (%s, limit %.0f)" % (top, "OK" if top <= lim["h_max"] else "TOO HIGH", lim["h_max"]),
               "Protrusion beyond the face (actuators): %.1f mm" % xmax]
        w = J.get("window")
        if w:
            r = min(w, key=lambda q: abs(q[0] - self.ang))
            lo = r[3] if self.on else r[2]
            if lo is not None and r[1] - lo >= 159.5:     # planner scanned 160 mm down without a hit: free to the bottom
                lo = J["lift"]["min"]
            ok = lo is not None and lo - 0.5 <= self.lift <= r[1] + 0.5
            txt.append("Planned lift band at %d deg (%s): %s .. %.1f  -> %s"
                       % (r[0], "Grail held" if self.on else "no Grail", "none" if lo is None else "%.1f" % lo, r[1],
                          "inside" if ok else "OUTSIDE"))
        for n in J["grail"]["objects"]:
            g = self.doc.getObject(n).Shape.BoundBox
            over = lim.get("edge_x") is not None and g.XMax < lim["edge_x"]
            txt.append("Grail bottom z %.1f, x %.1f..%.1f  %s" % (g.ZMin, g.XMin, g.XMax,
                       ("over the roof (L4 if it rests at %.0f+)" % lim["roof"]) if over else ""))
        txt.append("Magnet: %s" % ("ON - Grail follows the arm" if self.on else "off"))
        return "\n".join(txt)

    def collisions(self):
        J = self.J
        names = J["actuators"] + J["grail"]["objects"]
        others = J["fixed"] + J["grail"]["objects"]
        out = []
        for a in names:
            for b in others + [n for n in J["lift"]["objects"] if n not in J["flip"]["objects"]]:
                if a == b or frozenset((a, b)) in EXPECTED:
                    continue
                if a in J["lift"]["objects"] and b in J["lift"]["objects"] and not (a in J["flip"]["objects"]):
                    continue
                if self.on and (a in J["grail"]["objects"] or b in J["grail"]["objects"]) and \
                        (a in J["flip"]["objects"] or b in J["flip"]["objects"]):
                    continue
                if b == "ENV_TABLE" and a in J["grail"]["objects"]:
                    continue
                oa, ob = self.doc.getObject(a), self.doc.getObject(b)
                if oa is None or ob is None or not oa.Shape.BoundBox.intersect(ob.Shape.BoundBox):
                    continue
                try:
                    v = oa.Shape.common(ob.Shape).Volume
                except Exception:
                    v = -1
                if v > 0.5:
                    key = tuple(sorted((a, b)))
                    out.append((key, v))
        seen, lines = set(), []
        for k, v in sorted(out, key=lambda q: -q[1]):
            if k in seen:
                continue
            seen.add(k)
            lines.append("%s x %s : %.1f mm3" % (k[0], k[1], v))
        return "\n".join(lines) if lines else "No collision at this pose."


class Panel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.st = None
        lay = QtWidgets.QVBoxLayout(self)
        self.ver = QtWidgets.QComboBox()
        self.ver.addItems([v for v in ("v3", "v2", "v1") if os.path.exists(os.path.join(C.CAD, "joints_%s.json" % v))])
        self.ver.currentTextChanged.connect(self.load)
        lay.addWidget(QtWidgets.QLabel("Grail lift version"))
        lay.addWidget(self.ver)
        self.sl = {}
        for key in ("lift", "flip", "approach", "seq"):
            lab = QtWidgets.QLabel()
            s = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            s.valueChanged.connect(lambda val, k=key: self.moved(k, val))
            lay.addWidget(lab)
            lay.addWidget(s)
            self.sl[key] = (s, lab)
        row = QtWidgets.QHBoxLayout()
        self.mag = QtWidgets.QCheckBox("Magnet ON")
        self.mag.toggled.connect(self.magnet)
        self.play = QtWidgets.QPushButton("Play sequence")
        self.play.clicked.connect(self.toggle_play)
        rg = QtWidgets.QPushButton("Reset Grail")
        rg.clicked.connect(self.reset_grail)
        for w in (self.mag, self.play, rg):
            row.addWidget(w)
        lay.addLayout(row)
        cb = QtWidgets.QPushButton("Check collisions at this pose")
        cb.clicked.connect(self.check)
        lay.addWidget(cb)
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
        self.busy = False
        self.load(self.ver.currentText())

    # slider scales: lift and approach in 0.5 mm, flip in 0.5 deg, sequence in 0.05 s
    def load(self, v):
        if not v:
            return
        self.st = Study(v)
        J = self.st.J
        self.T = C.seq_duration(J)
        self.cfg = {"lift": (J["lift"]["min"], J["lift"]["max"], 0.5, J["lift"]["label"]),
                    "flip": (J["flip"]["min"], J["flip"]["max"], 0.5, J["flip"]["label"]),
                    "approach": (-60.0, 60.0, 0.5, "Grail approach (robot driving in), mm"),
                    "seq": (0.0, self.T, 0.05, "Sequence time (s)")}
        self.busy = True
        for k, (lo, hi, step, lab) in self.cfg.items():
            s, _ = self.sl[k]
            s.setRange(int(round(lo / step)), int(round(hi / step)))
        self.sync()
        self.busy = False
        self.refresh()

    def sync(self):
        st = self.st
        vals = {"lift": st.lift, "flip": st.ang, "approach": st.app}
        for k, val in vals.items():
            s, _ = self.sl[k]
            s.blockSignals(True)
            s.setValue(int(round(val / self.cfg[k][2])))
            s.blockSignals(False)
        self.mag.blockSignals(True)
        self.mag.setChecked(st.on)
        self.mag.blockSignals(False)

    def labels(self, label=""):
        st = self.st
        vals = {"lift": st.lift, "flip": st.ang, "approach": st.app,
                "seq": self.sl["seq"][0].value() * self.cfg["seq"][2]}
        for k, (s, lab) in self.sl.items():
            lab.setText("%s: %.1f" % (self.cfg[k][3], vals[k]))
        if label:
            self.sl["seq"][1].setText("%s: %.2f  -  %s" % (self.cfg["seq"][3], vals["seq"], label))

    def refresh(self, label=""):
        self.labels(label)
        self.info.setText(self.st.readouts())

    def moved(self, k, val):
        if self.busy or self.st is None:
            return
        x = val * self.cfg[k][2]
        if k == "seq":
            label = self.st.from_sequence(x)
            self.sync()
            self.refresh(label)
            return
        if k == "lift":
            self.st.lift = x
        elif k == "flip":
            self.st.ang = x
        elif k == "approach":
            self.st.approach(x)
            self.refresh()
            return
        self.st.apply()
        self.refresh()

    def magnet(self, on):
        self.st.magnet(on)
        self.refresh()

    def reset_grail(self):
        self.st.reset_grail()
        self.sync()
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
        if d.objectName() == "GrailLiftSliders":
            d.close()
            d.deleteLater()
    dock = QtWidgets.QDockWidget("Grail lift - motion study", mw)
    dock.setObjectName("GrailLiftSliders")
    dock.setWidget(Panel())
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    dock.show()
    return dock


_dock = show()
