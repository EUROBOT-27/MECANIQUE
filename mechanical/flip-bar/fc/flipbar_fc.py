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
RHO = {"alu": 2.70e-3, "steel": 7.85e-3, "abs": 0.75e-3, "tpu": 1.2e-3}   # g/mm3 (ABS ~50 % infill)


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
    s0, s1, w = P.link_slot(length)
    return spline_prism(P.link_outline(length), y0, y1).cut(slot_y((s0, 0), (s1, 0), w, y0 - 1, y1 + 1))


def b608(x, z, y0):
    """608ZZ: 8 x 22 x 7."""
    return tube_y(x, z, 22.0, 8.0, y0, y0 + 7.0)


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


def switch(angle_deg, r=55.0):
    """Ender endstop (switch 20 x 10 x 6.5 on a 1.6 mm PCB) on the column front, crank layer, at angle (deg) / r."""
    y = P.COL[1]
    sw = box(-10, 10, y, y + 1.6 + 6.5, -5, 5).fuse(box(-20, 14, y, y + 1.6, -8, 8))
    a = math.radians(angle_deg)
    m = App.Placement(V(P.O1[0] + r * math.cos(a), 0, P.O1[1] + r * math.sin(a)), rot_y(angle_deg)).toMatrix()
    return sw.transformGeometry(m)


def bumper(angle_deg):
    a = math.radians(angle_deg)
    x, z = P.O1[0] + P.STOP_R * math.cos(a), P.O1[1] + P.STOP_R * math.sin(a)
    return cyl_y(x, z, P.STOP_D, P.COL[1], P.CRANK[1] + 1).fuse(cyl_y(x, z, 4, P.COL[0], P.COL[1]))


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
    so = [(x, z, 5.5) for x, z in P.STANDOFFS]
    # column: crank shaft + intermediate shaft holes (Ø12, bearings in the housings behind), O2 shaft Ø8 (clamped)
    parts["column"] = frame_plate(*P.COL, [(P.O1[0], P.O1[1], 12), (P.I_POS[0], P.I_POS[1], 12),
                                            (P.O2[0], P.O2[1], 8)] + so, x1=P.COLUMN_X1)
    mh = P.MOTOR["holes"] / 2
    parts["rear_plate"] = frame_plate(*P.REAR, [(P.O1[0], P.O1[1], 12), (P.I_POS[0], P.I_POS[1], 12),
                                                 (P.O2[0], P.O2[1], 8), (P.M_POS[0], P.M_POS[1], 22.5)] + so +
                                      [(P.M_POS[0] + sx * mh, P.M_POS[1] + sz * mh, 3.4) for sx in (1, -1) for sz in (1, -1)])
    parts["standoffs"] = Part.makeCompound([tube_y(x, z, 10, 5.5, P.REAR[1], P.COL[0]) for x, z in P.STANDOFFS])
    hs, br = [], []
    for (y0, y1) in (P.HOUSING_R, P.HOUSING_C):     # one printed double housing per plate (crank + intermediate)
        h = cyl_y(P.O1[0], P.O1[1], P.HOUSING_D, y0, y1).fuse(cyl_y(P.I_POS[0], P.I_POS[1], P.HOUSING_D, y0, y1))
        for (x, z) in (P.O1, P.I_POS):
            h = h.cut(cyl_y(x, z, 22.0, y0 - 1, y1 + 1))
            br.append(b608(x, z, y0))
        hs.append(h.removeSplitter())
    parts["housings"] = Part.makeCompound(hs)
    parts["bearings_fixed"] = Part.makeCompound(br)
    # rocker ground shaft: Ø8, clamped in both plates, out to the rocker hub front + e-clip
    parts["shaft_O2"] = cyl_y(P.O2[0], P.O2[1], 8, P.REAR[0], P.ROCK_HUB[1] + 1.5)
    parts["shaft_I"] = cyl_y(P.I_POS[0], P.I_POS[1], 8, P.HOUSING_R[0], P.HOUSING_C[1])
    # angle brackets: both plates -> base plate (clear of the gears: at the outer ends)
    x0, x1 = P.FRAME_X
    bk = []
    for (yp0, yp1), sgn, xr in ((P.COL, -1, P.COLUMN_X1), (P.REAR, 1, x1)):
        for bx0, bx1 in ((x0 + 2, x0 + 22), (xr - 22, xr - 2)):
            yb = yp0 if sgn < 0 else yp1
            bk.append(box(bx0, bx1, min(yb, yb + sgn * 25), max(yb, yb + sgn * 25), P.BASE_TOP, P.BASE_TOP + 4)
                      .fuse(box(bx0, bx1, min(yb, yb + sgn * 4), max(yb, yb + sgn * 4), P.BASE_TOP, P.BASE_TOP + 25)))
    parts["brackets"] = Part.makeCompound(bk)
    parts["motor"] = nema17()
    sg = math.copysign(1, P.SWEEP)
    a0, a1 = math.degrees(P.PHI0), math.degrees(P.PHI1)
    parts["switch_home"] = switch(a0 - sg * P.HOME_SWITCH_DEG)
    parts["switch_upright"] = switch(a1 + sg * P.END_SWITCH_DEG)
    stop_off = math.degrees(math.atan((P.LINK_W / 2 + P.STOP_D / 2) / P.STOP_R)) + P.STOP_PAST_DEG
    parts["stop_home"] = bumper(a0 - sg * stop_off)
    parts["stop_upright"] = bumper(a1 + sg * stop_off)
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
    """O1 at the origin, P1 along +X at R1. Plate + clamp hub on the shaft + P1 hub with two 608."""
    s = link_plate(P.R1, *P.CRANK)
    s = s.fuse(cyl_y(0, 0, 22, P.COL[1] + 0.5, P.CRANK[0]))                       # clamp hub on the D8 shaft
    s = s.fuse(cyl_y(P.R1, 0, P.HUB_D, *P.CRANK_HUB))                              # P1 hub
    s = s.cut(cyl_y(P.R1, 0, 22, P.CRANK_HUB[0] - 1, P.CRANK_HUB[1] + 1)).cut(cyl_y(0, 0, 8, P.COL[1], P.CRANK[1] + 1))
    return s.removeSplitter()


def crank_bearings_local():
    return b608(P.R1, 0, P.CRANK_HUB[0]).fuse(b608(P.R1, 0, P.CRANK_HUB[0] + 7))


def crank_shaft_local():
    return cyl_y(0, 0, 8, P.HOUSING_R[0], P.CRANK[1])


def crank_gear_local():
    to_i = math.atan2(P.I_POS[1] - P.O1[1], P.I_POS[0] - P.O1[0]) - P.PHI0      # crank frame
    return involute_gear(P.Z_WHEEL, P.GEAR_M, *P.STAGE2, 8, mesh_phase(P.Z_WHEEL, to_i, True))


def rocker_local():
    s = link_plate(P.R2, *P.ROCK)
    for x in (0, P.R2):
        s = s.fuse(cyl_y(x, 0, P.HUB_D, *P.ROCK_HUB)).cut(cyl_y(x, 0, 22, P.ROCK_HUB[0] - 1, P.ROCK_HUB[1] + 1))
    return s.removeSplitter()


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
    """Ø8 pins fixed in the bar, through the link hub bearings; spacers between the hub and the bar."""
    p1 = cyl_y(P.P1[0], P.P1[1], 8, P.CRANK_HUB[0], P.BAR[1]).fuse(cyl_y(P.P1[0], P.P1[1], 14, P.CRANK_HUB[1] + 0.5, P.BAR[0]))
    p2 = cyl_y(P.P2[0], P.P2[1], 8, P.ROCK_HUB[0], P.BAR[1]).fuse(cyl_y(P.P2[0], P.P2[1], 14, P.ROCK_HUB[1] + 0.5, P.BAR[0]))
    return p1.fuse(p2)


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


def stones_local():
    return [box(-P.STONE_L / 2, P.STONE_L / 2, P.Y_STONE, P.Y_STONE + P.STONE_W, v - P.STONE_W / 2, v + P.STONE_W / 2)
            for v in P.STONE_V]


def int_gears_local():
    to_m = math.atan2(P.M_POS[1] - P.I_POS[1], P.M_POS[0] - P.I_POS[0])
    to_o = math.atan2(P.O1[1] - P.I_POS[1], P.O1[0] - P.I_POS[0])
    g45 = involute_gear(P.Z_WHEEL, P.GEAR_M, *P.STAGE1, 8, mesh_phase(P.Z_WHEEL, to_m, False))
    g15 = involute_gear(P.Z_PINION, P.GEAR_M, *P.STAGE2, 8, mesh_phase(P.Z_PINION, to_o, False))
    return g45, g15


def motor_pinion_local():
    to_i = math.atan2(P.I_POS[1] - P.M_POS[1], P.I_POS[0] - P.M_POS[0])
    g = involute_gear(P.Z_PINION, P.GEAR_M, *P.STAGE1, 5, mesh_phase(P.Z_PINION, to_i, True))
    shaft = cyl_y(0, 0, 5, P.REAR[0] + P.MOTOR["flange_boss_h"], P.REAR[0] + P.MOTOR["shaft_l"])
    return g, shaft


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
            "int": App.Placement(V(P.I_POS[0], 0, P.I_POS[1]), rot_y(-3 * dphi)),
            "mot": App.Placement(V(P.M_POS[0], 0, P.M_POS[1]), rot_y(9 * dphi))}


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
    add("Gear_crank_45T", crank_gear_local(), "crank_gear")
    add("Rocker", rocker_local(), "rocker")
    add("Rocker_bearings", rocker_bearings_local(), "rocker")
    add("Bar", bar_local(), "bar")
    add("Bar_pins", bar_pins_local(), "bar")
    for i, (sp, tpu, ring, cup) in enumerate(stations_local()):
        add("Station_spacer_%d" % (i + 1), sp, "bar")
        add("Station_TPU_%d" % (i + 1), tpu, "bar")
        add("Support_ring_%d" % (i + 1), ring, "bar")
        add("DPS30_%d" % (i + 1), cup, "bar")
    for i, st in enumerate(stones_local()):
        add("Stone_%d" % (i + 1), st, "bar")
    g45, g15 = int_gears_local()
    add("Gear_int_45T", g45, "int")
    add("Gear_int_15T", g15, "int")
    gm, sh = motor_pinion_local()
    add("Gear_motor_15T", gm, "mot")
    add("Motor_shaft", sh, "mot")
    return objs


def pose(objs, item):
    pl = placements(item)
    for n, (o, k) in objs.items():
        if k in pl:
            o.Placement = pl[k]


# crank-kind shapes are built in the crank frame: P1 along +X. The rocker in its frame: P2 along +X.
EXPECTED = {("Gear_crank_45T", "Gear_int_15T"), ("Gear_int_45T", "Gear_motor_15T"),     # meshes
            ("Crank", "Crank_bearings"), ("Rocker", "Rocker_bearings"), ("Crank_shaft", "Gear_crank_45T"),
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
    mov = [o.Shape.BoundBox for n, (o, k) in objs.items() if k in ("bar", "rocker", "crank") and not n.startswith("Stone")]
    tab = objs["table"][0].Shape
    table_hits = [n for n, (o, k) in objs.items() if k in ("bar", "rocker", "crank") and not n.startswith("Stone")
                  and o.Shape.BoundBox.ZMin < 0.5]
    return hits, max(b.ZMax for b in act), max(b.ZMax for b in st), min(b.ZMin for b in mov if b is not None), table_hits


LABELS = {"base_330": "Base_plate_330", "wheels": "Drive_wheels", "column": "Column_alu_5mm", "rear_plate": "Rear_plate_alu_5mm",
          "standoffs": "Standoffs_10x35_M5_x4", "housings": "Bearing_housings_printed_x4", "bearings_fixed": "608ZZ_frame_x4",
          "shaft_O2": "Rocker_ground_shaft_D8", "shaft_I": "Intermediate_shaft_D8", "brackets": "Angle_brackets_x4",
          "motor": "Stepper_17HS4401S", "switch_home": "Endstop_home", "switch_upright": "Endstop_upright",
          "stop_home": "Hard_stop_home_rubber", "stop_upright": "Hard_stop_upright_rubber", "pumps": "Vacuum_pumps_12V_x3",
          "valves": "Vent_valves_12V_x3", "Crank": "Crank_alu_6mm", "Crank_bearings": "608ZZ_crank_pin_x2",
          "Crank_shaft": "Crank_shaft_D8", "Gear_crank_45T": "Gear_45T_m1_crank_ABS", "Rocker": "Rocker_alu_6mm",
          "Rocker_bearings": "608ZZ_rocker_x4", "Bar": "Cup_bar_alu_5mm", "Bar_pins": "Bar_pins_D8_with_spacers",
          "Gear_int_45T": "Gear_45T_m1_intermediate_ABS", "Gear_int_15T": "Gear_15T_m1_intermediate_ABS",
          "Gear_motor_15T": "Gear_15T_m1_motor_ABS", "Motor_shaft": "Motor_shaft_D5",
          "Station_spacer_1": "Station_spacer_ABS", "Station_TPU_1": "Station_TPU_95A_clapets_v8",
          "Support_ring_1": "Support_ring_ABS"}
GROUPS = [("Robot_base", ["base_330", "wheels"]),
          ("Frame", ["column", "rear_plate", "standoffs", "housings", "bearings_fixed", "brackets", "shaft_O2", "shaft_I"]),
          ("Drive", ["motor", "Motor_shaft", "Gear_"]),
          ("Switches_stops", ["switch_", "stop_"]),
          ("Four_bar", ["Crank", "Crank_", "Rocker", "Rocker_", "Bar_pins"]),
          ("Cup_bar", ["Bar", "Station_spacer_", "Station_TPU_", "Support_ring_", "DPS30_"]),
          ("Vacuum", ["pumps", "valves"]),
          ("Stones_3", ["Stone_"])]


def mass_report(objs):
    mat = {"Bar": "alu", "Bar_pins": "steel", "Crank": "alu", "Crank_bearings": "steel", "Crank_shaft": "steel",
           "Gear_crank_45T": "abs", "Rocker": "alu", "Rocker_bearings": "steel"}
    out, bar_assy = [], 0.0
    for n, (o, k) in objs.items():
        if k not in ("bar", "crank", "crank_gear", "rocker") or n.startswith("Stone"):
            continue
        m_ = mat.get(n, "abs" if n.startswith(("Station_spacer", "Support_ring")) else "tpu")
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
    lines, worst_top, worst_st, low, allhits = [], (0, 0), (0, 0), (1e9, 0), []
    for it in items:
        hits, top, st, mn, th = check(objs, it)
        if top > worst_top[0]:
            worst_top = (top, it[0])
        if st > worst_st[0]:
            worst_st = (st, it[0])
        if mn < low[0]:
            low = (mn, it[0])
        allhits += [(it[0],) + h for h in hits] + [(it[0], n, "table", 0) for n in th]
    FIXED_OK = {("base_330", "brackets"), ("column", "brackets"), ("rear_plate", "brackets"), ("housings", "bearings_fixed"),
                ("column", "shaft_O2"), ("rear_plate", "shaft_O2"), ("housings", "shaft_I"), ("bearings_fixed", "shaft_I"),
                ("column", "standoffs"), ("rear_plate", "standoffs"), ("rear_plate", "motor"), ("column", "switch_home"),
                ("column", "switch_upright"), ("column", "stop_home"), ("column", "stop_upright"), ("pumps", "valves"),
                ("base_330", "wheels")}
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
    lines.append("moving parts (not the stones) lowest point: %.1f mm at s %.3f (above the table)" % low)
    masses, bar_assy = mass_report(objs)
    lines.append("")
    lines.append("masses (g): " + ", ".join("%s %.0f" % (n, g) for n, g in masses))
    lines.append("bar assembly (bar + pins + spacers + TPU stations + support rings + cups): %.0f g (flipbar_params assumes %.0f g)" % (
        bar_assy, P.M_BAR_ASSY * 1000))
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
              "Gear_crank_45T", "Gear_int_45T",
              "Gear_int_15T", "Gear_motor_15T"):
        sh = objs[n][0].Shape.copy()
        sh.Placement = App.Placement()
        sh.exportStep(os.path.join(out, "parts", "%s.step" % LABELS.get(n, n)))
    print("->", out)


if __name__ in ("__main__", "flipbar_fc") and not App.GuiUp:
    main()
