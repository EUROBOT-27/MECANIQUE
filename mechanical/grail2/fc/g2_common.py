# g2_common.py - shared helpers for grail2 (Baha's "essai mecanisme vis ecrou 1.0": T8 lead-screw lift + 180 deg servo flip).
# Frame of the whole folder ("grail2 frame"), from the SOLIDWORKS assembly frame (Y up):
#   x = SW X - 673.995          along the servo / flip axis
#   y = -(SW Z - 1304.905)      0 on the lead screw axis, +y = the side the magnet points to at flip 0
#   z = SW Y - 845.976          up; z = 0 = bottom of the NEMA17 body (lowest point of the mechanism).
# The assembly does not say how the mechanism is mounted in the robot: heights are given from the motor bottom,
# i.e. as if the motor stood on the table (the lowest it could ever be).
import json
import os

import FreeCAD as App
from FreeCAD import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))                      # mechanical/grail2
CAD = os.path.join(ROOT, "CAD_FC")
SW_EXPORT = os.path.join(CAD, "STEP", "sw_export")
MECH = os.path.normpath(os.path.join(ROOT, ".."))                      # mechanical/
JOINTS = os.path.join(CAD, "joints_grail2.json")

SW_ORIGIN = (673.995161, 1304.904526, 845.975518)                     # SW X, SW Z, SW Y of the grail2 origin
H_MAX = 350.0                                                          # robot + actuators at all times [GR F.3]
LEAD = 8.0                                                             # mm per screw turn (helix pitch in "vis 300mm")


def sw_frame():
    """Matrix: SW assembly coordinates -> grail2 frame."""
    X0, Z0, Y0 = SW_ORIGIN
    return App.Matrix(1, 0, 0, -X0,
                      0, 0, -1, Z0,
                      0, 1, 0, -Y0,
                      0, 0, 0, 1)


def comp_matrix(c):
    """Component transform from the SW dump (rot rows = part axes in the assembly, pos in mm) as a FreeCAD matrix."""
    r, t = c["rot"], c["pos"]
    return App.Matrix(r[0], r[3], r[6], t[0],
                      r[1], r[4], r[7], t[1],
                      r[2], r[5], r[8], t[2],
                      0, 0, 0, 1)


def load_joints(path=JOINTS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_joints(data, path=JOINTS):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


# ---------------------------------------------------------------- joints
def lift_pl(lift):
    return App.Placement(Vector(0, 0, lift), App.Rotation())


def flip_pl(J, lift, ang):
    """Flip group: rotation about the servo axis (along +x; +ang turns +y towards +z), then the lift."""
    p0 = Vector(*J["flip"]["axis_point"])
    r = App.Placement(Vector(0, 0, 0), App.Rotation(Vector(1, 0, 0), ang), p0)
    return lift_pl(lift).multiply(r)


def screw_pl(lift):
    """Screw + coupling + motor shaft turn LEAD mm of lift per turn (visual: right-hand thread assumed)."""
    return App.Placement(Vector(0, 0, 0), App.Rotation(Vector(0, 0, 1), -360.0 * lift / LEAD), Vector(0, 0, 0))


def simulate(J, t):
    """Sequence rows: [duration, lift, flip, label]; row 0 = start pose. Returns (lift, flip, label) at time t."""
    seq = J["sequence"]
    lift, ang, t0 = seq[0][1], seq[0][2], 0.0
    for dur, l1, a1, lab in seq[1:]:
        if t < t0 + dur:
            f = max(0.0, (t - t0) / dur) if dur > 0 else 1.0
            return lift + (l1 - lift) * f, ang + (a1 - ang) * f, lab
        lift, ang, t0 = l1, a1, t0 + dur
    return lift, ang, seq[-1][3]


def seq_duration(J):
    return sum(s[0] for s in J["sequence"][1:])


def placements(J, lift, ang):
    """{object name: placement to multiply onto its base placement} for a pose."""
    out = {}
    for n in J["lift"]["objects"]:
        out[n] = lift_pl(lift)
    for n in J["flip"]["objects"]:
        out[n] = flip_pl(J, lift, ang)
    for n in J["screw"]["objects"]:
        out[n] = screw_pl(lift)
    return out
