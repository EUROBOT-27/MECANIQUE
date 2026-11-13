# hub_gif.py - GIF of the grooved central hub on base_330 (front + rear units), front view + side view.
# Same geometry as the interactive drawing (concept: mechanical/concepts/central-hub-builder.md).
# Run with a Python that has matplotlib + Pillow, e.g. FreeCAD's:  <FreeCAD>/bin/python.exe hub_gif.py
# Output: ../simulations/central_hub/hub_base330.gif (+ hub_base330_end.png)
# Frame: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table. mm.
import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "simulations", "central_hub")
os.makedirs(OUT, exist_ok=True)

# --- base_330 (mechanical/base_330/base_330.py) ---
PLATE = dict(x=165, y=140, z0=13.5, z1=18.5)
MOT = dict(x=61.5, r=18.5, z=45)
WH_X, WH_W, WH_R = 94, 20, 45
# --- hub ---
R, CUP, FACE = 50, 165, 170           # hub radius, cup radius, stone face radius from the hub axis
ZH = [55, 165, 275]                   # stone centres in the stack (bottom, middle, top), base at 0
OFF = [40, 0, -40]                    # sleeve height - cup height (arm step at radius DROP)
DROP = 100
BR = dict(x=70, y0=50, y1=55, z=68, t=5)   # bridge over the drive motors
LIFT = 10

def groove(k, phi):
    t = max(0.0, min(1.0, phi / 90.0))
    f = 1 - (1 - t) ** 3
    return [105 * f, 0.0, -105 * f][k]

def direction(u, phi):
    a = math.radians(phi)
    d = (-math.sin(a), math.cos(a))
    return d if u == 0 else (-d[0], -d[1])

def stone(u, k, phi, rho):
    d = direction(u, phi); w = (-d[1], d[0])
    c = (d[0] * (FACE + 55), d[1] * (FACE + 55))
    r = math.radians(rho)
    hw = 160 * abs(math.cos(r)) + 55 * abs(math.sin(r))
    vh = 160 * abs(math.sin(r)) + 55 * abs(math.cos(r))
    zc = ZH[k] + LIFT + groove(k, phi)
    ex = abs(w[0]) * hw + abs(d[0]) * 55
    ey = abs(w[1]) * hw + abs(d[1]) * 55
    return c[0] - ex, c[0] + ex, c[1] - ey, c[1] + ey, zc - vh, zc + vh

def ease(t): return 2 * t * t if t < .5 else 1 - (-2 * t + 2) ** 2 / 2

# steps: per shaft index (0 bottom, 1 middle, 2 top): (phi, rho, gone); both units do the same, mirrored
H = lambda phi=0, rho=0, gone=False: (phi, rho, gone)
STEPS = [
    ("Both stacks held, base +10", [H(), H(), H()]),
    ("1. Middle shafts: 90 deg along the level groove", [H(), H(90), H()]),
    ("Middle stones spin upright (front: left, rear: right)", [H(), H(90, 90), H()]),
    ("Towers left behind, robot drives on", [H(), H(90, 0, True), H()]),
    ("2. Top shafts: turn + go down 105 in one move", [H(), H(90, 0, True), H(90)]),
    ("Top stones spin upright", [H(), H(90, 0, True), H(90, 90)]),
    ("Robot drives on", [H(), H(90, 0, True), H(90, 0, True)]),
    ("3. Bottom shafts: rise fast, then turn", [H(90), H(90, 0, True), H(90, 0, True)]),
    ("Bottom stones spin upright: 6 standing stones", [H(90, 90), H(90, 0, True), H(90, 0, True)]),
]
COLS = ["#0f766e", "#7c3aed", "#c2410c"]   # bottom, middle, top groove colours
STONE, EDGE, ROBOT, MOTC, TEAM = "#c99a5b", "#8a6332", "#8d9aa2", "#6b7a84", "#005b8c"

def draw(ax, view, state, title):
    ax.clear(); ax.set_aspect("equal"); ax.axis("off")
    xl = (-560, 560) if view == "front" else (-460, 460)
    ax.set_xlim(*xl); ax.set_ylim(-30, 460)
    ax.axhline(0, color="#18232b", lw=1.5)
    ax.axhline(350, color="#c2372b", lw=1, ls="--"); ax.text(xl[0] + 8, 356, "350 limit", color="#c2372b", fontsize=7)
    ax.add_patch(Rectangle((xl[0], 169), xl[1] - xl[0], 12, color="#2e7d4f", alpha=.15, lw=0))
    ax.set_title(title, fontsize=9, loc="left")
    # base
    if view == "front":
        ax.add_patch(Rectangle((-165, 13.5), 330, 5, color=ROBOT))
        for s in (-1, 1): ax.add_patch(Rectangle((s * WH_X - WH_W / 2, 0), WH_W, 90, color=ROBOT, alpha=.8))
        ax.add_patch(Rectangle((-MOT["x"], MOT["z"] - MOT["r"]), 2 * MOT["x"], 2 * MOT["r"], color=MOTC))
        ax.text(xl[0] + 8, -24, "<- robot's LEFT (front stones)", fontsize=7, color="#5b6b75")
        ax.text(xl[1] - 8, -24, "robot's RIGHT (rear stones) ->", fontsize=7, color="#5b6b75", ha="right")
    else:
        ax.add_patch(Rectangle((-140, 13.5), 280, 5, color=ROBOT))
        ax.add_patch(Circle((0, 45), 45, color=ROBOT, alpha=.5)); ax.add_patch(Circle((0, 45), 18.5, color=MOTC))
        ax.text(xl[0] + 8, -24, "<- back", fontsize=7, color="#5b6b75"); ax.text(xl[1] - 8, -24, "front ->", fontsize=7, color="#5b6b75", ha="right")
    lift = LIFT
    def stones(u, alpha_held, alpha_move):
        for k in range(3):
            phi, rho, gone = state[k]
            if gone: continue
            x0, x1, y0, y1, z0, z1 = stone(u, k, phi, rho)
            a0, a1 = (x0, x1) if view == "front" else (y0, y1)
            moving = phi > 0.5
            ax.add_patch(Rectangle((a0, z0), a1 - a0, z1 - z0, facecolor=STONE, edgecolor=EDGE,
                                   alpha=alpha_move if moving else alpha_held, lw=1, ls="-" if moving else "--"))
    def arms(u, alpha):
        for k in range(3):
            phi, rho, gone = state[k]
            d = direction(u, phi); c = d[0] if view == "front" else d[1]
            zc = ZH[k] + lift + groove(k, phi); zs = zc + OFF[k]
            pts = [(R, zs), (DROP, zs), (DROP, zc), (CUP, zc)]
            ax.plot([c * r for r, z in pts], [z for r, z in pts], color=COLS[k], lw=3, alpha=alpha * (.5 if gone else 1), solid_capstyle="round")
            ax.add_patch(Rectangle((c * R - 12, zs - 10), 24, 20, facecolor="white", edgecolor=COLS[k], lw=1.5, alpha=alpha))
    stones(1, .12, .35); arms(1, .7)
    # hub, bridge, grooves
    ax.add_patch(Rectangle((-R, BR["z"] + BR["t"]), 2 * R, 345 + lift - BR["z"] - BR["t"], facecolor=TEAM, alpha=.10, edgecolor=TEAM))
    for u in (0, 1):
        for k in range(3):
            xs, zs_ = [], []
            for i in range(31):
                phi = 90 * i / 30; d = direction(u, phi)
                xs.append((d[0] if view == "front" else d[1]) * R); zs_.append(ZH[k] + lift + groove(k, phi) + OFF[k])
            ax.plot(xs, zs_, color=COLS[k], lw=2 if u == 0 else 1, ls="-" if u == 0 else ":")
    if view == "front":
        ax.add_patch(Rectangle((-BR["x"], 18.5), 2 * BR["x"], BR["z"] - 18.5, fill=False, edgecolor=TEAM, ls="--", lw=1))
        ax.add_patch(Rectangle((-BR["x"], BR["z"]), 2 * BR["x"], BR["t"], color=TEAM))
    else:
        for y in (-BR["y1"], BR["y0"]): ax.add_patch(Rectangle((y, 18.5), BR["y1"] - BR["y0"], BR["z"] - 18.5, color=TEAM, alpha=.6))
        ax.add_patch(Rectangle((-BR["y1"], BR["z"]), 2 * BR["y1"], BR["t"], color=TEAM))
    stones(0, .22, .65); arms(0, 1)

def frames():
    seq, prev = [], STEPS[0][1]
    for title, target in STEPS:
        n = 1 if target == prev else 10
        for i in range(1, n + 1):
            t = ease(i / n)
            st = [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, q[2] if t >= 1 else (p[2] or q[2] and t > .5)) for p, q in zip(prev, target)]
            seq.append((title, st))
        for _ in range(6): seq.append((title, target))   # hold
        prev = target
    return seq

def main():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.4), dpi=90, gridspec_kw=dict(width_ratios=[1120, 920]))
    fig.subplots_adjust(left=0.005, right=0.995, top=0.86, bottom=0.01, wspace=0.03)
    fig.suptitle("Grooved central hub on base_330 - front + rear units (Ayoub's idea, not reviewed)", fontsize=10)
    imgs = []
    for title, st in frames():
        draw(a1, "front", st, "Front view - " + title); draw(a2, "side", st, "Side view (from the left)")
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()
        imgs.append(Image.frombuffer("RGBA", (w, h), fig.canvas.buffer_rgba()).convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=64))
    gif = os.path.join(OUT, "hub_base330.gif")
    imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=90, loop=0, optimize=True)
    imgs[-1].convert("RGB").save(os.path.join(OUT, "hub_base330_end.png"))
    print("wrote", gif, len(imgs), "frames", os.path.getsize(gif) // 1024, "kB")

if __name__ == "__main__":
    main()
