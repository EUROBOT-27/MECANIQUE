# sheet_a.py - one PNG sheet of the option A poses (top view + front view each), drawn from the CAD_FC/HUB_A_*.FCStd shapes.
# Run: "<FreeCAD>/bin/freecadcmd.exe" fc/sheet_a.py   (from mechanical/central-hub/, after hub_a_fc.py)
# Output: ../simulations/central_hub/option_a_sheet.png
import os
import FreeCAD as App
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAD = os.path.join(ROOT, "CAD_FC")
OUT = os.path.join(ROOT, "..", "simulations", "central_hub", "option_a_sheet.png")
POSES = [("HUB_A_HOME", "Home: both stacks held"), ("HUB_A_1_MIDDLE", "1. Middle ring turned + spun"),
         ("HUB_A_2_TOP", "2. Top ring turned, carriage down, spun"), ("HUB_A_3_BOTTOM", "3. Bottom ring turned, carriage up, spun")]
COL = {"bottom": "#0f766e", "middle": "#7c3aed", "top": "#c2410c"}

def style(name):
    if name.startswith("Stone"): return "#c99a5b", "#8a6332", 0.55
    if name.startswith("Level"): return COL[name.split("_")[1]], "#18232b", 1.0
    return "#9aa5ad", "#5b6b75", 1.0

def draw(ax, doc, view):
    polys, cols, eds, depth = [], [], [], []
    for o in doc.Objects:
        if not hasattr(o, "Shape") or o.Shape.isNull(): continue
        fc, ec, a = style(o.Name)
        v, f = o.Shape.tessellate(1.5)
        for t in f:
            p = [v[i] for i in t]
            if view == "top": xy = [(q.x, q.y) for q in p]; d = sum(q.z for q in p) / 3
            else: xy = [(q.x, q.z) for q in p]; d = -sum(q.y for q in p) / 3   # seen from behind (-Y)
            polys.append(xy); depth.append(d)
            c = matplotlib.colors.to_rgba(fc, a); cols.append(c); eds.append(matplotlib.colors.to_rgba(ec, 0.15))
    order = sorted(range(len(polys)), key=lambda i: depth[i])
    ax.add_collection(PolyCollection([polys[i] for i in order], facecolors=[cols[i] for i in order],
                                     edgecolors=[eds[i] for i in order], linewidths=0.2))
    ax.set_aspect("equal"); ax.set_xlim(-340, 340)
    if view == "top":
        ax.set_ylim(-340, 340); ax.text(-330, 315, "top view (front = up)", fontsize=7, color="#5b6b75")
    else:
        ax.set_ylim(-20, 370); ax.axhline(0, color="#18232b", lw=1); ax.axhline(350, color="#c2372b", lw=0.8, ls="--")
        ax.text(-330, 355, "350", fontsize=7, color="#c2372b"); ax.text(-330, -15, "seen from behind (robot's left = left)", fontsize=7, color="#5b6b75")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#d0d6da")

fig, axs = plt.subplots(2, 4, figsize=(17, 8.6), dpi=100, gridspec_kw=dict(height_ratios=[680, 390]))
fig.suptitle("Central hub - option A (Ayoub's idea, not reviewed): rings + slides, every move reversible.  "
             "Green = bottom level, purple = middle, orange = top; rear unit = front turned 180", fontsize=11)
for c, (name, title) in enumerate(POSES):
    doc = App.openDocument(os.path.join(CAD, name + ".FCStd"))
    draw(axs[0][c], doc, "top"); draw(axs[1][c], doc, "front")
    axs[0][c].set_title(title, fontsize=10, loc="left")
    App.closeDocument(doc.Name)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT); print("wrote", OUT)
