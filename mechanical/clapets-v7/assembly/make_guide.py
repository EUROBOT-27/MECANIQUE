# make_guide.py - builds the module A assembly guide (A4 PDF) from assembly/steps.py and the images rendered by
# fc/assembly_images_v7.py.   Run: python mechanical/clapets-v7/assembly/make_guide.py
import importlib.util
import json
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
spec = importlib.util.spec_from_file_location("steps", os.path.join(HERE, "steps.py"))
steps_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(steps_mod)
STEPS, FINAL = steps_mod.STEPS, steps_mod.FINAL
VIEWS = json.load(open(os.path.join(IMG, "views.json"), encoding="utf-8"))

INK, MUTED, LINE, ACCENT = "#1c2928", "#5b6b69", "#9aa8a6", "#c4561d"
A4 = (8.27, 11.69)
NPAGES = len(STEPS) + 2
DATE = "2026-11-10"
plt.rcParams["font.family"] = "DejaVu Sans"


def crop(path, pad=20):
    im = Image.open(path).convert("RGB")
    px = im.load()
    w, h = im.size
    xs, ys = [], []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            if r < 245 or g < 245 or b < 245:
                xs.append(x)
                ys.append(y)
    x0, x1 = max(min(xs) - pad, 0), min(max(xs) + pad, w)
    y0, y1 = max(min(ys) - pad, 0), min(max(ys) + pad, h)
    return im.crop((x0, y0, x1, y1)), (x0, y0)


def header(fig, n, title):
    fig.text(0.04, 0.955, title, color=INK, fontsize=16, fontweight="bold", va="center")


def title_block(fig, n):          # 2026-11-10: page number only
    fig.text(0.5, 0.025, "%d / %d" % (n, NPAGES), ha="center", fontsize=8, color=MUTED)


def place_image(fig, im, box):
    """box = (x0, y0, w, h) in figure fraction; keeps the aspect, centred. Returns the axes and the scale."""
    x0, y0, bw, bh = box
    iw, ih = im.size
    fw, fh = A4
    s = min(bw * fw / iw, bh * fh / ih)          # inch per px
    w, h = iw * s / fw, ih * s / fh
    ax = fig.add_axes([x0 + (bw - w) / 2, y0 + (bh - h) / 2, w, h])
    ax.imshow(im)
    ax.set_xlim(0, iw)
    ax.set_ylim(ih, 0)
    ax.axis("off")
    return ax


def step_page(pdf, st, n):
    fig = plt.figure(figsize=A4)
    header(fig, n, "Step %d  ·  %s" % (st["id"], st["title"]))
    v = VIEWS[str(st["id"])]
    # ---- exploded view + balloons in a column on the right
    im, (ox, oy) = crop(os.path.join(IMG, v["exploded"]))
    iw, ih = im.size
    canvas = Image.new("RGB", (int(iw * 1.45), ih), "white")
    canvas.paste(im, (0, 0))
    ax = place_image(fig, canvas, (0.04, 0.47, 0.92, 0.46))
    balls = v["balloons"]
    order = sorted(range(len(balls)), key=lambda i: balls[i]["px1"][1])
    col_x = iw * 1.08
    ys = [ih * (0.08 + 0.84 * k / max(len(balls) - 1, 1)) for k in range(len(balls))] if len(balls) > 1 else [ih / 2]
    for k, i in enumerate(order):
        b = balls[i]
        x1, y1 = b["px1"][0] - ox, b["px1"][1] - oy
        x0, y0 = b["px0"][0] - ox, b["px0"][1] - oy
        for (q0, q1) in b.get("arrows_px", []):          # one arrow per part: from where it is drawn to where it goes
            ax.add_patch(FancyArrowPatch((q1[0] - ox, q1[1] - oy), (q0[0] - ox, q0[1] - oy), arrowstyle="-|>",
                                         mutation_scale=10, color=ACCENT, lw=1.0, linestyle=(0, (4, 3))))
        by = ys[k]
        ax.plot([x1, col_x - 22], [y1, by], color=INK, lw=0.6)
        ax.plot([x1], [y1], "o", color=INK, ms=2.5)
        ax.add_patch(Circle((col_x, by), 20, fc="white", ec=INK, lw=1.0))
        ax.text(col_x, by, str(k + 1), ha="center", va="center", fontsize=8, fontweight="bold", color=INK)
        ax.text(col_x + 30, by, b["text"], ha="left", va="center", fontsize=7.5, color=INK)
    # ---- detail (2D) bottom-left with a 10 mm scale bar
    dim, _ = crop(os.path.join(IMG, v["detail"]), pad=30)
    dax = place_image(fig, dim, (0.04, 0.10, 0.44, 0.30))
    dw, dh = dim.size
    mmpx = v["detail_mm_per_px"]
    L = 10.0 / mmpx
    dax.plot([20, 20 + L], [dh - 15, dh - 15], color=INK, lw=2)
    dax.text(20 + L / 2, dh - 28, "10 mm", ha="center", fontsize=6.5, color=INK)
    fig.text(0.04, 0.41, "Detail", fontsize=9, fontweight="bold", color=INK)
    fig.text(0.04, 0.085, "\n".join(textwrap.wrap(st["detail"]["caption"], 62)), fontsize=6.8, color=MUTED, va="top")
    fig.add_artist(Rectangle((0.04, 0.10), 0.44, 0.30, transform=fig.transFigure, fill=False, ec=LINE, lw=0.6))
    # ---- right column: instructions, parts, tools
    x = 0.52
    fig.text(x, 0.41, "How", fontsize=9, fontweight="bold", color=INK)
    fig.text(x, 0.395, "\n".join(textwrap.wrap(st["intro"], 58)), fontsize=7.3, color=INK, va="top", linespacing=1.35)
    lines_intro = len(textwrap.wrap(st["intro"], 58))
    y = 0.395 - lines_intro * 0.0135 - 0.02
    fig.text(x, y, "Parts and fasteners (one door unit)" if st["id"] >= 8 else "Parts and fasteners", fontsize=9, fontweight="bold", color=INK)
    y -= 0.018
    for q, item in st["parts"]:
        fig.text(x, y, q, fontsize=7.3, color=INK, fontweight="bold")
        for j, ln in enumerate(textwrap.wrap(item, 52)):
            fig.text(x + 0.035, y - j * 0.013, ln, fontsize=7.3, color=INK)
        y -= 0.013 * max(1, len(textwrap.wrap(item, 52))) + 0.004
    y -= 0.012
    fig.text(x, y, "Tools", fontsize=9, fontweight="bold", color=INK)
    fig.text(x, y - 0.016, "\n".join(textwrap.wrap(st["tools"], 58)), fontsize=7.3, color=INK, va="top")
    title_block(fig, n)
    pdf.savefig(fig)
    plt.close(fig)


def cover_page(pdf):
    fig = plt.figure(figsize=A4)
    header(fig, 1, "Clapets v7 · Module A")
    fig.text(0.04, 0.925, "Assembly guide: lift + door units", fontsize=11, color=MUTED)
    im, _ = crop(os.path.join(IMG, "cover.png"))
    place_image(fig, im, (0.08, 0.54, 0.84, 0.35))
    fig.text(0.04, 0.515, "Contents", fontsize=10, fontweight="bold", color=INK)
    y = 0.495
    for st in STEPS:
        fig.text(0.05, y, "Step %2d   %s" % (st["id"], st["title"]), fontsize=8, color=INK, family="DejaVu Sans Mono")
        fig.text(0.5, y, "sheet %d" % (st["id"] + 1), fontsize=8, color=MUTED)
        y -= 0.016
    fig.text(0.05, y, "Last     %s" % FINAL["title"], fontsize=8, color=INK, family="DejaVu Sans Mono")
    fig.text(0.5, y, "sheet %d" % NPAGES, fontsize=8, color=MUTED)
    notes = ["Steps 1-7 build the lift. Steps 8-13 build the right door unit; the left one is its mirror.",
             "Coloured parts = this step, grey = already in place, dashed arrows = assembly direction."]
    y -= 0.03
    fig.text(0.04, y, "Notes", fontsize=10, fontweight="bold", color=INK)
    y -= 0.02
    for t in notes:
        for j, ln in enumerate(textwrap.wrap(t, 105)):
            fig.text(0.05, y, ("·  " if j == 0 else "   ") + ln, fontsize=7.5, color=INK)
            y -= 0.015
    title_block(fig, 1)
    pdf.savefig(fig)
    plt.close(fig)


def final_page(pdf):
    fig = plt.figure(figsize=A4)
    header(fig, NPAGES, FINAL["title"])
    im, _ = crop(os.path.join(IMG, "cover.png"))
    place_image(fig, im, (0.15, 0.5, 0.7, 0.4))
    y = 0.46
    for i, t in enumerate(FINAL["text"], 1):
        lines = textwrap.wrap(t, 95)
        for j, ln in enumerate(lines):
            fig.text(0.05, y, ("%d.  " % i if j == 0 else "     ") + ln, fontsize=8.5, color=INK)
            y -= 0.018
        y -= 0.01
    title_block(fig, NPAGES)
    pdf.savefig(fig)
    plt.close(fig)


def main():
    out = os.path.join(HERE, "clapets_v7_moduleA_assembly.pdf")
    with PdfPages(out) as pdf:
        cover_page(pdf)
        for st in STEPS:
            step_page(pdf, st, st["id"] + 1)
        final_page(pdf)
    print(out)


if __name__ == "__main__":
    main()
