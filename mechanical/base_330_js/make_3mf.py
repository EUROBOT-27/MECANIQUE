# make_3mf.py - every printed part of base_330_js on one 256 x 256 plate (Bambu X1C, ABS - D-023) -> CAD/base_330_js_print.3mf
# Run after base_330_js.py:  freecadcmd -c "__file__=r'<path>/make_3mf.py'; exec(open(__file__).read())"
# The AMT102-V encoder (CDR "Poenc1_102-v-2530") is bought: only its support (bracket + arm) and the odometry wheel are printed.
#
# Print orientation (chosen so the precise holes are round and nothing needs support):
#   odo_bracket   on its back wall (-Y face down): bridge, ears and flanges stand up, no overhang
#   odo_arm       on the inner side plate (-X face down): 625 seats + F623 bores vertical (round, accurate)
#   odo_wheel     flat (axis vertical)
#   caster_spacer flat

import os
import zipfile

import FreeCAD as App
import MeshPart
import Part

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
CAD = os.path.join(HERE, "CAD")
V = App.Vector
BED = 256.0
GAP = 8.0

PARTS = [  # name, copies, rotation (axis, deg)
    ("odo_bracket", 2, (V(1, 0, 0), 90)),
    ("odo_arm", 2, (V(0, 1, 0), -90)),
    ("odo_wheel", 2, (V(0, 1, 0), -90)),
    ("caster_spacer", 2, None),
]


def oriented(name, rot):
    s = Part.read(os.path.join(CAD, name + ".step"))
    if rot:
        s.rotate(V(0, 0, 0), rot[0], rot[1])
    bb = s.BoundBox
    s.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    return s


def mesh_xml(shape):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False)
    pts, tris = m.Topology
    v = "".join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (p.x, p.y, p.z) for p in pts)
    t = "".join('<triangle v1="%d" v2="%d" v3="%d"/>' % tr for tr in tris)
    return "<mesh><vertices>%s</vertices><triangles>%s</triangles></mesh>" % (v, t), len(tris)


def main():
    objs, items, report = [], [], []
    total = 0.0
    x = y = row_h = 0.0
    oid = 0
    for name, n, rot in PARTS:
        s = oriented(name, rot)
        bb = s.BoundBox
        mx, ntri = mesh_xml(s)
        for i in range(n):
            if x + bb.XLength > BED - GAP:
                x, y, row_h = 0.0, y + row_h + GAP, 0.0
            oid += 1
            objs.append('<object id="%d" name="%s_%d" type="model">%s</object>' % (oid, name, i + 1, mx))
            items.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.3f %.3f 0" printable="1"/>' % (
                oid, x + GAP, y + GAP))
            report.append("%-14s #%d  %5.1f x %5.1f x %5.1f mm at (%.0f, %.0f), %.1f cm3, %d triangles" % (
                name, i + 1, bb.XLength, bb.YLength, bb.ZLength, x + GAP, y + GAP, s.Volume / 1000, ntri))
            total += s.Volume / 1000
            x += bb.XLength + GAP
            row_h = max(row_h, bb.YLength)
    assert y + row_h + GAP <= BED, "parts do not fit on one plate"
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             '<metadata name="Title">base_330_js printed parts (ABS)</metadata>'
             '<metadata name="Designer">IEEE RAS INSAT - Eurobot 2027</metadata>'
             '<resources>%s</resources><build>%s</build></model>') % ("".join(objs), "".join(items))
    ctypes = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    out = os.path.join(CAD, "base_330_js_print.3mf")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
    print("\n".join(report))
    print("plate used: %.0f x %.0f mm of %.0f x %.0f; total %.1f cm3 -> %s" % (
        BED, y + row_h + GAP, BED, BED, total, out))


main()
