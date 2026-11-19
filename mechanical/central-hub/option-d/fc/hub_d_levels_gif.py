# hub_d_levels_gif.py - Central hub OPTION D: zoomed GIF of the 3 levels of the FRONT unit doing the real build
# sequence (fc/check_d.py run B, front part only): unpinch, then middle -> bottom -> top, each: transfer, spin, hub
# lift sets the tower on the table, vent, ring back. Rear unit, robot and rear stones hidden.
# With cd.BOTTOM_FIXED (2026-11-19): the bottom stone sits in a fixed holder and is left lying first; middle -> top.
# One colour per level so each arm can be followed: top = red, middle = green, bottom = blue.
#
# Run (FreeCAD GUI needed; it closes itself at the end):
#   "<FreeCAD>/bin/FreeCAD.exe" mechanical/central-hub/option-d/fc/hub_d_levels_gif.py
# Output: ../../simulations/central_hub/option_d_levels.gif
# On error: traceback in <temp>/hub_d_levels_gif_error.txt
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import FreeCAD as App  # noqa: E402
import FreeCADGui as Gui  # noqa: E402
import Part  # noqa: E402
from PySide import QtCore  # noqa: E402

_src = open(os.path.join(HERE, "hub_d_fc.py"), encoding="utf-8").read()
_src = _src[:_src.rstrip().rfind("main()")]
F = {"__file__": os.path.join(HERE, "hub_d_fc.py"), "__name__": "hub_d_fc"}
exec(compile(_src, "hub_d_fc.py", "exec"), F)
cd, cc, np = F["cd"], F["cc"], F["np"]

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "simulations", "central_hub"))
STEP = 2
W, H = 680, 600
CAPTION_H = 92
VIEWS = {"iso": (-40.0, 0.40, (-90, 60, 165), 470), "front": (0.0, 0.04, (-90, 0, 165), 420)}
VIEW_LABELS = {"iso": "3D view, front unit only (towers go to the robot's left)",
               "front": "Seen from the front: the height of each stone"}
LCOL = {"T": (0.88, 0.20, 0.20), "M": (0.20, 0.65, 0.30), "B": (0.20, 0.45, 0.85)}
LNAME = {"T": "top: drag link", "M": "middle: rigid arm",
         "B": "bottom: fixed holder (no motor)" if cd.BOTTOM_FIXED else "bottom: roller + ramp"}
DARK, GUIDE, STONE, TOWER = (0.30, 0.31, 0.34), (0.75, 0.10, 0.65), (0.80, 0.65, 0.42), (0.66, 0.52, 0.33)


def camera_string(az_deg, el, target, height):
    a = math.radians(az_deg)
    z = App.Vector(math.sin(a), math.cos(a), el).normalize()
    x = App.Vector(0, 0, 1).cross(z).normalize()
    y = z.cross(x)
    m = App.Matrix(x.x, y.x, z.x, 0, x.y, y.y, z.y, 0, x.z, y.z, z.z, 0, 0, 0, 0, 1)
    r = App.Rotation(m)
    ax, ang = r.Axis, r.Angle
    pos = App.Vector(*target) + z * 3000
    return ("#Inventor V2.1 ascii\n\nOrthographicCamera {\n viewportMapping ADJUST_CAMERA\n"
            " position %f %f %f\n orientation %f %f %f %f\n nearDistance 10\n farDistance 8000\n"
            " aspectRatio 1\n focalDistance 3000\n height %f\n}\n" % (pos.x, pos.y, pos.z, ax.x, ax.y, ax.z, ang, height))


def states():
    """front part of run B: stop once the rear unit starts moving"""
    S = cd.seq_front_only()
    out = []
    for st in S:
        if any(abs(st["phi"][("R", lv)]) > 0.01 for lv in "BMT") or any(st["tower"][("R", lv)] for lv in "BMT"):
            break
        out.append(st)
    keep = out[::STEP]
    if keep[-1] is not out[-1]:
        keep.append(out[-1])
    return keep


class Scene:
    def __init__(self, doc):
        self.doc, self.objs = doc, {}

    def put(self, name, shape, col, transp=0, placement=None):
        o = self.objs.get(name)
        if o is None:
            o = self.doc.addObject("Part::Feature", name.replace(" ", "_"))
            o.ViewObject.ShapeColor = col
            o.ViewObject.LineColor = tuple(c * 0.5 for c in col)
            o.ViewObject.Transparency = transp
            self.objs[name] = o
        if shape is not None:
            o.Shape = shape
        if placement is not None:
            o.Placement = placement
        o.Visibility = True
        return o


def place(Rm=None, L=0.0):
    Rm = np.eye(3) if Rm is None else np.asarray(Rm, float)
    return App.Placement(F["mat"](Rm, (0, 0, L)))


def build_static(sc):
    sc.put("table", Part.makeBox(700, 500, 2, App.Vector(-450, -250, -2)), (0.93, 0.93, 0.90))
    sc.put("spine", F["spine"](0.0), DARK, 55)
    for lv in cd.TRANSFER:
        key = ("F", lv)
        m, p = F["motor"](key, 0.0)
        sc.put("motor F" + lv, m, (0.15, 0.15, 0.15)); sc.put("pinion F" + lv, p, (0.85, 0.75, 0.2))
        back = np.asarray(cc.W(cd.phi_abs("F", 0.0)), float).T
        sc.put("ring F" + lv, F["moved"](F["ring"](key, 0.0, 0.0), back), LCOL[lv], 15)
    if cd.BOTTOM_FIXED:
        sc.put("bottom collar", F["collar"](0.0), LCOL["B"], 15)
    else:
        sc.put("ramp FB", F["ramp"]("F", 0.0), GUIDE)
    sc.put("anchor FT", F["anchor"]("F", 0.0), GUIDE)


def show(sc, st):
    L = st["L"]
    for n in ["spine", "bottom collar" if cd.BOTTOM_FIXED else "ramp FB", "anchor FT"] + \
             ["%s F%s" % (w, lv) for lv in cd.TRANSFER for w in ("motor", "pinion")]:
        sc.objs[n].Placement = place(None, L)
    seen = set()
    for lv in "BMT":
        k = ("F", lv)
        if lv in cd.TRANSFER:
            sc.objs["ring F" + lv].Placement = place(cc.W(cd.phi_abs("F", st["phi"][k])), L)
        world, stone = F["arm"]("F", lv, st["phi"][k], L, st["spin"][k], st["held"][k])
        for n, s in world.items():
            col = (0.2, 0.2, 0.2) if n.endswith(("cup", "spin servo", "bearing housing", "cup mount")) else LCOL[lv]
            if n.endswith(("rod", "roller", "cam lever")):
                col = GUIDE
            sc.put(n, s, col, 40 if n.endswith(("post", "lug")) else 0)
            seen.add(n)
        if stone is not None:
            n = "F%s stone" % lv
            sc.put(n, stone, STONE, 55); seen.add(n)
        if st["tower"][k]:
            n = "F%s tower" % lv
            if lv == "B" and cd.BOTTOM_FIXED:              # bottom stone left lying on the table
                sc.put(n, F["arm"]("F", lv, 0.0, 0.0, 0.0, True)[1], TOWER, 45); seen.add(n)
            else:
                sc.put(n, F["arm"]("F", lv, 90.0, 0.0, 90.0, True)[1], TOWER, 45); seen.add(n)
    for n, o in sc.objs.items():
        if n.endswith(("stone", "tower")) and n not in seen:
            o.Visibility = False


def render():
    if "hub_d_levels" in App.listDocuments():
        App.closeDocument("hub_d_levels")
    doc = App.newDocument("hub_d_levels")
    sc = Scene(doc)
    build_static(sc)
    frames = states()
    show(sc, frames[0]); doc.recompute()
    Gui.updateGui()
    view = Gui.getDocument(doc.Name).ActiveView
    try:
        view.setCameraType("Orthographic")
    except Exception:
        pass
    cams = {k: camera_string(*v) for k, v in VIEWS.items()}
    tmp = tempfile.mkdtemp(prefix="hub_d_levels_")
    for i, st in enumerate(frames):
        show(sc, st)
        doc.recompute()
        for key in VIEWS:
            view.setCamera(cams[key])
            Gui.updateGui()
            view.saveImage(os.path.join(tmp, "f%03d_%s.png" % (i, key)), W, H, "White")
    App.closeDocument(doc.Name)
    return tmp, frames


def make_gif(tmp, frames):
    from PIL import Image, ImageDraw, ImageFont

    def font(sz, bold=False):
        for name in (("arialbd.ttf" if bold else "arial.ttf"), "DejaVuSans.ttf"):
            try:
                return ImageFont.truetype(name, sz)
            except Exception:
                pass
        return ImageFont.load_default()

    f1, f2, f3 = font(18, True), font(15), font(14)
    imgs = []
    for i, st in enumerate(frames):
        canvas = Image.new("RGB", (W * len(VIEWS), H + CAPTION_H), (24, 28, 34))
        for j, key in enumerate(VIEWS):
            canvas.paste(Image.open(os.path.join(tmp, "f%03d_%s.png" % (i, key))).convert("RGB"), (j * W, 0))
        d = ImageDraw.Draw(canvas)
        for j, key in enumerate(VIEWS):
            d.text((j * W + 10, 8), VIEW_LABELS[key], font=f2, fill=(70, 70, 70))
        for k, lv in enumerate("TMB"):
            y = 34 + k * 21
            d.rectangle((14, y + 3, 28, y + 15), fill=tuple(int(c * 255) for c in LCOL[lv]))
            ring = ("   ring %5.1f deg" % st["phi"][("F", lv)]) if lv in cd.TRANSFER else ""
            d.text((36, y), LNAME[lv] + ring, font=f3, fill=(50, 50, 50))
        y = 34 + 3 * 21
        d.rectangle((14, y + 3, 28, y + 15), fill=tuple(int(c * 255) for c in GUIDE))
        d.text((36, y), "fixed guides (rod, anchor)" if cd.BOTTOM_FIXED else "fixed guides (rod, anchor, ramp, roller)",
               font=f3, fill=(50, 50, 50))
        d.text((14, H + 8), "Central hub option D, front unit: " + ("bottom left lying, middle -> top" if cd.BOTTOM_FIXED
               else "middle -> bottom -> top") + " (FreeCAD model)", font=f1,
               fill=(120, 220, 140))
        d.text((14, H + 36), st["label"], font=f2, fill=(225, 228, 232))
        d.text((14, H + 62), "hub lift %4.1f mm" % st["L"], font=f3, fill=(200, 204, 210))
        imgs.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "option_d_levels.gif")
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=80, loop=0, optimize=True)
    n = len(imgs)
    for tag, idx in (("a", n // 6), ("b", n // 2), ("c", 5 * n // 6)):
        imgs[idx].convert("RGB").save(os.path.join(OUT, "option_d_levels_%s.png" % tag))
    return path


def run():
    try:
        tmp, frames = render()
        path = make_gif(tmp, frames)
        shutil.rmtree(tmp, ignore_errors=True)
        App.Console.PrintMessage("GIF written: %s (%d frames)\n" % (path, len(frames)))
    except Exception:
        import traceback
        with open(os.path.join(tempfile.gettempdir(), "hub_d_levels_gif_error.txt"), "w") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


os.makedirs(OUT, exist_ok=True)
QtCore.QTimer.singleShot(3000, run)
