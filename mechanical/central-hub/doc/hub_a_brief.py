# hub_a_brief.py - PDF brief on central hub option A: advantages, drawbacks, best match strategy.
# Run (system Python with reportlab + matplotlib + Pillow), from mechanical/central-hub/:
#     python doc/hub_a_brief.py
# Inputs: ../simulations/central_hub/hub_option_a_sequence.gif (frames for the figures), numbers from CONNECTIONS.md,
# hub_a_report.txt, the Gazebo run (EB27_Classic_Sim, 2026-11-15) and project/strategy.md (table coordinates).
# Output: HUB_A_brief.pdf (next to CONNECTIONS.md)
import math, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
                                PageBreak, KeepTogether)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GIF = os.path.normpath(os.path.join(ROOT, "..", "simulations", "central_hub", "hub_option_a_sequence.gif"))
TMP = os.path.join(HERE, "_tmp"); os.makedirs(TMP, exist_ok=True)
OUT = os.path.join(ROOT, "HUB_A_brief.pdf")

INK, MUTED, ACC = colors.HexColor("#18232b"), colors.HexColor("#5b6b75"), colors.HexColor("#e6007e")
GOOD, BAD, WARN = colors.HexColor("#1a7f37"), colors.HexColor("#c2372b"), colors.HexColor("#b26b00")

# ---------------- figures ----------------
def gif_frame(caption_has, path):
    """First GIF frame whose index matches a fraction (the GIF has no captions to search): pick by fraction."""
    im = Image.open(GIF); n = im.n_frames
    im.seek(int(caption_has * (n - 1))); im.convert("RGB").save(path)
    return path

def table_map(path):
    """Yellow castle corner of the table: tower / wall zones, throne room, nearest quarries, the 2 hub stops."""
    fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=150)
    ax.set_xlim(-20, 1350); ax.set_ylim(2020, -20); ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), 3000, 2000, fc="#f4f1e8", ec="#18232b", lw=1.2))
    ax.add_patch(Rectangle((6, 755), 489, 490, fc="#f7b500", alpha=0.25, ec="#b98500"))
    ax.text(250, 1000, "throne room\n(start / home)", ha="center", va="center", fontsize=8)
    def wall(cx, cy, ang, lab=None):
        w, h = 390, 190
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        pts = [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))]
        ax.add_patch(Polygon(pts, closed=True, fc="none", ec="#8a8f94", lw=1, ls="--"))
        if lab: ax.text(cx, cy, lab, fontsize=6.5, color="#5b6b75", ha="center", va="center")
    wall(250, 400, 0, "wall"); wall(679, 571, 45); wall(850, 1000, 90, "central\nwall"); wall(679, 1429, -45); wall(250, 1600, 0, "wall")
    towers = [(500, 400), (850, 748), (850, 1246), (503, 1599)]
    for x, y in towers:
        ax.add_patch(Circle((x, y), 95, fc="#f7b500", alpha=0.35, ec="#b98500", lw=1.2))
    for x0 in (590, 1090):                                           # nearest border quarries (stones along x)
        for y0 in (5, 1995 - 110):
            ax.add_patch(Rectangle((x0, y0), 320, 110, fc="#d9ad72", ec="#8a6a3a"))
    ax.text(750, 140, "quarry (3 stones)", ha="center", fontsize=6.5); ax.text(750, 1865, "quarry", ha="center", fontsize=6.5)
    # stops: the hub puts its 2 towers 450 mm apart, square to the heading (front stone -> left, rear -> right)
    stops = [("A: middle pair", towers[0], towers[1], "#8b5cf6"), ("B: top pair", towers[3], towers[2], "#e0612a")]
    for lab, p, q, col in stops:
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        ux, uy = (q[0] - p[0]), (q[1] - p[1]); L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        hx, hy = -uy, ux                                             # heading, square to the tower line
        if hy > 0: hx, hy = -hx, -hy
        corners = [(mx + a * ux * 165 + b * hx * 140, my + a * uy * 165 + b * hy * 140) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        ax.add_patch(Polygon(corners, closed=True, fc=col, alpha=0.25, ec=col, lw=1.5))
        ax.add_patch(FancyArrowPatch((mx, my), (mx + hx * 190, my + hy * 190), arrowstyle="-|>", mutation_scale=10, color=col))
        for s in (-1, 1):
            tx, ty = mx + s * ux * 225, my + s * uy * 225
            ax.add_patch(Rectangle((tx - 55, ty - 55), 110, 110, fc=col, ec="#18232b", lw=0.8))
        ax.text(mx + hx * 260, my + hy * 260, lab, color=col, fontsize=8, weight="bold", ha="center", va="center")
        ax.text(mx - hx * 210 + 10, my - hy * 210, "%.0f mm\napart" % L, fontsize=6.5, color="#5b6b75", ha="center")
    ax.text(1000, 1000, "C: bottom pair\n= spare\n(see below)", color="#14958a", fontsize=8, weight="bold", ha="center", va="center")
    ax.set_xticks(range(0, 1400, 200)); ax.set_yticks(range(0, 2001, 250)); ax.tick_params(labelsize=7)
    ax.set_xlabel("x (mm), yellow side - blue is the mirror x -> 3000 - x", fontsize=7)
    ax.set_title("Two stops fill all 4 tower zones (zone pairs ~495 mm apart, hub pair 450 mm)", fontsize=9)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return path

def timeline(path):
    """Gazebo timeline (EB27_Classic_Sim, 40 mm/s slides) as bars."""
    rows = [("grip + unpinch", 0.0, 0.5, "#5b6b75"), ("middle pair", 0.5, 3.5, "#8b5cf6"), ("drive", 4.0, 1.7, "#9aa5ad"),
            ("top pair", 5.7, 13.8, "#e0612a"), ("drive", 19.5, 1.7, "#9aa5ad"), ("bottom pair", 21.2, 12.6, "#14958a")]
    fig, ax = plt.subplots(figsize=(7.2, 1.5), dpi=150)
    for i, (lab, t0, d, c) in enumerate(rows):
        ax.barh(0, d, left=t0, color=c, height=0.5)
        ax.text(t0 + d / 2, 0, lab, ha="center", va="center", fontsize=6.5, color="white" if d > 3 else "#18232b",
                rotation=0 if d > 3 else 90)
    ax.set_xlim(0, 34); ax.set_yticks([]); ax.set_xlabel("seconds (Gazebo, 2026-11-15, geometry before the middle-arm fix: 6/6 towers standing in 33.8 s; the top level is now ~1 s shorter)", fontsize=7)
    ax.tick_params(labelsize=7)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return path

# ---------------- document ----------------
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=19, leading=23, textColor=INK, alignment=0, spaceAfter=2)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=9, textColor=MUTED, leading=12)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, leading=16, textColor=INK, spaceBefore=10, spaceAfter=4)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontSize=10.5, leading=13, textColor=INK, spaceBefore=6, spaceAfter=2)
B = ParagraphStyle("B", parent=ss["Normal"], fontSize=9, leading=12.2, textColor=INK)
SM = ParagraphStyle("SM", parent=B, fontSize=8, leading=10.4)
CAP = ParagraphStyle("CAP", parent=B, fontSize=7.5, leading=9.5, textColor=MUTED)

def tbl(rows, widths, head_bg="#eef1f3", font=8):
    data = [[Paragraph(c, ParagraphStyle("c", parent=SM, fontSize=font, leading=font * 1.28)) if isinstance(c, str) else c for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(head_bg)), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d6db")),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t

def build():
    W = A4[0] - 30 * mm
    f1 = gif_frame(0.30, os.path.join(TMP, "f_top.png"))
    f2 = gif_frame(0.80, os.path.join(TMP, "f_bottom.png"))
    fm = table_map(os.path.join(TMP, "map.png"))
    ft = timeline(os.path.join(TMP, "timeline.png"))
    S = []
    S.append(Paragraph("Central hub - option A", H1))
    S.append(Paragraph("Advantages, drawbacks and the best way to use it in a match &nbsp;|&nbsp; 2026-11-15 &nbsp;|&nbsp; "
                       "concept by Ayoub, <b>proposal, not reviewed by Seif</b>", SUB))
    S.append(Spacer(1, 6))
    S.append(Paragraph(
        "<b>What it is.</b> A Ø100 column in the middle of the robot with 3 rings, one per stone of a quarry stack. Each ring "
        "carries a front arm and a rear arm, so the robot carries <b>two full stacks (6 stones)</b>. A ring turns 90° "
        "(one MG996R inside the hub, 2:1 internal gear), the top and bottom arms slide their cup to the spin height "
        "(N20 + lead screw), a MG90S spins the stone upright and the cup vents (middle and top stones drop 15 mm, the bottom one is set on the table): <b>2 towers per stop, 450 mm apart</b>, "
        "front stone on the robot's left, rear stone on its right. Order: middle, then top, then bottom.", B))
    S.append(Spacer(1, 4))
    S.append(RLImage(f1, width=W, height=W * 688 / 1360))
    S.append(Paragraph("GIF frame (simulations/central_hub/hub_option_a_sequence.gif): robot seen from the front-left and the "
                       "rear-right, the inside of the hub, and the actuator strip. Magenta = actuator working.", CAP))

    S.append(Paragraph("1. Key numbers", H2))
    S.append(tbl([
        ["Item", "Value", "Source"],
        ["Stones carried / towers per stop", "6 (2 stacks) / 2, 450 mm apart", "hub_a_fc.py"],
        ["Actuators", "13 motors (3 MG996R, 4 N20, 6 MG90S) + 6 pumps + 6 vent valves + 4 switches. "
                      "Electronics: 9 PWM, 4 DC channels, 12 MOSFETs, 4 inputs", "CONNECTIONS.md §3"],
        ["Height", "mechanism 328 mm, stones up to 345 mm (limit 350)", "hub_a_report.txt, GR F.3"],
        ["Collisions", "0 in 164 steps between levels, min gap 5.3 mm (middle arm, fixed 2026-11-15: was 2 mm); <b>bottom slide hits the Ø90 drive wheels</b> (open, smaller wheel planned)", "hub_a_env_report.txt"],
        ["Full cycle (Gazebo)", "6/6 towers standing, 33.8 s incl. 2 drives of 340 mm, with 40 mm/s slides", "EB27_Classic_Sim"],
        ["Slides today", "M4 screw + 300 rpm N20 = 3.5 mm/s, <b>~35 s per stroke</b>: too slow", "CONNECTIONS.md §3"],
    ], [42 * mm, 95 * mm, W - 137 * mm]))

    S.append(Paragraph("2. Advantages", H2))
    adv = [
        ("6 stones in one load", "Two whole quarry stacks are taken in one go. Fewer trips to the quarries than any 1- or 3-stone gripper."),
        ("2 towers per stop", "Front and rear place at the same time. Towers are worth 1 + 5 = 6 points each [G E.1]; the hub "
                              "builds them without a wall or a jig to lean the stone against."),
        ("Pair spacing fits the castle", "Three pairs of our tower zones are ~495 mm apart; the hub puts its towers 450 mm apart. "
                                         "Each tower lands ~23 mm off its zone centre, and a tower counts as soon as part of it is in the Ø200 zone, so there is ~130 mm of margin."),
        ("Every move is reversible", "No grooves, no elastics, no one-way latches. Each level can be stopped, sent home and retried."),
        ("Levels are independent", "Each ring has its own band and its own servo. The middle level is very fast (~3.5 s, no slide)."),
        ("Turn drive is protected", "The 3 turn servos sit inside the hub bore. Hoses and wires go down the same bore."),
        ("Inside the rules on height", "Mechanism 328 mm, stones 345 mm, in every pose of the sequence (GR F.3)."),
        ("Symmetric", "The rear unit is the front unit turned 180°. Mass is balanced on the drive axle."),
        ("Verified early", "164-step clash check in FreeCAD, then 6/6 towers standing and 0 disturbed in Gazebo."),
        ("Parts in hand", "MG996R, MG90S, N20, suction cups are in the parts library; printed parts in ABS."),
    ]
    S.append(tbl([["Advantage", "Why it matters"]] + [["<font color='#1a7f37'><b>+</b></font> <b>%s</b>" % a, b] for a, b in adv],
                 [48 * mm, W - 48 * mm]))

    S.append(Paragraph("3. Drawbacks and risks", H2))
    dis = [
        ("High", "Slides far too slow", "M4 lead screw on a 300 rpm N20 = ~35 s per stroke. Needs a T8 lead-8 screw, a >= 1000 rpm N20 or a rack (~40 mm/s, as in Gazebo)."),
        ("High", "Uses the whole robot", "The 2 stacks sit on the front and rear faces, and the arms sweep the front-left and rear-right quarters out to r ~280. "
                                         "The clapets/wall modules (front + back in layout-v1), the Grail lift (right) and the launcher (left) all want that space. "
                                         "The column also takes the centre top, where the LiDAR, beacon mast and Grail L4 roof go."),
        ("High", "Bottom slide hits the drive wheels", "Clash A: 45 of 167 steps with the Ø90 wheels of base_330 (and with layout-v1). Needs smaller wheels or a moved slide."),
        ("High", "Only 4 tower zones", "6 stones can become 6 towers, but only 4 score as towers (24 pts). The third pair adds ~2 pts at best."),
        ("Med", "Front and rear are coupled", "One servo per ring moves both arms: no single tower, and one dead servo loses both towers of that level."),
        ("Med", "Tight exit between towers", "Inner faces of the 2 towers are at r 170; the plate is ±165 wide. 5 mm each side when the robot drives on. Drive straight along the heading, never turn at the stop."),
        ("Med", "Cups rub the towers after venting", "Seen in Gazebo on all 6 towers. Retract (slide up a few mm, or turn the ring with the cup spun back) before the robot moves."),
        ("Med", "Turn accuracy", "Many MG996R turn only 120-160°, giving a 60-80° ring turn with the 2:1 gear; backlash doubles at the cup. No feedback on turn or spin."),
        ("Med", "Stiffness", "Plain ABS journal bearings (10 mm long, ~0.5° tilt = 2.5 mm at the stone) and 143 mm printed cantilever rails."),
        ("Med", "Complexity", "13 motors, 6 pumps, 6 valves: many wires and hoses through one Ø38 free bore, no service loop designed yet. A 370 pump stays sealed when stopped: valves are needed."),
        ("Low", "Assembly", "A turn servo comes out only after the segments above it. Some nuts are loose (J2, J10, J18)."),
        ("Low", "Standing stones show no tag", "Tag 13 is only on the long faces, so placed towers are hard to see for vision checks."),
    ]
    sev = {"High": BAD, "Med": WARN, "Low": MUTED}
    S.append(tbl([["", "Drawback", "Detail / what to do"]] +
                 [["<font color='%s'><b>%s</b></font>" % (sev[s].hexval().replace("0x", "#"), s), "<b>%s</b>" % a, b] for s, a, b in dis],
                 [12 * mm, 40 * mm, W - 52 * mm]))

    S.append(PageBreak())
    S.append(Paragraph("4. Best strategy in a real match", H2))
    S.append(Paragraph(
        "The hub is a <b>tower machine</b>. Its value is 4 towers in the 4 tower zones = <b>24 points</b> "
        "(4 x (1 stone + 5)) from 2 stacks. Laying the same 2 stacks down as walls would give 2 x (3 + 5) = 16 points with a "
        "much simpler gripper, so the hub only pays off if it fills <b>all 4 tower zones</b> quickly and reliably. "
        "The table makes that possible with only <b>2 stops</b>:", B))
    S.append(Spacer(1, 4))
    S.append(RLImage(fm, width=W * 0.82, height=W * 0.82 * 6.4 / 7.2))
    S.append(Paragraph("Yellow side (coordinates from Docs/table.svg via project/strategy.md). Stop A: robot centre ~(675, 574), "
                       "towers at (500, 400) + (850, 748). Stop B: ~(676, 1422), towers at (503, 1599) + (850, 1246). "
                       "Quarry y positions are approximate.", CAP))

    S.append(Paragraph("Match plan (yellow; blue mirrors x)", H3))
    plan = [
        ["Time", "Step", "Notes"],
        ["0-12 s", "Leave the throne room, take stack 1 with the <b>front</b> face at a border quarry (x 590-910).",
         "Approach square to the border: the stones lie along x, so they line up with the cups."],
        ["12-22 s", "Reverse along x ~750 to the quarry on the other long border, take stack 2 with the <b>rear</b> face.",
         "Same heading, no turn. Both stacks held, base +10 mm."],
        ["22-30 s", "Drive to <b>stop A</b>, heading square to the line of zones (500, 400)-(850, 748). Unpinch + <b>middle pair</b> (~4 s).",
         "Middle first: no slide, fastest, and it frees the space the top and bottom stones pass through."],
        ["30-48 s", "Drive straight on >= 340 mm, then go to <b>stop B</b> (~850 mm). <b>Top pair</b> into (503, 1599) + (850, 1246) (~14 s).",
         "Drive on along the heading first (5 mm each side between the towers), only then turn."],
        ["48-62 s", "<b>Bottom pair (stop C)</b>: see the options below. ~13 s.",
         "Keep it for last: by then the hub is empty above it."],
        ["62-85 s", "Hub empty: the robot is free for the Grail, walls with the other modules, or a second load.",
         "Towers are next to the throne room: stay clear of them."],
        ["85-100 s", "Attack phase (SIMAs, cannonballs) and return home (+10).", ""],
    ]
    S.append(tbl(plan, [16 * mm, 88 * mm, W - 104 * mm]))

    S.append(Paragraph("What to do with the bottom pair (stop C)", H3))
    S.append(tbl([
        ["Option", "Points", "Comment"],
        ["<b>Spare pair (recommended)</b>: if a tower of A or B fell or missed its zone, go back and place the bottom pair there.",
         "keeps 24", "Turns 2 extra stones into insurance. Both towers of a stop are placed again together, so the robot stops beside the old pair, square to it."],
        ["Stand them in 2 construction zones nobody will use for a wall.", "+2", "1 point per stone in a zone [G E.1]. Do not block a wall zone the team needs (one building per zone)."],
        ["Do not place them; bring them home.", "0", "Stones still held at the end do not count. Only if time runs out."],
    ], [70 * mm, 18 * mm, W - 88 * mm]))

    S.append(Paragraph("Rules of thumb on the table", H3))
    for t in [
        "<b>Towers first, walls after</b> in the diagonal wall zones: stops A and B stand on the zones (679, 571) and (679, 1429).",
        "<b>Never turn at a stop.</b> Drive straight out along the heading for >= 340 mm (Gazebo: shorter steps make the next level knock the towers).",
        "<b>Vent, then retract, then move.</b> Lift the top and bottom cups a few mm and spin back before turning the ring home.",
        "<b>Check the pair before leaving</b> (vacuum sensor or camera on the zone): the bottom pair can only repair a stop if the robot knows it failed.",
        "<b>Do it early.</b> The towers stand next to our throne room; a late opponent visit near our castle is less likely than a crowded centre.",
        "<b>Blue side:</b> mirror x -> 3000 - x. Front stones still go to the robot's left, so plan the heading per side.",
    ]:
        S.append(Paragraph("&bull; " + t, B))

    S.append(Paragraph("5. Before this can play a match", H2))
    S.append(tbl([
        ["#", "Action", "Why"],
        ["1", "Faster slides: T8 lead-8 screw or >= 1000 rpm N20 (or a rack)", "35 s per stroke today makes the plan above impossible"],
        ["2", "Smaller drive wheels, re-run fc/check_env_a.py", "Clash A with the bottom slide"],
        ["3", "Check against layout-v1 (front module, Grail lift, launcher, LiDAR, beacon)", "The hub uses both faces and the centre of the robot"],
        ["4", "Measure the MG996R range and the gear backlash", "Ring angle and stone position at r 225"],
        ["5", "Add feedback: vacuum sensor per cup, home switch per ring", "Needed to know when to use the spare pair"],
        ["6", "Retract move after venting (slide up / small ring back-off)", "Cups rub the towers (Gazebo)"],
        ["7", "Design the 90° service loops for hoses and wires (J17)", "12 hoses/wire bundles through one bore"],
        ["8", "Seif review, then log a decision (proposed until confirmed)", "It is still Ayoub's proposal"],
    ], [8 * mm, 85 * mm, W - 93 * mm]))
    S.append(Spacer(1, 8))
    S.append(RLImage(ft, width=W, height=W * 1.5 / 7.2))
    S.append(Spacer(1, 6))
    S.append(RLImage(f2, width=W, height=W * 688 / 1360))
    S.append(Paragraph("GIF frame during the bottom level. The full GIF shows the whole cycle with the robot driving on between levels.", CAP))

    def footer(c, d):
        c.saveState(); c.setFont("Helvetica", 7); c.setFillColor(MUTED)
        c.drawString(15 * mm, 9 * mm, "IEEE RAS INSAT - Eurobot 2027 - central hub option A brief (proposal)")
        c.drawRightString(A4[0] - 15 * mm, 9 * mm, "page %d" % d.page); c.restoreState()
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm, bottomMargin=15 * mm,
                            title="Central hub option A - brief", author="IEEE RAS INSAT")
    doc.build(S, onFirstPage=footer, onLaterPages=footer)
    print("wrote", OUT)

build()
