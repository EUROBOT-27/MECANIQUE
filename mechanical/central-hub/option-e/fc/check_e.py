# check_e.py - central hub option E, doubled (Ayoub, 2026-11-19, proposal).
# Two units, front + back, around one fixed column at the robot centre. Each unit:
#   - a TURRET turning 0 -> 90 deg about the column (front: toward the robot's left, back: toward its right),
#     MG996R + printed 2:1 gears, hard stops at 0 and 90;
#   - ONE CARRIAGE on the turret, T8 lead screw + one 8 mm guide rod, NEMA17 on the turret top plate (GT2 belt 1:1);
#     the carriage carries the SPIN MG996R and the shaft cup (VS2-S30) that takes one stone at a time;
#   - a HOLDER FRAME (no doors: doors break the 1400 mm deployed perimeter when doubled): 2 columns at x = +-100 with
#     one VS2-S30 per lower stone on each column (2 cups per stone, centred), lifted 15 mm by an MG90S to carry.
# Order per unit: top -> middle -> bottom, each: lift above the holder cups, turn 90, down, spin 90 (stands up),
# set down, vent, rise along the tower face, turn back. The robot drives on between towers.
#
# Plain Python (numpy + matplotlib + Pillow), oriented boxes, same level as ../../fc/check_c.py.
# Frame as options A-D: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table.
# Base (2026-11-20, Ayoub: "the mechanism must fit the base, keep the base as it is"): mechanical/base_330_js, unchanged:
# plate 336 x 260 x 5 (z 11.5-16.5), 37D motors on hinges, JSUMO wheels (worst-case envelope), 2 odometry modules
# (AMT102 + swing arm, x 132-167), 4 KSM15 ball units at (+-130, +-105). The layout-v1 version of option E is kept in
# CAD_FC/layout-v1/ (snapshot). Perimeter limits are reported but not designed for in this version (Ayoub, 2026-11-20).
# Run from mechanical/central-hub/option-e/:
#   python fc/check_e.py          -> hub_e_report.txt
#   python fc/check_e.py --gif    -> also ../../simulations/central_hub/option_e_sequence.gif + option_e_sheet.png
import os
import sys
import itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIM = os.path.join(ROOT, "..", "..", "simulations", "central_hub")
MARGIN = 3.0

# ================================================================== numbers (mm, deg)
STONE = np.array([320.0, 110.0, 110.0])          # nominal [G D.4]; worst 324 x 115 (see the report)
BODY_W, BODY_D, CHAMFER = 168.0, 130.0, 0.0      # half width (X), half depth (Y): base_330_js plate 336 x 260
FLOOR_Z = (11.5, 16.5)                           # base_330_js plate (nominal Ø74 JSUMO wheel)
FACE = 171.0                                     # stack face = cup faces, from the column axis. >= 163 so that a stone
                                                 # lying beside the robot (y +-160) clears the other unit's stack, and
                                                 # 3 mm past the plate edge (168) so a tower stands beside the plate
DF = FACE - 168.0                                # outer carriage + holder parts moved out by this (layout-v1: 168)
RC = FACE + STONE[1] / 2                         # 223 stone centre radius
Z_ST = {"T": 275.0, "M": 165.0, "B": 55.0}       # stone centres, stack on the table
L_CARRY = 15.0                                   # holder lift + carriage, while carrying
HOLD_X, HOLD_TOP = 100.0, 185.0                  # holder columns at t = +-100; column top (z, holder down)
Z_TURN_TOP = 283.0                               # top stone turns 8 mm above the stack
Z_TURN = 250.0                                   # middle / bottom stone turns here: bottom 195 > holder cups (180)
Z_SPIN, Z_SET = 174.0, 160.0                     # spin height (corners clear the table), tower set down
DRIVE = 340.0                                    # robot drives on between towers
UNITS = {"F": dict(phi0=0.0, zb=65.5, zh=65.5, zt=335.0, zht=335.0),     # zb arm / zh hub of the bottom plate
         "R": dict(phi0=180.0, zb=65.5, zh=80.0, zt=335.0, zht=326.0)}   # zt / zht: top plate arm / hub
# base_330_js: the 37D motors reach z 62.5 (x 15-74.5, y +-18.5), the JSUMO envelope z 77 (x 79-131, y +-40). The
# turret's lower arm turns over them at 90 deg: arm at z 65.5 (3 mm over the motors), bottom pad at r <= 76 (3 mm
# inside the wheel envelope). Lift: zc 55 (bottom stone) .. 290 (carry, top stone) with the block 16.5 above the cup
# axis and 27.5 tall -> block 71.5 .. 334 between the bottom pad (70.5) and the top plate (335).
# Both turrets' arms are at the same level (the carriage must reach the bottom stone); their hubs are stacked on the
# column, joined to the arm by a web (r 15-34) + a riser at r 34-40. No gear reaches r 34, and the pinions sit at
# polar -35 / 145, where no riser ever passes.
RISER_R, WEB_R = (34.0, 40.0), (15.0, 34.0)
PLATE_T = 5.0                                    # the rear plates step (riser) from their hub to the arm level
R_COL = 10.0                                     # fixed column: 20 mm aluminium tube, beacon support on its top
R_HUB = 15.0                                     # turret hub on the column (printed bushing)
R_SCREW = 66.0                                   # T8 screw at (r 66, t 0)
ROD = (56.0, -28.3)                              # guide rod (r, t): 30 from the screw, 62.7 from the axis
T_ROD = ROD[1]
# Everything of the turret below z 80 stays within 76 of the axis: it turns over the wheel envelope (x >= 79).
PAD_B = [((56.0, 74.5), (-10.0, 10.0)), ((52.0, 70.0), (-22.0, -8.0)), ((48.0, 64.0), (-36.3, -20.3))]  # bottom pad
PAD_T = dict(r=(44.0, 92.0), t=(-38.0, 67.0))    # top pad (608 + rod + NEMA17)
NEMA_C = (70.0, 45.0)                            # NEMA17 beside the screw (+t), r 48.9-91.2: 3 mm clear of the other
                                                 # unit's carriage when that one is at the side; belt ~1:1 (GT2 20T)
CAR_R, CAR_A, CAR_H = (46.0, 80.0), 16.5, 27.5   # carriage block: r range, bottom above the cup axis, height
CAR_T_LOW, CAR_LOW_H = 6.5, 10.0                 # lowest 10 mm of the block stop at t 6.5: clear of the own turn pinion
CAR_T = (-45.0, 12.5)                            # carriage block along t: LM8UU clamp side (-t) + T8 flange pocket
NEMA_R = (NEMA_C[0] - 21.15, NEMA_C[0] + 21.15)                           # NEMA17 inboard of the screw, hanging under the top plate, belt 1:1
# turn drive: printed spur gears m 1, 60 T sector on the bottom hub (pitch r 30) + 30 T pinion on an MG996R (2:1).
# The hub gears sit where nothing else is: front under its hub (z 40-45, inside the drive motors, x < 32), rear over
# its hub (z 74-79). Front servo hangs upside down, rear servo stands on a 6 mm block. Shafts 45 from the axis.
GEAR_R, PINION_R = 30.0, 15.0                    # tip radii 31 / 16, centre distance 45
PINION_PSI = {"F": -40.0, "R": 140.0}           # polar of the turn pinions (2026-11-20: -35/145 -> -40/140, clear of
                                                 # the carriage at the bottom stone on base_330_js)
GEAR_SECTOR = (-142.0, -28.0)                    # hub gear teeth, polar relative to the turret (mesh at -40 - turn)
TURN = {"F": dict(shaft=(28.93, 34.47), sx=1, block=0.0, gear_z=(72.0, 77.0)),     # servo on the floor
        "R": dict(shaft=(-28.93, -34.47), sx=-1, block=0.0, gear_z=(86.0, 91.0))}   # on the floor too (2026-11-20: on the
# 3 mm block the ear screw heads hit the rear arm at z 59; on the floor they stop at 58)
for _u in TURN:                                  # body under its pinion, spline + printed shaft up to the gear plane
    TURN[_u]["body_z"] = (FLOOR_Z[1] + TURN[_u]["block"], FLOOR_Z[1] + TURN[_u]["block"] + 36.8)
MG996 = dict(L=40.7, W=19.7, H=36.8, SHAFT_OFF=10.2, EAR_L=54.0)   # body; shaft 10.2 from one end
HOLD_POST_T = (84.0, 100.0)                      # holder slide posts (|t|): clear of the ball-unit holders (130, 105)
MG90S_T = 50.0                                   # holder MG90S body t 50-72.8 (between the carriage and the posts)
# ================================================================== boxes
class Box:
    def __init__(s, name, c, h, R=None, grp="", col="0.6", kind=""):
        s.name, s.c, s.h = name, np.asarray(c, float), np.asarray(h, float)
        s.R = np.eye(3) if R is None else np.asarray(R, float)
        s.grp, s.col, s.kind = grp, col, kind
        s.rad = float(np.linalg.norm(s.h))

    @staticmethod
    def lohi(name, lo, hi, **kw):
        lo, hi = np.asarray(lo, float), np.asarray(hi, float)
        return Box(name, (lo + hi) / 2, (hi - lo) / 2, None, **kw)

    def corners(s):
        sg = np.array(list(itertools.product((-1, 1), repeat=3)))
        return s.c + (sg * s.h) @ s.R.T

    def faces(s):
        P = s.corners()
        idx = [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)]
        return [[P[i] for i in f] for f in idx]


def overlap(a, b, m=0.0):
    if np.linalg.norm(a.c - b.c) > a.rad + b.rad + m:
        return False
    A, B = a.R, b.R
    ha, hb = a.h + m / 2, b.h + m / 2
    t = b.c - a.c
    axes = [A[:, i] for i in range(3)] + [B[:, i] for i in range(3)]
    axes += [np.cross(A[:, i], B[:, j]) for i in range(3) for j in range(3)]
    for L in axes:
        n = np.linalg.norm(L)
        if n < 1e-9:
            continue
        L = L / n
        ra = sum(ha[i] * abs(A[:, i] @ L) for i in range(3))
        rb = sum(hb[i] * abs(B[:, i] @ L) for i in range(3))
        if abs(t @ L) > ra + rb - 1e-6:
            return False
    return True


def frame(phi, spin=0.0):
    """phi = polar angle of the unit (0 = +Y, grows toward -X). ur radial, ut tangential, a / b = stone axes"""
    p = np.radians(phi)
    ur = np.array([-np.sin(p), np.cos(p), 0.0])
    ut = np.array([np.cos(p), np.sin(p), 0.0])
    s = np.radians(spin)
    a = np.cos(s) * ut + np.sin(s) * np.array([0, 0, 1.0])
    b = np.cross(a, ur)
    return ur, ut, a, b


def rbox(name, phi, r, t, z, **kw):
    """box given by (lo, hi) ranges in the unit frame (r, t, z) at polar phi"""
    ur, ut, _, _ = frame(phi)
    c = ur * (r[0] + r[1]) / 2 + ut * (t[0] + t[1]) / 2 + np.array([0, 0, (z[0] + z[1]) / 2])
    h = ((r[1] - r[0]) / 2, (t[1] - t[0]) / 2, (z[1] - z[0]) / 2)
    return Box(name, c, h, np.column_stack([ur, ut, [0, 0, 1.0]]), **kw)


def stone_box(name, phi, z, spin, **kw):
    ur, ut, a, b = frame(phi, spin)
    return Box(name, ur * RC + [0, 0, z], STONE / 2, np.column_stack([a, ur, b]), **kw)


# ================================================================== robot parts
def fixed_robot():
    """base_330_js as it is (bounding boxes of mechanical/base_330_js/CAD/base_330_js_assembly.FCStd)"""
    g = dict(grp="fixed")
    f = [Box.lohi("plate", (-BODY_W, -BODY_D, FLOOR_Z[0]), (BODY_W, BODY_D, FLOOR_Z[1]), col="0.85", kind="floor", **g)]
    for sx in (1, -1):
        lo = lambda a, b: min(sx * a, sx * b)
        hi = lambda a, b: max(sx * a, sx * b)
        f.append(Box.lohi("JSUMO envelope", (lo(79, 131), -40, -3), (hi(79, 131), 40, 77), col="0.12", **g))
        f.append(Box.lohi("37D motor", (lo(15, 74.5), -18.5, 25.5), (hi(15, 74.5), 18.5, 62.5), col="0.35", **g))
        f.append(Box.lohi("hinge", (lo(31.9, 77.7), -20, 16.5), (hi(31.9, 77.7), 20, 57.0), col="0.5", **g))
        f.append(Box.lohi("odometry bracket", (lo(132.2, 163.2), -78, 16.5), (hi(132.2, 163.2), -34, 64.2),
                          grp="odom", col="0.3", kind="odom"))
        f.append(Box.lohi("odometry wheel + AMT", (lo(136.0, 167.2), -30.5, -0.3), (hi(136.0, 167.2), 30.5, 60.7),
                          grp="odom", col="0.1", kind="odom"))
        for sy in (1, -1):
            f.append(Box.lohi("ball holder", (sx * 130 - 22, sy * 105 - 22, 16.5), (sx * 130 + 22, sy * 105 + 22, 29),
                              col="0.4", **g))
            f.append(Box.lohi("ball unit nut", (sx * 130 - 12, sy * 105 - 12, 29), (sx * 130 + 12, sy * 105 + 12, 41),
                              col="0.4", **g))
    f.append(Box.lohi("column", (-R_COL, -R_COL, FLOOR_Z[1]), (R_COL, R_COL, 350), col="0.3", kind="column", **g))
    # beacon support on top of the column: 80 x 80 (<= 100 x 100, >= 70), top 430 [GR F.6]
    f.append(Box.lohi("beacon support", (-40, -40, 350), (40, 40, 430), col="0.15", kind="beacon", **g))
    return f


def turret(u, th):
    """fixed-to-turret parts of unit u at turn th"""
    U = UNITS[u]
    phi = U["phi0"] + th
    col = "#2b6cd4"
    g = dict(grp="tur" + u, col=col)
    zb, zh, zt, zht = U["zb"], U["zh"], U["zt"], U["zht"]
    rs, ts = (R_SCREW - 4, R_SCREW + 4), (-4, 4)
    P = [rbox("bottom hub " + u, phi, (-R_HUB, R_HUB), (-R_HUB, R_HUB), (zh, zh + PLATE_T), kind="hub", **g),
         rbox("bottom web " + u, phi, WEB_R, (-10, 10), (zh, zh + PLATE_T), kind="hub", **g),
         rbox("bottom spoke " + u, phi, (WEB_R[1] if zh == zb else RISER_R[1], 56.0), (-10, 10),
              (zb, zb + PLATE_T), **g),
         *[rbox("bottom pad %d %s" % (i, u), phi, r, t, (zb, zb + PLATE_T), **g) for i, (r, t) in enumerate(PAD_B)],
         rbox("top hub " + u, phi, (-R_HUB, R_HUB), (-R_HUB, R_HUB), (zht, zht + PLATE_T), kind="hub", **g),
         rbox("top web " + u, phi, WEB_R, (-10, 10), (zht, zht + PLATE_T), kind="hub", **g),
         rbox("top spoke " + u, phi, (WEB_R[1] if zht == zt else 31.0, PAD_T["r"][0]), (-21, 21), (zt, zt + PLATE_T), **g),
         rbox("top pad " + u, phi, PAD_T["r"], PAD_T["t"], (zt, zt + PLATE_T), **g),
         rbox("T8 screw " + u, phi, rs, ts, (zb + PLATE_T, zt), kind="screw", grp="tur" + u, col="0.55"),
         rbox("guide rod " + u, phi, (ROD[0] - 4, ROD[0] + 4), (ROD[1] - 4, ROD[1] + 4), (zb, zt), kind="screw", grp="tur" + u,
              col="0.75"),
         rbox("NEMA17 " + u, phi, NEMA_R, (NEMA_C[1] - 21.15, NEMA_C[1] + 21.15), (zt - 42, zt), grp="tur" + u,
              col="0.1"),
         rbox("GT2 pulleys + belt " + u, phi, (R_SCREW - 8, NEMA_C[0] + 8), (-8, NEMA_C[1] + 8), (zt + PLATE_T + 1, 349.5),
              grp="tur" + u, col="0.25")]
    if zh != zb:                                 # rear bottom: riser from its hub down to the arm level
        P.append(rbox("bottom riser " + u, phi, RISER_R, (-10, 10), (zb, zh + PLATE_T), **g))
    if zht != zt:                                # rear top: riser beside the NEMA (t -30..-20), joins web and arm
        P.append(rbox("top riser " + u, phi, (25.0, 31.0), (-30, -20), (zht, zt + PLATE_T), **g))
        P.append(rbox("top web link " + u, phi, (WEB_R[0], 30), (-30, 10), (zht, zht + PLATE_T), kind="hub", **g))
    return P


def carriage(u, th, zc, spin):
    phi = UNITS[u]["phi0"] + th
    g = dict(grp="car" + u)
    ur, ut, a, b = frame(phi, spin)
    z0 = zc + CAR_A
    P = [rbox("carriage " + u, phi, CAR_R, CAR_T, (z0 + CAR_LOW_H, z0 + CAR_H), col="#7a1fa2", kind="carriage", **g),
         rbox("carriage low " + u, phi, CAR_R, (CAR_T[0], CAR_T_LOW), (z0, z0 + CAR_LOW_H), col="#7a1fa2", kind="carriage", **g),
         rbox("carriage arm " + u, phi, (CAR_R[1], 144 + DF), (-17, 12.5), (z0, z0 + 4), col="#7a1fa2", **g),
         rbox("carriage arm out " + u, phi, (94, 144 + DF), (12.5, 38), (z0, z0 + 4), col="#7a1fa2", **g),
         rbox("carriage drop " + u, phi, (136 + DF, 140 + DF), (-17, 38), (zc - 12, z0 + 4), col="#7a1fa2", **g),
         rbox("spin MG996R " + u, phi, (106 + DF, 144 + DF), (-17, 38), (zc - 10, zc + 10), col="0.2", **g),
         rbox("cup bearing " + u, phi, (144 + DF, 150 + DF), (-11, 11), (zc - 11, zc + 11), col="0.45", **g)]
    P.append(Box("shaft cup " + u, ur * (FACE - 9) + [0, 0, zc], (9, 15, 15), np.column_stack([ur, a, b]),
                 col="0.02", kind="cup", **g))
    return P


def holder(u, L):
    phi = UNITS[u]["phi0"]
    g = dict(grp="hold" + u, col="#2e8b57")
    P = []
    for t in (-HOLD_X, HOLD_X):
        P.append(rbox(f"holder column {u}{t:+.0f}", phi, (128 + DF, 150 + DF), (t - 10, t + 10), (38 + L, HOLD_TOP + L), **g))
        for lv in ("B", "M"):
            P.append(rbox(f"holder cup {u}{lv}{t:+.0f}", phi, (150 + DF, FACE), (t - 15, t + 15),
                          (Z_ST[lv] - 15 + L, Z_ST[lv] + 15 + L), kind="hcup", grp="hold" + u, col="0.02"))
    P.append(rbox("holder crossbar " + u, phi, (128 + DF, 146 + DF), (-110, 110), (30 + L, 38 + L), **g))
    return P


def fixed_unit(u):
    """unit parts fixed to the body: turn servo, holder lift servo + its rods"""
    phi = UNITS[u]["phi0"]
    g = dict(grp="fixed")
    T = TURN[u]
    sx, (x0, y0) = T["sx"], T["shaft"]
    xa, xb = sorted((x0 - sx * MG996["SHAFT_OFF"], x0 + sx * (MG996["L"] - MG996["SHAFT_OFF"])))
    out = [Box.lohi("turn MG996R " + u, (xa, y0 - MG996["W"] / 2, T["body_z"][0]), (xb, y0 + MG996["W"] / 2,
                                                                                       T["body_z"][1]), col="0.2", **g),
           Box.lohi("turn pinion " + u, (x0 - PINION_R - 1, y0 - PINION_R - 1, T["gear_z"][0]),
                    (x0 + PINION_R + 1, y0 + PINION_R + 1, T["gear_z"][1]), col="0.5", kind="pinion", **g),
           rbox("holder MG90S + cradle " + u, phi, (101, 120), (MG90S_T - 6.5, MG90S_T + 33), (FLOOR_Z[1], 55),
                col="0.2", **g)]
    for t in (-1, 1):
        out.append(rbox(f"holder post {u}{t:+d}", phi, (108, 128), sorted((t * HOLD_POST_T[0], t * HOLD_POST_T[1])),
                        (FLOOR_Z[1], 195), col="0.2", **g))
    if T["block"]:
        out.append(Box.lohi("turn servo block " + u, (xa, y0 - MG996["W"] / 2, FLOOR_Z[1]),
                            (xb, y0 + MG996["W"] / 2, FLOOR_Z[1] + T["block"]), col="0.6", **g))
    return out


def free_volumes():
    """the layout-v1 reservations (Grail lift, launcher, pumps) don't apply to base_330_js: none checked here"""
    return []


# ================================================================== sequence
def sequence():
    S = []
    st = dict(L={"F": L_CARRY, "R": L_CARRY}, th={"F": 0.0, "R": 0.0},
              zc={"F": Z_ST["T"] + L_CARRY, "R": Z_ST["T"] + L_CARRY}, spin={"F": 0.0, "R": 0.0},
              held={"F": None, "R": None}, vac={"F": True, "R": True}, vented={"F": None, "R": None},
              stack={"F": ["B", "M", "T"], "R": ["B", "M", "T"]}, towers=[], label="", act=set())

    def snap():
        S.append({k: (dict(v) if isinstance(v, dict) else v) for k, v in st.items()} |
                 {"stack": {u: list(v) for u, v in st["stack"].items()}, "towers": list(st["towers"])})

    def push(label, act, n, u=None, drive=0.0, **chg):
        a = {k: (st[k][u] if u else st[k]) for k in chg if k != "Lboth"}
        aL, aZ = dict(st["L"]), dict(st["zc"])
        for i in range(1, n + 1):
            f = 0.5 - 0.5 * np.cos(np.pi * i / n)
            for k, v in chg.items():
                if k == "Lboth":
                    continue
                if u:
                    st[k][u] = a[k] + (v - a[k]) * f
            if "Lboth" in chg:
                for w in ("F", "R"):
                    st["L"][w] = aL[w] + (chg["Lboth"] - aL[w]) * f
                    if st["held"][w] is None:                       # the shaft cup moves with the stack
                        st["zc"][w] = aZ[w] + st["L"][w] - aL[w]
            if drive:
                st["towers"] = [(nm, w, y - drive / n) for nm, w, y in st["towers"]]
            st["label"], st["act"] = label, set(act)
            snap()

    def hold(label, n):
        for _ in range(n):
            st["label"], st["act"] = label, set()
            snap()

    def build(u, lv, last):
        side = "left" if u == "F" else "right"
        un = "front" if u == "F" else "rear"
        name = {"T": "top", "M": "middle", "B": "bottom"}[lv]
        tag = f"{un} {name}"
        zt = Z_TURN_TOP if lv == "T" else Z_TURN
        st["vac"][u] = True
        if lv != "T":
            hold(f"{tag}: shaft cup on, its 2 holder cups vent", 3)
        st["stack"][u].remove(lv)
        st["held"][u] = lv
        push(f"{tag}: lift above the holder cups (stone bottom {zt - 55:.0f})", ["shaft Z " + u], 8 if lv == "T" else 12,
             u, zc=zt)
        push(f"{tag}: turret turns 90 deg to the robot's {side}", ["turn " + u], 16, u, th=90.0)
        push(f"{tag}: down to spin height", ["shaft Z " + u], 8, u, zc=Z_SPIN)
        push(f"{tag}: spin 90 deg, the stone stands up", ["spin " + u], 10, u, spin=90.0)
        push(f"{tag}: tower set on the table", ["shaft Z " + u], 4, u, zc=Z_SET)
        st["vac"][u] = False
        st["held"][u] = None
        st["towers"].append((lv, u, 0.0))
        st["vented"][u] = lv
        hold(f"{tag}: vent", 2)
        push(f"{tag}: cup spins back, rises along the tower face", ["spin " + u, "shaft Z " + u], 8, u,
             spin=0.0, zc=Z_TURN)
        push(f"{tag}: turret turns back (cup slides off the tower face)", ["turn " + u], 12, u, th=0.0)
        st["vented"][u] = None
        nxt = {"T": "M", "M": "B", "B": None}[lv]
        if nxt:
            push(f"{un}: cup down to the {('middle' if nxt == 'M' else 'bottom')} stone", ["shaft Z " + u], 8, u,
                 zc=Z_ST[nxt])
        if not last:
            push("holders lift 15 mm (carry)", ["holder lift"], 4, Lboth=L_CARRY)
            push(f"robot drives {DRIVE:.0f} mm to the next tower zone", ["wheels"], 10, drive=DRIVE)
            push("holders down", ["holder lift"], 4, Lboth=0.0)

    hold("carry: 2 stacks, holder cups on the lower stones, shaft cups on the top stones", 5)
    push("set both stacks down in the tower zone", ["holder lift"], 6, Lboth=0.0)
    seq = [("F", "T"), ("F", "M"), ("F", "B"), ("R", "T"), ("R", "M"), ("R", "B")]
    for i, (u, lv) in enumerate(seq):
        build(u, lv, last=(i == len(seq) - 1))
    push("robot drives on: 6 towers from 2 quarry stacks", ["wheels"], 10, drive=DRIVE)
    hold("done", 6)
    return S


def parts(s, with_free=False):
    P = fixed_robot()
    for u in ("F", "R"):
        P += turret(u, s["th"][u]) + carriage(u, s["th"][u], s["zc"][u], s["spin"][u]) + holder(u, s["L"][u])
        P += fixed_unit(u)
        phi0 = UNITS[u]["phi0"]
        for lv in s["stack"][u]:
            P.append(stone_box(f"stone {u}{lv}", phi0, Z_ST[lv] + s["L"][u], 0.0, grp="stack" + u,
                               col="#d9b26f", kind="stone"))
        if s["held"][u]:
            P.append(stone_box(f"held stone {u}{s['held'][u]}", phi0 + s["th"][u], s["zc"][u], s["spin"][u],
                               grp="car" + u, col="#e08a2c", kind="held"))
    for lv, u, y in s["towers"]:
        b = stone_box(f"tower {u}{lv}", UNITS[u]["phi0"] + 90.0, Z_SET, 90.0, grp="tower" + u + lv,
                      col="#a8834a", kind="tower")
        b.c = b.c + [0, y, 0]
        P.append(b)
    if with_free:
        P += free_volumes()
    return P


# ================================================================== checks
def allowed(a, b, s):
    """pairs that touch by design -> (skip, margin)"""
    ka, kb = a.kind, b.kind
    if {ka, kb} == {"hub", "column"}:
        return True, 0
    if {ka, kb} == {"pinion", "carriage"}:
        return False, 0.0                                  # square box round a round pinion: real gap ~4 mm (FreeCAD check)
    if "beacon" in (ka, kb):
        return False, 0.0                                  # belt/pulleys under the beacon support (z 349.5 < 350)
    if {ka, kb} == {"odom", "floor"}:
        return True, 0                                     # odometry modules on / through the base plate
    if a.grp == b.grp:
        return True, 0
    if {ka, kb} <= {"stone"}:
        return True, 0                                     # stack stones rest on each other
    for x, y in ((a, b), (b, a)):
        if x.kind == "carriage" and y.kind == "screw" and x.grp[-1] == y.grp[-1]:
            return True, 0
        if x.kind == "pinion" and y.grp == "tur" + x.name[-1]:
            return False, 0.0                          # pinion meshes its own turret's hub gear
        if x.kind == "hcup" and y.kind == "stone" and x.grp[-1] == y.grp[-1]:
            return True, 0
        if x.kind == "cup" and y.kind == "tower" and y.name == f"tower {x.grp[-1]}{s['vented'][x.grp[-1]]}":
            return True, 0
    for x, y in ((a, b), (b, a)):
        if x.kind == "carriage" and y.kind == "screw" and x.grp[-1] == y.grp[-1]:
            return True, 0
        if x.kind == "pinion" and y.grp == "tur" + x.name[-1]:
            return False, 0.0                          # pinion meshes its own turret's hub gear                                 # carriage rides its own screw + rod
        if x.kind == "hcup" and y.kind == "stone" and x.grp[-1] == y.grp[-1]:
            return True, 0                                 # holder cups grip their stack
        if x.kind == "cup" and y.kind in ("stone", "tower"):
            if y.kind == "tower" and y.name == f"tower {x.grp[-1]}{s['vented'][x.grp[-1]]}":
                return True, 0                             # leaves the tower it just vented (vacuum off)
            return False, 0.0                              # cup on stone faces: touching allowed
        if x.kind == "held" and y.kind == "stone":
            return False, 0.0                              # the held stone starts resting on the one below
        if x.kind == "hcup" and y.kind == "held" and x.grp[-1] == y.grp[-1]:
            return False, 0.0                              # held stone slides up past its vented holder cups
        if x.grp.startswith("tur") and y.grp.startswith("car") and x.grp[-1] == y.grp[-1]:
            return False, 0.0                              # same unit, designed close
    return False, MARGIN


def check(S, step=1):
    clashes, zmax, zmin_spin = {}, 0.0, 1e9
    free = free_volumes()
    free_hits = {}
    for i in range(0, len(S), step):
        s = S[i]
        P = parts(s)
        movers = [p for p in P if p.grp.startswith(("tur", "car", "hold")) or p.kind in ("held",)]
        others = P
        for a in movers:
            for b in others:
                if b is a or (b in movers and id(b) < id(a)):
                    continue
                skip, m = allowed(a, b, s)
                if skip:
                    continue
                if overlap(a, b, m):
                    k = (a.name, b.name)
                    clashes.setdefault(k, (i, s["label"]))
        for p in P:
            if p.kind in ("beacon", "stone", "tower", "column"):
                continue
            zmax = max(zmax, p.corners()[:, 2].max())
            if p.kind == "held" and 1 < max(s["spin"].values()) < 89:
                zmin_spin = min(zmin_spin, p.corners()[:, 2].min())
        for v in free:
            if v.name.startswith("pumps"):
                continue
            for p in P:
                if p.kind in ("floor",) or p.grp == "free":
                    continue
                if overlap(v, p, 0.0):
                    free_hits.setdefault((v.name, p.name), (i, s["label"]))
    return clashes, zmax, zmin_spin, free_hits


def hull2(P):
    P = sorted(set(map(tuple, np.round(P, 3))))
    if len(P) < 3:
        return P
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and ((h[-1][0] - h[-2][0]) * (p[1] - h[-2][1])
                                   - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0])) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, up = half(P), half(P[::-1])
    return lo[:-1] + up[:-1]


def body_outline():
    w, d, c = BODY_W, BODY_D, CHAMFER
    return [(-w + c, -d), (w - c, -d), (w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c)]


def perimeter(s):
    pts = list(body_outline())
    for p in parts(s):
        if p.kind in ("stone", "tower", "held", "beacon", "floor") or p.grp == "free":
            continue
        pts += [tuple(c[:2]) for c in p.corners()]
    H = hull2(pts)
    return sum(np.hypot(H[i][0] - H[i - 1][0], H[i][1] - H[i - 1][1]) for i in range(len(H))), H


# ================================================================== drawing
def render(S, out_gif, sheet):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib.patches import Polygon, Circle
    from PIL import Image

    def draw(s, fig, free=False):
        fig.clf()
        ax = fig.add_axes([0.0, 0.08, 0.58, 0.86], projection="3d")
        P = parts(s, with_free=free)
        oct_ = body_outline()
        for p in P:
            if p.kind == "floor":
                for z in FLOOR_Z:
                    ax.add_collection3d(Poly3DCollection([[(x, y, z) for x, y in oct_]], fc="0.85", ec="0.4", lw=0.3))
                continue
            al = 0.25 if p.grp == "free" else 0.95
            ax.add_collection3d(Poly3DCollection(p.faces(), facecolor=p.col, edgecolor="0.2", linewidths=0.25,
                                                 alpha=al))
        ax.set_xlim(-360, 360); ax.set_ylim(-380, 340); ax.set_zlim(0, 440)
        ax.set_box_aspect((720, 720, 440))
        ax.view_init(elev=26, azim=118)
        ax.set_axis_off()
        a2 = fig.add_axes([0.58, 0.20, 0.41, 0.74])
        a2.add_patch(Polygon(oct_, closed=True, fc="0.9", ec="0.4", lw=0.6))
        for p in sorted(P, key=lambda q: q.corners()[:, 2].max()):
            if p.kind in ("floor", "beacon"):
                continue
            a2.add_patch(Polygon(hull2(p.corners()[:, :2]), closed=True, fc=p.col, ec="0.2", lw=0.3,
                                 alpha=0.3 if p.grp == "free" else 0.9))
        a2.add_patch(Circle((0, 0), 40, fill=False, ec="0.1", lw=0.8))
        per, H = perimeter(s)
        a2.add_patch(Polygon(H, closed=True, fill=False, ec="#c0392b", ls="--", lw=0.7))
        a2.set_xlim(-420, 420); a2.set_ylim(-460, 420); a2.set_aspect("equal")
        a2.set_xticks([]); a2.set_yticks([])
        a2.text(0.02, 0.97, "top view, front = up\n" + f"perimeter now {per:.0f} mm (dashed)", fontsize=7,
                transform=a2.transAxes, va="top")
        fig.text(0.02, 0.955, "Central hub option E (doubled): per unit 1 turret + 1 shaft (Z, turn, spin) + "
                 "holder cups; front -> robot's left, rear -> right", fontsize=9, weight="bold")
        fig.text(0.02, 0.035, s["label"], fontsize=9)
        x = 0.59
        for a in ["holder lift", "shaft Z F", "turn F", "spin F", "shaft Z R", "turn R", "spin R", "wheels"]:
            on = a in s["act"]
            fig.text(x, 0.12, a, fontsize=7, color="white" if on else "0.35",
                     bbox=dict(fc="#c2185b" if on else "0.9", ec="none", pad=1.5))
            x += 0.05
        fig.text(0.59, 0.165, "front: Z {:.0f} turn {:.0f} spin {:.0f}   rear: Z {:.0f} turn {:.0f} spin {:.0f}".format(
            s["zc"]["F"], s["th"]["F"], s["spin"]["F"], s["zc"]["R"], s["th"]["R"], s["spin"]["R"]), fontsize=7)

    fig = plt.figure(figsize=(11, 6), dpi=75)
    frames = []
    for s in S:
        draw(s, fig)
        fig.canvas.draw()
        im = Image.frombuffer("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB")
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    frames[0].save(out_gif, save_all=True, append_images=frames[1:], duration=65, loop=0, optimize=True)
    # sheet: both turrets out (deployed), free volumes shown
    i = next(j for j, t in enumerate(S) if t["label"].startswith("front top: spin"))
    s = dict(S[i])
    fig2 = plt.figure(figsize=(11, 6), dpi=110)
    draw(s, fig2, free=True)
    fig2.text(0.59, 0.075, "yellow = Grail lift + L4 roof (front-right), red = launcher (rear-left), "
              "grey = pumps", fontsize=7)
    fig2.savefig(sheet)


# ================================================================== main
def main():
    S = sequence()
    clashes, zmax, zmin_spin, free_hits = check(S)
    # deployed envelope: both turrets out, both spun, holders up (every mechanism open at once, FAQ Q10)
    dep = dict(S[0])
    dep.update(th={"F": 90.0, "R": 90.0}, spin={"F": 90.0, "R": 90.0}, zc={"F": Z_SET, "R": Z_SET},
               L={"F": L_CARRY, "R": L_CARRY}, held={"F": None, "R": None}, stack={"F": [], "R": []}, towers=[])
    per_start, _ = perimeter(S[0])
    per_dep, _ = perimeter(dep)
    per_max = max(perimeter(s)[0] for s in S[::3])
    lines = ["Central hub option E, doubled (Ayoub, 2026-11-19, proposal): turret + one shaft + holder cups per unit",
             f"base: base_330_js plate {2*BODY_W:.0f} x {2*BODY_D:.0f} (unchanged); stack face r {FACE:.0f}",
             "perimeter limits not designed for in this version (Ayoub, 2026-11-20): reported only",
             f"states: {len(S)} (front builds 3 towers while the rear holds its stack, then the rear), "
             f"margin {MARGIN} mm",
             f"highest point (robot + held stone; column = beacon mast, excluded [GR F.3]): {zmax:.1f} mm (limit 350 [GR F.3])",
             f"lowest stone corner during a spin: {zmin_spin:.1f} mm (> 0 = clears the table)",
             f"perimeter at start (both stacks out of count, FAQ Q1): {per_start:.0f} mm (limit 1200 [GR F.3])",
             f"perimeter deployed (both turrets out + holders up, FAQ Q10): {per_dep:.0f} mm (limit 1400)",
             f"largest perimeter seen in the sequence: {per_max:.0f} mm",
             f"clashes: {len(clashes)}"]
    for (a, b), (i, lab) in clashes.items():
        lines.append(f"  state {i}: {lab} | {a} x {b}")
    lines.append(f"free volumes entered by a part: {len(free_hits)}")
    for (a, b), (i, lab) in free_hits.items():
        lines.append(f"  state {i}: {lab} | {a} x {b}")
    for v in free_volumes():
        d = 2 * v.h
        lines.append(f"  {v.name}: {d[0]:.0f} x {d[1]:.0f} x {d[2]:.0f} mm = {np.prod(d) / 1e6:.2f} L, "
                     f"x {v.c[0]-v.h[0]:.0f}..{v.c[0]+v.h[0]:.0f}, y {v.c[1]-v.h[1]:.0f}..{v.c[1]+v.h[1]:.0f}, "
                     f"z {v.c[2]-v.h[2]:.0f}..{v.c[2]+v.h[2]:.0f}")
    rep = "\n".join(lines)
    print(rep)
    with open(os.path.join(ROOT, "hub_e_report.txt"), "w", encoding="utf-8") as f:
        f.write(rep + "\n")
    if "--gif" in sys.argv:
        os.makedirs(SIM, exist_ok=True)
        render(S, os.path.join(SIM, "option_e_sequence.gif"), os.path.join(SIM, "option_e_sheet.png"))
        print("gif written")


if __name__ == "__main__":
    main()
