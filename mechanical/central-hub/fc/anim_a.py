# anim_a.py - animation of central hub option A on the robot (base_330): middle stones first, then top, then bottom,
# front unit (stones -> robot's left) and rear unit (stones -> robot's right) together.
# Panels: robot seen from the FRONT-LEFT (front unit) | robot seen from the REAR-RIGHT (rear unit) |
#         INSIDE of the hub (quarter cut away: turn servos, pinions, ring gears, slide motors near the hub) |
#         actuator strip: every actuator lights up (magenta) while it works; vacuum (blue) while a stone is held.
# Shapes and sequence come from hub_a_fc.py (same geometry as the clash check). Robot = base_330 plate (STEP) +
# drive wheel / motor placeholders + the bridge over the motors (same numbers as check_env_a.py).
# Between two levels the robot drives on 340 mm (Gazebo, 2026-11-15: >= 0.34 m or the next level knocks the towers).
# Run: "<FreeCAD>/bin/freecadcmd.exe" fc/anim_a.py   (from mechanical/central-hub/; ~1 h, ~20 s a frame;
#      an interrupted run resumes from _frames_tmp/ if anim_a.py and hub_a_fc.py are unchanged)
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
from matplotlib.patches import Circle, FancyBboxPatch
from PIL import Image

V = G["V"]; NAMES = G["NAMES"]; arm = G["arm"]; ring_shape = G["ring_shape"]; pinion = G["pinion"]
polar = G["polar"]; rz = G["rz"]
OUT = os.path.join(G["SIM"], "hub_option_a_sequence.gif")
BASE_STEP = os.path.normpath(os.path.join(G["ROOT"], "..", "base_330", "base_330.step"))
COL = {0: "#14958a", 1: "#8b5cf6", 2: "#e0612a"}
ACT_C, ON_C, VAC_C = "#2b3035", "#e6007e", "#1f6feb"
FIX_C, FAS_C, STONE_C, PLACED_C = "#b3bcc2", "#6b757c", "#d9ad72", "#b98d55"
PLATE_C, WHEEL_C, MOTOR_C, BRIDGE_C = "#d5dbe1", "#1d2125", "#7d8790", "#9fb1c4"
BASE_COLS = {PLATE_C, WHEEL_C, MOTOR_C, BRIDGE_C}
DRIVE = 340.0                                      # robot drives on between two levels (mm)

# ---------------- cameras ----------------
def basis(c):
    n = math.sqrt(sum(x * x for x in c)); c = tuple(x / n for x in c)
    r = (-c[1], c[0], 0.0); n = math.hypot(r[0], r[1]); r = (r[0] / n, r[1] / n, 0.0)
    u = (c[1] * r[2] - c[2] * r[1], c[2] * r[0] - c[0] * r[2], c[0] * r[1] - c[1] * r[0])
    return c, r, u
CAMS = {"front": basis((-0.62, 0.80, 0.52)),       # front-left, from above: the front unit (stones -> left)
        "rear": basis((0.62, -0.80, 0.52)),        # rear-right, from above: the rear unit (stones -> right)
        "inside": basis((0.55, 0.80, 0.55))}       # the cut-away quarter (x > 0, y > 0) faces this camera
def P(view, x, y, z):
    c, r, u = CAMS[view]
    return (x * r[0] + y * r[1], x * u[0] + y * u[1] + z * u[2])

MAXE = 10.0                                         # split triangles longer than this (mm): the painter's sort uses
def _split(t, maxe, out):                           # triangle centres, so long thin rail faces were drawn in the wrong
    a, b, c = t                                     # order and parts looked as if they went through each other
    e = [(a - b).Length, (b - c).Length, (c - a).Length]
    m = max(e)
    if m <= maxe: out.append(t); return
    i = e.index(m)
    if i == 0: mid = (a + b) * 0.5; _split([a, mid, c], maxe, out); _split([mid, b, c], maxe, out)
    elif i == 1: mid = (b + c) * 0.5; _split([a, b, mid], maxe, out); _split([a, mid, c], maxe, out)
    else: mid = (c + a) * 0.5; _split([a, b, mid], maxe, out); _split([mid, b, c], maxe, out)

def tris(shape, tol, maxe=None):
    v, f = shape.tessellate(tol)
    out = []
    for t in f: _split([v[i] for i in t], maxe or MAXE, out)
    return out

# ---------------- fixed geometry ----------------
FIXED = G["fixed_parts"]()
CUT = Part.makeCylinder(66, 400, V(0, 0, -10), V(0, 0, 1), 90)        # sector 0..90 deg = x > 0, y > 0, near the axis
FIX_MAXE, BASE_MAXE = 30.0, 60.0                   # fixed parts: coarser split (10 mm everywhere = 2.5 M triangles a frame)
HUB_T = tris(FIXED["hub"], 1.5, FIX_MAXE) + sum([tris(c, 1.0, FIX_MAXE) for c in FIXED["cradles"]], [])
HUB_CUT_T = tris(FIXED["hub"].cut(CUT), 1.0, FIX_MAXE) + sum([tris(c, 1.0, FIX_MAXE) for c in FIXED["cradles"]], [])
TURN_T = [tris(s, 1.5, 15.0) for s in FIXED["turn_servos"]]
FFAS_T = tris(FIXED["fasteners"], 2.0, FIX_MAXE)

def robot_base():
    out = []
    try:
        plate = Part.read(BASE_STEP); plate.translate(V(0, 0, 13.5))
    except Exception:
        plate = Part.makeBox(330, 280, 5, V(-165, -140, 13.5))
    out += [(t, PLATE_C) for t in tris(plate, 2.0, BASE_MAXE)]
    for x0 in (-103.8, 83.8):                                            # wheel placeholders Ø90 x 20 (to be shrunk)
        out += [(t, WHEEL_C) for t in tris(Part.makeCylinder(45, 20, V(x0, 0, 45), V(1, 0, 0)), 2.0, BASE_MAXE)]
    out += [(t, MOTOR_C) for t in tris(Part.makeCylinder(18.5, 123, V(-61.5, 0, 45), V(1, 0, 0)), 2.0, BASE_MAXE)]
    br = Part.makeBox(140, 110, 5, V(-70, -55, 68)).fuse([Part.makeBox(140, 5, 49.5, V(-70, s, 18.5)) for s in (50, -55)])
    out += [(t, BRIDGE_C) for t in tris(br, 2.0, BASE_MAXE)]
    return out
BASE_T = robot_base()

# ---------------- moving geometry, split by actuator ----------------
def level_split(k, st):
    """Ring k + both arms, split: structure, turn pinion, slide drive (N20, screw, coupler, bearing, switch),
    spin servos, fasteners, stones."""
    struct, slide, spin, fas, stones = [ring_shape(k, st["phi"])], [], [], [], []
    for u in (0, 1):
        m, a_, f_, s = arm(k, st["cz"], st["rho"], st["stone"])
        a = polar(u, st["phi"])
        struct.append(rz(m, a)); fas += [rz(x, a) for x in f_]
        spin += [rz(x, a) for x in a_[-2:]]                 # spin servo + its ears (last 2 in arm())
        slide += [rz(x, a) for x in a_[:-2]]
        if s: stones.append(rz(s, a))
    return dict(struct=struct[0].fuse(struct[1:]), turn=pinion(k, st["phi"]), slide=Part.makeCompound(slide) if slide else None,
                spin=Part.makeCompound(spin), fas=Part.makeCompound(fas), stones=stones)

def scene(st, act, placed):
    """Coloured triangles for the robot views and for the cut-away, built once per frame."""
    c_act = lambda key: ON_C if key in act else ACT_C
    full = [(t, c, 1.0) for t, c in BASE_T] + [(t, FIX_C, 1.0) for t in HUB_T] + [(t, FAS_C, 1.0) for t in FFAS_T]
    cut = [(t, FIX_C, 1.0) for t in HUB_CUT_T] + [(t, FAS_C, 1.0) for t in FFAS_T]
    for k in range(3):
        ts = [(t, c_act(("turn", k)), 1.0) for t in TURN_T[k]]
        full += ts; cut += ts
        L = level_split(k, st[k])
        full += [(t, COL[k], 1.0) for t in tris(L["struct"], 1.2)]
        cut += [(t, COL[k], 1.0) for t in tris(L["struct"].cut(CUT), 1.0)]
        for key, shp in ((("turn", k), L["turn"]), (("slide", k), L["slide"]), (("spin", k), L["spin"])):
            if shp is None: continue
            tt = [(t, c_act(key), 1.0) for t in tris(shp, 1.5, 15.0)]
            full += tt; cut += tt
        ft = [(t, FAS_C, 1.0) for t in tris(L["fas"], 2.0, 20.0)]
        full += ft; cut += ft
        for s in L["stones"]: full += [(t, STONE_C, 0.72) for t in tris(s, 5, 40.0)]
    for s, al in placed: full += [(t, PLACED_C, al) for t in tris(s, 5, 40.0)]
    return full, cut

def polys(items, view):
    c = CAMS[view][0]; out = []
    for t, col, a in items:
        d = sum(p.x * c[0] + p.y * c[1] + p.z * c[2] for p in t) / 3
        out.append((d, [P(view, p.x, p.y, p.z) for p in t], col, a))
    out.sort(key=lambda it: it[0])
    return out

def lims(view, xs, ys, zs, pad=15):
    pts = [P(view, x, y, z) for x in xs for y in ys for z in zs]
    return (min(p[0] for p in pts) - pad, max(p[0] for p in pts) + pad), (min(p[1] for p in pts) - pad, max(p[1] for p in pts) + pad)
LIM = {v: lims(v, (-370, 370), (-340, 330), (0, 345), 4) for v in ("front", "rear")}

def draw(ax, items, view):
    ax.clear(); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    if view in ("front", "rear"):
        (x0, x1), (y0, y1) = LIM[view]; ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
        for g in range(-500, 501, 100):                                  # table grid, 100 mm
            for a, b in (((g, -500, 0), (g, 500, 0)), ((-500, g, 0), (500, g, 0))):
                p, q = P(view, *a), P(view, *b)
                ax.plot([p[0], q[0]], [p[1], q[1]], color="#dfe4e8", lw=0.6, zorder=0)
        p, q = P(view, 0, 200, 0), P(view, 0, 330, 0)                     # arrow: robot's forward direction
        ax.annotate("", q, p, arrowprops=dict(arrowstyle="-|>", color="#18232b", lw=1.2), zorder=0)
        ax.text(*P(view, 0, 345, 0), "forward", fontsize=7, color="#18232b", ha="center", zorder=0)
        for side, x in (("LEFT", -390), ("RIGHT", 390)):
            ax.text(*P(view, x, 0, 0), "robot's\n" + side, fontsize=7, color="#5b6b75", ha="center", va="center", zorder=0)
        title = ("FRONT-LEFT view: front arms (stones -> robot's left)" if view == "front"
                 else "REAR-RIGHT view: rear arms (stones -> robot's right)")
        ax.set_title(title, fontsize=9, color="#18232b", loc="left", pad=3)
    else:
        cx, cy = P(view, 0, 0, 185)
        ax.set_xlim(cx - 125, cx + 125); ax.set_ylim(cy - 180, cy + 180)
        ax.set_facecolor("#eef1f3")
        ax.set_title("INSIDE the hub (front-right quarter cut away)", fontsize=9, color="#18232b", loc="left", pad=3)
    ax.add_collection(PolyCollection([it[1] for it in items], facecolors=[to_rgba(it[2], it[3]) for it in items],
                                     edgecolors=[to_rgba("#18232b", (0.03 if it[2] in BASE_COLS else 0.16) * it[3]) for it in items],
                                     linewidths=0.35 if view == "inside" else 0.2))

def inside_labels(ax, act):
    def lab(xyz, txt, dx, dy, on):
        x, y = P("inside", *xyz)
        ax.annotate(txt, (x, y), (x + dx, y + dy), fontsize=6.6, color="white" if on else "#18232b",
                    weight="bold" if on else "normal",
                    bbox=dict(boxstyle="round,pad=0.2", fc=ON_C if on else "white", ec="none", alpha=0.92),
                    arrowprops=dict(arrowstyle="-", color=ON_C if on else "#18232b", lw=0.8 if on else 0.5))
    c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
    z = G["RING_Z"]
    lab((5 * c, 5 * s, 220), "TURN-T  MG996R\n(top ring)", -122, 48, ("turn", 2) in act)
    lab((5 * c, 5 * s, 168), "TURN-M  MG996R\n(middle ring)", -122, 18, ("turn", 1) in act)
    lab((5 * c, 5 * s, 118), "TURN-B  MG996R\n(bottom ring, upside down)", -122, -62, ("turn", 0) in act)
    lab((26 * c, 26 * s, z[2] + 4), "pinion -> internal gear\nservo 180 deg = ring 90 deg", 38, 48, any(a[0] == "turn" for a in act))
    lab((0, 0, 330), "bore: wires + vacuum hoses", 22, 22, False)

# ---------------- actuator strip ----------------
LAMPS = [("TURN", "MG996R\nring turn", lambda k: ("turn", k), (0, 1, 2)),
         ("SLIDE", "N20 + M4 screw\nfront + rear", lambda k: ("slide", k), (0, 2)),
         ("SPIN", "2 x MG90S\nfront + rear", lambda k: ("spin", k), (0, 1, 2)),
         ("VACUUM", "2 x pump\nfront + rear", lambda k: ("vac", k), (0, 1, 2)),
         ("VENT", "2 x valve\nfront + rear", lambda k: ("vent", k), (0, 1, 2))]

def draw_strip(ax, act, phase):
    ax.clear(); ax.set_xlim(0, 100); ax.set_ylim(0, 22); ax.axis("off")
    for g, (name, sub, key, levels) in enumerate(LAMPS):
        x0 = 1 + g * 13.2
        ax.add_patch(FancyBboxPatch((x0, 1.5), 12.4, 19, boxstyle="round,pad=0.2,rounding_size=1", fc="#f5f7f8", ec="#d0d6db", lw=0.8))
        ax.text(x0 + 0.6, 18.4, name, fontsize=8.5, weight="bold", color="#18232b", va="center")
        ax.text(x0 + 0.6, 14.6, sub, fontsize=6.3, color="#5b6b75", va="center", linespacing=1.05)
        for i, k in enumerate((2, 1, 0)):
            y = 10.2 - i * 3.6
            if k not in levels:
                ax.text(x0 + 1.4, y, "-", fontsize=7, color="#b3bcc2", va="center"); continue
            on = key(k) in act
            col = (VAC_C if name == "VACUUM" else ON_C) if on else "#c9cfd4"
            ax.add_patch(Circle((x0 + 1.4, y), 1.05, fc=col, ec="none"))
            ax.text(x0 + 3.0, y, NAMES[k], fontsize=7, color=COL[k], weight="bold" if on else "normal", va="center")
    # sequence progress: middle -> top -> bottom
    x0 = 68
    ax.add_patch(FancyBboxPatch((x0, 1.5), 31, 19, boxstyle="round,pad=0.2,rounding_size=1", fc="#f5f7f8", ec="#d0d6db", lw=0.8))
    ax.text(x0 + 0.6, 18.4, "SEQUENCE", fontsize=8.5, weight="bold", color="#18232b", va="center")
    steps = [("unpinch", None), ("1 middle", 1), ("drive", None), ("2 top", 2), ("drive", None), ("3 bottom", 0), ("home", None)]
    w = 30.0 / len(steps)
    for i, (txt, k) in enumerate(steps):
        done, cur = i < phase, i == phase
        fc = (COL[k] if k is not None else "#5b6b75") if (done or cur) else "#e3e7ea"
        ax.add_patch(FancyBboxPatch((x0 + 0.5 + i * w, 8.5), w - 0.6, 5.5, boxstyle="round,pad=0.1,rounding_size=0.6",
                                    fc=fc, ec=ON_C if cur else "none", lw=1.6, alpha=1.0 if cur else (0.55 if done else 1.0)))
        ax.text(x0 + 0.5 + i * w + (w - 0.6) / 2, 11.25, txt, fontsize=6.3, ha="center", va="center",
                color="white" if (done or cur) else "#5b6b75", weight="bold" if cur else "normal")
    ax.text(x0 + 0.6, 4.6, "magenta = actuator working now   blue = vacuum holding\n"
            "robot drives on 340 mm between levels (towers stay)", fontsize=6.3, color="#5b6b75", va="center")

# ---------------- frames ----------------
def _drop(s, dz, dy=0.0):
    c = s.copy(); c.translate(V(0, dy, -dz)); return c

def active(prev, st):
    a = set()
    for k in range(3):
        for key, name in (("phi", "turn"), ("cz", "slide"), ("rho", "spin")):
            if abs(prev[k][key] - st[k][key]) > 1e-6: a.add((name, k))
        if st[k]["stone"]: a.add(("vac", k))
    return a

def phase_of(label, ph):
    if label.startswith("Unpinch") or label.startswith("Both"): return 0
    if label.startswith("1.") or label.startswith("Middle") or (label.startswith("Placed: 2 towers")): return 1
    if label.startswith("2.") or label.startswith("Top") or label.startswith("Placed: 2 more"): return 3
    if label.startswith("3.") or label.startswith("Bottom") or label.startswith("Placed: 6"): return 5
    return ph

def frames():
    """(caption, state, active set, placed[(shape, alpha)], phase)."""
    seq = G["sequence"]()
    out, placed, old, prev, ph = [], [], [], seq[0][1], 0
    for i, (label, st) in enumerate(seq):
        ph = phase_of(label, ph)
        act = active(prev, st)
        for k in range(3):
            if prev[k]["stone"] and not st[k]["stone"]:
                ss = level_split(k, prev[k])["stones"]
                for j in range(1, 4):
                    out.append((label + "  (pumps off, valves open)", st, act | {("vent", k)},
                                old + placed + [(_drop(s, s.BoundBox.ZMin * j / 3), 1.0) for s in ss], ph))
                placed = placed + [(_drop(s, s.BoundBox.ZMin), 1.0) for s in ss]
        out.append((label, st, act, old + placed, ph))
        nxt = seq[i + 1][0] if i + 1 < len(seq) else None
        if nxt != label:
            out += [(label, st, active(st, st), old + placed, ph)] * 3       # hold: only the vacuum stays on
        last_of_level = nxt is None or (nxt[:1].isdigit() and nxt != label)
        if last_of_level and placed:
            n = 6
            for j in range(1, n + 1):                                         # robot drives on: towers slide back
                dy = -DRIVE * j / n
                sh = [(_drop(s, 0, dy), 1.0 - 0.6 * j / n) for s, _ in placed]
                out.append(("Robot drives on %.0f mm (towers stay on the table)" % (DRIVE * j / n), st, active(st, st), sh,
                            ph + 1 if ph < 5 else 6))
            old = [(s, 0.4) for s, _ in sh]; placed = []
            if ph < 5: ph += 1
        prev = st
    ph = 6
    out += [("Back home: 6 towers built (2 per stop), all arms ready again", seq[-1][1], set(), old, 6)] * 8
    return out

def main():
    fig = plt.figure(figsize=(17, 8.4), dpi=80)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.66], height_ratios=[1, 0.27], left=0.008, right=0.992,
                          top=0.885, bottom=0.01, wspace=0.03, hspace=0.06)
    a_front, a_rear, a_in, a_strip = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[:, 2]), fig.add_subplot(gs[1, :2])
    imgs, cache = [], {}
    TMPD = os.path.join(G["SIM"], "_frames_tmp"); os.makedirs(TMPD, exist_ok=True)
    # resume: frames left by an interrupted run are kept if both scripts are unchanged (hash in _frames_tmp/stamp)
    import hashlib
    stamp = hashlib.sha1(b"".join(open(f, "rb").read() for f in (os.path.join(HERE, "anim_a.py"), G["__file__"]))).hexdigest()
    sp = os.path.join(TMPD, "stamp")
    old = open(sp).read().strip() if os.path.exists(sp) else None
    if old != stamp:
        for f in os.listdir(TMPD): os.remove(os.path.join(TMPD, f))
    open(sp, "w").write(stamp)
    fr = frames()
    print("frames:", len(fr))
    for n, (cap, st, act, placed, ph) in enumerate(fr):
        key = (cap, repr([(round(s["phi"], 2), round(s["cz"], 2), round(s["rho"], 2), s["stone"]) for s in st]),
               tuple(sorted(act)), ph,
               tuple((round(s.BoundBox.ZMin, 1), round(s.BoundBox.XMin, 1), round(s.BoundBox.YMin, 1), a) for s, a in placed))
        if key not in cache and os.path.exists(os.path.join(TMPD, "f%04d.png" % len(cache))):
            cache[key] = os.path.join(TMPD, "f%04d.png" % len(cache))     # kept from an interrupted run
        if key not in cache:
            full, cut = scene(st, act, placed)
            draw(a_front, polys(full, "front"), "front"); draw(a_rear, polys(full, "rear"), "rear")
            draw(a_in, polys(cut, "inside"), "inside"); inside_labels(a_in, act)
            draw_strip(a_strip, act, ph)
            for t in list(fig.texts): t.remove()
            fig.text(0.008, 0.958, "Central hub - option A on base_330 (Ayoub's idea, not reviewed): middle -> top -> bottom, "
                     "front + rear unit together", fontsize=12, color="#5b6b75")
            fig.text(0.008, 0.905, cap, fontsize=12, weight="bold", color="#18232b")
            fig.text(0.992, 0.905, "green bottom / purple middle / orange top level - dark = actuators idle - magenta = working"
                     " - grey = hub - pale blue = base_330 + bridge (wheels: placeholder Ø90)", fontsize=7.5, color="#5b6b75", ha="right")
            fig.canvas.draw(); w, h = fig.canvas.get_width_height()
            fp = os.path.join(TMPD, "f%04d.png" % len(cache))                 # frames go to disk: low memory
            Image.frombuffer("RGBA", (w, h), fig.canvas.buffer_rgba()).convert("RGB").save(fp)
            cache[key] = fp
            if n % 20 == 0: print("frame", n, "/", len(fr), flush=True)
        imgs.append(cache[key])
    plt.close(fig)
    def gen():
        for fp in imgs[1:]: yield Image.open(fp).convert("P", palette=Image.ADAPTIVE, colors=160)
    first = Image.open(imgs[0]).convert("P", palette=Image.ADAPTIVE, colors=160)
    first.save(OUT, save_all=True, append_images=gen(), duration=110, loop=0, optimize=True)
    for f in os.listdir(TMPD): os.remove(os.path.join(TMPD, f))
    os.rmdir(TMPD)
    print("wrote %s: %d frames, %d kB" % (OUT, len(imgs), os.path.getsize(OUT) // 1024))

if os.environ.get("HUB_ANIM_TEST"):
    # quick check: render 3 frames to PNG
    fig = plt.figure(figsize=(17, 8.4), dpi=80)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.66], height_ratios=[1, 0.27], left=0.008, right=0.992,
                          top=0.885, bottom=0.01, wspace=0.03, hspace=0.06)
    a_front, a_rear, a_in, a_strip = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[:, 2]), fig.add_subplot(gs[1, :2])
    fr = frames(); print("frames:", len(fr))
    for idx in [int(i) for i in os.environ["HUB_ANIM_TEST"].split(",")]:
        cap, st, act, placed, ph = fr[idx]
        full, cut = scene(st, act, placed)
        draw(a_front, polys(full, "front"), "front"); draw(a_rear, polys(full, "rear"), "rear")
        draw(a_in, polys(cut, "inside"), "inside"); inside_labels(a_in, act); draw_strip(a_strip, act, ph)
        for t in list(fig.texts): t.remove()
        fig.text(0.008, 0.905, cap, fontsize=12, weight="bold", color="#18232b")
        fig.savefig(os.environ["HUB_ANIM_OUT"] + "_%d.png" % idx)
        ext = a_in.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(os.environ["HUB_ANIM_OUT"] + "_%d_inside.png" % idx, bbox_inches=ext, dpi=220)
        print("test frame", idx, cap)
else:
    main()
