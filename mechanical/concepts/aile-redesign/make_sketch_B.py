# make_sketch_B.py - detailed sketch of option B (spine + cap) drawn along the load paths -> img/B_detail.png
# Run: python mechanical/concepts/aile-redesign/make_sketch_B.py
# Module mm (clapets v7, right door unit): x across (150 = limit), y toward the stack, z up from the table.
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Patch, Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img")
os.makedirs(OUT, exist_ok=True)

PART, CAP, BOUGHT, GEAR, GHOST, LIMIT, INK, KEEP = "#2f6fb0", "#6b4fb0", "#3d4448", "#c56f22", "#9aa8a6", "#b0521c", "#1c2928", "#d9534f"
S = {
    "part": dict(fc=PART + "33", ec=PART, lw=1.4),
    "partd": dict(fc=PART + "66", ec=PART, lw=1.4),
    "cap": dict(fc=CAP + "33", ec=CAP, lw=1.4),
    "bought": dict(fc=BOUGHT + "40", ec=BOUGHT, lw=0.9),
    "gear": dict(fc="none", ec=GEAR, lw=1.2, ls=(0, (3, 2))),
    "ghost": dict(fc="none", ec=GHOST, lw=0.9, ls=(0, (4, 2))),
    "ghostfill": dict(fc="#e3e9e8", ec=GHOST, lw=0.8),
    "hole": dict(fc="white", ec=INK, lw=0.9),
    "win": dict(fc="white", ec=PART, lw=1.1),
    "keep": dict(fc=KEEP + "18", ec=KEEP, lw=0.8, ls=(0, (2, 2)), hatch="////"),
    "nutwin": dict(fc="#ffe9a8", ec="#b07b00", lw=1.1),
}


def R(ax, x0, a0, x1, a1, k, **kw):
    ax.add_patch(Rectangle((x0, a0), x1 - x0, a1 - a0, **{**S[k], **kw}))


def RR(ax, x0, a0, x1, a1, k, r=4):     # rounded window
    ax.add_patch(FancyBboxPatch((x0 + r, a0 + r), x1 - x0 - 2 * r, a1 - a0 - 2 * r, boxstyle="round,pad=%g" % r, **S[k]))


def P(ax, pts, k):
    ax.add_patch(Polygon(pts, closed=True, **S[k]))


def C(ax, x, a, r, k):
    ax.add_patch(Circle((x, a), r, **S[k]))


def T(ax, x, a, s, c="#5b6b69", ha="left", size=7.2, bold=False):
    ax.text(x, a, s, color=c, ha=ha, va="center", fontsize=size, fontweight="bold" if bold else "normal", family="monospace")


def rib(ax, xa, za, xb, zb, w=3.2):       # S-curved rib band, w wide, from (xa, za) to (xb, zb)
    t = np.linspace(0, 1, 60)
    s_ = t * t * (3 - 2 * t)                 # smoothstep: vertical at both ends, diagonal in the middle
    x = xa + (xb - xa) * s_
    z = za + (zb - za) * t
    dx, dz = np.gradient(x), np.gradient(z)
    n = np.hypot(dx, dz)
    nx, nz = -dz / n * w / 2, dx / n * w / 2
    pts = list(zip(x + nx, z + nz)) + list(zip((x - nx)[::-1], (z - nz)[::-1]))
    ax.add_patch(Polygon(pts, closed=True, **S["partd"]))


def arch_win(ax, x0, x1, z0, z1):        # window: rounded bottom, pointed-arch (45 deg) top
    w = x1 - x0
    xc = (x0 + x1) / 2
    t = np.linspace(np.pi, 2 * np.pi, 20)
    bottom = [(xc + w / 2 * np.cos(a), z0 + w / 2 + w / 2 * np.sin(a)) for a in t]
    top = [(x1, z1 - w / 2), (xc, z1), (x0, z1 - w / 2)]
    ax.add_patch(Polygon(bottom + top, closed=True, **S["win"]))


def tri_win(ax, pts, inset=0):        # truss window (polygon, rounded look via thick white edge)
    ax.add_patch(Polygon(pts, closed=True, fc="white", ec=PART, lw=1.1, joinstyle="round"))


# ---------------------------------------------------------------- FRONT VIEW (from the stack side): x ->, z ^
def front(ax):
    ax.axhline(0, color=GHOST, lw=1)
    T(ax, 52, 4, "table z 0")
    R(ax, 50, 55, 95, 245, "ghostfill")
    T(ax, 52, 150, "plate")
    ax.axvline(150, color=LIMIT, lw=1, ls=(0, (6, 3)))
    T(ax, 149, 262, "x 150", c=LIMIT, ha="right")
    # spine: keel on the plate (x 66..95) + back wall behind the servo (x 95..150) + outer wall edge (x 147..150)
    P(ax, [(66, 27), (150, 27), (150, 226), (66, 226)], "part")
    # keel window between the M4s, pointed-arch top (prints upright with no support)
    arch_win(ax, 71, 91, 84, 206)
    T(ax, 81, 140, "window", c=PART, ha="center", size=6.3)
    # curved ribs in the back wall above the gears: two S-curves from the bottom pod corners to the top pod
    R(ax, 98, 110, 145, 216, "win")
    for (xa, za), (xb, zb) in (((99, 112), (144, 214)), ((144, 112), (99, 214))):
        rib(ax, xa, za, xb, zb)
    T(ax, 121.5, 222, "curved ribs (load paths)", c=PART, ha="center", size=6.3)
    # bottom shelf + bearing boss, top shelf
    R(ax, 66, 27, 150, 36, "partd")
    R(ax, 66, 218, 150, 226, "partd")
    # cap with a stiffening rib on top
    P(ax, [(66, 226), (150, 226), (150, 236), (66, 236)], "cap")
    T(ax, 108, 241, "flat cap, 2 screws", c=CAP, ha="center", size=6.5, bold=True)
    # bought parts
    for z in (29, 226):
        R(ax, 120, z, 142, z + 7, "bought")
    R(ax, 127, 30, 135, 233, "bought")
    ax.plot([131, 131], [24, 239], color=INK, lw=0.6, ls=(0, (8, 2, 2, 2)))
    R(ax, 100.8, 49, 141.2, 87, "bought")
    T(ax, 121, 60, "servo", c="white", ha="center", bold=True)
    R(ax, 112, 96.4, 150, 104.4, "gear")
    R(ax, 121, 104.4, 141, 126.4, "gear")
    T(ax, 110, 100, "gears (open)", c=GEAR, ha="right")
    # arm keep-out zones around the rod
    for z0, z1 in ((39, 49), (212, 222)):
        R(ax, 114, z0, 168, z1, "keep")
    T(ax, 168, 54, "arm swing\n(keep out)", c=KEEP, ha="right", size=6.3)
    for z in (65, 235):
        C(ax, 85, z, 2.6, "hole")
    T(ax, 85, 58, "M4", ha="center", size=6.5)
    T(ax, 68, 22, "SPINE", c=PART, bold=True)
    ax.set_xlim(50, 175)
    ax.set_ylim(-5, 268)
    ax.set_title("Front view, from the stack side (x →, z ↑)", fontsize=9, color=INK)


# ---------------------------------------------------------------- TOP VIEW: x ->, y down toward the stack
def top(ax):
    R(ax, 50, 47.5, 95, 50.5, "ghostfill")
    T(ax, 52, 45, "plate")
    ax.axvline(150, color=LIMIT, lw=1, ls=(0, (6, 3)))
    # bottom shelf outline (z 27..36), with the bearing boss in front
    P(ax, [(66, 50.5), (95, 50.5), (95, 38), (150, 38), (150, 80), (145.5, 90), (131, 96.5), (116.5, 90), (112, 80), (100, 66), (66, 60)], "part")
    # C-section walls (full height)
    R(ax, 66, 50.5, 95, 56, "partd")        # keel on the plate
    R(ax, 95, 38, 150, 41, "partd")         # back wall behind the servo
    R(ax, 92, 38, 98, 56, "partd")          # web keel <-> back wall
    R(ax, 147, 38, 150, 66, "partd")        # outer wall
    T(ax, 68, 62.5, "keel on the plate", c=PART, size=6.5)
    T(ax, 99, 35, "back wall (behind the servo)", c=PART, size=6.5)
    T(ax, 152, 52, "outer\nwall", c=PART, size=6.5)
    # servo + inner lip + outer posts with nut windows facing x 150
    R(ax, 100.8, 41.8, 141.2, 62.2, "bought")
    T(ax, 121, 52, "MG996R", c="white", ha="center", bold=True)
    R(ax, 92.7, 51, 100.3, 63, "partd")                       # inner post (ear y 57)
    C(ax, 96.5, 57, 1.8, "hole")
    R(ax, 93.6, 54.1, 99.4, 66, "nutwin")
    T(ax, 96.5, 70.5, "inner nut window\n-> front", c="#8a6100", ha="center", size=6.3)
    C(ax, 96.5, 47, 1.8, "ghost")
    T(ax, 82, 41.5, "4th ear on the plate edge:\nno screw", c=KEEP, ha="center", size=5.8)
    for y in (47, 57):
        C(ax, 145.5, y, 1.8, "hole")
        R(ax, 142.6, y - 2.9, 150.6, y + 2.9, "nutwin")
    T(ax, 152, 44, "2 nut windows\n-> robot side", c="#8a6100", size=6.3)
    # gears, rod, arm swing
    C(ax, 131, 82, 18.75, "gear")
    C(ax, 131, 52, 13.75, "gear")
    C(ax, 131, 82, 4, "bought")
    ax.add_patch(Circle((131, 82), 17, fc="none", ec=KEEP, lw=0.8, ls=(0, (2, 2))))
    T(ax, 112, 104, "arm swing r ≈ 17 (arm heights only)", c=KEEP, size=6.3)
    # cable slot in the outer wall
    R(ax, 147, 48, 150, 62, "win")
    T(ax, 152, 60, "cable slot", size=6.3)
    ax.axhline(140, color=GHOST, lw=1, ls=(0, (4, 2)))
    T(ax, 52, 137, "stack face y 140")
    ax.set_xlim(50, 175)
    ax.set_ylim(145, 30)
    ax.set_title("Top view (x →, y ↓ toward the stack); bottom shelf outline", fontsize=9, color=INK)


# ---------------------------------------------------------------- SIDE VIEW from outside (x+): y ->, z ^
def side(ax):
    ax.axhline(0, color=GHOST, lw=1)
    R(ax, 47.5, 55, 50.5, 245, "ghostfill")
    T(ax, 46, 150, "plate", ha="right")
    # outer wall face with windows
    R(ax, 38, 27, 66, 226, "part")
    arch_win(ax, 42, 62, 110, 205)
    T(ax, 52, 157, "window", c=PART, ha="center", size=6.3)
    # shelves reaching forward to the bearing bosses
    P(ax, [(38, 27), (96.5, 27), (96.5, 36), (66, 36), (38, 36)], "partd")
    P(ax, [(38, 218), (96.5, 218), (96.5, 226), (38, 226)], "partd")
    P(ax, [(38, 226), (96.5, 226), (96.5, 236), (38, 236)], "cap")
    # nut windows + cable slot on this face
    for y in (47, 57):
        R(ax, y - 2.9, 63, y + 2.9, 73, "nutwin")
    T(ax, 68, 68, "nut windows\n(servo ears)", c="#8a6100", size=6.3)
    R(ax, 48, 52, 62, 58, "win")
    T(ax, 68, 55, "cable slot", size=6.3)
    # bought + gears (behind the wall, dashed)
    R(ax, 41.8, 49, 62.2, 87, "ghost")
    T(ax, 52, 80, "servo\n(behind)", ha="center", size=6.3)
    for z in (29, 226):
        R(ax, 71, z, 93, z + 7, "bought")
    R(ax, 78, 30, 86, 233, "bought")
    R(ax, 63, 96.4, 101, 104.4, "gear")
    T(ax, 103, 100, "gears", c=GEAR)
    for z0, z1 in ((39, 49), (212, 222)):
        R(ax, 65, z0, 140, z1, "keep")
    T(ax, 104, 44, "arm", c=KEEP, size=6.3)
    T(ax, 104, 217, "arm", c=KEEP, size=6.3)
    ax.axvline(140, color=GHOST, lw=1, ls=(0, (4, 2)))
    T(ax, 139, 262, "stack face", ha="right")
    ax.set_xlim(30, 145)
    ax.set_ylim(-5, 268)
    ax.set_title("Side view from outside, the robot's side (y →, z ↑)", fontsize=9, color=INK)


def main():
    fig, axs = plt.subplots(1, 3, figsize=(17, 8.6), gridspec_kw=dict(width_ratios=[1.05, 1.15, 0.95]))
    front(axs[0])
    top(axs[1])
    side(axs[2])
    for a in axs:
        a.set_aspect("equal")
        a.tick_params(labelsize=7, colors="#5b6b69")
        a.grid(True, color="#e3e9e8", lw=0.5)
        for s in a.spines.values():
            s.set_color("#c8d2d0")
    fig.suptitle("Option B · spine + cap, along the load paths (detail v2: 3 servo screws, curved ribs, flat cap)", fontsize=14, fontweight="bold",
                 color=INK, x=0.01, ha="left")
    items = [Patch(**S["partd"], label="spine walls / shelves"), Patch(**S["part"], label="spine (behind)"),
             Patch(**S["cap"], label="cap"), Patch(**S["bought"], label="bought"), Patch(**S["gear"], label="gears"),
             Patch(**S["nutwin"], label="nut window"), Patch(**S["keep"], label="arm swing: keep out"),
             Patch(**S["ghost"], label="context")]
    fig.legend(handles=items, loc="lower center", ncol=8, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    path = os.path.join(OUT, "B_detail.png")
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(path)


if __name__ == "__main__":
    main()
