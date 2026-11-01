# v6_fc.py - CLAPETS MODULE v6 (copy of v5, refined for the first print): two modules with a clean interface (decision D-017, see docs/).
#   MODULE A "clapets" (lift + 2 doors) is designed AROUND reserved space for MODULE B "tete" (suction head):
#     - lift = Two Trees Bluer V2 Y axis on end (2 rails, the real butterfly plate + its 4 V-wheels, NEMA17, T8 screw)
#     - 2 door units (body + bolt-on cap), plain Ø8 rod in 2x 608 each, MG996R + 20T -> 28T, short doors that fold
#     - reserved for B: fixed zone, tube passage, rest envelope (cups vertical), turning disc R 140 (B needs R 108)
#   MODULE B bolts on the plate front (the 4 wheel bolts): Ø8 shaft in 2x 608, MG996R + 20T -> 30T, MDF carrier with
#     3 TPU cup stations (one cup per box, the middle one on the axis).
# Run (headless), from this folder's parent: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v6_fc.py   (~1 min)
# Output ../CAD_FC/: STEP/ (parts, MODULE_CLAPETS_V6.step, MODULE_A_CLAPETS.step, MODULE_B_TETE.step), STL/, DXF/,
#   MODULE_CLAPETS_V6.FCStd, report.txt (rest-pose collisions, module A vs the reserved head space)
# Inputs: fc/plaque_papillon_reelle.json (real butterfly plate), resources/mg996r/mg996R_v2.step (real servo).
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
    PL_GAP, PL_T = 4.0, 3.0                                 # real plate (from the .3dm): 3.0 thick, 14.0 from the wheel plane
    PL_Y0 = RAIL_YC + RAIL_W / 2 + PL_GAP                   # butterfly plate rear 47.5, front 50.5
    PL_Y1 = PL_Y0 + PL_T
    PL_ZC = 150
    WH_X, WH_DZ = 60.0, 37.5
    WH_R, WH_W = WH_X - RAIL_DX - RAIL_W / 2, 10.2
    SPRING_U = SPRING_V = 85                                # corner holes (M4) -> door units
    CLAMP_V = 10                                            # centre holes Ø4.3 (M4) -> nut support
    PIN_X = 25.8                                            # 3rd plate hole Ø4.2 at (25.8, 0): locating pin of the nut support
    MOT_Z1, SHELF_T = 46, 6
    CPL_Z0, CPL_Z1, SCREW_Z0, SCREW_Z1 = 58, 83, 71, 363
    NUT_Z = 110
    TOP_Z0, TOP_Z1 = 344, 366                              # 608 from below, 2.8 mm roof over it
    LIFT_CARRY, LIFT_TURN = 15, 75                          # turn: axis 165 + 75 = 240 >= 229.8 (stack half-diagonal) + 10
    BRG_R, BRG_T, BOSS_R = 11.1, 7.2, 14.5                  # 608 seat Ø22.2 (FDM holes print ~0.1 small) + 0.6 lead-in
    ROD_R = 4.1                                             # Ø8.2 bore for the clamps on the Ø8 rods (slides on, clamp closes it)
    INS3_R, INS3_D = 2.0, 6.0                               # M3 brass heat-set insert: hole Ø4.0 x 6
    INS4_R, INS4_D = 2.8, 7.0                               # M4 brass heat-set insert: hole Ø5.6 x 7
    # ---- reserved space for module B (in the carriage frame) ----
    HZ = 165                                                # head axis along y at x 0, z 165 = middle box centre (middle cup on it)
    RES_ROT_R, RES_ROT_Y0 = 140, 108.0                      # turning disc: R 140 (head needs R 108), from the carrier rear to the face
    RES_FIX = (-62, 62, PL_Y1, RES_ROT_Y0, 100, 200)       # fixed zone: bracket, bearings, drive (x0, x1, y0, y1, z0, z1)
    RES_CABLE = (-62, 62, PL_Y1, RES_ROT_Y0, 200, 230)     # tube passage above the bracket (slack loop for 90 deg + lift)
    RES_REST_X = 30                                         # rest envelope: carrier/rings x ±28 + 2 (folded door tips stop at x 30)
    # ---- MODULE A: door units ----
    PX, PY = 131, 82                                        # door rod (right): behind the head's turning disc; 28T tips stay at x <= 150
    LOW, UP, PT = 30, 226, 6
    W_X0, W_X1 = 66, 93                                     # back wall x (M4 at x 85); clear of the door servo flange
    WEB_Y0, WEB_Y1, WEB_Z0 = 57.0, 65.0, 120                # rear web (behind the arm lugs, min y 67.7), above the 28T hub
    ROD_Z0, ROD_Z1 = 30, 233
    GM, GZ1, GZ2 = 1.25, 20, 28                             # 20T pinion (MG996R) -> 28T on the rod: x1.4 (longer arms)
    GC = GM * (GZ1 + GZ2) / 2                               # 30
    SVY = PY - GC                                           # door servo axis (132, 52)
    # MG996R from the real model (mechanical/resources/mg996r-servo-3.snapshot.9/mg996R_v2.step): body 40.4 x 20.4 x 38,
    # shaft 10.2 from the shaft-end face, flange (2.4 thick) 28 above the bottom, ear holes Ø4 at ±24.5 from the body
    # centre, y ±5. Cable grommet: shaft-end face, centred, 3.7..8.3 above the bottom, sticks out 5.8.
    SV_L, SV_W, SV_H, SV_FL, SV_OUT, SV_HORN = 40.4, 20.4, 38.0, 28.0, 10.2, 43.5
    SV_EAR = 24.5
    SV_STEP = os.path.join(HERE, "..", "..", "clapets-v5", "resources", "mg996r", "mg996R_v2.step")  # shared with v5
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
    SY0, SY1, TAB_Y0 = 141, 183, 128                        # doors +7 mm (max: folded tips must stop at x 30)
    PAD_Y0, PAD_Y1 = 145, 182
    DZ0, DZ1 = 20, 265
    PADS_Z = ((35, 75), (145, 185), (225, 265))
    ARM1, ARM2 = (39, 49), (212, 222)
    FL1, FL2 = (37, 53), (206, 224)
    A_FOLD, A_CLAMP, A_OPEN = 90.0, 3.0, -38.0             # open -38: the whole door is behind the face; servo 128 x 1.4 = 179 deg
    NUT_W, NUT_L, NUT_T = 5.8, 6.6, 2.8                     # M3 nut pocket (nut 5.5 AF x 2.4) +0.3
    CAB_Z0, CAB_Z1, CAB_OUT = 3.7, 8.3, 5.8                 # grommet height above the bottom, how far it sticks out
    CAP_Z1 = UP + PT + 3                                    # door unit top cap: UP..235, printed upside down
    # ---- MODULE B: suction head ----
    CUPS_Z = (85, 165, 245)                                 # one cup per box, the middle one ON the head axis (box centre)
    ST_R_RIM, ST_R_RING, ST_R_HOLE, ST_R_HUB = 25, 28, 20, 8
    ST_BOLT_R, ST_BOLT_A = 24, (30, 150, 270)
    HB_Y0, HB_Y1 = PL_Y1, 86.0                              # bearing tube; floor 50.3..54 (pocket for module A's M3 head)
    HBR_Y0 = 54.0                                           # 608s at y 54..61 and 79..86 (25 mm apart), bore Ø22.1 from the front
    HC_Y0, HC_Y1 = 86.5, 94.5                               # shaft clamp hub, behind the gear
    HG_Y0, HG_Y1 = 94.5, 102.5                              # gear plane (head 30T on the shaft, 20T on the servo horn)
    HF_Y0, HF_Y1 = 103.0, 109.0                             # flange Ø56 = mount of the middle cup station (its 3 screws)
    CA_Y0, CA_Y1 = HF_Y1, HF_Y1 + 6                         # MDF 6 carrier 109..115
    RIM_Y1, RING_Y1 = CA_Y1 + 3, CA_Y1 + 6
    TH_Y0, TH_Y1 = CA_Y1 - 3.0, 122.0                       # TPU hub can move back 3 mm into the carrier hole
    CUP_Y0 = TH_Y1                                          # DP-S30 bellows Ø30, 18 mm -> face at y 140
    CA_Z0, CA_Z1 = CUPS_Z[0] - ST_R_RING, CUPS_Z[2] + ST_R_RING
    HGZ1, HGZ2 = 20, 30                                     # head gear pair x1.5: head 90 deg = servo 135 deg
    HGC = GM * (HGZ1 + HGZ2) / 2                            # 31.25
    HS_ANG = 25                                             # head servo axis 25 deg down-left of the head axis
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


def prism_xz(s, loop_xz, y0, y1):       # polygon in the xz plane (mirrored by s), extruded along +y
    pts = [Vector(s * p[0], y0, p[1]) for p in loop_xz]
    if s < 0:
        pts.reverse()
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, y1 - y0, 0))


def prism_yz(s, loop_yz, x0, x1):       # polygon in the yz plane, extruded along x from s*x0 to s*x1
    pts = [Vector(s * x0, p[0], p[1]) for p in loop_yz]
    if s < 0:
        pts.reverse()
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(s * (x1 - x0), 0, 0))


def chbox(s, x0, x1, y0, y1, z0, z1, c=1.5):   # box with its 4 vertical edges chamfered c x 45 deg
    return prism(s, [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)], z0, z1)


def zslot(s, x, y, z0, z1, r, dx=0.0, dy=0.0):   # vertical hole r, elongated ±dx / ±dy (lumiere)
    a = vcyl(s, x - dx, y - dy, z0, z1, r)
    b = vcyl(s, x + dx, y + dy, z0, z1, r)
    if dx:
        return a.fuse([b, box(s, x - dx, x + dx, y - r, y + r, z0, z1)])
    return a.fuse([b, box(s, x - r, x + r, y - dy, y + dy, z0, z1)])


def lead_in(s, x, y, z, r, up):          # 0.6 x 45 deg chamfer at the mouth of a vertical seat (face at z, opening up/down)
    h = 0.6
    if up:
        return Part.makeCone(r, r + h, h + 0.01, Vector(s * x, y, z - h), Vector(0, 0, 1))
    return Part.makeCone(r + h, r, h + 0.01, Vector(s * x, y, z - 0.01), Vector(0, 0, 1))


def circle(cx, cy, r, n):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def chamfer_loop(loop, c):              # cut every sharp corner (turn > 35 deg) of a convex loop by c (polygon arcs stay)
    out, n = [], len(loop)
    for i in range(n):
        p0, p1, p2 = loop[i - 1], loop[i], loop[(i + 1) % n]
        u = (p0[0] - p1[0], p0[1] - p1[1])
        v = (p2[0] - p1[0], p2[1] - p1[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        turn = math.pi - math.acos(max(-1, min(1, (u[0] * v[0] + u[1] * v[1]) / (lu * lv))))
        if turn > math.radians(35) and lu > 2 * c and lv > 2 * c:
            out += [(p1[0] + u[0] / lu * c, p1[1] + u[1] / lu * c), (p1[0] + v[0] / lv * c, p1[1] + v[1] / lv * c)]
        else:
            out.append(p1)
    return out


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




G.HS_X = -G.HGC * math.sin(math.radians(G.HS_ANG))  # (-13.2, 136.7): clear of the boss and module A's M3 heads
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


def support_ecrou():    # behind the plate, between the rails. Print: shelf on the bed.
    # 3 points on the real plate: 2x M4 x 8 button head (the printer's own) through the centre holes into M4 inserts,
    # + a printed pin in the plate's 3rd hole (x 25.8). T8 nut flange UNDER the shelf: the lift pushes plastic on brass,
    # the 4x M3 only locate it (into M3 inserts, from below; holes Ø4 in the flange let the nut self-centre on the screw).
    top = G.PL_ZC + G.CLAMP_V + 10
    wy0 = G.PL_Y0 - 8                                                                                # wall 8 thick, 2 mm off the screw
    a = [chbox(1, -25, 29.5, wy0, G.PL_Y0, G.NUT_Z, top, 2), chbox(1, -25, 25, YC - 13, wy0 + 1, G.NUT_Z, G.NUT_Z + 6, 3)]
    a += [box(s, 19, 25, YC - 11, wy0 + 0.5, G.NUT_Z + 6, top) for s in (1, -1)]
    a += [prism_xz(s, [(19, G.NUT_Z + 6), (19, G.NUT_Z + 14), (11, G.NUT_Z + 6)], YC - 11, wy0 + 0.5) for s in (1, -1)]   # 45 deg gussets
    a.append(ycyl(1, G.PIN_X, G.PL_Y0 - 0.1, G.PL_Y1 - 0.4, G.PL_ZC, 1.95))                            # locating pin Ø3.9
    c = [vcyl(1, 0, YC, G.NUT_Z - 1, G.NUT_Z + 7, 5.5)]                                              # nut body Ø10.2 up through the shelf
    c += [vcyl(1, 8 * math.cos(math.radians(45 + 90 * k)), YC + 8 * math.sin(math.radians(45 + 90 * k)), G.NUT_Z - 1,
               G.NUT_Z + G.INS3_D, G.INS3_R) for k in range(4)]
    for bz in (G.PL_ZC - G.CLAMP_V, G.PL_ZC + G.CLAMP_V):
        c.append(ycyl(1, 0, G.PL_Y0 - G.INS4_D, G.PL_Y0 + 1, bz, G.INS4_R))
    part("A_SUPPORT_ECROU", solid(a, c), 1270, PETG, "print", "A")


# ---------------------------------------------------------------- MODULE A: door units
def unit_plate_loop():
    return hull([(G.W_X0, G.PL_Y1), (G.W_X1, G.PL_Y1), (G.W_X0, G.PL_Y1 + 10)] + circle(G.PX, G.PY, G.BOSS_R, 40))


def cap_screws():       # door unit cap -> body: 3x M3 into inserts (inner side wall, rear web x2)
    return ((G.W_X0 + 4, 69), (104, G.WEB_Y0 + 4), (141, G.WEB_Y0 + 4))


def aile(s, name):
    # Door unit BODY, printed upright with no support: 9 mm bottom plate on the bed, an L spine (back wall on the
    # butterfly plate + inner side wall), a rear web with a 45 deg lower edge that closes the frame into a box behind the
    # rod (the arms only ever swing in front of it), 45 deg fillets at the joints, chamfered vertical edges.
    # The top plate is a separate bolt-on cap (A_CAPOT_AILE): rod, arms and 28T drop in from the top.
    a, c = [], []
    zb = G.LOW - 3                                                                                    # flat bottom (was a boss)
    a.append(prism(s, chamfer_loop(unit_plate_loop(), 2), zb, G.LOW + G.PT))
    a.append(chbox(s, 99, 150, G.SVY - 11, G.SVY + 11, zb, G.LOW + G.PT, 3))                           # servo area (bottom plate)
    a.append(vcyl(s, G.PX, G.PY, zb, G.LOW + G.PT, G.BOSS_R))
    a.append(chbox(s, G.W_X0, G.W_X1, G.PL_Y1, G.WEB_Y0, zb, G.PL_ZC + G.SPRING_V + 9, 2))             # back wall on the plate
    a.append(chbox(s, G.W_X0, G.W_X0 + 8, G.PL_Y1, G.PL_Y1 + 22, zb, G.UP, 2))                         # inner side wall
    web = [(G.W_X0, G.WEB_Z0 - 8), (G.W_X0 + 8, G.WEB_Z0 - 8), (148, G.WEB_Z0 + 140 - G.W_X0 - 8), (148, G.UP), (G.W_X0, G.UP)]
    a.append(prism_xz(s, web, G.WEB_Y0 - 0.1, G.WEB_Y1))                                               # rear web, 45 deg underside
    a.append(prism_xz(s, [(G.W_X0 + 8, G.LOW + G.PT), (G.W_X0 + 16, G.LOW + G.PT), (G.W_X0 + 8, G.LOW + G.PT + 8)], G.WEB_Y0, G.PL_Y1 + 22))
    a.append(prism(s, [(G.W_X0 + 8, G.WEB_Y1), (G.W_X0 + 14, G.WEB_Y1), (G.W_X0 + 8, G.WEB_Y1 + 6)], G.WEB_Z0, G.UP))
    a.append(prism_yz(s,[(G.WEB_Y0, G.LOW + G.PT), (G.WEB_Y0 + 7, G.LOW + G.PT), (G.WEB_Y0, G.LOW + G.PT + 7)], G.W_X0 + 8, 92))
    c.append(vcyl(s, G.PX, G.PY, G.LOW + G.PT - G.BRG_T, G.LOW + G.PT + 0.1, G.BRG_R))
    c.append(lead_in(s, G.PX, G.PY, G.LOW + G.PT, G.BRG_R, True))
    c.append(vcyl(s, G.PX, G.PY, zb - 1, G.UP + 1, 5.0))
    for x, y in cap_screws():
        c.append(vcyl(s, x, y, G.UP - G.INS3_D, G.UP + 1, G.INS3_R))
    for side, hy in ((-1, (5,)), (1, (-5, 5))):                                                      # MG996R posts up to the flange
        hx = G.SV_XC + side * G.SV_EAR
        y0 = G.SVY - 11 if side > 0 else G.PL_Y1
        a.append(box(s, hx - 3.8, hx + 3.8, y0, G.SVY + 11, G.LOW + G.PT, G.SV_FLZ))
        for dy in hy:
            yy0, yy1 = G.SVY + dy - G.SV_SLOT, G.SVY + dy + G.SV_SLOT
            c += [vcyl(s, hx, yy0, G.SV_FLZ - 13, G.SV_FLZ + 1, 1.7), vcyl(s, hx, yy1, G.SV_FLZ - 13, G.SV_FLZ + 1, 1.7),
                  box(s, hx - 1.7, hx + 1.7, yy0, yy1, G.SV_FLZ - 13, G.SV_FLZ + 1)]
            nb = nut(s, 2, hx, G.SVY + dy, G.SV_FLZ - 8, 0, side * 10)
            c += [nb.translated(Vector(0, d, 0)) for d in (-G.SV_SLOT, 0, G.SV_SLOT)]
    for bz in (G.PL_ZC - G.SPRING_V, G.PL_ZC + G.SPRING_V):                                          # M4 on the plate corners:
        for d in (-1.5, 1.5):                                                                         # slot ±1.5 in x (centre the doors)
            c.append(ycyl(s, G.SPRING_U + d, G.PL_Y1 - 1, G.PL_Y1 + 7, bz, 2.25))
        c.append(box(s, G.SPRING_U - 1.5, G.SPRING_U + 1.5, G.PL_Y1 - 1, G.PL_Y1 + 7, bz - 2.25, bz + 2.25))
        c.append(box(s, G.SPRING_U - 4.2 - 1.5, G.SPRING_U + 4.2 + 1.5, G.PL_Y1 + 2.4, G.PL_Y1 + 9, bz - 3.7, bz + 3.7))   # M4 nut slides
    # servo cable: it leaves the servo's shaft-end face = the OUTER end (x 141), centred, at the bottom, right against
    # the outer post. Channel in the post's inner face (open to the front, so the grommet slides in with the servo),
    # down into the 13 mm under the servo, out through a 10 x 10 slot in the bottom plate (the Dupont connector passes);
    # a zip tie through the 2 holes beside it holds the cable under the plate.
    xe = G.SV_X1
    c.append(box(s, xe - 0.5, xe + G.CAB_OUT + 0.6, G.SVY - 5, G.SVY + 12, G.LOW + G.PT - 0.1, G.SV_BOT + G.CAB_Z1 + 1.5))
    c.append(chbox(s, xe - 6, xe + G.CAB_OUT - 0.3, G.SVY - 5, G.SVY + 5, zb - 1, G.LOW + G.PT + 1, 1.5))
    for d in (-1, 1):
        c.append(box(s, xe - 15, xe - 10.5, min(G.SVY + d * 5, G.SVY + d * 7.6), max(G.SVY + d * 5, G.SVY + d * 7.6), zb - 1, G.LOW + G.PT + 1))
    # the flange ear. The strap (A_BRIDE_SERVO) screws on them and presses the servo down onto its flange screws.
    ztop = G.SV_BOT + G.SV_H
    for side in (-1, 1):
        hx = G.SV_XC + side * G.SV_EAR
        y0 = G.SVY - 11 if side > 0 else G.PL_Y1
        a.append(box(s, hx - 3.8, hx + 3.8, y0, G.SVY + 11, G.SV_FLZ + 3.8, ztop))                    # clears the ear's rib (+3.5)
        c += [vcyl(s, hx, G.SVY, ztop - 9, ztop + 1, 1.7), nut(s, 2, hx, G.SVY, ztop - 4.5, 0, side * 10)]
    a.append(box(s, 148.5, 150, G.SVY - 11, G.SVY + 11, G.LOW + G.PT, ztop))
    part(name, solid(a, c), 1270, PETG2, "print", "A")


def bride_servo(s, name):    # strap over the door servo body: 2x M3 into the post tops, ring around the output shaft
    ztop = G.SV_BOT + G.SV_H
    xa, xb = G.SV_XC - G.SV_EAR, G.SV_XC + G.SV_EAR
    a = [box(s, G.W_X1 + 0.1, xb + 3.8, G.SVY - 6, G.SVY + 6, ztop, ztop + 3), vcyl(s, G.PX, G.SVY, ztop, ztop + 3, 10.5)]
    c = [vcyl(s, G.PX, G.SVY, ztop - 1, ztop + 5, 7.3),                                            # output boss Ø13.2 passes
         box(s, G.PX - 24.5, G.PX - 8.1, G.SVY - 9.5, G.SVY + 9.5, ztop - 1, ztop + 1.4)]              # pocket: the case's label pad (+1.1)
    c += [zslot(s, x, G.SVY, ztop - 1, ztop + 5, 1.7, dx=1.0) for x in (xa, xb)]                   # lumiere ±1 in x
    part(name, solid(a, c), 1270, PETG, "print", "A")


def capot_aile(s, name):    # top cap of the door unit: top 608 (from below, lead-in), 3x M3 into the body's inserts.
    # Printed upside down (flat 9 mm plate, no support). Its back edge bears on the back wall's front face.
    loop = hull([(G.W_X0, G.WEB_Y0 + 0.2), (148, G.WEB_Y0 + 0.2), (148, G.WEB_Y1), (G.W_X0, G.PL_Y1 + 22)] + circle(G.PX, G.PY, G.BOSS_R, 40))
    a = [prism(s, chamfer_loop(loop, 2), G.UP, G.CAP_Z1)]
    c = [vcyl(s, G.PX, G.PY, G.UP - 0.1, G.UP + G.BRG_T, G.BRG_R), lead_in(s, G.PX, G.PY, G.UP, G.BRG_R, False),
         vcyl(s, G.PX, G.PY, G.UP, G.CAP_Z1 + 1, 5.0)]
    for x, y in cap_screws():
        c += [vcyl(s, x, y, G.UP - 1, G.CAP_Z1 + 1, 1.75), vcyl(s, x, y, G.CAP_Z1 - 3.2, G.CAP_Z1 + 1, 3.1)]
    part(name, solid(a, c), 1270, PETG2, "print", "A")


def bras(s, name, arm, fl):
    hub = circle(G.PX, G.PY, 11, 48)
    fy1 = G.BOX_Y0 - 3.5                                                                             # +3 deg clamp swings it ~1.2 mm forward
    flp = [(G.SX0 - 12, G.TAB_Y0), (G.SX0, G.TAB_Y0), (G.SX0, fy1), (G.SX0 - 12, fy1)]
    z0, z1 = arm
    a = [prism(s, hull(hub + flp), z0, z1), box(s, G.SX0 - 12, G.SX0, G.TAB_Y0, fy1, fl[0], fl[1])]
    ca, cc = split_clamp_z(s, G.PX, G.PY, z0, z1, [(z0 + z1) / 2])
    a += ca
    c = cc + [vcyl(s, G.PX, G.PY, z0 - 1, z1 + 1, G.ROD_R)]
    for z in (fl[0] + 3.5, fl[1] - 3.5):
        c += [xcyl(s, G.SX0 - 13, G.SX0 + 0.1, (G.TAB_Y0 + fy1) / 2, z, 1.7),
              nut(s, 0, G.SX0 - 12 + G.NUT_T / 2 - 0.1, (G.TAB_Y0 + fy1) / 2, z, 0, 0)]
    part(name, solid(a, c), 1270, PETG, "print", "A")


def roue_porte():
    hz1 = G.GZB + 14
    a = [prism(1, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.PY, G.GZB, hz1, 10)]
    ca, cc = split_clamp_z(1, G.PX, G.PY, G.GZB, hz1, [G.GZB + 4, hz1 - 4], lug_dir=1)
    a += ca
    part("A_ROUE_PORTE_28T", solid(a, cc + [vcyl(1, G.PX, G.PY, G.GZA - 1, hz1 + 1, G.ROD_R)]), 1270, PETG2, "print", "A")


def pignon_porte():
    a = [prism(1, gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R + 3)]
    c = [vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T - 1, G.GZA, G.HORN_R + 0.2), vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2)]
    c += [vcyl(1, G.PX + 7.5 * math.cos(math.pi / 2 * k), G.SVY + 7.5 * math.sin(math.pi / 2 * k), G.GZA - 1, G.GZB + 1, 0.8) for k in range(4)]
    part("A_PIGNON_PORTE_20T", solid(a, c), 1270, PETG2, "print", "A")


def entretoises():   # printed spacers: they touch only the 608 INNER races (Ø12), so nothing rubs on the outer race
    lo0, lo1 = G.LOW + G.PT, G.ARM1[0]                  # bottom: 608 top face -> arm BAS (3 mm)
    hi0, hi1 = G.ARM2[1], G.UP                          # top: arm HAUT -> 608 in the cap (4 mm)
    for name, z0, z1 in (("A_ENTRETOISE_608_BAS", lo0, lo1), ("A_ENTRETOISE_608_HAUT", hi0, hi1)):
        part(name, solid([vcyl(1, G.PX, G.PY, z0, z1, 6.0)], [vcyl(1, G.PX, G.PY, z0 - 1, z1 + 1, 4.15)]), 1270, PETG, "print", "A")
    # head: sleeve between the 2 outer races in the bracket tube (sets the front 608 flush with the tube)
    part("B_ENTRETOISE_TETE", solid([ycyl(1, 0, G.HBR_Y0 + 7, G.HB_Y1 - 7, G.HZ, 11.0)], [ycyl(1, 0, G.HBR_Y0 + 6, G.HB_Y1 - 6, G.HZ, 8.5)]),
         1270, PETG, "print", "B")


def tole():
    a, c = [box(1, G.SX0, G.SX1, G.SY0, G.SY1, G.DZ0, G.DZ1)], []
    for f0, f1 in (G.FL1, G.FL2):
        a.append(box(1, G.SX0, G.SX1, G.TAB_Y0, G.SY0, f0, f1))
        for z in (f0 + 3.5, f1 - 3.5):                                                                # lumiere ±1.5 in y: set the pad
            yc = (G.TAB_Y0 + G.BOX_Y0 - 3.5) / 2                                                       # position vs the box face
            c += [xcyl(1, G.SX0 - 1, G.SX1 + 1, yc + d, z, 1.7) for d in (-1.5, 1.5)]
            c.append(box(1, G.SX0 - 1, G.SX1 + 1, yc - 1.5, yc + 1.5, z - 1.7, z + 1.7))
    part("A_TOLE_PORTE", solid(a, c), 750, MDF, "mdf", "A")


# ---------------------------------------------------------------- MODULE B: suction head
def tete_support():     # bracket: 4x M5 (the wheel bolts, longer) on the plate; bearing tube (608 at both ends); servo posts
    hz = G.HZ
    a = [prism_xz(1, chamfer_loop([(-52, 100), (52, 100), (52, 200), (-52, 200)], 4), G.PL_Y1, G.PL_Y1 + 6)]
    for sx in (1, -1):
        for dz in (-G.WH_DZ, G.WH_DZ):
            a.append(box(1, min(sx * 52, sx * 65.5), max(sx * 52, sx * 65.5), G.PL_Y1, G.PL_Y1 + 6, G.PL_ZC + dz - 8, G.PL_ZC + dz + 8))
    a.append(ycyl(1, 0, G.HB_Y0, G.HB_Y1, hz, 17))                                                   # bearing tube
    a.append(box(1, -6, 6, G.PL_Y1, G.HB_Y1, hz + 10, 200))                                          # web: tube <-> plate (top)
    for hx in (G.HS_SVXC - G.SV_EAR, G.HS_SVXC + G.SV_EAR):                                              # servo posts to the flange
        a.append(chbox(1, hx - 3.8, hx + 3.8, G.PL_Y1, G.HS_FL_Y, G.HS_Z - 11, G.HS_Z + 11, 1.5))
    c = [ycyl(1, 0, G.HBR_Y0, G.HB_Y1 + 1, hz, G.BRG_R),                                              # both 608 slide in from the front
         Part.makeCone(G.BRG_R, G.BRG_R + 0.6, 0.61, Vector(0, G.HB_Y1 - 0.6, hz), Vector(0, 1, 0)),
         # head servo cable: it leaves the shaft-end face (+x end, x -3.2), centred, at the bottom = next to the plate.
         # The servo window is extended past that end, then an L slot runs down to the bracket's bottom edge (lay the
         # cable in from the front); 2 zip-tie holes beside it open into the plate's centre notch.
         box(1, G.HS_SVX1 - 0.5, G.HS_SVX1 + 14, G.PL_Y1 - 1, G.PL_Y1 + 7, G.HS_Z - 5.5, G.HS_Z + 5.5),
         box(1, G.HS_SVX1 + 6, G.HS_SVX1 + 14, G.PL_Y1 - 1, G.PL_Y1 + 7, 99, G.HS_Z),
         box(1, G.HS_SVX1 + 2, G.HS_SVX1 + 4.6, G.PL_Y1 - 1, G.PL_Y1 + 7, 104, 108.5),
         box(1, G.HS_SVX1 + 16, G.HS_SVX1 + 18.6, G.PL_Y1 - 1, G.PL_Y1 + 7, 104, 108.5),
         ycyl(1, 0, G.HB_Y0 - 1, G.HB_Y1 + 1, hz, 5.0)]
    c.append(box(1, G.HS_SVX0 - 1.5, G.HS_SVX1 + 0.6, G.PL_Y1 - 1, G.PL_Y1 + 7, G.HS_Z - G.SV_W / 2 - 1, G.HS_Z + G.SV_W / 2 + 1))   # window: servo body
    for bz in (G.PL_ZC - G.CLAMP_V, G.PL_ZC + G.CLAMP_V):                                              # pockets: module A's M4 button heads
        c.append(ycyl(1, 0, G.PL_Y1 - 1, G.PL_Y1 + 2.6, bz, 4.2))                                       # (Ø7.6 x 2.2)
    for sx in (1, -1):
        for dz in (-G.WH_DZ, G.WH_DZ):
            c.append(ycyl(1, sx * G.WH_X, G.PL_Y1 - 1, G.PL_Y1 + 7, G.PL_ZC + dz, 2.75))
    for hx in (G.HS_SVXC - G.SV_EAR, G.HS_SVXC + G.SV_EAR):                                              # M3 through the flange (±1.5 slot in x)
        out = -1 if hx < G.HS_SVXC else 1
        for dz in (-5, 5):
            c += [ycyl(1, hx + d, G.HS_FL_Y - 13, G.HS_FL_Y + 1, G.HS_Z + dz, 1.7) for d in (-1.5, 0, 1.5)]
            c.append(box(1, min(hx - 3.3, hx + out * 12), max(hx + 3.3, hx + out * 12), G.HS_FL_Y - 9, G.HS_FL_Y - 6.4, G.HS_Z + dz - 2.8, G.HS_Z + dz + 2.8))
    part("B_SUPPORT_TETE", solid(a, c), 1270, PETG, "print", "B")


def tete_moyeu():       # clamp hub + 30T gear + Ø56 flange in one part. The middle cup station screws INTO the flange
    hz = G.HZ                                    # (3x M3, nuts in pockets at the back): it also holds the carrier.
    ang_to_servo = math.degrees(math.atan2(G.HS_Z - hz, G.HS_X))
    a = [ycyl(1, 0, G.HC_Y0, G.HC_Y1, hz, 10),                                                       # clamp hub
         ycyl(1, 0, G.HB_Y1 + 0.05, G.HC_Y0 + 0.1, hz, 6.0),                                         # boss on the 608 inner race
         box(1, -6, 6, G.HC_Y0, G.HC_Y1, hz + 4, hz + 14),                                           # its lug (up: away from the pinion)
         prism_y(gear(0, hz, G.GM, G.HGZ2, ang_to_servo + 180.0 / G.HGZ2, 0.15), G.HG_Y0, G.HG_Y1),
         ycyl(1, 0, G.HG_Y1 - 0.1, G.HF_Y0 + 0.1, hz, 12),                                          # neck gear -> flange
         ycyl(1, 0, G.HF_Y0, G.HF_Y1, hz, G.ST_R_RING)]
    c = [ycyl(1, 0, G.HC_Y0 - 1, G.HF_Y0 + 1.5, hz, G.ROD_R),                                          # shaft (blind: ends in the flange)
         box(1, -0.6, 0.6, G.HC_Y0 - 1, G.HC_Y1 + 0.01, hz, hz + 15),                                # clamp slot
         xcyl(1, -7, 7, (G.HC_Y0 + G.HC_Y1) / 2, hz + 9.5, 1.7), xcyl(1, -7, -4.5, (G.HC_Y0 + G.HC_Y1) / 2, hz + 9.5, 3.0),
         box(1, 6 - G.NUT_T, 6 + 0.01, G.HC_Y0 - 1, G.HC_Y1 + 0.01, hz + 9.5 - 2.8, hz + 9.5 + 2.8),
         ycyl(1, 0, G.HF_Y1 - 3, G.HF_Y1 + 1, hz, 10)]                                              # room for the TPU hub to move back
    for ang in G.ST_BOLT_A:
        t = math.radians(ang)
        x, z = G.ST_BOLT_R * math.cos(t), hz + G.ST_BOLT_R * math.sin(t)
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


def tete_plateau():     # MDF 6 carrier: 3 stations (middle on the axis, clamped onto the hub flange), tube notches
    a = [prism_y(stadium(G.CA_Z0, G.CA_Z1, G.ST_R_RING), G.CA_Y0, G.CA_Y1)]
    c = []
    for cz in G.CUPS_Z:
        c.append(ycyl(1, 0, G.CA_Y0 - 1, G.CA_Y1 + 1, cz, G.ST_R_HOLE))
        for ang in G.ST_BOLT_A:
            t = math.radians(ang)
            c.append(ycyl(1, G.ST_BOLT_R * math.cos(t), G.CA_Y0 - 1, G.CA_Y1 + 1, cz + G.ST_BOLT_R * math.sin(t), 1.7))
        # tube notch: from the station hole to the +x edge, in the carrier's thickness (the tube leaves sideways, then back)
        c.append(box(1, G.ST_R_HOLE - 1, G.ST_R_RING + 1, G.CA_Y0 - 1, G.CA_Y1 + 1, cz - 2.6, cz + 2.6))
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
    # the REAL butterfly plate (Two Trees Bluer V2 heatbed base, "Product 298"), outline + holes read from the .3dm
    # (fc/plaque_papillon_reelle.json, centre = wheel pattern). Mounted with its 3rd hole at +x, eccentric wheels at +x.
    import json
    with open(os.path.join(HERE, "plaque_papillon_reelle.json")) as f:
        pl = json.load(f)
    y0, y1, cz = G.PL_Y0, G.PL_Y1, G.PL_ZC
    a = [prism_xz(1, [(x, cz + z) for x, z in pl["outer"]], y0, y1)]
    c = [ycyl(1, x, y0 - 1, y1 + 1, cz + z, d / 2) for x, z, d in pl["holes"]]
    part("REF_PLAQUE_PAPILLON", solid(a, c), 2700, DARK, "ref", "A")
    part("REF_ROUE_V", ycyl(1, G.WH_X, YC - G.WH_W / 2, YC + G.WH_W / 2, G.PL_ZC - G.WH_DZ, G.WH_R), 1400, DARK, "ref", "A")
    part("REF_608ZZ", solid([vcyl(1, G.PX, G.PY, G.LOW + G.PT - 7, G.LOW + G.PT, 11)], [vcyl(1, G.PX, G.PY, 0, 400, 4)]), 7850, STEEL, "ref", "A")
    part("REF_608ZZ_TETE", solid([ycyl(1, 0, G.HBR_Y0, G.HBR_Y0 + 7, G.HZ, 11)], [ycyl(1, 0, 0, 200, G.HZ, 4)]), 7850, STEEL, "ref", "B")
    part("REF_NEMA17", solid([box(1, -21.15, 21.15, YC - 21.15, YC + 21.15, G.MOT_Z1 - 40, G.MOT_Z1),
                              vcyl(1, 0, YC, G.MOT_Z1, G.MOT_Z1 + 2, 11), vcyl(1, 0, YC, G.MOT_Z1 + 2, G.MOT_Z1 + 24, 2.5)]), 3500, DARK, "ref", "A")
    part("REF_COUPLEUR_5x8", solid([vcyl(1, 0, YC, G.CPL_Z0, G.CPL_Z1, 9.5)],
                                   [vcyl(1, 0, YC, G.SCREW_Z0, G.CPL_Z1 + 1, 4), vcyl(1, 0, YC, G.CPL_Z0 - 1, G.MOT_Z1 + 24, 2.5)]), 2700, ALU, "ref", "A")
    part("REF_VIS_T8", vcyl(1, 0, YC, G.SCREW_Z0, G.SCREW_Z1, 4), 7850, STEEL, "ref", "A")
    part("REF_ECROU_T8", solid([vcyl(1, 0, YC, G.NUT_Z - 3.5, G.NUT_Z, 11), vcyl(1, 0, YC, G.NUT_Z - 0.1, G.NUT_Z + 11.5, 5.1)],   # flange under the shelf
                               [vcyl(1, 0, YC, 0, 400, 4)]), 8500, BRASS, "ref", "A")
    part("REF_TIGE_PORTE_D8", vcyl(1, G.PX, G.PY, G.ROD_Z0, G.ROD_Z1, 4), 7850, STEEL, "ref", "A")
    part("REF_AXE_TETE_D8", ycyl(1, 0, G.HBR_Y0 + 0.5, G.HF_Y0 + 1.5, G.HZ, 4), 7850, STEEL, "ref", "B")
    part("REF_MOUSSE_PORTE", box(1, G.PAD_X0, G.SX0, G.PAD_Y0, G.PAD_Y1, G.PADS_Z[0][0], G.PADS_Z[0][1]), 50, FOAM, "ref", "A")
    # MG996R = the real model (body, shaft, screws, cable grommet; its straight wire stub is replaced by the routed cable)
    sv = Part.read(G.SV_STEP)
    sv = Part.makeCompound(sv.Solids[:8])
    for s, name in ((1, "REF_MG996R_D"), (-1, "REF_MG996R_G")):
        sh = sv.copy()
        if s < 0:
            sh.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 180)
        sh.translate(Vector(s * G.PX, G.SVY, G.SV_BOT + 28))
        cab = box(s, G.PX + 12, G.PX + 14.5, G.SVY - 3, G.SVY + 3, G.LOW - 15, G.SV_BOT + 7.5)       # cable: down through the slot
        part(name, Part.makeCompound(sh.Solids + [cab]), 1200, SERVO, "ref", "A")
    sh = sv.copy()                                                                                   # head servo: top -> +y
    sh.rotate(Vector(0, 0, 0), Vector(1, 0, 0), -90)
    sh.translate(Vector(G.HS_X, G.HS_BODY_Y0 + 28, G.HS_Z))
    cab = [box(1, G.HS_X + 14, G.HS_X + 20, G.HS_BODY_Y0 + 4.5, G.HS_BODY_Y0 + 7.5, G.HS_Z - 2.5, G.HS_Z + 2.5),
           box(1, G.HS_X + 17, G.HS_X + 20, G.HS_BODY_Y0 + 4.5, G.HS_BODY_Y0 + 7.5, 95, G.HS_Z + 2.5)]
    part("REF_MG996R_TETE", Part.makeCompound(sh.Solids + cab), 1200, SERVO, "ref", "B")
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
         ("REF_608ZZ_TETE", 0, G.HB_Y1 - 7 - G.HBR_Y0, 0, "carriage"), ("B_ENTRETOISE_TETE", 0, 0, 0, "carriage"),
         ("A_BRIDE_SERVO_D", 0, 0, 0, "carriage"), ("A_BRIDE_SERVO_G", 0, 0, 0, "carriage"),
         ("A_CAPOT_AILE_D", 0, 0, 0, "carriage"), ("A_CAPOT_AILE_G", 0, 0, 0, "carriage"),
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
              ("A_ENTRETOISE_608_BAS", dx, 0, 0, door), ("A_ENTRETOISE_608_HAUT", dx, 0, 0, door),
              ("REF_608ZZ", dx, 0, 0, "carriage"), ("REF_608ZZ", dx, 0, G.UP - (G.LOW + G.PT - 7), "carriage"),
              ("A_TOLE_PORTE", 0 if s > 0 else -(G.SX0 + G.SX1), 0, 0, door)]
        p += [("REF_MOUSSE_PORTE", 0 if s > 0 else -(G.PAD_X0 + G.SX0), 0, z0 - G.PADS_Z[0][0], door) for z0, _ in G.PADS_Z]
    return p


def build_all():
    socle(); haut(); support_ecrou(); aile(1, "A_AILE_D"); aile(-1, "A_AILE_G")
    for s, tag in ((1, "D"), (-1, "G")):
        bras(s, "A_BRAS_PORTE_%s_BAS" % tag, G.ARM1, G.FL1)
        bras(s, "A_BRAS_PORTE_%s_HAUT" % tag, G.ARM2, G.FL2)
    roue_porte(); pignon_porte(); tole(); bride_servo(1, "A_BRIDE_SERVO_D"); bride_servo(-1, "A_BRIDE_SERVO_G")
    capot_aile(1, "A_CAPOT_AILE_D"); capot_aile(-1, "A_CAPOT_AILE_G")
    entretoises(); tete_support(); tete_moyeu(); tete_pignon(); tete_plateau(); tete_station_tpu(); tete_bague(); refs()


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

    doc = App.newDocument("MODULE_CLAPETS_V6")
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
    doc.saveAs(os.path.join(OUT, "MODULE_CLAPETS_V6.FCStd"))
    Import.export(real, os.path.join(OUT, "STEP", "MODULE_CLAPETS_V6.step"))
    Import.export([o for o in real if o.Module == "A"], os.path.join(OUT, "STEP", "MODULE_A_CLAPETS.step"))
    Import.export([o for o in real if o.Module == "B"], os.path.join(OUT, "STEP", "MODULE_B_TETE.step"))
    with open(os.path.join(OUT, "report.txt"), "w") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep))


main()
