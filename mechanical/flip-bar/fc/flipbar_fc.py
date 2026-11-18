# flipbar_fc.py - FreeCAD model of the single-bar flip (Maatoug, 2026-11-14) + collision / height sweep over the
# whole range of motion (hard stop to hard stop).
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" flipbar_fc.py   (from mechanical/flip-bar/fc/, ~3-6 min)
# Writes ../CAD/flipbar.FCStd, ../CAD/flipbar.step, ../CAD/parts/*.step, ../collision_report.txt.
# Same frame and four-bar as Ayoub's flip-6cups (see flipbar_params.py). Real parts: 17HS4401S, 608ZZ, DP-S30,
# Ender endstops, 12 V pumps + vent valves, base_330. Cup stations: clapets-v8 B_STATION_TPU (same TPU part) on a
# printed spacer, under a Barbatronic-style support ring.
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flipbar_params as P  # noqa: E402

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402

V = App.Vector
ROOT = os.path.normpath(os.path.join(HERE, ".."))
BASE_STEP = os.path.normpath(os.path.join(ROOT, "..", "base_330", "base_330.step"))
RHO = {"alu": 2.70e-3, "steel": 7.85e-3, "abs": 0.75e-3, "tpu": 1.2e-3, "hose": 0.73e-3}   # g/mm3 (ABS ~50 % infill;
# hose = PU tube 4 x 2.5 drawn as a solid Ø4)


def rot_y(deg):
    """Turns the XZ plane counter-clockwise (x right, z up) by deg: about -Y."""
    return App.Rotation(V(0, -1, 0), deg)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_y(x, z, d, y0, y1):
    return Part.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))


def tube_y(x, z, d_out, d_in, y0, y1):
    return cyl_y(x, z, d_out, y0, y1).cut(cyl_y(x, z, d_in, y0 - 1, y1 + 1))


def poly_y(pts, y0, y1):
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, y1 - y0, 0))


def rounded_rect_xz(x0, x1, z0, z1, r, y0, y1, r_top=None):
    rt = r if r_top is None else r_top
    core = box(x0, x1, y0, y1, z0 + r, z1 - rt).fuse(box(x0 + r, x1 - r, y0, y1, z0, z0 + r))
    core = core.fuse(box(x0 + rt, x1 - rt, y0, y1, z1 - rt, z1))
    for cx, cz, rr in ((x0 + r, z0 + r, r), (x1 - r, z0 + r, r), (x0 + rt, z1 - rt, rt), (x1 - rt, z1 - rt, rt)):
        core = core.fuse(cyl_y(cx, cz, 2 * rr, y0, y1))
    return core.removeSplitter()


def spline_prism(pts, y0, y1):
    """Closed smooth (periodic B-spline) outline through (x, z) points, extruded from y0 to y1."""
    bs = Part.BSplineCurve()
    bs.interpolate(Points=[V(x, y0, z) for x, z in pts], PeriodicFlag=True)
    return Part.Face(Part.Wire([bs.toShape()])).extrude(V(0, y1 - y0, 0))


def slot_y(a, b, w, y0, y1):
    """Round-ended slot from point a to b (x, z), width w, through y0..y1."""
    L = math.dist(a, b)
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    s = box(0, L, y0, y1, -w / 2, w / 2).fuse(cyl_y(0, 0, w, y0, y1)).fuse(cyl_y(L, 0, w, y0, y1))
    return s.removeSplitter().transformGeometry(App.Placement(V(a[0], 0, a[1]), rot_y(ang)).toMatrix())


def link_plate(length, y0, y1):
    """Smooth plate: hubs blended into the web (flipbar_params.link_outline), lightening slot."""
    s = spline_prism(P.link_outline(length), y0, y1)
    sl = P.link_slot(length)
    return s.cut(slot_y((sl[0], 0), (sl[1], 0), sl[2], y0 - 1, y1 + 1)) if sl else s


def b608(x, z, y0):
    """608ZZ: 8 x 22 x 7."""
    return tube_y(x, z, 22.0, 8.0, y0, y0 + 7.0)


# ---------------------------------------------------------------- fasteners (drawn, swept, counted) - 2026-11-17
BOM = {}                                  # label -> quantity, filled while the parts are built
HEADS = {"cap": {3: (5.5, 3.0), 5: (8.5, 5.0)}, "button": {3: (5.7, 1.65), 4: (7.6, 2.2), 5: (9.5, 2.75)},
         "set": {3: (0.0, 0.0)}, "hex": {8: (13.0, 5.3)}}
NUTS = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.7), 8: (13.0, 6.5)}     # across flats, thickness
THIN_NUT = {8: 4.0}                       # DIN 439
NYLOC = {8: 8.0}                          # DIN 985
HEAD_NAME = {"cap": "socket head", "button": "button head", "set": "set screw", "hex": "hex bolt"}


def _count(label, n=1):
    BOM[label] = BOM.get(label, 0) + n


def screw(p, d, length, m=3, head="cap", count=True):
    """Screw with its head seat at point p (x, y, z), shank along the unit vector d. No thread, ISO sizes."""
    p, d = V(*p), V(*d)
    hd, hh = HEADS[head][m]
    s = Part.makeCylinder(m / 2.0, length, p, d)
    if head == "hex":
        r = hd / math.sqrt(3)
        hx = Part.Face(Part.makePolygon([V(r * math.cos(math.pi * i / 3), r * math.sin(math.pi * i / 3), 0)
                                         for i in range(7)])).extrude(V(0, 0, hh))
        s = s.fuse(hx.transformGeometry(App.Placement(p, App.Rotation(V(0, 0, 1), d * -1.0)).toMatrix()))
    elif hh:
        s = s.fuse(Part.makeCylinder(hd / 2.0, hh, p, d * -1.0))
    if count:
        _count("M%d x %d %s" % (m, length, HEAD_NAME[head]))
    return s


def hexnut(p, d, m=3, count=True, corner_y=False, thin=False, nyloc=False):
    """Nut centred on p, axis along d. Built along +Z: corners on local X, or on local Y with corner_y (to match the pocket)."""
    af, th = NUTS[m]
    if thin:
        th = THIN_NUT[m]
    if nyloc:
        th = NYLOC[m]
    r = af / math.sqrt(3)
    k0 = 0.5 if corner_y else 0.0
    n = Part.Face(Part.makePolygon([V(r * math.cos(math.pi * (i + k0) / 3), r * math.sin(math.pi * (i + k0) / 3), -th / 2)
                                    for i in range(7)])).extrude(V(0, 0, th))
    n = n.cut(Part.makeCylinder(m / 2.0, th + 2, V(0, 0, -th / 2 - 1), V(0, 0, 1)))
    n = n.transformGeometry(App.Placement(V(*p), App.Rotation(V(0, 0, 1), V(*d))).toMatrix())
    if count:
        _count("M%d %snut" % (m, "thin " if thin else "nyloc " if nyloc else ""))
    return n


def turn(shape, x, z, deg):
    """Place a shape built at the origin: turn it by deg in the XZ plane, then move its origin to (x, z)."""
    return shape.transformGeometry(App.Placement(V(x, 0, z), rot_y(deg)).toMatrix())


def housing(y0, y1, plate_at_y0):
    """Printed 608 housing on a frame plate (crank shaft). Seat D22.2 + lead-in at the open mouth; two ears, each with
    an M3 x 12 from the plate's outer face into a nut pocket that opens to free air at the ear tip."""
    cx, cz = P.O1
    e, w = P.HOUSING_EAR_R, P.HOUSING_EAR_W
    nw, nl, nt = P.NUT3
    s = cyl_y(cx, cz, P.HOUSING_D, y0, y1).fuse(slot_y((cx - e, cz), (cx + e, cz), w, y0, y1)).removeSplitter()
    s = s.cut(cyl_y(cx, cz, P.BRG_SEAT_D, y0 - 1, y1 + 1))
    r, h = P.BRG_SEAT_D / 2, P.BRG_LEAD
    if plate_at_y0:
        s = s.cut(Part.makeCone(r, r + h, h + 0.01, V(cx, y1 - h, cz), V(0, 1, 0)))
        ny0 = y0 + P.HOUSING_NUT_FLOOR
    else:
        s = s.cut(Part.makeCone(r + h, r, h + 0.01, V(cx, y0 - 0.01, cz), V(0, 1, 0)))
        ny0 = y1 - P.HOUSING_NUT_FLOOR - nt
    for sx in (-1, 1):
        s = s.cut(cyl_y(cx + sx * e, cz, P.M3_CLEAR, y0 - 1, y1 + 1))
        xa, xb = cx + sx * (e - nl / 2), cx + sx * (e + w / 2 + 1)
        s = s.cut(box(min(xa, xb), max(xa, xb), ny0, ny0 + nt, cz - nw / 2, cz + nw / 2))
    return s, ny0 + nt / 2


def anchor():
    """Printed zip-tie anchor, built at the origin: L along +X, W across Z, H along +Y (mounting face at y 0).
    1 mm chamfer on the 4 outside corners; M3 socket head sunk 3 mm; tie tunnel 4 x 2 under a 2.5 mm bridge."""
    L, W, H = P.ANCHOR
    c = 1.0
    s = poly_y([(c, -W / 2), (L - c, -W / 2), (L, -W / 2 + c), (L, W / 2 - c), (L - c, W / 2), (c, W / 2), (0, W / 2 - c),
                (0, -W / 2 + c)], 0, H)
    s = s.cut(cyl_y(4.5, 0, P.M3_CLEAR, -1, H + 1)).cut(cyl_y(4.5, 0, 6.2, H - 3, H + 1))
    return s.cut(box(10, 14, 1.5, 3.5, -W / 2 - 1, W / 2 + 1))


def anchors_on(anchors, y_face, front):
    """Anchors + their M3 x 8 on a plate face at y_face; front = the anchor stands towards +Y."""
    L, W, H = P.ANCHOR
    out, scr = [], []
    for (x, z, a), (sx, sz) in zip(anchors, P.anchor_screws(anchors)):
        s = anchor()
        if not front:
            s = s.mirror(V(0, 0, 0), V(0, 1, 0))
        s.translate(V(0, y_face, 0))
        out.append(turn(s, x, z, a))
        d = 1 if front else -1
        scr.append(screw((sx, y_face + d * (H - 3), sz), (0, -d, 0), 8))
    return out, scr


# ---------------------------------------------------------------- joints on flat links (2026-11-18)
def sleeve_y(x, z, y0, y1, d=None, bore=P.SHAFT_BORE):
    """Printed sleeve on a Ø8 shaft / bolt: touches the 608 inner race only."""
    return tube_y(x, z, P.SLEEVE_D if d is None else d, bore, y0, y1)


def link_hub(x, toward, y_plate, d):
    """Printed bearing hub on a flat link (link frame, pin at (x, 0)); the SAME part at the 3 joints.
    d = +1: on the link's front face, -1: on its back face. toward = +-1: the tongue runs that way along the link.
    Two 608 in a Ø22.2 seat that opens on the link (lead-in there): the link's Ø20 hole closes that side, the 2 mm lip
    at the far end closes the other. Tongue: 2 x M3 x 10, heads on the tongue, into M3 tapped in the link."""
    L, th = P.LINK_HUB_TONGUE
    w, c = P.LINK_W / 2, 1.0
    ya, yb = sorted((y_plate, y_plate + d * (14.0 + P.LINK_HUB_LIP)))
    ta, tb = sorted((y_plate, y_plate + d * th))
    sa, sb = sorted((y_plate - d * 1.0, y_plate + d * 14.0))
    xt = x + toward * L
    tongue = poly_y([(x, -w), (xt - toward * c, -w), (xt, -w + c), (xt, w - c), (xt - toward * c, w), (x, w)], ta, tb)
    s = cyl_y(x, 0, P.LINK_HUB_BODY_D, ya, yb).fuse(tongue).removeSplitter()
    s = s.cut(cyl_y(x, 0, P.BRG_SEAT_D, sa, sb)).cut(cyl_y(x, 0, P.LINK_HUB_LIP_BORE, ya - 1, yb + 1))
    r, h = P.BRG_SEAT_D / 2, P.BRG_LEAD
    if d > 0:
        s = s.cut(Part.makeCone(r + h, r, h + 0.01, V(x, y_plate - 0.01, 0), V(0, 1, 0)))
    else:
        s = s.cut(Part.makeCone(r, r + h, h + 0.01, V(x, y_plate - h, 0), V(0, 1, 0)))
    for q in P.LINK_HUB_SCREWS:
        s = s.cut(cyl_y(x + toward * q, 0, P.M3_CLEAR, ta - 1, tb + 1))
    return s


def link_hub_screws(x, toward, y_plate, d):
    return [screw((x + toward * q, y_plate + d * P.LINK_HUB_TONGUE[1], 0), (0, -d, 0), 10) for q in P.LINK_HUB_SCREWS]


def tube_path(pts, d):
    """Round tube through (x, y, z) points: straight runs + a ball at each corner."""
    out = []
    for a, b in zip(pts, pts[1:]):
        a, b = V(*a), V(*b)
        out.append(Part.makeCylinder(d / 2, (b - a).Length, a, b - a))
    out += [Part.makeSphere(d / 2, V(*q)) for q in pts[1:-1]]
    s = out[0]
    for o in out[1:]:
        s = s.fuse(o)
    return s


# ---------------------------------------------------------------- involute spur gear (axis along Y)
def involute_gear(z, m, y0, y1, bore, phase=0.0, backlash=P.BACKLASH, pa=20.0, n=8):
    """Gear centred on the local origin, axis +Y, teeth in the XZ plane. phase (rad) = angle of tooth 0's centre."""
    a = math.radians(pa)
    r = m * z / 2; rb = r * math.cos(a); ra = r + m; rf = r - 1.25 * m
    inv = lambda x: math.tan(x) - x
    psi = (math.pi * m / 2 - backlash / 2) / (2 * r)          # half tooth angle at the pitch circle

    def beta(rho):
        return psi + inv(a) - inv(math.acos(min(1.0, rb / rho)))

    r0 = max(rb, rf)
    pts = []
    for k in range(z):
        c = phase + 2 * math.pi * k / z
        right = [(rho, c - beta(rho)) for rho in [r0 + (ra - r0) * i / n for i in range(n + 1)]]
        left = [(rho, c + beta(rho)) for rho in [ra - (ra - r0) * i / n for i in range(n + 1)]]
        if rf < rb:   # radial flank below the base circle (pinion)
            right = [(rf, c - beta(rb))] + right
            left = left + [(rf, c + beta(rb))]
        tip = [(ra, c - beta(ra) + (2 * beta(ra)) * i / 3) for i in range(1, 3)]
        pts += right + tip + left
        nxt = c + 2 * math.pi / z - (beta(rb) if rf < rb else beta(r0))
        pts += [(rf, left[-1][1] + (nxt - left[-1][1]) * i / 3) for i in range(1, 3)]
    xz = [(rho * math.cos(t), rho * math.sin(t)) for rho, t in pts]
    g = poly_y(xz, y0, y1)
    return g.cut(cyl_y(0, 0, bore, y0 - 1, y1 + 1))


def mesh_phase(z, toward, tooth=True):
    """Phase so a tooth (or a gap) points along the angle `toward`."""
    return toward + (0.0 if tooth else math.pi / z)


# ---------------------------------------------------------------- fixed parts (robot frame)
def frame_plate(y0, y1, holes, x1=None):
    x0 = P.FRAME_X[0]
    x1 = P.FRAME_X[1] if x1 is None else x1
    s = rounded_rect_xz(x0, x1, P.BASE_TOP, P.FRAME_Z1, 8, y0, y1, r_top=14)
    for x, z, d in holes:
        s = s.cut(cyl_y(x, z, d, y0 - 1, y1 + 1))
    return s


def switch(angle_deg, away, r=55.0):
    """Ender endstop (switch 20 x 10 x 6.5 on a 1.6 mm PCB) on the column front, crank layer, at angle (deg) / r.
    2 x M3 x 6 button head through the PCB, tapped in the column, on the side away from the crank (away = +-1).
    Returns (switch, [screws], [(x, z) of the tapped holes])."""
    y = P.COL[1]
    sw = box(-10, 10, y, y + 1.6 + 6.5, -5, 5).fuse(box(-20, 14, y, y + 1.6, -8, 8))
    a = math.radians(angle_deg)
    cx, cz = P.O1[0] + r * math.cos(a), P.O1[1] + r * math.sin(a)
    m = App.Placement(V(cx, 0, cz), rot_y(angle_deg)).toMatrix()
    scr, holes = [], []
    for zl in P.SWITCH_SCREW_Z:
        xl, zl = P.SWITCH_SCREW_X, away * zl
        sw = sw.cut(cyl_y(xl, zl, P.M3_CLEAR, y - 1, y + 2.6))
        scr.append(screw((xl, y + 1.6, zl), (0, -1, 0), 6, head="button").transformGeometry(m))
        dx, dz = P.rot(xl, zl, a)
        holes.append((cx + dx, cz + dz))
    return sw.transformGeometry(m), scr, holes


def bumper(angle_deg):
    """Hard stop: rubber sleeve Ø10 x 4 on an M4 x 16 from the column's back face, locked by an M4 nut on the front
    face (the nut hides inside the sleeve's radius). Returns (rubber, [screw, nut], column hole)."""
    a = math.radians(angle_deg)
    x, z = P.O1[0] + P.STOP_R * math.cos(a), P.O1[1] + P.STOP_R * math.sin(a)
    rubber = tube_y(x, z, P.STOP_D, 4.0, P.COL[1] + NUTS[4][1], P.CRANK[1] + 2)
    fast = [screw((x, P.COL[0], z), (0, 1, 0), 16, m=4, head="button"),
            hexnut((x, P.COL[1] + NUTS[4][1] / 2, z), (0, 1, 0), m=4)]
    return rubber, fast, (x, z, P.M4_CLEAR)


def nema17():
    mx, mz = P.M_POS
    b = P.MOTOR["body"] / 2; y1 = P.REAR[0]
    body = box(mx - b, mx + b, y1 - P.MOTOR["length"], y1, mz - b, mz + b)
    boss = cyl_y(mx, mz, P.MOTOR["flange_boss_d"], y1, y1 + P.MOTOR["flange_boss_h"])
    return body.fuse(boss)


def fixed_parts():
    parts = {}
    parts["table"] = box(-500, 500, -350, 450, -2, 0)
    if os.path.exists(BASE_STEP):
        b = Part.read(BASE_STEP); b.translate(V(0, 0, P.BASE_Z)); parts["base_330"] = b
    else:
        parts["base_330"] = box(-165, 165, -140, 140, P.BASE_Z, P.BASE_TOP)
    parts["wheels"] = Part.makeCylinder(45, 20, V(83.8, 0, 45), V(1, 0, 0)).fuse(
        Part.makeCylinder(45, 20, V(-83.8, 0, 45), V(-1, 0, 0)))
    x0, x1 = P.FRAME_X
    fx, tapped, fb = [], [], []
    so = [(x, z, 5.5) for x, z in P.STANDOFFS]
    so += [(P.O1[0] + sx * P.HOUSING_EAR_R, P.O1[1], P.M3_CLEAR) for sx in (-1, 1)]     # housing screws
    # column: crank shaft hole Ø15 (bearing in the housing behind), O2 axle Ø8
    col_holes = [(P.O1[0], P.O1[1], P.PLATE_BRG_HOLE), (P.O2[0], P.O2[1], 8)]
    rear_holes = [(P.O1[0], P.O1[1], P.PLATE_BRG_HOLE), (P.O2[0], P.O2[1], 8), (P.M_POS[0], P.M_POS[1], 22.5)]
    # switches (M3 x 6 tapped in the column) + hard stops (M4 x 16 + nut) on the column front, crank layer
    sg = math.copysign(1, P.SWEEP)
    a0, a1 = math.degrees(P.PHI0), math.degrees(P.PHI1)
    for name, ang, away in (("switch_home", a0 - sg * P.HOME_SWITCH_DEG, -sg), ("switch_upright", a1 + sg * P.END_SWITCH_DEG, sg)):
        parts[name], scr, holes = switch(ang, away)
        tapped += scr
        col_holes += [(x, z, P.M3_TAP) for x, z in holes]
    stop_off = math.degrees(math.atan((P.LINK_W / 2 + P.STOP_D / 2) / P.STOP_R)) + P.STOP_PAST_DEG
    for name, ang in (("stop_home", a0 - sg * stop_off), ("stop_upright", a1 + sg * stop_off)):
        parts[name], fs, hole = bumper(ang)
        fx += fs
        col_holes.append(hole)
    # angle brackets behind each plate -> base plate (column: clear of the sector, x < -77 and x > 7). One M4 x 16 +
    # nut per leg: head on the plate's front face / under the base, nut on the bracket
    bk = []
    for holes, (yp0, yp1), xr in ((col_holes, P.COL, P.COLUMN_X1), (rear_holes, P.REAR, x1)):
        for bx0, bx1 in ((x0 + 2, x0 + 22), (xr - 22, xr - 2)):
            xc, zs, ys = (bx0 + bx1) / 2, P.BASE_TOP + P.BRACKET_SCREW, yp0 - P.BRACKET_SCREW
            b = box(bx0, bx1, yp0 - 25, yp0, P.BASE_TOP, P.BASE_TOP + 4).fuse(box(bx0, bx1, yp0 - 4, yp0, P.BASE_TOP, P.BASE_TOP + 25))
            b = b.cut(cyl_y(xc, zs, P.M4_CLEAR, yp0 - 5, yp0 + 1))
            bk.append(b.cut(Part.makeCylinder(P.M4_CLEAR / 2, 6, V(xc, ys, P.BASE_TOP - 1), V(0, 0, 1))))
            holes.append((xc, zs, P.M4_CLEAR))
            fx.append(screw((xc, yp1, zs), (0, -1, 0), 16, m=4, head="button"))
            fx.append(hexnut((xc, yp0 - 4 - NUTS[4][1] / 2, zs), (0, 1, 0), m=4))
            fb.append(screw((xc, ys, P.BASE_Z), (0, 0, 1), 16, m=4, head="button"))
            fb.append(hexnut((xc, ys, P.BASE_TOP + 4 + NUTS[4][1] / 2), (0, 0, 1), m=4))
    parts["brackets"] = Part.makeCompound(bk)
    parts["fasteners_base"] = Part.makeCompound(fb)        # through the base plate: 4 holes to drill in base_330
    parts["column"] = frame_plate(*P.COL, col_holes + so, x1=P.COLUMN_X1)
    mh = P.MOTOR["holes"] / 2
    parts["rear_plate"] = frame_plate(*P.REAR, rear_holes + so +
                                      [(x, z, P.M3_TAP) for x, z in P.anchor_screws(P.REAR_ANCHORS)] +
                                      [(P.M_POS[0] + sx * mh, P.M_POS[1] + sz * mh, 3.4) for sx in (1, -1) for sz in (1, -1)])
    parts["standoffs"] = Part.makeCompound([tube_y(x, z, 10, 5.5, P.REAR[1], P.COL[0]) for x, z in P.STANDOFFS])
    hs, br = [], []
    # one printed housing per plate (crank shaft): M3 x 12, head on the plate's outer face, nut in the ear pocket
    for (y0, y1), at_y0, y_head in ((P.HOUSING_R, True, P.REAR[0]), (P.HOUSING_C, False, P.COL[1])):
        h, y_nut = housing(y0, y1, at_y0)
        hs.append(h)
        br.append(b608(P.O1[0], P.O1[1], y0))
        for sx in (-1, 1):
            x = P.O1[0] + sx * P.HOUSING_EAR_R
            fx.append(screw((x, y_head, P.O1[1]), (0, 1 if at_y0 else -1, 0), 12, head="button"))
            fx.append(hexnut((x, y_nut, P.O1[1]), (0, 1, 0)))
    parts["housings"] = Part.makeCompound(hs)
    fx += [screw((P.M_POS[0] + sx * mh, P.REAR[1], P.M_POS[1] + sz * mh), (0, -1, 0), 8, head="button")
           for sx in (1, -1) for sz in (1, -1)]     # motor: 4 x M3 x 8 from the rear plate's front face into the motor
    for x, z in P.STANDOFFS:                         # M5 x 55 through column + standoff + rear plate, nut on the back
        fx.append(screw((x, P.COL[1], z), (0, -1, 0), 55, m=5, head="button"))
        fx.append(hexnut((x, P.REAR[0] - NUTS[5][1] / 2, z), (0, 1, 0), m=5))
    an, sc = anchors_on(P.REAR_ANCHORS, P.REAR[0], False)
    parts["anchors_fixed"] = Part.makeCompound(an)
    _count("Zip-tie anchor (printed ABS)", len(an))
    parts["bearings_fixed"] = Part.makeCompound(br)
    # rocker ground axle: M8 x 80 hex bolt (DIN 931: the bearings sit on its plain shank) from the FRONT: head inside
    # the rocker's Ø20 hole (13 mm socket), through the rocker's two 608, a printed sleeve, the column, a printed tube
    # between the plates (a 5th standoff), the rear plate; washer + nyloc nut on the back. The nut clamps the whole
    # stack -> the axle is fixed and the rocker is held both ways along Y
    ox, oz = P.O2
    parts["shaft_O2"] = screw((ox, P.ROCK_HUB[1], oz), (0, -1, 0), 80, m=8, head="hex")
    parts["sleeves_fixed"] = Part.makeCompound([tube_y(ox, oz, P.O2_TUBE_D, 8.4, P.REAR[1], P.COL[0]),
                                                sleeve_y(ox, oz, P.COL[1], P.ROCK_HUB[0])])
    fx.append(tube_y(ox, oz, 16.0, 8.4, P.REAR[0] - 1.6, P.REAR[0]))
    _count("M8 washer")
    fx.append(hexnut((ox, P.REAR[0] - 1.6 - NYLOC[8] / 2, oz), (0, 1, 0), m=8, nyloc=True))
    parts["fasteners_fixed"] = Part.makeCompound(fx)
    parts["fasteners_tapped"] = Part.makeCompound(sc + tapped)   # M3 tapped in the plates (thread = expected overlap)
    parts["motor"] = nema17()
    # vacuum: 3 pumps (one per cup) in one layer on the base, valves on top
    pitch = P.PUMP_D + 2.0
    pumps = [Part.makeCylinder(P.PUMP_D / 2, P.PUMP_L, V(P.PUMP_X0 + pitch / 2 + i * pitch, P.PUMP_Y0, P.BASE_TOP + 2 + P.PUMP_D / 2), V(0, 1, 0))
             for i in range(P.N_PUMPS)]
    vx, vy, vz = P.VALVE
    zt = P.BASE_TOP + 2 + P.PUMP_D
    valves = [box(P.PUMP_X0 + 2 + i * pitch, P.PUMP_X0 + 2 + i * pitch + vx, P.PUMP_Y0 + 10, P.PUMP_Y0 + 10 + vy, zt, zt + vz)
              for i in range(P.N_PUMPS)]
    parts["pumps"] = Part.makeCompound(pumps)
    parts["valves"] = Part.makeCompound(valves)
    return parts


# ---------------------------------------------------------------- moving parts, local frames
def crank_local():
    """Flat 6 mm plate (laser-cut): O1 at the origin, P1 along +X at R1. Holes only: Ø8 on the shaft, Ø20 under the P1
    hub, M3 tapped for the clamp hub (O1 side) and the bearing hub (P1 side)."""
    y0, y1 = P.CRANK
    s = link_plate(P.R1, y0, y1).cut(cyl_y(0, 0, 8, y0 - 1, y1 + 1)).cut(cyl_y(P.R1, 0, P.LINK_PIN_HOLE, y0 - 1, y1 + 1))
    for x in list(P.CRANK_CLAMP_SCREWS) + [P.R1 - q for q in P.LINK_HUB_SCREWS]:
        s = s.cut(cyl_y(x, 0, P.M3_TAP, y0 - 1, y1 + 1))
    return s


def crank_hub_local():
    return link_hub(P.R1, -1, P.CRANK[1], +1)


def crank_clamp_local():
    """Printed clamp hub on the crank's front face: split clamp on the Ø8 shaft (same clamp as the sector), slit and
    lug on the side away from P1; a tongue on the P1 side (the clamp's hinge side, so it still closes) takes 2 x M3 x 10,
    heads sunk 6 mm, into M3 tapped in the crank. This is what carries the torque from the shaft into the crank."""
    y0, y1 = P.CRANK_CLAMP
    w, c = P.LINK_W / 2, 1.0
    xt = P.CRANK_CLAMP_SCREWS[1] + 5.0
    s = cyl_y(0, 0, P.CRANK_CLAMP_D, y0, y1).fuse(
        poly_y([(4.5, -w), (xt - c, -w), (xt, -w + c), (xt, w - c), (xt - c, w), (4.5, w)], y0, y1))
    add, cuts = _clamp_lug(y0, y1)
    s = s.fuse(turn(add, 0, 0, 180.0)).removeSplitter()
    for k in cuts:
        s = s.cut(turn(k, 0, 0, 180.0))
    for x in P.CRANK_CLAMP_SCREWS:
        s = s.cut(cyl_y(x, 0, P.M3_CLEAR, y0 - 1, y1 + 1)).cut(cyl_y(x, 0, 6.2, y0 + 4.0, y1 + 1))
    return s.cut(cyl_y(0, 0, P.SHAFT_BORE, y0 - 1, y1 + 1))


def crank_sleeves_local():
    """Printed sleeves on the crank shaft: sector -> column bearing, column bearing -> crank (through the column's Ø15
    hole). With the sector's 1 mm boss they fill the shaft between the two 608, so nothing can slide along it."""
    return Part.makeCompound([sleeve_y(0, 0, P.GEAR[1], P.HOUSING_C[0]), sleeve_y(0, 0, P.HOUSING_C[1], P.CRANK[0])])


def crank_fasteners_local():
    f = [turn(clamp_fasteners(*P.CRANK_CLAMP), 0, 0, 180.0)]
    f += [screw((x, P.CRANK_CLAMP[0] + 4.0, 0), (0, -1, 0), 10) for x in P.CRANK_CLAMP_SCREWS]
    return Part.makeCompound(f + link_hub_screws(P.R1, -1, P.CRANK[1], +1))


def crank_bearings_local():
    return b608(P.R1, 0, P.CRANK_HUB[0]).fuse(b608(P.R1, 0, P.CRANK_HUB[0] + 7))


def crank_shaft_local():
    return cyl_y(0, 0, 8, P.HOUSING_R[0], P.CRANK_CLAMP[1])


def crank_gear_local():
    """Crank SECTOR gear (crank frame: P1 along +X): the teeth only where the pinion meets them over the travel,
    full hub disc on the shaft, two lightening windows."""
    y0, y1 = P.GEAR
    to_m = math.radians(P.PINION_ANG) - P.PHI0                     # pinion direction at the start, crank frame
    full = involute_gear(P.Z_WHEEL, P.GEAR_M, y0, y1, 8, mesh_phase(P.Z_WHEEL, to_m, True))
    b0, b1 = P.sector_span()
    R = P.GEAR_M * (P.Z_WHEEL / 2 + 2)
    pie = poly_y([(0.0, 0.0)] + [(R * math.cos(math.radians(b0 + (b1 - b0) * k / 48)),
                                  R * math.sin(math.radians(b0 + (b1 - b0) * k / 48))) for k in range(49)], y0 - 1, y1 + 1)
    g = full.common(pie).fuse(cyl_y(0, 0, P.SECTOR_HUB_D, y0, y1)).removeSplitter()
    g = g.fuse(cyl_y(0, 0, P.SLEEVE_D, P.HOUSING_R[1], y0)).removeSplitter()      # 1 mm boss against the rear 608's inner race
    r_in, r_out = P.SECTOR_HUB_D / 2 + 4, P.GEAR_M * (P.Z_WHEEL / 2 - 1.25) - 5
    mid = (b0 + b1) / 2
    for c0, c1 in ((b0 + 14, mid - 4), (mid + 4, b1 - 14)):     # windows, a 8-ish deg rib in the middle
        inner = [(r_in * math.cos(math.radians(c0 + (c1 - c0) * k / 24)), r_in * math.sin(math.radians(c0 + (c1 - c0) * k / 24)))
                 for k in range(25)]
        outer = [(r_out * math.cos(math.radians(c1 - (c1 - c0) * k / 24)), r_out * math.sin(math.radians(c1 - (c1 - c0) * k / 24)))
                 for k in range(25)]
        g = g.cut(poly_y(inner + outer, y0 - 1, y1 + 1))
    # 2026-11-17: split clamp on the D8 shaft (the v7 rod clamp): lug on the side without teeth, slot through the bore,
    # M3 x 12 across it, nut in a pocket on the lug's side face (it can't turn), head in a counterbore
    add, cuts = _clamp_lug()
    g = g.fuse(turn(add, 0, 0, mid + 180.0)).removeSplitter()
    for c in cuts:
        g = g.cut(turn(c, 0, 0, mid + 180.0))
    return g.cut(cyl_y(0, 0, P.SHAFT_BORE, y0 - 1, y1 + 1))


def _clamp_lug(y0=None, y1=None):
    """Split clamp lug on a Ø8 shaft, pointing +X: (solid to add, [cuts]). Slit through the bore, M3 x 12 across it,
    head in a counterbore, nut in a pocket; the pocket and the counterbore are cut out to free air through the hub."""
    if y0 is None:
        y0, y1 = P.GEAR
    ym = (y0 + y1) / 2
    r0, r1, w = P.CLAMP_LUG
    rs = (r0 + r1) / 2
    nw, nl, nt = P.NUT3
    add = box(r0, r1, y0, y1, -w / 2, w / 2)
    cuts = [box(0, r1 + 1, y0 - 1, y1 + 1, -0.6, 0.6),
            Part.makeCylinder(P.M3_CLEAR / 2, w + 2, V(rs, ym, -w / 2 - 1), V(0, 0, 1)),
            box(rs - nw / 2, rs + nw / 2, ym - nl / 2, ym + nl / 2, w / 2 - nt, w / 2 + 9),
            Part.makeCylinder(3.3, 11, V(rs, ym, -w / 2 - 9), V(0, 0, 1))]
    return add, cuts


def clamp_fasteners(y0, y1):
    """M3 x 12 + nut of a split clamp built by _clamp_lug (lug pointing +X)."""
    ym = (y0 + y1) / 2
    r0, r1, w = P.CLAMP_LUG
    rs = (r0 + r1) / 2
    return screw((rs, ym, -w / 2 + 2), (0, 0, 1), 12).fuse(hexnut((rs, ym, w / 2 - P.NUT3[2] + NUTS[3][1] / 2), (0, 0, 1), corner_y=True))


def sector_fasteners_local():
    b0, b1 = P.sector_span()
    return turn(clamp_fasteners(*P.GEAR), 0, 0, (b0 + b1) / 2 + 180.0)


def rocker_local():
    """Flat 6 mm plate (laser-cut): Ø20 hole + 2 x M3 tapped at each end (hubs on the back face), lightening slot."""
    y0, y1 = P.ROCK
    s = link_plate(P.R2, y0, y1)
    for x, sg in ((0, 1), (P.R2, -1)):
        s = s.cut(cyl_y(x, 0, P.LINK_PIN_HOLE, y0 - 1, y1 + 1))
        for q in P.LINK_HUB_SCREWS:
            s = s.cut(cyl_y(x + sg * q, 0, P.M3_TAP, y0 - 1, y1 + 1))
    return s


def rocker_hubs_local():
    return Part.makeCompound([link_hub(0, 1, P.ROCK[0], -1), link_hub(P.R2, -1, P.ROCK[0], -1)])


def rocker_fasteners_local():
    return Part.makeCompound(link_hub_screws(0, 1, P.ROCK[0], -1) + link_hub_screws(P.R2, -1, P.ROCK[0], -1))


def rocker_bearings_local():
    return Part.makeCompound([b608(x, 0, P.ROCK_HUB[0] + k * 7) for x in (0, P.R2) for k in (0, 1)])


def bar_local():
    """Bar in the bar frame (u -> x, v -> z), 5 mm aluminium: smooth outline (flipbar_params.bar_outline) + holes."""
    y0, y1 = P.BAR
    s = spline_prism(P.bar_outline(), y0, y1)
    for h in P.bar_holes():
        if h[0] == "circle":
            s = s.cut(cyl_y(h[1], h[2], h[3], y0 - 1, y1 + 1))
        else:
            s = s.cut(slot_y(h[1], h[2], h[3], y0 - 1, y1 + 1))
    return s


def bar_pins_local():
    """Bar pins = M8 x 30 hex bolts, head on the bar's front face (P2's head sits in a notch of the middle spacer).
    P1: printed sleeve + the two inner races clamped by a thin nut inside the crank's Ø20 hole -> holds the bar both
    ways along Y. P2: a full nut locks the bolt on the bar; the bolt only slides in the rocker's bearings (a second
    axial stop would fight the first). Returns (bolts, nuts, P1 sleeve)."""
    b = [screw((q[0], P.BAR[1], q[1]), (0, -1, 0), 30, m=8, head="hex") for q in (P.P1, P.P2)]
    n = [hexnut((P.P1[0], P.CRANK_HUB[0] - THIN_NUT[8] / 2, P.P1[1]), (0, 1, 0), m=8, thin=True),
         hexnut((P.P2[0], P.BAR[0] - NUTS[8][1] / 2, P.P2[1]), (0, 1, 0), m=8)]
    return Part.makeCompound(b), Part.makeCompound(n), sleeve_y(P.P1[0], P.P1[1], P.CRANK_HUB[1], P.BAR[0])


def hoses_local():
    """Ø4 hoses on the bar: out of each spacer slot (+u), up onto the anchor under it, then side by side down the +u
    flank to the bottom anchor. From there a free loop to the vent valves (not drawn; length in motion_report.txt)."""
    y_slot, y_top = P.BAR[1] + 3.0, P.hose_exit()[1]
    return Part.makeCompound([tube_path([(22.0, y_slot, cv), (u, y_slot, cv), (u, y_top, cv - 8.0), (u, y_top, P.HOSE_END_V)], 4.0)
                              for u, cv in zip(P.HOSE_U, P.CUP_V)])


def _bolts(cu, cv, y0, y1, d):
    return [cyl_y(cu + P.ST_BOLT_R * math.cos(math.radians(a)), cv + P.ST_BOLT_R * math.sin(math.radians(a)), d, y0, y1)
            for a in P.ST_BOLT_A]


def station_spacer(cu, cv):
    """Printed spacer Ø62 on the bar front: bore Ø40 (TPU hub travel + the cup's M5 elbow), tube slot towards +u."""
    y0, y1 = P.Y_SPACER
    s = tube_y(cu, cv, 2 * P.ST_R_OUT, 2 * P.ST_R_HOLE, y0, y1)
    s = s.cut(box(cu + P.ST_R_HOLE - 1, cu + P.ST_R_OUT + 1, y0 - 1, y0 + 6, cv - 3, cv + 3))      # Ø4 tube out
    for c in _bolts(cu, cv, y0 - 1, y1 + 1, 3.4):
        s = s.cut(c)
    if math.dist((cu, cv), P.P2) < P.ST_R_OUT + 10:      # the P2 bolt head sits under this spacer: notch open at the rim
        s = s.cut(cyl_y(P.P2[0], P.P2[1], 20.0, y0 - 1, y0 + HEADS["hex"][8][1] + 1.0))
    return s


def station_tpu(cu, cv):
    """clapets-v8 B_STATION_TPU (TPU 95A, same part): rim clamped, spring disc with 3 spiral slots, hub M5 + nut pocket."""
    yr0, yr1 = P.Y_RIM
    rim = tube_y(cu, cv, 2 * P.ST_R_RIM, 2 * P.ST_R_HOLE, yr0, yr1)
    disc = tube_y(cu, cv, 2 * (P.ST_R_HOLE + 0.5), 2 * (P.ST_R_HUB - 0.5), yr0, yr0 + P.DISC_T)
    for k in range(3):
        a0 = 2 * math.pi * k / 3
        inner, outer = [], []
        for i in range(25):
            t = i / 24
            r = P.ST_R_HUB + 0.6 + (P.ST_R_HOLE - 1.4 - P.ST_R_HUB) * t
            ang = a0 + math.radians(200) * t
            inner.append((cu + (r - 1.2) * math.cos(ang), cv + (r - 1.2) * math.sin(ang)))
            outer.append((cu + (r + 1.2) * math.cos(ang), cv + (r + 1.2) * math.sin(ang)))
        disc = disc.cut(poly_y(inner + list(reversed(outer)), yr0 - 1, yr0 + P.DISC_T + 1))
    hub = cyl_y(cu, cv, 2 * P.ST_R_HUB, *P.Y_HUB).cut(cyl_y(cu, cv, 5.2, P.Y_HUB[0] - 1, P.Y_HUB[1] + 1))
    hub = hub.cut(poly_y([(cu + 4.6 * math.cos(math.pi * i / 3), cv + 4.6 * math.sin(math.pi * i / 3)) for i in range(6)],
                         P.Y_HUB[0] - 1, P.Y_HUB[0] + 4))
    st = rim.fuse(disc).fuse(hub)
    for c in _bolts(cu, cv, yr0 - 1, yr1 + 1, 3.4):
        st = st.cut(c)
    return st.removeSplitter()


def support_ring(cu, cv):
    """Printed support ring (after Barbatronic's cup pot): flange clamps the TPU rim, Ø62 wall up to the stone face.
    The bellows pulls the stone onto its rim. 3 round-ended windows between the bolts (see the cup, lighter)."""
    yf0, yf1 = P.Y_RING
    s = tube_y(cu, cv, 2 * P.ST_R_OUT, 2 * P.ST_R_HOLE, yf0, yf1)
    s = s.fuse(tube_y(cu, cv, 2 * P.ST_R_OUT, 2 * P.ST_R_WALL, yf1 - 0.5, P.Y_SEAT)).removeSplitter()
    for c in _bolts(cu, cv, yf0 - 1, yf1 + 1, 3.4):
        s = s.cut(c)
    ya, yb = yf1 + 2 + P.WINDOW_W / 2, P.Y_SEAT - 3 - P.WINDOW_W / 2
    for a in P.ST_BOLT_A:
        w = a + 60.0                                              # halfway between two bolts
        win = Part.makeCylinder(P.WINDOW_W / 2, 8, V(P.ST_R_WALL - 2, ya, 0), V(1, 0, 0))
        win = win.fuse(Part.makeCylinder(P.WINDOW_W / 2, 8, V(P.ST_R_WALL - 2, yb, 0), V(1, 0, 0)))
        win = win.fuse(box(P.ST_R_WALL - 2, P.ST_R_WALL + 6, ya, yb, -P.WINDOW_W / 2, P.WINDOW_W / 2))
        s = s.cut(win.transformGeometry(App.Placement(V(cu, 0, cv), rot_y(w)).toMatrix()))
    return s


def dps30(cu, cv):
    """DP-S30 squeezed 3 mm (lip on the stone face, level with the ring rim) + its M5 stem through the TPU hub."""
    y = P.Y_HUB[1]
    c = cyl_y(cu, cv, 18, y, y + 3).fuse(cyl_y(cu, cv, 24, y + 3, y + 7))
    c = c.fuse(Part.makeCone(12, P.CUP_D / 2, P.Y_SEAT - (y + 7), V(cu, y + 7, cv), V(0, 1, 0)))
    return c.fuse(cyl_y(cu, cv, 5, P.Y_HUB[0] - 6, y))


def stations_local():
    return [(station_spacer(P.CUP_U, v), station_tpu(P.CUP_U, v), support_ring(P.CUP_U, v), dps30(P.CUP_U, v))
            for v in P.CUP_V]


def bar_fasteners_local():
    """Station bolts (M3 x 20, head on the ring flange, tapped in the bar) + the bar's zip-tie anchors and their screws."""
    f = []
    for cv in P.CUP_V:
        for a in P.ST_BOLT_A:
            t = math.radians(a)
            f.append(screw((P.CUP_U + P.ST_BOLT_R * math.cos(t), P.Y_RING[1], cv + P.ST_BOLT_R * math.sin(t)), (0, -1, 0), 20))
    an, sc = anchors_on(P.BAR_ANCHORS, P.BAR[1], True)
    _count("Zip-tie anchor (printed ABS)", len(an))
    return Part.makeCompound(f + sc), Part.makeCompound(an)


def stones_local():
    return [box(-P.STONE_L / 2, P.STONE_L / 2, P.Y_STONE, P.Y_STONE + P.STONE_W, v - P.STONE_W / 2, v + P.STONE_W / 2)
            for v in P.STONE_V]


def motor_pinion_local():
    to_o = math.atan2(P.O1[1] - P.M_POS[1], P.O1[0] - P.M_POS[0])
    g = involute_gear(P.Z_PINION, P.GEAR_M, *P.GEAR, P.PINION_BORE, mesh_phase(P.Z_PINION, to_o, False))
    # 2026-11-17: hub behind the teeth (towards the motor): M3 x 8 set screw on the shaft's flat, nut in a slot that
    # opens on the hub's motor-side face (drop the nut in before the pinion goes on the shaft)
    hy0, hy1 = P.PINION_HUB_Y
    nw, nl, nt = P.NUT3
    rn = P.PINION_BORE / 2 + 1.8                     # nut slot starts 1.8 mm outside the bore
    g = g.fuse(cyl_y(0, 0, P.PINION_HUB_D, hy0, hy1)).removeSplitter().cut(cyl_y(0, 0, P.PINION_BORE, hy0 - 1, hy1 + 1))
    g = g.cut(Part.makeCylinder(P.M3_CLEAR / 2, P.PINION_HUB_D / 2 + 1, V(0, P.PINION_SET_Y, 0), V(1, 0, 0)))
    g = g.cut(box(rn, rn + nt, hy0 - 1, P.PINION_SET_Y + nl / 2, -nw / 2, nw / 2))
    fast = screw((P.PINION_HUB_D / 2, P.PINION_SET_Y, 0), (-1, 0, 0), 8, head="set").fuse(
        hexnut((rn + nt / 2, P.PINION_SET_Y, 0), (1, 0, 0), corner_y=True))
    shaft = cyl_y(0, 0, 5, P.REAR[0] + P.MOTOR["flange_boss_h"], P.REAR[0] + P.MOTOR["shaft_l"])
    return g, shaft, fast


# ---------------------------------------------------------------- placements
def placements(item):
    s, pose, p1, p2 = item
    a1 = math.degrees(math.atan2(p1[1] - P.O1[1], p1[0] - P.O1[0]))
    a2 = math.degrees(math.atan2(p2[1] - P.O2[1], p2[0] - P.O2[0]))
    dphi = a1 - math.degrees(P.PHI0)              # crank turned from the start (deg)
    return {"crank": App.Placement(V(P.O1[0], 0, P.O1[1]), rot_y(a1)),
            "crank_gear": App.Placement(V(P.O1[0], 0, P.O1[1]), rot_y(a1)),
            "rocker": App.Placement(V(P.O2[0], 0, P.O2[1]), rot_y(a2)),
            "bar": App.Placement(V(pose[0], 0, pose[1]), rot_y(math.degrees(pose[2]))),
            "mot": App.Placement(V(P.M_POS[0], 0, P.M_POS[1]), rot_y(-P.RATIO * dphi))}


def build(doc):
    objs = {}

    def add(name, shape, kind):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        objs[name] = (o, kind)

    for n, sh in fixed_parts().items():
        add(n, sh, "fixed")
    # crank kind: built with O1 at the origin and P1 along +X -> placed by the crank angle
    add("Crank", crank_local(), "crank")
    add("Crank_bearings", crank_bearings_local(), "crank")
    add("Crank_shaft", crank_shaft_local(), "crank")
    add("Gear_crank_sector", crank_gear_local(), "crank_gear")
    add("Hub_crank", crank_hub_local(), "crank")
    add("Crank_clamp", crank_clamp_local(), "crank")
    add("Crank_sleeves", crank_sleeves_local(), "crank")
    add("Fasteners_crank", crank_fasteners_local(), "crank")
    add("Rocker", rocker_local(), "rocker")
    add("Rocker_bearings", rocker_bearings_local(), "rocker")
    add("Hub_rocker", rocker_hubs_local(), "rocker")
    add("Fasteners_rocker", rocker_fasteners_local(), "rocker")
    add("Bar", bar_local(), "bar")
    pb, pn, ps = bar_pins_local()
    add("Bar_pins", pb, "bar")
    add("Bar_pin_nuts", pn, "bar")
    add("Sleeve_P1", ps, "bar")
    add("Hoses", hoses_local(), "bar")
    for i, (sp, tpu, ring, cup) in enumerate(stations_local()):
        add("Station_spacer_%d" % (i + 1), sp, "bar")
        add("Station_TPU_%d" % (i + 1), tpu, "bar")
        add("Support_ring_%d" % (i + 1), ring, "bar")
        add("DPS30_%d" % (i + 1), cup, "bar")
    for i, st in enumerate(stones_local()):
        add("Stone_%d" % (i + 1), st, "bar")
    gm, sh, gf = motor_pinion_local()
    add("Gear_motor_15T", gm, "mot")
    add("Motor_shaft", sh, "mot")
    add("Fasteners_pinion", gf, "mot")
    add("Fasteners_sector", sector_fasteners_local(), "crank_gear")
    bf, ba = bar_fasteners_local()
    add("Fasteners_bar", bf, "bar")
    add("Anchors_bar", ba, "bar")
    return objs


def pose(objs, item):
    pl = placements(item)
    for n, (o, k) in objs.items():
        if k in pl:
            o.Placement = pl[k]


# crank-kind shapes are built in the crank frame: P1 along +X. The rocker in its frame: P2 along +X.
EXPECTED = {("Gear_crank_sector", "Gear_motor_15T"),     # mesh
            ("Crank", "Crank_bearings"), ("Rocker", "Rocker_bearings"), ("Crank_shaft", "Gear_crank_sector"),
            ("Motor_shaft", "Gear_motor_15T"), ("motor", "Motor_shaft"), ("motor", "rear_plate"),
            ("column", "switch_home"), ("column", "switch_upright"), ("column", "stop_home"), ("column", "stop_upright")}
STOP_CONTACT = {"stop_home", "stop_upright"}     # the crank resting on a hard stop at the end of the over-travel = the stop working
MOVING_ACT = ("crank", "crank_gear", "rocker", "bar")


def check(objs, item):
    pose(objs, item)
    shapes = [(n, o.Shape, k) for n, (o, k) in objs.items() if n != "table"]
    hits = []
    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            (a, sa, ka), (b, sb, kb) = shapes[i], shapes[j]
            if ka == kb or (a, b) in EXPECTED or (b, a) in EXPECTED:
                continue
            if ka == "fixed" and kb == "fixed":
                continue
            if not sa.BoundBox.intersect(sb.BoundBox):
                continue
            v = sa.common(sb).Volume
            if (a in STOP_CONTACT or b in STOP_CONTACT) and v < 10.0:
                continue                     # tangent contact with the rubber stop (a few mm3 of facets)
            if v > 1.0:
                hits.append((a, b, v))
    act = [o.Shape.BoundBox for n, (o, k) in objs.items() if k in ("bar", "rocker", "crank", "crank_gear") and not n.startswith("Stone")]
    st = [objs["Stone_%d" % i][0].Shape.BoundBox for i in (1, 2, 3)]
    mov = [(o.Shape.BoundBox.ZMin, n) for n, (o, k) in objs.items() if k in ("bar", "rocker", "crank") and not n.startswith("Stone")]
    tab = objs["table"][0].Shape
    table_hits = [n for n, (o, k) in objs.items() if k in ("bar", "rocker", "crank") and not n.startswith("Stone")
                  and o.Shape.BoundBox.ZMin < 0.5]
    return hits, max(b.ZMax for b in act), max(b.ZMax for b in st), min(mov), table_hits


LABELS = {"base_330": "Base_plate_330", "wheels": "Drive_wheels", "column": "Column_alu_5mm", "rear_plate": "Rear_plate_alu_5mm",
          "standoffs": "Standoffs_10x35_M5_x4", "housings": "Bearing_housings_printed_x2", "bearings_fixed": "608ZZ_frame_x2",
          "shaft_O2": "Rocker_axle_M8x80_hex_bolt", "brackets": "Angle_brackets_x4", "sleeves_fixed": "O2_tube_D14x35_and_sleeve_D11.5x6_ABS",
          "fasteners_base": "Bracket_to_base_M4x16_nut_x4", "Hub_crank": "Link_hub_crank_P1_ABS", "Hub_rocker": "Link_hubs_rocker_ABS_x2",
          "Crank_clamp": "Crank_clamp_hub_ABS", "Crank_sleeves": "Crank_shaft_sleeves_D11.5_ABS_x2", "Fasteners_crank": "Fasteners_crank_M3",
          "Fasteners_rocker": "Fasteners_rocker_M3x10_x4", "Bar_pin_nuts": "Bar_pin_nuts_M8", "Sleeve_P1": "Sleeve_P1_D11.5x6_ABS",
          "Hoses": "Hoses_D4_on_the_bar",
          "motor": "Stepper_17HS4401S", "switch_home": "Endstop_home", "switch_upright": "Endstop_upright",
          "stop_home": "Hard_stop_home_rubber", "stop_upright": "Hard_stop_upright_rubber", "pumps": "Vacuum_pumps_12V_x3",
          "valves": "Vent_valves_12V_x3", "Crank": "Crank_alu_6mm", "Crank_bearings": "608ZZ_crank_pin_x2",
          "Crank_shaft": "Crank_shaft_D8", "Gear_crank_sector": "Gear_sector_100T_m08_crank_ABS", "Rocker": "Rocker_alu_6mm",
          "Rocker_bearings": "608ZZ_rocker_x4", "Bar": "Cup_bar_alu_5mm", "Bar_pins": "Bar_pins_M8x30_hex_bolts_x2",
          "Gear_motor_15T": "Gear_15T_m08_motor_ABS", "Motor_shaft": "Motor_shaft_D5",
          "Station_spacer_1": "Station_spacer_ABS", "Station_TPU_1": "Station_TPU_95A_clapets_v8",
          "Support_ring_1": "Support_ring_ABS", "fasteners_fixed": "Fasteners_frame", "fasteners_tapped": "Screws_tapped_in_the_plates_M3", "anchors_fixed": "Zip_tie_anchors_frame_x2",
          "Fasteners_bar": "Fasteners_bar_M3", "Anchors_bar": "Zip_tie_anchors_bar_x3", "Fasteners_sector": "Sector_clamp_M3x12_nut",
          "Fasteners_pinion": "Pinion_set_screw_M3x8_nut"}
GROUPS = [("Robot_base", ["base_330", "wheels"]),
          ("Frame", ["column", "rear_plate", "standoffs", "housings", "bearings_fixed", "brackets", "shaft_O2", "fasteners_fixed", "fasteners_tapped",
                     "anchors_fixed", "sleeves_fixed", "fasteners_base"]),
          ("Drive", ["motor", "Motor_shaft", "Gear_", "Fasteners_sector", "Fasteners_pinion"]),
          ("Switches_stops", ["switch_", "stop_"]),
          ("Four_bar", ["Crank", "Crank_", "Rocker", "Rocker_", "Bar_pin", "Hub_", "Fasteners_crank", "Fasteners_rocker", "Sleeve_P1"]),
          ("Cup_bar", ["Bar", "Station_spacer_", "Station_TPU_", "Support_ring_", "DPS30_", "Fasteners_bar", "Anchors_bar", "Hoses"]),
          ("Vacuum", ["pumps", "valves"]),
          ("Stones_3", ["Stone_"])]


def mass_report(objs):
    mat = {"Bar": "alu", "Bar_pins": "steel", "Crank": "alu", "Crank_bearings": "steel", "Crank_shaft": "steel",
           "Gear_crank_sector": "abs", "Rocker": "alu", "Rocker_bearings": "steel", "Hub_crank": "abs", "Crank_clamp": "abs",
           "Crank_sleeves": "abs", "Hub_rocker": "abs", "Sleeve_P1": "abs", "Bar_pin_nuts": "steel", "Hoses": "hose"}
    out, bar_assy = [], 0.0
    for n, (o, k) in objs.items():
        if k not in ("bar", "crank", "crank_gear", "rocker") or n.startswith("Stone"):
            continue
        m_ = mat.get(n, "steel" if n.startswith("Fasteners") else
                     "abs" if n.startswith(("Station_spacer", "Support_ring", "Anchors")) else "tpu")
        g = o.Shape.Volume * RHO[m_]
        if n.startswith("DPS30"):
            g = 8.0                          # DP-S30 cup ~8 g (seller), not its solid volume
        out.append((n, g))
        if k == "bar":
            bar_assy += g
    return out, bar_assy


def main():
    out = os.path.join(ROOT, "CAD")
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    doc = App.newDocument("flipbar")
    objs = build(doc)
    stop = P.STOP_PAST_DEG / math.degrees(abs(P.SWEEP))
    items = [it for it in P.sweep_path(-stop, 1 + stop, 84) if it[1] is not None]
    lines, worst_top, worst_st, low, allhits = [], (0, 0), (0, 0), (1e9, 0, ""), []
    for it in items:
        hits, top, st, mn, th = check(objs, it)
        if top > worst_top[0]:
            worst_top = (top, it[0])
        if st > worst_st[0]:
            worst_st = (st, it[0])
        if mn[0] < low[0]:
            low = (mn[0], it[0], mn[1])
        allhits += [(it[0],) + h for h in hits] + [(it[0], n, "table", 0) for n in th]
    FIXED_OK = {("base_330", "brackets"), ("column", "brackets"), ("rear_plate", "brackets"), ("housings", "bearings_fixed"),
                ("column", "shaft_O2"), ("rear_plate", "shaft_O2"),
                ("column", "standoffs"), ("rear_plate", "standoffs"), ("rear_plate", "motor"), ("column", "switch_home"),
                ("column", "switch_upright"), ("column", "stop_home"), ("column", "stop_upright"), ("pumps", "valves"),
                ("base_330", "wheels"), ("motor", "fasteners_fixed"), ("rear_plate", "fasteners_tapped"),
                ("column", "fasteners_tapped"), ("base_330", "fasteners_base")}
    fx = [(n, o.Shape) for n, (o, k) in objs.items() if k == "fixed" and n != "table"]
    fixed_hits = []
    for i in range(len(fx)):
        for j in range(i + 1, len(fx)):
            (a, sa), (b, sb) = fx[i], fx[j]
            if (a, b) in FIXED_OK or (b, a) in FIXED_OK or not sa.BoundBox.intersect(sb.BoundBox):
                continue
            v = sa.common(sb).Volume
            if v > 1.0:
                fixed_hits.append((a, b, v))
    lines.append("Single-bar flip - solid check over the whole range (flipbar_fc.py), %d poses from s %.3f (home stop) to "
                 "s %.3f (upright stop)" % (len(items), -stop, 1 + stop))
    lines.append("Expected contacts ignored: gear meshes, bearings in hubs/housings, shafts in gears, motor on the rear plate,")
    lines.append("switches and stops on the column. Parts moving together (same link) are not checked against each other.")
    lines.append("")
    lines.append("fixed parts against each other (frame, motor, pumps, base): %d overlap(s)%s" % (
        len(fixed_hits), "".join("\n   %s x %s %.0f mm3" % h for h in fixed_hits)))
    lines.append("moving parts, unexpected overlaps: %d" % len(allhits))
    seen = {}
    for s, a, b, v in allhits:
        seen.setdefault((a, b), []).append((s, v))
    for (a, b), lst in sorted(seen.items(), key=lambda kv: -max(v for _, v in kv[1])):
        lines.append("   %-22s x %-22s s %.3f..%.3f, max %.0f mm3" % (a, b, min(x for x, _ in lst), max(x for x, _ in lst),
                                                                  max(v for _, v in lst)))
    lines.append("")
    lines.append("actuators highest point (exact solids): %.1f mm at s %.3f -> %s" % (
        worst_top[0], worst_top[1], "OK (limit 350)" if worst_top[0] <= 350 else "OVER 350"))
    lines.append("stones highest: %.1f mm at s %.3f (castle / construction zones only)" % worst_st)
    lines.append("moving parts (not the stones) lowest point: %.1f mm at s %.3f, %s (above the table)" % low)
    masses, bar_assy = mass_report(objs)
    lines.append("")
    lines.append("masses (g): " + ", ".join("%s %.0f" % (n, g) for n, g in masses))
    lines.append("bar assembly (bar + M8 pins and nuts + spacers + TPU stations + support rings + cups + bolts + anchors + hoses): %.0f g "
                 "(flipbar_params assumes %.0f g)" % (bar_assy, P.M_BAR_ASSY * 1000))
    lines.append("")
    lines.append("fasteners drawn and swept (not drawn: pump and valve clamps, the hose loop to the valves, cables):")
    for k in sorted(BOM):
        lines.append("   %2d x %s" % (BOM[k], k))
    print("\n".join(lines))
    open(os.path.join(ROOT, "collision_report.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

    # save at the start pose: robot + stones, no table
    pose(objs, items[min(range(len(items)), key=lambda i: abs(items[i][0]))])
    doc.removeObject("table")
    keep = [o for n, (o, k) in objs.items() if n != "table"]
    for o in keep:
        o.Label = LABELS.get(o.Name, o.Name)
    for gname, members in GROUPS:
        g = doc.addObject("App::DocumentObjectGroup", gname)
        for o in keep:
            if any(o.Name == m or (m.endswith("_") and o.Name.startswith(m)) for m in members):
                g.addObject(o)
    doc.recompute()
    Part.makeCompound([o.Shape.copy() for o in keep]).exportStep(os.path.join(out, "flipbar.step"))
    doc.saveAs(os.path.join(out, "flipbar.FCStd"))
    for n in ("Bar", "Crank", "Rocker", "column", "rear_plate", "Station_spacer_1", "Station_TPU_1", "Support_ring_1",
              "Gear_crank_sector", "Gear_motor_15T"):
        sh = objs[n][0].Shape.copy()
        sh.Placement = App.Placement()
        sh.exportStep(os.path.join(out, "parts", "%s.step" % LABELS.get(n, n)))
    n0 = dict(BOM)                                   # the shapes below are rebuilt for export only: don't count twice
    for n, sh in (("Bearing_housing_rear_plate_ABS", housing(*P.HOUSING_R, True)[0]),
                  ("Bearing_housing_column_ABS", housing(*P.HOUSING_C, False)[0]), ("Zip_tie_anchor_ABS", anchor()),
                  ("Link_hub_2x608_ABS", link_hub(0, 1, 0, 1)), ("Crank_clamp_hub_ABS", crank_clamp_local()),
                  ("Station_spacer_P2_notch_ABS", station_spacer(P.CUP_U, P.CUP_V[1])),
                  ("O2_tube_D14x35_ABS", tube_y(0, 0, P.O2_TUBE_D, 8.4, 0, P.COL[0] - P.REAR[1])),
                  ("Sleeve_D11.5x6_ABS", sleeve_y(0, 0, 0, 6)), ("Sleeve_D11.5x8_ABS", sleeve_y(0, 0, 0, 8)),
                  ("Sleeve_D11.5x10_ABS", sleeve_y(0, 0, 0, 10))):
        sh.exportStep(os.path.join(out, "parts", "%s.step" % n))
    print("->", out)


if __name__ in ("__main__", "flipbar_fc") and not App.GuiUp:
    main()
