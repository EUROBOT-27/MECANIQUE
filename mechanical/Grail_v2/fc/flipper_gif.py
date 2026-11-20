# flipper_gif.py - colour GIF of the Flipper cycle, rendered from the real solids of CAD_FC/FLIPPER_B330.FCStd
# (Seif 2026-11-20: after the static + motion checks). Same kinematics as fc/flipper_fc.py and fc/flipper_motion_check.py
# (numbers read from the report): pick -> lift (the pinion turns on the rack) -> flip 180 at the top -> lower onto the
# Grail deck -> magnet off, lower 6 (stowed) -> way back without the Grail: down 14, turn back, down to the pick.
# Three panels, no footer: 3D from the front-right / side view along y (the flip plane, red line = 350 mechanism limit) /
# close view of the pinion on the rack, seen from the front, following the carriage (column and wheels hidden).
#
# Run (FreeCAD GUI needed; it closes itself), from mechanical/Grail_v2, after fc/flipper_fc.py:
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/flipper_gif.py
# Output: sim/flipper_cycle.gif + stills sim/flipper_cycle_*.png
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
OUT = os.path.normpath(os.path.join(HERE, "..", "sim"))
TMP = os.path.join(ROOT, "claude-workspace", "tmp", "flipper_gif")
H = 540
# key: (width px, azimuth deg from +Y towards +X, rise, look-at point, visible height mm); "close" follows the pinion
VIEWS = {"iso": (540, 135.0, 0.55, (120, 0, 190), 470),
         "side": (480, 180.0, 0.0, (125, 0, 205), 440),
         "close": (420, 0.0, 0.0, None, 64)}
VIEW_LABELS = {"iso": "3D view (front-right), magnet red = ON, grey = OFF",
               "side": "Side view, red line = 350 mechanism limit",
               "close": "Pinion on the rack (from the front, column hidden)"}
LIFT_STEP, FLIP_STEP, BACK_FLIP_STEP = 4.0, 5.0, 10.0
ARM_G = ("_3_ARM_pick_pose", "_8c_SCREWS_arm")
LIFT_G = ("_2_CARRIAGE_pick_pose", "_8b_SCREWS_carriage")
GRAIL_G = ("_4_GRAIL_pick",)
SPIN = ("PINION_v2", "INSERT_M3_PINION", "SCR_M3x6_SET_PINION")
SEE_THROUGH = ("PROFILE_2020",)                 # transparent in the close view
CLOSE_SHOW = SPIN + ("RACK_m1_printed", "NEMA17", "MOTOR_BRACKET", "SADDLE_SOCLE", "TOP_MEMBER_2020",
                                   "TOP_CAP")   # only these in the close view (the carriage's wheels hide the rack)


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
    b = re.search(r"turn back at pivot z ([\d.]+)", rep)
    return (px, z_pick, z_flip - z_pick, z_flip - z_place, z_place - z_stow, (float(p.group(1)), float(p.group(2))),
            float(b.group(1)) - z_pick)


def frames(top, over, rel, back):
    """(tag, lift, flip angle, Grail state: 'held' | 'deck', magnet on)"""
    F = [("start", 0.0, 0.0, "held", True)] * 4
    n = int(round(top / LIFT_STEP))
    F += [("lift", top * i / n, 0.0, "held", True) for i in range(1, n + 1)]
    F += [("flip%d" % a, top, float(a), "held", True) for a in range(int(FLIP_STEP), 181, int(FLIP_STEP))]
    F += [("lower", top - over * i / 3, 180.0, "held", True) for i in range(1, 4)]
    F += [("release", top - over, 180.0, "deck", False)] * 3
    F += [("stow", top - over - rel * i / 3, 180.0, "deck", False) for i in range(1, 4)]
    F += [("placed", top - over - rel, 180.0, "deck", False)] * 5
    lz0 = top - over - rel                                   # way back: go down, then turn back, then down
    F += [("back_down1", lz0 - (lz0 - back) * i / 4, 180.0, "deck", False) for i in range(1, 5)]
    F += [("back_turn", back, float(a), "deck", False) for a in range(175, -1, -int(FLIP_STEP))]
    n = max(1, int(round(back / (2 * LIFT_STEP))))
    F += [("back_down2", back * (1 - i / n), 0.0, "deck", False) for i in range(1, n + 1)]
    F += [("ready", 0.0, 0.0, "deck", False)] * 4
    return F


def run():
    try:
        px, z_pick, top, over, rel, (pin_x, pin_z), back = numbers()
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
        parts = [o for o in doc.Objects if o.TypeId == "Part::Feature" and not o.Name.startswith("PLACE_")]
        see = [doc.getObject(n) for n in SEE_THROUGH if doc.getObject(n)]
        see_tr = {o.Name: o.ViewObject.Transparency for o in see}
        base = {o.Name: App.Placement(o.Placement) for o in arm + lift + grail}
        mag = doc.getObject("MAGNET_D30")
        mag_off = (0.25, 0.25, 0.28)                          # magnet OFF: dark grey (ON: bright red)
        P = (px, z_pick)
        view = Gui.getDocument(doc.Name).ActiveView
        try:
            view.setCameraType("Orthographic")
        except Exception:
            pass
        shutil.rmtree(TMP, ignore_errors=True)
        os.makedirs(TMP, exist_ok=True)
        F = frames(top, over, rel, back)
        for i, (tag, lz, a, gstate, mag_on) in enumerate(F):
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
                mag.ViewObject.ShapeColor = (0.95, 0.20, 0.20) if mag_on else mag_off
            for key, (w, az, el, target, height) in VIEWS.items():
                for o in parts:
                    o.ViewObject.Visibility = (o.Name in CLOSE_SHOW) if key == "close" else                         (o.Name != "CTX_LIMIT_350" or key == "side")
                for o in see:
                    o.ViewObject.Transparency = 75 if key == "close" else see_tr[o.Name]
                tgt = target if target else (pin_x + 8.0, 0.0, pin_z + lz)     # mesh point near the centre
                view.setCamera(camera_string(az, el, tgt, height))
                Gui.updateGui()
                view.saveImage(os.path.join(TMP, "f%03d_%s.png" % (i, key)), w, H, "White")
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

    def font(sz):
        for name in ("arial.ttf", "DejaVuSans.ttf"):
            try:
                return ImageFont.truetype(name, sz)
            except Exception:
                pass
        return ImageFont.load_default()

    f2 = font(14)
    total_w = sum(v[0] for v in VIEWS.values())
    imgs = []
    for i in range(len(F)):
        canvas = Image.new("RGB", (total_w, H), (255, 255, 255))
        d = ImageDraw.Draw(canvas)
        x0 = 0
        for key, v in VIEWS.items():
            canvas.paste(Image.open(os.path.join(TMP, "f%03d_%s.png" % (i, key))).convert("RGB"), (x0, 0))
            tb = d.textbbox((x0 + 10, 8), VIEW_LABELS[key], font=f2)
            d.rectangle([tb[0] - 4, tb[1] - 3, tb[2] + 4, tb[3] + 3], fill=(255, 255, 255))
            d.text((x0 + 10, 8), VIEW_LABELS[key], font=f2, fill=(90, 90, 90))
            if x0:
                d.line([(x0, 0), (x0, H)], fill=(200, 200, 200), width=1)
            x0 += v[0]
        imgs.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "flipper_cycle.gif")
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=90, loop=0, optimize=True)
    tags = [t for t, *_ in F]
    for tag, idx in (("start", 0), ("flip90", tags.index("flip90")), ("placed", tags.index("placed"))):
        imgs[idx].convert("RGB").save(os.path.join(OUT, "flipper_cycle_%s.png" % tag))
    return path


if App.GuiUp:
    QtCore.QTimer.singleShot(3000, run)
