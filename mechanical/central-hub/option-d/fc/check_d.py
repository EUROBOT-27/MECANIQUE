# check_d.py - central hub option D: ONE TRANSFER ACTUATOR PER BOX.
# Every stone has its own ring on the hub axis, turned 0 -> 90 by its own N20 gear motor (inside the hollow spine,
# pinion on the ring's internal teeth). The stone's height change comes from a PASSIVE guide fixed on the spine, so one actuator makes the
# whole move from the stack to the spin-safe position beside the robot:
#   top    : parallelogram arm + drag link to a fixed anchor (as option C)
#   middle : rigid arm, plain turn
#   bottom : parallelogram arm + roller under a fixed ramp (as option C)
# Then the cup servo stands the stone up (bearing shaft + hard stops) and the shared hub lift sets the tower down.
# Why the swing axis is the hub axis: the stone's heading turns exactly 90 deg (face +Y -> -X) and its cup face is at
# r 176 at both ends; a rotation of 90 deg about a vertical axis that maps (0, 231) to (-231, 0) has its axis at (0, 0).
# A single tilted hinge (pure arc, no guide) was tried first: it needs the hinge 450-550 mm away for the compact end
# position, or puts the towers 70-150 mm further out (deployed perimeter >= 1477 > 1400) - see README.
#
# Geometry of the arms, guides, robot and stones is imported from option C (../../fc/check_c.py) so both options are
# checked the same way. Plain Python (numpy + matplotlib), boxes + cylinders.
# Run from mechanical/central-hub/option-d/:
#   python fc/check_d.py          -> hub_d_report.txt + ../../simulations/central_hub/option_d_sheet.png
#   python fc/check_d.py --gif    -> also ../../simulations/central_hub/option_d_sequence.gif
# Frame: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table. mm, degrees.
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                                   # option-d/
sys.path.insert(0, os.path.join(ROOT, "..", "fc"))
import check_c as cc                                           # noqa: E402
from check_c import Box, Cyl, W, R_t, R_r, overlap, seg_box    # noqa: E402

SIM = os.path.join(ROOT, "..", "..", "simulations", "central_hub")
MARGIN = cc.MARGIN
LV = ("B", "M", "T")
UN = ("F", "R")
NAMES = cc.NAMES
UNAME = {"F": "front", "R": "rear"}

# ================================================================== rings: one per box, two per level
R_RING = 48.0                                   # ring outer r; posts start at r >= 54
R_RING_IN = 35.0                                # ring bore: internal teeth, pitch r 36 (m 1, 72 T)
RING_Z = {("F", "B"): (131.0, 141.0), ("R", "B"): (141.0, 151.0),     # B: above the ramps (top 127.6)
          ("F", "M"): (151.0, 161.0), ("R", "M"): (161.0, 171.0),
          ("F", "T"): (174.5, 184.5), ("R", "T"): (184.5, 194.5)}

# Transfer drive per ring: N20 gear motor (12 x 10 mm, 34 long with gearbox + encoder) standing INSIDE the hollow
# spine, around the mast. Pinion 22 T (pitch r 11) on the motor shaft at r 25 pokes through a window in the spine wall
# and meshes the ring's internal 72 T: ratio 3.27 (96 deg of ring = 314 deg of motor). Hard stops on the ring at -3
# and 90, encoder for the positions in between (unpinch). The 6 motors are 60 deg apart: a pinion (+-26 deg at r 25)
# never meets another motor (+-14 deg). A first layout with 270 deg servos OUTSIDE the spine (pinion on the ring's
# outer teeth) has no solution: the only free space is 2 slots of ~20 deg (polar 124-144 / 304-324) and each would
# have to hold 3 servos + pinions in z 87-238 (search 2026-11-18).
R_SPINE = 34.0                                  # hollow spine, wall 4 (bore r 30); the mast r 10 runs through it
MOT_R, PIN_R = 25.0, 11.0
MOTOR = {("F", "B"): (0.0, "below"), ("R", "B"): (60.0, "below"), ("F", "M"): (120.0, "below"),
         ("R", "M"): (180.0, "above"), ("F", "T"): (240.0, "above"), ("R", "T"): (300.0, "above")}
N20_L = 34.0
M_POST_TOP = 171.5                              # middle post top: 3 under the lower top ring + its lug (174.5)
M_BEAM_R0 = 65.0                                # middle beam starts outside the top rings' lugs (r <= 62)


def phi_abs(u, phi):
    return phi + (0.0 if u == "F" else 180.0)


# ================================================================== parts
def spine_parts(L):
    off = np.array([0, 0, L])
    p = [Cyl("spine", R_SPINE, cc.SPINE_Z[0] + L, cc.SPINE_Z[1] + L, "spine")]
    for (u, lv), (z0, z1) in RING_Z.items():
        pol, where = MOTOR[(u, lv)]
        pin = Box.lohi("pinion %s%s" % (u, lv), (MOT_R - PIN_R, -PIN_R, z0 + 1), (MOT_R + PIN_R, PIN_R, z1 - 1))
        zs = (z0 - 1 - N20_L, z0 - 1) if where == "below" else (z1 + 1, z1 + 1 + N20_L)
        mo = Box.lohi("motor %s%s" % (u, lv), (MOT_R - 5, -6, zs[0]), (MOT_R + 5, 6, zs[1]))
        for b in (pin, mo):
            q = b.to(W(pol), off); q.grp = "spine"; p.append(q)
    for u in UN:                                               # drag-link anchors + bottom ramps, as option C
        A = cc.A_point(None, u) + off
        ang = np.arctan2(A[1], A[0])
        s = np.array([np.cos(ang) * (R_SPINE - 2), np.sin(ang) * (R_SPINE - 2), A[2]])
        p.append(seg_box("anchor %sT" % u, s, A + (A - s) / np.linalg.norm(A - s) * 6, 12, "spine"))
        for ph in np.arange(cc.PARK - 5, 96, 5.0):
            rl = cc.roller_local(cc.bottom_alpha(min(max(ph, cc.PARK), 90)))
            seg = Box.lohi("ramp %sB" % u, (40, -2.6, rl[2] + 5), (54, 2.6, rl[2] + 11))
            p.append(seg.to(W(phi_abs(u, ph)), off, grp="spine"))
    return p


class Ann(Cyl):
    """annulus on the hub axis (ring with internal teeth): only r_in .. r is solid"""
    def __init__(s, name, r_in, r, z0, z1, grp=""):
        super().__init__(name, r, z0, z1, grp); s.r_in = r_in


def ov(a, b, m=0.0):
    """overlap() from option C, plus annuli; the spine is hollow (bore r R_SPINE - 4)"""
    for x, y in ((a, b), (b, a)):
        if isinstance(x, Cyl) and not isinstance(y, Cyl):
            r_in = x.r_in if isinstance(x, Ann) else (R_SPINE - 4 if x.name == "spine" else 0.0)
            if r_in <= 0: break
            if np.linalg.norm(x.c - y.c) > x.rad + y.rad + m: return False
            P = y.points(7); rr = np.hypot(P[:, 0], P[:, 1])
            return bool(((rr < x.r + m) & (rr > r_in - m) & (P[:, 2] > x.z0 - m) & (P[:, 2] < x.z1 + m)).any())
    return overlap(a, b, m)


def ring_parts(L):
    return [Ann("ring %s%s" % k, R_RING_IN, R_RING, z0 + L, z1 + L, "ring" + k[0] + k[1]) for k, (z0, z1) in RING_Z.items()]


def arm_parts(lv, u, phi, L, spin=0.0, held=True, size=cc.STONE):
    """one arm (+ its stone), as option C but the post is bolted to the arm's OWN ring"""
    Wm = W(phi_abs(u, phi)); off = np.array([0, 0, L]); g = u + lv
    rz0, rz1 = RING_Z[(u, lv)]
    P = []
    if lv == "M":
        tip_r, zlt = cc.TIP_R, cc.CUP_END - cc.CUP_DZ["M"]
        # post stops 3 below the lower top ring (174.5); the beam starts at r 65, outside the top rings' lugs (r <= 62)
        P += [Box.lohi("lug", (R_RING - 2, -12, rz0), (54, 12, rz1)),
              Box.lohi("post", (54, -12, rz0), (74, 12, M_POST_TOP)),
              Box.lohi("beam", (M_BEAM_R0, -12, cc.CUP_END + 8), (tip_r - 5, 12, cc.CUP_END + 20))]
    else:
        a = cc.alpha_at(lv, phi)
        lr, lt, ur, ut = cc.link_pts(lv, a)
        tip_r, zlt = lt[0], lt[2]
        z0, z1 = (rz1, cc.ZR[lv] + cc.HP + 8) if lv == "T" else (cc.ZR[lv] - 8, rz1)
        P.append(Box.lohi("lug", (R_RING - 2, -12, rz0), (cc.R0[lv] - 12, 12, rz1)))     # ring -> post, 2 x M3
        P.append(Box.lohi("post", (cc.R0[lv] - 12, -12, z0), (cc.R0[lv] + 6, 12, z1)))
        for nm, p0, p1 in (("lower link", lr, lt), ("upper link", ur, ut)):
            P.append(Box(nm, (p0 + p1) / 2, ((cc.LP + 12) / 2, 12, 4), R_t(a)))
        if lv == "T":
            Bp = cc.B_local(a)
            P.append(Box.lohi("ball stud", (Bp[0] - 5, min(0, Bp[1]) - 5, Bp[2] - 5), (Bp[0] + 5, max(0, Bp[1]) + 5, Bp[2] + 5)))
        else:
            rl = cc.roller_local(a)
            P.append(seg_box("cam lever", lr, rl, 6))
            P.append(Box.lohi("roller", rl - [2, 5, 5], rl + [2, 5, 5]))
    cup = zlt + cc.CUP_DZ[lv]
    P += [Box.lohi("carrier", (tip_r - 5, -16, zlt - 8), (tip_r + 6, 16, zlt + cc.HP + 8)),
          Box.lohi("spin unit", (tip_r + 6, -16, cup - 16), (tip_r + 30, 16, cup + 18)),
          Box.lohi("cup", (tip_r + 30, -15, cup - 15), (tip_r + cc.CUP_OFF, 15, cup + 15))]
    out = [b.to(Wm, off, name="%s %s" % (g, b.name), grp=g) for b in P]
    if lv == "T":
        Bw = Wm @ cc.B_local(cc.alpha_at("T", phi)) + off
        out.append(seg_box("%s rod" % g, Bw, cc.A_point(None, u) + off, 10, g + "rod"))
    if held:
        face = tip_r + cc.CUP_OFF
        dz = -cc.MID_CUP_DZ if lv == "M" else 0.0
        c_rel = R_r(spin) @ np.array([size[1] / 2, 0, dz])
        sb = Box("%s stone" % g, np.array([face, 0, cup]) + c_rel, (size[1] / 2, size[0] / 2, size[2] / 2), R_r(spin))
        out.append(sb.to(Wm, off, grp=g + "stone"))
    return out


# ================================================================== sequences
def new_state():
    k = [(u, lv) for u in UN for lv in LV]
    return dict(L=0.0, phi={x: 0.0 for x in k}, spin={x: 0.0 for x in k},
                held={x: True for x in k}, tower={x: False for x in k})


def build_levels(S, st, units, tag):
    """units transfer together (the same moves, each arm on its own servo); the other unit keeps its stack"""
    def push(label):
        s = {kk: (dict(v) if isinstance(v, dict) else v) for kk, v in st.items()}
        s["label"] = tag + label; S.append(s)

    def go_phi(lvs, a, b, n, label):
        for v in np.linspace(a, b, n)[1:]:
            for u in units:
                for lv in lvs: st["phi"][(u, lv)] = float(v)
            push(label)

    def go_L(a, b, n, label):
        for v in np.linspace(a, b, n)[1:]:
            st["L"] = float(v); push(label)

    for lv in ("M", "B", "T"):
        n = NAMES[lv]
        if lv == "M": go_phi(("T", "B"), 0, cc.PARK, 3, "unpinch: top + bottom rings to %g" % cc.PARK)
        if st["L"] != cc.L_SPIN: go_L(st["L"], cc.L_SPIN, 5, "%s: hub to %g" % (n, cc.L_SPIN))
        go_phi((lv,), st["phi"][(units[0], lv)], 90, 48, "%s: transfer" % n)
        if lv == "M": go_phi(("T", "B"), cc.PARK, 0, 3, "top + bottom rings back to 0")
        for v in np.linspace(0, 90, 31)[1:]:
            for u in units: st["spin"][(u, lv)] = float(v)
            push("%s: spin" % n)
        go_L(cc.L_SPIN, 0, 8, "%s: hub lowers, the tower stands on the table" % n)
        for u in units: st["held"][(u, lv)] = False; st["tower"][(u, lv)] = True
        go_phi((lv,), 90, 0, 46, "%s: vented, arm returns" % n)
        for u in units: st["spin"][(u, lv)] = 0.0; st["tower"][(u, lv)] = False


def seq_both():
    S, st = [], new_state()
    S.append({**{k: (dict(v) if isinstance(v, dict) else v) for k, v in st.items()}, "label": "both: home"})
    build_levels(S, st, ("F", "R"), "both units: ")
    return S


def seq_front_only():
    """front unit builds its 3 towers while the rear unit keeps its 3-stone stack in its cups (wall carried), then the rear"""
    S, st = [], new_state()
    build_levels(S, st, ("F",), "front only (rear holds its stack): ")
    build_levels(S, st, ("R",), "rear only: ")
    return S


# ================================================================== check
def collect(state, with_towers=True):
    L = state["L"]
    parts = spine_parts(L) + ring_parts(L)
    for u in UN:
        for lv in LV:
            k = (u, lv)
            parts += arm_parts(lv, u, state["phi"][k], L, state["spin"][k], state["held"][k])
            if with_towers and state["tower"][k]:
                tb = [b for b in arm_parts(lv, u, 90.0, 0.0, 90.0, True) if b.name.endswith("stone")][0]
                tb.name = "%s%s tower" % (u, lv); tb.grp = u + lv + "tower"; parts.append(tb)
    return parts


def base(g): return g.replace("rod", "").replace("stone", "").replace("tower", "")


def allowed(a, b, state):
    ga, gb = a.grp, b.grp
    if ga == gb and ga != "spine": return True                       # joints inside one arm
    na, nb = a.name, b.name
    if base(ga) == base(gb) and len(base(ga)) == 2:
        if "rod" in ga + gb:
            o = a if "rod" in gb else b
            return o.name.endswith(("lower link", "ball stud"))
        if ("stone" in ga + gb) or ("tower" in ga + gb):
            o = a if ("stone" in gb or "tower" in gb) else b
            if o.name.endswith("cup"): return True
            if ("stone" in ga + gb) and ("tower" in ga + gb): return True
        return False
    for x, y in ((a, b), (b, a)):
        if x.grp.startswith("ring"):
            key = x.grp[4:]
            if y.grp == key and y.name.endswith(("post", "lug")): return True   # lug + post bolted to its own ring
            if y.name == "pinion " + key: return True                  # pinion meshes its own ring
    if "spine" in (na, nb) and (nb if na == "spine" else na).startswith(("pinion", "motor", "anchor")):
        return True                       # pinion through its wall window, motor in its wall groove, anchor bolted on
    if {na.split()[0], nb.split()[0]} == {"motor", "pinion"} and na.split()[1] == nb.split()[1]:
        return True                       # pinion on its own motor's shaft
    if "rod" in ga + gb and "anchor" in na + nb:
        rod, anc = (a, b) if "rod" in ga else (b, a)
        if anc.name.split()[1] == rod.grp.replace("rod", ""): return True
    if "ramp" in na + nb:
        rmp, o = (a, b) if "ramp" in na else (b, a)
        if o.name.endswith(("roller", "cam lever")) and rmp.name.split()[1] == o.grp: return True
    if ga.endswith("stone") and gb.endswith("stone") and ga[0] == gb[0]:   # stones of one stack touch
        if state["phi"][(ga[0], ga[1])] <= 0.01 and state["phi"][(gb[0], gb[1])] <= 0.01: return True
    return False


def check(states, fixed):
    clashes, tight = {}, {}
    zmin, zmax, zwho = 1e9, -1e9, None
    # fixed spine parts against each other + the robot: once
    sp0 = spine_parts(0.0) + ring_parts(0.0)
    st0 = states[0]
    for i in range(len(sp0)):
        for j in range(i + 1, len(sp0)):
            a, b = sp0[i], sp0[j]
            if a.name.startswith("ramp") and b.name.startswith("ramp"): continue
            if allowed(a, b, st0): continue
            key = tuple(sorted((a.name, b.name)))
            if ov(a, b): clashes.setdefault(key, []).append("static")
            elif ov(a, b, MARGIN): tight.setdefault(key, []).append("static")
    for s in states:
        parts = collect(s)
        sp = [p for p in parts if p.grp == "spine" or p.grp.startswith("ring")]
        mov = [p for p in parts if p not in sp]
        for p in mov + sp:
            if isinstance(p, Cyl) or p.name.endswith("tower"): continue
            k = p.corners()[:, 2]
            zmin = min(zmin, k.min())
            if k.max() > zmax: zmax, zwho = k.max(), (p.name, s["label"])
        pairs = [(a, b) for a in mov for b in fixed + sp]
        pairs += [(mov[i], mov[j]) for i in range(len(mov)) for j in range(i + 1, len(mov))]
        pairs += [(a, b) for a in sp for b in fixed]
        for a, b in pairs:
            if allowed(a, b, s): continue
            m = -0.5 if (a.name.endswith(("stone", "tower")) and b.name.endswith(("stone", "tower"))) else 0.0
            key = tuple(sorted((a.name, b.name)))
            if ov(a, b, m): clashes.setdefault(key, []).append(s["label"])
            elif ov(a, b, MARGIN): tight.setdefault(key, []).append(s["label"])
    return clashes, tight, zmin, zmax, zwho


def perim(parts):
    return cc.perim(parts)


# ================================================================== report
def main():
    fixed = cc.fixed_robot()
    fixed = [p for p in fixed if p.name != "lift servo"] + [p for p in fixed if p.name == "lift servo"]
    runs = (("A. both units together (as option C)", seq_both()),
            ("B. front unit alone while the rear unit holds its stack, then rear alone", seq_front_only()))
    L = []; P = L.append
    P("Central hub - option D: ONE transfer motor per box (own ring on the hub axis + passive guide), cup servo stands")
    P("the stone up, shared hub lift sets the towers down. Box check on base_330_js, both units (front -> left, rear -> right).")
    P("Arm geometry, guides, robot, stones: imported from option C (fc/check_c.py).")
    P("")
    P("== Rings and transfer motors ==")
    for u in UN:
        for lv in LV:
            z0, z1 = RING_Z[(u, lv)]; pol, wh = MOTOR[(u, lv)]
            P("%-5s %-6s ring z %5.1f-%5.1f (r %g-%g, internal 72 T)   N20 at polar %3g (front frame), r %g, %s the ring, pinion 22 T" %
              (UNAME[u], NAMES[lv], z0, z1, R_RING_IN, R_RING, pol, MOT_R, wh))
    P("ratio 72/22 = 3.27: ring -3 .. 93 = %.0f deg of motor shaft (N20 with encoder, hard stops at -3 and 90)" % (96 * 72 / 22))
    P("")
    P("== Transfer path (from option C, unchanged): cup height (hub at 0) ==")
    for lv in ("T", "M", "B"):
        zs = " / ".join("%.0f" % cc.cup_z(lv, p) for p in (cc.PARK, 0, 15, 30, 45, 60, 75, 90))
        P("%-6s z at turn %g/0/15/30/45/60/75/90: %s" % (NAMES[lv], cc.PARK, zs))
    P("top drag link worst transmission angle %.0f deg; bottom ramp steepest %.0f deg" %
      (cc.transmission(cc.DRAG, cc.TOP_TAB), cc.cam_slope()))
    P("")
    total = 0
    worst_z = (-1e9, None)
    all_cl, all_ti = {}, {}
    zlo = 1e9
    for title, states in runs:
        cl, ti, zmin, zmax, zwho = check(states, fixed)
        total += len(states)
        P("== Run %s: %d states ==" % (title, len(states)))
        P("clashes: %s" % ("none" if not cl else ""))
        for (a, b), labs in sorted(cl.items()):
            P("  %s x %s: %d states (%s ... %s)" % (a, b, len(labs), labs[0], labs[-1]))
        P("closer than %g mm: %s" % (MARGIN, "none" if not ti else ""))
        for (a, b), labs in sorted(ti.items()):
            P("  %s x %s: %d states (%s ... %s)" % (a, b, len(labs), labs[0], labs[-1]))
        P("height: parts + held stones z %.1f .. %.1f (highest: %s, '%s')" % (zmin, zmax, zwho[0], zwho[1]))
        P("")
        all_cl.update(cl); all_ti.update(ti); zlo = min(zlo, zmin)
        if zmax > worst_z[0]: worst_z = (zmax, zwho)
    home = seq_both()[0]
    dep = new_state()
    for k in dep["phi"]: dep["phi"][k] = 90.0; dep["spin"][k] = 90.0
    P("== Perimeter (convex hull, stones excluded per FAQ Q1) [GR F.3] ==")
    P("start, arms home: %.0f mm (limit 1200; the base_330_js plate alone is 1232)" % perim(fixed + collect(home, False)))
    P("deployed, all 6 arms at 90 + spun: %.0f mm (limit 1400, FAQ Q10)" % perim(fixed + collect(dep, False)))
    P("")
    P("== Summary ==")
    P("%d states; clashes: %s; closer than %g mm: %d pairs; height %.1f .. %.1f (limit 350 [GR F.3])" %
      (total, "none" if not all_cl else "%d pairs" % len(all_cl), MARGIN, len(all_ti), zlo, worst_z[0]))
    txt = "\n".join(L)
    with open(os.path.join(ROOT, "hub_d_report.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)
    if "--nofig" not in sys.argv:
        sheet(fixed)
    if "--gif" in sys.argv:
        gif(fixed, runs[1][1])


# ================================================================== drawings
COL = dict(cc.COL)


def style(p):
    if p.grp == "robot": return COL["robot"]
    if p.grp == "spine" or p.grp.startswith("ring"): return COL["spine"]
    if p.name.endswith(("stone", "tower")): return COL["stone"]
    if "rod" in p.grp: return COL["rod"]
    return COL[p.grp[1]]


def scene(ax, parts, plane, alpha=1.0, only=None):
    for p in parts:
        if only and not only(p): continue
        fc, ec = style(p)
        cc.draw(ax, p, plane, fc=fc, ec=ec, lw=0.5, alpha=alpha * (0.5 if p.name.endswith(("stone", "tower")) else 0.9))


def sheet(fixed):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(2, 2, figsize=(16, 13))
    home = seq_both()[0]
    # 1 top view: front unit mid-way, rear unit still holding its stack
    a = ax[0, 0]; a.set_title("Top view: front top stone at turn 45 and 90 on its own motor,\nrear unit still holding its stack (hub at %g)" % cc.L_SPIN)
    scene(a, fixed, (0, 1))
    s = new_state(); s["L"] = cc.L_SPIN
    for k in s["held"]: s["held"][k] = k[0] == "R"
    scene(a, collect(s, False), (0, 1), 0.35)
    for p_, al in ((45, 0.55), (90, 1.0)):
        s2 = new_state(); s2["L"] = cc.L_SPIN; s2["phi"][("F", "T")] = p_
        for k in s2["held"]: s2["held"][k] = k == ("F", "T") or k[0] == "R"
        scene(a, collect(s2, False), (0, 1), al, only=lambda p: p.grp.startswith("FT"))
    a.set_xlim(-430, 430); a.set_ylim(-330, 330); a.set_aspect("equal"); a.grid(alpha=0.3)
    a.set_xlabel("x (robot's left = -x)"); a.set_ylabel("y (forward)")
    # 2 hub cross-sections: motors inside the spine, around the mast
    from matplotlib.patches import Circle, Wedge
    a = ax[0, 1]; a.set_title("Hub section (x-y): 6 N20 motors inside the hollow spine,\npinion through the wall into each ring's internal teeth")
    a.add_patch(Circle((0, 0), R_RING, fc="#ccd", ec="k", alpha=0.4))
    a.add_patch(Circle((0, 0), R_RING_IN, fc="white", ec="k", ls="--"))
    a.add_patch(Wedge((0, 0), R_SPINE, 0, 360, width=4, fc="#9ab", ec="k"))
    a.add_patch(Circle((0, 0), 10, fc="#888", ec="k")); a.text(-6, -2, "mast", fontsize=7)
    for (u, lv), (pol, wh) in MOTOR.items():
        Wm = W(pol)
        c = Wm @ np.array([MOT_R, 0, 0])
        a.add_patch(Circle(c[:2], PIN_R, fc=COL[lv][0], ec="k", alpha=0.35))
        m = Box.lohi("m", (MOT_R - 5, -6, 0), (MOT_R + 5, 6, 1)).to(Wm, np.zeros(3))
        cc.draw(a, m, (0, 1), fc=COL[lv][0], ec="k", alpha=0.9)
        a.text(*(Wm @ np.array([MOT_R + 16, 0, 0]))[:2], "%s %s\n(%s)" % (UNAME[u], NAMES[lv], wh), fontsize=7, ha="center")
    a.set_xlim(-70, 70); a.set_ylim(-70, 70); a.set_aspect("equal"); a.grid(alpha=0.3)
    a.set_xlabel("x"); a.set_ylabel("y")
    # 3 side view home
    a = ax[1, 0]; a.set_title("Side view (y-z), home: front + rear stacks, every stone held at the middle of its face")
    scene(a, fixed, (1, 2), only=lambda p: isinstance(p, Cyl) or abs(p.c[0]) < 170)
    scene(a, collect(home, False), (1, 2))
    a.axhline(350, color="r", ls="--", lw=1); a.text(-320, 353, "350 [GR F.3]", color="r", fontsize=8)
    a.set_xlim(-330, 330); a.set_ylim(-10, 375); a.set_aspect("equal"); a.grid(alpha=0.3)
    # 4 front view: front unit tower built while the rear holds
    a = ax[1, 1]; a.set_title("Front view (x-z): front bottom stone spinning, rear unit still holding its stack")
    scene(a, fixed, (0, 2), only=lambda p: isinstance(p, Cyl) or abs(p.c[1]) < 150)
    for sp_, al in ((0, 0.3), (45, 0.5), (90, 1.0)):
        s = new_state(); s["L"] = cc.L_SPIN; s["phi"][("F", "B")] = 90.0; s["spin"][("F", "B")] = sp_
        for k in s["held"]: s["held"][k] = k == ("F", "B") or k[0] == "R"
        scene(a, collect(s, False), (0, 2), al, only=lambda p: p.grp.startswith(("FB", "R")) or p.grp == "spine")
    a.axhline(350, color="r", ls="--", lw=1); a.axhline(0, color="k", lw=1)
    a.set_xlim(-430, 430); a.set_ylim(-10, 375); a.set_aspect("equal"); a.grid(alpha=0.3)
    fig.suptitle("Central hub option D: 1 transfer N20 per box (own ring + passive guide), 1 spin servo per cup, 1 hub-lift servo", fontsize=12)
    fig.tight_layout()
    os.makedirs(SIM, exist_ok=True)
    fig.savefig(os.path.join(SIM, "option_d_sheet.png"), dpi=90)
    plt.close(fig)


def gif(fixed, states):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    keep = states[::4]

    def frame(i):
        s = keep[i]
        for a in ax: a.clear()
        parts = collect(s)
        scene(ax[0], fixed, (0, 1)); scene(ax[0], parts, (0, 1))
        ax[0].set_xlim(-430, 430); ax[0].set_ylim(-330, 330); ax[0].set_aspect("equal"); ax[0].set_title("top view")
        scene(ax[1], fixed, (0, 2), only=lambda p: isinstance(p, Cyl) or abs(p.c[1]) < 150)
        scene(ax[1], parts, (0, 2))
        ax[1].axhline(350, color="r", ls="--", lw=1); ax[1].axhline(0, color="k", lw=1)
        ax[1].set_xlim(-430, 430); ax[1].set_ylim(-10, 375); ax[1].set_aspect("equal"); ax[1].set_title("front view")
        fig.suptitle("Central hub option D - " + s["label"], fontsize=10)
    an = FuncAnimation(fig, frame, frames=len(keep))
    an.save(os.path.join(SIM, "option_d_sequence.gif"), writer=PillowWriter(fps=10))
    plt.close(fig)


if __name__ == "__main__":
    main()
