# Module B v1 "T1": turning plate that turns the WHOLE quarry stack 90 deg (D-028).
#
#   butterfly plate (module A's lift) -> printed bracket (4 wheel bolts) with a bearing housing (2 x 6002)
#   -> HOLLOW shaft (tube Ø15 x 1) -> printed hub (33T gear + flange + coupler clamp)
#   -> MDF 6 turning plate with 3 cups (one per stone, station S3)
#   MG996R (+ round horn) on the bracket drives the hub: 22T pinion -> 33T (x1.5: 90 deg plate = 135 deg servo).
#
# Pumps and valves stay in the robot (Seif, 2026-11-18). The 3 cup tubes run in front of the plate to its centre,
# go back THROUGH the hollow shaft (they only twist a little when the plate turns), come out at the back of the
# bearing housing, then up the bracket to the robot.
#
# The turn ("lift-turn"): the lift raises the stack while it turns so its low corner skims the table:
#   stack centre height c(t) = 160 sin t + 165 cos t + CLEAR  (table frame), t = 0 -> 90 deg.
#   Mid-turn the stack reaches ~465 mm: castle only (FAQ Q9 yes, D-028). The plate itself stays <= 350 mm:
#   that is why the cups are 85 mm apart vertically.
#
# Run (from suction-v1/):  freecadcmd fc/turn_t1.py            -> CAD_FC/turn/T1_S3/    (grab pose: lift 0, t = 0)
#                          ANGLE=90 freecadcmd fc/turn_t1.py   -> CAD_FC/turn/T1_S3_a90/ (static pose, end of turn)
#                          STATION=S1 freecadcmd fc/turn_t1.py -> CAD_FC/turn/T1_S1/    (rigid holders, same holes)
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import Part
import lib
from lib import V, box, ycyl, xcyl, solid, fuse, tube, screw, nut, spur_gear, hex_y
import params as P

# ------------------------------------------------------------------ main numbers
STATION = os.environ.get("STATION", "S3").upper()   # S3 (TPU + rigid ring, default) or S1 (rigid): same holes
HZ = lib.ZC[1]                     # turning axis z = middle stone centre at lift 0 (module 139 = table 165)
PITCH = 85.0                     # vertical cup pitch (stones 1 / 3 gripped 25 mm off their centre)
MID_U = 70.0                     # middle cup 70 mm to the side: the axis stays free for the tubes
CLEAR = 5.0                      # low stack corner above the table during the lift-turn
GM, ZP, ZG = 1.25, 22, 33        # gear module, pinion (servo), hub gear (x1.5; 22/33 keeps the pinion collar off the housing)
CD = GM * (ZP + ZG) / 2          # 34.4 centre distance
SERVO_Y0 = P.PL_Y1 + 0.5         # servo body bottom (0.5 off the plate face, through a window in the bracket)
SV_BOT_Z = -28.0                 # MG996R model: body bottom at model z -28 (lib.servo_mg996r)
SV_HORN, HORN_T, HORN_R = 47.4, 2.5, 10.4                  # measured horn disc top above the servo bottom (v7)
HORN_BOSS_R, HORN_BOSS_T, HORN_HOLE_R, HORN_SCR_R = 4.6, 0.8, 7.2, 1.25
HORN_TOP = SERVO_Y0 + SV_HORN    # 98.4
PX, PZ = 0.0, HZ - CD            # pinion axis: straight below the turning axis
BR_T = 6.0
YB = P.PL_Y1 + BR_T              # 56.5 bracket front face
# hollow shaft + bearings (6002-2RS 15 x 32 x 9, local)
SH_R, SH_RI = 7.5, 6.5           # tube Ø15 x 1 (copper plumbing pipe / aluminium / steel): Ø13 inside, 3 tubes Ø4 need 8.6
BRG_OD, BRG_W = 32.0, 9.0
BRG_SEAT = 16.05                 # press fit: Ø32.1 (+0.1, as the 608 seats of v7); confirm with an ABS coupon
Y_SH0 = 69.0                     # shaft rear end (tubes bend out behind it, R12, clear of module A's M4 heads)
Y_COL0, Y_COL1 = Y_SH0, Y_SH0 + 8.0          # rear coupler collar 69..77
Y_BR1 = Y_COL1                   # rear bearing 77..86
Y_BR2 = Y_BR1 + BRG_W + 2.0      # front bearing 88..97 (2 mm shoulder between them, part of the housing)
HOUS_R, Y_HOUS1 = 19.0, Y_BR2 + BRG_W
SHOULDER_R = 13.5                # shoulder touches the outer races only (6002 inner race Ø~20)
COL_R, SCR_OFF = 14.0, 10.2      # rear collar Ø28; clamp screws 10.2 off the axis (clear of the Ø15 shaft)
Y_G0 = HORN_TOP                  # gear plane (pinion on the horn, 33T on the hub)
Y_G1 = Y_G0 + 6.0
Y_F0, FL_T, FL_R = Y_G1 + 0.5, 4.0, 40.0     # hub flange behind the turning plate
YC_B = Y_F0 + FL_T               # turning plate back face
CAR_T = P.STATION["car_t"]
YF = YC_B + CAR_T                # turning plate front face (station frame y 0)
CLAMP_R, Y_CL1 = 16.0, YF + 8.0  # hub coupler clamp Ø32, through the plate centre, 8 mm in front of it
Y_SH1 = Y_CL1                    # shaft front end
TUBE_Y = 22.0                    # tubes cross the plate front at this height to reach the centre
# behind the shaft the 3 tubes fan out in the bracket plane: (direction from the shaft, x where they turn up)
TUBE_FAN = {"top": (50.0, 22.0), "mid": (0.0, 38.0), "bot": (-30.0, 50.0)}
Y_TUBE_BACK = 59.0               # ... and this y (in front of the bracket back plate)
Y_TUBE_EXIT = Y_SH0 - 12.0       # tubes bend out of the shaft end with R12 (57)
ANGLE = float(os.environ.get("ANGLE", "0"))


def lift_at(t_deg):
    t = math.radians(t_deg)
    return 160 * math.sin(t) + 165 * math.cos(t) + CLEAR - P.STONE_CZ_TABLE[1]


def at(u, v, y=0.0):
    """Turning-plate frame -> module frame at t = 0: u = x, v = z - HZ, y from the plate front face."""
    return V(u, YF + y, HZ + v)


def coupler(y0, y1, r_out, slot_dir, scr_off, scr_y, head_side, slot_from=None):
    """Coupler-style clamp (design-principles 2026-11-18): round hub r_out, slot through one side (slot_dir = -1: towards
    -z), M3 across the slot INSIDE the outline at scr_off from the axis; head counterbore on head_side (+1 / -1 in x),
    nut pocket on the other side. Returns (add, cut)."""
    sf = y0 if slot_from is None else slot_from
    zc = HZ + slot_dir * scr_off
    half = math.sqrt(r_out ** 2 - scr_off ** 2)
    cut = [box(-0.6, 0.6, sf, y1 + 1, min(HZ, HZ + slot_dir * (r_out + 1)), max(HZ, HZ + slot_dir * (r_out + 1))),
           xcyl(1.7, -half - 1, half + 1, scr_y, zc)]
    h0 = 4.0                                                   # counterbore / pocket start (from the slot plane)
    if head_side > 0:
        cut += [xcyl(3.1, h0, half + 1, scr_y, zc), box(-half - 1, -h0 + 0.5, scr_y - 2.95, scr_y + 2.95, zc - 3.4, zc + 3.4)]
    else:
        cut += [xcyl(3.1, -half - 1, -h0, scr_y, zc), box(h0 - 0.5, half + 1, scr_y - 2.95, scr_y + 2.95, zc - 3.4, zc + 3.4)]
    return [ycyl(r_out, y0, y1, 0, HZ)], cut


# ------------------------------------------------------------------ fixed side (rides the lift, does not turn)
def servo():
    raw = lib.servo_mg996r()
    d = os.path.join(lib.HERE, "..", "..", "resources", "mg996r-servo-3.snapshot.9")
    horn = Part.read(os.path.join(d, "mg996_arm_round.step"))
    horn.translate(V(0, 0, SV_HORN - HORN_T - 28))                    # seated on the spline (as clapets v7)
    sv = Part.makeCompound(raw.Solids + horn.Solids)
    # model (x, y, z) -> module (PX + x, SERVO_Y0 - SV_BOT_Z + z, PZ - y): shaft along +y, body on the plate
    sv.transformShape(App.Matrix(1, 0, 0, PX, 0, 0, 1, SERVO_Y0 - SV_BOT_Z, 0, -1, 0, PZ, 0, 0, 0, 1))
    e = sv.common(box(PX + 10.6, PX + 18.0, YB, Y_G0 - 5, PZ - 15, PZ + 15))
    ear_y = e.BoundBox.YMin                                           # ear underside = post top
    ear_x = [PX - 30.2 - 4.55, PX + 10.2 + 4.55]                      # MG996R ear holes 49.5 apart
    return sv, ear_y, ear_x


def back_tube_path(key):
    """Fixed part of a cup tube: shaft end -> bend out -> fan out in the bracket plane -> up to the robot."""
    b = math.radians(BUNDLE[key])
    ox, oz = 2.31 * math.cos(b), HZ + 2.31 * math.sin(b)
    fa, xk = TUBE_FAN[key]
    c2 = V(xk, Y_TUBE_BACK, oz + (xk - ox) * math.tan(math.radians(fa)))
    return [V(ox, Y_SH0 + 12, oz), V(ox, Y_TUBE_EXIT, oz), c2, V(xk, Y_TUBE_BACK, 230)]


def bracket(ear_y, ear_x):
    add = [box(-52, 52, P.PL_Y1, YB, 88, 200)]
    for s in (1, -1):
        for bz in lib.BOLT_Z:
            add.append(box(min(s * 52, s * 65.5), max(s * 52, s * 65.5), P.PL_Y1, YB, bz - 8, bz + 8))
    add.append(ycyl(HOUS_R, P.PL_Y1, Y_HOUS1, 0, HZ))                                  # bearing housing
    add.append(box(-3, 3, YB - 0.01, Y_HOUS1 - 8, HZ + HOUS_R - 2, 198))               # top web
    for ex in ear_x:                                                                    # servo posts (0.4 off the body)
        x0, x1 = (ex - 3.8, PX - 30.6) if ex < PX else (PX + 10.6, ex + 3.8)
        add.append(box(x0, x1, YB - 0.01, ear_y, PZ - 11, PZ + 11))
    add.append(box(-15, 15, YB - 0.01, YB + 8, 188, 200))                               # wire tie block (servo cable)
    x0, x1 = 17.0, 54.5
    add += [box(x0, x0 + 2, YB - 0.01, YB + 8.5, 185, 195), box(x1 - 2, x1, YB - 0.01, YB + 8.5, 185, 195),
            box(x0, x1, YB + 6, YB + 8.5, 185, 195)]                                   # tube clip (bridge over the 3 tubes)
    cut = [ycyl(BRG_SEAT, P.PL_Y1 - 1, Y_BR1 + BRG_W, 0, HZ),                           # rear bearing from the back + cavity
           ycyl(BRG_SEAT, Y_BR2, Y_HOUS1 + 1, 0, HZ),                                    # front bearing from the front
           Part.makeCone(BRG_SEAT, BRG_SEAT + 0.6, 0.61, V(0, Y_HOUS1 - 0.6, HZ), V(0, 1, 0)),
           ycyl(SHOULDER_R, Y_BR1, Y_BR2 + 0.1, 0, HZ),                                  # shoulder: outer races only
           box(-5, HOUS_R + 1, Y_TUBE_EXIT - 3.0, Y_TUBE_BACK + 3.5, HZ - 14, HZ + 18),  # tube exit window (right)
           xcyl(3.6, 0, HOUS_R + 1, (Y_COL0 + Y_COL1) / 2, HZ - SCR_OFF),                     # key access: rear collar screw
           box(PX - 31.2, PX + 11.2, P.PL_Y1 - 1, YB + 1, PZ - 10.9, PZ + 10.9),          # servo body window
           box(PX + 10, PX + 25, P.PL_Y1 - 1, YB + 1, PZ - 5, PZ + 4),                     # servo wire exit
           box(-16, 16, YB + 2, YB + 6, 192, 196)]                                       # zip-tie tunnel (servo cable)
    cut += lib.plate_head_pockets()
    for key in TUBE_FAN:                                                                # tube guide grooves (Ø6)
        cut.append(tube(back_tube_path(key), P.TUBE["r_min_static"], od=6.0)[0])
    for s in (1, -1):
        for bz in lib.BOLT_Z:
            cut.append(ycyl(P.M5_CLEAR / 2, P.PL_Y1 - 1, YB + 1, s * 60, bz))
    for ex in ear_x:
        for dz in (-5.0, 5.0):
            cut += [ycyl(P.INS3["hole"] / 2, ear_y - P.INS3["depth"], ear_y + 0.01, ex, PZ + dz),
                    Part.makeCone(P.INS3["cone_d"] / 2, P.INS3["hole"] / 2, P.INS3["cone_h"], V(ex, ear_y, PZ + dz), V(0, -1, 0))]
    return solid(add, cut)


def pinion():
    """22T on the round horn: teeth from the horn disc top forward, plus a plain collar AROUND the horn disc that
    centres the pinion on the horn (as the v7 door pinion)."""
    a = [spur_gear(ZP, GM, Y_G0, Y_G1, 0, PX, PZ, 90.0), ycyl(HORN_R + 3.0, Y_G0 - HORN_T, Y_G0 + 0.01, PX, PZ)]
    c = [ycyl(HORN_R + 0.3, Y_G0 - HORN_T - 1, Y_G0, PX, PZ),                                   # horn disc pocket
         ycyl(HORN_BOSS_R + 0.3, Y_G0 - 1, Y_G0 + HORN_BOSS_T + 0.5, PX, PZ),                   # horn centre boss
         ycyl(3.2, Y_G0 - 1, Y_G1 + 1, PX, PZ)]                                                 # horn screw + key
    for k in range(4):
        a_ = math.pi / 2 * k
        x, z = PX + HORN_HOLE_R * math.cos(a_), PZ + HORN_HOLE_R * math.sin(a_)
        c += [ycyl(HORN_SCR_R, Y_G0 - 1, Y_G1 + 1, x, z), ycyl(2.2, Y_G1 - 1.5, Y_G1 + 1, x, z)]
    return solid(a, c)


def rear_collar():
    add, cut = coupler(Y_COL0, Y_COL1 - 0.45, COL_R, -1, SCR_OFF, (Y_COL0 + Y_COL1) / 2, +1)
    add.append(ycyl(9.8, Y_COL1 - 0.5, Y_COL1, 0, HZ))                    # touches the inner race only
    cut.append(ycyl(SH_R + 0.05, Y_COL0 - 1, Y_COL1 + 1, 0, HZ))
    return solid(add, cut)


# ------------------------------------------------------------------ turning side
# tube direction of each station (alpha) and its position (u, v); screws behind the plate stay >= 44 from the axis
ST = {"top": (270.0, 0.0, PITCH), "mid": (180.0, MID_U, 0.0), "bot": (90.0, 0.0, -PITCH)}
CAR_SCREW_R, CAR_SCREW_A = 36.0, (90.0, 180.0, 270.0)
BUNDLE = {"top": 150.0, "mid": 30.0, "bot": 270.0}     # place of each tube in the 3-tube bundle inside the shaft


def hub():
    a = [ycyl(9.8, Y_HOUS1 + 0.05, Y_G0 + 0.01, 0, HZ),                                    # boss on the front inner race
         spur_gear(ZG, GM, Y_G0, Y_G1, 0, 0, HZ, -90.0 + 180.0 / ZG),
         ycyl(13.0, Y_G1 - 0.01, Y_F0 + 0.01, 0, HZ),
         ycyl(FL_R, Y_F0, YC_B, 0, HZ)]
    ca, cc = coupler(YC_B - 0.01, Y_CL1, CLAMP_R, -1, SCR_OFF, YF + 4.0, -1, slot_from=YC_B + 1.5)
    a += ca
    c = cc + [ycyl(SH_R + 0.05, Y_HOUS1 - 1, Y_CL1 + 1, 0, HZ)]                            # shaft bore (through)
    for ang in CAR_SCREW_A:                                                                # plate screws, nuts at the back
        x, z = CAR_SCREW_R * math.cos(math.radians(ang)), HZ + CAR_SCREW_R * math.sin(math.radians(ang))
        c += [ycyl(1.7, Y_F0 - 1, YC_B + 1, x, z), hex_y(5.5 + 0.4, Y_F0 - 0.01, Y_F0 + 2.6, x, z)]
    return solid(a, c)


def outline():
    core = fuse([box(-42, 42, YC_B, YF, HZ - PITCH, HZ + PITCH),
                 ycyl(42, YC_B, YF, 0, HZ + PITCH), ycyl(42, YC_B, YF, 0, HZ - PITCH)])
    mid = fuse([box(0, MID_U, YC_B, YF, HZ - 42, HZ + 42), ycyl(42, YC_B, YF, MID_U, HZ)])
    return fuse([core, mid])


def env(shapes):
    """Highest / lowest point above the table during the lift-turn (math on every vertex, no sweep)."""
    top, low = -1e9, 1e9
    for sh in shapes:
        pts = sh.tessellate(1.0)[0] if sh.Faces else [v.Point for v in sh.Vertexes]
        for p in pts:
            A, B = 160 + p.x, 165 + (p.z - HZ)
            cands = [0.0, math.pi / 2]
            ts = math.atan2(A, B)
            if 0 < ts < math.pi / 2:
                cands.append(ts)
            hs = [CLEAR + A * math.sin(t) + B * math.cos(t) for t in cands]
            top, low = max(top, max(hs)), min(low, min(hs))
    return round(top, 1), round(low, 1)


def build():
    st, sinfo = lib.load_station(STATION)
    fixed, turn, cuts = [], [], []

    # ---- fixed side
    sv, ear_y, ear_x = servo()
    fixed += [("T1_BRACKET", bracket(ear_y, ear_x), "print"), ("T1_PINION_22T", pinion(), "print"),
              ("REF_MG996R_HORN", sv, "bought")]
    for y0, nm in ((Y_BR1, "REAR"), (Y_BR2, "FRONT")):
        fixed.append(("REF_6002_" + nm, ycyl(BRG_OD / 2, y0, y0 + BRG_W, 0, HZ).cut(ycyl(SH_R, y0 - 1, y0 + BRG_W + 1, 0, HZ)), "bought"))
    for s in (1, -1):
        for bz in lib.BOLT_Z:
            tag = "%s%d" % ("R" if s > 0 else "L", int(bz))
            fixed += [("FIX_M5x35_" + tag, screw(V(s * 60, P.PL_Y0 - 10.5, bz), V(0, 1, 0), 35, 5), "fastener"),
                      ("FIX_NYLOC_M5_" + tag, nut(V(s * 60, YB, bz), V(0, 1, 0), 5), "fastener")]
    for i, ex in enumerate(ear_x):
        for dz in (-5.0, 5.0):
            fixed.append(("FIX_M3x8_SERVO_%d%s" % (i + 1, "a" if dz < 0 else "b"), screw(V(ex, ear_y + 2.5, PZ + dz), V(0, -1, 0), 8, 3), "fastener"))

    # ---- turning side: shaft, collar, hub, plate, stations
    turn.append(("REF_SHAFT_TUBE_15x1x%d" % round(Y_SH1 - Y_SH0), ycyl(SH_R, Y_SH0, Y_SH1, 0, HZ).cut(ycyl(SH_RI, Y_SH0 - 1, Y_SH1 + 1, 0, HZ)), "bought"))
    turn.append(("T1_REAR_COLLAR", rear_collar(), "print"))
    turn.append(("FIX_M3x12_REAR_COLLAR", screw(V(4.0, (Y_COL0 + Y_COL1) / 2, HZ - SCR_OFF), V(-1, 0, 0), 12, 3), "fastener"))
    turn.append(("T1_HUB_33T", hub(), "print"))
    turn.append(("FIX_M3x14_HUB_CLAMP", screw(V(-4.0, YF + 4.0, HZ - SCR_OFF), V(1, 0, 0), 14, 3), "fastener"))
    ports = {}
    for key, (a, u, v) in ST.items():
        pt = at(u, v)
        sp, port, d = lib.put_station(st, sinfo, key.upper(), a, pt)
        turn += sp
        ports[key] = (port, d)
        cuts += lib.station_cuts(a, pt)
    for k, ang in enumerate(CAR_SCREW_A):
        x, z = CAR_SCREW_R * math.cos(math.radians(ang)), HZ + CAR_SCREW_R * math.sin(math.radians(ang))
        cuts.append(ycyl(1.7, YC_B - 1, YF + 1, x, z))
        turn.append(("FIX_M3x10_PLATE_%d" % (k + 1), screw(V(x, YF, z), V(0, -1, 0), 10, 3), "fastener"))
    cuts.append(ycyl(CLAMP_R + 0.5, YC_B - 1, YF + 1, 0, HZ))                             # hub clamp through the plate
    plate = solid([outline()], cuts)
    turn.insert(4, ("T1_TURN_PLATE_MDF6", plate, "mdf"))

    # ---- tubes: cup -> centre of the plate -> through the shaft -> out of the housing -> up the bracket
    r_b, s_str, R = 2.31, P.TUBE["straight_after_fitting"], P.TUBE["r_min_static"]
    tubes_turn, tubes_fixed = [], []
    for k, key in enumerate(("top", "mid", "bot")):
        port, d = ports[key]
        b = math.radians(BUNDLE[key])
        ox, oz = r_b * math.cos(b), HZ + r_b * math.sin(b)
        p1 = port + d * s_str
        yt = YF + TUBE_Y
        if key == "mid":
            front = [port, p1, V(ox, yt, oz)]
        else:
            sgn = 1 if key == "top" else -1
            front = [port, p1, V(ox, yt, HZ + sgn * 30), V(ox, yt, oz)]
        tb_t, L1, r1 = tube(front + [V(ox, Y_SH0 + 12, oz)], R)                                   # turns with the plate
        tb_f, L2, r2 = tube(back_tube_path(key), R)
        tubes_turn.append(("REF_TUBE_%s_PLATE" % key.upper(), tb_t, L1, r1))
        tubes_fixed.append(("REF_TUBE_%s_TO_ROBOT" % key.upper(), tb_f, L2, r2))
    turn += [(n, s, "bought") for n, s, _, _ in tubes_turn]
    fixed += [(n, s, "bought") for n, s, _, _ in tubes_fixed]

    # held stack (reference): face on the squashed cups
    y_face = YF + sinfo["stone_face_y_held"]
    stack = [("REF_STONE_%d" % (k + 1), box(-P.STONE_L / 2, P.STONE_L / 2, y_face, y_face + P.STONE_W,
                                              -P.MODULE_Z + P.STONE_H * k, -P.MODULE_Z + P.STONE_H * (k + 1)), "ref") for k in range(3)]

    top_turn, low_turn = env([s for n, s, k in turn])
    lift_peak = lift_at(math.degrees(math.atan2(160, 165)))
    fixed_top = max(s.BoundBox.ZMax for n, s, k in fixed if not n.startswith("REF_TUBE"))
    pb = plate.BoundBox

    # ---- pose
    lift = lift_at(ANGLE) if "ANGLE" in os.environ else 0.0
    out = []
    for n, s, k in fixed:
        s = s.copy()
        if n == "T1_PINION_22T":                                     # pinion turns the other way, x1.5
            s.rotate(V(PX, 0, PZ), V(0, 1, 0), ANGLE * ZG / ZP)
        s.translate(V(0, 0, lift)); out.append((n, s, k))
    for n, s, k in turn + stack:
        s = s.copy(); s.rotate(V(0, 0, HZ), V(0, 1, 0), -ANGLE); s.translate(V(0, 0, lift)); out.append((n, s, k))
    pl = lib.plate_ref(); pl.translate(V(0, 0, lift))
    out.append(("REF_BUTTERFLY_PLATE", pl, "ref"))

    info = dict(title="T1 turning plate: turns the whole stack 90 deg (pose: turn %.0f deg, lift %.1f)" % (ANGLE, lift),
                station="%s (TPU disc + support ring)" % STATION,
                cups="3 x DP-S30, one per stone: (x, table z at lift 0) = (0, %.0f), (%.0f, 165), (0, %.0f)" % (165 - PITCH, MID_U, 165 + PITCH),
                turning_axis="x 0, table %.0f at lift 0 (= middle stone centre)" % (HZ + P.MODULE_Z),
                drive="MG996R + round horn, 22T -> 33T m%.2f (90 deg plate = 135 deg servo)" % GM,
                joint="hollow shaft: tube Ø15 x 1 x %.0f (copper / alu / steel) in 2 x 6002-2RS; hub + rear collar = coupler clamps" % (Y_SH1 - Y_SH0),
                pneumatics="pumps + valves in the robot; 3 tubes Ø4 through the hollow shaft",
                plate_front_y=round(YF, 1), stack_face_y=round(y_face, 1),
                stack_face_vs_layout_v1="%+.1f mm (layout-v1 stack face y %.0f)" % (y_face - P.STACK_FACE_Y, P.STACK_FACE_Y),
                turn_plate_size="%.0f x %.0f (MDF 6)" % (pb.XLength, pb.ZLength),
                lift_turn="lift = 160 sin t + 165 cos t + %.0f - 165: 5 at t 0, peak %.1f at t 44 deg, 0 at t 90" % (CLEAR, lift_peak),
                turning_parts_max_height=top_turn, turning_parts_min_height=low_turn,
                fixed_parts_top_at_peak_lift=round(fixed_top + P.MODULE_Z + lift_peak, 1),
                stack_top_mid_turn=round(2 * math.hypot(160, 165) + CLEAR, 1),
                tubes_on_plate={n: "%.0f mm, min bend R%.1f" % (L, r) for n, _, L, r in tubes_turn},
                tubes_to_robot={n: "%.0f mm to z %.0f, min bend R%.1f" % (L, 230, r) for n, _, L, r in tubes_fixed},
                fits="A+B front (|x| <= 65.5 at the plate, door units from 66) and B alone (back)")
    notes = ["Tubes: in the shaft they turn with the plate; behind it they are held still: the bundle twists 90 deg over "
             "~25 mm (Ø4 PU, fine). In the 90 deg pose the two tube parts don't line up (that twist).",
             "Height: every turning part stays <= 350 during the lift-turn (turning_parts_max_height). The STACK passes "
             "350 mid-turn: castle only (Q9 yes, D-028).",
             "Assembly (before the bracket goes on the butterfly plate): rear 6002 from the back, front 6002 from the "
             "front; shaft from the front through both; rear collar on from the back (M3 x 12, key through the side "
             "hole); hub on the front end (nuts in its 3 pockets first), clamp M3 x 14 from the left; tubes pushed through "
             "the shaft; then the bracket on the 4 wheel bolts; servo + pinion; plate with its stations to the hub flange.",
             "Doors (A+B): open before turning.",
             "Middle cup 70 mm to the right of the stone centre; top / bottom cups 25 mm off their stone centre."]
    return out, info, notes


if lib.is_main(__file__):
    parts, info, notes = build()
    lib.save("T1_%s" % STATION + ("_a%d" % int(ANGLE) if "ANGLE" in os.environ else ""), "turn", parts, info, notes,
             files="ANGLE" not in os.environ)
