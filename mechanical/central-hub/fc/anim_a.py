# anim_a.py - animation of central hub option A working: middle stones first, then top, then bottom.
# Panels: 3D view (front-right, from above) | zoom on the INSIDE of the hub (quarter cut away: turn servos, pinions,
# ring gears) | elevation seen from behind with the 350 mm line.
# Shapes and sequence come from hub_a_fc.py (same geometry as the clash check).
# Run: "<FreeCAD>/bin/freecadcmd.exe" fc/anim_a.py   (from mechanical/central-hub/; ~10 min)
# Output: ../simulations/central_hub/hub_option_a_sequence.gif
import math, os
os.environ["HUB_A_NO_MAIN"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
G = {"__file__": os.path.join(HERE, "hub_a_fc.py"), "__name__": "hub_a"}
exec(open(G["__file__"], encoding="utf-8").read(), G)

import Part
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgba
from PIL import Image

V = G["V"]; level_parts = G["level_parts"]; NAMES = G["NAMES"]
OUT = os.path.join(G["SIM"], "hub_option_a_sequence.gif")
COL = {0: "#14958a", 1: "#8b5cf6", 2: "#e0612a"}
ACT_C, FIX_C, STONE_C, PLACED_C = "#2b3035", "#b3bcc2", "#d9ad72", "#b98d55"

# camera for the 3D views: from the front-right, above
cam = (0.55, 0.80, 0.55); n = math.sqrt(sum(c * c for c in cam)); cam = tuple(c / n for c in cam)
right = (-cam[1], cam[0], 0.0); n = math.hypot(*right[:2]); right = (right[0] / n, right[1] / n, 0.0)
up = (cam[1] * right[2] - cam[2] * right[1], cam[2] * right[0] - cam[0] * right[2], cam[0] * right[1] - cam[1] * right[0])
def P(x, y, z): return (x * right[0] + y * right[1], x * up[0] + y * up[1] + z * up[2])

def tris(shape, tol):
    v, f = shape.tessellate(tol)
    return [[v[i] for i in t] for t in f]

def project(t, view):
    if view == "back":
        return -sum(p.y for p in t) / 3, [(p.x, p.z) for p in t]
    return sum(p.x * cam[0] + p.y * cam[1] + p.z * cam[2] for p in t) / 3, [P(p.x, p.y, p.z) for p in t]

FIXED = G["fixed_parts"]()
# quarter facing the camera cut away, only near the axis (r < 66): opens the hub, rings and spacers, keeps the arms
CUT = Part.makeCylinder(66, 400, V(0, 0, -10), V(0, 0, 1), 90)        # sector 0..90 deg = x > 0, y > 0
FIX_T = tris(FIXED["hub"], 1.5) + sum([tris(c, 1.0) for c in FIXED["cradles"]], [])
FIX_CUT_T = tris(FIXED["hub"].cut(CUT), 1.0) + sum([tris(c, 1.0) for c in FIXED["cradles"]], [])
SERVO_T = sum([tris(s, 1.0) for s in FIXED["turn_servos"]], []) + tris(FIXED["fasteners"], 1.0)

def scene(st, placed):
    """Triangles with colours for the full views and for the cutaway, built once per frame."""
    full = [(t, FIX_C, 1.0) for t in FIX_T] + [(t, ACT_C, 1.0) for t in SERVO_T]
    cut = [(t, FIX_C, 1.0) for t in FIX_CUT_T] + [(t, ACT_C, 1.0) for t in SERVO_T]
    for k in range(3):
        m, a, ss = level_parts(k, st[k])
        at = tris(a, 1.0)
        full += [(t, COL[k], 1.0) for t in tris(m, 1.2)] + [(t, ACT_C, 1.0) for t in at]
        cut += [(t, COL[k], 1.0) for t in tris(m.cut(CUT), 1.0)] + [(t, ACT_C, 1.0) for t in at]
        for s in ss: full += [(t, STONE_C, 0.8) for t in tris(s, 5)]
    for s, al in placed: full += [(t, PLACED_C, al) for t in tris(s, 5)]
    return full, cut

def polys(items, view):
    out = []
    for t, c, a in items:
        d, xy = project(t, view); out.append((d, xy, c, a))
    out.sort(key=lambda it: it[0])
    return out

def draw(ax, items, view):
    ax.clear(); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    if view == "iso":
        ax.set_xlim(-400, 400); ax.set_ylim(-280, 470)
        for z, c, ls in ((0, "#18232b", "-"), (350, "#c2372b", "--")):
            q = [P(x, y, z) for x, y in [(-330, -330), (330, -330), (330, 330), (-330, 330), (-330, -330)]]
            ax.plot([a for a, b in q], [b for a, b in q], color=c, lw=0.7, ls=ls)
        ax.text(-390, 450, "3D view (front-right, from above)", fontsize=8, color="#5b6b75")
    elif view == "zoom":
        cx, cy = P(0, 0, 185)
        ax.set_xlim(cx - 120, cx + 120); ax.set_ylim(cy - 175, cy + 175)
        ax.text(cx - 117, cy + 163, "ZOOM: inside the hub (front-right quarter cut away)", fontsize=8, color="#18232b", weight="bold")
        ax.set_facecolor("#eef1f3")
    else:
        ax.set_xlim(-360, 360); ax.set_ylim(-25, 380)
        ax.axhline(0, color="#18232b", lw=1.2); ax.axhline(350, color="#c2372b", lw=0.8, ls="--")
        ax.text(-355, 356, "350 mm limit", fontsize=8, color="#c2372b")
        ax.text(-355, -20, "seen from behind: robot's LEFT (front stones)", fontsize=8, color="#5b6b75")
        ax.text(355, -20, "robot's RIGHT (rear stones)", fontsize=8, color="#5b6b75", ha="right")
    ax.add_collection(PolyCollection([it[1] for it in items], facecolors=[to_rgba(it[2], it[3]) for it in items],
                                     edgecolors=[to_rgba("#18232b", 0.18 * it[3]) for it in items],
                                     linewidths=0.35 if view == "zoom" else 0.25))

def zoom_labels(ax):
    def lab(xyz, txt, dx, dy):
        x, y = P(*xyz)
        ax.annotate(txt, (x, y), (x + dx, y + dy), fontsize=7, color="#18232b",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85),
                    arrowprops=dict(arrowstyle="-", color="#18232b", lw=0.6))
    c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
    z = G["RING_Z"]
    lab((5 * c, 5 * s, 118), "turn servo MG996R\n(bottom ring, upside down)", -118, -55)
    lab((5 * c, 5 * s, 168), "turn servo (middle ring)", -118, 25)
    lab((5 * c, 5 * s, 220), "turn servo (top ring)", -118, 45)
    lab((26 * c, 26 * s, z[2] + 4), "pinion through a window\nin the hub wall:\nservo 180 deg -> ring 90 deg", 35, 40)
    lab((54 * c, 54 * s, z[0] - 4), "internal gear\nin the ring bore", 35, -40)
    lab((0, 0, 330), "bore: wires + vacuum hoses", 20, 25)

def frames():
    """(caption, state, placed[(shape, alpha)]): holds on each step, placed towers drop onto the table, fade when the
    robot drives on."""
    seq = G["sequence"]()
    out, placed, prev = [], [], seq[0][1]
    for i, (label, st) in enumerate(seq):
        for k in range(3):
            if prev[k]["stone"] and not st[k]["stone"]:
                ss = level_parts(k, prev[k])[2]
                for j in range(1, 4):
                    out.append((label, st, placed + [(_drop(s, s.BoundBox.ZMin * j / 3), 1.0) for s in ss]))
                placed = placed + [(_drop(s, s.BoundBox.ZMin), 1.0) for s in ss]
        out.append((label, st, list(placed)))
        last_of_level = (i + 1 == len(seq)) or (seq[i + 1][0][:1].isdigit() and seq[i + 1][0] != label)
        if i + 1 == len(seq) or seq[i + 1][0] != label:
            out += [(label, st, list(placed))] * 4
        if last_of_level and placed:
            for a in (0.6, 0.3):
                out.append(("Robot drives on (towers stay)", st, [(s, a) for s, _ in placed]))
            placed = []
        prev = st
    out += [("Back home: 6 towers built, all arms ready again", seq[-1][1], [])] * 8
    return out

def _drop(s, dz):
    c = s.copy(); c.translate(V(0, 0, -dz)); return c

def main():
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(17, 6.2), dpi=80, gridspec_kw=dict(width_ratios=[1, 0.66, 1.05]))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.87, bottom=0.02, wspace=0.03)
    imgs, cache = [], {}
    for cap, st, placed in frames():
        key = (cap, repr([(round(s["phi"], 2), round(s["cz"], 2), round(s["rho"], 2), s["stone"]) for s in st]),
               tuple((round(s.BoundBox.ZMin, 1), round(s.BoundBox.XMin, 1), a) for s, a in placed))
        if key not in cache:
            full, cut = scene(st, placed)
            draw(a1, polys(full, "iso"), "iso"); draw(a2, polys(cut, "iso"), "zoom"); zoom_labels(a2)
            draw(a3, polys(full, "back"), "back")
            for t in list(fig.texts): t.remove()
            fig.text(0.01, 0.955, "Central hub - option A (Ayoub's idea, not reviewed): middle -> top -> bottom", fontsize=12, color="#5b6b75")
            fig.text(0.01, 0.895, cap, fontsize=11, weight="bold", color="#18232b")
            fig.text(0.99, 0.895, "green bottom / purple middle / orange top level - black = actuators (servos, N20 + screws) - grey = hub",
                     fontsize=8, color="#5b6b75", ha="right")
            fig.canvas.draw(); w, h = fig.canvas.get_width_height()
            cache[key] = Image.frombuffer("RGBA", (w, h), fig.canvas.buffer_rgba()).convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=128)
        imgs.append(cache[key])
    imgs[0].save(OUT, save_all=True, append_images=imgs[1:], duration=100, loop=0, optimize=True)
    print("wrote %s: %d frames, %d kB" % (OUT, len(imgs), os.path.getsize(OUT) // 1024))

main()
