# layout_fc.py - ROBOT LAYOUT v1 (Seif, 2026-11-13): where every mechanism sits, with the rule checks.
#   Front = clapets v7 module (real parts, from the v7 FCStd, in each pose), sitting ON the robot floor:
#           FRONT_MOD "AB" = lift + doors + suction head, "B" = lift + suction head only (no door units).
#   Back  = BACK_MODE: "mirror" (a 2nd copy of the front module), "flip6" (Ayoub's 6-cup flip, simplified),
#           "simple" (pick without turning, a reserved box).
#   Right = Grail pickup (lift + roof spot), Left = cannonball launcher, middle = drive (JSUMO JS7444 + Pololu 37D),
#   floor (chamfered corners) + ball transfers (2 on the axis or 4 in the corners), electronics, battery, pumps,
#   roof (L4), beacon support, e-stop.
# Run (headless, a few min), from mechanical/layout-v1/:
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/layout_fc.py
#   Options (set before the command, Windows: set NAME=value &):
#     LAYOUT_FRONT_MOD=AB|B   LAYOUT_BACK=mirror|flip6|simple   LAYOUT_CHAMFER=30   LAYOUT_CASTERS=4|2
#     LAYOUT_HALF_W, LAYOUT_FRONT, LAYOUT_BACK_FACE (body size)   LAYOUT_MODULE_Z (module raise, default: socle on the floor)
# Output: CAD/LAYOUT_<front>_<back>.FCStd, report_<front>_<back>.txt (perimeters + chamfer sweep, height, start
#   area, casters, overlaps between reserved volumes and the real module parts in every pose).
# Frame (mm): X right, Y forward (front face = stack face), Z up, Z 0 = table; origin = robot centre = drive axle.
import math, os, re

import FreeCAD as App
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
V7 = os.path.normpath(os.path.join(ROOT, "..", "clapets-v7", "CAD_FC", "MODULE_CLAPETS_V7.FCStd"))
ENV = os.environ.get
FRONT_MOD = ENV("LAYOUT_FRONT_MOD", "AB").upper()
BACK_MODE = ENV("LAYOUT_BACK", "mirror")
TAG = "%s_%s" % (FRONT_MOD, BACK_MODE)
assert FRONT_MOD in ("AB", "B") and BACK_MODE in ("mirror", "flip6", "simple")


# ============================================================================================ module (v7)
def is_door_part(lab, grp):
    """Door units and everything that only serves the doors (dropped in the 'B only' module)."""
    if grp.startswith(("door_", "pinion_")):
        return True
    if grp != "carriage":
        return False
    base = lab.rsplit("-", 1)[0]
    if base.startswith(("A_AILE", "A_CAPOT_AILE", "FIX_VIS_AILE", "FIX_ECROU_AILE")):
        return True
    if base == "REF_608ZZ":                       # door hinge bearings (the head ones are REF_608ZZ_TETE)
        return True
    return bool(re.search(r"_(D|G)$", base))      # door servos + their wires (REF_MG996R_D, REF_FIL_*_G ...)


def say(*a):
    print("[layout]", *a, flush=True)


say("loading v7")
v7 = App.openDocument(V7)
MOD_ALL = [(o.Label, o.MotionGroup, o.Placement, o.Shape.copy())
           for o in v7.Objects if o.TypeId == "Part::Feature" and getattr(o, "MotionGroup", "") not in ("", "stack", "reserve")]
STACK = [o.Shape.copy() for o in v7.Objects if getattr(o, "MotionGroup", "") == "stack"]
App.closeDocument(v7.Name)
MOD = [m for m in MOD_ALL if FRONT_MOD == "AB" or not is_door_part(m[0], m[1])]
DROPPED = [m[0] for m in MOD_ALL if FRONT_MOD == "B" and is_door_part(m[0], m[1])]
SOCLE_Z0 = min(m[3].BoundBox.ZMin for m in MOD_ALL if m[0].startswith("A_SOCLE"))
NEMA_BB = [m[3].BoundBox for m in MOD_ALL if m[0].startswith("REF_NEMA17")][0]


# ============================================================================================ parameters
class P:
    # ---- floor + casters (KSM15-FL ball transfers: 21 mm from the ball bottom to the body top)
    FLOOR_Z0, FLOOR_T = 21.0, 5.0  # floor plate z 21..26
    CASTER_D, CASTER_H = 24.0, 21.0   # body Ø ASSUMED (to measure)
    CASTERS = int(ENV("LAYOUT_CASTERS", "4"))   # 4 = one per corner (inside the chamfer), 2 = on the Y axis
    CASTER_CLEAR = 4.0             # caster body -> chamfer edge / body side
    # ---- module on the floor: socle bottom on the floor top
    MODULE_Z = float(ENV("LAYOUT_MODULE_Z", FLOOR_Z0 + FLOOR_T - SOCLE_Z0))
    # ---- drive (D-004): JSUMO JS7444 74 mm (width 44 ASSUMED from the name, to measure), Pololu 37D (#4742)
    WHEEL_D, WHEEL_W = 74.0, 44.0
    MOTOR_D, MOTOR_L = 37.0, 68.0  # 37D x 68 L (the encoder version is 68 L; #4742 has no encoder: shorter)
    MOTOR_GAP = 6.0                # wheel inner face -> gearbox face (shaft + hub + bracket)
    # ---- body. AB: the v7 door units fix the width (x ±150) and the front (wheels clear the door units).
    #      B: the drive fixes the width (2 x (wheel + gap + motor) + 4 = 240); the front is set so the lift NEMA
    #      (it goes through the floor) clears the drive motors in Y.
    HALF_W = float(ENV("LAYOUT_HALF_W", 150.0 if FRONT_MOD == "AB" else WHEEL_W + MOTOR_GAP + MOTOR_L + 2.0))
    FRONT = float(ENV("LAYOUT_FRONT", 146.0 if FRONT_MOD == "AB" else round(140.0 - NEMA_BB.YMin + MOTOR_D / 2 + 2.0, 1)))
    BACK = float(ENV("LAYOUT_BACK_FACE", {"mirror": FRONT, "flip6": 140.0, "simple": 110.0}[BACK_MODE]))
    CHAMFER = float(ENV("LAYOUT_CHAMFER", "30"))   # 45° chamfer on the 4 body corners (leg length)
    CHAMFER_SWEEP = (0, 20, 30, 40, 50, 60)
    # ---- reserved volumes
    SIDE_BAY_X = 66.0 if FRONT_MOD == "AB" else 76.0    # AB: door units from x 66; B: V-wheel bolts at x 73
    ROOF_Z, ROOF_T = 300.0, 6.0    # L4: Grail on our roof > 300 mm (G E.2)
    GRAIL = 70.0                   # Grail: > 60 mm cube (G E.2); 70 x 70 x 100 assumed
    GRAIL_H = 100.0
    BEACON_D, BEACON_TOP = 80.0, 430.0   # support Ø ≥ 70, <= 100 x 100, top 430 ± 5, full from 350 (GR F.6)
    ESTOP_D, ESTOP_TOP = 40.0, 360.0     # red, Ø ≥ 20, top <= 375 (GR F.4.c)
    LIDAR_IN_MAST = True           # LD06-class LiDAR inside the beacon support (GR F.6 allows sensors in the support)


S = P.HALF_W
FR, BK = P.FRONT, P.BACK
MZ = P.MODULE_Z
OFF = FR - 140.0                   # module y -> robot Y (front module)
WR = P.WHEEL_D / 2
WX0 = S - P.WHEEL_W
MX1 = WX0 - P.MOTOR_GAP
MX0 = MX1 - P.MOTOR_L
FZ1 = P.FLOOR_Z0 + P.FLOOR_T
# limits of the volumes between the front and back mechanisms (module y -> robot Y)
SIDE_Y1 = OFF + (34.0 if FRONT_MOD == "AB" else 46.0)   # AB: door units from y 34; B: butterfly plate at y 47.5
CORE_Y1 = OFF + 12.0                                     # V-wheel bolts of the lift at y ~13
ROOF_Y1 = OFF + 32.0                                     # roof strip up to the lift (rails pass through cut-outs)
if BACK_MODE == "mirror":
    SIDE_Y0, CORE_Y0, ROOF_Y0 = -(BK - 140 + (SIDE_Y1 - OFF)), -(BK - 140 + 12.0), -(BK - 140 + 32.0)
else:
    SIDE_Y0, CORE_Y0, ROOF_Y0 = -40.0, -min(CORE_Y1, 18.0), -min(ROOF_Y1, 38.0)


def body_poly(c):
    """Body outline (top view), counter-clockwise, 45° chamfers of leg c on the 4 corners."""
    x0, x1, y0, y1 = -S, S, -BK, FR
    if c <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def body_prism(c):
    pl = body_poly(c)
    w = Part.makePolygon([Vector(x, y, -50) for x, y in pl] + [Vector(pl[0][0], pl[0][1], -50)])
    return Part.Face(w).extrude(Vector(0, 0, 700))


def caster_xy(c):
    r = P.CASTER_D / 2 + P.CASTER_CLEAR
    if P.CASTERS == 2:
        return [(0, FR - 26.0), (0, -(BK - 26.0))]
    d = max(r, (c + r * math.sqrt(2)) / 2)          # inset from both sides: clears the chamfer edge by CASTER_CLEAR
    return [(sx * (S - d), y) for sx in (1, -1) for y in (FR - d, -(BK - d))]


def make(spec):
    t = spec[0]
    if t == "box":
        _, x0, x1, y0, y1, z0, z1 = spec
        return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))
    if t == "cylx":
        _, x0, x1, y, z, r = spec
        a, b = min(x0, x1), max(x0, x1)
        return Part.makeCylinder(r, b - a, Vector(a, y, z), Vector(1, 0, 0))
    if t == "cyly":
        _, x, y0, y1, z, r = spec
        a, b = min(y0, y1), max(y0, y1)
        return Part.makeCylinder(r, b - a, Vector(x, a, z), Vector(0, 1, 0))
    if t == "cylz":
        _, x, y, z0, z1, r = spec
        return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0), Vector(0, 0, 1))


def nema_cutouts():
    """Floor holes for the lift NEMA, which hangs below the socle (front, and back if mirrored)."""
    bb, out = NEMA_BB, []
    ys = [(bb.YMin + OFF, bb.YMax + OFF)]
    if BACK_MODE == "mirror":
        ys.append((-(bb.YMax + BK - 140), -(bb.YMin + BK - 140)))
    for y0, y1 in ys:
        out.append(Part.makeBox(bb.XLength + 4, y1 - y0 + 4, 20, Vector(bb.XMin - 2, y0 - 2, 15)))
    return out


def build(c):
    """Blocks (name: (kind, spec, note)) and their shapes for a chamfer c."""
    B = {}

    def box(name, x0, x1, y0, y1, z0, z1, kind="res", note=""):
        B[name] = (kind, ("box", x0, x1, y0, y1, z0, z1), note)

    for s, side in ((1, "R"), (-1, "L")):
        B["WHEEL_" + side] = ("real", ("cylx", s * WX0, s * S, 0, WR, WR), "JSUMO JS7444 Ø74 (width assumed 44)")
        B["DRIVE_MOTOR_" + side] = ("real", ("cylx", s * MX0, s * MX1, 0, WR, P.MOTOR_D / 2), "Pololu 37D, 37 x 68")
    for i, (x, y) in enumerate(caster_xy(c)):
        B["CASTER_%d" % (i + 1)] = ("real", ("cylz", x, y, 0, P.CASTER_H, P.CASTER_D / 2), "KSM15-FL ball transfer")
    box("FLOOR", -S, S, -BK, FR, P.FLOOR_Z0, FZ1, kind="real", note="floor plate, chamfered, cut-outs below")
    X = P.SIDE_BAY_X
    box("SHOOTER_L", -S, -X, SIDE_Y0, SIDE_Y1, WR * 2 + 4, P.ROOF_Z, note="cannonball launcher + magazine (left)")
    box("GRAIL_LIFT_R", X, S, SIDE_Y0, SIDE_Y1, WR * 2 + 4, P.ROOF_Z, note="Grail pickup + lift to the roof (right)")
    box("CORE", -X + 2, X - 2, CORE_Y0, CORE_Y1, 60 + MZ, P.ROOF_Z, note="centre slab: battery + electronics + pumps")
    box("ROOF", -S, S, ROOF_Y0, ROOF_Y1, P.ROOF_Z, P.ROOF_Z + P.ROOF_T, kind="real",
        note="L4 roof strip between the 2 lifts (cut-outs for the rails)")
    G = P.GRAIL
    box("GRAIL_ON_ROOF", S - G - 5, S - 5, -G / 2, G / 2, P.ROOF_Z + P.ROOF_T, P.ROOF_Z + P.ROOF_T + P.GRAIL_H,
        note="Grail at L4 (may pass 350 in the castle, G E.1; FAQ Q8)")
    B["BEACON_SUPPORT"] = ("real", ("cylz", 0, 0, 350, P.BEACON_TOP, P.BEACON_D / 2), "GR F.6, on a bridge over the 2 top ties")
    B["ESTOP"] = ("real", ("cylz", -S + 35, 0, P.ROOF_Z + P.ROOF_T, P.ESTOP_TOP, P.ESTOP_D / 2), "GR F.4.c, on the roof strip, left")
    if P.LIDAR_IN_MAST:
        B["LIDAR_IN_MAST"] = ("res", ("cylz", 0, 0, 375, 410, 20), "LD06-class inside the beacon support (GR F.6)")
    if BACK_MODE == "flip6":      # Ayoub's flip-6cups, simplified (mechanical/flip-6cups/fc/flip6_params.py)
        box("BACK_FLIP6_LINKS", -145, 145, -BK, -BK + 30, 20, 330, note="column + crank/rocker + cup plate (plate turns in XZ: ±145)")
        B["BACK_FLIP6_MOTOR"] = ("res", ("cyly", -35, -BK + 30, -BK + 107, 50, 18.5), "JGB37-520 on the crank, 77 long")
        B["BACK_FLIP6_PUMPS"] = ("res", ("box", -110, 110, -BK + 30, -BK + 70, 120, 240), "6 pumps + 6 valves (Ayoub: one per cup)")
    elif BACK_MODE == "simple":
        box("BACK_SIMPLE_PICK", -120, 120, -BK, -BK + 70, 30, 330, note="pick without turning (suction plate + small lift), 70 deep")
    if BACK_MODE != "mirror":      # what is left behind the back mechanism, down to the side bays
        yb = -BK + (107 if BACK_MODE == "flip6" else 70)
        if yb < SIDE_Y0 - 5:
            box("FREE_BACK", -S, S, yb, SIDE_Y0, FZ1, 350, note="free: battery, pumps, electronics, more")

    body = body_prism(c)
    SH = {}
    for n, (k, spec, note) in B.items():
        sh = make(spec)
        if n == "FLOOR":
            for cut in nema_cutouts():
                sh = sh.cut(cut)
            for s in (1, -1):   # wheel + drive motor slots
                x0, x1 = sorted((s * (MX0 - 3), s * (S + 1)))
                sh = sh.cut(Part.makeBox(x1 - x0, 2 * (P.MOTOR_D / 2 + 3), 20, Vector(x0, -(P.MOTOR_D / 2 + 3), 15)))
                x0, x1 = sorted((s * (WX0 - 3), s * (S + 1)))
                sh = sh.cut(Part.makeBox(x1 - x0, 2 * (WR + 5), 20, Vector(x0, -(WR + 5), 15)))
        if spec[0] == "box":
            sh = sh.common(body)   # every box follows the chamfered outline
        SH[n] = sh
    return B, SH


GRAIL_START = ("box", S + 5, S + 5 + P.GRAIL, -P.GRAIL / 2, P.GRAIL / 2, 0, P.GRAIL_H)   # right of the robot, on the floor

# ============================================================================================ module poses
PX, PY, SVY, HZ = 131.0, 82.0, 52.0, 165.0
HGC, HS_ANG = 31.25, 25.0
HS_X = -HGC * math.sin(math.radians(HS_ANG)); HS_Z = HZ - HGC * math.cos(math.radians(HS_ANG))
EXEMPT = ("REF_RAIL", "A_TRAVERSE_HAUT", "REF_VIS_T8", "FIX_TNUT_RAILS", "FIX_VIS_RAILS")   # cut to length on the robot
POSES = {"start_folded": (0, 90.0, 0), "approach_open": (0, -30.0, 0), "clamp": (0, 3.0, 0),
         "open_release": (0, -38.0, 0), "lift75_turn90": (75, -38.0, 90)}
if FRONT_MOD == "B":     # no doors: only the lift and the head move
    POSES = {"start": (0, 90.0, 0), "lift15_carry": (15, 90.0, 0), "lift75_turn90": (75, 90.0, 90)}


def mod_pl(base, grp, h, a, ph):
    lift = App.Placement(Vector(0, 0, h), App.Rotation())
    if grp == "fixed":
        return base
    if grp in ("carriage", "reserve"):
        return lift.multiply(base)
    if grp.startswith("door_"):
        s = 1 if grp.endswith("D") else -1
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), s * a), Vector(s * PX, PY, 0))).multiply(base)
    if grp.startswith("pinion_"):
        s = 1 if grp.endswith("D") else -1
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), -s * 1.4 * a), Vector(s * PX, SVY, 0))).multiply(base)
    if grp == "hpinion":
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), -1.5 * ph), Vector(HS_X, 0, HS_Z))).multiply(base)
    if grp == "head":
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), ph), Vector(0, 0, HZ))).multiply(base)
    return base


FRONT_PL = App.Placement(Vector(0, OFF, MZ), App.Rotation())
BACK_PL = App.Placement(Vector(0, 0, MZ), App.Rotation(Vector(0, 0, 1), 180)).multiply(
    App.Placement(Vector(0, BK - 140, 0), App.Rotation()))
back_is_module = BACK_MODE == "mirror"
SIDES = ["F"] + (["B"] if back_is_module else [])


def module_shapes(pose, where):
    h, a, ph = POSES[pose]
    out = []
    for lab, grp, base, sh in MOD:
        s = sh.copy()
        s.Placement = (FRONT_PL if where == "F" else BACK_PL).multiply(mod_pl(base, grp, h, a, ph))
        out.append((lab, s))
    return out


# ============================================================================================ geometry helpers
def hull2(pts):
    p = sorted(set((round(q[0], 2), round(q[1], 2)) for q in pts))
    cr = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0: lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0: up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def perim(poly):
    return sum(math.hypot(poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]) for i in range(len(poly)))


def pts2(shape):
    pts = [(v.Point.x, v.Point.y) for v in shape.Vertexes]
    for e in shape.Edges:
        try:
            pts += [(p.x, p.y) for p in e.discretize(Number=16)]
        except Exception:
            pass
    return pts


def outside_dist(pt, poly):
    """How far a point is outside a convex CCW polygon (<= 0 inside)."""
    d = -1e9
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i - 1], poly[i]
        ex, ey = bx - ax, by - ay
        d = max(d, -(ex * (pt[1] - ay) - ey * (pt[0] - ax)) / math.hypot(ex, ey))
    return d


say("module poses")
MOD_SHAPES = {(side, pose): module_shapes(pose, side) for side in SIDES for pose in POSES}
MOD_PTS = {}
for key, lst in MOD_SHAPES.items():
    MOD_PTS[key] = []
    for lab, s in lst:
        MOD_PTS[key] += pts2(s)
START = list(POSES)[0]


def perimeters(block_pts):
    """(start perimeter, hull) and the worst deployed perimeter with one module working / both working."""
    def per(fp, bp):
        pts = block_pts + MOD_PTS[("F", fp)] + (MOD_PTS[("B", bp)] if back_is_module else [])
        hl = hull2(pts)
        return perim(hl), hl
    p0, h0 = per(START, START)
    rows, w1, w2 = [], (0, ""), (0, "")
    for fp in POSES:
        for bp in (POSES if back_is_module else [START]):
            pp, _ = per(fp, bp)
            tag = "front %s / back %s" % (fp, bp) if back_is_module else "front %s" % fp
            one = fp == START or bp == START
            if one:
                rows.append((tag, pp))
                if pp > w1[0]:
                    w1 = (pp, tag)
            if pp > w2[0]:
                w2 = (pp, tag)
    return p0, h0, rows, w1, w2


# ============================================================================================ chamfer sweep
L = []
L.append("ROBOT LAYOUT v1 - front module: %s, back: %s   (mechanical/layout-v1/fc/layout_fc.py)" % (FRONT_MOD, BACK_MODE))
L.append("Body X ±%.1f, front face Y +%.1f, back face Y -%.1f -> %.1f x %.1f, corner chamfers %.0f, %d casters" % (
    S, FR, BK, 2 * S, FR + BK, P.CHAMFER, P.CASTERS))
L.append("Module raised %.1f mm: socle on the floor top (z %.1f). Module y 140 (stack face) = robot Y %+.1f." % (MZ, FZ1, FR))
if DROPPED:
    L.append("Module B only: %d door parts removed (%s)" % (len(DROPPED), ", ".join(sorted(set(d.rsplit('-', 1)[0] for d in DROPPED)))))
L.append("")
L.append("== Chamfer sweep: perimeter vs corner chamfer (carried stones not counted: FAQ Q1) [GR F.3]")
L.append("   chamfer   start (<=1200)   deployed, one module working (<=1400)")
sweep = {}
for c in sorted(set(P.CHAMFER_SWEEP) | {P.CHAMFER}):
    say("chamfer", c)
    _, sh = build(c)
    bp = []
    for s in sh.values():
        bp += pts2(s)
    p0, _, _, w1, _ = perimeters(bp)
    sweep[c] = (p0, w1[0])
    L.append("   %5.0f     %7.1f (%+6.1f)   %7.1f (%+6.1f)%s" % (c, p0, 1200 - p0, w1[0], 1400 - w1[0],
             "   <- used below" if c == P.CHAMFER else ""))
L.append("   (gain of a chamfer c on a plain box = 2.34 c; less when module parts fill the corner, see below)")
L.append("")

BLOCKS, BLOCK_SHAPES = build(P.CHAMFER)
BLOCK_PTS = []
for sh in BLOCK_SHAPES.values():
    BLOCK_PTS += pts2(sh)
P0, H0, ROWS, W1, W2 = perimeters(BLOCK_PTS)
xs = [p[0] for p in H0]; ys = [p[1] for p in H0]

L.append("== Perimeter with chamfer %.0f" % P.CHAMFER)
L.append("  start                                     %7.1f  (limit 1200, margin %+.1f)  hull X %.1f..%.1f Y %.1f..%.1f" % (
    P0, 1200 - P0, min(xs), max(xs), min(ys), max(ys)))
for tag, pp in ROWS:
    L.append("  %-42s %7.1f  (limit 1400, margin %+.1f)" % (tag, pp, 1400 - pp))
L.append("  worst with ONE module working (other at start): %.1f (%s)" % W1)
if back_is_module:
    L.append("  worst with BOTH modules working at once:        %.1f (%s)  -> never allowed if > 1400" % W2)
poly = body_poly(P.CHAMFER)
outs = {}
for side in SIDES:
    for lab, s in MOD_SHAPES[(side, START)]:
        d = max(outside_dist(p, poly) for p in pts2(s))
        if d > 0.5:
            outs["%s:%s" % (side, lab.rsplit("-", 1)[0])] = d
L.append("  module parts outside the chamfered body at start (they set the hull, not the floor): %s" % (
    ", ".join("%s %.1f" % (k, v) for k, v in sorted(outs.items(), key=lambda kv: -kv[1])) if outs else "none"))
L.append("")

L.append("== Start area 500 x 500 with the Grail on the floor at the right [G D.3, G E.2]")
gx1 = GRAIL_START[2]
ext_x = max(max(xs), gx1) - min(xs)
ext_y = max(ys) - min(ys)
L.append("  robot + Grail: %.1f (X) x %.1f (Y) -> %s (Grail %s x %s, 5 mm from the body)" % (
    ext_x, ext_y, "fits" if ext_x <= 500 and ext_y <= 500 else "DOES NOT FIT", P.GRAIL, P.GRAIL))
L.append("")

L.append("== Casters (KSM15-FL, Ø%.0f assumed) and support polygon" % P.CASTER_D)
cxy = caster_xy(P.CHAMFER)
L.append("  casters at " + ", ".join("(%.1f, %.1f)" % p for p in cxy))
L.append("  drive wheel contacts at (±%.1f, 0)" % (S - P.WHEEL_W / 2))
L.append("  support polygon: X ±%.1f, Y %.1f..%.1f; carried stack centre at Y %+.1f (%.1f mm %s the front support line)" % (
    max(abs(p[0]) for p in cxy + [(S - P.WHEEL_W / 2, 0)]), min(p[1] for p in cxy), max(p[1] for p in cxy),
    FR + 55, abs(FR + 55 - max(p[1] for p in cxy)), "beyond" if FR + 55 > max(p[1] for p in cxy) else "inside"))
if P.CASTERS == 4:
    L.append("  6 contact points: the drive wheels need a sprung mount (or casters ~1 mm above the wheel line)")
L.append("")

L.append("== Height [GR F.3: <= 350; beacon support top 430 ± 5 GR F.6; e-stop <= 375 GR F.4.c]")
L.append("   Profiles, top tie, lead screw, T-nuts, rail screws are exempt here (cut to length on the robot).")
over = {}
for pose in POSES:
    zr = 0
    for lab, s in MOD_SHAPES[("F", pose)]:
        z = s.BoundBox.ZMax
        if lab.startswith(EXEMPT):
            zr = max(zr, z)
        elif z > 350.0:
            over.setdefault(lab.rsplit("-", 1)[0], {})[pose] = z
    zm = max(s.BoundBox.ZMax for lab, s in MOD_SHAPES[("F", pose)] if not lab.startswith(EXEMPT))
    L.append("  module %-16s max %.1f; profiles / top tie / lead screw %.1f (cut on the robot)" % (pose, zm, zr))
if over:
    L.append("  ! moving parts over 350 (NOT trimmable; Seif fixes it in the module B rework):")
    for lab, d in sorted(over.items(), key=lambda kv: -max(kv[1].values())):
        L.append("      %-26s %s" % (lab, ", ".join("%s %.1f" % (p, z) for p, z in d.items())))
L.append("  cups (v7 head, z 85/165/245 above the table by design) now at z %.0f/%.0f/%.0f: %.0f mm above the stone"
         " centres -> the head must come down %.0f mm relative to the socle (module B rework)" % (85 + MZ, 165 + MZ, 245 + MZ, MZ, MZ))
nb = NEMA_BB
L.append("  lift NEMA hangs %.1f below the socle: bottom at z %.1f on the robot -> floor cut-out (done), %.1f mm above the table" % (
    SOCLE_Z0 - nb.ZMin, nb.ZMin + MZ, nb.ZMin + MZ))
for n, sh in BLOCK_SHAPES.items():
    z = sh.BoundBox.ZMax
    lim = 435 if n.startswith(("BEACON", "LIDAR")) else 375 if n == "ESTOP" else 350
    if n == "GRAIL_ON_ROOF":
        lim = 1e9
    if z > lim:
        L.append("  ! %s top %.1f > %s" % (n, z, lim))
L.append("  blocks: all within their limits unless listed above (Grail on the roof: see FAQ Q8)")
L.append("")

say("overlaps")
L.append("== Overlaps: reserved volumes / known parts vs the real v7 module parts, every pose (> 1 mm3)")
L.append("   (E) = expected, see the note; everything else is a real conflict to solve")
hits = {}
for pose in POSES:
    for side in SIDES:
        for lab, s in MOD_SHAPES[(side, pose)]:
            bb = s.BoundBox
            for n, bs in BLOCK_SHAPES.items():
                if not bb.intersect(bs.BoundBox):
                    continue
                try:
                    v = s.common(bs).Volume
                except Exception:
                    v = 0
                if v > 1.0:
                    hits.setdefault((n, side, lab), []).append((pose, v))
if not hits:
    L.append("  none")
by_block = {}
for (n, side, lab), lst in sorted(hits.items()):
    by_block.setdefault(n, []).append("%s:%s [%s]" % (side, lab, ", ".join("%s %.0f" % (p, v) for p, v in lst)))
EXPECTED = {"BEACON_SUPPORT": "(E) top ties + lead screws cut to <= 350 on the robot; the support sits on a bridge over them",
            "ROOF": "(E) rails + lead screws pass through the roof strip: cut-outs",
            "LIDAR_IN_MAST": "(E) same as the beacon support"}
for n, items in by_block.items():
    L.append("  %s (%s): %d part(s)  %s" % (n, BLOCKS[n][2], len(items), EXPECTED.get(n, "")))
    for it in items[:12]:
        L.append("      " + it)
    if len(items) > 12:
        L.append("      ... %d more" % (len(items) - 12))
L.append("")
L.append("== Overlaps between blocks (> 1 mm3)")
names = list(BLOCK_SHAPES)
bh = 0
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = BLOCK_SHAPES[names[i]], BLOCK_SHAPES[names[j]]
        if not a.BoundBox.intersect(b.BoundBox):
            continue
        v = a.common(b).Volume
        if v > 1.0 and {names[i], names[j]} != {"BEACON_SUPPORT", "LIDAR_IN_MAST"}:
            bh += 1
            L.append("  %s x %s: %.0f mm3" % (names[i], names[j], v))
if bh == 0:
    L.append("  none")
L.append("")
L.append("== Reserved volumes (mm)")
for n, (k, spec, note) in BLOCKS.items():
    bb = BLOCK_SHAPES[n].BoundBox
    L.append("  %-18s %-4s X %7.1f..%-7.1f Y %7.1f..%-7.1f Z %6.1f..%-6.1f %5.2f L  %s" % (
        n, k, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, BLOCK_SHAPES[n].Volume / 1e6, note))

rep = os.path.join(ROOT, "report_%s.txt" % TAG)
open(rep, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ============================================================================================ FCStd to look at
os.makedirs(os.path.join(ROOT, "CAD"), exist_ok=True)
doc = App.newDocument("LAYOUT")
gm = doc.addObject("App::DocumentObjectGroup", "Front_module_v7_%s_start" % FRONT_MOD)
for lab, s in MOD_SHAPES[("F", START)]:
    o = doc.addObject("Part::Feature", "F_" + lab); o.Shape = s; gm.addObject(o)
if back_is_module:
    gb = doc.addObject("App::DocumentObjectGroup", "Back_module_v7_%s_start" % FRONT_MOD)
    for lab, s in MOD_SHAPES[("B", START)]:
        o = doc.addObject("Part::Feature", "B_" + lab); o.Shape = s; gb.addObject(o)
gr = doc.addObject("App::DocumentObjectGroup", "Reserved_volumes")
for n, sh in BLOCK_SHAPES.items():
    o = doc.addObject("Part::Feature", n); o.Shape = sh; gr.addObject(o)
o = doc.addObject("Part::Feature", "GRAIL_AT_START"); o.Shape = make(GRAIL_START)
for s in STACK:
    o = doc.addObject("Part::Feature", "REF_STACK_FRONT"); s2 = s.copy(); s2.Placement = App.Placement(Vector(0, OFF, 0), App.Rotation()).multiply(s.Placement); o.Shape = s2
hl = doc.addObject("Part::Feature", "HULL_START")
hl.Shape = Part.makePolygon([Vector(x, y, 0.5) for x, y in H0] + [Vector(H0[0][0], H0[0][1], 0.5)])
out = os.path.join(ROOT, "CAD", "LAYOUT_%s.FCStd" % TAG)
doc.saveAs(out)
print("->", out, rep)
