# flipper_gif.py - colour GIF of the Flipper cycle, rendered from the real solids of CAD_FC/FLIPPER_B330.FCStd
# (Seif 2026-11-20: after the static + motion checks). Same kinematics as fc/flipper_fc.py and fc/flipper_motion_check.py
# (numbers read from the report): pick -> lift (the pinion turns on the rack) -> flip 180 at the top -> lower onto the
# Grail deck -> magnet off, lower 6 (stowed) -> way back without the Grail: up, flip back, down to the pick.
# Views: 3D from the front-right + side view along y (the flip plane). The 350 limit sheet shows in the side view only.
#
# Run (FreeCAD GUI needed; it closes itself), from mechanical/Grail_v2, after fc/flipper_fc.py:
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/flipper_gif.py
# Output: ../simulations/grail_lift/flipper_cycle.gif + stills flipper_cycle_*.png
# Frames go to claude-workspace/tmp/flipper_gif (deleted at the end). On error: CAD_FC/flipper_gif_error.txt
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import FreeCAD as App  # noqa: E402
import FreeCADGui as Gui  # noqa: E402
from PySide import QtCore  # noqa: E402

import common as C  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "mechanical", "simulations", "grail_lift")
TMP = os.path.join(ROOT, "claude-workspace", "tmp", "flipper_gif")
W, H, CAPTION_H = 600, 560, 64
# (azimuth deg from +Y towards +X, rise, look-at point, visible height mm)
VIEWS = {"iso": (135.0, 0.55, (120, 0, 190), 470), "side": (180.0, 0.0, (125, 0, 205), 440)}
VIEW_LABELS = {"iso": "3D view (from the front-right)", "side": "Side view (flip plane), red line = 350 limit"}
LIFT_STEP, FLIP_STEP, BACK_FLIP_STEP = 4.0, 5.0, 10.0
ARM_G = ("_3_ARM_pick_pose", "_8c_SCREWS_arm")
LIFT_G = ("_2_CARRIAGE_pick_pose", "_8b_SCREWS_carriage")
GRAIL_G = ("_4_GRAIL_pick",)
SPIN = ("PINION_v2", "INSERT_M3_PINION", "SCR_M3x6_SET_PINION")


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


def numbers():
    rep = open(os.path.join(C.CAD, "FLIPPER_B330_report.txt"), encoding="utf-8", errors="replace").read()
    m = re.search(r"Flip axis x ([\d.]+); LZ ([\d.]+); pivot z ([\d.]+) \(pick\) -> ([\d.]+) \(flip\) -> ([\d.]+) \(place\)"
                  r" -> ([\d.]+) \(stowed\)", rep)
    px, _, z_pick, z_flip, z_place, z_stow = (float(v) for v in m.groups())
    p = re.search(r"pinion centre x ([\d.]+), z ([\d.]+) \(pick\)", rep)
    return px, z_pick, z_flip - z_pick, z_flip - z_place, z_place - z_stow, (float(p.group(1)), float(p.group(2)))


def frames(top, over, rel):
    """(caption, lift, flip angle, Grail state: 'held' | 'floor' | 'deck', magnet on)"""
    F = [("Start: carriage down, magnet on the Grail's top plate", 0.0, 0.0, "held", True)] * 4
    n = int(round(top / LIFT_STEP))
    F += [("Lift %.0f / %.0f mm (pinion on the rack), magnet ON" % (top * i / n, top), top * i / n, 0.0, "held", True)
          for i in range(1, n + 1)]
    F += [("Flip %d deg at the top (MG996R), magnet ON" % a, top, float(a), "held", True)
          for a in range(int(FLIP_STEP), 181, int(FLIP_STEP))]
    F += [("Lower onto the Grail deck (z %.0f), %.0f / %.0f mm" % (C.ROOF_TOP, over * i / 3, over), top - over * i / 3,
           180.0, "held", True) for i in range(1, 4)]
    F += [("Grail on the deck, upside down (L4): magnet OFF", top - over, 180.0, "deck", False)] * 3
    F += [("Magnet off, arm lowers %.0f / %.0f mm into the deck slot (stowed)" % (rel * i / 3, rel),
           top - over - rel * i / 3, 180.0, "deck", False) for i in range(1, 4)]
    F += [("Stowed: Grail free on the deck", top - over - rel, 180.0, "deck", False)] * 5
    F += [("Way back (no Grail): up %.0f mm" % ((over + rel) * i / 3), top - over - rel + (over + rel) * i / 3, 180.0,
           "deck", False) for i in range(1, 4)]
    F += [("Way back: flip %d deg" % a, top, float(a), "deck", False) for a in range(170, -1, -int(BACK_FLIP_STEP))]
    n = int(round(top / (2 * LIFT_STEP)))
    F += [("Way back: down to the pick height", top * (1 - i / n), 0.0, "deck", False) for i in range(1, n + 1)]
    F += [("Ready for the next Grail (the next match)", 0.0, 0.0, "deck", False)] * 4
    return F


def run():
    try:
        px, z_pick, top, over, rel, (pin_x, pin_z) = numbers()
        doc = App.openDocument(os.path.join(C.CAD, "FLIPPER_B330.FCStd"))
        Gui.updateGui()

        def members(groups):
            out = []
            for g in groups:
                grp = doc.getObject(g)
                out += [o for o in (grp.Group if grp else []) if o.TypeId == "Part::Feature"]
            return out

        arm, lift, grail = members(ARM_G), members(LIFT_G), members(GRAIL_G)
        for o in doc.Objects:
            if o.TypeId == "Part::Feature":
                o.ViewObject.Visibility = not o.Name.startswith("PLACE_")
        limit = doc.getObject("CTX_LIMIT_350")
        if limit:
            limit.ViewObject.ShapeColor = (0.90, 0.15, 0.15)
            limit.ViewObject.LineColor = (0.90, 0.15, 0.15)
            limit.ViewObject.LineWidth = 3.0
            limit.ViewObject.Transparency = 0
        base = {o.Name: App.Placement(o.Placement) for o in arm + lift + grail}
        mag = doc.getObject("MAGNET_D30")
        mag_col = (0.25, 0.25, 0.28)                       # magnet OFF: dark grey (ON: bright red)
        P = (px, z_pick)
        view = Gui.getDocument(doc.Name).ActiveView
        try:
            view.setCameraType("Orthographic")
        except Exception:
            pass
        cams = {k: camera_string(*v) for k, v in VIEWS.items()}
        shutil.rmtree(TMP, ignore_errors=True)
        os.makedirs(TMP, exist_ok=True)
        F = frames(top, over, rel)
        for i, (cap, lz, a, gstate, mag_on) in enumerate(F):
            pl_arm = C.rot_pl(P, a, lz)
            pl_lift = App.Placement(App.Vector(0, 0, lz), App.Rotation())
            spin = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 1, 0), math.degrees(lz / 10.0)),
                                 App.Vector(pin_x, 0, pin_z))
            for o in arm:
                o.Placement = pl_arm.multiply(base[o.Name])
            for o in lift:
                o.Placement = (pl_lift.multiply(spin) if o.Name in SPIN else pl_lift).multiply(base[o.Name])
            gpl = pl_arm if gstate == "held" else C.rot_pl(P, 180.0, top - over)
            for o in grail:
                o.Placement = gpl.multiply(base[o.Name])
            if mag:
                mag.ViewObject.ShapeColor = (0.95, 0.20, 0.20) if mag_on else mag_col
            for key in VIEWS:
                if limit:
                    limit.ViewObject.Visibility = key == "side"
                view.setCamera(cams[key])
                Gui.updateGui()
                view.saveImage(os.path.join(TMP, "f%03d_%s.png" % (i, key)), W, H, "White")
        App.closeDocument(doc.Name)          # not saved: the FCStd stays as the generator wrote it
        path = make_gif(F)
        shutil.rmtree(TMP, ignore_errors=True)
        App.Console.PrintMessage("GIF written: %s (%d frames)\n" % (path, len(F)))
    except Exception:
        import traceback
        with open(os.path.join(C.CAD, "flipper_gif_error.txt"), "w") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


def make_gif(F):
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
    for i, (cap, lz, a, gstate, mag_on) in enumerate(F):
        canvas = Image.new("RGB", (W * len(VIEWS), H + CAPTION_H), (24, 28, 34))
        for j, key in enumerate(VIEWS):
            canvas.paste(Image.open(os.path.join(TMP, "f%03d_%s.png" % (i, key))).convert("RGB"), (j * W, 0))
        d = ImageDraw.Draw(canvas)
        for j, key in enumerate(VIEWS):
            d.text((j * W + 10, 8), VIEW_LABELS[key], font=f2, fill=(90, 90, 90))
        d.text((14, H + 8), "Flipper (Grail lift, D-029) on base_330_js - FreeCAD model, Grail deck at %.0f, magnet red = ON, grey = OFF"
               % C.ROOF_TOP, font=f1, fill=(120, 220, 140))
        d.text((14, H + 36), cap, font=f2, fill=(225, 228, 232))
        imgs.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "flipper_cycle.gif")
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=90, loop=0, optimize=True)
    caps = [c for c, *_ in F]
    picks = {"start": 0, "flip90": caps.index("Flip 90 deg at the top (MG996R), magnet ON"),
             "placed": caps.index("Stowed: Grail free on the deck")}
    for tag, idx in picks.items():
        imgs[idx].convert("RGB").save(os.path.join(OUT, "flipper_cycle_%s.png" % tag))
    return path


if App.GuiUp:
    QtCore.QTimer.singleShot(3000, run)
