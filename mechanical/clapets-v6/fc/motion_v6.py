# motion_v6.py - full cycle of the clapets module v6 (modules A + B) + checks at every step.
#   Headless check:  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" motion_v6.py
#       -> ../CAD_FC/motion/motion_report.txt: collisions, start footprint (base 300 x 300), perimeter, height <= 350
#   Door range sweep (no stack): same, with  set V4_MODE=range  (env var)
#   Video: "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" motion_v6.py  -> frames, motion.gif / .mp4, copied to the hub
# Cycle: start (doors folded) -> unfold -> clamp -> carry (lift 15) -> lower -> doors open (cups hold) -> lift 72 ->
#        turn the stack 90 deg -> lower -> release -> head back -> doors fold.
import math
import os

import FreeCAD as App
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
OUT = os.path.join(CAD, "motion")
FCSTD = os.path.join(CAD, "MODULE_CLAPETS_V6.FCStd")
HUB_SIM = os.environ.get("CLAPETS_COPY_DIR", "")              # optional: also copy videos/reports/images there

PX, PY, SVY, HZ = 131.0, 82.0, 52.0, 165.0        # = v6_fc.py class G
HGC, HS_ANG = 31.25, 25.0
HS_X = -HGC * math.sin(math.radians(HS_ANG))
HS_Z = HZ - HGC * math.cos(math.radians(HS_ANG))
HEAD_RATIO = 30 / 20                               # head pinion turns -1.5x the head
DOOR_RATIO = 28 / 20                               # door pinion turns -1.4x the door
BASE_X, BASE_Y0, BASE_Y1 = 150.0, -160.0, 140.0
EXEMPT_HEIGHT = ("REF_RAIL", "A_TRAVERSE_HAUT", "REF_VIS_T8", "REF_608ZZ_1", "RES_")   # rails/top tie: height ignored for now (Maatoug)

# timeline: (duration s, lift mm, door deg, head deg, stack follows lift, stack follows head, label) at the END of each step
A_FOLD, A_OPEN_APPROACH, A_CLAMP, A_OPEN = 90.0, -30.0, 3.0, -38.0
TIMELINE = [   # (duration, lift, doors, head, stack follows lift, stack follows head, stack present, label) at step END
    (0.5, 0, A_FOLD, 0, 0, 0, 0, "start: doors folded inside the base"),
    (1.5, 0, A_OPEN_APPROACH, 0, 0, 0, 0, "doors open"),
    (1.0, 0, A_OPEN_APPROACH, 0, 0, 0, 1, "approach: stack at the face"),
    (1.0, 0, A_CLAMP, 0, 0, 0, 1, "doors clamp the stack"),
    (1.0, 15, A_CLAMP, 0, 1, 0, 1, "carry: lift 15 mm"),
    (0.5, 15, A_CLAMP, 0, 1, 0, 1, "carry"),
    (1.0, 0, A_CLAMP, 0, 1, 0, 1, "in the castle: lower"),
    (1.0, 0, A_OPEN, 0, 1, 1, 1, "cups hold, doors open -38 deg"),
    (2.0, 75, A_OPEN, 0, 1, 1, 1, "lift 75 mm with the stack"),
    (2.0, 75, A_OPEN, 90, 1, 1, 1, "turn the stack 90 deg"),
    (1.5, 0, A_OPEN, 90, 1, 1, 1, "lower (towers 5 mm above the table)"),
    (0.5, 0, A_OPEN, 90, 0, 0, 1, "release: cups vent"),
    (1.0, 0, A_OPEN, 90, 0, 0, 0, "robot backs away"),
    (1.5, 0, A_OPEN, 0, 0, 0, 0, "head back"),
    (1.5, 0, A_FOLD, 0, 0, 0, 0, "doors fold"),
]


def total_time():
    return sum(t[0] for t in TIMELINE)


def pose(t):
    t0, prev = 0.0, (0, A_FOLD, 0, 0, 0)
    for dur, h, a, ph, sl, sh, pres, label in TIMELINE:
        if t <= t0 + dur + 1e-9:
            f = (t - t0) / dur
            lerp = lambda x0, x1: x0 + (x1 - x0) * f
            return lerp(prev[0], h), lerp(prev[1], a), lerp(prev[2], ph), sl, sh, label
        t0, prev = t0 + dur, (h, a, ph, sl, sh)
    last = TIMELINE[-1]
    return last[1], last[2], last[3], last[4], last[5], last[7]


def present(t):
    t0 = 0.0
    for step in TIMELINE:
        if t <= t0 + step[0] + 1e-9:
            return step[6]
        t0 += step[0]
    return TIMELINE[-1][6]


def stack_state(t):
    """stack placement params: it keeps the last lift/turn it had while held."""
    h_s, ph_s = 0.0, 0.0
    n = int(round(t * 20))
    for k in range(n + 1):
        tk = k / 20.0
        h, a, ph, sl, sh, _ = pose(tk)
        if sl:
            h_s = h
        if sh:
            ph_s = ph
    return h_s, ph_s


def placement(base, grp, h, a, ph, hs, phs):
    def lift(z):
        return App.Placement(Vector(0, 0, z), App.Rotation())
    if grp == "fixed":
        return base
    if grp == "carriage":
        return lift(h).multiply(base)
    if grp.startswith("door_"):
        s = 1 if grp.endswith("D") else -1
        rot = App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), s * a), Vector(s * PX, PY, 0))
        return lift(h).multiply(rot).multiply(base)
    if grp.startswith("pinion_"):
        s = 1 if grp.endswith("D") else -1
        rot = App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), -s * DOOR_RATIO * a), Vector(s * PX, SVY, 0))
        return lift(h).multiply(rot).multiply(base)
    if grp == "hpinion":
        rot = App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), -HEAD_RATIO * ph), Vector(HS_X, 0, HS_Z))
        return lift(h).multiply(rot).multiply(base)
    if grp == "reserve":
        return lift(h).multiply(base)
    if grp == "head":
        rot = App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), ph), Vector(0, 0, HZ))
        return lift(h).multiply(rot).multiply(base)
    if grp == "stack":
        if hs is None:                                       # stack not there (before the approach / after backing away)
            return App.Placement(Vector(0, 2000, 0), App.Rotation()).multiply(base)
        rot = App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), phs), Vector(0, 0, HZ))
        return lift(hs).multiply(rot).multiply(base)
    return base


def objects(doc):
    return [o for o in doc.Objects if o.TypeId == "Part::Feature"]


# ---------------------------------------------------------------- geometry helpers for the checks
def cloud(shape):
    pts = [v.Point for v in shape.Vertexes]
    for e in shape.Edges:
        try:
            pts += e.discretize(Number=12)
        except Exception:
            pass
    return pts


def hull2(pts):
    p = sorted(set((round(q[0], 3), round(q[1], 3)) for q in pts))
    if len(p) < 3:
        return p
    cr = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def perimeter(poly):
    return sum(math.hypot(poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]) for i in range(len(poly)))


# ---------------------------------------------------------------- headless check
def check(doc, fps=5):
    objs = objects(doc)
    base = {o.Name: o.Placement for o in objs}
    groups = {o.Name: o.MotionGroup for o in objs}
    shapes0 = {o.Name: o.Shape.copy() for o in objs}
    clouds = {n: [base[n].inverse().multVec(p) for p in cloud(shapes0[n])] for n in shapes0}   # local coords
    label = {o.Name: o.Label for o in objs}
    module = {o.Name: getattr(o, "Module", "-") for o in objs}
    base_sq = [(-BASE_X, BASE_Y0), (BASE_X, BASE_Y0), (BASE_X, BASE_Y1), (-BASE_X, BASE_Y1)]
    worst, foot, peri, height = {}, {}, {}, {}
    n = int(total_time() * fps) + 1
    for k in range(n):
        t = k / fps
        h, a, ph, _, _, lab = pose(t)
        hs, phs = stack_state(t)
        if not present(t):
            hs = None
        cur, pts, zmax, zwho = {}, [], -1e9, ""
        for nm in shapes0:
            pl = placement(base[nm], groups[nm], h, a, ph, hs, phs)
            sh = shapes0[nm].copy()
            sh.Placement = pl
            cur[nm] = sh
            if groups[nm] not in ("stack", "reserve"):
                wp = [pl.multVec(p) for p in clouds[nm]]
                pts += [(p.x, p.y) for p in wp]
                if not nm.startswith(EXEMPT_HEIGHT):
                    zm = max(p.z for p in wp)
                    if zm > zmax:
                        zmax, zwho = zm, label[nm]
        # footprint / perimeter (base square + module, stack not counted)
        poly = hull2(pts + base_sq)
        P = perimeter(poly)
        outside = max([max(abs(x) - BASE_X, y - BASE_Y1, BASE_Y0 - y) for x, y in pts] + [0.0])
        key = lab
        if key not in peri or P > peri[key][0]:
            peri[key] = (P, t)
        if key not in foot or outside > foot[key][0]:
            foot[key] = (outside, t)
        if key not in height or zmax > height[key][0]:
            height[key] = (zmax, t, zwho)
        # collisions between parts that move relative to each other
        names = list(cur)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                gi, gj = groups[names[i]], groups[names[j]]
                if gi == gj:
                    continue
                if "reserve" in (gi, gj):
                    # module A must stay out of the head's turning disc whenever the head is turned
                    other = names[j] if gi == "reserve" else names[i]
                    resn = names[i] if gi == "reserve" else names[j]
                    if not (resn.startswith("RES_TETE_ROTATION") and ph > 0.5 and module[other] == "A"):
                        continue
                si, sj = cur[names[i]], cur[names[j]]
                if not si.BoundBox.intersect(sj.BoundBox):
                    continue
                v = si.common(sj).Volume
                if v > 0.05:
                    pair = tuple(sorted((label[names[i]], label[names[j]])))
                    expected = any(p.startswith("REF_PILE") for p in pair) and any(p.startswith(("REF_MOUSSE", "REF_VENTOUSE")) for p in pair)
                    kk = (pair, expected)
                    if kk not in worst or v > worst[kk][0]:
                        worst[kk] = (v, t, lab)
    lines = ["Clapets v6 motion study: %d frames, %.1f s, %d fps. Base 300 x 300 (x ±150, y -160..140). Stack not counted (FAQ Q1)." % (n, total_time(), fps), ""]
    lines.append("%-42s %10s %12s %22s" % ("step", "perimeter", "outside base", "highest part (z)"))
    for dur, _, _, _, _, _, _, lab in TIMELINE:
        P, _ = peri[lab]
        o, _ = foot[lab]
        z, _, who = height[lab]
        lines.append("%-42s %8.1f mm %9.1f mm   %6.1f  %s" % (lab, P, o, z, who))
    lines.append("")
    lines.append("Limits: start perimeter <= 1200 and nothing outside the base; deployed <= 1400; height <= 350 (rails, top tie, screw exempt).")
    exp = sorted((k, v) for k, v in worst.items() if k[1])
    bad = sorted(((k, v) for k, v in worst.items() if not k[1]), key=lambda kv: -kv[1][0])
    lines += ["", "Expected contacts (pads squeezing the stack, cups on the box face):"]
    lines += ["  %-50s max %8.1f mm3 at t %.1f s (%s)" % (" / ".join(p), v, t, lab) for (p, _), (v, t, lab) in exp]
    lines += ["", "UNEXPECTED collisions (incl. module A inside the head's turning disc while it turns): %d" % len(bad)]
    lines += ["  %-50s max %8.1f mm3 at t %.1f s (%s)" % (" / ".join(p), v, t, lab) for (p, _), (v, t, lab) in bad]
    for d in [OUT] + ([HUB_SIM] if HUB_SIM else []):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "motion_report.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def door_range(doc):
    """sweep the doors alone (no stack, carriage down, head vertical) from 0 outwards and inwards until a collision."""
    objs = [o for o in objects(doc) if o.MotionGroup != "stack"]
    base = {o.Name: o.Placement for o in objs}
    groups = {o.Name: o.MotionGroup for o in objs}
    shapes0 = {o.Name: o.Shape.copy() for o in objs}
    label = {o.Name: o.Label for o in objs}
    res = []
    for sign, side in ((-1, "open (outwards)"), (1, "fold (inwards)")):
        a, hit = 0.0, None
        while abs(a) < 170:
            a2 = a + sign * 1.0
            cur = {}
            for nm in shapes0:
                sh = shapes0[nm].copy()
                sh.Placement = placement(base[nm], groups[nm], 0, a2, 0, 0, 0)
                cur[nm] = sh
            hits = []
            names = list(cur)
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    gi, gj = groups[names[i]], groups[names[j]]
                    if gi == gj or not (gi.startswith(("door", "pinion")) or gj.startswith(("door", "pinion"))):
                        continue
                    if cur[names[i]].BoundBox.intersect(cur[names[j]].BoundBox):
                        v = cur[names[i]].common(cur[names[j]]).Volume
                        if v > 0.05:
                            hits.append((label[names[i]], label[names[j]], v))
            if hits:
                hit = (a2, hits)
                break
            a = a2
        res.append((side, a, hit))
    lines = ["Door range, no stack (carriage down, head vertical), 1 deg steps:"]
    for side, a, hit in res:
        lines.append("  %-16s free to %+6.1f deg" % (side, a))
        if hit:
            for l1, l2, v in sorted(hit[1], key=lambda x: -x[2])[:4]:
                lines.append("      first contact at %+6.1f: %s / %s (%.1f mm3)" % (hit[0], l1, l2, v))
    lines.append("  Needed: fold +90, clamp +3, open -38. Servo window (180 deg / x1.4) = 128.6 deg of door travel.")
    for d in [OUT] + ([HUB_SIM] if HUB_SIM else []):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "door_range_report.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


# ---------------------------------------------------------------- GUI: animation + video
def animate(doc, fps=10):
    import shutil
    import subprocess

    import FreeCADGui as Gui
    from PIL import Image, ImageDraw
    from PySide import QtCore
    objs = objects(doc)
    base = {o.Name: o.Placement for o in objs}
    groups = {o.Name: o.MotionGroup for o in objs}
    view = Gui.getDocument(doc.Name).ActiveView
    view.viewIsometric()
    view.fitAll()
    fdir = os.path.join(OUT, "frames")
    os.makedirs(fdir, exist_ok=True)
    for f in os.listdir(fdir):
        os.remove(os.path.join(fdir, f))
    n = int(total_time() * fps) + 1
    st = {"k": 0, "imgs": []}

    def step():
        k = st["k"]
        if k >= n:
            imgs = st["imgs"]
            gif = os.path.join(OUT, "motion.gif")
            imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=int(1000 / fps), loop=0)
            mp4 = os.path.join(OUT, "motion.mp4")
            ff = shutil.which("ffmpeg")
            if ff:
                subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(fdir, "f%03d.png"),
                                "-vf", "scale=1200:-2,format=yuv420p", "-c:v", "libx264", "-crf", "20", mp4])
            for src in (gif, mp4) if HUB_SIM else ():
                os.makedirs(HUB_SIM, exist_ok=True)
                if os.path.exists(src):
                    shutil.copy(src, os.path.join(HUB_SIM, "clapets_v6_" + os.path.basename(src)))
            App.closeDocument(doc.Name)
            Gui.getMainWindow().close()
            return
        t = k / fps
        h, a, ph, _, _, lab = pose(t)
        hs, phs = stack_state(t)
        if not present(t):
            hs = None
        for o in objs:
            o.Placement = placement(base[o.Name], groups[o.Name], h, a, ph, hs, phs)
        Gui.updateGui()
        p = os.path.join(fdir, "f%03d.png" % k)
        view.saveImage(p, 1200, 900, "White")
        im = Image.open(p).convert("RGB")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, im.width, 34], fill=(255, 255, 255))
        d.text((12, 10), "%s  |  lift %.0f mm  |  doors %+.0f deg  |  head %.0f deg" % (lab, h, a, ph), fill=(20, 20, 20))
        im.save(p)
        st["imgs"].append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
        st["k"] = k + 1
        QtCore.QTimer.singleShot(0, step)

    step()


if App.GuiUp:
    from PySide import QtCore
    _doc = App.openDocument(FCSTD)
    QtCore.QTimer.singleShot(3000, lambda: animate(_doc))
else:
    _doc = App.openDocument(FCSTD)
    if os.environ.get("V4_MODE") == "range":
        door_range(_doc)
    else:
        check(_doc)
    App.closeDocument(_doc.Name)
