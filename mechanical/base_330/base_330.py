# base_330.py - parametric, symmetric robot base plate (330 mm wide) for FreeCAD.
#
# Run headless:  freecadcmd base_330.py      (or as a macro in the FreeCAD GUI)
# Writes next to this file: base_330.FCStd (PartDesign Body: Sketch + Pad), base_330.step, base_330.dxf
#
# Frame: X = wheel axis (width, 330), Y = front/back (length, 280), Z = up. Origin = plate centre, bottom face.
# Every feature is defined for x >= 0 (and y >= 0 where it applies) and mirrored, so the plate is symmetric
# about the YZ and XZ planes.
#
# Derived from: base - Copy.SLDPRT, hinge.SLDPRT, MCC.SLDPRT (Pololu 37D, no encoder), accouplement_hbaieb.SLDPRT,
# roue-90mm avec axe40mm - Copy.SLDPRT, sysRoueCodeusee.SLDPRT, caster_ball.SLDPRT and their placement in
# Robot_assembly - Copy.SLDASM.

import os

# ---------------------------------------------------------------- parameters (mm)
W = 330.0          # width along the wheel axis (was 290)
L = 280.0          # length front/back (unchanged)
T = 5.0            # plate thickness (unchanged)

# Drive chain along X (from the assembly): motors back to back, motor face against the hinge plate.
MOTOR_FACE_X = 61.5        # inner face of the hinge's motor plate
WHEEL_BOSS_X = 78.0        # wheel hub boss face, pressed against the coupler collar
WHEEL_BOSS = 5.8           # hub boss length of roue-90mm avec axe40mm
WHEEL_W = 20.0             # tyre width
WHEEL_CLEAR = 5.0          # gap tyre <-> pocket walls, each side (was 3)

# Wheel pocket (through the plate) and encoder channel/notch
POCKET_Y = 50.0            # pocket half-length (unchanged)
CHANNEL_Y = 22.5           # encoder housing channel half-width (unchanged)
FILLET_R = 10.0            # rounding of the pocket/channel corner (unchanged)
NOTCH_Y = 30.5             # encoder wheel notch half-width (tyre Ø61 chord at the top face 27.8 + 2.7 mm)
NOTCH_CLEAR = 2.4          # gap encoder wheel <-> inner notch wall

# Encoder system (sysRoueCodeusee): two vertical Ø8 rods, 70 mm apart along Y, pressed into the plate
ROD_X = 134.5              # puts the encoder housing 3 mm outside the tyre and the wheel inside x = 165
ROD_Y = 35.0
ROD_D = 7.85               # press fit for Ø8 rods (same as before)
ENC_WHEEL_IN = 25.4        # encoder wheel inner face = ROD_X + 25.4 (from the part)

# Hinge (motor bracket) holes: 4 x Ø3.5, pattern 24 (X) x 30 (Y), centred on the motor axis (y = 0)
HINGE_D = 3.5
HINGE_X = (26.9, 50.9)
HINGE_Y = 15.0

# Lift: spacer between the plate and each hinge. Casters reach 16.5 mm below the plate top; the shaft is 20.5 mm
# above the hinge seat; wheel radius 45 -> an 8 mm lift puts the casters exactly on the floor. Design principle:
# casters ~2 mm above the floor so the drive wheels always carry the weight -> 6 mm lift.
# Made of laser-cut MDF layers (only 3 and 5 mm available): 3 + 3 = 6 -> 2 layers per lift, same outline.
LIFT_H = 6.0
LIFT_LAYERS = (3.0, 3.0)   # bottom -> top
LIFT_X0, LIFT_X1 = 16.0, 68.0  # footprint (x >= 0 side; mirrored): hinge base x 18.9..64.7 + ~3 mm
LIFT_Y1 = 24.0                 # footprint y -24..24 (hinge base y -20..20), stays clear of the slots at |y| >= 25.5
LIFT_R = 3.0                   # corner radius
# The lift is held by the hinge bolts (through hinge + lift + plate) and strapped through the two slots below.

# Strap slots across the motors, used to fix the lift (were x -55.09..55.92 -> made symmetric)
SLOT_X = 55.5              # slot end centres at +/- SLOT_X
SLOT_Y = 27.5
SLOT_W = 4.0

# Corner holes for the aluminium profiles: 11 mm from each edge (same as before)
CORNER_D = 6.35
CORNER_INSET = 11.0

# Caster balls - unchanged from the original base
CASTER_Y = 110.0
CASTER_D = 33.0
CASTER_SCREW_X = 20.0
CASTER_SCREW_D = 4.0

# ---------------------------------------------------------------- derived
W2, L2 = W / 2, L / 2
TYRE_IN = WHEEL_BOSS_X + WHEEL_BOSS                  # 83.8
TYRE_OUT = TYRE_IN + WHEEL_W                         # 103.8
POCKET_X0 = round(TYRE_IN - WHEEL_CLEAR, 1)          # 80.8
POCKET_X1 = round(TYRE_OUT + WHEEL_CLEAR, 1)         # 106.8
NOTCH_X = round(ROD_X + ENC_WHEEL_IN - NOTCH_CLEAR, 1)


def geometry():
    """Return (outline, circles, slots). outline = list of ('line', p0, p1) / ('arc', centre, r, a0, a1) (CCW)."""
    P0, P1, R = POCKET_X0, POCKET_X1, FILLET_R
    CY, PY, NY, NX = CHANNEL_Y, POCKET_Y, NOTCH_Y, NOTCH_X
    assert P1 + R < NX < W2 and CY < NY < PY < L2

    # right half, counter-clockwise, from (0, -L2) to (0, L2)
    right = [
        ("line", (0, -L2), (W2, -L2)),
        ("line", (W2, -L2), (W2, -NY)),
        ("line", (W2, -NY), (NX, -NY)),
        ("line", (NX, -NY), (NX, -CY)),
        ("line", (NX, -CY), (P1 + R, -CY)),
        ("arc", (P1 + R, -CY - R), R, 90, 180),
        ("line", (P1, -CY - R), (P1, -PY)),
        ("line", (P1, -PY), (P0, -PY)),
        ("line", (P0, -PY), (P0, PY)),
        ("line", (P0, PY), (P1, PY)),
        ("line", (P1, PY), (P1, CY + R)),
        ("arc", (P1 + R, CY + R), R, 180, 270),
        ("line", (P1 + R, CY), (NX, CY)),
        ("line", (NX, CY), (NX, NY)),
        ("line", (NX, NY), (W2, NY)),
        ("line", (W2, NY), (W2, L2)),
        ("line", (W2, L2), (0, L2)),
    ]

    def mirror_x(seg):
        if seg[0] == "line":
            return ("line", (-seg[2][0], seg[2][1]), (-seg[1][0], seg[1][1]))
        _, c, r, a0, a1 = seg
        return ("arc", (-c[0], c[1]), r, (180 - a1) % 360, (180 - a0) % 360)

    left = [mirror_x(s) for s in reversed(right)]
    outline = right + left

    circles = []  # (x, y, d)

    def quad(x, y, d):  # 4 mirrored copies
        for sx in (1, -1):
            for sy in (1, -1):
                circles.append((sx * x, sy * y, d))

    for hx in HINGE_X:
        quad(hx, HINGE_Y, HINGE_D)
    quad(ROD_X, ROD_Y, ROD_D)
    quad(W2 - CORNER_INSET, L2 - CORNER_INSET, CORNER_D)
    quad(CASTER_SCREW_X, CASTER_Y, CASTER_SCREW_D)
    for sy in (1, -1):
        circles.append((0.0, sy * CASTER_Y, CASTER_D))

    slots = [(SLOT_X, sy * SLOT_Y, SLOT_W) for sy in (1, -1)]  # (half length to end centres, y, width)
    return outline, circles, slots


def lift_geometry():
    """Lift layer (x >= 0 side, centred on the motor axis): rounded rectangle + the 4 hinge holes."""
    x0, x1, y1, r = LIFT_X0, LIFT_X1, LIFT_Y1, LIFT_R
    outline = [
        ("line", (x0 + r, -y1), (x1 - r, -y1)),
        ("arc", (x1 - r, -y1 + r), r, 270, 360),
        ("line", (x1, -y1 + r), (x1, y1 - r)),
        ("arc", (x1 - r, y1 - r), r, 0, 90),
        ("line", (x1 - r, y1), (x0 + r, y1)),
        ("arc", (x0 + r, y1 - r), r, 90, 180),
        ("line", (x0, y1 - r), (x0, -y1 + r)),
        ("arc", (x0 + r, -y1 + r), r, 180, 270),
    ]
    circles = [(hx, sy * HINGE_Y, HINGE_D) for hx in HINGE_X for sy in (1, -1)]
    return outline, circles, []


def slot_segments(hx, y, w):
    r = w / 2
    return [
        ("line", (-hx, y - r), (hx, y - r)),
        ("arc", (hx, y), r, 270, 90),
        ("line", (hx, y + r), (-hx, y + r)),
        ("arc", (-hx, y), r, 90, 270),
    ]


# ---------------------------------------------------------------- FreeCAD model
def build(doc, name, geom, thickness, z0=0.0):
    import FreeCAD as App
    import Part
    import Sketcher  # noqa: F401

    V = App.Vector
    outline, circles, slots = geom
    body = doc.addObject("PartDesign::Body", name)
    body.Placement.Base = V(0, 0, z0)
    sk = body.newObject("Sketcher::SketchObject", name + "_Sketch")
    sk.AttachmentSupport = [(body.Origin.OriginFeatures[3], "")]  # XY plane
    sk.MapMode = "FlatFace"

    def add(seg):
        if seg[0] == "line":
            sk.addGeometry(Part.LineSegment(V(*seg[1], 0), V(*seg[2], 0)))
        else:
            _, c, r, a0, a1 = seg
            import math
            a1 = a1 if a1 > a0 else a1 + 360
            sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(*c, 0), V(0, 0, 1), r), math.radians(a0), math.radians(a1)))

    for s in outline:
        add(s)
    for x, y, d in circles:
        sk.addGeometry(Part.Circle(V(x, y, 0), V(0, 0, 1), d / 2))
    for hx, y, w in slots:
        for s in slot_segments(hx, y, w):
            add(s)

    pad = body.newObject("PartDesign::Pad", name + "_Pad")
    pad.Profile = sk
    pad.Length = thickness
    sk.Visibility = False
    doc.recompute()
    assert body.Shape.isValid() and len(body.Shape.Solids) == 1, name + " solid is not valid"
    return body


# ---------------------------------------------------------------- DXF (R12, mm) for laser cutting
def write_dxf(path, geom):
    outline, circles, slots = geom
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC",
           "0", "SECTION", "2", "ENTITIES"]

    def seg(s):
        if s[0] == "line":
            out.extend(["0", "LINE", "8", "0", "10", "%.4f" % s[1][0], "20", "%.4f" % s[1][1], "30", "0",
                        "11", "%.4f" % s[2][0], "21", "%.4f" % s[2][1], "31", "0"])
        else:
            _, c, r, a0, a1 = s
            out.extend(["0", "ARC", "8", "0", "10", "%.4f" % c[0], "20", "%.4f" % c[1], "30", "0",
                        "40", "%.4f" % r, "50", "%.4f" % (a0 % 360), "51", "%.4f" % (a1 % 360)])

    for s in outline:
        seg(s)
    for x, y, d in circles:
        out.extend(["0", "CIRCLE", "8", "0", "10", "%.4f" % x, "20", "%.4f" % y, "30", "0", "40", "%.4f" % (d / 2)])
    for hx, y, w in slots:
        for s in slot_segments(hx, y, w):
            seg(s)
    out.extend(["0", "ENDSEC", "0", "EOF"])
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


def main():
    import FreeCAD as App
    import Part  # noqa: F401
    here = os.path.dirname(os.path.abspath(__file__))
    for n in ("base_330", "lift"):
        if n in App.listDocuments():
            App.closeDocument(n)

    # base plate
    doc = App.newDocument("base_330")
    shape = build(doc, "Base330", geometry(), T).Shape
    doc.saveAs(os.path.join(here, "base_330.FCStd"))
    shape.exportStep(os.path.join(here, "base_330.step"))
    write_dxf(os.path.join(here, "base_330.dxf"), geometry())
    bb = shape.BoundBox
    print("base_330: %.1f x %.1f x %.1f mm, volume %.0f mm3, %d faces" % (
        bb.XLength, bb.YLength, bb.ZLength, shape.Volume, len(shape.Faces)))
    print("pocket x %.1f..%.1f, encoder notch from x %.1f, rods at x %.1f" % (
        POCKET_X0, POCKET_X1, NOTCH_X, ROD_X))

    # lift: one layer outline, stacked 5 + 3 mm on top of the plate (shown for the x > 0 motor, in plate coords)
    assert abs(sum(LIFT_LAYERS) - LIFT_H) < 1e-6
    doc = App.newDocument("lift")
    z, solids = T, []
    for i, th in enumerate(LIFT_LAYERS):
        solids.append(build(doc, "Lift_%dmm_%d" % (th, i + 1), lift_geometry(), th, z).Shape)
        z += th
    doc.saveAs(os.path.join(here, "lift.FCStd"))
    Part.makeCompound(solids).exportStep(os.path.join(here, "lift.step"))
    write_dxf(os.path.join(here, "lift_layer.dxf"), lift_geometry())
    print("lift: %.0f x %.0f mm, layers %s mm = %.1f mm" % (
        LIFT_X1 - LIFT_X0, 2 * LIFT_Y1, " + ".join("%g" % t for t in LIFT_LAYERS), LIFT_H))


if __name__ in ("__main__", "base_330"):
    main()
