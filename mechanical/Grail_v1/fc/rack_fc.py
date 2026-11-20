# rack_fc.py - Baha's Grail lift, rack-and-pinion version ("essai mecanisme cremaillere last version", SolidWorks,
# 2026-11-19), assembled in FreeCAD from the per-part STLs exported out of the SolidWorks assembly.
#   Run (from mechanical/Grail_v1):  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/rack_fc.py
#   -> CAD_FC/GRAIL_V1_RACK.FCStd, CAD_FC/rack_report.txt  (no STEP: the parts are faceted meshes, a STEP was 100 MB)
#
# Source: "Essai cremaillere/*.STL" - SolidWorks wrote each part in the ASSEMBLY's coordinates, so the parts are
#   already in place. The assembly could not be saved as STEP (newer SolidWorks than ours).
# Frame (same as ../grail-lift): x = outward, the side where the servo + magnet are (the Grail starts on +x),
#   y = along the robot face, z = up, z = 0 = table. The SolidWorks assembly is Y-up and the profile leans 1.0 deg:
#   everything is turned so the profile stands vertical, then x = SW X, y = -SW Z, z = SW Y.
#   ASSUMPTION: profile bottom PROFILE_Z0 above the table (the assembly does not say how the lift is mounted).
# Meshes -> solids: each STL is split into its bodies, cleaned and closed into a solid where possible (faceted solids,
#   good enough for boxes and placement; not for fine fits). No clash check here (Seif, 2026-11-19: not until the
#   mechanism is fixed).
import glob
import os

import FreeCAD as App
import Mesh
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))              # mechanical/Grail_v1
SRC = os.path.join(ROOT, "Essai cremaillere")
CAD = os.path.join(ROOT, "CAD_FC")
OUT_FC = os.path.join(CAD, "GRAIL_V1_RACK.FCStd")
OUT_REP = os.path.join(CAD, "rack_report.txt")
PREFIX = "essai mecanisme cremaillere last version ss - "

PROFILE_Z0 = 5.0       # profile bottom above the table (assumption, as grail-lift v1)
H_MAX = 350.0          # [GR F.3]
ROOF_MIN = 300.0       # L4 [G E.2]

# short name, file key (start of the STL name after PREFIX), group, colour (r, g, b)
PARTS = [
    ("PROFILE_316", "F_profilet_316", "fixed", (0.75, 0.75, 0.78)),
    ("RACK_310", "essai mecanisme last version-2025", "fixed", (0.95, 0.55, 0.10)),
    ("CARRIAGE_PLATE", "chariot imprimante 3d.SLDPRT-1 Chapa", "moving", (0.55, 0.55, 0.60)),
    ("VWHEELS", "chariot imprimante 3d.SLDPRT-1 Roldana", "moving", (0.15, 0.15, 0.15)),
    ("WHEEL_SCREWS_M5", "chariot imprimante 3d.SLDPRT-1 Parafuso", "moving", (0.35, 0.35, 0.35)),
    ("WHEEL_NUTS_M5", "chariot imprimante 3d.SLDPRT-1 Porca", "moving", (0.35, 0.35, 0.35)),
    ("SUPPORT_FIXATION", "support fixation es7i7", "moving", (0.30, 0.50, 0.85)),
    ("NEMA17", "Nema17", "moving", (0.20, 0.20, 0.22)),
    ("PINION", "el pignon 2025", "moving", (0.95, 0.80, 0.10)),
    ("SERVO_MG996R", "Tower Pro MG 996R", "moving", (0.10, 0.25, 0.70)),
    ("HORN", "[3879] Servo Motor Horn", "moving", (0.95, 0.95, 0.95)),
    ("SUPPORT_U", "support en u", "arm", (0.20, 0.70, 0.35)),
    ("MAGNET_5KG", "Magnet 5KG", "arm", (0.80, 0.10, 0.10)),
]


def find_stl(key):
    for f in glob.glob(os.path.join(SRC, "*.STL")):
        if os.path.basename(f)[len(PREFIX):].startswith(key):
            return f
    raise FileNotFoundError(key)


def frame_from_profile():
    """Placement that stands the profile up (its long axis -> z) and puts its bottom centre at (0, 0, PROFILE_Z0)."""
    m = Mesh.Mesh(find_stl("F_profilet_316"))
    pts = [p for p in m.Points]
    n = len(pts)
    c = Vector(sum(p.x for p in pts) / n, sum(p.y for p in pts) / n, sum(p.z for p in pts) / n)
    # long axis from the two end faces: mean of points in the bottom / top 2 mm
    ys = [p.y for p in pts]
    lo, hi = min(ys), max(ys)
    bot = [p for p in pts if p.y < lo + 2]
    top = [p for p in pts if p.y > hi - 2]
    b = Vector(sum(p.x for p in bot) / len(bot), sum(p.y for p in bot) / len(bot), sum(p.z for p in bot) / len(bot))
    t = Vector(sum(p.x for p in top) / len(top), sum(p.y for p in top) / len(top), sum(p.z for p in top) / len(top))
    ax = (t - b).normalize()
    # SW -> FC axes: x = SW X, y = -SW Z, z = SW Y
    swap = App.Matrix(1, 0, 0, 0,
                      0, 0, -1, 0,
                      0, 1, 0, 0,
                      0, 0, 0, 1)
    ax_fc = swap.multVec(ax)
    untilt = App.Rotation(ax_fc, Vector(0, 0, 1))          # profile axis -> +z
    M = untilt.toMatrix().multiply(swap)
    b_fc = M.multVec(b)
    M2 = App.Matrix()
    M2.move(Vector(-b_fc.x, -b_fc.y, PROFILE_Z0 - b_fc.z))
    M = M2.multiply(M)
    tilt = ax.getAngle(Vector(0, 1, 0)) * 180 / 3.141592653589793
    return M, tilt, c


def mesh_to_solids(mesh):
    """Split into bodies, clean, close into solids. Returns (solids, failed shells)."""
    solids, failed = [], []
    for comp in mesh.getSeparateComponents():
        if comp.CountFacets < 4:                 # stray triangles (the repair calls crash on them)
            continue
        for fix in ("removeDuplicatedPoints", "removeDuplicatedFacets", "fixIndices", "removeNonManifolds",
                    "harmonizeNormals"):
            try:
                getattr(comp, fix)()
            except Exception:
                pass
        sh = Part.Shape()
        sh.makeShapeFromMesh(comp.Topology, 0.05)
        try:
            s = Part.Solid(Part.Shell(sh.Faces))
            if s.Volume < 0:
                s.reverse()
            if comp.CountFacets < 4000:
                s = s.removeSplitter()
            if s.isValid() and s.Volume > 0.5:
                solids.append(s)
                continue
        except Exception:
            pass
        failed.append(sh)
    return solids, failed


def build():
    M, tilt, _ = frame_from_profile()
    doc = App.newDocument("GRAIL_V1_RACK")
    parts, info = {}, {}
    for name, key, group, col in PARTS:
        m = Mesh.Mesh(find_stl(key))
        m.transform(M)
        print("part", name, m.CountFacets, flush=True)
        sols, bad = mesh_to_solids(m)
        shape = Part.makeCompound(sols + bad)
        f = doc.addObject("Part::Feature", name)
        f.Shape = shape
        f.addProperty("App::PropertyString", "Group_", "Grail").Group_ = group
        f.addProperty("App::PropertyString", "SourceSTL", "Grail").SourceSTL = os.path.basename(find_stl(key))
        if App.GuiUp:
            f.ViewObject.ShapeColor = col
        parts[name] = shape
        info[name] = (group, len(sols), len(bad), m.CountFacets)
    doc.recompute()
    doc.saveAs(OUT_FC)
    print("saved", OUT_FC, flush=True)
    return doc, parts, info, tilt


def bb_txt(b):
    return "x %7.1f..%7.1f  y %7.1f..%7.1f  z %7.1f..%7.1f  (%.1f x %.1f x %.1f)" % (
        b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, b.XLength, b.YLength, b.ZLength)


def union_bb(shapes):
    out = None
    for s in shapes:
        out = s.BoundBox if out is None else out.united(s.BoundBox)
    return out


def main():
    doc, P, info, tilt = build()
    r = []
    r.append("GRAIL V1 - RACK VERSION (Baha, 2026-11-19), assembled from the SolidWorks STLs by fc/rack_fc.py")
    r.append("Frame: x = outward (servo/magnet side), y = along the face, z = up. Profile stood up (it leaned %.2f deg in "
             "the SW assembly); profile bottom ASSUMED at z = %.1f." % (tilt, PROFILE_Z0))
    r.append("")
    r.append("PARTS (group | bodies closed into solids / left as open shells | facets)")
    for n, s in P.items():
        g, ns, nb, nf = info[n]
        r.append("  %-17s %-6s %2d / %d  %6d  %s" % (n, g, ns, nb, nf, bb_txt(s.BoundBox)))
    fixed = [n for n in P if info[n][0] == "fixed"]
    moving = [n for n in P if info[n][0] != "fixed"]
    mb = union_bb([P[n] for n in moving])
    fb = union_bb([P[n] for n in fixed])
    allb = union_bb(P.values())
    r.append("")
    r.append("OVERALL            " + bb_txt(allb))
    r.append("FIXED (profile+rack) " + bb_txt(fb))
    r.append("MOVING (carriage..magnet) " + bb_txt(mb))
    r.append("  moving block height %.1f mm; highest point of the whole model %.1f (limit %.0f)" % (mb.ZLength, allb.ZMax, H_MAX))

    # ---- lift travel along the rack / profile
    pin, rack, prof, wh = P["PINION"].BoundBox, P["RACK_310"].BoundBox, P["PROFILE_316"].BoundBox, P["VWHEELS"].BoundBox
    pin_c = pin.Center.z
    up_rack = (rack.ZMax - 11.0) - pin_c          # pinion tip radius ~11 (20T m1): gear centre stays >= 11 from the end
    dn_rack = (rack.ZMin + 11.0) - pin_c
    up_prof = prof.ZMax - wh.ZMax                  # wheels stay on the profile
    dn_prof = prof.ZMin - wh.ZMin
    dn_table = 0.0 - mb.ZMin
    up = min(up_rack, up_prof)
    dn = max(dn_rack, dn_prof, dn_table)
    r.append("")
    r.append("LIFT TRAVEL from the model pose (+ = up)")
    r.append("  pinion on the rack: %+.1f .. %+.1f   wheels on the profile: %+.1f .. %+.1f   moving block above the table: >= %+.1f"
             % (dn_rack, up_rack, dn_prof, up_prof, dn_table))
    r.append("  -> usable travel %+.1f .. %+.1f = %.1f mm; moving block top then %.1f .. %.1f, bottom %.1f .. %.1f"
             % (dn, up, up - dn, mb.ZMax + dn, mb.ZMax + up, mb.ZMin + dn, mb.ZMin + up))

    # ---- servo axis (horn: thin direction = axis)
    hb = P["HORN"].BoundBox
    dims = {"x": hb.XLength, "y": hb.YLength, "z": hb.ZLength}
    axis = min(dims, key=dims.get)
    r.append("")
    r.append("SERVO AXIS along %s, through x %.1f z %.1f (horn centre)  ->  %.1f mm out from the profile centre, %.1f above "
             "the profile bottom at the model pose" % (axis, hb.Center.x, hb.Center.z, hb.Center.x, hb.Center.z - PROFILE_Z0))
    r.append("  servo axis height over the travel: %.1f .. %.1f" % (hb.Center.z + dn, hb.Center.z + up))
    mg = P["MAGNET_5KG"].BoundBox
    r.append("  magnet centre x %.1f y %.1f z %.1f -> %.1f mm from the servo axis (in x-z)"
             % (mg.Center.x, mg.Center.y, mg.Center.z, ((mg.Center.x - hb.Center.x) ** 2 + (mg.Center.z - hb.Center.z) ** 2) ** 0.5))

    with open(OUT_REP, "w", encoding="utf-8") as fh:
        fh.write("\n".join(r) + "\n")
    print("\n".join(r))


main()
