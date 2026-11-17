# hub_fc.py - FreeCAD model of the grooved central hub (Ayoub's concept, not reviewed).
# Only the hub column + its 6 shafts (sleeves, follower pins, arms, spin shafts, cups) + reference stones.
# No robot base, no elastics/latches: each sleeve is meant to be driven both ways by an actuator (not modelled yet).
# Concept: mechanical/concepts/central-hub-builder.md. Same numbers as ../hub_gif.py.
#
# Run (headless):  "<FreeCAD>/bin/freecadcmd.exe" fc/hub_fc.py      (from mechanical/central-hub/)
# Writes CAD_FC/HUB_HOME.FCStd (both stacks held), CAD_FC/HUB_DEPLOYED.FCStd (6 stones standing),
# and hub_report.txt (groove slope / drive check, step-by-step clash check).
# Frame: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table. mm.
import math, os, sys
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "CAD_FC")
os.makedirs(OUT, exist_ok=True)
V = App.Vector

# ---------------- parameters ----------------
HUB_R = 50.0          # hub column radius
HUB_RI = 38.0         # bore (printed/turned tube)
HUB_Z0, HUB_Z1 = 73.0, 345.0   # sits on the bridge top (z 73), top under 350
GROOVE_RC = 48.0      # groove centre-line radius
GROOVE_RT = 3.25      # groove half-width (Ø6 pin + 0.5)
PIN_R = 3.0
SLV_RI, SLV_RO = HUB_R + 0.5, 62.0   # partial sleeve
SLV_H = 30.0
SLV_ARC = 40.0        # deg; sleeves pass each other >= ~60 deg apart, so 40 leaves margin
ARM_W, ARM_T = 14.0, 8.0
DROP = 100.0          # radius of the arm's vertical step
SHAFT_R0, SHAFT_R1, SHAFT_D = 108.0, 150.0, 8.0   # spin shaft (radial)
CUP_R0, CUP_R1, CUP_D = 150.0, 170.0, 30.0        # cup holder + cup, stone face at 170
FACE = 170.0
ZH = [55.0, 165.0, 275.0]   # stone centres (bottom, middle, top), base at 0
OFF = [40.0, 0.0, -40.0]    # sleeve z - cup z
LIFT = 10.0
STONE = (320.0, 110.0, 110.0)
NAMES = ["bottom", "middle", "top"]

def groove(k, phi):
    t = max(0.0, min(1.0, phi / 90.0))
    f = 1 - (1 - t) ** 3
    return [105 * f, 0.0, -105 * f][k]

def theta(u, phi):
    """Polar angle (deg) of a shaft: front unit starts at +Y and ends at -X; rear unit = front turned 180."""
    return 90.0 + phi + (180.0 if u == 1 else 0.0)

def zc(k, phi): return ZH[k] + LIFT + groove(k, phi)
def zs(k, phi): return zc(k, phi) + OFF[k]

def rot_z(shape, deg):
    s = shape.copy(); s.rotate(V(0, 0, 0), V(0, 0, 1), deg); return s

# ---------------- hub ----------------
def groove_tube(u, k):
    pts = []
    for i in range(-2, 47):                      # -4..92 deg, a little past both ends
        phi = 2.0 * i
        a = math.radians(theta(u, phi))
        pts.append(V(GROOVE_RC * math.cos(a), GROOVE_RC * math.sin(a), zs(k, max(0.0, min(90.0, phi)))))
    # clean duplicates at the clamped ends (keep the path smooth)
    bs = Part.BSplineCurve(); bs.interpolate(pts)
    path = Part.Wire(bs.toShape())
    p0 = pts[0]; t0 = bs.tangent(bs.FirstParameter)[0]
    prof = Part.Wire(Part.makeCircle(GROOVE_RT, p0, t0))
    sweep = Part.BRepOffsetAPI.MakePipeShell(path)
    sweep.setFrenetMode(True); sweep.add(prof); sweep.build(); sweep.makeSolid()
    tube = sweep.shape()
    ends = [Part.makeSphere(GROOVE_RT, pts[0]), Part.makeSphere(GROOVE_RT, pts[-1])]
    return tube.fuse(ends)

def make_hub():
    hub = Part.makeCylinder(HUB_R, HUB_Z1 - HUB_Z0, V(0, 0, HUB_Z0))
    hub = hub.cut(Part.makeCylinder(HUB_RI, HUB_Z1 - HUB_Z0, V(0, 0, HUB_Z0)))
    for u in (0, 1):
        for k in range(3):
            hub = hub.cut(groove_tube(u, k))
    return hub.removeSplitter()

# ---------------- one shaft ----------------
def shaft_parts(u, k, phi, rho):
    """Returns dict of solids for shaft k of unit u at turn phi (deg) and spin rho (deg)."""
    th = theta(u, phi)
    z_s, z_c = zs(k, phi), zc(k, phi)
    # built along +X at angle 0, then turned to th
    slv = Part.makeCylinder(SLV_RO, SLV_H, V(0, 0, z_s - SLV_H / 2), V(0, 0, 1), SLV_ARC)
    slv = slv.cut(Part.makeCylinder(SLV_RI, SLV_H, V(0, 0, z_s - SLV_H / 2), V(0, 0, 1), SLV_ARC))
    slv = rot_z(slv, -SLV_ARC / 2)
    pin = Part.makeCylinder(PIN_R, SLV_RI - 45.5 + 1, V(45.5, 0, z_s), V(1, 0, 0))
    arm = Part.makeBox(DROP - SLV_RO + 1, ARM_W, ARM_T, V(SLV_RO - 1, -ARM_W / 2, z_s - ARM_T / 2))
    lo, hi = min(z_s, z_c) - ARM_T / 2, max(z_s, z_c) + ARM_T / 2
    leg = Part.makeBox(SHAFT_R0 - DROP, ARM_W, hi - lo, V(DROP, -ARM_W / 2, lo))
    shaft = Part.makeCylinder(SHAFT_D / 2, SHAFT_R1 - SHAFT_R0, V(SHAFT_R0, 0, z_c), V(1, 0, 0))
    cup = Part.makeCylinder(CUP_D / 2, CUP_R1 - CUP_R0, V(CUP_R0, 0, z_c), V(1, 0, 0))
    sl, sw, sh = STONE
    stone = Part.makeBox(sw, sl, sh, V(FACE, -sl / 2, z_c - sh / 2))
    for s in (cup, stone):                       # the spin turns the cup and the stone about the shaft axis
        s.rotate(V(0, 0, z_c), V(1, 0, 0), rho)
    parts = dict(sleeve=slv, pin=pin, arm=arm.fuse(leg).removeSplitter(), shaft=shaft, cup=cup, stone=stone)
    return {n: rot_z(s, th) for n, s in parts.items()}

# ---------------- documents ----------------
def build_doc(name, states):
    """states[u][k] = (phi, rho, gone)"""
    doc = App.newDocument(name)
    doc.addObject("Part::Feature", "Hub").Shape = make_hub()
    for u, unit in enumerate(("Front", "Rear")):
        grp = doc.addObject("App::DocumentObjectGroup", unit + "Unit")
        for k in range(3):
            phi, rho, gone = states[u][k]
            for n, s in shaft_parts(u, k, phi, rho).items():
                if n == "stone" and gone: continue
                o = doc.addObject("Part::Feature", "%s_%s_%s" % (unit, NAMES[k], n))
                o.Shape = s; grp.addObject(o)
    doc.recompute()
    path = os.path.join(OUT, name + ".FCStd")
    doc.saveAs(path)
    App.closeDocument(doc.Name)
    return path

# ---------------- checks ----------------
def slope_report(lines):
    lines.append("Groove slope (angle of the groove from horizontal, at the pin radius %.0f mm)" % GROOVE_RC)
    lines.append("A follower turned by a torque about the hub jams above ~55-60 deg (friction 0.3-0.4);")
    lines.append("a follower pushed up/down jams below ~30-35 deg. Cam rule of thumb: keep it under ~45 deg.")
    for k in range(3):
        worst, at = 0.0, 0.0
        for i in range(0, 900):
            phi = i * 0.1
            dz = abs(groove(k, phi + 0.1) - groove(k, phi))
            ds = GROOVE_RC * math.radians(0.1)
            a = math.degrees(math.atan2(dz, ds))
            if a > worst: worst, at = a, phi
        avg = math.degrees(math.atan2(abs(groove(k, 90)), GROOVE_RC * math.pi / 2))
        lines.append("  %-6s groove: max %.0f deg at phi %.0f, average %.0f deg (straight helix)" % (NAMES[k], worst, at, avg))
    for r in (50, 80, 110):
        lines.append("  a straight 105 mm / 90 deg helix at radius %d: %.0f deg" % (r, math.degrees(math.atan2(105, r * math.pi / 2))))

def clash_check(lines):
    """Front unit (rear is the same turned 180). Order middle -> top -> bottom; each: turn 0->90, spin 0->90, release."""
    seq = []
    state = [[0.0, 0.0, False] for _ in range(3)]
    for k in (1, 2, 0):
        for i in range(0, 31):
            state[k][0] = 3.0 * i; seq.append(("turn %s %2.0f" % (NAMES[k], state[k][0]), [s[:] for s in state]))
        for i in range(1, 16):
            state[k][1] = 6.0 * i; seq.append(("spin %s %2.0f" % (NAMES[k], state[k][1]), [s[:] for s in state]))
        state[k][2] = True
    hub = Part.makeCylinder(HUB_R, HUB_Z1 - HUB_Z0, V(0, 0, HUB_Z0))   # plain column: same answer, much faster
    bad, worst_top, worst_bot = [], 0.0, 1e9
    for label, st in seq:
        P = [shaft_parts(0, k, st[k][0], st[k][1]) for k in range(3)]
        hard = []
        for k in range(3):
            mech = P[k]["sleeve"].fuse([P[k]["arm"], P[k]["shaft"], P[k]["cup"]])
            stn = None if st[k][2] else P[k]["stone"]
            hard.append((k, mech, stn))
            if stn:
                bb = stn.BoundBox; worst_top = max(worst_top, bb.ZMax); worst_bot = min(worst_bot, bb.ZMin)
            if mech.common(hub).Volume > 1.0 and True:
                # sleeves sit on the hub with 0.5 clearance; anything else touching the hub is a clash
                bad.append("%s: %s mechanism hits the hub" % (label, NAMES[k]))
        for i in range(3):
            for j in range(i + 1, 3):
                ki, mi, si = hard[i]; kj, mj, sj = hard[j]
                if mi.common(mj).Volume > 1.0: bad.append("%s: %s / %s mechanisms" % (label, NAMES[ki], NAMES[kj]))
                if si and mj.common(si).Volume > 1.0: bad.append("%s: %s mechanism / %s stone" % (label, NAMES[kj], NAMES[ki]))
                if sj and mi.common(sj).Volume > 1.0: bad.append("%s: %s mechanism / %s stone" % (label, NAMES[ki], NAMES[kj]))
                if si and sj:
                    a = si.copy(); a.scale(0.99, a.BoundBox.Center); b = sj.copy(); b.scale(0.99, b.BoundBox.Center)
                    if a.common(b).Volume > 10.0: bad.append("%s: %s / %s stones" % (label, NAMES[ki], NAMES[kj]))
    lines.append("")
    lines.append("Clash check, front unit, %d steps (turn every 3 deg, spin every 6 deg; rear unit = same turned 180):" % len(seq))
    lines.append("  stones: lowest %.1f mm, highest %.1f mm (limits 0 / 350 [GR F.3])" % (worst_bot, worst_top))
    if bad:
        lines.append("  %d clashes:" % len(bad)); lines += ["    " + b for b in bad[:60]]
    else:
        lines.append("  no clashes (sleeves, arms, shafts, cups, stones, hub)")

def main():
    H = lambda phi=0.0, rho=0.0, gone=False: (phi, rho, gone)
    home = [[H(), H(), H()], [H(), H(), H()]]
    dep = [[H(90, 90), H(90, 90), H(90, 90)]] * 2
    files = [build_doc("HUB_HOME", home), build_doc("HUB_DEPLOYED", dep)]
    lines = ["Central hub (grooved) - report", ""]
    lines.append("Hub Ø%.0f, bore Ø%.0f, z %.0f-%.0f; sleeves %.0f deg x %.0f mm; pin Ø%.0f in groove Ø%.1f at r %.0f" %
                 (2 * HUB_R, 2 * HUB_RI, HUB_Z0, HUB_Z1, SLV_ARC, SLV_H, 2 * PIN_R, 2 * GROOVE_RT, GROOVE_RC))
    for k in range(3):
        lines.append("  %-6s sleeve z %.0f -> %.0f, cup z %.0f -> %.0f" % (NAMES[k], zs(k, 0), zs(k, 90), zc(k, 0), zc(k, 90)))
    lines.append("")
    slope_report(lines)
    clash_check(lines)
    lines.append(""); lines += ["wrote " + os.path.relpath(f, ROOT) for f in files]
    txt = "\n".join(lines)
    with open(os.path.join(ROOT, "hub_report.txt"), "w", encoding="utf-8") as fh:
        fh.write(txt + "\n")
    print(txt)

main()
