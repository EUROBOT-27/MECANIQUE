# base_330_js_assembly.py - base_330_js + JSUMO drive (nominal + uncertainty envelope) + 2 AMT102 odometry modules
# (+ clapets v7 module A if its STEP is there), with the fit checks.
#
# Run (after base_330_js.py):  freecadcmd base_330_js_assembly.py     (~1-2 min with the clapets module)
#   GUI (keeps colours):        freecad.exe base_330_js_assembly.py   (closes itself)
# Writes: CAD/base_330_js_assembly.FCStd + .step, base_330_js_report.txt
#
# Frame: table frame of the base: X = wheel axis, Y = forward (clapets on +Y, odometry brackets on -Y),
# Z = up, origin = robot centre ON THE FLOOR, computed for the NOMINAL wheel (Ø74).
# Placeholders (no CAD in the repo): JSUMO wheel (plain cylinder), Pololu 37D motor, hinge bracket, KSM15-FL ball unit.
# Real models: the plate + printed parts (base_330_js.py), AMT102-V from resources/CDR-2027 (parts/), the existing
# sysRoueCodeusee odometry wheel (parts/dead_wheel_sysRoueCodeusee.step), clapets module A.

import math
import os
import sys

import FreeCAD as App
import Part

HERE = (os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals()
        else r"D:\Eurbot27_git\MECANIQUE\mechanical\base_330_js")
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("base_330_js_params", os.path.join(HERE, "base_330_js.py"))
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)

V = App.Vector
CAD = os.path.join(HERE, "CAD")
AMT_STEP = os.path.join(HERE, "parts", "AMT102-V_from_CDR.step")
DW_STEP = os.path.join(HERE, "parts", "dead_wheel_sysRoueCodeusee.step")
CLAP_STEP = os.path.normpath(os.path.join(HERE, "..", "clapets", "clapets-v7", "CAD_FC", "STEP", "MODULE_A_CLAPETS.step"))
WITH_CLAPETS = os.path.exists(CLAP_STEP) and "--no-clapets" not in sys.argv

D_NOM = J.WHEEL_D_NOM
PZ0 = J.plate_top_height(D_NOM) - J.T          # plate bottom above the floor (nominal)
PT = PZ0 + J.T                                 # plate top above the floor
AXLE_Z = PT + J.SHAFT_ABOVE_SEAT

COLORS = {"plate": (0.87, 0.78, 0.60), "print": (0.20, 0.45, 0.85), "wheel": (0.10, 0.10, 0.10),
          "env": (1.0, 0.3, 0.2), "motor": (0.55, 0.55, 0.58), "metal": (0.75, 0.75, 0.78), "amt": (0.15, 0.55, 0.25),
          "spacer": (0.95, 0.75, 0.10)}


def up(s, dz=PZ0):
    s = s.copy()
    s.translate(V(0, 0, dz))
    return s


def mirror_x(s):
    return s.mirror(V(0, 0, 0), V(1, 0, 0))


def both(s):
    return Part.makeCompound([s, mirror_x(s)])


def drive(d, x_in, w):
    return Part.makeCylinder(d / 2, w, V(x_in, 0, AXLE_Z), V(1, 0, 0))


def amt_shape():
    s = Part.read(AMT_STEP)
    s.Placement = J.amt_placement()
    s = s.copy()       # bake the placement
    return s


def amt_left():
    s = Part.read(AMT_STEP)
    # mirror of amt_placement() about x = 0 (kept a proper rotation): local x -> -Y, local y -> -Z, local z -> +X
    m = App.Matrix(0, 0, 1, 0,
                   -1, 0, 0, 0,
                   0, -1, 0, 0,
                   0, 0, 0, 1)
    pl = App.Placement(m)
    pl.Base = V(-(J.ENC_FACE_X - 3.77), 0, J.PIV_Z)
    s.Placement = pl
    return s.copy()


_DW = None


def dead_wheel():
    global _DW
    if _DW is None:
        _DW = Part.read(DW_STEP)
    s = _DW.copy()
    s.Placement = J.dead_wheel_placement()
    return s.copy()


def odo_side(theta_deg=0.0):
    """Moving + fixed odometry parts of the RIGHT module in the plate frame; arm group rotated by theta about the pivot."""
    fixed = {"odo_bracket": J.odo_bracket()}
    bp = J.bought_parts()
    moving = {"odo_arm": J.odo_arm(), "dead_wheel": dead_wheel(), "amt102": amt_shape(),
              "shaft_D6": bp["shaft_D6"], "bearing_696": bp["bearing_696"], "eclip_shim": bp["eclip_shim"]}
    other = {"bearing_F623": bp["bearing_F623"], "spring": bp["spring"], "screws_M3": bp["screws_M3"]}
    if theta_deg:
        for k in moving:
            moving[k] = moving[k].copy()
            moving[k].rotate(V(0, J.PIV_Y, J.PIV_Z), V(1, 0, 0), theta_deg)
    return fixed, moving, other


def placeholders():
    P = {}
    hinge, motor, wheel, env = [], [], [], []
    for s in (1, -1):
        h = Part.makeBox(J.HINGE_PLATE_OUT - J.HINGE_X0, 40, 3, V(J.HINGE_X0, -20, PT)).fuse(
            Part.makeBox(J.HINGE_PLATE_OUT - J.MOTOR_FACE_X, 40, J.SHAFT_ABOVE_SEAT + 20, V(J.MOTOR_FACE_X, -20, PT)))
        # Pololu 37D: output shaft 7 mm off the gearbox axis -> gearbox axis 7 mm ABOVE the shaft (only way it fits)
        m = Part.makeCylinder(18.5, J.MOTOR_FACE_X - J.MOTOR_BACK_X, V(J.MOTOR_BACK_X, 0, AXLE_Z + 7.0), V(1, 0, 0))
        w = drive(D_NOM, J.WHEEL_IN_NOM, J.WHEEL_W_NOM)
        e = drive(J.WHEEL_D_MAX, J.WHEEL_IN_NOM - J.WHEEL_IN_TOL, J.WHEEL_W_MAX + 2 * J.WHEEL_IN_TOL)
        if s < 0:
            h, m, w, e = (mirror_x(x) for x in (h, m, w, e))
        hinge.append(h), motor.append(m), wheel.append(w), env.append(e)
    P["hinges_PH"] = Part.makeCompound(hinge)
    P["motors_37D_PH"] = Part.makeCompound(motor)
    P["wheels_JS7444_nominal_PH"] = Part.makeCompound(wheel)
    P["wheels_JS7444_ENVELOPE"] = Part.makeCompound(env)
    units, holders, shims = [], [], []
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = sx * J.BALL_X, sy * J.BALL_Y
            units.append(up(J.ball_unit(x, y)))
            holders.append(up(J.ball_holder(x, y)))
            if J.BALL_SHIM_T > 0:
                sh = J.ball_shim()
                sh.translate(V(x, y, J.PLATE_TOP + J.ball_base_above_top(J.WHEEL_D_NOM)))
                shims.append(up(sh))
    P["ball_units_KSM15_PH"] = Part.makeCompound(units)
    P["ball_holders"] = Part.makeCompound(holders)
    if shims:
        P["ball_shims"] = Part.makeCompound(shims)
    return P


def vol(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def main():
    lines = []
    W = lines.append
    if "base_330_js_assembly" in App.listDocuments():
        App.closeDocument("base_330_js_assembly")
    doc = App.newDocument("base_330_js_assembly")

    plate = up(Part.read(os.path.join(CAD, "base_330_js.step")))
    fixed, moving, other = odo_side()
    R = {}
    R["plate"] = plate
    for d in (fixed, moving, other):
        for k, s in d.items():
            sl = amt_left() if k == "amt102" else mirror_x(s)
            R[k] = Part.makeCompound([up(s), up(sl)])
    R.update(placeholders())

    # ---------------------------------------------------------------- interference matrix (nominal pose)
    allowed = {frozenset(p) for p in [("dead_wheel", "shaft_D6"), ("amt102", "shaft_D6"),
                                      ("eclip_shim", "shaft_D6"),     # e-clip sits in a shaft groove (not modelled)
                                      ("wheels_JS7444_nominal_PH", "wheels_JS7444_ENVELOPE"),
                                      ("ball_units_KSM15_PH", "ball_holders"),   # stud in the roof hole (radius 4 vs 4.25: no overlap expected)
                                      ("ball_units_KSM15_PH", "ball_shims")]}
    W("base_330_js_assembly.py - JSUMO JS7444 + AMT102 odometry (existing sysRoueCodeusee wheel) on the %.0f x %.0f base"
      % (J.W, J.L))
    W("Nominal wheel Ø%.0f: plate bottom %.1f / top %.1f above the floor, drive axle %.1f" % (D_NOM, PZ0, PT, AXLE_Z))
    W("Motors %.0f mm apart (back ends at x ±%.1f), wheel pocket x %.1f..%.1f y ±%.0f, perimeter (rectangle) %.0f mm" % (
        J.MOTOR_GAP, J.MOTOR_BACK_X, J.POCKET_X0, J.POCKET_X1, J.POCKET_Y, 2 * (J.W + J.L)))
    per = 2 * (J.W + J.L)
    W("Plate perimeter %.0f mm vs 1200 at start [GR F.3]: %s (margin %.0f mm; the robot hull adds what sticks out)" % (
        per, "OK" if per <= 1200 else "TOO BIG", 1200 - per))
    W("")
    W("1. Interferences (common volume > 0.01 mm3) between parts, nominal pose:")
    keys = [k for k in R if k != "wheels_JS7444_nominal_PH"]
    n_clash = 0
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if frozenset((a, b)) in allowed:
                continue
            v = vol(R[a], R[b])
            if v > 0.01 or v < 0:
                n_clash += 1
                W("   CLASH  %-26s x %-26s %.2f mm3" % (a, b, v))
    W("   -> %d clash(es) (allowed by design: wheel/AMT on the shaft = grub screw / sleeve, e-clip in its groove)" % n_clash)

    # ---------------------------------------------------------------- drive wheel envelope clearances
    W("")
    W("2. Drive wheel UNCERTAINTY ENVELOPE Ø%.0f x %.0f (x %.0f..%.0f) - clearances:" % (
        J.WHEEL_D_MAX, J.WHEEL_W_MAX + 2 * J.WHEEL_IN_TOL, J.WHEEL_IN_NOM - J.WHEEL_IN_TOL,
        J.WHEEL_IN_NOM + J.WHEEL_IN_TOL + J.WHEEL_W_MAX))
    env = R["wheels_JS7444_ENVELOPE"]
    def dist(a, b):
        return min(x.distToShape(y)[0] for x in a.Solids for y in b.Solids
                   if (x.BoundBox.XMin > 0) == (y.BoundBox.XMax > 0))

    for k in ("plate", "odo_bracket", "odo_arm", "dead_wheel", "amt102", "hinges_PH", "screws_M3", "ball_holders"):
        W("   %-14s %6.1f mm" % (k, dist(env, R[k]) if k != "plate" else env.distToShape(R[k])[0]))
    side = plate.cut(Part.makeBox(J.W, 2 * J.TONGUE_Y, 50, V(-J.W2, -J.TONGUE_Y, -10)))
    W("   plate beside the hinge tongue (|y| > %.0f) %.1f mm; the tongue itself carries the hinge foot" % (
        J.TONGUE_Y, env.distToShape(side)[0]))
    nom = R["wheels_JS7444_nominal_PH"]
    W("   nominal Ø74 x 44 wheel <-> plate %.1f mm, <-> AMT102 %.1f mm, <-> odometry arm %.1f mm" % (
        nom.distToShape(plate)[0], dist(nom, R["amt102"]), nom.distToShape(R["odo_arm"])[0]))
    mot = R["motors_37D_PH"].Solids
    W("   motor back ends %.1f mm apart" % (mot[0].BoundBox.XMin - mot[1].BoundBox.XMax))

    # ---------------------------------------------------------------- floor contact for the real wheel size
    W("")
    W("3. Floor contact vs the real JSUMO diameter (plate frame fixed, the floor moves):")
    W("   wheel Ø | plate top | ball gap (shim %.1f) | shim for %.0f mm | odo arm angle | wheel dz | spring +mm" % (
        J.BALL_SHIM_T, J.BALL_GAP))
    th_min = -math.degrees(math.asin(J.ARM_DROOP / 60.0))
    for d in (J.WHEEL_D_MIN, J.WHEEL_D_NOM, 77.0, J.WHEEL_D_MAX):
        pt = J.plate_top_height(d)
        gap = J.BALL_GAP + J.ball_shim_t(d) - J.BALL_SHIM_T
        floor_pf = -(pt - J.T)
        dz = floor_pf + J.ODO_R - J.PIV_Z
        th = math.degrees(math.asin(dz / (0 - J.PIV_Y)))
        ds = (J.SPRING_Y - J.PIV_Y) * math.sin(math.radians(th))
        W("   %5.1f   | %6.1f    | %6.1f                  | %6.1f          | %+6.2f deg    | %+5.1f    | %+5.2f" % (
            d, pt, gap, J.ball_shim_t(d), th, dz, ds))
    W("   droop stop (nut under the beam) set at %.1f deg = wheel %.1f mm below the nominal floor" % (th_min, -J.ARM_DROOP))
    bu = R["ball_units_KSM15_PH"].BoundBox
    W("   4 x KSM15-FL at (±%.0f, ±%.0f): ball bottom %.2f above the floor (Ø%.0f), holder roof %.1f above the plate top,"
      % (J.BALL_X, J.BALL_Y, bu.ZMin, D_NOM, J.HOLDER_IN))
    W("   stud left for the shim %.1f mm (shim needs ≤ %.1f for Ø%.0f); support rectangle %.0f x %.0f, plate edge %.1f / %.1f mm away" % (
        J.BALL_STUD_FREE, J.ball_shim_t(J.WHEEL_D_MAX), J.WHEEL_D_MAX, 2 * J.BALL_X, 2 * J.BALL_Y,
        J.W2 - J.BALL_X - J.HOLDER["flange_d"] / 2, J.L2 - J.BALL_Y - J.HOLDER["flange_d"] / 2))
    hb = R["ball_holders"]
    for k in ("odo_bracket", "screws_M3", "hinges_PH"):
        W("   ball holders <-> %-12s %.1f mm" % (k, hb.distToShape(R[k])[0]))

    # ---------------------------------------------------------------- arm sweep: travel before any clash
    W("")
    W("4. Arm travel (rotate the arm + wheel + AMT about the pivot; clash with plate / bracket / screws / spring?):")
    stat = Part.makeCompound([up(J.odo_bracket()), plate.copy()])
    first_up = None
    for th in [th_min] + [x * 0.5 for x in range(0, 41)]:
        _, mv, _ = odo_side(th)
        mshape = Part.makeCompound([up(s) for k, s in mv.items()])
        v = vol(mshape, stat)
        if th == th_min:
            W("   droop %.1f deg: clash volume %.2f mm3" % (th, v))
        elif v > 0.01 and first_up is None:
            first_up = th
    lim = first_up if first_up is not None else 20.0
    W("   upward: free up to %.1f deg = wheel +%.1f mm (first contact %s)" % (
        lim - 0.5, 60 * math.sin(math.radians(lim - 0.5)), "at %.1f deg" % lim if first_up else "none up to 20 deg"))
    spring_solid = J.SPRING[2] - 10.0
    W("   spring: installed %.0f mm (free %.0f) -> %.1f mm preload; wheel force = spring force x %.2f" % (
        J.SPRING[2], J.SPRING[1], J.SPRING[1] - J.SPRING[2], (J.SPRING_Y - J.PIV_Y) / (0 - J.PIV_Y)))
    W("   (spring solid ~10 mm assumed -> %.0f mm more travel at the spring)" % spring_solid)

    # ---------------------------------------------------------------- odometry numbers
    W("")
    W("5. Odometry:")
    W("   track (O-ring contact planes) %.1f mm, existing wheel Ø%.0f (O-ring tyre), contact on the axle line (y = 0)" % (
        2 * J.ODO_X, 2 * J.DW_R))
    W("   AMT102 at 2048 PPR -> 8192 counts/rev -> %.4f mm/count" % (math.pi * 2 * J.ODO_R / 8192))
    amt = R["amt102"]
    W("   x stack (right side): AMT %.1f..%.1f | beam %.1f..%.1f | shim | wheel %.1f..%.1f | plate edge %.1f" % (
        amt.BoundBox.XMin if amt.BoundBox.XMin > 0 else J.ENC_FACE_X - J.AMT_LEN, J.ENC_FACE_X,
        J.ARM_X[0], J.ARM_X[1], J.DW_X0, J.DW_X1, J.W2))
    W("   AMT102 bounding box z %.1f..%.1f above the floor" % (amt.BoundBox.ZMin, amt.BoundBox.ZMax))
    for k in ("odo_bracket", "odo_arm", "dead_wheel"):
        bb = R[k].optimalBoundingBox()
        W("   %-12s z %.1f..%.1f, |x| <= %.1f" % (k, bb.ZMin, bb.ZMax, max(abs(bb.XMin), abs(bb.XMax))))
    W("   arm/encoder above the floor: arm %.1f, AMT %.1f, odometry wheel bottom %.2f (squash %.1f)" % (
        R["odo_arm"].optimalBoundingBox().ZMin, amt.optimalBoundingBox().ZMin, R["dead_wheel"].optimalBoundingBox().ZMin,
        J.ODO_SQUASH))

    # ---------------------------------------------------------------- clapets module A
    objs = dict(R)
    if WITH_CLAPETS:
        W("")
        W("6. Clapets v7 module A (moved by 0, %d, %.1f):" % (J.CLAP_DY, PT))
        clap = Part.read(CLAP_STEP)
        clap.translate(V(0, J.CLAP_DY, PT))
        sols = clap.Solids
        ours = {k: R[k] for k in ("plate", "wheels_JS7444_ENVELOPE", "odo_bracket", "odo_arm", "amt102",
                                  "hinges_PH", "motors_37D_PH", "ball_holders", "ball_units_KSM15_PH")}
        n = 0
        best = []
        for so in sols:
            for k, s in ours.items():
                v = vol(so, s)
                if v > 0.01:
                    n += 1
                    W("   CLASH clapets solid (bb y %.0f..%.0f) x %s: %.1f mm3" % (so.BoundBox.YMin, so.BoundBox.YMax, k, v))
            if so.BoundBox.intersect(env.BoundBox) or so.BoundBox.YMin < 60:
                ob = so.optimalBoundingBox()
                # distToShape returns a false 0 on the imported NEMA17 model: never report less than the gap
                # between the exact bounding boxes
                gap = min(math.sqrt(sum(max(0.0, g) ** 2 for g in (
                    max(e.BoundBox.XMin - ob.XMax, ob.XMin - e.BoundBox.XMax),
                    max(e.BoundBox.YMin - ob.YMax, ob.YMin - e.BoundBox.YMax),
                    max(e.BoundBox.ZMin - ob.ZMax, ob.ZMin - e.BoundBox.ZMax)))) for e in env.Solids)
                best.append((max(gap, min(so.distToShape(e)[0] for e in env.Solids)), ob))
        best.sort(key=lambda t: t[0])
        W("   %d solids, %d clash(es); closest to the drive wheel envelope:" % (len(sols), n))
        for dd, bb in best[:4]:
            W("     %.1f mm  solid bb x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f" % (
                dd, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
        W("   stack face at y %.0f (%.0f mm in front of the plate edge)" % (140 + J.CLAP_DY, 140 + J.CLAP_DY - J.L2))
        objs["clapets_v7_moduleA"] = clap

    # ---------------------------------------------------------------- save
    cmap = {"plate": "plate", "odo_bracket": "print", "odo_arm": "print", "dead_wheel": "wheel", "amt102": "amt",
            "wheels_JS7444_nominal_PH": "wheel", "wheels_JS7444_ENVELOPE": "env", "motors_37D_PH": "motor",
            "ball_holders": "print", "ball_shims": "spacer", "spring": "spacer"}
    for k, s in objs.items():
        o = doc.addObject("Part::Feature", k)
        o.Shape = s
        if App.GuiUp:
            o.ViewObject.ShapeColor = COLORS[cmap.get(k, "metal")]
            if k == "wheels_JS7444_ENVELOPE":
                o.ViewObject.Transparency = 75
    doc.recompute()
    doc.saveAs(os.path.join(CAD, "base_330_js_assembly.FCStd"))
    Part.makeCompound([s for k, s in objs.items() if k != "wheels_JS7444_ENVELOPE"]).exportStep(
        os.path.join(CAD, "base_330_js_assembly.step"))
    if App.GuiUp:
        import FreeCADGui as Gui
        v = Gui.activeDocument().activeView()
        v.viewIsometric()
        v.fitAll()
        v.saveImage(os.path.join(HERE, "base_330_js_assembly.png"), 1600, 1000, "White")
    txt = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "base_330_js_report.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


_LAUNCHED = any(os.path.basename(str(a)).lower() == "base_330_js_assembly.py" for a in sys.argv)
if _LAUNCHED and App.GuiUp:
    import FreeCADGui as Gui
    from PySide import QtCore

    def _gui_run():
        try:
            main()
        except Exception:
            import tempfile
            import traceback
            with open(os.path.join(tempfile.gettempdir(), "base_330_js_assembly_error.txt"), "w") as f:
                f.write(traceback.format_exc())
        Gui.getMainWindow().close()

    QtCore.QTimer.singleShot(2000, _gui_run)
elif _LAUNCHED or __name__ == "__main__":
    main()
