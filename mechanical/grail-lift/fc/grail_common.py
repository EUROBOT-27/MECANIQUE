# grail_common.py - shared helpers for the Grail lift scripts (v1 rebuild, v2 concept, sliders, motion check).
# Frame used everywhere (the "robot frame" of the lift): x = outward normal of the robot face that carries the lift
# (the Grail starts on the +x side), y = along that face, z = up, z = 0 is the table.
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))                 # mechanical/grail-lift
CAD = os.path.join(ROOT, "CAD_FC")
SW = os.path.join(ROOT, "sw")
RES = os.path.normpath(os.path.join(ROOT, "..", "resources"))    # mechanical/resources
SERVO_DIR = os.path.join(RES, "mg996r-servo-3.snapshot.9")

H_MAX = 350.0          # robot + actuators, at all times [GR F.3], [G E.1]; the Grail itself may pass it in the castle [G E.2]
ROOF_MIN = 300.0       # L4: Grail on the robot's roof, roof > 300 mm [G E.2]


# ---------------------------------------------------------------- simple solids
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl(r, h, p, d):
    return Part.makeCylinder(r, h, Vector(*p), Vector(*d))


def profile_2020(z0, z1, xc=0.0, yc=0.0):
    """20 x 20 aluminium profile along z (simplified: 4 slots 6.2 wide x 6 deep, centre bore 4.2)."""
    s = box(xc - 10, xc + 10, yc - 10, yc + 10, z0, z1)
    L = z1 - z0
    w, d = 6.2, 6.0                                  # slot opening, depth
    for sx in (1, -1):
        x0 = xc + sx * 10 - (d if sx > 0 else 0)
        s = s.cut(box(x0, x0 + d, yc - w / 2, yc + w / 2, z0 - 1, z1 + 1))
    for sy in (1, -1):
        y0 = yc + sy * 10 - (d if sy > 0 else 0)
        s = s.cut(box(xc - w / 2, xc + w / 2, y0, y0 + d, z0 - 1, z1 + 1))
    return s.cut(cyl(2.1, L + 2, (xc, yc, z0 - 1), (0, 0, 1)))


def rack_m1(z0, z1, x0, x1, y_back, teeth_dir=1):
    """Module-1 straight rack along z. Back face at y_back, pitch line at y_back + 4.5 * dir, tips +1.0 further.
    Face width = x1 - x0. Teeth = trapezoids (visual model, pitch pi)."""
    sgn = teeth_dir
    yb, yp = y_back, y_back + sgn * 3.5             # body to the root line (pitch line - 1.0 dedendum... simplified)
    body = box(x0, x1, min(yb, yp), max(yb, yp), z0, z1)
    pitch = math.pi
    n = int((z1 - z0) / pitch)
    teeth = []
    for i in range(n):
        zc = z0 + pitch * (i + 0.5)
        root_y, tip_y = yp, y_back + sgn * 5.5
        pts = [Vector(x0, root_y, zc - 1.2), Vector(x0, root_y, zc + 1.2),
               Vector(x0, tip_y, zc + 0.4), Vector(x0, tip_y, zc - 0.4)]
        w = Part.makePolygon(pts + [pts[0]])
        teeth.append(Part.Face(w).extrude(Vector(x1 - x0, 0, 0)))
    return body.fuse(teeth).removeSplitter()


def pinion_m1(z_teeth, width, center, axis):
    """Module-1 spur gear (visual): pitch circle r = z/2, tips r + 1, roots r - 1.25. axis = 'x' or 'y' or 'z'."""
    r = z_teeth / 2.0
    pts = []
    for i in range(z_teeth):
        a0 = 2 * math.pi * i / z_teeth
        for da, rr in ((-0.42, r - 1.25), (-0.20, r + 1.0), (0.20, r + 1.0), (0.42, r - 1.25)):
            a = a0 + da * 2 * math.pi / z_teeth
            pts.append(Vector(rr * math.cos(a), rr * math.sin(a), 0))
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    g = face.extrude(Vector(0, 0, width)).cut(cyl(2.55, width + 2, (0, 0, -1), (0, 0, 1)))
    g.translate(Vector(0, 0, -width / 2))
    if axis == "x":
        g.rotate(Vector(0, 0, 0), Vector(0, 1, 0), 90)
    elif axis == "y":
        g.rotate(Vector(0, 0, 0), Vector(1, 0, 0), -90)
    g.translate(Vector(*center))
    return g


def vwheel(center, axis_dir=(1, 0, 0)):
    """V-wheel (Ender / OpenBuilds style): Ø24, 10.2 wide, V rim (visual)."""
    c = Vector(*center)
    d = Vector(*axis_dir)
    w = cyl(12.0, 10.2, (0, 0, -5.1), (0, 0, 1))
    w = w.cut(cyl(2.55, 12, (0, 0, -6), (0, 0, 1)))
    if d.x:
        w.rotate(Vector(0, 0, 0), Vector(0, 1, 0), 90)
    elif d.y:
        w.rotate(Vector(0, 0, 0), Vector(1, 0, 0), -90)
    w.translate(c)
    return w


def read_step(path):
    s = Part.read(path)
    return s


def mat_from_rows(rx, ry, rz):
    """Matrix whose rows are the world axes expressed in the source frame (world = M * src)."""
    m = App.Matrix(rx[0], rx[1], rx[2], 0, ry[0], ry[1], ry[2], 0, rz[0], rz[1], rz[2], 0, 0, 0, 0, 1)
    return m


def place_shape(shape, rows, offset):
    s = shape.copy()
    if rows:
        s.transformShape(mat_from_rows(*rows))        # exact for rigid moves (transformGeometry makes B-splines)
    s.translate(Vector(*offset))
    return s


# ---------------------------------------------------------------- joints file
def save_joints(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


def load_joints(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def lift_pl(J, lift):
    return App.Placement(Vector(0, 0, lift - J["lift"]["base"]), App.Rotation())


def flip_pl(J, lift, ang):
    """Placement applied to the flip group (rotation about the flip axis, then the lift)."""
    f = J["flip"]
    p0 = Vector(*f["axis_point"])
    rot = App.Rotation(Vector(*f["axis_dir"]), ang - f["base"])
    r = App.Placement(Vector(0, 0, 0), rot, p0)        # rotation about p0
    return lift_pl(J, lift).multiply(r)


def simulate(J, t):
    """Replay the sequence up to time t. Sequence rows: (duration, lift, flip, magnet_on, approach, label); row 0 is
    the start pose (duration ignored). 'approach' moves the free Grail along x before it is picked (robot driving in).
    Returns (lift, flip, magnet_on, grail_placement, label)."""
    seq = J["sequence"]
    s0 = Vector(*J["grail"]["start_offset"])
    ad = Vector(*J["grail"].get("approach_dir", [1, 0, 0]))   # direction the robot's approach moves the free Grail
    free = App.Placement(s0 + ad * seq[0][4], App.Rotation())
    on, picked, rel = bool(seq[0][3]), False, None
    lift, ang, app = seq[0][1], seq[0][2], seq[0][4]
    t0 = 0.0
    for k in range(1, len(seq)):
        dur, l1, a1, mag, ap1, lab = seq[k]
        if t < t0 + dur:
            f = max(0.0, (t - t0) / dur) if dur > 0 else 1.0
            L = lift + (l1 - lift) * f
            A = ang + (a1 - ang) * f
            if on:
                g = flip_pl(J, L, A).multiply(rel)
            elif not picked:
                g = App.Placement(s0 + ad * (app + (ap1 - app) * f), App.Rotation())
            else:
                g = free
            return L, A, on, g, lab
        lift, ang, app = l1, a1, ap1
        if not picked and not on:
            free = App.Placement(s0 + ad * app, App.Rotation())
        if mag and not on:
            rel = flip_pl(J, lift, ang).inverse().multiply(free)
            on, picked = True, True
        elif not mag and on:
            free = flip_pl(J, lift, ang).multiply(rel)
            on = False
        t0 += dur
    g = flip_pl(J, lift, ang).multiply(rel) if on else free
    return lift, ang, on, g, seq[-1][5]


def seq_duration(J):
    return sum(s[0] for s in J["sequence"][1:])
