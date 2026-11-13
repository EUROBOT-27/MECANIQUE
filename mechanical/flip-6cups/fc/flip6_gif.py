# flip6_gif.py - animation of the 6-cup flip, both cases, as a GIF (FreeCAD GUI needed for the renders).
#
#   freecad flip6_gif.py      (run from this folder or with the full path; FreeCAD closes itself at the end)
#
# Case A: 3 stones held from the middle (2 cups per stone) -> flip 90 deg -> drop 8.8 mm -> fingers push -> return.
# Case B: 6 stones (2 stacks end to end), 3 cups per stack, held off-centre -> flip locked, the robot carries them.
# Output: ../../simulations/flip_6cups/flip6_cases.gif (+ frames in a temp folder)

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

import flip6_fc as F  # noqa: E402
import flip6_params as P  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "simulations", "flip_6cups"))
W, H = 640, 540
CAPTION_H = 74
# (azimuth deg, rise, look-at point, visible height mm) of each camera
VIEWS = {"iso": (35.0, 0.55, (0, 110, 215), 760), "front": (0.0, 0.0, (0, 150, 235), 700)}
VIEW_LABELS = {"iso": "3D view (stones side)", "front": "Front view: four-bar behind the plate (stones see-through)"}


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def camera_string(az_deg, el, target, height):
    """Orthographic camera (Inventor string, no animation) on the stones side (+Y), az_deg to the right,
    el = rise (0 = level), looking at target, `height` mm of scene visible vertically."""
    a = math.radians(az_deg)
    z = App.Vector(math.sin(a), math.cos(a), el).normalize()   # camera +Z points back towards the eye
    x = App.Vector(0, 0, 1).cross(z).normalize()
    y = z.cross(x)
    m = App.Matrix(x.x, y.x, z.x, 0, x.y, y.y, z.y, 0, x.z, y.z, z.z, 0, 0, 0, 0, 1)
    r = App.Rotation(m)
    ax, ang = r.Axis, r.Angle
    pos = App.Vector(*target) + z * 3000
    return ("#Inventor V2.1 ascii\n\nOrthographicCamera {\n viewportMapping ADJUST_CAMERA\n"
            " position %f %f %f\n orientation %f %f %f %f\n nearDistance 10\n farDistance 8000\n"
            " aspectRatio 1\n focalDistance 3000\n height %f\n}\n" % (pos.x, pos.y, pos.z, ax.x, ax.y, ax.z, ang, height))


def script():
    """List of frames: dict(s, n_stacks, finger, released, drop, push, az, caption)."""
    fr = []
    A = "Case A - 3 stones held FROM THE MIDDLE (2 cups per stone): flip allowed"
    B = "Case B - 6 stones: cups 1-3 hold the left stack, cups 4-6 the right stack, OFF-CENTRE: flip locked"

    def add(n, **k):
        for i in range(n):
            d = dict(s=0.0, n_stacks=1, finger=0.0, released=False, drop=0.0, push=0.0, az=0.0, caption=A, sub="")
            d.update({kk: (vv(i / max(n - 1, 1)) if callable(vv) else vv) for kk, vv in k.items()})
            fr.append(d)

    add(10, sub="Stack of 3, 6 DP-S30 cups (1 pump each): each stone held at its quarter points (u = +/-80)")
    add(40, s=lambda t: ease(t), sub="JGB37-520 gear motor direct on the crank, four-bar: stones turn 90 deg, > 7 mm off the table")
    add(6, s=1.0, sub="Stones upright, 8.8 mm above the table")
    add(5, s=1.0, released=True, drop=lambda t: P.END_GAP * t * t, sub="6 pumps stop, 6 vent valves open: the stones drop 8.8 mm")
    add(10, s=1.0, released=True, drop=P.END_GAP, finger=lambda t: 90 * ease(t),
        push=lambda t: F.EJECT_PUSH * ease(t), sub="3 x MG90S fingers push the stones 19.5 mm off the cups")
    add(8, s=1.0, released=True, drop=P.END_GAP, push=F.EJECT_PUSH, finger=lambda t: 90 * (1 - ease(t)),
        sub="Fingers fold back")
    add(30, s=lambda t: 1 - ease(t), released=True, drop=P.END_GAP, push=F.EJECT_PUSH,
        sub="Plate returns empty - 3 stones standing")
    add(8, released=True, drop=P.END_GAP, push=F.EJECT_PUSH, sub="Plate returns empty - 3 stones standing")
    add(22, n_stacks=2, caption=B, sub="2 quarry stacks end to end (650 mm): each stone held 85 mm off its middle")
    add(22, n_stacks=2, caption=B, sub="No flip with 6 stones: firmware allows FLIP only in the 3-stones-centred mode")
    add(22, n_stacks=2, caption=B, sub="Carried as two walls (330 mm high), released stack by stack (cups 1-3, then 4-6)")
    return fr


def render():
    if "flip6_gif" in App.listDocuments():
        App.closeDocument("flip6_gif")
    doc = App.newDocument("flip6_gif")
    objs = F.build(doc, 1, 0.0)
    table = objs["table"][0]
    table.Shape = F.box(-400, 400, -150, 420, -2, 0)
    for n, (o, k) in objs.items():
        if n.startswith("Stone"):
            o.ViewObject.Transparency = 55
    objs["Plate"][0].ViewObject.Transparency = 25
    doc.recompute()
    Gui.updateGui()
    gdoc = Gui.getDocument(doc.Name)
    view = gdoc.ActiveView
    try:
        view.setCameraType("Orthographic")
    except Exception:
        pass
    cams = {k: camera_string(*v) for k, v in VIEWS.items()}

    tmp = tempfile.mkdtemp(prefix="flip6_")
    frames = script()
    cur_stacks = None
    upright = F.placements(1.0)["plate"]
    for i, f in enumerate(frames):
        if f["n_stacks"] != cur_stacks:
            F.set_stones(objs, f["n_stacks"])
            cur_stacks = f["n_stacks"]
        for k in range(3):                     # new finger shape first: assigning a Shape resets the Placement
            o = objs["Finger_%d" % (k + 1)][0]
            o.Shape = F.finger_local(k, f["finger"])
        F.pose(objs, f["s"])
        if f["released"]:
            moved = App.Placement(App.Vector(0, f["push"], -f["drop"]), App.Rotation())
            for n in F.stone_names(1):
                objs[n][0].Placement = moved.multiply(upright)
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

    f1, f2 = font(19, True), font(16)
    imgs = []
    for i, f in enumerate(frames):
        canvas = Image.new("RGB", (W * len(VIEWS), H + CAPTION_H), (24, 28, 34))
        for j, key in enumerate(VIEWS):
            canvas.paste(Image.open(os.path.join(tmp, "f%03d_%s.png" % (i, key))).convert("RGB"), (j * W, 0))
        d = ImageDraw.Draw(canvas)
        for j, key in enumerate(VIEWS):
            d.text((j * W + 10, 8), VIEW_LABELS[key], font=f2, fill=(90, 90, 90))
        col = (120, 220, 140) if f["n_stacks"] == 1 else (255, 170, 90)
        d.text((14, H + 10), f["caption"], font=f1, fill=col)
        d.text((14, H + 42), f["sub"], font=f2, fill=(225, 228, 232))
        imgs.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "flip6_cases.gif")
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=70, loop=0, optimize=True)
    # stills for the README
    for tag, idx in (("caseA_start", 0), ("caseA_mid", 30), ("caseA_upright", 52), ("caseB", len(frames) - 40)):
        imgs[idx].convert("RGB").save(os.path.join(OUT, "flip6_%s.png" % tag))
    return path


def run():
    try:
        tmp, frames = render()
        path = make_gif(tmp, frames)
        shutil.rmtree(tmp, ignore_errors=True)
        App.Console.PrintMessage("GIF written: %s (%d frames)\n" % (path, len(frames)))
    except Exception:
        import traceback
        with open(os.path.join(tempfile.gettempdir(), "flip6_gif_error.txt"), "w") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


os.makedirs(OUT, exist_ok=True)
QtCore.QTimer.singleShot(3000, run)
