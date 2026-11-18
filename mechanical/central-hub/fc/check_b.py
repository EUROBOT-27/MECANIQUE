# check_b.py - option B concept check (one lift + one turret), plain Python (numpy + matplotlib, no FreeCAD).
# Every part is an oriented box; overlap test = separating axis theorem (15 axes), "tight" = overlap once both boxes
# grow by MARGIN. Same base_330 parts as fc/check_env_a.py (plate, drive motors, wheels, bridge).
# Run from mechanical/central-hub/:  python fc/check_b.py  -> hub_b_report.txt + ../simulations/central_hub/option_b_sheet.png
# Frame (as option A): X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table. mm.
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIM = os.path.join(ROOT, "..", "simulations", "central_hub")
MARGIN = 3.0

# ---- numbers -------------------------------------------------------------------------------------------------
STONE = np.array([320.0, 110.0, 110.0])     # nominal; tolerance +-4/5 [G D.4] -> worst 324 x 115
FACE = 170.0                                # stack face, as option A (stone centre at r 225)
LIFT = 10.0                                 # stack 10 mm off the table, as option A
Z_STACK = [55 + LIFT, 165 + LIFT, 275 + LIFT]   # bottom, middle, top stone centres = cup heights
UNPINCH = [40.0, 3.0, 3.0]                  # cup rise before the swing: bottom arm drop clears the wheel top (z 90), others lift off
Z_SPIN = 173.0                              # spin height: nominal corner 4 above the table, top 342
PARK = 20.0                                 # turret angle for every vertical move (cup rim >= 5 mm off the stack face)
CUP_DZ = -31.0                              # cup centre below the carriage centre (L-shaped arm)
CAR_H, BRIDGE_TOP, TOP_PLATE = 40.0, 73.0, 345.0
HOLDER_X = 100.0                            # fixed holder cups (3 per unit), off-centre on the stone face

def R_z(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def R_y(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

class Box:
    def __init__(s, name, lo, hi, R=np.eye(3), about=np.zeros(3)):
        lo, hi = np.array(lo, float), np.array(hi, float)
        s.name, s.h = name, (hi - lo) / 2
        s.R = R; s.c = R @ ((lo + hi) / 2 - about) + about
    def moved(s, R, about=np.zeros(3), name=None):
        b = Box.__new__(Box); b.name, b.h = name or s.name, s.h
        b.R = R @ s.R; b.c = R @ (s.c - about) + about; return b
    def corners(s):
        sg = np.array([[i, j, k] for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)])
        return s.c + (sg * s.h) @ s.R.T

def overlap(a, b, m=0.0):
    A, B = a.R, b.R; ha, hb = a.h + m / 2, b.h + m / 2
    t = b.c - a.c
    axes = [A[:, i] for i in range(3)] + [B[:, i] for i in range(3)]
    axes += [np.cross(A[:, i], B[:, j]) for i in range(3) for j in range(3)]
    for L in axes:
        n = np.linalg.norm(L)
        if n < 1e-9: continue
        L = L / n
        ra = sum(ha[i] * abs(A[:, i] @ L) for i in range(3))
        rb = sum(hb[i] * abs(B[:, i] @ L) for i in range(3))
        if abs(t @ L) > ra + rb - 1e-6: return False
    return True

# ---- fixed parts ---------------------------------------------------------------------------------------------
def fixed():
    f = [Box("plate", (-165, -140, 13.5), (165, 140, 18.5)),
         Box("drive motors", (-61.5, -18.5, 26.5), (61.5, 18.5, 63.5)),
         Box("wheel L", (-104, -45, 0), (-84, 45, 90)), Box("wheel R", (84, -45, 0), (104, 45, 90)),
         Box("bridge plate", (-70, -55, 68), (70, 55, 73)),
         Box("bridge wall F", (-70, 50, 18.5), (70, 55, 68)), Box("bridge wall R", (-70, -55, 18.5), (70, -50, 68)),
         Box("lift motor", (19, 64, 18.5), (61, 106, 58.5)), Box("lift coupler", (33, 78, 58.5), (47, 92, 78)),
         Box("top plate", (-40, -40, TOP_PLATE), (60, 105, 350))]
    for u, rot in (("F", 0), ("R", 180)):      # rear unit = front unit turned 180 deg
        Rz = R_z(rot)
        f.append(Box("holder bar " + u, (HOLDER_X - 12, 120, 18.5), (HOLDER_X + 12, 140, 340)).moved(Rz))
        for k, z in enumerate(Z_STACK):
            f.append(Box("holder cup %s%d" % (u, k), (HOLDER_X - 15, 140, z - 15), (HOLDER_X + 15, FACE, z + 15)).moved(Rz))
    return f

def stack_stone(unit, k, dz=0.0):
    z = Z_STACK[k] + dz
    return Box("stone %s%d" % (unit, k), (-STONE[0] / 2, FACE, z - 55), (STONE[0] / 2, FACE + 110, z + 55)).moved(
        R_z(0 if unit == "F" else 180))

# ---- moving parts (front arm drawn at turret 0 = pointing +Y; rear = +180) -------------------------------------
def carriage(c):
    return [Box("carriage", (-45, -45, c - CAR_H / 2), (45, 45, c + CAR_H / 2)),
            Box("nut ear", (25, 30, c - 15), (55, 100, c + 15))]

def arm(unit, c, th):
    cup = c + CUP_DZ
    parts = [Box("beam", (-12, 45, c - 8), (12, 112, c + 8)),
             Box("drop", (-12, 100, cup - 10), (12, 112, c + 8)),
             Box("spin servo", (-20, 112, cup - 12), (20, 150, cup + 28)),   # body mostly above the cup axis
             Box("cup", (-15, 150, cup - 15), (15, FACE, cup + 15))]
    Rz = R_z(th + (0 if unit == "F" else 180))
    return [p.moved(Rz, name="%s %s" % (unit, p.name)) for p in parts]

def held_stone(unit, cup, th, spin=0.0, size=STONE):
    # stone held at its face centre; spin = turn about the arm's radial axis (stone stands up at 90)
    b = Box("held stone " + unit, (-size[0] / 2, FACE, cup - size[2] / 2), (size[0] / 2, FACE + size[1], cup + size[2] / 2))
    piv = np.array([0, FACE + size[1] / 2, cup])
    b = b.moved(R_spin(spin), piv)
    return b.moved(R_z(th + (0 if unit == "F" else 180)))

def R_spin(a):   # about the Y axis (radial for the front arm at turret 0)
    return R_y(a)

# ---- sequence ------------------------------------------------------------------------------------------------
def lin(a, b, n): return list(np.linspace(a, b, n))

def sequence():
    """yields (label, c, th, held: None or dict(cup, spin), level k, stones still in the stack)"""
    steps = []
    in_stack = {0, 1, 2}
    c = Z_STACK[2] - CUP_DZ
    for k in (2, 1, 0):                                   # top, middle, bottom
        ce = Z_STACK[k] - CUP_DZ
        for cc in lin(c, ce, 8): steps.append(("L%d move to level (park)" % k, cc, PARK, None, k, set(in_stack)))
        for t in lin(PARK, 0, 6): steps.append(("L%d engage" % k, ce, t, None, k, set(in_stack)))
        in_stack.discard(k)
        cu = ce + UNPINCH[k]
        for cc in lin(ce, cu, 3): steps.append(("L%d unpinch" % k, cc, 0, dict(cup=cc + CUP_DZ, spin=0), k, set(in_stack)))
        for t in lin(0, 90, 31): steps.append(("L%d swing out" % k, cu, t, dict(cup=cu + CUP_DZ, spin=0), k, set(in_stack)))
        cs = Z_SPIN - CUP_DZ
        for cc in lin(cu, cs, 8): steps.append(("L%d to spin height" % k, cc, 90, dict(cup=cc + CUP_DZ, spin=0), k, set(in_stack)))
        for a in lin(0, 90, 31): steps.append(("L%d spin" % k, cs, 90, dict(cup=Z_SPIN, spin=a), k, set(in_stack)))
        cset = STONE[0] / 2 - CUP_DZ
        for cc in lin(cs, cset, 4): steps.append(("L%d set on table" % k, cc, 90, dict(cup=cc + CUP_DZ, spin=90), k, set(in_stack)))
        for t in lin(90, PARK, 24): steps.append(("L%d return" % k, cset, t, None, k, set(in_stack)))
        c = cset
    return steps

def intended(label, k, a, b):
    """contact by design: the cup on its stone while engaging, the held stone on its holder cup / the stone below
    at the very start of the unpinch (both vented / lifted right after)"""
    u = a[0] if a[0] in "FR" else a[-1]
    if "engage" in label and a.endswith("cup") and b == "stone %s%d" % (u, k): return True
    if ("unpinch" in label or "swing out" in label) and a.startswith("held stone") and b in (
            "holder cup %s%d" % (u, k), "stone %s%d" % (u, k - 1)): return True
    return False

def check():
    F = fixed()
    out, clashes, tight = [], {}, {}
    zmax, zmin, cmin, cmax = -1e9, 1e9, 1e9, -1e9
    steps = sequence()
    for label, c, th, held, k, in_stack in steps:
        cmin, cmax = min(cmin, c), max(cmax, c)
        mov = carriage(c)
        for u in ("F", "R"):
            mov += arm(u, c, th)
        stones_fixed = [stack_stone(u, j, 0) for u in ("F", "R") for j in in_stack]
        helds = [held_stone(u, held["cup"], th, held["spin"]) for u in ("F", "R")] if held else []
        own = {"F": [], "R": []}
        for a in mov + helds:
            pts = a.corners(); zmax = max(zmax, pts[:, 2].max()); zmin = min(zmin, pts[:, 2].min())
        pairs = []
        for a in mov:
            for b in F + stones_fixed:
                if a.name in ("carriage", "nut ear") and b.name in ("top plate",): continue
                pairs.append((a, b))
        for a in helds:
            for b in F + stones_fixed + [m for m in mov if not m.name.startswith(a.name[-1] + " ")]:
                pairs.append((a, b))
        if len(helds) == 2: pairs.append((helds[0], helds[1]))
        for a in mov:                      # front arm vs rear arm parts
            if a.name.startswith("F "):
                for b in mov:
                    if b.name.startswith("R "): pairs.append((a, b))
        for a, b in pairs:
            key = (a.name, b.name)
            if intended(label, k, a.name, b.name): continue
            if overlap(a, b):
                clashes.setdefault(key, []).append(label)
            elif overlap(a, b, MARGIN):
                tight.setdefault(key, []).append(label)
    return steps, clashes, tight, zmin, zmax, cmin, cmax

def spin_envelope(size, zc):
    best = (1e9, -1e9)
    for a in np.linspace(0, 90, 181):
        b = Box("s", (-size[0] / 2, -size[1] / 2, -size[2] / 2), (size[0] / 2, size[1] / 2, size[2] / 2)).moved(R_y(a))
        z = b.corners()[:, 2] + zc
        best = (min(best[0], z.min()), max(best[1], z.max()))
    return best

def main():
    steps, clashes, tight, zmin, zmax, cmin, cmax = check()
    L = []
    P = L.append
    P("Central hub - option B (one lift + one turret) - concept check, %d steps, both units" % len(steps))
    P("")
    P("Order: top, middle, bottom. Each level: park %g deg, move to the level, engage (turret %g -> 0), unpinch, swing 0 -> 90," % (PARK, PARK))
    P("lift to the spin height %g, spin 90, set on the table, vent, turn back to %g." % (Z_SPIN, PARK))
    P("")
    P("== Height budget ==")
    P("carriage centre %.0f .. %.0f -> block %.0f .. %.0f (bridge top %.0f, top plate %.0f)" %
      (cmin, cmax, cmin - CAR_H / 2, cmax + CAR_H / 2, BRIDGE_TOP, TOP_PLATE))
    P("lift stroke %.0f mm; moving parts + held stones z %.1f .. %.1f (limits 0 / 350 [GR F.3])" % (cmax - cmin, zmin, zmax))
    P("")
    P("== Spin (stone turns about the cup axis at its face centre) ==")
    for nm, sz in (("nominal 320 x 110", STONE), ("worst 324 x 115", np.array([324.0, 115.0, 115.0]))):
        lo, hi = spin_envelope(sz, Z_SPIN)
        P("%-18s at %g: lowest corner %.1f, highest %.1f" % (nm, Z_SPIN, lo, hi))
    P("Any in-plane stand-up needs 320 sin a + 110 cos a = 338 mm of height at a = 71 deg (out of 350): the margin is")
    P("physics, not mechanism. B sets the spin height with a homed stepper (option A: N20 + switch on a printed rail).")
    P("")
    P("== Cup clearance to the stack face while parked ==")
    th = np.radians(PARK)
    P("turret %g deg: cup rim %.1f mm off the face (face at r %g)" % (PARK, FACE - (FACE * np.cos(th) + 15 * np.sin(th)), FACE))
    P("")
    P("== Clashes (overlap; intended contacts left out: cup on its stone while engaging, held stone leaving its holder cup and the stone below) ==")
    P("none" if not clashes else "")
    for (a, b), labs in clashes.items():
        P("%s x %s: %d steps (%s ... %s)" % (a, b, len(labs), labs[0], labs[-1]))
    P("")
    P("== Closer than %g mm (not a clash) ==" % MARGIN)
    P("none" if not tight else "")
    for (a, b), labs in tight.items():
        P("%s x %s: %d steps (%s ... %s)" % (a, b, len(labs), labs[0], labs[-1]))
    txt = "\n".join(L)
    with open(os.path.join(ROOT, "hub_b_report.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)
    sheet()

def hull(P):   # 2D convex hull, monotone chain
    pts = sorted(set(map(tuple, np.round(P, 6))))
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h[:-1]
    return np.array(half(pts) + half(pts[::-1]))

def sheet():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    fig, ax = plt.subplots(1, 3, figsize=(16, 5.6))
    def draw(a, b, plane, **kw):
        pts = b.corners()
        i, j = plane
        P2 = pts[:, [i, j]]
        a.add_patch(Polygon(hull(P2), closed=True, **kw))
    F = fixed()
    # top view
    a = ax[0]; a.set_title("Top view: turret 0 / 45 / 90 deg (front unit left, rear unit right)")
    for b in F:
        draw(a, b, (0, 1), fc="#d9d9d9", ec="#888", lw=0.6)
    for u in ("F", "R"):
        for j in (0, 1):
            draw(a, stack_stone(u, j), (0, 1), fc="#f1e2c3", ec="#a08850", lw=0.6)
    for th, al in ((0, 0.25), (45, 0.45), (90, 1.0)):
        for u in ("F", "R"):
            for p in arm(u, 280, th): draw(a, p, (0, 1), fc="#3b6fb6", ec="#1d3c66", alpha=al, lw=0.6)
            draw(a, held_stone(u, 285, th), (0, 1), fc="#e39b3a", ec="#8a5212", alpha=al * 0.7, lw=0.8)
    for b in carriage(280): draw(a, b, (0, 1), fc="#6aa56a", ec="#2e5e2e", lw=0.6)
    a.set_xlim(-300, 300); a.set_ylim(-300, 300); a.set_aspect("equal"); a.grid(alpha=0.3)
    a.set_xlabel("x (mm, robot's left = -x)"); a.set_ylabel("y (mm, forward)")
    # side view (y-z), front unit at turret 0, three cup heights
    a = ax[1]; a.set_title("Side view (y-z): lift positions for the 3 levels")
    for b in F:
        if abs(b.c[0]) < 170: draw(a, b, (1, 2), fc="#d9d9d9", ec="#888", lw=0.6)
    for u in ("F", "R"):
        for j in range(3): draw(a, stack_stone(u, j), (1, 2), fc="#f1e2c3", ec="#a08850", lw=0.6)
    for k, col in zip(range(3), ("#5b8bd0", "#7a5bd0", "#d07a5b")):
        c = Z_STACK[k] - CUP_DZ
        for p in arm("F", c, 0) + arm("R", c, 0) + carriage(c):
            draw(a, p, (1, 2), fc=col, ec="k", alpha=0.35, lw=0.5)
    a.axhline(350, color="r", lw=1, ls="--"); a.text(-290, 352, "350 [GR F.3]", color="r", fontsize=8)
    a.set_xlim(-300, 300); a.set_ylim(-10, 380); a.set_aspect("equal"); a.grid(alpha=0.3)
    a.set_xlabel("y (mm)"); a.set_ylabel("z (mm)")
    # spin envelope (front stone at turret 90, seen along x)
    a = ax[2]; a.set_title("Spin at z %g (seen from the robot's left)" % Z_SPIN)
    for ang in np.linspace(0, 90, 7):
        b = held_stone("F", Z_SPIN, 90, ang)
        draw(a, b, (1, 2), fc="none", ec="#e39b3a", lw=1.2 if ang in (0, 90) else 0.6)
    b = held_stone("F", STONE[0] / 2, 90, 90)
    draw(a, b, (1, 2), fc="#e39b3a", ec="#8a5212", alpha=0.5)
    a.axhline(0, color="k", lw=1); a.axhline(350, color="r", lw=1, ls="--")
    lo, hi = spin_envelope(STONE, Z_SPIN)
    a.text(-170, 355, "highest %.0f" % hi, color="r", fontsize=8); a.text(-170, -12, "lowest %.0f" % lo, fontsize=8)
    a.set_xlim(-200, 200); a.set_ylim(-25, 380); a.set_aspect("equal"); a.grid(alpha=0.3)
    a.set_xlabel("y (mm)"); a.set_ylabel("z (mm)")
    fig.suptitle("Central hub option B: 1 lift (NEMA17 + T8) + 1 turret (MG996R) + 2 spin MG996R, fixed holder cups", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(SIM, "option_b_sheet.png"), dpi=110)

if __name__ == "__main__":
    main()
