# base_330_js.py - 330 x 280 base plate for the JSUMO JS7444 wheels + AMT102-V odometry modules (FreeCAD).
#
# Run headless:  freecadcmd base_330_js.py      (or as a macro in the FreeCAD GUI)
# Writes into CAD/: base_330_js.FCStd/.step/.dxf (plate), odo_bracket / odo_arm / odo_wheel .step/.stl (printed),
#                   caster_spacer.step/.stl/.dxf
# Then run base_330_js_assembly.py for the fit / clash / floor checks (report: base_330_js_report.txt).
#
# Same frame and outline as ../base_330 (330 x 280 x 5): X = wheel axis, Y = front/back, Z = up,
# origin = plate centre, BOTTOM face of the plate ("plate frame"). Every plate feature is mirrored about X = 0 and Y = 0.
# Printed odometry parts are built for the x > 0 side with the bracket at -Y; they are symmetric about their own
# mid-plane (x = ODO_X), so the left side uses the same parts, mirrored in place.
#
# What changed vs base_330: wheel well sized for the JSUMO wheel with an UNCERTAINTY ENVELOPE (wheel not measured
# yet), no MDF lift (hinge straight on the plate; ride height set by a printed caster spacer instead), the
# sysRoueCodeusee encoder rods replaced by a sprung swing arm that carries the AMT102-V encoder (the
# "Poenc1_102-v-2530" part of resources/CDR-2027 BlocOdometrie), and the clapets mount moved 12 mm forward.

import importlib.util
import math
import os

HERE = (os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals()
        else os.getcwd())
OUT = os.path.join(HERE, "CAD")

# reuse the sketch / DXF writers of base_330 (parameters there are NOT used)
_spec = importlib.util.spec_from_file_location("base_330_lib", os.path.join(HERE, "..", "base_330", "base_330.py"))
B0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B0)

# ======================================================================= plate (same size as base_330)
W, L, T = 330.0, 280.0, 5.0
W2, L2 = W / 2, L / 2

# ======================================================================= JSUMO JS7444 drive wheel (D-004) - NOT MEASURED
# Shop data: "74 mm" (mikroelectron), another page says 77 x 44. Width 44 is from the name. Hub / bore unknown.
# The plate is cut for the ENVELOPE (MAX values); the ride height is computed with the NOMINAL value and corrected with
# the caster spacer once the real wheel is measured.
WHEEL_D_NOM = 74.0
WHEEL_D_MIN = 72.0          # worn tyre / smaller than announced
WHEEL_D_MAX = 80.0          # 77 (other shop page) + 3 mm margin
WHEEL_W_NOM = 44.0
WHEEL_W_MAX = 48.0          # width + hub boss that may stick out
WHEEL_IN_NOM = 68.0         # inner face of the wheel (hub pushed on the Pololu 6 mm D shaft)
WHEEL_IN_TOL = 2.0          # +/- where the hub really ends up on the shaft
# Drive chain = base_330 (same Pololu 37D + same hinge brackets)
MOTOR_FACE_X = 61.5         # inner face of the hinge motor plate
HINGE_PLATE_OUT = 64.7      # outer face of the hinge motor plate (wheel can't come closer than this)
SHAFT_ABOVE_SEAT = 20.5     # motor shaft above the hinge seat (base_330)
LIFT_H = 0.0                # no MDF lift any more: hinge straight on the plate (Ø74 wheel -> plate 11.5 above the floor)
HINGE_D, HINGE_X, HINGE_Y = 3.5, (26.9, 50.9), 15.0

# wheel well (through the plate)
POCKET_X0 = 65.0                                                     # 0.3 past the hinge plate
POCKET_X1 = WHEEL_IN_NOM + WHEEL_IN_TOL + WHEEL_W_MAX + 3.0          # 121: 3 mm past the worst-case outer face
POCKET_Y = WHEEL_D_MAX / 2 + 5.0                                     # 45: 5 mm past the Ø80 envelope

# no strap slots (base_330 had 2 across the motors, used to strap the MDF lift): removed 2026-11-18 at Ayoub's request,
# the middle of the plate only keeps the 8 hinge holes
# corner holes (side-wall profiles), casters, back wall profiles: as base_330
CORNER_D, CORNER_INSET = 6.35, 11.0
CASTER_Y, CASTER_D, CASTER_SCREW_X, CASTER_SCREW_D = 110.0, 33.0, 20.0, 4.0
CASTER_REACH = 16.5         # caster ball bottom below the plate top, flange on the plate (base_330)
PROF_X, PROF_Y, PROF_D = 100.0, 130.0, 5.5

# clapets v7 module A: same 4 x M4 pattern; module moved CLAP_DY forward. The socle starts 8.5 mm behind its holes'
# y = 18 row (module frame y 8.5) -> socle front at CLAP_DY + 8.5 must clear the Ø80 wheel envelope (y 40) by >= 3.
CLAP_X, CLAP_Y, CLAP_D = 63.0, (18.0, 53.0), 4.8
CLAP_SOCLE_Y0 = 8.5
CLAP_DY = math.ceil(WHEEL_D_MAX / 2 + 3.0 - CLAP_SOCLE_Y0)          # 35 (base_330: 23)

# ======================================================================= odometry module (AMT102-V on a swing arm)
# Odometry wheel: printed hub + O-ring tyre. Its plane is outside the drive wheel, on the axle line (y = 0).
ODO_X = 136.0               # wheel mid-plane -> odometry track 272 mm
ODO_HUB_D = 50.0            # printed hub flanges
ODO_GROOVE_D = 46.0         # groove bottom
ODO_ORING_CS = 3.5          # O-ring 46 x 3.5 (ID x CS) NBR -> tyre OD 53
ODO_D = ODO_GROOVE_D + 2 * ODO_ORING_CS
ODO_SQUASH = 0.3            # O-ring flattening under the spring force
ODO_R = ODO_D / 2 - ODO_SQUASH
ODO_W = 8.0                 # hub width
ODO_BOSS = (9.0, 1.0)       # Ø x length of the bosses that touch the 625 inner races (locate the shaft axially)
SHAFT_D = 5.0               # AMT sleeve Ø5 (the one in the CDR model)
BRG = (5.0, 16.0, 5.0)      # 625ZZ: d, D, B (in the Ender V-wheels / local)
BRG_LIP = 1.0
ARM_PLATE_T = BRG[2] + BRG_LIP                                       # 6
X_IN = (ODO_X - ODO_W / 2 - ODO_BOSS[1] - ARM_PLATE_T, ODO_X - ODO_W / 2 - ODO_BOSS[1])   # inner arm plate 125..131
X_OUT = (ODO_X + ODO_W / 2 + ODO_BOSS[1], ODO_X + ODO_W / 2 + ODO_BOSS[1] + ARM_PLATE_T)  # outer arm plate 141..147
ENC_FACE_X = X_OUT[1]       # AMT102 mounting face on the outer arm plate
ENC_SHAFT_IN = 8.0          # shaft past the AMT mounting face (CDR model: cap inside at ~9.0)
ENC_HOLE_Y = 9.53           # AMT102 base holes (2 x, 19.05 apart, from the CDR model) -> M2 x 6 into M2 heat-set inserts
ENC_INSERT = (3.2, 4.0)     # M2 insert hole Ø x depth

# Arm: pivot axis // X (// drive axle) -> the arm swings in the YZ plane, so the odometry TRACK never changes.
PIV_Y = -60.0               # arm length 60
PLATE_TOP = T
FLOOR_NOM = -(WHEEL_D_NOM / 2 - SHAFT_ABOVE_SEAT - LIFT_H - T)       # floor in the plate frame (-11.5)
PIV_Z = FLOOR_NOM + ODO_R   # arm horizontal with the nominal wheel
ARM_BAND = 6.0              # side plates are PIV_Z +/- 6 between the hub and the axle boss
AXLE_BOSS = (13.5, 11.0, 4.0)   # half y, half z, corner R of the boss round the axle (holds the 625 + the AMT inserts)
HUB_D, PIV_BRG = 16.0, (3.0, 10.0, 4.0, 11.5, 1.0)   # F623ZZ: d, D, B, flange Ø, flange t (2 per arm)
CROSS_Y = (-45.0, -37.0)    # crossbar between the side plates (spring seat)
SPRING_Y = -41.0
SPRING = (8.0, 25.0, 20.0)  # OD, free length, installed length (Ender bed-levelling spring, 4 in hand)
ARM_DROOP = 5.0             # wheel may drop 5 mm below the nominal floor before the nut stops it
# Bracket (one printed part, bolted with 4 x M3 x 12 through the plate)
EAR_T = 6.0
EAR_X = ((X_IN[0] - 1.0 - EAR_T, X_IN[0] - 1.0), (X_OUT[1] + 1.0, X_OUT[1] + 1.0 + EAR_T))  # 118..124, 148..154
EAR_Y = (-74.0, -46.0)
BACK_Y = (-78.0, -74.0)
BRIDGE_Y = (-78.0, -34.0)
BRIDGE_T = 5.0
BRIDGE_Z0 = PIV_Z + ARM_BAND + SPRING[2]
FLANGE = (8.0, 4.0, (-74.0, -50.0))     # width outside each ear, thickness, y range
FOOT_HOLES_X = (EAR_X[0][0] - FLANGE[0] / 2, EAR_X[1][1] + FLANGE[0] / 2)   # 114, 158
FOOT_HOLES_Y = (-55.0, -69.0)
M3_CLEAR = 3.4
NOTCH_Y = 30.0              # plate notch round the odometry wheel + encoder (x POCKET_X1 .. edge)

# caster spacer (printed): sets the caster 2 mm above the floor. Thickness = CASTER_GAP + CASTER_REACH - plate top height
CASTER_GAP = 2.0


def plate_top_height(wheel_d):
    """Plate top above the floor for a given drive wheel diameter."""
    return wheel_d / 2 - SHAFT_ABOVE_SEAT - LIFT_H


def caster_spacer_t(wheel_d):
    return round(CASTER_GAP + CASTER_REACH - plate_top_height(wheel_d), 2)


CASTER_SPACER_T = caster_spacer_t(WHEEL_D_NOM)        # 2.0 for Ø74 (0.5 for Ø77): re-run after measuring the wheel
CASTER_SPACER = (26.0, 20.0, 6.0)                     # half x, half y, corner R


# ======================================================================= plate geometry
def geometry():
    P0, P1, PY, NY = POCKET_X0, POCKET_X1, POCKET_Y, NOTCH_Y
    assert HINGE_PLATE_OUT < P0 < P1 < W2 and NY < PY < L2
    right = [
        ("line", (0, -L2), (W2, -L2)),
        ("line", (W2, -L2), (W2, -NY)),
        ("line", (W2, -NY), (P1, -NY)),
        ("line", (P1, -NY), (P1, -PY)),
        ("line", (P1, -PY), (P0, -PY)),
        ("line", (P0, -PY), (P0, PY)),
        ("line", (P0, PY), (P1, PY)),
        ("line", (P1, PY), (P1, NY)),
        ("line", (P1, NY), (W2, NY)),
        ("line", (W2, NY), (W2, L2)),
        ("line", (W2, L2), (0, L2)),
    ]
    left = [("line", (-s[2][0], s[2][1]), (-s[1][0], s[1][1])) for s in reversed(right)]
    circles = []

    def quad(x, y, d):
        for sx in (1, -1):
            for sy in (1, -1):
                circles.append((sx * x, sy * y, d))

    for hx in HINGE_X:
        quad(hx, HINGE_Y, HINGE_D)
    quad(W2 - CORNER_INSET, L2 - CORNER_INSET, CORNER_D)
    quad(CASTER_SCREW_X, CASTER_Y, CASTER_SCREW_D)
    for cy in CLAP_Y:
        quad(CLAP_X, cy + CLAP_DY, CLAP_D)
    quad(PROF_X, PROF_Y, PROF_D)
    for fx in FOOT_HOLES_X:
        for fy in FOOT_HOLES_Y:
            quad(fx, -fy, M3_CLEAR)
    for sy in (1, -1):
        circles.append((0.0, sy * CASTER_Y, CASTER_D))
    return right + left, circles, []


def spacer_geometry():
    hx, hy, r = CASTER_SPACER
    outline = [
        ("line", (-hx + r, -hy), (hx - r, -hy)), ("arc", (hx - r, -hy + r), r, 270, 360),
        ("line", (hx, -hy + r), (hx, hy - r)), ("arc", (hx - r, hy - r), r, 0, 90),
        ("line", (hx - r, hy), (-hx + r, hy)), ("arc", (-hx + r, hy - r), r, 90, 180),
        ("line", (-hx, hy - r), (-hx, -hy + r)), ("arc", (-hx + r, -hy + r), r, 180, 270),
    ]
    circles = [(0.0, 0.0, CASTER_D), (CASTER_SCREW_X, 0.0, CASTER_SCREW_D), (-CASTER_SCREW_X, 0.0, CASTER_SCREW_D)]
    return outline, circles, []


# ======================================================================= printed odometry parts (plate frame, x > 0)
def _V(*a):
    import FreeCAD as App
    return App.Vector(*a)


def box(x0, x1, y0, y1, z0, z1):
    import Part
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, _V(x0, y0, z0))


def cyl_x(r, x0, x1, y, z):
    import Part
    return Part.makeCylinder(r, x1 - x0, _V(x0, y, z), _V(1, 0, 0))


def cyl_z(r, z0, z1, x, y):
    import Part
    return Part.makeCylinder(r, z1 - z0, _V(x, y, z0), _V(0, 0, 1))


def rrect_x(x0, x1, yc, zc, hy, hz, r):
    """Rounded rectangle in the YZ plane, extruded along X."""
    s = box(x0, x1, yc - hy + r, yc + hy - r, zc - hz, zc + hz).fuse(box(x0, x1, yc - hy, yc + hy, zc - hz + r, zc + hz - r))
    for sy in (1, -1):
        for sz in (1, -1):
            s = s.fuse(cyl_x(r, x0, x1, yc + sy * (hy - r), zc + sz * (hz - r)))
    return s.removeSplitter()


def odo_arm():
    """Swing arm: 2 side plates (625 seats + AMT inserts on the outer one), pivot hub (2 x F623), spring crossbar."""
    zc, hb = PIV_Z, ARM_BAND
    by, bz, br = AXLE_BOSS
    s = None
    for (x0, x1) in (X_IN, X_OUT):
        p = box(x0, x1, PIV_Y, 0.0, zc - hb, zc + hb).fuse(rrect_x(x0, x1, 0.0, zc, by, bz, br))
        s = p if s is None else s.fuse(p)
    s = s.fuse(cyl_x(HUB_D / 2, X_IN[0], X_OUT[1], PIV_Y, zc))
    s = s.fuse(box(X_IN[0], X_OUT[1], CROSS_Y[0], CROSS_Y[1], zc, zc + hb))
    # bores
    d, D, B = BRG
    s = s.cut(cyl_x(D / 2, X_IN[0] + BRG_LIP, X_IN[1] + 0.01, 0, zc))           # 625 seat, from the wheel side
    s = s.cut(cyl_x(D / 2, X_OUT[0] - 0.01, X_OUT[1] - BRG_LIP, 0, zc))
    s = s.cut(cyl_x(4.5, X_IN[0] - 1, X_OUT[1] + 1, 0, zc))                     # Ø9 through the lips (inner race free)
    pd, pD, pB = PIV_BRG[:3]
    s = s.cut(cyl_x(M3_CLEAR / 2, X_IN[0] - 1, X_OUT[1] + 1, PIV_Y, zc))
    s = s.cut(cyl_x(pD / 2, X_IN[0] - 0.01, X_IN[0] + pB, PIV_Y, zc))
    s = s.cut(cyl_x(pD / 2, X_OUT[1] - pB, X_OUT[1] + 0.01, PIV_Y, zc))
    for sy in (1, -1):                                                          # AMT102: 2 x M2 inserts
        s = s.cut(cyl_x(ENC_INSERT[0] / 2, X_OUT[1] - ENC_INSERT[1], X_OUT[1] + 0.01, sy * ENC_HOLE_Y, zc))
    s = s.cut(cyl_z(2.25, zc - 1, zc + hb + 1, ODO_X, SPRING_Y))                 # Ø4.5 for the M3 spring guide
    return s.removeSplitter()


def odo_wheel():
    """Printed hub: 2 flanges + O-ring groove, bosses on the 625 inner races, Ø5 bore (press + retaining compound)."""
    zc = PIV_Z
    x0, x1 = ODO_X - ODO_W / 2, ODO_X + ODO_W / 2
    gw = ODO_ORING_CS + 0.1
    s = cyl_x(ODO_HUB_D / 2, x0, x1, 0, zc)
    s = s.cut(cyl_x(ODO_HUB_D / 2 + 1, ODO_X - gw / 2, ODO_X + gw / 2, 0, zc).cut(
        cyl_x(ODO_GROOVE_D / 2, ODO_X - gw / 2, ODO_X + gw / 2, 0, zc)))
    s = s.fuse(cyl_x(ODO_BOSS[0] / 2, x0 - ODO_BOSS[1], x1 + ODO_BOSS[1], 0, zc))
    s = s.cut(cyl_x(SHAFT_D / 2 - 0.05, x0 - 2, x1 + 2, 0, zc))
    # lightening holes (6 x Ø9) - keep the hub stiff, cut the print time
    for i in range(6):
        a = math.radians(60 * i)
        s = s.cut(cyl_x(4.5, x0 - 1, x1 + 1, 15 * math.cos(a), zc + 15 * math.sin(a)))
    return s.removeSplitter()


def odo_bracket():
    """Bracket: 2 ears (pivot), back wall, spring bridge, 2 foot flanges (4 x M3 through the plate)."""
    z0, zb0 = PLATE_TOP, BRIDGE_Z0
    zb1 = zb0 + BRIDGE_T
    s = None
    for (x0, x1) in EAR_X:
        e = box(x0, x1, EAR_Y[0], EAR_Y[1], z0, zb1)
        s = e if s is None else s.fuse(e)
    s = s.fuse(box(EAR_X[0][0], EAR_X[1][1], BACK_Y[0], BACK_Y[1], z0, zb1))
    s = s.fuse(box(EAR_X[0][0], EAR_X[1][1], BRIDGE_Y[0], EAR_Y[1], zb0, zb1))
    # forward cantilever over the spring: starts at the arm's inner plate, so it stays out of the drive-wheel envelope
    s = s.fuse(box(X_IN[0] + 1.0, EAR_X[1][1], EAR_Y[1] - 0.01, BRIDGE_Y[1], zb0, zb1))
    fw, ft, (fy0, fy1) = FLANGE
    s = s.fuse(box(EAR_X[0][0] - fw, EAR_X[0][0], fy0, fy1, z0, z0 + ft))
    s = s.fuse(box(EAR_X[1][1], EAR_X[1][1] + fw, fy0, fy1, z0, z0 + ft))
    s = s.fuse(box(EAR_X[0][0] - fw, EAR_X[1][1] + fw, BACK_Y[0], fy0, z0, z0 + ft))
    s = s.cut(cyl_x(M3_CLEAR / 2, EAR_X[0][0] - 1, EAR_X[1][1] + 1, PIV_Y, PIV_Z))   # pivot M3 x 40
    s = s.cut(cyl_z(M3_CLEAR / 2, zb0 - 1, zb1 + 1, ODO_X, SPRING_Y))                # spring guide M3 x 35
    for fx in FOOT_HOLES_X:
        for fy in FOOT_HOLES_Y:
            s = s.cut(cyl_z(M3_CLEAR / 2, z0 - 1, z0 + ft + 1, fx, fy))
    return s.removeSplitter()


def caster_spacer():
    import FreeCAD as App
    doc = App.newDocument("_sp")
    sh = B0.build(doc, "Spacer", spacer_geometry(), CASTER_SPACER_T).Shape.copy()
    App.closeDocument(doc.Name)
    return sh


# ======================================================================= bought parts (plate frame, x > 0), for the assembly
def amt_placement():
    """AMT102 local frame (CDR model): shaft = local Z, base face z = -3.77, connector toward local -Y.
    Robot: shaft along +X, base face on the outer arm plate, connector pointing UP."""
    import FreeCAD as App
    m = App.Matrix(0, 0, 1, 0,
                   -1, 0, 0, 0,
                   0, -1, 0, 0,
                   0, 0, 0, 1)
    pl = App.Placement(m)
    pl.Base = _V(ENC_FACE_X + 3.77, 0, PIV_Z)
    return pl


def bought_parts():
    """Shaft, 2 x 625ZZ, 2 x F623ZZ, O-ring, spring, M3 pivot + guide screws/nuts (simplified)."""
    zc = PIV_Z
    d, D, B = BRG
    P = {}
    P["shaft_D5"] = cyl_x(SHAFT_D / 2, X_IN[0] + BRG_LIP, ENC_FACE_X + ENC_SHAFT_IN, 0, zc)
    P["bearing_625"] = (cyl_x(D / 2, X_IN[1] - B, X_IN[1], 0, zc).cut(cyl_x(d / 2, X_IN[1] - B, X_IN[1], 0, zc))).fuse(
        cyl_x(D / 2, X_OUT[0], X_OUT[0] + B, 0, zc).cut(cyl_x(d / 2, X_OUT[0], X_OUT[0] + B, 0, zc)))
    pd, pD, pB, pF, pFt = PIV_BRG
    f = []
    for x0, x1, xf in ((X_IN[0], X_IN[0] + pB, X_IN[0] - pFt), (X_OUT[1] - pB, X_OUT[1], X_OUT[1])):
        f.append(cyl_x(pD / 2, x0, x1, PIV_Y, zc).fuse(cyl_x(pF / 2, xf, xf + pFt, PIV_Y, zc)).cut(
            cyl_x(pd / 2, min(x0, xf) - 1, max(x1, xf + pFt) + 1, PIV_Y, zc)))
    P["bearing_F623"] = f[0].fuse(f[1])
    import Part
    tor = Part.makeTorus((ODO_GROOVE_D + ODO_ORING_CS) / 2, ODO_ORING_CS / 2, _V(ODO_X, 0, zc), _V(1, 0, 0))
    P["oring"] = tor
    od, l0, li = SPRING
    zs = zc + ARM_BAND
    P["spring"] = cyl_z(od / 2, zs, zs + li, ODO_X, SPRING_Y).cut(cyl_z(od / 2 - 1, zs, zs + li, ODO_X, SPRING_Y))
    zb1 = BRIDGE_Z0 + BRIDGE_T
    guide = cyl_z(1.5, zb1 - 35, zb1, ODO_X, SPRING_Y).fuse(cyl_z(2.75, zb1, zb1 + 3, ODO_X, SPRING_Y))
    nut_z = zc - 2.4 - 0.5
    guide = guide.fuse(cyl_z(3.2, nut_z, zc, ODO_X, SPRING_Y))                   # nut + washer = droop stop
    piv = cyl_x(1.5, EAR_X[0][0], EAR_X[1][1] + 6, PIV_Y, zc).fuse(
        cyl_x(2.75, EAR_X[0][0] - 3, EAR_X[0][0], PIV_Y, zc)).fuse(
        cyl_x(3.2, EAR_X[1][1], EAR_X[1][1] + 4, PIV_Y, zc))                        # M3 x 40 + nyloc
    P["screws_M3"] = guide.fuse(piv)
    return P


# ======================================================================= main
def main():
    import FreeCAD as App
    import Mesh
    import Part
    os.makedirs(OUT, exist_ok=True)
    for n in list(App.listDocuments()):
        if n.startswith("base_330_js") or n.startswith("odo_"):
            App.closeDocument(n)

    doc = App.newDocument("base_330_js")
    plate = B0.build(doc, "Base330JS", geometry(), T).Shape
    doc.saveAs(os.path.join(OUT, "base_330_js.FCStd"))
    plate.exportStep(os.path.join(OUT, "base_330_js.step"))
    B0.write_dxf(os.path.join(OUT, "base_330_js.dxf"), geometry())
    bb = plate.BoundBox
    print("plate %.1f x %.1f x %.1f, %d holes, wheel well x %.1f..%.1f y +-%.1f, notch y +-%.1f" % (
        bb.XLength, bb.YLength, bb.ZLength, len(geometry()[1]), POCKET_X0, POCKET_X1, POCKET_Y, NOTCH_Y))

    parts = {"odo_bracket": odo_bracket(), "odo_arm": odo_arm(), "odo_wheel": odo_wheel(),
             "caster_spacer": caster_spacer()}
    for name, sh in parts.items():
        assert sh.isValid() and len(sh.Solids) == 1, name
        sh.exportStep(os.path.join(OUT, name + ".step"))
        m = Mesh.Mesh()
        m.addFacets(sh.tessellate(0.05))
        m.write(os.path.join(OUT, name + ".stl"))
        print("%-14s %5.1f x %5.1f x %5.1f mm, %5.1f cm3" % (
            name, sh.BoundBox.XLength, sh.BoundBox.YLength, sh.BoundBox.ZLength, sh.Volume / 1000))
    B0.write_dxf(os.path.join(OUT, "caster_spacer.dxf"), spacer_geometry())
    print("pivot z %.2f (plate frame), bridge %.1f..%.1f, caster spacer %.1f mm, CLAP_DY %d" % (
        PIV_Z, BRIDGE_Z0, BRIDGE_Z0 + BRIDGE_T, CASTER_SPACER_T, CLAP_DY))


if __name__ in ("__main__", "base_330_js"):
    main()
