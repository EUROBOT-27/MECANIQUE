# hub_e_fc.py - Central hub OPTION E (doubled), FreeCAD model (Ayoub, proposal 2026-11-19, not reviewed).
# Two units (front -> robot's left, rear -> robot's right) around one fixed 20 mm column. Each unit:
#   turret (bottom + top plate, printed) turned 0 -> 90 deg by an MG996R through a 2:1 spur pair (60 T sector on the
#   hub, 30 T pinion, m 1); one carriage on a T8 screw + 8 mm rod, NEMA17 + GT2 belt 1:1; spin MG996R + VS2-S30 cup;
#   holder frame with 2 cups per lower stone (x = +-100), lifted 15 mm by an MG90S.
# Every number comes from fc/check_e.py (box model), so the two agree. Printed parts (blue) as plain blocks with their
# holes, bought parts as outer shapes, gear teeth trapezoidal. Since 2026-11-20 every screw, nut, washer, heat-set
# insert and collar is drawn by fc/hub_e_hw.py, with its holes, counterbores and nut pockets cut into the parts.
#
# Base (2026-11-20): mechanical/base_330_js as it is, loaded from base_330_js/CAD/base_330_js_assembly.FCStd (plate,
# 37D motors + hinges, JSUMO worst-case envelope, both odometry modules, 4 ball units). The layout-v1 version is in
# CAD_FC/layout-v1/ (snapshot).
# Run from mechanical/central-hub/option-e/ (GUI, so the files keep their colours; closes itself):
#   "D:/FreeCad/bin/FreeCAD.exe" fc/hub_e_fc.py
# or without colours:  "D:/FreeCad/bin/freecadcmd.exe" fc/hub_e_fc.py
# Writes CAD_FC/HUB_E_*.FCStd (poses), CAD_FC/HUB_E_HOME.step, hub_e_fc_report.txt (solid clash check).
# Frame: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table. mm.
import os
import sys
import math
import copy
import traceback
import numpy as np
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_e as ce            # noqa: E402
import hub_e_hw as hw           # noqa: E402
import types                    # noqa: E402
V = App.Vector
OUT = os.path.join(ROOT, "CAD_FC")
UNAME = {"F": "front", "R": "rear"}
LNAME = {"T": "top", "M": "middle", "B": "bottom"}

BLUE = (0.10, 0.38, 0.88)                       # every 3D-printed part (Ayoub, 2026-11-20)
COL = dict(stone=(0.85, 0.70, 0.44), held=(0.88, 0.54, 0.17), tower=(0.66, 0.51, 0.29),
           turF=BLUE, turR=BLUE, car=BLUE, hold=BLUE, print=BLUE, blackox=(0.13, 0.13, 0.15), zinc=(0.80, 0.81, 0.83),
           servo=(0.12, 0.12, 0.14), steel=(0.70, 0.72, 0.75), brass=(0.80, 0.65, 0.25), cup=(0.95, 0.95, 0.95),
           alu=(0.62, 0.65, 0.70), floor=(0.86, 0.86, 0.84), plate=(0.87, 0.78, 0.60), envelope=(0.30, 0.30, 0.32), wheel=(0.08, 0.08, 0.08), dark=(0.30, 0.30, 0.32),
           belt=(0.15, 0.15, 0.15), gear=BLUE, reserve_grail=(0.95, 0.77, 0.06),
           reserve_launch=(0.91, 0.30, 0.24), reserve_pump=(0.60, 0.65, 0.66))


# ---------------------------------------------------------------- helpers
def mat(Rm, off=(0, 0, 0)):
    return App.Matrix(Rm[0, 0], Rm[0, 1], Rm[0, 2], off[0],
                      Rm[1, 0], Rm[1, 1], Rm[1, 2], off[1],
                      Rm[2, 0], Rm[2, 1], Rm[2, 2], off[2],
                      0, 0, 0, 1)


def moved(shape, Rm, off=(0, 0, 0)):
    s = shape.copy()
    s.transformShape(mat(np.asarray(Rm, float), off))
    return s


def to_unit(shape, phi):
    """local (r, t, z) frame at polar phi -> world"""
    ur, ut, _, _ = ce.frame(phi)
    return moved(shape, np.column_stack([ur, ut, [0, 0, 1.0]]))


def lbox(r, t, z):
    return Part.makeBox(r[1] - r[0], t[1] - t[0], z[1] - z[0], V(r[0], t[0], z[0]))


def cyl_r(r0, r1, rad, t=0.0, z=0.0):
    """cylinder along the local r axis"""
    return Part.makeCylinder(rad, r1 - r0, V(r0, t, z), V(1, 0, 0))


def cyl_z(x, y, z0, z1, rad):
    return Part.makeCylinder(rad, z1 - z0, V(x, y, z0))


def tube_z(x, y, z0, z1, ro, ri):
    return cyl_z(x, y, z0, z1, ro).cut(cyl_z(x, y, z0, z1, ri))


def obox(b):
    """check_e.Box -> solid"""
    s = Part.makeBox(*(2 * b.h), V(*(-b.h)))
    return moved(s, b.R, b.c)


def gear(n_teeth, m, a0=None, a1=None, r_in=0.0, z0=0.0, z1=5.0, cx=0.0, cy=0.0, rot=0.0):
    """spur gear (trapezoidal teeth), full or a sector a0..a1 (deg, local), extruded z0..z1, centred (cx, cy)"""
    rp = n_teeth * m / 2
    ra, rf = rp + m, rp - 1.25 * m
    p = 2 * math.pi / n_teeth
    pts = []
    if a0 is None:
        ks = range(n_teeth)
    else:
        k0, k1 = int(math.floor(math.radians(a0) / p)), int(math.ceil(math.radians(a1) / p))
        ks = range(k0, k1 + 1)
    for k in ks:
        a = k * p + math.radians(rot)
        for rr, f in ((rf, -0.5), (rf, -0.28), (ra, -0.14), (ra, 0.14), (rf, 0.28)):
            pts.append((rr * math.cos(a + f * p), rr * math.sin(a + f * p)))
    if a0 is not None:
        a_end = (ks[-1] + 0.5) * p + math.radians(rot)
        pts.append((rf * math.cos(a_end), rf * math.sin(a_end)))
        for a in np.linspace(a_end, (ks[0] - 0.5) * p + math.radians(rot), 24):
            pts.append((r_in * math.cos(a), r_in * math.sin(a)))
    pts.append(pts[0])
    w = Part.makePolygon([V(cx + x, cy + y, z0) for x, y in pts])
    sol = Part.Face(w).extrude(V(0, 0, z1 - z0))
    if a0 is None and r_in > 0:
        sol = sol.cut(cyl_z(cx, cy, z0, z1, r_in))
    return sol


# ---------------------------------------------------------------- bought parts (local shapes)
def mg996r_local(shaft_face_r, t_shaft, z_c, along_t=True):
    """MG996R lying in the local frame: shaft along +r at r = shaft_face_r, body along t, 19.7 thick in z"""
    m = ce.MG996
    t0 = t_shaft - m["SHAFT_OFF"]
    body = lbox((shaft_face_r - m["H"], shaft_face_r), (t0, t0 + m["L"]), (z_c - m["W"] / 2, z_c + m["W"] / 2))
    tc = t0 + m["L"] / 2
    ears = lbox((shaft_face_r - 10.3, shaft_face_r - 7.8), (tc - m["EAR_L"] / 2, tc + m["EAR_L"] / 2),
                (z_c - m["W"] / 2, z_c + m["W"] / 2))
    spline = cyl_r(shaft_face_r, shaft_face_r + 4, 3.0, t_shaft, z_c)
    return body.fuse(ears).fuse(spline)


def mg996r_upright(x0, y0, sx, z0):
    """MG996R standing on z0, shaft up at (x0, y0), body along sx * X"""
    m = ce.MG996
    xa, xb = sorted((x0 - sx * m["SHAFT_OFF"], x0 + sx * (m["L"] - m["SHAFT_OFF"])))
    body = Part.makeBox(xb - xa, m["W"], m["H"], V(xa, y0 - m["W"] / 2, z0))
    xc = (xa + xb) / 2
    ears = Part.makeBox(m["EAR_L"], m["W"], 2.5, V(xc - m["EAR_L"] / 2, y0 - m["W"] / 2, z0 + 26.5))
    spline = cyl_z(x0, y0, z0 + m["H"], z0 + m["H"] + 4, 3.0)
    return body.fuse(ears).fuse(spline)


def vs2_cup_local(r_face, t=0.0, z=0.0):
    """VS2-S30 bellows cup + VW7-M5 neck along +r, face (lip) at r_face"""
    r0 = r_face - 18.0
    s = cyl_r(r0 - 4, r0, 7.0, t, z)                       # neck / connector
    s = s.fuse(cyl_r(r0, r0 + 6, 15.0, t, z)).fuse(cyl_r(r0 + 6, r0 + 9, 12.0, t, z)).fuse(
        cyl_r(r0 + 9, r_face, 15.0, t, z))
    return s


def nema17_local(r, t, z_top):
    """NEMA17 hanging under a plate at z_top, shaft up; 42.3 square, 40 long"""
    a = 42.3 / 2
    rc = (r[0] + r[1]) / 2
    body = lbox((rc - a, rc + a), (t - a, t + a), (z_top - 40, z_top))
    boss = Part.makeCylinder(11, 2, V(rc, t, z_top))
    shaft = Part.makeCylinder(2.5, 14, V(rc, t, z_top))
    return body.fuse(boss).fuse(shaft), rc


def gt2_pulley(x, y, z0):
    return cyl_z(x, y, z0, z0 + 1, 8.0).fuse(cyl_z(x, y, z0 + 1, z0 + 7, 6.1)).fuse(cyl_z(x, y, z0 + 7, z0 + 8, 8.0))


# ---------------------------------------------------------------- fixed robot: base_330_js as it is
BASE_FC = os.path.normpath(os.path.join(ROOT, "..", "..", "base_330_js", "CAD", "base_330_js_assembly.FCStd"))
BASE_PARTS = {"plate": "plate", "odo_bracket": "print", "odo_arm": "print", "dead_wheel": "wheel", "amt102": "dark",
              "shaft_D6": "steel", "bearing_696": "steel", "eclip_shim": "steel", "bearing_F623": "steel",
              "spring": "steel", "screws_M3": "blackox", "hinges_PH": "dark", "motors_37D_PH": "dark",
              "wheels_JS7444_nominal_PH": "wheel", "wheels_JS7444_ENVELOPE": "envelope",
              "ball_units_KSM15_PH": "steel", "ball_holders": "print", "ball_shims": "print"}
_BASE = {}


def base_shapes():
    """the parts of mechanical/base_330_js/CAD/base_330_js_assembly.FCStd (clapets module A left out)"""
    if not _BASE:
        doc = App.openDocument(BASE_FC)
        for o in doc.Objects:
            if o.Name in BASE_PARTS:
                _BASE[o.Name] = o.Shape.copy()
        App.closeDocument(doc.Name)
    return _BASE


def robot():
    out = {}
    for n, s in base_shapes().items():
        out["base " + n] = ("robot", s.copy(), BASE_PARTS[n])
    out["column"] = ("column", tube_z(0, 0, ce.FLOOR_Z[1], 350, ce.R_COL, ce.R_COL - 2), "alu")
    out["beacon support"] = ("beacon", tube_z(0, 0, 350, 430, 40, 37).fuse(cyl_z(0, 0, 350, 353, 40)), "dark")
    return out


def pinion_rot(u, th):
    """tooth phase of the turn pinion so it meshes the hub sector (sector teeth at world angle 90 + phi - 6 k)"""
    alpha = 90.0 + ce.PINION_PSI[u]                           # hub -> pinion, math angle
    e0 = ((90.0 + ce.UNITS[u]["phi0"] - alpha) + 3.0) % 6.0 - 3.0
    return alpha + 186.0 - 2.0 * e0 - 2.0 * th


def fixed_unit(u, th):
    """turn MG996R on 2 printed posts + horn + printed pinion (turns 2x the turret), holder slide posts with feet,
    holder MG90S in a printed cradle"""
    out = {}
    T = ce.TURN[u]
    (x0, y0), sx = T["shaft"], T["sx"]
    z1 = ce.FLOOR_Z[1]
    zb = z1 + T["block"]
    m = ce.MG996
    xa, xb = sorted((x0 - sx * m["SHAFT_OFF"], x0 + sx * (m["L"] - m["SHAFT_OFF"])))
    out["turn MG996R " + u] = ("fixed" + u, mg996r_upright(x0, y0, sx, zb), "servo")
    if T["block"]:
        out["turn servo block " + u] = ("fixed" + u, Part.makeBox(xb - xa, m["W"], T["block"], V(xa, y0 - m["W"] / 2, z1)),
                                        "print")
    zE = zb + 26.5                                            # ear bottom: 2 printed posts under the ears
    for side, p0 in (("A", xa - 10), ("B", xb)):
        out["turn servo post %s %s" % (u, side)] = ("fixed" + u, Part.makeBox(10, 22, zE - z1, V(p0, y0 - 11, z1)), "print")
    top = zb + m["H"]
    horn = cyl_z(x0, y0, top, top + 4, 4.5).fuse(cyl_z(x0, y0, top + 2, top + 4, 10.5)).cut(cyl_z(x0, y0, top, top + 4, 3.0))
    for dy in (-7, 7):
        horn = horn.cut(cyl_z(x0, y0 + dy, top, top + 4, 1.1))
    out["turn horn " + u] = ("fixed" + u, horn, "dark")      # round horn of the servo kit
    g0, g1 = T["gear_z"]
    # printed pinion + hub down to the horn (2 M2 from under the horn), M3 down the bore into the spline;
    # pinion turns -2 x the turret
    pin = gear(30, 1.0, r_in=hw.CLR[3], z0=g0, z1=g1, cx=x0, cy=y0, rot=pinion_rot(u, th))
    pin = pin.fuse(cyl_z(x0, y0, top + 4, g0, 10.0)).cut(cyl_z(x0, y0, top + 4, g1, hw.CLR[3]))
    for dy in (-7, 7):
        pin = pin.cut(cyl_z(x0, y0 + dy, top + 4, top + 10, 0.8))
    out["turn pinion " + u] = ("fixed" + u, pin, "gear")
    phi = ce.UNITS[u]["phi0"]
    p0, p1 = ce.HOLD_POST_T
    for t in (-1, 1):                                         # slide posts + a foot inboard (2 floor screws each)
        tt = sorted((t * p0, t * p1))
        post = lbox((118, 128), tt, (z1, 195)).fuse(lbox((108, 118), tt, (z1, z1 + 10)))
        out["holder post %s%+d" % (u, t)] = ("fixed" + u, to_unit(post, phi), "hold")
    T0 = ce.MG90S_T                                           # MG90S 22.8 x 12.2, ears 32.5 long at 16 from the bottom
    mg = lbox((105, 117.2), (T0, T0 + 22.8), (z1, z1 + 28.5)).fuse(Part.makeCylinder(3, 4, V(111, T0 + 5, z1 + 28.5))).fuse(
        lbox((105, 117.2), (T0 - 4.85, T0 + 27.65), (z1 + 16, z1 + 18.5)))
    out["holder MG90S " + u] = ("fixed" + u, to_unit(mg, phi), "servo")
    cradle = lbox((101, 120), (T0 - 6.5, T0 + 33), (z1, z1 + 16)).cut(lbox((104.8, 117.4), (T0 - 0.2, T0 + 23), (z1, z1 + 16)))
    out["holder MG90S cradle " + u] = ("fixed" + u, to_unit(cradle, phi), "print")
    return out


# ---------------------------------------------------------------- turret, carriage, holder
def belt_strip(c1, c2, o0, o1, z0, z1):
    """flat strip between two pulley centres (local r, t), offset o0..o1 from the centre line"""
    d = np.array(c2, float) - np.array(c1, float)
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    pts = [np.array(c1) + n * o0, np.array(c2) + n * o0, np.array(c2) + n * o1, np.array(c1) + n * o1]
    w = Part.makePolygon([V(p[0], p[1], z0) for p in pts] + [V(pts[0][0], pts[0][1], z0)])
    return Part.Face(w).extrude(V(0, 0, z1 - z0))


def turret(u, th):
    U = ce.UNITS[u]
    phi = U["phi0"] + th
    g = "tur" + u
    zb, zh, zt, zht = U["zb"], U["zh"], U["zt"], U["zht"]
    P5 = ce.PLATE_T
    R, (rr, rt) = ce.R_SCREW, ce.ROD
    out = {}
    hub_b = Part.makeCylinder(ce.R_HUB, P5, V(0, 0, zh)).cut(Part.makeCylinder(ce.R_COL + 0.3, P5, V(0, 0, zh)))
    if u == "R":                                     # spacer boss (r 18, 3 tall) on the front gear's top face
        hub_b = hub_b.fuse(tube_z(0, 0, zh - 3, zh, 18, ce.R_COL + 0.3))
    web_b = lbox(ce.WEB_R, (-10, 10), (zh, zh + P5)).cut(Part.makeCylinder(ce.R_HUB, P5, V(0, 0, zh)))
    bot = hub_b.fuse(web_b).fuse(lbox((ce.WEB_R[1] if zh == zb else ce.RISER_R[1], 56.0), (-10, 10), (zb, zb + P5)))
    if zh != zb:
        bot = bot.fuse(lbox(ce.RISER_R, (-10, 10), (zb, zh + P5)))
    for r, t in ce.PAD_B:                            # pad within r 76 of the axis (it turns over the wheel envelope)
        bot = bot.fuse(lbox(r, t, (zb, zb + P5)))
    bot = bot.cut(cyl_z(R, 0, zb, zb + P5, 5.0)).cut(cyl_z(rr, rt, zb, zb + P5, 4.0))
    out["bottom plate " + u] = (g, to_unit(bot, phi), "tur" + u)
    a0, a1 = -ce.GEAR_SECTOR[1], -ce.GEAR_SECTOR[0]           # polar offsets -> local angles
    g0, g1 = ce.TURN[u]["gear_z"]
    sector = gear(60, 1.0, a0, a1, r_in=ce.R_COL + 0.3, z0=g0, z1=g1)
    sector = sector.fuse(Part.makeCylinder(ce.R_HUB, g0 - (zh + P5), V(0, 0, zh + P5))).cut(
        Part.makeCylinder(ce.R_COL + 0.3, g1 - zh, V(0, 0, zh)))
    out["turn gear sector " + u] = (g, to_unit(sector, phi), "gear")
    # top plate
    hub_t = Part.makeCylinder(ce.R_HUB, P5, V(0, 0, zht)).cut(Part.makeCylinder(ce.R_COL + 0.3, P5, V(0, 0, zht)))
    if u == "F":                                     # spacer boss down to 1 mm over the rear top hub
        hub_t = hub_t.fuse(tube_z(0, 0, zht - 3, zht, 18, ce.R_COL + 0.3))
    web_t = lbox(ce.WEB_R, (-10, 10), (zht, zht + P5)).cut(Part.makeCylinder(ce.R_HUB, P5, V(0, 0, zht)))
    spoke_t = lbox((ce.WEB_R[1] if zht == zt else 31.0, ce.PAD_T["r"][0]), (-21, 21), (zt, zt + P5))
    pad_t = lbox(ce.PAD_T["r"], ce.PAD_T["t"], (zt, zt + P5))
    top = hub_t.fuse(web_t).fuse(spoke_t).fuse(pad_t)
    if zht != zt:
        top = top.fuse(lbox((25, 31), (-30, -20), (zht, zt + P5))).fuse(
            lbox((ce.WEB_R[0], 30), (-30, 10), (zht, zht + P5)).cut(Part.makeCylinder(ce.R_HUB, P5, V(0, 0, zht))))
    nema, rn = nema17_local((ce.NEMA_C[0] - 21.15, ce.NEMA_C[0] + 21.15), ce.NEMA_C[1], zt)
    top = top.cut(cyl_z(rn, ce.NEMA_C[1], zt, zt + P5, 11.5)).cut(cyl_z(R, 0, zt, zt + P5, 11.0)).cut(
        cyl_z(rr, rt, zt, zt + P5, 4.0))
    out["top plate " + u] = (g, to_unit(top, phi), "tur" + u)
    out["608 bearing " + u] = (g, to_unit(tube_z(R, 0, zt, zt + 7, 11, 4), phi), "steel")
    out["NEMA17 " + u] = (g, to_unit(nema, phi), "servo")
    out["T8 screw " + u] = ("screw" + u, to_unit(cyl_z(R, 0, zb + P5 + 1, 349, 4.0), phi), "steel")
    out["guide rod " + u] = ("screw" + u, to_unit(cyl_z(rr, rt, zb, zt + P5, 4.0), phi), "steel")
    zp = zt + P5 + 1 + 0.5
    pul = gt2_pulley(rn, ce.NEMA_C[1], zp).fuse(gt2_pulley(R, 0, zp))
    out["GT2 pulleys " + u] = (g, to_unit(pul, phi), "steel")
    c1, c2 = (R, 0.0), (rn, ce.NEMA_C[1])
    belt = belt_strip(c1, c2, 6.1, 7.5, zp + 1, zp + 7).fuse(belt_strip(c1, c2, -7.5, -6.1, zp + 1, zp + 7))
    out["GT2 belt " + u] = (g, to_unit(belt, phi), "belt")
    return out


def carriage(u, th, zc, spin, held):
    phi = ce.UNITS[u]["phi0"] + th
    g = "car" + u
    out = {}
    R, (rr, rt) = ce.R_SCREW, ce.ROD
    DF = ce.DF
    z0 = zc + ce.CAR_A                                        # block bottom (the cup axis is at zc, under it)
    z1 = z0 + ce.CAR_H
    zl = z0 + ce.CAR_LOW_H
    blk = lbox(ce.CAR_R, (ce.CAR_T[0], ce.CAR_T_LOW), (z0, zl)).fuse(lbox(ce.CAR_R, ce.CAR_T, (zl, z1)))
    blk = blk.cut(cyl_z(R, 0, z0, z1, 4.6)).cut(cyl_z(R, 0, z0 + 4, z1 - 12, 5.2)).cut(
        cyl_z(R, 0, z1 - 12, z1, 11.3))                       # T8: screw clearance, nut body, flange pocket (open top)
    blk = blk.cut(cyl_z(rr, rt, z0, z1, 4.6)).cut(cyl_z(rr, rt, z0 + 2, z1, 7.6))   # LM8UU on a ledge
    arm = lbox((ce.CAR_R[1], 144 + DF), (-17, 12.5), (z0, z0 + 4)).fuse(lbox((94, 144 + DF), (12.5, 38), (z0, z0 + 4)))
    drop = lbox((136 + DF, 140 + DF), (-17, 38), (zc - 12, z0 + 4)).cut(
        lbox((136 + DF, 140 + DF), (-10.5, 30.8), (zc - 10.2, zc + 10.2)))
    out["carriage " + u] = (g, to_unit(blk.fuse(arm).fuse(drop), phi), "car")
    nut = tube_z(R, 0, z1 - 23.5, z1 - 12, 5.1, 4.0).fuse(tube_z(R, 0, z1 - 12, z1 - 8.5, 11, 4.0))   # T8 nut, 15 long
    for a in range(4):
        nut = nut.cut(cyl_z(R + 8 * math.cos(a * math.pi / 2), 8 * math.sin(a * math.pi / 2), z1 - 12, z1 - 8.5, 1.75))
    out["T8 nut " + u] = (g, to_unit(nut, phi), "brass")
    out["LM8UU " + u] = (g, to_unit(tube_z(rr, rt, z0 + 2, z0 + 26, 7.5, 4.0), phi), "steel")
    face = 143.2 + DF
    out["spin MG996R " + u] = (g, to_unit(mg996r_local(face, 0.0, zc), phi), "servo")
    # horn + adapter + cup turn with the spin; a tab on the horn shows the angle
    sp = math.radians(spin)
    tab = lbox((147 + DF, 149.5 + DF), (-2, 2), (0, 11))
    rot = np.array([[1, 0, 0], [0, math.cos(sp), -math.sin(sp)], [0, math.sin(sp), math.cos(sp)]])
    tab = moved(tab, rot, (0, 0, zc))
    horn = cyl_r(147 + DF, 149.5 + DF, 10, 0, zc).fuse(cyl_r(149.5 + DF, 150 + DF, 8, 0, zc)).fuse(tab)
    out["spin horn " + u] = (g, to_unit(horn, phi), "dark")
    out["shaft cup " + u] = (g + "cup", to_unit(vs2_cup_local(ce.FACE, 0, zc), phi), "cup")
    if held:
        b = ce.stone_box("held", ce.UNITS[u]["phi0"] + th, zc, spin)
        out["held stone %s%s" % (u, held)] = ("held" + u, obox(b), "held")
    return out


def holder(u, L):
    phi = ce.UNITS[u]["phi0"]
    g = "hold" + u
    DF = ce.DF
    fr = lbox((128 + DF, 146 + DF), (-110, 110), (30 + L, 38 + L))
    for t in (-ce.HOLD_X, ce.HOLD_X):
        fr = fr.fuse(lbox((128 + DF, 150 + DF), (t - 10, t + 10), (38 + L, ce.HOLD_TOP + L)))
    out = {"holder frame " + u: (g, to_unit(fr, phi), "hold")}
    for t in (-ce.HOLD_X, ce.HOLD_X):
        for lv in ("B", "M"):
            out["holder cup %s%s%+d" % (u, lv, t)] = (g + "cup", to_unit(vs2_cup_local(ce.FACE, t, ce.Z_ST[lv] + L), phi),
                                                      "cup")
    return out


def stones(st):
    out = {}
    for u in "FR":
        for lv in st["stack"][u]:
            b = ce.stone_box("s", ce.UNITS[u]["phi0"], ce.Z_ST[lv] + st["L"][u], 0.0)
            out["stone %s%s" % (u, lv)] = ("stack" + u, obox(b), "stone")
    for lv, u, y in st["towers"]:
        b = ce.stone_box("t", ce.UNITS[u]["phi0"] + 90, ce.Z_SET, 90.0)
        b.c = b.c + [0, y, 0]
        out["tower %s%s" % (u, lv)] = ("tower" + u + lv, obox(b), "tower")
    return out


def reserves():
    out = {}
    for v, key in zip(ce.free_volumes(), ("reserve_grail", "reserve_launch", "reserve_pump", "reserve_pump")):
        out["RESERVE " + v.name] = ("reserve", obox(v), key)
    return out


def pose(st):
    P = {}
    P.update(robot())
    for u in "FR":
        P.update(fixed_unit(u, st["th"][u]))
        P.update(turret(u, st["th"][u]))
        P.update(carriage(u, st["th"][u], st["zc"][u], st["spin"][u], st["held"][u]))
        P.update(holder(u, st["L"][u]))
    P.update(stones(st))
    hw.apply(P, st, HF)
    return P


HF = types.SimpleNamespace(ce=ce, cyl_z=cyl_z, cyl_r=cyl_r, to_unit=to_unit)


# ---------------------------------------------------------------- checks
def allowed(na, ga, nb, gb):
    if ga == gb:
        return True
    if nb in hw.JOINS.get(na, ()) or na in hw.JOINS.get(nb, ()):
        return True                                          # fastener through a part of another group (floor...)
    pair = {ga, gb}
    if "reserve" in pair or "beacon" in pair or "grail" in pair:
        return True                                          # checked separately
    for (n1, g1, n2, g2) in ((na, ga, nb, gb), (nb, gb, na, ga)):
        u = g1[-4] if g1.endswith("cup") else g1[-1]
        if g1 == "column" and g2.startswith("tur"):
            return True                                      # turret hubs turn on the column
        if g1 == "screw" + u and g2 in ("car" + u, "tur" + u):
            return True                                      # screw / rod through the carriage and the plates
        if n1 == "turn pinion " + u and n2 == "turn gear sector " + u:
            return True                                      # the pair meshes
        if g1 == "car" + u + "cup" and (g2.startswith(("stack", "held", "tower"))):
            return True                                      # shaft cup on a stone face
        if g1 == "hold" + u + "cup" and g2 in ("stack" + u, "held" + u):
            return True                                      # holder cups on their stack
        if g1 == "car" + u + "cup" and g2 == "car" + u:
            return True
        if g1 == "hold" + u + "cup" and g2 == "hold" + u:
            return True
    return False


def common_vol(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    v = 0.0
    for sa in a.Solids:
        if not sa.BoundBox.intersect(b.BoundBox):
            continue
        for sb in b.Solids:
            if sa.BoundBox.intersect(sb.BoundBox):
                try:
                    v += sa.common(sb).Volume
                except Exception:
                    pass
    return v


def check_pose(P):
    names = list(P)
    bad = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            ga, a, _ = P[na]
            gb, b, _ = P[nb]
            if allowed(na, ga, nb, gb):
                continue
            if ga.startswith(("stack", "held", "tower")) and gb.startswith(("stack", "held", "tower")):
                a = a.copy(); a.scale(0.99, a.BoundBox.Center)
                b = b.copy(); b.scale(0.99, b.BoundBox.Center)
            v = common_vol(a, b)
            if v > 1.0:
                bad.append("%s x %s (%.0f mm3)" % (na, nb, v))
    res = []
    for n, (g, s, _) in P.items():
        if g != "reserve" or n.startswith("RESERVE pumps"):
            continue
        for m, (h, t, _) in P.items():
            if h in ("reserve", "robot") or m == n:
                continue
            v = common_vol(s, t)
            if v > 1.0:
                res.append("%s x %s (%.0f mm3)" % (n, m, v))
    zs = [s.BoundBox.ZMax for n, (g, s, _) in P.items()
          if g not in ("column", "beacon", "reserve", "grail") and not g.startswith(("stack", "tower"))]
    return bad, res, max(zs)


def perimeter(P):
    pts = [tuple(p) for p in ce.body_outline()]
    for n, (g, s, _) in P.items():
        if g in ("reserve", "beacon") or g.startswith(("stack", "held", "tower")):
            continue
        try:
            vs = s.tessellate(2.0)[0]
        except Exception:
            vs = [v.Point for v in s.Vertexes]
        pts += [(p.x, p.y) for p in vs]
    H = ce.hull2(pts)
    return sum(math.hypot(H[i][0] - H[i - 1][0], H[i][1] - H[i - 1][1]) for i in range(len(H)))


# ---------------------------------------------------------------- save
GROUP_LABEL = {"robot": "Base_330_js", "odom": "Odometry", "column": "Column_and_beacon", "beacon": "Column_and_beacon",
               "colhw": "Column_and_beacon",
               "grail": "Reserved_volumes", "reserve": "Reserved_volumes"}


def group_label(g):
    if g in GROUP_LABEL:
        return GROUP_LABEL[g]
    u = UNAME.get(g[-1], "") if not g.endswith("cup") else UNAME.get(g[-4], "")
    for key, lab in (("tur", "Turret_"), ("screw", "Turret_"), ("car", "Carriage_"), ("held", "Carriage_"),
                     ("hold", "Holder_"), ("fixed", "Fixed_drives_"), ("stack", "Stones_"), ("tower", "Towers")):
        if g.startswith(key):
            if key == "tower":
                return lab
            uu = g[len(key)] if len(g) > len(key) else ""
            return lab + UNAME.get(uu, uu)
    return g


def save(name, P):
    doc = App.newDocument(name)
    groups = {}
    for n, (g, s, ck) in P.items():
        lab = group_label(g) + ("_fasteners" if n in hw.FASTENERS else "")
        if lab not in groups:
            groups[lab] = doc.addObject("App::DocumentObjectGroup", lab)
        o = doc.addObject("Part::Feature", n.replace(" ", "_").replace("+", "p").replace("-", "m").replace("(", "")
                          .replace(")", "").replace(".", "_"))
        o.Label = n
        o.Shape = s
        groups[lab].addObject(o)
        if App.GuiUp:
            c = COL.get(ck, (0.7, 0.7, 0.7))
            o.ViewObject.ShapeColor = c
            o.ViewObject.LineColor = tuple(x * 0.45 for x in c)
            if g in ("reserve", "grail"):
                o.ViewObject.Transparency = 70
            if ck == "cup":
                o.ViewObject.Transparency = 20
            if ck == "envelope":                     # JSUMO worst-case envelope (checked against every part)
                o.ViewObject.Transparency = 85
    doc.recompute()
    if App.GuiUp:
        import FreeCADGui as Gui
        v = Gui.getDocument(doc.Name).activeView()
        v.viewIsometric()
        v.fitAll()
    path = os.path.join(OUT, name + ".FCStd")
    doc.saveAs(path)
    App.closeDocument(doc.Name)
    return path


def state(**kw):
    st = {"L": {"F": 0.0, "R": 0.0}, "th": {"F": 0.0, "R": 0.0}, "zc": {"F": ce.Z_ST["T"], "R": ce.Z_ST["T"]},
          "spin": {"F": 0.0, "R": 0.0}, "held": {"F": None, "R": None},
          "stack": {"F": ["B", "M", "T"], "R": ["B", "M", "T"]}, "towers": []}
    for k, v in kw.items():
        st[k].update(v) if isinstance(v, dict) else st.__setitem__(k, v)
    return st


def main():
    os.makedirs(OUT, exist_ok=True)
    poses = [
        ("HUB_E_HOME", "home: both stacks set down, shaft cups on the top stones, holder cups on the lower ones",
         state()),
        ("HUB_E_1_FRONT_TOP_TURN45", "front top stone lifted 8 and turned 45 deg, rear holds its stack",
         state(th={"F": 45.0}, zc={"F": ce.Z_TURN_TOP}, held={"F": "T"}, stack={"F": ["B", "M"]})),
        ("HUB_E_2_FRONT_TOP_SPIN", "front top stone at 90 deg, spinning (45), rear holds its stack",
         state(th={"F": 90.0}, zc={"F": ce.Z_SPIN}, spin={"F": 45.0}, held={"F": "T"}, stack={"F": ["B", "M"]})),
        ("HUB_E_3_REAR_MIDDLE_UP", "front done (its towers left behind); rear middle stone stood up beside the robot,"
         " rear top tower 340 mm behind",
         state(th={"R": 90.0}, zc={"R": ce.Z_SET}, spin={"R": 90.0}, held={"R": "M"},
               stack={"F": [], "R": ["B"]}, towers=[("T", "R", -ce.DRIVE)])),
        ("HUB_E_DEPLOYED", "both turrets at 90, cups spun, holders up 15 (every mechanism open, FAQ Q10), no stones",
         state(th={"F": 90.0, "R": 90.0}, zc={"F": ce.Z_SET, "R": ce.Z_SET}, spin={"F": 90.0, "R": 90.0},
               L={"F": ce.L_CARRY, "R": ce.L_CARRY}, stack={"F": [], "R": []})),
    ]
    extra = [("carry (holders + cups up 15)", state(L={"F": ce.L_CARRY, "R": ce.L_CARRY},
                                                   zc={"F": ce.Z_ST["T"] + ce.L_CARRY, "R": ce.Z_ST["T"] + ce.L_CARRY}))]
    for u in "FR":
        other = "R" if u == "F" else "F"
        for th in (15.0, 30.0, 60.0, 75.0):
            extra.append(("%s middle stone turning at %g" % (UNAME[u], th),
                          state(th={u: th}, zc={u: ce.Z_TURN}, held={u: "M"}, stack={u: ["B"]})))
        extra.append(("%s cup down at the bottom stone" % UNAME[u], state(zc={u: ce.Z_ST["B"]}, stack={u: ["B"]})))
        extra.append(("%s bottom stone set down as a tower" % UNAME[u],
                      state(th={u: 90.0}, zc={u: ce.Z_SET}, spin={u: 90.0}, held={u: "B"}, stack={u: []})))
    R = ["Central hub - option E (doubled) - FreeCAD model report (fc/hub_e_fc.py)", ""]
    R.append("Solid clash check (FreeCAD booleans, > 1 mm3) of the saved poses + %d extra poses. Left out by design:"
             % len(extra))
    R.append("parts of one group, turret hubs on the column, screw + rod through their plates and carriage, the turn")
    R.append("pinion in its gear sector, cups on stone faces, stones of one stack (shrunk 1 %% when checked together).")
    R.append("Base = mechanical/base_330_js as it is (plate, 37D motors + hinges, JSUMO worst-case envelope, both odometry modules, ball units).")
    R.append("")
    allbad, ztop = 0, 0.0
    for name, label, st in poses:
        P = pose(st)
        bad, res, zmax = check_pose(P)
        per = perimeter(P)
        ztop = max(ztop, zmax)
        allbad += len(bad) + len(res)
        save(name, P)
        R.append("%-26s highest %.1f  perimeter %.0f  %s" % (name, zmax, per,
                 "no clashes" if not (bad or res) else "%d clashes" % (len(bad) + len(res))))
        R.append("    " + label)
        R += ["    " + b for b in bad + res]
        if name == "HUB_E_HOME":
            bom = dict(hw.BOM)
            Part.makeCompound([s for n, (g, s, _) in P.items() if g not in ("reserve",)]).exportStep(
                os.path.join(OUT, "HUB_E_HOME.step"))
    nb = 0
    for label, st in extra:
        P = pose(st)
        bad, res, zmax = check_pose(P)
        ztop = max(ztop, zmax)
        nb += len(bad) + len(res)
        if bad or res:
            R.append("%-40s highest %.1f  %d clashes" % (label, zmax, len(bad) + len(res)))
            R += ["    " + b for b in bad + res]
    R.append("")
    R.append("extra poses (%d): %s" % (len(extra), "no clashes" if nb == 0 else "%d clashes, see above" % nb))
    R.append("highest point of the mechanism + held stones over all poses: %.1f mm (limit 350 [GR F.3]; the column"
             " is the beacon mast)" % ztop)
    R.append("")
    R.append("Parts (both units): 2 NEMA17 + 2 T8 screws (278) + brass nuts + 2 GT2 belts + 4 GT2 20T pulleys + 2 x 608;")
    R.append("2 guide rods 8 mm (276, e-clip groove at the bottom) + 2 LM8UU; 4 MG996R (2 turn, 2 spin) + 2 MG90S (holder lift); 2 printed 60 T gear")
    R.append("sectors + 2 printed 30 T pinions (m 1); 10 VS2-S30 cups (2 shaft + 8 holder); column 20 mm aluminium tube.")
    R.append("Printed (ABS, D-023, blue in the model): 2 bottom plates (with their 60 T sector) + 2 top plates, 2 carriages,")
    R.append("2 holder frames, 4 holder slide posts, 4 turn servo posts, 2 pinions (with hub), 2 MG90S cradles, column foot,")
    R.append("1 hub clamp collar, beacon plug. Bought: 2 round servo horns (MG996R kit).")
    R.append("")
    R.append("Fasteners (fc/hub_e_hw.py, both units, counted in HUB_E_HOME):")
    R += ["  %3d x %s" % (n, k) for k, n in sorted(bom.items())]
    R.append("  %3d   total" % sum(bom.values()))
    R.append("")
    R.append("Wrote CAD_FC/HUB_E_*.FCStd + CAD_FC/HUB_E_HOME.step")
    txt = "\n".join(R)
    with open(os.path.join(ROOT, "hub_e_fc_report.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)


def run():
    try:
        main()
    except Exception:
        with open(os.path.join(ROOT, "hub_e_fc_error.txt"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
    if App.GuiUp:
        import FreeCADGui as Gui
        Gui.getMainWindow().close()


import builtins                                  # noqa: E402
if not getattr(builtins, "HUB_E_IMPORT_ONLY", False):    # set by fc/hub_e_gif.py, which only needs the shapes
    if App.GuiUp:
        from PySide import QtCore
        QtCore.QTimer.singleShot(2000, run)
    else:
        run()
