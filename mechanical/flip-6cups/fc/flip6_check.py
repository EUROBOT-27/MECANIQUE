# flip6_check.py - kinematic checks of the 6-cup flip (plain Python): floor clearance, height, transmission angle,
# pin <-> link crossings (the crank pin passes through the rocker layer, the rocker ground pin through the crank
# layer) and motor torque. Writes ../motion_report.txt.
#   python flip6_check.py

import math
import os

import flip6_params as P

G = 9.81
N = 600


def seg_dist(p, a, b):
    ax, az = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * az) / (ax * ax + az * az)))
    return math.dist(p, (a[0] + t * ax, a[1] + t * az))


def cog(pose, n_stacks):
    """Centre of mass (world XZ) and mass of plate assembly + stones."""
    pts = [((0.0, 0.0), P.M_PLATE_ASSY)] + [(s, P.M_STONE) for s in P.stones(n_stacks)]
    m = sum(w for _, w in pts)
    x = sum(P.to_world(pose, p)[0] * w for p, w in pts) / m
    z = sum(P.to_world(pose, p)[1] * w for p, w in pts) / m
    return (x, z), m


def run():
    rows, lines = [], []
    poses = [P.pose_at(i / N) for i in range(N + 1)]
    clear, top, mu_min, pin1, pin2 = 1e9, 0.0, 180.0, 1e9, 1e9
    torque = []
    for i, (pose, p1, p2) in enumerate(poses):
        zs = [c[1] for c in P.stack_corners(pose)]
        if math.radians(1) < pose[2] < math.radians(89):
            clear = min(clear, min(zs))
        top = max(top, max(zs))
        v1 = (p1[0] - p2[0], p1[1] - p2[1]); v2 = (P.O2[0] - p2[0], P.O2[1] - p2[1])
        m = math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))))))
        mu_min = min(mu_min, m, 180 - m)
        pin1 = min(pin1, seg_dist(p1, P.O2, p2))          # crank pin vs rocker bar
        pin2 = min(pin2, seg_dist(P.O2, P.O1, p1))        # rocker ground pin vs crank bar
        if i:
            (c0, mass), (c1, _) = cog(poses[i - 1][0], 1), cog(pose, 1)
            dphi = abs(P.SWEEP) / N
            torque.append(mass * G * (c1[1] - c0[1]) / 1000 / dphi)   # N.m at the crank (quasi-static)
    c6, m6 = cog(P.START, 2)
    # holding torque, 6 stones, start pose: virtual work with a tiny crank step
    pa = P.pose_at(1e-3)[0]
    c6b, _ = cog(pa, 2)
    hold6 = m6 * G * (c6b[1] - c6[1]) / 1000 / (abs(P.SWEEP) * 1e-3)
    tmax = max(abs(t) for t in torque)
    # JGB37-520 directly on the crank: motor torque = crank torque (its gearbox losses are in the rated value)
    t_flip = math.degrees(abs(P.SWEEP)) / (P.MOTOR_RPM * 6.0)
    # ejector: MG90S on a 25 mm finger (+ roller r 4), pushing a 90 g stone that stands on the table
    f_push = P.MG90_TORQUE / 0.029
    pinr = P.PIN_D / 2 + 1
    lines += [
        "6-cup flip - kinematic report (flip6_check.py)",
        "",
        "Four-bar: crank %.1f, rocker %.1f, coupler %.1f, ground link %.1f mm; crank travel %.1f deg" % (
            P.R1, P.R2, P.COUPLER, math.dist(P.O1, P.O2), math.degrees(abs(P.SWEEP))),
        "Ground pivots O1 (crank/motor) (%.1f, %.1f), O2 (rocker) (%.1f, %.1f) [x, z mm]" % (P.O1 + P.O2),
        "Start pose: stack centre (%.1f, %.1f), 0 deg.  End pose: (%.1f, %.1f), %.1f deg" % (
            P.START[0], P.START[1], P.END[0], P.END[1], math.degrees(P.END[2])),
        "",
        "Case A, 3 stones held from the middle (2 cups per stone), FLIP ALLOWED:",
        "  min floor clearance during the flip  %.1f mm (rule of thumb >= 4)" % clear,
        "  stones upright: bottom %.1f mm above the table, top %.1f mm" % (P.END_GAP, P.END_GAP + P.STONE_L),
        "  max height of the stones during the flip  %.1f mm  (> 350: see README, GR F.3)" % top,
        "  min transmission angle  %.1f deg (V2: 44)" % mu_min,
        "  peak torque at the crank = at the JGB37-520 (direct)  %.2f N.m; rated %.1f -> margin x%.1f, stall %.1f -> x%.1f" % (
            tmax, P.MOTOR_RATED, P.MOTOR_RATED / tmax, P.MOTOR_STALL, P.MOTOR_STALL / tmax),
        "  flip time at %.0f rpm (120 deg crank)  %.2f s" % (P.MOTOR_RPM, t_flip),
        "  ejector push (MG90S, 29 mm to the roller)  %.1f N (stone weight %.1f N)" % (f_push, P.M_STONE * G),
        "",
        "Case B, 6 stones (2 stacks end to end, gap %.0f mm), each held by 3 cups off-centre, NO FLIP:" % P.STACK_GAP,
        "  each stone held %.0f mm off its middle; load span %.0f mm" % (
            (P.STONE_L + P.STACK_GAP) / 2 - P.CUP_U, 2 * P.STONE_L + P.STACK_GAP),
        "  holding torque at the crank = at the motor (start pose)  %.2f N.m (rated %.1f -> x%.1f)" % (
            abs(hold6), P.MOTOR_RATED, P.MOTOR_RATED / abs(hold6)),
        "  height 330 mm (stack on the table)",
        "",
        "Pin crossings (links in separate layers, pins cross the other layer):",
        "  crank pin (P1) vs rocker bar centre line: min %.1f mm (needs > %.1f)  %s" % (
            pin1, LINK_HALF + pinr, "OK" if pin1 > LINK_HALF + pinr else "CLASH"),
        "  rocker ground pin (O2) vs crank bar centre line: min %.1f mm (needs > %.1f)  %s" % (
            pin2, LINK_HALF + pinr, "OK" if pin2 > LINK_HALF + pinr else "CLASH"),
    ]
    return lines, dict(clear=clear, top=top, mu=mu_min, pin1=pin1, pin2=pin2, tmax=tmax, hold6=hold6)


LINK_HALF = P.BOSS_D / 2

if __name__ == "__main__":
    lines, _ = run()
    txt = "\n".join(lines) + "\n"
    print(txt)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motion_report.txt"), "w") as f:
        f.write(txt)
