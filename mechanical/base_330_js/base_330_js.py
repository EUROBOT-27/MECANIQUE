# base_330_js.py - 336 x 260 base plate for the JSUMO JS7444 wheels + AMT102-V odometry modules (FreeCAD).
#
# Run headless:  freecadcmd base_330_js.py      (or as a macro in the FreeCAD GUI)
# Writes into CAD/: base_330_js.FCStd/.step/.dxf (plate), odo_bracket / odo_arm .step/.stl (printed),
#                   ball_holder .step/.stl, ball_shim .step/.stl/.dxf (4 x KSM15-FL ball transfer units, one per corner)
# The odometry wheel is NOT printed: it is the existing wheel of the sysRoueCodeusee units (Ø58 rim + O-ring = Ø61,
# 10 wide, Ø6 bore + M3 grub screw), model in parts/dead_wheel_sysRoueCodeusee.step.
# Then run base_330_js_assembly.py for the fit / clash / floor checks (report: base_330_js_report.txt).
#
# Same frame and outline as ../base_330 (330 x 280 x 5): X = wheel axis, Y = front/back, Z = up,
# origin = plate centre, BOTTOM face of the plate ("plate frame"). Every plate feature is mirrored about X = 0 and Y = 0.
# Printed odometry parts are built for the x > 0 side with the bracket at -Y; they are symmetric about their own
# mid-plane (x = ODO_X), so the left side uses the same parts, mirrored in place.
#
# What changed vs base_330: wheel well sized for the JSUMO wheel with an UNCERTAINTY ENVELOPE (wheel not measured
# yet), no MDF lift (hinge straight on the plate; ride height set by printed shims instead), the
# sysRoueCodeusee encoder rods replaced by a sprung swing arm that carries the AMT102-V encoder (the
# "Poenc1_102-v-2530" part of resources/CDR-2027 BlocOdometrie), and the clapets mount moved 12 mm forward.
# 2026-11-18 (Ayoub): motors 30 mm apart (were 4), 5 mm round the drive wheel envelope, odometry rebuilt smaller
# around the EXISTING sysRoueCodeusee wheel: encoder inside, wheel outside at the edge of the base, one 11 mm swing
# beam instead of two side plates. The plate grows to the width this needs (W is computed, 336).
# 2026-11-18 (Ayoub), perimeter rework: plate 336 x 260 = 1192 mm <= 1200 [GR F.3]. Motors still 30 apart, wheels
# unchanged. 5 mm safety round the JSUMO envelope for the AMT (was 3) and for the wheel well on the inside too, except
# the tongue under the hinge foot. The odometry stack moved 2 mm out and the wheel now ends 0.8 mm inside the edge.
# Back-wall profile holes follow the shorter plate (L2 - 10, as base_330).
# 2026-11-18 (Ayoub): the 2 casters (front/back, x = 0) are replaced by 4 x KSM15-FL ball transfer units, one per corner,
# through a Ø25 plate hole, hung from a printed holder (M8 stud + nut) with a printed shim ring that sets the height.

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

# ======================================================================= plate (L, T as base_330; W computed below)
L, T = 260.0, 5.0           # base_330: 280. 2 x (336 + 260) = 1192 <= 1200 [GR F.3]
L2 = L / 2

# ======================================================================= JSUMO JS7444 drive wheel (D-004) - NOT MEASURED
# Shop data: "74 mm" (mikroelectron), another page says 77 x 44. Width 44 is from the name. Hub / bore unknown.
# The plate is cut for the ENVELOPE (MAX values); the ride height is computed with the NOMINAL value and corrected with
# the ball-unit shims once the real wheel is measured.
WHEEL_D_NOM = 74.0
WHEEL_D_MIN = 72.0          # worn tyre / smaller than announced
WHEEL_D_MAX = 80.0          # 77 (other shop page) + 3 mm margin
WHEEL_W_NOM = 44.0
WHEEL_W_MAX = 48.0          # width + hub boss that may stick out
WHEEL_IN_TOL = 2.0          # +/- where the hub really ends up on the shaft
# Drive chain = base_330 (same Pololu 37D + same hinge brackets), moved out so the motors are MOTOR_GAP apart
MOTOR_GAP = 30.0            # between the two motor back ends (base_330: 4). Ayoub 2026-11-18: "at least 3-5 cm"
MOTOR_SHIFT = (MOTOR_GAP - 4.0) / 2                                  # 13: every drive part moves out by this
MOTOR_BACK_X = 2.0 + MOTOR_SHIFT                                     # back end of the motor (base_330: 2)
HINGE_X0 = 18.9 + MOTOR_SHIFT                                        # inner end of the hinge foot
MOTOR_FACE_X = 61.5 + MOTOR_SHIFT                                    # inner face of the hinge motor plate
HINGE_PLATE_OUT = 64.7 + MOTOR_SHIFT                                 # outer face of the hinge motor plate
WHEEL_IN_NOM = 68.0 + MOTOR_SHIFT                                    # 81: inner face of the wheel (hub on the 6 mm D shaft)
SHAFT_ABOVE_SEAT = 20.5     # motor shaft above the hinge seat (base_330)
LIFT_H = 0.0                # no MDF lift any more: hinge straight on the plate (Ø74 wheel -> plate 11.5 above the floor)
HINGE_D, HINGE_X, HINGE_Y = 3.5, (26.9 + MOTOR_SHIFT, 50.9 + MOTOR_SHIFT), 15.0

# wheel well (through the plate): WHEEL_CLEAR all round the worst-case envelope, except on the inside where the
# hinge foot sits on the plate (the edge stays 0.3 past the hinge plate: 3.3 mm to the nominal wheel)
WHEEL_CLEAR = 5.0
ENV_X0 = WHEEL_IN_NOM - WHEEL_IN_TOL                                 # 79
ENV_X1 = WHEEL_IN_NOM + WHEEL_IN_TOL + WHEEL_W_MAX                   # 131: worst-case outer face
POCKET_X0 = HINGE_PLATE_OUT + 0.3                                    # 78: only under the hinge foot (tongue)
POCKET_XIN = ENV_X0 - WHEEL_CLEAR                                    # 74: inner edge beside the tongue
TONGUE_Y = 21.0                                                      # hinge foot y +-20 (holes at +-15)
POCKET_X1 = ENV_X1 + WHEEL_CLEAR                                     # 136
POCKET_Y = WHEEL_D_MAX / 2 + WHEEL_CLEAR                             # 45

# no strap slots (base_330 had 2 across the motors, used to strap the MDF lift): removed 2026-11-18 at Ayoub's request,
# the middle of the plate only keeps the 8 hinge holes
# corner holes (side-wall profiles), back wall profiles: as base_330
CORNER_D, CORNER_INSET = 6.35, 11.0
PROF_X, PROF_Y, PROF_D = 100.0, L2 - 10.0, 5.5   # 20x20 profile flush with the edge

# clapets v7 module A: same 4-hole pattern as base_330, but fixed with 4 x M3 (Ayoub, 2026-11-18): Ø3.4 = M3
# clearance (ISO 273 medium; base_330 had Ø4.8 for M4). The socle holes stay Ø4.4, so M3 takes up the socle's print error;
# use a washer under the head on the socle. Module moved CLAP_DY forward. The socle starts 8.5 mm behind its holes'
# y = 18 row (module frame y 8.5) -> socle front at CLAP_DY + 8.5 must clear the Ø80 wheel envelope (y 40) by >= 3.
CLAP_X, CLAP_Y, CLAP_D = 63.0, (18.0, 53.0), 3.4
CLAP_SOCLE_Y0 = 8.5
CLAP_DY = math.ceil(WHEEL_D_MAX / 2 + 3.0 - CLAP_SOCLE_Y0)          # 35 (base_330: 23)

# ======================================================================= odometry module (AMT102-V on a swing arm)
# Odometry wheel = the EXISTING wheel of the sysRoueCodeusee units (not printed). Measured on its SolidWorks model
# (D:/ensi/sysRoueCodeusee.SLDPRT, exported to parts/dead_wheel_sysRoueCodeusee.step, frame: axis X, hub face x = 0):
# Ø58 rim, O-ring tyre Ø61 at x 6..9 (contact plane x 7.5), width 10, Ø6 bore, Ø12 hub boss with an M3 grub screw.
DW_R = 30.5                 # tyre radius
DW_W = 10.0
DW_CONTACT = 7.5            # contact plane from the hub face
ODO_SQUASH = 0.3            # O-ring flattening under the spring force
ODO_R = DW_R - ODO_SQUASH
SHAFT_D = 6.0               # wheel bore Ø6 (grub screw) + AMT102 Ø6 sleeve (in the AMT kit)
BRG = (6.0, 15.0, 5.0)      # 696ZZ: d, D, B (2 per arm, side by side)
BRG_LIP = 1.0               # lip on the encoder side (bore Ø12: e-clip on the shaft, outer race stop)
LIP_BORE = 12.0
AMT_LEN = 9.2               # AMT102-V body along the shaft from its mounting face (CDR model)
AMT_CLEAR = WHEEL_CLEAR     # AMT <-> worst-case drive wheel envelope (5, was 3)
# x stack, from the inside out: drive envelope | AMT_CLEAR | AMT | arm beam (2 x 696 + lip) | shim 1 | wheel | edge
ENC_FACE_X = ENV_X1 + AMT_CLEAR + AMT_LEN                            # 143.2: AMT mounting face = inner face of the beam
ARM_T = 2 * BRG[2] + BRG_LIP                                         # 11
ARM_X = (ENC_FACE_X, ENC_FACE_X + ARM_T)                             # 143.2..154.2
ARM_XC = (ARM_X[0] + ARM_X[1]) / 2
SHIM_T = 1.0                # M6 shim washer 6 x 10 x 1 between the outer 696 inner race and the wheel hub
DW_X0 = ARM_X[1] + SHIM_T                                            # 155.2: wheel hub face
DW_X1 = DW_X0 + DW_W                                                 # 165.2: outer face of the wheel
ODO_X = DW_X0 + DW_CONTACT                                           # 162.7: contact plane -> track 325.4
EDGE_CLEAR = 0.8            # wheel outer face <-> plate outline (in the open notch; was 2.5)
ENC_SHAFT_IN = 8.0          # shaft past the AMT mounting face (CDR model: cap inside at ~9.0)
ENC_HOLE_Y = 9.53           # AMT102 base holes (2 x, 19.05 apart, from the CDR model)
ENC_PILOT = (1.7, 6.0)      # M2 x 8 self-tapping screw pilot Ø x depth (no inserts: 1.2 mm wall to the 696 seat)

# plate width = what the odometry stack needs (330 before)
W = 2.0 * math.ceil(DW_X1 + EDGE_CLEAR - 1e-6)                            # 336
W2 = W / 2

# Arm: pivot axis // X (// drive axle) -> the arm swings in the YZ plane, so the odometry TRACK never changes.
PIV_Y = -60.0               # arm length 60
PLATE_TOP = T
FLOOR_NOM = -(WHEEL_D_NOM / 2 - SHAFT_ABOVE_SEAT - LIFT_H - T)       # floor in the plate frame (-11.5)
PIV_Z = FLOOR_NOM + ODO_R   # arm horizontal with the nominal wheel
ARM_BAND = 6.0              # beam is PIV_Z +/- 6 between the hub and the axle boss
AXLE_BOSS = (13.5, 11.0, 4.0)   # half y, half z, corner R of the boss round the axle (2 x 696 + the AMT screws)
HUB_D, PIV_BRG = 16.0, (3.0, 10.0, 4.0, 11.5, 1.0)   # F623ZZ: d, D, B, flange Ø, flange t (2 per arm)
SPRING_Y = -41.0            # spring sits on the top of the beam, 19 mm from the pivot
SPRING = (8.0, 25.0, 20.0)  # OD, free length, installed length (Ender bed-levelling spring, 4 in hand)
ARM_DROOP = 5.0             # wheel may drop 5 mm below the nominal floor before the nut stops it
DROOP_GAP = ARM_DROOP * (SPRING_Y - PIV_Y) / (0 - PIV_Y)             # 1.6: nut gap under the beam at the spring axis
# Bracket (one printed part, bolted with 3 x M3 x 12 through the plate)
EAR_T = 6.0
EAR_X = ((ARM_X[0] - 1.0 - EAR_T, ARM_X[0] - 1.0), (ARM_X[1] + 1.0, ARM_X[1] + 1.0 + EAR_T))  # 136.2..142.2, 155.2..161.2
EAR_Y = (-74.0, -46.0)
BACK_Y = (-78.0, -74.0)
BRIDGE_Y = (-78.0, -34.0)
BRIDGE_T = 5.0
BRIDGE_Z0 = PIV_Z + ARM_BAND + SPRING[2]
FOOT_T = 4.0
FLANGE = (6.0, (-74.0, -50.0))          # inner flange: width inside the inner ear, y range
MID_FOOT_Y = (-74.0, -68.5)             # foot between the ears, behind the pivot hub (hub reaches y -68)
FOOT_HOLES = ((EAR_X[0][0] - FLANGE[0] / 2, -54.0), (EAR_X[0][0] - FLANGE[0] / 2, -70.0),
              (ARM_XC, (MID_FOOT_Y[0] + MID_FOOT_Y[1]) / 2))
M3_CLEAR = 3.4
NOTCH_Y = 32.5              # plate notch round the odometry wheel + encoder (x POCKET_X1 .. edge): Ø61 chord + 3

# ======================================================================= 4 x ball transfer unit KSM15-FL (one per corner)
# Shop drawing: body Ø24, ball Ø15.875 sticking out 4, 21 from the ball top to the body base, M8 x 18 stud, 40 kg each.
# Mounted ball DOWN: the body goes through a Ø25 plate hole and is hung from a printed holder on the plate top
# (stud through the holder roof, washer + M8 nut on top). The unit is 21 tall but the plate bottom is only 11.5 above
# the floor (Ø74), so it cannot hang under the plate. A printed shim ring between the body base and the roof sets the
# ball BALL_GAP above the floor for the real wheel diameter (the roof is placed for the smallest wheel, Ø72 -> shim 0).
BALL_D, BALL_BODY_D, BALL_H, BALL_STUD = 15.875, 24.0, 21.0, (8.0, 18.0)
BALL_OUT = 4.0              # ball below the body face
BALL_X, BALL_Y = 130.0, 105.0   # corners: 5 mm from the odometry bracket (y -78), 5 from the corner holes, 25 from the edges
BALL_GAP = 2.0              # ball above the floor (drive wheels carry the robot, like the old casters)
BALL_HOLE = 25.0            # plate hole (body Ø24 + 1)
HOLDER = dict(tube_od=32.0, bore=24.6, roof=5.0, flange_d=44.0, flange_t=4.0, screw_r=19.0, stud_hole=8.5)
HOLDER_SCREW_A = (0.0, 120.0, 240.0)    # 3 x M3 x 12 through the plate, nut + washer under it


def plate_top_height(wheel_d):
    """Plate top above the floor for a given drive wheel diameter."""
    return wheel_d / 2 - SHAFT_ABOVE_SEAT - LIFT_H


# body base above the plate top for a wheel diameter; the holder roof sits at the highest one (smallest wheel)
def ball_base_above_top(wheel_d):
    return BALL_GAP + BALL_H - plate_top_height(wheel_d)


HOLDER_IN = ball_base_above_top(WHEEL_D_MIN)            # 7.5: roof underside above the plate top
BALL_STUD_FREE = BALL_STUD[1] - HOLDER["roof"] - 1.6 - 6.5   # stud left for the shim (washer 1.6 + nut 6.5): 4.9


def ball_shim_t(wheel_d):
    return round(HOLDER_IN - ball_base_above_top(wheel_d), 2)


BALL_SHIM_T = ball_shim_t(WHEEL_D_NOM)                  # 1.0 for Ø74 (Ø72: 0, Ø77: 2.5, Ø80: 4.0)
assert 0 <= ball_shim_t(WHEEL_D_MAX) <= BALL_STUD_FREE


# ======================================================================= plate geometry
def geometry():
    P0, P1, PY, NY, PI, TY = POCKET_X0, POCKET_X1, POCKET_Y, NOTCH_Y, POCKET_XIN, TONGUE_Y
    assert HINGE_X[1] + HINGE_D < PI < HINGE_PLATE_OUT < P0 < P1 < W2 and HINGE_Y < TY < NY < PY < L2
    right = [
        ("line", (0, -L2), (W2, -L2)),
        ("line", (W2, -L2), (W2, -NY)),
        ("line", (W2, -NY), (P1, -NY)),
        ("line", (P1, -NY), (P1, -PY)),
        ("line", (P1, -PY), (PI, -PY)),
        ("line", (PI, -PY), (PI, -TY)),
        ("line", (PI, -TY), (P0, -TY)),
        ("line", (P0, -TY), (P0, TY)),
        ("line", (P0, TY), (PI, TY)),
        ("line", (PI, TY), (PI, PY)),
        ("line", (PI, PY), (P1, PY)),
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
    quad(BALL_X, BALL_Y, BALL_HOLE)
    for a in HOLDER_SCREW_A:
        quad(BALL_X + HOLDER["screw_r"] * math.cos(math.radians(a)),
             BALL_Y + HOLDER["screw_r"] * math.sin(math.radians(a)), M3_CLEAR)
    for cy in CLAP_Y:
        quad(CLAP_X, cy + CLAP_DY, CLAP_D)
    quad(PROF_X, PROF_Y, PROF_D)
    for fx, fy in FOOT_HOLES:
        quad(fx, -fy, M3_CLEAR)
    return right + left, circles, []


def shim_geometry():
    r0, r1 = BALL_BODY_D / 2, HOLDER["stud_hole"] / 2
    outline = [("arc", (0.0, 0.0), r0, 0, 180), ("arc", (0.0, 0.0), r0, 180, 360)]
    return outline, [(0.0, 0.0, 2 * r1)], []


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
    """Swing beam (one 11 mm part): 2 x 696 seats from the wheel side, 1 mm lip on the encoder side, AMT102 pilot
    holes on the inner face, pivot hub (2 x F623), spring seat on the top + guide hole."""
    zc, hb = PIV_Z, ARM_BAND
    by, bz, br = AXLE_BOSS
    x0, x1 = ARM_X
    s = box(x0, x1, PIV_Y, 0.0, zc - hb, zc + hb).fuse(rrect_x(x0, x1, 0.0, zc, by, bz, br))
    s = s.fuse(cyl_x(HUB_D / 2, x0, x1, PIV_Y, zc))
    d, D, B = BRG
    s = s.cut(cyl_x(D / 2, x0 + BRG_LIP, x1 + 0.01, 0, zc))                      # 2 x 696 seat, from the wheel side
    s = s.cut(cyl_x(LIP_BORE / 2, x0 - 1, x0 + BRG_LIP + 0.01, 0, zc))            # lip: Ø12 (e-clip + inner race free)
    pd, pD, pB = PIV_BRG[:3]
    s = s.cut(cyl_x(M3_CLEAR / 2, x0 - 1, x1 + 1, PIV_Y, zc))
    s = s.cut(cyl_x(pD / 2, x0 - 0.01, x0 + pB, PIV_Y, zc))
    s = s.cut(cyl_x(pD / 2, x1 - pB, x1 + 0.01, PIV_Y, zc))
    for sy in (1, -1):                                                          # AMT102: 2 x M2 self-tapping
        s = s.cut(cyl_x(ENC_PILOT[0] / 2, x0 - 0.01, x0 + ENC_PILOT[1], sy * ENC_HOLE_Y, zc))
    s = s.cut(cyl_z(2.25, zc - hb - 1, zc + hb + 1, ARM_XC, SPRING_Y))           # Ø4.5 for the M3 spring guide
    return s.removeSplitter()


def odo_bracket():
    """Bracket: 2 ears (pivot), back wall, spring bridge, inner flange + middle foot (3 x M3 through the plate)."""
    z0, zb0 = PLATE_TOP, BRIDGE_Z0
    zb1 = zb0 + BRIDGE_T
    s = None
    for (x0, x1) in EAR_X:
        e = box(x0, x1, EAR_Y[0], EAR_Y[1], z0, zb1)
        s = e if s is None else s.fuse(e)
    s = s.fuse(box(EAR_X[0][0], EAR_X[1][1], BACK_Y[0], BACK_Y[1], z0, zb1))
    s = s.fuse(box(EAR_X[0][0], EAR_X[1][1], BRIDGE_Y[0], BRIDGE_Y[1], zb0, zb1))   # bridge over the spring
    fw, (fy0, fy1) = FLANGE
    s = s.fuse(box(EAR_X[0][0] - fw, EAR_X[0][0], fy0, fy1, z0, z0 + FOOT_T))
    s = s.fuse(box(EAR_X[0][1] - 0.01, EAR_X[1][0] + 0.01, MID_FOOT_Y[0], MID_FOOT_Y[1], z0, z0 + FOOT_T))
    s = s.cut(cyl_x(M3_CLEAR / 2, EAR_X[0][0] - 1, EAR_X[1][1] + 1, PIV_Y, PIV_Z))   # pivot M3 x 30
    s = s.cut(cyl_z(M3_CLEAR / 2, zb0 - 1, zb1 + 1, ARM_XC, SPRING_Y))               # spring guide M3 x 40
    for fx, fy in FOOT_HOLES:
        s = s.cut(cyl_z(M3_CLEAR / 2, z0 - 1, z0 + FOOT_T + 1, fx, fy))
    return s.removeSplitter()


def ball_holder(x=BALL_X, y=BALL_Y):
    """Printed holder (plate frame, at one corner): flange on the plate top with 3 x M3, tube round the ball body,
    roof with the M8 stud hole. The body slides in from below through the Ø25 plate hole."""
    H = HOLDER
    z0 = PLATE_TOP
    zr = z0 + HOLDER_IN
    s = cyl_z(H["flange_d"] / 2, z0, z0 + H["flange_t"], x, y).fuse(cyl_z(H["tube_od"] / 2, z0, zr + H["roof"], x, y))
    s = s.cut(cyl_z(H["bore"] / 2, z0 - 1, zr, x, y))
    s = s.cut(cyl_z(H["stud_hole"] / 2, zr - 1, zr + H["roof"] + 1, x, y))
    for a in HOLDER_SCREW_A:
        sx = x + H["screw_r"] * math.cos(math.radians(a))
        sy = y + H["screw_r"] * math.sin(math.radians(a))
        s = s.cut(cyl_z(M3_CLEAR / 2, z0 - 1, z0 + H["flange_t"] + 1, sx, sy))
    return s.removeSplitter()


def ball_shim(t=None):
    t = BALL_SHIM_T if t is None else t
    return cyl_z(BALL_BODY_D / 2, 0, t, 0, 0).cut(cyl_z(HOLDER["stud_hole"] / 2, -1, t + 1, 0, 0))


def ball_unit(x, y, wheel_d=WHEEL_D_NOM):
    """KSM15-FL placeholder (plate frame), ball down, body base at the height for this wheel diameter."""
    zb = PLATE_TOP + ball_base_above_top(wheel_d)          # body base
    zf = zb - (BALL_H - BALL_OUT)                          # body face (ball side)
    s = cyl_z(BALL_BODY_D / 2, zf, zb, x, y)
    import Part
    s = s.fuse(Part.makeSphere(BALL_D / 2, _V(x, y, zf - BALL_OUT + BALL_D / 2)))
    return s.fuse(cyl_z(BALL_STUD[0] / 2, zb, zb + BALL_STUD[1], x, y))


# ======================================================================= bought parts (plate frame, x > 0), for the assembly
def amt_placement():
    """AMT102 local frame (CDR model): shaft = local Z, base face z = -3.77, connector toward local -Y.
    Robot: shaft along X, base face on the INNER face of the swing beam, body toward the robot centre (-X),
    connector pointing UP."""
    import FreeCAD as App
    m = App.Matrix(0, 0, -1, 0,
                   1, 0, 0, 0,
                   0, -1, 0, 0,
                   0, 0, 0, 1)
    pl = App.Placement(m)
    pl.Base = _V(ENC_FACE_X - 3.77, 0, PIV_Z)
    return pl


def dead_wheel_placement():
    """parts/dead_wheel_sysRoueCodeusee.step frame (axis X, hub face x = 0) -> plate frame, right side."""
    import FreeCAD as App
    return App.Placement(_V(DW_X0, 0, PIV_Z), App.Rotation())


def bought_parts():
    """Ø6 shaft, 2 x 696ZZ, e-clip, shim, 2 x F623ZZ, spring, M3 pivot + guide screws/nuts (simplified)."""
    zc = PIV_Z
    d, D, B = BRG
    x0, x1 = ARM_X
    P = {}
    P["shaft_D6"] = cyl_x(SHAFT_D / 2, ENC_FACE_X - ENC_SHAFT_IN, DW_X1, 0, zc)
    ring = lambda r0, r1, a, b: cyl_x(r1, a, b, 0, zc).cut(cyl_x(r0, a, b, 0, zc))
    P["bearing_696"] = ring(d / 2, D / 2, x0 + BRG_LIP, x0 + BRG_LIP + B).fuse(ring(d / 2, D / 2, x1 - B, x1))
    P["eclip_shim"] = ring(2.5, 5.5, x0 + 0.3, x0 + 1.0).fuse(ring(d / 2, 5.0, x1, x1 + SHIM_T))   # DIN 6799-5 + 6x10x1
    pd, pD, pB, pF, pFt = PIV_BRG
    f = []
    for a, b, xf in ((x0, x0 + pB, x0 - pFt), (x1 - pB, x1, x1)):
        f.append(cyl_x(pD / 2, a, b, PIV_Y, zc).fuse(cyl_x(pF / 2, xf, xf + pFt, PIV_Y, zc)).cut(
            cyl_x(pd / 2, min(a, xf) - 1, max(b, xf + pFt) + 1, PIV_Y, zc)))
    P["bearing_F623"] = f[0].fuse(f[1])
    od, l0, li = SPRING
    zs = zc + ARM_BAND
    P["spring"] = cyl_z(od / 2, zs, zs + li, ARM_XC, SPRING_Y).cut(cyl_z(od / 2 - 1, zs, zs + li, ARM_XC, SPRING_Y))
    zb1 = BRIDGE_Z0 + BRIDGE_T
    nut_top = zc - ARM_BAND - DROOP_GAP
    guide = cyl_z(1.5, nut_top - 3.5, zb1, ARM_XC, SPRING_Y).fuse(cyl_z(2.75, zb1, zb1 + 3, ARM_XC, SPRING_Y))
    guide = guide.fuse(cyl_z(3.2, nut_top - 2.9, nut_top, ARM_XC, SPRING_Y))       # nut + washer = droop stop
    piv = cyl_x(1.5, EAR_X[0][0], EAR_X[1][1] + 4, PIV_Y, zc).fuse(
        cyl_x(2.75, EAR_X[0][0] - 3, EAR_X[0][0], PIV_Y, zc)).fuse(
        cyl_x(3.2, EAR_X[1][1], EAR_X[1][1] + 4, PIV_Y, zc))                        # M3 x 30 + nyloc
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

    for stale in ("odo_wheel.step", "odo_wheel.stl"):       # the printed wheel is gone (existing wheel reused)
        if os.path.exists(os.path.join(OUT, stale)):
            os.remove(os.path.join(OUT, stale))
    for stale in ("caster_spacer.step", "caster_spacer.stl", "caster_spacer.dxf"):   # casters replaced by ball units
        if os.path.exists(os.path.join(OUT, stale)):
            os.remove(os.path.join(OUT, stale))
    hold = ball_holder()
    hold.translate(_V(-BALL_X, -BALL_Y, -PLATE_TOP))          # holder exported at the origin, flange on z = 0
    parts = {"odo_bracket": odo_bracket(), "odo_arm": odo_arm(), "ball_holder": hold}
    if BALL_SHIM_T >= 0.4:
        parts["ball_shim"] = ball_shim()
    for name, sh in parts.items():
        assert sh.isValid() and len(sh.Solids) == 1, name
        sh.exportStep(os.path.join(OUT, name + ".step"))
        m = Mesh.Mesh()
        m.addFacets(sh.tessellate(0.05))
        m.write(os.path.join(OUT, name + ".stl"))
        print("%-14s %5.1f x %5.1f x %5.1f mm, %5.1f cm3" % (
            name, sh.BoundBox.XLength, sh.BoundBox.YLength, sh.BoundBox.ZLength, sh.Volume / 1000))
    B0.write_dxf(os.path.join(OUT, "ball_shim.dxf"), shim_geometry())
    print("pivot z %.2f (plate frame), bridge %.1f..%.1f, ball shim %.1f mm (holder roof %.1f above the plate top), CLAP_DY %d" % (
        PIV_Z, BRIDGE_Z0, BRIDGE_Z0 + BRIDGE_T, BALL_SHIM_T, HOLDER_IN, CLAP_DY))
    print("W %.0f, motor gap %.0f, pocket x %.1f..%.1f, AMT x %.1f..%.1f, beam %.1f..%.1f, wheel %.1f..%.1f, track %.1f" % (
        W, MOTOR_GAP, POCKET_X0, POCKET_X1, ENC_FACE_X - AMT_LEN, ENC_FACE_X, ARM_X[0], ARM_X[1], DW_X0, DW_X1, 2 * ODO_X))


if __name__ in ("__main__", "base_330_js"):
    main()
