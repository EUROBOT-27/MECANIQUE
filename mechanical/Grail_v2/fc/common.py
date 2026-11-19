# common.py - shared context + checks for the Grail v2 generators (top grip, Grail turned over onto the roof).
# Frame = layout-v1 robot frame: X right (the Grail side is the RIGHT face, x = +FACE), Y forward, Z up, z = 0 = table.
# Every variant turns the Grail 180 deg about an axis along Y: picked by its TOP on the floor outside the right face,
# it ends UPSIDE DOWN on the roof, the magnet under it in a roof slot (a top grip can't end above the Grail: the magnet
# would be at roof + Grail height > 350 [GR F.3]).
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))                     # mechanical/Grail_v2
CAD = os.path.join(ROOT, "CAD_FC")
MECH = os.path.normpath(os.path.join(ROOT, ".."))                     # mechanical/
SERVO_DIR = os.path.join(MECH, "resources", "mg996r-servo-3.snapshot.9")
sys.path.insert(0, os.path.join(MECH, "grail-lift", "fc"))
import grail_common as GC                                              # noqa: E402  (profile, rack, pinion, V-wheel)

# ------------------------------------------------------------------ robot context (layout-v1, A+B front)
FACE = 150.0            # right body face x
BODY_Y = 146.0          # body y +-
ROOF_BOT, ROOF_TOP = 300.0, 306.0
ROOF_Y = 38.0           # roof strip y +- (between the two clapets lifts)
WHEEL = dict(x0=106.0, x1=150.0, r=37.0, z=37.0)    # right drive wheel envelope (axis along x)
BAY = dict(x0=66.0, x1=150.0, y=40.0, z0=78.0, z1=300.0)   # right side bay reserved for the Grail (layout-v1)
H_MAX = 350.0           # [GR F.3]
H_DESIGN = 348.0        # keep 2 mm
SIDE_L = 292.0          # side length of the hull for the perimeter-bump estimate (body Y)

# ------------------------------------------------------------------ Grail + magnet
G_W = 70.0              # Grail footprint (x and y)
G_H = 80.0              # Grail height  (> 60 mm cube [G E.2]; layout-v1 assumed 70 x 70 x 100)
G_MASS = 0.150          # kg
GAP_OUT = 10.0          # Grail on the floor this far from the face at the pick
EDGE_IN = 5.0           # Grail on the roof this far inside the face
X_PICK = FACE + GAP_OUT + G_W / 2          # Grail centre x at the pick (on the floor)
X_PLACE = FACE - EDGE_IN - G_W / 2         # Grail centre x on the roof
MAG_D, MAG_L, MAG_MASS = 25.0, 20.0, 0.050  # electromagnet 12 V 5 kg (KK-P25/20 type), 🇹🇳
ABS_RHO = 1.04e-6 * 0.6                     # kg/mm3, ABS at ~60 % effective (walls + infill)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl(r, h, p, d):
    return Part.makeCylinder(r, h, Vector(*p), Vector(*d))


def bar(p0, p1, t, y0, y1):
    """Flat bar in the X-Z plane from p0 to p1 (x, z), in-plane thickness t, y0..y1, round ends."""
    a, b = Vector(p0[0], 0, p0[1]), Vector(p1[0], 0, p1[1])
    d = b - a
    L = d.Length
    ang = math.degrees(math.atan2(d.z, d.x))
    s = box(0, L, y0, y1, -t / 2, t / 2)
    s = s.fuse(cyl(t / 2, y1 - y0, (0, y0, 0), (0, 1, 0))).fuse(cyl(t / 2, y1 - y0, (L, y0, 0), (0, 1, 0)))
    s.rotate(Vector(0, 0, 0), Vector(0, -1, 0), ang)
    s.translate(a)
    return s.removeSplitter()


def grail(xc=X_PICK, zb=0.0):
    """Grail standing on its bottom at z = zb, steel plate (1.5) on its TOP face."""
    g = box(xc - G_W / 2, xc + G_W / 2, -G_W / 2, G_W / 2, zb, zb + G_H - 1.5)
    plate = box(xc - 30, xc + 30, -30, 30, zb + G_H - 1.5, zb + G_H)
    return g, plate


def magnet_down(xc, z_face):
    """Magnet with its face down at z_face (pick pose), M4 stud up."""
    m = cyl(MAG_D / 2, MAG_L, (xc, 0, z_face), (0, 0, 1))
    return m.fuse(cyl(2.0, 8, (xc, 0, z_face + MAG_L), (0, 0, 1)))


def robot_context(slot=None):
    """Reference solids: body (ghost box up to the roof plate), roof strip (with slot), right wheel."""
    out = {}
    out["CTX_BODY_ghost"] = box(-FACE, FACE, -BODY_Y, BODY_Y, 21, ROOF_BOT).cut(
        box(BAY["x0"], BAY["x1"] + 1, -BAY["y"], BAY["y"], BAY["z0"], BAY["z1"] + 1))
    roof = box(-FACE, FACE, -ROOF_Y, ROOF_Y, ROOF_BOT, ROOF_TOP)
    if slot:
        roof = roof.cut(box(slot[0], slot[1], slot[2], slot[3], ROOF_BOT - 1, ROOF_TOP + 1))
    out["CTX_ROOF"] = roof
    out["CTX_WHEEL_R"] = cyl(WHEEL["r"], WHEEL["x1"] - WHEEL["x0"], (WHEEL["x0"], 0, WHEEL["z"]), (1, 0, 0))
    return out


def servo_mg996r(axis_x, axis_z, horn_face_y, body="-x"):
    """MG996R lying, shaft along +y, horn (round) outer face at horn_face_y. body = '-x' (inward) or '-z' (down)."""
    sv = GC.read_step(os.path.join(SERVO_DIR, "mg996R_v2.step"))
    hn = GC.read_step(os.path.join(SERVO_DIR, "mg996_arm_round.step"))
    rows = ((1, 0, 0), (0, 0, 1), (0, -1, 0)) if body == "-x" else ((0, 1, 0), (0, 0, 1), (1, 0, 0))
    s = GC.place_shape(sv, rows, (axis_x, 0, axis_z))
    h = GC.place_shape(hn, rows, (axis_x, 0, axis_z))
    dy = horn_face_y - h.BoundBox.YMax
    s.translate(Vector(0, dy, 0))
    h.translate(Vector(0, dy, 0))
    return s, h


# ------------------------------------------------------------------ poses + checks
def rot_pl(center_xz, ang_deg, lift=0.0):
    """Turn about the axis along y through (x, z) by ang (counter-clockwise seen from -y: +x towards +z), then lift."""
    c = Vector(center_xz[0], 0, center_xz[1])
    pl = App.Placement(Vector(0, 0, 0), App.Rotation(Vector(0, -1, 0), ang_deg), c)
    return App.Placement(Vector(0, 0, lift), App.Rotation()).multiply(pl)


def moved(shape, pl):
    s = shape.copy()
    s.Placement = pl.multiply(s.Placement)
    return s


def bb(shape):
    try:
        return shape.optimalBoundingBox(False, False)
    except Exception:
        return shape.BoundBox


def grail_points(pl):
    """Corners + edge midpoints of the Grail (pick pose) moved by pl."""
    x0, x1 = X_PICK - G_W / 2, X_PICK + G_W / 2
    pts = []
    for x in (x0, X_PICK, x1):
        for y in (-G_W / 2, 0, G_W / 2):
            for z in (0, G_H / 2, G_H):
                pts.append(pl.multVec(Vector(x, y, z)))
    return pts


def grail_in_robot(pl, tol=0.05):
    """Grail points inside the robot (x < FACE and below the roof top), not counting the final rest on the roof."""
    bad = [p for p in grail_points(pl) if p.x < FACE - tol and p.z < ROOF_TOP - tol and abs(p.y) < BODY_Y]
    return bad


def bump(d):
    """Perimeter added by a narrow protrusion d at the middle of a side of length SIDE_L (convex hull)."""
    if d <= 0:
        return 0.0
    return 2 * math.sqrt((SIDE_L / 2) ** 2 + d ** 2) - SIDE_L


def torque_kgcm(items, axis_x):
    """items = [(mass kg, x of centre)] -> |sum m * (x - axis)| in kg.cm."""
    return abs(sum(m * (x - axis_x) for m, x in items)) / 10.0


def com(shape):
    """Centre of mass of a shape or compound (volume-weighted over its solids)."""
    sols = shape.Solids
    v = sum(x.Volume for x in sols)
    c = Vector(0, 0, 0)
    for x in sols:
        c += x.CenterOfMass * (x.Volume / v)
    return c


def mass_of(shape):
    try:
        return shape.Volume * ABS_RHO
    except Exception:
        return 0.0


def save(doc, name, report_lines):
    os.makedirs(CAD, exist_ok=True)
    doc.recompute()
    doc.saveAs(os.path.join(CAD, name + ".FCStd"))
    with open(os.path.join(CAD, name + "_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print("\n".join(report_lines).encode("ascii", "replace").decode())


def add(doc, name, shape, group=None, groups=None):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    if groups is not None and group:
        if group not in groups:
            groups[group] = doc.addObject("App::DocumentObjectGroup", group)
        groups[group].addObject(o)
    return o


def run_cycle(steps, parts, fixed_top):
    """steps: [{'label', 'pls': {group: Placement}, 'held': bool, 'gpl': Placement or None, 'final': bool}]
    parts: {name: (shape at the pick pose, group)} for the MOVING actuator parts (not the Grail).
    Returns (table lines, summary dict). Bounding boxes only (no clash check)."""
    lines = ["  %-26s %8s %8s %9s %9s %s" % ("step", "act.top", "act.out", "Grail.bot", "Grail.top", "Grail inside robot?")]
    worst = dict(top=fixed_top, top_step="fixed parts", out=-1e9, out_step="", grail_bad=[], grail_top=0.0)
    for st in steps:
        ztop, xout = -1e9, -1e9
        for name, (shape, grp) in parts.items():
            b = bb(moved(shape, st["pls"][grp]))
            ztop, xout = max(ztop, b.ZMax), max(xout, b.XMax)
        gb = gt = float("nan")
        flag = ""
        if st.get("gpl") is not None:
            pts = grail_points(st["gpl"])
            gb, gt = min(p.z for p in pts), max(p.z for p in pts)
            worst["grail_top"] = max(worst["grail_top"], gt)
            if st.get("held") and not st.get("final"):
                bad = grail_in_robot(st["gpl"])
                if bad:
                    flag = "YES (%d pts, lowest z %.1f, x %.1f)" % (len(bad), min(p.z for p in bad),
                                                                   min(bad, key=lambda p: p.z).x)
                    worst["grail_bad"].append(st["label"])
        lines.append("  %-26s %8.1f %8.1f %9.1f %9.1f %s" % (st["label"], ztop, xout - FACE, gb, gt, flag))
        if ztop > worst["top"]:
            worst["top"], worst["top_step"] = ztop, st["label"]
        if xout - FACE > worst["out"]:
            worst["out"], worst["out_step"] = xout - FACE, st["label"]
    return lines, worst


def summary_lines(worst, start_out):
    ok_h = "OK" if worst["top"] <= H_DESIGN else "OVER"
    return [
        "  highest actuator point over the cycle: %.1f (%s, limit %.0f, design %.0f) -> %s"
        % (worst["top"], worst["top_step"], H_MAX, H_DESIGN, ok_h),
        "  max protrusion past the right face: %.1f mm (%s) -> perimeter bump ~%.0f mm (estimate, narrow protrusion "
        "mid-side, side %.0f)" % (worst["out"], worst["out_step"], bump(worst["out"]), SIDE_L),
        "  at the start (stowed): %.1f mm past the face -> bump ~%.0f mm" % (start_out, bump(start_out)),
        "  Grail entering the robot body before it lands: %s" % (", ".join(worst["grail_bad"]) or "never"),
        "  Grail highest point in the cycle: %.1f (only the Grail may pass 350, in the castle [G E.2])" % worst["grail_top"],
    ]


# ------------------------------------------------------------------ lift unit (B, C): Baha's tested rack idea
def lift_unit(xc, yc, zp0, zp1, zc, zr0, zr1, plate_x=None):
    """2020 column along z at (xc, yc), z zp0..zp1, m1 rack in its -y slot (teeth -y, z zr0..zr1).
    Carriage centred at height zc: plate on the +y face (y yc+12..+18), 3 V-wheels in the +-x slots,
    NEMA17 shaft along +x with a 20T m1 pinion on the rack (pinion 20 mm under the carriage centre), body inward.
    Returns (fixed parts, carriage parts at zc)."""
    fixed = {"LIFT_PROFILE_2020": GC.profile_2020(zp0, zp1, xc, yc),
             "LIFT_RACK_M1": GC.rack_m1(zr0, zr1, xc - 3, xc + 3, yc - 4, -1)}
    px0, px1 = plate_x if plate_x else (xc - 35, xc + 32)
    car = {"CAR_PLATE": box(px0, px1, yc + 12, yc + 18, zc - 37.5, zc + 37.5)}
    wh = []
    for (dx, dz) in ((19.5, 25), (19.5, -25), (-19.5, 0)):
        wh.append(GC.vwheel((xc + dx, yc, zc + dz), (0, 1, 0)))
    car["CAR_VWHEELS"] = Part.makeCompound(wh)
    zm = zc - 20.0
    yp = yc - 18.5                                    # pinion centre (rack pitch line at yc - 8.5, r 10)
    car["LIFT_PINION_20T"] = GC.pinion_m1(20, 10, (xc, yp, zm), "x")
    face = xc - 11.0
    car["LIFT_NEMA17"] = box(face - 40, face, yp - 21, yp + 21, zm - 21, zm + 21).fuse(
        cyl(2.5, 22, (face, yp, zm), (1, 0, 0)))
    car["LIFT_MOTOR_BRACKET"] = box(face - 4, face, yp + 21, yc + 12, zm - 21, zm + 21)
    return fixed, car


def rack_x(z0, z1, x_pitch, y0, y1, teeth_dir=1):
    """Fixed m1 rack along z with its teeth along +-x, pitch line at x_pitch (visual teeth)."""
    sgn = teeth_dir
    root = x_pitch - sgn * 1.25
    back = x_pitch - sgn * 8.0
    body = box(min(back, root), max(back, root), y0, y1, z0, z1)
    teeth = []
    n = int((z1 - z0) / math.pi)
    for i in range(n):
        zc = z0 + math.pi * (i + 0.5)
        tip = x_pitch + sgn * 1.0
        pts = [Vector(root, y0, zc - 1.2), Vector(root, y0, zc + 1.2), Vector(tip, y0, zc + 0.4), Vector(tip, y0, zc - 0.4)]
        teeth.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, y1 - y0, 0)))
    return body.fuse(teeth).removeSplitter()
