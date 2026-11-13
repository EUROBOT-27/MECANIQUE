# v1_fc.py - Baha's "essai mecanisme 1" (SolidWorks, 2026-11-10) rebuilt in FreeCAD so it can be opened, measured and
# moved with the slider macro (sliders_fc.py).
#   Run (from mechanical/grail-lift):  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v1_fc.py
#   -> CAD_FC/GRAIL_LIFT_V1.FCStd, CAD_FC/joints_v1.json, CAD_FC/v1_report.txt, CAD_FC/STEP/GRAIL_LIFT_V1.step
#
# Sources:
#   * Real parts: CAD_FC/STEP/v1_sw_export/essai_mecanisme_1_partial.step = the assembly exported from SOLIDWORKS with
#     the parts that resolved (ISO rack 1M 280, ISO 20T 1M gear, M6 nut, MG996R, 4-pad horn, 5 kg electromagnet).
#   * Rebuilt (APPROXIMATE, from the assembly's saved preview image, the mates and the parts around them) because their
#     files stayed on Baha's PC: the 280 mm profile, "support fixation es7i7" (grey box holding the motor),
#     "support en u extension lel bras" (blue box holding the servo + magnet). NEMA14: not in the STEP export ->
#     block model from the sizes SOLIDWORKS reported. Coupling ("liaison bin el pignon wel motour"): real dims (Ø7 x 25
#     + Ø10.4 x 1 flange). The Mini V Gantry Set was suppressed in the assembly (not modelled).
# Frame: the SOLIDWORKS assembly is tilted ~2.5 deg; everything is brought into the profile's own frame, then
#   x = SW profile X (magnet side), y = -SW profile Z, z = SW profile Y - 15 (ASSUMPTION: profile bottom 5 mm above
#   the table; the assembly does not say how the lift is mounted).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import Import
import Part
from FreeCAD import Vector

import grail_common as C

STEP_IN = os.path.join(C.CAD, "STEP", "v1_sw_export", "essai_mecanisme_1_partial.step")
OUT_FC = os.path.join(C.CAD, "GRAIL_LIFT_V1.FCStd")
Z_SHIFT = -15.0

# profile component frame in the SW assembly (rows = its X, Y, Z axes in assembly coords, origin), from the SW API
XP, YP, ZP = Vector(0.999, -0.004, 0.044), Vector(0.003, 1.0, 0.018), Vector(-0.044, -0.017, 0.999)
O = Vector(709.0, 788.2, 1244.5)
XP.normalize()
ZP = XP.cross(YP)
ZP.normalize()
YP = ZP.cross(XP)
# world (SW) -> FC: first SW -> profile local, then local (X, Y, Z) -> FC (X, -Z, Y + Z_SHIFT)
M_LOCAL = C.mat_from_rows((XP.x, XP.y, XP.z), (YP.x, YP.y, YP.z), (ZP.x, ZP.y, ZP.z))
M_FC = C.mat_from_rows((1, 0, 0), (0, 0, -1), (0, 1, 0))


def sw_to_fc(shape):
    s = shape.copy()
    s.translate(-O)
    s.transformShape(M_LOCAL)                      # exact for rigid moves (transformGeometry makes B-splines)
    s.transformShape(M_FC)
    s.translate(Vector(0, 0, Z_SHIFT))
    return s


def lbox(X0, X1, Y0, Y1, Z0, Z1):
    """Box given in the profile's local frame (SW X, Y, Z) -> FC."""
    return C.box(X0, X1, -Z1, -Z0, Y0 + Z_SHIFT, Y1 + Z_SHIFT)


def lcyl_x(r, X0, X1, Y, Z):
    return C.cyl(r, X1 - X0, (X0, -Z, Y + Z_SHIFT), (1, 0, 0))


def shell(X0, X1, Y0, Y1, Z0, Z1, t, open_faces):
    outer = lbox(X0, X1, Y0, Y1, Z0, Z1)
    ix0 = X0 - 1 if "-X" in open_faces else X0 + t
    ix1 = X1 + 1 if "+X" in open_faces else X1 - t
    iy0 = Y0 - 1 if "-Y" in open_faces else Y0 + t
    iy1 = Y1 + 1 if "+Y" in open_faces else Y1 - t
    iz0 = Z0 - 1 if "-Z" in open_faces else Z0 + t
    iz1 = Z1 + 1 if "+Z" in open_faces else Z1 - t
    return outer.cut(lbox(ix0, ix1, iy0, iy1, iz0, iz1))


def build():
    doc = App.newDocument("GRAIL_LIFT_V1")
    tmp = App.newDocument("v1_import")
    Import.insert(STEP_IN, tmp.Name)
    parts = {}
    servo = []
    for o in tmp.Objects:
        if o.TypeId != "Part::Feature" or o.Shape.isNull():
            continue
        lab = o.Label
        sh = sw_to_fc(o.Shape)
        if lab.startswith("rack"):
            parts["REAL_RACK_1M_280"] = sh
        elif lab.startswith("spur gear"):
            parts["REAL_PINION_20T_1M"] = sh
        elif lab.startswith("hex nut"):
            parts["REAL_NUT_M6"] = sh
        elif lab.startswith("mg996R"):
            servo.append(sh)
        elif lab.startswith("mg996_arm"):
            parts["REAL_HORN_4PAD"] = sh
        elif lab.startswith("Magnet"):
            parts["REAL_MAGNET_5KG"] = sh
    App.closeDocument(tmp.Name)
    parts["REAL_SERVO_MG996R"] = Part.makeCompound(servo)

    # ---- rebuilt parts (approximate) ----
    parts["APPROX_PROFILE_2020_280"] = C.profile_2020(20 + Z_SHIFT, 300 + Z_SHIFT, 0, 6)   # local X -10..10, Z -16..4
    grey = shell(12, 85, 232, 302, -22, 40, 3, ("-Y",))
    grey = grey.fuse(lbox(31.8, 34.8, 235, 299, -19, 37))                                  # motor wall
    grey = grey.cut(lcyl_x(11.25, 30, 36, 270.0, 17.4)).cut(lcyl_x(6, 10, 16, 270.0, 17.4))
    parts["APPROX_SUPPORT_FIXATION_grey"] = grey.removeSplitter()
    blue = shell(85, 138.5, 236, 298, -34, 45, 3, ("-X", "+Y"))
    parts["APPROX_SUPPORT_U_blue"] = blue.removeSplitter()
    # NEMA14 (block model): flange+body x 34.8..64.4, 35 x 35 about the axis (Y 270, Z 17.4); shaft Ø5 x 13.5..34.8;
    # connector block (SW box 64.4..91.5)
    nema = lbox(34.8, 64.4, 252.5, 287.5, -0.1, 34.9).fuse(lbox(64.4, 91.5, 262, 278, 2, 33))
    parts["APPROX_NEMA14"] = nema.removeSplitter()
    parts["REAL_NEMA14_SHAFT"] = lcyl_x(2.5, 13.5, 34.8, 270.0, 17.4)
    coup = lcyl_x(3.5, -3.2, 21.8, 270.0, 17.4).fuse(lcyl_x(5.2, -4.2, -3.2, 270.0, 17.4))
    parts["REAL_COUPLING_liaison"] = coup

    for name, sh in parts.items():
        f = doc.addObject("Part::Feature", name)
        f.Shape = sh
    doc.recompute()
    return doc, parts


def main():
    doc, parts = build()
    rep = []
    # travel: the 20T gear must stay on the rack (gear centre z between rack ends +- tip radius), carriage above table
    rk = parts["REAL_RACK_1M_280"].BoundBox
    gr = parts["REAL_PINION_20T_1M"].BoundBox
    moving = [n for n in parts if n not in ("REAL_RACK_1M_280", "APPROX_PROFILE_2020_280")]
    mov_bb = None
    for n in moving:
        b = parts[n].BoundBox
        mov_bb = b if mov_bb is None else mov_bb.united(b)
    gz = gr.Center.z
    up = (rk.ZMax - 11) - gz
    down = max((rk.ZMin + 11) - gz, 2.0 - mov_bb.ZMin)
    mag = parts["REAL_MAGNET_5KG"].BoundBox
    # servo shaft axis (the Ø6 shaft solid of the MG996R model): the tilt axis
    shaft = [s for s in parts["REAL_SERVO_MG996R"].Solids if 300 < s.Volume < 450][0].BoundBox
    axis_pt = (shaft.Center.x, shaft.Center.y, shaft.Center.z)
    horn = parts["REAL_HORN_4PAD"].BoundBox
    rep.append("GRAIL LIFT v1 (Baha, essai mecanisme 1) - rebuilt %s" % "2026-11-10")
    rep.append("profile bottom assumed 5 mm above the table (not given by the assembly)")
    rep.append("moving block (everything but profile + rack): x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f  -> height %.1f mm"
               % (mov_bb.XMin, mov_bb.XMax, mov_bb.YMin, mov_bb.YMax, mov_bb.ZMin, mov_bb.ZMax, mov_bb.ZLength))
    rep.append("lift travel on the rack, from the model pose: %.1f .. +%.1f mm  (total %.1f mm)" % (down, up, up - down))
    rep.append("magnet centre z at model pose %.1f -> range %.1f .. %.1f" % (mag.Center.z, mag.Center.z + down, mag.Center.z + up))
    rep.append("servo shaft (tilt axis) at x %.2f z %.2f ; 4-pad horn centre x %.2f z %.2f -> horn off the shaft by %.2f mm"
               % (axis_pt[0], axis_pt[2], horn.Center.x, horn.Center.z,
                  ((horn.Center.x - axis_pt[0]) ** 2 + (horn.Center.z - axis_pt[2]) ** 2) ** 0.5))
    rep.append("")
    rep.append("interferences at the model pose (common volume > 1 mm3):")
    names = list(parts)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = parts[names[i]], parts[names[j]]
            if not a.BoundBox.intersect(b.BoundBox):
                continue
            try:
                v = a.common(b).Volume
            except Exception:
                v = -1
            if v > 1:
                rep.append("  %-32s x %-32s %8.1f mm3" % (names[i], names[j], v))
    # joints for the slider macro: lift = displacement from the model pose; tilt about the servo shaft (axis along y)
    tilt_group = ["APPROX_SUPPORT_U_blue", "REAL_MAGNET_5KG", "REAL_HORN_4PAD", "REAL_NUT_M6"]
    lift_group = [n for n in moving if n not in tilt_group]
    grail_x0 = mag.XMax
    # Grail: 80 cube with a 1.5 steel plate, gripped at mid-height, on the table when the lift is at its lowest
    g = 80.0
    gz0 = 0.0
    lift_low = down
    pick_mag_z = mag.Center.z + lift_low
    grail = C.box(grail_x0 + 1.5, grail_x0 + 1.5 + g, mag.Center.y - g / 2, mag.Center.y + g / 2, gz0, gz0 + g)
    plate = C.box(grail_x0, grail_x0 + 1.5, mag.Center.y - 15, mag.Center.y + 15, pick_mag_z - 15, pick_mag_z + 15)
    f = doc.addObject("Part::Feature", "GRAIL_80")
    f.Shape = grail.fuse(plate)
    floor = doc.addObject("Part::Feature", "ENV_TABLE")
    floor.Shape = C.box(-150, 350, -150, 150, -2, 0)
    doc.recompute()
    rep.append("")
    rep.append("Grail 80 cube gripped at %.1f above its bottom (magnet at the lowest lift). Highest Grail bottom with the "
               "lift alone: %.1f mm (L4 needs > %.0f)" % (pick_mag_z, up - down, C.ROOF_MIN))
    J = {
        "name": "v1", "fcstd": os.path.basename(OUT_FC),
        "lift": {"objects": lift_group + tilt_group, "base": 0.0, "min": round(down, 1), "max": round(up, 1),
                 "label": "Lift (mm from model pose)"},
        "flip": {"objects": tilt_group, "axis_point": list(axis_pt), "axis_dir": [0, -1, 0], "base": 0.0,
                 "min": -120.0, "max": 120.0, "label": "Tilt about the servo shaft (deg)"},
        "grail": {"objects": ["GRAIL_80"], "start_offset": [0, 0, 0]},
        "actuators": lift_group + tilt_group,
        "fixed": ["APPROX_PROFILE_2020_280", "REAL_RACK_1M_280", "ENV_TABLE"],
        "limits": {"h_max": C.H_MAX, "roof": 305.0, "edge_x": None},
        "colors": {"APPROX_SUPPORT_U_blue": [0.15, 0.35, 0.85], "APPROX_SUPPORT_FIXATION_grey": [0.75, 0.75, 0.75],
                   "REAL_MAGNET_5KG": [0.6, 0.6, 0.6], "GRAIL_80": [0.95, 0.75, 0.1], "ENV_TABLE": [0.3, 0.55, 0.3],
                   "APPROX_NEMA14": [0.15, 0.15, 0.15], "REAL_SERVO_MG996R": [0.1, 0.1, 0.1],
                   "APPROX_PROFILE_2020_280": [0.8, 0.8, 0.85]},
        "transparent": {"ENV_TABLE": 60},
        "sequence": [
            [0, 0.0, 0.0, 0, 0, "model pose (as saved in SOLIDWORKS)"],
            [2.0, round(down, 1), 0.0, 0, 0, "lift down to the Grail"],
            [0.5, round(down, 1), 0.0, 1, 0, "magnet ON"],
            [2.5, round(up, 1), 0.0, 1, 0, "lift to the top of the rack"],
            [1.5, round(up, 1), -90.0, 1, 0, "tilt -90 deg"],
            [1.5, round(up, 1), 90.0, 1, 0, "tilt +90 deg"],
            [1.0, round(up, 1), 0.0, 1, 0, "back to 0"],
        ],
    }
    C.save_joints(os.path.join(C.CAD, "joints_v1.json"), J)
    os.makedirs(os.path.join(C.CAD, "STEP"), exist_ok=True)
    doc.saveAs(OUT_FC)
    Import.export([o for o in doc.Objects if o.TypeId == "Part::Feature"], os.path.join(C.CAD, "STEP", "GRAIL_LIFT_V1.step"))
    with open(os.path.join(C.CAD, "v1_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep))


main()
