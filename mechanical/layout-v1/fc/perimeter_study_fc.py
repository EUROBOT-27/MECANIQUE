# perimeter_study_fc.py - top views + perimeter checks of the layout v1 robot with the clapets modules open
#   (Maatoug, 2026-11-13). Reuses layout_fc.py's own geometry (same module poses, same body, same hull code) so the
#   numbers match the study; only the v7 path is fixed (mechanical/clapets/clapets-v7 since the folder move).
# Run (from mechanical/layout-v1/):  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/perimeter_study_fc.py
#   then: "C:/Program Files/FreeCAD 1.1/bin/python.exe" fc/perimeter_plot.py
# Output: perimeter-study/topview_data.json (2D outlines of every part per scene + all the numbers)
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("LAYOUT_FRONT_MOD", "AB")
os.environ.setdefault("LAYOUT_BACK", "mirror")
src = open(os.path.join(HERE, "layout_fc.py"), encoding="utf-8").read()
src = src.replace('os.path.join(ROOT, "..", "clapets-v7"', 'os.path.join(ROOT, "..", "clapets", "clapets-v7"')
# stop before layout_fc builds its own shape copies for every pose (memory): only the definitions are needed
src = src.split('say("module poses")')[0]
G = {"__file__": os.path.join(HERE, "layout_fc.py"), "__name__": "layout_fc"}
exec(compile(src, "layout_fc.py", "exec"), G)
App, Part, Vector = G["App"], G["Part"], G["Vector"]
hull2, perim, pts2, build, P, MOD, STACK = G["hull2"], G["perim"], G["pts2"], G["build"], G["P"], G["MOD"], G["STACK"]
mod_pl, FRONT_PL, BACK_PL, OFF, is_door_part = G["mod_pl"], G["FRONT_PL"], G["BACK_PL"], G["OFF"], G["is_door_part"]
OUTD = os.path.normpath(os.path.join(HERE, "..", "perimeter-study"))
os.makedirs(OUTD, exist_ok=True)


def say(*a):
    print("[perim]", *a, flush=True)


def pts_fine(shape, n):
    pts = [(v.Point.x, v.Point.y) for v in shape.Vertexes]
    for e in shape.Edges:
        try:
            pts += [(p.x, p.y) for p in e.discretize(Number=n)]
        except Exception:
            pass
    return pts


say("blocks, chamfer", P.CHAMFER)
BLOCKS, BSH = build(P.CHAMFER)
BLOCK_PTS = []
for sh in BSH.values():
    BLOCK_PTS += pts2(sh)
BLOCK_HULL = hull2(BLOCK_PTS)

# local point clouds of every module part (computed once, then moved per pose)
LOCAL = []
for lab, grp, base, sh in MOD:
    inv = sh.Placement.inverse()
    raw = [inv.multVec(v.Point) for v in sh.Vertexes]
    for e in sh.Edges:
        try:
            raw += [inv.multVec(p) for p in e.discretize(Number=16)]
        except Exception:
            pass
    # plain tuples, deduplicated at 0.1 mm (FreeCAD Vectors are heavy)
    LOCAL.append((lab, grp, base, list({(round(p.x, 1), round(p.y, 1), round(p.z, 1)) for p in raw})))
    del raw
del MOD[:]          # the shapes are no longer needed (memory)
import gc; gc.collect()


def module_parts(h, a, ph, side, drop_doors=False, only=None):
    """[(label, group, 2D hull, zmax)] for one module at lift h, door angle a, head angle ph.
    only = None (all parts), "door" (door parts only), "rest" (everything but the door parts)."""
    out = []
    root = FRONT_PL if side == "F" else BACK_PL
    for lab, grp, base, pts in LOCAL:
        dp = is_door_part(lab, grp)
        if (drop_doors and dp) or (only == "door" and not dp) or (only == "rest" and dp):
            continue
        m = root.multiply(mod_pl(base, grp, h, a, ph)).toMatrix()
        xy, zm = [], -1e9
        for x, y, z in pts:
            xy.append((m.A11 * x + m.A12 * y + m.A13 * z + m.A14, m.A21 * x + m.A22 * y + m.A23 * z + m.A24))
            zm = max(zm, m.A31 * x + m.A32 * y + m.A33 * z + m.A34)
        out.append((lab, grp, hull2(xy), zm))
    return out


def scene_perim(parts_lists, extra=()):
    pts = list(BLOCK_HULL) + list(extra)
    for parts in parts_lists:
        for _, _, hl, _ in parts:
            pts += hl
    hl = hull2(pts)
    return perim(hl), hl


POSES = G["POSES"]
SCENES = [   # (key, title, front pose, back pose, back without doors)
    ("start", "Start: both modules folded", "start_folded", "start_folded", False),
    ("one_open", "One module open (approach -30), other folded", "approach_open", "start_folded", False),
    ("both_approach", "Both open, approach (doors -30)", "approach_open", "approach_open", False),
    ("both_release", "Both fully open (doors -38, release)", "open_release", "open_release", False),
    ("both_lift_turn", "Both fully open + lift 75 + head turned 90", "lift75_turn90", "lift75_turn90", False),
]
data = {"chamfer": P.CHAMFER, "body": G["body_poly"](P.CHAMFER), "blocks": {}, "scenes": {}, "numbers": {}}
for n, sh in BSH.items():
    data["blocks"][n] = {"hull": hull2(pts2(sh)), "zmax": sh.BoundBox.ZMax, "kind": BLOCKS[n][0]}

for key, title, fp, bp, nodoor in SCENES:
    say("scene", key)
    fparts = module_parts(*POSES[fp], "F")
    bparts = module_parts(*POSES[bp], "B", nodoor)
    p, hl = scene_perim([fparts, bparts])
    data["scenes"][key] = {"title": title, "front": fp, "back": bp, "perimeter": p, "hull": hl,
                           "parts": [{"side": sd, "label": l, "group": g, "hull": h, "zmax": z}
                                     for sd, lst in (("F", fparts), ("B", bparts)) for l, g, h, z in lst]}
    say("  perimeter %.1f" % p)

# ---- 1. measurement check: the reserved blocks with finer arcs (64 points per edge instead of 16)
say("fine check")
fine = []
for sh in BSH.values():
    fine += pts_fine(sh, 64)
data["numbers"]["both_approach_fine_blocks"] = perim(hull2(fine + [q for p in data["scenes"]["both_approach"]["parts"] for q in p["hull"]]))

# ---- 2. door angle sweep (lift 0, head 0): only the door parts move with the angle
say("door sweep")
ANG = list(range(90, -41, -2)) + [-38, -30, 3]
ANG = sorted(set(ANG), reverse=True)
MH = {}
for side in ("F", "B"):
    rest = [q for _, _, hl, _ in module_parts(0, 0, 0, side, only="rest") for q in hl]
    for a in ANG:
        pts = list(rest)
        for _, _, hl, _ in module_parts(0, a, 0, side, only="door"):
            pts += hl
        MH[(side, a)] = hull2(pts)
grid = {}
for fa in ANG:
    for ba in ANG:
        grid["%d|%d" % (fa, ba)] = perim(hull2(BLOCK_HULL + MH[("F", fa)] + MH[("B", ba)]))
data["numbers"]["door_angles"] = ANG
data["numbers"]["grid"] = grid
sym = [(a, grid["%d|%d" % (a, a)]) for a in ANG]
one = [(a, grid["%d|90" % a]) for a in ANG]
data["numbers"]["sym_sweep"] = sym
data["numbers"]["one_sweep"] = one
say("worst symmetric", max(sym, key=lambda t: t[1]), "worst one-open", max(one, key=lambda t: t[1]))

# door tip positions (the door part points farthest from its hinge), per angle, front right door
tips = {}
for a in (90, 3, -30, -38):
    best = (0, None)
    for lab, grp, hl, _ in module_parts(0, a, 0, "F"):
        if grp.startswith("door_D"):
            for x, y in hl:
                d = math.hypot(x - 131.0, y - (82.0 + OFF))   # hinge PX, PY of layout_fc.py
                if d > best[0]:
                    best = (d, (x, y))
    tips[a] = best
data["numbers"]["door_tip_front_right"] = {str(k): v for k, v in tips.items()}

# ---- 3. front A+B + back B only (no doors on the back), both working
say("AB front + B back")
for key, fp, bp in (("ABfront_Bback_both", "approach_open", "lift75_turn90"),
                    ("ABfront_Bback_start", "start_folded", "start_folded")):
    hF, aF, pF = POSES[fp]
    hB, aB, pB = POSES[bp]
    p, hl = scene_perim([module_parts(hF, aF, pF, "F"), module_parts(hB, aB, pB, "B", True)])
    data["numbers"][key] = p
    say(key, p)
fparts = module_parts(*POSES["approach_open"], "F")
bparts = module_parts(*POSES["lift75_turn90"], "B", True)
p, hl = scene_perim([fparts, bparts])
data["scenes"]["ab_front_b_back"] = {"title": "Option: front A+B open (-30) + back B only working", "front": "approach_open",
                                     "back": "lift75_turn90 (no doors)", "perimeter": p, "hull": hl,
                                     "parts": [{"side": sd, "label": l, "group": g, "hull": h, "zmax": z}
                                               for sd, lst in (("F", fparts), ("B", bparts)) for l, g, h, z in lst]}

# ---- 4. FAQ Q1 sensitivity: count the carried quarry stack (clamp pose) in the hull
say("stack sensitivity")
stk = []
for s in STACK:
    s2 = s.copy()
    s2.Placement = App.Placement(Vector(0, OFF, 0), App.Rotation()).multiply(s.Placement)
    stk.append(s2)
stk_pts_f = []
for s in stk:
    stk_pts_f += pts2(s)
stk_pts_b = [(-x, -y) for x, y in stk_pts_f]   # back = front turned 180° about Z
bbs = [s.BoundBox for s in stk]
data["numbers"]["stack_bbox_front"] = [min(b.XMin for b in bbs), max(b.XMax for b in bbs),
                                       min(b.YMin for b in bbs), max(b.YMax for b in bbs)]
data["stack_front"] = hull2(stk_pts_f)
for key, fp, bp, extra in (("stack_front_clamp_back_folded", "clamp", "start_folded", stk_pts_f),
                           ("stack_both_clamp", "clamp", "clamp", stk_pts_f + stk_pts_b)):
    p, _ = scene_perim([module_parts(*POSES[fp], "F"), module_parts(*POSES[bp], "B")], extra)
    data["numbers"][key] = p
    say(key, p)

json.dump(data, open(os.path.join(OUTD, "topview_data.json"), "w"), indent=0)
say("->", os.path.join(OUTD, "topview_data.json"))
