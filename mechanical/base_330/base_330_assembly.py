# base_330_assembly.py - base_330 + the clapets v7 mechanism (module A) mounted on it.
#
# Run with the GUI (keeps names + colours in the FCStd and the STEP; the window closes itself, ~1 min):
#     freecad.exe base_330_assembly.py
# (freecadcmd works too, but the FCStd then opens with no colours.)
# Writes next to this file: base_330_assembly.FCStd, base_330_assembly.step (for SolidWorks).
#
# Frame = base_330 frame on the table: X = wheel axis, Y = forward (mechanism on the +Y edge), Z = up,
# origin = robot centre on the table. Plate bottom 13.5 mm above the table (base_330 README).
# The mechanism is NOT modified: MODULE_A_CLAPETS.step (clapets-v7/CAD_FC/STEP) is moved as one block by
# (0, CLAP_DY, plate top): its socle stands on the plate, 23 mm forward (see base_330.py, "Clapets v7 mount").
# Drive wheels and motors are PLACEHOLDERS (their real CAD is not in the repo): wheel Ø90 x 20, Pololu 37D body Ø37.

import os
import sys

import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("base_330_params", os.path.join(HERE, "base_330.py"))
B = importlib.util.module_from_spec(_spec)   # parameters only: base_330.main() runs only as "__main__"/"base_330"
_spec.loader.exec_module(B)

V = App.Vector
CLAP_STEP = os.path.normpath(os.path.join(HERE, "..", "clapets-v7", "CAD_FC", "STEP", "MODULE_A_CLAPETS.step"))
BASE_Z = 13.5                       # plate bottom above the table
TOP_Z = BASE_Z + B.T                # plate top = socle bottom (18.5)
SOCLE_T = 6.0                       # socle floor thickness under the M4 heads (clapets v7: RAIL_Z0)
WASHER_T, WASHER_D = 0.8, 9.0       # M4 washers (ISO 7089)
NUT_T, NUT_AF = 3.2, 7.0            # M4 nut
SCREW_L, HEAD_D, HEAD_H = 20.0, 7.6, 2.2   # M4 x 20 button head (ISO 7380)

COLORS = {"base": (0.87, 0.78, 0.60), "lift": (0.72, 0.58, 0.40), "wheel": (0.15, 0.15, 0.15),
          "motor": (0.55, 0.55, 0.58), "screw": (0.30, 0.30, 0.32), "nut": (0.80, 0.80, 0.82),
          "profile": (0.78, 0.80, 0.84), "wall": (0.80, 0.68, 0.48)}


def hex_prism(x, y, z0, af, h):
    import math
    r = af / 2 / math.cos(math.radians(30))
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def mount_fasteners():
    """4 x M4 x 20 button head from the top (washer on the socle), washer + nut under the plate."""
    screws, nuts = [], []
    zt = TOP_Z + SOCLE_T                                     # socle floor top face
    for sx in (1, -1):
        for cy in B.CLAP_Y:
            x, y = sx * B.CLAP_X, cy + B.CLAP_DY
            z_head = zt + WASHER_T
            screws.append(Part.makeCylinder(HEAD_D / 2, HEAD_H, V(x, y, z_head)).fuse(
                Part.makeCylinder(2.0, SCREW_L, V(x, y, z_head - SCREW_L))))
            nuts.append(Part.makeCylinder(WASHER_D / 2, WASHER_T, V(x, y, zt)).cut(
                Part.makeCylinder(2.2, WASHER_T, V(x, y, zt))))                       # top washer
            zb = BASE_Z - WASHER_T
            nuts.append(Part.makeCylinder(WASHER_D / 2, WASHER_T, V(x, y, zb)).cut(
                Part.makeCylinder(2.2, WASHER_T, V(x, y, zb))))                       # bottom washer
            nuts.append(hex_prism(x, y, zb - NUT_T, NUT_AF, NUT_T).cut(
                Part.makeCylinder(2.0, NUT_T, V(x, y, zb - NUT_T))))                  # nut
    return Part.makeCompound(screws), Part.makeCompound(nuts)


def back_wall_parts():
    """2 x 2020 profiles (simplified: square + centre bore) on the rear holes, the MDF back wall on their inner face,
    2 x M5 x 12 from under the plate. Returns (profiles, wall, screws)."""
    profs, screws = [], []
    for sx in (1, -1):
        x, y = sx * B.PROF_X, -B.PROF_Y
        p = Part.makeBox(20, 20, B.PROF_L, V(x - 10, y - 10, TOP_Z)).cut(
            Part.makeCylinder(2.1, B.PROF_L, V(x, y, TOP_Z)))
        profs.append(p)
        screws.append(Part.makeCylinder(4.75, 2.75, V(x, y, BASE_Z - 2.75)).fuse(
            Part.makeCylinder(2.5, 12, V(x, y, BASE_Z - 2.75 + 2.75))))          # M5 x 12 button head
    import Part as _P
    tmp = App.newDocument("_wall_tmp")
    wall = B.build(tmp, "W", B.wall_geometry(), B.BW_T).Shape.copy()
    App.closeDocument(tmp.Name)
    wall.rotate(V(0, 0, 0), V(1, 0, 0), 90)                  # (u, v, t) -> (u, -t, v)
    wall.translate(V(0, -B.PROF_Y + 10 + B.BW_T, TOP_Z))     # on the profiles' inner face (y -120): y -120..-115
    return _P.makeCompound(profs), wall, Part.makeCompound(screws)


def drive_placeholders():
    tyre_in = B.WHEEL_BOSS_X + B.WHEEL_BOSS
    wheels = [Part.makeCylinder(45, B.WHEEL_W, V(s * tyre_in, 0, 45), V(s, 0, 0)) for s in (1, -1)]
    motors = [Part.makeCylinder(18.5, B.MOTOR_FACE_X - 2, V(s * 2, 0, 45), V(s, 0, 0)) for s in (1, -1)]
    return Part.makeCompound(wheels), Part.makeCompound(motors)


def lifts():
    """Both lifts (2 x 3 mm MDF each) on the plate top, under the hinges."""
    out = []
    for s in (1, -1):
        z = TOP_Z
        for th in B.LIFT_LAYERS:
            outline, circles, _ = B.lift_geometry()
            edges = []
            for seg in outline:
                if seg[0] == "line":
                    edges.append(Part.LineSegment(V(*seg[1], 0), V(*seg[2], 0)).toShape())
                else:
                    import math
                    _, c, r, a0, a1 = seg
                    a1 = a1 if a1 > a0 else a1 + 360
                    edges.append(Part.ArcOfCircle(Part.Circle(V(*c, 0), V(0, 0, 1), r),
                                                  math.radians(a0), math.radians(a1)).toShape())
            face = Part.Face(Part.Wire(Part.__sortEdges__(edges)))
            sol = face.extrude(V(0, 0, th))
            for x, y, d in circles:
                sol = sol.cut(Part.makeCylinder(d / 2, th, V(x, y, 0)))
            if s < 0:
                sol = sol.mirror(V(0, 0, 0), V(1, 0, 0))
            sol.translate(V(0, 0, z))
            out.append(sol)
            z += th
    return Part.makeCompound(out)


def main():
    if "base_330_assembly" in App.listDocuments():
        App.closeDocument("base_330_assembly")
    doc = App.newDocument("base_330_assembly")

    def add(name, label, shape, color, group):
        o = doc.addObject("Part::Feature", name)
        o.Label = label
        o.Shape = shape
        if App.GuiUp:
            o.ViewObject.ShapeColor = color
        group.addObject(o)
        return o

    g_base = doc.addObject("App::Part", "Robot_base")
    plate = Part.read(os.path.join(HERE, "base_330.step"))
    plate.translate(V(0, 0, BASE_Z))
    add("Base_plate_330", "Base_plate_330", plate, COLORS["base"], g_base)
    add("Lifts_MDF", "Lifts_MDF_2x(3+3)", lifts(), COLORS["lift"], g_base)
    wh, mo = drive_placeholders()
    add("Drive_wheels", "Drive_wheels_PLACEHOLDER_D90", wh, COLORS["wheel"], g_base)
    add("Drive_motors", "Drive_motors_PLACEHOLDER_37D", mo, COLORS["motor"], g_base)
    sc, nu = mount_fasteners()
    add("Socle_screws", "Socle_to_base_M4x20_button_x4", sc, COLORS["screw"], g_base)
    add("Socle_nuts", "Socle_to_base_M4_nut_washers_x4", nu, COLORS["nut"], g_base)

    g_wall = doc.addObject("App::Part", "Electronics_back_wall")
    pr, wa, ms = back_wall_parts()
    add("Profiles_2020", "Profiles_2020_L200_x2", pr, COLORS["profile"], g_wall)
    add("Back_wall", "Back_wall_MDF5", wa, COLORS["wall"], g_wall)
    add("Profile_screws", "Profile_to_base_M5x12_button_x2", ms, COLORS["screw"], g_wall)

    # clapets v7 module A, imported as is (names and colours from its STEP), moved as one block
    g_clap = doc.addObject("App::Part", "Clapets_v7_module_A")
    before = set(o.Name for o in doc.Objects)
    if App.GuiUp:
        import ImportGui
        ImportGui.insert(CLAP_STEP, doc.Name)
        new = [o for o in doc.Objects if o.Name not in before]
        tops = [o for o in new if not o.InList]             # top-level imported objects
        for o in tops:
            g_clap.addObject(o)
    else:
        sh = Part.read(CLAP_STEP)
        o = doc.addObject("Part::Feature", "MODULE_A_CLAPETS")
        o.Shape = sh
        g_clap.addObject(o)
    g_clap.Placement = App.Placement(V(0, B.CLAP_DY, TOP_Z), App.Rotation())
    doc.recompute()

    # ---- checks: socle on the plate, hole axes, clearance mechanism <-> drive placeholders
    clap = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.InList and o.Shape.Solids
            and g_clap in o.InListRecursive]
    lines = []
    drive = Part.makeCompound([wh, mo, doc.Lifts_MDF.Shape])
    worst = []
    for o in clap:
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        worst.append((s.distToShape(drive)[0], o.Label))
    worst.sort()
    lines.append("Closest mechanism parts to the drive (placeholders + lifts):")
    lines += ["  %6.1f mm  %s" % w for w in worst[:6]]
    socle = [o for o in clap if o.Label.startswith("A_SOCLE")]
    if socle:
        s = socle[0].Shape.copy()
        s.Placement = socle[0].getGlobalPlacement()
        bb = s.BoundBox
        lines.append("Socle: z %.2f..%.2f (plate top %.1f), y %.1f..%.1f" % (bb.ZMin, bb.ZMax, TOP_Z, bb.YMin, bb.YMax))
        lines.append("Socle <-> plate overlap volume: %.3f mm3" % s.common(plate).Volume)
    # gap in Y (the wall is a flat slab across the rear; distToShape gives a false 0 on the imported NEMA model)
    d_clap = 1e9
    for o in clap:
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        d_clap = min(d_clap, s.BoundBox.YMin - wa.BoundBox.YMax)
    lines.append("Back wall: y %.1f..%.1f, z %.1f..%.1f; overlap with plate %.3f, profiles %.3f mm3; "
                 "%.1f mm from the drive, %.1f mm from module A" % (
                     wa.BoundBox.YMin, wa.BoundBox.YMax, wa.BoundBox.ZMin, wa.BoundBox.ZMax,
                     wa.common(plate).Volume, wa.common(pr).Volume, wa.distToShape(drive)[0], d_clap))
    lines.append("Profiles: overlap with plate %.3f mm3, M5 screws vs plate %.3f mm3" % (
        pr.common(plate).Volume, ms.common(plate).Volume))
    print("\n".join(lines))

    step = os.path.join(HERE, "base_330_assembly.step")
    if App.GuiUp:
        import ImportGui
        ImportGui.export([g_base, g_wall, g_clap], step)
    else:
        Part.makeCompound([o.Shape for o in (g_base, g_wall, g_clap)]).exportStep(step)
    doc.saveAs(os.path.join(HERE, "base_330_assembly.FCStd"))
    with open(os.path.join(HERE, "base_330_assembly_report.txt"), "w") as f:
        f.write("base_330_assembly.py - clapets v7 module A on base_330 (moved by 0, %.1f, %.1f)\n\n"
                % (B.CLAP_DY, TOP_Z) + "\n".join(lines) + "\n")


_LAUNCHED = any(os.path.basename(str(a)).lower() == "base_330_assembly.py" for a in sys.argv)
if _LAUNCHED and App.GuiUp:
    import FreeCADGui as Gui
    from PySide import QtCore

    def _gui_run():
        try:
            main()
        except Exception:
            import tempfile
            import traceback
            with open(os.path.join(tempfile.gettempdir(), "base_330_assembly_error.txt"), "w") as f:
                f.write(traceback.format_exc())
        Gui.getMainWindow().close()

    QtCore.QTimer.singleShot(2000, _gui_run)
elif _LAUNCHED or __name__ == "__main__":
    main()
