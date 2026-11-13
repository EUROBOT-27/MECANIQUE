# flip6_params.py - parameters + four-bar kinematics of the 6-cup flip mechanism (plain Python, no FreeCAD).
#
# Frame (same as base_330): X = robot width / wheel axis, Y = forward (the mechanism is on the +Y edge), Z = up,
# origin = robot centre on the table. The flip happens in the XZ plane (seen from the front, +Y looking back).
#
# Plate frame (u, v): origin = plate centre = centre of the 3-stone stack it holds, u along X and v along Z in the
# start pose (stones horizontal). The plate (four-bar coupler) turns by theta: 0 = start, +90 deg = stones upright.

import math

# ---------------------------------------------------------------- stones
STONE_L, STONE_W = 320.0, 110.0        # 320 x 110 x 110
STACK_GAP = 10.0                       # gap between the 2 stacks in the 6-stone case (end to end along X)
END_GAP = 8.8                          # upright stones end 8.8 mm above the table, then drop (as V2)

# ---------------------------------------------------------------- cups: 2 columns x 3 rows
CUP_U = 80.0                           # columns at u = +/-80 (quarter points of a centred stone)
CUP_V = (-110.0, 0.0, 110.0)           # one row per stone layer
# DP-S30 bellows cup (same cup as the clapets v7/v8 suction head: one stock of spares), in a printed TPU holder.
# Size from the v7 model (bellows Ø30 x 18): ASSUMED until the cups arrive (parts-library: "size ?").
CUP_D = 30.0                           # DP-S30 lip Ø
CUP_BELLOWS = 18.0                     # bellows length (free)
CUP_HOLDER = 17.0                      # TPU holder on the plate front: Ø20 body + side barb for the Ø4 hose
CUP_H = CUP_HOLDER + CUP_BELLOWS       # plate front face -> stone face = 35 (unchanged from the Ø50 concept)

# ---------------------------------------------------------------- actuators (real parts, see README "Actuators")
# Flip drive: JGB37-520 DC gear motor with Hall encoder, DIRECT on the crank (no extra gear stage).
# Datasheet values of the common JGB37-520 drawing - measure ours (parts-library: label not read yet).
JGB_BOX_D, JGB_BOX_L = 37.0, 26.5      # gearbox Ø37, length 26.5 (high-ratio versions; 19..26.5 depending on ratio)
JGB_MOT_D, JGB_MOT_L = 35.5, 33.0      # 520 motor can
JGB_ENC_D, JGB_ENC_L = 33.0, 17.0      # Hall encoder cap at the back
JGB_OFFSET = 7.0                       # output shaft is 7 mm off the gearbox axis (eccentric output)
JGB_BOSS_D, JGB_BOSS_L = 12.0, 5.0     # bearing boss around the shaft on the gearbox face
JGB_SHAFT_D, JGB_SHAFT_L = 6.0, 14.0   # Ø6 D-shaft past the boss
JGB_HOLES_R, JGB_HOLES_N = 15.5, 6     # M3 holes on the gearbox face, Ø31 circle around the GEARBOX axis
MOTOR_RATED = 1.0                      # N.m: pick the 12 V version rated >= 10 kg.cm (<= ~35 rpm out)
MOTOR_STALL = 2.5                      # N.m: typical stall of that version (check the label / seller table)
MOTOR_RPM = 30.0                       # loaded speed assumed for the flip time

# Ejectors: 3 x TowerPro MG90S (body 22.8 x 12.2 x 28.5 to the top of the case, ears 32.2 long, 2.5 thick,
# spline Ø4.8 x 4 with its axis 5.9 mm from one end of the body). 2.2 kg.cm at 4.8 V.
MG90_L, MG90_W, MG90_H = 22.8, 12.2, 28.5
MG90_EAR_L, MG90_EAR_T, MG90_EAR_Z = 32.2, 2.5, 15.9   # ear underside 15.9 above the case bottom
MG90_SHAFT_E = 5.9
MG90_TORQUE = 2.2 * 0.0981             # N.m

# Vacuum: 6 x 12 V mini pumps (Lextronic, Ø31.8 x 66) = one pump per cup, + 6 x mini 12 V 2-way NC vent valves
PUMP_D, PUMP_L = 31.8, 66.0
VALVE = (27.0, 14.0, 17.0)             # mini vent valve body (x, y, z) incl. the coil, approximate
CUPS = [(su * CUP_U, v) for su in (-1, 1) for v in CUP_V]   # cups 1-3 = left column, 4-6 = right column

# ---------------------------------------------------------------- four-bar (synthesised, see README)
O1 = (-34.765, 50.434)                 # crank ground pivot = gearbox shaft (on the column)
O2 = (-97.175, 244.733)                # rocker ground pivot (on the column)
P1 = (-97.285, -48.499)                # crank pin on the plate (plate frame)
P2 = (5.083, -28.904)                  # rocker pin on the plate (plate frame)
START = (0.0, 165.0, 0.0)              # plate pose (x, z, theta rad): stack resting on the table
END = (5.218, STONE_L / 2 + END_GAP, math.radians(90))

# ---------------------------------------------------------------- Y layers (mm)
Y_COL = (125.0, 130.0)                 # column, 5 mm aluminium
Y_CRANK = (133.0, 139.0)               # crank (red), 6 mm
Y_ROCK = (142.0, 148.0)                # rocker (blue), 6 mm
Y_PLATE = (152.0, 155.0)               # cup plate (purple), 3 mm aluminium
Y_STONE = Y_PLATE[1] + CUP_H           # stone face touching the cups
LINK_W = 18.0                          # link width (boss Ø24 at the joints)
BOSS_D = 24.0
PIN_D = 8.0                            # ISO 7379 Ø8 shoulder screws + 688ZZ (8x16x5)

# Plate outline (plate frame): 230 x 290, R12 corners
PLATE_U, PLATE_V, PLATE_R = 115.0, 145.0, 12.0

# Masses (kg) for the torque check
M_STONE = 0.090
M_PLATE_ASSY = 0.52                    # 3 mm alu plate ~0.34 + 6 DP-S30 + TPU holders ~0.07 + 3 MG90S 0.04
                                       # + servo brackets, fingers, hoses ~0.07

R1 = math.dist(O1, (START[0] + P1[0], START[1] + P1[1]))
R2 = math.dist(O2, (START[0] + P2[0], START[1] + P2[1]))
COUPLER = math.dist(P1, P2)


def rot(u, v, t):
    c, s = math.cos(t), math.sin(t)
    return (u * c - v * s, u * s + v * c)


def to_world(pose, p):
    a, b = rot(p[0], p[1], pose[2])
    return (pose[0] + a, pose[1] + b)


def _p2(P1w, prev):
    d = math.dist(O2, P1w)
    a = (R2 * R2 - COUPLER * COUPLER + d * d) / (2 * d)
    h = math.sqrt(max(R2 * R2 - a * a, 0.0))
    ex, ez = (P1w[0] - O2[0]) / d, (P1w[1] - O2[1]) / d
    mx, mz = O2[0] + a * ex, O2[1] + a * ez
    s1, s2 = (mx - h * ez, mz + h * ex), (mx + h * ez, mz - h * ex)
    return s1 if math.dist(s1, prev) <= math.dist(s2, prev) else s2


PHI0 = math.atan2(START[1] + P1[1] - O1[1], START[0] + P1[0] - O1[0])
_e = to_world(END, P1)
PHI1 = math.atan2(_e[1] - O1[1], _e[0] - O1[0])
SWEEP = ((PHI1 - PHI0) + math.pi) % (2 * math.pi) - math.pi   # crank travel start -> end (rad, negative = CW)


def pose_at(s, steps=None):
    """Plate pose for crank progress s in [0, 1] (0 = start, 1 = stones upright). Returns (x, z, theta), P1w, P2w."""
    n = max(2, int(abs(s) * 400) + 1)
    prev = to_world(START, P2)
    base = math.atan2(P2[1] - P1[1], P2[0] - P1[0])
    for i in range(1, n + 1):
        phi = PHI0 + SWEEP * s * i / n
        P1w = (O1[0] + R1 * math.cos(phi), O1[1] + R1 * math.sin(phi))
        prev = _p2(P1w, prev)
    P1w = (O1[0] + R1 * math.cos(PHI0 + SWEEP * s), O1[1] + R1 * math.sin(PHI0 + SWEEP * s))
    if s == 0:
        prev = to_world(START, P2)
    t = math.atan2(prev[1] - P1w[1], prev[0] - P1w[0]) - base
    a, b = rot(P1[0], P1[1], t)
    return (P1w[0] - a, P1w[1] - b, t), P1w, prev


def stack_corners(pose, n_stacks=1):
    """World XZ corners of the held stones' outline (1 centred stack, or 2 stacks end to end)."""
    hx = STONE_L / 2 if n_stacks == 1 else STONE_L + STACK_GAP / 2
    hz = 3 * STONE_W / 2
    return [to_world(pose, (sx * hx, sz * hz)) for sx in (-1, 1) for sz in (-1, 1)]


def stones(n_stacks):
    """Stone centres in the plate frame (u, v) and their long axis: list of (u, v)."""
    if n_stacks == 1:
        us = [0.0]
    else:
        us = [-(STONE_L + STACK_GAP) / 2, (STONE_L + STACK_GAP) / 2]
    return [(u, v) for u in us for v in CUP_V]


if __name__ == "__main__":
    print("crank %.1f, rocker %.1f, coupler %.1f, ground link %.1f, crank travel %.1f deg" % (
        R1, R2, COUPLER, math.dist(O1, O2), math.degrees(SWEEP)))
    for s in (0, 0.25, 0.5, 0.75, 1):
        p, a, b = pose_at(s)
        print(s, [round(v, 2) for v in p[:2]], round(math.degrees(p[2]), 2))
