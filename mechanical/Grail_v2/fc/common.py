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
# Robot base the Grail lift is placed on (env GRAIL_BASE):
#   b330      (default since 2026-11-20, Seif): Ayoub's base_330_js (336 x 260 plate, JSUMO wheels, odometry outside
#             the wheel); frame = its assembly frame: X = wheel axis, Y = front (clapets) / back, Z up, z 0 = table
#   layout_v1 : Seif's layout-v1 (300 x 292 body)
BASE = os.environ.get("GRAIL_BASE", "b330")
B330_ASM = os.path.join(os.path.normpath(os.path.join(HERE, "..", "..")), "base_330_js", "CAD", "base_330_js_assembly.FCStd")
if BASE == "b330":
    FACE = 168.0        # right edge of the 336 plate
    BODY_Y = 130.0
    WHEEL = dict(x0=79.0, x1=131.0, r=40.0, z=37.0)    # JSUMO worst-case envelope Ø80 x 52 (nominal Ø74 x 44, x 81..125)
    PLATE_TOP = 16.5
else:
    FACE = 150.0        # right body face x
    BODY_Y = 146.0      # body y +-
    WHEEL = dict(x0=106.0, x1=150.0, r=37.0, z=37.0)    # right drive wheel envelope (axis along x)
    PLATE_TOP = 26.0
ROOF_BOT, ROOF_TOP = 300.0, 306.0
ROOF_Y = 38.0           # roof strip y +- (between the front and back modules' lifts)
BAY = dict(x0=66.0, x1=150.0, y=40.0, z0=78.0, z1=300.0)   # right side bay reserved for the Grail (layout-v1)
H_MAX = 350.0           # [GR F.3]
H_DESIGN = 348.0        # keep 2 mm
SIDE_L = 2 * BODY_Y     # side length of the hull for the perimeter-bump estimate

# ------------------------------------------------------------------ Grail + magnet
G_W = 70.0              # Grail footprint (x and y)
G_H = 80.0              # Grail height  (> 60 mm cube [G E.2]; layout-v1 assumed 70 x 70 x 100)
G_MASS = 0.150          # kg
GAP_OUT = 10.0          # Grail on the floor this far from the face at the pick
EDGE_IN = 5.0           # Grail on the roof this far inside the face
X_PICK = FACE + GAP_OUT + G_W / 2          # Grail centre x at the pick (on the floor)
X_PLACE = FACE - EDGE_IN - G_W / 2         # Grail centre x on the roof
MAG_D, MAG_L, MAG_MASS = 30.0, 22.0, 0.080  # electromagnet 12 V, Ø30 (same model as grail-lift/sw/Magnet 5KG.step, Ø30
                                            # version, Seif 2026-11-20); height 22 + M4 stud ASSUMED (P30/22 size) 🇹🇳
MAG_SEAT = 30.3                             # seat bore for the magnet (Baha's U had Ø30.3: intentional)
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


def servo_mg996r(axis_x, axis_z, horn_face_y, body="-x"):
    """MG996R lying, shaft along +y, round horn ON THE SPLINE, horn's outer face at horn_face_y.
    body = '-x' (inward) or '-z' (down). Model frame (mg996R_v2.step): shaft along +z, spline top z 15.5, gearbox top
    z 10.6, ear flange z 0..2.9 (ears 54 long, holes +-24.75 from the body centre x -10, 10 apart), body bottom z -28.3.
    The round horn file is centred on z 0: it is raised HORN_DZ so it sits on the spline above the gearbox."""
    sv = GC.read_step(os.path.join(SERVO_DIR, "mg996R_v2.step"))
    hn = GC.read_step(os.path.join(SERVO_DIR, "mg996_arm_round.step")).copy()
    hn.translate(Vector(0, 0, HORN_DZ))
    rows = ((1, 0, 0), (0, 0, 1), (0, -1, 0)) if body == "-x" else ((0, 1, 0), (0, 0, 1), (1, 0, 0))
    s = GC.place_shape(sv, rows, (axis_x, 0, axis_z))
    h = GC.place_shape(hn, rows, (axis_x, 0, axis_z))
    dy = horn_face_y - (3.3 + HORN_DZ)            # horn top (model z 3.3 + HORN_DZ) -> horn_face_y
    s.translate(Vector(0, dy, 0))
    h.translate(Vector(0, dy, 0))
    return s, h, dy


HORN_DZ = 13.8              # round horn: bottom at model z 10.8 (just above the gearbox top 10.6), top 17.1
SERVO_EAR = dict(z0=0.0, z1=2.9, holes_x=(-34.75, 14.75), holes_y=(-5.0, 5.0), body_x=(-30.3, 10.3), body_y=10.25)
# ABS fits (clapets v7 coupons 2026-11-12 + design-principles): bearing seat +0.2 (608: Ø22.2), round horn pocket Ø21.4
# (disc Ø20.8 x 2.5, boss Ø9.2 x 0.8, hub Ø9 x 3) + 4 x M2 Ø2.5 at r 7.2 (T9), nut pocket M3 6.0 x 6.9 x 2.8 / M4 7.4 x
# 8.4 x 3.6, clearance holes +0.1..0.2 (ABS shrinks holes)
FIT = dict(seat_625=16.2, horn_pocket=21.4, horn_boss=9.8, horn_t=2.5, horn_boss_t=0.8, m2=2.5, m3=3.5, m4=4.6, m5=5.6,
           pin5_press=5.0, nut_m3=(6.0, 6.9, 2.8), nut_m4=(7.4, 8.4, 3.6))


def flip_head(px, pz, arm_y=10.0, horn_face_y=-5.0, y625=(8.0, 13.0), mount_plate_t=5.0):
    """Flip head at the pick pose, pivot (px, pz), arm in the plane y ~ 0. Printed parts drawn for real.
    ARM group (rotates):
      ARM_PRINTED  one printed part: hub Ø24 x arm_y (round horn screwed on its -y face, 4 x M2 into the horn holes at
                   r 7.2; Ø5 shaft pressed in a blind hole from +y), bar 14 thick, cup (seat MAG_SEAT, magnet face 4 mm
                   proud, M4 hole for the stud + nut)
      SHAFT_5      Ø5 steel pin, hub -> 625 · SERVO_HORN (real) · MAGNET_D30
    BODY group (rides the lift):
      SERVO_MG996R (real, body DOWN, shaft +y) · BEARING_625
      SERVO_MOUNT  printed: plate under the servo ears (body cut-out, 2 ear screws M3) + 625 cheek (+y) + the bar that
                   joins them UNDER the pivot (the arm and the Grail never reach there). The caller fuses its own base
                   to it (x < the servo plate's XMin).
    Returns (arm parts, body parts, info)."""
    arm, body = {}, {}
    zf = G_H
    # ---- servo (body down)
    sv, hn, dy = servo_mg996r(px, pz, horn_face_y, body="-z")
    arm["SERVO_HORN"] = hn
    body["SERVO_MG996R"] = sv
    # model -> world for the servo ('-z' rows): world x = px + model y, world y = model z + dy, world z = pz + model x
    ear_y0, ear_y1 = SERVO_EAR["z0"] + dy, SERVO_EAR["z1"] + dy
    bx0, bx1 = SERVO_EAR["body_x"]
    # ---- ARM_PRINTED: hub from the horn disc's top face to +arm_y/2; collar around the disc with the Ø21.4 pocket
    y_dt = horn_face_y - FIT["horn_boss_t"]              # horn disc top (the boss sits above it)
    y_db = y_dt - FIT["horn_t"]                          # disc bottom
    hub = cyl(12, arm_y / 2 - y_dt, (px, y_dt, pz), (0, 1, 0))
    collar = cyl(FIT["horn_pocket"] / 2 + 2.5, y_dt - y_db + 1.0, (px, y_db - 1.0, pz), (0, 1, 0))
    cup_h = MAG_L - 4.0
    zc0 = zf + 4.0                                   # cup rim (magnet face 4 mm proud)
    cup = cyl(MAG_SEAT / 2 + 3, cup_h + 4, (X_PICK, 0, zc0), (0, 0, 1))
    ztop = zc0 + cup_h + 4
    barp = bar((px, pz), (X_PICK, ztop - 7), 14.0, -arm_y / 2, arm_y / 2)
    armp = hub.fuse(collar).fuse(barp).fuse(cup).removeSplitter()
    armp = armp.cut(cyl(MAG_SEAT / 2, cup_h + 0.1, (X_PICK, 0, zc0 - 0.1), (0, 0, 1)))       # magnet seat
    armp = armp.cut(cyl(FIT["m4"] / 2, 10, (X_PICK, 0, zc0 + cup_h - 1), (0, 0, 1)))           # M4 stud hole
    nw, nl, nt = FIT["nut_m4"]
    armp = armp.cut(box(X_PICK - nw / 2, X_PICK + nw / 2, -nl / 2 - 6, nl / 2, ztop - nt - 0.6, ztop - 0.6))  # M4 nut pocket, open -y
    armp = armp.cut(cyl(FIT["horn_pocket"] / 2, y_dt - y_db + 1.0, (px, y_db - 1.0, pz), (0, 1, 0)))   # horn disc pocket
    armp = armp.cut(cyl(FIT["horn_boss"] / 2, FIT["horn_boss_t"] + 0.5, (px, y_dt - 0.01, pz), (0, 1, 0)))  # boss recess
    armp = armp.cut(cyl(FIT["pin5_press"] / 2, 6.0, (px, arm_y / 2 - 6.0, pz), (0, 1, 0)))       # Ø5 pin, press, from +y
    for (a_, b_) in ((0, 7.2), (7.2, 0), (0, -7.2), (-7.2, 0)):                                 # 4 x M2 x 12 into the horn
        armp = armp.cut(cyl(FIT["m2"] / 2, 30, (px + a_, y_db - 2, pz + b_), (0, 1, 0)))
        armp = armp.cut(cyl(2.2, 1.6, (px + a_, arm_y / 2 - 1.5, pz + b_), (0, 1, 0)))         # head below the +y face
    arm["ARM_PRINTED"] = armp.removeSplitter()
    arm["SHAFT_5"] = cyl(2.5, y625[1] + 2 - (arm_y / 2 - 6.0), (px, arm_y / 2 - 6.0, pz), (0, 1, 0))
    arm["MAGNET_D30"] = magnet_down(X_PICK, zf)
    # ---- SERVO_MOUNT: plate under the ears (servo side of the ears = -y of the ear flange)
    t = mount_plate_t
    sp_y0, sp_y1 = ear_y0 - t, ear_y0
    sx0, sx1 = px - SERVO_EAR["body_y"] - 4, px + SERVO_EAR["body_y"] + 4
    sz0, sz1 = pz + SERVO_EAR["holes_x"][0] - 6, pz + SERVO_EAR["holes_x"][1] + 6
    plate = box(sx0, sx1, sp_y0, sp_y1, sz0, sz1)
    plate = plate.cut(box(px - SERVO_EAR["body_y"] - 0.3, px + SERVO_EAR["body_y"] + 0.3, sp_y0 - 1, sp_y1 + 1,
                          pz + bx0 - 0.3, pz + bx1 + 0.3))                                       # body cut-out
    nw, nl, nt = FIT["nut_m3"]
    for hx in SERVO_EAR["holes_x"]:
        for hy in SERVO_EAR["holes_y"]:
            if hy < 0:                                                                            # 2 M3 x 12 (one per ear)
                plate = plate.cut(cyl(FIT["m3"] / 2, t + 2, (px + hy, sp_y0 - 1, pz + hx), (0, 1, 0)))
                plate = plate.cut(box(px + hy - nw / 2, px + hy + nw / 2, sp_y0 - 0.1, sp_y0 + nt, pz + hx - nl / 2,
                                      pz + hx + nl / 2))                                         # nut pocket, -y face
    # cheek with the 625 (+y), joined under the pivot to the servo plate
    zb0, zb1 = pz - 46, pz - 40
    cheek = box(px - 12, px + 5.5, y625[0] - 1, y625[1], zb0, pz + 9).fuse(
        cyl(10.5, y625[1] + 1 - y625[0], (px, y625[0] - 1, pz), (0, 1, 0)))
    joiner = box(px - 12, px + 5.5, sp_y0, y625[1], zb0, zb1)
    down = box(px - 12, px + 5.5, sp_y0, sp_y1, zb0, sz0 + 1) if zb0 < sz0 else None
    mount = plate.fuse(cheek).fuse(joiner)
    if down is not None:
        mount = mount.fuse(down)
    mount = mount.cut(cyl(FIT["seat_625"] / 2, 30, (px, y625[0], pz), (0, 1, 0)))              # 625 seat Ø16.2, open +y
    mount = mount.cut(cyl(5.0, 30, (px, y625[0] - 5, pz), (0, 1, 0)))                            # lip hole Ø10 (outer ring only)
    mount = mount.cut(cyl(3.0, 30, (px, -10, pz), (0, 1, 0)))                                   # shaft clearance
    body["SERVO_MOUNT"] = mount.removeSplitter()
    body["BEARING_625"] = cyl(8, 5, (px, y625[0], pz), (0, 1, 0)).cut(cyl(2.5, 7, (px, y625[0] - 1, pz), (0, 1, 0)))
    info = dict(dy=dy, ear_y=(ear_y0, ear_y1), plate_y=(sp_y0, sp_y1), plate_x=(sx0, sx1), plate_z=(sz0, sz1),
                cup_top=ztop, joiner_z=(zb0, zb1))
    return arm, body, info


def robot_context(slot=None):
    """Reference solids: body (ghost box up to the roof plate), roof strip (with slot), right wheel.
    On base_330_js only the roof strip: the real base parts are loaded from its assembly (flipper_fc)."""
    out = {}
    if BASE == "b330":
        roof = box(-FACE, FACE, -ROOF_Y, ROOF_Y, ROOF_BOT, ROOF_TOP)
        if slot:
            roof = roof.cut(box(slot[0], slot[1], slot[2], slot[3], ROOF_BOT - 1, ROOF_TOP + 1))
        out["CTX_ROOF_STRIP"] = roof
        return out
    out["CTX_BODY_ghost"] = box(-FACE, FACE, -BODY_Y, BODY_Y, 21, ROOF_BOT).cut(
        box(BAY["x0"], BAY["x1"] + 1, -BAY["y"], BAY["y"], BAY["z0"], BAY["z1"] + 1))
    roof = box(-FACE, FACE, -ROOF_Y, ROOF_Y, ROOF_BOT, ROOF_TOP)
    if slot:
        roof = roof.cut(box(slot[0], slot[1], slot[2], slot[3], ROOF_BOT - 1, ROOF_TOP + 1))
    out["CTX_ROOF"] = roof
    out["CTX_WHEEL_R"] = cyl(WHEEL["r"], WHEEL["x1"] - WHEEL["x0"], (WHEEL["x0"], 0, WHEEL["z"]), (1, 0, 0))
    return out


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
