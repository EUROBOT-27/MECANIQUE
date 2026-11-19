# check_c.py - option C concept check: ONE TRANSFER SERVO PER LEVEL carries each stone from the stack to the
# spin-safe position beside the robot in one arc (ring turns 0 -> 90 about the hub, the arm is a parallelogram whose
# angle is tied to the turn); then the CUP SERVO stands the stone up (spin, as option B: bearing shaft + hard stops).
#   top level    : parallelogram tied to the spine by a fixed DRAG LINK (rod with 2 ball links)
#   middle level : no height change -> rigid arm, ring only
#   bottom level : parallelogram driven by a ROLLER under a fixed RAMP (cam) on the spine. A drag link does not fit
#                  there: its anchor would have to sit below the bridge, or the rod would cross the top arm.
# Plain Python (numpy + matplotlib), oriented boxes + cylinders, no FreeCAD (same level as check_b.py).
# Run from mechanical/central-hub/:
#   python fc/check_c.py            -> hub_c_report.txt + ../simulations/central_hub/option_c_sheet.png
#   python fc/check_c.py --gif      -> also ../simulations/central_hub/option_c_sequence.gif
#   python fc/check_c.py --search   -> drag-link search for the top level (kinematics + own-arm clearance), prints only
# Frame (as options A/B): X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table.
# Robot = base_330_js (336 x 280, JSUMO wheels, AMT102 odometry, plate z 11.5-16.5). mm, degrees.
import os
import sys
import itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIM = os.path.join(ROOT, "..", "simulations", "central_hub")
MARGIN = 3.0

# ================================================================== numbers
STONE = np.array([320.0, 110.0, 110.0])        # nominal [G D.4]; worst 324 x 115
WORST = np.array([324.0, 115.0, 115.0])
FACE = 176.0                                   # cup face from the hub axis, at the stack AND at the side: the tower
                                               # stands 8 mm off the base_330_js plate edge (x 168)
Z_STONE = {"B": 55.0, "M": 165.0, "T": 275.0}  # stone centres, stack standing on the table (hub lift L = 0)
CUP_END = 160.0                                # every cup ends its transfer here (hub frame): stone centre 160 = a
                                               # standing stone's bottom on the table once the hub is back at L = 0
MID_CUP_DZ = -5.0                              # middle cup 5 mm below its stone centre (inside the +-5 stone tolerance)
L_CARRY, L_SPIN, L_MAX = 12.0, 14.0, 20.0      # hub lift: walls carried at 12, transfers + spins at 14 (cup 174)
PARK = -3.0                                    # top + bottom rings turn back 3 deg before the middle goes (unpinch)

LP, HP = 81.3, 30.0                            # parallelogram: link length, spacing of the 2 links
CUP_OFF = 44.5                                 # cup face, radial, from the tip pivots
TIP_R = FACE - CUP_OFF                         # 131.5 tip pivots at both ends of the transfer
CUP_DZ = {"T": 15.0, "B": 5.0, "M": 15.0}      # cup axis above the lower tip pivot
HALF = {lv: np.degrees(np.arcsin(abs(Z_STONE[lv] - CUP_END) / 2 / LP)) for lv in ("T", "B")}   # 45.0 / 40.2
A0 = {"T": HALF["T"], "B": -HALF["B"]}         # link angle at turn 0 ...
A1 = {"T": -HALF["T"], "B": HALF["B"]}         # ... and at turn 90
R0 = {lv: TIP_R - LP * np.cos(np.radians(HALF[lv])) for lv in ("T", "B")}                       # 74.0 / 69.4
ZR = {lv: (Z_STONE[lv] + CUP_END) / 2 - CUP_DZ[lv] for lv in ("T", "B")}                       # 202.5 / 102.5

# hub
R_SPINE = 28.0                                 # lifting spine (printed tube sliding on the fixed mast)
SPINE_Z = (76.0, 330.0)                        # at L = 0 (3 mm over the bridge = the lift's lower stop)
R_RING = 58.0                                  # rings (gear pitch r ~ 56), each in its own band
RING_Z = {"B": (131.0, 141.0), "M": (146.0, 156.0), "T": (ZR["T"] - 18, ZR["T"] - 8)}
MAST_TOP = 350.0                               # fixed mast; the beacon support continues above it (430 +- 5 [GR F.6])

# top drag link: ball stud B on the lower link at e from the root, offset tB sideways (t > 0 = the side the arm
# turns toward); ball stud A on a spine bracket at polar phA, radius rA, sideways tA. zA and the rod length are
# solved so that the links are at A0 at turn 0 and A1 at turn 90.
DRAG = dict(e=50.0, tB=30.0, rA=70.0, tA=30.0, phA=80.0)

# bottom cam: lever behind the lower root pivot (inside the post), roller (623ZZ, 10 mm) at its end rolls UNDER a fixed
# ramp on the spine. Weight of arm + stone presses the roller up onto the ramp (one-sided ramp, safety lip below).
CAM_E = 22.0                                   # lever length
CAM_DIP = 3.0                                  # cup drop at turn -5 (unpinch)

# transfer servos (MG996R, on the spine under their ring, pinion on the ring gear), polar angle in the front-unit frame
SERVO_PHI = {"T": 135.0, "M": -45.0, "B": 135.0}


# ================================================================== geometry helpers
def W(phi):
    """arm frame (r, t, z) -> world. phi = 0: arm points +Y; turns toward -X (robot's left) as phi grows"""
    p = np.radians(phi)
    return np.array([[-np.sin(p), -np.cos(p), 0], [np.cos(p), -np.sin(p), 0], [0, 0, 1.0]])


def R_t(a):        # rotation about the local t axis, positive = r toward z
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])


def R_r(a):        # rotation about the local r axis: the spin
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


class Box:
    def __init__(s, name, c, h, R=None, grp=""):
        s.name, s.c, s.h = name, np.asarray(c, float), np.asarray(h, float)
        s.R = np.eye(3) if R is None else R
        s.grp = grp
        s.rad = float(np.linalg.norm(s.h))

    @staticmethod
    def lohi(name, lo, hi, grp=""):
        lo, hi = np.asarray(lo, float), np.asarray(hi, float)
        return Box(name, (lo + hi) / 2, (hi - lo) / 2, None, grp)

    def to(s, Wm, off, name=None, grp=None):
        return Box(name or s.name, Wm @ s.c + off, s.h, Wm @ s.R, s.grp if grp is None else grp)

    def corners(s):
        sg = np.array(list(itertools.product((-1, 1), repeat=3)))
        return s.c + (sg * s.h) @ s.R.T

    def points(s, n=6):
        g = np.linspace(-1, 1, n)
        sg = np.array(list(itertools.product(g, g, g)))
        return s.c + (sg * s.h) @ s.R.T


class Cyl:
    """vertical cylinder on the hub axis (spine, rings, mast)"""
    def __init__(s, name, r, z0, z1, grp=""):
        s.name, s.r, s.z0, s.z1, s.grp = name, r, z0, z1, grp
        s.c = np.array([0, 0, (z0 + z1) / 2]); s.rad = float(np.hypot(r, (z1 - z0) / 2))


def seg_box(name, p, q, w, grp=""):
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = q - p; n = np.linalg.norm(d); u = d / n
    a = np.array([0, 0, 1.0]) if abs(u[2]) < 0.9 else np.array([1.0, 0, 0])
    v = np.cross(u, a); v /= np.linalg.norm(v); w2 = np.cross(u, v)
    return Box(name, (p + q) / 2, (n / 2, w / 2, w / 2), np.column_stack([u, v, w2]), grp)


def overlap(a, b, m=0.0):
    if np.linalg.norm(a.c - b.c) > a.rad + b.rad + m: return False
    if isinstance(a, Cyl) or isinstance(b, Cyl):
        cy, bx = (a, b) if isinstance(a, Cyl) else (b, a)
        if isinstance(bx, Cyl): return False
        P = bx.points(7)
        inside = (np.hypot(P[:, 0], P[:, 1]) < cy.r + m) & (P[:, 2] > cy.z0 - m) & (P[:, 2] < cy.z1 + m)
        return bool(inside.any())
    A, B = a.R, b.R; ha, hb = a.h + m / 2, b.h + m / 2
    t = b.c - a.c
    axes = [A[:, i] for i in range(3)] + [B[:, i] for i in range(3)]
    axes += [np.cross(A[:, i], B[:, j]) for i in range(3) for j in range(3)]
    for Lx in axes:
        n = np.linalg.norm(Lx)
        if n < 1e-9: continue
        Lx = Lx / n
        ra = sum(ha[i] * abs(A[:, i] @ Lx) for i in range(3))
        rb = sum(hb[i] * abs(B[:, i] @ Lx) for i in range(3))
        if abs(t @ Lx) > ra + rb - 1e-6: return False
    return True


# ================================================================== top: drag-link kinematics
def link_pts(lv, a):
    """lower root, lower tip, upper root, upper tip (arm frame r, t, z; hub at L = 0)"""
    ar = np.radians(a)
    lr = np.array([R0[lv], 0, ZR[lv]]); lt = lr + LP * np.array([np.cos(ar), 0, np.sin(ar)])
    return lr, lt, lr + [0, 0, HP], lt + [0, 0, HP]


def B_local(a, d=None):
    d = d or DRAG; ar = np.radians(a)
    return np.array([R0["T"] + d["e"] * np.cos(ar), d["tB"], ZR["T"] + d["e"] * np.sin(ar)])


def A_point(d=None, unit="F"):
    d = d or DRAG
    p = d["phA"] + (0 if unit == "F" else 180)
    return W(p) @ np.array([d["rA"], d["tA"], 0.0]) + [0, 0, d["zA"]]


def solve_drag(d):
    d = dict(d); d["zA"] = 0.0
    B0 = W(0) @ B_local(A0["T"], d); B1 = W(90) @ B_local(A1["T"], d)
    Axy = A_point(d)[:2]
    h0, h1 = np.sum((Axy - B0[:2]) ** 2), np.sum((Axy - B1[:2]) ** 2)
    if abs(B1[2] - B0[2]) < 1e-6: return None
    d["zA"] = float((B1[2] ** 2 - B0[2] ** 2 + h1 - h0) / (2 * (B1[2] - B0[2])))
    d["l"] = float(np.linalg.norm(A_point(d) - B0))
    return d


def drag_alpha(phi, d, prev):
    A = A_point(d)
    g = lambda a: np.linalg.norm(A - W(phi) @ B_local(a, d)) - d["l"]
    cand = np.linspace(-85, 85, 681); vals = np.array([g(a) for a in cand])
    roots = [cand[i] - vals[i] * (cand[i + 1] - cand[i]) / (vals[i + 1] - vals[i])
             for i in range(len(cand) - 1) if vals[i] * vals[i + 1] <= 0]
    if not roots: return None
    return min(roots, key=lambda x: abs(x - prev))


PHIS = np.linspace(PARK, 90, 191)
def drag_table(d):
    al, prev = [], A0["T"]
    i0 = int(np.argmin(abs(PHIS)))
    out = np.zeros(len(PHIS))
    for i in range(i0, len(PHIS)):                       # from 0 up
        a = drag_alpha(PHIS[i], d, prev)
        if a is None: return None
        out[i] = prev = a
    prev = out[i0]
    for i in range(i0 - 1, -1, -1):                      # from 0 down to PARK
        a = drag_alpha(PHIS[i], d, prev)
        if a is None: return None
        out[i] = prev = a
    return out


def transmission(d, tab):
    """worst angle between the rod and the path of its ball stud (90 = rod pushes straight, 0 = toggle)"""
    worst = 90.0
    for p, a in zip(PHIS, tab):
        Bp = W(p) @ B_local(a, d)
        dB = W(p) @ (B_local(a + 0.5, d) - B_local(a - 0.5, d)); rod = A_point(d) - Bp
        ang = np.degrees(np.arcsin(min(1, abs(dB @ rod) / np.linalg.norm(dB) / np.linalg.norm(rod))))
        worst = min(worst, ang)
    return worst


DRAG = solve_drag(DRAG)
TOP_TAB = drag_table(DRAG)


# ================================================================== bottom: cam profile
def bottom_cup(phi):
    """cup height (hub frame, L = 0) chosen for the bottom level (PARK..0: unpinch dip): fast rise off the table and over the plate corner,
    dwell at the end (the arm can turn back after venting without pushing on the tower)"""
    if phi < 0: return Z_STONE["B"] - CAM_DIP * (-phi / -PARK)
    u = phi / 90.0
    return Z_STONE["B"] + (CUP_END - Z_STONE["B"]) * (1 - (1 - u) ** 2)


def bottom_alpha(phi):
    return float(np.degrees(np.arcsin((bottom_cup(phi) - CUP_DZ["B"] - ZR["B"]) / LP)))


def roller_local(a):
    ar = np.radians(a)
    return np.array([R0["B"] - CAM_E * np.cos(ar), 0.0, ZR["B"] - CAM_E * np.sin(ar)])


def cam_slope():
    """steepest ramp angle seen by the roller (deg), over the whole turn incl. the unpinch"""
    ph = np.linspace(PARK, 90, 381); worst = 0.0
    for p0, p1 in zip(ph[:-1], ph[1:]):
        r0, r1 = roller_local(bottom_alpha(p0)), roller_local(bottom_alpha(p1))
        ds = (r0[0] + r1[0]) / 2 * np.radians(p1 - p0)
        worst = max(worst, np.degrees(np.arctan2(abs(r1[2] - r0[2]), ds)))
    return worst


def alpha_at(lv, phi):
    if lv == "M": return 0.0
    if lv == "B": return bottom_alpha(phi)
    return float(np.interp(phi, PHIS, TOP_TAB))


def cup_z(lv, phi, L=0.0):
    if lv == "M": return CUP_END + L
    _, lt, _, _ = link_pts(lv, alpha_at(lv, phi)); return lt[2] + CUP_DZ[lv] + L


def cup_r(lv, phi):
    if lv == "M": return FACE
    return link_pts(lv, alpha_at(lv, phi))[1][0] + CUP_OFF


# ================================================================== parts
def fixed_robot():
    f = [Box.lohi("plate", (-168, -140, 11.5), (168, 140, 16.5)),
         Box.lohi("bridge plate", (-70, -55, 68), (70, 55, 73)),
         Box.lohi("bridge wall F", (-70, 50, 16.5), (70, 55, 68)),
         Box.lohi("bridge wall R", (-70, -55, 16.5), (70, -50, 68)),
         Box.lohi("lift servo", (-22, 24, 20), (21, 44, 63)),      # MG996R under the bridge plate, crank up through it
         Cyl("mast", 10.0, 73.0, MAST_TOP)]
    for sx, side in ((1, "R"), (-1, "L")):
        lo = lambda a, b: min(sx * a, sx * b)
        hi = lambda a, b: max(sx * a, sx * b)
        f += [Box.lohi("drive motor " + side, (lo(15, 78), -18.5, 16.5), (hi(15, 78), 18.5, 63)),
              Box.lohi("wheel " + side, (lo(79, 131), -40, 0), (hi(79, 131), 40, 77)),
              Box.lohi("odometry " + side, (lo(130, 166), -80, 0), (hi(130, 166), 35, 62))]
    for p in f: p.grp = "robot"
    return f


def spine_parts(L):
    off = np.array([0, 0, L])
    p = [Cyl("spine", R_SPINE, SPINE_Z[0] + L, SPINE_Z[1] + L, "spine")]
    for lv in ("B", "M", "T"):
        p.append(Cyl("ring " + lv, R_RING, RING_Z[lv][0] + L, RING_Z[lv][1] + L, "ring" + lv))
        z1 = RING_Z[lv][0]
        sv = Box.lohi("transfer servo " + lv, (62, -10, z1 - 43), (103, 10, z1 - 1))
        p.append(sv.to(W(SERVO_PHI[lv]), off, grp="spine"))
    for u in ("F", "R"):
        A = A_point(None, u) + off
        ang = np.arctan2(A[1], A[0])
        s = np.array([np.cos(ang) * (R_SPINE - 2), np.sin(ang) * (R_SPINE - 2), A[2]])
        p.append(seg_box("anchor %sT" % u, s, A + (A - s) / np.linalg.norm(A - s) * 6, 12, "spine"))
        # bottom ramp: one fixed segment every 5 deg of turn, r 40..54, its underside on the roller top
        for ph in np.arange(PARK - 5, 96, 5.0):
            rl = roller_local(bottom_alpha(min(max(ph, PARK), 90)))
            seg = Box.lohi("ramp %sB" % u, (40, -2.6, rl[2] + 5), (54, 2.6, rl[2] + 11))
            p.append(seg.to(W(ph + (0 if u == "F" else 180)), off, grp="spine"))
    return p


def arm_parts(lv, u, phi, L, spin=0.0, held=True, size=STONE):
    """parts of one arm (+ its held stone) in world coordinates"""
    Wm = W(phi + (0 if u == "F" else 180)); off = np.array([0, 0, L]); g = u + lv
    P = []
    if lv == "M":
        tip_r, zlt = TIP_R, CUP_END - CUP_DZ["M"]
        P += [Box.lohi("post", (54, -12, RING_Z["M"][1]), (74, 12, CUP_END + 20)),
              Box.lohi("beam", (74, -12, CUP_END + 8), (tip_r - 5, 12, CUP_END + 20))]
    else:
        a = alpha_at(lv, phi)
        lr, lt, ur, ut = link_pts(lv, a)
        tip_r, zlt = lt[0], lt[2]
        z0, z1 = (RING_Z[lv][1], ZR[lv] + HP + 8) if lv == "T" else (ZR[lv] - 8, RING_Z[lv][1])
        P.append(Box.lohi("post", (R0[lv] - 12, -12, z0), (R0[lv] + 6, 12, z1)))
        for nm, p0, p1 in (("lower link", lr, lt), ("upper link", ur, ut)):
            P.append(Box(nm, (p0 + p1) / 2, ((LP + 12) / 2, 12, 4), R_t(a)))
        if lv == "T":
            Bp = B_local(a)
            P.append(Box.lohi("ball stud", (Bp[0] - 5, min(0, Bp[1]) - 5, Bp[2] - 5), (Bp[0] + 5, max(0, Bp[1]) + 5, Bp[2] + 5)))
        else:
            rl = roller_local(a)
            P.append(seg_box("cam lever", lr, rl, 6))       # thinner than the roller: the ramp only touches the roller
            P.append(Box.lohi("roller", rl - [2, 5, 5], rl + [2, 5, 5]))
    cup = zlt + CUP_DZ[lv]
    P += [Box.lohi("carrier", (tip_r - 5, -16, zlt - 8), (tip_r + 6, 16, zlt + HP + 8)),
          Box.lohi("spin unit", (tip_r + 6, -16, cup - 16), (tip_r + 30, 16, cup + 18)),
          Box.lohi("cup", (tip_r + 30, -15, cup - 15), (tip_r + CUP_OFF, 15, cup + 15))]
    out = [b.to(Wm, off, name="%s %s" % (g, b.name), grp=g) for b in P]
    if lv == "T":
        Bw = Wm @ B_local(alpha_at("T", phi)) + off
        out.append(seg_box("%s rod" % g, Bw, A_point(None, u) + off, 10, g + "rod"))
    if held:
        face = tip_r + CUP_OFF
        dz = -MID_CUP_DZ if lv == "M" else 0.0
        c_rel = R_r(spin) @ np.array([size[1] / 2, 0, dz])
        sb = Box("%s stone" % g, np.array([face, 0, cup]) + c_rel, (size[1] / 2, size[0] / 2, size[2] / 2), R_r(spin))
        out.append(sb.to(Wm, off, grp=g + "stone"))
    return out


# ================================================================== sequence
def lin(a, b, n): return list(np.linspace(a, b, n))


NAMES = {"M": "middle", "B": "bottom", "T": "top"}
def sequence():
    S = []
    st = dict(L=0.0, phi=dict(T=0.0, M=0.0, B=0.0), spin=dict(T=0.0, M=0.0, B=0.0),
              held=dict(T=True, M=True, B=True), tower=dict(T=False, M=False, B=False))
    def push(label):
        s = {k: (dict(v) if isinstance(v, dict) else v) for k, v in st.items()}
        s["label"] = label; S.append(s)
    def go(key, sub, a, b, n, label):
        for v in lin(a, b, n)[1:]:
            if sub: st[key][sub] = v
            else: st[key] = v
            push(label)
    push("pick: cups on the stack faces, vacuum on")
    go("L", None, 0, L_SPIN, 5, "hub lifts the stack (walls: carry at %g, set down, vent)" % L_CARRY)
    for lv in ("M", "B", "T"):
        n = NAMES[lv]
        if lv == "M":
            for p in lin(0, PARK, 3)[1:]:
                st["phi"]["T"] = st["phi"]["B"] = p; push("unpinch: top + bottom rings turn back to %g" % PARK)
        if st["L"] != L_SPIN: go("L", None, st["L"], L_SPIN, 5, "%s: hub to %g" % (n, L_SPIN))
        go("phi", lv, st["phi"][lv], 90, 48, "%s: transfer" % n)
        if lv == "M":
            for p in lin(PARK, 0, 3)[1:]:
                st["phi"]["T"] = st["phi"]["B"] = p; push("top + bottom rings back to 0")
        go("spin", lv, 0, 90, 31, "%s: spin" % n)
        go("L", None, L_SPIN, 0, 8, "%s: hub lowers, the tower stands on the table" % n)
        st["held"][lv] = False; st["tower"][lv] = True
        go("phi", lv, 90, 0, 46, "%s: vented, arm returns" % n)
        st["spin"][lv] = 0.0; st["tower"][lv] = False          # robot drives away (>= 0.34 m) before the next level
    return S


# ================================================================== check
def collect(state, with_towers=True):
    L = state["L"]
    parts = spine_parts(L)
    for u in ("F", "R"):
        for lv in ("B", "M", "T"):
            parts += arm_parts(lv, u, state["phi"][lv], L, state["spin"][lv], state["held"][lv])
            if with_towers and state["tower"][lv]:
                tb = [b for b in arm_parts(lv, u, 90.0, 0.0, 90.0, True) if b.name.endswith("stone")][0]
                tb.name = "%s%s tower" % (u, lv); tb.grp = u + lv + "tower"; parts.append(tb)
    return parts


def base(g): return g.replace("rod", "").replace("stone", "").replace("tower", "")


def allowed(a, b, state):
    ga, gb = a.grp, b.grp
    if ga == gb: return True                                         # joints inside one arm
    na, nb = a.name, b.name
    if base(ga) == base(gb) and len(base(ga)) == 2:
        if "rod" in ga + gb:                                         # rod pinned to its own lower link
            o = a if "rod" in gb else b
            return o.name.endswith(("lower link", "ball stud"))
        if ("stone" in ga + gb) or ("tower" in ga + gb):
            o = a if ("stone" in gb or "tower" in gb) else b
            if o.name.endswith("cup"): return True                   # cup on its own stone
            if ("stone" in ga + gb) and ("tower" in ga + gb): return True
        return False
    if ga.startswith("ring") or gb.startswith("ring"):               # post bolted to its own ring
        r, o = (a, b) if ga.startswith("ring") else (b, a)
        if o.grp[1:2] == r.grp[-1] and o.name.endswith("post"): return True
    if "rod" in ga + gb and "anchor" in na + nb:                     # rod ends on its anchor
        rod, anc = (a, b) if "rod" in ga else (b, a)
        if anc.name.split()[1] == rod.grp.replace("rod", ""): return True
    if "ramp" in na + nb:                                            # roller rolls on its own ramp
        rmp, o = (a, b) if "ramp" in na else (b, a)
        if o.name.endswith(("roller", "cam lever")) and rmp.name.split()[1] == o.grp: return True   # ramp drawn in 5 deg steps; along the lever the real ramp is level
    if ga.endswith("stone") and gb.endswith("stone") and ga[0] == gb[0]:   # stones of one stack touch
        if state["phi"][ga[1]] <= 0.01 and state["phi"][gb[1]] <= 0.01: return True
    return False


def check(states, fixed):
    clashes, tight = {}, {}
    zmin, zmax, zwho = 1e9, -1e9, None
    for s in states:
        parts = collect(s)
        sp = [p for p in parts if p.grp == "spine" or p.grp.startswith("ring")]
        mov = [p for p in parts if p not in sp]
        for p in mov + sp:
            if isinstance(p, Cyl) or p.name.endswith("tower"): continue
            k = p.corners()[:, 2]
            if k.min() < zmin: zmin = k.min()
            if k.max() > zmax: zmax, zwho = k.max(), (p.name, s["label"])
        pairs = [(a, b) for a in mov for b in fixed + sp]
        pairs += [(mov[i], mov[j]) for i in range(len(mov)) for j in range(i + 1, len(mov))]
        pairs += [(a, b) for a in sp for b in fixed]
        for a, b in pairs:
            if allowed(a, b, s): continue
            m = -0.5 if (a.name.endswith(("stone", "tower")) and b.name.endswith(("stone", "tower"))) else 0.0
            key = tuple(sorted((a.name, b.name)))
            if overlap(a, b, m): clashes.setdefault(key, []).append(s["label"])
            elif overlap(a, b, MARGIN): tight.setdefault(key, []).append(s["label"])
    return clashes, tight, zmin, zmax, zwho


# ================================================================== top drag-link search (--search)
def search():
    global DRAG, TOP_TAB
    keep = (DRAG, TOP_TAB)
    res = []
    for e in (30.0, 40.0, 50.0):
        for tB in (20.0, 24.0, 30.0):
            for rA in (45.0, 55.0, 70.0, 85.0):
                for phA in (80.0, 90.0, 100.0, 110.0):
                    d = solve_drag(dict(e=e, tB=tB, rA=rA, tA=tB, phA=phA))
                    if d is None or not (SPINE_Z[0] + 8 < d["zA"] < SPINE_Z[1] - 8): continue
                    tab = drag_table(d)
                    if tab is None: continue
                    dd = np.diff(tab)
                    if not np.all(dd <= 0.05) or tab[0] <= A0["T"]: continue
                    DRAG, TOP_TAB = d, tab
                    tr = transmission(d, tab)
                    n = 0
                    for p in PHIS[::6]:
                        ps = arm_parts("T", "F", float(p), 0.0, 0.0, True)
                        rod = [b for b in ps if "rod" in b.grp][0]
                        for b in ps:
                            if b.name.endswith(("post", "upper link", "carrier", "spin unit", "cup", "stone")) and overlap(rod, b, 3): n += 1
                        for b in spine_parts(0.0):
                            if (isinstance(b, Cyl) and not b.name.startswith("ring T")) or b.name.startswith("transfer"):
                                if overlap(rod, b, 3): n += 1
                    dwell = abs(np.interp(80, PHIS, tab) - tab[-1])
                    up = cup_z("T", PARK) - Z_STONE["T"]
                    res.append((n, round(dwell, 1), -round(tr), e, tB, rA, phA, round(d["zA"]), round(d["l"]), round(up, 1)))
    DRAG, TOP_TAB = keep
    res.sort()
    for r in res[:20]:
        print("own clashes %d  dwell %.1f  transmission %d  e %g tB=tA %g rA %g phA %g -> zA %d l %d  unpinch +%.1f" %
              (r[0], r[1], -r[2], *r[3:]))


# ================================================================== perimeter, spin envelope
def hull(P):
    pts = sorted(set(map(tuple, np.round(np.asarray(P), 6))))
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h[:-1]
    return np.array(half(pts) + half(pts[::-1]))


def perim(parts):
    P = []
    for p in parts:
        if isinstance(p, Cyl):
            a = np.linspace(0, 2 * np.pi, 33); P += list(np.column_stack([p.r * np.cos(a), p.r * np.sin(a)]))
        elif not p.name.endswith(("stone", "tower")):
            P += list(p.corners()[:, :2])
    h = hull(P)
    return float(np.sum(np.linalg.norm(np.roll(h, -1, axis=0) - h, axis=1)))


def spin_env(cupz, dz, size=STONE):
    lo, hi = 1e9, -1e9
    for s in np.linspace(0, 90, 181):
        b = Box("s", R_r(s) @ np.array([size[1] / 2, 0, dz]) + [0, 0, cupz], (size[1] / 2, size[0] / 2, size[2] / 2), R_r(s))
        z = b.corners()[:, 2]; lo, hi = min(lo, z.min()), max(hi, z.max())
    return lo, hi


# ================================================================== report
def main():
    if "--search" in sys.argv:
        search(); return
    fixed = fixed_robot()
    states = sequence()
    clashes, tight, zmin, zmax, zwho = check(states, fixed)
    L = []; P = L.append
    P("Central hub - option C: 1 transfer servo per level (ring + arm tied to the turn), cup servo stands the stone up")
    P("concept check on base_330_js, %d states, both units (front stones -> robot's left, rear stones -> right)" % len(states))
    P("Order: unpinch (top + bottom rings to %g), middle, bottom, top. Hub lift %g for every transfer + spin, 0 to set down." % (PARK, L_SPIN))
    P("")
    P("== Transfer: cup height (hub at 0) and cup face radius along the turn ==")
    for lv in ("T", "M", "B"):
        zs = " / ".join("%.0f" % cup_z(lv, p) for p in (PARK, 0, 15, 30, 45, 60, 75, 90))
        rs = " / ".join("%.0f" % cup_r(lv, p) for p in (0, 45, 90))
        P("%-6s z at turn %g/0/15/30/45/60/75/90: %s   face r at 0/45/90: %s" % (NAMES[lv], PARK, zs, rs))
    d = DRAG
    P("top    drag link: links %+.1f -> %+.1f deg (%+.1f at turn %g); rod %.0f mm between ball studs;" %
      (TOP_TAB[np.argmin(abs(PHIS))], TOP_TAB[-1], TOP_TAB[0], PARK, d["l"]))
    P("       B on the lower link %g from the root pivot, %g to the side; A on a spine bracket at polar %g, r %g, side %g, z %.0f" %
      (d["e"], d["tB"], d["phA"], d["rA"], d["tA"], d["zA"]))
    P("       worst transmission angle %.0f deg (90 = rod pushes straight; keep > 30); last 10 deg of turn move the links %.1f deg" %
      (transmission(d, TOP_TAB), abs(np.interp(80, PHIS, TOP_TAB) - TOP_TAB[-1])))
    P("bottom cam: lever %g behind the lower root pivot, roller under a fixed ramp (r 40-54); steepest ramp %.0f deg" % (CAM_E, cam_slope()))
    P("       (the grooved hub had 77 deg, cam rule of thumb < 45); last 10 deg of turn move the links %.1f deg" %
      abs(bottom_alpha(80) - bottom_alpha(90)))
    for lv in ("T", "B"):
        r90 = cup_r(lv, 90); r80 = cup_r(lv, 80)
        P("%-6s return after venting: first 10 deg move the cup %.1f mm toward the tower (+) / away (-)" % (NAMES[lv], r80 - r90))
    P("")
    P("== Spin (cup on a bearing shaft + hard stops; stone turns about the cup axis at cup z %g) ==" % (CUP_END + L_SPIN))
    for nm, dz, sz in (("top/bottom, nominal", 0.0, STONE), ("top/bottom, worst 324 x 115", 0.0, WORST),
                       ("middle (cup 5 below), nominal", -MID_CUP_DZ, STONE), ("middle, worst", -MID_CUP_DZ, WORST)):
        lo, hi = spin_env(CUP_END + L_SPIN, dz, sz)
        P("%-30s lowest corner %.1f, highest %.1f  (limits 0 / 350 [GR F.3])" % (nm, lo, hi))
    P("")
    P("== Height [GR F.3] ==")
    P("moving parts + held stones z %.1f .. %.1f (highest: %s, '%s')" % (zmin, zmax, zwho[0], zwho[1]))
    P("")
    dep = dict(states[0]); dep["phi"] = dict(T=90.0, M=90.0, B=90.0); dep["spin"] = dict(T=90.0, M=90.0, B=90.0)
    P("== Perimeter (convex hull, stones excluded per FAQ Q1) [GR F.3] ==")
    P("start, arms home: %.0f mm (limit 1200; the base_330_js plate alone is 1232: test base, see its README)" %
      perim(fixed + collect(states[0], False)))
    P("deployed, all 3 levels at 90 + spun: %.0f mm (limit 1400, FAQ Q10)" % perim(fixed + collect(dep, False)))
    P("")
    P("== Clashes (left out by design: joints inside an arm, cup on its stone, stones touching inside the stack, rod on")
    P("   its anchor, roller on its ramp, post on its ring) ==")
    P("none" if not clashes else "")
    for (a, b), labs in sorted(clashes.items()):
        P("%s x %s: %d states (%s ... %s)" % (a, b, len(labs), labs[0], labs[-1]))
    P("")
    P("== Closer than %g mm (not a clash) ==" % MARGIN)
    P("none" if not tight else "")
    for (a, b), labs in sorted(tight.items()):
        P("%s x %s: %d states (%s ... %s)" % (a, b, len(labs), labs[0], labs[-1]))
    txt = "\n".join(L)
    with open(os.path.join(ROOT, "hub_c_report.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)
    sheet(fixed)
    if "--gif" in sys.argv: gif(fixed, states)


# ================================================================== drawings
COL = {"robot": ("#d9d9d9", "#888"), "spine": ("#9ab", "#456"), "stone": ("#e39b3a", "#8a5212"),
       "T": ("#3b6fb6", "#1d3c66"), "M": ("#6aa56a", "#2e5e2e"), "B": ("#b65b3b", "#66301d"), "rod": ("#222", "#000")}


def draw(ax, b, plane, **kw):
    from matplotlib.patches import Polygon, Rectangle, Circle
    if isinstance(b, Cyl):
        if plane == (0, 1): ax.add_patch(Circle((0, 0), b.r, **kw))
        else: ax.add_patch(Rectangle((-b.r, b.z0), 2 * b.r, b.z1 - b.z0, **kw))
        return
    ax.add_patch(Polygon(hull(b.corners()[:, list(plane)]), closed=True, **kw))


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
        draw(ax, p, plane, fc=fc, ec=ec, lw=0.5, alpha=alpha * (0.5 if p.name.endswith(("stone", "tower")) else 0.9))


def sheet(fixed):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 3, figsize=(19, 12))
    home = sequence()[0]
    st = lambda **kw: {**home, **kw}
    # 1 top view
    a = ax[0, 0]; a.set_title("Top view: home + top level at turn 45 and 90 (hub at %g)" % L_SPIN)
    scene(a, fixed, (0, 1)); scene(a, collect(home, False), (0, 1), 0.3)
    for p_, al in ((45, 0.5), (90, 1.0)):
        s = st(L=L_SPIN, phi=dict(T=p_, M=0.0, B=0.0), held=dict(T=True, M=False, B=False))
        scene(a, collect(s, False), (0, 1), al, only=lambda p: p.grp.startswith(("FT", "RT")))
    a.set_xlim(-430, 430); a.set_ylim(-330, 330); a.set_aspect("equal"); a.grid(alpha=0.3)
    a.set_xlabel("x (robot's left = -x)"); a.set_ylabel("y (forward)")
    # 2 side view home
    a = ax[0, 1]; a.set_title("Side view (y-z), home: each level holds its stone at the middle of its face")
    scene(a, fixed, (1, 2), only=lambda p: isinstance(p, Cyl) or abs(p.c[0]) < 170)
    scene(a, collect(home, False), (1, 2))
    a.axhline(350, color="r", ls="--", lw=1); a.text(-320, 353, "350 [GR F.3]", color="r", fontsize=8)
    a.set_xlim(-330, 330); a.set_ylim(-10, 375); a.set_aspect("equal"); a.grid(alpha=0.3)
    # 3 cup height vs turn
    a = ax[0, 2]; a.set_title("Cup height vs ring turn (hub at %g)" % L_SPIN)
    ph = np.linspace(PARK, 90, 96)
    for lv in ("T", "M", "B"):
        a.plot(ph, [cup_z(lv, p, L_SPIN) for p in ph], label=NAMES[lv], color=COL[lv][0], lw=2)
    a.axhspan(169, 181, color="#e39b3a", alpha=0.25, label="spin-safe centre 169-181")
    a.set_xlabel("ring turn (deg)"); a.set_ylabel("cup z (mm)"); a.grid(alpha=0.3); a.legend()
    # 4 + 5 radial views of top and bottom arms
    for a, lv in ((ax[1, 0], "T"), (ax[1, 1], "B")):
        a.set_title("%s arm in its own plane (r-z) at turn 0 / 30 / 60 / 90" % NAMES[lv])
        for p_, al in ((0, 0.25), (30, 0.45), (60, 0.7), (90, 1.0)):
            Wi = W(p_).T
            for b in arm_parts(lv, "F", p_, 0.0, 0.0, True):
                if "rod" in b.grp: continue
                bl = Box(b.name, Wi @ b.c, b.h, Wi @ b.R, b.grp)
                fc, ec = style(b); draw(a, bl, (0, 2), fc=fc, ec=ec, lw=0.6, alpha=al * 0.8)
            if lv == "T":
                Bl = B_local(alpha_at("T", p_)); Al = Wi @ A_point(None, "F")
                a.plot([Bl[0], Al[0]], [Bl[2], Al[2]], color="k", lw=2, alpha=al)
        if lv == "B":
            for ph_ in np.arange(PARK, 91, 5.0):
                rl = roller_local(bottom_alpha(ph_)); a.plot([40, 54], [rl[2] + 5, rl[2] + 5], color="#456", lw=1)
        from matplotlib.patches import Rectangle
        a.add_patch(Rectangle((0, SPINE_Z[0]), R_SPINE, SPINE_Z[1] - SPINE_Z[0], fc="#9ab", alpha=0.6))
        a.axhline(0, color="k", lw=1)
        a.set_xlim(0, 310); a.set_ylim(-5, 345); a.set_aspect("equal"); a.grid(alpha=0.3)
        a.set_xlabel("r from hub axis"); a.set_ylabel("z (hub at 0)")
    # 6 front view: bottom stone spin + towers
    a = ax[1, 2]; a.set_title("Front view (x-z): bottom stone at spin height, spinning (hub %g)" % L_SPIN)
    scene(a, fixed, (0, 2), only=lambda p: isinstance(p, Cyl) or abs(p.c[1]) < 150)
    for sp_, al in ((0, 0.3), (45, 0.5), (90, 1.0)):
        s = st(L=L_SPIN, phi=dict(T=0.0, M=0.0, B=90.0), held=dict(T=False, M=False, B=True), spin=dict(T=0.0, M=0.0, B=sp_))
        scene(a, collect(s, False), (0, 2), al, only=lambda p: p.grp.startswith(("FB", "RB")) or p.grp == "spine")
    a.axhline(350, color="r", ls="--", lw=1); a.axhline(0, color="k", lw=1)
    a.set_xlim(-430, 430); a.set_ylim(-10, 375); a.set_aspect("equal"); a.grid(alpha=0.3)
    fig.suptitle("Central hub option C: per level 1 transfer servo (top: drag link, middle: plain turn, bottom: ramp cam) + 1 spin servo per cup; 1 hub-lift servo", fontsize=12)
    fig.tight_layout()
    os.makedirs(SIM, exist_ok=True)
    fig.savefig(os.path.join(SIM, "option_c_sheet.png"), dpi=95)
    plt.close(fig)


def gif(fixed, states):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    keep = states[::3]
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
        fig.suptitle("Central hub option C - " + s["label"])
    an = FuncAnimation(fig, frame, frames=len(keep))
    an.save(os.path.join(SIM, "option_c_sequence.gif"), writer=PillowWriter(fps=10))
    plt.close(fig)


if __name__ == "__main__":
    main()


