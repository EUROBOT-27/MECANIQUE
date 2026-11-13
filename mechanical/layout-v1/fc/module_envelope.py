# module_envelope.py - footprint (2D convex hull) + height of the clapets v7 module A+B in its key poses,
#   for the robot layout. No collision check, no motion study: one placement per pose (a few seconds).
# Run: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/module_envelope.py   (from mechanical/layout-v1/)
# Output: envelopes/clapets_v7_AB.json  (module frame: x right, y towards the stack, z 0 = table; y 140 = stack face)
import json, math, os
import FreeCAD as App
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FCSTD = os.path.normpath(os.path.join(HERE, "..", "..", "clapets-v7", "CAD_FC", "MODULE_CLAPETS_V7.FCStd"))
OUT = os.path.normpath(os.path.join(HERE, "..", "envelopes", "clapets_v7_AB.json"))

# same constants as clapets-v7/fc/motion_v7.py
PX, PY, SVY, HZ = 131.0, 82.0, 52.0, 165.0
HGC, HS_ANG = 31.25, 25.0
HS_X = -HGC * math.sin(math.radians(HS_ANG)); HS_Z = HZ - HGC * math.cos(math.radians(HS_ANG))
HEAD_RATIO, DOOR_RATIO = 30 / 20, 28 / 20
# rails, top tie, lead screw: height exempt in the v7 prototype (to be cut on the robot, top tie <= 350)
EXEMPT_HEIGHT = ("REF_RAIL", "A_TRAVERSE_HAUT", "REF_VIS_T8", "FIX_TNUT_RAILS", "FIX_VIS_RAILS")

POSES = {   # name: (lift mm, door deg, head deg)   door: +90 folded, +3 clamp, -30 approach, -38 open
    "start_folded": (0, 90.0, 0),
    "approach_open": (0, -30.0, 0),
    "clamp": (0, 3.0, 0),
    "open_release": (0, -38.0, 0),
    "open_lift75_turn90": (75, -38.0, 90),
}


def placement(base, grp, h, a, ph):
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
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 0, 1), -s * DOOR_RATIO * a), Vector(s * PX, SVY, 0))).multiply(base)
    if grp == "hpinion":
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), -HEAD_RATIO * ph), Vector(HS_X, 0, HS_Z))).multiply(base)
    if grp == "head":
        return lift.multiply(App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), ph), Vector(0, 0, HZ))).multiply(base)
    return base


def cloud(shape):
    pts = [v.Point for v in shape.Vertexes]
    for e in shape.Edges:
        try:
            pts += e.discretize(Number=12)
        except Exception:
            pass
    return pts


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


doc = App.openDocument(FCSTD)
objs = [o for o in doc.Objects if o.TypeId == "Part::Feature" and hasattr(o, "MotionGroup")]
local = {}
for o in objs:
    if o.MotionGroup in ("stack", "reserve"):
        continue
    inv = o.Placement.inverse()
    local[o.Name] = (o, [inv.multVec(p) for p in cloud(o.Shape)])

res = {"source": "mechanical/clapets-v7/CAD_FC/MODULE_CLAPETS_V7.FCStd", "frame": "x right, y towards the stack, z 0 = table; y 140 = stack face",
       "height_exempt": list(EXEMPT_HEIGHT), "poses": {}}
for name, (h, a, ph) in POSES.items():
    pts, zmax, zwho, zmax_all, zwho_all = [], -1e9, "", -1e9, ""
    ymin_who = (1e9, "")
    for nm, (o, cl) in local.items():
        pl = placement(o.Placement, o.MotionGroup, h, a, ph)
        wp = [pl.multVec(p) for p in cl]
        pts += [(p.x, p.y) for p in wp]
        zm = max(p.z for p in wp)
        if zm > zmax_all: zmax_all, zwho_all = zm, o.Label
        if not o.Label.startswith(EXEMPT_HEIGHT) and zm > zmax: zmax, zwho = zm, o.Label
        ym = min(p.y for p in wp)
        if ym < ymin_who[0]: ymin_who = (ym, o.Label)
    hl = hull2(pts)
    xs = [p[0] for p in hl]; ys = [p[1] for p in hl]
    res["poses"][name] = {"lift": h, "door": a, "head": ph, "hull": hl,
                          "bbox": [min(xs), max(xs), min(ys), max(ys)],
                          "ymin_part": ymin_who[1], "zmax": round(zmax, 1), "zmax_part": zwho,
                          "zmax_incl_exempt": round(zmax_all, 1), "zmax_incl_exempt_part": zwho_all}
    print("%-20s bbox x %.1f..%.1f y %.1f..%.1f (ymin %s)  zmax %.1f (%s)  incl rails %.1f" % (
        name, min(xs), max(xs), min(ys), max(ys), ymin_who[1], zmax, zwho, zmax_all))
json.dump(res, open(OUT, "w"), indent=1)
print("->", OUT)
