# perimeter_plot.py - draws the top views from perimeter-study/topview_data.json (made by perimeter_study_fc.py).
# Run with FreeCAD's Python (it has matplotlib):  "C:/Program Files/FreeCAD 1.1/bin/python.exe" fc/perimeter_plot.py
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.normpath(os.path.join(HERE, "..", "perimeter-study"))
D = json.load(open(os.path.join(OUTD, "topview_data.json")))

GROUP_COL = {"fixed": "#8a8f98", "carriage": "#4a78c2", "head": "#d98c1f", "hpinion": "#d98c1f",
             "door": "#3a9a52", "pinion": "#3a9a52"}
BLOCK_COL = {"WHEEL": "#222222", "DRIVE_MOTOR": "#555555", "CASTER": "#777777", "SHOOTER": "#c94a4a",
             "GRAIL": "#8e5fc2", "CORE": "#c9b24a", "ROOF": "#bbbbbb", "BEACON": "#333399", "ESTOP": "#e02020",
             "LIDAR": "#333399", "FLOOR": "#e9e4d8"}


def gcol(g):
    for k, c in GROUP_COL.items():
        if g.startswith(k):
            return c
    return "#999999"


def bcol(n):
    for k, c in BLOCK_COL.items():
        if n.startswith(k):
            return c
    return "#aaaaaa"


def rect_perim(w, h):
    return 2 * (w + h)


def draw(ax, sc, title, lim=1400.0, show_stack=False):
    # floor and body outline
    for n, b in sorted(D["blocks"].items(), key=lambda kv: kv[1]["zmax"]):
        if len(b["hull"]) < 3:
            continue
        a = 0.9 if n == "FLOOR" else 0.35
        ax.add_patch(Polygon(b["hull"], closed=True, fc=bcol(n), ec="none", alpha=a, zorder=1 if n == "FLOOR" else 2))
    body = D["body"]
    ax.add_patch(Polygon(body, closed=True, fill=False, ec="black", lw=1.2, ls="--", zorder=6))
    for p in sorted(sc["parts"], key=lambda p: p["zmax"]):
        if len(p["hull"]) < 3:
            continue
        ax.add_patch(Polygon(p["hull"], closed=True, fc=gcol(p["group"]), ec="#00000055", lw=0.3, alpha=0.75, zorder=3))
    if show_stack:
        ax.add_patch(Polygon(D["stack_front"], closed=True, fc="#c8a46a", ec="#8a6a3a", alpha=0.35, zorder=2.5))
    hl = sc["hull"]
    per = sc["perimeter"]
    ok = per <= lim
    ax.add_patch(Polygon(hl, closed=True, fill=False, ec="#118833" if ok else "#d01010", lw=2.0, zorder=7))
    xs = [p[0] for p in hl]; ys = [p[1] for p in hl]
    ax.set_title("%s\nhull perimeter %.1f mm  (limit %d: %s %.1f)" % (
        title, per, lim, "margin" if ok else "OVER by", abs(lim - per)), fontsize=9.5,
        color="#118833" if ok else "#d01010")
    ax.text(0.02, 0.02, "hull X %.0f..%.0f (%.0f)\nhull Y %.0f..%.0f (%.0f)" % (
        min(xs), max(xs), max(xs) - min(xs), min(ys), max(ys), max(ys) - min(ys)),
        transform=ax.transAxes, fontsize=7.5, va="bottom", family="monospace")
    ax.set_aspect("equal")
    ax.set_xlim(-260, 260); ax.set_ylim(-280, 280)
    ax.axhline(0, color="#00000022", lw=0.6); ax.axvline(0, color="#00000022", lw=0.6)
    ax.text(0, 268, "FRONT module", ha="center", fontsize=7.5, color="#444")
    ax.text(0, -275, "BACK module (mirror)", ha="center", fontsize=7.5, color="#444")
    ax.tick_params(labelsize=7)
    ax.grid(color="#00000010")


def legend(fig):
    from matplotlib.patches import Patch
    h = [Patch(fc=GROUP_COL["door"], label="door units (swing about Z)"),
         Patch(fc=GROUP_COL["carriage"], label="lift carriage"),
         Patch(fc=GROUP_COL["head"], label="suction head"),
         Patch(fc=GROUP_COL["fixed"], label="module frame (socle, rails)"),
         Patch(fc=BLOCK_COL["FLOOR"], label="floor"),
         Patch(fc="none", ec="black", ls="--", label="body outline (chamfer %g)" % D["chamfer"]),
         Patch(fc="none", ec="#d01010", lw=2, label="convex hull (red > limit, green ok)")]
    fig.legend(handles=h, loc="lower center", ncol=4, fontsize=8, frameon=False)


S = D["scenes"]
# 1. the main sheet: start, one open, both open (approach), both fully open
fig, axs = plt.subplots(2, 2, figsize=(12, 13))
draw(axs[0][0], S["start"], S["start"]["title"], lim=1200)
draw(axs[0][1], S["one_open"], S["one_open"]["title"])
draw(axs[1][0], S["both_approach"], S["both_approach"]["title"])
draw(axs[1][1], S["both_release"], S["both_release"]["title"])
fig.suptitle("Layout v1, A+B front / mirror back, top view (X right, Y forward, mm) [GR F.3]", fontsize=12)
legend(fig)
fig.tight_layout(rect=(0, 0.04, 1, 0.97))
fig.savefig(os.path.join(OUTD, "topview_sheet.png"), dpi=130)

# 2. one big picture per "both open" scene
for key in ("both_approach", "both_release", "both_lift_turn", "ab_front_b_back"):
    fig, ax = plt.subplots(figsize=(8, 8.6))
    draw(ax, S[key], S[key]["title"])
    legend(fig)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(OUTD, "topview_%s.png" % key), dpi=140)

# 3. door angle map: perimeter vs front / back door angle
N = D["numbers"]
ang = N["door_angles"]
asc = sorted(ang)
import numpy as np
M = np.array([[N["grid"]["%d|%d" % (fa, ba)] for fa in asc] for ba in asc])
fig, ax = plt.subplots(figsize=(8, 6.6))
im = ax.imshow(M, origin="lower", extent=(asc[0], asc[-1], asc[0], asc[-1]), cmap="RdYlGn_r", vmin=1100, vmax=1550, aspect="auto")
cs = ax.contour(asc, asc, M, levels=[1300, 1350, 1400], colors=["#555", "#555", "black"], linewidths=[0.8, 0.8, 2.2])
ax.clabel(cs, fmt="%d", fontsize=8)
fig.colorbar(im, label="hull perimeter (mm)")
for a, lab in ((90, "folded"), (3, "clamp"), (-30, "approach"), (-38, "release")):
    ax.axvline(a, color="#00000030", lw=0.7); ax.axhline(a, color="#00000030", lw=0.7)
    ax.text(a, asc[0] - 4, lab, rotation=90, fontsize=7, ha="center", va="top")
ax.set_xlabel("front door angle (deg; +90 folded, +3 clamp, -30 approach, -38 release)", labelpad=34)
ax.set_ylabel("back door angle (deg)")
ax.set_title("Perimeter vs door angles (lift 0, head 0). Black line = 1400 limit", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUTD, "door_angle_map.png"), dpi=130)
print("done ->", OUTD)
