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
# Run (from mechanical/grail-lift): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v3_fc.py   (~3 min)
#   -> CAD_FC/GRAIL_LIFT_V3.FCStd, joints_v3.json, v3_report.txt, STEP/GRAIL_LIFT_V3.step
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
    COL_X, COL_Y = (-42.0, -22.0), (22.0, 42.0)
    PLATE_Y = (15.0, 21.0)
    CAR_DZ = (-20.0, 45.0)        # carriage plate about the flip axis: it sits beside the bracket (y 15..21), so it may
                                  # pass the axis; bottom >= wheel top at the pick pose
    SLIDE_DZ = ((-18.0, -3.0), (28.0, 43.0))   # printed slider shoes in the column's +-x slots (2 per face), about the axis
    BAR_Z = (-20.0, -13.0)        # cradle bar under the arm sweep
    # lift drive: T8 lead screw (library) + NEMA17 (library) standing ON the roof, screw down through a roof hole,
    # 608 bearing block low in the robot, brass nut on an arm under the carriage. Self-locking: no drop at 100 s / e-stop.
    # Place = the only spot clear of the carriage, the arm sweep, the Grail landing, the back clapets (rails, top tie,
    # carriage bolts) and the beacon support (robot X -57..-15, Y 56..98).
    SCR_X, SCR_Y = -73.0, 36.0
    SCREW_TOP = 280.0             # coupler 5->8 from here to the roof
    SCREW_BOT = 88.0              # 608 bearing block below (78 .. 88)
    NUT_DZ = (-20.0, -5.0)        # nut holder about the flip axis
    Z_LIFT_MAX = SCREW_TOP + 5.0 - 2.0   # nut top 2 mm under the screw top
    SLOT_MARGIN = 3.0


Y_M = G.Y_MAG                                        # magnet / Grail centre plane (bracket centre: G.Y_S - 6.3)
FLANGE_A = (G.Y_S + G.HORN_TOP, G.Y_S + G.HORN_TOP + G.T_U)
FLANGE_B = (G.Y_S - G.SV_BOT - G.PIVOT_GAP - G.T_U, G.Y_S - G.SV_BOT - G.PIVOT_GAP)
XA = G.X_A
X_STRIP = XA + G.L_U
R_MAG = G.L_U + G.T_U + G.L_PLATE + G.MAG_D / 2      # magnet centre radius (on the arm line)
Z_PICK = G.GH + G.MAG_T / 2 + G.T_OFF                # axis height when the magnet face sits on the Grail top
ZA = Z_PICK                                          # model is built at the PICK pose (flip 0, arm pointing out)


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
    bay = C.box(G.COL_X[0] - 6 - G.SLOT_MARGIN, -2, G.PLATE_Y[0] - G.SLOT_MARGIN, 44, 0, 400)   # column + carriage
    bay = bay.fuse(C.cyl(12, 400, (G.SCR_X, G.SCR_Y, 0), (0, 0, 1)))                           # coupler / screw hole
    notch = C.box(-14, -1, Y_M - G.GY / 2 - 5, Y_M + G.GY / 2 + 5, 0, 400)        # roof edge: the Grail's corner passes here
    roof = C.box(-300, -2, -150, 150, G.ROOF - L.ROOF_T, G.ROOF).cut(slot).cut(bay).cut(notch)
    add("ENV_ROOF", roof, "env")
    # robot body below the roof = 4 boxes around the free lift column (x0..-2, y -44..44, above the wheel)
    lx0, zr = XA - R_MAG - G.MAG_D / 2 - G.SLOT_MARGIN, G.ROOF - L.ROOF_T
    body = [C.box(-300, lx0, -150, 150, L.PLATE_Z[1], zr), C.box(lx0, -2, -150, -44, L.PLATE_Z[1], zr),
            C.box(lx0, -2, 44, 150, L.PLATE_Z[1], zr), C.box(lx0, -2, -44, 44, L.PLATE_Z[1], L.WHEEL_D + 1).cut(w).cut(m)]
    add("ENV_BODY", Part.makeCompound(body), "env")

    # ---- fixed: column, belt, idlers, NEMA17 low inboard
    col_z = (L.WHEEL_D + 2, 346.0)
    cx, cy = (G.COL_X[0] + G.COL_X[1]) / 2, (G.COL_Y[0] + G.COL_Y[1]) / 2
    add("COL_2020", C.profile_2020(col_z[0], col_z[1], cx, cy), "fixed")
    # lift drive (fixed): T8 screw, 608 block, 5->8 coupler, NEMA17 standing on the roof
    add("SCREW_T8", C.cyl(4, G.SCREW_TOP - G.SCREW_BOT, (G.SCR_X, G.SCR_Y, G.SCREW_BOT), (0, 0, 1)), "fixed")
    add("BEARING_608_BLOCK", C.box(G.SCR_X - 11, G.SCR_X + 11, G.SCR_Y - 8, G.SCR_Y + 8, G.SCREW_BOT - 10, G.SCREW_BOT),
        "fixed")
    add("COUPLER_5x8", C.cyl(10, G.ROOF - G.SCREW_TOP, (G.SCR_X, G.SCR_Y, G.SCREW_TOP), (0, 0, 1)), "fixed")
    add("NEMA17_LIFT", C.box(G.SCR_X - 21, G.SCR_X + 21, G.SCR_Y - 21, G.SCR_Y + 21, G.ROOF, G.ROOF + 42), "fixed")

    # ---- carriage (lift group): plate beside the bracket, slider frame around the column, nut arm under it
    z0, z1 = ZA + G.CAR_DZ[0], ZA + G.CAR_DZ[1]
    plate = C.box(G.COL_X[0] - 6, XA + 12, G.PLATE_Y[0], G.PLATE_Y[1], z0, z1)
    add("CAR_PLATE", plate, "lift")
    frame = [C.box(G.COL_X[0] - 6, G.COL_X[0] - 1, G.PLATE_Y[1], G.COL_Y[1] - 2, z0, z1),
             C.box(G.COL_X[1] + 1, G.COL_X[1] + 6, G.PLATE_Y[1], G.COL_Y[1] - 2, z0, z1)]
    add("CAR_SLIDE_FRAME", Part.makeCompound(frame), "lift")
    shoes = []
    for d0, d1 in G.SLIDE_DZ:
        shoes.append(C.box(G.COL_X[0] - 1, G.COL_X[0] + 4, cy - 2.8, cy + 2.8, ZA + d0, ZA + d1))   # in the -x slot
        shoes.append(C.box(G.COL_X[1] - 4, G.COL_X[1] + 1, cy - 2.8, cy + 2.8, ZA + d0, ZA + d1))   # in the +x slot
    add("CAR_SLIDERS", Part.makeCompound(shoes), "lift")
    arm = C.box(G.SCR_X - 10, G.COL_X[0] - 6, G.PLATE_Y[0], G.SCR_Y + 8, ZA + G.NUT_DZ[0], ZA + G.NUT_DZ[1])
    arm = arm.cut(C.cyl(8.5, 40, (G.SCR_X, G.SCR_Y, ZA - 30), (0, 0, 1)))
    add("CAR_NUT_ARM", arm, "lift")
    nut = C.cyl(8, G.NUT_DZ[1] - G.NUT_DZ[0], (G.SCR_X, G.SCR_Y, ZA + G.NUT_DZ[0]), (0, 0, 1))
    add("NUT_T8_brass", nut.cut(C.cyl(4.2, 40, (G.SCR_X, G.SCR_Y, ZA - 30), (0, 0, 1))), "lift")
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
    drive = ["SCREW_T8", "BEARING_608_BLOCK", "COUPLER_5x8", "NEMA17_LIFT"]
    env = solids([n for n in P if grp[n] == "env" and n != "ENV_TABLE"] + ["COL_2020"] + drive)
    env_lift = solids(["ENV_ROOF", "ENV_BODY", "ENV_WHEEL", "ENV_DRIVE_MOTOR", "ENV_DOOR_UNITS"] + drive)
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
    doc = App.newDocument("GRAIL_LIFT_V3")
    for n, s in P.items():
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
    doc.recompute()
    rep = ["GRAIL LIFT v3 (compact, side face above the drive wheel) - generated by fc/v3_fc.py", ""]
    # start-pose sanity (pick pose here): collisions of the static model
    names = list(P)
    rep.append("Interferences at the pick pose (> 0.5 mm3, not counting the Grail on its magnet):")
    n_hit = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if {grp[a], grp[b]} <= {"env", "fixed"} or grp[a] == grp[b] == "lift" or grp[a] == grp[b] == "flip":
                continue
            if {a, b} in ({"GRAIL_80", "MAGNET_P25"}, {"GRAIL_80", "ENV_TABLE"}, {"COL_2020", "CAR_SLIDERS"}, {"SCREW_T8", "NUT_T8_brass"},
                          {"SCREW_T8", "BEARING_608_BLOCK"}, {"SCREW_T8", "COUPLER_5x8"}, {"COUPLER_5x8", "NEMA17_LIFT"},
                          {"PIVOT_PIN_M3", "CRADLE_printed"}, {"PIVOT_PIN_M3", "U_BRACKET_steel"},
                          {"SERVO_HORN_ROUND", "SERVO_MG996R"}, {"SERVO_HORN_ROUND", "U_BRACKET_steel"}):
                continue
            v = hits(P[a], P[b])
            if v > 0.5:
                n_hit += 1
                rep.append("  %-18s x %-18s %8.1f mm3" % (a, b, v))
    if not n_hit:
        rep.append("  none")
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
        "name": "v3", "fcstd": "GRAIL_LIFT_V3.FCStd",
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
                   "CAR_PLATE": [0.2, 0.45, 0.85], "CRADLE_printed": [0.2, 0.45, 0.85], "COL_2020": [0.8, 0.8, 0.85],
                   "SERVO_MG996R": [0.1, 0.1, 0.1], "CAR_SLIDERS": [0.9, 0.9, 0.9], "NEMA17_LIFT": [0.15, 0.15, 0.15],
                   "SCREW_T8": [0.8, 0.8, 0.8], "NUT_T8_brass": [0.85, 0.7, 0.3]},
        "transparent": {"ENV_ROOF": 55, "ENV_TABLE": 60, "ENV_BODY": 88, "ENV_DOOR_UNITS": 70},
        "sequence": seq,
        "robot_mount": {"side": L.GRAIL_SIDE, "x": L.GRAIL_X, "half_y": L.HALF_Y},
    }
    C.save_joints(os.path.join(C.CAD, "joints_v3.json"), J)
    os.makedirs(os.path.join(C.CAD, "STEP"), exist_ok=True)
    doc.saveAs(os.path.join(C.CAD, "GRAIL_LIFT_V3.FCStd"))
    Import.export([o for o in doc.Objects if not o.Name.startswith("ENV_")], os.path.join(C.CAD, "STEP", "GRAIL_LIFT_V3.step"))
    rep.append("")
    rep.append("Sequence: %d steps, %.1f s" % (len(seq), sum(s[0] for s in seq)))
    with open(os.path.join(C.CAD, "v3_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep[:14]))
    print("\n".join(rep[-8:]))


main()
