# flipper_views.py - still images of the Flipper from every side, rendered from CAD_FC/FLIPPER_B330.FCStd (pick pose, as
# built: base plate, saddle, column, carriage, arm on the Grail, Grail deck). Red line = 350 mechanism limit (side views).
# Robot frame: +y = front (clapets), +x = the right face where the Flipper works, z up.
#
# Run (FreeCAD GUI needed; it closes itself), from mechanical/Grail_v2, after fc/flipper_fc.py:
#   "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/flipper_views.py
# Output: sim/views/flipper_<view>.png (7 views) + sim/views/flipper_all_views.png (contact sheet)
# On error: CAD_FC/flipper_views_error.txt
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import FreeCAD as App  # noqa: E402
import FreeCADGui as Gui  # noqa: E402
from PySide import QtCore  # noqa: E402

import common as C  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "sim", "views"))
W, H = 1100, 1000
TARGET, HEIGHT = (120.0, 0.0, 185.0), 470.0
# name: (azimuth deg from +Y towards +X, rise, label, show the 350 line)
VIEWS = {
    "iso_front_right": (135.0, 0.55, "3D view from the front-right", False),
    "iso_back_left": (225.0, 0.55, "3D view from the back-left", False),
    "front": (0.0, 0.0, "Front view (from +y, clapets side)", True),
    "back": (180.0, 0.0, "Back view (from -y): the flip plane", True),
    "right": (90.0, 0.0, "Right view (from +x, the Flipper's face)", True),
    "left": (270.0, 0.0, "Left view (from -x, robot inside)", True),
    "top": (180.0, 100.0, "Top view (front up)", False),
}


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


def run():
    try:
        doc = App.openDocument(os.path.join(C.CAD, "FLIPPER_B330.FCStd"))
        Gui.updateGui()
        parts = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
        for o in parts:
            o.ViewObject.Visibility = not o.Name.startswith("PLACE_")
        limit = doc.getObject("CTX_LIMIT_350")
        if limit:
            limit.ViewObject.ShapeColor = (0.90, 0.15, 0.15)
            limit.ViewObject.LineColor = (0.90, 0.15, 0.15)
            limit.ViewObject.LineWidth = 3.0
            limit.ViewObject.Transparency = 0
        view = Gui.getDocument(doc.Name).ActiveView
        try:
            view.setCameraType("Orthographic")
        except Exception:
            pass
        os.makedirs(OUT, exist_ok=True)
        for key, (az, el, label, show_limit) in VIEWS.items():
            if limit:
                limit.ViewObject.Visibility = show_limit
            view.setCamera(camera_string(az, el, TARGET, HEIGHT))
            Gui.updateGui()
            view.saveImage(os.path.join(OUT, "flipper_%s.png" % key), W, H, "White")
        App.closeDocument(doc.Name)          # not saved
        label_and_sheet()
    except Exception:
        import traceback
        with open(os.path.join(C.CAD, "flipper_views_error.txt"), "w") as f:
            f.write(traceback.format_exc())
    Gui.getMainWindow().close()


def label_and_sheet():
    from PIL import Image, ImageDraw, ImageFont

    def font(sz):
        for name in ("arial.ttf", "DejaVuSans.ttf"):
            try:
                return ImageFont.truetype(name, sz)
            except Exception:
                pass
        return ImageFont.load_default()

    f = font(26)
    imgs = []
    for key, (az, el, label, show_limit) in VIEWS.items():
        p = os.path.join(OUT, "flipper_%s.png" % key)
        im = Image.open(p).convert("RGB")
        d = ImageDraw.Draw(im)
        text = label + ("   (red line = 350 mechanism limit)" if show_limit else "")
        d.text((18, 14), text, font=f, fill=(70, 70, 70))
        im.save(p)
        imgs.append(im)
    cols, sw, sh = 4, W // 2, H // 2
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * sw, rows * sh), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(imgs):
        x, y = (i % cols) * sw, (i // cols) * sh
        sheet.paste(im.resize((sw, sh), Image.LANCZOS), (x, y))
        d.rectangle([x, y, x + sw - 1, y + sh - 1], outline=(210, 210, 210))
    d.text((cols * sw - sw + 20, sh + 30), "Flipper (Grail lift, D-029)\non base_330_js, pick pose\nGrail deck at %.0f" % C.ROOF_TOP,
           font=font(24), fill=(60, 60, 60))
    sheet.save(os.path.join(OUT, "flipper_all_views.png"))


if App.GuiUp:
    QtCore.QTimer.singleShot(3000, run)
