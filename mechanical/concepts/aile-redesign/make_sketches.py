# make_sketches.py - rough, to-scale sketches of the door unit (A_AILE) redesign options -> img/option_<X>.png
# Run from anywhere:  python mechanical/concepts/aile-redesign/make_sketches.py
# Module coordinates in mm (clapets v7): x across (x 150 = module limit), y toward the stack, z up from the table.
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Patch, Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img")
os.makedirs(OUT, exist_ok=True)

PART, CAP, BOUGHT, GEAR, GHOST, LIMIT, INK = "#2f6fb0", "#6b4fb0", "#3d4448", "#c56f22", "#9aa8a6", "#b0521c", "#1c2928"
STYLE = {
    "part": dict(fc=PART + "2e", ec=PART, lw=1.4),
    "cap": dict(fc=CAP + "2e", ec=CAP, lw=1.4),
    "bought": dict(fc=BOUGHT + "40", ec=BOUGHT, lw=0.9),
    "gear": dict(fc="none", ec=GEAR, lw=1.2, ls=(0, (3, 2))),
    "ghost": dict(fc="none", ec=GHOST, lw=0.9, ls=(0, (4, 2))),
    "ghostfill": dict(fc="#e3e9e8", ec=GHOST, lw=0.8),
    "hole": dict(fc="white", ec=INK, lw=0.9),
    "win": dict(fc="white", ec=PART, lw=1.0),
}


def rect(ax, x0, a0, x1, a1, k, **kw):
    ax.add_patch(Rectangle((x0, a0), x1 - x0, a1 - a0, **{**STYLE[k], **kw}))


def poly(ax, pts, k):
    ax.add_patch(Polygon(pts, closed=True, **STYLE[k]))


def circ(ax, x, a, r, k):
    ax.add_patch(Circle((x, a), r, **STYLE[k]))


def txt(ax, x, a, s, c="#5b6b69", ha="left", size=7.5, bold=False):
    ax.text(x, a, s, color=c, ha=ha, va="center", fontsize=size, fontweight="bold" if bold else "normal", family="monospace")


# ---------------------------------------------------------------- context, same in every option
def front_context(ax, arm_lo=(39, 49)):
    ax.axhline(0, color=GHOST, lw=1)
    txt(ax, 52, 4, "table z 0")
    rect(ax, 50, 55, 95, 245, "ghostfill")
    txt(ax, 53, 150, "butterfly\nplate")
    ax.axvline(150, color=LIMIT, lw=1, ls=(0, (6, 3)))
    txt(ax, 149, 262, "x 150 limit", c=LIMIT, ha="right")
    for z0, z1 in (arm_lo, (212, 222)):
        rect(ax, 120, z0, 168, z1, "ghost")
        txt(ax, 166, z1 + 4, "arm", ha="right")
    rect(ax, 168, 20, 171, 265, "ghost")
    txt(ax, 173, 140, "door\nsheet")
    for z in (65, 235):
        circ(ax, 85, z, 2.6, "hole")
    txt(ax, 85, 58, "M4", ha="center", size=6.5)
    txt(ax, 85, 228, "M4", ha="center", size=6.5)


def top_context(ax):
    rect(ax, 50, 47.5, 95, 50.5, "ghostfill")
    txt(ax, 52, 44, "plate")
    ax.axvline(150, color=LIMIT, lw=1, ls=(0, (6, 3)))
    ax.axhline(140, color=GHOST, lw=1, ls=(0, (4, 2)))
    txt(ax, 52, 144, "stack face y 140")
    poly(ax, [(124, 74), (139, 72), (168, 127), (168, 136.5), (156, 136.5), (123, 90)], "ghost")
    txt(ax, 152, 104, "arm")
    rect(ax, 168, 127, 171, 183, "ghost")


def rod_front(ax, z0=30, z1=233):
    rect(ax, 127, z0, 135, z1, "bought")
    ax.plot([131, 131], [z0 - 6, z1 + 6], color=INK, lw=0.6, ls=(0, (8, 2, 2, 2)))
    txt(ax, 137, (z0 + z1) / 2 + 30, "rod")


def brg_front(ax, z):
    rect(ax, 120, z, 142, z + 7, "bought")
    txt(ax, 131, z + 3.5, "608", ha="center", size=6.5, c="white")


def servo_top_std(ax):
    rect(ax, 100.8, 41.8, 141.2, 62.2, "bought")
    for x, y in ((96.5, 47), (96.5, 57), (145.5, 47), (145.5, 57)):
        circ(ax, x, y, 1.8, "hole")
    txt(ax, 121, 52, "MG996R", ha="center", c="white", bold=True)


def gears_top(ax):
    circ(ax, 131, 82, 18.75, "gear")
    circ(ax, 131, 52, 13.75, "gear")
    txt(ax, 151, 76, "28T", c=GEAR)


def rod_top(ax):
    circ(ax, 131, 82, 4, "bought")


# ---------------------------------------------------------------- options
def front_A(ax):
    poly(ax, [(66, 27), (150, 27), (150, 87), (147, 87), (147, 36), (100, 36), (100, 77), (92, 77), (92, 75), (66, 75)], "part")
    rect(ax, 142, 36, 150, 77, "part")
    rect(ax, 143.5, 68, 148.5, 74, "win")
    rect(ax, 93, 68, 99, 74, "win")
    poly(ax, [(66, 222), (95, 222), (95, 224), (150, 224), (150, 240), (66, 245)], "cap")
    brg_front(ax, 29)
    brg_front(ax, 226)
    rod_front(ax)
    rect(ax, 100.8, 49, 141.2, 87, "bought")
    txt(ax, 121, 62, "servo", ha="center", c="white", bold=True)
    rect(ax, 112, 96.4, 150, 104.4, "gear")
    txt(ax, 110, 100, "gears", ha="right", c=GEAR)
    txt(ax, 68, 31, "LOW BRACKET", c=PART, bold=True)
    txt(ax, 68, 250, "HIGH BRACKET", c=CAP, bold=True)
    txt(ax, 152, 71, "nut\nwindows", c=PART, size=6.5)


def top_A(ax):
    poly(ax, [(66, 50.5), (95, 50.5), (95, 40), (150, 40), (150, 96), (117, 96.5), (110, 82), (66, 66)], "part")
    servo_top_std(ax)
    gears_top(ax)
    rod_top(ax)
    txt(ax, 68, 58, "low bracket", c=PART, bold=True)
    txt(ax, 97, 36, "servo sits beside the plate (x > 95)")


def front_B(ax):
    poly(ax, [(66, 27), (150, 27), (150, 226), (66, 226), (66, 160), (100, 160), (100, 110), (66, 110)], "part")
    rect(ax, 104, 125, 144, 205, "win")
    txt(ax, 124, 165, "window", ha="center", c=PART)
    rect(ax, 70, 30, 96, 60, "win")
    rect(ax, 66, 226, 150, 238, "cap")
    brg_front(ax, 29)
    brg_front(ax, 226)
    rod_front(ax)
    rect(ax, 100.8, 49, 141.2, 87, "bought")
    txt(ax, 121, 62, "servo", ha="center", c="white", bold=True)
    rect(ax, 112, 96.4, 150, 104.4, "gear")
    txt(ax, 68, 22, "SPINE (one part)", c=PART, bold=True)
    txt(ax, 68, 244, "CAP, 2 screws", c=CAP, bold=True)


def top_B(ax):
    poly(ax, [(66, 50.5), (95, 50.5), (95, 40), (150, 40), (150, 96), (144, 96), (144, 53.5), (69, 53.5), (69, 66), (66, 66)], "part")
    circ(ax, 131, 82, 14.5, "part")
    servo_top_std(ax)
    gears_top(ax)
    rod_top(ax)
    txt(ax, 97, 36, "C-channel: wall on the plate + outer wall", c=PART)
    txt(ax, 100, 104, "608 boss (bottom, and in the cap)")


def front_C(ax):
    poly(ax, [(66, 27), (150, 27), (150, 40), (95, 40), (95, 75), (66, 75)], "part")
    poly(ax, [(66, 160), (95, 160), (95, 178), (100, 178), (100, 226), (150, 226), (150, 240), (66, 245)], "cap")
    rect(ax, 142, 178, 150, 226, "cap")
    brg_front(ax, 29)
    brg_front(ax, 226)
    rod_front(ax)
    rect(ax, 100.8, 185, 141.2, 223, "bought")
    txt(ax, 121, 204, "servo\nupside down", ha="center", c="white", bold=True)
    rect(ax, 112, 167.6, 150, 175.6, "gear")
    txt(ax, 110, 171, "gears", ha="right", c=GEAR)
    txt(ax, 68, 22, "BEARING BLOCK", c=PART, bold=True)
    txt(ax, 68, 250, "HIGH BRACKET + DRIVE", c=CAP, bold=True)


def top_C(ax):
    poly(ax, [(66, 50.5), (95, 50.5), (95, 40), (150, 40), (150, 96), (117, 96.5), (110, 82), (66, 66)], "cap")
    servo_top_std(ax)
    gears_top(ax)
    rod_top(ax)
    txt(ax, 68, 58, "high bracket", c=CAP, bold=True)
    txt(ax, 97, 36, "same footprint as A, but at the top")


def front_D(ax):
    poly(ax, [(66, 27), (150, 27), (150, 98), (108, 98), (108, 75), (66, 75)], "part")
    poly(ax, [(66, 222), (95, 222), (95, 224), (150, 224), (150, 240), (66, 245)], "cap")
    rect(ax, 120.8, 27, 141.2, 74.4, "bought")
    txt(ax, 131, 50, "servo", ha="center", c="white", bold=True)
    rect(ax, 125, 74.4, 137, 84, "gear")
    txt(ax, 123, 79, "coupler", ha="right", c=GEAR)
    brg_front(ax, 86)
    brg_front(ax, 226)
    rod_front(ax, 84, 233)
    txt(ax, 68, 22, "LOW BRACKET = SERVO CRADLE", c=PART, bold=True)
    txt(ax, 68, 250, "HIGH BRACKET", c=CAP, bold=True)
    txt(ax, 166, 118, "low arm moved up", ha="right", c=LIMIT, size=6.5)


def top_D(ax):
    poly(ax, [(66, 50.5), (108, 50.5), (108, 44), (150, 44), (150, 100), (112, 100), (112, 66), (66, 66)], "part")
    rect(ax, 120.8, 51.8, 141.2, 92.2, "bought")
    for y in (47.5, 96.5):
        circ(ax, 131, y, 1.8, "hole")
    txt(ax, 131, 64, "MG996R\nturned 90°", ha="center", c="white", bold=True)
    rod_top(ax)
    txt(ax, 97, 40, "servo under the rod, output on the rod axis", c=PART)


OPTIONS = {
    "A": ("A · Two corner brackets", front_A, top_A, None),
    "B": ("B · Spine + cap", front_B, top_B, None),
    "C": ("C · Brackets, drive on top", front_C, top_C, None),
    "D": ("D · Direct drive, no gears", front_D, top_D, (100, 110)),
}


def legend(fig):
    items = [Patch(**STYLE["part"], label="new printed part"), Patch(**STYLE["cap"], label="2nd printed part"),
             Patch(**STYLE["bought"], label="bought (servo, 608, rod)"), Patch(**STYLE["gear"], label="gears / coupler"),
             Patch(**STYLE["ghost"], label="context (plate, arms, door sheet)")]
    fig.legend(handles=items, loc="lower center", ncol=5, fontsize=8, frameon=False)


def draw(key):
    title, front, top, arm_lo = OPTIONS[key]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 7.6), gridspec_kw=dict(width_ratios=[1, 1.15]))
    front_context(a1, arm_lo or (39, 49))
    front(a1)
    a1.set_xlim(50, 185)
    a1.set_ylim(-5, 270)
    a1.set_title("Front view: looking at the plate from the stack side (x →, z ↑)", fontsize=9, color=INK)
    top_context(a2)
    top(a2)
    a2.set_xlim(50, 185)
    a2.set_ylim(150, 30)                       # y grows toward the stack (down the page)
    a2.set_title("Top view: looking down (x →, y ↓ toward the stack)", fontsize=9, color=INK)
    for a in (a1, a2):
        a.set_aspect("equal")
        a.tick_params(labelsize=7, colors="#5b6b69")
        a.grid(True, color="#e3e9e8", lw=0.5)
        for s in a.spines.values():
            s.set_color("#c8d2d0")
    fig.suptitle(title, fontsize=14, fontweight="bold", color=INK, x=0.02, ha="left")
    legend(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    path = os.path.join(OUT, "option_%s.png" % key)
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


if __name__ == "__main__":
    for k in OPTIONS:
        print(draw(k))
