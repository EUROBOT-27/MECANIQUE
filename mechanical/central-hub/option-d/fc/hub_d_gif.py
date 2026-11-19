# hub_d_gif.py - Central hub OPTION D: GIF rendered from the FreeCAD model (real solids, not the box check).
# Uses the part geometry of fc/hub_d_fc.py and the build sequence of fc/check_d.py (run B: the front unit builds its
# 3 towers while the rear unit holds its stack, then the rear unit builds), so the GIF, the box check and the FCStd
# poses all agree.
#
# Run (FreeCAD GUI needed for the renders; it closes itself at the end):
#   "<FreeCAD>/bin/FreeCAD.exe" mechanical/central-hub/option-d/fc/hub_d_gif.py
# Output: ../../simulations/central_hub/option_d_freecad.gif (+ 4 stills option_d_freecad_*.png)
# On error: traceback in <temp>/hub_d_gif_error.txt
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

# hub_d_fc.py runs main() when loaded: take its functions without running it
_src = open(os.path.join(HERE, "hub_d_fc.py"), encoding="utf-8").read()
_src = _src[:_src.rstrip().rfind("main()")]
F = {"__file__": os.path.join(HERE, "hub_d_fc.py"), "__name__": "hub_d_fc"}
exec(compile(_src, "hub_d_fc.py", "exec"), F)
cd, cc, np = F["cd"], F["cc"], F["np"]

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "simulations", "central_hub"))
STEP = 4                                    # keep 1 state in STEP (806 states -> ~200 frames)
W, H = 640, 520
CAPTION_H = 64
# (azimuth deg from +Y towards +X, rise, look-at point, visible height mm)
VIEWS = {"iso": (-40.0, 0.6, (-40, 0, 150), 760), "top": (180.0, 100.0, (0, 0, 150), 640)}
VIEW_LABELS = {"iso": "3D view (front unit's towers on the robot's left)",
               "top": "Top view (front up, robot's left = left)"}

GREY, DARK = (0.72, 0.72, 0.74), (0.30, 0.31, 0.34)
UCOL = {"F": (0.20, 0.45, 0.85), "R": (0.90, 0.50, 0.15)}
STONE, TOWER = (0.80, 0.65, 0.42), (0.66, 0.52, 0.33)


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
    S = cd.seq_front_only()
    keep = S[::STEP]
    if keep[-1] is not S[-1]:
        keep.append(S[-1])
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


def build_static(sc):
    """parts that never change shape: robot, table, 350 line, spine / motors / ramps / anchors (move with L only),
    rings (turn with phi + move with L): built once, then moved with Placement"""
    for k, s in F["robot"]().items():
        sc.put("robot " + k, s, GREY, 0)
    sc.put("table", Part.makeBox(900, 700, 2, App.Vector(-450, -350, -2)), (0.93, 0.93, 0.90))
    sc.put("spine", F["spine"](0.0), DARK, 0)
    for key in cd.RING_Z:
        m, p = F["motor"](key, 0.0)
        sc.put("motor %s%s" % key, m, (0.15, 0.15, 0.15))
        sc.put("pinion %s%s" % key, p, (0.85, 0.75, 0.2))
        rz0, rz1 = cd.RING_Z[key]
        ring0 = F["ring"](key, 0.0, 0.0)
        # bring it back to its own frame (phi_abs(u, 0) undone) so a Placement can turn it to any phi
        back = np.asarray(cc.W(cd.phi_abs(key[0], 0.0)), float).T
        sc.put("ring %s%s" % key, F["moved"](ring0, back), UCOL[key[0]])
    for u in "FR":
        sc.put("ramp %sB" % u, F["ramp"](u, 0.0), DARK)
        sc.put("anchor %sT" % u, F["anchor"](u, 0.0), DARK)


def place(Rm=None, L=0.0):
    Rm = np.eye(3) if Rm is None else np.asarray(Rm, float)
    return App.Placement(F["mat"](Rm, (0, 0, L)))


def show(sc, st):
    L = st["L"]
    lift = place(None, L)
    for n in ["spine", "ramp FB", "ramp RB", "anchor FT", "anchor RT"] + \
             ["%s %s%s" % (w, *k) for k in cd.RING_Z for w in ("motor", "pinion")]:
        sc.objs[n].Placement = lift
    for key in cd.RING_Z:
        sc.objs["ring %s%s" % key].Placement = place(cc.W(cd.phi_abs(key[0], st["phi"][key])), L)
    seen = set()
    for u in "FR":
        for lv in "BMT":
            k = (u, lv)
            world, stone = F["arm"](u, lv, st["phi"][k], L, st["spin"][k], st["held"][k])
            for n, s in world.items():
                sc.put(n, s, UCOL[u] if not n.endswith(("cup", "spin servo")) else (0.2, 0.2, 0.2))
                seen.add(n)
            if stone is not None:
                n = "%s%s stone" % k
                sc.put(n, stone, STONE, 60); seen.add(n)
            if st["tower"][k]:
                n = "%s%s tower" % k
                sc.put(n, F["arm"](u, lv, 90.0, 0.0, 90.0, True)[1], TOWER, 40); seen.add(n)
    for n, o in sc.objs.items():
        if (n.endswith(("stone", "tower"))) and n not in seen:
            o.Visibility = False


def render():
    if "hub_d_gif" in App.listDocuments():
        App.closeDocument("hub_d_gif")
    doc = App.newDocument("hub_d_gif")
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
    tmp = tempfile.mkdtemp(prefix="hub_d_gif_")
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

    f1, f2 = font(19, True), font(15)
    imgs = []
    for i, st in enumerate(frames):
        canvas = Image.new("RGB", (W * len(VIEWS), H + CAPTION_H), (24, 28, 34))
        for j, key in enumerate(VIEWS):
            canvas.paste(Image.open(os.path.join(tmp, "f%03d_%s.png" % (i, key))).convert("RGB"), (j * W, 0))
        d = ImageDraw.Draw(canvas)
        for j, key in enumerate(VIEWS):
            d.text((j * W + 10, 8), VIEW_LABELS[key], font=f2, fill=(90, 90, 90))
        d.text((14, H + 8), "Central hub option D (FreeCAD model) - one ring + one N20 per stone", font=f1,
               fill=(120, 220, 140))
        d.text((14, H + 36), st["label"], font=f2, fill=(225, 228, 232))
        imgs.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "option_d_freecad.gif")
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=80, loop=0, optimize=True)
    n = len(imgs)
    for tag, idx in (("home", 0), ("transfer", n // 10), ("spin", n // 5), ("rear_build", 2 * n // 3)):
        imgs[idx].convert("RGB").save(os.path.join(OUT, "option_d_freecad_%s.png" % tag))
    return path


def run():
    try:
        tmp, frames = render()
        path = make_gif(tmp, frames)
        shutil.rmtree(tmp, ignore_errors=True)
        App.Console.PrintMessage("GIF written: %s (%d frames)\n" % (path, len(frames)))
    except Exception:
        import traceback
        with open(os.path.join(tempfile.gettempdir(), "hub_d_gif_error.txt"), "w") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


os.makedirs(OUT, exist_ok=True)
QtCore.QTimer.singleShot(3000, run)
