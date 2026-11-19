# check_e.py - central hub option E (Ayoub's idea, 2026-11-19): the CLAPET DOORS hold the stack, ONE shaft carriage
# goes up/down on the hub and turns around it; its suction cup takes ONE stone at a time to the side, then the cup
# spins 90 deg and the stone stands up as a tower.
#
# Problem: the doors pinch the stack from its two ends, so the cup cannot pull a stone out, and a closed door is in
# the stone's path when it turns around the hub. Solution modelled here:
#   1. SHORT DOORS: they clamp only up to z 195 (bottom stone + the lower 85 mm of the middle one). The cup holds the
#      top stone while the stack is carried.
#   2. Every stone is LIFTED ABOVE THE DOOR TOPS before it turns (bottom face >= 205, top face <= 338 < 350).
#   3. The doors only UNCLAMP (8 mm) to let the middle / bottom stone slide up; they clamp again on what is left,
#      so the robot can carry it to the next tower zone. Order top -> middle -> bottom.
#
# Plain Python (numpy + matplotlib + Pillow), oriented boxes, same level as ../../fc/check_c.py.
# Frame as options A-D: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table.
# Run from mechanical/central-hub/option-e/:
#   python fc/check_e_doors.py          -> hub_e_doors_report.txt
#   python fc/check_e_doors.py --gif    -> also ../../simulations/central_hub/option_e_doors_sequence.gif + option_e_doors_sheet.png
import os
import sys
import itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIM = os.path.join(ROOT, "..", "..", "simulations", "central_hub")
MARGIN = 3.0

# ================================================================== numbers (mm, deg)
STONE = np.array([320.0, 110.0, 110.0])          # nominal [G D.4]
FACE = 176.0                                     # cup face from the hub axis (stack face, and at the side: as option C)
RC = FACE + STONE[1] / 2                         # 231 stone centre radius
Z_ST = {"T": 275.0, "M": 165.0, "B": 55.0}       # stone centres, stack on the table
DOOR_Z = (20.0, 195.0)                           # door sheet height: clamps the bottom stone + 85 of the middle one
DOOR_X = 161.0                                   # door inner face (pad) when clamped
DOOR_T = 6.0                                     # pad + sheet
DOOR_Y = (186.0, 276.0)
DOOR_OPEN = 8.0                                  # unclamp stroke
BODY = dict(x=(DOOR_X + DOOR_T, DOOR_X + DOOR_T + 30), y=(200.0, 262.0))   # door servo + gears, outside the sheet
L_CARRY = 15.0                                   # clapets lift while carrying (doors + cup together)
Z_SWING_TOP = 283.0                              # top stone turns 8 mm above the stack
Z_SWING = 260.0                                  # middle / bottom stone turns here: bottom face 205 > door top 195
Z_SPIN, Z_SET = 174.0, 160.0                     # spin height (corners clear the table), then set the tower down
DRIVE = 340.0                                    # robot drives on between towers
R_COL, R_SHAFT, SHAFT_Z = 40.0, 95.0, (28.0, 340.0)


# ================================================================== boxes
class Box:
    def __init__(s, name, c, h, R=None, grp="", col="0.6"):
        s.name, s.c, s.h = name, np.asarray(c, float), np.asarray(h, float)
        s.R = np.eye(3) if R is None else np.asarray(R, float)
        s.grp, s.col = grp, col
        s.rad = float(np.linalg.norm(s.h))

    @staticmethod
    def lohi(name, lo, hi, grp="", col="0.6"):
        lo, hi = np.asarray(lo, float), np.asarray(hi, float)
        return Box(name, (lo + hi) / 2, (hi - lo) / 2, None, grp, col)

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
    """unit vectors at turn phi (0 = cup faces +Y, grows toward -X = robot's left) and cup spin"""
    p = np.radians(phi)
    ur = np.array([-np.sin(p), np.cos(p), 0.0])            # radial (out of the hub)
    ut = np.array([np.cos(p), np.sin(p), 0.0])             # tangential (stone long axis before the spin)
    s = np.radians(spin)
    a = np.cos(s) * ut + np.sin(s) * np.array([0, 0, 1.0])   # stone long axis
    b = np.cross(a, ur)                                      # stone 3rd axis
    return ur, ut, a, b


def stone_held(phi, z, spin, name="held stone"):
    ur, ut, a, b = frame(phi, spin)
    return Box(name, ur * RC + [0, 0, z], STONE / 2, np.column_stack([a, ur, b]), "stone", "#e08a2c")


def carriage(phi, z, spin):
    """shaft (on the turntable), carriage, arm, spin servo, cup"""
    ur, ut, a, b = frame(phi, spin)
    Rr = np.column_stack([ur, ut, [0, 0, 1.0]])
    out = []
    zc = (SHAFT_Z[0] + SHAFT_Z[1]) / 2
    out.append(Box("shaft", ur * R_SHAFT + [0, 0, zc], (6, 6, (SHAFT_Z[1] - SHAFT_Z[0]) / 2), Rr, "hub", "#7a1fa2"))
    out.append(Box("carriage", ur * 97.5 + [0, 0, z], (12.5, 16, 20), Rr, "car", "#b04fd0"))
    out.append(Box("arm", ur * 117.5 + [0, 0, z], (7.5, 10, 8), Rr, "car", "#b04fd0"))
    out.append(Box("spin servo", ur * 142.5 + [0, 0, z], (17.5, 20, 10), Rr, "car", "0.25"))
    Rc = np.column_stack([ur, a, b])
    out.append(Box("cup", ur * 168 + [0, 0, z], (8, 15, 15), Rc, "cup", "0.05"))
    return out


def fixed_robot():
    f = [Box.lohi("plate", (-168, -140, 11.5), (168, 140, 16.5), "robot", "0.82")]
    for sx in (1, -1):
        lo = lambda a, b: min(sx * a, sx * b)
        hi = lambda a, b: max(sx * a, sx * b)
        f.append(Box.lohi("wheel", (lo(79, 131), -40, 0), (hi(79, 131), 40, 77), "robot", "0.15"))
    # hub column (drawn as a square prism, checked as one)
    f.append(Box.lohi("hub column", (-R_COL, -R_COL, 16.5), (R_COL, R_COL, 340), "robot", "0.55"))
    return f


def doors(L, d):
    out = []
    for sx in (1, -1):
        x0 = sx * (DOOR_X + d * DOOR_OPEN)
        x1 = x0 + sx * DOOR_T
        out.append(Box.lohi("door " + ("R" if sx > 0 else "L"), (min(x0, x1), DOOR_Y[0], DOOR_Z[0] + L),
                            (max(x0, x1), DOOR_Y[1], DOOR_Z[1] + L), "door", "#2b6cd4"))
        bx = [sx * (BODY["x"][0] + d * DOOR_OPEN), sx * (BODY["x"][1] + d * DOOR_OPEN)]
        out.append(Box.lohi("door unit " + ("R" if sx > 0 else "L"), (min(bx), BODY["y"][0], DOOR_Z[0] + L),
                            (max(bx), BODY["y"][1], DOOR_Z[1] + L), "door", "#173f80"))
    return out


# ================================================================== sequence
def sequence():
    S = []
    st = dict(L=L_CARRY, d=0.0, phi=0.0, z=Z_ST["T"] + L_CARRY, spin=0.0, held=None, vac=True,
              stack=["B", "M", "T"], towers=[], label="", act=set(), vented=None)

    def push(label, act=(), n=1, **chg):
        a = {k: st[k] for k in chg if k != "drive"}
        for i in range(1, n + 1):
            f = i / n
            f = 0.5 - 0.5 * np.cos(np.pi * f)              # smooth start / stop
            for k, v in chg.items():
                if k == "drive":
                    continue
                st[k] = a[k] + (v - a[k]) * f
            if "drive" in chg:
                st["towers"] = [(nm, y0 - chg["drive"] / n) for nm, y0 in st["towers"]]
            st["label"], st["act"] = label, set(act)
            S.append(dict(st, towers=list(st["towers"]), stack=list(st["stack"])))

    def hold(label, n):
        for _ in range(n):
            st["label"], st["act"] = label, set()
            S.append(dict(st, towers=list(st["towers"]), stack=list(st["stack"])))

    def build(lv, first):
        name = {"T": "top", "M": "middle", "B": "bottom"}[lv]
        z_sw = Z_SWING_TOP if lv == "T" else Z_SWING
        st["vac"] = True
        if lv != "T":
            push(f"{name}: doors unclamp {DOOR_OPEN:.0f} mm, cup holds the {name} stone", ["doors", "vacuum"], 6, d=1.0)
        st["stack"].remove(lv)
        st["held"] = lv
        push(f"{name}: shaft lifts the stone above the door tops (bottom face {z_sw - 55:.0f} > {DOOR_Z[1]:.0f})",
             ["shaft Z"], 14 if lv != "T" else 6, z=z_sw)
        if lv != "T" and st["stack"]:
            push(f"{name}: doors clamp again on what is left", ["doors"], 5, d=0.0)
        push(f"{name}: carriage turns 90 deg around the hub, over the doors", ["turn"], 20, phi=90.0)
        push(f"{name}: down to spin height", ["shaft Z"], 10, z=Z_SPIN)
        push(f"{name}: cup spins 90 deg, the stone stands up", ["spin"], 14, spin=90.0)
        push(f"{name}: tower set on the table", ["shaft Z"], 5, z=Z_SET)
        st["vac"] = False
        st["held"] = None
        st["towers"].append((lv, 0.0))
        st["vented"] = lv
        hold(f"{name}: vent", 3)
        nxt = {"T": "M", "M": "B", "B": None}[lv]
        z_next = Z_ST[nxt] if nxt else Z_SWING
        if lv == "B" and st["d"] > 0:
            push("doors close", ["doors"], 4, d=0.0)
        push(f"{name}: carriage turns back, cup spins back", ["turn", "spin"], 16, phi=0.0, spin=0.0)
        st["vented"] = None
        if nxt:
            push(f"cup to the {('middle' if nxt == 'M' else 'bottom')} stone", ["shaft Z"], 8, z=z_next)
            push("lift 15 mm: the doors carry what is left", ["lift"], 4, L=L_CARRY)
            push(f"robot drives {DRIVE:.0f} mm to the next tower zone", ["wheels"], 12, drive=DRIVE, L=L_CARRY)
            push("set down", ["lift"], 4, L=0.0)
        else:
            push(f"robot drives on: 3 towers from one quarry stack", ["wheels"], 12, drive=DRIVE)

    hold("carry: doors clamp bottom + middle, the cup holds the top stone", 6)
    push("set the stack down in the tower zone", ["lift"], 8, L=0.0, z=Z_ST["T"])
    build("T", True)
    build("M", False)
    build("B", False)
    hold("done", 8)
    return S


def parts(s):
    P = fixed_robot() + doors(s["L"], s["d"]) + carriage(s["phi"], s["z"], s["spin"])
    for lv in s["stack"]:
        P.append(Box("stone " + lv, (0, RC, Z_ST[lv] + s["L"]), STONE / 2, None, "stack", "#d9b26f"))
    if s["held"]:
        P.append(stone_held(s["phi"], s["z"], s["spin"], "held stone " + s["held"]))
    for lv, y in s["towers"]:
        b = stone_held(90.0, Z_SET, 90.0, "tower " + lv)
        b.c = b.c + [0, y, 0]
        b.grp, b.col = "tower", "#a8834a"
        P.append(b)
    return P


def check(S):
    clashes, brush, zmax, zmin_spin = [], [], 0.0, 1e9
    for i, s in enumerate(S):
        P = parts(s)
        for p in P:
            if p.grp in ("tower",) or p.name.startswith("stone"):
                continue
            zmax = max(zmax, p.corners()[:, 2].max())
        held = [p for p in P if p.name.startswith("held")]
        car = [p for p in P if p.grp in ("car", "cup")]
        movers = held + car
        for a in movers:
            for b in P:
                if b is a or b in movers or b.name == "shaft":
                    continue
                if a.grp == "cup" and b.grp in ("stack", "tower"):
                    if b.name == "tower " + str(s["vented"]):
                        continue                              # cup leaves the tower it just vented (vacuum off)
                    if overlap(a, b, 0.0):                    # the cup touches stone faces: grip / brush
                        brush.append((i, s["label"], b.name))
                    continue
                elif a.name.startswith("held") and b.grp == "stack":
                    m = 0.0                                   # the stone starts resting on the one below
                elif a.grp in ("car",) and b.name == "hub column":
                    continue
                else:
                    m = MARGIN
                if a.name.startswith("held") and b.name == "hub column":
                    m = MARGIN
                if overlap(a, b, m):
                    clashes.append((i, s["label"], a.name, b.name))
        for h in held:
            zmax = max(zmax, h.corners()[:, 2].max())
            if s["spin"] > 1 and s["spin"] < 89:
                zmin_spin = min(zmin_spin, h.corners()[:, 2].min())
    return clashes, brush, zmax, zmin_spin


# ================================================================== drawing
def hull(P):
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


def render(S, out_gif, sheet):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib.patches import Polygon, Circle
    from PIL import Image

    ACTS = ["lift", "doors", "shaft Z", "turn", "spin", "vacuum", "wheels"]

    def draw(s, fig):
        fig.clf()
        ax = fig.add_axes([0.0, 0.10, 0.60, 0.84], projection="3d")
        P = parts(s)
        for p in P:
            alpha = 0.35 if p.name == "hub column" else 0.95
            pc = Poly3DCollection(p.faces(), facecolor=p.col, edgecolor="0.2", linewidths=0.3, alpha=alpha)
            ax.add_collection3d(pc)
        ax.plot([-450, 300], [0, 0], [0, 0], lw=0)
        ax.set_xlim(-440, 260); ax.set_ylim(-420, 380); ax.set_zlim(0, 400)
        ax.set_box_aspect((700, 800, 400))
        ax.view_init(elev=24, azim=128)
        ax.set_axis_off()
        zl = 350
        xx, yy = np.meshgrid([-300, 200], [-200, 330])
        ax.plot_wireframe(xx, yy, np.full_like(xx, zl, dtype=float), color="r", lw=0.4, alpha=0.4)
        ax.text(-300, -200, zl + 8, "350 mm", color="r", fontsize=7)
        # top view
        a2 = fig.add_axes([0.60, 0.22, 0.39, 0.72])
        for p in sorted(P, key=lambda q: q.corners()[:, 2].max()):
            H = hull(p.corners()[:, :2])
            a2.add_patch(Polygon(H, closed=True, fc=p.col, ec="0.2", lw=0.4,
                                 alpha=0.35 if p.name == "hub column" else 0.9))
        a2.add_patch(Circle((0, 0), 333, fill=False, ls="--", ec="#c0392b", lw=0.6))
        a2.text(-330, 300, "stone sweep r 333", color="#c0392b", fontsize=6)
        a2.set_xlim(-440, 260); a2.set_ylim(-470, 380); a2.set_aspect("equal")
        a2.set_xticks([]); a2.set_yticks([])
        a2.set_title("top view (front = up)", fontsize=8)
        fig.text(0.02, 0.955, "Central hub option E: clapet doors + ONE shaft (Z + turn + spin), "
                 "one stone at a time, top > middle > bottom", fontsize=9, weight="bold")
        fig.text(0.02, 0.05, s["label"], fontsize=9)
        x = 0.62
        for a in ACTS:
            on = a in s["act"] or (a == "vacuum" and s["vac"])
            fig.text(x, 0.12, a, fontsize=7.5, color="white" if on else "0.35",
                     bbox=dict(fc="#c2185b" if on else "0.9", ec="none", pad=1.5))
            x += 0.052
        fig.text(0.62, 0.17, f"Z {s['z']:.0f}  turn {s['phi']:.0f}°  spin {s['spin']:.0f}°  doors "
                 f"{'open' if s['d'] > 0.5 else 'clamped'}", fontsize=7.5)

    fig = plt.figure(figsize=(11, 6), dpi=80)
    frames = []
    for i, s in enumerate(S):
        draw(s, fig)
        fig.canvas.draw()
        im = Image.frombuffer("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB")
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
        if sheet and i == next(j for j, t in enumerate(S) if t["label"].startswith("middle: carriage turns 90")) + 10:
            im.save(sheet)
    frames[0].save(out_gif, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)


# ================================================================== main
def main():
    S = sequence()
    clashes, brush, zmax, zmin_spin = check(S)
    lines = ["Central hub option E (Ayoub, 2026-11-19, concept): clapet doors + one shaft carriage on the hub",
             f"states: {len(S)}, margin {MARGIN} mm (cup vs stone faces: 0, touching = grip)",
             f"door top z {DOOR_Z[1]:.0f}; stones turn with their bottom face at >= {Z_SWING - 55:.0f}",
             f"highest point (robot + held stone): {zmax:.1f} mm (limit 350 [GR F.3])",
             f"lowest stone corner during the spin: {zmin_spin:.1f} mm (> 0 = clears the table)",
             f"clashes: {len(clashes)}"]
    seen = set()
    for c in clashes:
        k = (c[1], c[2], c[3])
        if k not in seen:
            seen.add(k)
            lines.append(f"  state {c[0]}: {c[1]} | {c[2]} x {c[3]}")
    bl = [b for b in brush if "turns back" in b[1]]
    lines.append(f"cup touches / brushes a stack stone face (vacuum off) while turning back: {len(bl)} states"
                 + (" (" + ", ".join(sorted({b[2] for b in bl})) + ")" if bl else ""))
    rep = "\n".join(lines)
    print(rep)
    with open(os.path.join(ROOT, "hub_e_doors_report.txt"), "w", encoding="utf-8") as f:
        f.write(rep + "\n")
    if "--gif" in sys.argv:
        os.makedirs(SIM, exist_ok=True)
        render(S, os.path.join(SIM, "option_e_doors_sequence.gif"), os.path.join(SIM, "option_e_doors_sheet.png"))
        print("gif written")


if __name__ == "__main__":
    main()
