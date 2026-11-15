# How far can each clapets module move toward the robot centre (Y) in layout v1 A+B / mirror?
# Run (from mechanical/layout-v1/): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/inward_gap_fc.py   (~1 min)
# Bounding-box check of every module part (all poses) against the drive and the other module.
import os
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["LAYOUT_FRONT_MOD"] = "AB"; os.environ["LAYOUT_BACK"] = "mirror"
src = open(os.path.join(HERE, "layout_fc.py"), encoding="utf-8").read()
src = src.replace('os.path.join(ROOT, "..", "clapets-v7"', 'os.path.join(ROOT, "..", "clapets", "clapets-v7"')
src = src.split('say("module poses")')[0]
G = {"__file__": os.path.join(HERE, "layout_fc.py"), "__name__": "x"}
exec(compile(src, "layout_fc.py", "exec"), G)
MOD, POSES, mod_pl, FRONT_PL, P = G["MOD"], G["POSES"], G["mod_pl"], G["FRONT_PL"], G["P"]
S, WX0, MX0, MX1, WR = G["S"], G["WX0"], G["MX0"], G["MX1"], G["WR"]

# every front part, union of its bbox over all poses (robot frame)
parts = {}
for lab, grp, base, sh in MOD:
    bbs = []
    for pose, (h, a, ph) in POSES.items():
        s = sh.copy(); s.Placement = FRONT_PL.multiply(mod_pl(base, grp, h, a, ph)); bbs.append(s.BoundBox)
    b = bbs[0]
    for o in bbs[1:]:
        b = b.united(o)
    parts[lab] = (grp, b)

drive = {"WHEEL_R": (WX0, S, -WR, WR, 0, 2 * WR), "WHEEL_L": (-S, -WX0, -WR, WR, 0, 2 * WR),
         "MOTOR_R": (MX0, MX1, -P.MOTOR_D / 2, P.MOTOR_D / 2, WR - P.MOTOR_D / 2, WR + P.MOTOR_D / 2),
         "MOTOR_L": (-MX1, -MX0, -P.MOTOR_D / 2, P.MOTOR_D / 2, WR - P.MOTOR_D / 2, WR + P.MOTOR_D / 2)}


def ov(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0) > 0.01


# 1. drive: how far can the front module move in -Y before each part touches a drive block? (gap in Y, < 0 = overlap)
res = []
for lab, (grp, b) in parts.items():
    for dn, (x0, x1, y0, y1, z0, z1) in drive.items():
        if ov(b.XMin, b.XMax, x0, x1) and ov(b.ZMin, b.ZMax, z0, z1):
            res.append((b.YMin - y1, lab, dn, b))
res.sort()
print("== front module parts vs drive (gap in Y; < 0 = overlap now)")
for g, lab, dn, b in res[:10]:
    print("  %7.1f  %-26s vs %-8s  part X %.0f..%.0f Y %.1f..%.1f Z %.1f..%.1f" % (g, lab, dn, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))

# 2. other module (mirror: X,Y -> -X,-Y). Both move in by d: gap between part pairs = (front YMin) - (back YMax), closes 2d
res2 = []
for la, (ga, a) in parts.items():
    for lb, (gb, b) in parts.items():
        bx0, bx1, by1 = -b.XMax, -b.XMin, -b.YMin
        if ov(a.XMin, a.XMax, bx0, bx1) and ov(a.ZMin, a.ZMax, b.ZMin, b.ZMax):
            res2.append((a.YMin - by1, la, lb))
res2.sort()
print("== front vs back module (gap in Y; each module may move in by gap/2)")
for g, la, lb in res2[:8]:
    print("  %7.1f  F:%-24s vs B:%s" % (g, la, lb))

# 3. lowest Y of the module and the footprint at start
print("== front module: lowest Y over all poses: %.1f (%s)" % min((b.YMin, l) for l, (g, b) in parts.items()))
print("   stack face / body front Y %.1f, body back Y %.1f" % (P.FRONT, -P.BACK))
# NEMA (through the floor) vs motors
for l, (g, b) in parts.items():
    if l.startswith("REF_NEMA17"):
        print("   lift NEMA X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
    if l.startswith("A_SOCLE"):
        print("   socle     X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
    if l.startswith("A_AILE_D"):
        print("   door unit X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
