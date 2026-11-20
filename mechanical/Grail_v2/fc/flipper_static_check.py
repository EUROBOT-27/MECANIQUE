# flipper_static_check.py - static collision check of the Flipper on base_330_js (Seif 2026-11-20: after validation).
# Real overlap volumes (Part common), not bounding boxes, between every pair of solids in two poses:
#   PICK  : the model as built (carriage low, arm at the pick, Grail on the floor)
#   PLACE : the ghost parts (PLACE_*: arm, Grail, X plate, servo, servo mount, NEMA, pinion, motor bracket at the place)
# against the fixed parts (column, rack, saddle, brackets, base plate, Grail deck, the 350 limit sheet z 350..351) and the base_330_js parts
# (wheel, drive motor, hinge, odometry, ball units, clapets module A). Overlaps that are meant to be there (threads,
# pressed parts, screws through holes not drilled yet, the bought wheel stack) are listed apart.
#   Run (from mechanical/Grail_v2, after fc/flipper_fc.py): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_static_check.py
#   -> CAD_FC/FLIPPER_static_check.txt
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App

import common as C

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
    ("SCR_M5_TOP", "TNUT_M5_TOP", "thread in the T-nut"), ("SCR_M5_TOP", "PROFILE_2020", "M5 in the column's tapped end hole"),
    ("SCR_M5_TOP", "TOP_MEMBER", "through a Ø5.5 hole drilled across the cross-member"),
    ("SCR_M5_TOP", "TOP_L_BRACKET", "through the bracket's hole"), ("TNUT_M5", "PROFILE_2020", "T-nut in the slot (model)"),
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


def main():
    doc = App.openDocument(os.path.join(C.CAD, "FLIPPER_B330.FCStd"))
    objs = {o.Name: o.Shape for o in doc.Objects if o.TypeId == "Part::Feature" and not o.Shape.isNull()}
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
    ghosts = {n: s for n, s in objs.items() if n.startswith("PLACE_")}
    fixed_names = [n for n in objs if not n.startswith("PLACE_") and (
        n.startswith(("PROFILE", "RACK", "SADDLE", "TOP_", "BOTTOM_", "CTX_", "B330_", "SCR_M4x16", "NUT_M4_FLOOR",
                      "SCR_M5x12_HEEL", "TNUT_M5_HEEL", "SCR_M5x10_TOP", "TNUT_M5_TOP")))]
    pick = {n: s for n, s in objs.items() if not n.startswith("PLACE_")}
    lines = ["FLIPPER static collision check (real overlap volumes > %.1f mm3) - fc/flipper_static_check.py" % MIN_VOL, ""]

    def check(title, pairs):
        clashes, exp, others = [], [], []
        n_pairs = 0
        for (na, a), (nb, b) in pairs:
            if na.startswith("B330_") and nb.startswith("B330_"):
                continue                                  # inside Ayoub's base model, not ours
            if not a.BoundBox.intersect(b.BoundBox):
                continue
            n_pairs += 1
            try:
                v = a.common(b).Volume
            except Exception:
                continue
            if v <= MIN_VOL:
                continue
            why = expected(na, nb)
            if not why and (na.startswith("B330_") or nb.startswith("B330_")) and "CTX_LIMIT_350" in (na, nb):
                others.append((v, na, nb, "z max %.1f" % (a if na.startswith("B330_") else b).BoundBox.ZMax))
                continue
            (exp if why else clashes).append((v, na, nb, why))
        lines.append("== %s: %d pairs with touching boxes" % (title, n_pairs))
        lines.append("  CLASHES: %d" % len(clashes))
        for v, na, nb, _ in sorted(clashes, reverse=True):
            lines.append("    %8.1f mm3  %-28s x %s" % (v, na, nb))
        if others:
            lines.append("  base_330_js parts above the 350 limit (not the Flipper): %d" % len(others))
            for v, na, nb, why in sorted(others, reverse=True):
                lines.append("    %-28s %s" % (na if na.startswith("B330_") else nb, why))
        lines.append("  expected overlaps: %d" % len(exp))
        for v, na, nb, why in sorted(exp, reverse=True):
            lines.append("    %8.1f mm3  %-28s x %-28s %s" % (v, na, nb, why))
        lines.append("")

    allp = dict(pick)
    allp.update(base)
    check("PICK pose (as built) incl. base_330_js", itertools.combinations(sorted(allp.items()), 2))
    fixed = {n: objs[n] for n in fixed_names}
    fixed.update(base)
    pairs = [((ng, g), (nf, f)) for ng, g in sorted(ghosts.items()) for nf, f in sorted(fixed.items())]
    pairs += list(itertools.combinations(sorted(ghosts.items()), 2))
    check("PLACE pose (ghost parts) vs fixed parts + base, and among themselves", pairs)
    out = os.path.join(C.CAD, "FLIPPER_static_check.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


main()
