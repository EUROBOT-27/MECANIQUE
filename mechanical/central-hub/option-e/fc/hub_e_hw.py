# hub_e_hw.py - Central hub OPTION E: screws, nuts, washers, inserts and collars (Ayoub, 2026-11-20, proposal).
# Used by fc/hub_e_fc.py: apply(P, st, hf) adds every fastener of a pose to the part dict P and cuts its holes,
# counterbores, insert holes and nut pockets into the parts it goes through.
# Rules from mechanical/design-principles.md: M3 heat-set insert K 6.0 L 6.0 -> hole 5.4, blind depth 7, wall >= 1.6;
# nut pockets M3 6.0 x 6.9 x 2.8 (M4 7.4 x 8.4 x 3.6), open to free air; servo ears on nuts under a 1.6 mm roof;
# rod / column clamps coupler style (screw across the slot inside the round outline). ISO metric sizes only.
# Frames: local unit frame (r, t, z) as hub_e_fc.lbox, mapped to the world by hf.to_unit(shape, phi).
import math
from collections import Counter
import FreeCAD as App
import Part

V = App.Vector

#            dk    k    socket
SHCS = {2: (3.8, 2.0, 1.5), 3: (5.5, 3.0, 2.5), 4: (7.0, 4.0, 3.0), 5: (8.5, 5.0, 4.0)}
NUT = {2: (4.0, 1.6), 3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0)}          # AF, height (ISO 4032)
NYLOC_H = {3: 4.0, 4: 5.0}                                                   # DIN 985
WASHER = {3: (3.2, 7.0, 0.5), 4: (4.3, 9.0, 0.8), 5: (5.3, 10.0, 1.0)}      # DIN 125: id, od, h
INSERT = {3: (5.4, 6.0), 4: (6.3, 8.0)}            # drawn at the hole Ø (design-principles), length
CLR = {2: 1.1, 3: 1.7, 4: 2.2, 5: 2.75}            # clearance hole radius (ABS: +0.2)
INS_R = {3: 2.7, 4: 3.15}                          # insert hole radius

FASTENERS = set()      # part names that are fasteners (own folder in the FreeCAD tree)
JOINS = {}             # fastener name -> names of parts of other groups it may go into (screw through the floor...)
BOM = Counter()        # filled by apply(); the report prints it for the HOME pose


# ---------------------------------------------------------------- shapes (local: axis +Z, z = 0 at the bearing face)
def put(shape, at, axis):
    """local +Z -> axis, local origin -> at"""
    s = shape.copy()
    s.transformShape(App.Placement(V(*at), App.Rotation(V(0, 0, 1), V(*axis))).toMatrix())
    return s


def hexagon(af, h, z0=0.0):
    rc = af / math.sqrt(3)
    pts = [V(rc * math.cos(math.radians(30 + 60 * k)), rc * math.sin(math.radians(30 + 60 * k)), z0) for k in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def shcs_shape(d, L):
    """socket head cap screw ISO 4762: head z -k..0, shank 0..L"""
    dk, k, s = SHCS[d]
    head = Part.makeCylinder(dk / 2, k, V(0, 0, -k)).cut(hexagon(s, 0.6 * k, -k))
    return head.fuse(Part.makeCylinder(d / 2, L))


def setscrew_shape(d, L):
    """set screw ISO 4026, socket at z = 0"""
    return Part.makeCylinder(d / 2, L).cut(hexagon(SHCS[d][2] if d in SHCS else 2.0, 0.5 * L))


def nut_shape(d, nyloc=False):
    af, m = NUT[d]
    h = NYLOC_H[d] if nyloc else m
    s = hexagon(af, h).cut(Part.makeCylinder(d / 2, h))
    return s


def washer_shape(d):
    di, do, h = WASHER[d]
    return Part.makeCylinder(do / 2, h).cut(Part.makeCylinder(di / 2, h))


def insert_shape(d):
    do, L = INSERT[d]
    s = Part.makeCylinder(do / 2, L).cut(Part.makeCylinder(d / 2, L))
    for z in (L * 0.3, L * 0.65):                                           # two knurl bands
        s = s.cut(Part.makeCylinder(do / 2, 0.6, V(0, 0, z)).cut(Part.makeCylinder(do / 2 - 0.3, 0.6, V(0, 0, z))))
    return s


def collar_din705_shape(d, D, b, set_d):
    """steel shaft collar DIN 705: ring along Z (0..b), set screw hole along +X"""
    s = Part.makeCylinder(D / 2, b).cut(Part.makeCylinder(d / 2, b))
    return s.cut(Part.makeCylinder(set_d / 2, D / 2, V(0, 0, b / 2), V(1, 0, 0)))


# ---------------------------------------------------------------- kit
class Kit:
    def __init__(s, P, tf):
        s.P, s.tf, s.cuts = P, tf, {}

    def cut(s, host, shape_local):
        s.cuts.setdefault(host, []).append(s.tf(shape_local))

    def add(s, name, group, shape_local, ck, bom=None, joins=(), fastener=True):
        assert name not in s.P, name
        s.P[name] = (group, s.tf(shape_local), ck)
        if fastener:
            FASTENERS.add(name)
        if joins:
            JOINS[name] = set(joins)
        if bom:
            BOM[bom] += 1

    def screw(s, name, group, d, L, at, axis, joins=()):
        s.add(name, group, put(shcs_shape(d, L), at, axis), "blackox", "SHCS M%gx%g ISO 4762" % (d, L), joins)

    def nut(s, name, group, d, at, axis, nyloc=False, joins=()):
        s.add(name, group, put(nut_shape(d, nyloc), at, axis), "zinc",
              ("nyloc nut M%g DIN 985" if nyloc else "hex nut M%g ISO 4032") % d, joins)

    def washer(s, name, group, d, at, axis, joins=()):
        s.add(name, group, put(washer_shape(d), at, axis), "zinc", "washer M%g DIN 125" % d, joins)

    def insert(s, name, group, d, at, axis):
        s.add(name, group, put(insert_shape(d), at, axis), "brass", "heat-set insert M%g (K6 L6)" % d
              if d == 3 else "heat-set insert M%g" % d)

    def finish(s):
        for host, cl in s.cuts.items():
            g, sh, ck = s.P[host]
            c = cl[0] if len(cl) == 1 else Part.makeCompound(cl)
            s.P[host] = (g, sh.cut(c), ck)


def box(lo, hi):
    return Part.makeBox(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], V(*lo))


# ---------------------------------------------------------------- column, hub collars, beacon support
def column_hw(P, hf):
    ce = hf.ce
    k = Kit(P, lambda s: s)
    g = "colhw"
    z0, z1 = ce.FLOOR_Z
    # printed column foot: flange r24 on the floor + sleeve r13.5, bore 10.1; 4 x M4 through the floor plate
    zs = ce.UNITS["F"]["zh"]                                  # the sleeve carries the front bottom hub (no collar there)
    foot = hf.cyl_z(0, 0, z1, z1 + 6, 24).fuse(hf.cyl_z(0, 0, z1 + 6, zs, 13.5)).cut(hf.cyl_z(0, 0, z1, zs, 10.1))
    P["column foot"] = (g, foot, "print")
    for i in range(4):
        a = math.radians(45 + 90 * i)
        x, y = 18.5 * math.cos(a), 18.5 * math.sin(a)
        k.cut("column foot", hf.cyl_z(x, y, z1 - 1, z1 + 7, CLR[4]))
        k.cut("base plate", hf.cyl_z(x, y, z0 - 1, z1 + 1, CLR[4]))
        n = "column foot M4 %d" % (i + 1)
        k.washer(n + " washer", g, 4, (x, y, z1 + 6), (0, 0, 1))
        k.screw(n + " screw", g, 4, 20, (x, y, z1 + 6.8), (0, 0, -1), joins=("base plate",))
        k.washer(n + " washer under", g, 4, (x, y, z0), (0, 0, -1))
        k.nut(n + " nyloc", g, 4, (x, y, z0 - 0.8), (0, 0, -1), nyloc=True)
    # cross bolt M4 along Y through the sleeve and the tube (drilled Ø4.4): the column can neither turn nor lift
    # (along Y: the 37D motor back ends are at x +-15)
    zc = z1 + 16
    k.cut("column foot", Part.makeCylinder(CLR[4], 28, V(0, -14, zc), V(0, 1, 0)))
    k.cut("column", Part.makeCylinder(CLR[4], 22, V(0, -11, zc), V(0, 1, 0)))
    k.washer("column cross bolt washer A", g, 4, (0, -13.5, zc), (0, -1, 0))
    k.screw("column cross bolt M4x40", g, 4, 40, (0, -14.3, zc), (0, 1, 0), joins=("column",))
    k.washer("column cross bolt washer B", g, 4, (0, 13.5, zc), (0, 1, 0))
    k.nut("column cross bolt nyloc", g, 4, (0, 14.3, zc), (0, 1, 0), nyloc=True)
    # printed clamp collar (coupler style) over the front top hub: holds the turret hub stack down on the foot sleeve
    for nm, zb in (("top", ce.UNITS["F"]["zt"] + ce.PLATE_T),):
        zm = zb + 5
        col = hf.cyl_z(0, 0, zb, zb + 10, 20).cut(hf.cyl_z(0, 0, zb, zb + 10, 10.1))
        col = col.cut(box((10, -0.75, zb), (21, 0.75, zb + 10)))                          # slot
        col = col.cut(Part.makeCylinder(3.25, 15, V(15, -21, zm), V(0, 1, 0)))            # head counterbore
        col = col.cut(Part.makeCylinder(CLR[3], 42, V(15, -21, zm), V(0, 1, 0)))
        col = col.cut(box((12, 6, zm - 3.45), (21, 8.8, zm + 3.45)))                     # M3 nut pocket, open outward
        P["hub collar " + nm] = (g, col, "print")
        k.screw("hub collar %s M3x16" % nm, g, 3, 16, (15, -6, zm), (0, 1, 0))
        k.nut("hub collar %s nut" % nm, g, 3, (15, 6.2, zm), (0, 1, 0))
    # beacon support: printed plug in the tube top + M4 insert, M4 screw down through the support's base disc
    plug = hf.cyl_z(0, 0, 325, 350, 7.9).cut(hf.cyl_z(0, 0, 341, 350, INS_R[4]))
    P["beacon plug"] = ("beacon", plug, "print")
    k.insert("beacon plug insert M4", "beacon", 4, (0, 0, 350), (0, 0, -1))
    k.cut("beacon support", hf.cyl_z(0, 0, 349, 354, CLR[4]))
    k.washer("beacon M4 washer", "beacon", 4, (0, 0, 353), (0, 0, 1))
    k.screw("beacon M4x12", "beacon", 4, 12, (0, 0, 353.8), (0, 0, -1), joins=("beacon support",))
    k.finish()


# ---------------------------------------------------------------- turret
def turret_hw(P, hf, u, th):
    ce = hf.ce
    U = ce.UNITS[u]
    phi = U["phi0"] + th
    k = Kit(P, lambda s: hf.to_unit(s, phi))
    g, zb, zt = "tur" + u, U["zb"], U["zt"]
    rn, tn = ce.NEMA_C
    # NEMA17 on the top plate: 4 x M3x10 + washers (31 mm square)
    for i, (a, b) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        x, y = rn + a * 15.5, tn + b * 15.5
        k.cut("top plate " + u, hf.cyl_z(x, y, zt - 1, zt + ce.PLATE_T + 1, CLR[3]))
        k.washer("NEMA %s M3 washer %d" % (u, i + 1), g, 3, (x, y, zt + ce.PLATE_T), (0, 0, 1))
        k.screw("NEMA %s M3x10 %d" % (u, i + 1), g, 3, 10, (x, y, zt + ce.PLATE_T + 0.5), (0, 0, -1))
    # guide rod: DIN 705 collar (8 / 16 x 8, M4 set screw) over the top pad; e-clip DIN 6799-6 under the bottom pad
    # (a collar there would turn over the 37D motor, 3 mm under the pad)
    r, t = ce.ROD
    k.add("rod e-clip " + u, "screw" + u, put(Part.makeCylinder(6.25, 0.7).cut(Part.makeCylinder(3.2, 0.7)),
                                               (r, t, zb - 0.7), (0, 0, 1)), "blackox", "e-clip DIN 6799-6 (rod Ø8, groove)")
    for nm, z0 in (("top", zt + ce.PLATE_T),):
        c = put(collar_din705_shape(8, 16, 8, 4), (r, t, z0), (0, 0, 1))
        k.add("rod collar %s %s" % (u, nm), "screw" + u, c, "steel", "shaft collar 8 mm DIN 705 (D16 b8)")
        k.add("rod collar %s %s set screw" % (u, nm), "screw" + u, put(setscrew_shape(4, 4), (r + 8, t, z0 + 4),
                                                                         (-1, 0, 0)), "blackox", "set screw M4x4 ISO 4026")
    k.finish()


# ---------------------------------------------------------------- carriage
def carriage_hw(P, hf, u, th, zc):
    ce = hf.ce
    phi = ce.UNITS[u]["phi0"] + th
    k = Kit(P, lambda s: hf.to_unit(s, phi))
    g, host, R = "car" + u, "carriage " + u, ce.R_SCREW
    rr, rt = ce.ROD
    z0 = zc + ce.CAR_A
    z1 = z0 + ce.CAR_H
    # T8 brass nut: 2 x M3x18 down through the flange (PCD 16) and the block, nuts in pockets near the bottom, open to the
    # -r / +r faces (no inserts: the flange holes are 8 from the screw axis, the nut bore is 5.2)
    for i, (x, lo, hi) in enumerate(((R - 8, ce.CAR_R[0] - 1, R - 8 + 3.45), (R + 8, R + 8 - 3.45, ce.CAR_R[1] + 1))):
        k.cut(host, hf.cyl_z(x, 0, z0 + 0.5, z1 - 8, CLR[3]))
        k.cut(host, box((lo, -3.0, z0 + 1.5), (hi, 3.0, z0 + 4.3)))
        k.screw("T8 nut %s M3x18 %d" % (u, i + 1), g, 3, 18, (x, 0, z1 - 8.5), (0, 0, -1))
        k.nut("T8 nut %s M3 nut %d" % (u, i + 1), g, 3, (x, 0, z0 + 1.7), (0, 0, 1))
    # LM8UU: clamp (coupler style): slot from the bore to the -t face, M3x20 across it along r, nut pocket open to -t
    zm, ts = z0 + 14, ce.CAR_T[0] + 4.5
    k.cut(host, box((rr - 0.75, ce.CAR_T[0] - 1, z0), (rr + 0.75, rt - 7, z1)))
    k.cut(host, hf.cyl_r(ce.CAR_R[0] - 1, rr - 6, 3.25, ts, zm))
    k.cut(host, hf.cyl_r(ce.CAR_R[0] - 1, rr + 15, CLR[3], ts, zm))
    k.cut(host, box((rr + 6, ce.CAR_T[0] - 1, zm - 3.45), (rr + 8.8, ts + 3, zm + 3.45)))
    k.screw("LM8UU clamp %s M3x20" % u, g, 3, 20, (rr - 6, ts, zm), (1, 0, 0))
    k.nut("LM8UU clamp %s nut" % u, g, 3, (rr + 6.2, ts, zm), (1, 0, 0))
    # spin MG996R: 4 x M3x12 through the ears and the drop plate, washer + nut on the plate's outer face
    m, DF = ce.MG996, ce.DF
    tc = -m["SHAFT_OFF"] + m["L"] / 2
    face = 143.2 + DF
    for i, (t, dz) in enumerate(((tc - 24.75, -5), (tc - 24.75, 5), (tc + 24.75, -5), (tc + 24.75, 5))):
        z = zc + dz
        k.cut(host, hf.cyl_r(135 + DF, 141 + DF, CLR[3], t, z))
        k.cut("spin MG996R " + u, hf.cyl_r(face - 11, face - 7, CLR[3], t, z))
        k.screw("spin servo %s M3x12 %d" % (u, i + 1), g, 3, 12, (face - 10.3, t, z), (1, 0, 0))
        k.washer("spin servo %s washer %d" % (u, i + 1), g, 3, (140 + DF, t, z), (1, 0, 0))
        k.nut("spin servo %s nut %d" % (u, i + 1), g, 3, (140.5 + DF, t, z), (1, 0, 0))
    k.finish()


# ---------------------------------------------------------------- fixed drives (turn servo, holder posts, MG90S)
def fixed_hw(P, hf, u):
    ce = hf.ce
    z0, z1 = ce.FLOOR_Z
    g = "fixed" + u
    # turn MG996R (world frame)
    kw = Kit(P, lambda s: s)
    T, m = ce.TURN[u], ce.MG996
    (x0, y0), sx = T["shaft"], T["sx"]
    zs = z1 + T["block"]
    zE = zs + 26.5                                            # ear bottom
    xa, xb = sorted((x0 - sx * m["SHAFT_OFF"], x0 + sx * (m["L"] - m["SHAFT_OFF"])))
    xc = (xa + xb) / 2
    for side, (p0, p1), hx, low in (("A", (xa - 10, xa), xc - 24.75, True), ("B", (xb, xb + 10), xc + 24.75, False)):
        post = "turn servo post %s %s" % (u, side)
        for j, hy in enumerate((y0 - 5, y0 + 5)):
            kw.cut(post, hf.cyl_z(hx, hy, zE - 6.5, zE + 0.1, CLR[3]))
            kw.cut("turn MG996R " + u, hf.cyl_z(hx, hy, zE - 0.1, zE + 2.6, CLR[3]))
            x_lo, x_hi = (p0 - 1, hx + 3.45) if low else (hx - 3.45, p1 + 1)     # pocket open away from the body
            kw.cut(post, box((x_lo, hy - 3.0, zE - 4.4), (x_hi, hy + 3.0, zE - 1.6)))
            n = "turn servo %s ear %s%d" % (u, side, j + 1)
            kw.screw(n + " M3x8", g, 3, 8, (hx, hy, zE + 2.5), (0, 0, -1))
            kw.nut(n + " nut", g, 3, (hx, hy, zE - 1.8), (0, 0, -1))
        pc = (p0 + p1) / 2                                    # post to the floor: M3 from under the floor + insert
        kw.cut(post, hf.cyl_z(pc, y0, z1 - 0.1, z1 + 7, INS_R[3]))
        kw.cut("base plate", hf.cyl_z(pc, y0, z0 - 1, z1 + 1, CLR[3]))
        kw.insert("turn servo post %s %s insert" % (u, side), g, 3, (pc, y0, z1), (0, 0, 1))
        kw.screw("turn servo post %s %s M3x12" % (u, side), g, 3, 12, (pc, y0, z0), (0, 0, 1), joins=("base plate",))
    # horn on the pinion hub: the 2 self-tapping M2 screws of the servo kit, from under the horn
    top = zs + m["H"]
    for j, dy in enumerate((-7, 7)):
        kw.add("turn horn %s M2x8 %d" % (u, j + 1), g, put(shcs_shape(2, 8), (x0, y0 + dy, top + 2), (0, 0, 1)),
               "blackox", "M2x8 screw (servo kit, self-tapping)")
    # pinion: M3 down through the printed hub into the servo spline
    g1 = T["gear_z"][1]
    L = min(n for n in (16, 20, 25, 30, 35, 40, 45) if (top + 4) - (g1 + 0.5 - n) >= 4)   # 4..8 mm into the spline
    kw.washer("turn pinion %s washer" % u, g, 3, (x0, y0, g1), (0, 0, 1))
    kw.screw("turn pinion %s M3x%d" % (u, L), g, 3, L, (x0, y0, g1 + 0.5), (0, 0, -1))
    kw.finish()

    # holder posts + MG90S cradle (unit frame, phi0)
    phi = ce.UNITS[u]["phi0"]
    k = Kit(P, lambda s: hf.to_unit(s, phi))
    tp = sum(ce.HOLD_POST_T) / 2
    for t in (-1, 1):
        post = "holder post %s%+d" % (u, t)
        for r in (113.0, 123.0):
            k.cut(post, hf.cyl_z(r, t * tp, z1 - 0.1, z1 + 7, INS_R[3]))
            k.cut("base plate", hf.cyl_z(r, t * tp, z0 - 1, z1 + 1, CLR[3]))
            n = "holder post %s%+d r%d" % (u, t, r)
            k.insert(n + " insert", g, 3, (r, t * tp, z1), (0, 0, 1))
            k.screw(n + " M3x12", g, 3, 12, (r, t * tp, z0), (0, 0, 1), joins=("base plate",))
    cradle = "holder MG90S cradle " + u
    T0 = ce.MG90S_T
    for r in (106.5, 114.5):
        k.cut(cradle, hf.cyl_z(r, T0 + 28, z1 - 0.1, z1 + 7, INS_R[3]))
        k.cut("base plate", hf.cyl_z(r, T0 + 28, z0 - 1, z1 + 1, CLR[3]))
        k.insert("MG90S cradle %s r%d insert" % (u, r), g, 3, (r, T0 + 28, z1), (0, 0, 1))
        k.screw("MG90S cradle %s r%d M3x12" % (u, r), g, 3, 12, (r, T0 + 28, z0), (0, 0, 1), joins=("base plate",))
    zE = z1 + 16                                              # MG90S ears: M2x8 + M2 nut under a 1.6 roof
    for j, t in enumerate((T0 + 11.4 - 13.75, T0 + 11.4 + 13.75)):
        k.cut(cradle, hf.cyl_z(111.1, t, zE - 6, zE + 0.1, CLR[2]))
        k.cut(cradle, box((100, t - 2.25, zE - 3.4), (111.1 + 2.6, t + 2.25, zE - 1.6)))
        k.cut("holder MG90S " + u, hf.cyl_z(111.1, t, zE - 0.1, zE + 2.6, CLR[2]))
        k.screw("MG90S %s ear M2x8 %d" % (u, j + 1), g, 2, 8, (111.1, t, zE + 2.5), (0, 0, -1))
        k.nut("MG90S %s ear nut %d" % (u, j + 1), g, 2, (111.1, t, zE - 1.8), (0, 0, -1))
    k.finish()


# ---------------------------------------------------------------- holder cups (VW7-M5 thread + M5 nut in the column)
def holder_hw(P, hf, u, L):
    ce = hf.ce
    phi = ce.UNITS[u]["phi0"]
    k = Kit(P, lambda s: hf.to_unit(s, phi))
    host = "holder frame " + u
    D = ce.DF
    for t in (-ce.HOLD_X, ce.HOLD_X):
        sg = 1 if t > 0 else -1
        for lv in ("B", "M"):
            z = ce.Z_ST[lv] + L
            k.cut(host, hf.cyl_r(146 + D, 150.5 + D, 7.5, t, z))                      # VW7 hex in a counterbore
            k.cut(host, hf.cyl_r(140 + D, 146.1 + D, CLR[5], t, z))
            lo, hi = sorted((t - sg * 4.7, t + sg * 11))                        # M5 nut pocket, open to the side face
            k.cut(host, box((141.3 + D, lo, z - 4.2), (145.7 + D, hi, z + 4.2)))
            n = "holder cup %s%s%+d" % (u, lv, t)
            k.add(n + " VW7 thread", "hold" + u + "cup", hf.cyl_r(141 + D, 146 + D, 2.5, t, z), "brass", fastener=False)
            k.nut(n + " M5 nut", "hold" + u, 5, (141.5 + D, t, z), (1, 0, 0))
    k.finish()


def apply(P, st, hf):
    """add the hardware of pose st to P (in place)"""
    BOM.clear()
    column_hw(P, hf)
    for u in "FR":
        turret_hw(P, hf, u, st["th"][u])
        carriage_hw(P, hf, u, st["th"][u], st["zc"][u])
        fixed_hw(P, hf, u)
        holder_hw(P, hf, u, st["L"][u])
    return P
