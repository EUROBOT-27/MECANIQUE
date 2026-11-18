# hub_a_fc.py - Central hub, OPTION A (Ayoub's concept, not reviewed): no grooves, no elastics, every move reversible.
#  - 3 full rings on the hub column, one per stack level, each in its own fixed band (they only turn, never cross).
#  - Each ring carries 2 arms 180 deg apart: front arm (stone goes to the robot's left) + rear arm (to the right).
#    A 90 deg turn of a ring swings both: 2 towers per stop (front + rear stones end ~450 mm apart).
#  - Turn: one MG996R per ring INSIDE the hub bore; its pinion pokes through a window in the hub wall and meshes an
#    internal gear in the ring bore (2:1, 180 deg servo -> 90 deg ring). Teeth drawn as simple blocks.
#  - Height: top and bottom arms carry a vertical slide (rail + carriage, N20 gear motor + M4 lead screw, nut in the carriage); the middle arm
#    is fixed. All 3 arms park at the same angle, so seen from the side (r, z) their parts must not overlap:
#    top rail r 76-84, bottom rail r 104-112, middle arm stepped between them, >= 5 mm while it turns (see 2026-11-15 below). Heights change only once turned out
#    (exception: the bottom carriage rises +16 at home before its turn, once the levels above are empty).
#  - Spin: one micro servo per carriage, radial axis, turns cup + stone 90 deg (stone stands up).
#
# 2026-11-14 (connections, see ../CONNECTIONS.md): hub split into 4 segments S1-S4 with the spacers as collars, clamped by
# 3 M4 tie rods; pinion windows and ring gear bands open to the top (assembly: segment, ring, servo + pinion, next
# segment); MG996R ears + wall slots; printed servo cradles held by radial M3 through the collars; ring lugs + arm pads
# (2 x M3 each); N20 clamps, couplers, screw-end bearings, lead nuts, limit switches; every fastener drawn.
# 2026-11-15 (Ayoub: the middle arm collided with the top and bottom arms): the gaps at the rail ends were 2 mm. Top rail
# shortened (ends at 161, top stone dropped 15 mm from the spin height like the middle), middle crossover raised 199 -> 213,
# rails moved apart (top 4 mm in, bottom 2 mm out, bottom spin shaft 2 mm shorter).
# Previous version (grooved hub, rejected for drive + clashes): fc/hub_fc.py + hub_report.txt.
#
# Run: "<FreeCAD>/bin/freecadcmd.exe" fc/hub_a_fc.py   (from mechanical/central-hub/)
# Writes CAD_FC/HUB_A_*.FCStd (poses), hub_a_report.txt (clash + height check of the full sequence + fastener list).
# Animation: fc/anim_a.py. Sheet: fc/sheet_a.py. Fixed parts + base_330 check: fc/check_env_a.py.
# Frame: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table. mm.
import math, os
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "CAD_FC"); os.makedirs(OUT, exist_ok=True)
SIM = os.path.join(ROOT, "..", "simulations", "central_hub"); os.makedirs(SIM, exist_ok=True)
V = App.Vector

# ---------------- parameters ----------------
HUB_R, HUB_RI, HUB_Z0, HUB_Z1 = 50.0, 38.0, 73.0, 345.0
RING_RI, RING_RO, RING_H = 50.5, 62.0, 20.0
RING_Z = [90.0, 140.0, 245.0]              # ring band centres: bottom, middle, top (bottom low: room for its turn servo)
MID_OVER = 213.0                           # middle arm crosses over the bottom rail here (cap top 193 -> 16 mm gap; was 199 = 2 mm)
BR, TR = 104.0, 76.0                        # bottom rail r 104-112 (between the middle post r 92-98 and drop r 118-124: ~5 mm each side
                                            # as the middle arm turns), top rail r 76-84 (~7 mm). Were 102-110 / 80-88 (2 mm)
COLLAR_RO = 56.0                           # collars between the rings (were the spacer tubes): axial location
BAR_W, BAR_T = 14.0, 8.0
RAIL_R0, RAIL_R1, RAIL_W = 100.0, 110.0, 10.0
CAR_R0, CAR_R1, CAR_H = 110.0, 116.0, 24.0
SERVO = (23.0, 12.2, 22.7)                 # MG90S body, output axis radial (r 116..139)
SHAFT_R0, SHAFT_R1, SHAFT_D = 139.0, 150.0, 8.0
CUP_R0, CUP_R1, CUP_D = 150.0, 170.0, 30.0
FACE = 170.0
STONE = (320.0, 110.0, 110.0)
LIFT = 10.0
Z_STACK = [55.0 + LIFT, 165.0 + LIFT, 275.0 + LIFT]   # cup / stone centre heights in the stack
Z_SPIN = 175.0                             # spin-safe height (169..181 for a 320 x 110 stone, table..350)
Z_SET = 160.0                              # standing stone centre when it touches the table (320 / 2)
Z_CLEAR = Z_STACK[0] - 5 + 16              # bottom carriage before its turn: stone clears the base plate (z 18.5)
RAIL_Z = {0: (Z_STACK[0] - 5 - CAR_H / 2 - 2, Z_SPIN + CAR_H / 2 + 2),
          2: (Z_SPIN - CAR_H / 2 - 2, Z_STACK[2] + 5 + CAR_H / 2 + 2)}   # top rail ends at 161: the top cup stops at the spin
# height and the stone drops 15 mm like the middle one (was set at 160 -> rail end 146, 2 mm over the middle bar)
# Turn drive INSIDE the hub: one MG996R per ring in the 76 mm bore; its pinion pokes through a window in the hub wall and
# meshes an internal gear cut in the ring's bore (pitch r 52). Pinion pitch r 26 -> the ring turns half the servo angle,
# same direction: 180 deg servo -> 90 deg ring. Bottom + middle servos hang upside down above their pinion, top below.
PIN_POLAR = 45.0                            # mesh direction (inside the hub nothing else is in the way)
PIN_PR, PIN_C, GEAR_PR = 26.0, 26.0, 52.0   # pinion pitch radius, pinion centre off the hub axis, ring gear pitch radius
PIN_TIP, PIN_TH = 27.5, 8.0
GEAR_RO = 54.5                              # internal gear band cut in the ring bore (r 50.5 -> 54.5)
TURN_SERVO = (40.7, 19.7, 37.0)             # MG996R body; output shaft 10 mm from one end, + 4 mm spline boss
SERVO_UP = [True, True, False]              # body above the pinion (servo upside down) for bottom + middle
EAR_L, EAR_T, EAR_W, EAR_FROM_FACE = 7.0, 2.5, 18.0, 9.0   # MG996R ears: 7 past each end (54.5 overall), 9 from the output face
EAR_HOLE = 4.4                              # ear hole centre past the body end (hole spacing 49.5), holes at perp +-5
# Slide drive: N20 gear motor (12 x 10 x 24 incl. gearbox) + M4 lead screw beside the rail, nut block in the carriage.
SCREW_T, SCREW_D = 11.0, 4.0
NAMES = ["bottom", "middle", "top"]
# Hub segments (printed, ABS): joints at the top face of each ring band, the collar below each band belongs to the segment.
SEG_Z = [HUB_Z0] + [z + RING_H / 2 + 0.5 for z in RING_Z] + [HUB_Z1]     # 73 / 100.5 / 150.5 / 255.5 / 345
SPIG_R, SPIG_H = 41.0, 3.0                  # centring spigot at each joint (lip r 38.2-41 of the upper segment)
FLANGE = 94.0                               # S1 square flange on the bridge, 4 x M4 at (+-40, +-40)
ROD_R, ROD_POL = 44.0, (135.0, 225.0, 315.0)   # 3 M4 tie rods in the hub wall (windows are at polar 7-83)
CRADLE_R, CRADLE_ALONG, CRADLE_PERP = 37.6, 30.0, 16.0   # printed servo cradle: leaves |perp| > 16 free for hoses/wires
J5_ANG = (165.0, 195.0)                     # radial cradle screws, in the servo frame (polar 210 / 240): insert wall 3.4 to the cradle side
LUG_RO, LUG_HALF, PAD_T = 76.0, 20.0, 13.0  # ring lug r 62-76 over +-20 deg; arm pad +-13 wide in the lug slot
LUG_SCREW_R, LUG_SCREW_T = 69.0, 9.5

def polar(u, phi): return 90.0 + phi + (180.0 if u else 0.0)   # front starts at +Y and ends at -X; rear = turned 180

def rz(s, deg):
    s = s.copy(); s.rotate(V(0, 0, 0), V(0, 0, 1), deg); return s

def box(r0, r1, t0, t1, z0, z1):
    return Part.makeBox(r1 - r0, t1 - t0, z1 - z0, V(r0, t0, z0))

def cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))

def annulus(ri, ro, z0, z1):
    return cyl(ro, z0, z1).cut(cyl(ri, z0, z1))

def hexnut(af, h, x, y, z0, hole=None):
    R = af / math.sqrt(3)
    pts = [V(x + R * math.cos(math.radians(60 * i + 30)), y + R * math.sin(math.radians(60 * i + 30)), z0) for i in range(7)]
    s = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))
    if hole: s = s.cut(Part.makeCylinder(hole / 2, h, V(x, y, z0)))
    return s

def screw(p, d, L, dia, head_d, head_h):
    """Screw with its head behind p (from p - d*head_h to p) and the shank from p along unit vector d for L."""
    s = Part.makeCylinder(dia / 2, L, p, d)
    if head_h > 0: s = s.fuse(Part.makeCylinder(head_d / 2, head_h, p - d * head_h, d))
    return s

# ---------------- turn servos (fixed, inside the bore) ----------------
def turn_servo_z(k):
    """(z0 body bottom, output face z, ear z0, ear z1) of turn servo k."""
    z, sh = RING_Z[k], TURN_SERVO[2]
    if SERVO_UP[k]:
        z0 = z + PIN_TH / 2 + 4; face = z0; e0 = face + EAR_FROM_FACE; e1 = e0 + EAR_T
    else:
        z0 = z - PIN_TH / 2 - 4 - sh; face = z0 + sh; e1 = face - EAR_FROM_FACE; e0 = e1 - EAR_T
    return z0, face, e0, e1

def cradle_z(k):
    z0, face, e0, e1 = turn_servo_z(k)
    return (e1, z0 + TURN_SERVO[2]) if SERVO_UP[k] else (z0, e0)

A_IN = PIN_C + 10 - TURN_SERVO[0] - EAR_HOLE      # inner ear hole, along the servo axis (-9.1)

def seg_of(z):
    for i in range(4):
        if SEG_Z[i] <= z < SEG_Z[i + 1]: return i
    return 3

def pinion_env(k):
    """Window for pinion k: open from just below the pinion to the top of its segment (the pinion drops in from above)."""
    z0 = RING_Z[k] - PIN_TH / 2 - 1
    return rz(Part.makeCylinder(PIN_TIP + 1.0, SEG_Z[k + 1] - z0, V(PIN_C, 0, z0)), PIN_POLAR)

def ear_slot(k):
    """Slot in the hub wall for the outer ear of servo k, open to the segment end the servo comes in from."""
    z0, face, e0, e1 = turn_servo_z(k)
    i = seg_of(e0)
    za, zb = (SEG_Z[i], e1 + 1) if SERVO_UP[k] else (e0 - 1, SEG_Z[i + 1])
    return rz(box(35.0, 44.5, -10, 10, za, zb), PIN_POLAR)   # from r 35: the ear's side edges meet the bore at r 38

def turn_servo(k):
    sx, sy, sh = TURN_SERVO
    z0, face, e0, e1 = turn_servo_z(k)
    body = box(PIN_C + 10 - sx, PIN_C + 10, -sy / 2, sy / 2, z0, z0 + sh)
    boss = (RING_Z[k] + PIN_TH / 2, z0) if SERVO_UP[k] else (z0 + sh, RING_Z[k] - PIN_TH / 2)
    bs = Part.makeCylinder(6, boss[1] - boss[0], V(PIN_C, 0, boss[0]))
    ears = box(PIN_C + 10 - sx - EAR_L, PIN_C + 10 + EAR_L, -EAR_W / 2, EAR_W / 2, e0, e1)
    for a in (A_IN, PIN_C + 10 + EAR_HOLE):
        for p in (-5, 5): ears = ears.cut(cyl(2.2, e0, e1, a, p))
    return rz(body.fuse([bs, ears]), PIN_POLAR)

def j5_dir(a): return V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)

def cradle(k):
    """Printed cradle: hugs the inner part of the servo body, inner ear screwed to it (J4), held by 2 radial M3 (J5)."""
    sx, sy, sh = TURN_SERVO
    zc0, zc1 = cradle_z(k)
    c = cyl(CRADLE_R, zc0, zc1).common(box(-CRADLE_R, CRADLE_ALONG, -CRADLE_PERP, CRADLE_PERP, zc0, zc1))
    c = c.cut(box(PIN_C + 10 - sx - 0.3, PIN_C + 10 + 0.3, -sy / 2 - 0.3, sy / 2 + 0.3, zc0, zc1))
    z0, face, e0, e1 = turn_servo_z(k)
    nz = e0 + 7.8 if SERVO_UP[k] else e1 - 10.6
    for p in (-5, 5):                                                             # J4 holes + M3 nut pockets 6.9 x 2.8 (open to the back)
        c = c.cut(cyl(1.7, zc0, zc1, A_IN, p)).cut(box(-CRADLE_R, A_IN + 3.0, p - 3.45, p + 3.45, nz, nz + 2.8))
    zm = (zc0 + zc1) / 2
    for a in J5_ANG:                                                              # J5 insert holes: Ø5.4 x 7 + mouth Ø6.2 -> 5.4 over 1.5
        d = j5_dir(a)
        c = c.cut(Part.makeCylinder(2.7, 7.0, V(0, 0, zm) + d * (CRADLE_R - 7.0), d))
        c = c.cut(Part.makeCone(2.7, 3.1, 1.5, V(0, 0, zm) + d * (CRADLE_R - 1.5), d))
    return rz(c, PIN_POLAR)

def fixed_fasteners():
    """Every fastener that does not move: J2 hub->bridge, J3 tie rods, J4 servo ears, J5 cradle screws."""
    f = []
    for x in (-40, 40):                                                           # J2: 4 x M4x16 ISO 7380 + nut under the bridge
        for y in (-40, 40):
            f.append(screw(V(x, y, 77.2), V(0, 0, -1), 16, 4.0, 7.6, 2.2))
            f.append(hexnut(7.0, 3.2, x, y, 64.8, 4.0))
    for a in ROD_POL:                                                             # J3: 3 x M4 rod, nut in S1 + nut in S4
        x, y = ROD_R * math.cos(math.radians(a)), ROD_R * math.sin(math.radians(a))
        f.append(cyl(2.0, HUB_Z0 + 0.5, HUB_Z1 - 1.0, x, y))
        f.append(hexnut(7.0, 3.2, x, y, HUB_Z0 + 0.3, 4.0))
        f.append(hexnut(7.0, 3.2, x, y, HUB_Z1 - 4.2, 4.0))
    for k in range(3):
        z0, face, e0, e1 = turn_servo_z(k)
        loc = []
        for p in (-5, 5):                                                         # J4: M3x12 through the inner ear + nut in the cradle
            if SERVO_UP[k]:
                loc.append(screw(V(A_IN, p, e0), V(0, 0, 1), 12, 3.0, 5.5, 3.0))
                loc.append(hexnut(5.5, 2.4, A_IN, p, e0 + 8.0, 3.0))
            else:
                loc.append(screw(V(A_IN, p, e1), V(0, 0, -1), 12, 3.0, 5.5, 3.0))
                loc.append(hexnut(5.5, 2.4, A_IN, p, e1 - 10.4, 3.0))
        zm = sum(cradle_z(k)) / 2
        for a in J5_ANG:                                                          # J5: M3x25 countersunk, radial, + insert
            d = j5_dir(a)
            loc.append(screw(V(0, 0, zm) + d * (COLLAR_RO - 1.7), d * -1, 23.3, 3.0, 6.0, 1.7))
            loc.append(Part.makeCylinder(2.7, 6.0, V(0, 0, zm) + d * (CRADLE_R - 6.5), d).cut(
                Part.makeCylinder(1.5, 6.0, V(0, 0, zm) + d * (CRADLE_R - 6.5), d)))
        f += [rz(s, PIN_POLAR) for s in loc]
    return f

def segment(i):
    za, zb = SEG_Z[i], SEG_Z[i + 1]
    s = annulus(HUB_RI, HUB_R, za, zb)
    zc = RING_Z[i] - RING_H / 2 - 0.5 if i < 3 else zb                          # collar up to the ring band
    if zc > za: s = s.fuse(annulus(HUB_RI, COLLAR_RO, za, zc))
    if i == 0:
        s = s.fuse(box(-FLANGE / 2, FLANGE / 2, -FLANGE / 2, FLANGE / 2, za, zc).cut(cyl(HUB_RI, za, zc)))
        for x in (-40, 40):
            for y in (-40, 40):
                s = s.cut(cyl(2.25, za, zc, x, y)).cut(cyl(4.25, zc - 2.5, zc, x, y))
    if i < 3: s = s.cut(pinion_env(i)).cut(annulus(HUB_RI - 0.1, SPIG_R + 0.3, zb - SPIG_H, zb))   # window + spigot recess
    if i > 0: s = s.fuse(annulus(HUB_RI + 0.2, SPIG_R, za - SPIG_H, za))                            # spigot lip
    for k in range(3): s = s.cut(ear_slot(k))
    for a in ROD_POL:
        x, y = ROD_R * math.cos(math.radians(a)), ROD_R * math.sin(math.radians(a))
        s = s.cut(cyl(2.25, za - SPIG_H, zb, x, y))
        if i == 0: s = s.cut(box(x - 3.7, x + 3.7, y - 4.2, y + 4.2, za, za + 3.8))   # captive nut, S1 underside
        if i == 3: s = s.cut(cyl(5.0, zb - 5.0, zb, x, y))                             # top nut, S4
    for k in range(3):
        zm = sum(cradle_z(k)) / 2
        if za <= zm < zb:
            for a in J5_ANG:
                d = rz(Part.Vertex(j5_dir(a)), PIN_POLAR).Point
                s = s.cut(Part.makeCylinder(1.7, 20.0, V(0, 0, zm) + d * 37.0, d))
                s = s.cut(Part.makeCone(1.5, 3.2, 1.7, V(0, 0, zm) + d * (COLLAR_RO - 1.7), d))
    return s

def fixed_parts():
    p = {}
    p["segments"] = [segment(i) for i in range(4)]
    p["hub"] = p["segments"][0].fuse(p["segments"][1:])
    p["turn_servos"] = [turn_servo(k) for k in range(3)]
    p["cradles"] = [cradle(k) for k in range(3)]
    p["fasteners"] = Part.makeCompound(fixed_fasteners())
    p["all"] = [p["hub"], p["fasteners"]] + p["cradles"] + p["turn_servos"]
    return p

# ---------------- moving parts ----------------
def pinion(k, phi):
    """Turn pinion of ring k + its servo horn (J6): turns 2 x phi (internal gear, same direction as the ring)."""
    z = RING_Z[k]
    g = Part.makeCylinder(PIN_PR - 1.2, PIN_TH, V(0, 0, z - PIN_TH / 2))
    teeth = []
    for i in range(16):
        t = Part.makeBox(PIN_TIP - PIN_PR + 2.4, 3.2, PIN_TH, V(PIN_PR - 1.5, -1.6, z - PIN_TH / 2))
        t.rotate(V(0, 0, 0), V(0, 0, 1), i * 22.5); teeth.append(t)
    g = g.fuse(teeth)
    g = g.cut(Part.makeCylinder(3, PIN_TH, V(PIN_PR * 0.55, 0, z - PIN_TH / 2)))   # hole: shows the rotation
    hz = z + PIN_TH / 2 - 2.2 if SERVO_UP[k] else z - PIN_TH / 2                     # horn pocket on the servo side
    fz = z - PIN_TH / 2 if SERVO_UP[k] else z + PIN_TH / 2 - 2.4                    # centre screw pocket, far side
    g = g.cut(cyl(10.2, hz, hz + 2.2)).cut(cyl(2.7, fz, fz + 2.4)).cut(cyl(1.3, z - PIN_TH / 2, z + PIN_TH / 2))
    parts = [g, cyl(10.0, hz, hz + 2.2)]                                            # round horn (comes with the servo)
    for i in range(4):                                                              # 4 x M2x6 self-tapping through horn into the pinion
        a = math.radians(45 + 90 * i)
        parts.append(cyl(1.0, z - PIN_TH / 2 + 1.0, z + PIN_TH / 2 - 1.0, 7 * math.cos(a), 7 * math.sin(a)))
    parts.append(cyl(2.5, fz, fz + 2.0).fuse(cyl(1.25, z - PIN_TH / 2, z + PIN_TH / 2)))   # centre screw into the spline
    out = []
    for s in parts:
        s.rotate(V(0, 0, 0), V(0, 0, 1), 2.0 * phi); s.translate(V(PIN_C, 0, 0)); out.append(rz(s, PIN_POLAR))
    return Part.makeCompound(out)

def ring_shape(k, phi):
    zr = RING_Z[k]; z0, z1 = zr - RING_H / 2, zr + RING_H / 2
    r = annulus(RING_RI, RING_RO, z0, z1)
    for a in (90.0, 270.0):                                                        # lugs where the arms bolt on (J8)
        lug = Part.makeCylinder(LUG_RO, RING_H, V(0, 0, z0), V(0, 0, 1), 2 * LUG_HALF)
        lug.rotate(V(0, 0, 0), V(0, 0, 1), -LUG_HALF)
        lug = lug.cut(cyl(RING_RO - 0.5, z0, z1))
        lug = lug.cut(box(RING_RO - 0.6, LUG_RO + 0.1, -PAD_T - 0.2, PAD_T + 0.2, zr - BAR_T / 2 - 0.2, zr + BAR_T / 2 + 0.2))
        for t in (-LUG_SCREW_T, LUG_SCREW_T):
            lug = lug.cut(cyl(1.7, z0, z1, LUG_SCREW_R, t)).cut(box(LUG_SCREW_R - 3.0, LUG_SCREW_R + 3.0, t - 3.45, t + 3.45, z0, z0 + 2.8))
        r = r.fuse(rz(lug, a))
    r = r.cut(cyl(GEAR_RO, zr - PIN_TH / 2 - 1, z1))   # internal gear band, open to the top face (pinion drops in)
    teeth = []                                     # internal teeth over ~165 deg (90 deg of travel + the mesh)
    for i in range(32):
        t = Part.makeBox(GEAR_RO - GEAR_PR + 1.0, 3.2, PIN_TH, V(GEAR_PR + 0.4, -1.6, zr - PIN_TH / 2))
        t.rotate(V(0, 0, 0), V(0, 0, 1), PIN_POLAR - 130 + i * (360.0 / 64)); teeth.append(t)
    r = r.fuse(teeth)
    return rz(r, phi)

def switch(r0, z0, top_screws):
    """Mini micro-switch 12.8 x 6.5 x 5.8 beside the rail (t -17.8..-5) + 2 x M2x12 + nuts (J18)."""
    sw = box(r0, r0 + 6.5, -17.8, -5.0, z0, z0 + 5.8)
    f = []
    for t in (-14.6, -8.2):
        if top_screws:   # heads on the switch top, nuts under the shelf below it
            f.append(screw(V(r0 + 3.25, t, z0 + 5.8), V(0, 0, -1), 12, 2.0, 3.8, 1.5))
            f.append(hexnut(4.0, 1.6, r0 + 3.25, t, z0 - 4.6, 2.0))
        else:            # heads under the switch, nuts on the shelf above it
            f.append(screw(V(r0 + 3.25, t, z0), V(0, 0, 1), 12, 2.0, 3.8, 1.5))
            f.append(hexnut(4.0, 1.6, r0 + 3.25, t, z0 + 8.8, 2.0))
    return sw, f

def arm(k, cz, rho, with_stone):
    """One arm of ring k in local frame (radial = +X, all on the centre line t = 0), cup centre at height cz, spin rho.
    Layout rule: all 3 levels park at the same angle and turn the same way, so seen from the side (r, z) their parts
    must never overlap. Top rail r 80-88, bottom rail r 102-110; the middle arm goes out under the top rail, up between
    the rails, out over the bottom rail, then down to its cup. Returns (structure, [actuators], [fasteners], stone)."""
    zr = RING_Z[k]
    s, act, fas, holes = [], [], [], []
    def bar(r0, r1, z): s.append(box(r0, r1, -7, 7, z - BAR_T / 2, z + BAR_T / 2))
    s.append(box(RING_RO, LUG_RO, -PAD_T, PAD_T, zr - BAR_T / 2, zr + BAR_T / 2))   # pad in the ring lug
    for t in (-LUG_SCREW_T, LUG_SCREW_T):                                             # J8: 2 x M3x25 + nut in the lug
        holes.append(cyl(1.7, zr - BAR_T / 2, zr + BAR_T / 2, LUG_SCREW_R, t))
        fas.append(screw(V(LUG_SCREW_R, t, zr + RING_H / 2), V(0, 0, -1), 20.0, 3.0, 5.5, 3.0))
        fas.append(hexnut(5.5, 2.4, LUG_SCREW_R, t, zr - RING_H / 2 + 0.2, 3.0))
    if k == 0:                                          # bottom: rail r 104-112 (BR = 104), N20 under the screw
        z0, z1 = RAIL_Z[0]; b = BR - 102.0              # b: shift of the 2026-11-14 bottom slide (rail was r 102-110)
        bar(RING_RO, BR, zr)
        s.append(box(BR, BR + 8, -5, 5, z0, z1))
        s.append(box(BR, BR + 8, -5, SCREW_T + 4, z1, z1 + 4))          # top cap: bearing for the screw end (J12)
        holes.append(cyl(4.0, z1, z1 + 4, 106 + b, SCREW_T))
        act.append(annulus(2.0, 4.0, z1 + 0.5, z1 + 3.5).translated(V(106 + b, SCREW_T, 0)))
        act.append(cyl(SCREW_D / 2, z0 + 1, z1 + 4, 106 + b, SCREW_T))   # M4 lead screw
        act.append(cyl(4.0, z0, z0 + 6, 106 + b, SCREW_T))               # J11 coupler 3 -> 4
        n20 = box(101 + b, 111 + b, SCREW_T - 6, SCREW_T + 6, z0 - 24, z0)
        act.append(n20)
        s.append(box(99 + b, 113 + b, -1, 23, z0 - 12, z0).cut(n20))     # J10 N20 clamp under the rail
        for t in (1.0, 21.0):
            fas.append(screw(V(99 + b, t, z0 - 6), V(1, 0, 0), 16, 2.0, 3.8, 1.5))
            fas.append(box(114 + b, 115.6 + b, t - 2, t + 2, z0 - 8, z0 - 4))
        s.append(box(BR, BR + 8, -18, -1, z0 - 10.2, z0 - 7.2))          # switch shelf (joins the clamp)
        sw, f = switch(103 + b, z0 - 7.2, True); act.append(sw); fas += f
        s.append(box(BR + 8, BR + 16, -12, 12, cz - CAR_H / 2, cz + CAR_H / 2))
        s.append(box(105 + b, 111 + b, -16, -12, cz - 13, cz - 6))       # tab that presses the switch at cz 60
        blk = box(101 + b, 112 + b, SCREW_T - 5, SCREW_T + 5, cz - 6, cz + 8).cut(cyl(2.2, cz - 6, cz + 8, 106 + b, SCREW_T))
        s.append(blk.cut(hexnut(7.0, 3.4, 106 + b, SCREW_T, cz - 1.7)))  # nut block, J13 nut in a pocket
        fas.append(hexnut(7.0, 3.2, 106 + b, SCREW_T, cz - 1.6, 4.0))
        r_srv = BR + 16                                  # spin servo r 120-143, shaft 143-150 (shorter than top/middle)
    elif k == 2:                                        # top: rail r 76-84 (TR = 76), N20 above the screw
        z0, z1 = RAIL_Z[2]; b = TR - 80.0               # b: shift of the 2026-11-14 top slide (rail was r 80-88)
        bar(RING_RO, TR, zr)
        s.append(box(TR, TR + 8, -5, 5, z0, z1))
        s.append(box(TR, TR + 8, -5, SCREW_T + 4, z0, z0 + 4))          # bottom cap + bearing (middle bar passes under it)
        holes.append(cyl(4.0, z0, z0 + 4, 84 + b, SCREW_T))
        act.append(annulus(2.0, 4.0, z0 + 0.5, z0 + 3.5).translated(V(84 + b, SCREW_T, 0)))
        act.append(cyl(SCREW_D / 2, z0, z1 - 1, 84 + b, SCREW_T))
        act.append(cyl(4.0, z1 - 6, z1, 84 + b, SCREW_T))                # J11 coupler
        n20 = box(79 + b, 89 + b, SCREW_T - 6, SCREW_T + 6, z1, z1 + 24)
        act.append(n20)
        s.append(box(77 + b, 91 + b, -1, 23, z1, z1 + 12).cut(n20))      # J10 N20 clamp on the rail top
        for t in (1.0, 21.0):
            fas.append(screw(V(77 + b, t, z1 + 6), V(1, 0, 0), 16, 2.0, 3.8, 1.5))
            fas.append(box(92 + b, 93.6 + b, t - 2, t + 2, z1 + 4, z1 + 8))
        s.append(box(TR, TR + 8, -18, -1, z1 + 7.2, z1 + 10.2))          # switch shelf
        sw, f = switch(81 + b, z1 + 1.4, False); act.append(sw); fas += f
        s.append(box(TR + 8, 118, -12, 12, cz - CAR_H / 2, cz + CAR_H / 2))
        s.append(box(83 + b, 89 + b, -16, -12, cz + 6, cz + 13))         # tab that presses the switch at cz 290
        blk = box(79 + b, 90 + b, SCREW_T - 5, SCREW_T + 5, cz - 8, cz + 6).cut(cyl(2.2, cz - 8, cz + 6, 84 + b, SCREW_T))
        s.append(blk.cut(hexnut(7.0, 3.4, 84 + b, SCREW_T, cz - 1.7)))
        fas.append(hexnut(7.0, 3.2, 84 + b, SCREW_T, cz - 1.6, 4.0))
        r_srv = 118.0
    else:                                               # middle: fixed, stepped arm
        bar(RING_RO, 98, zr)
        s.append(box(92, 98, -7, 7, zr - BAR_T / 2, MID_OVER + BAR_T / 2))
        bar(92, 124, MID_OVER)
        s.append(box(118, 124, -12, 12, cz - CAR_H / 2, MID_OVER + BAR_T / 2))
        r_srv = 124.0
    sl, sw_, sh_ = SERVO
    act.append(box(r_srv, r_srv + sl, -sw_ / 2, sw_ / 2, cz - sh_ / 2, cz + sh_ / 2))   # spin servo (MG90S)
    act.append(box(r_srv + 3, r_srv + 6, -16, 16, cz - 1.2, cz + 1.2))                  # its mounting ears
    for t in (-1, 1):                                                                   # J14: tabs + 2 x M2x8
        s.append(box(r_srv - 2, r_srv + 3, 11 if t > 0 else -17, 17 if t > 0 else -11, cz - 5, cz + 5))
        fas.append(screw(V(r_srv + 6, t * 13.9, cz), V(-1, 0, 0), 8, 2.0, 3.8, 1.5))
    ra = r_srv + sl
    s.append(Part.makeCylinder(SHAFT_D / 2, CUP_R0 - ra, V(ra, 0, cz), V(1, 0, 0)))
    s.append(Part.makeCylinder(8.0, 2.0, V(ra, 0, cz), V(1, 0, 0)))                   # J15 cup adaptor flange on the horn
    for sg in (-1, 1):                                                                  # 2 x M2 into the horn (turn with rho)
        a = math.radians(rho)
        fas.append(Part.makeCylinder(1.0, 4.0, V(ra - 2, sg * 5 * math.cos(a), cz + sg * 5 * math.sin(a)), V(1, 0, 0)))
    cup = Part.makeCylinder(CUP_D / 2, CUP_R1 - CUP_R0, V(CUP_R0, 0, cz), V(1, 0, 0))
    cup.rotate(V(0, 0, cz), V(1, 0, 0), rho); s.append(cup)
    st = None
    if with_stone:
        sl, sw, sh = STONE
        st = Part.makeBox(sw, sl, sh, V(FACE, -sl / 2, cz - sh / 2))
        st.rotate(V(0, 0, cz), V(1, 0, 0), rho)
    struct = s[0].fuse(s[1:])
    if holes: struct = struct.cut(holes)
    return struct, act, fas, st

def level_full(k, st):
    """Ring k with both arms: (structure, actuators, fasteners, stones). Actuators include the turn pinion + horn."""
    struct, acts, fas, stones = [ring_shape(k, st["phi"])], [pinion(k, st["phi"])], [], []
    for u in (0, 1):
        m, a_, f_, s = arm(k, st["cz"], st["rho"], st["stone"])
        a = polar(u, st["phi"])
        struct.append(rz(m, a)); acts += [rz(x, a) for x in a_]; fas += [rz(x, a) for x in f_]
        if s: stones.append(rz(s, a))
    return struct[0].fuse(struct[1:]), Part.makeCompound(acts), Part.makeCompound(fas), stones

def level_parts(k, st):
    """(structure, actuators + fasteners, stones) - used by the animation and the checks."""
    m, a, f, ss = level_full(k, st)
    return m, Part.makeCompound([a, f]), ss

def level(k, st):
    """st = dict(phi, cz, rho, stone) for ring k (front and rear arms do the same). Returns mech, [stones]."""
    m, a, ss = level_parts(k, st)
    return Part.makeCompound([m, a]), ss

# ---------------- sequence ----------------
def sequence():
    S = [dict(phi=0.0, cz=Z_STACK[k], rho=0.0, stone=True) for k in range(3)]
    out = [("Both stacks held (base +10)", [dict(s) for s in S])]
    def go(label, k, key, a, b, step):
        n = max(1, int(round(abs(b - a) / step)))
        for i in range(1, n + 1):
            S[k][key] = a + (b - a) * i / n
            out.append((label, [dict(s) for s in S]))
    go("Unpinch: top +5, bottom -5", 2, "cz", Z_STACK[2], Z_STACK[2] + 5, 5); go("Unpinch: top +5, bottom -5", 0, "cz", Z_STACK[0], Z_STACK[0] - 5, 5)
    # middle
    go("1. Middle ring turns 90 (front -> left, rear -> right)", 1, "phi", 0, 90, 6)
    go("Middle stones spin upright", 1, "rho", 0, 90, 10)
    S[1]["stone"] = False; out.append(("Placed: 2 towers; cups vented", [dict(s) for s in S]))
    go("Middle arms spin back + turn home", 1, "rho", 90, 0, 15); go("Middle arms spin back + turn home", 1, "phi", 90, 0, 9)
    # top
    go("2. Top ring turns 90", 2, "phi", 0, 90, 6)
    go("Top carriages go down to 175", 2, "cz", Z_STACK[2] + 5, Z_SPIN, 10)
    go("Top stones spin upright", 2, "rho", 0, 90, 10)
    S[2]["stone"] = False; out.append(("Placed: 2 more towers; cups vented (stones drop 15 mm)", [dict(s) for s in S]))
    go("Top arms back home", 2, "rho", 90, 0, 15); go("Top arms back home", 2, "cz", Z_SPIN, Z_STACK[2], 20)
    go("Top arms back home", 2, "phi", 90, 0, 9)
    # bottom
    go("Bottom carriages rise +16 (stones clear the base plate)", 0, "cz", Z_STACK[0] - 5, Z_CLEAR, 8)
    go("3. Bottom ring turns 90", 0, "phi", 0, 90, 6)
    go("Bottom carriages rise to 175", 0, "cz", Z_CLEAR, Z_SPIN, 10)
    go("Bottom stones spin upright", 0, "rho", 0, 90, 10)
    go("Bottom carriages set the stones on the table", 0, "cz", Z_SPIN, Z_SET, 5)
    S[0]["stone"] = False; out.append(("Placed: 6 towers", [dict(s) for s in S]))
    go("Bottom arms back home", 0, "rho", 90, 0, 15); go("Bottom arms back home", 0, "cz", Z_SET, Z_STACK[0], 20)
    go("Bottom arms back home", 0, "phi", 90, 0, 9)
    return out

# ---------------- checks ----------------
def common_vol(a, b):
    """Overlap volume, solid by solid (compounds hold parts that touch or nest by design, e.g. a screw in its nut)."""
    if not a.BoundBox.intersect(b.BoundBox): return 0.0
    v = 0.0
    for sa in a.Solids:
        if not sa.BoundBox.intersect(b.BoundBox): continue
        for sb in b.Solids:
            if sa.BoundBox.intersect(sb.BoundBox): v += sa.common(sb).Volume
    return v

def hit(a, b, tol=1.0):
    return common_vol(a, b) > tol

def check(seq, fixed):
    fx = fixed["all"]
    bad, zmin, zmax, mzmax = [], 1e9, -1e9, -1e9
    for label, st in seq:
        L = [level(k, st[k]) for k in range(3)]
        for k in range(3):
            m, ss = L[k]
            mzmax = max(mzmax, m.BoundBox.ZMax)
            for f in fx:
                if hit(m, f): bad.append("%s: %s level hits a fixed part (hub, cradles, turn servos, fixed fasteners)" % (label, NAMES[k]))
            for s in ss:
                zmin = min(zmin, s.BoundBox.ZMin); zmax = max(zmax, s.BoundBox.ZMax)
                for f in fx:
                    if hit(s, f): bad.append("%s: %s stone hits a fixed part" % (label, NAMES[k]))
            for j in range(k + 1, 3):
                mj, sj = L[j]
                if hit(m, mj): bad.append("%s: %s / %s mechanisms" % (label, NAMES[k], NAMES[j]))
                for s in sj:
                    if hit(m, s): bad.append("%s: %s mechanism / %s stone" % (label, NAMES[k], NAMES[j]))
                for s in ss:
                    if hit(mj, s): bad.append("%s: %s mechanism / %s stone" % (label, NAMES[j], NAMES[k]))
                for a in ss:
                    for b in sj:
                        a2 = a.copy(); a2.scale(0.99, a2.BoundBox.Center); b2 = b.copy(); b2.scale(0.99, b2.BoundBox.Center)
                        if hit(a2, b2, 10.0): bad.append("%s: %s / %s stones" % (label, NAMES[k], NAMES[j]))
    return bad, zmin, zmax, mzmax

def check_fixed(fixed):
    """Fixed parts against each other (fasteners excluded: they sit in their holes by design)."""
    parts = [("S%d" % (i + 1), s) for i, s in enumerate(fixed["segments"])]
    parts += [("cradle " + NAMES[k], c) for k, c in enumerate(fixed["cradles"])]
    parts += [("turn servo " + NAMES[k], t) for k, t in enumerate(fixed["turn_servos"])]
    bad = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            if parts[i][0].startswith("S") and parts[j][0].startswith("S"):
                continue   # segments: spigot lip in recess, checked by construction
            if hit(parts[i][1], parts[j][1], 0.5): bad.append("%s / %s" % (parts[i][0], parts[j][0]))
    # fasteners vs servos (a screw must not go through a servo)
    for k, t in enumerate(fixed["turn_servos"]):
        if hit(fixed["fasteners"], t, 0.5): bad.append("fixed fasteners / turn servo " + NAMES[k])
    return bad

# fastener list (whole hub, both units) - keep in step with ../CONNECTIONS.md
BOM = [
    ("J2", "M4x16 button head ISO 7380 + nut", 4), ("J3", "M4 threaded rod 272 mm + 2 nuts", 3),
    ("J4", "M3x12 socket head + nut (inner servo ear)", 6), ("J5", "M3x25 countersunk + M3 insert (radial, cradle)", 6),
    ("J6", "MG996R round horn + 4 x M2x6 self-tapping + centre screw", 3), ("J8", "M3x20 socket head + nut (arm -> ring lug)", 12),
    ("J10", "M2x16 + nut (N20 clamp)", 8), ("J11", "coupler 3 -> 4 mm", 4), ("J12", "bearing 4 x 8 x 3 (screw end)", 4),
    ("J13", "M4 nut (lead nut, in the carriage)", 4), ("J14", "M2x8 self-tapping (MG90S ears)", 12),
    ("J15", "M2 self-tapping (cup adaptor -> horn)", 12), ("J18", "micro-switch + 2 x M2x12 + nuts", 4),
]

# ---------------- outputs ----------------
def save_doc(name, st, fixed):
    doc = App.newDocument(name)
    for i, s in enumerate(fixed["segments"]): doc.addObject("Part::Feature", "Hub_S%d" % (i + 1)).Shape = s
    doc.addObject("Part::Feature", "Fasteners_fixed").Shape = fixed["fasteners"]
    for k in range(3):
        doc.addObject("Part::Feature", "TurnServo_" + NAMES[k]).Shape = fixed["turn_servos"][k]
        doc.addObject("Part::Feature", "Cradle_" + NAMES[k]).Shape = fixed["cradles"][k]
        m, a, f, ss = level_full(k, st[k])
        doc.addObject("Part::Feature", "Level_" + NAMES[k]).Shape = m
        doc.addObject("Part::Feature", "Actuators_" + NAMES[k]).Shape = a
        doc.addObject("Part::Feature", "Fasteners_" + NAMES[k]).Shape = f
        for i, s in enumerate(ss):
            doc.addObject("Part::Feature", "Stone_%s_%s" % (NAMES[k], ("front", "rear")[i])).Shape = s
    doc.recompute(); path = os.path.join(OUT, name + ".FCStd"); doc.saveAs(path); App.closeDocument(doc.Name)
    return path

def main():
    fixed = fixed_parts()
    seq = sequence()
    poses = {"HUB_A_HOME": seq[0][1]}
    for label, st in seq:
        if label.startswith("Middle stones spin"): poses["HUB_A_1_MIDDLE"] = st
        if label.startswith("Top stones spin"): poses["HUB_A_2_TOP"] = st
        if label.startswith("Bottom stones spin"): poses["HUB_A_3_BOTTOM"] = st
    files = [save_doc(n, s, fixed) for n, s in poses.items()]
    badf = check_fixed(fixed)
    bad, zmin, zmax, mzmax = check(seq, fixed)
    L = ["Central hub - option A - report", ""]
    L.append("Hub Ø%.0f z %.0f-%.0f in 4 segments (joints z %s), 3 M4 tie rods; rings Ø%.0f x %.0f at z %s, lugs to r %.0f;"
             " top rail r 76-84, bottom rail r 104-112, middle arm over at z %.0f" %
             (2 * HUB_R, HUB_Z0, HUB_Z1, "/".join("%.1f" % z for z in SEG_Z[1:4]), 2 * RING_RO, RING_H,
              "/".join("%.0f" % z for z in RING_Z), LUG_RO, MID_OVER))
    L.append("Cup heights: stack %s, spin at %.0f; bottom rises to %.0f before its turn; slide travel bottom %.0f, top %.0f mm" %
             ("/".join("%.0f" % z for z in Z_STACK), Z_SPIN, Z_CLEAR, Z_SPIN - (Z_STACK[0] - 5), Z_STACK[2] + 5 - Z_SPIN))
    L.append("Actuators: 3 turn MG996R inside the hub (1 per ring, both units, 2:1 internal gear), 4 slides (N20 + M4 screw;"
             " top + bottom, front + rear), 6 spin MG90S, 6 pumps (off the hub, hoses through the bore), 4 limit switches")
    L.append("")
    L.append("Fixed parts against each other (segments, cradles, turn servos with ears, fixed fasteners): " +
             ("no clashes" if not badf else "%d clashes: %s" % (len(badf), "; ".join(badf))))
    L.append("Sequence check: %d steps, both units, every part (rings, lugs, arms, rails, carriages, servos, cups, stones,"
             " switches, fasteners; fixed: segments, cradles, turn servos, fixed fasteners)" % len(seq))
    L.append("  stones: lowest %.1f, highest %.1f mm; mechanism highest %.1f mm (limits 0 / 350 [GR F.3])" % (zmin, zmax, mzmax))
    if bad:
        seen = []
        for b in bad:
            if b not in seen: seen.append(b)
        L.append("  %d clashes:" % len(seen)); L += ["    " + b for b in seen[:80]]
    else:
        L.append("  no clashes")
    L.append("")
    L.append("Fasteners (whole hub, both units):")
    L += ["  %-4s %3d x %s" % (j, q, d) for j, d, q in BOM]
    L.append("")
    L += ["wrote " + os.path.relpath(f, ROOT) for f in files]
    L.append("base_330 check: fc/check_env_a.py; animation: fc/anim_a.py; sheet: fc/sheet_a.py")
    txt = "\n".join(L)
    open(os.path.join(ROOT, "hub_a_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)

if not os.environ.get("HUB_A_NO_MAIN"):
    main()
