# check_common.py - shared by fc/flipper_static_check.py and fc/flipper_motion_check.py: overlaps that are meant to be
# there (threads, pressed parts, holes not drilled yet, gear mesh) and the base_330_js parts to check against.
import FreeCAD as App

MIN_VOL = 1.0          # mm3: smaller overlaps are face contacts on the meshed parts (profile, rack STL)
EXPECTED = [           # (name prefix A, name prefix B, why)
    ("SCR_M3x12_PLATE", "X_PLATE", "thread in the plate's tapped hole"),
    ("SCR_M3x20_TABS", "X_PLATE", "tab: drill Ø2.5 + tap M3 (hole not in the model)"),
    ("SCR_M4x16_FLOOR", "B330_plate", "base plate hole to add (Seif confirms)"),
    ("NUT_M4_FLOOR", "B330_plate", "under the plate"),
    ("INSERT_M3_PINION", "PINION_v2", "heat-set insert pressed in"),
    ("SCR_M3x6_SET_PINION", "INSERT_M3_PINION", "set screw in the insert's thread"),
    ("SCR_M3x6_SET_PINION", "PINION_v2", "set screw in the insert's thread"),
    ("SCR_M3x6_SET_PINION", "NEMA17", "set screw on the shaft's flat"),
    ("SCR_M2x12_HORN", "SERVO_HORN", "self-tapping into the horn holes"),
    ("SCR_M3x8_NEMA", "NEMA17", "thread in the motor"),
    ("SHAFT_5", "ARM_PRINTED", "pin pressed in the hub"),
    ("SHAFT_5", "BEARING_625", "pin in the bearing bore"),
    ("SERVO_HORN", "SERVO_MG996R", "horn on the spline"),
    ("NUT_M4_MAGNET", "MAGNET_D30", "nut on the magnet's stud"),
    ("SCR_M5x12_HEEL", "TNUT_M5_HEEL", "thread in the T-nut"),
    ("SCR_M5x10_TOP", "TNUT_M5_TOP", "thread in the T-nut"),
    ("M5x25_SCREWS", "V_WHEELS", "bought wheel stack (printer model)"),
    ("M5x25_SCREWS", "M5_", "bought wheel stack"), ("M5x25_SCREWS", "ECCENTRIC", "bought wheel stack"),
    ("M5x25_SCREWS", "BRONZE", "bought wheel stack"), ("M5x25_SCREWS", "X_PLATE", "bought wheel stack"),
    ("M5x25_SCREWS", "M5_NYLOC", "bought wheel stack"), ("ECCENTRIC", "V_WHEELS", "bought wheel stack"),
    ("SCR_M3x10_SERVO", "SERVO_MG996R", "through the servo's ear holes"),
    ("SCR_M3x10_SERVO", "NUT_M3_SERVO", "thread in the nut"),
    ("PINION_v2", "NEMA17", "on the motor shaft"),
    ("GRAIL", "MAGNET_D30", "magnet on the Grail's plate"), ("GRAIL_PLATE", "MAGNET_D30", "magnet on the Grail's plate"),
    ("GRAIL", "CTX_LIMIT_350", "the Grail may pass 350 once on the deck [G E.2]"),
    ("PINION_v2", "RACK_m1", "gear mesh: tooth phase not set in a static model (centre distance 10.0 = m1 20T)"),
    ("SCR_M5_TOP", "TNUT_M5_TOP", "thread in the T-nut"), ("SCR_M5_TOP", "PROFILE_2020", "M5 in the column's tapped end hole / blind-joint head in the back slot"),
    ("SCR_M5_TOP", "TOP_MEMBER", "M5 in the cross-member's tapped end (blind joint)"), ("TNUT_M5", "PROFILE_2020", "T-nut in the slot (model)"),
    ("TNUT_M5_TOP", "TOP_MEMBER", "T-nut in the cross-member's slot (model)"),
]
BASE_PARTS = ("wheels_JS7444_nominal_PH", "motors_37D_PH", "hinges_PH", "odo_bracket", "odo_arm", "dead_wheel", "amt102",
              "spring", "screws_M3", "ball_holders", "clapets_v7_moduleA")


def expected(a, b):
    for x, y, why in EXPECTED:
        for p_, q_ in ((a, b), (b, a)):
            pa = p_[6:] if p_.startswith("PLACE_") else p_
            qa = q_[6:] if q_.startswith("PLACE_") else q_
            if pa.startswith(x) and qa.startswith(y):
                return why
    return None




def load_base(C):
    """base_330_js parts near the Flipper (solids of the clapets module split), named B330_<part>[_i]."""
    asm = App.openDocument(C.B330_ASM)
    base = {}
    for n in BASE_PARTS:
        o = asm.getObject(n)
        if o is None:
            continue
        sols = o.Shape.Solids if n == "clapets_v7_moduleA" else [o.Shape]
        for i, so in enumerate(sols):
            base["B330_%s%s" % (n, "_%d" % i if len(sols) > 1 else "")] = so
    App.closeDocument(asm.Name)
    return base
