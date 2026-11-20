# flipper_pinion_fc.py - Flipper lift pinion v2 (m1, 20 T) for the printed rack (parts/cremaillere.STL, m1, 10.6 wide).
# Redo of Baha's "el pignon" (parts/el_pignon.STEP):
#   * real involute teeth (20 deg), face width FACE_W (was 5 mm),
#   * long hub kept (the motor must sit past the carriage wheel) but Ø16 instead of Ø10.5: stiff enough (report),
#   * hub thick enough for Seif's M3 insert (K 5.0, the one el pignon was drawn for: hole Ø4.5, cone Ø5.2 = D-025)
#     radial, the M3 set screw bearing on the shaft's D flat (was a 2.7 mm wall: the insert would reach the bore),
#   * D bore (NEMA17 shaft Ø5, flat at 4.5), one solid (was 2).
# Frame: axis = z, z = 0 at the motor-side face (hub), gear on top. Print: gear face down (z top on the bed) or as is.
#   Run (from mechanical/Grail_v2): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_pinion_fc.py
#   -> CAD_FC/FLIPPER_PINION.FCStd, print/FLIPPER_PINION.step + .stl, CAD_FC/FLIPPER_PINION_report.txt
import math
import os

import FreeCAD as App
import Mesh
import MeshPart
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
CAD = os.path.join(ROOT, "CAD_FC")
PRINT = os.path.join(ROOT, "print")


class G:
    M, Z, PA = 1.0, 20, 20.0              # module, teeth, pressure angle
    BACKLASH = 0.15                       # total, taken off the tooth thickness (printed gear on a printed rack)
    FACE_W = 10.0                         # tooth width (rack is 10.6)
    HUB_D = 16.0                          # hub Ø (root Ø is 17.5): 5 mm of wall for the insert (el pignon: 2.7)
    HUB_L = 31.5                          # long hub: the motor face sits 5 mm past the carriage's eccentric wheel
                                          # (fc/flipper_fc.py: wheel edge 32 mm from the profile centre; el pignon: 29)
    INS_Z = 8.0                           # insert axis from the motor-side face (inside the shaft's 21 mm)
    BORE_D, FLAT = 5.15, 4.6              # NEMA17 shaft Ø5, D flat at 4.5 (+0.1)
    INS_K, INS_L = 5.0, 4.0               # Seif's M3 insert (knurl Ø, length) -> D-025: hole K*0.9, cone K+0.2 over L/4
    BOSS_GAP = 0.5                        # hub face starts this far from the motor face (clears the motor boss)


def involute_tooth_pts(n=12):
    m, z = G.M, G.Z
    rp = m * z / 2
    rb = rp * math.cos(math.radians(G.PA))
    ra = rp + m
    rf = rp - 1.25 * m
    # half tooth angle at the pitch circle, minus backlash
    s_p = math.pi * m / 2 - G.BACKLASH / 2
    inv = lambda a: math.tan(a) - a
    a_p = math.radians(G.PA)
    half_p = s_p / (2 * rp)                         # half thickness angle at pitch
    pts = []
    r_start = max(rb, rf)
    for i in range(n + 1):
        r = r_start + (ra - r_start) * i / n
        a = math.acos(min(1.0, rb / r))
        th = half_p + inv(a_p) - inv(a)             # half-angle of the tooth at radius r
        pts.append((r, th))
    return rf, ra, pts


def gear_profile():
    rf, ra, half = involute_tooth_pts()
    poly = []
    step = 2 * math.pi / G.Z
    for k in range(G.Z):
        c = k * step
        # root arc start (from previous gap middle) to the tooth's right flank
        right = [(r, c - th) for r, th in half]
        left = [(r, c + th) for r, th in reversed(half)]
        g0 = c - step / 2
        poly.append((rf, g0))
        poly.append((rf, right[0][1]))
        poly += right + left
        poly.append((rf, left[-1][1]))
    pts = [Vector(r * math.cos(a), r * math.sin(a), 0) for r, a in poly]
    # remove consecutive duplicates
    clean = [pts[0]]
    for p in pts[1:]:
        if (p - clean[-1]).Length > 1e-4:
            clean.append(p)
    if (clean[0] - clean[-1]).Length < 1e-4:
        clean.pop()
    return Part.Face(Part.makePolygon(clean + [clean[0]])), rf, ra


def d_bore(z0, h):
    c = Part.makeCylinder(G.BORE_D / 2, h, Vector(0, 0, z0))
    cut = Part.makeBox(10, 10, h + 2, Vector(G.FLAT - G.BORE_D / 2, -5, z0 - 1))     # flat at x = FLAT - r
    return c.cut(cut)


def insert_hole(x_surface):
    """Radial M3 insert hole along +x from the hub surface down to the bore (D-025: K*0.9, cone K+0.2 over L/4)."""
    zc = G.BOSS_GAP + G.INS_Z
    d_h = G.INS_K * 0.9
    hole = Part.makeCylinder(d_h / 2, 20, Vector(0, 0, zc), Vector(1, 0, 0))
    cl = G.INS_L * 0.25
    cone = Part.makeCone(d_h / 2, (G.INS_K + 0.2) / 2, cl, Vector(x_surface - cl, 0, zc), Vector(1, 0, 0))
    cone = cone.fuse(Part.makeCylinder((G.INS_K + 0.2) / 2, 3, Vector(x_surface, 0, zc), Vector(1, 0, 0)))
    return hole.fuse(cone)


def build():
    face, rf, ra = gear_profile()
    z_g0 = G.BOSS_GAP + G.HUB_L
    gear = face.extrude(Vector(0, 0, G.FACE_W))
    gear.translate(Vector(0, 0, z_g0))
    hub = Part.makeCylinder(G.HUB_D / 2, G.HUB_L, Vector(0, 0, G.BOSS_GAP))
    body = hub.fuse(gear).removeSplitter()
    L = z_g0 + G.FACE_W - G.BOSS_GAP
    body = body.cut(d_bore(G.BOSS_GAP - 1, L + 2))
    body = body.cut(insert_hole(G.HUB_D / 2))
    body.translate(Vector(0, 0, -G.BOSS_GAP))       # part frame: z 0 = hub face
    return body.removeSplitter(), rf, ra, L


def main():
    os.makedirs(CAD, exist_ok=True)
    os.makedirs(PRINT, exist_ok=True)
    body, rf, ra, L = build()
    doc = App.newDocument("FLIPPER_PINION")
    o = doc.addObject("Part::Feature", "FLIPPER_PINION_m1_20T")
    o.Shape = body
    doc.recompute()
    doc.saveAs(os.path.join(CAD, "FLIPPER_PINION.FCStd"))
    body.exportStep(os.path.join(PRINT, "FLIPPER_PINION.step"))
    mesh = MeshPart.meshFromShape(Shape=body, LinearDeflection=0.02, AngularDeflection=0.1)
    mesh.write(os.path.join(PRINT, "FLIPPER_PINION.stl"))
    wall = G.HUB_D / 2 - G.FLAT + G.BORE_D / 2   # from the flat to the hub surface, along the insert axis
    r = ["FLIPPER PINION v2 - fc/flipper_pinion_fc.py",
         "m%.1f, %d teeth, pressure angle %.0f deg, backlash %.2f: tip Ø%.2f, pitch Ø%.2f, root Ø%.2f"
         % (G.M, G.Z, G.PA, G.BACKLASH, 2 * ra, G.M * G.Z, 2 * rf),
         "teeth %.1f wide (rack 10.6); hub Ø%.1f x %.1f on the motor side; total length %.1f (NEMA17 shaft ~24 from the face)"
         % (G.FACE_W, G.HUB_D, G.HUB_L, L),
         "gear centre %.1f mm from the motor face (el pignon: ~31). Stiffness at 10 N on the teeth: steel shaft Ø5 "
         "bends ~0.02 mm; hub Ø16 ABS ~0.3 MPa (el pignon Ø10.5 hub, 2.7 mm wall at the insert)" % (G.BOSS_GAP + G.HUB_L + G.FACE_W / 2),
         "bore: D Ø%.2f, flat at %.2f from the axis side; M3 insert K %.1f L %.1f: hole Ø%.2f, cone Ø%.2f x %.1f; "
         "wall from the flat to the hub surface %.2f (insert L + 1 = %.1f)"
         % (G.BORE_D, G.FLAT, G.INS_K, G.INS_L, G.INS_K * 0.9, G.INS_K + 0.2, G.INS_L * 0.25, wall, G.INS_L + 1),
         "volume %.0f mm3, ~%.1f g ABS (100 %%)" % (body.Volume, body.Volume * 1.04e-3),
         "solids %d, valid %s" % (len(body.Solids), body.isValid())]
    open(os.path.join(CAD, "FLIPPER_PINION_report.txt"), "w", encoding="utf-8").write("\n".join(r) + "\n")
    print("\n".join(r))


main()
