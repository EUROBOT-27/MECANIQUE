# flipbar_check.py - range of motion + forces of the single-bar flip (plain Python; plots if matplotlib is there).
#   "C:/Program Files/FreeCAD 1.1/bin/python.exe" flipbar_check.py      (FreeCAD's Python has matplotlib + PIL)
# Writes ../motion_report.txt and, with matplotlib, ../../simulations/flip_bar/{range_of_motion.png, curves.png,
# flipbar_front.gif}.
import math
import os

import flipbar_params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SIM = os.path.normpath(os.path.join(ROOT, "..", "simulations", "flip_bar"))
DEG = math.degrees(abs(P.SWEEP))                     # 120 deg of crank = s 0 -> 1
STOP_S = P.STOP_PAST_DEG / DEG                       # hard stops, in s
ACT = P.actuator_points()
STONES = P.stone_corners()


def transmission(p1, p2):
    v1 = (p1[0] - p2[0], p1[1] - p2[1]); v2 = (P.O2[0] - p2[0], P.O2[1] - p2[1])
    c = (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))
    m = math.degrees(math.acos(max(-1.0, min(1.0, c))))
    return min(m, 180 - m)


def eval_pose(item):
    s, pose, p1, p2 = item
    act = [P.to_world(pose, q) for q in ACT]
    st = [P.to_world(pose, q) for q in STONES]
    return dict(s=s, pose=pose, p1=p1, p2=p2, theta=math.degrees(pose[2]),
                act_top=max(q[1] for q in act), act_low=min(q[1] for q in act),
                st_top=max(q[1] for q in st), st_low=min(q[1] for q in st),
                act_x=(min(q[0] for q in act), max(q[0] for q in act)), mu=transmission(p1, p2))


# ---------------------------------------------------------------- 1. full mobility of the four-bar (toggle limits)
def find_limit(direction):
    s, step = 0.0, 0.01
    prev = P.to_world(P.START, P.P2)
    while step > 1e-5:
        r = P.pose_at_phi(P.PHI0 + P.SWEEP * (s + direction * step), prev)
        if r is None:
            step /= 2
        else:
            s += direction * step
            prev = r[2]
        if abs(s) > 5:
            return None
    return s


S_LO, S_HI = find_limit(-1), find_limit(+1)

# ---------------------------------------------------------------- 2. sweep over the used range + hard-stop over-travel
N = 1200
path = [eval_pose(it) for it in P.sweep_path(-STOP_S, 1 + STOP_S, N) if it[1] is not None]
dphi = abs(P.SWEEP) * (1 + 2 * STOP_S) / N


def torques(with_stones):
    """Quasi-static torque at the crank (N.m) = d(potential)/d(crank angle), + = motor lifts toward upright."""
    pe = [P.potential(p["pose"], p["p1"], p["p2"], 0, with_stones) for p in path]
    return [(pe[min(i + 1, len(pe) - 1)] - pe[max(i - 1, 0)]) / (dphi * (min(i + 1, len(pe) - 1) - max(i - 1, 0)))
            for i in range(len(pe))]


T_st, T_empty = torques(True), torques(False)


def inertia_J():
    """Reflected inertia at the crank J(phi) (kg.m2): bodies' COG speeds + rotations + motor rotor x ratio^2."""
    I_stack = 3 * P.STONE_M * (0.320 ** 2 + 0.330 ** 2) / 12
    I_bar = P.M_BAR_ASSY * (0.06 ** 2 + 0.25 ** 2) / 12
    J = []
    for i in range(len(path)):
        a, b = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        dp = dphi * (min(i + 1, len(path) - 1) - max(i - 1, 0))
        ba = P.cog_world(a["pose"], a["p1"], a["p2"], 0); bb = P.cog_world(b["pose"], b["p1"], b["p2"], 0)
        j = sum(m * ((cb[0] - ca[0]) ** 2 + (cb[1] - ca[1]) ** 2) / 1e6 / dp ** 2 for (m, ca), (_, cb) in zip(ba, bb))
        dth = (b["pose"][2] - a["pose"][2]) / dp
        j += (I_stack + I_bar) * dth ** 2 + (P.M_CRANK / 3 + P.M_CRANK_P1) * (P.R1 / 1000) ** 2
        j += P.MOTOR["inertia"] * P.RATIO ** 2
        J.append(j)
    return J


J = inertia_J()


def profile(T, frac=0.25):
    """Trapezoid crank-speed profile over s 0 -> 1 in T seconds: phi_dot, phi_ddot at each path index."""
    Th = abs(P.SWEEP); ta = frac * T
    vmax = Th / (T - ta); acc = vmax / ta
    out = []
    for p in path:
        x = max(0.0, min(1.0, p["s"])) * Th
        if x < 0.5 * acc * ta * ta:
            v, a = math.sqrt(2 * acc * x), acc
        elif x > Th - 0.5 * acc * ta * ta:
            v, a = math.sqrt(max(2 * acc * (Th - x), 0.0)), -acc
        else:
            v, a = vmax, 0.0
        out.append((v, a))
    return out, vmax


def motor_side(t_crank):
    """Torque the motor must give (N.m): drives through the gears, or brakes when the load drives."""
    return t_crank / (P.RATIO * P.ETA) if t_crank >= 0 else t_crank * P.ETA / P.RATIO


def usable(rpm):
    """Assumed usable torque of the 17HS4401S at ~1 A, 24 V: 0.20 N.m up to 300 rpm, down to 0.12 at 600 rpm."""
    return P.MOTOR_USABLE if rpm <= 300 else max(0.0, P.MOTOR_USABLE - (rpm - 300) * 0.08 / 300)


# ---------------------------------------------------------------- 3. pin forces (bar = 3-force body, rocker = 2-force)
def pin_forces(p, with_stones=True):
    pose, p1, p2 = p["pose"], p["p1"], p["p2"]
    bodies = [(P.M_BAR_ASSY, P.to_world(pose, (0.0, -10.0)))]
    if with_stones:
        bodies += [(P.STONE_M, P.to_world(pose, (0.0, v))) for v in P.STONE_V]
    m = sum(b[0] for b in bodies)
    cx = sum(b[0] * b[1][0] for b in bodies) / m; cz = sum(b[0] * b[1][1] for b in bodies) / m
    W = (0.0, -m * P.G)
    u = (p2[0] - P.O2[0], p2[1] - P.O2[1]); L = math.hypot(*u); u = (u[0] / L, u[1] / L)
    cr = lambda a, b: a[0] * b[1] - a[1] * b[0]
    f = -cr((cx - p1[0], cz - p1[1]), W) / cr((p2[0] - p1[0], p2[1] - p1[1]), u)
    F1 = (-(f * u[0] + W[0]), -(f * u[1] + W[1]))
    return math.hypot(*F1), abs(f)


F = [pin_forces(p) for p in path]

# ---------------------------------------------------------------- report
used = [p for p in path if 0 <= p["s"] <= 1]
iu = [i for i, p in enumerate(path) if 0 <= p["s"] <= 1]
L = []
L.append("Single-bar flip - range of motion + forces (flipbar_check.py, %s)" % "2026-11-18")
L.append("")
L.append("== Four-bar (Ayoub's flip-6cups synthesis): crank %.1f, rocker %.1f, coupler %.1f, ground %.1f mm" % (
    P.R1, P.R2, P.COUPLER, P.GROUND))
L.append("   non-Grashof (295.0 > 253.4): no link can turn fully; the crank swings between two toggle positions")
L.append("   used travel: crank %.1f deg (s 0 = stack on the table, s 1 = stones upright %.1f mm above it), bar 0 -> 90 deg" % (
    DEG, P.END_GAP))
if S_LO is not None and S_HI is not None:
    L.append("   toggle limits (linkage locks): s %.3f (crank %.1f deg before the start) and s %.3f (%.1f deg past upright)" % (
        S_LO, -S_LO * DEG, S_HI, (S_HI - 1) * DEG))
L.append("   hard stops (rubber, on the column, crank layer): %.1f deg past each end = s %.3f / %.3f -> %.1f / %.1f deg from the toggles" % (
    P.STOP_PAST_DEG, -STOP_S, 1 + STOP_S, (S_LO is not None and (-STOP_S - S_LO) * DEG) or 0,
    (S_HI is not None and (S_HI - 1 - STOP_S) * DEG) or 0))
L.append("")
L.append("== Geometry over the travel (s 0 -> 1), and at the hard stops")
mu_min = min(p["mu"] for p in used)
L.append("   transmission angle  min %.1f deg (>= 40 good) at s %.2f; at the stops %.1f / %.1f deg" % (
    mu_min, min(used, key=lambda p: p["mu"])["s"], path[0]["mu"], path[-1]["mu"]))
top = max(path, key=lambda p: p["act_top"])
L.append("   ACTUATORS highest point  %.1f mm at s %.2f (bar %.1f deg)  -> %s (limit 350, game rules E.1)" % (
    top["act_top"], top["s"], top["theta"], "OK, margin %.1f" % (350 - top["act_top"]) if top["act_top"] <= 350 else "OVER"))
L.append("   actuators lowest point   %.1f mm (above the table)" % min(p["act_low"] for p in path))
L.append("   stones highest  %.1f mm at s %.2f (game elements may pass 350 in the castle / construction zones only)" % (
    max(p["st_top"] for p in used), max(used, key=lambda p: p["st_top"])["s"]))
mid = [p for p in used if 1.0 < p["theta"] < 89.0]
L.append("   stones lowest during the flip  %.1f mm (bar between 1 and 89 deg, as flip-6cups; at s 0 they rest on the table)" % min(p["st_low"] for p in mid))
L.append("   actuators X span over the travel: %.1f .. %.1f mm (bar + stations; the stones don't count, FAQ Q1)" % (
    min(p["act_x"][0] for p in path), max(p["act_x"][1] for p in path)))
L.append("")
L.append("== Torque (quasi-static, gravity; masses from the CAD: bar assembly %.3f, crank %.3f, rocker %.3f, stones 3 x %.3f kg)" % (
    P.M_BAR_ASSY, P.M_CRANK + P.M_CRANK_P1, P.M_ROCKER + P.M_ROCKER_P2, P.STONE_M))
for name, T in (("with 3 stones", T_st), ("empty (stones released)", T_empty)):
    tu = [T[i] for i in iu]
    imax, imin = max(iu, key=lambda i: T[i]), min(iu, key=lambda i: T[i])
    L.append("   %-24s crank: lift peak %+.2f N.m (s %.2f), brake peak %+.2f N.m (s %.2f); sign changes at s %s" % (
        name, T[imax], path[imax]["s"], T[imin], path[imin]["s"],
        ", ".join("%.2f" % path[i]["s"] for i in iu[1:] if (T[i] > 0) != (T[i - 1] > 0)) or "never"))
L.append("   unpowered (gears back-drive): with the torque > 0 the bar falls back toward the start, < 0 it falls toward")
L.append("   upright -> rests on the hard stop there. The stops take the full load: %.2f N.m with stones." % max(abs(t) for t in T_st))
L.append("")
L.append("== Drive: %s, one spur pair %dT pinion -> %dT sector = %.2f:1, module %.1f, %.0f mm wide, printed ABS, efficiency %.2f" % (
    P.MOTOR["name"], P.Z_PINION, P.Z_WHEEL, P.RATIO, P.GEAR_M, P.GEAR_W, P.ETA))
L.append("   motor: holding %.2f N.m at %.1f A (datasheet, CHECK the label); driven at ~%.1f A -> usable %.2f N.m up to 300 rpm (assumed)" % (
    P.MOTOR["hold"], P.MOTOR["rated_a"], P.DRIVER_A, P.MOTOR_USABLE))
L.append("   resolution: %d microsteps -> %.4f deg of crank per microstep (%.0f microsteps per crank degree)" % (
    P.MICROSTEPS, P.MOTOR["step_deg"] / P.MICROSTEPS / P.RATIO, P.RATIO * P.MICROSTEPS / P.MOTOR["step_deg"]))
for Tf in (0.6, 1.0, 1.5):
    prof, vmax = profile(Tf)
    need, worst = [], (0, 0, 0)
    for i in iu:
        v, a = prof[i]
        jp = (J[min(i + 1, len(J) - 1)] - J[max(i - 1, 0)]) / (dphi * 2)
        tc = T_st[i] + J[i] * a + 0.5 * jp * v * v
        tm = abs(motor_side(tc))
        rpm = v / (2 * math.pi) * 60 * P.RATIO
        marg = usable(rpm) / tm if tm > 1e-6 else 99
        if worst[0] == 0 or marg < worst[0]:
            worst = (marg, path[i]["s"], tm)
        need.append(tm)
    rpm_max = vmax / (2 * math.pi) * 60 * P.RATIO
    L.append("   flip in %.1f s (trapezoid, 25%% ramps): motor up to %.0f rpm, peak motor torque %.3f N.m, worst margin x%.2f at s %.2f %s" % (
        Tf, rpm_max, max(need), worst[0], worst[1], "OK" if worst[0] >= 1.5 else ("TIGHT" if worst[0] >= 1.0 else "TOO WEAK")))
hold = max(abs(motor_side(T_st[i])) for i in iu)
L.append("   holding (powered, standstill): worst %.3f N.m at the motor = %.0f%% of the usable torque" % (hold, 100 * hold / P.MOTOR_USABLE))
tc_peak = max(abs(t) for t in T_st) * 1.3            # + inertia/hoses margin
ft = tc_peak / (P.GEAR_M * P.Z_WHEEL / 2 / 1000)
sig = ft / (P.GEAR_W * P.GEAR_M * P.LEWIS_Y[P.Z_PINION])
L.append("   teeth: crank torque %.2f N.m (peak x1.3), tooth force %.0f N, pinion root stress %.1f MPa (Lewis) -> x%.1f vs ABS ~%d MPa" % (
    tc_peak, ft, sig, P.ABS_YIELD / sig, P.ABS_YIELD))
bl = P.BACKLASH / (P.GEAR_M * P.Z_WHEEL / 2)
L.append("   backlash at the crank: ~%.2f deg (%.2f mm designed); crossed where the torque changes sign (slow down there)" % (
    math.degrees(bl), P.BACKLASH))
b0, b1 = P.sector_span()
r_tip = P.GEAR_M * (P.Z_WHEEL / 2 + 1)
a_lo = min(math.degrees(P.PHI0), math.degrees(P.PHI1)) - P.STOP_PAST_DEG
a_hi = max(math.degrees(P.PHI0), math.degrees(P.PHI1)) + P.STOP_PAST_DEG
low = min(P.O1[1] + r_tip * math.sin(math.radians(b + ph)) for ph in [a_lo + (a_hi - a_lo) * k / 60 for k in range(61)]
          for b in [b0 + (b1 - b0) * k / 140 for k in range(141)])
L.append("   sector: %.0f deg of teeth (%.0f of the %d), tip r %.1f; lowest tooth tip over the travel z %.1f (base top %.1f: %.1f mm clear)" % (
    b1 - b0, (b1 - b0) / 360 * P.Z_WHEEL, P.Z_WHEEL, r_tip, low, P.BASE_TOP, low - P.BASE_TOP))
L.append("   gear layout: crank sector on O1 (%.1f, %.1f), motor pinion (%.1f, %.1f), centres %.1f mm apart" % (
    P.O1[0], P.O1[1], P.M_POS[0], P.M_POS[1], P.CD))
L.append("")
L.append("== Joints")
L.append("   pin forces (with stones): crank pin / crank shaft max %.1f N, rocker max %.1f N (in-plane)" % (
    max(f[0] for f in F), max(f[1] for f in F)))
y_st = P.Y_STONE + P.STONE_W / 2; y_link = (P.CRANK[0] + P.ROCK[1]) / 2; y_bar = (P.BAR[0] + P.Y_STATION[1]) / 2
M_out = (3 * P.STONE_M * (y_st - y_link) + P.M_BAR_ASSY * (y_bar - y_link)) * P.G / 1000
L.append("   out-of-plane moment (stones' COG %.0f mm in front of the link mid-plane y %.0f): %.2f N.m" % (y_st - y_link, y_link, M_out))
for name, span in (("crank shaft, 608 in rear plate + column", P.COL[0] + 3.5 - (P.REAR[1] + 3.5)),
                   ("P1 / P2 / O2 hubs, two 608 back to back", 7.0)):
    L.append("   -> %-40s bearings %.0f mm apart: pair force %.0f N each (608 static rating 1370 N)" % (name, span, M_out / (span / 1000)))
L.append("   in-plane friction: 608 (mu ~0.003) x %.0f N x 4 mm = %.4f N.m per joint (negligible)" % (
    max(f[0] for f in F), 0.003 * max(f[0] for f in F) * 0.004))
(_eu, _ev), _ey = P.hose_exit()
_vp = P.VALVE_PORT
_hd = [math.dist(P.to_world(p["pose"], (_eu, _ev)) + (_ey,), (_vp[0], _vp[2], _vp[1])) for p in path]
_loop = math.ceil(max(_hd) * 1.25 / 10) * 10
L.append("")
L.append("== Hoses (3 x D4): tied on the 3 bar anchors, they leave the bar under the bottom anchor (bar frame u %.0f, v %.0f)" % (_eu, _ev))
L.append("   straight distance from that point to the middle vent valve over the travel: %.0f mm (s %.2f) .. %.0f mm (s %.2f)" % (
    min(_hd), path[_hd.index(min(_hd))]["s"], max(_hd), path[_hd.index(max(_hd))]["s"]))
L.append("   -> free loop of %.0f mm (longest distance x 1.25): %.0f mm of slack at the closest pose. To try with real hoses." % (
    _loop, _loop - min(_hd)))

txt = "\n".join(L) + "\n"
print(txt)
open(os.path.join(ROOT, "motion_report.txt"), "w", encoding="utf-8").write(txt)

# ---------------------------------------------------------------- plots + GIF (FreeCAD's Python)
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Circle, PathPatch
    from matplotlib.path import Path
except ImportError:
    raise SystemExit("matplotlib not found: run with FreeCAD's python.exe for the plots")

os.makedirs(SIM, exist_ok=True)


def circle_pts(u, v, r, n=28):
    return [(u + r * math.cos(2 * math.pi * i / n), v + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def slot_pts(a, b, w, n=12):
    import cmath
    d = complex(b[0] - a[0], b[1] - a[1]); d /= abs(d); r = w / 2
    pts = []
    for c, a0 in ((b, -90), (a, 90)):
        for i in range(n + 1):
            z = complex(*c) + r * d * cmath.exp(1j * math.radians(a0 + 180 * i / n))
            pts.append((z.real, z.imag))
    return pts


def bar_holes_pts():
    out = []
    for h in P.bar_holes():
        out.append(circle_pts(h[1], h[2], h[3] / 2, 16) if h[0] == "circle" else slot_pts(h[1], h[2], h[3]))
    return out


def bar_shapes():
    """Bar-frame drawing items: (kind, outline, holes)."""
    out = [("bar", P.bar_outline(), bar_holes_pts())]
    for u, v, r in P.station_circles():
        out.append(("ring", circle_pts(u, v, r, 40), [circle_pts(u, v, P.ST_R_WALL, 40)]))
        out.append(("tpu", circle_pts(u, v, P.ST_R_WALL, 40), [circle_pts(u, v, P.CUP_D / 2 + 0.5, 30)]))
        out.append(("cup", circle_pts(u, v, P.CUP_D / 2, 30), [circle_pts(u, v, 2.5, 10)]))
    return out


BS = bar_shapes()
LINK_SHAPES = {}
for _L in (P.R1, P.R2):
    _sl = P.link_slot(_L)
    LINK_SHAPES[_L] = (P.link_outline(_L), ([slot_pts((_sl[0], 0), (_sl[1], 0), _sl[2])] if _sl else []) +
                       [circle_pts(0, 0, 4, 12), circle_pts(_L, 0, 4, 12)])
COL = {"bar": "#2c4f8c", "ring": "#3a3a40", "tpu": "#2fa34f", "cup": "#111111", "stone": "#d2b48c",
       "crank": "#c0392b", "rocker": "#2a62d4", "frame": "#c8ccd4"}


def shape_patch(outer, holes, fc, alpha, z):
    verts, codes = [], []
    for k, ring in enumerate([outer] + holes):
        ring = list(ring) if k == 0 else list(reversed(ring)) if _area(ring) > 0 else list(ring)
        if k == 0 and _area(ring) < 0:
            ring = ring[::-1]
        verts += ring + [ring[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(ring) - 1) + [Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), fc=fc, ec="#00000055", lw=0.4, alpha=alpha, zorder=z)


def _area(r):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]))


def link_poly(a, b, w=18.0):
    dx, dz = b[0] - a[0], b[1] - a[1]; L_ = math.hypot(dx, dz); nx, nz = -dz / L_ * w / 2, dx / L_ * w / 2
    return [(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)]


def draw_frame(ax):
    x0, x1 = P.FRAME_X[0], P.COLUMN_X1
    ax.add_patch(Polygon([(x0, P.BASE_TOP), (x1, P.BASE_TOP), (x1, P.FRAME_Z1), (x0, P.FRAME_Z1)], closed=True,
                         fc=COL["frame"], ec="#888", lw=0.6, alpha=0.5, zorder=1))
    ax.add_patch(Polygon([(-165, P.BASE_Z), (165, P.BASE_Z), (165, P.BASE_TOP), (-165, P.BASE_TOP)], closed=True,
                         fc="#dcc79a", ec="#9a8455", lw=0.6, zorder=1))
    ax.axhline(0, color="#555", lw=1.2, zorder=0)
    ax.axhline(350, color="#d01010", lw=1.0, ls="--", zorder=0)
    ax.text(250, 353, "350 mm (actuators)", color="#d01010", fontsize=7, ha="right", va="bottom")


def draw_gears(ax, phi_rel, alpha=1.0):
    """Sector pitch arc (turns with the crank) + pinion pitch circle with a mark (crank turned phi_rel from the start)."""
    rw, rp = P.GEAR_M * P.Z_WHEEL / 2, P.GEAR_M * P.Z_PINION / 2
    b0, b1 = P.sector_span()
    ph = P.PHI0 + phi_rel
    arc = [(P.O1[0] + rw * math.cos(math.radians(b0 + (b1 - b0) * k / 40) + ph),
            P.O1[1] + rw * math.sin(math.radians(b0 + (b1 - b0) * k / 40) + ph)) for k in range(41)]
    ax.add_patch(Polygon([P.O1] + arc, closed=True, fc="#f2c14e", ec="#8a6a10", lw=0.8, alpha=0.55 * alpha, zorder=2))
    rot_ = -phi_rel * P.RATIO
    ax.add_patch(Circle(P.M_POS, rp, fc="#f2c14e", ec="#8a6a10", lw=0.8, alpha=alpha, zorder=2))
    ax.plot([P.M_POS[0], P.M_POS[0] + rp * math.cos(rot_)], [P.M_POS[1], P.M_POS[1] + rp * math.sin(rot_)],
            color="#4a4a4a", lw=0.8, alpha=alpha, zorder=2)
    m = P.MOTOR["body"] / 2
    ax.add_patch(Polygon([(P.M_POS[0] - m, P.M_POS[1] - m), (P.M_POS[0] + m, P.M_POS[1] - m), (P.M_POS[0] + m, P.M_POS[1] + m),
                          (P.M_POS[0] - m, P.M_POS[1] + m)], closed=True, fill=False, ec="#222", lw=0.8, ls=":", alpha=alpha, zorder=2))


def draw_pose(ax, p, alpha=1.0, stones=True, lw=0.6):
    pose = p["pose"]
    if stones:
        for v in P.STONE_V:
            q = [P.to_world(pose, c) for c in ((-160, v - 55), (160, v - 55), (160, v + 55), (-160, v + 55))]
            ax.add_patch(Polygon(q, closed=True, fc=COL["stone"], ec="#8a6a3a", lw=lw, alpha=0.55 * alpha, zorder=3))
    for (o, q, L_, kind) in ((P.O1, p["p1"], P.R1, "crank"), (P.O2, p["p2"], P.R2, "rocker")):
        lp = (o[0], o[1], math.atan2(q[1] - o[1], q[0] - o[0]))
        outer, holes = LINK_SHAPES[L_]
        ax.add_patch(shape_patch([P.to_world(lp, c) for c in outer], [[P.to_world(lp, c) for c in h] for h in holes],
                                 COL[kind], alpha, 4))
    for z, (kind, outer, holes) in enumerate(BS):
        ax.add_patch(shape_patch([P.to_world(pose, c) for c in outer], [[P.to_world(pose, c) for c in h] for h in holes],
                                 COL[kind], 0.95 * alpha, 5 + 0.01 * z))
    for c in (P.O1, P.O2, p["p1"], p["p2"]):
        ax.add_patch(Circle(c, 4, fc="white", ec="#333", lw=0.6, alpha=alpha, zorder=7))


def setup(ax, title):
    ax.set_aspect("equal"); ax.set_xlim(-280, 280); ax.set_ylim(-15, 500)
    ax.set_title(title, fontsize=10); ax.tick_params(labelsize=7); ax.grid(color="#e4e4e4", lw=0.6); ax.set_axisbelow(True)
    ax.set_xlabel("X (mm), seen from the front (+Y looking back)", fontsize=8); ax.set_ylabel("Z (mm)", fontsize=8)


# 1. range of motion: 4 key poses
st_top = max(used, key=lambda p: p["st_top"])
keys = [(min(path, key=lambda p: abs(p["s"])), "start (s 0): stack on the table"),
        (top, "highest actuator point: %.1f mm" % top["act_top"]),
        (st_top, "stones highest: %.0f mm (castle only)" % st_top["st_top"]),
        (min(path, key=lambda p: abs(p["s"] - 1)), "upright (s 1): stones %.1f mm above the table" % P.END_GAP)]
fig, axs = plt.subplots(2, 2, figsize=(12, 11))
for ax, (p, lab) in zip([a for row in axs for a in row], keys):
    draw_frame(ax); draw_gears(ax, p["s"] * P.SWEEP * -1)
    draw_pose(ax, p)
    ax.plot([q["pose"][0] for q in path], [q["pose"][1] for q in path], color="#333", lw=0.8, ls="--", zorder=8)
    setup(ax, "crank %.0f deg, bar %.1f deg: %s" % (p["s"] * DEG, p["theta"], lab))
fig.suptitle("Single-bar flip, range of motion (front view). Dashed: stack centre path. Min transmission angle %.1f deg" % mu_min,
             fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(os.path.join(SIM, "range_of_motion.png"), dpi=120); plt.close(fig)

# 2. curves vs crank angle
ca = [p["s"] * DEG for p in path]
fig, axs = plt.subplots(2, 2, figsize=(11, 7.5))
a = axs[0][0]; a.plot(ca, [p["theta"] for p in path], color="#7a4fc9"); a.set_ylabel("bar angle (deg)")
a.set_title("Bar angle vs crank angle", fontsize=9)
a = axs[0][1]; a.plot(ca, [p["act_top"] for p in path], label="actuators, highest point", color="#7a4fc9")
a.plot(ca, [p["st_top"] for p in path], label="stones, top", color="#b08a50")
a.plot(ca, [p["st_low"] for p in path], label="stones, lowest point", color="#b08a50", ls=":")
a.axhline(350, color="#d01010", ls="--", lw=0.8); a.axhline(0, color="#555", lw=0.8)
a.legend(fontsize=7); a.set_title("Heights (mm)", fontsize=9)
a = axs[1][0]; a.plot(ca, [p["mu"] for p in path], color="#2a62d4"); a.axhline(40, color="#d01010", ls="--", lw=0.8)
a.set_title("Transmission angle (deg, keep >= 40)", fontsize=9)
a = axs[1][1]
for Tf, col in ((0.6, "#d43a2a"), (1.0, "#e0a020"), (1.5, "#3a9a52")):
    prof, vmax = profile(Tf)
    tm = []
    for i in range(len(path)):
        v, acc = prof[i]
        jp = (J[min(i + 1, len(J) - 1)] - J[max(i - 1, 0)]) / (dphi * 2)
        tm.append(abs(motor_side(T_st[i] + J[i] * acc + 0.5 * jp * v * v)))
    a.plot(ca, tm, color=col, label="flip in %.1f s" % Tf)
a.plot(ca, [abs(motor_side(t)) for t in T_st], color="#333", ls=":", label="static (holding)")
a.axhline(P.MOTOR_USABLE, color="#d01010", ls="--", lw=0.8, label="usable %.2f N.m" % P.MOTOR_USABLE)
a.legend(fontsize=7); a.set_title("Torque at the motor (N.m), %.2f:1, with 3 stones" % P.RATIO, fontsize=9)
for row in axs:
    for a in row:
        a.set_xlabel("crank angle from the start (deg)", fontsize=8); a.tick_params(labelsize=7); a.grid(color="#e4e4e4", lw=0.6)
        a.axvspan(-P.STOP_PAST_DEG, 0, color="#00000010"); a.axvspan(DEG, DEG + P.STOP_PAST_DEG, color="#00000010")
fig.tight_layout(); fig.savefig(os.path.join(SIM, "curves.png"), dpi=130); plt.close(fig)

# 3. GIF: start -> upright -> release top stone -> back to the start
from PIL import Image
import io
frames = []
seq = [k / 30 for k in range(31)] + [1.0] * 6 + [1 - k / 30 for k in range(31)]
for n, s in enumerate(seq):
    i = min(range(len(path)), key=lambda j: abs(path[j]["s"] - s))
    fig, ax = plt.subplots(figsize=(6, 5.6))
    draw_frame(ax); draw_gears(ax, path[i]["s"] * P.SWEEP * -1)
    draw_pose(ax, path[i], stones=n < 34)
    if n >= 34 and n < 37:     # released stones standing on the table
        for v in P.STONE_V:
            q = [P.to_world(path[i]["pose"], c) for c in ((-160, v - 55), (160, v - 55), (160, v + 55), (-160, v + 55))]
            q = [(x, z - P.END_GAP) for x, z in q]
            ax.add_patch(Polygon(q, closed=True, fc=COL["stone"], ec="#8a6a3a", lw=0.6, alpha=0.55, zorder=3))
    setup(ax, "Single-bar flip, crank %.0f deg, bar %.0f deg, top %.0f mm" % (
        path[i]["s"] * DEG, path[i]["theta"], path[i]["act_top"]))
    buf = io.BytesIO(); fig.savefig(buf, dpi=80); plt.close(fig); buf.seek(0)
    frames.append(Image.open(buf).convert("P", palette=Image.ADAPTIVE))
frames[0].save(os.path.join(SIM, "flipbar_front.gif"), save_all=True, append_images=frames[1:], duration=70, loop=0)
print("plots ->", SIM)
