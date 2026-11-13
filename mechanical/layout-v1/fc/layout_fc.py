# layout_fc.py - ROBOT LAYOUT v1 (Seif, 2026-11-13): where every mechanism sits, with the rule checks.
#   Front = clapets v7 module A + B (real parts, from the v7 FCStd, in each pose).
#   Back  = BACK_MODE: "mirror" (a 2nd module A+B), "flip6" (Ayoub's 6-cup flip, simplified), "simple" (pick
#           without turning, a reserved box).
#   Right = Grail pickup (lift + roof spot), Left = cannonball launcher, middle = drive (JSUMO JS7444 + Pololu 37D),
#   floor + 2 ball transfers, electronics, battery, pumps, roof (L4), beacon support, e-stop.
# Run (headless, ~1 min), from mechanical/layout-v1/:
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/layout_fc.py
#   set LAYOUT_BACK=flip6 (or simple) before it to try another back module.
# Output: CAD/LAYOUT_<back>.FCStd (open it in FreeCAD to look), report_<back>.txt (perimeters, height, start area,
#   overlaps between reserved volumes and the real module parts in every pose).
# Frame (mm): X right, Y forward (front face = stack face), Z up, Z 0 = table; origin = robot centre = drive axle.
import json, math, os

import FreeCAD as App
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
V7 = os.path.normpath(os.path.join(ROOT, "..", "clapets-v7", "CAD_FC", "MODULE_CLAPETS_V7.FCStd"))
BACK_MODE = os.environ.get("LAYOUT_BACK", "mirror")


# ============================================================================================ parameters
class P:
    # ---- body
    HALF_W = 150.0                 # X ±150: the v7 door units reach x ±150 (outer walls)
    FRONT = 146.0                  # front face (= stack face, v7 y 140) at Y +146. Set by the drive (see report)
    BACK = float(os.environ.get("LAYOUT_BACK_FACE", {"mirror": 146.0, "flip6": 140.0, "simple": 110.0}[BACK_MODE]))
    # ---- drive (D-004): JSUMO JS7444 74 mm (width 44 ASSUMED from the name, to measure), Pololu 37D (#4742)
    WHEEL_D, WHEEL_W = 74.0, 44.0
    WHEEL_X1 = 150.0               # wheel outer face flush with the body side
    MOTOR_D, MOTOR_L = 37.0, 68.0  # 37D x 68 L (the encoder version is 68 L; #4742 has no encoder: shorter)
    MOTOR_GAP = 6.0                # wheel inner face -> gearbox face (shaft + hub + bracket)
    # ---- floor + casters (KSM15-FL ball transfers: 21 mm from the ball bottom to the body top)
    FLOOR_Z0, FLOOR_T = 21.0, 5.0  # floor plate z 21..26 (v7: the lowest moving part, door units, is at z 27)
    CASTER_D, CASTER_H = 24.0, 21.0   # body Ø ASSUMED (to measure)
    CASTER_Y = 120.0               # 2 casters on the Y axis at ±120 (front one) / back one at -(BACK - 26)
    # ---- reserved volumes (x0, x1, y0, y1, z0, z1)
    SIDE_BAY_X = 66.0              # side bays from |x| 66 (v7 door units start at x 66) to the body side
    SIDE_BAY_Y = 40.0              # between the front and back door units (they start at Y ±40 with FRONT 146)
    CORE_Y = 18.0                  # centre slab between the 2 lifts: |Y| < 18 (V-wheel bolts of the lifts at ~22)
    ROOF_Z, ROOF_T = 300.0, 6.0    # L4: Grail on our roof > 300 mm (G E.2)
    GRAIL = 70.0                   # Grail: > 60 mm cube (G E.2); 70 x 70 x 100 assumed
    GRAIL_H = 100.0
    BEACON_D, BEACON_TOP = 80.0, 430.0   # support Ø ≥ 70, ≤ 100 x 100, top 430 ± 5, full from 350 (GR F.6)
    ESTOP_D, ESTOP_TOP = 40.0, 360.0     # red, Ø ≥ 20, top ≤ 375 (GR F.4.c)
    LIDAR_IN_MAST = True           # LD06-class LiDAR inside the beacon support (Barbatronic 2027 does it); GR F.6 allows
                                   # sensors in the support, the cut for a rotating device < 2 cm tall and not see-through


S = P.HALF_W
FR, BK = P.FRONT, P.BACK
WR = P.WHEEL_D / 2
WX0 = P.WHEEL_X1 - P.WHEEL_W
MX1 = WX0 - P.MOTOR_GAP
MX0 = MX1 - P.MOTOR_L
FZ1 = P.FLOOR_Z0 + P.FLOOR_T

# name: (kind, shape spec, note)   kind: "real" (a part we know) or "res" (reserved volume)
BLOCKS = {}


def box(name, x0, x1, y0, y1, z0, z1, kind="res", note=""):
    BLOCKS[name] = (kind, ("box", x0, x1, y0, y1, z0, z1), note)


def cylx(name, x0, x1, y, z, r, kind="real", note=""):
    BLOCKS[name] = (kind, ("cylx", x0, x1, y, z, r), note)


def cylz(name, x, y, z0, z1, r, kind="real", note=""):
    BLOCKS[name] = (kind, ("cylz", x, y, z0, z1, r), note)


for s, side in ((1, "R"), (-1, "L")):
    cylx("WHEEL_" + side, s * WX0, s * P.WHEEL_X1, 0, WR, WR, note="JSUMO JS7444 Ø74 (width assumed 44)")
    cylx("DRIVE_MOTOR_" + side, s * MX0, s * MX1, 0, WR, P.MOTOR_D / 2, note="Pololu 37D, 37 x 68")
cylz("CASTER_F", 0, P.CASTER_Y, 0, P.CASTER_H, P.CASTER_D / 2, note="KSM15-FL ball transfer")
cylz("CASTER_B", 0, -(BK - 26), 0, P.CASTER_H, P.CASTER_D / 2, note="KSM15-FL ball transfer")
box("FLOOR", -S, S, -BK, FR, P.FLOOR_Z0, FZ1, kind="real", note="floor plate, cut-outs below")
B = P.SIDE_BAY_X
box("SHOOTER_L", -S, -B, -P.SIDE_BAY_Y, P.SIDE_BAY_Y, WR * 2 + 4, P.ROOF_Z, note="cannonball launcher + magazine (left)")
box("GRAIL_LIFT_R", B, S, -P.SIDE_BAY_Y, P.SIDE_BAY_Y, WR * 2 + 4, P.ROOF_Z, note="Grail pickup + lift to the roof (right)")
box("CORE", -B + 2, B - 2, -P.CORE_Y, P.CORE_Y, 60, P.ROOF_Z, note="centre slab: battery + electronics + pumps")
box("ROOF", -S, S, -38, 38, P.ROOF_Z, P.ROOF_Z + P.ROOF_T, kind="real", note="L4 roof strip between the 2 lifts (cut-outs for the rails)")
G = P.GRAIL
box("GRAIL_ON_ROOF", S - G - 5, S - 5, -G / 2, G / 2, P.ROOF_Z + P.ROOF_T, P.ROOF_Z + P.ROOF_T + P.GRAIL_H,
    note="Grail at L4 (may pass 350 in the castle, G E.1; FAQ Q8)")
cylz("BEACON_SUPPORT", 0, 0, 350, P.BEACON_TOP, P.BEACON_D / 2, note="GR F.6, on a bridge over the 2 top ties")
cylz("ESTOP", -S + 35, 0, P.ROOF_Z + P.ROOF_T, P.ESTOP_TOP, P.ESTOP_D / 2, note="GR F.4.c, on the roof strip, left")
if P.LIDAR_IN_MAST:
    cylz("LIDAR_IN_MAST", 0, 0, 375, 410, 20, kind="res", note="LD06-class inside the beacon support: allowed, opening < 2 cm tall, not see-through (GR F.6)")

if BACK_MODE == "flip6":      # Ayoub's flip-6cups, simplified (mechanical/flip-6cups/fc/flip6_params.py), face at -BK
    box("BACK_FLIP6_LINKS", -145, 145, -BK, -BK + 30, 20, 330, note="column + crank/rocker + cup plate (plate turns in XZ: ±145)")
    BLOCKS["BACK_FLIP6_MOTOR"] = ("res", ("cyly", -35, -BK + 30, -BK + 107, 50, 18.5), "JGB37-520 on the crank, 77 long")
    BLOCKS["BACK_FLIP6_PUMPS"] = ("res", ("box", -110, 110, -BK + 30, -BK + 70, 120, 240), "6 pumps + 6 valves (Ayoub: one per cup)")
elif BACK_MODE == "simple":
    box("BACK_SIMPLE_PICK", -120, 120, -BK, -BK + 70, 30, 330, note="pick without turning (suction plate + small lift), 70 deep")
if BACK_MODE != "mirror":      # what is left behind the back mechanism, down to the side bays
    yb = -BK + (107 if BACK_MODE == "flip6" else 70)
    if yb < -P.SIDE_BAY_Y - 5:
        box("FREE_BACK", -S, S, yb, -P.SIDE_BAY_Y, FZ1, 350, note="free: battery, pumps, electronics, more")

GRAIL_START = ("box", S + 5, S + 5 + G, -G / 2, G / 2, 0, P.GRAIL_H)   # at the right of the robot, on the floor


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


def floor_shape():
    f = make(BLOCKS["FLOOR"][1])
    cuts = []
    for s in (1, -1):   # wheel + drive motor slot
        x0, x1 = sorted((s * (MX0 - 3), s * (S + 1)))
        cuts.append(Part.makeBox(x1 - x0, 2 * (P.MOTOR_D / 2 + 3), 20, Vector(x0, -(P.MOTOR_D / 2 + 3), 15)))
        x0, x1 = sorted((s * (WX0 - 3), s * (S + 1)))
        cuts.append(Part.makeBox(x1 - x0, 2 * (WR + 5), 20, Vector(x0, -(WR + 5), 15)))
    for c in cuts:
        f = f.cut(c)
    return f


# ============================================================================================ module A+B (v7)
PX, PY, SVY, HZ = 131.0, 82.0, 52.0, 165.0
HGC, HS_ANG = 31.25, 25.0
HS_X = -HGC * math.sin(math.radians(HS_ANG)); HS_Z = HZ - HGC * math.cos(math.radians(HS_ANG))
EXEMPT = ("REF_RAIL", "A_TRAVERSE_HAUT", "REF_VIS_T8", "FIX_TNUT_RAILS", "FIX_VIS_RAILS")
POSES = {"start_folded": (0, 90.0, 0), "approach_open": (0, -30.0, 0), "clamp": (0, 3.0, 0),
         "open_release": (0, -38.0, 0), "lift75_turn90": (75, -38.0, 90)}


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


FRONT_PL = App.Placement(Vector(0, FR - 140, 0), App.Rotation())
BACK_PL = App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), 180)).multiply(App.Placement(Vector(0, BK - 140, 0), App.Rotation()))

v7 = App.openDocument(V7)
MOD = [(o.Label.rsplit("-", 1)[0], o.MotionGroup, o.Placement, o.Shape.copy())
       for o in v7.Objects if o.TypeId == "Part::Feature" and getattr(o, "MotionGroup", "") not in ("", "stack", "reserve")]
STACK = [o.Shape.copy() for o in v7.Objects if getattr(o, "MotionGroup", "") == "stack"]
App.closeDocument(v7.Name)


def module_shapes(pose, where):
    h, a, ph = POSES[pose]
    out = []
    for lab, grp, base, sh in MOD:
        s = sh.copy()
        s.Placement = (FRONT_PL if where == "F" else BACK_PL).multiply(mod_pl(base, grp, h, a, ph))
        out.append((lab, s))
    return out


# ============================================================================================ checks
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


BLOCK_SHAPES = {n: (floor_shape() if n == "FLOOR" else make(spec)) for n, (k, spec, note) in BLOCKS.items()}
BLOCK_PTS = []
for n, sh in BLOCK_SHAPES.items():
    BLOCK_PTS += pts2(sh)

back_is_module = BACK_MODE == "mirror"
pose_names = list(POSES)
mod_pts = {}
for pose in pose_names:
    mod_pts[("F", pose)] = []
    for lab, s in module_shapes(pose, "F"):
        mod_pts[("F", pose)] += pts2(s)
    if back_is_module:
        mod_pts[("B", pose)] = []
        for lab, s in module_shapes(pose, "B"):
            mod_pts[("B", pose)] += pts2(s)


def robot_perimeter(fp, bp):
    pts = BLOCK_PTS + mod_pts[("F", fp)]
    if back_is_module:
        pts += mod_pts[("B", bp)]
    hl = hull2(pts)
    return perim(hl), hl


L = []
L.append("ROBOT LAYOUT v1 - back module: %s   (mechanical/layout-v1/fc/layout_fc.py)" % BACK_MODE)
L.append("Body X ±%.0f, front face Y +%.0f, back face Y -%.0f -> box %.0f x %.0f (a plain box = perimeter %.0f)" % (
    S, FR, BK, 2 * S, FR + BK, 2 * (2 * S + FR + BK)))
L.append("")
L.append("== Perimeter (convex hull of the vertical projection, carried stones not counted: FAQ Q1) [GR F.3]")
P0, H0 = robot_perimeter("start_folded", "start_folded")
xs = [p[0] for p in H0]; ys = [p[1] for p in H0]
L.append("  start (doors folded)                      %7.1f  (limit 1200, margin %+.1f)  hull X %.1f..%.1f Y %.1f..%.1f" % (
    P0, 1200 - P0, min(xs), max(xs), min(ys), max(ys)))
worst1, worst2 = (0, ""), (0, "")
for fp in pose_names:
    for bp in (pose_names if back_is_module else ["start_folded"]):
        Pp, _ = robot_perimeter(fp, bp)
        tag = "front %s / back %s" % (fp, bp) if back_is_module else "front %s" % fp
        one_active = (fp == "start_folded" or bp == "start_folded")
        if one_active and Pp > worst1[0]:
            worst1 = (Pp, tag)
        if Pp > worst2[0]:
            worst2 = (Pp, tag)
        if one_active:
            L.append("  %-42s %7.1f  (limit 1400, margin %+.1f)" % (tag, Pp, 1400 - Pp))
L.append("  worst with ONE module working (other folded): %.1f (%s)" % worst1)
if back_is_module:
    L.append("  worst with BOTH modules working at once:      %.1f (%s)  -> never allowed if > 1400" % worst2)
L.append("")

L.append("== Start area 500 x 500 with the Grail on the floor at the right [G D.3, G E.2]")
gx0, gx1 = GRAIL_START[1], GRAIL_START[2]
ext_x = max(max(xs), gx1) - min(xs)
ext_y = max(ys) - min(ys)
L.append("  robot + Grail: %.1f (X) x %.1f (Y) -> %s (Grail %s x %s, 5 mm from the body)" % (
    ext_x, ext_y, "fits" if ext_x <= 500 and ext_y <= 500 else "DOES NOT FIT", P.GRAIL, P.GRAIL))
L.append("")

L.append("== Height [GR F.3: <= 350; beacon support top 430 ± 5 GR F.6; e-stop <= 375 GR F.4.c]")
for pose in pose_names:
    zm, who, zr = 0, "", 0
    for lab, s in module_shapes(pose, "F"):
        z = s.BoundBox.ZMax
        if lab.startswith(EXEMPT):
            zr = max(zr, z)
        elif z > zm:
            zm, who = z, lab
    L.append("  module %-16s max %.1f (%s); rails / top tie / lead screw %.1f (cut to <= 350 on the robot)" % (pose, zm, who, zr))
for n, sh in BLOCK_SHAPES.items():
    z = sh.BoundBox.ZMax
    lim = 435 if n.startswith(("BEACON", "LIDAR")) else 375 if n == "ESTOP" else 350
    if n == "GRAIL_ON_ROOF":
        lim = 1e9
    if z > lim:
        L.append("  ! %s top %.1f > %s" % (n, z, lim))
L.append("  blocks: all within their limits unless listed above (Grail on the roof: see FAQ Q8)")
L.append("")

L.append("== Overlaps: reserved volumes / known parts vs the real v7 module parts, every pose (> 1 mm3)")
L.append("   (E) = expected, see the note; everything else is a real conflict to solve")
hits = {}
for pose in pose_names:
    sides = ["F"] + (["B"] if back_is_module else [])
    for side in sides:
        for lab, s in module_shapes(pose, side):
            bb = s.BoundBox
            for n, bs in BLOCK_SHAPES.items():
                if n in ("BEACON_SUPPORT", "LIDAR_IN_MAST", "GRAIL_ON_ROOF") and pose != "lift75_turn90":
                    pass
                if not bb.intersect(bs.BoundBox):
                    continue
                try:
                    v = s.common(bs).Volume
                except Exception:
                    v = 0
                if v > 1.0:
                    key = (n, side, lab)
                    hits.setdefault(key, []).append((pose, v))
if not hits:
    L.append("  none")
by_block = {}
for (n, side, lab), lst in sorted(hits.items()):
    by_block.setdefault(n, []).append("%s:%s [%s]" % (side, lab, ", ".join("%s %.0f" % (p, v) for p, v in lst)))
EXPECTED = {"BEACON_SUPPORT": "(E) top ties + lead screws cut to <= 350 on the robot; the support sits on a bridge over them",
            "FLOOR": "(E) module A's socle + rails move up onto the floor (z 26); door sheet bottom z 20 -> floor cut-out or sheet from z 27",
            "ROOF": "(E) rails + lead screws pass through the roof strip: cut-outs"}
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

rep = os.path.join(ROOT, "report_%s.txt" % BACK_MODE)
open(rep, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ============================================================================================ FCStd to look at
os.makedirs(os.path.join(ROOT, "CAD"), exist_ok=True)
doc = App.newDocument("LAYOUT")
gm = doc.addObject("App::DocumentObjectGroup", "Front_module_v7_start")
for lab, s in module_shapes("start_folded", "F"):
    o = doc.addObject("Part::Feature", "F_" + lab); o.Shape = s; gm.addObject(o)
if back_is_module:
    gb = doc.addObject("App::DocumentObjectGroup", "Back_module_v7_start")
    for lab, s in module_shapes("start_folded", "B"):
        o = doc.addObject("Part::Feature", "B_" + lab); o.Shape = s; gb.addObject(o)
gr = doc.addObject("App::DocumentObjectGroup", "Reserved_volumes")
for n, sh in BLOCK_SHAPES.items():
    o = doc.addObject("Part::Feature", n); o.Shape = sh; gr.addObject(o)
o = doc.addObject("Part::Feature", "GRAIL_AT_START"); o.Shape = make(GRAIL_START)
for s in STACK:
    o = doc.addObject("Part::Feature", "REF_STACK_FRONT"); s2 = s.copy(); s2.Placement = FRONT_PL.multiply(s.Placement); o.Shape = s2
hl = doc.addObject("Part::Feature", "HULL_START")
hl.Shape = Part.makePolygon([Vector(x, y, 0.5) for x, y in H0] + [Vector(H0[0][0], H0[0][1], 0.5)])
out = os.path.join(ROOT, "CAD", "LAYOUT_%s.FCStd" % BACK_MODE)
doc.saveAs(out)
print("->", out, rep)
