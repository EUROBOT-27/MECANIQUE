# flipper_fc.py - FLIPPER (was option B): Grail lift with a top grip + 180 deg flip onto the roof (D-029),
# rack-and-pinion lift built from REAL parts:
#   * Two Trees Bluer V2 X-axis carriage: steel plate + 3 V-wheels + M5x25 screws, nyloc nuts, spacers, eccentric
#     (../resources/two-trees-bluer-v2-parts/*_X.step, x_carriage_plate.step) on the real 2020 profile (cut to length),
#   * Seif's printed rack (parts/cremaillere.STL, m1, 310 x 10.6 x 5, V back seated in the profile's V-groove),
#   * real NEMA17 (nema17.step = Two Trees Z motor, standard ~40 mm body, Seif 2026-11-20: a shorter one may replace it -> MOTOR_* below),
#   * pinion v2 (print/FLIPPER_PINION.step from fc/flipper_pinion_fc.py: m1 20T, long Ø16 hub),
#   * flip head from common.flip_head (MG996R + 625 cheek + arm + Ø30 magnet in a cup).
# Why the motor sits where it does: the X plate is 2 mm from the profile's front face and its wheels ride the two side
# faces, so the rack goes on the BACK face; the motor shaft runs along y and the motor body must clear the eccentric
# wheel -> long pinion hub (as Baha's el pignon).
# Robot frame (layout-v1): X right (right face x 150), Y forward, Z up. Grail bay (layout-v1 report, T1 back):
# x 66..150, y -52..40, z 78..300.
#   Run (from mechanical/Grail_v2): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_fc.py
#   -> CAD_FC/FLIPPER.FCStd, CAD_FC/FLIPPER_report.txt   (bounding boxes + layout envelope; no clash check)
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import Mesh
import Part
from FreeCAD import Vector

import common as C

RES = os.path.join(C.MECH, "resources", "two-trees-bluer-v2-parts")
PARTS = os.path.join(C.ROOT, "parts")
PRINT = os.path.join(C.ROOT, "print")
BAY = dict(x0=66.0, x1=150.0, y0=-52.0, y1=40.0, z0=78.0, z1=300.0)     # GRAIL_LIFT_R, layout-v1 T1 report


class G:
    # ---- flip geometry
    LZ = 58.0                                # pivot above the Grail top at the pick (= under the roof top at the place)
    PX = (C.X_PICK + C.X_PLACE) / 2
    Z_PICK = C.G_H + LZ
    Z_PLACE = C.ROOF_TOP - LZ
    OVER, REL = 6.0, 6.0
    # ---- column: real 2020, profile centre (XC, YC); plate faces +x (towards the right face)
    XC, YC = 110.0, 4.0
    PROF_Z0, PROF_Z1 = 78.0, 275.0           # profile cut length (bay floor .. under the arm's path at the place)
    # ---- carriage: plate centre height at the pick; pivot H_P above it
    H_P = None                                # computed: Z_PICK - ZC_PICK
    ZC_PICK = 116.0                           # lowest plate centre (bottom wheel stays on the profile)
    # ---- rack: V back seated RACK_SEAT deep in the back-face groove, teeth towards -x
    RACK_SEAT = 2.62
    # ---- motor (standard NEMA17 40 mm for now) + pinion
    MOTOR_FACE_GAP = 1.0                      # motor face this far past the eccentric wheel (in -y)
    PIN_DZ = 10.0                             # pinion centre above the plate centre
    PIN_BOSS_GAP = 0.5                        # flipper_pinion_fc: hub face 0.5 from the motor face
    PIN_GEAR_OFF = 0.5 + 27.5 + 5.0           # gear centre from the motor face (flipper_pinion_fc: BOSS_GAP + HUB_L + FACE_W/2)


# printer frame of the X axis (from the STLs / STEPs): profile centre line y 246.9, z 235.5; plate centre x 120.6
P_Y, P_Z, P_XC = 246.9, 235.5, 120.6


def printer_to_robot(zc):
    """Matrix: printer (x along the profile, plate normal +y, wheels on +-z faces) -> robot (profile along z,
    plate normal +x, wheels on +-y faces), plate centre at height zc."""
    m = App.Matrix(0, 1, 0, G.XC - P_Y,
                   0, 0, 1, G.YC - P_Z,
                   1, 0, 0, zc - P_XC,
                   0, 0, 0, 1)
    return m


def load(name, m):
    s = Part.read(os.path.join(RES, name))
    s = s.copy()
    s.transformShape(m)
    return s


def mesh_solid(path, m=None):
    me = Mesh.Mesh(path)
    if m is not None:
        me.transform(m)
    sh = Part.Shape()
    sh.makeShapeFromMesh(me.Topology, 0.05)
    so = Part.Solid(Part.Shell(sh.Faces))
    if so.Volume < 0:
        so.reverse()
    return so


def nema_frame():
    """Real NEMA17 (Two Trees Z motor, nema17.step: body 42 x 42 x ~38, shaft Ø5 along +z of the printer frame).
    Returns (shape, shaft direction d, flange-face centre on the axis)."""
    s = Part.read(os.path.join(RES, "nema17.step"))
    b = s.optimalBoundingBox(False, False)
    d = Vector(0, 0, 1)
    zs = b.ZMax - 5.0                                     # through the shaft
    sec = Part.makeCompound(s.slice(d, zs)).BoundBox
    c = Vector(sec.Center.x, sec.Center.y, 0)
    face = max(v.Point.z for so in s.Solids for v in so.Vertexes
               if math.hypot(v.Point.x - c.x, v.Point.y - c.y) > 12.5)
    return s, d, Vector(c.x, c.y, face)


def build(doc, groups):
    fixed, lift, arm_all = {}, {}, {}
    zc = G.ZC_PICK
    G.H_P = G.Z_PICK - zc
    M = printer_to_robot(zc)
    # ---------------- fixed column: real 2020 cut to length, rack
    Mp = printer_to_robot(zc)
    prof = load("profile_2020_X_350.step", Mp)
    cut = C.box(G.XC - 15, G.XC + 15, G.YC - 15, G.YC + 15, G.PROF_Z0, G.PROF_Z1)
    fixed["PROFILE_2020"] = prof.common(cut)
    # rack (local: x = length 0..310, y = 0 (V tip) .. 5 (tooth tips), z = width 0..10.59)
    rack = mesh_solid(os.path.join(PARTS, "cremaillere.STL"))
    rm = App.Matrix(0, -1, 0, G.XC - 10 + G.RACK_SEAT,
                    0, 0, 1, G.YC - 10.59 / 2,
                    1, 0, 0, G.PROF_Z0,
                    0, 0, 0, 1)
    rack = rack.transformGeometry(rm) if False else rack
    rack = rack.copy()
    rack.transformShape(rm)
    rack = rack.common(C.box(G.XC - 30, G.XC, G.YC - 10, G.YC + 10, G.PROF_Z0, G.PROF_Z1))
    fixed["RACK_m1_printed"] = rack
    # ---------------- carriage (real X carriage)
    for nm, fn in (("X_PLATE", "x_carriage_plate.step"), ("V_WHEELS_x3", "v_wheels_X.step"),
                   ("M5x25_SCREWS", "m5x25_wheel_screws_X.step"), ("M5_NYLOC", "m5_nyloc_nuts_X.step"),
                   ("M5_SPACERS", "m5_spacers_X.step"), ("ECCENTRIC", "eccentric_spacer_X.step"),
                   ("BRONZE_WASHER", "bronze_washers_X.step")):
        lift[nm] = load(fn, M)
    plate_bb = C.bb(lift["X_PLATE"])
    wheel_bb = C.bb(lift["V_WHEELS_x3"])
    # eccentric (single) wheel on -y: its -y edge
    wheels = sorted(lift["V_WHEELS_x3"].Solids, key=lambda s: s.BoundBox.Center.y)
    ecc_wheel_ymin = C.bb(wheels[0]).YMin
    # ---------------- motor + pinion
    pitch_x = G.XC - 10 + G.RACK_SEAT - 4.0               # rack pitch line (tips at local y 5, pitch 1 below)
    pin_x = pitch_x - 10.0                                # pinion pitch radius 10
    pin_z = zc + G.PIN_DZ
    face_y = ecc_wheel_ymin - G.MOTOR_FACE_GAP
    gear_y = face_y + G.PIN_GEAR_OFF
    nm_s, d, fcen = nema_frame()
    rot = App.Rotation(d, Vector(0, 1, 0))
    pl = App.Placement(Vector(pin_x, face_y, pin_z) - rot.multVec(fcen), rot)
    motor = nm_s.copy()
    motor.Placement = pl.multiply(motor.Placement)
    lift["NEMA17"] = motor
    pin = Part.read(os.path.join(PRINT, "FLIPPER_PINION.step"))
    pin = pin.copy()
    # pinion local z (motor-side face at 0) -> +y; place hub face at face_y + boss gap
    pin.Placement = App.Placement(Vector(pin_x, face_y + G.PIN_BOSS_GAP, pin_z), App.Rotation(Vector(1, 0, 0), -90))
    lift["PINION_v2"] = pin
    # motor bracket (printed): plate in x-z at y face_y-?.. motor flange side, notch for the eccentric wheel,
    # joined to the X plate's back face by a flange
    mb = C.box(pin_x - 21.15, G.XC + 12.1, face_y, face_y + 4, pin_z - 21.15, pin_z + 21.15)
    mb = mb.cut(C.cyl(11.5, 10, (pin_x, face_y - 1, pin_z), (0, 1, 0)))
    wb = C.bb(wheels[0])
    mb = mb.cut(C.box(wb.XMin - 1, wb.XMax + 1, face_y - 1, face_y + 5, wb.ZMin - 1, wb.ZMax + 1))
    mb = mb.cut(C.box(G.XC - 10.5, G.XC + 10.5, face_y - 1, face_y + 5, G.PROF_Z0 - 500, G.PROF_Z1 + 500))   # profile
    lift["MOTOR_BRACKET"] = mb.removeSplitter()
    # ---------------- flip head (arm + servo + cheek), servo bracket to the X plate's front face
    arm, head = C.flip_head(G.PX, G.Z_PICK, plate_bb.XMax)
    lift.update(head)
    arm_all.update(arm)
    for n, s in arm_all.items():
        C.add(doc, n, s, "ARM_pick_pose", groups)
    for n, s in lift.items():
        C.add(doc, n, s, "CARRIAGE_pick_pose", groups)
    for n, s in fixed.items():
        C.add(doc, n, s, "FIXED_column", groups)
    g, plate = C.grail()
    C.add(doc, "GRAIL", g, "GRAIL_pick", groups)
    C.add(doc, "GRAIL_PLATE", plate, "GRAIL_pick", groups)
    info = dict(plate_bb=plate_bb, wheel_bb=wheel_bb, ecc_ymin=ecc_wheel_ymin, pitch_x=pitch_x, pin=(pin_x, gear_y, pin_z),
                face_y=face_y, motor_bb=C.bb(motor), pin_bb=C.bb(pin), wheels=wheels)
    return arm_all, lift, fixed, (g, plate), info


def main():
    doc = App.newDocument("FLIPPER")
    groups = {}
    arm, lift, fixed, gr, info = build(doc, groups)
    P = (G.PX, G.Z_PICK)
    top = G.Z_PLACE + G.OVER - G.Z_PICK
    steps = []

    def st(label, lz, a, held, final=False, grail_lz=None, grail_a=None):
        pl_arm = C.rot_pl(P, a, lz)
        gpl = pl_arm if held else C.rot_pl(P, grail_a, grail_lz)
        steps.append(dict(label=label, pls={"arm": pl_arm, "lift": App.Placement(Vector(0, 0, lz), App.Rotation())},
                          held=held, gpl=gpl, final=final))

    for i in range(0, 5):
        st("lift %5.1f, flip 0" % (G.Z_PICK + top * i / 4.0), top * i / 4.0, 0, True)
    for a in list(range(15, 180, 15)) + [170, 175, 180]:
        st("flip %3d at %5.1f" % (a, G.Z_PICK + top), top, a, True)
    st("lower to place %5.1f" % G.Z_PLACE, top - G.OVER, 180, True, final=True)
    st("magnet off, lower %.0f" % G.REL, top - G.OVER - G.REL, 180, False, grail_lz=top - G.OVER, grail_a=180)
    parts = {n: (s, "arm") for n, s in arm.items()}
    parts.update({n: (s, "lift") for n, s in lift.items()})
    fixed_top = max(C.bb(s).ZMax for s in fixed.values())
    lines, worst = C.run_cycle(steps, parts, fixed_top)
    stow = steps[-1]["pls"]
    start_out = max(max(C.bb(C.moved(s, stow[g])).XMax for s, g in parts.values()),
                    max(C.bb(s).XMax for s in fixed.values())) - C.FACE
    fin = steps[-2]["gpl"]
    for n, s in arm.items():
        C.add(doc, "PLACE_" + n, C.moved(s, fin), "GHOST_place", groups)
    for n in ("X_PLATE", "SERVO_MG996R", "SERVO_BRACKET", "CHEEK_625", "NEMA17", "PINION_v2", "MOTOR_BRACKET"):
        C.add(doc, "PLACE_" + n, C.moved(lift[n], steps[-2]["pls"]["lift"]), "GHOST_place", groups)
    C.add(doc, "PLACE_GRAIL", C.moved(gr[0].fuse(gr[1]), fin), "GHOST_place", groups)

    # roof slot (arm parts)
    xs, ys = [], []
    for s_ in steps[-5:]:
        for n, s in arm.items():
            b = C.bb(C.moved(s, s_["pls"]["arm"]))
            if b.ZMin < C.ROOF_TOP and b.ZMax > C.ROOF_BOT and b.XMin < C.FACE:
                xs += [b.XMin, min(b.XMax, C.FACE)]
                ys += [b.YMin, b.YMax]
    slot = (min(xs) - 2, C.FACE + 1, min(ys) - 2, max(ys) + 2) if xs else None
    for n, s in C.robot_context(slot).items():
        C.add(doc, n, s, "ROBOT_CONTEXT", groups)
    drive = C.box(32, 100, -18.5, 18.5, 18.5, 55.5)
    C.add(doc, "CTX_DRIVE_MOTOR_R", drive, "ROBOT_CONTEXT", groups)
    C.add(doc, "CTX_GRAIL_BAY", C.box(BAY["x0"], BAY["x1"], BAY["y0"], BAY["y1"], BAY["z0"], BAY["z1"]), "ROBOT_CONTEXT", groups)

    # ---- layout envelope (bounding boxes vs the bay, the wheel, the drive motor); pick + top poses
    env = []
    wheel_c = (C.WHEEL["z"], C.WHEEL["r"])
    checks = [(n, C.bb(s)) for n, s in fixed.items()]
    for s_, tag in ((steps[0], "pick"), (steps[4], "top")):
        for n, (s, g) in parts.items():
            if g == "lift" or n in ("SERVO_HORN", "SHAFT_5", "ARM_HUB"):
                checks.append(("%s @%s" % (n, tag), C.bb(C.moved(s, s_["pls"][g]))))
    for n, b in checks:
        out = []
        if b.YMin < BAY["y0"] - 0.1 or b.YMax > BAY["y1"] + 0.1:
            out.append("y %.1f..%.1f (bay %.0f..%.0f)" % (b.YMin, b.YMax, BAY["y0"], BAY["y1"]))
        if b.XMin < BAY["x0"] - 0.1:
            out.append("x from %.1f (bay from %.0f)" % (b.XMin, BAY["x0"]))
        if b.ZMin < BAY["z0"] - 0.1:
            out.append("z from %.1f (bay from %.0f)" % (b.ZMin, BAY["z0"]))
        if b.ZMax > C.ROOF_BOT + 0.1 and b.XMin < C.FACE:
            out.append("z to %.1f (roof plate from %.0f)" % (b.ZMax, C.ROOF_BOT))
        if b.XMax > C.WHEEL["x0"] and b.XMin < C.WHEEL["x1"] and min(abs(b.YMin), abs(b.YMax)) < wheel_c[1] or (b.YMin < 0 < b.YMax and b.XMax > C.WHEEL["x0"]):
            yy = 0.0 if b.YMin < 0 < b.YMax else min(abs(b.YMin), abs(b.YMax))
            if yy < wheel_c[1]:
                wt = wheel_c[0] + math.sqrt(wheel_c[1] ** 2 - yy ** 2)
                if b.ZMin < wt + 1:
                    out.append("over the wheel: bottom %.1f vs wheel top %.1f" % (b.ZMin, wt))
        if b.XMin < 100 and b.XMax > 32 and b.YMin < 18.5 and b.YMax > -18.5 and b.ZMin < 55.5:
            out.append("drive motor zone (bottom %.1f)" % b.ZMin)
        if out:
            env.append("  %-34s %s" % (n[:34], "; ".join(out)))

    # ---- numbers
    pb = info["plate_bb"]
    zc_top = G.ZC_PICK + top
    wb = info["wheel_bb"]
    wheel_lo, wheel_hi = wb.ZMin - G.ZC_PICK, wb.ZMax - G.ZC_PICK          # wheel extents around the plate centre
    pin_x, gear_y, pin_z = info["pin"]
    rb = C.bb(fixed["RACK_m1_printed"])
    plate_top_place = pb.ZMax + (G.Z_PLACE - G.Z_PICK)
    arm_lower_at = lambda x: G.Z_PLACE + (G.PX - x) / (G.PX - C.X_PLACE) * (C.ROOF_TOP - G.Z_PLACE) - 7.0
    arm_mass = sum(C.mass_of(arm[n]) for n in ("ARM", "ARM_HUB", "MAG_CUP"))
    m_moving = C.G_MASS + C.MAG_MASS + arm_mass + 0.055 + 0.28 + 0.039 + 0.03 + 0.06    # + servo, NEMA, plate, wheels, brackets
    f_lift = m_moving * 9.81
    t_pin = f_lift * 0.010
    arm_c = C.com(arm["ARM"].fuse(arm["MAG_CUP"]))
    mag_c = C.com(arm["MAGNET_D30"])
    g_c = Vector(C.X_PICK, 0, C.G_H / 2)
    tmax, tang = 0.0, 0
    for a in range(0, 181, 5):
        pl = C.rot_pl(P, a)
        t = C.torque_kgcm([(C.G_MASS, pl.multVec(g_c).x), (C.MAG_MASS, pl.multVec(mag_c).x),
                           (arm_mass, pl.multVec(arm_c).x)], G.PX)
        if t > tmax:
            tmax, tang = t, a
    grail_r = math.hypot(C.X_PICK - C.G_W / 2 - G.PX, C.G_H - G.Z_PICK)
    sb = C.bb(lift["SERVO_MG996R"])
    servo_r = max(math.hypot(x - G.PX, z - G.Z_PICK) for x in (sb.XMin, sb.XMax) for z in (sb.ZMin, sb.ZMax))
    cb = C.bb(lift["CHEEK_625"])
    cheek_r = max(math.hypot(x - G.PX, z - G.Z_PICK) for x in (cb.XMin, cb.XMax) for z in (cb.ZMin, cb.ZMax))
    mbb = info["motor_bb"]

    r = ["FLIPPER (rack lift, real Two Trees X carriage + NEMA17 + printed rack) - fc/flipper_fc.py",
         "Grail %.0f x %.0f x %.0f picked by its top at x %.1f, placed upside down at x %.1f (roof top %.0f); magnet Ø%.0f x %.0f"
         % (C.G_W, C.G_W, C.G_H, C.X_PICK, C.X_PLACE, C.ROOF_TOP, C.MAG_D, C.MAG_L),
         "Flip axis x %.1f; LZ %.0f; pivot z %.1f (pick) -> %.1f (flip) -> %.1f (place) -> %.1f (stowed); travel %.1f"
         % (G.PX, G.LZ, G.Z_PICK, G.Z_PICK + top, G.Z_PLACE, G.Z_PLACE - G.REL, top + G.REL),
         "Column: real 2020 at x %.0f, y %.0f, z %.0f..%.0f; plate centre z %.1f (pick) .. %.1f (flip), pivot %.1f above it"
         % (G.XC, G.YC, G.PROF_Z0, G.PROF_Z1, G.ZC_PICK, zc_top, G.H_P),
         "",
         "CARRIAGE / DRIVE",
         "  wheels on the profile: wheel extents %.1f..%+.1f around the plate centre -> on the profile from plate z %.1f to %.1f "
         "(travel uses %.1f..%.1f: %s)"
         % (wheel_lo, wheel_hi, G.PROF_Z0 - wheel_lo, G.PROF_Z1 - wheel_hi, G.ZC_PICK, zc_top,
            "OK" if G.ZC_PICK >= G.PROF_Z0 - wheel_lo - 0.1 and zc_top <= G.PROF_Z1 - wheel_hi + 0.1 else "WHEEL OFF THE PROFILE"),
         "  rack: pitch line x %.2f (tips %.2f past the back face), z %.1f..%.1f; pinion centre x %.2f, z %.1f (pick) .. %.1f "
         "(flip), on the rack: %s"
         % (info["pitch_x"], 2.38, rb.ZMin, rb.ZMax, pin_x, pin_z, pin_z + top,
            "OK" if rb.ZMin + 11 <= pin_z - G.REL and pin_z + top <= rb.ZMax - 11 else "OFF THE RACK"),
         "  motor face y %.1f (eccentric wheel edge %.1f); gear centre y %.1f vs rack centre %.1f; motor body x %.1f..%.1f "
         "y %.1f..%.1f z %.1f..%.1f (pick)"
         % (info["face_y"], info["ecc_ymin"], gear_y, G.YC, mbb.XMin, mbb.XMax, mbb.YMin, mbb.YMax, mbb.ZMin, mbb.ZMax),
         "  lift: ~%.2f kg moving -> %.1f N on the rack, %.3f N.m on the motor (NEMA17 ~0.4); the rack can be back-driven: "
         "at 100 s / e-stop the carriage drops (Grail already released at the end; mid-carry it falls)" % (m_moving, f_lift, t_pin),
         "",
         "CYCLE (bounding boxes, no clash check). act.out = actuator x past the right face (x %.0f)" % C.FACE]
    r += lines
    r += ["", "SUMMARY"] + C.summary_lines(worst, start_out)
    r += ["  roof slot for the arm: %s" % ("x %.1f..%.1f, y %.1f..%.1f" % slot if slot else "none"),
          "  plate top at the place %.1f vs the arm's lower edge above x %.0f..%.0f: %.1f..%.1f"
          % (plate_top_place, pb.XMin, pb.XMax, arm_lower_at(pb.XMax), arm_lower_at(pb.XMin)),
          "  profile top %.0f vs the arm's lower edge above the profile (x %.0f..%.0f): %.1f..%.1f"
          % (G.PROF_Z1, G.XC - 10, G.XC + 10, arm_lower_at(G.XC + 10), arm_lower_at(G.XC - 10)),
          "  Grail nearest point to the axis %.1f; servo reaches %.1f, 625 cheek %.1f (both must stay below)"
          % (grail_r, servo_r, cheek_r),
          "  flip torque max %.1f kg.cm at %d deg (MG996R ~9.4: %.1fx)" % (tmax, tang, 9.4 / tmax if tmax else 0),
          "",
          "LAYOUT ENVELOPE (bounding boxes vs layout-v1: Grail bay x %.0f..%.0f, y %.0f..%.0f, z %.0f..%.0f; right wheel; drive motor)"
          % (BAY["x0"], BAY["x1"], BAY["y0"], BAY["y1"], BAY["z0"], BAY["z1"])]
    r += env or ["  everything inside the bay"]
    r += ["",
          "PARTS (📦 library · 🇹🇳 local · ✈️ import)",
          "  Two Trees X carriage: plate + 3 V-wheels + 3 M5x25 + nyloc + spacers + eccentric 📦 · 2020 profile cut to %.0f 📦 · "
          "NEMA17 📦 (40 mm; shorter later) · rack m1 printed (Seif's, fits) cut to %.0f · pinion v2 printed (M3 insert K5) · "
          "MG996R + horn 📦 · 625 + Ø5 shaft 📦/🇹🇳 · electromagnet Ø30 🇹🇳"
          % (G.PROF_Z1 - G.PROF_Z0, rb.ZLength),
          "  printed ABS: motor bracket, servo bracket + 625 cheek, arm + magnet cup (~%.0f g), pinion" % (arm_mass * 1000)]
    C.save(doc, "FLIPPER", r)


main()
