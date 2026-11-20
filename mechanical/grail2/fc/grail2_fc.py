# grail2_fc.py - Baha's "essai mecanisme vis ecrou 1.0" (SolidWorks, 2026-11-19) rebuilt in FreeCAD + headless motion check.
#   Run (from mechanical/grail2):  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/grail2_fc.py
#   -> CAD_FC/GRAIL2.FCStd, CAD_FC/joints_grail2.json, CAD_FC/grail2_report.txt, CAD_FC/STEP/GRAIL2.step
#
# Sources (frame: see g2_common.py):
#   * SW_*   = Baha's own parts, exact: exported from SOLIDWORKS (tools/solidworks/dump_asm.cs) to CAD_FC/STEP/sw_export/
#              and placed with the component transforms of the assembly (sw_dump.json).
#   * REAL_* = bought-part models that were in the assembly (coupling CXJH D25, 4-pad servo arm, 5 kg electromagnet).
#   * REF_*  = parts whose SW file stayed on Baha's PC (suppressed in the assembly), replaced by our library models and
#              placed with the mate geometry still stored in the assembly: NEMA17, T8 nut, MG996R.
#   * APPROX_* = parts whose file is missing and that we have no model of, rebuilt to fit the mates: round servo horn,
#              "support en u" (the flip U), "multipurpose bracket" (servo holder). Their shape is an ASSUMPTION.
#   * ADD_*  = our addition (2026-11-20, Maatoug): TRANSLATION GUIDE ("bloc de guidage en translation") from lab parts:
#              1 Ø8 smooth rod behind the screw + 2 SCS8UU blocks on a printed guide plate (on the nut mount and the
#              bloc's ears) + a printed top plate holding the rod top and a 608 bearing on the screw top + a printed rod
#              foot on the stepper support. Stops the carriage turning with the screw, holds the screw at both ends.
#              SCS8UU at the catalogue size (30 long, 34 wide, 22 high, rod axis 11 above the base): MEASURE ours.
#   * The pin "tige articulation vis ecrou" (Ø5 x 60, in the folder but not in the assembly) is put through the Ø5
#     holes of the nut mount and the bloc, where it obviously goes.
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import Import
import Part
from FreeCAD import Vector

import g2_common as C

sys.path.insert(0, os.path.join(C.MECH, "resources", "linear-motion"))
import linear_parts as LP                                    # SCS8UU / SK8 catalogue models (lab parts)

OUT_FC = os.path.join(C.CAD, "GRAIL2.FCStd")
DUMP = os.path.join(C.SW_EXPORT, "sw_dump.json")

SW_PARTS = {          # SW component name prefix -> (object name, STEP file in sw_export)
    "CXJH-C-D25": ("REAL_COUPLING_CXJH_D25_d5_e5", "CXJH-C-D25-d5-e5.step.step"),
    "mg996_arm_4pad": ("REAL_SERVO_ARM_4PAD_unmated", "mg996_arm_4pad (1).step.step"),
    "support fixation stepper": ("SW_SUPPORT_STEPPER", "support fixation stepper.step"),
    "vis 300mm": ("SW_SCREW_T8_L300_lead8", "vis 300mm.step"),
    "piece de fixation sur l ecrou": ("SW_NUT_MOUNT", "piece de fixation sur l ecrou.step"),
    "bloc de rotation 180": ("SW_BLOC_ROTATION_180", "bloc de rotation 180.step"),
    "Magnet 5KG": ("REAL_MAGNET_5KG", "Magnet 5KG.step.step"),
}
NEMA_STEP = os.path.join(C.MECH, "clapets", "clapets-v5", "CAD_FC", "STEP", "REF_NEMA17.step")
NUT_STEP = os.path.join(C.MECH, "clapets", "clapets-v5", "CAD_FC", "STEP", "REF_ECROU_T8.step")
SERVO_STEP = os.path.join(C.MECH, "grail-lift", "sw", "servo-duplicates", "mg996R_v2.step")

# ---- numbers read from the assembly (SW mate geometry, converted to the grail2 frame)
AXIS = Vector(0.0, 57.285, 186.144)        # servo output axis (horn / U pivot / bloc Ø6.3 hole), along x
HORN_FACE_X = -34.660                      # U arm face that touches the horn (SW X 639.335)
SPLINE_TOP_X = -29.260                     # servo spline boss top (SW X 644.735, Ø12.95)
U_PIN_FACE_X = 35.400                      # U face on the pin side: SW says X 709.835 = inside the bloc wall (stale,
                                           # U suppressed) -> put 0.1 mm off the wall's inner face (x 35.5)
PIN_HOLE = (-7.855, 154.144)               # Ø5 cross holes of nut mount + bloc (y, z), along x
NUT_FLANGE_TOP_Z = 134.144                 # T8 nut flange against the nut mount bottom (SW Y 980.12)
MOTOR_FACE_Z = 40.0                        # NEMA17 face against the stepper support (SW Y 885.98)
U_BASE_R = 40.0                            # U base inner face, from the axis (SW: Ø30.3 magnet hole circle)
U_T = 2.5                                  # ASSUMED U sheet thickness
U_W = 36.0                                 # ASSUMED U width (must clear the Ø30.3 magnet hole)

COLORS = {"SW_BLOC_ROTATION_180": (0.15, 0.35, 0.85), "SW_NUT_MOUNT": (0.95, 0.55, 0.1),
          "SW_SUPPORT_STEPPER": (0.75, 0.75, 0.75), "SW_SCREW_T8_L300_lead8": (0.85, 0.85, 0.9),
          "REF_NUT_T8": (0.8, 0.65, 0.2), "REF_NEMA17": (0.15, 0.15, 0.15), "REF_SERVO_MG996R": (0.1, 0.1, 0.1),
          "APPROX_U_BRACKET": (0.9, 0.2, 0.2), "APPROX_SERVO_BRACKET": (0.5, 0.5, 0.55),
          "APPROX_HORN_ROUND": (0.95, 0.95, 0.95), "REAL_MAGNET_5KG": (0.6, 0.6, 0.6),
          "REAL_COUPLING_CXJH_D25_d5_e5": (0.7, 0.7, 0.75), "SW_PIN_TIGE_D5x60": (0.3, 0.3, 0.3),
          "REAL_SERVO_ARM_4PAD_unmated": (1.0, 0.0, 1.0), "ADD_GUIDE_ROD_D8": (0.85, 0.85, 0.9),
          "ADD_SCS8UU_x2": (0.75, 0.78, 0.82), "ADD_GUIDE_PLATE_printed": (0.2, 0.7, 0.3),
          "ADD_SK8_rod_foot": (0.75, 0.78, 0.82), "ADD_SK8_BRACKET_printed": (0.2, 0.7, 0.3), "ADD_TOP_PLATE_608_printed": (0.2, 0.7, 0.3)}

# ---- translation guide (ADD_*), grail2 frame
GUIDE = {"rod_y": -32.0, "rod_z": (47.0, 365.6),        # Ø8 rod behind the screw, from the SK8 (on the support) to the top plate
         "scs": (30.0, 34.0, 22.0, 11.0),               # SCS8UU: length, width, height, rod axis height above its base
         "plate_y": (-21.0, -11.0),                     # printed guide plate: from the SCS bases to the nut mount back
         "z0": 134.144,                                 # bottom of the carriage (nut mount / bloc floor)
         "top_t": 8.0}                                  # top plate thickness (holds the 608: Ø22 x 7)

LIFT_OBJS = ["SW_NUT_MOUNT", "SW_BLOC_ROTATION_180", "SW_PIN_TIGE_D5x60", "REF_NUT_T8", "REF_SERVO_MG996R",
             "APPROX_SERVO_BRACKET", "REAL_SERVO_ARM_4PAD_unmated", "ADD_SCS8UU_x2", "ADD_GUIDE_PLATE_printed"]
FLIP_OBJS = ["APPROX_U_BRACKET", "APPROX_HORN_ROUND", "REAL_MAGNET_5KG"]
SCREW_OBJS = ["SW_SCREW_T8_L300_lead8", "REAL_COUPLING_CXJH_D25_d5_e5"]
FIXED_OBJS = ["REF_NEMA17", "SW_SUPPORT_STEPPER", "ADD_GUIDE_ROD_D8", "ADD_SK8_rod_foot", "ADD_SK8_BRACKET_printed",
              "ADD_TOP_PLATE_608_printed"]
# touching by design (fasteners, shafts in bores, parts screwed together): not reported as clashes
EXPECTED = {frozenset(p) for p in (
    ("SCREW_PROXY", "REF_NUT_T8"), ("SCREW_PROXY", "REAL_COUPLING_CXJH_D25_d5_e5"),
    ("REAL_COUPLING_CXJH_D25_d5_e5", "REF_NEMA17"), ("REF_NEMA17", "SW_SUPPORT_STEPPER"),
    ("SW_PIN_TIGE_D5x60", "SW_BLOC_ROTATION_180"), ("SW_PIN_TIGE_D5x60", "SW_NUT_MOUNT"),
    ("REF_NUT_T8", "SW_NUT_MOUNT"), ("REF_SERVO_MG996R", "APPROX_HORN_ROUND"),
    ("APPROX_HORN_ROUND", "APPROX_U_BRACKET"), ("APPROX_U_BRACKET", "SW_BLOC_ROTATION_180"),
    ("REAL_MAGNET_5KG", "APPROX_U_BRACKET"), ("REF_SERVO_MG996R", "APPROX_SERVO_BRACKET"),
    ("APPROX_SERVO_BRACKET", "SW_BLOC_ROTATION_180"),
    ("ADD_GUIDE_ROD_D8", "ADD_SCS8UU_x2"), ("ADD_SCS8UU_x2", "ADD_GUIDE_PLATE_printed"),
    ("ADD_GUIDE_PLATE_printed", "SW_NUT_MOUNT"), ("ADD_GUIDE_PLATE_printed", "SW_BLOC_ROTATION_180"),
    ("ADD_GUIDE_PLATE_printed", "SW_PIN_TIGE_D5x60"),
    ("ADD_SK8_rod_foot", "ADD_GUIDE_ROD_D8"), ("ADD_SK8_rod_foot", "ADD_SK8_BRACKET_printed"),
    ("ADD_SK8_BRACKET_printed", "SW_SUPPORT_STEPPER"),
    ("ADD_TOP_PLATE_608_printed", "ADD_GUIDE_ROD_D8"), ("ADD_TOP_PLATE_608_printed", "SCREW_PROXY"))}
IGNORE = {"REAL_SERVO_ARM_4PAD_unmated", "SW_SCREW_T8_L300_lead8"}    # unmated leftover / replaced by the proxy


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl(r, p0, p1):
    p0, p1 = Vector(*p0), Vector(*p1)
    return Part.makeCylinder(r, (p1 - p0).Length, p0, p1 - p0)


def placed(path, rows, offset):
    """Read a STEP and place it: rows = images of the local x, y, z axes (columns of the rotation)."""
    s = Part.read(path)
    ex, ey, ez = rows
    m = App.Matrix(ex[0], ey[0], ez[0], offset[0],
                   ex[1], ey[1], ez[1], offset[1],
                   ex[2], ey[2], ez[2], offset[2], 0, 0, 0, 1)
    s.transformShape(m)
    return s


def u_bracket():
    """APPROX 'support en u' at flip 0 (magnet along +y): two arms + base with the Ø30.3 magnet hole + Ø6 pivot pin."""
    ay, az = AXIS.y, AXIS.z
    r_out = U_BASE_R + U_T

    def arm(x0, x1):
        a = box(x0, x1, ay, ay + r_out, az - U_W / 2, az + U_W / 2)
        return a.fuse(cyl(U_W / 2, (x0, ay, az), (x1, ay, az)))

    s = arm(HORN_FACE_X - U_T, HORN_FACE_X).fuse(arm(U_PIN_FACE_X - U_T, U_PIN_FACE_X))
    s = s.fuse(box(HORN_FACE_X - U_T, U_PIN_FACE_X, ay + U_BASE_R, ay + r_out, az - U_W / 2, az + U_W / 2))
    s = s.cut(cyl(15.15, (1.84, ay + U_BASE_R - 1, az), (1.84, ay + r_out + 1, az)))
    s = s.fuse(cyl(3.0, (U_PIN_FACE_X - 0.1, ay, az), (37.5, ay, az)))           # pivot pin into the bloc Ø6.3 hole
    return s.removeSplitter()


def servo_bracket():
    """APPROX 'multipurpose bracket': two posts from the bloc floor (4 x Ø4 holes) to the servo tabs."""
    parts = []
    for yc in (23.0, 71.6):                                    # servo tab centres
        parts.append(box(-17.76, -14.76, yc - 2.3, yc + 2.3, 136.144, 196.4))     # post behind the tab
        parts.append(box(-25.3, -13.3, yc - 5.0, yc + 5.0, 136.144, 139.144))     # foot on the floor holes
    return parts[0].fuse(parts[1:]).removeSplitter()


def build():
    import json
    with open(DUMP, encoding="utf-8") as f:
        dump = json.load(f)
    F = C.sw_frame()
    shapes, notes = {}, []
    for c in dump["components"]:
        if not c["loaded"]:
            notes.append("missing in the assembly folder (suppressed): %s" % os.path.basename(c["path"]))
            continue
        for pre, (name, fn) in SW_PARTS.items():
            if c["name"].startswith(pre):
                s = Part.read(os.path.join(C.SW_EXPORT, fn))
                s.transformShape(C.comp_matrix(c))
                s.transformShape(F)
                shapes[name] = s
                if name == "REAL_MAGNET_5KG":
                    r = c["rot"]
                    d = Vector(r[3], r[4], r[5])                         # magnet axis (part Y) in SW coords
                    d = Vector(d.x, -d.z, d.y)                           # -> grail2 frame
                    o = Vector(c["pos"][0] - C.SW_ORIGIN[0], -(c["pos"][2] - C.SW_ORIGIN[1]), c["pos"][1] - C.SW_ORIGIN[2])
                    tilt = math.degrees(math.atan2(d.z, d.y))
                    s.rotate(AXIS, Vector(1, 0, 0), -tilt)               # flip 0 = magnet pointing +y
                    v = o - AXIS
                    v.x = 0.0
                    off = abs(v.y * d.z - v.z * d.y) / math.hypot(d.y, d.z)   # magnet axis line -> servo axis, in y-z
                    notes.append("magnet axis as saved: %.1f deg above +y, passes %.2f mm from the servo axis "
                                 "(re-aligned to flip 0)" % (tilt, off))
    # library parts placed on the mates
    shapes["REF_NEMA17"] = placed(NEMA_STEP, ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0, -33.5, MOTOR_FACE_Z - 46.0))
    shapes["REF_NUT_T8"] = placed(NUT_STEP, ((1, 0, 0), (0, -1, 0), (0, 0, -1)), (0, 33.5, NUT_FLANGE_TOP_Z + 106.5))
    shapes["REF_SERVO_MG996R"] = placed(SERVO_STEP, ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
                                        (SPLINE_TOP_X + 11.5, AXIS.y, AXIS.z))
    shapes["APPROX_HORN_ROUND"] = cyl(10.0, (HORN_FACE_X, AXIS.y, AXIS.z), (HORN_FACE_X + 4.5, AXIS.y, AXIS.z))
    shapes["APPROX_U_BRACKET"] = u_bracket()
    shapes["APPROX_SERVO_BRACKET"] = servo_bracket()
    pin = Part.read(os.path.join(C.SW_EXPORT, "tige articulation vis ecrou.step"))
    pin.rotate(Vector(0, 0, 0), Vector(0, 1, 0), 90)                            # its z axis -> +x
    pin.translate(Vector(-30.0, PIN_HOLE[0], PIN_HOLE[1]))
    shapes["SW_PIN_TIGE_D5x60"] = pin
    shapes.update(guide(shapes["SW_SCREW_T8_L300_lead8"].BoundBox.ZMax))
    return shapes, notes


def guide(screw_top):
    """ADD: translation guide = Ø8 rod + 2 SCS8UU + printed guide plate, rod foot, top plate with a 608 on the screw."""
    ry, (rz0, rz1) = GUIDE["rod_y"], GUIDE["rod_z"]
    L_, W_, H_, h_ = GUIDE["scs"]
    py0, py1 = GUIDE["plate_y"]
    z0 = GUIDE["z0"]
    out = {"ADD_GUIDE_ROD_D8": cyl(4.0, (0, ry, rz0), (0, ry, rz1))}
    blocks = []
    for k in range(2):                                   # vendor SCS8UU, its flat (holes) face on the guide plate (y = py0)
        b = LP.scs8uu()
        b.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 180)  # holes face from -y to +y (towards the plate)
        b.translate(Vector(0, ry, z0 + (k + 0.5) * L_))
        blocks.append(b)
    out["ADD_SCS8UU_x2"] = Part.makeCompound(blocks)
    out["ADD_GUIDE_PLATE_printed"] = box(-15.0, 15.0, py0, py1, z0, z0 + 2 * L_)     # between the bloc ears (x +-15..18), bolted to them
    # rod bottom: catalogue SK8, base towards -y, bolted to a printed L bracket standing on the stepper support top
    sk = LP.sk8()
    sk.translate(Vector(0, ry, rz0 + LP.SK8["L"] / 2))
    out["ADD_SK8_rod_foot"] = sk
    yb = ry - LP.SK8["h"]                                # SK8 base face
    br = box(-21.0, 21.0, yb - 6.0, yb, rz0 - 4.0, rz0 + LP.SK8["L"])            # plate behind the SK8 base
    br = br.fuse(box(-21.0, 21.0, yb - 6.0, -36.0, rz0 - 4.0, rz0))               # foot on the support top (z 43)
    out["ADD_SK8_BRACKET_printed"] = br.removeSplitter()
    t = GUIDE["top_t"]
    top = box(-13.0, 13.0, ry - 10.0, 13.0, screw_top - t, screw_top)
    top = top.cut(cyl(4.0, (0, ry, screw_top - t - 1), (0, ry, screw_top + 1)))
    top = top.cut(cyl(4.0, (0, 0, screw_top - t - 1), (0, 0, screw_top + 1)))      # screw through the 608 bore
    out["ADD_TOP_PLATE_608_printed"] = top
    return out


def vol(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def moved(s, pl):
    t = s.copy()
    t.Placement = pl.multiply(t.Placement)
    return t


def main():
    shapes, notes = build()
    sb = shapes["SW_SCREW_T8_L300_lead8"].BoundBox
    screw_top = sb.ZMax
    screw_bot = shapes["SW_SCREW_T8_L300_lead8"].BoundBox.ZMin
    proxy = cyl(4.0, (0, 0, screw_bot), (0, 0, screw_top))                   # threaded screw -> plain Ø8 for checks
    rep = ["GRAIL2 - Baha's 'essai mecanisme vis ecrou 1.0' (SOLIDWORKS, 2026-11-19) rebuilt in FreeCAD",
           "Frame: x = flip axis direction, y = magnet side (0 on the screw axis), z up, z 0 = NEMA17 bottom.", ""]
    rep += ["Sources: " + n for n in notes]

    # ---- coupling bores vs screw
    bores = sorted({round(f.Surface.Radius * 2, 2) for f in shapes["REAL_COUPLING_CXJH_D25_d5_e5"].Faces
                    if isinstance(f.Surface, Part.Cylinder) and f.Surface.Radius < 5})
    rep.append("Coupling CXJH-C-D25 bores: %s mm; screw Ø8.0, NEMA17 shaft Ø5.0" % bores)

    # ---- static clashes at the model pose
    J = {"name": "grail2", "fcstd": os.path.basename(OUT_FC),
         "lift": {"objects": LIFT_OBJS + FLIP_OBJS, "label": "Lift (mm from the model pose)"},
         "flip": {"objects": FLIP_OBJS, "axis_point": [AXIS.x, AXIS.y, AXIS.z], "axis_dir": [1, 0, 0],
                  "label": "Flip about the servo axis (deg, 0 = magnet pointing +y, + = up)"},
         "screw": {"objects": SCREW_OBJS, "lead": C.LEAD},
         "fixed": FIXED_OBJS, "expected": [sorted(p) for p in EXPECTED], "ignore": sorted(IGNORE),
         "colors": {k: list(v) for k, v in COLORS.items()}, "h_max": C.H_MAX}
    chk = {k: v for k, v in shapes.items() if k not in IGNORE}
    chk["SCREW_PROXY"] = proxy
    names = sorted(chk)
    rep += ["", "Clashes at the model pose (common volume > 0.5 mm3; 'by design' = parts fastened / shaft in bore):"]
    n_cl = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = vol(chk[names[i]], chk[names[j]])
            if v > 0.5 or v < 0:
                tag = "by design" if frozenset((names[i], names[j])) in EXPECTED else "CLASH"
                rep.append("  %-30s x %-30s %9.1f mm3  %s" % (names[i], names[j], v, tag))
                n_cl += tag == "CLASH"
    if not n_cl:
        rep.append("  no unexpected clash")

    # ---- lift travel
    nut = shapes["REF_NUT_T8"].BoundBox
    coup_top = shapes["REAL_COUPLING_CXJH_D25_d5_e5"].BoundBox.ZMax
    lo_geo = coup_top - nut.ZMin                     # nut bottom on the coupling
    hi_geo = screw_top - nut.ZMax                    # nut still fully on the thread
    carriage = [n for n in LIFT_OBJS + FLIP_OBJS if n not in IGNORE]
    fixed = {n: chk[n] for n in FIXED_OBJS + ["SCREW_PROXY", "REAL_COUPLING_CXJH_D25_d5_e5"]}
    lo, hi = lo_geo, hi_geo
    for step_dir, start, end in ((-1, 0.0, lo_geo - 20), (1, 0.0, hi_geo + 20)):
        d = start
        while (d >= end) if step_dir < 0 else (d <= end):
            hit = None
            for a in carriage:
                sa = moved(chk[a], C.lift_pl(d))
                for b, sbb in fixed.items():
                    if frozenset((a, b)) in EXPECTED:
                        continue
                    if vol(sa, sbb) > 0.5:
                        hit = (a, b)
                        break
                if hit:
                    break
            if hit:
                if step_dir < 0:
                    lo = max(lo, d + 1.0)
                else:
                    hi = min(hi, d - 1.0)
                rep.append("lift %s: first solid contact at %+.0f mm: %s x %s" % ("down" if step_dir < 0 else "up", d, hit[0], hit[1]))
                break
            d += step_dir * 1.0
    top0 = max(chk[n].BoundBox.ZMax for n in carriage)
    h350 = C.H_MAX - top0
    rep += ["", "LIFT (screw lead %.0f mm/turn)" % C.LEAD,
            "  nut on the screw: %+.1f (nut on the coupling) .. %+.1f (nut at the screw top) mm from the model pose"
            % (lo_geo, hi_geo),
            "  usable travel: %+.1f .. %+.1f  = %.1f mm = %.1f screw turns" % (lo, hi, hi - lo, (hi - lo) / C.LEAD),
            "  carriage top at the model pose z %.1f (flip 0); fixed screw top z %.1f; mechanism height (motor bottom -> "
            "screw top) %.1f mm vs %.0f" % (top0, screw_top, screw_top, C.H_MAX),
            "  carriage top reaches %.0f mm at lift %+.1f (if the motor bottom were on the table)" % (C.H_MAX, h350),
            "  GUIDE (added): Ø8 rod at y %.0f, z %.0f..%.1f (cut %.0f mm), 2 SCS8UU on a printed plate, top plate + 608 "
            "on the screw top" % (GUIDE["rod_y"], GUIDE["rod_z"][0], GUIDE["rod_z"][1], GUIDE["rod_z"][1] - GUIDE["rod_z"][0])]

    # ---- flip sweep (relative to the carriage: same at every lift)
    flip_vs = {n: chk[n] for n in carriage if n not in FLIP_OBJS}
    flip_vs["SCREW_PROXY"] = proxy
    flip_vs["ADD_GUIDE_ROD_D8"] = chk["ADD_GUIDE_ROD_D8"]
    blocked = {}
    ang_list = [a * 2.0 for a in range(-90, 91)]                                 # -180 .. +180 step 2
    for a in ang_list:
        pl = C.flip_pl(J, 0.0, a)
        hits = []
        for f in FLIP_OBJS:
            sf = moved(chk[f], pl)
            for b, sbb in flip_vs.items():
                if frozenset((f, b)) in EXPECTED:
                    continue
                v = vol(sf, sbb)
                if v > 0.5:
                    hits.append("%s x %s (%.0f mm3)" % (f, b, v))
        if hits:
            blocked[a] = hits
    free_hi = next((a for a in ang_list if a > 0 and a in blocked), None)
    free_lo = next((a for a in reversed(ang_list) if a < 0 and a in blocked), None)
    fhi = (free_hi - 2.0) if free_hi is not None else 180.0
    flo = (free_lo + 2.0) if free_lo is not None else -180.0
    rep += ["", "FLIP about the servo axis (0 = magnet pointing out along +y, +90 = magnet up, -90 = magnet down)"]
    if 0.0 in blocked:
        rep.append("  BLOCKED already at 0: " + "; ".join(blocked[0.0]))
    rep.append("  free arc around 0 (2 deg steps): %+.0f .. %+.0f deg  (span %.0f deg)" % (flo, fhi, fhi - flo))
    if free_hi is not None:
        rep.append("  stop going up at %+.0f: %s" % (free_hi, "; ".join(blocked[free_hi])))
    if free_lo is not None:
        rep.append("  stop going down at %+.0f: %s" % (free_lo, "; ".join(blocked[free_lo])))
    for tgt in (180.0, -180.0):
        if tgt in blocked:
            rep.append("  at %+.0f (the '180' pose): %s" % (tgt, "; ".join(blocked[tgt])))
    # height of the flip group over the arc, at lift 0
    tops = [(a, max(moved(chk[f], C.flip_pl(J, 0.0, a)).BoundBox.ZMax for f in FLIP_OBJS)) for a in ang_list if flo <= a <= fhi]
    amax = max(tops, key=lambda q: q[1])
    rep.append("  highest flip-group point over the free arc: z %.1f at %+.0f deg (lift 0)" % (amax[1], amax[0]))
    mag = moved(chk["REAL_MAGNET_5KG"], C.flip_pl(J, 0.0, 0.0)).BoundBox
    rep.append("  magnet at flip 0: face at y %.1f (%.1f beyond the screw axis), centre z %.1f; Ø25"
               % (mag.YMax, mag.YMax, (mag.ZMin + mag.ZMax) / 2))

    # ---- sequence for the slider panel
    top_lift = min(hi, h350 - max(0.0, amax[1] - top0))
    J["lift"].update({"min": round(lo, 1), "max": round(hi, 1), "base": 0.0})
    J["flip"].update({"min": -180.0, "max": 180.0, "free": [flo, fhi], "base": 0.0})
    J["flip_blocked"] = {"%.0f" % a: h for a, h in blocked.items()}
    J["sequence"] = [
        [0, 0.0, 0.0, "model pose (as saved in SOLIDWORKS)"],
        [2.5, round(lo, 1), 0.0, "lift down to the bottom stop"],
        [4.0, round(top_lift, 1), 0.0, "lift up to the highest pose under 350 (motor on the table)"],
        [2.0, round(top_lift, 1), fhi, "flip up to the stop"],
        [3.0, round(top_lift, 1), flo, "flip down to the stop"],
        [1.0, round(top_lift, 1), 0.0, "flip back to 0"],
        [3.0, 0.0, 0.0, "back to the model pose"],
    ]
    rep += ["", "Masses (SOLIDWORKS, as modelled): see sw_export/sw_dump.json",
            "Objects: SW_* exact, REAL_*/REF_* bought parts, APPROX_* rebuilt (shape assumed), SCREW_PROXY = Ø8 for checks."]

    # ---- write
    doc = App.newDocument("GRAIL2")
    for name, s in shapes.items():
        o = doc.addObject("Part::Feature", name)
        o.Shape = s
    doc.recompute()
    os.makedirs(os.path.join(C.CAD, "STEP"), exist_ok=True)
    doc.saveAs(OUT_FC)
    Import.export([o for o in doc.Objects], os.path.join(C.CAD, "STEP", "GRAIL2.step"))
    C.save_joints(J)
    with open(os.path.join(C.CAD, "grail2_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep))


main()
