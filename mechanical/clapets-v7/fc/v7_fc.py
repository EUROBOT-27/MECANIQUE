# v7_fc.py - CLAPETS MODULE v7 (v6 + reworked door units): two modules with a clean interface (decision D-017, see docs/).
#   MODULE A "clapets" (lift + 2 doors) is designed AROUND reserved space for MODULE B "tete" (suction head):
#     - lift = Two Trees Bluer V2 Y axis on end (2 rails, the real butterfly plate + its 4 V-wheels, NEMA17, T8 screw)
#     - 2 door units (body + bolt-on cap), plain Ø8 rod in 2x 608 each, MG996R + 20T -> 28T, short doors that fold
#     - reserved for B: fixed zone, tube passage, rest envelope (cups vertical), turning disc R 140 (B needs R 108)
#   MODULE B bolts on the plate front (the 4 wheel bolts): Ø8 shaft in 2x 608, MG996R + 20T -> 30T, MDF carrier with
#     3 TPU cup stations (one cup per box, the middle one on the axis).
# Run (headless), from this folder's parent: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v7_fc.py   (~1 min)
# Output ../CAD_FC/: STEP/ (parts, MODULE_CLAPETS_V7.step, MODULE_A_CLAPETS.step, MODULE_B_TETE.step), STL/, DXF/,
#   MODULE_CLAPETS_V7.FCStd, report.txt (rest-pose collisions, module A vs the reserved head space)
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
    RAIL_W, RAIL_DX, RAIL_YC, RAIL_Z0, RAIL_L = 20, 40.45, 58.5 + LIFT_DY - 0.5, 6, 350   # v7: -0.5 (real plate gap 4.5)
    PL_GAP, PL_T = 4.5, 3.0                                 # real plate (from the .3dm): 3.0 thick, 14.0 from the wheel plane
    PL_Y0 = RAIL_YC + RAIL_W / 2 + PL_GAP                   # butterfly plate rear 47.5, front 50.5
    PL_Y1 = PL_Y0 + PL_T
    PL_ZC = 150
    WH_X, WH_DZ = 60.0, 37.5
    # v7: real Two Trees parts (../../resources/two-trees-bluer-v2-parts, printer coordinates). Printer -> module:
    # X = TT_X0 - x, Y = z - TT_ZR + RAIL_YC, Z = y - (printer y of the reference) + (module z of the reference)
    TT_DIR = os.path.join(HERE, "..", "..", "resources", "two-trees-bluer-v2-parts")
    TT_X0, TT_ZR, TT_YR0, TT_YW = 120.75, 54.0, 115.1, 290.1   # axis x, rail centre plane, rail bottom end, wheel centre
    TT_ZAX = (263.0, 191.2)                                 # printer Z axis (motor, coupler, nut): x, y
    TT_CPL_Z0, TT_NUT_FL = 50.5, 263.1                      # printer coupler bottom; nut flange face on the long-body side
    WH_R, WH_W = WH_X - RAIL_DX - RAIL_W / 2, 10.2
    SPRING_U = SPRING_V = 85                                # corner holes (M4) -> door units
    SUP_WALL = 5.0                                          # 2026-11-10: nut support wall (M4 nuts in pockets, no inserts)
    CLAMP_V = 10                                            # centre holes Ø4.3 (M4) -> nut support
    PIN_X = 25.8                                            # 3rd plate hole Ø4.2 at (25.8, 0): not used since 2026-11-10 (nut support pin removed)
    MOT_PAD, MOT_L, SHELF_T = 1.0, 37.0, 6                   # 2026-11-10: no pad, 1 mm air gap under the motor (it hangs from the clamp plate); body 37.0 (2026-11-09: printer's own motor, from its model)
    MOT_Z1 = MOT_PAD + MOT_L                                # motor top face = underside of the clamp plate (38)
    BLK_Y1, BLK_YI = 58.5 + LIFT_DY - 0.5 + 10 + 12, 58.5 + LIFT_DY - 0.5 + 10 + 6   # rail blocks to y 55; inserts at y 49
    CPL_Z0, CPL_Z1, SCREW_Z0, SCREW_Z1 = 47, 72, 60, 363    # v7: coupler 2 mm over the clamp plate; lead screw 303 mm
    NUT_Z = 110
    TOP_Z0, TOP_Z1 = 344, 366                              # 608 from below, 2.8 mm roof over it
    LIFT_CARRY, LIFT_TURN = 15, 75                          # turn: axis 165 + 75 = 240 >= 229.8 (stack half-diagonal) + 10
    BRG_R, BRG_T, BOSS_R = 11.1, 7.2, 14.5                  # 608 seat Ø22.2 (FDM holes print ~0.1 small) + 0.6 lead-in
    ROD_R = 4.1                                             # Ø8.2 bore for the clamps on the Ø8 rods (slides on, clamp closes it)
    INS3_R, INS3_D = 2.3, 7.0                               # M3 heat-set insert hole Ø4.6 (fits Seif's inserts, OD 5.6..6.0 x 6);
                                                            # 2026-11-09: blind depth 6.5 -> 7.0 = insert + 1 (design-principles.md)
    INS_CH = 0.5                                            # 2026-11-09: 0.5 x 45 deg lead-in at every insert hole mouth (Ø5.6 = small end of the insert)
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
    SV_L, SV_W, SV_H, SV_FL, SV_OUT, SV_HORN = 40.4, 20.4, 38.0, 28.0, 10.2, 47.4   # 2026-11-09: measured horn disc top (v6 model: 45.7)
    SV_EAR = 24.5
    SV_DIR = os.path.join(HERE, "..", "..", "resources", "mg996r-servo-3.snapshot.9")   # real GrabCAD model (body + horns)
    SV_STEP = os.path.join(SV_DIR, "mg996R_v2.step")
    HORN_STEP = os.path.join(SV_DIR, "mg996_arm_round.step")   # round horn: hub Ø9 x 3, disc Ø20.8 x 2.5, boss Ø9.2 x 0.8
    SV_X1 = PX + SV_OUT
    SV_X0 = SV_X1 - SV_L
    SV_XC = (SV_X0 + SV_X1) / 2
    SV_BOT = LOW + PT + 13                                  # door servo stands on the bottom plate; flange above the plate lobe
    SV_FLZ = SV_BOT + SV_FL
    GZA = SV_BOT + SV_HORN
    GZB = GZA + 8                                           # door gears z 92.5..100.5 (28T reaches y 100.75 < 108)
    HUB28_H = 22.0                                          # 2026-11-10: 28T clamp hub height (was 14: its 2 nut pockets overlapped)
    HORN_R, HORN_T = 10.4, 2.5                              # v6: real round horn disc (was Ø21 x 2)
    HORN_BOSS_R, HORN_BOSS_T, HORN_HOLE_R = 4.6, 0.8, 7.2   # centre boss Ø9.2 on the disc top; screw holes on r 7.2 (axes)
    HORN_SCR_R = 1.25                                       # 2026-11-12: M2 holes in the pinion Ø2.2 -> Ø2.5 (ABS coupon T9: too tight)
    SV_SLOT = 2
    OW_X0 = 146.5                                           # v7 door unit: outer wall x 146.5..150, full height
    BW_X0, BW_Y1 = 100.0, 45.0                              # v7: back wall of the box (y 41..45) from x 100; inner closing wall x 100..104
    HEAD3_R = 3.3                                           # M3 button head Ø5.7 + clearance
    PAD_X0, PAD_T = 160, 8
    SX0 = PAD_X0 + PAD_T
    SX1 = SX0 + 3
    SY0, SY1, TAB_Y0 = 141, 183, 127                        # doors +7 mm (max: folded tips must stop at x 30)
                                                            # 2026-11-10: TAB_Y0 128 -> 127: arm tab 9.5 thick, insert walls 1.75
    PAD_Y0, PAD_Y1 = 145, 182
    DZ0, DZ1 = 20, 265
    PADS_Z = ((35, 75), (145, 185), (225, 265))
    ARM1, ARM2 = (39, 49), (212, 222)
    ARM_SC, TAB_D = 7.0, 8.0                                # 2026-11-10: door sheet screws 7 above / below the arm (nut in free air,
                                                            # room for a 5.5 wrench); tab 8 deep behind the sheet, M3 x 16 + nut
    FL1 = (ARM1[0] - ARM_SC - 5, ARM1[1] + ARM_SC + 5)     # (27, 61)
    FL2 = (ARM2[0] - ARM_SC - 5, ARM2[1] + ARM_SC + 5)     # (200, 234)
    A_FOLD, A_CLAMP, A_OPEN = 90.0, 3.0, -38.0             # open -38: the whole door is behind the face; servo 128 x 1.4 = 179 deg
    NUT_W, NUT_L, NUT_T = 5.8, 6.6, 2.8                     # M3 nut pocket (nut 5.5 AF x 2.4) +0.3
    CLAMP_NUT_W, CLAMP_NUT_L = 6.0, 6.9                     # 2026-11-10: roomier pockets on the rod clamps (printed holes come out small)
    # 2026-11-10: door servo posts: M3 nut under a roof (an insert can't get > 1.1 mm of wall: servo body 4.3 from the ear hole)
    POST_ROOF, POST_HEX, POST_HEX_D, POST_WIN = 1.6, 5.9, 2.5, 10.0   # roof over the nut; hex recess AF x depth; window height
                                                            # 2026-11-12: AF 5.7 -> 5.9 = 0.2 per side on the 5.5 nut (Seif, after T3)
    CAB_Z0, CAB_Z1, CAB_OUT = 3.7, 8.3, 5.8                 # grommet height above the bottom, how far it sticks out
    RHO_PRINT = 1240                                        # 2026-11-10: PLA (we print PLA / ABS, no PETG); was 1270 (PETG)
    CAP_Z1 = 242.0                                          # 2026-11-10 (option B): cap UP..242, covers the top plate M4 (z 235)
    # ---- 2026-11-10: door unit rebuilt as option B (mechanical/concepts/aile-redesign): C-section spine + cap
    K_X0, K_X1, K_Y1 = 66.0, 99.0, 60.5                     # keel on the plate (y PL_Y1..60.5), carries the bottom M4
    BWB_Y0, BWB_Y1 = 34.0, 37.0                             # back wall behind the servo (20T tips reach y 38.25)
    WEB_X0 = 96.2                                           # web keel <-> back wall; its inside fillet must stay clear of the plate edge (x 95)
    OWB_X0 = 147.0                                          # outer wall x 147..150
    FRONT_Y = 63.0                                          # front of the servo zone (posts, top shelf)
    OWB_Y1 = 69.0                                           # outer wall front edge (28T stays at y >= 72.2 there); 2026-11-12: 66 -> 69,
                                                            # the strip in front of the ear opening was 2 mm (T8: fragile), now 5 mm
    EAR_IN_H = 33.0                                         # 2026-11-12: inner ear key opening 15 -> 33 tall above the flange (T8: no room for the key)
    # 2026-11-12: cap -> body, 3rd screw from the FRONT: a tab hangs from the cap over the keel's front face (x 67.5..78,
    # z 210..226, 4 mm thick), M3 x 10 through it into an M3 insert set horizontally in the keel's front face
    CTAB_X0, CTAB_X1, CTAB_Z0, CTAB_T = 67.5, 78.0, 210.0, 4.2
    CTAB_SCR = (72.75, 218.0)                               # screw axis (x, z), along -y
    # 2026-11-12: form lock on the butterfly plate: 2 flat teeth in the plate's plane (y 47.8..50.5) against the two
    # diagonal edges of the plate's wing (bottom tooth on the body, top tooth on the cap). The wing sits between them:
    # the door clamp reaction (+x) and the stack weight (-z) bear on the plate's edges, not on the M4s' grip.
    # Mount: push the unit outward (+x) in its M4 slots until the teeth touch, then tighten.
    LOCK_X0, LOCK_X1, LOCK_GAP, LOCK_Y0 = 67.0, 76.0, 0.3, 47.8   # tooth x range, normal gap to the edge, tooth back face
    TSH_Z0 = 218.0                                          # top shelf z 218..226 (stays at y <= 63: the top arm swings in front)
    WIN_Z0, WIN_Z1 = 112.0, 212.0                           # big windows in the back + outer walls
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
    HS_BODY_Y0 = 51.0                                       # body bottom 0.5 off the plate (its screw heads stick out 0.3)
    HCAB_X, HCAB_Z1 = 21.0, 215.0                           # v6: head servo cable rises at x ~21 (clear of the Ø34 tube) to z 215
    HS_HORN_Y = HS_BODY_Y0 + SV_HORN                        # v6: real horn top 96.7, inside the gear plane: the 20T is
                                                            # shorter (96.7..102.5) and sits ON the horn (no collar)


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


def ins_hole(s, x, y, z, dirv, d=3):     # heat-set insert hole: face centre (x, y, z), dirv = into the part; + 45 deg lead-in
    r, depth = (G.INS3_R, G.INS3_D) if d == 3 else (G.INS4_R, G.INS4_D)
    p, u = Vector(s * x, y, z), Vector(s * dirv[0], dirv[1], dirv[2])
    hole = Part.makeCylinder(r, depth + 1, p - u * 1, u)
    cone = Part.makeCone(r + G.INS_CH + 0.01, r, G.INS_CH + 0.01, p - u * 0.01, u)
    return hole.fuse(cone)


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


def nut(s, axis, x, y, z, open_, ext, w=None, l=None):
    w, l = w or G.NUT_W, l or G.NUT_L
    lo, hi, half = [x, y, z], [x, y, z], [0.0, 0.0, 0.0]
    half[axis] = G.NUT_T / 2
    a1, a2 = (axis + 1) % 3, (axis + 2) % 3
    half[a1], half[a2] = w / 2, l / 2
    if open_ == a1:
        half[a1], half[a2] = l / 2, w / 2
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


def split_clamp_z(s, x, y, z0, z1, screws_z, lug_dir=-1, cb_ext=0.0, nut_ext=0.0):
    """Split clamp on a vertical Ø8 rod: lug towards lug_dir*y, slot through the bore, M3 screws along x.
    cb_ext: the head counterbore goes cb_ext further out (2026-11-08: the arm hub hid half of the head: no way in).
    nut_ext: the nut pocket goes nut_ext further out (2026-11-10: the arm hub covered the pocket mouth: no way in)."""
    y_a, y_b = (y - 4, y - 14) if lug_dir < 0 else (y + 4, y + 14)
    a = [box(s, x - 6, x + 6, min(y_a, y_b), max(y_a, y_b), z0, z1)]
    c = [box(s, x - 0.6, x + 0.6, min(y, y_b) - 1, max(y, y_b) + 1, z0 - 1, z1 + 1)]
    ym = (y_a + y_b) / 2
    for z in screws_z:
        c += [xcyl(s, x - 7, x + 7, ym, z, 1.7), nut(s, 0, x + 6 - G.NUT_T / 2 + 0.1, ym, z, 0, nut_ext, G.CLAMP_NUT_W, G.CLAMP_NUT_L),
              xcyl(s, x - 7 - cb_ext, x - 4, ym, z, 3.3)]                     # 2026-11-10: Ø6.6 for the Ø5.5 head (was 6.0)
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
    # v7: the motor stands on the floor (on its pad) in a notch of the base, open at the back for its connector. The rail
    # blocks are bigger: 2 M3 inserts each on top, for the motor clamp plate. Floor screws (M4) outside the blocks.
    a = [box(1, -68, 68, YC - 24.5, YC + 27.5, 0, G.RAIL_Z0)]
    c = [box(1, -21.65, 21.65, YC - 31, YC + 21.65, -1, G.RAIL_Z0 + 1)]                                # motor notch
    for s in (1, -1):
        a.append(box(s, G.RAIL_DX - 14, G.RAIL_DX + 16, RY0 - 4, G.BLK_Y1, G.RAIL_Z0, G.MOT_Z1))
        c += [box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, RY0 - 0.2, RY1 + 0.2, G.RAIL_Z0, 100),
              ycyl(s, G.RAIL_DX, RY0 - 5, RY0 + 1, 30, 2.75)]
        c += [ins_hole(s, x, G.BLK_YI, G.MOT_Z1, (0, 0, -1)) for x in (G.RAIL_DX - 7, G.RAIL_DX + 7)]
        c += [vcyl(s, 63, y, -1, G.RAIL_Z0 + 1, 2.2) for y in (YC - 15, YC + 20)]                    # M4 to the robot floor
    part("A_SOCLE", solid(a, c), G.RHO_PRINT, PETG, "print", "A")


def platine_moteur():   # v7: clamp plate on the motor's top face AND both rail blocks; the rails pass through it
    z0, z1 = G.MOT_Z1, G.MOT_Z1 + G.SHELF_T
    # 2026-11-10: flush with the socle's rail blocks (same outline, square edges) + the motor's square face in the middle
    a = [box(1, -(G.RAIL_DX + 16), G.RAIL_DX + 16, RY0 - 4, G.BLK_Y1, z0, z1), box(1, -21, 21, YC - 21, G.BLK_Y1, z0, z1)]
    c = [vcyl(1, 0, YC, z0 - 1, z1 + 1, 11.5)]                                                       # boss Ø22 + shaft
    c += [vcyl(1, dx, YC + dy, z0 - 1, z1 + 1, 1.7) for dx in (-15.5, 15.5) for dy in (-15.5, 15.5)]  # 4x M3 into the motor
    for s in (1, -1):
        c.append(box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, RY0 - 0.2, RY1 + 0.2, z0 - 1, z1 + 1))   # the rail passes through
        c += [vcyl(s, x, G.BLK_YI, z0 - 1, z1 + 1, 1.7) for x in (G.RAIL_DX - 7, G.RAIL_DX + 7)]      # 4x M3 into the blocks
    part("A_PLATINE_MOTEUR", solid(a, c), G.RHO_PRINT, PETG, "print", "A")
    # 2026-11-10: no pad (none in stock): the motor hangs from the clamp plate by its 4 screws, 1 mm air gap under it


def haut():
    top = G.RAIL_Z0 + G.RAIL_L
    a = [box(1, -G.RAIL_DX - 14, G.RAIL_DX + 14, RY0 - 4, RY1 + 4, G.TOP_Z0, G.TOP_Z1)]
    c = [vcyl(1, 0, YC, G.TOP_Z0 - 1, top + G.BRG_T, G.BRG_R)]
    for s in (1, -1):
        c += [box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, RY0 - 0.2, RY1 + 0.2, G.TOP_Z0 - 1, top), ycyl(s, G.RAIL_DX, RY0 - 5, RY0 + 1, G.TOP_Z0 + 6, 2.75)]
    part("A_TRAVERSE_HAUT", solid(a, c), G.RHO_PRINT, PETG, "print", "A")


def support_ecrou():    # behind the plate, between the rails. Print: shelf on the bed.
    # 2x M4 x 8 button head through the plate's centre holes: the printer's own (they held the Y belt clamp under this
    # plate), into M4 NUTS in pockets in the wall's back face (2026-11-10: no M4 inserts in stock; wall 8 -> 5 mm so an
    # M4 x 8 goes through plate 3 + skin 1.6 + nut 3.2). 2026-11-10: symmetric,
    # the locating pin in the plate's 3rd hole (x 25.8) is gone (the 2 screws already fix it). T8 nut flange UNDER the shelf: the lift pushes plastic on brass,
    # the 4x M3 only locate it (from below; holes Ø4 in the flange let the nut self-centre on the screw).
    # 2026-11-08: M3 x 10 cut their own thread in Ø2.5 pilot holes through the 6 mm shelf (M3 inserts left only ~0.2 mm
    # of plastic next to the nut-body hole Ø11: heat-setting would push plastic into it). Wall now 1.25 mm.
    top = G.PL_ZC + G.CLAMP_V + 10
    wy0 = G.PL_Y0 - G.SUP_WALL                                                                       # wall 5 thick (was 8)
    a = [chbox(1, -25, 25, wy0, G.PL_Y0, G.NUT_Z, top, 2), chbox(1, -25, 25, YC - 13, wy0 + 1, G.NUT_Z, G.NUT_Z + 6, 3)]
    a += [box(s, 19, 25, YC - 11, wy0 + 0.5, G.NUT_Z + 6, top) for s in (1, -1)]
    a += [prism_xz(s, [(19, G.NUT_Z + 6), (19, G.NUT_Z + 14), (11, G.NUT_Z + 6)], YC - 11, wy0 + 0.5) for s in (1, -1)]   # 45 deg gussets
    c = [vcyl(1, 0, YC, G.NUT_Z - 1, G.NUT_Z + 7, 5.5)]                                              # nut body Ø10.2 up through the shelf
    c += [vcyl(1, 8 * math.cos(math.radians(90 * k)), YC + 8 * math.sin(math.radians(90 * k)), G.NUT_Z - 1,   # v7: real nut holes
               G.NUT_Z + 7, 1.25) for k in range(4)]                                                  # Ø2.5 pilot, through
    for bz in (G.PL_ZC - G.CLAMP_V, G.PL_ZC + G.CLAMP_V):
        c.append(ycyl(1, 0, wy0 - 1, G.PL_Y0 + 1, bz, 2.25))                                          # M4 clearance
        c.append(box(1, -3.7, 3.7, wy0 - 0.1, wy0 + 3.4, bz - 4.2, bz + 4.2))                        # M4 nut pocket (back face)
    part("A_SUPPORT_ECROU", solid(a, c), G.RHO_PRINT, PETG, "print", "A")


# ---------------------------------------------------------------- MODULE A: door units
def plate_diag(upper):    # 2026-11-12: the plate wing's diagonal edge (x 45..76), from the real outline: z = a + b * x
    import json
    with open(os.path.join(HERE, "plaque_papillon_reelle.json")) as f:
        pts = [(x, G.PL_ZC + v) for x, v in json.load(f)["outer"] if 45 < x < 76 and abs(v) > 45 and (v > 0) == upper]   # |v| > 45: not the concave outer arc
    n = len(pts)
    mx, mz = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    b = sum((p[0] - mx) * (p[1] - mz) for p in pts) / sum((p[0] - mx) ** 2 for p in pts)
    return mz - b * mx, b


def lock_tooth(s, upper, z_far):   # flat tooth beside the diagonal edge, LOCK_GAP (normal) from it, out to z_far
    a, b = plate_diag(upper)
    dz = G.LOCK_GAP * math.sqrt(1 + b * b) * (1 if upper else -1)
    x0, x1 = G.LOCK_X0, G.LOCK_X1
    loop = [(x0, a + b * x0 + dz), (x1, a + b * x1 + dz), (x1, z_far), (x0, z_far)]
    if not upper:
        loop.reverse()
    return prism_xz(s, loop, G.LOCK_Y0, G.PL_Y1 + 0.1)


def unit_plate_loop():
    return hull([(G.W_X0, G.PL_Y1), (G.W_X1, G.PL_Y1), (G.W_X0, G.PL_Y1 + 10)] + circle(G.PX, G.PY, G.BOSS_R, 40))


def cap_screws():       # 2026-11-10 (option B): cap -> top shelf, 2x M3 on a diagonal, free nuts under the shelf
    return ((103.0, 41.0), (143.0, 57.0))


def spine_loop():       # 2026-11-10: outline of the spine walls (keel + web + back wall + outer wall), one C-section
    return [(G.K_X0, G.PL_Y1), (G.WEB_X0, G.PL_Y1), (G.WEB_X0, G.BWB_Y0), (G.BASE_X, G.BWB_Y0), (G.BASE_X, G.OWB_Y1),
            (G.OWB_X0, G.OWB_Y1), (G.OWB_X0, G.BWB_Y1), (G.K_X1, G.BWB_Y1), (G.K_X1, G.K_Y1), (G.K_X0, G.K_Y1)]


def top_loop():         # outline of the top shelf = outline of the cap: the cap's edges and chamfers continue the body's
    return [(G.K_X0, G.PL_Y1), (G.WEB_X0, G.PL_Y1), (G.WEB_X0, G.BWB_Y0), (G.BASE_X, G.BWB_Y0), (G.BASE_X, G.OWB_Y1),
            (G.OWB_X0, G.OWB_Y1), (G.OWB_X0, G.FRONT_Y), (G.K_X1, G.FRONT_Y), (G.K_X1, G.K_Y1), (G.K_X0, G.K_Y1)]


def rrect(u0, u1, v0, v1, r, n=8):      # rounded rectangle (window outline), corners of radius r
    pts = []
    for cu, cv, a0, a1 in ((u1 - r, v0 + r, -90, 0), (u1 - r, v1 - r, 0, 90), (u0 + r, v1 - r, 90, 180), (u0 + r, v0 + r, 180, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n)
            p = (cu + r * math.cos(a), cv + r * math.sin(a))
            if not pts or math.hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) > 1e-6:
                pts.append(p)
    if math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6:
        pts.pop()
    return pts


def servo_posts(s, a, c):   # 3 ear posts: M3 nut in a hex recess under a 1.6 mm roof, window below to push it in
    zr = G.SV_FLZ - G.POST_ROOF
    zw1 = zr - G.POST_HEX_D
    hw, hexr = G.POST_HEX / 2, G.POST_HEX / math.sqrt(3)
    xo, xi = G.SV_XC + G.SV_EAR, G.SV_XC - G.SV_EAR
    a.append(box(s, xo - 3.8, G.BASE_X, G.BWB_Y1, G.FRONT_Y, G.LOW + G.PT, G.SV_FLZ))         # outer posts (2 ears)
    a.append(box(s, xi - 4.8, xi + 3.8, G.PL_Y1, G.FRONT_Y, G.LOW + G.PT, G.SV_FLZ))           # inner post (ear y 57)
    for hx, dy, opening in ((xo, -5, "out"), (xo, 5, "out"), (xi, 5, "front")):
        y = G.SVY + dy
        if opening == "out":     # outer ears: ONE window for both nuts (2026-11-12: the 3.4 mm wall between them removed),
            if dy < 0:           # open on the robot's side (x 150)
                c.append(box(s, hx - hw, G.BASE_X + 1, y - 3.3, y + 10 + 3.3, zw1 - G.POST_WIN, zw1 + 0.01))
        else:                    # inner ear: the plate and the keel block the sides, window open to the front
            c.append(box(s, hx - hw, hx + hw, y - 3.3, G.FRONT_Y + 1, zw1 - G.POST_WIN, zw1 + 0.01))
        c.append(prism(s, [(hx + hexr * math.cos(math.radians(30 + 60 * k)), y + hexr * math.sin(math.radians(30 + 60 * k)))
                           for k in range(6)], zw1 - 0.01, zr))
        c.append(vcyl(s, hx, y, zw1 - 1, G.SV_FLZ + 0.1, 1.7))
    # ear openings, both ends: from the ear up to just under the gears (z 77..95.4), open to the front (the servo slides
    # in) and, for the outer ears, on the robot's side too: fingers to start the screws, a hex key at an angle
    zs1 = G.GZA - 1.0
    c.append(box(s, G.SV_X1 - 1, G.BASE_X + 1, G.BWB_Y1 + 3, G.FRONT_Y + 1, G.SV_FLZ - 0.1, zs1))
    # 2026-11-12: the outer ear tip reaches x 148 (1 mm into the outer wall): a groove at ear height through the 5 mm
    # strip in front of the opening, so the servo still slides in from the front (1.4 mm of wall stays outside it)
    c.append(box(s, G.OWB_X0 - 0.1, G.BASE_X - 1.4, G.BWB_Y1 + 3, G.OWB_Y1 + 1, G.SV_FLZ - 0.1, G.SV_FLZ + 2.4 + 0.5))
    # inner ear: 4.5 mm flange entry (full depth) + an opening 15 tall around the screw, open to the front (hand + key);
    # behind it the web stays whole and gets a rib (see aile)
    xi, yi = G.SV_XC - G.SV_EAR, G.SVY + 5
    c.append(box(s, 93.0, G.SV_X0 + 0.2, G.BWB_Y1 + 3, G.FRONT_Y + 1, G.SV_FLZ - 0.1, G.SV_FLZ + 4.5))
    c.append(box(s, xi - 4.0, G.SV_X0 + 0.2, yi - 4.0, G.FRONT_Y + 1, G.SV_FLZ - 0.1, G.SV_FLZ + G.EAR_IN_H))


def m4_plate(s, c, z):      # M4 from behind the plate (head on the plate's back), slot ±1.5 in x, nut free on the front face
    for d in (-1.5, 1.5):
        c.append(ycyl(s, G.SPRING_U + d, G.PL_Y1 - 1, G.K_Y1 + 1, z, 2.25))
    c.append(box(s, G.SPRING_U - 1.5, G.SPRING_U + 1.5, G.PL_Y1 - 1, G.K_Y1 + 1, z - 2.25, z + 2.25))
    # nut pocket in the front face (M4 nut 7 AF x 3.2), keeps the ±1.5 slide
    c.append(box(s, G.SPRING_U - 4.2 - 1.5, G.SPRING_U + 4.2 + 1.5, G.K_Y1 - 3.6, G.K_Y1 + 0.1, z - 3.7, z + 3.7))


def aile(s, name):
    # 2026-11-10 OPTION B (mechanical/concepts/aile-redesign): C-section spine, 3 mm walls, printed upright, no support.
    #  keel on the plate (both M4 rows: bottom one here, top one in the cap) + web + back wall behind the servo + outer
    #  wall; bottom shelf (bottom 608 + servo floor), top shelf (cap screws). Front open: gears visible, servo slides in.
    #  Big windows with rounded corners (flat top <= 20 mm bridge). No inserts: every screw has a free or pocketed nut.
    a, c = [], []
    zb, zp, top = G.LOW - 3, G.LOW + G.PT, G.UP
    # walls: ONE outline (keel + web + back wall + outer wall), 1 mm chamfer on the outside corners, small fillet on
    # the inside ones; the top shelf and the cap use the same outline so their edges and chamfers line up
    a.append(prism(s, chamfer_loop(spine_loop(), 1.0), zb, top))
    # shelves
    base = hull([(G.K_X0, G.PL_Y1), (G.K_X0, G.K_Y1), (G.WEB_X0, G.BWB_Y0), (G.BASE_X, G.BWB_Y0), (G.BASE_X, G.OWB_Y1)]
                + circle(G.PX, G.PY, G.BOSS_R, 40))
    a.append(prism(s, chamfer_loop(base, 1.0), zb, zp))                                                 # bottom shelf
    a.append(prism(s, chamfer_loop(top_loop(), 1.0), G.TSH_Z0, top))                                   # top shelf
    # web 1.5 mm thicker (x 99 -> 100.5) beside the inner ear opening; 2026-11-12: over the full height (it was a local
    # rib z 57..107 with steps at its ends), so the inner face is one flat face
    a.append(box(s, G.K_X1 - 0.1, G.SV_X0 - 0.3, G.BWB_Y1 - 0.1, G.SVY + 1, zb, top))
    a.append(lock_tooth(s, False, zb))                                                                   # 2026-11-12: plate form lock
    servo_posts(s, a, c)
    # bottom 608 seat + rod passage
    c.append(vcyl(s, G.PX, G.PY, zp - G.BRG_T, zp + 0.1, G.BRG_R))
    c.append(lead_in(s, G.PX, G.PY, zp, G.BRG_R, True))
    c.append(vcyl(s, G.PX, G.PY, zb - 1, zp + 1, 5.0))
    # windows: keel (between the two M4 rows), back wall, outer wall
    # 2026-11-12: 71..91 -> 71..87: 5.5 mm of keel (was 1.5) beside the inner ear key opening
    c.append(prism_xz(s, rrect(71, 87, 82, 208, 7.9), G.PL_Y1 - 1, G.K_Y1 + 1))
    c.append(prism_xz(s, rrect(101, 143, G.WIN_Z0, G.WIN_Z1, 12), G.BWB_Y0 - 1, G.BWB_Y1 + 1))
    c.append(prism_yz(s, rrect(G.BWB_Y1 + 3, G.OWB_Y1 - 6, G.WIN_Z0, G.WIN_Z1, 9.9), G.OWB_X0 - 1, G.BASE_X + 1))
    # bottom plate M4 + cap screws through the top shelf (free nuts under it)
    m4_plate(s, c, G.PL_ZC - G.SPRING_V)
    c.append(ins_hole(s, G.CTAB_SCR[0], G.K_Y1, G.CTAB_SCR[1], (0, -1, 0)))                             # 2026-11-12: cap tab insert
    for x, y in cap_screws():
        c.append(vcyl(s, x, y, G.TSH_Z0 - 1, top + 1, 1.7))
        c.append(box(s, x - G.CLAMP_NUT_L / 2, x + G.CLAMP_NUT_L / 2, y - G.CLAMP_NUT_W / 2, y + G.CLAMP_NUT_W / 2,
                     G.TSH_Z0 - 0.1, G.TSH_Z0 + G.NUT_T))                                              # nut pocket under the shelf
    # servo cable straight out at the grommet height: channel in the posts open to the front (the servo slides in), but
    # through the outer wall only a grommet-size hole (2026-11-10: the full-width slot left a 2 mm strip at the front);
    # thread the connector through it before sliding the servo in
    zc0, zc1 = G.SV_BOT + G.CAB_Z0 - 0.6, G.SV_BOT + G.CAB_Z1 + 0.6
    c.append(box(s, G.SV_X1 - 0.5, G.OWB_X0 + 0.01, G.SVY - 4.3, G.FRONT_Y + 1, zc0, zc1))
    c.append(box(s, G.OWB_X0 - 0.1, G.BASE_X + 1, G.SVY - 4.5, G.SVY + 4.5, zc0, zc1))
    part(name, solid(a, c), G.RHO_PRINT, PETG2, "print", "A")


def bride_servo(s, name):    # strap over the door servo body: 2x M3 into the post tops, ring around the output shaft
    ztop = G.SV_BOT + G.SV_H
    xa, xb = G.SV_XC - G.SV_EAR, G.SV_XC + G.SV_EAR
    a = [box(s, G.W_X1 + 0.1, xb + 3.8, G.SVY - 6, G.SVY + 6, ztop, ztop + 3), vcyl(s, G.PX, G.SVY, ztop, ztop + 3, 10.5)]
    c = [vcyl(s, G.PX, G.SVY, ztop - 1, ztop + 5, 7.3),                                            # output boss Ø13.2 passes
         box(s, G.PX - 24.5, G.PX - 8.1, G.SVY - 9.5, G.SVY + 9.5, ztop - 1, ztop + 1.4)]              # pocket: the case's label pad (+1.1)
    c += [zslot(s, x, G.SVY, ztop - 1, ztop + 5, 1.7, dx=1.0) for x in (xa, xb)]                   # lumiere ±1 in x
    part(name, solid(a, c), G.RHO_PRINT, PETG, "print", "A")


def capot_aile(s, name):    # 2026-11-10 (option B): cap z 226..242 = top pod: top 608 + top plate M4 + 2 screws to the spine
    # Printed upside down (top face on the bed): the pockets and the 608 seat open upward, no support. 3 mm skins.
    a = [prism(s, chamfer_loop(top_loop(), 1.0), G.UP, G.CAP_Z1),                                       # = the body's top outline
         prism(s, chamfer_loop(hull([(112, 50), (G.BASE_X, 50), (G.BASE_X, G.OWB_Y1)] + circle(G.PX, G.PY, G.BOSS_R, 40)), 1.0), G.UP, G.CAP_Z1)]
    c = [vcyl(s, G.PX, G.PY, G.UP - 0.1, G.UP + G.BRG_T, G.BRG_R), lead_in(s, G.PX, G.PY, G.UP, G.BRG_R, False),
         vcyl(s, G.PX, G.PY, G.UP, G.CAP_Z1 + 1, 5.0)]
    c.append(box(s, 115, 137, G.BWB_Y1 + 3, G.FRONT_Y, G.UP - 0.1, G.CAP_Z1 - 3))                       # pocket (3 mm skins)
    zs = G.CAP_Z1 - 9.6                                                                                  # screw head seat (M3 x 16)
    for x, y in cap_screws():
        c += [vcyl(s, x, y, G.UP - 1, G.CAP_Z1 + 1, 1.7), vcyl(s, x, y, zs, G.CAP_Z1 + 1, 3.3)]
    m4_plate(s, c, G.PL_ZC + G.SPRING_V)                                                                 # top plate M4, nut on the front face
    # 2026-11-12: front tab over the keel (M3 x 10 into the body's insert; head on the tab) + top plate-lock tooth
    # the tab runs up the cap's whole front face (z 210..242, on the bed when printed) and sinks 0.5 into the cap: one solid
    a.append(chbox(s, G.CTAB_X0, G.CTAB_X1, G.K_Y1, G.K_Y1 + G.CTAB_T, G.CTAB_Z0, G.CAP_Z1, 1.0))
    a.append(box(s, G.CTAB_X0 + 1.0, G.CTAB_X1 - 1.0, G.K_Y1 - 0.5, G.K_Y1 + 0.1, G.UP, G.CAP_Z1))
    c.append(ycyl(s, G.CTAB_SCR[0], G.K_Y1 - 0.1, G.K_Y1 + G.CTAB_T + 1, G.CTAB_SCR[1], 1.7))
    a.append(lock_tooth(s, True, G.CAP_Z1))
    part(name, solid(a, c), G.RHO_PRINT, PETG2, "print", "A")


def arm_screws_z(arm):   # 2026-11-10: door sheet screws, one under and one over the arm
    return (arm[0] - G.ARM_SC, arm[1] + G.ARM_SC)


def bras(s, name, arm, fl):
    hub = circle(G.PX, G.PY, 11, 48)
    fy1 = G.BOX_Y0 - 3.5                                                                             # +3 deg clamp swings it ~1.2 mm forward
    flp = [(G.SX0 - 12, G.TAB_Y0), (G.SX0, G.TAB_Y0), (G.SX0, fy1), (G.SX0 - 12, fy1)]
    z0, z1 = arm
    a = [prism(s, hull(hub + flp), z0, z1), box(s, G.SX0 - G.TAB_D, G.SX0, G.TAB_Y0, fy1, fl[0], fl[1])]
    ca, cc = split_clamp_z(s, G.PX, G.PY, z0, z1, [(z0 + z1) / 2], cb_ext=20, nut_ext=8)   # key, screw and nut can get in
    a += ca
    c = cc + [vcyl(s, G.PX, G.PY, z0 - 1, z1 + 1, G.ROD_R)]
    # 2026-11-10: door sheet screws M3 x 16 + plain nut on the tab's inner face, 7 mm above / below the arm (free air)
    for z in arm_screws_z(arm):
        c.append(xcyl(s, G.SX0 - G.TAB_D - 1, G.SX0 + 0.1, (G.TAB_Y0 + fy1) / 2, z, 1.7))
    part(name, solid(a, c), G.RHO_PRINT, PETG, "print", "A")


def hub28_screws_z():    # 2026-11-10: 11 apart (the 2 nut pockets overlapped at 6): 2.2 mm of plastic above the gear,
    return (G.GZB + 5.5, G.GZB + 16.5)                   # 4.1 between the pockets, 2.2 at the top (hub 22)


def roue_porte():
    hz1 = G.GZB + G.HUB28_H
    a = [prism(1, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.PY, G.GZB, hz1, 10)]
    ca, cc = split_clamp_z(1, G.PX, G.PY, G.GZB, hz1, hub28_screws_z(), lug_dir=1, nut_ext=4, cb_ext=6)   # 2026-11-10: nut pocket + head hole cut out through the Ø20 hub
    a += ca
    part("A_ROUE_PORTE_28T", solid(a, cc + [vcyl(1, G.PX, G.PY, G.GZA - 1, hz1 + 1, G.ROD_R)]), G.RHO_PRINT, PETG2, "print", "A")


def pignon_porte():
    a = [prism(1, gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R + 3)]
    c = [vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T - 1, G.GZA, G.HORN_R + 0.3), vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2),
         vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZA + G.HORN_BOSS_T + 0.5, G.HORN_BOSS_R + 0.3)]
    c += [vcyl(1, G.PX + G.HORN_HOLE_R * math.cos(math.pi / 2 * k), G.SVY + G.HORN_HOLE_R * math.sin(math.pi / 2 * k), G.GZA - 1, G.GZB + 1, G.HORN_SCR_R) for k in range(4)]   # v7: M2 clearance
    part("A_PIGNON_PORTE_20T", solid(a, c), G.RHO_PRINT, PETG2, "print", "A")


def entretoises():   # printed spacers: they touch only the 608 INNER races (Ø12), so nothing rubs on the outer race
    lo0, lo1 = G.LOW + G.PT, G.ARM1[0]                  # bottom: 608 top face -> arm BAS (3 mm)
    hi0, hi1 = G.ARM2[1], G.UP                          # top: arm HAUT -> 608 in the cap (4 mm)
    for name, z0, z1 in (("A_ENTRETOISE_608_BAS", lo0, lo1), ("A_ENTRETOISE_608_HAUT", hi0, hi1)):
        part(name, solid([vcyl(1, G.PX, G.PY, z0, z1, 6.0)], [vcyl(1, G.PX, G.PY, z0 - 1, z1 + 1, 4.15)]), G.RHO_PRINT, PETG, "print", "A")
    # head: sleeve between the 2 outer races in the bracket tube (sets the front 608 flush with the tube)
    part("B_ENTRETOISE_TETE", solid([ycyl(1, 0, G.HBR_Y0 + 7, G.HB_Y1 - 7, G.HZ, 11.0)], [ycyl(1, 0, G.HBR_Y0 + 6, G.HB_Y1 - 6, G.HZ, 8.5)]),
         G.RHO_PRINT, PETG, "print", "B")


def tole():
    a, c = [box(1, G.SX0, G.SX1, G.SY0, G.SY1, G.DZ0, G.DZ1)], []
    for (f0, f1), arm in ((G.FL1, G.ARM1), (G.FL2, G.ARM2)):
        a.append(box(1, G.SX0, G.SX1, G.TAB_Y0, G.SY0, f0, f1))
        for z in arm_screws_z(arm):                                                                   # lumiere ±1.5 in y: set the pad
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
        a.append(chbox(1, hx - 3.8, hx + 3.8, G.PL_Y1, G.HS_FL_Y, G.HS_Z - 11, G.HS_Z + 11, 0.5))   # 2026-11-08: c 0.5 (insert wall)
    c = [ycyl(1, 0, G.HBR_Y0, G.HB_Y1 + 1, hz, G.BRG_R),                                              # both 608 slide in from the front
         Part.makeCone(G.BRG_R, G.BRG_R + 0.6, 0.61, Vector(0, G.HB_Y1 - 0.6, hz), Vector(0, 1, 0)),
         # head servo cable: it leaves the shaft-end face (+x end, x -3.2), centred, at the bottom = next to the plate.
         # The servo window is extended past that end, then an L slot runs down to the bracket's bottom edge (lay the
         # cable in from the front); 2 zip-tie holes beside it open into the plate's centre notch.
         box(1, G.HS_SVX1 - 0.5, G.HS_SVX1 + 14, G.PL_Y1 - 1, G.PL_Y1 + 10, G.HS_Z - 5.5, G.HS_Z + 5.5),
         # v6: cable straight out (+x), then UP in a groove in the bracket front, to the tube passage (z 200+)
         box(1, G.HS_SVX1 + 13, G.HCAB_X + 3, G.PL_Y1 + 4, G.PL_Y1 + 8, G.HS_Z - 3.5, G.HS_Z + 3.5),
         box(1, G.HCAB_X - 3, G.HCAB_X + 3, G.PL_Y1 + 4, G.PL_Y1 + 8, G.HS_Z - 3.5, 201),
         ycyl(1, 0, G.HB_Y0 - 1, G.HB_Y1 + 1, hz, 5.0)]
    c.append(box(1, G.HS_SVX0 - 1.5, G.HS_SVX1 + 0.6, G.PL_Y1 - 1, G.PL_Y1 + 7, G.HS_Z - G.SV_W / 2 - 1, G.HS_Z + G.SV_W / 2 + 1))   # window: servo body
    for bz in (G.PL_ZC - G.CLAMP_V, G.PL_ZC + G.CLAMP_V):                                              # pockets: module A's M4 button heads
        c.append(ycyl(1, 0, G.PL_Y1 - 1, G.PL_Y1 + 2.6, bz, 4.2))                                       # (Ø7.6 x 2.2)
    for sx in (1, -1):
        for dz in (-G.WH_DZ, G.WH_DZ):
            c.append(ycyl(1, sx * G.WH_X, G.PL_Y1 - 1, G.PL_Y1 + 7, G.PL_ZC + dz, 2.75))
    # 2026-11-08: M3 inserts in the post tops (as the door units); the side-entry nut pockets had 0.5-0.8 mm walls.
    # The ±1.5 mesh slots are gone: the mesh relies on the printed centre distance (+ the play of the ear holes).
    for hx in (G.HS_SVXC - G.SV_EAR, G.HS_SVXC + G.SV_EAR):
        for dz in (-5, 5):
            c.append(ins_hole(1, hx, G.HS_FL_Y, G.HS_Z + dz, (0, -1, 0)))
    part("B_SUPPORT_TETE", solid(a, c), G.RHO_PRINT, PETG, "print", "B")


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
         xcyl(1, -7, 7, (G.HC_Y0 + G.HC_Y1) / 2, hz + 9.5, 1.7), xcyl(1, -9, -4.5, (G.HC_Y0 + G.HC_Y1) / 2, hz + 9.5, 3.0),
         box(1, 6 - G.NUT_T, 6 + 0.01, G.HC_Y0 - 1, G.HC_Y1 + 0.01, hz + 9.5 - 2.8, hz + 9.5 + 2.8),
         ycyl(1, 0, G.HF_Y1 - 3, G.HF_Y1 + 1, hz, 10)]                                              # room for the TPU hub to move back
    for ang in G.ST_BOLT_A:
        t = math.radians(ang)
        x, z = G.ST_BOLT_R * math.cos(t), hz + G.ST_BOLT_R * math.sin(t)
        c += [ycyl(1, x, G.HF_Y0 - 1, G.HF_Y1 + 1, z, 1.7), prism_y(circle(x, z, 3.25, 6), G.HF_Y0 - 1, G.HF_Y0 + 2.6)]
    part("B_MOYEU_TETE_30T", solid(a, c), G.RHO_PRINT, PETG2, "print", "B")


def tete_pignon():      # 20T on the head MG996R horn (horn in a pocket at the rear)
    ang_to_head = math.degrees(math.atan2(G.HZ - G.HS_Z, -G.HS_X))
    y0 = G.HS_HORN_Y                                                        # v6: sits on the real horn's disc, centred by its boss
    a = [prism_y(gear(G.HS_X, G.HS_Z, G.GM, G.HGZ1, ang_to_head, 0.15), y0, G.HG_Y1)]
    c = [ycyl(1, G.HS_X, y0 - 1, G.HG_Y1 + 1, G.HS_Z, 3.2), ycyl(1, G.HS_X, y0 - 1, y0 + G.HORN_BOSS_T + 0.5, G.HS_Z, G.HORN_BOSS_R + 0.3)]
    c += [ycyl(1, G.HS_X + G.HORN_HOLE_R * math.cos(math.pi / 2 * k), y0 - 1, G.HG_Y1 + 1, G.HS_Z + G.HORN_HOLE_R * math.sin(math.pi / 2 * k), 1.1) for k in range(4)]
    c += [ycyl(1, G.HS_X + G.HORN_HOLE_R * math.cos(math.pi / 2 * k), G.HG_Y1 - 1.5, G.HG_Y1 + 1, G.HS_Z + G.HORN_HOLE_R * math.sin(math.pi / 2 * k), 2.2)
          for k in range(4)]                                                                   # v7: M2 heads below the face
    part("B_PIGNON_TETE_20T", solid(a, c), G.RHO_PRINT, PETG2, "print", "B")


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
    part("B_BAGUE_STATION", solid(a, c), G.RHO_PRINT, PETG, "print", "B")


# ---------------------------------------------------------------- references + reserved space
def refs():
    # v7: real Two Trees Bluer V2 parts (see ../../resources/two-trees-bluer-v2-parts/SOURCE.md)
    def tt(name):
        return Part.read(os.path.join(G.TT_DIR, name + ".step"))
    def tt_axis(shape, y_ref, z_ref):           # Y-axis parts: printer y along the rails -> module z
        m = App.Matrix(-1, 0, 0, G.TT_X0, 0, 0, 1, G.RAIL_YC - G.TT_ZR, 0, 1, 0, z_ref - y_ref, 0, 0, 0, 1)
        sh = shape.copy(); sh.transformShape(m)
        return Part.makeCompound(sh.Solids)
    part("REF_RAILS_2020", tt_axis(tt("rails_2020_Y"), G.TT_YR0, G.RAIL_Z0), 2700, DARK, "ref", "A")
    # the REAL butterfly plate (Two Trees Bluer V2 heatbed base, "Product 298"), outline + holes read from the .3dm
    # (fc/plaque_papillon_reelle.json, centre = wheel pattern). Mounted with its 3rd hole at +x, eccentric wheels at +x.
    import json
    with open(os.path.join(HERE, "plaque_papillon_reelle.json")) as f:
        pl = json.load(f)
    y0, y1, cz = G.PL_Y0, G.PL_Y1, G.PL_ZC
    a = [prism_xz(1, [(x, cz + z) for x, z in pl["outer"]], y0, y1)]
    c = [ycyl(1, x, y0 - 1, y1 + 1, cz + z, d / 2) for x, z, d in pl["holes"]]
    part("REF_PLAQUE_PAPILLON", solid(a, c), 2700, DARK, "ref", "A")
    # (butterfly_plate.step is B-spline only, no true holes: the exact plate above is kept)
    for name, f in (("REF_ROUES_V", "v_wheels_Y"), ("REF_ENTRETOISES_M5", "m5_spacers_Y"),
                    ("REF_ENTRETOISES_EXC", "eccentric_spacers_Y"), ("REF_RONDELLES_BRONZE", "bronze_washers_Y")):
        part(name, tt_axis(tt(f), G.TT_YW, G.PL_ZC), 2700, DARK, "ref", "A")
    # (the printer's M5 wheel screws + nyloc nuts are not used: ours are longer, through the head bracket -> fasteners)
    part("REF_608ZZ", solid([vcyl(1, G.PX, G.PY, G.LOW + G.PT - 7, G.LOW + G.PT, 11)], [vcyl(1, G.PX, G.PY, 0, 400, 4)]), 7850, STEEL, "ref", "A")
    part("REF_608ZZ_TETE", solid([ycyl(1, 0, G.HBR_Y0, G.HBR_Y0 + 7, G.HZ, 11)], [ycyl(1, 0, 0, 200, G.HZ, 4)]), 7850, STEEL, "ref", "B")
    mot = tt("nema17")                                                       # v7: real motor, body top on the shelf
    bot = min(f.BoundBox.ZMin for f in mot.Faces if f.Area > 1000 and f.BoundBox.ZLength < 1e-6)
    mot.translate(Vector(-G.TT_ZAX[0], YC - G.TT_ZAX[1], G.MOT_PAD - bot))                  # v7: standing on its pad
    part("REF_NEMA17", Part.makeCompound(mot.Solids), 3500, DARK, "ref", "A")
    cpl = tt("coupler_5x8")
    cpl.translate(Vector(-G.TT_ZAX[0], YC - G.TT_ZAX[1], G.CPL_Z0 - G.TT_CPL_Z0))
    part("REF_COUPLEUR_5x8", Part.makeCompound(cpl.Solids), 2700, ALU, "ref", "A")
    part("REF_VIS_T8", vcyl(1, 0, YC, G.SCREW_Z0, G.SCREW_Z1, 4), 7850, STEEL, "ref", "A")
    nut = tt("lead_nut_TR8x8")                                               # v7: real nut, flipped: long body up, flange under the shelf
    nut.transformShape(App.Matrix(1, 0, 0, -G.TT_ZAX[0], 0, -1, 0, G.TT_ZAX[1] + YC, 0, 0, -1, G.NUT_Z + G.TT_NUT_FL, 0, 0, 0, 1))
    part("REF_ECROU_T8", Part.makeCompound(nut.Solids), 8500, BRASS, "ref", "A")
    part("REF_TIGE_PORTE_D8", vcyl(1, G.PX, G.PY, G.ROD_Z0, G.ROD_Z1, 4), 7850, STEEL, "ref", "A")
    part("REF_AXE_TETE_D8", ycyl(1, 0, G.HBR_Y0 + 0.5, G.HF_Y0 + 1.5, G.HZ, 4), 7850, STEEL, "ref", "B")
    part("REF_MOUSSE_PORTE", box(1, G.PAD_X0, G.SX0, G.PAD_Y0, G.PAD_Y1, G.PADS_Z[0][0], G.PADS_Z[0][1]), 50, FOAM, "ref", "A")
    # MG996R = the real model (body, shaft, screws, cable grommet; its straight wire stub is replaced by the routed cable)
    raw = Part.read(G.SV_STEP)
    horn = Part.read(G.HORN_STEP)
    horn.translate(Vector(0, 0, G.SV_HORN - G.HORN_T - 28))                 # seated on the spline (hub 0.2 above the body)
    sv = Part.makeCompound(raw.Solids[:8] + horn.Solids)                    # v6: real horn added
    # v6: the real GrabCAD wires (3 x Ø1.4, straight out of the grommet), trimmed at the grommet face (x 16) so they
    # don't overlap it; one part per wire so each gets its colour
    trim = Part.makeBox(20, 20, 20, Vector(16.0, -10, -32))
    wires = [("BRUN", raw.Solids[10].common(trim)), ("ROUGE", raw.Solids[8].common(trim)), ("ORANGE", raw.Solids[9].common(trim))]
    for s, tag in ((1, "D"), (-1, "G")):
        def place(shape):
            sh = shape.copy()
            if s < 0:
                sh.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 180)
            sh.translate(Vector(s * G.PX, G.SVY, G.SV_BOT + 28))
            return Part.makeCompound(sh.Solids)                             # bake the placement into the solids
        part("REF_MG996R_" + tag, place(sv), 1200, SERVO, "ref", "A")
        for col, w in wires:
            part("REF_FIL_%s_%s" % (col, tag), place(w), 1500, SERVO, "ref", "A")
    def place_h(shape):                                                     # head servo: top -> +y
        sh = shape.copy()
        sh.rotate(Vector(0, 0, 0), Vector(1, 0, 0), -90)
        sh.translate(Vector(G.HS_X, G.HS_BODY_Y0 + 28, G.HS_Z))
        return Part.makeCompound(sh.Solids)
    part("REF_MG996R_TETE", place_h(sv), 1200, SERVO, "ref", "B")
    wy = G.HS_BODY_Y0 + 28 - 22.0                                           # wire axis y (servo z -22)
    for (col, w), dz in zip(wires, (1.4, 0.0, -1.4)):                       # servo y -> world -z
        stub = place_h(w)
        x0, z = G.HS_X + 22.6, G.HS_Z + dz
        xc = G.HCAB_X - dz                                                  # top wire turns first: no crossing
        run = [Part.makeCylinder(0.7, xc - x0, Vector(x0, wy, z), Vector(1, 0, 0)), Part.makeSphere(0.7, Vector(xc, wy, z)),
               Part.makeCylinder(0.7, G.HCAB_Z1 - z, Vector(xc, wy, z), Vector(0, 0, 1))]
        part("REF_FIL_%s_TETE" % col, Part.makeCompound(stub.Solids + run), 1500, SERVO, "ref", "B")
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
# =============================================================================================== v7: fasteners
# Every screw, nut and insert, at its real place (ISO sizes, no threads). Parts FIX_VIS_* (screws, dark), FIX_ECROU_*
# (nuts, silver), FIX_INSERT_* (heat-set inserts, brass; modelled at the hole size), FIX_TNUT_*. Bill of materials in
# report.txt. Each FIX part carries its own count; placements() adds them (FIXP).
FIXP = []
FBOM = {}
HEADS = {("BH", 3): (5.7, 1.65), ("BH", 4): (7.6, 2.2), ("BH", 5): (9.5, 2.75),
         ("SH", 3): (5.5, 3.0), ("SH", 4): (7.0, 4.0), ("SH", 5): (8.5, 5.0), ("PAN", 2): (3.8, 1.3)}
HNAME = {"BH": "button head (ISO 7380)", "SH": "socket head (ISO 4762)", "PAN": "pan head self-tapping (servo horn)"}
NUTS = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0)}
INSERTS = {3: (4.6, 6.0), 4: (5.6, 6.0)}   # modelled at the hole Ø; M3 length 6.0 measured 2026-11-09


def _put(sh, p, d, spin=0.0):
    r = App.Rotation(Vector(0, 0, 1), Vector(*d))
    if spin:
        r = r.multiply(App.Rotation(Vector(0, 0, 1), spin))
    sh = sh.copy()
    sh.transformShape(App.Placement(Vector(*p), r).toMatrix())
    return sh


def f_screw(head, d, L, p, dirv):      # p = head bearing face, dirv = direction of the shank
    dk, k = HEADS[(head, d)]
    ds = d - 0.1                                    # real thread major diameter is just under nominal
    sol = [Part.makeCylinder(ds / 2, L - 0.3), Part.makeCone(ds / 2, ds / 2 - 0.3, 0.3, Vector(0, 0, L - 0.3))]
    if head == "BH":
        sol += [Part.makeCylinder(dk / 2, 0.4 * k, Vector(0, 0, -0.4 * k)),
                Part.makeCone(dk / 2, dk * 0.3, 0.6 * k, Vector(0, 0, -0.4 * k), Vector(0, 0, -1))]
    else:
        sol += [Part.makeCylinder(dk / 2, k, Vector(0, 0, -k))]
    return _put(Part.makeCompound(sol), p, dirv)


def f_nut(d, p, axis, spin=0.0, nyloc=False):
    af, h = NUTS[d]
    if nyloc:
        h = 5.0
    rc = af / math.sqrt(3)
    hexp = Part.Face(Part.makePolygon([Vector(rc * math.cos(math.radians(60 * k)), rc * math.sin(math.radians(60 * k)), -h / 2) for k in range(7)]))
    sh = hexp.extrude(Vector(0, 0, h)).cut(Part.makeCylinder(d / 2, h + 2, Vector(0, 0, -h / 2 - 1)))
    return _put(sh, p, axis, spin)


def f_insert(d, p, dirv):              # p = flush face, dirv = into the part
    od, L = INSERTS[d]
    sh = Part.makeCylinder(od / 2, L).cut(Part.makeCylinder(d / 2, L + 2, Vector(0, 0, -1)))
    return _put(sh, p, dirv)


def fix(name, shapes, bom, places, module):
    """One FIX part (all its shapes share a colour), with its BOM per placement, placed at each (dx, dy, dz, group)."""
    part(name, Part.makeCompound(shapes), 7850, STEEL, "ref", module)
    FBOM[name] = bom
    for dx, dy, dz, grp in places:
        FIXP.append((name, dx, dy, dz, grp))


def fasteners():
    L = -2 * G.PX
    s3, b3 = "M3 x %d " + HNAME["SH"], "M3 x %d " + HNAME["BH"]
    N3, I3 = "M3 nut (ISO 4032)", "M3 heat-set insert (hole dia 4.6 x 7 + 0.5 chamfer)"
    for s, tag in ((1, "D"), (-1, "G")):
        # ---- door unit (option B, 2026-11-10): servo flange 3x M3 x 8 + nut under the post roof; cap 2x M3 x 16 + nut in
        # a pocket under the top shelf; plate corners 2x M4 x 16 from behind the plate + nut in a pocket in the keel / cap front face
        sv = [(G.SV_XC + G.SV_EAR, -5), (G.SV_XC + G.SV_EAR, 5), (G.SV_XC - G.SV_EAR, 5)]
        vis = [f_screw("BH", 3, 8, (s * x, G.SVY + dy, G.SV_FLZ + 2.4), (0, 0, -1)) for x, dy in sv]
        zn = G.SV_FLZ - G.POST_ROOF - 1.2                                         # 2026-11-10: nut pushed up against the roof
        nuts = [f_nut(3, (s * x, G.SVY + dy, zn), (0, 0, 1), 30) for x, dy in sv]
        vis += [f_screw("BH", 3, 16, (s * x, y, G.CAP_Z1 - 9.6), (0, 0, -1)) for x, y in cap_screws()]
        vis.append(f_screw("BH", 3, 10, (s * G.CTAB_SCR[0], G.K_Y1 + G.CTAB_T, G.CTAB_SCR[1]), (0, -1, 0)))   # 2026-11-12: cap tab
        nuts += [f_nut(3, (s * x, y, G.TSH_Z0 + 1.4), (0, 0, 1)) for x, y in cap_screws()]           # in its pocket
        corners = (G.PL_ZC - G.SPRING_V, G.PL_ZC + G.SPRING_V)
        vis += [f_screw("BH", 4, 16, (s * G.SPRING_U, G.PL_Y0, bz), (0, 1, 0)) for bz in corners]
        nuts += [f_nut(4, (s * G.SPRING_U, G.K_Y1 - 1.8, bz), (0, 1, 0)) for bz in corners]            # in its pocket
        fix("FIX_VIS_AILE_" + tag, vis, {b3 % 8: 3, b3 % 16: 2, b3 % 10: 1, "M4 x 16 " + HNAME["BH"]: 2}, [(0, 0, 0, "carriage")], "A")
        fix("FIX_INSERT_AILE_" + tag, [f_insert(3, (s * G.CTAB_SCR[0], G.K_Y1, G.CTAB_SCR[1]), (0, -1, 0))], {I3: 1}, [(0, 0, 0, "carriage")], "A")
        fix("FIX_ECROU_AILE_" + tag, nuts, {N3: 5, "M4 nut (ISO 4032)": 2}, [(0, 0, 0, "carriage")], "A")
        # ---- arms: split clamp (M3 x 12 socket head + nut) + 2x M3 x 16 through the door sheet + nut on the tab (2026-11-10)
        fy1 = G.BOX_Y0 - 3.5
        ym = (G.TAB_Y0 + fy1) / 2
        vis, nuts, ins = [], [], []
        for (z0, z1), fl in ((G.ARM1, G.FL1), (G.ARM2, G.FL2)):
            zc = (z0 + z1) / 2
            vis.append(f_screw("SH", 3, 12, (s * (G.PX - 4), G.PY - 9, zc), (s, 0, 0)))   # 2026-11-10: x 10 ended inside the nut
            nuts.append(f_nut(3, (s * (G.PX + 4.7), G.PY - 9, zc), (1, 0, 0)))
            for z in arm_screws_z((z0, z1)):
                vis.append(f_screw("BH", 3, 16, (s * G.SX1, ym, z), (-s, 0, 0)))
                nuts.append(f_nut(3, (s * (G.SX0 - G.TAB_D - 1.2), ym, z), (1, 0, 0)))
        fix("FIX_VIS_BRAS_" + tag, vis, {s3 % 12: 2, b3 % 16: 4}, [(0, 0, 0, "door_" + tag)], "A")
        fix("FIX_ECROU_BRAS_" + tag, nuts, {N3: 6}, [(0, 0, 0, "door_" + tag)], "A")
    # ---- 28T split clamp (built on the right, translated to the left like the gear) + door pinion horn screws
    hz1 = G.GZB + G.HUB28_H
    fix("FIX_VIS_ROUE_28T", [f_screw("SH", 3, 12, (G.PX - 4, G.PY + 9, z), (1, 0, 0)) for z in hub28_screws_z()],
        {s3 % 12: 2}, [(0, 0, 0, "door_D"), (L, 0, 0, "door_G")], "A")
    fix("FIX_ECROU_ROUE_28T", [f_nut(3, (G.PX + 4.7, G.PY + 9, z), (1, 0, 0)) for z in hub28_screws_z()],
        {N3: 2}, [(0, 0, 0, "door_D"), (L, 0, 0, "door_G")], "A")
    hr = G.HORN_HOLE_R
    fix("FIX_VIS_PIGNON_PORTE", [f_screw("PAN", 2, 10, (G.PX + hr * math.cos(math.pi / 2 * k), G.SVY + hr * math.sin(math.pi / 2 * k), G.GZB), (0, 0, -1))
                                 for k in range(4)], {"M2 x 10 " + HNAME["PAN"]: 4}, [(0, 0, 0, "pinion_D"), (L, 0, 0, "pinion_G")], "A")
    # ---- lift: nut support (2x M4 x 8 through the plate into M4 nuts in pockets; 4x M3 x 10 through the T8 flange, cutting their
    #      own thread in Ø2.5 pilot holes: 2026-11-08, inserts there left ~0.2 mm of plastic next to the nut-body hole)
    fix("FIX_VIS_PLAQUE_ECROU", [f_screw("BH", 4, 8, (0, G.PL_Y1, G.PL_ZC + d), (0, -1, 0)) for d in (-G.CLAMP_V, G.CLAMP_V)],
        {"M4 x 8 " + HNAME["BH"]: 2}, [(0, 0, 0, "carriage")], "A")          # heads in the head bracket's pockets (allowed)
    nuts4 = [f_nut(4, (0, G.PL_Y0 - G.SUP_WALL + 1.8, G.PL_ZC + d), (0, 1, 0), 90) for d in (-G.CLAMP_V, G.CLAMP_V)]   # in their pockets
    pts = [(8 * math.cos(math.radians(90 * k)), YC + 8 * math.sin(math.radians(90 * k))) for k in range(4)]
    vis = [f_screw("BH", 3, 10, (x, y, G.NUT_Z - 3.9), (0, 0, 1)) for x, y in pts]
    fix("FIX_VIS_SUPPORT_ECROU", vis, {b3 % 10 + ", into a dia 2.5 pilot hole (cuts its own thread)": 4}, [(0, 0, 0, "carriage")], "A")
    fix("FIX_ECROU_SUPPORT_ECROU", nuts4, {"M4 nut (ISO 4032)": 2}, [(0, 0, 0, "carriage")], "A")
    # ---- motor on the socle shelf (4x M3 x 10), rails in the socle and the top tie (M5 x 8 into T-nuts)
    fix("FIX_VIS_MOTEUR", [f_screw("SH", 3, 10, (dx, YC + dy, G.MOT_Z1 + G.SHELF_T), (0, 0, -1)) for dx in (-15.5, 15.5) for dy in (-15.5, 15.5)],
        {s3 % 10: 4}, [(0, 0, 0, "fixed")], "A")
    pb = [(sx * (G.RAIL_DX + dx), G.BLK_YI) for sx in (1, -1) for dx in (-7, 7)]
    fix("FIX_VIS_PLATINE", [f_screw("BH", 3, 12, (x, y, G.MOT_Z1 + G.SHELF_T), (0, 0, -1)) for x, y in pb], {b3 % 12: 4}, [(0, 0, 0, "fixed")], "A")
    fix("FIX_INSERT_SOCLE", [f_insert(3, (x, y, G.MOT_Z1), (0, 0, -1)) for x, y in pb], {I3: 4}, [(0, 0, 0, "fixed")], "A")
    rz = [(sx, z) for sx in (1, -1) for z in (30, G.TOP_Z0 + 6)]
    fix("FIX_VIS_RAILS", [f_screw("BH", 5, 8, (sx * G.RAIL_DX, RY0 - 4, z), (0, 1, 0)) for sx, z in rz],
        {"M5 x 8 " + HNAME["BH"]: 4}, [(0, 0, 0, "fixed")], "A")
    fix("FIX_TNUT_RAILS", [box(1, sx * G.RAIL_DX - 3, sx * G.RAIL_DX + 3, RY0 + 1.8, RY0 + 4.8, z - 5, z + 5).cut(
        ycyl(1, sx * G.RAIL_DX, RY0, RY0 + 6, z, 2.5)) for sx, z in rz],
        {"M5 T-nut for the 2020 slot": 4}, [(0, 0, 0, "fixed")], "A")
    # ---- head bracket: the 4 wheel bolts, longer (M5 x 35 socket head through wheel + spacer + plate + bracket) + nyloc
    yb = PARTS["REF_ROUES_V"][0].BoundBox.YMin
    wb = [(G.TT_X0 - px, G.PL_ZC + py - G.TT_YW) for px in (60.67, 180.67) for py in (252.59, 327.59)]   # real wheel axes
    fix("FIX_VIS_ROUES", [f_screw("SH", 5, 35, (x, yb, z), (0, 1, 0)) for x, z in wb], {"M5 x 35 " + HNAME["SH"]: 4}, [(0, 0, 0, "carriage")], "B")
    fix("FIX_ECROU_ROUES", [f_nut(5, (x, G.PL_Y1 + 6 + 2.5, z), (0, 1, 0), nyloc=True) for x, z in wb],
        {"M5 nyloc nut (ISO 10511)": 4}, [(0, 0, 0, "carriage")], "B")
    # ---- head servo on the bracket posts (4x M3 x 8 into inserts in the post tops; 2026-11-08, were nuts in thin pockets)
    hs = [(hx, G.HS_Z + dz) for hx in (G.HS_SVXC - G.SV_EAR, G.HS_SVXC + G.SV_EAR) for dz in (-5, 5)]
    fix("FIX_VIS_TETE_SERVO", [f_screw("BH", 3, 8, (x, G.HS_FL_Y + 2.4, z), (0, -1, 0)) for x, z in hs], {b3 % 8: 4}, [(0, 0, 0, "carriage")], "B")
    fix("FIX_INSERT_TETE_SERVO", [f_insert(3, (x, G.HS_FL_Y, z), (0, -1, 0)) for x, z in hs], {I3: 4}, [(0, 0, 0, "carriage")], "B")
    # ---- head hub clamp (M3 x 12 socket head + nut), head pinion horn screws (M2 x 6 in counterbores)
    yh = (G.HC_Y0 + G.HC_Y1) / 2
    fix("FIX_VIS_TETE_MOYEU", [f_screw("SH", 3, 12, (-4.5, yh, G.HZ + 9.5), (1, 0, 0))], {s3 % 12: 1}, [(0, 0, 0, "head")], "B")
    fix("FIX_ECROU_TETE_MOYEU", [f_nut(3, (4.7, yh, G.HZ + 9.5), (1, 0, 0), spin=30)], {N3: 1}, [(0, 0, 0, "head")], "B")
    fix("FIX_VIS_TETE_PIGNON", [f_screw("PAN", 2, 6, (G.HS_X + hr * math.cos(math.pi / 2 * k), G.HG_Y1 - 1.5, G.HS_Z + hr * math.sin(math.pi / 2 * k)), (0, -1, 0))
                                for k in range(4)], {"M2 x 6 " + HNAME["PAN"]: 4}, [(0, 0, 0, "hpinion")], "B")
    # ---- cup stations: 3x M3 x 16 each, through ring + TPU rim + carrier; nuts behind the carrier (outer) / in the flange (middle)
    bolts = [(G.ST_BOLT_R * math.cos(math.radians(a)), G.ST_BOLT_R * math.sin(math.radians(a))) for a in G.ST_BOLT_A]
    fix("FIX_VIS_STATION", [f_screw("BH", 3, 16, (x, G.RING_Y1, z), (0, -1, 0)) for x, z in bolts], {b3 % 16: 3},
        [(0, 0, cz, "head") for cz in G.CUPS_Z], "B")
    fix("FIX_ECROU_STATION_EXT", [f_nut(3, (x, G.CA_Y0 - 1.2, z), (0, 1, 0)) for x, z in bolts], {N3: 3},
        [(0, 0, cz, "head") for cz in (G.CUPS_Z[0], G.CUPS_Z[2])], "B")
    fix("FIX_ECROU_STATION_MIL", [f_nut(3, (x, G.HF_Y0 + 1.2, z), (0, 1, 0)) for x, z in bolts], {N3: 3},
        [(0, 0, G.CUPS_Z[1], "head")], "B")


def bom_lines():
    tot = {}
    for name, dx, dy, dz, grp in FIXP:
        for k, n in FBOM[name].items():
            tot[k] = tot.get(k, 0) + n
    tot["M4 x (6 + chassis) " + HNAME["BH"] + ": socle to the robot base, length set by the chassis"] = 4
    return ["", "Fasteners (bill of materials, whole module, both door units):"] + ["  %3d x  %s" % (n, k) for k, n in sorted(tot.items())]


def placements():
    L = -2 * G.PX
    p = [("A_SOCLE", 0, 0, 0, "fixed"), ("A_PLATINE_MOTEUR", 0, 0, 0, "fixed"), ("A_TRAVERSE_HAUT", 0, 0, 0, "fixed"), ("REF_NEMA17", 0, 0, 0, "fixed"),
         ("REF_COUPLEUR_5x8", 0, 0, 0, "fixed"), ("REF_VIS_T8", 0, 0, 0, "fixed"),
         ("REF_608ZZ", -G.PX, YC - G.PY, G.RAIL_Z0 + G.RAIL_L - (G.LOW + G.PT - 7), "fixed"),
         ("REF_RAILS_2020", 0, 0, 0, "fixed"), ("REF_ROUES_V", 0, 0, 0, "carriage"), ("REF_ENTRETOISES_M5", 0, 0, 0, "carriage"),
         ("REF_ENTRETOISES_EXC", 0, 0, 0, "carriage"), ("REF_RONDELLES_BRONZE", 0, 0, 0, "carriage"),
         ("REF_PLAQUE_PAPILLON", 0, 0, 0, "carriage"), ("A_SUPPORT_ECROU", 0, 0, 0, "carriage"), ("REF_ECROU_T8", 0, 0, 0, "carriage"),
         ("A_AILE_D", 0, 0, 0, "carriage"), ("A_AILE_G", 0, 0, 0, "carriage"), ("REF_MG996R_D", 0, 0, 0, "carriage"), ("REF_MG996R_G", 0, 0, 0, "carriage"),
         ("B_SUPPORT_TETE", 0, 0, 0, "carriage"), ("REF_608ZZ_TETE", 0, 0, 0, "carriage"),
         ("REF_608ZZ_TETE", 0, G.HB_Y1 - 7 - G.HBR_Y0, 0, "carriage"), ("B_ENTRETOISE_TETE", 0, 0, 0, "carriage"),
         ("A_CAPOT_AILE_D", 0, 0, 0, "carriage"), ("A_CAPOT_AILE_G", 0, 0, 0, "carriage"),
         ("REF_MG996R_TETE", 0, 0, 0, "carriage"), ("REF_FIL_BRUN_TETE", 0, 0, 0, "carriage"),
         ("REF_FIL_ROUGE_TETE", 0, 0, 0, "carriage"), ("REF_FIL_ORANGE_TETE", 0, 0, 0, "carriage"),
         ("REF_FIL_BRUN_D", 0, 0, 0, "carriage"), ("REF_FIL_ROUGE_D", 0, 0, 0, "carriage"), ("REF_FIL_ORANGE_D", 0, 0, 0, "carriage"),
         ("REF_FIL_BRUN_G", 0, 0, 0, "carriage"), ("REF_FIL_ROUGE_G", 0, 0, 0, "carriage"), ("REF_FIL_ORANGE_G", 0, 0, 0, "carriage"),
         ("B_PIGNON_TETE_20T", 0, 0, 0, "hpinion"),
         ("B_MOYEU_TETE_30T", 0, 0, 0, "head"), ("REF_AXE_TETE_D8", 0, 0, 0, "head"), ("B_PLATEAU_TETE", 0, 0, 0, "head"),
         ("REF_PILE_3_PIERRES", 0, 0, 0, "stack"),
         ("RES_TETE_ROTATION", 0, 0, 0, "reserve"), ("RES_TETE_FIXE", 0, 0, 0, "reserve"), ("RES_TETE_CABLES", 0, 0, 0, "reserve"),
         ("RES_TETE_REPOS", 0, 0, 0, "reserve")]
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
    return p + FIXP


def build_all():
    socle(); platine_moteur(); haut(); support_ecrou(); aile(1, "A_AILE_D"); aile(-1, "A_AILE_G")
    for s, tag in ((1, "D"), (-1, "G")):
        bras(s, "A_BRAS_PORTE_%s_BAS" % tag, G.ARM1, G.FL1)
        bras(s, "A_BRAS_PORTE_%s_HAUT" % tag, G.ARM2, G.FL2)
    roue_porte(); pignon_porte(); tole(); 
    capot_aile(1, "A_CAPOT_AILE_D"); capot_aile(-1, "A_CAPOT_AILE_G")
    entretoises(); tete_support(); tete_moyeu(); tete_pignon(); tete_plateau(); tete_station_tpu(); tete_bague(); refs(); fasteners()


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

    doc = App.newDocument("MODULE_CLAPETS_V7")
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
    clashes, expected = [], []
    # v7: contacts that are real on the hardware (V-wheels in the V-slot, screw in the nut thread / coupler bore)
    EXPECTED = (("REF_RAILS_2020", "REF_ROUES_V"), ("REF_VIS_T8", "REF_ECROU_T8"), ("REF_COUPLEUR_5x8", "REF_VIS_T8"), ("A_SOCLE", "REF_RAILS_2020"),
                ("FIX_VIS_MOTEUR", "REF_NEMA17"), ("REF_ECROU_T8", "FIX_VIS_SUPPORT_ECROU"), ("FIX_VIS_SUPPORT_ECROU", "A_SUPPORT_ECROU"), ("FIX_VIS_PIGNON_PORTE", "REF_MG996R_D"),
                ("FIX_VIS_PIGNON_PORTE", "REF_MG996R_G"), ("FIX_VIS_TETE_PIGNON", "REF_MG996R_TETE"), ("FIX_TNUT_RAILS", "REF_RAILS_2020"), ("FIX_VIS_RAILS", "REF_RAILS_2020"))
    for i in range(len(real)):
        for j in range(i + 1, len(real)):
            si, sj = real[i].Shape, real[j].Shape
            if si.BoundBox.intersect(sj.BoundBox):
                v = si.common(sj).Volume
                if v > 0.01:
                    line = "  %9.2f mm3  %s / %s" % (v, real[i].Label, real[j].Label)
                    pair = {real[i].Label.rsplit("-", 1)[0], real[j].Label.rsplit("-", 1)[0]}
                    (expected if any(pair == set(e) for e in EXPECTED) else clashes).append(line)
    # module A must keep the head's fixed zone, cable passage and rest envelope free (the turning disc: checked in motion)
    res = [o for o in inst if o.MotionGroup == "reserve" and o.Name.startswith(("RES_TETE_FIXE", "RES_TETE_CABLES", "RES_TETE_REPOS"))]
    res_hits = []
    for r in res:
        for o in real:
            if o.Module != "A" or o.MotionGroup.startswith("door") or o.Label.startswith("FIX_VIS_PLAQUE_ECROU"):
                continue
            if r.Shape.BoundBox.intersect(o.Shape.BoundBox):
                v = r.Shape.common(o.Shape).Volume
                if v > 0.01:
                    res_hits.append("  %9.2f mm3  %s / %s" % (v, r.Label, o.Label))
    rep += ["", "Rest pose (carriage down, doors at contact, head vertical, stack in place): real parts"] + clashes
    rep.append("interferences: %d" % len(clashes))
    rep += ["", "Expected contacts (real on the hardware, not counted):"] + expected
    rep += bom_lines()
    rep += ["", "Module A (fixed parts) inside the space reserved for module B:"] + res_hits
    rep.append("reserve violations: %d" % len(res_hits))
    doc.saveAs(os.path.join(OUT, "MODULE_CLAPETS_V7.FCStd"))
    Import.export(real, os.path.join(OUT, "STEP", "MODULE_CLAPETS_V7.step"))
    Import.export([o for o in real if o.Module == "A"], os.path.join(OUT, "STEP", "MODULE_A_CLAPETS.step"))
    Import.export([o for o in real if o.Module == "B"], os.path.join(OUT, "STEP", "MODULE_B_TETE.step"))
    with open(os.path.join(OUT, "report.txt"), "w") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep))


main()
