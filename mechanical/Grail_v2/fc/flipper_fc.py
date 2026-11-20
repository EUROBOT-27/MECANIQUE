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
    LZ = float(os.environ.get("FLIPPER_LZ", "80"))   # pivot above the Grail top at the pick (= under the roof top at the
                                              # place). 80 (was 58): the travel shrinks so the column top stays under the
                                              # magnet cup, which hangs 26 mm under the roof top right above the column
    PX = (C.X_PICK + C.X_PLACE) / 2
    Z_PICK = C.G_H + LZ
    Z_PLACE = C.ROOF_TOP - LZ
    OVER, REL = 6.0, 6.0
    # ---- column: real 2020, profile centre (XC, YC); plate faces +x (towards the right face)
    # ---- column fixation variant (Seif 2026-11-20: see them in CAD before deciding), env FLIPPER_FIX:
    #   slot   : column x 110 over the wheel; 2020 L-brackets in the back slot's free ends (rack cut to the pinion's
    #            travel) to two 2020 cross-members running inward along x: bottom one above the drive motor, top one
    #            under the roof
    #   bridge : column x 110 standing on a plate that arches over the wheel (legs to the floor beside it) + top as slot
    #   inward : column x 85, over the drive motor, on a saddle above it (column starts lower) + top as slot
    #   saddle : (base_330_js, Seif 2026-11-20) printed saddle over the drive wheel AND motor, standing on the 4 free
    #            plate zones beside the wheel well and the motor; column on its deck, heel + 2 M5 T-nuts
    FIX = os.environ.get("FLIPPER_FIX", "saddle" if C.BASE == "b330" else "bridge")
    XC, YC = C.FACE - {"inward": 65.0}.get(FIX, 40.0), 4.0
    PROF_Z0 = {"bridge": 86.0, "inward": 60.0, "saddle": 88.0}.get(FIX, 78.0)   # slot: bay floor; bridge/saddle: on the deck
    PROF_Z1 = None                            # computed in build(): wheels at the top of the travel + 1
    # ---- carriage: plate centre height at the pick; pivot H_P above it
    H_P = None                                # computed: Z_PICK - ZC_PICK
    ZC_PICK = {"bridge": 125.0, "saddle": 127.0}.get(FIX, 116.0)   # lowest plate centre. bridge/saddle: PROF_Z0 + 39 = wheels 2 mm above the
                                                   # column's end, steel plate (37.5 under its centre) 4.5 above the deck
    # ---- rack: only its V nose enters the back-face slot, teeth towards -x. Real profile slot (measured, section at
    # mid-length): 8.9 wide at the face, 45 deg down to a 6.4 lip at 1.4 deep, cavity behind. Rack V back: 5.7 (nose)
    # -> 10.59 over 2.62 (~43 deg). The flanks meet with the nose 1.7 mm below the face (Seif: "not really inside").
    RACK_SEAT = None                          # computed: rack slid in from the profile's end (Seif), V back resting on
                                              # the slot cavity's inner faces (the pinion pushes it inward)
    # ---- motor (standard NEMA17 40 mm for now) + pinion
    MOTOR_FACE_GAP = 5.0                      # motor face this far past the eccentric wheel (in -y): bracket 4.5 + 0.5 clear
    PIN_DZ = {"bridge": 4.0, "saddle": 4.0}.get(FIX, 10.0)   # pinion centre above the plate centre (lower: its top clears
                                              # the top cross-member)
    PIN_BOSS_GAP = 0.5                        # flipper_pinion_fc: hub face 0.5 from the motor face
    PIN_GEAR_OFF = None                       # computed from print/FLIPPER_PINION.step (BOSS_GAP + length - FACE_W/2)
    BRACKET_T = 4.5                           # motor bracket plate (between the motor face and the eccentric wheel)
    BASE_T = 8.0                              # SERVO_MOUNT base on the X plate's front face


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
    G.PROF_Z1 = round(zc + (G.Z_PLACE + G.OVER - G.Z_PICK) + 37.0 + 1.0, 1)
    M = printer_to_robot(zc)
    # ---------------- fixed column: real 2020 cut to length, rack
    Mp = printer_to_robot(zc)
    prof = load("profile_2020_X_350.step", Mp)
    cut = C.box(G.XC - 15, G.XC + 15, G.YC - 15, G.YC + 15, G.PROF_Z0, G.PROF_Z1)
    fixed["PROFILE_2020"] = prof.common(cut)
    # rack (local: x = length 0..310, y = 0 (V nose) .. 5 (tooth tips), z = width 0..10.59). Seat = push it into the
    # back-face slot until its V back touches the slot faces (2D sections of the real profile and the rack).
    rack_l = mesh_solid(os.path.join(PARTS, "cremaillere.STL"))
    zmid = (G.PROF_Z0 + G.PROF_Z1) / 2
    psec = Part.makeFace(fixed["PROFILE_2020"].slice(Vector(0, 0, 1), zmid), "Part::FaceMakerBullseye")
    rsec_w = rack_l.slice(Vector(1, 0, 0), 155.0)
    rpts = [(v.Point.y, v.Point.z) for v in max(rsec_w, key=lambda w: w.BoundBox.DiagonalLength).OrderedVertexes]

    def rack_face(seat):
        pts = [Vector(G.XC - 10 + seat - y, G.YC - 10.59 / 2 + z, zmid) for y, z in rpts]
        return Part.Face(Part.makePolygon(pts + [pts[0]]))

    def overlap(seat):
        try:
            return psec.common(rack_face(seat)).Area
        except Exception:
            return 0.0
    scan = [k * 0.05 for k in range(0, 200)]
    ok = [overlap(v) <= 0.005 for v in scan]
    deepest = max(i for i, f in enumerate(ok) if f and i > 0 and scan[i] > 2.7)   # inside the cavity (past the lips)
    lo, hi = scan[deepest], scan[min(deepest + 1, len(scan) - 1)]
    for _ in range(25):
        mid_ = (lo + hi) / 2
        if overlap(mid_) > 0.005:
            hi = mid_
        else:
            lo = mid_
    shallow = deepest
    while shallow > 0 and ok[shallow - 1]:
        shallow -= 1
    G.RACK_PLAY = lo - scan[shallow]          # how far it can move between the lips and the inner faces
    G.RACK_SEAT = lo
    rm = App.Matrix(0, -1, 0, G.XC - 10 + G.RACK_SEAT,
                    0, 0, 1, G.YC - 10.59 / 2,
                    1, 0, 0, G.PROF_Z0,
                    0, 0, 0, 1)
    rack = rack_l.copy()
    rack.transformShape(rm)
    top_ = G.Z_PLACE + G.OVER - G.Z_PICK
    G.RACK_Z = (zc + G.PIN_DZ - 12.0, zc + G.PIN_DZ + top_ + 12.0)     # pinion travel +- tip radius + 1
    rack = rack.common(C.box(G.XC - 30, G.XC, G.YC - 10, G.YC + 10, G.RACK_Z[0], G.RACK_Z[1]))
    fixed["RACK_m1_printed"] = rack
    rack_print = rack_l.common(C.box(G.RACK_Z[0] - G.PROF_Z0, G.RACK_Z[1] - G.PROF_Z0, -1, 6, -1, 12))   # print file
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
    pin = Part.read(os.path.join(PRINT, "FLIPPER_PINION.step"))
    pin_len = pin.BoundBox.ZLength
    G.PIN_GEAR_OFF = G.PIN_BOSS_GAP + pin_len - 2.5                 # gear 5 wide at the far end
    gear_y = face_y + G.PIN_GEAR_OFF
    nm_s, d, fcen = nema_frame()
    rot = App.Rotation(d, Vector(0, 1, 0))
    pl = App.Placement(Vector(pin_x, face_y, pin_z) - rot.multVec(fcen), rot)
    motor = nm_s.copy()
    motor.Placement = pl.multiply(motor.Placement)
    lift["NEMA17"] = motor
    pin = pin.copy()
    # pinion local z (motor-side face at 0) -> +y; place hub face at face_y + boss gap
    pin.Placement = App.Placement(Vector(pin_x, face_y + G.PIN_BOSS_GAP, pin_z), App.Rotation(Vector(1, 0, 0), -90))
    lift["PINION_v2"] = pin
    ins = C.insert(5.0, 4.0, (8.0, 0, 8.0), (-1, 0, 0))                     # M3 insert K5 L4, radial, 8 from the hub face
    sscr = C._orient(Part.makeCylinder(1.45, 6.0), (2.05, 0, 8.0), (1, 0, 0))   # M3 x 6 set screw on the shaft flat
    for sh_ in (ins, sscr):
        sh_.Placement = pin.Placement.multiply(sh_.Placement)
    lift["INSERT_M3_PINION"] = ins
    lift["SCR_M3x6_SET_PINION"] = sscr
    # ---------------- MOTOR_BRACKET (printed), drawn explicitly so no wall is under 2.5 mm (Seif: thin bits unprintable):
    #   plate (4.5 thick) between the motor face and the eccentric wheel (0.5 off it), z zc-34..zc+34 so it backs both
    #   bridges fully; NEMA17 4 x M3 + Ø23 pilot; flanges (3 x 6.5) on its top and bottom edges, away from the wheel;
    #   two bridges to the X plate's bottom tabs, one M3 each (drill Ø2.5 + tap M3 in the tab). Form fit: the upper bridge
    #   butts on the plate's small bent tab, the lower one wraps the tab's end with a 2.7 step (0.3 clearance).
    xback = G.XC + 12.1                                  # X plate main sheet, back face
    by0, by1 = face_y, face_y + G.BRACKET_T
    tab_y = G.YC + 219.9 - P_Z                           # bottom tabs: y tab_y .. tab_y + 2.7
    xp = lift["X_PLATE"]
    def _bb_in(x0, x1, y0, y1, z0, z1):
        c_ = xp.common(C.box(x0, x1, y0, y1, z0, z1))
        return c_.BoundBox if c_.Volume > 0.01 else None
    low_tab = _bb_in(G.XC - 20, xback, tab_y - 0.1, tab_y + 2.8, zc - 36, zc - 12)
    small_tab = _bb_in(G.XC - 12, G.XC, tab_y - 12.0, tab_y - 0.5, zc + 12, zc + 36)
    up_x0 = (small_tab.XMax if small_tab else G.XC - 3.5) + 0.3
    low_x0 = low_tab.XMin if low_tab else G.XC - 4.6
    info_wheel_x0 = C.bb(wheels[0]).XMin
    x_end = xback - 0.6
    mb = C.box(pin_x - 21.15, x_end, by0, by1, zc - 34.0, zc + 34.0)
    mb = mb.fuse(C.box(up_x0, x_end, by1 - 0.5, tab_y - 0.05, zc + 23.0, zc + 34.0))            # upper bridge
    mb = mb.fuse(C.box(low_x0, x_end, by1 - 0.5, tab_y - 0.05, zc - 34.0, zc - 16.0))           # lower bridge
    mb = mb.fuse(C.box(low_x0 - 3.0, low_x0 - 0.3, by1 - 0.5, tab_y + 3.0, zc - 34.0, zc - 16.0))  # step round the tab's end
    for fz0, fz1 in ((zc + 31.0, zc + 34.0), (zc - 34.0, zc - 31.0)):                            # edge flanges (+y side)
        mb = mb.fuse(C.box(pin_x - 21.15, low_x0 - 3.0, by1 - 0.5, by1 + 6.0, fz0, fz1))
    mb = mb.removeSplitter()
    mb = mb.cut(C.cyl(11.5, 20, (pin_x, by0 - 1, pin_z), (0, 1, 0)))                         # pilot Ø23
    for dx in (-15.5, 15.5):
        for dz in (-15.5, 15.5):
            mb = mb.cut(C.cyl(C.FIT["m3"] / 2, 20, (pin_x + dx, by0 - 1, pin_z + dz), (0, 1, 0)))  # motor M3
            hx, hz = pin_x + dx, pin_z + dz
            if hx + 2.75 > info_wheel_x0 - 1 and abs(hz - zc) < 14:                               # head next to the wheel:
                mb = mb.cut(C.cyl(2.9, 1.9, (hx, by1 - 1.8, hz), (0, 1, 0)))                     # button head, counterbored
    tab_screws = []
    for zz, x0_ in ((zc + 28.5, up_x0), (zc - 25.0, low_x0)):   # one M3 per bridge, centred (counterbore walls >= 3)
        xx = 0.5 * (x0_ + x_end)
        mb = mb.cut(C.cyl(C.FIT["m3"] / 2, 40, (xx, by0 - 1, zz), (0, 1, 0)))
        mb = mb.cut(C.cyl(3.35, 3.5, (xx, by0 - 0.1, zz), (0, 1, 0)))                           # head counterbore
        tab_screws.append((xx, zz))
    mb, ch_done, ch_tried = C.chamfer_outer(mb.removeSplitter())
    lift["MOTOR_BRACKET"] = mb
    G.CHAMFERS = {"MOTOR_BRACKET": (ch_done, ch_tried)}
    scr = []
    for dx in (-15.5, 15.5):
        for dz in (-15.5, 15.5):
            hx, hz = pin_x + dx, pin_z + dz
            cb_ = hx + 2.75 > info_wheel_x0 - 1 and abs(hz - zc) < 14
            scr.append(C.screw(3, 8, (hx, by1 - (1.8 if cb_ else 0.0), hz), (0, -1, 0), button=True))
    lift["SCR_M3x8_NEMA_x4"] = Part.makeCompound(scr)
    lift["SCR_M3x20_TABS_x2"] = Part.makeCompound([C.screw(3, 20, (xx, by0 + 3.4, zz), (0, 1, 0)) for xx, zz in tab_screws])
    # ---------------- flip head (arm + servo + cheek) + its base on the X plate's front face = one printed SERVO_MOUNT
    arm, head, hinfo = C.flip_head(G.PX, G.Z_PICK)
    xf = plate_bb.XMax                                     # X plate front face
    xb1 = xf + G.BASE_T
    # X plate holes (printer frame, sliced) -> robot: y = printer z - P_Z + YC, z = printer x - P_XC + zc
    m5 = [(G.YC + 255.68 - P_Z, zc + px_ - P_XC) for px_ in (95.62, 145.62)]       # upper wheel screws -> M5x35
    m3 = [(G.YC + 255.18 - P_Z, zc + px_ - P_XC) for px_ in (110.62, 130.62)]      # tapped M3 (Ø2.5) in the plate
    ecc = (G.YC + 214.63 - P_Z, zc + 120.62 - P_XC)                                # eccentric wheel's nyloc
    sp_y0, sp_y1 = hinfo["plate_y"]
    sp_x0 = hinfo["plate_x"][0]
    base = C.box(xf, xb1, min(sp_y0, G.YC - 34.0), G.YC + 30.0, zc - 33.0, zc + 33.0)
    web = C.box(xb1 - 1, sp_x0 + 1, sp_y0, sp_y1, max(zc - 33.0, hinfo["plate_z"][0]), min(zc + 33.0, hinfo["plate_z"][1]))
    base = base.fuse(web)
    for (y, z) in m5:
        base = base.cut(C.cyl(C.FIT["m5"] / 2, 40, (xf - 1, y, z), (1, 0, 0)))
    for (y, z) in m3:
        base = base.cut(C.cyl(C.FIT["m3"] / 2, 40, (xf - 1, y, z), (1, 0, 0))).cut(C.cyl(3.35, 4, (xb1 - 3.5, y, z), (1, 0, 0)))
    base = base.cut(C.cyl(5.5, 6.5, (xf - 0.1, ecc[0], ecc[1]), (1, 0, 0)))
    for zz in (zc + 24.0, zc + 31.0):                    # zip-tie anchor: servo + magnet cables up the base's front face
        base = base.cut(C.box(xf - 1, xb1 + 1, G.YC + 2.0, G.YC + 6.0, zz - 1.0, zz + 1.0))
    plate_edge_y = G.YC + 200.9 - P_Z                    # X plate's -y edge
    base = base.fuse(C.box(xf, xb1, plate_edge_y - 2.4, min(sp_y0, G.YC - 34.0) + 1.0, zc - 30.0, zc + 30.0))       # lip root
    base = base.fuse(C.box(xf - 2.9, xf + 0.5, plate_edge_y - 2.4, plate_edge_y - 0.2, zc - 30.0, zc + 30.0))     # lip on the edge (form fit)
    for gz in (hinfo["plate_z"][0] + 0.0, None):          # gussets base / servo-plate web (top and bottom)
        pass
    wz0 = max(zc - 33.0, hinfo["plate_z"][0])
    wz1 = min(zc + 33.0, hinfo["plate_z"][1])
    for gz0 in (wz0, wz1 - 3.0):
        tri = Part.Face(Part.makePolygon([Vector(xb1 - 0.5, sp_y1 - 0.5, 0), Vector(xb1 + 7.0, sp_y1 - 0.5, 0),
                                          Vector(xb1 - 0.5, sp_y1 + 7.5, 0), Vector(xb1 - 0.5, sp_y1 - 0.5, 0)])).extrude(Vector(0, 0, 3.0))
        tri.translate(Vector(0, 0, gz0))
        base = base.fuse(tri)
    head["SERVO_MOUNT"] = head["SERVO_MOUNT"].fuse(base).removeSplitter()
    sm, ch_done, ch_tried = C.chamfer_outer(head["SERVO_MOUNT"])
    head["SERVO_MOUNT"] = sm
    G.CHAMFERS["SERVO_MOUNT"] = (ch_done, ch_tried)
    head["SCR_M3x12_PLATE_x2"] = Part.makeCompound([C.screw(3, 12, (xb1 - 3.5, y, z), (-1, 0, 0)) for (y, z) in m3])
    # the 2 upper wheel nylocs move onto the base's front (screws M5x25 -> M5x35)
    nuts = sorted(lift["M5_NYLOC"].Solids, key=lambda s: s.BoundBox.Center.y)
    moved_nuts = []
    for k, n_ in enumerate(nuts):
        n2 = n_.copy()
        if k > 0:
            n2.translate(Vector(G.BASE_T, 0, 0))
        moved_nuts.append(n2)
    lift["M5_NYLOC"] = Part.makeCompound(moved_nuts)
    scs = sorted(lift["M5x25_SCREWS"].Solids, key=lambda s_: s_.BoundBox.Center.y)
    new = [scs[0]]
    for s_ in scs[1:]:
        b_ = s_.BoundBox
        new.append(C.screw(5, 35, (b_.XMin + 5.0, b_.Center.y, b_.Center.z), (1, 0, 0)))
    lift["M5x25_SCREWS"] = Part.makeCompound(new)          # eccentric wheel: M5x25 kept; upper wheels: M5x35
    lift.update(head)
    arm_all.update(arm)
    hinfo.update(base_x=(xf, xb1), m5=m5, m3=m3, ecc=ecc)
    fixp = fixation(zc)
    isf = lambda n_: n_.startswith(("SCR_", "NUT_", "TNUT_", "INSERT_", "M5x25_SCREWS", "M5_NYLOC"))
    for n, s in fixp.items():
        C.add(doc, n, s, "8a_SCREWS_column" if isf(n) else "1b_FIXATION_" + G.FIX, groups)
    for n, s in arm_all.items():
        C.add(doc, n, s, "8c_SCREWS_arm" if isf(n) else "3_ARM_pick_pose", groups)
    for n, s in lift.items():
        C.add(doc, n, s, "8b_SCREWS_carriage" if isf(n) else "2_CARRIAGE_pick_pose", groups)
    for n, s in fixed.items():
        C.add(doc, n, s, "1_COLUMN_fixed", groups)
    g, plate = C.grail()
    C.add(doc, "GRAIL", g, "4_GRAIL_pick", groups)
    C.add(doc, "GRAIL_PLATE", plate, "4_GRAIL_pick", groups)
    info = dict(plate_bb=plate_bb, wheel_bb=wheel_bb, ecc_ymin=ecc_wheel_ymin, pitch_x=pitch_x, pin=(pin_x, gear_y, pin_z),
                face_y=face_y, motor_bb=C.bb(motor), pin_bb=C.bb(pin), wheels=wheels, head=hinfo,
                rack_print=rack_print, pin_len=pin_len, tab_screws=tab_screws, bracket_y=(by0, by1), fix=fixp)
    return arm_all, lift, fixed, (g, plate), info


def l_bracket(x_face, z0, up, inward_len=20.0, t=3.0, h_z=None):
    """2020 corner bracket (20 wide, 3 thick) on the column's back face (x_face) at z0..z0+20 (up=True) or z0-20..z0,
    its other leg running inward (-x) along the cross-member's face."""
    y0, y1 = G.YC - 10, G.YC + 10
    zz0, zz1 = (z0, z0 + 20) if up else (z0 - 20, z0)
    v = C.box(x_face - t, x_face, y0, y1, zz0, zz1)
    hz = z0 if h_z is None else h_z                      # level of the horizontal leg's contact face
    h = C.box(x_face - inward_len, x_face, y0, y1, (hz - t + t) if (up and h_z is not None) else ((hz - t) if up else hz),
              (hz + t) if (up and h_z is not None) else (hz if up else hz + t))
    return v.fuse(h).removeSplitter()


class S:
    """BRIDGE socle (printed ABS): a block over the right wheel with a tunnel around it. Robot frame."""
    X0, X1 = 80.0, 148.0                  # x: inner block above the drive motor .. 2 mm in from the right face
    Y0, Y1 = -52.0, 38.0                  # y: back = bay limit (back module's butterfly plate at -53); front: the door
                                          # unit starts at y 40 (z >= 53)
    Z0 = 26.0                             # floor plate top
    DECK_T = 3.0                          # deck over the tunnel (underside 80): top 83; a pad up to PROF_Z0 under the
                                          # column only (the carriage's steel plate passes 4.5 above the deck)
    WHEEL_CLR = 6.0                       # all round the wheel (R37 -> tunnel R43); wheel top 74 -> deck underside 80
    TUN_X0 = 101.0                        # tunnel from 5 mm inside the wheel's inner face (106) to past the face
    DRIVE = (104.0, 22.0, 60.0)           # cut-out for the drive motor + coupling: x < 104, |y| < 22, z < 60 (4.5 over it)
    FLOOR_SCREWS = ((90.0, -47.5), (118.0, -47.5), (144.0, -47.5), (88.0, 30.0), (86.0, 0.0))   # M4, top to floor
    BRACKET_NUT_X = 90.0                  # 2020 corner bracket screw (M5) on the deck behind the column
    # ribs on the deck (the tunnel is under it): heights from what the carriage brings down at the pick (steel plate
    # bottom 87.5, eccentric wheel 88, tabs 90, motor bracket 91, servo mount 92 / 97, servo 101, NEMA 108)
    RIBS = (((100.0, 104.0), (-43.0, 38.0), 4.0),        # along y beside the column: back wall - pad - front
            ((100.0, 148.0), (-43.0, -37.0), 12.0),      # along the back wall's top (behind the carriage)
            ((104.0, 148.0), (34.0, 38.0), 4.0),         # front edge
            ((136.0, 148.0), (30.0, 38.0), 12.0))        # front corner, past the servo mount (3 mm)


def bridge_socle():
    zt = G.PROF_Z0
    r = C.WHEEL["r"] + S.WHEEL_CLR
    zd = C.WHEEL["z"] + r + S.DECK_T                     # deck top (83)
    body = C.box(S.X0, S.X1, S.Y0, S.Y1, S.Z0, zd)
    body = body.fuse(C.box(G.XC - 10, G.XC + 10, G.YC - 10, G.YC + 10, zd - 1, zt))                    # pad under the column
    for (x0, x1), (y0, y1), h in S.RIBS:
        body = body.fuse(C.box(x0, x1, y0, y1, zd - 1, zd + h))
    body = body.cut(C.cyl(r, S.X1 + 5 - S.TUN_X0, (S.TUN_X0, 0.0, C.WHEEL["z"]), (1, 0, 0)))          # wheel tunnel
    body = body.cut(C.box(S.X0 - 1, S.DRIVE[0], -S.DRIVE[1], S.DRIVE[1], S.Z0 - 1, S.DRIVE[2]))        # drive motor
    body = body.cut(C.box(S.TUN_X0, S.X1 + 1, -r, r, S.Z0 - 1, C.WHEEL["z"]))                          # below the axis
    # column: M5 into its end, button head counterbored under the deck (head 2.75)
    body = body.cut(C.cyl(C.FIT["m5"] / 2, 20, (G.XC, G.YC, zt - 15), (0, 0, 1)))
    body = body.cut(C.cyl(5.2, 3.0, (G.XC, G.YC, zd - S.DECK_T - 0.01), (0, 0, 1)))
    # corner bracket behind the column: M5 down through the deck into a nut in a side pocket (inner block, solid there)
    bx = S.BRACKET_NUT_X
    body = body.cut(C.cyl(C.FIT["m5"] / 2, 14, (bx, G.YC, zd - 13), (0, 0, 1)))
    body = body.cut(C.box(bx - 4.2, bx + 4.2, G.YC - 4.6, S.Y1 + 1, zd - 12, zd - 7.6))                # M5 nut 8 AF x 4.4, open +y
    # floor: M4 from the deck top to the floor plate, heads counterbored flush
    for (x, y) in S.FLOOR_SCREWS:
        body = body.cut(C.cyl(C.FIT["m4"] / 2, zd - S.Z0 + 2, (x, y, S.Z0 - 1), (0, 0, 1)))
        body = body.cut(C.cyl(4.25, 4.2, (x, y, zd - 4.0), (0, 0, 1)))
    body = body.removeSplitter()
    # checks: wheel clearance (min distance from the wheel cylinder), drive motor box
    wheel = C.cyl(C.WHEEL["r"], C.WHEEL["x1"] - C.WHEEL["x0"], (C.WHEEL["x0"], 0, C.WHEEL["z"]), (1, 0, 0))
    drive = C.box(32, 100, -18.5, 18.5, 18.5, 55.5)
    info = dict(wheel_gap=body.distToShape(wheel)[0], drive_gap=body.distToShape(drive)[0],
                deck_under=C.WHEEL["z"] + r, deck_top=zd, mass=C.mass_of(body), screws=S.FLOOR_SCREWS, solids=len(body.Solids))
    return body, info


class SB:
    """SADDLE socle on base_330_js (printed ABS): deck over the drive wheel + motor + odometry, on 4 legs standing on
    the free plate zones (Seif's sketch 2026-11-20). Robot frame = base_330_js assembly frame."""
    Z_PLATE = 16.5                        # plate top
    DECK_Z0, DECK_T_MIN = 67.0, 3.0       # deck underside away from the wheel (drive motor top 62.5 + 4.5)
    CLR = 5.0                             # around the wheel's worst-case envelope Ø80 (R40) -> tunnel R45, crown 82
    TUN_X = (74.0, 136.0)                 # the plate's wheel well
    MOTOR_CUT = (15.0, 78.5, 22.0, 67.0)  # drive motor (top 62.5) + hinge (x <= 77.7, |y| <= 20): x0, x1, |y|, z
    ODO_CUT = (131.0, 142.0, -66.0, 33.0, 70.0)   # odometry: AMT (z 58.2), dead wheel, arm, bracket (61.2), screws (64.2)
    X0, X1 = 25.0, 141.0                  # x 25: the clapets NEMA17 (x -21..21, y 43..89) reaches z 76
    Y_OUT = 60.0                          # deck |y| for x >= 70
    Y_IN = 55.0                           # deck |y| for x < 70 (clapets rails at y 58, x 30..51)
    # legs on the free plate zones: (x0, x1), (y0, y1)
    LEGS = (((80.0, 128.0), (-60.0, -45.2)),    # beside the wheel well, back (odometry bracket from x 132), to the well edge
            ((80.0, 128.0), (45.2, 60.0)),      # beside the wheel well, front (clapets door unit from y 69)
            ((25.0, 74.0), (-42.0, -24.0)),     # beside the drive motor, back (hinge |y| <= 20; keep y > -43.5 for a back module socle)
            ((25.0, 66.0), (24.0, 40.0)))       # beside the drive motor, front (clapets socle from y 43.5)
    FOOT_T = 10.0                         # foot above the plate; the screw head sits in a Ø9 channel from the deck top
    SCREWS = ((88.0, -53.5), (120.0, -53.5), (88.0, 53.5), (120.0, 53.5), (33.0, -33.0), (66.0, -33.0), (33.0, 32.0), (58.0, 32.0))
    HEEL = (106.0, 118.0, -5.0, 13.0)     # heel on the column back face, within its width (the carriage tabs pass beside it)
    HEEL_Z1 = 112.0
    HEEL_SCREWS_Z = (96.0, 106.0)         # 2 x M5 into T-nuts in the back slot (free z 88..119 below the rack)
    # lightening, keeping the stiffness: pockets open at the BOTTOM inside the legs (3 mm walls round the screw channels,
    # 7 mm cap under the deck) and a grid under the deck over the drive motor (4 mm top skin, 3 mm ribs). The 3 mm crown
    # over the wheel, the pad, the heel and the ribs are not touched. (x0, x1, y0, y1, z0, z1)
    POCKETS = ((95.0, 113.0, -57.0, -50.0, 16.4, 60.0), (95.0, 113.0, 50.0, 57.0, 16.4, 60.0),          # legs beside the well
               (40.0, 59.0, -39.0, -27.0, 16.4, 60.0), (40.0, 51.0, 27.0, 37.0, 16.4, 60.0),           # legs beside the motor
               (28.0, 48.0, -19.0, -3.0, 66.9, 81.0), (28.0, 48.0, 3.0, 19.0, 66.9, 81.0),             # deck over the motor
               (51.0, 71.0, -19.0, -3.0, 66.9, 81.0), (51.0, 71.0, 3.0, 19.0, 66.9, 81.0),
               (28.0, 48.0, -52.0, -45.0, 66.9, 81.0), (51.0, 71.0, -52.0, -45.0, 66.9, 81.0),
               (28.0, 48.0, 45.0, 52.0, 66.9, 81.0), (51.0, 63.0, 45.0, 52.0, 66.9, 81.0))
    RIBS = ()                             # edge ribs removed (Seif 2026-11-20: unnecessary)


def saddle_socle():
    zt = G.PROF_Z0
    r = C.WHEEL["r"] + SB.CLR
    zd = C.WHEEL["z"] + r + SB.DECK_T_MIN           # deck top (85)
    # deck slab (narrower in y where the clapets rails are) + legs
    deck = C.box(70.0, SB.X1, -SB.Y_OUT, SB.Y_OUT, SB.DECK_Z0, zd).fuse(
        C.box(SB.X0, 70.0 + 0.01, -SB.Y_IN, SB.Y_IN, SB.DECK_Z0, zd))
    body = deck
    for (x0, x1), (y0, y1) in SB.LEGS:
        body = body.fuse(C.box(x0, x1, y0, y1, SB.Z_PLATE, SB.DECK_Z0 + 1))
    # pad under the column + heel on its back face
    body = body.fuse(C.box(G.XC - 10, G.XC + 10, G.YC - 10, G.YC + 10, zd - 1, zt))
    hx0, hx1, hy0, hy1 = SB.HEEL
    body = body.fuse(C.box(hx0, hx1, hy0, hy1, zd - 1, SB.HEEL_Z1))
    for (x0, x1), (y0, y1), h in SB.RIBS:
        body = body.fuse(C.box(x0, x1, y0, y1, zd - 1, zd + h))
    # form fit: a tongue under each well-side leg drops into the plate's wheel well (centres the saddle in y)
    for sgn in (1, -1):
        y_a, y_b = sorted((sgn * 45.2, sgn * 42.7))
        body = body.fuse(C.box(82.0, 126.0, y_a, y_b, SB.Z_PLATE - 4.0, SB.Z_PLATE + 0.5))
    # form fit: key on the heel's front face into the column's back slot (below the rack), and a gusset behind the heel
    body = body.fuse(C.box(hx1 - 0.5, hx1 + 1.4, G.YC - 2.8, G.YC + 2.8, zt + 0.5, SB.HEEL_Z1 - 2.0))
    for gy in (hy0, hy1 - 3.0):                          # gussets on both sides of the heel (its screws in the middle)
        gus = Part.Face(Part.makePolygon([Vector(hx0 + 0.5, 0, zd - 0.5), Vector(hx0 + 0.5, 0, SB.HEEL_Z1 - 3.0),
                                          Vector(hx0 - 14.0, 0, zd - 0.5), Vector(hx0 + 0.5, 0, zd - 0.5)])).extrude(Vector(0, 3.0, 0))
        gus.translate(Vector(0, gy, 0))
        body = body.fuse(gus)
    body = body.removeSplitter()
    # cut-outs: wheel tunnel (R45 around the worst-case envelope), drive motor + hinge, odometry module
    body = body.cut(C.cyl(r, SB.TUN_X[1] - SB.TUN_X[0], (SB.TUN_X[0], 0.0, C.WHEEL["z"]), (1, 0, 0)))
    body = body.cut(C.box(SB.TUN_X[0], SB.TUN_X[1], -r, r, 0.0, C.WHEEL["z"]))
    mx0, mx1, my, mz = SB.MOTOR_CUT
    body = body.cut(C.box(mx0, mx1, -my, my, 0.0, mz))
    ox0, ox1, oy0, oy1, oz = SB.ODO_CUT
    body = body.cut(C.box(ox0, ox1, oy0, oy1, 0.0, oz))
    # heel: 2 x M5 along x into T-nuts in the back slot, heads in counterbores on the heel's inner face
    for zz in SB.HEEL_SCREWS_Z:
        body = body.cut(C.cyl(C.FIT["m5"] / 2, hx1 - hx0 + 2, (hx0 - 1, G.YC, zz), (1, 0, 0)))
        body = body.cut(C.cyl(4.6, 5.2, (hx0 - 0.01, G.YC, zz), (1, 0, 0)))
    # floor: M4 from the top: Ø9 access channel from the deck top down to the foot, Ø4.6 through the foot (nut under the plate)
    for (x, y) in SB.SCREWS:
        body = body.cut(C.cyl(C.FIT["m4"] / 2, SB.FOOT_T + 2, (x, y, SB.Z_PLATE - 1), (0, 0, 1)))
        body = body.cut(C.cyl(4.5, zd + 20 - (SB.Z_PLATE + SB.FOOT_T), (x, y, SB.Z_PLATE + SB.FOOT_T), (0, 0, 1)))
    mass_full = C.mass_of(body)
    for (x0, x1, y0, y1, z0, z1) in SB.POCKETS:
        body = body.cut(C.box(x0, x1, y0, y1, z0, z1))
    body = body.removeSplitter()
    body, ch_done, ch_tried = C.chamfer_outer(body)
    G.CHAMFERS["SADDLE_SOCLE"] = (ch_done, ch_tried)
    info = dict(deck_top=zd, crown=C.WHEEL["z"] + r, mass=C.mass_of(body), mass_full=mass_full, solids=len(body.Solids),
                deck_under=C.WHEEL["z"] + r, wheel_gap=SB.CLR, drive_gap=SB.MOTOR_CUT[3] - 62.5)
    return body, info


def fixation(zc):
    """Column fixation parts for G.FIX (robot frame). Fasteners (SCR_ / NUT_ / TNUT_) in their holes."""
    out = {}
    xb = G.XC - 10                                       # column back face
    y0, y1 = G.YC - 10, G.YC + 10
    core_x = 40.0                                        # cross-members run inward to here (core structure, x <= 64)
    # ---- top (all variants): 2020 cross-member along x under the roof, back face of the column -> core
    out["TOP_MEMBER_2020"] = C.box(core_x, xb, y0, y1, G.PROF_Z1 - 20, G.PROF_Z1)
    out["TOP_L_BRACKET"] = l_bracket(xb, G.PROF_Z1, False)                               # in the back slot's top end
    zt_ = G.PROF_Z1 - 10.0
    out["SCR_M5x10_TOP_x2"] = Part.makeCompound([C.screw(5, 10, (xb - 3.0, G.YC, zt_), (1, 0, 0)),
                                                 C.screw(5, 10, (xb - 10.0, G.YC, G.PROF_Z1 + 3.0), (0, 0, -1))])
    out["TNUT_M5_TOP_x2"] = Part.makeCompound([C.tnut((xb + 4.0, G.YC, zt_), (1, 0, 0), (0, 0, 1)),
                                               C.tnut((xb - 10.0, G.YC, G.PROF_Z1 - 4.0), (0, 0, 1), (1, 0, 0))])
    if G.FIX == "slot":
        out["BOTTOM_MEMBER_2020"] = C.box(core_x, xb, y0, y1, G.PROF_Z0 - 20, G.PROF_Z0)  # above the drive motor
        out["BOTTOM_L_BRACKET"] = l_bracket(xb, G.PROF_Z0, True, h_z=G.SOCLE_INFO["deck_top"])
    elif G.FIX == "saddle":
        out["SADDLE_SOCLE"], G.SOCLE_INFO = saddle_socle()
        ft = SB.Z_PLATE + SB.FOOT_T
        out["SCR_M4x16_FLOOR_x8"] = Part.makeCompound([C.screw(4, 16, (x, y, ft), (0, 0, -1)) for (x, y) in SB.SCREWS])
        out["NUT_M4_FLOOR_x8"] = Part.makeCompound([C.nut(4, (x, y, SB.Z_PLATE - 5.0), (0, 0, -1)) for (x, y) in SB.SCREWS])
        hx0 = SB.HEEL[0]
        out["SCR_M5x12_HEEL_x2"] = Part.makeCompound([C.screw(5, 12, (hx0 + 5.2, G.YC, z), (1, 0, 0)) for z in SB.HEEL_SCREWS_Z])
        out["TNUT_M5_HEEL_x2"] = Part.makeCompound([C.tnut((xb + 4.0, G.YC, z), (1, 0, 0), (0, 0, 1)) for z in SB.HEEL_SCREWS_Z])
    elif G.FIX == "bridge":
        out["BRIDGE_SOCLE"], G.SOCLE_INFO = bridge_socle()
        out["BOTTOM_L_BRACKET"] = l_bracket(xb, G.PROF_Z0, True, h_z=G.SOCLE_INFO["deck_top"])
    elif G.FIX == "inward":
        x0, x1 = G.XC - 15, G.XC + 15
        out["MOTOR_SADDLE_TOP"] = C.box(x0, x1, -25.0, 25.0, G.PROF_Z0 - 3, G.PROF_Z0)
        out["MOTOR_SADDLE_LEG_BACK"] = C.box(x0, x1, -25.0, -21.0, 26.0, G.PROF_Z0 - 3)
        out["MOTOR_SADDLE_LEG_FRONT"] = C.box(x0, x1, 21.0, 25.0, 26.0, G.PROF_Z0 - 3)
    return out


def main():
    doc = App.newDocument("FLIPPER_" + G.FIX.upper())
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
        C.add(doc, "PLACE_" + n, C.moved(s, fin), "5_GHOST_place_pose", groups)
    for n in ("X_PLATE", "SERVO_MG996R", "SERVO_MOUNT", "NEMA17", "PINION_v2", "MOTOR_BRACKET"):
        C.add(doc, "PLACE_" + n, C.moved(lift[n], steps[-2]["pls"]["lift"]), "5_GHOST_place_pose", groups)
    C.add(doc, "PLACE_GRAIL", C.moved(gr[0].fuse(gr[1]), fin), "5_GHOST_place_pose", groups)

    # roof slot (arm parts)
    xs, ys = [], []
    for s_ in steps[-5:]:
        for n, s in arm.items():
            b = C.bb(C.moved(s, s_["pls"]["arm"]))
            if b.ZMin < C.ROOF_TOP and b.ZMax > C.ROOF_BOT and b.XMin < C.FACE:
                xs += [b.XMin, min(b.XMax, C.FACE)]
                ys += [b.YMin, b.YMax]
    slot = (min(xs) - 2, C.FACE + 1, min(ys) - 2, max(ys) + 2) if xs else None
    WITH_CTX = bool(os.environ.get("FLIPPER_CONTEXT"))
    for n, s in (C.robot_context(slot).items() if (WITH_CTX or C.BASE != "b330") else ()):
        C.add(doc, n, s, "6_ROBOT_CONTEXT", groups)
    base_ctx = {}
    if C.BASE == "b330":
        base_ctx = load_b330_context()                 # always loaded for the fit checks
        for n, s in (base_ctx.items() if WITH_CTX else ()):
            C.add(doc, "B330_" + n, s, "7_BASE_330_JS_reference", groups)
    else:
        drive = C.box(32, 100, -18.5, 18.5, 18.5, 55.5)
        C.add(doc, "CTX_DRIVE_MOTOR_R", drive, "6_ROBOT_CONTEXT", groups)
        C.add(doc, "CTX_FRONT_DOOR_UNIT_R", C.box(66, 150, 40, 102, 53, 252), "6_ROBOT_CONTEXT", groups)       # layout-v1 F_A_AILE_D
        C.add(doc, "CTX_BACK_BUTTERFLY", C.box(-95, 95, -56, -53, 81, 271), "6_ROBOT_CONTEXT", groups)         # layout-v1 B plate
        C.add(doc, "CTX_GRAIL_BAY", C.box(BAY["x0"], BAY["x1"], BAY["y0"], BAY["y1"], BAY["z0"], BAY["z1"]), "6_ROBOT_CONTEXT", groups)

    # ---- arm (cup + magnet included) vs the column, its fixation and the carriage at place + stowed: real distances
    arm_lines = []
    targets = [(n, s_, None) for n, s_ in list(fixed.items()) + list(info["fix"].items()) if not n.startswith(("SCR_", "NUT_", "TNUT_"))]
    targets += [(n, s_, "lift") for n, (s_, g) in parts.items() if g == "lift" and not n.startswith(("SCR_", "NUT_", "M5", "INSERT"))]
    for st_ in (steps[-2], steps[-1]):
        for an, (ash, ag) in parts.items():
            if ag != "arm" or an in ("SERVO_HORN",):
                continue
            a_ = C.moved(ash, st_["pls"]["arm"])
            for tn, tsh, tg in targets:
                t_ = C.moved(tsh, st_["pls"]["lift"]) if tg else tsh
                if not a_.BoundBox.intersect(t_.BoundBox):
                    continue
                d_ = a_.distToShape(t_)[0]
                if d_ < 0.01 and a_.common(t_).Volume < 0.001:
                    continue
                if d_ < 3.0:
                    arm_lines.append("  %-14s - %-20s %s: %.2f mm%s" % (an, tn, st_["label"], d_, "  CLASH" if d_ < 0.01 else ""))
    # ---- base_330_js: real distances between our parts (pick + top poses) and the base's parts
    b330_lines = b330_checks(base_ctx, fixed, info["fix"], parts, steps) if C.BASE == "b330" else []
    # ---- layout envelope (bounding boxes vs the bay, the wheel, the drive motor); pick + top poses
    env = []
    wheel_c = (C.WHEEL["z"], C.WHEEL["r"])
    checks = [(n, C.bb(s)) for n, s in fixed.items()]
    for s_, tag in ((steps[0], "pick"), (steps[4], "top")):
        for n, (s, g) in parts.items():
            if g == "lift" or n in ("SERVO_HORN", "SHAFT_5"):
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

    # ---- fixation: what it is + coarse checks (bounding boxes vs the wheel, drive motor, carriage at pick / top)
    fix_lines = {"saddle": ["  SADDLE_SOCLE (printed ABS, one part, %.0f g at 60 pct, %.0f g before the %d lightening pockets): deck x %.0f..%.0f over the drive wheel (tunnel R%.0f around its "
                            "worst-case envelope Ø80: crown z %.0f, deck top %.0f), the drive motor (deck underside %.0f, motor top 62.5) and "
                            "the odometry module (underside %.0f); pad under the column to %.0f; heel on the column's back face (x %.0f..%.0f, "
                            "to z %.0f) with 2 x M5 into T-nuts in the back slot (z %s)"
                            % (G.SOCLE_INFO.get("mass", 0) * 1000, G.SOCLE_INFO.get("mass_full", 0) * 1000, len(SB.POCKETS), SB.X0, SB.X1, C.WHEEL["r"] + SB.CLR, G.SOCLE_INFO.get("crown", 0),
                               G.SOCLE_INFO.get("deck_top", 0), SB.DECK_Z0, SB.ODO_CUT[4], G.PROF_Z0, SB.HEEL[0], SB.HEEL[1], SB.HEEL_Z1,
                               ", ".join("%.0f" % z for z in SB.HEEL_SCREWS_Z)),
                            "  legs on the free plate zones (Seif's sketch): %s" % "; ".join("x %.0f..%.0f y %.0f..%.0f" % (a[0], a[1], b[0], b[1]) for a, b in SB.LEGS),
                            "  PLATE HOLES TO ADD (not in the plate yet, Seif will confirm): %d x Ø4.4 for M4 at %s; M4 x 16 from the "
                            "top through a Ø9 channel + nut under the plate" % (len(SB.SCREWS), ", ".join("(%.0f, %.1f)" % p_ for p_ in SB.SCREWS))],
                 "slot": ["  rack cut to the pinion's travel (z %.0f..%.0f, %.0f long): the back slot is free at both ends" % (G.RACK_Z[0], G.RACK_Z[1], G.RACK_Z[1] - G.RACK_Z[0]),
                          "  bottom: 2020 corner bracket in the back slot (z %.0f..%.0f) onto a 2020 cross-member along x, z %.0f..%.0f, "
                          "x 40..%.0f (above the drive motor, top 55.5)" % (G.PROF_Z0, G.PROF_Z0 + 20, G.PROF_Z0 - 20, G.PROF_Z0, G.XC - 10)],
                 "bridge": ["  BRIDGE_SOCLE (printed ABS, one part): block x %.0f..%.0f, y %.0f..%.0f, z %.0f..%.0f with a tunnel R%.0f around "
                            "the wheel (x %.0f..): deck underside over the wheel z %.0f (wheel top 74), deck top %.0f, pad under the column to %.0f; wheel clearance %.1f mm (min "
                            "distance), drive motor %.1f mm; back wall 9 thick at y %.0f..%.0f; ribs on the deck (4 / 12 tall); front support = the inner block "
                            "above the drive motor (the door unit starts at y 40); %d solid, %.0f g ABS (60 pct)"
                            % (S.X0, S.X1, S.Y0, S.Y1, S.Z0, G.PROF_Z0, C.WHEEL["r"] + S.WHEEL_CLR, S.TUN_X0,
                               G.SOCLE_INFO["deck_under"], G.SOCLE_INFO["deck_top"], G.PROF_Z0, G.SOCLE_INFO["wheel_gap"], G.SOCLE_INFO["drive_gap"], S.Y0,
                               -(C.WHEEL["r"] + S.WHEEL_CLR), G.SOCLE_INFO["solids"], G.SOCLE_INFO["mass"] * 1000),
                            "  column: M5 x 12 button head from under the deck into its end + 2020 corner bracket in the back slot "
                            "(z %.0f..%.0f), M5 down through the deck into a nut in a side pocket" % (G.PROF_Z0, G.PROF_Z0 + 20),
                            "  floor: %d x M4 through the full height (%.0f) into the floor plate, heads counterbored flush with the "
                            "deck, at %s" % (len(S.FLOOR_SCREWS), G.PROF_Z0 - S.Z0, ", ".join("(%.0f, %.0f)" % p_ for p_ in S.FLOOR_SCREWS))],
                 "inward": ["  column at x %.0f (over the drive motor), on a saddle z %.0f..%.0f with legs at y +-21..25 beside the drive motor; "
                            "column bolted through its end hole (M5); servo mount base -> pivot reach %.0f mm"
                            % (G.XC, G.PROF_Z0 - 3, G.PROF_Z0, G.PX - (G.XC + 14.8))]}[G.FIX]
    fix_lines.append("  top (all variants): 2020 cross-member along x, x 40..%.0f, z %.0f..%.0f, corner bracket in the back slot's "
                     "top end (z %.0f..%.0f) -> the arm's lower edge above x %.0f..%.0f: %.1f..%.1f"
                     % (G.XC - 10, G.PROF_Z1 - 20, G.PROF_Z1, G.PROF_Z1 - 20, G.PROF_Z1, G.XC - 30, G.XC + 10,
                        G.Z_PLACE + (G.PX - (G.XC + 10)) / (G.PX - C.X_PLACE) * (C.ROOF_TOP - G.Z_PLACE) - 7.0,
                        G.Z_PLACE + (G.PX - min(G.XC - 30, C.X_PLACE)) / (G.PX - C.X_PLACE) * (C.ROOF_TOP - G.Z_PLACE) - 7.0))
    wheel_box = App.BoundBox(C.WHEEL["x0"], -C.WHEEL["r"], 0, C.WHEEL["x1"], C.WHEEL["r"], 2 * C.WHEEL["r"])
    drive_box = App.BoundBox(32, -18.5, 18.5, 100, 18.5, 55.5)
    for fn, fs in info["fix"].items():
        fb = C.bb(fs)
        hits = []
        if C.BASE != "b330" and fn != "BRIDGE_SOCLE" and fb.intersect(drive_box) and fb.ZMin < 55.5 and fb.YMin < 18.5 and fb.YMax > -18.5 and fb.XMin < 100 and fb.XMax > 32:
            hits.append("drive motor box (fix bottom %.1f vs motor top 55.5)" % fb.ZMin)
        if C.BASE != "b330" and fn != "BRIDGE_SOCLE" and fb.intersect(wheel_box) and (fb.YMin < C.WHEEL["r"] and fb.YMax > -C.WHEEL["r"]):
            yy = 0.0 if fb.YMin < 0 < fb.YMax else min(abs(fb.YMin), abs(fb.YMax))
            wt = C.WHEEL["z"] + math.sqrt(max(0.0, C.WHEEL["r"] ** 2 - yy ** 2)) if yy < C.WHEEL["r"] else -1
            if fb.ZMin < wt + 1:
                hits.append("wheel (bottom %.1f vs wheel top %.1f)" % (fb.ZMin, wt))
        for cn, cb_ in (("front door unit", App.BoundBox(66, 40, 53, 150, 102, 252)), ("back butterfly plate", App.BoundBox(-95, -56, 81, 95, -53, 271))):
            if C.BASE != "b330" and fb.intersect(cb_):
                hits.append(cn)
        for s_, tag in ((steps[0], "pick"), (steps[4], "top")):
            for n_, (sh_, g_) in parts.items():
                if g_ != "lift":
                    continue
                if fb.intersect(C.bb(C.moved(sh_, s_["pls"][g_]))):
                    d_ = fs.distToShape(C.moved(sh_, s_["pls"][g_]))[0] if fs.BoundBox.DiagonalLength < 300 else 0.0
                    hits.append("%s @%s (boxes meet, real gap %.1f)" % (n_, tag, d_))
        fix_lines.append("  %-20s x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f: %s" % (fn, fb.XMin, fb.XMax, fb.YMin, fb.YMax, fb.ZMin, fb.ZMax,
                                                                     "; ".join(hits) if hits else "clear"))

    # ---- numbers
    pb = info["plate_bb"]
    zc_top = G.ZC_PICK + top
    wb = info["wheel_bb"]
    wheel_lo, wheel_hi = wb.ZMin - G.ZC_PICK, wb.ZMax - G.ZC_PICK          # wheel extents around the plate centre
    pin_x, gear_y, pin_z = info["pin"]
    rb = C.bb(fixed["RACK_m1_printed"])
    plate_top_place = pb.ZMax + (G.Z_PLACE - G.Z_PICK)
    arm_lower_at = lambda x: G.Z_PLACE + (G.PX - x) / (G.PX - C.X_PLACE) * (C.ROOF_TOP - G.Z_PLACE) - 7.0
    arm_mass = C.mass_of(arm["ARM_PRINTED"])
    m_moving = C.G_MASS + C.MAG_MASS + arm_mass + 0.055 + 0.28 + 0.039 + 0.03 + 0.06    # + servo, NEMA, plate, wheels, brackets
    f_lift = m_moving * 9.81
    t_pin = f_lift * 0.010
    arm_c = C.com(arm["ARM_PRINTED"])
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
    # body parts in the Grail's plane (|y| < G_W/2) vs the zone the Grail sweeps: radius >= grail_r inside the angular
    # sector it travels through (pick corners' angles .. +180)
    gpts = [Vector(x, 0, z) for x in (C.X_PICK - C.G_W / 2, C.X_PICK + C.G_W / 2) for z in (0.0, C.G_H)]
    angs = [math.degrees(math.atan2(p_.z - G.Z_PICK, p_.x - G.PX)) for p_ in gpts]
    a0, a1 = min(angs), max(angs) + 180.0
    hits = []
    for n_ in ("SERVO_MOUNT", "SERVO_MG996R", "BEARING_625", "X_PLATE"):
        pts = lift[n_].tessellate(0.5)[0]
        for p_ in pts:
            if abs(p_.y) < C.G_W / 2 + 2:
                rr = math.hypot(p_.x - G.PX, p_.z - G.Z_PICK)
                aa = math.degrees(math.atan2(p_.z - G.Z_PICK, p_.x - G.PX))
                if aa < a0 - 1:
                    aa += 360
                if rr >= grail_r - 2 and a0 - 2 <= aa <= a1 + 2:
                    hits.append((n_, rr, aa))
    cheek_r = max(math.hypot(x - G.PX, z - G.Z_PICK) for x in (C.bb(lift["BEARING_625"]).XMin, C.bb(lift["BEARING_625"]).XMax)
                  for z in (C.bb(lift["BEARING_625"]).ZMin, C.bb(lift["BEARING_625"]).ZMax))
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
         "  rack: slid in from the end, V back on the cavity's inner faces (2D sections; play to the lips %.2f): nose %.2f below the face; pitch line x %.2f (tips %.2f past the back face), z %.1f..%.1f; "
         "pinion centre x %.2f, z %.1f (pick) .. %.1f (flip), on the rack: %s"
         % (G.RACK_PLAY, G.RACK_SEAT, info["pitch_x"], 5.0 - G.RACK_SEAT, rb.ZMin, rb.ZMax, pin_x, pin_z, pin_z + top,
            "OK" if rb.ZMin + 11 <= pin_z + 0.01 and pin_z + top <= rb.ZMax - 11 + 0.01 else "OFF THE RACK"),
         "  motor face y %.1f (eccentric wheel edge %.1f, gap %.1f); pinion %.1f long; gear centre y %.1f vs rack centre %.1f; motor body x %.1f..%.1f "
         "y %.1f..%.1f z %.1f..%.1f (pick)"
         % (info["face_y"], info["ecc_ymin"], info["ecc_ymin"] - info["face_y"], info["pin_len"], gear_y, G.YC, mbb.XMin, mbb.XMax, mbb.YMin, mbb.YMax, mbb.ZMin, mbb.ZMax),
         "  lift: ~%.2f kg moving -> %.1f N on the rack, %.3f N.m on the motor (NEMA17 ~0.4); the rack can be back-driven: "
         "at 100 s / e-stop the carriage drops (Grail already released at the end; mid-carry it falls)" % (m_moving, f_lift, t_pin),
         "",
         "  pinion: gear %.0f wide must pass the slot lip (6.35): gear tip x %.2f vs the back face x %.1f (%s)"
         % (5.0, pin_x + 11.0, G.XC - 10, "gear dips %.2f into the slot" % (pin_x + 11.0 - (G.XC - 10)) if pin_x + 11.0 > G.XC - 10 else "outside"),
         "",
         "COLUMN FIXATION: %s" % G.FIX.upper()]
    r += fix_lines
    r += ["",
         "CYCLE (bounding boxes, no clash check). act.out = actuator x past the right face (x %.0f)" % C.FACE]
    r += lines
    r += ["", "SUMMARY"] + C.summary_lines(worst, start_out)
    r += ["  arm (cup + magnet) vs column / fixation / carriage at the place and stowed poses (real distances, < 3 mm listed): "
          + ("none" if not arm_lines else "")] + arm_lines
    r += ["  chamfers 1 mm on the printed parts (convex straight edges between planar faces; refused edges left sharp): %s"
          % ", ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in getattr(G, "CHAMFERS", {}).items()),
          "  form fits: saddle tongues in the plate's wheel well (y); heel key in the column's back slot; servo mount lip on "
          "the X plate's lower edge; motor bracket steps on the X plate tabs' ends; arm on the horn's disc pocket"]
    r += ["  roof slot for the arm: %s" % ("x %.1f..%.1f, y %.1f..%.1f" % slot if slot else "none"),
          "  plate top at the place %.1f vs the arm's lower edge above x %.0f..%.0f: %.1f..%.1f"
          % (plate_top_place, pb.XMin, pb.XMax, arm_lower_at(pb.XMax), arm_lower_at(pb.XMin)),
          "  profile top %.0f vs the arm's lower edge above the profile (x %.0f..%.0f): %.1f..%.1f"
          % (G.PROF_Z1, G.XC - 10, G.XC + 10, arm_lower_at(G.XC + 10), arm_lower_at(G.XC - 10)),
          "  Grail nearest point to the axis %.1f, sweeping %.0f..%.0f deg; servo reaches %.1f, 625 %.1f; body points inside "
          "the Grail's swept zone: %s" % (grail_r, a0, a1, servo_r, cheek_r,
                                          ", ".join(sorted(set(h[0] for h in hits))) if hits else "none"),
          "  flip torque max %.1f kg.cm at %d deg (MG996R ~9.4: %.1fx)" % (tmax, tang, 9.4 / tmax if tmax else 0),
          "",
          ]
    if C.BASE == "b330":
        r += ["FIT ON BASE_330_JS (real distances to the base's parts from ../../base_330_js/CAD/base_330_js_assembly.FCStd; "
              "pick + top poses; < 3 mm listed)"] + b330_lines
    else:
        r += ["LAYOUT ENVELOPE (bounding boxes vs layout-v1: Grail bay x %.0f..%.0f, y %.0f..%.0f, z %.0f..%.0f; right wheel; drive motor)"
              % (BAY["x0"], BAY["x1"], BAY["y0"], BAY["y1"], BAY["z0"], BAY["z1"])]
        r += env or ["  everything inside the bay"]
    r += ["",
          "PARTS (📦 library · 🇹🇳 local · ✈️ import)",
          "  Two Trees X carriage: plate + 3 V-wheels + 3 M5x25 + nyloc + spacers + eccentric 📦 · 2020 profile cut to %.0f 📦 · "
          "NEMA17 📦 (40 mm; shorter later) · rack m1 printed (Seif's, fits) cut to %.0f · pinion v2 printed (M3 insert K5) · "
          "MG996R + round horn 📦 · 625 + Ø5 pin 📦/🇹🇳 · electromagnet Ø30 🇹🇳 · upper wheel screws M5x25 -> M5x35 🇹🇳 · "
          "2 x M3x16 + 2 x M3 self-tap + 4 x M2x6 + M4 nut"
          % (G.PROF_Z1 - G.PROF_Z0, rb.ZLength),
          "  printed ABS: motor bracket, servo bracket + 625 cheek, arm + magnet cup (~%.0f g), pinion" % (arm_mass * 1000)]
    # print files of the printed parts (robot frame at the pick pose; print orientation in the assembly sheet)
    os.makedirs(PRINT, exist_ok=True) if os.environ.get("FLIPPER_PRINT") else None
    import MeshPart
    for n, s_ in ((("FLIPPER_ARM", arm["ARM_PRINTED"]), ("FLIPPER_SERVO_MOUNT", lift["SERVO_MOUNT"]),
                   ("FLIPPER_MOTOR_BRACKET", lift["MOTOR_BRACKET"]), ("FLIPPER_RACK_%.0f" % (G.RACK_Z[1] - G.RACK_Z[0]), info["rack_print"]))
                  + ((("FLIPPER_BRIDGE_SOCLE", info["fix"]["BRIDGE_SOCLE"]),) if "BRIDGE_SOCLE" in info["fix"] else ())
                  + ((("FLIPPER_SADDLE_SOCLE", info["fix"]["SADDLE_SOCLE"]),) if "SADDLE_SOCLE" in info["fix"] else ())
                  if os.environ.get("FLIPPER_PRINT") else ()):
        s_.exportStep(os.path.join(PRINT, n + ".step"))
        MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.05, AngularDeflection=0.2).write(os.path.join(PRINT, n + ".stl"))
    hi = info["head"]
    r[r.index("PARTS (📦 library · 🇹🇳 local · ✈️ import)"):r.index("PARTS (📦 library · 🇹🇳 local · ✈️ import)")] = [
        "PRINTED PARTS (print/)",
        "  FLIPPER_ARM: hub Ø24 with the round horn's disc in a Ø21.4 pocket (+ Ø9.8 boss recess), 4 x M2 x 12 from +y "
        "into the horn holes at r 7.2 (Ø2.5, T9 coupon); Ø5 x %.0f pin pressed 6 deep from +y (pushed in LAST, through the "
        "625); bar 14 x 10; cup Ø%.1f seat %.0f deep (magnet face 4 proud), M4 stud + nut in a pocket; %d solid(s), "
        "%.0f g ABS (60 pct)" % (C.bb(arm["SHAFT_5"]).YLength, C.MAG_SEAT, C.MAG_L - 4, len(arm["ARM_PRINTED"].Solids), arm_mass * 1000),
        "  FLIPPER_SERVO_MOUNT: base %.0f thick on the X plate front (x %.1f..%.1f): 2 x M5x35 through the upper wheel screw "
        "holes (y %.1f, z %s), 2 x M3 into the plate's tapped holes (y %.1f, z %s), recess for the eccentric nyloc; servo "
        "plate y %.1f..%.1f under the ears (ear plane y %.1f..%.1f), 2 x M3 x 12 + nuts in pockets; 625 cheek (seat Ø16.2 "
        "open on +y, lip on the arm side); %d solid(s), %.0f g ABS (60 pct)"
        % (G.BASE_T, hi["base_x"][0], hi["base_x"][1], hi["m5"][0][0], ", ".join("%.1f" % z for _, z in hi["m5"]),
           hi["m3"][0][0], ", ".join("%.1f" % z for _, z in hi["m3"]), hi["plate_y"][0], hi["plate_y"][1], hi["ear_y"][0],
           hi["ear_y"][1], len(lift["SERVO_MOUNT"].Solids), C.mass_of(lift["SERVO_MOUNT"]) * 1000),
        "  FLIPPER_MOTOR_BRACKET: plate %.1f thick at y %.1f..%.1f (motor face side; %.1f off the eccentric wheel), "
        "NEMA17 4 x M3 + Ø23 pilot; 2 bridges to the X plate's bottom tabs (upper butts on the small bent tab, lower wraps the tab's end), 2 x M3x20 at %s (DRILL Ø2.5 + TAP M3 in the "
        "tabs); %d solid(s), %.0f g ABS (60 pct)" % (G.BRACKET_T, info["bracket_y"][0], info["bracket_y"][1],
                                                    info["ecc_ymin"] - info["bracket_y"][1],
                                                    ", ".join("(x %.0f, z %.0f)" % t_ for t_ in info["tab_screws"]),
                                                    len(lift["MOTOR_BRACKET"].Solids), C.mass_of(lift["MOTOR_BRACKET"]) * 1000),
        "  FLIPPER_RACK_%.0f: Seif's rack cut to %.0f (rack frame, as printed before)" % (G.PROF_Z1 - G.PROF_Z0, G.PROF_Z1 - G.PROF_Z0),
        "  servo body y %.1f..%.1f; SERVO_MOUNT y %.1f..%.1f" % (C.bb(lift["SERVO_MG996R"]).YMin,
                                                                               C.bb(lift["SERVO_MG996R"]).YMax,
                                                                               C.bb(lift["SERVO_MOUNT"]).YMin, C.bb(lift["SERVO_MOUNT"]).YMax),
        ""]
    if App.GuiUp:
        colour(doc)
    C.save(doc, ("FLIPPER_B330_IN_BASE" if WITH_CTX else "FLIPPER_B330") if C.BASE == "b330" else "FLIPPER_" + G.FIX.upper(), r)


B330_PARTS = ("plate", "wheels_JS7444_nominal_PH", "wheels_JS7444_ENVELOPE", "motors_37D_PH", "hinges_PH", "odo_bracket",
              "odo_arm", "dead_wheel", "amt102", "shaft_D6", "bearing_696", "bearing_F623", "spring", "screws_M3",
              "ball_units_KSM15_PH", "ball_holders", "ball_shims", "clapets_v7_moduleA")


def load_b330_context():
    """The real base_330_js parts (Ayoub's assembly, same frame: X wheel axis, Y front, z 0 table)."""
    d = App.openDocument(C.B330_ASM)
    out = {}
    for n in B330_PARTS:
        o = d.getObject(n)
        if o is not None and not o.Shape.isNull():
            out[n] = o.Shape.copy()
    App.closeDocument(d.Name)
    return out


def b330_checks(ctx, fixed, fix, parts, steps):
    """Smallest real distance from each of our parts (fixed, fixation, carriage at pick + top) to each base part;
    lines for < 3 mm. The plate is expected to touch the socle legs."""
    ours = [(n, s, "") for n, s in list(fixed.items()) + list(fix.items())]
    for s_, tag in ((steps[0], " @pick"), (steps[4], " @top")):
        for n, (sh, g) in parts.items():
            ours.append((n, C.moved(sh, s_["pls"][g]), tag))
    lines, worst = [], {}
    for on, osh, tag in ours:
        ob = C.bb(osh)
        ob.enlarge(3.0)
        for cn, csh in ctx.items():
            cands = [x for x in csh.Solids if x.BoundBox.intersect(ob)] if cn == "clapets_v7_moduleA" else (
                [csh] if csh.BoundBox.intersect(ob) else [])
            for c_ in cands:
                try:
                    d = osh.distToShape(c_)[0]
                    if d < 0.01 and osh.common(c_).Volume < 0.001:
                        # distToShape gives a false 0 on some imported models (clapets NEMA17): use the boxes' gap
                        a_, b_ = osh.optimalBoundingBox(False, False), c_.optimalBoundingBox(False, False)
                        d = max(0.0, a_.XMin - b_.XMax, b_.XMin - a_.XMax, a_.YMin - b_.YMax, b_.YMin - a_.YMax,
                                a_.ZMin - b_.ZMax, b_.ZMin - a_.ZMax)
                except Exception:
                    continue
                key = (on + tag, cn)
                worst[key] = min(d, worst.get(key, 1e9))
    for (on, cn), d in sorted(worst.items(), key=lambda kv: kv[1]):
        if d < 3.0:
            note = "sits on the plate (expected)" if cn == "plate" and on.startswith(("SADDLE", "BRIDGE")) else (
                "through the plate: holes to add (expected)" if cn == "plate" and on.startswith(("SCR_M4", "NUT_M4")) else (
                    "CLASH" if d < 0.01 else "close"))
            if cn == "wheels_JS7444_ENVELOPE":
                note += " (worst-case wheel Ø80)"
            lines.append("  %-30s - %-26s %6.2f mm  %s" % (on, cn, d, note))
    near = sorted(((d, on, cn) for (on, cn), d in worst.items() if d >= 3.0))[:8]
    lines.append("  nearest others: " + "; ".join("%s - %s %.1f" % (on, cn, d) for d, on, cn in near))
    return lines or ["  all >= 3 mm"]


COLOURS = [  # (name prefix, rgb, transparency)
    ("ARM_PRINTED", (1.0, 0.55, 0.10), 0), ("SERVO_MOUNT", (0.20, 0.45, 0.90), 0), ("MOTOR_BRACKET", (0.20, 0.70, 0.30), 0),
    ("PINION", (0.95, 0.80, 0.10), 0), ("RACK", (0.95, 0.60, 0.20), 0), ("SADDLE_SOCLE", (0.10, 0.60, 0.60), 0),
    ("BRIDGE_SOCLE", (0.10, 0.60, 0.60), 0), ("TOP_MEMBER", (0.75, 0.75, 0.80), 0), ("TOP_L", (0.60, 0.60, 0.65), 0),
    ("BOTTOM_L", (0.60, 0.60, 0.65), 0), ("PROFILE", (0.80, 0.80, 0.83), 0), ("X_PLATE", (0.35, 0.35, 0.40), 0),
    ("V_WHEELS", (0.08, 0.08, 0.08), 0), ("M5", (0.50, 0.50, 0.50), 0), ("ECCENTRIC", (0.60, 0.50, 0.30), 0),
    ("BRONZE", (0.70, 0.50, 0.20), 0), ("NEMA17", (0.15, 0.15, 0.17), 0), ("SERVO_MG996R", (0.10, 0.20, 0.60), 0),
    ("SERVO_HORN", (0.92, 0.92, 0.92), 0), ("BEARING", (0.70, 0.70, 0.72), 0), ("SHAFT", (0.60, 0.60, 0.62), 0),
    ("MAGNET", (0.85, 0.10, 0.10), 0), ("GRAIL_PLATE", (0.40, 0.40, 0.40), 0), ("GRAIL", (0.95, 0.75, 0.10), 0),
    ("SCR_", (0.22, 0.22, 0.25), 0), ("NUT_", (0.70, 0.70, 0.72), 0), ("TNUT_", (0.55, 0.55, 0.60), 0),
    ("INSERT_", (0.80, 0.65, 0.20), 0), ("M5x25_SCREWS", (0.22, 0.22, 0.25), 0), ("M5_NYLOC", (0.70, 0.70, 0.72), 0),
    ("CTX_ROOF", (0.85, 0.85, 0.70), 60),
    ("B330_plate", (0.82, 0.70, 0.50), 0), ("B330_wheels_JS7444_ENVELOPE", (1.0, 0.6, 0.6), 80),
    ("B330_wheels", (0.25, 0.15, 0.12), 0), ("B330_motors", (0.55, 0.55, 0.58), 0), ("B330_hinges", (0.30, 0.30, 0.35), 0),
    ("B330_odo", (0.15, 0.35, 0.80), 0), ("B330_amt", (0.10, 0.55, 0.20), 0), ("B330_dead_wheel", (0.10, 0.10, 0.10), 0),
    ("B330_clapets", (0.70, 0.70, 0.72), 70), ("B330_ball", (0.45, 0.45, 0.50), 0), ("B330_", (0.60, 0.60, 0.62), 0),
]


def colour(doc):
    """GUI only: colours by part, ghosts (place pose) see-through, everything visible."""
    for o in doc.Objects:
        vo = getattr(o, "ViewObject", None)
        if vo is None:
            continue
        vo.Visibility = True
        if o.TypeId != "Part::Feature":
            continue
        name = o.Name
        ghost = name.startswith("PLACE_")
        key = name[6:] if ghost else name
        for pre, rgb, tr in COLOURS:
            if key.startswith(pre):
                vo.ShapeColor = rgb
                vo.Transparency = 70 if ghost else tr
                break
        else:
            vo.Transparency = 70 if ghost else 0


_LAUNCHED = any(os.path.basename(str(a)).lower() == "flipper_fc.py" for a in sys.argv)
if App.GuiUp and _LAUNCHED:
    import FreeCADGui as Gui
    from PySide import QtCore

    def _gui_run():
        try:
            main()
            v = Gui.activeDocument().activeView()
            v.viewIsometric()
            v.fitAll()
            App.ActiveDocument.save()
        except Exception:
            import traceback
            with open(os.path.join(C.CAD, "flipper_gui_error.txt"), "w") as f:
                f.write(traceback.format_exc())
        Gui.getMainWindow().close()

    QtCore.QTimer.singleShot(1500, _gui_run)
else:
    main()
