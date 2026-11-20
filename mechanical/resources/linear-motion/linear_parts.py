# linear_parts.py - models of the linear-motion parts we have in the lab (parts-library.md), for the generators.
#   Import: sys.path.insert(0, <this folder>); import linear_parts as LP; LP.scs8uu(), LP.sk8()
#   Run (from this folder): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" linear_parts.py  -> SCS8UU.step, SK8.step
# Since 2026-11-20 (Maatoug sent vendor CAD files, converted with tools/solidworks): scs8uu() / sk8() return the VENDOR
# models (vendor/SCS8UU.step from SCS8UU.SLDPRT, vendor/SoporteVertical_SK8.step from the Inventor .ipt), moved into
# the frame below. The catalogue builders (catalogue_scs8uu / catalogue_sk8) stay as a fallback if a vendor file is missing.
#
# Local frame of both parts: rod axis = z, through (0, 0); the part spans z -L/2 .. +L/2.
#   SCS8UU: its flat mounting face (the 4 tapped holes, 24 x 16) at y = -11; the other side is crowned.
#   SK8: base face at y = -20 (2 x M5 holes on 32 along x), clamp slit + screw above the rod.
import os

import Part
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))

# SCS8UU = aluminium housing + LM8UU (Ø8 / Ø15 x 24). Catalogue: W 34 (x), H 22 (y), L 30 (z), rod axis in the middle
# of H (h = 11), 4 x M4 tapped through holes on 24 (x) x 18 (z), mounting faces y = +-11.
SCS8UU = {"W": 34.0, "H": 22.0, "L": 30.0, "h": 11.0, "B": 24.0, "C": 18.0, "hole": 3.3, "lm_od": 15.0, "lm_l": 24.0}
# SK8 shaft support (seller sheet: d 8, h 20, E 21, W 42, L 14, F 32.8, G 6, P 18, B 32, S 5.5 (M5), clamp M4).
# Base face at y = -h, base G thick, tower P wide up to y = F - h, slit + M4 clamp screw above the rod.
SK8 = {"d": 8.0, "h": 20.0, "W": 42.0, "L": 14.0, "F": 32.8, "G": 6.0, "P": 18.0, "B": 32.0, "S": 5.5, "clamp": 4.0}


def _box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def _cyl(r, p0, p1):
    p0, p1 = Vector(*p0), Vector(*p1)
    return Part.makeCylinder(r, (p1 - p0).Length, p0, p1 - p0)


VENDOR = os.path.join(HERE, "vendor")


def scs8uu():
    """Vendor SCS8UU (one solid, Ø8 bore), mounting face at y = -10.97, z -15..15; catalogue model if missing."""
    f = os.path.join(VENDOR, "SCS8UU.step")
    if not os.path.exists(f):
        return catalogue_scs8uu()
    s = Part.read(f)                       # vendor frame: rod along z at (0, 0), z -30 .. 0, holes face at y = -10.97
    s.translate(Vector(0, 0, 15.0))
    return s


def sk8():
    """Vendor SK8 (body + clamp screw), base face at y = -20, rod along z at the origin, z -7..7; catalogue if missing."""
    f = os.path.join(VENDOR, "SoporteVertical_SK8.step")
    if not os.path.exists(f):
        return catalogue_sk8()
    s = Part.read(f)                       # vendor frame: base face y = 0, rod along z at (21, 20), z 0 .. 14
    s.translate(Vector(-21.0, -20.0, -7.0))
    return s


def catalogue_scs8uu():
    """Housing with the LM8UU inside (one solid each), rod bore Ø8. Mounting faces y = +-H/2."""
    s = SCS8UU
    W, H, L = s["W"], s["H"], s["L"]
    hs = _box(-W / 2, W / 2, -H / 2, H / 2, -L / 2, L / 2)
    # two side grooves along the length (the dark bands on the real part), 2 x 2 at mid-height of the x faces
    for sx in (1, -1):
        x0 = sx * W / 2 - (2.0 if sx > 0 else 0.0)
        hs = hs.cut(_box(x0, x0 + 2.0, -1.0, 1.0, -L / 2 - 1, L / 2 + 1))
    hs = hs.cut(_cyl(s["lm_od"] / 2, (0, 0, -L / 2 - 1), (0, 0, L / 2 + 1)))
    for x in (-s["B"] / 2, s["B"] / 2):
        for z in (-s["C"] / 2, s["C"] / 2):
            hs = hs.cut(_cyl(s["hole"] / 2, (x, -H / 2 - 1, z), (x, H / 2 + 1, z)))
    lm = _cyl(s["lm_od"] / 2, (0, 0, -s["lm_l"] / 2), (0, 0, s["lm_l"] / 2))
    lm = lm.cut(_cyl(4.0, (0, 0, -L), (0, 0, L)))
    return Part.makeCompound([hs.removeSplitter(), lm])


def catalogue_sk8():
    """SK8 rod support: base face at y = -h, rod Ø8 along z at the origin, clamp slit above the rod."""
    s = SK8
    h, W, L, F, G, P = s["h"], s["W"], s["L"], s["F"], s["G"], s["P"]
    base = _box(-W / 2, W / 2, -h, -h + G, -L / 2, L / 2)
    tower = _box(-P / 2, P / 2, -h + G - 0.01, F - h, -L / 2, L / 2)
    sh = base.fuse(tower)
    sh = sh.cut(_cyl(s["d"] / 2, (0, 0, -L), (0, 0, L)))                         # rod bore
    sh = sh.cut(_box(-0.5, 0.5, 0, F - h + 1, -L, L))                           # clamp slit
    sh = sh.cut(_cyl(s["clamp"] / 2 * 0.85, (-P, 8.0, 0), (P, 8.0, 0)))         # M4 clamp screw (tapped one side)
    for x in (-s["B"] / 2, s["B"] / 2):                                         # 2 x M5 mounting holes through the base
        sh = sh.cut(_cyl(s["S"] / 2, (x, -h - 1, 0), (x, -h + G + 1, 0)))
    return sh.removeSplitter()


import sys  # noqa: E402  (freecadcmd imports the script as a module: write the STEPs only when it is the script run)

if __name__ == "__main__" or any(a.endswith("linear_parts.py") for a in sys.argv):
    catalogue_scs8uu().exportStep(os.path.join(HERE, "SCS8UU_catalogue.step"))     # catalogue versions (fallback, for comparison)
    catalogue_sk8().exportStep(os.path.join(HERE, "SK8_catalogue.step"))
    for n, f in (("SCS8UU vendor", scs8uu), ("SK8 vendor", sk8), ("SCS8UU catalogue", catalogue_scs8uu), ("SK8 catalogue", catalogue_sk8)):
        sh = f()
        print(n, sh.BoundBox, "valid", sh.isValid())
