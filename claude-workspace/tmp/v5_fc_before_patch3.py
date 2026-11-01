# v5_fc.py - CLAPETS MODULE v5: two modules with a clean interface (decision D-017).
#   MODULE A "clapets" (lift + 2 doors) is designed AROUND reserved space for MODULE B "tete" (suction head):
#     - lift (Two Trees Bluer V2 Y axis on end) moved 25 mm back: 58 mm of fixed depth for the head behind its rotating part
#     - door rods moved back (y 82): every door-unit part stays behind the head's rotating disc
#     - reserved: head fixed zone, head rest envelope (cups vertical), head turning disc R 140 (needs R 126)
#   MODULE B bolts on the plate front (1x M3 + the 4 wheel bolts): Ø8 shaft in 2x 608 35 mm apart, MG996R in the fixed
#     zone driving it with a 20T -> 30T gear pair (no belt), MDF carrier with 3 TPU cup stations (one cup per box),
#     tube holes + clip slots + a reserved passage for the tube slack loop (tubes not modelled).
# Run (headless): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" v5_fc.py   (~1 min)
# Output ../CAD_FC/: STEP/ (parts, MODULE_CLAPETS_V5.step, MODULE_A_CLAPETS.step, MODULE_B_TETE.step), STL/, DXF/,
#   MODULE_CLAPETS_V5.FCStd, report.txt (rest-pose collisions, both modules vs the reserved head space)
# Frame (mm): x right, y towards the stack, z up; z 0 = table. Base 300 x 300: x ±150, y -160..140 (y 140 = stack face).
import math
import os

import FreeCAD as App
import Import
import MeshPart
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))


# =============================================================================================== parameters
class G:
    YF = BOX_Y0 = 140                                       # base front face = stack face (cups touch it)
    BASE_X, BASE_Y0 = 150, -160
    # ---- Two Trees Bluer V2 lift, 25 mm further back than v4 ----
    LIFT_DY = -25
    RAIL_W, RAIL_DX, RAIL_YC, RAIL_Z0, RAIL_L = 20, 40.45, 58.5 + LIFT_DY, 6, 350
    PL_GAP, PL_T = 3.3, 3.5
    PL_Y0 = RAIL_YC + RAIL_W / 2 + PL_GAP                   # butterfly plate rear 46.8, front 50.3
    PL_Y1 = PL_Y0 + PL_T
    PL_ZC = 150
    WH_X, WH_DZ = 60.0, 37.5
    WH_R, WH_W = WH_X - RAIL_DX - RAIL_W / 2, 10.2
    SPRING_U = SPRING_V = 85                                # corner holes (M4) -> door units
    CLAMP_V = 10                                            # centre holes (M3) -> nut support; the lower one also holds module B
    MOT_Z1, SHELF_T = 46, 6
    CPL_Z0, CPL_Z1, SCREW_Z0, SCREW_Z1 = 58, 83, 71, 363
    NUT_Z = 110
    TOP_Z0, TOP_Z1 = 344, 364
    LIFT_CARRY, LIFT_TURN = 15, 72
    BRG_R, BRG_T, BOSS_R = 11.05, 7.1, 14.5
    # ---- reserved space for module B (in the carriage frame) ----
    HZ = 175                                                # head axis along y at x 0, z 175
    RES_ROT_R, RES_ROT_Y0 = 140, 108.0                      # turning disc: R 140 (needs 126), from the carrier rear to the face
    RES_FIX = (-62, 62, PL_Y1, RES_ROT_Y0, 100, 200)       # fixed zone: bracket, bearings, drive (x0, x1, y0, y1, z0, z1)
    RES_CABLE = (-62, 62, PL_Y1, RES_ROT_Y0, 200, 230)     # tube passage above the bracket (slack loop for 90 deg + lift)
    RES_REST_X = 36                                         # rest envelope: cups vertical, x ±36 (doors fold in front of it)
    # ---- MODULE A: door units ----
    PX, PY = 131, 82                                        # door rod (right): behind the head's turning disc; 28T tips stay at x <= 150
    LOW, UP, PT = 30, 226, 6
    W_X0, W_X1 = 66, 93                                     # back wall x (M4 at x 85); clear of the door servo flange
    ROD_Z0, ROD_Z1 = 30, 233
    GM, GZ1, GZ2 = 1.25, 20, 28                             # 20T pinion (MG996R) -> 28T on the rod: x1.4 (longer arms)
    GC = GM * (GZ1 + GZ2) / 2                               # 30
    SVY = PY - GC                                           # door servo axis (132, 52)
    SV_L, SV_W, SV_H, SV_FL, SV_OUT, SV_HORN = 40.7, 19.7, 37.0, 26.6, 10.0, 43.5   # MG996R, CHECK
    SV_X1 = PX + SV_OUT
    SV_X0 = SV_X1 - SV_L
    SV_XC = (SV_X0 + SV_X1) / 2
    SV_BOT = LOW + PT + 13                                  # door servo stands on the bottom plate; flange above the plate lobe
    SV_FLZ = SV_BOT + SV_FL
    GZA = SV_BOT + SV_HORN
    GZB = GZA + 8                                           # door gears z 92.5..100.5 (28T reaches y 100.75 < 108)
    HORN_R, HORN_T = 10.5, 2.0
    SV_SLOT = 2
    PAD_X0, PAD_T = 160, 8
    SX0 = PAD_X0 + PAD_T
    SX1 = SX0 + 3
    SY0, SY1, TAB_Y0 = 141, 176, 128
    PAD_Y0, PAD_Y1 = 145, 175
    DZ0, DZ1 = 20, 265
    PADS_Z = ((35, 75), (145, 185), (225, 265))
    ARM1, ARM2 = (39, 49), (212, 222)
    FL1, FL2 = (37, 53), (206, 224)
    A_FOLD, A_CLAMP, A_OPEN = 90.0, 3.0, -35.0             # open -35: the whole door is behind the face (stack turns clear)
    NUT_W, NUT_L, NUT_T = 5.6, 6.4, 2.6
    # ---- MODULE B: suction head ----
    CUPS_Z = (77, 135, 240)                                 # one cup per box
    ST_R_RIM, ST_R_RING, ST_R_HOLE, ST_R_HUB = 25, 28, 20, 8
    ST_BOLT_R, ST_BOLT_A = 24, (30, 150, 270)
    HB_Y0, HB_Y1 = PL_Y1, 92.0                              # bearing tube; 608 at both ends (35 mm apart)
    HG_Y0, HG_Y1 = 94.5, 102.5                              # gear plane (head 30T on the shaft, 20T on the servo horn)
    HF_Y0, HF_Y1 = HG_Y1, 108.5                             # flange (same part as the 30T gear), split clamp on the shaft
    CA_Y0, CA_Y1 = HF_Y1, HF_Y1 + 6                         # MDF 6 carrier 108.5..114.5
    RIM_Y1, RING_Y1 = CA_Y1 + 3, CA_Y1 + 6
    TH_Y0, TH_Y1 = CA_Y1 - 3.3, 122.0
    CUP_Y0 = TH_Y1                                          # DP-S30 bellows Ø30, 18 mm -> face at y 140
    CA_Z0, CA_Z1 = CUPS_Z[0] - ST_R_RING, CUPS_Z[2] + ST_R_RING
    HGZ1, HGZ2 = 20, 30                                     # head gear pair x1.5: head 90 deg = servo 135 deg
    HGC = GM * (HGZ1 + HGZ2) / 2                            # 31.25
    HS_ANG = 45                                             # head servo axis 45 deg down-left of the head axis
    HS_X = -HGC * math.sin(math.radians(HS_ANG))            # (-22.1, 152.9): clear of the boss, the M3 heads and the ears
    HS_Z = HZ - HGC * math.cos(math.radians(HS_ANG))
    HS_HORN_Y = HG_Y0                                       # horn top (towards +y) = gear plane rear
    HS_BODY_Y0 = HS_HORN_Y - SV_HORN                        # body bottom 51.0 (0.7 mm off the plate)


# =============================================================================================== geometry
def box(s, x0, x1, y0, y1, z0, z1):
    a, b = s * x0, s * x1
    return Part.makeBox(abs(b - a), y1 - y0, z1 - z0, Vector(min(a, b), y0, z0))


def vcyl(s, x, y, z0, z1, r):
    return Part.makeCylinder(r, z1 - z0, Vector(s * x, y, z0), Vector(0, 0, 1))


def xcyl(s, x0, x1, y, z, r):
    a, b = s * x0, s * x1
    return Part.makeCylinder(r, abs(b - a), Vector(min(a, b), y, z), Vector(1, 0, 0))


def ycyl(s, x, y0, y1, z, r):
    return Part.makeCylinder(r, y1 - y0, Vector(s * x, y0, z), Vector(0, 1, 0))


def prism(s, loop, z0, z1):
    pts = [Vector(s * p[0], p[1], z0) for p in loop]
    if s < 0:
        pts.reverse()
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, 0, z1 - z0))


def prism_y(loop_xz, y0, y1):           # polygon in the xz plane, extruded along +y
    pts = [Vector(p[0], y0, p[1]) for p in loop_xz]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, y1 - y0, 0))


def circle(cx, cy, r, n):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def hull(pts):
    p = sorted(set(pts))
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


def gear(cx, cy, m, z, phase_deg, bl):
    a20 = math.radians(20)
    r = m * z / 2
    rb, ra, rf = r * math.cos(a20), r + m, r - 1.25 * m
    inv = lambda x: math.tan(x) - x
    psi = (math.pi * m / 2 - bl / 2) / (2 * r)
    beta = lambda rho: psi + inv(a20) - inv(math.acos(min(1, rb / rho)))
    r0 = max(rb, rf)
    rad = [r0 + (ra - r0) * i / 7 for i in range(8)]
    pts = []
    add = lambda rho, ang: pts.append((cx + rho * math.cos(ang), cy + rho * math.sin(ang)))
    for k in range(z):
        c = math.radians(phase_deg) + 2 * math.pi * k / z
        b0 = beta(r0)
        if rf < rb:
            add(rf, c - b0)
        for rho in rad:
            add(rho, c - beta(rho))
        add(ra, c)
        for rho in reversed(rad):
            add(rho, c + beta(rho))
        if rf < rb:
            add(rf, c + b0)
        add(rf, c + math.pi / z)
    return pts


def gt2(cx, cz, teeth):
    """GT2 pulley outline in the xz plane (pitch 2 mm): OD = pitch dia - 0.508, round grooves r 0.555 every tooth."""
    od = teeth * G.GT2_P / math.pi - 0.508
    pts = []
    for k in range(teeth):
        a0 = 2 * math.pi * k / teeth
        for i in range(6):                                  # land
            a = a0 + (2 * math.pi / teeth) * (0.45 * i / 5)
            pts.append((cx + od / 2 * math.cos(a), cz + od / 2 * math.sin(a)))
        for i in range(1, 6):                               # groove
            t = i / 6
            a = a0 + (2 * math.pi / teeth) * (0.45 + 0.55 * t)
            r = od / 2 - 0.75 * math.sin(math.pi * t)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def nut(s, axis, x, y, z, open_, ext):
    lo, hi, half = [x, y, z], [x, y, z], [0.0, 0.0, 0.0]
    half[axis] = G.NUT_T / 2
    a1, a2 = (axis + 1) % 3, (axis + 2) % 3
    half[a1], half[a2] = G.NUT_W / 2, G.NUT_L / 2
    if open_ == a1:
        half[a1], half[a2] = G.NUT_L / 2, G.NUT_W / 2
    for i in range(3):
        lo[i] -= half[i]
        hi[i] += half[i]
    if ext > 0:
        hi[open_] += ext
    elif ext < 0:
        lo[open_] += ext
    return box(s, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def solid(adds, cuts=()):
    sh = adds[0]
    if len(adds) > 1:
        sh = sh.fuse(adds[1:])
    if cuts:
        sh = sh.cut(list(cuts))
    clean = sh.removeSplitter()
    clean.fix(1e-7, 1e-7, 1e-7)
    if clean.isValid() and abs(clean.Volume - sh.Volume) < 1e-3 * sh.Volume:
        return clean
    sh = sh.copy()
    sh.fix(1e-7, 1e-7, 1e-7)
    return sh


def split_clamp_z(s, x, y, z0, z1, screws_z, lug_dir=-1):
    """Split clamp on a vertical Ø8 rod: lug towards lug_dir*y, slot through the bore, M3 screws along x."""
    y_a, y_b = (y - 4, y - 14) if lug_dir < 0 else (y + 4, y + 14)
    a = [box(s, x - 6, x + 6, min(y_a, y_b), max(y_a, y_b), z0, z1)]
    c = [box(s, x - 0.6, x + 0.6, min(y, y_b) - 1, max(y, y_b) + 1, z0 - 1, z1 + 1)]
    ym = (y_a + y_b) / 2
    for z in screws_z:
        c += [xcyl(s, x - 7, x + 7, ym, z, 1.7), nut(s, 0, x + 6 - G.NUT_T / 2 + 0.1, ym, z, 0, 0), xcyl(s, x - 7, x - 4, ym, z, 3.0)]
    return a, c




G.HS_ANG = 25                                       # (set after the clearance check: body clear of the boss + M3 heads)
G.HS_X = -G.HGC * math.sin(math.radians(G.HS_ANG))  # (-13.2, 146.7)
G.HS_Z = G.HZ - G.HGC * math.cos(math.radians(G.HS_ANG))
G.HS_SVX1 = G.HS_X + G.SV_OUT                      # head servo body x -43.9..-3.2 (output 10 mm from its +x end)
G.HS_SVX0 = G.HS_SVX1 - G.SV_L
G.HS_SVXC = (G.HS_SVX0 + G.HS_SVX1) / 2
G.HS_FL_Y = G.HS_BODY_Y0 + G.SV_FL                  # flange rear face 77.6 (posts end here)


# =============================================================================================== parts
PETG, PETG2, TPU, MDF, ALU, STEEL, DARK = (0.95, 0.45, 0.10), (0.20, 0.45, 0.85), (0.15, 0.75, 0.30), (0.72, 0.58, 0.40), \
    (0.78, 0.80, 0.83), (0.62, 0.63, 0.66), (0.13, 0.13, 0.15)
FOAM, BRASS, BOXC, SERVO, RUBBER, GHOST = (0.25, 0.65, 0.35), (0.80, 0.62, 0.25), (0.85, 0.72, 0.48), (0.10, 0.10, 0.12), \
    (0.30, 0.30, 0.32), (0.55, 0.30, 0.85)
PARTS = {}      # name -> (shape, density, colour, kind, module)  kind: print / tpu / mdf / ref / reserve; module: A / B / -


def part(name, shape, rho, rgb, kind, module):
    PARTS[name] = (shape, rho, rgb, kind, module)


RY0, RY1 = G.RAIL_YC - G.RAIL_W / 2, G.RAIL_YC + G.RAIL_W / 2
YC = G.RAIL_YC


# ---------------------------------------------------------------- MODULE A: lift
def socle():
    a = [box(1, -62, 62, YC - 24.5, YC + 27.5, 0, G.RAIL_Z0), box(1, -26.5, 26.5, YC - 22.5, YC + 22.5, G.MOT_Z1, G.MOT_Z1 + G.SHELF_T)]
    c = []
    for s in (1, -1):
        a.append(box(s, G.RAIL_DX - 14, G.RAIL_DX + 14, RY0 - 4, RY1 + 4, G.RAIL_Z0, G.MOT_Z1 + G.SHELF_T))
        c += [box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, RY0 - 0.2, RY1 + 0.2, G.RAIL_Z0, 100),
              ycyl(s, G.RAIL_DX, RY0 - 5, RY0 + 1, 30, 2.75)] + [vcyl(s, 55, y, -1, G.RAIL_Z0 + 1, 2.2) for y in (YC - 18.5, YC + 21.5)]
    c.append(vcyl(1, 0, YC, G.MOT_Z1 - 1, G.MOT_Z1 + G.SHELF_T + 1, 11.5))
    c += [vcyl(1, dx, YC + dy, G.MOT_Z1 - 1, G.MOT_Z1 + G.SHELF_T + 1, 1.7) for dx in (-15.5, 15.5) for dy in (-15.5, 15.5)]
    part("A_SOCLE", solid(a, c), 1270, PETG, "print", "A")


def haut():
    top = G.RAIL_Z0 + G.RAIL_L
    a = [box(1, -G.RAIL_DX - 14, G.RAIL_DX + 14, RY0 - 4, RY1 + 4, G.TOP_Z0, G.TOP_Z1)]
    c = [vcyl(1, 0, YC, G.TOP_Z0 - 1, top + G.BRG_T, G.BRG_R)]
    for s in (1, -1):
        c += [box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, RY0 - 0.2, RY1 + 0.2, G.TOP_Z0 - 1, top), ycyl(s, G.RAIL_DX, RY0 - 5, RY0 + 1, G.TOP_Z0 + 6, 2.75)]
    part("A_TRAVERSE_HAUT", solid(a, c), 1270, PETG, "print", "A")


def support_ecrou():    # behind the plate, between the rails; 2x M3 through the plate's centre holes (heads sit in pockets of B)
    top = G.PL_ZC + G.CLAMP_V + 10
    a = [box(1, -25, 25, G.PL_Y0 - 5, G.PL_Y0, G.NUT_Z - 10, top), box(1, -25, 25, YC - 20.5, G.PL_Y0 - 5, G.NUT_Z, G.NUT_Z + 6)]
    a += [box(s, 19, 25, YC - 18.5, G.PL_Y0 - 5, G.NUT_Z + 6, top) for s in (1, -1)]
    c = [vcyl(1, 0, YC, G.NUT_Z - 1, G.NUT_Z + 7, 5.6)]
    c += [vcyl(1, qx, YC + qy, G.NUT_Z - 1, G.NUT_Z + 7, 2.0) for qx, qy in ((8, 0), (-8, 0), (0, 8), (0, -8))]
    for bz in (G.PL_ZC - G.CLAMP_V, G.PL_ZC + G.CLAMP_V):
        c += [ycyl(1, 0, G.PL_Y0 - 6, G.PL_Y0 + 1, bz, 1.7), nut(1, 1, 0, G.PL_Y0 - 5 + G.NUT_T / 2 - 0.1, bz, 1, -3)]
    c.append(box(1, -12, 12, G.PL_Y0 - 5.5, G.PL_Y0 + 0.1, G.NUT_Z + 5.5, G.NUT_Z + 10.5))
    part("A_SUPPORT_ECROU", solid(a, c), 1270, PETG, "print", "A")


# ---------------------------------------------------------------- MODULE A: door units
def unit_plate_loop():
    return hull([(G.W_X0, G.PL_Y1), (G.W_X1, G.PL_Y1), (G.W_X0, G.PL_Y1 + 10)] + circle(G.PX, G.PY, G.BOSS_R, 40))


def aile(s, name):
    a, c = [], []
    a.append(prism(s, unit_plate_loop(), G.LOW, G.LOW + G.PT))
    a.append(prism(s, unit_plate_loop(), G.UP, G.UP + G.PT))
    a.append(box(s, 99, 150, G.SVY - 11, G.SVY + 11, G.LOW, G.LOW + G.PT))                            # servo area (bottom plate)
    a.append(vcyl(s, G.PX, G.PY, G.LOW - 3, G.LOW + G.PT, G.BOSS_R))
    a.append(vcyl(s, G.PX, G.PY, G.UP, G.UP + G.PT + 3, G.BOSS_R))
    a.append(box(s, G.W_X0, G.W_X1, G.PL_Y1, G.PL_Y1 + 6, G.LOW, G.PL_ZC + G.SPRING_V + 9))           # back wall on the plate
    a.append(box(s, G.W_X0, G.W_X0 + 6, G.PL_Y1, G.PL_Y1 + 22, G.LOW, G.UP + G.PT))                    # inner side wall
    a.append(box(s, 104, 113, 66, 72, G.LOW + G.PT, G.UP))                                            # rib: closes the C-frame
    for z0 in (110, 200):
        a.append(box(s, G.W_X1 - 1, 106, G.PL_Y1, 72, z0, z0 + 10))                                    # gussets
    c.append(vcyl(s, G.PX, G.PY, G.LOW + G.PT + 0.1 - G.BRG_T - 0.1, G.LOW + G.PT + 0.1, G.BRG_R))
    c.append(vcyl(s, G.PX, G.PY, G.UP - 0.1, G.UP + G.BRG_T, G.BRG_R))
    c.append(vcyl(s, G.PX, G.PY, G.LOW - 4, G.UP + G.PT + 4, 5.0))
    for side, hy in ((-1, (5,)), (1, (-5, 5))):                                                      # MG996R posts up to the flange
        hx = G.SV_XC + side * 24.375
        y0 = G.SVY - 11 if side > 0 else G.PL_Y1
        a.append(box(s, hx - 3.8, hx + 3.8, y0, G.SVY + 11, G.LOW + G.PT, G.SV_FLZ))
        for dy in hy:
            yy0, yy1 = G.SVY + dy - G.SV_SLOT, G.SVY + dy + G.SV_SLOT
            c += [vcyl(s, hx, yy0, G.SV_FLZ - 13, G.SV_FLZ + 1, 1.7), vcyl(s, hx, yy1, G.SV_FLZ - 13, G.SV_FLZ + 1, 1.7),
                  box(s, hx - 1.7, hx + 1.7, yy0, yy1, G.SV_FLZ - 13, G.SV_FLZ + 1)]
            nb = nut(s, 2, hx, G.SVY + dy, G.SV_FLZ - 8, 0, side * 10)
            c += [nb.translated(Vector(0, d, 0)) for d in (-G.SV_SLOT, 0, G.SV_SLOT)]
    for bz in (G.PL_ZC - G.SPRING_V, G.PL_ZC + G.SPRING_V):
        c.append(ycyl(s, G.SPRING_U, G.PL_Y1 - 1, G.PL_Y1 + 7, bz, 2.25))
        c.append(box(s, G.SPRING_U - 4.1, G.SPRING_U + 4.1, G.PL_Y1 + 2.4, G.PL_Y1 + 9, bz - 3.6, bz + 3.6))
    part(name, solid(a, c), 1270, PETG2, "print", "A")


def bras(s, name, arm, fl):
    hub = circle(G.PX, G.PY, 11, 48)
    fy1 = G.BOX_Y0 - 3.5                                                                             # +3 deg clamp swings it ~1.2 mm forward
    flp = [(G.SX0 - 12, G.TAB_Y0), (G.SX0, G.TAB_Y0), (G.SX0, fy1), (G.SX0 - 12, fy1)]
    z0, z1 = arm
    a = [prism(s, hull(hub + flp), z0, z1), box(s, G.SX0 - 12, G.SX0, G.TAB_Y0, fy1, fl[0], fl[1])]
    ca, cc = split_clamp_z(s, G.PX, G.PY, z0, z1, [(z0 + z1) / 2])
    a += ca
    c = cc + [vcyl(s, G.PX, G.PY, z0 - 1, z1 + 1, 4.05)]
    for z in (fl[0] + 3.5, fl[1] - 3.5):
        c += [xcyl(s, G.SX0 - 13, G.SX0 + 0.1, (G.TAB_Y0 + fy1) / 2, z, 1.7),
              nut(s, 0, G.SX0 - 12 + G.NUT_T / 2 - 0.1, (G.TAB_Y0 + fy1) / 2, z, 0, 0)]
    part(name, solid(a, c), 1270, PETG, "print", "A")


def roue_porte():
    hz1 = G.GZB + 14
    a = [prism(1, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.PY, G.GZB, hz1, 10)]
    ca, cc = split_clamp_z(1, G.PX, G.PY, G.GZB, hz1, [G.GZB + 4, hz1 - 4], lug_dir=1)
    a += ca
    part("A_ROUE_PORTE_28T", solid(a, cc + [vcyl(1, G.PX, G.PY, G.GZA - 1, hz1 + 1, 4.05)]), 1270, PETG2, "print", "A")


def pignon_porte():
    a = [prism(1, gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R + 3)]
    c = [vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T - 1, G.GZA, G.HORN_R + 0.2), vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2)]
    c += [vcyl(1, G.PX + 7.5 * math.cos(math.pi / 2 * k), G.SVY + 7.5 * math.sin(math.pi / 2 * k), G.GZA - 1, G.GZB + 1, 0.8) for k in range(4)]
    part("A_PIGNON_PORTE_20T", solid(a, c), 1270, PETG2, "print", "A")


def tole():
    a, c = [box(1, G.SX0, G.SX1, G.SY0, G.SY1, G.DZ0, G.DZ1)], []
    for f0, f1 in (G.FL1, G.FL2):
        a.append(box(1, G.SX0, G.SX1, G.TAB_Y0, G.SY0, f0, f1))
        c += [xcyl(1, G.SX0 - 1, G.SX1 + 1, (G.TAB_Y0 + G.BOX_Y0 - 3.5) / 2, z, 1.7) for z in (f0 + 3.5, f1 - 3.5)]
    part("A_TOLE_PORTE", solid(a, c), 750, MDF, "mdf", "A")


# ---------------------------------------------------------------- MODULE B: suction head
def tete_support():     # bracket: 4x M5 (the wheel bolts, longer) on the plate; bearing tube (608 at both ends); servo posts
    hz = G.HZ
    a = [box(1, -52, 52, G.PL_Y1, G.PL_Y1 + 6, 100, 200)]
    for sx in (1, -1):
        for dz in (-G.WH_DZ, G.WH_DZ):
            a.append(box(1, min(sx * 52, sx * 65.5), max(sx * 52, sx * 65.5), G.PL_Y1, G.PL_Y1 + 6, G.PL_ZC + dz - 8, G.PL_ZC + dz + 8))
    a.append(ycyl(1, 0, G.HB_Y0, G.HB_Y1, hz, 17))                                                   # bearing tube
    a.append(box(1, -6, 6, G.PL_Y1, G.HB_Y1, hz + 10, 200))                                          # web: tube <-> plate (top)
    for hx in (G.HS_SVXC - 24.375, G.HS_SVXC + 24.375):                                              # servo posts to the flange
        a.append(box(1, hx - 3.8, hx + 3.8, G.PL_Y1, G.HS_FL_Y, G.HS_Z - 11, G.HS_Z + 11))
    c = [ycyl(1, 0, G.HB_Y0 - 1, G.HB_Y0 + G.BRG_T, hz, G.BRG_R), ycyl(1, 0, G.HB_Y1 - G.BRG_T, G.HB_Y1 + 1, hz, G.BRG_R),
         ycyl(1, 0, G.HB_Y0 - 1, G.HB_Y1 + 1, hz, 5.0)]
    c.append(box(1, G.HS_SVX0 - 1.5, G.HS_SVX1 + 0.6, G.PL_Y1 - 1, G.PL_Y1 + 7, G.HS_Z - G.SV_W / 2 - 1, G.HS_Z + G.SV_W / 2 + 1))   # window: servo body
    for bz in (G.PL_ZC - G.CLAMP_V, G.PL_ZC + G.CLAMP_V):                                              # pockets: module A's M3 heads
        c.append(ycyl(1, 0, G.PL_Y1 - 1, G.PL_Y1 + 3.5, bz, 3.4))
    for sx in (1, -1):
        for dz in (-G.WH_DZ, G.WH_DZ):
            c.append(ycyl(1, sx * G.WH_X, G.PL_Y1 - 1, G.PL_Y1 + 7, G.PL_ZC + dz, 2.75))
    for hx in (G.HS_SVXC - 24.375, G.HS_SVXC + 24.375):                                              # M3 through the flange (±1.5 slot in x)
        out = -1 if hx < G.HS_SVXC else 1
        for dz in (-5, 5):
            c += [ycyl(1, hx + d, G.HS_FL_Y - 13, G.HS_FL_Y + 1, G.HS_Z + dz, 1.7) for d in (-1.5, 0, 1.5)]
            c.append(box(1, min(hx - 3.3, hx + out * 12), max(hx + 3.3, hx + out * 12), G.HS_FL_Y - 9, G.HS_FL_Y - 6.4, G.HS_Z + dz - 2.8, G.HS_Z + dz + 2.8))
    part("B_SUPPORT_TETE", solid(a, c), 1270, PETG, "print", "B")


def tete_moyeu():       # 30T gear + flange in one part; split clamp in the flange; 3x M3 to the carrier
    hz = G.HZ
    ang_to_servo = math.degrees(math.atan2(G.HS_Z - hz, G.HS_X))
    a = [prism_y(gear(0, hz, G.GM, G.HGZ2, ang_to_servo + 180.0 / G.HGZ2, 0.15), G.HG_Y0, G.HG_Y1),
         ycyl(1, 0, G.HF_Y0, G.HF_Y1, hz, 22)]
    c = [ycyl(1, 0, G.HG_Y0 - 1, G.HF_Y1 + 1, hz, 4.05),
         box(1, -0.6, 0.6, G.HF_Y0 - 1, G.HF_Y1 + 1, hz, hz + 23)]                                    # slot up through the flange
    c += [xcyl(1, -9, 9, G.HF_Y0 + 3, hz + 13, 1.7), xcyl(1, -9, -5, G.HF_Y0 + 3, hz + 13, 3.0),
          box(1, 5.4, 5.4 + G.NUT_T, G.HF_Y0 + 3 - 3.2, G.HF_Y1 + 1, hz + 13 - 2.8, hz + 13 + 2.8)]
    for k in range(3):
        ang = math.radians(210 + 120 * k)
        x, z = 15 * math.cos(ang), hz + 15 * math.sin(ang)
        c += [ycyl(1, x, G.HF_Y0 - 1, G.HF_Y1 + 1, z, 1.7), prism_y(circle(x, z, 3.25, 6), G.HF_Y0 - 1, G.HF_Y0 + 2.6)]
    part("B_MOYEU_TETE_30T", solid(a, c), 1270, PETG2, "print", "B")


def tete_pignon():      # 20T on the head MG996R horn (horn in a pocket at the rear)
    ang_to_head = math.degrees(math.atan2(G.HZ - G.HS_Z, -G.HS_X))
    a = [prism_y(gear(G.HS_X, G.HS_Z, G.GM, G.HGZ1, ang_to_head, 0.15), G.HG_Y0, G.HG_Y1),
         ycyl(1, G.HS_X, G.HG_Y0 - G.HORN_T, G.HG_Y0, G.HS_Z, G.HORN_R + 3)]
    c = [ycyl(1, G.HS_X, G.HG_Y0 - G.HORN_T - 1, G.HG_Y0, G.HS_Z, G.HORN_R + 0.2), ycyl(1, G.HS_X, G.HG_Y0 - 1, G.HG_Y1 + 1, G.HS_Z, 3.2)]
    c += [ycyl(1, G.HS_X + 7.5 * math.cos(math.pi / 2 * k), G.HG_Y0 - 1, G.HG_Y1 + 1, G.HS_Z + 7.5 * math.sin(math.pi / 2 * k), 0.8) for k in range(4)]
    part("B_PIGNON_TETE_20T", solid(a, c), 1270, PETG2, "print", "B")


def stadium(z0, z1, r):
    loop = []
    for k in range(25):
        a = math.pi * k / 24
        loop.append((r * math.cos(a), z1 - r + r * math.sin(a)))
    for k in range(25):
        a = math.pi + math.pi * k / 24
        loop.append((r * math.cos(a), z0 + r + r * math.sin(a)))
    return loop


def tete_plateau():     # MDF 6 carrier: 3 stations, hub bolts, tube holes + zip-tie slots along the tube route (to the top)
    hz = G.HZ
    a = [prism_y(stadium(G.CA_Z0, G.CA_Z1, G.ST_R_RING), G.CA_Y0, G.CA_Y1)]
    c = []
    for cz in G.CUPS_Z:
        c.append(ycyl(1, 0, G.CA_Y0 - 1, G.CA_Y1 + 1, cz, G.ST_R_HOLE))
        for ang in G.ST_BOLT_A:
            t = math.radians(ang)
            c.append(ycyl(1, G.ST_BOLT_R * math.cos(t), G.CA_Y0 - 1, G.CA_Y1 + 1, cz + G.ST_BOLT_R * math.sin(t), 1.7))
    for k in range(3):
        ang = math.radians(210 + 120 * k)
        c.append(ycyl(1, 15 * math.cos(ang), G.CA_Y0 - 1, G.CA_Y1 + 1, hz + 15 * math.sin(ang), 1.7))
    # tube route: up the carrier rear at x +17, zip-tie slot pairs every ~40 mm, exit over the top end
    for z in (100, 160, 205, 255):
        if any(abs(z - cz) < G.ST_R_RING for cz in G.CUPS_Z) or abs(z - hz) < 24:
            continue
        for dx in (-4, 4):
            c.append(box(1, 17 + dx - 0.8, 17 + dx + 0.8, G.CA_Y0 - 1, G.CA_Y1 + 1, z - 2.5, z + 2.5))
    part("B_PLATEAU_TETE", solid(a, c), 750, MDF, "mdf", "B")


def tete_station_tpu():   # TPU 95A spring disc (after Barbatronic): rim clamped, 3 spiral arms, hub with M5 + nut pocket
    rim = solid([ycyl(1, 0, G.CA_Y1, G.RIM_Y1, 0, G.ST_R_RIM)], [ycyl(1, 0, G.CA_Y1 - 1, G.RIM_Y1 + 1, 0, G.ST_R_HOLE)])
    disc = solid([ycyl(1, 0, G.CA_Y1, G.CA_Y1 + 2.5, 0, G.ST_R_HOLE + 0.5)], [ycyl(1, 0, G.CA_Y1 - 1, G.CA_Y1 + 4, 0, G.ST_R_HUB - 0.5)])
    slots = []
    for k in range(3):
        a0 = 2 * math.pi * k / 3
        inner, outer = [], []
        for i in range(25):
            t = i / 24
            r = G.ST_R_HUB + 0.6 + (G.ST_R_HOLE - 1.4 - G.ST_R_HUB) * t
            ang = a0 + math.radians(200) * t
            inner.append(((r - 1.2) * math.cos(ang), (r - 1.2) * math.sin(ang)))
            outer.append(((r + 1.2) * math.cos(ang), (r + 1.2) * math.sin(ang)))
        slots.append(prism_y(inner + list(reversed(outer)), G.CA_Y1 - 1, G.CA_Y1 + 4))
    disc = disc.cut(slots)
    hub = solid([ycyl(1, 0, G.TH_Y0, G.TH_Y1, 0, G.ST_R_HUB)],
                [ycyl(1, 0, G.TH_Y0 - 1, G.TH_Y1 + 1, 0, 2.6), prism_y(circle(0, 0, 4.6, 6), G.TH_Y0 - 1, G.TH_Y0 + 4)])
    st = solid([rim, disc, hub])
    for ang in G.ST_BOLT_A:
        t = math.radians(ang)
        st = st.cut(ycyl(1, G.ST_BOLT_R * math.cos(t), G.CA_Y1 - 1, G.RIM_Y1 + 1, G.ST_BOLT_R * math.sin(t), 1.7))
    part("B_STATION_TPU", st, 1200, TPU, "tpu", "B")


def tete_bague():       # clamp ring over the TPU rim; a notch lets the tube leave towards the route (x +17)
    a = [ycyl(1, 0, G.RIM_Y1, G.RING_Y1, 0, G.ST_R_RING)]
    c = [ycyl(1, 0, G.RIM_Y1 - 1, G.RING_Y1 + 1, 0, G.ST_R_HOLE)]
    for ang in G.ST_BOLT_A:
        t = math.radians(ang)
        c.append(ycyl(1, G.ST_BOLT_R * math.cos(t), G.RIM_Y1 - 1, G.RING_Y1 + 1, G.ST_BOLT_R * math.sin(t), 1.7))
    part("B_BAGUE_STATION", solid(a, c), 1270, PETG, "print", "B")


# ---------------------------------------------------------------- references + reserved space
def refs():
    part("REF_RAIL_2020", box(1, G.RAIL_DX - 10, G.RAIL_DX + 10, RY0, RY1, G.RAIL_Z0, G.RAIL_Z0 + G.RAIL_L), 2700, DARK, "ref", "A")
    y0, y1, cz = G.PL_Y0, G.PL_Y1, G.PL_ZC
    a, c = [box(1, -72, 72, y0, y1, cz - 52, cz + 52)], []
    for su in (1, -1):
        for sv in (1, -1):
            a += [box(1, min(su * 40, su * 85), max(su * 40, su * 85), y0, y1, min(cz + sv * 40, cz + sv * 85), max(cz + sv * 40, cz + sv * 85)),
                  ycyl(1, su * G.SPRING_U, y0, y1, cz + sv * G.SPRING_V, 12)]
            c += [ycyl(1, su * G.SPRING_U, y0 - 1, y1 + 1, cz + sv * G.SPRING_V, 2.25), ycyl(1, su * G.WH_X, y0 - 1, y1 + 1, cz + sv * G.WH_DZ, 2.6)]
    c += [ycyl(1, 0, y0 - 1, y1 + 1, cz + sv * G.CLAMP_V, 1.7) for sv in (1, -1)]
    part("REF_PLAQUE_PAPILLON", solid(a, c), 7850, DARK, "ref", "A")
    part("REF_ROUE_V", ycyl(1, G.WH_X, YC - G.WH_W / 2, YC + G.WH_W / 2, G.PL_ZC - G.WH_DZ, G.WH_R), 1400, DARK, "ref", "A")
    part("REF_608ZZ", solid([vcyl(1, G.PX, G.PY, G.LOW + G.PT - 7, G.LOW + G.PT, 11)], [vcyl(1, G.PX, G.PY, 0, 400, 4)]), 7850, STEEL, "ref", "A")
    part("REF_608ZZ_TETE", solid([ycyl(1, 0, G.HB_Y0, G.HB_Y0 + 7, G.HZ, 11)], [ycyl(1, 0, 0, 200, G.HZ, 4)]), 7850, STEEL, "ref", "B")
    part("REF_NEMA17", solid([box(1, -21.15, 21.15, YC - 21.15, YC + 21.15, G.MOT_Z1 - 40, G.MOT_Z1),
                              vcyl(1, 0, YC, G.MOT_Z1, G.MOT_Z1 + 2, 11), vcyl(1, 0, YC, G.MOT_Z1 + 2, G.MOT_Z1 + 24, 2.5)]), 3500, DARK, "ref", "A")
    part("REF_COUPLEUR_5x8", solid([vcyl(1, 0, YC, G.CPL_Z0, G.CPL_Z1, 9.5)],
                                   [vcyl(1, 0, YC, G.SCREW_Z0, G.CPL_Z1 + 1, 4), vcyl(1, 0, YC, G.CPL_Z0 - 1, G.MOT_Z1 + 24, 2.5)]), 2700, ALU, "ref", "A")
    part("REF_VIS_T8", vcyl(1, 0, YC, G.SCREW_Z0, G.SCREW_Z1, 4), 7850, STEEL, "ref", "A")
    part("REF_ECROU_T8", solid([vcyl(1, 0, YC, G.NUT_Z + 6, G.NUT_Z + 9.5, 11), vcyl(1, 0, YC, G.NUT_Z - 5.5, G.NUT_Z + 6, 5.1)],
                               [vcyl(1, 0, YC, 0, 400, 4)]), 8500, BRASS, "ref", "A")
    part("REF_TIGE_PORTE_D8", vcyl(1, G.PX, G.PY, G.ROD_Z0, G.ROD_Z1, 4), 7850, STEEL, "ref", "A")
    part("REF_AXE_TETE_D8", ycyl(1, 0, G.HB_Y0 + 0.5, G.HF_Y1, G.HZ, 4), 7850, STEEL, "ref", "B")
    part("REF_MOUSSE_PORTE", box(1, G.PAD_X0, G.SX0, G.PAD_Y0, G.PAD_Y1, G.PADS_Z[0][0], G.PADS_Z[0][1]), 50, FOAM, "ref", "A")
    for s, name in ((1, "REF_MG996R_D"), (-1, "REF_MG996R_G")):
        b = G.SV_BOT
        part(name, solid([box(s, G.SV_X0, G.SV_X1, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, b, b + G.SV_H),
                          box(s, G.SV_XC - 27.25, G.SV_XC + 27.25, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_FLZ, G.SV_FLZ + 2.4),
                          vcyl(s, G.PX, G.SVY, b + G.SV_H, G.GZA - G.HORN_T, 3), vcyl(s, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R)]), 1200, SERVO, "ref", "A")
    b0 = G.HS_BODY_Y0                                                                                  # head servo, axis along y
    part("REF_MG996R_TETE", solid([box(1, G.HS_SVX0, G.HS_SVX1, b0, b0 + G.SV_H, G.HS_Z - G.SV_W / 2, G.HS_Z + G.SV_W / 2),
                                   box(1, G.HS_SVXC - 27.25, G.HS_SVXC + 27.25, G.HS_FL_Y, G.HS_FL_Y + 2.4, G.HS_Z - G.SV_W / 2, G.HS_Z + G.SV_W / 2),
                                   ycyl(1, G.HS_X, b0 + G.SV_H, G.HG_Y0 - G.HORN_T, G.HS_Z, 3),
                                   ycyl(1, G.HS_X, G.HG_Y0 - G.HORN_T, G.HG_Y0, G.HS_Z, G.HORN_R)]), 1200, SERVO, "ref", "B")
    part("REF_VENTOUSE_DPS30", solid([ycyl(1, 0, G.CUP_Y0, G.YF, 0, 15), ycyl(1, 0, G.TH_Y0 + 1, G.CUP_Y0, 0, 2.5)]), 1100, RUBBER, "ref", "B")
    part("REF_PILE_3_PIERRES", Part.makeCompound([box(1, -160, 160, G.BOX_Y0, G.BOX_Y0 + 110, 110 * i + 0.5, 110 * (i + 1) - 0.5) for i in range(3)]),
         100, BOXC, "ref", "-")
    # reserved space for module B (shown transparent; module A must keep it free)
    part("RES_TETE_ROTATION", ycyl(1, 0, G.RES_ROT_Y0, G.YF, G.HZ, G.RES_ROT_R), 1, GHOST, "reserve", "-")
    x0, x1, y0_, y1_, z0, z1 = G.RES_FIX
    part("RES_TETE_FIXE", box(1, x0, x1, y0_, y1_, z0, z1), 1, GHOST, "reserve", "-")
    x0, x1, y0_, y1_, z0, z1 = G.RES_CABLE
    part("RES_TETE_CABLES", box(1, x0, x1, y0_, y1_, z0, z1), 1, GHOST, "reserve", "-")
    part("RES_TETE_REPOS", box(1, -G.RES_REST_X, G.RES_REST_X, G.RES_ROT_Y0, G.YF, G.CA_Z0, G.CA_Z1), 1, GHOST, "reserve", "-")


# =============================================================================================== assembly
def placements():
    L = -2 * G.PX
    p = [("A_SOCLE", 0, 0, 0, "fixed"), ("A_TRAVERSE_HAUT", 0, 0, 0, "fixed"), ("REF_NEMA17", 0, 0, 0, "fixed"),
         ("REF_COUPLEUR_5x8", 0, 0, 0, "fixed"), ("REF_VIS_T8", 0, 0, 0, "fixed"),
         ("REF_608ZZ", -G.PX, YC - G.PY, G.RAIL_Z0 + G.RAIL_L - (G.LOW + G.PT - 7), "fixed"),
         ("REF_RAIL_2020", 0, 0, 0, "fixed"), ("REF_RAIL_2020", -2 * G.RAIL_DX, 0, 0, "fixed"),
         ("REF_PLAQUE_PAPILLON", 0, 0, 0, "carriage"), ("A_SUPPORT_ECROU", 0, 0, 0, "carriage"), ("REF_ECROU_T8", 0, 0, 0, "carriage"),
         ("A_AILE_D", 0, 0, 0, "carriage"), ("A_AILE_G", 0, 0, 0, "carriage"), ("REF_MG996R_D", 0, 0, 0, "carriage"), ("REF_MG996R_G", 0, 0, 0, "carriage"),
         ("B_SUPPORT_TETE", 0, 0, 0, "carriage"), ("REF_608ZZ_TETE", 0, 0, 0, "carriage"),
         ("REF_608ZZ_TETE", 0, G.HB_Y1 - 7 - G.HB_Y0, 0, "carriage"),
         ("REF_MG996R_TETE", 0, 0, 0, "carriage"), ("B_PIGNON_TETE_20T", 0, 0, 0, "hpinion"),
         ("B_MOYEU_TETE_30T", 0, 0, 0, "head"), ("REF_AXE_TETE_D8", 0, 0, 0, "head"), ("B_PLATEAU_TETE", 0, 0, 0, "head"),
         ("REF_PILE_3_PIERRES", 0, 0, 0, "stack"),
         ("RES_TETE_ROTATION", 0, 0, 0, "reserve"), ("RES_TETE_FIXE", 0, 0, 0, "reserve"), ("RES_TETE_CABLES", 0, 0, 0, "reserve"),
         ("RES_TETE_REPOS", 0, 0, 0, "reserve")]
    p += [("REF_ROUE_V", dx, 0, dz, "carriage") for dx in (0, -2 * G.WH_X) for dz in (0, 2 * G.WH_DZ)]
    for cz in G.CUPS_Z:
        p += [("B_STATION_TPU", 0, 0, cz, "head"), ("B_BAGUE_STATION", 0, 0, cz, "head"), ("REF_VENTOUSE_DPS30", 0, 0, cz, "head")]
    for s, dx, tag in ((1, 0, "D"), (-1, L, "G")):
        door = "door_" + tag
        p += [("A_BRAS_PORTE_" + tag + "_BAS", 0, 0, 0, door), ("A_BRAS_PORTE_" + tag + "_HAUT", 0, 0, 0, door),
              ("REF_TIGE_PORTE_D8", dx, 0, 0, door), ("A_ROUE_PORTE_28T", dx, 0, 0, door),
              ("A_PIGNON_PORTE_20T", dx, 0, 0, "pinion_" + tag),
              ("REF_608ZZ", dx, 0, 0, "carriage"), ("REF_608ZZ", dx, 0, G.UP - (G.LOW + G.PT - 7), "carriage"),
              ("A_TOLE_PORTE", 0 if s > 0 else -(G.SX0 + G.SX1), 0, 0, door)]
        p += [("REF_MOUSSE_PORTE", 0 if s > 0 else -(G.PAD_X0 + G.SX0), 0, z0 - G.PADS_Z[0][0], door) for z0, _ in G.PADS_Z]
    return p


def build_all():
    socle(); haut(); support_ecrou(); aile(1, "A_AILE_D"); aile(-1, "A_AILE_G")
    for s, tag in ((1, "D"), (-1, "G")):
        bras(s, "A_BRAS_PORTE_%s_BAS" % tag, G.ARM1, G.FL1)
        bras(s, "A_BRAS_PORTE_%s_HAUT" % tag, G.ARM2, G.FL2)
    roue_porte(); pignon_porte(); tole()
    tete_support(); tete_moyeu(); tete_pignon(); tete_plateau(); tete_station_tpu(); tete_bague(); refs()


def main():
    for d in ("", "STEP", "STL", "DXF"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    build_all()
    rep, printed = [], []
    for name, (sh, rho, rgb, kind, mod) in PARTS.items():
        bb = sh.BoundBox
        big = max(bb.XLength, bb.YLength, bb.ZLength)
        flag = "" if kind not in ("print", "tpu") or big <= 250 else "  TOO BIG FOR THE X1C (256)"
        rep.append("%-24s %-7s %s solids %d  mass %7.1f g  size %6.1f x %6.1f x %6.1f  %s%s" % (
            name, kind, mod, len(sh.Solids), sh.Volume * 1e-6 * rho, bb.XLength, bb.YLength, bb.ZLength, "valid" if sh.isValid() else "INVALID", flag))
        if kind == "reserve":
            continue
        sh.exportStep(os.path.join(OUT, "STEP", name + ".step"))
        if kind in ("print", "tpu"):
            MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.01, AngularDeflection=0.0349, Relative=False).write(os.path.join(OUT, "STL", name + ".stl"))
            printed.append("%s  (module %s)%s" % (name, mod, "  TPU 95A" if kind == "tpu" else ""))
        if kind == "mdf":
            face = max(sh.Faces, key=lambda f: f.Area)
            import importDXF
            tmp = App.newDocument("dxf_tmp")
            o = tmp.addObject("Part::Feature", name)
            o.Shape = face
            importDXF.export([o], os.path.join(OUT, "DXF", name + ".dxf"))
            App.closeDocument(tmp.Name)
    with open(os.path.join(OUT, "STL", "printed_parts.txt"), "w") as f:
        f.write("\n".join(printed) + "\n")

    doc = App.newDocument("MODULE_CLAPETS_V5")
    folders = {}
    for key, label in (("A", "A  Clapets module: lift + doors"), ("B", "B  Suction head module"),
                       ("reserve", "R  Reserved space for module B (transparent)"), ("stack", "S  Reference: stack")):
        folders[key] = doc.addObject("App::DocumentObjectGroup", "F_" + key)
        folders[key].Label = label
    inst, count = [], {}
    for name, dx, dy, dz, grp in placements():
        count[name] = count.get(name, 0) + 1
        o = doc.addObject("Part::Feature", "%s_%d" % (name, count[name]))
        o.Shape = PARTS[name][0].copy()
        o.Placement = App.Placement(Vector(dx, dy, dz), App.Rotation())
        o.Label = "%s-%d" % (name, count[name])
        o.addProperty("App::PropertyString", "MotionGroup", "Motion").MotionGroup = grp
        o.addProperty("App::PropertyString", "Module", "Motion").Module = PARTS[name][4]
        key = "reserve" if grp == "reserve" else ("stack" if grp == "stack" else PARTS[name][4])
        folders[key].addObject(o)
        inst.append(o)
    doc.recompute()
    real = [o for o in inst if o.MotionGroup != "reserve"]
    clashes = []
    for i in range(len(real)):
        for j in range(i + 1, len(real)):
            si, sj = real[i].Shape, real[j].Shape
            if si.BoundBox.intersect(sj.BoundBox):
                v = si.common(sj).Volume
                if v > 0.01:
                    clashes.append("  %9.2f mm3  %s / %s" % (v, real[i].Label, real[j].Label))
    # module A must keep the head's fixed zone, cable passage and rest envelope free (the turning disc: checked in motion)
    res = [o for o in inst if o.MotionGroup == "reserve" and o.Name.startswith(("RES_TETE_FIXE", "RES_TETE_CABLES", "RES_TETE_REPOS"))]
    res_hits = []
    for r in res:
        for o in real:
            if o.Module != "A" or o.MotionGroup.startswith("door"):
                continue
            if r.Shape.BoundBox.intersect(o.Shape.BoundBox):
                v = r.Shape.common(o.Shape).Volume
                if v > 0.01:
                    res_hits.append("  %9.2f mm3  %s / %s" % (v, r.Label, o.Label))
    rep += ["", "Rest pose (carriage down, doors at contact, head vertical, stack in place): real parts"] + clashes
    rep.append("interferences: %d" % len(clashes))
    rep += ["", "Module A (fixed parts) inside the space reserved for module B:"] + res_hits
    rep.append("reserve violations: %d" % len(res_hits))
    doc.saveAs(os.path.join(OUT, "MODULE_CLAPETS_V5.FCStd"))
    Import.export(real, os.path.join(OUT, "STEP", "MODULE_CLAPETS_V5.step"))
    Import.export([o for o in real if o.Module == "A"], os.path.join(OUT, "STEP", "MODULE_A_CLAPETS.step"))
    Import.export([o for o in real if o.Module == "B"], os.path.join(OUT, "STEP", "MODULE_B_TETE.step"))
    with open(os.path.join(OUT, "report.txt"), "w") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep))


main()
