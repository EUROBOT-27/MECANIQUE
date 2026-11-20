# hub_e_gif.py - GIF of central hub option E (doubled), rendered from the FreeCAD solids of fc/hub_e_fc.py.
# Sequence = fc/check_e.py (front unit builds its 3 towers while the rear holds its stack, then the rear), every
# STEP-th state. Every part is built once; each frame only moves them (placements): turrets turn, carriages slide and
# turn, cups spin, holders lift, pinions turn 2x the turret. The robot is drawn fixed: when it drives on, the towers
# it left move back.
# Run from mechanical/central-hub/option-e/ (GUI, closes itself):
#   "D:/FreeCad/bin/FreeCAD.exe" fc/hub_e_gif.py
# -> ../../simulations/central_hub/option_e_freecad.gif + stills option_e_freecad_*.png
import os
import sys
import math
import shutil
import tempfile
import traceback
import builtins
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
builtins.HUB_E_IMPORT_ONLY = True
import check_e as ce            # noqa: E402
import hub_e_fc as hf           # noqa: E402
V = App.Vector
OUT = os.path.join(ROOT, "..", "..", "simulations", "central_hub")
STEP = 3
W3, H3, WT = 760, 560, 440      # 3D view, top view widths, height
CAPTION_H = 84
ACTS = ["holder lift", "shaft Z F", "turn F", "spin F", "shaft Z R", "turn R", "spin R", "wheels"]


def placement_z(th):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th))


class Scene:
    def __init__(self, doc):
        self.doc, self.objs, self.base = doc, {}, {}

    def add(self, name, shape, ck, transp=0):
        o = self.doc.addObject("Part::Feature", "o%d" % len(self.objs))
        o.Label = name
        o.Shape = shape
        c = hf.COL.get(ck, (0.7, 0.7, 0.7))
        o.ViewObject.ShapeColor = c
        o.ViewObject.LineColor = tuple(x * 0.45 for x in c)
        o.ViewObject.Transparency = transp
        self.objs[name] = o
        self.base[name] = o.Placement.copy()     # a shape may carry its position as a placement: keep it
        return o


def build(doc):
    sc = Scene(doc)
    # fixed: robot, column, beacon, fixed drives (pinions move)
    for n, (g, s, ck) in hf.robot().items():
        sc.add(n, s, ck, 85 if ck == "envelope" else 0)       # base_330_js; JSUMO worst-case envelope see-through
    for u in "FR":
        for n, (g, s, ck) in hf.fixed_unit(u, 0.0).items():
            sc.add(n, s, ck)
        for n, (g, s, ck) in hf.turret(u, 0.0).items():
            sc.add(n, s, ck)
        for n, (g, s, ck) in hf.carriage(u, 0.0, 0.0, 0.0, None).items():
            sc.add(n, s, ck, 15 if ck == "cup" else 0)
        for n, (g, s, ck) in hf.holder(u, 0.0).items():
            sc.add(n, s, ck, 15 if ck == "cup" else 0)
        full = hf.state()
        for n, (g, s, ck) in hf.stones(full).items():
            if n.startswith("stone " + u):
                st0 = hf.state(L={"F": 0.0, "R": 0.0})
                sc.add(n, s, ck)
        sc.add("held " + u, hf.Part.makeBox(1, 1, 1), "held").ViewObject.Visibility = False
        for lv in "TMB":
            sc.add("tower %s%s" % (u, lv), hf.Part.makeBox(1, 1, 1), "tower").ViewObject.Visibility = False
    return sc


TURRET = ("bottom plate", "turn gear sector", "top plate", "608 bearing", "NEMA17", "T8 screw", "guide rod",
          "GT2 pulleys", "GT2 belt")
CARR = ("carriage", "T8 nut", "LM8UU", "spin MG996R")
SPIN = ("spin horn", "shaft cup")


def show(sc, st):
    O = sc.objs

    def put(n, pl):                              # frame motion on top of the part's own placement
        O[n].Placement = pl.multiply(sc.base[n])
    for u in "FR":
        th, zc, sp, L = st["th"][u], st["zc"][u], st["spin"][u], st["L"][u]
        pz = placement_z(th)
        for n in TURRET:
            put("%s %s" % (n, u), pz)
        pc = pz.multiply(App.Placement(V(0, 0, zc), App.Rotation()))
        for n in CARR:
            put("%s %s" % (n, u), pc)
        ur, _, _, _ = ce.frame(ce.UNITS[u]["phi0"])
        ps = pc.multiply(App.Placement(V(0, 0, 0), App.Rotation(V(-ur[0], -ur[1], 0), sp)))
        for n in SPIN:
            put("%s %s" % (n, u), ps)
        x0, y0 = ce.TURN[u]["shaft"]
        put("turn pinion " + u, App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), -2 * th), V(x0, y0, 0)))
        ph = App.Placement(V(0, 0, L), App.Rotation())
        for n, o in O.items():
            if n.startswith(("holder frame " + u, "holder cup " + u)):
                put(n, ph)
        for lv in "TMB":
            o = O.get("stone %s%s" % (u, lv))
            if o is not None:
                o.ViewObject.Visibility = lv in st["stack"][u]
                put("stone %s%s" % (u, lv), ph)
        h = O["held " + u]
        if st["held"][u]:
            b = ce.stone_box("h", ce.UNITS[u]["phi0"] + th, zc, sp)
            h.Shape = hf.obox(b)
            h.ViewObject.Visibility = True
        else:
            h.ViewObject.Visibility = False
    present = {}
    for lv, u, y in st["towers"]:
        present["tower %s%s" % (u, lv)] = y
    for u in "FR":
        for lv in "TMB":
            n = "tower %s%s" % (u, lv)
            o = O[n]
            if n in present:
                b = ce.stone_box("t", ce.UNITS[u]["phi0"] + 90, ce.Z_SET, 90.0)
                b.c = b.c + [0, present[n], 0]
                o.Shape = hf.obox(b)
                o.ViewObject.Visibility = True
            else:
                o.ViewObject.Visibility = False


# (azimuth deg from +Y towards +X, rise, look-at point, visible height mm); fixed cameras as in option D,
# framed toward the rear so the towers the robot leaves stay in view
VIEWS = {"3d": (-40.0, 0.6, (-40, -180, 150), 900), "top": (180.0, 100.0, (0, -260, 150), 1000)}


def camera_string(az_deg, el, target, height):
    a = math.radians(az_deg)
    z = V(math.sin(a), math.cos(a), el).normalize()
    x = V(0, 0, 1).cross(z).normalize()
    y = z.cross(x)
    m = App.Matrix(x.x, y.x, z.x, 0, x.y, y.y, z.y, 0, x.z, y.z, z.z, 0, 0, 0, 0, 1)
    r = App.Rotation(m)
    ax, ang = r.Axis, r.Angle
    pos = V(*target) + z * 3000
    return ("#Inventor V2.1 ascii\n\nOrthographicCamera {\n viewportMapping ADJUST_CAMERA\n"
            " position %f %f %f\n orientation %f %f %f %f\n nearDistance 10\n farDistance 8000\n"
            " aspectRatio 1\n focalDistance 3000\n height %f\n}\n" % (pos.x, pos.y, pos.z, ax.x, ax.y, ax.z, ang, height))


def render():
    S = ce.sequence()
    keep = S[::STEP]
    if keep[-1] is not S[-1]:
        keep.append(S[-1])
    doc = App.newDocument("hub_e_gif")
    sc = build(doc)
    view = Gui.getDocument(doc.Name).activeView()
    view.setCameraType("Orthographic")
    Gui.runCommand("Std_DrawStyle", 0)
    show(sc, keep[0])
    doc.recompute()
    cams = {k: camera_string(*v) for k, v in VIEWS.items()}
    tmp = tempfile.mkdtemp(prefix="hub_e_gif_")
    for i, st in enumerate(keep):
        show(sc, st)
        doc.recompute()
        view.setCamera(cams["3d"]); Gui.updateGui()
        view.saveImage(os.path.join(tmp, "f%03d_3d.png" % i), W3, H3, "White")
        view.setCamera(cams["top"]); Gui.updateGui()
        view.saveImage(os.path.join(tmp, "f%03d_top.png" % i), WT, H3, "White")
    App.closeDocument(doc.Name)
    return tmp, keep


def make_gif(tmp, frames):
    from PIL import Image, ImageDraw, ImageFont

    def font(sz, bold=False):
        for name in (("arialbd.ttf" if bold else "arial.ttf"), "DejaVuSans.ttf"):
            try:
                return ImageFont.truetype(name, sz)
            except Exception:
                pass
        return ImageFont.load_default()

    f1, f2, f3 = font(17, True), font(15), font(12)
    imgs = []
    for i, st in enumerate(frames):
        canvas = Image.new("RGB", (W3 + WT, H3 + CAPTION_H), (24, 28, 34))
        canvas.paste(Image.open(os.path.join(tmp, "f%03d_3d.png" % i)).convert("RGB"), (0, 0))
        canvas.paste(Image.open(os.path.join(tmp, "f%03d_top.png" % i)).convert("RGB"), (W3, 0))
        d = ImageDraw.Draw(canvas)
        d.line([(W3, 0), (W3, H3)], fill=(200, 200, 200), width=2)
        d.text((10, 8), "3D, from the front-left", font=f3, fill=(90, 90, 90))
        d.text((W3 + 10, 8), "top view (front = up, robot's left = left)", font=f3, fill=(90, 90, 90))
        d.text((W3 + 10, 26), "robot drawn fixed: towers move back as it drives on", font=f3, fill=(110, 110, 110))
        d.text((12, H3 + 6), "Central hub option E (FreeCAD model): per unit 1 turret + 1 shaft (lift, turn, spin) "
               "+ holder cups; front -> left, rear -> right", font=f1, fill=(120, 220, 140))
        d.text((12, H3 + 32), st["label"], font=f2, fill=(225, 228, 232))
        x = 12
        for a in ACTS:
            on = a in st["act"]
            w = d.textlength(a, font=f3) + 12
            d.rectangle([x, H3 + 58, x + w, H3 + 76], fill=(194, 24, 91) if on else (60, 64, 72))
            d.text((x + 6, H3 + 60), a, font=f3, fill=(255, 255, 255) if on else (170, 170, 170))
            x += w + 6
        vac = "vacuum: front " + ("on" if st["vac"]["F"] else "off") + ", rear " + ("on" if st["vac"]["R"] else "off")
        d.text((x + 10, H3 + 60), vac, font=f3, fill=(170, 170, 170))
        imgs.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "option_e_freecad.gif")
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=90, loop=0, optimize=True)
    n = len(imgs)
    picks = {"home": 0}
    for tag, key in (("transfer", "front top: turret turns"), ("spin", "front top: spin"),
                     ("rear_build", "rear middle: spin")):
        j = next((k for k, s in enumerate(frames) if s["label"].startswith(key)), None)
        if j is not None:
            picks[tag] = min(j + 2, n - 1)
    for tag, idx in picks.items():
        imgs[idx].convert("RGB").save(os.path.join(OUT, "option_e_freecad_%s.png" % tag))
    return path


def run():
    try:
        tmp, frames = render()
        path = make_gif(tmp, frames)
        shutil.rmtree(tmp, ignore_errors=True)
        App.Console.PrintMessage("GIF written: %s (%d frames)\n" % (path, len(frames)))
    except Exception:
        with open(os.path.join(ROOT, "hub_e_gif_error.txt"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(2500, run)
