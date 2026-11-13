# v2_fc.py - Grail lift v2 (concept, Maatoug + Claude, 2026-11-10): Baha's v1 idea kept (rack + pinion lift, MG996R
# turning an electromagnet about a horizontal axis), made able to put the Grail on the roof under the 350 mm rule:
#   * the servo turns the magnet 180 deg OVER the robot's edge (flip), coordinated with the lift (planned path below);
#   * the magnet sits on the club's steel U servo bracket (photo 2026-11-10): horn on one side, pivot pin on the other,
#     so the arm is held on both sides of the servo instead of hanging on the servo spline;
#   * the carriage rides on 4 V-wheels on the 2020 column (v1 had no guide), NEMA17 from the library, pinion directly
#     on the motor shaft (v1: 38 mm coupling overhang), rack lying in the front slot, motor perpendicular to the plate.
# Run (from mechanical/grail-lift):  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v2_fc.py   (~2-4 min)
#   -> CAD_FC/GRAIL_LIFT_V2.FCStd, CAD_FC/joints_v2.json (slider macro + motion check), CAD_FC/v2_report.txt,
#      CAD_FC/STEP/GRAIL_LIFT_V2.step
# Frame: x = outward normal of the robot face carrying the lift (face plane x = 0), y along the face, z up, table z = 0.
# The model is built at the PICK pose: flip 0 deg (arm pointing +x), flip axis at z = G.Z_PICK, Grail on the table.
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import Import
import Part
from FreeCAD import Vector

import grail_common as C


class G:
    # robot context (ASSUMPTIONS until Seif's roof layout exists)
    ROOF = 305.0                 # roof top surface (plate 300..305): L4 needs > 300 [G E.2]
    ROOF_EDGE = -2.0             # roof plate stops 2 mm inside the face
    SKIN = 3.0                   # face skin x -3..0
    H_LIM = C.H_MAX - 2.0        # 2 mm margin under 350 for every actuator
    # Grail (ours, > 60 mm cube [G E.2]; FAQ Q3 open): 80 cube, 1.5 steel plate on one face, gripped 25 below its top
    GRAIL = 80.0
    GRIP_FROM_TOP = 25.0
    PLATE_T = 1.5
    Z_PICK = GRAIL - GRIP_FROM_TOP          # flip axis height when the magnet faces the Grail on the table (55)
    APPROACH = 30.0                          # Grail starts 30 mm away from the magnet face; the robot drives in
    # flip axis (servo shaft), along y
    X_A = -15.0
    # U bracket (club part, photo): ESTIMATED - measure it (arm length to the inside of the strip, inner width, t)
    L_U, T_U, U_HALF_W, U_DISC_R = 45.0, 2.5, 13.0, 13.0
    # MG996R (real model): shaft top 15.8, horn top 19.4 above the ear plane, body bottom 28.3 below it
    HORN_TOP, SV_BOT = 19.4, 28.3
    PIVOT_GAP = 3.7                          # printed rear cap + pivot pin between servo bottom and the 2nd bracket side
    Y_M = -78.0                              # magnet / Grail centre plane
    # column + drive
    X_C = -100.0                             # 2020 column centre (front face x = -90), y = 0
    COL_Z = (3.0, 345.0)
    PLATE_X = (-82.0, -76.0)                 # carriage plate (printed, 6 thick), 8 mm in front of the column
    PLATE_Y = (-36.0, 36.0)
    CAR_DZ = (-52.0, 12.0)                   # carriage extent about the flip axis (budget: 350 at top, table at pick)
    WHEEL_DZ = (-2.0, -40.0)                 # V-wheel centres about the flip axis (38 apart)
    PIN_DZ = -25.0                           # pinion / motor axis below the flip axis
    PIN_Y = 8.5                              # pinion axis y (rack pitch line at y = -1.5)
    RACK_Y_BACK = -6.0
    RACK_Z = (12.0, 330.0)
    MAGNET_T = 20.0
    MASS = {"grail": 0.15, "magnet": 0.045, "bracket": 0.030}


Y_S = G.Y_M + (G.SV_BOT + G.PIVOT_GAP + G.T_U - (G.HORN_TOP + G.T_U)) / 2.0   # servo ear plane so the bracket centres on Y_M
FLANGE_A = (Y_S + G.HORN_TOP, Y_S + G.HORN_TOP + G.T_U)
FLANGE_B = (Y_S - G.SV_BOT - G.PIVOT_GAP - G.T_U, Y_S - G.SV_BOT - G.PIVOT_GAP)
XA, ZA = G.X_A, G.Z_PICK
X_STRIP = XA + G.L_U
X_MAG = X_STRIP + G.T_U
X_FACE = X_MAG + G.MAGNET_T


def parts_at_pick():
    P, grp = {}, {}

    def add(name, shape, group):
        P[name] = shape
        grp[name] = group

    # ---- fixed: column, rack, robot context
    add("COL_2020", C.profile_2020(G.COL_Z[0], G.COL_Z[1], G.X_C, 0.0), "fixed")
    add("RACK_M1", C.rack_m1(G.RACK_Z[0], G.RACK_Z[1], G.X_C + 10, G.X_C + 15.8, G.RACK_Y_BACK, 1), "fixed")
    roof = C.box(-260, G.ROOF_EDGE, -160, 100, G.ROOF - 5, G.ROOF)
    roof = roof.cut(C.box(-113, -28, -37, 41, G.ROOF - 6, G.ROOF + 1))           # opening A: column, carriage, motor
    roof = roof.cut(C.box(-60, 1, -109, -36, G.ROOF - 6, G.ROOF + 1))            # opening B: servo, cradle, bracket swing (Grail keeps 77.5 of 80 mm on the roof)
    add("ENV_ROOF", roof, "env")
    skin = C.box(-G.SKIN, 0, -160, 100, 20, G.ROOF - 5)
    skin = skin.cut(C.box(-G.SKIN - 1, 1, FLANGE_B[0] - 2, FLANGE_A[1] + 2, 19, G.ROOF))   # slot for the bracket
    add("ENV_FACE_SKIN", skin, "env")
    add("ENV_TABLE", C.box(-300, 300, -200, 150, -2, 0), "env")
    # robot body under the roof (stand-in for everything else in the robot): solid, except the lift bay
    body = C.box(-260, -G.SKIN, -160, 100, 20, G.ROOF - 5)
    body = body.cut(C.box(-113, -28, -37, 41, 0, G.ROOF)).cut(C.box(-60, 1, -109, -36, 0, G.ROOF))
    body = body.cut(C.box(-86, 1, -109, -36, 0, G.ROOF - 5))      # under the roof: cradle path to the carriage
    add("ENV_BODY", body, "env")

    # ---- carriage (lift group)
    z0, z1 = ZA + G.CAR_DZ[0], ZA + G.CAR_DZ[1]
    pz = ZA + G.PIN_DZ
    plate = C.box(G.PLATE_X[0], G.PLATE_X[1], G.PLATE_Y[0], G.PLATE_Y[1], z0, z1)
    plate = plate.cut(C.cyl(11.5, 10, (G.PLATE_X[0] - 1, G.PIN_Y, pz), (1, 0, 0)))  # NEMA17 pilot Ø22
    add("CAR_PLATE", plate, "lift")
    wheels, spacers = [], []
    for dz in G.WHEEL_DZ:
        for sy in (1, -1):
            c = (G.X_C, sy * 18.0, ZA + dz)
            wheels.append(C.vwheel(c, (1, 0, 0)))
            spacers.append(C.cyl(4.0, G.PLATE_X[0] - (G.X_C + 5.1), (G.X_C + 5.1, sy * 18.0, ZA + dz), (1, 0, 0)))
    add("CAR_VWHEELS", Part.makeCompound(wheels), "lift")
    add("CAR_SPACERS", Part.makeCompound(spacers), "lift")
    add("CAR_PINION_20T", C.pinion_m1(20, 5.0, (G.X_C + 12.9, G.PIN_Y, pz), "x"), "lift")
    # NEMA17 (real model from the club's file): find its shaft, put the face on the plate, shaft along -x
    nm = C.read_step(os.path.join(C.CAD, "STEP", "v1_sw_export", "nema17.step"))
    sh = [f for f in nm.Faces if f.Surface.__class__.__name__ == "Cylinder" and abs(f.Surface.Radius - 2.5) < 0.3]
    sb = sh[0].BoundBox if sh else None
    nb = nm.BoundBox
    tip_low = sb is not None and abs(sb.YMin - nb.YMin) < abs(sb.YMax - nb.YMax)
    # motor local y = axis. Face plane = where the shaft leaves the body (shaft end opposite the tip)
    face_y = (sb.YMax if tip_low else sb.YMin) if sb else nb.YMin + 20
    rows = ((0, 1, 0), (0, 0, 1), (1, 0, 0)) if tip_low else ((0, -1, 0), (0, 0, 1), (-1, 0, 0))   # right-handed both
    m = C.place_shape(nm, rows, (0, 0, 0))
    mb = m.BoundBox
    # after mapping, the shaft tip is at the smallest x; face at x = -(face_y) (or +face_y): find it from the mapping
    face_x = (face_y if tip_low else -face_y)
    m.translate(Vector(G.PLATE_X[1] - face_x, G.PIN_Y, pz))
    m = m.cut(C.box(-200, G.X_C + 10.5, -100, 100, -100, 500))     # shaft cut to ~14 mm (stock 24 would hit the column)
    add("CAR_NEMA17", m, "lift")

    # servo + horn + cradle (lift group)
    sv = C.read_step(os.path.join(C.SERVO_DIR, "mg996R_v2.step"))
    rows_sv = ((1, 0, 0), (0, 0, 1), (0, -1, 0))         # servo lying: body inward (-x), shaft along +y, 10 above axis
    add("SERVO_MG996R", C.place_shape(sv, rows_sv, (XA, Y_S, ZA)), "lift")
    hn = C.read_step(os.path.join(C.SERVO_DIR, "mg996_arm_round.step"))
    hn.translate(Vector(0, 0, G.HORN_TOP - 3.3))
    add("SERVO_HORN_ROUND", C.place_shape(hn, rows_sv, (XA, Y_S, ZA)), "flip")
    ear = C.box(XA - 40, XA + 17, Y_S - 4, Y_S, ZA - 52, ZA + 8)                  # ears at x XA-34.5 / XA+14.5
    ear = ear.cut(C.box(XA - 30.7, XA + 10.7, Y_S - 5, Y_S + 1, ZA - 10.7, ZA + 10.7))
    cap = C.box(XA - 9, XA + 9, Y_S - G.SV_BOT - G.PIVOT_GAP, Y_S - G.SV_BOT - 0.3, ZA - 52, ZA)
    cap = cap.fuse(C.cyl(9, G.PIVOT_GAP - 0.3, (XA, Y_S - G.SV_BOT - G.PIVOT_GAP, ZA), (0, 1, 0)))
    bars = C.box(G.PLATE_X[0], XA + 17, Y_S - G.SV_BOT - G.PIVOT_GAP, Y_S, ZA - 52, ZA - 44)
    tie = C.box(G.PLATE_X[0], G.PLATE_X[1], Y_S - G.SV_BOT - G.PIVOT_GAP, G.PLATE_Y[0] + 0.01, ZA - 52, ZA - 44)
    add("CRADLE_printed", ear.fuse([cap, bars, tie]).removeSplitter(), "lift")
    add("PIVOT_PIN_M3", C.cyl(1.5, G.PIVOT_GAP + 2 * G.T_U + 2, (XA, FLANGE_B[0] - 1, ZA), (0, 1, 0)), "lift")

    # ---- flip group: U bracket + magnet
    def flange(y0, y1):
        f = C.cyl(G.U_DISC_R, y1 - y0, (XA, y0, ZA), (0, 1, 0))
        f = f.fuse(C.box(XA, X_STRIP + G.T_U, y0, y1, ZA - G.U_HALF_W, ZA + G.U_HALF_W))
        return f.cut(C.cyl(4.2 if y0 > Y_S else 1.6, y1 - y0 + 2, (XA, y0 - 1, ZA), (0, 1, 0)))
    ub = flange(*FLANGE_A).fuse(flange(*FLANGE_B))
    ub = ub.fuse(C.box(X_STRIP, X_STRIP + G.T_U, FLANGE_B[0], FLANGE_A[1], ZA - G.U_HALF_W, ZA + G.U_HALF_W))
    add("U_BRACKET_steel", ub.removeSplitter(), "flip")
    mg = C.read_step(os.path.join(C.SW, "Magnet 5KG.step"))
    add("MAGNET_P25", C.place_shape(mg, ((0, 1, 0), (0, 0, 1), (1, 0, 0)), (X_MAG, G.Y_M, ZA)), "flip")   # wire lug along y

    # ---- Grail at the pick pose (touching the magnet face)
    gb = C.box(X_FACE + G.PLATE_T, X_FACE + G.PLATE_T + G.GRAIL, G.Y_M - G.GRAIL / 2, G.Y_M + G.GRAIL / 2, 0, G.GRAIL)
    gp = C.box(X_FACE, X_FACE + G.PLATE_T, G.Y_M - 20, G.Y_M + 20, ZA - 20, ZA + 20)
    add("GRAIL_80", gb.fuse(gp), "grail")
    return P, grp


# ---------------------------------------------------------------- planner
def rot(shape, ang, dz=0.0):
    s = shape.copy()
    s.rotate(Vector(XA, 0, ZA), Vector(0, -1, 0), ang)     # +ang turns +x towards +z (over the top)
    s.translate(Vector(0, 0, dz))
    return s


def hits(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return 0.0


def plan(P, grp):
    flip = Part.makeCompound([P[n] for n in P if grp[n] == "flip"])
    lift_top = max(P[n].BoundBox.ZMax for n in P if grp[n] == "lift") - ZA
    print("tops above the axis:", sorted(((round(P[n].BoundBox.ZMax - ZA, 1), n) for n in P if grp[n] in ("lift", "flip")), reverse=True)[:5])
    lift_bot = min(P[n].BoundBox.ZMin for n in P if grp[n] == "lift") - ZA
    grail = P["GRAIL_80"]
    # robot body below the roof: solid, except the lift bay (= the roof openings, full height) for the mechanism.
    # The Grail may never be inside the face below the roof: it sees the body without the bay.
    env = Part.makeCompound([P["ENV_ROOF"], P["ENV_FACE_SKIN"], P["ENV_BODY"]])
    env_g = Part.makeCompound([P["ENV_ROOF"], C.box(-400, 0, -400, 400, 1, G.ROOF)])
    rows = []
    for ang in range(0, 181, 2):
        fr = rot(flip, ang)
        gr = rot(grail, ang)
        top_rel = max(lift_top, fr.BoundBox.ZMax - ZA)
        hi = G.H_LIM - top_rel
        lo_hw = 1.0 - min(lift_bot, fr.BoundBox.ZMin - ZA)        # keep above the table

        def lo_for(shape_rel, env=env):
            """Lowest axis height of the free band that touches the top limit: scan down from hi (4 mm), refine."""
            hit = lambda z: hits(shape_rel.translated(Vector(0, 0, z - ZA)), env) > 0.5
            if hit(hi):
                return None
            z, stop = hi, max(lo_hw, hi - 160.0)
            while z - 4.0 >= stop:
                if hit(z - 4.0):
                    a, b = z - 4.0, z
                    for _ in range(6):
                        mid = (a + b) / 2
                        a, b = (mid, b) if hit(mid) else (a, mid)
                    return b
                z -= 4.0
            return stop if not hit(stop) else z

        lo_ng = lo_for(fr)
        lo_g = lo_for(fr)
        lo_gg = lo_for(gr, env_g)
        lo_g = None if (lo_g is None or lo_gg is None) else max(lo_g, lo_gg)
        rows.append((ang, hi, lo_ng, lo_g, gr.BoundBox.ZMin - ZA))
        print("plan %3d  hi %.1f  lo(no grail) %s  lo(grail) %s" % (ang, hi, lo_ng, lo_g))
    return rows


def main():
    P, grp = parts_at_pick()
    doc = App.newDocument("GRAIL_LIFT_V2")
    for n, s in P.items():
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
    doc.recompute()
    rows = plan(P, grp)
    rep = ["GRAIL LIFT v2 concept - generated by fc/v2_fc.py", ""]
    rep.append("Pick: flip axis at z %.1f, magnet face x %.1f, Grail x %.1f..%.1f (outside the face), grip %.0f below its top"
               % (ZA, X_FACE, X_FACE, X_FACE + G.PLATE_T + G.GRAIL, G.GRIP_FROM_TOP))
    rep.append("Servo ear plane y %.1f, bracket sides y %.1f..%.1f and %.1f..%.1f, magnet/Grail centre y %.1f"
               % (Y_S, FLANGE_A[0], FLANGE_A[1], FLANGE_B[0], FLANGE_B[1], G.Y_M))
    rep.append("")
    rep.append("Allowed flip-axis height per flip angle (actuators <= %.0f, nothing in the roof / face, table clear):" % G.H_LIM)
    rep.append(" angle   max      min(no Grail)  min(Grail held)  margin(Grail)")
    worst = None
    for ang, hi, lo_ng, lo_g, gzr in rows:
        m = None if lo_g is None else hi - lo_g
        if m is not None and (worst is None or m < worst[1]):
            worst = (ang, m)
        rep.append(" %5d  %6.1f   %8s       %8s        %s" % (ang, hi, "-" if lo_ng is None else "%.1f" % lo_ng,
                                                              "-" if lo_g is None else "%.1f" % lo_g,
                                                              "IMPOSSIBLE" if m is None or m < 0 else "%.1f" % m))
    # path: as high as allowed (1 mm under the max), never under the min
    def zpath(ang, with_grail):
        r = min(rows, key=lambda q: abs(q[0] - ang))
        lo = r[3] if with_grail else r[2]
        return max(r[1] - 1.0, lo if lo is not None else -1e9)
    gz180 = [r for r in rows if r[0] == 180][0][4]
    z_place = G.ROOF + 0.5 - gz180
    rep.append("")
    rep.append("Worst margin with the Grail: %.1f mm at %d deg" % (worst[1], worst[0]) if worst else "no feasible angle")
    rep.append("Place on the roof: flip 180, axis z %.1f (Grail bottom 0.5 above the roof); allowed min there %.1f"
               % (z_place, [r for r in rows if r[0] == 180][0][2] or float("nan")))
    # torque on the servo with the Grail held horizontally (flip 0 or 180)
    g = 9.81
    r_grail = (X_FACE + G.PLATE_T + G.GRAIL / 2 - XA) / 1000
    r_mag = (X_MAG + G.MAGNET_T / 2 - XA) / 1000
    r_br = (G.L_U / 2) / 1000
    tq = g * (G.MASS["grail"] * r_grail + G.MASS["magnet"] * r_mag + G.MASS["bracket"] * r_br)
    rep.append("Servo torque, arm horizontal with the Grail: %.2f N.m = %.1f kg.cm (MG996R ~9.4 kg.cm at 4.8 V)"
               % (tq, tq / 0.0981))
    car_h = G.CAR_DZ[1] - G.CAR_DZ[0]
    rep.append("Carriage height %.0f mm; lift travel (axis) %.0f .. %.0f" % (car_h, ZA, max(r[1] for r in rows)))
    xs = max(P[n].BoundBox.XMax for n in P if grp[n] in ("flip",))
    rep.append("Max protrusion beyond the face (flip 0): %.1f mm (deployed perimeter); folded (flip 180): 0" % xs)

    # ---- sequence (duration, axis z, flip, magnet, approach, label); speeds: lift 120 mm/s, flip 120 deg/s
    seq = []
    cur = [0, None, None, 0, 0.0, ""]

    def go(z, a, mag, app, label, min_t=0.15):
        if cur[1] is None:
            seq.append([0, round(z, 2), a, mag, app, label])
        else:
            d = max(abs(z - cur[1]) / 120.0, abs(a - cur[2]) / 120.0, abs(app - cur[4]) / 60.0, min_t)
            seq.append([round(d, 3), round(z, 2), a, mag, app, label])
        cur[1], cur[2], cur[3], cur[4] = z, a, mag, app
    go(zpath(180, False), 180, 0, 0.0, "start: arm folded over the roof, lift up")
    for a in range(175, -1, -5):
        go(zpath(a, False), a, 0, 0.0, "unfold over the edge (no Grail)", 0.08)
    go(ZA, 0, 0, 0.0, "lower to the Grail height")
    go(ZA, 0, 0, -G.APPROACH, "robot drives in: magnet touches the steel plate", 0.5)
    go(ZA, 0, 1, -G.APPROACH, "magnet ON", 0.3)
    go(zpath(0, True), 0, 1, -G.APPROACH, "lift with the Grail")
    for a in range(5, 181, 5):
        go(zpath(a, True), a, 1, -G.APPROACH, "flip over the edge with the Grail", 0.08)
    go(z_place, 180, 1, -G.APPROACH, "lower: Grail sits on the roof")
    go(z_place, 180, 0, -G.APPROACH, "magnet OFF (reverse pulse)", 0.3)
    for a in (178, 176, 174, 172, 170, 165, 160, 155, 150, 145, 140):
        go(zpath(a, False), a, 0, -G.APPROACH, "arm leaves the Grail", 0.08)
    go(zpath(140, False), 140, 0, -G.APPROACH, "park: Grail free on the roof (L4)", 0.5)

    J = {
        "name": "v2", "fcstd": "GRAIL_LIFT_V2.FCStd",
        "lift": {"objects": [n for n in P if grp[n] in ("lift", "flip")], "base": ZA,
                 "min": round(ZA - 0.0, 1), "max": round(max(r[1] for r in rows), 1),
                 "label": "Lift: flip-axis height (mm)"},
        "flip": {"objects": [n for n in P if grp[n] == "flip"], "axis_point": [XA, 0.0, ZA], "axis_dir": [0, -1, 0],
                 "base": 0.0, "min": 0.0, "max": 180.0, "label": "Flip (deg, 0 = arm out, 180 = over the roof)"},
        "grail": {"objects": ["GRAIL_80"], "start_offset": [G.APPROACH, 0, 0]},
        "actuators": [n for n in P if grp[n] in ("lift", "flip")],
        "fixed": [n for n in P if grp[n] in ("fixed", "env")],
        "limits": {"h_max": C.H_MAX, "roof": G.ROOF, "edge_x": 0.0},
        "window": [[r[0], round(r[1], 1), None if r[2] is None else round(r[2], 1),
                    None if r[3] is None else round(r[3], 1)] for r in rows],
        "colors": {"U_BRACKET_steel": [0.12, 0.12, 0.12], "MAGNET_P25": [0.65, 0.65, 0.65],
                   "GRAIL_80": [0.95, 0.75, 0.1], "ENV_ROOF": [0.55, 0.45, 0.35], "ENV_FACE_SKIN": [0.55, 0.45, 0.35],
                   "ENV_TABLE": [0.3, 0.55, 0.3], "ENV_BODY": [0.85, 0.8, 0.7], "CAR_PLATE": [0.2, 0.45, 0.85], "CRADLE_printed": [0.2, 0.45, 0.85],
                   "COL_2020": [0.8, 0.8, 0.85], "RACK_M1": [0.95, 0.95, 0.95], "CAR_PINION_20T": [0.95, 0.95, 0.95],
                   "CAR_NEMA17": [0.15, 0.15, 0.15], "SERVO_MG996R": [0.1, 0.1, 0.1], "CAR_VWHEELS": [0.9, 0.9, 0.9],
                   "SERVO_HORN_ROUND": [0.95, 0.95, 0.95], "PIVOT_PIN_M3": [0.7, 0.7, 0.7]},
        "transparent": {"ENV_ROOF": 55, "ENV_FACE_SKIN": 70, "ENV_TABLE": 60, "ENV_BODY": 85},
        "sequence": seq,
    }
    C.save_joints(os.path.join(C.CAD, "joints_v2.json"), J)
    os.makedirs(os.path.join(C.CAD, "STEP"), exist_ok=True)
    doc.saveAs(os.path.join(C.CAD, "GRAIL_LIFT_V2.FCStd"))
    Import.export([o for o in doc.Objects if not o.Name.startswith("ENV_")],
                  os.path.join(C.CAD, "STEP", "GRAIL_LIFT_V2.step"))
    rep.append("")
    rep.append("Sequence: %d steps, %.1f s" % (len(seq), sum(s[0] for s in seq)))
    for s in seq:
        rep.append("  %5.2f s  axis z %6.1f  flip %5.1f  magnet %d  approach %5.1f  %s" % tuple(s))
    with open(os.path.join(C.CAD, "v2_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep[:12]))


main()
