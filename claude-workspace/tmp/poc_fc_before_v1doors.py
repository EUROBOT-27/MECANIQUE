# poc_fc.py - PROOF OF CONCEPT clapets module (PoC 2), FreeCAD version of ../sw/swpoc.cs (same design, same numbers).
#   Lift = the Two Trees Bluer V2 Y axis stood on end: 2 rails + the butterfly bed plate (4 V-wheels) as the carriage;
#   NEMA17 standing in a printed base, coupler, T8 screw up the middle behind the plate, 608 at the top.
#   Doors: one FIXED plain Ø8 rod per door (no flat needed), hub on 2x 608ZZ around it with a 40T gear printed on it (x2),
#   MG996R upside down under the top plate.
#   Centre in front of the plate kept free for the suction head (reserved block). See ../README.md.
# Run (headless):  "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" poc_fc.py
# Output: ../CAD_FC/  (STEP/ every part + assembly, STL/ printed parts, MODULE_CLAPETS_POC.FCStd, report.txt)
# Robot frame (mm) = FreeCAD frame: x right, y towards the stack, z up, z = 0 = table / bench board.
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
    YF, BOX_Y0 = 140, 143                                   # module face, stack face
    # ---- printer parts: Two Trees Bluer V2, from Eurobot 2027-ALL/mechanical/resources/3D Printer Two Trees Bluer V2.3dm ----
    # The plate itself did not import; its holes come from the screws/nuts/wheel bolts that go through it.
    # Plate frame: u across the rails (= x), v along the rails (= z), centre = between the 4 wheels.
    RAIL_W, RAIL_DX = 20, 40.45                             # 2 Y rails = 2020 x 350 mm, centres 80.9 apart (3dm)
    RAIL_YC, RAIL_Z0, RAIL_L = 58.5, 6, 350                 # rails stand in the base: z 6 .. 356
    PL_GAP, PL_T = 3.3, 3.5                                 # gap rail face -> plate, thickness: from the 3dm, CHECK
    PL_Y0 = RAIL_YC + RAIL_W / 2 + PL_GAP                   # plate rear face y 71.8, front 75.3
    PL_ZC = 150                                             # our choice: height of the plate centre (carriage down)
    WH_X, WH_DZ = 60.0, 37.5                                # wheel bolts at u ±60, v ±37.5 (3dm)
    WH_R, WH_W = WH_X - RAIL_DX - RAIL_W / 2, 10.2          # ref wheel = contact radius in the V-slot (9.55)
    WH_Z0, WH_Z1 = PL_ZC - WH_DZ, PL_ZC + WH_DZ
    SPRING_U = SPRING_V = 85                                # 4 bed-spring holes (corner lobes) u ±85 v ±85 (3dm), M4 assumed
    CLAMP_V = 10                                            # 2 belt-clamp holes u 0, v ±10 (3dm), M3 assumed
    WING_BOLTS = [(SPRING_U, PL_ZC - SPRING_V), (SPRING_U, PL_ZC + SPRING_V)]   # (x, z), M4
    NUT_BOLTS = [(0.0, PL_ZC - CLAMP_V), (0.0, PL_ZC + CLAMP_V)]                # (x, z), M3
    # ---- lift ----
    MOT_Z1, SHELF_T = 46, 6                                 # motor face (top of the body) z 46, shelf 46..52
    CPL_Z0, CPL_Z1, SCREW_Z0, SCREW_Z1 = 58, 83, 71, 363    # coupler; screw 292 mm (cut the ~400 mm printer screw)
    NUT_Z = 110                                             # nut shelf 110..116, flange on top, below the clamp holes
    TOP_Z0, TOP_Z1 = 344, 364                               # top tie (rail tops at 356), 608 for the screw end
    LIFT = 18                                               # max travel (software); 15 mm used
    # ---- door units ----
    PX, PY = 125, 113                                       # fixed hinge rod (right), 3 mm further back so the
                                                            # 40T ring stays behind the unit plates (front edge W_Y1)
    LOW, UP, PT = 96, 200, 6                                # unit plates
    W_X0, W_X1, W_Y0, W_Y1 = 66, 146, PL_Y0 + PL_T, 140     # plates reach y 140: they cover the ring, 3 mm before the stack
    HUB_R, HUB_Z0, HUB_Z1 = 14, 103.8, 198.2                # door hub on 2x 608ZZ (M8 washer each end)
    BRG_R, BRG_T = 11.05, 7.1
    GM, GZ1, GZ2 = 1.25, 20, 40                             # 20T pinion (MG996R) -> 40T ring on the hub, x2
    # x2: holding ~0.96 N.m at the hinge (3 pads x 4 N x 80 mm) -> 0.48 N.m at the servo, ~45-50 % of MG996R stall.
    # Door travel is limited to ~90 deg (servo 180 deg / 2): enough for open -21 / clamp +5; no full fold on the PoC.
    GC = GM * (GZ1 + GZ2) / 2
    SVY = PY - GC                                           # servo axis (125, 83.5)
    SV_L, SV_W, SV_H, SV_FL, SV_OUT, SV_HORN = 40.7, 19.7, 37.0, 26.6, 10.0, 43.5   # MG996R (= MG995), CHECK
    SV_X0 = PX - SV_OUT
    SV_X1 = SV_X0 + SV_L
    SV_XC = (SV_X0 + SV_X1) / 2                             # body x 115..155.7
    SV_TOP = UP                                             # servo body "bottom" (cable end) against the plate
    SV_FLZ = SV_TOP - SV_FL                                 # flange face on the body side (posts end here)
    GZB = SV_TOP - SV_HORN
    GZA = GZB - 8                                           # gears z 148.5..156.5
    SHEET_T, PAD_T = 3, 10                                  # 3 mm plywood / alu sheet
    SX0 = 170
    SX1 = SX0 + SHEET_T                                     # pad face at x 160 = box end
    SY0, SY1, TAB_Y0 = BOX_Y0 + 2, 225, PY + 14             # sheet y 145..225, tabs back to 130
    PAD_Y0, PAD_Y1 = 172, 220
    DZ0, DZ1 = 15, 320
    ARM1, ARM2 = (104, 114), (188, 198)
    FL1, FL2 = (103, 118), (180, 198)                       # lower flange above the lower plate (it sweeps over it)
    NUT_W, NUT_L, NUT_T = 5.6, 6.4, 2.6                     # M3 nut trap
    SV_SLOT = 2                                             # servo posts: ±2 mm slots along the gear line = mesh adjustment
    HORN_R, HORN_T = 10.5, 2.0                              # MG996R round horn Ø21 x 2 (CHECK): pocket in the pinion
    # hinge rod: plain Ø8 rod (lab stock), cut to 110 mm, FIXED: blind hole in the top plate (3 mm roof) + printed cap
    # screwed under the bottom plate (2x M3 x 8 into captive nuts). Snug bores stop it turning; it carries no torque.
    ROD_BORE_R, ROD_L, CAP_T, CAP_DY = 4.05, 110, 3, 9
    HEAD_X, HEAD_Y0, HEAD_Z0, HEAD_Z1 = 60, W_Y0 + 3, 90, 330   # reserved block for the future suction head


# =============================================================================================== geometry
# s = +1 right / -1 left: mirror in x
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
        pts.reverse()           # mirroring flips the winding: keep the face normal +z, else the solid is inside out
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return face.extrude(Vector(0, 0, z1 - z0))


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


# involute spur gear outline, 20 deg, no profile shift; phase = angle of tooth 0 centre (deg); bl = backlash (mm)
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


# M3 nut trap (nut axis along 'axis': 0 x, 1 y, 2 z) centred at (x, y, z), open along 'open' by 'ext' mm
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
    # merge coplanar faces; removeSplitter can leave an "unorientable" shell (seen on mirrored parts), fix() repairs it
    clean = sh.removeSplitter()
    clean.fix(1e-7, 1e-7, 1e-7)
    if clean.isValid() and abs(clean.Volume - sh.Volume) < 1e-3 * sh.Volume:
        return clean
    sh = sh.copy()
    sh.fix(1e-7, 1e-7, 1e-7)
    return sh


# =============================================================================================== parts
PETG, PETG2, ALU, STEEL, DARK = (0.95, 0.45, 0.10), (0.20, 0.45, 0.85), (0.78, 0.80, 0.83), (0.62, 0.63, 0.66), (0.13, 0.13, 0.15)
FOAM, WOOD, BRASS, BOXC, SERVO, GHOST = (0.25, 0.65, 0.35), (0.80, 0.65, 0.45), (0.80, 0.62, 0.25), (0.85, 0.72, 0.48), (0.10, 0.10, 0.12), (0.30, 0.80, 0.40)

PARTS = {}      # name -> (shape, density kg/m3, colour, printed)


def part(name, shape, rho, rgb, printed):
    PARTS[name] = (shape, rho, rgb, printed)


RY0, RY1 = G.RAIL_YC - G.RAIL_W / 2, G.RAIL_YC + G.RAIL_W / 2


def socle():    # base: screwed to the bench board; 2 rail sockets (M5 + T-nut, rear slot); motor shelf between them
    a = [box(1, -62, 62, 34, 86, 0, G.RAIL_Z0), box(1, -26.5, 26.5, 36, 81, G.MOT_Z1, G.MOT_Z1 + G.SHELF_T)]
    c = []
    for s in (1, -1):
        a.append(box(s, G.RAIL_DX - 14, G.RAIL_DX + 14, RY0 - 4, RY1 + 4, G.RAIL_Z0, G.MOT_Z1 + G.SHELF_T))
        c.append(box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, RY0 - 0.2, RY1 + 0.2, G.RAIL_Z0, 100))      # rail pocket
        c.append(ycyl(s, G.RAIL_DX, RY0 - 5, RY0 + 1, 30, 2.75))                                         # M5x10 + T-nut
        c += [vcyl(s, 55, y, -1, G.RAIL_Z0 + 1, 2.2) for y in (40, 80)]                                   # wood screws
    c.append(vcyl(1, 0, G.RAIL_YC, G.MOT_Z1 - 1, G.MOT_Z1 + G.SHELF_T + 1, 11.5))                         # Ø22 pilot
    c += [vcyl(1, dx, G.RAIL_YC + dy, G.MOT_Z1 - 1, G.MOT_Z1 + G.SHELF_T + 1, 1.7) for dx in (-15.5, 15.5) for dy in (-15.5, 15.5)]
    part("SOCLE", solid(a, c), 1270, PETG, True)


def haut():     # top tie: caps both rail tops (M5 + T-nut), 608ZZ for the top end of the screw
    top = G.RAIL_Z0 + G.RAIL_L
    a = [box(1, -G.RAIL_DX - 14, G.RAIL_DX + 14, RY0 - 4, RY1 + 4, G.TOP_Z0, G.TOP_Z1)]
    c = [vcyl(1, 0, G.RAIL_YC, G.TOP_Z0 - 1, top + G.BRG_T, G.BRG_R)]                                     # 608 from below
    for s in (1, -1):
        c.append(box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, RY0 - 0.2, RY1 + 0.2, G.TOP_Z0 - 1, top))
        c.append(ycyl(s, G.RAIL_DX, RY0 - 5, RY0 + 1, G.TOP_Z0 + 6, 2.75))
    part("TRAVERSE_HAUT", solid(a, c), 1270, PETG, True)


def support_ecrou():    # nut shelf: bolted to the plate's rear face (belt-clamp holes), floating T8 nut (4x M3, Ø4 holes)
    top = G.PL_ZC + G.CLAMP_V + 10
    a = [box(1, -25, 25, G.PL_Y0 - 5, G.PL_Y0, G.NUT_Z - 10, top), box(1, -25, 25, 38, G.PL_Y0 - 5, G.NUT_Z, G.NUT_Z + 6)]
    a += [box(s, 19, 25, 40, G.PL_Y0 - 5, G.NUT_Z + 6, top) for s in (1, -1)]                              # ribs
    c = [vcyl(1, 0, G.RAIL_YC, G.NUT_Z - 1, G.NUT_Z + 7, 5.6)]
    c += [vcyl(1, qx, G.RAIL_YC + qy, G.NUT_Z - 1, G.NUT_Z + 7, 2.0) for qx, qy in ((8, 0), (-8, 0), (0, 8), (0, -8))]
    for bx, bz in G.NUT_BOLTS:
        c.append(ycyl(1, bx, G.PL_Y0 - 6, G.PL_Y0 + 1, bz, 1.7))                                         # M3 through the plate
        c.append(nut(1, 1, bx, G.PL_Y0 - 5 + G.NUT_T / 2 - 0.1, bz, 1, -3))                              # nut from the back
    c.append(box(1, -12, 12, G.PL_Y0 - 5.5, G.PL_Y0 + 0.1, G.NUT_Z + 5.5, G.NUT_Z + 10.5))               # notch for the nut flange
    part("SUPPORT_ECROU", solid(a, c), 1270, PETG, True)


def aile(s, name):      # door unit frame: 2 plates holding the fixed Ø8 hinge rod, back wall bolted to the plate, MG996R posts
    a, c = [], []
    for z in (G.LOW, G.UP):
        a.append(box(s, G.W_X0, G.W_X1, G.W_Y0, G.W_Y1, z, z + G.PT))
        a.append(vcyl(s, G.PX, G.PY, z, z + G.PT, 12))                                                  # shaft boss
    a.append(box(s, 100, 166, G.SVY - 12, G.W_Y0 + 1, G.UP, G.UP + G.PT))                                # servo extension (behind)
    a.append(box(s, G.W_X1, 166, G.W_Y0, G.SVY + 12, G.UP, G.UP + G.PT))
    a.append(box(s, G.W_X0, 105, G.W_Y0, G.W_Y0 + 6, G.PL_ZC - G.SPRING_V - 9, G.PL_ZC + G.SPRING_V + 9))   # back wall
    a.append(box(s, G.W_X0, G.W_X0 + 6, G.W_Y0, G.W_Y1, G.LOW, G.UP + G.PT))                             # inner side wall
    a.append(vcyl(s, G.PX, G.PY, G.UP + G.PT, G.UP + G.PT + 3, 12))                                      # roof over the rod
    c.append(vcyl(s, G.PX, G.PY, G.LOW - 1, G.UP + G.PT, G.ROD_BORE_R))                                   # Ø8 rod: through bottom, blind top
    for dy in (-G.CAP_DY, G.CAP_DY):                                                                    # cap under the bottom plate:
        c.append(vcyl(s, G.PX, G.PY + dy, G.LOW - 1, G.LOW + 5, 1.7))                                    # M3 x 8 from below...
        c.append(nut(s, 2, G.PX, G.PY + dy, G.LOW + 3.5, 0, 25))                                          # ...nut slid in from the side
    for side in (-1, 1):                                                                                 # MG996R posts
        hx = G.SV_XC + side * 24.375
        a.append(box(s, hx - 3.8, hx + 3.8, G.SVY - 11, G.SVY + 11, G.SV_FLZ, G.UP))                     # clears the body by 0.2
        for dy in (-5, 5):
            y0, y1 = G.SVY + dy - G.SV_SLOT, G.SVY + dy + G.SV_SLOT                                         # slot along the gear line
            c += [vcyl(s, hx, y0, G.SV_FLZ - 1, G.SV_FLZ + 13, 1.7), vcyl(s, hx, y1, G.SV_FLZ - 1, G.SV_FLZ + 13, 1.7),
                  box(s, hx - 1.7, hx + 1.7, y0, y1, G.SV_FLZ - 1, G.SV_FLZ + 13)]
            nb = nut(s, 2, hx, G.SVY + dy, G.SV_FLZ + 8, 0, side * 10)                                    # nut slid in from the side,
            c += [nb.translated(App.Vector(0, d, 0)) for d in (-G.SV_SLOT, 0, G.SV_SLOT)]                 # pocket long enough to slide
    for bx, bz in G.WING_BOLTS:
        c.append(ycyl(s, bx, G.W_Y0 - 1, G.W_Y0 + 7, bz, 2.25))                                          # M4 through the spring hole
        c.append(box(s, bx - 4.1, bx + 4.1, G.W_Y0 + 2.4, G.W_Y0 + 9, bz - 3.6, bz + 3.6))               # M4 nut, from the front
    part(name, solid(a, c), 1270, PETG2, True)


def moyeu(s, name):     # door hub: turns on the fixed Ø8 rod (2x 608ZZ), 40T ring gear printed on it, 2 arms to the sheet tabs
    a = [vcyl(s, G.PX, G.PY, G.HUB_Z0, G.HUB_Z1, G.HUB_R),
         prism(s, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB)]
    fl = [(G.PX + 38, G.PY + 14), (G.SX0, G.PY + 14), (G.SX0, G.PY + 26), (G.PX + 38, G.PY + 26)]
    arm = hull(circle(G.PX, G.PY, G.HUB_R, 48) + fl)
    a += [prism(s, arm, *G.ARM1), prism(s, arm, *G.ARM2)]
    c = []
    for f0, f1 in (G.FL1, G.FL2):
        a.append(box(s, G.PX + 38, G.SX0, G.PY + 14, G.PY + 26, f0, f1))                                # flange behind the tab
        for z in (f0 + 3.5, f1 - 3.5):
            c.append(xcyl(s, G.PX + 37, G.SX0 + 0.1, G.PY + 20, z, 1.7))
            c.append(nut(s, 0, G.PX + 38 + G.NUT_T / 2 - 0.1, G.PY + 20, z, 0, 0))
    c += [vcyl(s, G.PX, G.PY, G.HUB_Z0 - 1, G.HUB_Z0 + G.BRG_T, G.BRG_R),                                # 608 bottom
          vcyl(s, G.PX, G.PY, G.HUB_Z1 - G.BRG_T, G.HUB_Z1 + 1, G.BRG_R),                                # 608 top
          vcyl(s, G.PX, G.PY, G.HUB_Z0 - 1, G.HUB_Z1 + 1, 5.0)]                                          # shaft clearance
    part(name, solid(a, c), 1270, PETG, True)


def pignon():   # 20T m1.25 + collar: the round horn sits in a pocket (centres it), 4x M2 screws through the horn into the pinion
    a = [prism(1, gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.SVY, G.GZB, G.GZB + G.HORN_T, G.HORN_R + 3)]
    c = [vcyl(1, G.PX, G.SVY, G.GZB, G.GZB + G.HORN_T + 1, G.HORN_R + 0.2),                                # horn pocket, open towards the servo
         vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2)]                                                  # horn screw access
    c += [vcyl(1, G.PX + 7.5 * math.cos(math.pi / 2 * k), G.SVY + 7.5 * math.sin(math.pi / 2 * k), G.GZA - 1, G.GZB + 1, 0.8) for k in range(4)]   # M2 pilot
    part("PIGNON_SERVO_20T", solid(a, c), 1270, PETG2, True)


def bouchon():  # cap under the bottom plate: stops the hinge rod sliding down (2x M3 x 8)
    a = [vcyl(1, G.PX, G.PY, G.LOW - G.CAP_T, G.LOW, 13)]
    c = [vcyl(1, G.PX, G.PY + dy, G.LOW - G.CAP_T - 1, G.LOW + 1, 1.7) for dy in (-G.CAP_DY, G.CAP_DY)]
    part("BOUCHON_TIGE", solid(a, c), 1270, PETG, True)


def tole():     # door sheet: 3 mm plywood or aluminium, 80 mm deep (right; the left one is the same part moved)
    a, c = [box(1, G.SX0, G.SX1, G.SY0, G.SY1, G.DZ0, G.DZ1)], []
    for f0, f1 in (G.FL1, G.FL2):
        a.append(box(1, G.SX0, G.SX1, G.TAB_Y0, G.SY0, f0, f1))
        c += [xcyl(1, G.SX0 - 1, G.SX1 + 1, G.PY + 20, z, 1.7) for z in (f0 + 3.5, f1 - 3.5)]
    part("TOLE_PORTE", solid(a, c), 700, WOOD, False)


def refs():     # reference parts, simplified (not made)
    part("MOUSSE_60x48x10", box(1, 160, G.SX0, G.PAD_Y0, G.PAD_Y1, 25, 85), 50, FOAM, False)
    part("REF_RAIL_2020", box(1, G.RAIL_DX - 10, G.RAIL_DX + 10, RY0, RY1, G.RAIL_Z0, G.RAIL_Z0 + G.RAIL_L), 2700, DARK, False)
    y0, y1, cz = G.PL_Y0, G.PL_Y0 + G.PL_T, G.PL_ZC     # butterfly plate: outline approximate, holes exact (3dm)
    a, c = [box(1, -72, 72, y0, y1, cz - 52, cz + 52)], []
    for su in (1, -1):
        for sv in (1, -1):
            a.append(box(1, min(su * 40, su * 85), max(su * 40, su * 85), y0, y1, min(cz + sv * 40, cz + sv * 85), max(cz + sv * 40, cz + sv * 85)))
            a.append(ycyl(1, su * G.SPRING_U, y0, y1, cz + sv * G.SPRING_V, 12))
            c.append(ycyl(1, su * G.SPRING_U, y0 - 1, y1 + 1, cz + sv * G.SPRING_V, 2.25))
            c.append(ycyl(1, su * G.WH_X, y0 - 1, y1 + 1, cz + sv * G.WH_DZ, 2.6))
    c += [ycyl(1, 0, y0 - 1, y1 + 1, cz + sv * G.CLAMP_V, 1.7) for sv in (1, -1)]
    part("REF_PLAQUE_PAPILLON", solid(a, c), 7850, DARK, False)
    part("REF_ROUE_V", ycyl(1, G.WH_X, G.RAIL_YC - G.WH_W / 2, G.RAIL_YC + G.WH_W / 2, G.WH_Z0, G.WH_R), 1400, DARK, False)
    part("REF_TIGE_D8x110", vcyl(1, G.PX, G.PY, G.LOW, G.LOW + G.ROD_L, 4), 7850, STEEL, False)
    part("REF_608ZZ", solid([vcyl(1, G.PX, G.PY, G.HUB_Z0, G.HUB_Z0 + 7, 11)], [vcyl(1, G.PX, G.PY, 0, 400, 4)]), 7850, STEEL, False)
    part("REF_NEMA17", solid([box(1, -21.15, 21.15, G.RAIL_YC - 21.15, G.RAIL_YC + 21.15, G.MOT_Z1 - 40, G.MOT_Z1),
                              vcyl(1, 0, G.RAIL_YC, G.MOT_Z1, G.MOT_Z1 + 2, 11), vcyl(1, 0, G.RAIL_YC, G.MOT_Z1 + 2, G.MOT_Z1 + 24, 2.5)]),
         3500, DARK, False)
    part("REF_COUPLEUR_5x8", solid([vcyl(1, 0, G.RAIL_YC, G.CPL_Z0, G.CPL_Z1, 9.5)],
                                   [vcyl(1, 0, G.RAIL_YC, G.SCREW_Z0, G.CPL_Z1 + 1, 4), vcyl(1, 0, G.RAIL_YC, G.CPL_Z0 - 1, G.MOT_Z1 + 24, 2.5)]),
         2700, ALU, False)
    part("REF_VIS_T8", vcyl(1, 0, G.RAIL_YC, G.SCREW_Z0, G.SCREW_Z1, 4), 7850, STEEL, False)
    part("REF_ECROU_T8", solid([vcyl(1, 0, G.RAIL_YC, G.NUT_Z + 6, G.NUT_Z + 9.5, 11), vcyl(1, 0, G.RAIL_YC, G.NUT_Z - 5.5, G.NUT_Z + 6, 5.1)],
                               [vcyl(1, 0, G.RAIL_YC, 0, 400, 4)]), 8500, BRASS, False)
    for s, name in ((1, "REF_MG996R_D"), (-1, "REF_MG996R_G")):     # upside down: body against the upper plate, horn below
        part(name, solid([box(s, G.SV_X0, G.SV_X1, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_TOP - G.SV_H, G.SV_TOP),
                          box(s, G.SV_XC - 27.25, G.SV_XC + 27.25, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_FLZ - 2.4, G.SV_FLZ),
                          vcyl(s, G.PX, G.SVY, G.GZB + 2, G.SV_TOP - G.SV_H, 3), vcyl(s, G.PX, G.SVY, G.GZB, G.GZB + 2, 10.5)]),
             1200, SERVO, False)
    part("REF_PILE_3_PIERRES", Part.makeCompound([box(1, -160, 160, G.BOX_Y0, G.BOX_Y0 + 110, 110 * i + 0.5, 110 * (i + 1) - 0.5) for i in range(3)]),
         100, BOXC, False)
    part("RESERVE_TETE_VENTOUSES", box(1, -G.HEAD_X, G.HEAD_X, G.HEAD_Y0, G.YF, G.HEAD_Z0, G.HEAD_Z1), 10, GHOST, False)


# =============================================================================================== assembly
def placements():
    """(part name, dx, dy, dz) for every instance; every part is modelled at its place (carriage DOWN, doors at 0)."""
    L = -2 * G.PX
    p = [("SOCLE", 0, 0, 0), ("TRAVERSE_HAUT", 0, 0, 0), ("REF_NEMA17", 0, 0, 0), ("REF_COUPLEUR_5x8", 0, 0, 0), ("REF_VIS_T8", 0, 0, 0),
         ("REF_608ZZ", -G.PX, G.RAIL_YC - G.PY, G.RAIL_Z0 + G.RAIL_L - G.HUB_Z0),             # screw top bearing
         ("REF_RAIL_2020", 0, 0, 0), ("REF_RAIL_2020", -2 * G.RAIL_DX, 0, 0),
         ("REF_PLAQUE_PAPILLON", 0, 0, 0), ("SUPPORT_ECROU", 0, 0, 0), ("REF_ECROU_T8", 0, 0, 0),
         ("AILE_D", 0, 0, 0), ("AILE_G", 0, 0, 0), ("MOYEU_PORTE_D", 0, 0, 0), ("MOYEU_PORTE_G", 0, 0, 0),
         ("REF_MG996R_D", 0, 0, 0), ("REF_MG996R_G", 0, 0, 0), ("REF_PILE_3_PIERRES", 0, 0, 0), ("RESERVE_TETE_VENTOUSES", 0, 0, 0)]
    p += [("REF_ROUE_V", dx, 0, dz) for dx in (0, -2 * G.WH_X) for dz in (0, G.WH_Z1 - G.WH_Z0)]
    for dx in (0, L):
        p += [("REF_TIGE_D8x110", dx, 0, 0), ("BOUCHON_TIGE", dx, 0, 0), ("PIGNON_SERVO_20T", dx, 0, 0),
              ("REF_608ZZ", dx, 0, 0), ("REF_608ZZ", dx, 0, G.HUB_Z1 - 7 - G.HUB_Z0)]
    p += [("TOLE_PORTE", dx, 0, 0) for dx in (0, -(G.SX0 + G.SX1))]
    p += [("MOUSSE_60x48x10", dx, 0, dz) for dx in (0, -(160 + G.SX0)) for dz in (0, 110, 220)]
    return p


def main():
    for d in ("", "STEP", "STL"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    socle(); haut(); support_ecrou(); aile(1, "AILE_D"); aile(-1, "AILE_G"); moyeu(1, "MOYEU_PORTE_D"); moyeu(-1, "MOYEU_PORTE_G")
    pignon(); bouchon(); tole(); refs()

    rep = []
    printed = []
    for name, (sh, rho, rgb, pr) in PARTS.items():
        bb = sh.BoundBox
        rep.append("%-24s solids %d  mass %7.1f g   size %.1f x %.1f x %.1f mm   %s" % (
            name, len(sh.Solids), sh.Volume * 1e-9 * rho * 1000, bb.XLength, bb.YLength, bb.ZLength, "valid" if sh.isValid() else "INVALID"))
        sh.exportStep(os.path.join(OUT, "STEP", name + ".step"))
        if pr:
            mesh = MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.01, AngularDeflection=0.0349, Relative=False)
            mesh.write(os.path.join(OUT, "STL", name + ".stl"))
            printed.append(name)
    with open(os.path.join(OUT, "STL", "printed_parts.txt"), "w") as f:
        f.write("\n".join(printed) + "\n")

    # assembly document (one Part::Feature per instance) + interference check
    doc = App.newDocument("MODULE_CLAPETS_POC")
    inst = []
    count = {}
    for name, dx, dy, dz in placements():
        count[name] = count.get(name, 0) + 1
        o = doc.addObject("Part::Feature", "%s_%d" % (name, count[name]))
        o.Shape = PARTS[name][0].copy()
        o.Placement = App.Placement(Vector(dx, dy, dz), App.Rotation())
        o.Label = "%s-%d" % (name, count[name])
        inst.append(o)
    # tree folders for inspection
    folders = {k: doc.addObject("App::DocumentObjectGroup", k) for k in ("Printed", "Bought_or_printer_parts", "Reference")}
    folders["Printed"].Label = "1 Printed (PETG)"
    folders["Bought_or_printer_parts"].Label = "2 Bought / Two Trees printer parts"
    folders["Reference"].Label = "3 Reference (stack, suction-head reserved space)"
    for o in inst:
        name = o.Name.rsplit("_", 1)[0]
        if PARTS[name][3]:
            folders["Printed"].addObject(o)
        elif name in ("REF_PILE_3_PIERRES", "RESERVE_TETE_VENTOUSES"):
            folders["Reference"].addObject(o)
        else:
            folders["Bought_or_printer_parts"].addObject(o)
    doc.recompute()

    clashes = []
    for i in range(len(inst)):
        si = inst[i].Shape
        for j in range(i + 1, len(inst)):
            sj = inst[j].Shape
            if not si.BoundBox.intersect(sj.BoundBox):
                continue
            v = si.common(sj).Volume
            if v > 0.01:
                clashes.append("  %9.2f mm3  %s / %s" % (v, inst[i].Label, inst[j].Label))
    rep.append("")
    rep += clashes
    rep.append("interferences: %d   (the suction-head reserved block must stay at 0)" % len(clashes))

    doc.saveAs(os.path.join(OUT, "MODULE_CLAPETS_POC.FCStd"))
    Import.export(inst, os.path.join(OUT, "STEP", "MODULE_CLAPETS_POC.step"))
    with open(os.path.join(OUT, "report.txt"), "w") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep))


main()
