# tolerance_tests_v7.py - small test coupons for the clapets v7 module A fits, printed in PLA before the real parts.
# Each coupon repeats one feature of the real parts (same size, same print orientation) in 3 variants:
# smaller / CAD value / bigger. Variant marks: 1, 2 or 3 small grooves on the top face next to each feature
# (1 = smaller, 2 = the CAD value, 3 = bigger).
# Run (from mechanical/clapets-v7, after fc/v7_fc.py):
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/tolerance_tests_v7.py
# Output: tolerance-tests/stl/T*.stl  (+ tolerance-tests/volumes.txt). Print every coupon as it lies (z up).
# Picture: "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/tolerance_image_v7.py -> tolerance-tests/coupons.png
import math
import os

import FreeCAD as App
import MeshPart
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "tolerance-tests", "stl")
os.makedirs(OUT, exist_ok=True)
FCSTD = os.path.join(ROOT, "CAD_FC", "MODULE_CLAPETS_V7.FCStd")


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def zcyl(x, y, z0, z1, r):
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0), Vector(0, 0, 1))


def xcyl(x0, x1, y, z, r):
    return Part.makeCylinder(r, x1 - x0, Vector(x0, y, z), Vector(1, 0, 0))


def ycyl(x, y0, y1, z, r):
    return Part.makeCylinder(r, y1 - y0, Vector(x, y0, z), Vector(0, 1, 0))


def hexprism(x, y, z0, z1, af, corner_deg=90):     # hex with flats AF, a corner at corner_deg
    rc = af / math.sqrt(3)
    pts = [Vector(x + rc * math.cos(math.radians(corner_deg + 60 * k)), y + rc * math.sin(math.radians(corner_deg + 60 * k)), z0) for k in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, 0, z1 - z0))


def marks(x, y, z_top, k):                          # k grooves 0.8 wide, 0.6 deep, 6 long, on the top face
    return [box(x + i * 1.8, x + i * 1.8 + 0.8, y, y + 6, z_top - 0.6, z_top + 1) for i in range(k)]


def solid(adds, cuts):
    s = adds[0]
    for a in adds[1:]:
        s = s.fuse(a)
    for c in cuts:
        s = s.cut(c)
    return s.removeSplitter()


def save(name, shape, log):
    path = os.path.join(OUT, name + ".stl")
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.08, Relative=False)
    mesh.write(path)
    log.append("%-28s %6.1f cm3  %5.1f g PLA (solid)" % (name, shape.Volume / 1000, shape.Volume / 1000 * 1.24))


def lead_in_up(x, y, z, r, h=0.6):                  # 45 deg chamfer at a hole mouth opening upward
    return Part.makeCone(r, r + h, h + 0.01, Vector(x, y, z - h), Vector(0, 0, 1))


def main():
    log = []
    # ---- T1: 608 bearing seat (bottom of the door unit, top in the cap), axis vertical. CAD: Ø22.2 x 7.2 + 0.6 lead-in
    a, c = [box(0, 84, 0, 30, 0, 10)], []
    for i, d in enumerate((22.0, 22.2, 22.4)):
        x = 14 + 28 * i
        c += [zcyl(x, 15, 10 - 7.2, 10.1, d / 2), lead_in_up(x, 15, 10, d / 2), zcyl(x, 15, -1, 11, 5.0)]
        c += marks(x - 2, 1, 10, i + 1)
    save("T1_608_seat_22.0_22.2_22.4", solid(a, c), log)

    # ---- T2: rod clamp on the Ø8 rod (arms, 28T), bore vertical, M3 x 12 along x, nut pocket from the +x face.
    #      CAD: bore Ø8.2, pocket 6.0 x 6.9 x 2.8, head hole Ø6.6. Variants on the bore: 8.1 / 8.2 / 8.3
    parts = []
    for i, d in enumerate((8.1, 8.2, 8.3)):
        ox = 32 * i
        a = [zcyl(ox, 0, 0, 10, 11), box(ox - 6, ox + 6, 4, 14, 0, 10)]
        c = [zcyl(ox, 0, -1, 11, d / 2), box(ox - 0.6, ox + 0.6, 0, 15, -1, 11),
             xcyl(ox - 7, ox + 7, 9, 5, 1.7), box(ox + 6 - 1.4 - 1.3, ox + 6.1 + 4, 9 - 3.0, 9 + 3.0, 5 - 3.45, 5 + 3.45),
             xcyl(ox - 20, ox - 4, 9, 5, 3.3)]
        c += marks(ox - 3, -9, 10, i + 1)
        parts.append(solid(a, c))
    save("T2_rod_clamp_8.1_8.2_8.3", Part.makeCompound(parts), log)

    # ---- T3: servo ear post: M3 nut in a hex recess under a 1.6 roof, window below open to the side (printed upright).
    #      CAD: hex AF 5.7 (flats toward the servo), depth 2.5, window 10 tall. Variants on AF: 5.6 / 5.7 / 5.8
    a, c = [box(0, 48, 0, 14, 0, 3)], []
    for i, af in enumerate((5.6, 5.7, 5.8)):
        x = 8 + 16 * i
        a.append(box(x - 4.3, x + 4.3, 1, 13, 0, 26))
        zr, zw1 = 26 - 1.6, 26 - 1.6 - 2.5
        c += [hexprism(x, 7, zw1 - 0.01, zr, af), box(x - af / 2, x + 5, 7 - 3.3, 7 + 3.3, zw1 - 10, zw1 + 0.01),
              zcyl(x, 7, zw1 - 1, 26.1, 1.7)]
        c += marks(x - 2.5, 0, 3, i + 1)
    save("T3_servo_post_hex_5.6_5.7_5.8", solid(a, c), log)

    # ---- T4: M4 nut pocket in an upright face (keel / cap front face), axis horizontal, with the ±1.5 slide.
    #      CAD: pocket 11.4 (incl. slide) x 7.4 x 3.6 deep, slot Ø4.5 ±1.5. Variants on the 7.4: 7.2 / 7.4 / 7.6
    a, c = [box(0, 66, 0, 20, 0, 3)], []
    for i, h in enumerate((7.2, 7.4, 7.6)):
        x = 11 + 22 * i
        a.append(box(x - 9, x + 9, 5, 15, 0, 24))                      # wall 10 thick (y), like the keel
        z = 14
        for d in (-1.5, 1.5):
            c.append(ycyl(x + d, 4, 16, z, 2.25))
        c += [box(x - 1.5, x + 1.5, 4, 16, z - 2.25, z + 2.25), box(x - 5.7, x + 5.7, 15 - 3.6, 15.1, z - h / 2, z + h / 2)]
        c += marks(x - 2.5, 16, 3, i + 1)
    save("T4_M4_pocket_7.2_7.4_7.6", solid(a, c), log)

    # ---- T5: M3 nut pocket under a shelf (cap screws under the top shelf), opening downward, printed upright.
    #      CAD: 6.0 x 6.9 x 2.8, hole Ø3.4. Variants on the 6.0: 5.8 / 6.0 / 6.2
    a, c = [box(0, 60, 0, 16, 0, 3), box(0, 4, 0, 16, 0, 20), box(56, 60, 0, 16, 0, 20), box(0, 60, 0, 16, 12, 20)], []
    for i, w in enumerate((5.8, 6.0, 6.2)):
        x = 14 + 16 * i
        c += [box(x - 3.45, x + 3.45, 8 - w / 2, 8 + w / 2, 11.9, 12 + 2.8), zcyl(x, 8, 11, 21, 1.7)]
        c += marks(x - 2.5, 9, 20, i + 1)
    save("T5_shelf_nut_pocket_5.8_6.0_6.2", solid(a, c), log)

    # ---- T6: M3 heat-set insert holes (socle, 4 inserts), vertical. CAD: Ø4.6 x 7, 0.5 x 45 deg lead-in.
    #      Variants Ø4.4 / 4.6 / 4.8 (2026-11-10: the M4 inserts are gone, nuts instead)
    a, c = [box(0, 48, 0, 16, 0, 12)], []
    for i, d in enumerate((4.4, 4.6, 4.8)):
        x = 8 + 16 * i
        c += [zcyl(x, 8, 12 - 7, 12.1, d / 2), Part.makeCone(d / 2 + 0.5, d / 2, 0.51, Vector(x, 8, 11.99), Vector(0, 0, -1)),
              zcyl(x, 8, 0, 6, 1.7)]
        c += marks(x - 2.5, 1, 12, i + 1)
    save("T6_insert_holes_M3_4.4_4.6_4.8", solid(a, c), log)

    # ---- T7: 2020 profile passage (socle rail blocks, motor plate). CAD: 20.4 square. Variants 20.2 / 20.4 / 20.6
    a, c = [box(0, 96, 0, 32, 0, 6)], []
    for i, w in enumerate((20.2, 20.4, 20.6)):
        x = 16 + 32 * i
        c += [box(x - w / 2, x + w / 2, 16 - w / 2, 16 + w / 2, -1, 7)]
        c += marks(x - 13.5, 28, 6, i + 1)
    save("T7_2020_passage_20.2_20.4_20.6", solid(a, c), log)

    # ---- T8: the real door unit's bottom pod (servo cradle, 3 posts + nut windows, cable exit, bottom 608), cut from
    #      A_AILE_D. Tests: servo slides in, ears + screws + nuts, cable, bearing, and the 20T / 28T mesh on a rod.
    doc = App.openDocument(FCSTD)
    aile = [o for o in doc.Objects if o.Label.startswith("A_AILE_D")][0].Shape
    pod = aile.common(box(88, 151, 30, 100, 26, 96)).removeSplitter()
    save("T8_servo_cradle_from_A_AILE_D", pod, log)
    # ---- T9 / T10: the real door gears (20T pinion on the servo horn, 28T on the rod with its clamp), as they print
    #      (flat, z up): horn pocket + M2 holes, rod bore + split clamp + nut pockets; used with T8 for the mesh check
    for tag, label in (("T9_pinion_20T", "A_PIGNON_PORTE_20T"), ("T10_gear_28T", "A_ROUE_PORTE_28T")):
        sh = [o for o in doc.Objects if o.Label.startswith(label) and o.Shape.BoundBox.XMin > 0][0].Shape.copy()
        bb = sh.BoundBox
        sh.translate(Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
        save(tag, sh, log)
    App.closeDocument(doc.Name)

    with open(os.path.join(ROOT, "tolerance-tests", "volumes.txt"), "w") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


main()
