# Module B (suction-v1) shared parameters. Plain Python, no FreeCAD import: every generator reads it.
# Frame = clapets v7 module frame (so module A and B line up):
#   X = across the robot face (left/right), Y = forward (out of the module, towards the stone), Z = up.
#   z = 0 at the bottom of module A's socle. The socle sits on the robot floor: table z = module z + MODULE_Z.
# Values marked DATASHEET come from seller drawings / datasheets (2026-11-18): replace with caliper values.

# ---------------------------------------------------------------- module A interface (from clapets-v7/fc/v7_fc.py)
MODULE_Z = 26.0              # socle bottom above the table (layout-v1: floor plate top at 26)
PL_ZC = 150.0                # butterfly plate centre z at lift 0 (module frame)
PL_Y0, PL_T = 47.5, 3.0      # plate back face y, thickness -> front face PL_Y1
PL_Y1 = PL_Y0 + PL_T         # 50.5: everything of module B starts here
LIFT_MIN, LIFT_CARRY, LIFT_MAX = 0.0, 15.0, 75.0   # lift travel (v7): carry = stack off the table, max = top of travel

# Butterfly plate holes (Two Trees Bluer V2 heatbed base, from the .3dm; x, z relative to the plate centre, Ø)
PLATE_HOLES = {
    "wheel":  [(-60.0, 37.5, 5.3), (-60.0, -37.5, 5.3), (60.0, -37.5, 7.5), (60.0, 37.5, 7.5)],   # V-wheel bolts (7.5 = eccentric side)
    "corner": [(-85.0, -85.0, 4.5), (-85.0, 85.0, 4.5), (85.0, 85.0, 4.5), (85.0, -85.0, 4.5)],   # M4: door units in A+B, free in B alone
    "centre": [(25.8, 0.0, 4.2), (0.0, -10.0, 4.3), (0.0, 10.0, 4.3)],
}
WHEEL_BOLT = "M5 x 35 socket head through wheel + spacer + plate + module B bracket, nyloc"   # v7 FIX_VIS_ROUES
# A+B: the door units sit at |x| >= 66 (keel K_X0) on the plate face and swing out to the sides; module B keeps
# inside |x| <= 62 next to the plate (v7 RES_FIX) unless a variant proves more room.
B_X_MAX_AB = 62.0

# ---------------------------------------------------------------- game elements
STONE_L, STONE_W, STONE_H = 320.0, 110.0, 110.0   # length (x), depth (y), height (z) when lying; tol +-4/5
STONE_TOL = 5.0
STACK_N = 3
STONE_CZ_TABLE = (55.0, 165.0, 275.0)             # stone centres above the table, quarry stack
HEIGHT_MAX = 350.0                                 # robot + held objects, above the table [GR F.3]
SPIN_HALF_DIAG = (160.0 ** 2 + 55.0 ** 2) ** 0.5   # 169.2: half-diagonal of a 320 x 110 face
STACK_FACE_Y = 146.0                               # layout-v1: stack face y in the module frame (front face of the body)

def table_to_module(z_table, lift=0.0):
    """Height above the table -> module z of a point that rides the butterfly plate at a given lift."""
    return z_table - MODULE_Z - lift

# ---------------------------------------------------------------- pneumatics (DATASHEET unless noted)
CUP = dict(name="DP-S30 / VS2-S30 bellows", d_lip=30.0, h_free=18.0, stroke=6.0, d_neck=12.0,  # DATASHEET (seller: Ø30, ~18 tall)
           thread="M5 male via VW7-M5")
VW7 = dict(thread="M5", hex_af=8.0, length=12.5, barb_d=4.0)                       # DATASHEET (seller drawing ~12.5 long)
ELBOW_PL4_M5 = dict(hex_af=8.0, hex_h=8.0, body_d=10.0, length=18.2, tube_axis_h=14.9, swivel=True,  # DATASHEET (Misumi table)
                    thread_l=4.0,          # M5 male thread length (assumed)
                    axis_from_hex=11.0,    # outlet axis behind the hex front face (14.9 from the thread tip - thread 4)
                    body_l=8.0,            # round body behind the hex
                    reach=17.7)            # outlet end (collet) from the body axis
# Cup mounting = BULKHEAD: the elbow's M5 thread passes through a 2 mm printed wall and screws into the cup's female
# M5 insert; the elbow hex sits in a hex pocket behind the wall (no rotation), the cup neck sits on the wall front.
# The pull on the cup goes cup -> thread -> hex -> wall. If the real thread is too short: M5 female-female coupler.
BULKHEAD_WALL = 2.0
HEX_POCKET_CLEAR = 0.3       # on the across-flats
TUBE = dict(od=4.0, id=2.5, r_min_static=12.0, r_min_moving=20.0, straight_after_fitting=15.0)       # PU 4 x 2.5, catalogue 8-12
PUMP_370 = dict(body_d=27.0, body_l=58.0, head_w=27.0, port_od=4.3, mount_hole=4.5, mount_pitch=17.0, # DATASHEET (Pincheng PYP370 class)
                vacuum_kpa=-60.0, count_in_hand=6)
VALVE = dict(name="FA0520F class 2-pos 3-way 12 V", l=35.0, w=15.0, h=15.0, port_od=3.0)          # DATASHEET (retailer)
CUPS_PER_MODULE = 3          # one per stone, one pump per cup (Seif, 2026-11-18)

# ---------------------------------------------------------------- cup station <-> carrier interface (every station)
# Station frame: cup axis = +Y (towards the stone), carrier FRONT face at y = 0, carrier from y = -car_t to 0.
# Every station drops into the same carrier hole with the same 3 x M3 (nuts behind the carrier, open side).
STATION = dict(car_t=6.0, hole_d=50.0, bolt_r=34.0, bolt_a=(90.0, 210.0, 330.0), od_max=76.0,
               tube_side=(1.0, 0.0))  # the tube leaves towards +x (the carrier mirrors a station to send it to -x)

# ---------------------------------------------------------------- printing / fasteners (design-principles.md)
WALL, RIB = 3.0, 2.0
CHAMFER_OUT = 1.0
M3_CLEAR, M4_CLEAR, M5_CLEAR = 3.4, 4.5, 5.5
M3_NUT_POCKET = (6.0, 6.9, 2.8)       # W x L x depth
M4_NUT_POCKET = (7.4, 8.4, 3.6)
INS3 = dict(hole=5.4, depth=7.0, cone_d=6.2, cone_h=1.5)   # D-025
RHO_ABS, RHO_TPU = 1.04, 1.21
