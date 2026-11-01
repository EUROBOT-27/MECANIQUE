# v5_fc.py - CLAPETS MODULE v5: two modules with a clean interface (decision D-017).
#   MODULE A "clapets" (lift + 2 doors) is designed AROUND reserved space for MODULE B "tete" (suction head):
#     - lift (Two Trees Bluer V2 Y axis on end) moved 25 mm back: 58 mm of fixed depth for the head behind its rotating part
#     - door rods moved back (y 82): every door-unit part stays behind the head's rotating disc
#     - reserved: head fixed zone, head rest envelope (cups vertical), head turning disc R 140 (needs R 126)
#   MODULE B bolts on the plate front (1x M3 + the 4 wheel bolts): Ø8 shaft in 2x 608 35 mm apart, MG996R in the fixed
#     zone driving it with a 20T -> 30T gear pair (no belt), MDF carrier with 3 TPU cup stations (one cup per box),
#     tube holes + clip slots + a reserved passage for the tube slack loop (tubes not modelled).
# Run (headless): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" v5_fc.py   (~1 min)
# Output ../CAD_FC/: STEP/ (parts, MODULE_CLAPETS_V5.step, MODULE_A_CLAPETS.step, MODULE_B_TETE.step), STL/, DXF/,
#   MODULE_CLAPETS_V5.FCStd, report.txt (rest-pose collisions, both modules vs the reserved head space)
# Frame (mm): x right, y towards the stack, z up; z 0 = table. Base 300 x 300: x ±150, y -160..140 (y 140 = stack face).
import math
import os

import FreeCAD as App
import Import
import MeshPart
import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))


# =============================================================================================== parameters
class G:
    YF = BOX_Y0 = 140                                       # base front face = stack face (cups touch it)
    BASE_X, BASE_Y0 = 150, -160
    # ---- Two Trees Bluer V2 lift, 25 mm further back than v4 ----
    LIFT_DY = -25
    RAIL_W, RAIL_DX, RAIL_YC, RAIL_Z0, RAIL_L = 20, 40.45, 58.5 + LIFT_DY, 6, 350
    PL_GAP, PL_T = 3.3, 3.5
    PL_Y0 = RAIL_YC + RAIL_W / 2 + PL_GAP                   # butterfly plate rear 46.8, front 50.3
    PL_Y1 = PL_Y0 + PL_T
    PL_ZC = 150
    WH_X, WH_DZ = 60.0, 37.5
    WH_R, WH_W = WH_X - RAIL_DX - RAIL_W / 2, 10.2
    SPRING_U = SPRING_V = 85                                # corner holes (M4) -> door units
    CLAMP_V = 10                                            # centre holes (M3) -> nut support; the lower one also holds module B
    MOT_Z1, SHELF_T = 46, 6
    CPL_Z0, CPL_Z1, SCREW_Z0, SCREW_Z1 = 58, 83, 71, 363
    NUT_Z = 110
    TOP_Z0, TOP_Z1 = 344, 364
    LIFT_CARRY, LIFT_TURN = 15, 72
    BRG_R, BRG_T, BOSS_R = 11.05, 7.1, 14.5
    # ---- reserved space for module B (in the carriage frame) ----
    HZ = 175                                                # head axis along y at x 0, z 175
    RES_ROT_R, RES_ROT_Y0 = 140, 108.0                      # turning disc: R 140 (needs 126), from the carrier rear to the face
    RES_FIX = (-62, 62, PL_Y1, RES_ROT_Y0, 100, 200)       # fixed zone: bracket, bearings, drive (x0, x1, y0, y1, z0, z1)
    RES_CABLE = (-62, 62, PL_Y1, RES_ROT_Y0, 200, 230)     # tube passage above the bracket (slack loop for 90 deg + lift)
    RES_REST_X = 36                                         # rest envelope: cups vertical, x ±36 (doors fold in front of it)
    # ---- MODULE A: door units ----
    PX, PY = 132, 82                                        # door rod (right): behind the head's turning disc
    LOW, UP, PT = 30, 226, 6
    W_X0, W_X1 = 66, 94
    ROD_Z0, ROD_Z1 = 30, 233
    GM, GZ1, GZ2 = 1.25, 20, 28                             # 20T pinion (MG996R) -> 28T on the rod: x1.4 (longer arms)
    GC = GM * (GZ1 + GZ2) / 2                               # 30
    SVY = PY - GC                                           # door servo axis (132, 52)
    SV_L, SV_W, SV_H, SV_FL, SV_OUT, SV_HORN = 40.7, 19.7, 37.0, 26.6, 10.0, 43.5   # MG996R, CHECK
    SV_X1 = PX + SV_OUT
    SV_X0 = SV_X1 - SV_L
    SV_XC = (SV_X0 + SV_X1) / 2
    SV_BOT = LOW + PT + 13                                  # door servo stands on the bottom plate; flange above the plate lobe
    SV_FLZ = SV_BOT + SV_FL
    GZA = SV_BOT + SV_HORN
    GZB = GZA + 8                                           # door gears z 92.5..100.5 (28T reaches y 100.75 < 108)
    HORN_R, HORN_T = 10.5, 2.0
    SV_SLOT = 2
    PAD_X0, PAD_T = 160, 8
    SX0 = PAD_X0 + PAD_T
    SX1 = SX0 + 3
    SY0, SY1, TAB_Y0 = 141, 176, 128
    PAD_Y0, PAD_Y1 = 145, 175
    DZ0, DZ1 = 20, 265
    PADS_Z = ((35, 75), (145, 185), (225, 265))
    ARM1, ARM2 = (39, 49), (212, 222)
    FL1, FL2 = (37, 53), (206, 224)
    A_FOLD, A_CLAMP, A_OPEN = 90.0, 3.0, -35.0             # open -35: the whole door is behind the face (stack turns clear)
    NUT_W, NUT_L, NUT_T = 5.6, 6.4, 2.6
    # ---- MODULE B: suction head ----
    CUPS_Z = (77, 135, 240)                                 # one cup per box
    ST_R_RIM, ST_R_RING, ST_R_HOLE, ST_R_HUB = 25, 28, 20, 8
    ST_BOLT_R, ST_BOLT_A = 24, (30, 150, 270)
    HB_Y0, HB_Y1 = PL_Y1, 92.0                              # bearing tube; 608 at both ends (35 mm apart)
    HG_Y0, HG_Y1 = 94.5, 102.5                              # gear plane (head 30T on the shaft, 20T on the servo horn)
    HF_Y0, HF_Y1 = HG_Y1, 108.5                             # flange (same part as the 30T gear), split clamp on the shaft
    CA_Y0, CA_Y1 = HF_Y1, HF_Y1 + 6                         # MDF 6 carrier 108.5..114.5
    RIM_Y1, RING_Y1 = CA_Y1 + 3, CA_Y1 + 6
    TH_Y0, TH_Y1 = CA_Y1 - 3.3, 122.0
    CUP_Y0 = TH_Y1                                          # DP-S30 bellows Ø30, 18 mm -> face at y 140
    CA_Z0, CA_Z1 = CUPS_Z[0] - ST_R_RING, CUPS_Z[2] + ST_R_RING
    HGZ1, HGZ2 = 20, 30                                     # head gear pair x1.5: head 90 deg = servo 135 deg
    HGC = GM * (HGZ1 + HGZ2) / 2                            # 31.25
    HS_ANG = 45                                             # head servo axis 45 deg down-left of the head axis
    HS_X = -HGC * math.sin(math.radians(HS_ANG))            # (-22.1, 152.9): clear of the boss, the M3 heads and the ears
    HS_Z = HZ - HGC * math.cos(math.radians(HS_ANG))
    HS_HORN_Y = HG_Y0                                       # horn top (towards +y) = gear plane rear
    HS_BODY_Y0 = HS_HORN_Y - SV_HORN                        # body bottom 51.0 (0.7 mm off the plate)
