# hub_d_zoom_gif.py - Central hub OPTION D: zoomed GIF of the two height guides, rendered from the FreeCAD solids.
#   left : TOP level    - parallelogram arm + drag link (rod 157 mm, 2 ball links) to the fixed anchor on the spine
#   right: BOTTOM level - parallelogram arm + 22 mm cam lever + 623ZZ roller under the fixed ramp
# Front unit only, hub lift at 14 (transfer height), ring swept -3 -> 90 -> -3 deg, stone held flat (no spin).
# With cd.BOTTOM_FIXED (2026-11-19) the bottom level has no guide any more: only the top panel is drawn.
# Every other part (robot, other arms, other unit) is hidden so the guide can be seen.
#
# Run (FreeCAD GUI needed; it closes itself at the end):
#   "<FreeCAD>/bin/FreeCAD.exe" mechanical/central-hub/option-d/fc/hub_d_zoom_gif.py
# Output: ../../simulations/central_hub/option_d_guides_zoom.gif (+ stills option_d_guides_zoom_start/end.png)
# On error: traceback in <temp>/hub_d_zoom_gif_error.txt
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import FreeCAD as App  # noqa: E402
import FreeCADGui as Gui  # noqa: E402
from PySide import QtCore  # noqa: E402

_src = open(os.path.join(HERE, "hub_d_fc.py"), encoding="utf-8").read()
_src = _src[:_src.rstrip().rfind("main()")]
F = {"__file__": os.path.join(HERE, "hub_d_fc.py"), "__name__": "hub_d_fc"}
exec(compile(_src, "hub_d_fc.py", "exec"), F)
cd, cc, np = F["cd"], F["cc"], F["np"]

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "simulations", "central_hub"))
L = 14.0                                    # hub lift during the transfer
W, H = 720, 620
CAPTION_H = 120
LEVELS = "T" if cd.BOTTOM_FIXED else "TB"
# (azimuth deg from +Y towards +X, rise, look-at point, visible height mm)
VIEWS = {"T": (-35.0, 0.45, (-35, 45, 255), 300), "B": (-60.0, -0.12, (-40, 30, 125), 240)}   # bottom: from slightly below
TITLE = {"T": "TOP level: drag link (rod hangs from a fixed anchor)",
         "B": "BOTTOM level: roller under a fixed ramp (cam)"}
LEGEND = {"T": [("rod 157 mm + 2 ball joints", (0.90, 0.15, 0.15)), ("fixed anchor on the spine", (0.75, 0.10, 0.65)),
                ("parallelogram arm", (0.20, 0.45, 0.85)), ("ring + N20 pinion", (0.85, 0.75, 0.20))],
          "B": [("lever 22 mm + 623ZZ roller", (0.90, 0.15, 0.15)), ("fixed ramp on the spine", (0.75, 0.10, 0.65)),
                ("parallelogram arm", (0.20, 0.45, 0.85)), ("ring + N20 pinion", (0.85, 0.75, 0.20))]}

BLUE, RED, MAG, YEL = (0.20, 0.45, 0.85), (0.90, 0.15, 0.15), (0.75, 0.10, 0.65), (0.85, 0.75, 0.20)
DARK, STONE = (0.30, 0.31, 0.34), (0.80, 0.65, 0.42)


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


def phis():
    go = list(np.arange(cc.PARK, 90.0, 2.0)) + [90.0]
    return [cc.PARK] * 6 + go + [90.0] * 10 + go[::-1] + [cc.PARK] * 4


def colour(name):
    if name.endswith(("rod", "ball stud", "cam lever", "roller")):
        return RED
    if name.endswith(("cup", "spin servo", "bearing housing")):
        return (0.2, 0.2, 0.2)
    return BLUE


class Scene:
    def __init__(self, doc):
        self.doc, self.objs = doc, {}

    def put(self, name, shape, col, transp=0):
        o = self.objs.get(name)
        if o is None:
            o = self.doc.addObject("Part::Feature", name.replace(" ", "_"))
            o.ViewObject.ShapeColor = col
            o.ViewObject.LineColor = tuple(c * 0.5 for c in col)
            o.ViewObject.Transparency = transp
            self.objs[name] = o
        o.Shape = shape
        return o

    def only(self, names):
        for n, o in self.objs.items():
            o.Visibility = n in names


def build(sc, lv, phi):
    """all parts of level lv (front unit) at ring angle phi; returns the names to show"""
    key = ("F", lv)
    names = []
    sc.put("spine", F["spine"](L), DARK, 55); names.append("spine")
    m, p = F["motor"](key, L)
    sc.put("motor " + lv, m, (0.15, 0.15, 0.15)); sc.put("pinion " + lv, p, YEL)
    sc.put("ring " + lv, F["ring"](key, phi, L), YEL, 20)
    names += ["motor " + lv, "pinion " + lv, "ring " + lv]
    if lv == "T":
        sc.put("anchor", F["anchor"]("F", L), MAG); names.append("anchor")
    else:
        sc.put("ramp", F["ramp"]("F", L), MAG); names.append("ramp")
    world, stone = F["arm"]("F", lv, phi, L, 0.0, True)
    for n, s in world.items():
        see_through = 55 if n.endswith(("post", "lug", "carrier")) else 0       # so the lever / stud inside show
        sc.put(n, s, colour(n), see_through); names.append(n)
    if stone is not None:
        sc.put("stone " + lv, stone, STONE, 85); names.append("stone " + lv)
    return names


def stone_z(lv, phi):
    lr, lt, ur, ut = cc.link_pts(lv, cc.alpha_at(lv, phi))
    return lt[2] + cc.CUP_DZ[lv]                     # hub frame, as in the README (add 14 for the lift)


def render():
    if "hub_d_zoom" in App.listDocuments():
        App.closeDocument("hub_d_zoom")
    doc = App.newDocument("hub_d_zoom")
    sc = Scene(doc)
    for lv in LEVELS:
        build(sc, lv, cc.PARK)
    doc.recompute()
    Gui.updateGui()
    view = Gui.getDocument(doc.Name).ActiveView
    try:
        view.setCameraType("Orthographic")
    except Exception:
        pass
    cams = {k: camera_string(*v) for k, v in VIEWS.items()}
    tmp = tempfile.mkdtemp(prefix="hub_d_zoom_")
    frames = phis()
    for i, phi in enumerate(frames):
        for lv in LEVELS:
            sc.only(build(sc, lv, phi))
            doc.recompute()
            view.setCamera(cams[lv])
            Gui.updateGui()
            view.saveImage(os.path.join(tmp, "f%03d_%s.png" % (i, lv)), W, H, "White")
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
    for i, phi in enumerate(frames):
        canvas = Image.new("RGB", (W * max(2, len(LEVELS)), H + CAPTION_H), (24, 28, 34))
        d = ImageDraw.Draw(canvas)
        for j, lv in enumerate(LEVELS):
            x0 = j * W
            canvas.paste(Image.open(os.path.join(tmp, "f%03d_%s.png" % (i, lv))).convert("RGB"), (x0, 0))
            d.text((x0 + 12, 10), TITLE[lv], font=f1, fill=(40, 40, 40))
            for k, (txt, col) in enumerate(LEGEND[lv]):
                y = 40 + k * 22
                d.rectangle((x0 + 14, y + 3, x0 + 28, y + 15), fill=tuple(int(c * 255) for c in col))
                d.text((x0 + 36, y), txt, font=f3, fill=(50, 50, 50))
            a = cc.alpha_at(lv, phi)
            d.text((x0 + 14, H + 12), "ring %5.1f deg   arm links %+5.1f deg   stone centre %5.1f mm (hub frame)"
                   % (phi, a, stone_z(lv, phi)), font=f2, fill=(225, 228, 232))
        d.line((W, 0, W, H + CAPTION_H), fill=(24, 28, 34), width=3)
        d.text((14, H + 44), "Option D central hub, front unit, hub lift at 14 mm. One N20 turns each ring; "
               "the fixed guide sets the height.", font=f2, fill=(120, 220, 140))
        d.text((14, H + 70), "Top: the rod length is fixed, so the stud must drop as the arm swings toward "
               "the anchor (275 -> 160).", font=f3, fill=(200, 204, 210))
        if cd.BOTTOM_FIXED:
            d.text((W + 14, 40), "BOTTOM level: fixed holder (2026-11-19)", font=f1, fill=(225, 228, 232))
            for k, txt in enumerate(("No ring, no motor, no guide: a bracket on a collar",
                                     "of the spine holds the bottom cup.",
                                     "The bottom stone is carried with the stack (walls)",
                                     "and left lying when tower mode starts,",
                                     "so each unit builds 2 towers (middle + top).")):
                d.text((W + 14, 80 + k * 24), txt, font=f2, fill=(200, 204, 210))
        else:
            d.text((14, H + 92), "Bottom: weight pushes the roller up under the ramp; the ramp goes down, the "
                   "lever tips, the arm rises (55 -> 160).", font=f3, fill=(200, 204, 210))
        imgs.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "option_d_guides_zoom.gif")
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=90, loop=0, optimize=True)
    imgs[0].convert("RGB").save(os.path.join(OUT, "option_d_guides_zoom_start.png"))
    imgs[len(frames) // 2].convert("RGB").save(os.path.join(OUT, "option_d_guides_zoom_end.png"))
    return path


def run():
    try:
        tmp, frames = render()
        path = make_gif(tmp, frames)
        shutil.rmtree(tmp, ignore_errors=True)
        App.Console.PrintMessage("GIF written: %s (%d frames)\n" % (path, len(frames)))
    except Exception:
        import traceback
        with open(os.path.join(tempfile.gettempdir(), "hub_d_zoom_gif_error.txt"), "w") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


os.makedirs(OUT, exist_ok=True)
QtCore.QTimer.singleShot(3000, run)
