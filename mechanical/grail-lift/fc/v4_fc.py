# v4_fc.py - Grail lift v4 = v3 with the T8 lead screw replaced by the Two Trees printer's BELT axis (Maatoug + Claude,
# 2026-11-20). Everything else (column, carriage, arm, flip, roof slot, path planner) is v3's: see v3_fc.py.
# Belt drive (parts from mechanical/resources/two-trees-bluer-v2-parts/, the ones on Maatoug's bench):
#   * NEMA17 LYING on the roof (where v3's motor stood), shaft along -y, GT2 20T pulley above the roof;
#   * open GT2 6 mm belt down through a roof slot to the printer's X-axis TENSIONER (knob + 20T idler) low in the robot,
#     beside the drive motor; both belt ends in the printer's Y belt bracket, bolted to a printed arm on the carriage;
#   * NOT self-locking (unlike the T8): if the stepper is unpowered the carriage slides down (see the report).
# Translation guide (2026-11-20, no aluminium profile): the 2020 column + printed slider shoes are replaced by 2 Ø8 smooth
#   rods (lab): rod 1 carries 2 SCS8UU blocks (lab has 3; catalogue size, MEASURE), rod 2 a printed bushing that only
#   stops the turning. Rods held by a printed base above the wheel and a printed top clamp above the roof.
# v3 header, still true for v4:
# v3_fc.py - Grail lift v3, COMPACT (Maatoug + Claude, 2026-11-10). Fits on a SIDE face of the robot, in the column
# above the drive wheel, between the front and back clapets modules (robot layout: mechanical/robot/fc/layout.py).
# What changed from v2 (which needed a whole driving face + a 115 x 150 bay):
#   * the magnet grips the Grail's TOP face (magnet face down when the arm points out): picked from above, so the robot
#     only has to park with the Grail under the arm (+-25 mm), no driving into it;
#   * flip 180 deg over the side edge -> the Grail lands upside down ON the magnet, through a roof slot; the lift goes
#     down 12 mm and the arm ends below the roof surface: Grail free on the roof, magnet below it (no 350 mm problem at
#     the release, CDC D2 no longer applies);
#   * lift travel ~200 mm only, carriage = plate + 4 V-wheels on a 2020 column, driven by a GT2 belt from a NEMA17
#     fixed low in the robot (the moving block carries no motor), arm = MG996R in the club's steel U bracket.
# Run (from mechanical/grail-lift): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v4_fc.py   (~4 min)
#   -> CAD_FC/GRAIL_LIFT_V4.FCStd, joints_v4.json, v4_report.txt, STEP/GRAIL_LIFT_V4.step
# Local frame (like v2): x = outward normal of the side face (face plane x = 0, robot inside x < 0), y along the face,
# z up, table z = 0. In the robot (left side): robot Y = HALF_Y + x * side, robot X = GRAIL_X - y * side.
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "robot", "fc")))
import FreeCAD as App
import Import
import Part
from FreeCAD import Vector

import grail_common as C

sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "resources", "linear-motion")))
import linear_parts as LP                                    # SCS8UU catalogue model (lab parts)
from layout import L, wheel_center_y


class G:
    H_LIM = L.H_MAX - 2.0
    ROOF = L.ROOF
    # Grail: 80 x 80 footprint, 86 tall, steel plate on its TOP face (it ends upside down on the roof)
    GX, GY, GH, PLATE_T = 80.0, 80.0, 86.0, 1.5
    # flip axis (MG996R shaft) along y, at x = X_A; servo lying, body inward
    X_A = -19.0
    L_U, T_U, U_HALF_W, U_DISC_R = 45.0, 2.5, 13.0, 13.0          # U bracket (ESTIMATED, measure)
    HORN_TOP, SV_BOT, PIVOT_GAP = 19.4, 28.3, 3.7
    Y_S = -7.5                                                   # servo ear plane: bracket y -42 .. 14.4 (door units at |y| 44)
    MAG_D, MAG_T = 27.0, 20.0                                    # electromagnet Ø27 x 20 (5 kg)
    L_PLATE = 2.5                                                # L plate carrying the magnet off the strip
    T_OFF = 20.0         # magnet centre 20 below the arm line at the pick pose: at mid-flip its face is outside the side face
    Y_MAG = -30.0        # magnet / Grail centre plane: Grail lands clear of the carriage plate (y >= 15)
    # carriage: column 2020 beside the bracket, V-wheels on its +-x faces, plate between column and bracket
    COL_X, COL_Y = (-42.0, -22.0), (22.0, 42.0)   # v3's 2020 column (not used in v4: rods instead)
    # rods: rod 1 + 2 SCS8UU (base on the carriage plate at y 21, rod axis 11 above it), rod 2 + printed bushing
    ROD1_X, ROD2_X, ROD_Y = -35.0, -9.5, 32.0
    ROD_Z = (L.WHEEL_D + 2.0, 346.0)              # same span as v3's column (through the roof bay, top clamp above it)
    SCS = (30.0, 34.0, 22.0, 11.0)                # SCS8UU length, width, height, rod axis height (catalogue)
    SCS_DZ = -20.0                                # 2 blocks from ZA-20 to ZA+40
    BUSH_DZ = (5.0, 35.0)                         # rod 2 bushing about the flip axis
    PLATE_Y = (15.0, 21.0)
    CAR_DZ = (-20.0, 40.0)        # carriage plate about the flip axis: it sits beside the bracket (y 15..21), so it may
                                  # pass the axis; bottom >= wheel top at the pick pose
    SLIDE_DZ = ((-18.0, -3.0), (28.0, 43.0))   # printed slider shoes in the column's +-x slots (2 per face), about the axis
    BAR_Z = (-20.0, -13.0)        # cradle bar under the arm sweep
    # lift drive (v4): belt loop in the plane y = BELT_Y, pulley axes along y at x = BELT_X; the run on the carriage side
    # (x = BELT_X + PITCH_R) is clamped in the printer's belt bracket, the other run (BELT_X - PITCH_R) passes free.
    # Same corner as v3's screw: clear of the carriage, the arm sweep (y < 17), the door units (y > 44 for x > -84).
    BELT_X = -86.35
    BELT_Y = 30.0                 # belt centre plane (GT2, 6 wide)
    PITCH_R = 6.366               # GT2 20T pitch radius (40 mm / pi / 2)
    BELT_T = 1.4                  # belt thickness (band +-0.7 about the pitch line, simplified)
    PULLEY_Z = L.ROOF + 21.15     # motor lying on the roof (42.3 body): shaft axis 21.15 above the roof surface
    MOTOR_FACE_Y = 42.8           # NEMA17 face; boss 2 mm, pulley hub 8 + teeth 5.6 + flange 2.4 towards -y
    IDLER_Z = 53.0                # tensioner idler axis: tensioner top (plate) at +35.9, knob down to -37
    ARM_DZ = (-20.0, -5.0)        # printed arm carriage -> belt bracket, about the flip axis (v3's nut arm height)
    ARM_Y = (34.5, 41.6)          # above the belt (y 27..33), under the bracket's flange (41.7..43.7)
    BRACKET_DZ = -10.0            # centre of the belt bracket (28 tall) about the flip axis
    Z_LIFT_MAX = 283.0            # same top as v3 (bracket top then at 287, 31 mm under the pulley)
    SLOT_MARGIN = 3.0


Y_M = G.Y_MAG                                        # magnet / Grail centre plane (bracket centre: G.Y_S - 6.3)
FLANGE_A = (G.Y_S + G.HORN_TOP, G.Y_S + G.HORN_TOP + G.T_U)
FLANGE_B = (G.Y_S - G.SV_BOT - G.PIVOT_GAP - G.T_U, G.Y_S - G.SV_BOT - G.PIVOT_GAP)
XA = G.X_A
X_STRIP = XA + G.L_U
R_MAG = G.L_U + G.T_U + G.L_PLATE + G.MAG_D / 2      # magnet centre radius (on the arm line)
Z_PICK = G.GH + G.MAG_T / 2 + G.T_OFF                # axis height when the magnet face sits on the Grail top
ZA = Z_PICK                                          # model is built at the PICK pose (flip 0, arm pointing out)


TT = os.path.normpath(os.path.join(HERE, "..", "..", "resources", "two-trees-bluer-v2-parts"))
REF_NEMA17 = os.path.normpath(os.path.join(HERE, "..", "..", "clapets", "clapets-v5", "CAD_FC", "STEP", "REF_NEMA17.step"))
GUIDE_FIXED = ["GUIDE_RODS_D8", "ROD_BASE_printed", "ROD_TOP_CLAMP_printed"]
DRIVE_CHECKED = ["NEMA17_BELT", "PULLEY_GT2_20T", "IDLER_GT2_20T", "TENSIONER_X_printer", "BELT_GT2_free_run"]
BELT_EXPECTED = {frozenset(p) for p in (
    ("CAR_BELT_ARM", "BELT_CLAMP_bracket"), ("CAR_BELT_ARM", "SCS8UU_x2"), ("BELT_CLAMP_bracket", "BELT_GT2_loop"),
    ("GUIDE_RODS_D8", "SCS8UU_x2"), ("GUIDE_RODS_D8", "ROD2_BUSHING_printed"), ("SCS8UU_x2", "CAR_PLATE"),
    ("ROD2_BUSHING_printed", "CAR_PLATE"), ("SCS8UU_x2", "ROD2_BUSHING_printed"),
    ("GUIDE_RODS_D8", "ROD_BASE_printed"), ("GUIDE_RODS_D8", "ROD_TOP_CLAMP_printed"),
    ("CAR_BELT_ARM", "BELT_GT2_loop"))}


def belt_drive():
    """Fixed belt-drive parts (printer parts placed in the lift frame). Pulleys are measured stand-ins (the toothed
    meshes are 100 MB as STEP): idler 20T = Ø17 flanges, Ø12.2 teeth x 6, bore 5; motor pulley = hub Ø15.5 x 8,
    teeth Ø12.2 x 5.6, flange Ø15.5 x 2.4."""
    bx, by, pr, t = G.BELT_X, G.BELT_Y, G.PITCH_R, G.BELT_T / 2
    out = {}
    # NEMA17 (clapets-v5 library model: shaft +z at (0, 33.5), face z = 46) lying, shaft -> -y
    mot = C.read_step(REF_NEMA17)
    out["NEMA17_BELT"] = C.place_shape(mot, ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
                                       (bx, G.MOTOR_FACE_Y + 46.0, G.PULLEY_Z - 33.5))
    yf = G.MOTOR_FACE_Y - 2.0
    pul = C.cyl(7.75, 8.0, (bx, yf - 8.0, G.PULLEY_Z), (0, 1, 0))
    pul = pul.fuse([C.cyl(6.1, 5.6, (bx, yf - 13.6, G.PULLEY_Z), (0, 1, 0)),
                    C.cyl(7.75, 2.4, (bx, yf - 16.0, G.PULLEY_Z), (0, 1, 0))])
    out["PULLEY_GT2_20T"] = pul.cut(C.cyl(2.5, 20, (bx, yf - 18, G.PULLEY_Z), (0, 1, 0))).removeSplitter()
    idl = C.cyl(6.1, 6.0, (bx, by - 3.0, G.IDLER_Z), (0, 1, 0))
    idl = idl.fuse([C.cyl(8.5, 1.3, (bx, by - 4.3, G.IDLER_Z), (0, 1, 0)),
                    C.cyl(8.5, 1.3, (bx, by + 3.0, G.IDLER_Z), (0, 1, 0))])
    out["IDLER_GT2_20T"] = idl.cut(C.cyl(2.5, 12, (bx, by - 6, G.IDLER_Z), (0, 1, 0))).removeSplitter()
    # printer X tensioner (plate + body + slider + knob screw), printer coords -> local: x_p -> z, y_p -> y, z_p -> -x;
    # its idler centre (printer -72.66, 247.15, 235.55) on (BELT_X, BELT_Y, IDLER_Z); the belt leaves it towards +z
    ten = []
    for f in ("tensioner_X_plate", "tensioner_X_body", "tensioner_X_slider", "tensioner_X_knob_screw"):
        ten.append(C.place_shape(C.read_step(os.path.join(TT, f + ".step")), ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
                                 (bx + 235.55, by - 247.15, G.IDLER_Z + 72.66)))
    out["TENSIONER_X_printer"] = Part.makeCompound(ten)
    # belt: free run (checked) + the rest of the loop (clamped run + the two wraps, moves with the carriage: visual)
    z0, z1 = G.IDLER_Z, G.PULLEY_Z
    out["BELT_GT2_free_run"] = C.box(bx - pr - t, bx - pr + t, by - 3, by + 3, z0, z1)
    ring = C.cyl(pr + t, 6, (bx, by - 3, 0), (0, 1, 0)).cut(C.cyl(pr - t, 8, (bx, by - 4, 0), (0, 1, 0)))
    top = ring.common(C.box(bx - 10, bx + 10, by - 4, by + 4, 0, 10))
    top.translate(Vector(0, 0, z1))
    bot = ring.common(C.box(bx - 10, bx + 10, by - 4, by + 4, -10, 0))
    bot.translate(Vector(0, 0, z0))
    out["BELT_GT2_loop"] = Part.makeCompound([C.box(bx + pr - t, bx + pr + t, by - 3, by + 3, z0, z1), top, bot])
    return out


def drive_report(P, grp):
    """Belt drive vs the robot (fixed parts are not in the pick-pose check) + belt numbers."""
    rep = ["", "Belt drive (fixed) vs the robot around it (> 0.5 mm3):"]
    env = ["ENV_ROOF", "ENV_BODY", "ENV_WHEEL", "ENV_DRIVE_MOTOR", "ENV_DOOR_UNITS"] + GUIDE_FIXED
    n = 0
    for a in DRIVE_CHECKED + ["BELT_GT2_loop"]:
        for b in env:
            v = hits(P[a], P[b])
            if v > 0.5:
                n += 1
                rep.append("  %-20s x %-16s %8.1f mm3" % (a, b, v))
    if not n:
        rep.append("  none")
    ten = P["TENSIONER_X_printer"].BoundBox
    dm = P["ENV_DRIVE_MOTOR"].BoundBox
    mot = P["NEMA17_BELT"].BoundBox
    loop = 2 * (G.PULLEY_Z - G.IDLER_Z) + 2 * 3.14159 * G.PITCH_R
    rep += ["  belt loop (pitch line) %.0f mm = %.0f teeth; open belt: cut ~%.0f mm (+2 x ~30 for the bracket clamps)"
            % (loop, loop / 2.0, loop + 60),
            "  motor on the roof: x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f (limit %.0f)"
            % (mot.XMin, mot.XMax, mot.YMin, mot.YMax, mot.ZMin, mot.ZMax, G.H_LIM),
            "  tensioner: x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f; drive motor (Pololu) y up to %.1f -> gap %.1f mm"
            % (ten.XMin, ten.XMax, ten.YMin, ten.YMax, ten.ZMin, ten.ZMax, dm.YMax, ten.YMin - dm.YMax)]
    if ten.ZMin < L.PLATE_Z[1]:
        rep.append("  tensioner knob goes down to z %.1f: through the base plate (z %.0f..%.0f) -> hole needed there"
                   % (ten.ZMin, L.PLATE_Z[0], L.PLATE_Z[1]))
    rep += ["  lift force: moving block ~0.25 kg + Grail 0.15 kg = 3.9 N -> 0.025 N.m on the 20T pulley (NEMA17 ~0.4)",
            "  travel per motor turn 40 mm (20T x 2 mm); with 1/16 microsteps: 0.0125 mm/step",
            "  NOT self-locking: stepper unpowered (e-stop, end of match) -> the carriage slides down", ""]
    return rep


def wheel_local():
    """Drive wheel + Pololu motor of this side, in the lift's local frame (obstacles)."""
    wc = wheel_center_y()
    x0, x1 = L.WHEEL_OUT - L.HALF_Y - L.WHEEL_W, L.WHEEL_OUT - L.HALF_Y      # local x of the wheel faces
    w = C.cyl(L.WHEEL_D / 2, L.WHEEL_W, (x0, L.GRAIL_X, L.WHEEL_D / 2), (1, 0, 0))
    zc = L.WHEEL_D / 2 + (L.SHAFT_OFF if L.MOTOR_UP else 0)
    m0 = x0 - L.WHEEL_GAP - L.BOSS_L - L.GB_L - L.MOT_L - L.TERM_L
    m = C.cyl(L.GB_D / 2, x0 - L.WHEEL_GAP - m0, (m0, L.GRAIL_X, zc), (1, 0, 0))
    return w, m


def door_units_local():
    out = []
    for s in (1, -1):
        y0, y1 = sorted((-s * L.DOOR_UNIT_X[0], -s * L.DOOR_UNIT_X[1]))
        out.append(C.box(L.DOOR_UNIT_Y[0] - L.HALF_Y, L.DOOR_UNIT_Y[1] - L.HALF_Y, y0 + L.GRAIL_X, y1 + L.GRAIL_X,
                         L.CLAPETS_Z0 + L.DOOR_UNIT_Z[0], L.CLAPETS_Z0 + L.DOOR_UNIT_Z[1]))
    return Part.makeCompound(out)


def parts_at_pick():
    P, grp = {}, {}

    def add(name, shape, group):
        P[name] = shape
        grp[name] = group

    # ---- robot context (env): table, wheel + motor, door units, robot body below the roof, roof with slots
    add("ENV_TABLE", C.box(-260, 260, -160, 160, -2, 0), "env")
    w, m = wheel_local()
    add("ENV_WHEEL", w, "env")
    add("ENV_DRIVE_MOTOR", m, "env")
    add("ENV_DOOR_UNITS", door_units_local(), "env")
    slot = C.box(XA - R_MAG - G.MAG_D / 2 - G.SLOT_MARGIN, -2, FLANGE_B[0] - G.SLOT_MARGIN,
                 FLANGE_A[1] + G.SLOT_MARGIN, 0, 400)                      # arm + magnet pass the roof here
    bay = C.box(G.ROD1_X - G.SCS[1] / 2 - G.SLOT_MARGIN, -2, G.PLATE_Y[0] - G.SLOT_MARGIN, 44, 0, 400)   # rods + carriage
    bay = bay.fuse(C.box(G.BELT_X - G.PITCH_R - 3, G.BELT_X + G.PITCH_R + 3, G.BELT_Y - 5, G.BELT_Y + 5, 0, 400))  # belt slot
    notch = C.box(-14, -1, Y_M - G.GY / 2 - 5, Y_M + G.GY / 2 + 5, 0, 400)        # roof edge: the Grail's corner passes here
    roof = C.box(-300, -2, -150, 150, G.ROOF - L.ROOF_T, G.ROOF).cut(slot).cut(bay).cut(notch)
    add("ENV_ROOF", roof, "env")
    # robot body below the roof = 4 boxes around the free lift column (x0..-2, y -44..44, above the wheel)
    lx0, zr = XA - R_MAG - G.MAG_D / 2 - G.SLOT_MARGIN, G.ROOF - L.ROOF_T
    body = [C.box(-300, lx0, -150, 150, L.PLATE_Z[1], zr), C.box(lx0, -2, -150, -44, L.PLATE_Z[1], zr),
            C.box(lx0, -2, 44, 150, L.PLATE_Z[1], zr),
            C.box(lx0, -2, -44, 44, L.PLATE_Z[1], L.WHEEL_D + 1).cut(w).cut(m)
             .cut(C.box(lx0 - 1, -74, 19.0, 44.5, 0, 100))]          # v4: pocket for the belt tensioner
    add("ENV_BODY", Part.makeCompound(body), "env")

    # ---- fixed: translation guide (2 Ø8 rods, printed base above the wheel, printed top clamp above the roof)
    z0r, z1r = G.ROD_Z
    rods = [C.cyl(4.0, z1r - z0r, (x, G.ROD_Y, z0r), (0, 0, 1)) for x in (G.ROD1_X, G.ROD2_X)]
    add("GUIDE_RODS_D8", Part.makeCompound(rods), "fixed")
    holes = [C.cyl(4.0, 500, (x, G.ROD_Y, -100), (0, 0, 1)) for x in (G.ROD1_X, G.ROD2_X)]
    base = C.box(G.ROD1_X - 8, G.ROD2_X + 6, G.ROD_Y - 6, G.ROD_Y + 6, z0r, z0r + 16)   # above the wheel (z 76..92)
    add("ROD_BASE_printed", base.cut(holes[0]).cut(holes[1]), "fixed")     # bolted to the side frame (not modelled)
    top = C.box(G.ROD1_X - 8, G.ROD2_X + 6, G.ROD_Y - 6, 50.0, z1r - 10, z1r)
    top = top.fuse(C.box(G.ROD1_X - 8, G.ROD2_X + 6, 44.5, 50.0, G.ROOF, z1r))   # post down to the roof (y > 44)
    add("ROD_TOP_CLAMP_printed", top.cut(holes[0]).cut(holes[1]), "fixed")
    # lift drive (fixed): belt axis from the Two Trees printer
    for n, sh in belt_drive().items():
        add(n, sh, "fixed")

    # ---- carriage (lift group): plate beside the bracket, slider frame around the column, nut arm under it
    z0, z1 = ZA + G.CAR_DZ[0], ZA + G.CAR_DZ[1]
    sl, sw, sh, sa = G.SCS
    plate = C.box(G.ROD1_X - sw / 2, XA + 12, G.PLATE_Y[0], G.PLATE_Y[1], z0, z1)
    add("CAR_PLATE", plate, "lift")
    rod_hole = lambda x: C.cyl(4.0, 500, (x, G.ROD_Y, -100), (0, 0, 1))
    blocks = []
    for k in range(2):                       # vendor SCS8UU, its flat (holes) face (local -y) on the plate (y 21)
        b = LP.scs8uu()
        b.translate(Vector(G.ROD1_X, G.ROD_Y, ZA + G.SCS_DZ + (k + 0.5) * sl))
        blocks.append(b)
    add("SCS8UU_x2", Part.makeCompound(blocks), "lift")
    bush = C.box(G.ROD1_X + sw / 2, -1.0, G.PLATE_Y[1], G.ROD_Y + 9, ZA + G.BUSH_DZ[0], ZA + G.BUSH_DZ[1])
    add("ROD2_BUSHING_printed", bush.cut(rod_hole(G.ROD2_X)), "lift")      # Ø8.4 bore in reality: only stops turning
    # belt arm (printed, APPROX) from the slide frame over the belt to the bracket; the printer's belt bracket on it
    add("CAR_BELT_ARM", C.box(G.BELT_X - 1.7, G.ROD1_X - G.SCS[1] / 2, G.ARM_Y[0], G.ARM_Y[1], ZA + G.ARM_DZ[0], ZA + G.ARM_DZ[1]),
        "lift")
    br = C.read_step(os.path.join(TT, "belt_clamp_bracket_Y.step"))
    # printer -> local: x -> -x, y (belt direction) -> z, z -> y; its wall (printer x 113.2..115.2) on the clamped run
    add("BELT_CLAMP_bracket", C.place_shape(br, ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
                                            (G.BELT_X + G.PITCH_R + 114.165, G.BELT_Y - 54.435,
                                             ZA + G.BRACKET_DZ - 290.086)), "lift")
    sv = C.read_step(os.path.join(C.SERVO_DIR, "mg996R_v2.step"))
    rows_sv = ((1, 0, 0), (0, 0, 1), (0, -1, 0))        # servo lying, body inward (-x), shaft along +y
    add("SERVO_MG996R", C.place_shape(sv, rows_sv, (XA, G.Y_S, ZA)), "lift")
    ear = C.box(XA - 40, XA + 17, G.Y_S - 4, G.Y_S, ZA + G.BAR_Z[0], ZA + 8)
    ear = ear.cut(C.box(XA - 30.7, XA + 10.7, G.Y_S - 5, G.Y_S + 1, ZA - 10.7, ZA + 10.7))
    cap_y = (G.Y_S - G.SV_BOT - G.PIVOT_GAP, G.Y_S - G.SV_BOT - 0.3)
    cap = C.box(XA - 9, XA + 9, cap_y[0], cap_y[1], ZA + G.BAR_Z[0], ZA)
    cap = cap.fuse(C.cyl(9, cap_y[1] - cap_y[0], (XA, cap_y[0], ZA), (0, 1, 0)))
    bar = C.box(XA - 40, XA + 17, cap_y[0], G.PLATE_Y[0] + 0.01, ZA + G.BAR_Z[0], ZA + G.BAR_Z[1])
    add("CRADLE_printed", ear.fuse([cap, bar]).removeSplitter(), "lift")
    add("PIVOT_PIN_M3", C.cyl(1.5, G.PIVOT_GAP + 2 * G.T_U + 2, (XA, FLANGE_B[0] - 1, ZA), (0, 1, 0)), "lift")

    # ---- flip group: horn, U bracket, L plate, magnet (face DOWN at the pick pose)
    hn = C.read_step(os.path.join(C.SERVO_DIR, "mg996_arm_round.step"))
    hn.translate(Vector(0, 0, G.HORN_TOP - 3.3))
    add("SERVO_HORN_ROUND", C.place_shape(hn, rows_sv, (XA, G.Y_S, ZA)), "flip")

    def flange(y0, y1):
        f = C.cyl(G.U_DISC_R, y1 - y0, (XA, y0, ZA), (0, 1, 0))
        f = f.fuse(C.box(XA, X_STRIP + G.T_U, y0, y1, ZA - G.U_HALF_W, ZA + G.U_HALF_W))
        return f.cut(C.cyl(4.2 if y0 > G.Y_S else 1.6, y1 - y0 + 2, (XA, y0 - 1, ZA), (0, 1, 0)))
    ub = flange(*FLANGE_A).fuse(flange(*FLANGE_B))
    ub = ub.fuse(C.box(X_STRIP, X_STRIP + G.T_U, FLANGE_B[0], FLANGE_A[1], ZA - G.U_HALF_W, ZA + G.U_HALF_W))
    add("U_BRACKET_steel", ub.removeSplitter(), "flip")
    mx0 = X_STRIP + G.T_U
    mz = ZA - G.T_OFF                                            # magnet centre height at the pick pose
    lp = C.box(mx0, mx0 + G.L_PLATE + G.MAG_D, Y_M - 13, Y_M + 13, mz + G.MAG_T / 2, mz + G.MAG_T / 2 + G.L_PLATE)
    lp = lp.fuse(C.box(mx0, mx0 + G.L_PLATE, Y_M - 13, Y_M + 13, ZA - G.U_HALF_W, mz + G.MAG_T / 2 + G.L_PLATE))
    add("MAGNET_L_PLATE", lp, "flip")
    mg = C.read_step(os.path.join(C.SW, "Magnet 5KG.step"))     # Ø27 x 20 along its y; face at y = 20
    add("MAGNET_P25", C.place_shape(mg, ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
                                    (X_STRIP + G.T_U + G.L_PLATE + G.MAG_D / 2, Y_M, mz + G.MAG_T / 2)), "flip")

    # ---- Grail on the table, its top plate under the magnet face
    gx = XA + R_MAG
    gb = C.box(gx - G.GX / 2, gx + G.GX / 2, Y_M - G.GY / 2, Y_M + G.GY / 2, 0, G.GH - G.PLATE_T)
    gp = C.box(gx - 20, gx + 20, Y_M - 20, Y_M + 20, G.GH - G.PLATE_T, G.GH)
    add("GRAIL_80", gb.fuse(gp), "grail")
    return P, grp


def rot(shape, ang):
    s = shape.copy()
    s.rotate(Vector(XA, 0, ZA), Vector(0, -1, 0), ang)
    return s


def hits(a, b):
    """common volume of a and b; b may be a list of solids (each tested only if the boxes meet)."""
    if isinstance(b, (list, tuple)):
        return sum(hits(a, x) for x in b)
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return 0.0


def plan(P, grp):
    flip = Part.makeCompound([P[n] for n in P if grp[n] == "flip"])
    lift = Part.makeCompound([P[n] for n in P if grp[n] == "lift"])
    lift_top = lift.BoundBox.ZMax - ZA
    def solids(names):
        out = []
        for n in names:
            out += P[n].Solids or [P[n]]
        return out
    drive = DRIVE_CHECKED
    env = solids([n for n in P if grp[n] == "env" and n != "ENV_TABLE"] + GUIDE_FIXED + drive)
    env_lift = solids(["ENV_ROOF", "ENV_BODY", "ENV_WHEEL", "ENV_DRIVE_MOTOR", "ENV_DOOR_UNITS"] + GUIDE_FIXED + drive)
    grail = P["GRAIL_80"]
    lift_cache = {}

    def lift_free(z):
        """the carriage does not turn: its collisions depend on the height only (cached per 0.5 mm)"""
        k = round(z * 2) / 2
        if k not in lift_cache:
            lift_cache[k] = hits(lift.translated(Vector(0, 0, k - ZA)), env_lift) <= 0.5
        return lift_cache[k]
    rows = []
    for ang in range(0, 181, 6):
        fr, gr = rot(flip, ang), rot(grail, ang)
        hi = min(G.H_LIM - max(lift_top, fr.BoundBox.ZMax - ZA), G.Z_LIFT_MAX)

        def free(z, with_grail):
            d = Vector(0, 0, z - ZA)
            if not lift_free(z) or hits(fr.translated(d), env) > 0.5:
                return False
            return not (with_grail and hits(gr.translated(d), env) > 0.5)

        def band(with_grail):
            """free band of axis heights touching the top limit: scan down from hi in 3 mm steps, refine."""
            if not free(hi, with_grail):
                return None
            z, stop = hi, max(Z_PICK - 1, hi - 150.0)        # only the band near the top matters for the path
            while z - 10.0 >= stop:
                if not free(z - 10.0, with_grail):
                    a, b = z - 10.0, z
                    for _ in range(5):
                        mid = (a + b) / 2
                        a, b = (mid, b) if not free(mid, with_grail) else (a, mid)
                    return b
                z -= 10.0
            return z
        rows.append((ang, hi, band(False), band(True)))
        print("plan %3d  hi %.1f  lo %s  lo(grail) %s" % rows[-1], flush=True)
    return rows


def main():
    P, grp = parts_at_pick()
    doc = App.newDocument("GRAIL_LIFT_V4")
    for n, s in P.items():
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
    doc.recompute()
    rep = ["GRAIL LIFT v4 (v3 + the printer's belt axis instead of the T8 screw) - generated by fc/v4_fc.py", ""]
    # start-pose sanity (pick pose here): collisions of the static model
    names = list(P)
    rep.append("Interferences at the pick pose (> 0.5 mm3, not counting the Grail on its magnet):")
    n_hit = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if {grp[a], grp[b]} <= {"env", "fixed"} or grp[a] == grp[b] == "lift" or grp[a] == grp[b] == "flip":
                continue
            if {a, b} in ({"GRAIL_80", "MAGNET_P25"}, {"GRAIL_80", "ENV_TABLE"}, 
                          {"PIVOT_PIN_M3", "CRADLE_printed"}, {"PIVOT_PIN_M3", "U_BRACKET_steel"},
                          {"SERVO_HORN_ROUND", "SERVO_MG996R"}, {"SERVO_HORN_ROUND", "U_BRACKET_steel"}) \
                    or frozenset((a, b)) in BELT_EXPECTED:
                continue
            v = hits(P[a], P[b])
            if v > 0.5:
                n_hit += 1
                rep.append("  %-18s x %-18s %8.1f mm3" % (a, b, v))
    if not n_hit:
        rep.append("  none")
    rep += drive_report(P, grp)
    rows = plan(P, grp)
    rep.append("")
    rep.append("Axis height band per flip angle (actuators <= %.0f; nothing in roof / body / wheel / door units):" % G.H_LIM)
    rep.append(" angle    max    min(no Grail)  min(Grail)  margin(Grail)")
    worst = None
    for ang, hi, lo, log in rows:
        mg = None if log is None else hi - log
        if mg is not None and (worst is None or mg < worst[1]):
            worst = (ang, mg)
        rep.append(" %5d  %6.1f   %8s   %8s   %s" % (ang, hi, "-" if lo is None else "%.1f" % lo,
                                                     "-" if log is None else "%.1f" % log,
                                                     "IMPOSSIBLE" if mg is None or mg < 0 else "%.1f" % mg))

    def zpath(ang, with_grail):
        r = min(rows, key=lambda q: abs(q[0] - ang))
        lo = r[3] if with_grail else r[2]
        return max(r[1] - 1.0, lo if lo is not None else -1e9)
    gz180 = rot(P["GRAIL_80"], 180).BoundBox.ZMin - ZA
    z_place = G.ROOF + 0.5 - gz180
    z_park = z_place - 12.0
    rep.append("")
    rep.append(("Worst margin with the Grail: %.1f mm at %d deg" % (worst[1], worst[0])) if worst else "NO FEASIBLE PATH")
    rep.append("Pick: axis z %.1f (magnet face on the Grail top at %.0f). Place: axis z %.1f (Grail bottom 0.5 above "
               "the roof). Park: axis z %.1f (arm below the roof surface)." % (Z_PICK, G.GH, z_place, z_park))
    gxc = XA + R_MAG
    rep.append("Grail at pick: x %.1f..%.1f (outside the face), y %.1f..%.1f. On the roof: x %.1f..%.1f"
               % (gxc - G.GX / 2, gxc + G.GX / 2, Y_M - G.GY / 2, Y_M + G.GY / 2, XA - R_MAG - G.GX / 2, XA - R_MAG + G.GX / 2))
    fl = Part.makeCompound([P[n] for n in P if grp[n] in ("flip", "lift")])
    rep.append("Moving parts envelope at pick: x %.1f..%.1f  y %.1f..%.1f (free band between the door units: +-44)"
               % (fl.BoundBox.XMin, fl.BoundBox.XMax, fl.BoundBox.YMin, fl.BoundBox.YMax))
    tq = 9.81 * (0.15 * (R_MAG / 1000) + 0.045 * (R_MAG / 1000) + 0.03 * (G.L_U / 2000))
    rep.append("Servo torque, arm horizontal with the Grail: %.2f N.m = %.1f kg.cm (MG996R ~9.4)" % (tq, tq / 0.0981))

    seq, cur = [], [None, None, None, None]

    def go(z, a, mag, app, label, min_t=0.08):
        if cur[0] is None:
            seq.append([0, round(z, 2), a, mag, app, label])
        else:
            d = max(abs(z - cur[0]) / 120.0, abs(a - cur[1]) / 120.0, abs(app - cur[3]) / 60.0, min_t)
            seq.append([round(d, 3), round(z, 2), a, mag, app, label])
        cur[:] = [z, a, mag, app]
    APP = 60.0
    go(z_park, 180, 0, 0.0, "start / match: arm folded under the roof")
    for a in range(180, -1, -5):
        go(zpath(a, False), a, 0, 0.0, "unfold over the side edge (no Grail)")
    go(zpath(0, False), 0, 0, -APP, "robot parks: the Grail is under the arm", 0.8)
    go(Z_PICK, 0, 0, -APP, "lower: magnet face on the Grail top")
    go(Z_PICK, 0, 1, -APP, "magnet ON", 0.3)
    go(zpath(0, True), 0, 1, -APP, "lift the Grail")
    for a in range(5, 181, 5):
        go(zpath(a, True), a, 1, -APP, "flip over the side edge with the Grail")
    go(z_place, 180, 1, -APP, "Grail down on the roof (upside down, on the magnet)")
    go(z_place, 180, 0, -APP, "magnet OFF (reverse pulse)", 0.3)
    go(z_park, 180, 0, -APP, "arm down under the roof: Grail free (L4)", 0.3)

    J = {
        "name": "v4", "fcstd": "GRAIL_LIFT_V4.FCStd",
        "lift": {"objects": [n for n in P if grp[n] in ("lift", "flip")], "base": ZA, "min": round(Z_PICK, 1),
                 "max": round(max(r[1] for r in rows), 1), "label": "Lift: flip-axis height (mm)"},
        "flip": {"objects": [n for n in P if grp[n] == "flip"], "axis_point": [XA, 0.0, ZA], "axis_dir": [0, -1, 0],
                 "base": 0.0, "min": 0.0, "max": 180.0, "label": "Flip (deg, 0 = arm out, 180 = in, under the roof)"},
        "grail": {"objects": ["GRAIL_80"], "start_offset": [0, APP, 0], "approach_dir": [0, 1, 0]},
        "actuators": [n for n in P if grp[n] in ("lift", "flip")],
        "fixed": [n for n in P if grp[n] in ("fixed", "env")],
        "limits": {"h_max": L.H_MAX, "roof": G.ROOF, "edge_x": 0.0},
        "window": [[r[0], round(r[1], 1), None if r[2] is None else round(r[2], 1),
                    None if r[3] is None else round(r[3], 1)] for r in rows],
        "colors": {"U_BRACKET_steel": [0.12, 0.12, 0.12], "MAGNET_P25": [0.65, 0.65, 0.65],
                   "MAGNET_L_PLATE": [0.2, 0.45, 0.85], "GRAIL_80": [0.95, 0.75, 0.1], "ENV_ROOF": [0.55, 0.45, 0.35],
                   "ENV_TABLE": [0.3, 0.55, 0.3], "ENV_BODY": [0.85, 0.8, 0.7], "ENV_WHEEL": [0.1, 0.1, 0.1],
                   "ENV_DRIVE_MOTOR": [0.6, 0.6, 0.62], "ENV_DOOR_UNITS": [0.2, 0.45, 0.85],
                   "CAR_PLATE": [0.2, 0.45, 0.85], "CRADLE_printed": [0.2, 0.45, 0.85], "GUIDE_RODS_D8": [0.8, 0.8, 0.85],
                   "SCS8UU_x2": [0.75, 0.78, 0.82], "ROD2_BUSHING_printed": [0.2, 0.7, 0.3],
                   "ROD_BASE_printed": [0.2, 0.7, 0.3], "ROD_TOP_CLAMP_printed": [0.2, 0.7, 0.3],
                   "SERVO_MG996R": [0.1, 0.1, 0.1], "NEMA17_BELT": [0.15, 0.15, 0.15],
                   "BELT_GT2_loop": [0.12, 0.12, 0.12], "BELT_GT2_free_run": [0.12, 0.12, 0.12],
                   "PULLEY_GT2_20T": [0.85, 0.85, 0.85], "IDLER_GT2_20T": [0.85, 0.85, 0.85],
                   "TENSIONER_X_printer": [0.15, 0.3, 0.8], "BELT_CLAMP_bracket": [0.1, 0.1, 0.1],
                   "CAR_BELT_ARM": [0.2, 0.45, 0.85]},
        "transparent": {"ENV_ROOF": 55, "ENV_TABLE": 60, "ENV_BODY": 88, "ENV_DOOR_UNITS": 70},
        "sequence": seq,
        "robot_mount": {"side": L.GRAIL_SIDE, "x": L.GRAIL_X, "half_y": L.HALF_Y},
    }
    C.save_joints(os.path.join(C.CAD, "joints_v4.json"), J)
    os.makedirs(os.path.join(C.CAD, "STEP"), exist_ok=True)
    doc.saveAs(os.path.join(C.CAD, "GRAIL_LIFT_V4.FCStd"))
    Import.export([o for o in doc.Objects if not o.Name.startswith("ENV_")], os.path.join(C.CAD, "STEP", "GRAIL_LIFT_V4.step"))
    rep.append("")
    rep.append("Sequence: %d steps, %.1f s" % (len(seq), sum(s[0] for s in seq)))
    with open(os.path.join(C.CAD, "v4_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep[:14]))
    print("\n".join(rep[-8:]))


main()
