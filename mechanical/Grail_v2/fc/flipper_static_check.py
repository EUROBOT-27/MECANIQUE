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

from check_common import MIN_VOL, expected, load_base


def main():
    doc = App.openDocument(os.path.join(C.CAD, "FLIPPER_B330.FCStd"))
    objs = {o.Name: o.Shape for o in doc.Objects if o.TypeId == "Part::Feature" and not o.Shape.isNull()}
    base = load_base(C)
    ghosts = {n: s for n, s in objs.items() if n.startswith("PLACE_")}
    fixed_names = [n for n in objs if not n.startswith("PLACE_") and (
        n.startswith(("PROFILE", "RACK", "SADDLE", "TOP_", "BOTTOM_", "CTX_", "B330_", "SCR_M4x16", "NUT_M4_FLOOR",
                      "SCR_M5x12_HEEL", "TNUT_M5_HEEL", "SCR_M5_TOP", "TNUT_M5_TOP")))]
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
