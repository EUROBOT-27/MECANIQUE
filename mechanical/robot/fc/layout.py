# layout.py - the robot layout, ONE place for every number that places a mechanism on the robot.
# Read by mechanical/robot/fc/build_robot.py (full robot + Gazebo export) and by the mechanism generators that need the
# robot around them (mechanical/grail-lift/fc/v3_fc.py). Change a number here, re-run build_robot (tools: sync_robot).
#
# Robot frame (same as the Gazebo sim, eb27_description): X forward (driving direction), Y left (along the wheel
# axle), Z up, mm. Origin = middle of the drive-wheel axle, on the table. Layout idea from CDR-2027
# (resources/CDR-2027/MCAD/differential-structure.FCStd): structure + drive in the middle, **front and back faces free
# for mechanisms** -> here: clapets module on the front AND on the back, Grail lift on the left side above the wheel.


class L:
    # ---- footprint (start, everything folded): 300 x 300 -> perimeter 1200 [GR F.3]
    HALF_X = 150.0
    HALF_Y = 150.0
    H_MAX = 350.0
    ROOF = 305.0                 # roof top surface (plate ROOF-5 .. ROOF); L4 needs > 300 [G E.2]
    ROOF_T = 5.0
    PLATE_Z = (20.0, 25.0)       # base plate (bottom, top)

    # ---- drive: 2 x Pololu 37D 30:1 12 V (330 rpm, #4742 no encoder) + JSUMO silicone wheels
    WHEEL_D = 74.0               # JSUMO "74 mm" (shop page also says 77 x 44 for JS7444: MEASURE)
    WHEEL_W = 44.0
    WHEEL_OUT = 148.0            # outer face of the wheel, |Y| (2 mm inside the footprint)
    WHEEL_GAP = 2.0              # wheel inner face -> gearbox boss
    # Pololu 37D dimension drawing (37d-metal-gearmotors-dimension-diagram.pdf): gearbox Ø36.8 x L (21.5 for 19:1/30:1),
    # motor Ø34.8 x 30.7, boss Ø12 x 6, shaft Ø6 x 22 (D), output shaft 7.0 off the gearbox axis, terminals 5,
    # face 6 x M3 on Ø31 (threads 3 mm deep max)
    GB_D, GB_L, MOT_D, MOT_L, BOSS_D, BOSS_L, SHAFT_D, SHAFT_L, SHAFT_OFF, TERM_L = \
        36.8, 21.5, 34.8, 30.7, 12.0, 6.0, 6.0, 22.0, 7.0, 5.0
    MOTOR_UP = True              # gearbox axis 7 mm ABOVE the wheel axle (more ground clearance)
    # odometry: 2 free wheels with AMT102 encoders (CDR-2027 "BlocOdometrie" idea), space RESERVED (design TBD):
    # AMT102 (datasheet): 28.77 x 43.38 x ~11, shaft 15.34 from the round end
    ODOM_X = 31.0                # in front of the drive motors, between them and the front door units
    ODOM_Y = 86.0
    ODOM_WHEEL_D = 30.0
    CASTERS = ((125.0, 45.0), (125.0, -45.0), (-125.0, 45.0), (-125.0, -45.0))   # ball casters (x, y), Ø12
    CASTER_R = 6.0

    # ---- clapets (stack gripper), copied front and back
    CLAPETS = "clapets-v8"       # folder in mechanical/clapets/ (v8 = v7 module A + v8 suction head)
    CLAPETS_Z0 = 25.0            # clapets z = 0 = top of the base plate (socle sits on it); its NEMA17 (z -19.5) hangs
                                 # through a hole, 5.5 mm above the table
    CLAPETS_FACE = 140.0         # clapets y of the stack face -> robot X = +-HALF_X
    CLAPETS_BACK = True          # second module on the back face
    # door units of the clapets (A_AILE, fixed part) in robot coordinates, from the clapets model
    DOOR_UNIT_X = (44.0, 106.0)  # |X|
    DOOR_UNIT_Y = (66.0, 150.0)  # |Y|
    DOOR_UNIT_Z = (27.0, 244.0)  # + CLAPETS_Z0

    # ---- Grail lift (v3: top grip + flip over the side edge), on the LEFT side (+Y), above the left wheel
    GRAIL_LIFT = "v3"
    GRAIL_SIDE = 1               # +1 = left (+Y), -1 = right
    GRAIL_X = 0.0                # robot X of the lift's centre plane

    # ---- top: beacon support (GR F.6: top at 430 +-5, within Ø200 of the centre), battery, electronics (reserves)
    MAST_XY = (0.0, -60.0)
    MAST_D = 80.0                # head, full from 350 to the top (GR F.6); below 350: a post
    MAST_POST_D = 20.0
    MAST_TOP = 430.0
    BATTERY = ((-22.0, 22.0), (-95.0, -25.0), (150.0, 230.0))     # x, y, z ranges (reserve), between the clapets carriages
    ELECTRONICS = ((-22.0, 22.0), (-130.0, 20.0), (90.0, 150.0))  # reserve


def wheel_center_y():
    return L.WHEEL_OUT - L.WHEEL_W / 2


def wheel_separation():
    return 2 * wheel_center_y()
