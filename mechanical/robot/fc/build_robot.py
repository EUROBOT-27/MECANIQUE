# build_robot.py - the FULL robot, rebuilt from the current mechanism files every time it runs:
#   drive (Pololu 37D + JSUMO wheels, odometry reserves, casters), base plate, roof, beacon support, battery and
#   electronics reserves, clapets module front + back (mechanical/clapets/<L.CLAPETS>), Grail lift (mechanical/grail-lift,
#   L.GRAIL_LIFT). Layout numbers: layout.py.
# Run (from mechanical/robot):  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/build_robot.py      (~1-2 min)
#   -> CAD_FC/ROBOT.FCStd, CAD_FC/ROBOT.step, CAD_FC/robot_report.txt (perimeter, height, interferences between modules)
#   -> sim/excalibot_fc/  = Gazebo model for eurobot2027/Simulation-Euro27 (robot.yaml + robot.urdf.xacro + meshes/*.stl):
#      copy it to src/eb27_description/robots/excalibot_fc/ (tools/sync_robot.py does it), then ./sim build.
# Usually run through:  python tools/sync_robot.py   (rebuilds only if a source changed, then copies to the sim clone)
import hashlib
import json
import math
import os
import re
import shutil
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import FreeCAD as App
import Import
import Mesh
import MeshPart
import Part
from FreeCAD import Vector

from layout import L, wheel_center_y, wheel_separation

ROOT = os.path.normpath(os.path.join(HERE, ".."))                      # mechanical/robot
MECH = os.path.normpath(os.path.join(ROOT, ".."))                      # mechanical
CAD = os.path.join(ROOT, "CAD_FC")
SIM_NAME = "excalibot_fc"
SIM = os.path.join(ROOT, "sim", SIM_NAME)
CLAP_DIR = os.path.join(MECH, "clapets", L.CLAPETS)
GRAIL_DIR = os.path.join(MECH, "grail-lift")

# ---- colours: the sim shows every part in the colour it has in FreeCAD
COLOR = {}                                   # part name in the robot -> (r, g, b, a), 0..1
DEFAULT_RGBA = (0.8, 0.8, 0.8, 1.0)          # FreeCAD's default shape colour
GEN_COLORS = (                               # parts generated here (no FreeCAD file of their own): first prefix match
    ("DRIVE_WHEEL", (0.05, 0.05, 0.05)), ("DRIVE_MOTOR", (0.62, 0.63, 0.66)), ("DRIVE_BRACKET", (0.25, 0.25, 0.28)),
    ("CASTER", (0.30, 0.30, 0.32)), ("BASE_PLATE", (0.72, 0.58, 0.40)), ("ROOF_PLATE", (0.72, 0.58, 0.40)),
    ("BEACON_SUPPORT", (0.13, 0.13, 0.15)), ("RES_", (0.55, 0.30, 0.85)))


def _packed_rgba(v):
    return tuple(round(((v >> s) & 0xFF) / 255.0, 3) for s in (24, 16, 8, 0))


def _material_rgba(blob):
    """Diffuse colour of a FreeCAD 1.x ShapeAppearance blob (most common one if the faces differ).
    Layout: uint32 count, then per material 4 packed RGBA uint32 (ambient, diffuse, specular, emissive),
    float shininess, float transparency, 3 length-prefixed strings."""
    n = struct.unpack_from("<I", blob, 0)[0]
    off, seen = 4, {}
    for _ in range(n):
        dif = struct.unpack_from("<I", blob, off + 4)[0]
        tr = struct.unpack_from("<f", blob, off + 20)[0]
        rgba = _packed_rgba(dif)[:3] + (round(1.0 - tr, 3),)
        seen[rgba] = seen.get(rgba, 0) + 1
        off += 24
        try:
            for _s in range(3):
                off += 4 + struct.unpack_from("<I", blob, off)[0]
        except struct.error:
            break
    return max(seen, key=seen.get) if seen else None


def fc_colors(path):
    """Colours saved in an FCStd by the FreeCAD GUI: {object name: (r, g, b, a)}. Empty if it was saved headless
    (freecadcmd has no ViewObject, so the colours are read straight from GuiDocument.xml)."""
    out = {}
    try:
        z = zipfile.ZipFile(path)
        gui = z.read("GuiDocument.xml").decode("utf-8", "ignore")
    except (KeyError, OSError, zipfile.BadZipFile):
        return out
    for name, body in re.findall(r'<ViewProvider name="([^"]+)"(.*?)</ViewProvider>', gui, re.S):
        try:
            m = re.search(r'<MaterialList file="([^"]+)"', body)
            if m:                                                        # FreeCAD 1.x
                rgba = _material_rgba(z.read(m.group(1)))
            else:                                                        # FreeCAD 0.x: ShapeColor + Transparency
                c = re.search(r'name="ShapeColor".*?value="(\d+)"', body, re.S)
                tr = re.search(r'name="Transparency".*?value="(\d+)"', body, re.S)
                rgba = None
                if c:
                    rgba = _packed_rgba(int(c.group(1)))[:3] + ((round(1 - int(tr.group(1)) / 100.0, 3) if tr else 1.0),)
        except (KeyError, struct.error, ValueError):
            rgba = None
        if rgba:
            out[name] = rgba
    return out


def gen_color(name):
    for pre, rgb in GEN_COLORS:
        if name.startswith(pre):
            return tuple(rgb) + (1.0,)
    return DEFAULT_RGBA


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl(r, h, p, d):
    return Part.makeCylinder(r, h, Vector(*p), Vector(*d))


def mat(rows):
    r = rows
    return App.Matrix(r[0][0], r[0][1], r[0][2], 0, r[1][0], r[1][1], r[1][2], 0, r[2][0], r[2][1], r[2][2], 0, 0, 0, 0, 1)


# ======================================================================= parts we generate here
def drive_parts():
    P = {}
    wc = wheel_center_y()
    zc = L.WHEEL_D / 2
    zm = zc + (L.SHAFT_OFF if L.MOTOR_UP else 0.0)
    for side, s in (("L", 1), ("R", -1)):
        y_in = s * (L.WHEEL_OUT - L.WHEEL_W)
        w = cyl(L.WHEEL_D / 2, L.WHEEL_W, (0, y_in, zc), (0, s, 0))
        P["DRIVE_WHEEL_" + side] = w
        y_face = y_in - s * L.WHEEL_GAP                                  # gearbox boss face side
        boss = cyl(L.BOSS_D / 2, L.BOSS_L, (0, y_face, zc), (0, -s, 0))
        y_gb = y_face - s * L.BOSS_L
        gb = cyl(L.GB_D / 2, L.GB_L, (0, y_gb, zm), (0, -s, 0))
        y_m = y_gb - s * L.GB_L
        mo = cyl(L.MOT_D / 2, L.MOT_L, (0, y_m, zm), (0, -s, 0))
        y_t = y_m - s * L.MOT_L
        te = cyl(4.0, L.TERM_L, (0, y_t, zm), (0, -s, 0))
        sh = cyl(L.SHAFT_D / 2, L.SHAFT_L, (0, y_face, zc), (0, s, 0))
        P["DRIVE_MOTOR_" + side] = boss.fuse([gb, mo, te, sh])
        # motor bracket: 3 mm plate on the gearbox face, foot on the base plate (stand-in for Pololu #1084/#1995)
        yb0, yb1 = sorted((y_gb, y_gb + s * 3.0))
        br = box(-17, 17, yb0, yb1, L.PLATE_Z[1], zm + 20).cut(cyl(L.BOSS_D / 2 + 1, 10, (0, yb0 - 3, zc), (0, 1, 0)))
        br = br.fuse(box(-17, 17, *sorted((y_gb, y_gb - s * 30.0)), L.PLATE_Z[1], L.PLATE_Z[1] + 3))
        P["DRIVE_BRACKET_" + side] = br
        # odometry (RESERVE): free wheel + AMT102 on a sprung arm
        oy = s * L.ODOM_Y
        ow = cyl(L.ODOM_WHEEL_D / 2, 8, (L.ODOM_X, oy - 4, L.ODOM_WHEEL_D / 2), (0, 1, 0))
        enc = box(L.ODOM_X - 14.4, L.ODOM_X + 14.4, *sorted((oy + s * 6, oy + s * 17)),
                  L.ODOM_WHEEL_D / 2 - 15.3, L.ODOM_WHEEL_D / 2 + 28.0)
        P["RES_ODOM_" + side] = ow.fuse(enc)
    for i, (x, y) in enumerate(L.CASTERS):
        P["CASTER_%d" % i] = Part.makeSphere(L.CASTER_R, Vector(x, y, L.CASTER_R)).fuse(
            cyl(L.CASTER_R + 3, L.PLATE_Z[0] - L.CASTER_R, (x, y, L.CASTER_R), (0, 0, 1)))
    return P


def structure_parts(cut_zones):
    P = {}
    plate = box(-L.HALF_X, L.HALF_X, -L.HALF_Y, L.HALF_Y, *L.PLATE_Z)
    for s in (1, -1):                                                    # wheel wells
        y0, y1 = sorted((s * (L.WHEEL_OUT - L.WHEEL_W - 3), s * (L.HALF_Y + 1)))
        plate = plate.cut(box(-L.WHEEL_D / 2 - 4, L.WHEEL_D / 2 + 4, y0, y1, 0, 50))
    for z in cut_zones:
        plate = plate.cut(z)
    P["BASE_PLATE"] = plate
    mx, my = L.MAST_XY
    P["BEACON_SUPPORT"] = cyl(L.MAST_D / 2, L.MAST_TOP - L.H_MAX, (mx, my, L.H_MAX), (0, 0, 1)).fuse(
        cyl(L.MAST_POST_D / 2, L.H_MAX - L.ROOF + 1, (mx, my, L.ROOF), (0, 0, 1)))
    (bx, by, bz), (ex, ey, ez) = L.BATTERY, L.ELECTRONICS
    P["RES_BATTERY"] = box(bx[0], bx[1], by[0], by[1], bz[0], bz[1])
    P["RES_ELECTRONICS"] = box(ex[0], ex[1], ey[0], ey[1], ez[0], ez[1])
    return P


# ======================================================================= clapets
def clapets_consts():
    src = open(os.path.join(CLAP_DIR, "fc", [f for f in os.listdir(os.path.join(CLAP_DIR, "fc"))
                                              if f.startswith("motion_")][0]), encoding="utf-8").read()
    k = {}
    m = re.search(r"PX, PY, SVY, HZ = ([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)", src)
    k["PX"], k["PY"], k["SVY"], k["HZ"] = map(float, m.groups())
    m = re.search(r"HGC, HS_ANG = ([\d.]+), ([\d.]+)", src)
    k["HGC"], k["HS_ANG"] = map(float, m.groups())
    k["HEAD_RATIO"] = eval(re.search(r"HEAD_RATIO = ([\d. /]+)", src).group(1))
    k["DOOR_RATIO"] = eval(re.search(r"DOOR_RATIO = ([\d. /]+)", src).group(1))
    m = re.search(r"A_FOLD, A_OPEN_APPROACH, A_CLAMP, A_OPEN = ([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)", src)
    k["A_FOLD"], k["A_APPROACH"], k["A_CLAMP"], k["A_OPEN"] = map(float, m.groups())
    k["HS_X"] = -k["HGC"] * math.sin(math.radians(k["HS_ANG"]))
    k["HS_Z"] = k["HZ"] - k["HGC"] * math.cos(math.radians(k["HS_ANG"]))
    return k


def clapets_local_pl(grp, k, h, a, ph):
    """Same as the clapets motion script: placement of a motion group in the clapets frame."""
    lift = App.Placement(Vector(0, 0, h), App.Rotation())
    if grp == "carriage" or grp == "reserve":
        return lift
    if grp.startswith("door_"):
        s = 1 if grp.endswith("D") else -1
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), s * a), Vector(s * k["PX"], k["PY"], 0)))
    if grp.startswith("pinion_"):
        s = 1 if grp.endswith("D") else -1
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), -s * k["DOOR_RATIO"] * a),
                                           Vector(s * k["PX"], k["SVY"], 0)))
    if grp == "hpinion":
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), -k["HEAD_RATIO"] * ph),
                                           Vector(k["HS_X"], 0, k["HS_Z"])))
    if grp == "head":
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), ph), Vector(0, 0, k["HZ"])))
    return App.Placement()


def clapets_mount(back):
    """clapets frame -> robot frame. Front: X = y + (HALF_X - FACE), Y = -x, Z = z + Z0. Back: same, turned 180 deg."""
    dx = L.HALF_X - L.CLAPETS_FACE
    rows = ((0, 1, 0), (-1, 0, 0), (0, 0, 1))
    m = App.Matrix(rows[0][0], rows[0][1], rows[0][2], dx, rows[1][0], rows[1][1], rows[1][2], 0,
                   rows[2][0], rows[2][1], rows[2][2], L.CLAPETS_Z0, 0, 0, 0, 1)
    pl = App.Placement(m)
    if back:
        pl = App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), 180)).multiply(pl)
    return pl


def clapets_parts(k):
    path = os.path.join(CLAP_DIR, "CAD_FC", "MODULE_%s.FCStd" % L.CLAPETS.upper().replace("-", "_"))
    cols = fc_colors(path)
    doc = App.openDocument(path)
    objs = [o for o in doc.Objects if o.TypeId == "Part::Feature" and hasattr(o, "MotionGroup")
            and o.MotionGroup not in ("stack", "reserve") and not o.Name.startswith("RES_")]
    out = []
    for back in ((False, True) if L.CLAPETS_BACK else (False,)):
        mount = clapets_mount(back)
        tag = "CLAPETS_BACK_" if back else "CLAPETS_FRONT_"
        for o in objs:
            loc = clapets_local_pl(o.MotionGroup, k, 0.0, k["A_FOLD"], 0.0)      # start: doors folded
            sh = o.Shape.copy()
            sh.Placement = mount.multiply(loc).multiply(o.Shape.Placement)
            out.append((tag + o.Name, sh, o.MotionGroup, back))
            COLOR[tag + o.Name] = cols.get(o.Name, DEFAULT_RGBA)
    App.closeDocument(doc.Name)
    return out


# ======================================================================= Grail lift
def grail_parts():
    J = json.load(open(os.path.join(GRAIL_DIR, "CAD_FC", "joints_%s.json" % L.GRAIL_LIFT), encoding="utf-8"))
    cols = fc_colors(os.path.join(GRAIL_DIR, "CAD_FC", J["fcstd"]))   # saved from the GUI, if ever
    jcols = J.get("colors", {})                                          # else the generator's table (motion_fc shows it)
    doc = App.openDocument(os.path.join(GRAIL_DIR, "CAD_FC", J["fcstd"]))
    s = L.GRAIL_SIDE
    # local (x out of the side face, y along it, z) -> robot: Y = s*(HALF_Y + x), X = GRAIL_X - s*y
    rows = ((0, -s, 0), (s, 0, 0), (0, 0, 1))
    mount = App.Placement(App.Matrix(rows[0][0], rows[0][1], rows[0][2], L.GRAIL_X, rows[1][0], rows[1][1], rows[1][2],
                                     s * L.HALF_Y, rows[2][0], rows[2][1], rows[2][2], 0, 0, 0, 0, 1))
    st = J["sequence"][0]
    lift0, flip0 = st[1], st[2]
    lpl = App.Placement(Vector(0, 0, lift0 - J["lift"]["base"]), App.Rotation())
    fax = J["flip"]
    fpl = lpl.multiply(App.Placement(Vector(), App.Rotation(Vector(*fax["axis_dir"]), flip0 - fax["base"]),
                                     Vector(*fax["axis_point"])))
    out = []
    for o in doc.Objects:
        if o.TypeId != "Part::Feature" or o.Name.startswith("ENV_") or o.Name in J["grail"]["objects"]:
            continue
        grp = "flip" if o.Name in fax["objects"] else ("lift" if o.Name in J["lift"]["objects"] else "fixed")
        loc = {"flip": fpl, "lift": lpl}.get(grp, App.Placement())
        sh = o.Shape.copy()
        sh.Placement = mount.multiply(loc).multiply(o.Shape.Placement)
        out.append(("GRAIL_" + o.Name, sh, grp))
        COLOR["GRAIL_" + o.Name] = cols.get(o.Name) or (tuple(jcols[o.Name]) + (1.0,) if o.Name in jcols else DEFAULT_RGBA)
    App.closeDocument(doc.Name)
    # joints in robot frame (at the START pose = sim zero)
    ap = mount.multiply(lpl).multiply(App.Placement(Vector(*fax["axis_point"]), App.Rotation())).Base
    adir = mount.Rotation.multVec(Vector(*fax["axis_dir"]))
    jinfo = {"lift_dir": [0, 0, 1], "lift_zero": lift0, "lift_range": [J["lift"]["min"], J["lift"]["max"]],
             "flip_point": [ap.x, ap.y, ap.z], "flip_axis": [adir.x, adir.y, adir.z], "flip_zero": flip0,
             "flip_range": [fax["min"], fax["max"]], "roof_slot": None}
    return out, jinfo, mount


# ======================================================================= checks
def hull_perimeter(pts):
    pts = sorted(set((round(p[0], 2), round(p[1], 2)) for p in pts))
    if len(pts) < 3:
        return 0.0

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    h = lo[:-1] + hi[:-1]
    return sum(math.dist(h[i], h[(i + 1) % len(h)]) for i in range(len(h)))


def plan_points(shape):
    pts = []
    for v in shape.Vertexes:
        pts.append((v.X, v.Y))
    for e in shape.Edges:
        try:
            if e.Curve.__class__.__name__ == "Line":
                continue
        except Exception:
            pass                                      # some imported edges have no readable curve type
        try:
            for p in e.discretize(12):
                pts.append((p.x, p.y))
        except Exception:
            pass
    return pts


# ======================================================================= main
def main():
    os.makedirs(CAD, exist_ok=True)
    k = clapets_consts()
    parts = []                                        # (name, shape, module, group)
    for n, s in drive_parts().items():
        parts.append((n, s, "drive", "fixed"))
    for n, s, g, back in clapets_parts(k):
        parts.append((n, s, "clapets_back" if back else "clapets_front", g))
    gparts, gj, gmount = grail_parts()
    for n, s, g in gparts:
        parts.append((n, s, "grail", g))
    # base plate cut-outs: clapets motors/socles going through, the Grail-lift column bay
    cuts = []
    for n, s, m, g in parts:
        if n.startswith("RES_ODOM"):
            b = s.BoundBox
            cuts.append(box(b.XMin - 2, b.XMax + 2, b.YMin - 2, b.YMax + 2, 0, 60))
        if m.startswith("clapets") and ("NEMA17" in n or "COUPLEUR" in n):
            b = s.BoundBox
            cuts.append(box(b.XMin - 2, b.XMax + 2, b.YMin - 2, b.YMax + 2, 0, 60))
    for n, s in structure_parts(cuts).items():
        parts.append((n, s, "structure", "fixed"))
    # roof: plate at ROOF over the middle band, with the Grail-lift slot/bay (from the lift's own roof model)
    gdoc = App.openDocument(os.path.join(GRAIL_DIR, "CAD_FC", "GRAIL_LIFT_%s.FCStd" % L.GRAIL_LIFT.upper()))
    groof = gdoc.getObject("ENV_ROOF").Shape.copy()
    App.closeDocument(gdoc.Name)
    groof.Placement = gmount.multiply(groof.Placement)
    roof = box(-110, 110, -L.HALF_Y, L.HALF_Y, L.ROOF - L.ROOF_T, L.ROOF)
    slot = box(-200, 200, -200, 200, L.ROOF - L.ROOF_T - 1, L.ROOF + 1).cut(groof)   # where the lift's roof has holes
    hb = groof.BoundBox
    roof = roof.cut(slot.common(box(hb.XMin, hb.XMax, hb.YMin, hb.YMax, 0, 400)))
    for n, s, m, g in parts:                                            # clapets columns go through the roof
        if m.startswith("clapets") and ("RAILS" in n or "TRAVERSE" in n):
            b = s.BoundBox
            roof = roof.cut(box(b.XMin - 2, b.XMax + 2, b.YMin - 2, b.YMax + 2, 0, 500))
    parts.append(("ROOF_PLATE", roof, "structure", "fixed"))

    doc = App.newDocument("ROBOT")
    for n, s, m, g in parts:
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        o.addProperty("App::PropertyString", "Module", "Robot").Module = m
        o.addProperty("App::PropertyString", "MotionGroup", "Robot").MotionGroup = g
    doc.recompute()
    doc.saveAs(os.path.join(CAD, "ROBOT.FCStd"))
    Import.export([o for o in doc.Objects], os.path.join(CAD, "ROBOT.step"))

    # ---------------- checks at the start pose
    rep = ["ROBOT (start pose: clapets doors folded, Grail lift folded) - fc/build_robot.py", ""]
    rep.append("Layout: footprint %.0f x %.0f, drive track %.1f (wheel Ø%.0f x %.0f), clapets %s front%s (z0 %.0f), "
               "Grail lift %s on the %s side" % (2 * L.HALF_X, 2 * L.HALF_Y, wheel_separation(), L.WHEEL_D, L.WHEEL_W,
                                                 L.CLAPETS, " + back" if L.CLAPETS_BACK else "", L.CLAPETS_Z0,
                                                 L.GRAIL_LIFT, "left" if L.GRAIL_SIDE > 0 else "right"))
    real = [(n, s, m, g) for n, s, m, g in parts if not n.startswith("RES_")]
    pts = []
    for n, s, m, g in real:
        if not n.startswith("BEACON"):
            pts += plan_points(s)
    per = hull_perimeter(pts)
    allb = None
    for n, s, m, g in real:
        allb = s.BoundBox if allb is None else allb.united(s.BoundBox)
    rep.append("Start perimeter (convex hull of the vertical projection): %.1f mm  -> %s (limit 1200)"
               % (per, "OK" if per <= 1200.5 else "TOO BIG"))
    rep.append("Overall box: x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f" % (allb.XMin, allb.XMax, allb.YMin, allb.YMax,
                                                                          allb.ZMin, allb.ZMax))
    rep.append("")
    rep.append("Parts above %.0f mm (beacon support excluded, allowed up to %.0f):" % (L.H_MAX, L.MAST_TOP))
    tall = sorted(((s.BoundBox.ZMax, n) for n, s, m, g in real if s.BoundBox.ZMax > L.H_MAX + 0.01
                   and not n.startswith("BEACON")), reverse=True)
    for z, n in tall[:15]:
        rep.append("  %-45s z max %.1f" % (n, z))
    if not tall:
        rep.append("  none")
    rep.append("Parts below the table (z < 0):")
    low = [(s.BoundBox.ZMin, n) for n, s, m, g in real if s.BoundBox.ZMin < -0.01]
    rep += ["  %-45s z min %.1f" % (n, z) for z, n in sorted(low)] or ["  none"]
    rep.append("")
    rep.append("Interferences BETWEEN modules / with reserves (> 1 mm3):")
    mods = {}
    for n, s, m, g in parts:
        mods.setdefault(m, []).append((n, s))
    names = list(mods)
    hit = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            for na, sa in mods[names[i]]:
                for nb, sb in mods[names[j]]:
                    if not sa.BoundBox.intersect(sb.BoundBox):
                        continue
                    try:
                        v = sa.common(sb).Volume
                    except Exception:
                        v = -1
                    if v > 1:
                        hit += 1
                        rep.append("  %-40s x %-40s %9.1f mm3" % (na, nb, v))
    if not hit:
        rep.append("  none")
    with open(os.path.join(CAD, "robot_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep))
    export_sim(parts, k, gj)


# ======================================================================= Gazebo export
def write_stl(shapes, path, origin=Vector(0, 0, 0)):
    comp = Part.makeCompound([s.copy() for s in shapes])
    comp.translate(-origin)
    m = MeshPart.meshFromShape(Shape=comp, LinearDeflection=0.6, AngularDeflection=0.6, Relative=False)
    m.write(path)


def write_link(name, named, origin=Vector(0, 0, 0)):
    """meshes/<name>.stl = the whole link (the sim builds collision boxes from it) + one mesh per FreeCAD colour,
    meshes/<name>_<rrggbb[aa]>.stl, drawn by robot.urdf.xacro. Returns [(mesh, rgba)]."""
    write_stl([s for n, s in named], os.path.join(SIM, "meshes", name + ".stl"), origin)
    groups = {}
    for n, s in named:
        groups.setdefault(COLOR.get(n) or gen_color(n), []).append(s)
    vis = []
    for rgba in sorted(groups):
        tag = "".join("%02x" % round(c * 255) for c in rgba[:3]) + ("" if rgba[3] >= 0.999 else "%02x" % round(rgba[3] * 255))
        rel = "meshes/%s_%s.stl" % (name, tag)
        write_stl(groups[rgba], os.path.join(SIM, rel), origin)
        vis.append((rel, rgba))
    return vis


def yaml_visual(v):
    return "{mesh: %s, rgba: [%s]}" % (v[0], ", ".join("%.3f" % c for c in v[1]))


def export_sim(parts, k, gj):
    if os.path.isdir(SIM):
        shutil.rmtree(SIM)
    os.makedirs(os.path.join(SIM, "meshes"))
    mm = 0.001
    links = []                       # dicts: name, parent, type, origin(robot mm), axis, limits, mesh, zero
    moving = {}
    body = []
    for n, s, m, g in parts:
        if n.startswith(("DRIVE_WHEEL", "CASTER_", "RES_")):
            continue                 # wheels + casters are drawn by the sim's drive macro; reserves are not real parts
        if m.startswith("clapets") and g in ("carriage", "head", "hpinion", "door_D", "door_G", "pinion_D", "pinion_G"):
            key = (m, {"hpinion": "carriage", "pinion_D": "carriage", "pinion_G": "carriage"}.get(g, g))
            moving.setdefault(key, []).append((n, s))
        elif m == "grail" and g in ("lift", "flip"):
            moving.setdefault((m, g), []).append((n, s))
        else:
            body.append((n, s))
    body_vis = write_link("body", body)
    clap_mount = {"clapets_front": clapets_mount(False), "clapets_back": clapets_mount(True)}

    def add_link(name, parent, jtype, origin, axis, lo, hi, shapes, parent_origin):
        if not shapes:
            return
        o = Vector(*origin)
        vis = write_link(name, shapes, o)
        rel = o - Vector(*parent_origin)
        links.append({"name": name, "parent": parent, "type": jtype, "xyz": [round(rel.x * mm, 5), round(rel.y * mm, 5),
                      round(rel.z * mm, 5)], "axis": [round(a, 6) for a in axis], "lower": lo, "upper": hi,
                      "mesh": "meshes/%s.stl" % name, "visuals": vis})
    for mod in ("clapets_front", "clapets_back"):
        if (mod, "carriage") not in moving:
            continue
        mt = clap_mount[mod]
        lift_o = mt.multVec(Vector(0, 0, 0))
        add_link(mod + "_lift", "base_link", "prismatic", lift_o, [0, 0, 1], 0.0, 0.075,
                 moving[(mod, "carriage")], (0, 0, 0))
        for g, s in (("door_D", 1), ("door_G", -1)):
            p = mt.multVec(Vector(s * k["PX"], k["PY"], 0))
            ax = mt.Rotation.multVec(Vector(0, 0, s))
            # door angle a: 0 = straight, A_FOLD folded (sim zero), A_OPEN open -> joint q = a - A_FOLD
            add_link("%s_door_%s" % (mod, "right" if g == "door_D" else "left"), mod + "_lift", "revolute", p,
                     [ax.x, ax.y, ax.z], math.radians(k["A_OPEN"] - 10 - k["A_FOLD"]), 0.05,
                     moving.get((mod, g), []), lift_o)
        hp = mt.multVec(Vector(0, 0, k["HZ"]))
        hax = mt.Rotation.multVec(Vector(0, 1, 0))
        add_link(mod + "_head", mod + "_lift", "revolute", hp, [hax.x, hax.y, hax.z], -math.pi / 2, math.pi / 2,
                 moving.get((mod, "head"), []), lift_o)
    if ("grail", "lift") in moving:
        lo = [0, 0, 0]
        add_link("grail_lift", "base_link", "prismatic", lo, [0, 0, 1], round((gj["lift_range"][0] - gj["lift_zero"]) * mm, 4),
                 round((gj["lift_range"][1] - gj["lift_zero"]) * mm, 4), moving[("grail", "lift")], (0, 0, 0))
        add_link("grail_flip", "grail_lift", "revolute", gj["flip_point"], gj["flip_axis"],
                 math.radians(gj["flip_range"][0] - gj["flip_zero"]), math.radians(gj["flip_range"][1] - gj["flip_zero"]),
                 moving[("grail", "flip")], lo)
    # ---- robot.yaml
    wc = wheel_center_y()
    lines = ["# EXCALIBOT (hub FreeCAD model) - GENERATED by mechanical/robot/fc/build_robot.py, do not edit by hand:",
             "# change mechanical/robot/fc/layout.py or a mechanism generator, then run tools/sync_robot.py.",
             "# Frame: base_footprint = middle of the wheel axle on the floor, X forward, Y left, Z up, metres.",
             "name: %s" % SIM_NAME, "role: main", "urdf: robot.urdf.xacro", "",
             "body:", "  mesh: meshes/body.stl", "  mesh_scale: [0.001, 0.001, 0.001]", "  visuals:"] + [
             "    - %s" % yaml_visual(v) for v in body_vis] + ["  mass: 4.5",
             "  com: [0.0, 0.0, 0.12]", "  inertia: {ixx: 0.07, iyy: 0.07, izz: 0.07}", "  collisions:",
             "    - {type: box, size: [%.3f, %.3f, %.3f], xyz: [0.0, 0.0, %.3f]}" % (2 * L.HALF_X * mm, 2 * (L.WHEEL_OUT - L.WHEEL_W - 4) * mm,
                                                                                  (L.ROOF - L.PLATE_Z[0]) * mm, (L.ROOF + L.PLATE_Z[0]) / 2 * mm),
             "    - {type: cylinder, radius: %.3f, length: %.3f, xyz: [%.3f, %.3f, %.3f]}" % (
                 L.MAST_D / 2 * mm, (L.MAST_TOP - L.ROOF) * mm, L.MAST_XY[0] * mm, L.MAST_XY[1] * mm, (L.MAST_TOP + L.ROOF) / 2 * mm),
             "", "footprint:", "  size: [%.3f, %.3f]" % (2 * L.HALF_X * mm, 2 * L.HALF_Y * mm), "  center: [0.0, 0.0]", "",
             "drive:", "  type: diff", "  wheel_radius: %.4f" % (L.WHEEL_D / 2 * mm), "  wheel_width: %.4f" % (L.WHEEL_W * mm),
             "  wheel_separation: %.4f" % (wheel_separation() * mm), "  wheel_x: 0.0", "  wheel_mass: 0.11",
             "  wheel_friction: 1.0", "  casters:"]
    for x, y in L.CASTERS:
        lines.append("    - {xy: [%.3f, %.3f], radius: %.3f}" % (x * mm, y * mm, L.CASTER_R * mm))
    lines += ["  max_linear_velocity: 1.2", "  max_angular_velocity: 6.0", "  max_linear_acceleration: 3.0",
              "  max_angular_acceleration: 20.0", "", "# moving parts (read by robot.urdf.xacro): position-controlled joints,",
              "# command each with  ros2 topic pub /<ns>/<joint>/cmd std_msgs/msg/Float64 '{data: <m or rad>}'",
              "# zero = start pose (everything folded). Sign/limits: see each joint.", "actuators:"]
    for l in links:
        lines.append("  - {name: %s, parent: %s, type: %s, xyz: %s, axis: %s, lower: %.4f, upper: %.4f, mesh: %s, visuals: [%s]}"
                     % (l["name"], l["parent"], l["type"], l["xyz"], l["axis"], l["lower"], l["upper"], l["mesh"],
                        ", ".join(yaml_visual(v) for v in l["visuals"])))
    lines += ["", "sensors:", "  - type: lidar", "    name: lidar", "    topic: scan",
              "    xyz: [%.3f, %.3f, %.3f]" % (L.MAST_XY[0] * mm, L.MAST_XY[1] * mm, (L.MAST_TOP - 30) * mm),
              "    rpy: [0.0, 0.0, 0.0]", "    samples: 720", "    min_angle: -3.14159", "    max_angle: 3.14159",
              "    range_min: 0.12", "    range_max: 8.0", "    noise_stddev: 0.008", "    rate: 10",
              "  - type: imu", "    name: imu", "    topic: imu", "    xyz: [0.0, 0.0, 0.05]", "    rate: 100"]
    with open(os.path.join(SIM, "robot.yaml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    shutil.copy(os.path.join(HERE, "robot.urdf.xacro"), os.path.join(SIM, "robot.urdf.xacro"))
    # manifest: what this export was built from
    man = {"built_from": {}, "links": [l["name"] for l in links]}
    for p in sources():
        man["built_from"][os.path.relpath(p, MECH).replace("\\", "/")] = file_hash(p)
    json.dump(man, open(os.path.join(SIM, "manifest.json"), "w", encoding="utf-8"), indent=1)
    print("sim export:", SIM, "links:", [l["name"] for l in links])


def file_hash(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:12]


def sources():
    """Files the robot is built from (tools/sync_robot.py rebuilds when one of them changes)."""
    out = [os.path.join(HERE, f) for f in ("layout.py", "build_robot.py", "robot.urdf.xacro")]
    out.append(os.path.join(CLAP_DIR, "CAD_FC", "MODULE_%s.FCStd" % L.CLAPETS.upper().replace("-", "_")))
    out.append(os.path.join(GRAIL_DIR, "CAD_FC", "GRAIL_LIFT_%s.FCStd" % L.GRAIL_LIFT.upper()))
    out.append(os.path.join(GRAIL_DIR, "CAD_FC", "joints_%s.json" % L.GRAIL_LIFT))
    return out


main()
