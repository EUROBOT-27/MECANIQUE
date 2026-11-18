# flipbar_params.py - single-bar stone flip (Maatoug, 2026-11-14): parameters + four-bar kinematics (plain Python).
#
# Derived from Ayoub's flip-6cups (mechanical/flip-6cups/): SAME four-bar (his synthesis, values copied below so a
# change there doesn't silently move this design). Changes:
#   - the 230 x 290 cup plate becomes ONE vertical aluminium bar with 3 cups on the stack's centre line (one per
#     stone), so every actuator point stays <= 350 mm during the flip (the rule applies to actuators even in the
#     castle, game rules E.1: "the actuators must respect the height limit at all times");
#   - each cup sits in the clapets-v8 TPU spring station (B_STATION_TPU, after Barbatronic CDR-2027) with a
#     Barbatronic-style printed SUPPORT RING around it: the bellows pulls the stone onto the ring rim (Ø62 annulus)
#     -> rigid seat, no sag, no sway; the TPU spring lets the cup tilt to seat on bent cardboard;
#   - the bar is one smooth outline (lobes around the stations, arm to the crank pin, filleted, lightening slots);
#   - drive: our NEMA 17 (17HS4401S) through ONE printed spur pair: 15T pinion -> 100T SECTOR gear on the crank
#     shaft, module 0.8 = 6.67:1 (no belts, no worm). A sector, because a full wheel that size would hit the base:
#     reversible, back-drivable, motor stays powered to hold;
#   - rigid frame: column + rear plate (both 5 mm aluminium) tied by 4 standoffs; crank on its own D8 shaft on two
#     608 bearings (one per plate); rocker ground axle = an M8 bolt through both plates; every moving joint has TWO
#     608 bearings in a printed hub bolted on a flat (laser-cut) link; bar pins = M8 bolts (2026-11-18);
#   - no ejector servos (release = vent valve of that cup: one tower at a time); 3 pumps + 3 vent valves.
#
# Frame (base_330, same as flip-6cups): X = wheel axis, Y = forward (mechanism on the +Y edge), Z = up,
# origin = robot centre on the table. The flip happens in the XZ plane.
# Plate (= bar) frame (u, v): origin = centre of the 3-stone stack, u along X and v along Z at the start pose.
import math

# ---------------------------------------------------------------- stones
STONE_L, STONE_W = 320.0, 110.0
STONE_M = 0.090                         # kg
END_GAP = 8.8                           # upright stones end 8.8 mm above the table (Ayoub's synthesis)
STONE_V = (-110.0, 0.0, 110.0)          # stone centres (one stack of 3)

# ---------------------------------------------------------------- four-bar (copied from flip6_params.py, 2026-11-14)
O1 = (-34.765, 50.434)                  # crank ground pivot (crank shaft)
O2 = (-97.175, 244.733)                 # rocker ground pivot
P1 = (-97.285, -48.499)                 # crank pin on the bar (bar frame)
P2 = (5.083, -28.904)                   # rocker pin on the bar (bar frame)
START = (0.0, 165.0, 0.0)               # bar pose (x, z, theta rad): stack resting on the table
END = (5.218, STONE_L / 2 + END_GAP, math.radians(90))

R1 = math.dist(O1, (START[0] + P1[0], START[1] + P1[1]))      # crank 91.0
R2 = math.dist(O2, (START[0] + P2[0], START[1] + P2[1]))      # rocker 149.2
COUPLER = math.dist(P1, P2)                                    # 104.2
GROUND = math.dist(O1, O2)                                     # 204.1

# ---------------------------------------------------------------- bar + cups (bar frame)
CUP_V = (-110.0, 0.0, 85.0)             # cup centres: bottom + middle at the stone centres, TOP 25 mm lower: its Ø62
                                        # support ring is the highest actuator point mid-flip (at 100 it reaches 353.7)
CUP_U = 0.0
CUP_D, CUP_BELLOWS, CUP_SQUEEZE = 30.0, 18.0, 3.0   # DP-S30 (assumed size): lip 3 mm proud of the support ring when free
LINK_W = 20.0                           # crank / rocker plate width
HUB_D = 30.0                            # link hubs holding two 608 (OD 22)

# cup station = clapets-v8 TPU spring disc (same part) + printed spacer under it + printed support ring over it
ST_R_RIM, ST_R_HOLE, ST_R_HUB = 25.0, 20.0, 8.0     # B_STATION_TPU (clapets-v8), unchanged: rim, spring zone, hub
ST_BOLT_R = 24.0                                    # 3 x M3 through ring + TPU rim + spacer, tapped in the bar
ST_BOLT_A = (90.0, 210.0, 330.0)                    # v8 uses 30/150/270: turned so no bolt sits next to the P2 pin
ST_R_OUT, ST_R_WALL = 31.0, 28.0                    # spacer + support ring Ø62, ring wall 3 mm (Barbatronic pot: Ø66)
SPACER_T = 10.0                                     # room behind the TPU hub for the cup's M5 elbow fitting
RIM_T, DISC_T, RING_FL = 3.0, 2.5, 3.0              # TPU rim, TPU spring disc, ring flange (clamps the rim)
HUB_BACK, HUB_FRONT = 3.0, 7.0                      # TPU hub: 3 mm back into the spacer bore, 7 mm in front of the rim
WINDOW_W = 10.0                                     # 3 round-ended windows in the ring wall (see the cup, lighter)

# bar outline: smooth union of these (signed-distance blend, fillets ~BLEND), then holes
LOBE_R = 33.0                           # lobe around each station (Ø62 + 2 mm ledge)
SPINE_R = 15.0                          # spine joining the lobes (30 wide before the blend)
ARM_R, ARM_TO = 14.0, (0.0, -75.0)      # arm from the crank pin P1 into the spine
BOSS_P1_R, BOSS_P2_R = 16.0, 13.0
BLEND = 18.0
BAR_HOLE_D = 30.0                       # hole under each station (lighter: the spacer bears on r 15..31; bolts keep 7.8 mm)
PIN_D = 8.0

# ---------------------------------------------------------------- Y layers (mm)
REAR = (85.0, 90.0)                     # rear plate, 5 mm aluminium (motor on its back face)
HOUSING_R = (90.0, 97.0)                # printed 608 housing on the rear plate front face (crank shaft)
GEAR = (98.0, 108.0)                    # gear layer: motor 15T pinion -> crank 100T sector
HOUSING_C = (118.0, 125.0)              # printed 608 housing on the column back face (crank shaft)
HOUSING_D = 34.0                        # housing Ø (608 OD 22 + 6 mm walls)
COL = (125.0, 130.0)                    # column, 5 mm aluminium
CRANK = (133.0, 139.0)                  # crank plate, 6 mm aluminium
CRANK_HUB = (139.0, 153.0)              # crank's P1 bearings: two 608 in a printed hub on the crank's FRONT face
ROCK = (150.0, 156.0)                   # rocker plate, 6 mm aluminium
ROCK_HUB = (136.0, 150.0)               # rocker bearings at O2 and P2: two 608 in a printed hub on the rocker's BACK face
BAR = (159.0, 164.0)                    # bar, 5 mm aluminium
Y_SPACER = (BAR[1], BAR[1] + SPACER_T)                       # 164 -> 174
Y_RIM = (Y_SPACER[1], Y_SPACER[1] + RIM_T)                    # TPU rim 174 -> 177 (spring disc 174 -> 176.5)
Y_HUB = (Y_RIM[0] - HUB_BACK, Y_RIM[0] + HUB_FRONT)           # TPU hub 171 -> 181
Y_RING = (Y_RIM[1], Y_RIM[1] + RING_FL)                       # support ring flange 177 -> 180, wall up to the seat
Y_SEAT = Y_HUB[1] + CUP_BELLOWS - CUP_SQUEEZE                 # 196: ring rim = stone face when held
Y_STATION = (BAR[1], Y_SEAT)
Y_STONE = Y_SEAT

# ---------------------------------------------------------------- drive: 17HS4401S + one spur pair (printed ABS)
MOTOR = dict(name="17HS4401S", body=42.3, length=40.0, flange_boss_d=22.0, flange_boss_h=2.0, shaft_d=5.0,
             shaft_l=24.0, holes=31.0, hold=0.40, rated_a=1.7, step_deg=1.8, inertia=54e-7)  # datasheet values: CHECK labels
DRIVER_A = 1.0                          # Ender board drivers (TMC2225 / HR4988) set to ~1 A
MOTOR_USABLE = 0.20                     # N.m usable while moving (~half of holding at ~1 A, <= 300 rpm)
MICROSTEPS = 16
GEAR_M = 0.8                            # module: m 1 would need a 90T sector (tip r 46) that sweeps 7 deg too low
Z_PINION, Z_WHEEL = 15, 100             # Z_WHEEL = teeth of the FULL circle; only a ~140 deg sector is made
STAGES = 1
RATIO = Z_WHEEL / Z_PINION              # 6.67
ETA_STAGE = 0.90                        # printed spur gear mesh, greased
ETA = ETA_STAGE ** STAGES
CD = GEAR_M * (Z_PINION + Z_WHEEL) / 2  # centre distance 46
GEAR_W = 10.0
BACKLASH = 0.10                         # mm, designed (circular)
PINION_ANG = 90.0                       # motor straight above the crank shaft: the sector sweeps the upper side,
                                        # its empty side faces the base plate
M_POS = (O1[0] + CD * math.cos(math.radians(PINION_ANG)), O1[1] + CD * math.sin(math.radians(PINION_ANG)))
SECTOR_MARGIN_TEETH = 2                 # spare teeth past each end of the travel (hard stop included)
SECTOR_HUB_D = 26.0                     # full hub disc on the crank shaft (clamp)
LEWIS_Y = {15: 0.289, 100: 0.446}       # Lewis form factors, 20 deg full depth
ABS_YIELD = 40.0                        # MPa (printed ABS, along the layers: use ~1/2)

# ---------------------------------------------------------------- frame
BASE_Z, BASE_T = 13.5, 5.0              # base_330 bottom 13.5 above the table, 5 mm plate
BASE_TOP = BASE_Z + BASE_T
FRAME_X = (min(O1[0], O2[0]) - 40.0, max(O1[0], O2[0]) + 45.0)   # column + rear plate outline (as flip-6cups)
FRAME_Z1 = O2[1] + 28.0
COLUMN_X1 = 52.0                        # the column is wider on +X: the upright-side switch (x ~19) and stop (x ~40) sit on it
STANDOFFS = ((-128.0, 52.0), (O1[0], 25.0), (-128.0, 262.0), (-2.0, 262.0))   # (x, z), M5 through Ø10 spacers;
# the low right one sits straight under the crank shaft, in the zone the sector never sweeps
SHAFT_D = 8.0
B608 = (8.0, 22.0, 7.0)                 # bore, OD, width

# ---------------------------------------------------------------- fasteners + printed-part fits (2026-11-17)
# From mechanical/design-principles.md (clapets v7 + its ABS coupons): sized for ABS, nuts in pockets, every fastener
# drawn and swept, printed zip-tie anchors.
BRG_SEAT_D, BRG_LEAD = 22.2, 0.6        # printed 608 seat Ø22.2 + 0.6 x 45 deg lead-in (ABS coupon 2026-11-12: good)
PLATE_BRG_HOLE = 15.0                   # shaft hole in the plates under a 608: holds the outer race (inner Ø ~19), clear of the inner race (Ø12)
M3_CLEAR, M3_TAP = 3.4, 2.5             # clearance hole (printed + alu), tap drill in the 5 mm aluminium
NUT3 = (6.0, 6.9, 2.8)                  # M3 nut pocket (nut 5.5 AF x 6.35 x 2.4): the v7 clamp pocket, the nut can't turn
HOUSING_EAR_R, HOUSING_EAR_W = 21.0, 12.0   # housing ears: M3 x 12 from the plate's outer face into a nut pocket open at the ear tip
HOUSING_NUT_FLOOR = 2.2                 # plastic between the plate and the nut
SHAFT_BORE = 8.2                        # printed clamp bore on a Ø8 shaft (v7 ROD_R 4.1): slides on, the clamp closes it
CLAMP_LUG = (4.0, 14.0, 12.0)           # sector split clamp (v7 split_clamp_z): lug from r 4 to r 14, 12 wide, M3 x 12 at r 9
PINION_BORE = 5.2                       # printed bore on the Ø5 motor shaft (ABS holes print ~0.2 small)
PINION_HUB_D = 20.0                     # pinion hub behind the teeth: M3 set screw on the shaft's flat + captive nut
PINION_HUB_Y = (90.6, 98.0)
PINION_SET_Y = 94.0
ANCHOR = (18.0, 8.0, 6.0)               # printed zip-tie anchor (L x W x H): M3 at 4.5, tie tunnel 4 x 2 at 10..14
HOSE_U = (36.0, 40.0, 44.0)             # hose of the bottom / middle / top cup: side by side down the bar's +u flank
BAR_ANCHORS = tuple((40.0, cv - 8.0, -90.0) for cv in CUP_V)   # (u, v, deg): one under each spacer slot, on a bar tab
ANCHOR_TAB_R = 6.5                      # bar tab under each anchor screw (blended into the lobe)
HOSE_END_V = CUP_V[0] - 27.0            # the 3 hoses leave the bar under the bottom anchor
VALVE_PORT = (104.3, 67.0, 69.3)        # middle vent valve, top face (x, y, z): the fixed end of the hose loop
REAR_ANCHORS = ((-95.0, 121.0, 90.0), (-95.0, 191.0, 90.0))  # (x, z, deg) on the rear plate back face: motor + switch cables

# ---------------------------------------------------------------- joints, flat links, small fixings (2026-11-18)
# The 4 points left open on 2026-11-17. Checked first with the pivots' swept clearances: the rocker never comes
# within 90 mm of O1, the crank never within 85 mm of P2 or 113 mm of O2, the bar never covers O2.
LINK_HUB_BODY_D = 28.4                  # printed bearing hub: Ø22.2 seat + 3.1 mm walls, 16 long (2 x 608 + lip)
LINK_HUB_LIP, LINK_HUB_LIP_BORE = 2.0, 16.5   # lip at the far end holds the outer race; a sleeve (Ø11.5) passes through it
LINK_HUB_TONGUE = (36.0, 4.0)           # tongue along the link (length from the pin, thickness), LINK_W wide
LINK_HUB_SCREWS = (18.0, 30.0)          # 2 x M3 x 10 from the tongue into M3 tapped in the 6 mm link (from the pin)
LINK_PIN_HOLE = 20.0                    # hole in the link under a hub: closes the seat on the 608's outer race (land Ø ~19.2),
                                        # and a 13 mm socket (Ø ~18) reaches the M8 nut / bolt head that sits inside it
SLEEVE_D = 11.5                         # printed sleeves on Ø8: touch the 608 inner race only (its OD ~12.1)
CRANK_CLAMP = (CRANK[1], CRANK[1] + 10.0)   # crank clamp hub on the crank's front face at O1 (split clamp on the shaft)
CRANK_CLAMP_D = 26.0
CRANK_CLAMP_SCREWS = (19.0, 31.0)       # 2 x M3 x 10 into M3 tapped in the crank, on the web side (the clamp's hinge side)
O2_TUBE_D = 14.0                        # printed tube on the O2 bolt between the two plates (a 5th standoff)
M4_CLEAR = 4.5
BRACKET_SCREW = 15.0                    # bracket screws: 15 mm from the corner on each leg
SWITCH_SCREW_X, SWITCH_SCREW_Z = -16.5, (5.0, -1.0)   # endstop PCB screws, switch frame (x radial, z away from the crank): CHECK the real PCB

# hard stops + switches on the column front, in the crank layer (crank angle past each end)
HOME_SWITCH_DEG, END_SWITCH_DEG = 26.0, 26.0   # switch body centre, angle past each end, at r 55: body 5.2 mm from the
                                               # crank edge at the end, 3.0 mm at the hard stop; the LEVER reaches the crank
STOP_R, STOP_PAST_DEG, STOP_D = 75.0, 3.0, 10.0  # rubber bumpers: the crank stops 3 deg past each end

# ---------------------------------------------------------------- vacuum
N_PUMPS = 3
PUMP_X0, PUMP_Y0 = 55.0, 50.0           # pump rack corner on the base: clear of the wheel (y < 45) and the column bracket (x < 50)
PUMP_D, PUMP_L = 31.8, 66.0
VALVE = (27.0, 14.0, 17.0)

# ---------------------------------------------------------------- masses (kg) for the torque check (refined from the CAD)
M_BAR_ASSY = 0.358                      # from the CAD (flipbar_fc.py, collision_report.txt, 2026-11-18): bar 180, M8 pins + nuts 44,
                                        # 3 stations x 38, station bolts + anchors + their screws 20, hoses 4
M_CRANK = 0.039                         # crank plate (COG mid-length); at P1: 2 x 608 + printed hub + its 2 screws:
M_CRANK_P1 = 0.042
M_ROCKER = 0.050                        # rocker plate (COG mid-length); at P2: 2 x 608 + hub + screws (the O2 set adds no torque):
M_ROCKER_P2 = 0.043
G = 9.81


# ---------------------------------------------------------------- moving outlines (bar frame), shared by check + CAD
def _smin(a, b, k):
    """Polynomial smooth minimum: union of two distance fields with a fillet of about k."""
    h = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return b + (a - b) * h - k * h * (1.0 - h)


def _sd_capsule(u, v, a, b, r):
    du, dv = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((u - a[0]) * du + (v - a[1]) * dv) / (du * du + dv * dv)))
    return math.hypot(u - a[0] - t * du, v - a[1] - t * dv) - r


def bar_sdf(u, v):
    d = _sd_capsule(u, v, (CUP_U, CUP_V[0]), (CUP_U, CUP_V[-1]), SPINE_R)
    for cv in CUP_V:
        d = _smin(d, math.hypot(u - CUP_U, v - cv) - LOBE_R, BLEND)
    d = _smin(d, _sd_capsule(u, v, P1, ARM_TO, ARM_R), BLEND)
    d = _smin(d, math.hypot(u - P1[0], v - P1[1]) - BOSS_P1_R, BLEND * 0.6)
    d = _smin(d, math.hypot(u - P2[0], v - P2[1]) - BOSS_P2_R, BLEND * 0.6)
    for au, av in anchor_screws(BAR_ANCHORS):                    # tabs for the hose anchors
        d = _smin(d, math.hypot(u - au, v - av) - ANCHOR_TAB_R, 6.0)
    return d


def _contour(f, u0, u1, v0, v1, h):
    """Marching squares: the longest closed iso-0 contour of f (inside < 0), as a list of (u, v)."""
    nu, nv = int((u1 - u0) / h) + 2, int((v1 - v0) / h) + 2
    val = [[f(u0 + i * h, v0 + j * h) for j in range(nv)] for i in range(nu)]

    def ep(e):
        k, i, j = e
        i2, j2 = (i + 1, j) if k == "h" else (i, j + 1)
        fa, fb = val[i][j], val[i2][j2]
        t = fa / (fa - fb)
        return (u0 + h * (i + t * (i2 - i)), v0 + h * (j + t * (j2 - j)))

    adj = {}

    def link(e1, e2):
        adj.setdefault(e1, []).append(e2)
        adj.setdefault(e2, []).append(e1)

    for i in range(nu - 1):
        for j in range(nv - 1):
            c = (val[i][j] < 0, val[i + 1][j] < 0, val[i + 1][j + 1] < 0, val[i][j + 1] < 0)   # bl br tr tl
            E = {"B": ("h", i, j), "R": ("v", i + 1, j), "T": ("h", i, j + 1), "L": ("v", i, j)}
            cross = [n for n, (p, q) in (("B", (0, 1)), ("R", (1, 2)), ("T", (2, 3)), ("L", (3, 0))) if c[p] != c[q]]
            if len(cross) == 2:
                link(E[cross[0]], E[cross[1]])
            elif len(cross) == 4:
                centre = (val[i][j] + val[i + 1][j] + val[i + 1][j + 1] + val[i][j + 1]) / 4 < 0
                if c[0] == centre:      # bl in the same state as the centre: cut off br and tl
                    link(E["B"], E["R"]); link(E["T"], E["L"])
                else:
                    link(E["L"], E["B"]); link(E["R"], E["T"])
    loops, seen = [], set()
    for e0 in adj:
        if e0 in seen:
            continue
        loop, prev, cur = [], None, e0
        while cur not in seen:
            seen.add(cur); loop.append(ep(cur))
            nxt = [n for n in adj[cur] if n != prev]
            prev, cur = cur, (nxt[0] if nxt else adj[cur][0])
        loops.append(loop)
    return max(loops, key=len)


def _resample(loop, step):
    out, acc = [loop[0]], 0.0
    for a, b in zip(loop, loop[1:] + loop[:1]):
        acc += math.dist(a, b)
        if acc >= step:
            out.append(b); acc = 0.0
    if math.dist(out[-1], out[0]) < step * 0.5:
        out.pop()
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(out, out[1:] + out[:1]))
    return out if area > 0 else out[::-1]                  # counter-clockwise


_OUTLINE = []


def bar_outline(step=2.0):
    """Smooth bar outline (bar frame, counter-clockwise), ~step mm between points. Cached."""
    if not _OUTLINE:
        us = [CUP_U, P1[0], P2[0], ARM_TO[0], BAR_ANCHORS[0][0]]
        vs = list(CUP_V) + [P1[1], P2[1]]
        m = LOBE_R + BLEND + 4
        loop = _contour(bar_sdf, min(us) - m, max(us) + m, min(vs) - m, max(vs) + m, 1.0)
        _OUTLINE.extend(_resample(loop, step))
    return list(_OUTLINE)


def anchor_screws(anchors):
    """Screw axis (x, z) of each zip-tie anchor: 4.5 mm along the anchor from its origin."""
    return [(x + 4.5 * math.cos(math.radians(a)), z + 4.5 * math.sin(math.radians(a))) for x, z, a in anchors]


def bar_holes():
    """Holes through the bar: ('circle', u, v, d) / ('slot', (u0, v0), (u1, v1), width)."""
    h = [("circle", P1[0], P1[1], PIN_D), ("circle", P2[0], P2[1], PIN_D)]
    for cv in CUP_V:
        h.append(("circle", CUP_U, cv, BAR_HOLE_D))
        for a in ST_BOLT_A:
            t = math.radians(a)
            h.append(("circle", CUP_U + ST_BOLT_R * math.cos(t), cv + ST_BOLT_R * math.sin(t), M3_TAP))   # M3 tapped
    for au, av in anchor_screws(BAR_ANCHORS):
        h.append(("circle", au, av, M3_TAP))                                                          # zip-tie anchors, M3 tapped
    L = math.dist(P1, ARM_TO)
    du, dv = (ARM_TO[0] - P1[0]) / L, (ARM_TO[1] - P1[1]) / L
    h.append(("slot", (P1[0] + du * 26, P1[1] + dv * 26), (P1[0] + du * (L - 42), P1[1] + dv * (L - 42)), 10.0))
    return h


LINK_BLEND, LINK_SLOT_W = 6.0, 7.0      # crank / rocker: hubs blended into the plate, lightening slot
_LINKS = {}


def link_outline(length, step=2.0):
    """Crank / rocker plate outline in its own frame (pivot at the origin, other pin at (length, 0)), CCW."""
    if length not in _LINKS:
        def f(u, v):
            d = _sd_capsule(u, v, (0.0, 0.0), (length, 0.0), LINK_W / 2)
            d = _smin(d, math.hypot(u, v) - HUB_D / 2, LINK_BLEND)
            return _smin(d, math.hypot(u - length, v) - HUB_D / 2, LINK_BLEND)
        _LINKS[length] = _resample(_contour(f, -HUB_D, length + HUB_D, -HUB_D, HUB_D, 0.5), step)
    return list(_LINKS[length])


def link_slot(length):
    """Lightening slot (start, end, width) between the hub / clamp screws of the two ends; None if too short (crank)."""
    s0, s1 = 40.0, length - 40.0
    return (s0, s1, LINK_SLOT_W) if s1 - s0 >= 15.0 else None


def hose_exit():
    """Bar-frame point (u, v) and y where the 3 hoses leave the bar."""
    return (HOSE_U[1], HOSE_END_V), BAR[1] + ANCHOR[2] + 2.0


def station_circles():
    """(u, v, r) of the parts sticking out of the bar front at each cup: spacer + support ring Ø62."""
    return [(CUP_U, cv, ST_R_OUT) for cv in CUP_V]


def actuator_points(n_arc=36):
    """Boundary points (u, v) of every moving actuator part (bar, stations, cups) for the height check."""
    pts = bar_outline()
    for u, v, r in station_circles():
        pts += [(u + r * math.cos(2 * math.pi * i / n_arc), v + r * math.sin(2 * math.pi * i / n_arc)) for i in range(n_arc)]
    return pts


def sector_span():
    """(b0, b1) deg, crank frame (P1 = 0 deg): the arc the sector's teeth must cover = the pinion's direction over the
    whole crank travel, hard stops included, + SECTOR_MARGIN_TEETH at each end."""
    a0, a1 = math.degrees(PHI0), math.degrees(PHI1)
    lo, hi = min(a0, a1) - STOP_PAST_DEG, max(a0, a1) + STOP_PAST_DEG
    m = SECTOR_MARGIN_TEETH * 360.0 / Z_WHEEL
    return (PINION_ANG - hi - m, PINION_ANG - lo + m)


def stone_corners():
    return [(su * STONE_L / 2, v + sv * STONE_W / 2) for v in STONE_V for su in (-1, 1) for sv in (-1, 1)]


def rot(u, v, t):
    c, s = math.cos(t), math.sin(t)
    return (u * c - v * s, u * s + v * c)


def to_world(pose, p):
    a, b = rot(p[0], p[1], pose[2])
    return (pose[0] + a, pose[1] + b)


def _circle_cross(c0, r0, c1, r1, prev):
    d = math.dist(c0, c1)
    if d > r0 + r1 or d < abs(r0 - r1) or d == 0:
        return None
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = math.sqrt(max(r0 * r0 - a * a, 0.0))
    ex, ez = (c1[0] - c0[0]) / d, (c1[1] - c0[1]) / d
    mx, mz = c0[0] + a * ex, c0[1] + a * ez
    s1, s2 = (mx - h * ez, mz + h * ex), (mx + h * ez, mz - h * ex)
    return s1 if math.dist(s1, prev) <= math.dist(s2, prev) else s2


PHI0 = math.atan2(START[1] + P1[1] - O1[1], START[0] + P1[0] - O1[0])
_e = to_world(END, P1)
PHI1 = math.atan2(_e[1] - O1[1], _e[0] - O1[0])
SWEEP = ((PHI1 - PHI0) + math.pi) % (2 * math.pi) - math.pi     # crank travel start -> end (rad; sign = direction)
_BASE_ANG = math.atan2(P2[1] - P1[1], P2[0] - P1[0])


def pose_at_phi(phi, prev_p2=None):
    """Bar pose for crank angle phi (rad, world). Branch: closest to prev_p2 (default: start). None if it can't close."""
    if prev_p2 is None:
        prev_p2 = to_world(START, P2)
    p1 = (O1[0] + R1 * math.cos(phi), O1[1] + R1 * math.sin(phi))
    p2 = _circle_cross(O2, R2, p1, COUPLER, prev_p2)
    if p2 is None:
        return None
    t = math.atan2(p2[1] - p1[1], p2[0] - p1[0]) - _BASE_ANG
    a, b = rot(P1[0], P1[1], t)
    return (p1[0] - a, p1[1] - b, t), p1, p2


def sweep_path(s0, s1, n):
    """Poses for crank progress s in [s0, s1] (s = 0 start, 1 upright; outside = over-travel), branch-continuous."""
    out, prev = [], to_world(START, P2)
    # walk from s = 0 to s0 first so the branch is the assembled one
    for s in [s0 * i / 50 for i in range(51)]:
        r = pose_at_phi(PHI0 + SWEEP * s, prev)
        if r:
            prev = r[2]
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n
        r = pose_at_phi(PHI0 + SWEEP * s, prev)
        if r is None:
            out.append((s, None))
            continue
        prev = r[2]
        out.append((s,) + r)
    return out


def pose_at(s):
    for item in sweep_path(0.0, s, max(2, int(abs(s) * 400))):
        last = item
    return last[1:] if last[1] is not None else None


def cog_world(pose, p1, p2, phi, with_stones=True):
    """[(mass, (x, z))] of the moving bodies: bar assembly (+ stones), crank, rocker (COG at mid-length)."""
    bodies = [(M_BAR_ASSY, to_world(pose, (0.0, -10.0)))]          # bar assembly COG a little below the stack centre
    if with_stones:
        bodies += [(STONE_M, to_world(pose, (0.0, v))) for v in STONE_V]
    bodies.append((M_CRANK, ((O1[0] + p1[0]) / 2, (O1[1] + p1[1]) / 2)))
    bodies.append((M_CRANK_P1, p1))
    bodies.append((M_ROCKER, ((O2[0] + p2[0]) / 2, (O2[1] + p2[1]) / 2)))
    bodies.append((M_ROCKER_P2, p2))
    return bodies


def potential(pose, p1, p2, phi, with_stones=True):
    return sum(m * G * c[1] / 1000.0 for m, c in cog_world(pose, p1, p2, phi, with_stones))


if __name__ == "__main__":
    print("crank %.1f rocker %.1f coupler %.1f ground %.1f, travel %.1f deg, ratio %.0f:1" % (
        R1, R2, COUPLER, GROUND, math.degrees(SWEEP), RATIO))
    print("Grashof: s + l = %.1f, p + q = %.1f -> %s" % (
        min(R1, R2, COUPLER, GROUND) + max(R1, R2, COUPLER, GROUND),
        sum(sorted((R1, R2, COUPLER, GROUND))[1:3]),
        "non-Grashof (no link turns fully)" if min(R1, R2, COUPLER, GROUND) + max(R1, R2, COUPLER, GROUND) >
        sum(sorted((R1, R2, COUPLER, GROUND))[1:3]) else "Grashof"))
    for s in (0, 0.5, 1):
        p = pose_at(s)
        print(s, [round(v, 2) for v in p[0][:2]], round(math.degrees(p[0][2]), 2))
    print("M", M_POS, "sector (crank frame)", sector_span())
