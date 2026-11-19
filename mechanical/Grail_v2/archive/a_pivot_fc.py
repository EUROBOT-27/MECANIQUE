# a_pivot_fc.py - Grail v2, variant A "PIVOT": ONE servo, no lift.
# The arm turns 180 deg about an axis along y at the right face. A 180 deg turn maps the Grail's pick pose onto its
# place pose (upside down on the roof) only if the axis sits halfway between them:
#   x = (X_PICK + X_PLACE) / 2,  z = (G_H + ROOF_TOP) / 2.
# After the magnet is switched off the arm keeps turning ~20 deg (tip goes down + inward, under the roof) and stays
# there: that is also the stowed pose at the start.
#   ARCHIVED 2026-11-20 (not chosen, see ../README.md). Run (from mechanical/Grail_v2): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" archive/a_pivot_fc.py
#   -> CAD_FC/A_PIVOT.FCStd (pick pose + ghost at the place pose + robot context), CAD_FC/A_PIVOT_report.txt
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fc"))   # archived: common.py is in ../fc
import FreeCAD as App
from FreeCAD import Vector

import common as C


class G:
    PX = (C.X_PICK + C.X_PLACE) / 2          # pivot x
    PZ = (C.G_H + C.ROOF_TOP) / 2            # pivot z
    ARM_T, ARM_Y = 14.0, 10.0                # arm bar: in-plane thickness, width along y (y -5..5)
    TIP_H = 10.0                             # tip block above the magnet
    SHAFT_R = 4.0                            # Ø8 steel shaft, two 608 in the bearing block
    BLOCK = 14.0                             # bearing block half size (608 Ø22 + 3 wall)
    Y_BLOCK = (-32.0, -8.0)
    GEAR_ARM_T, GEAR_SERVO_T = 15, 18        # m1 gears: servo 18T -> shaft 15T (x1.2: 180 deg servo -> 216 deg arm)
    Y_GEAR = (-42.0, -36.0)
    PARK = 20.0                              # extra turn after the release (deg)


def build(doc, groups):
    mv, fx = {}, {}
    # magnet + tip block + arm (pick pose: arm from the pivot down-outward to the top of the Grail)
    zf = C.G_H
    mv["MAGNET"] = C.magnet_down(C.X_PICK, zf)
    ztip = zf + C.MAG_L
    mv["ARM_TIP"] = C.box(C.X_PICK - 16, C.X_PICK + 16, -G.ARM_Y / 2, G.ARM_Y / 2, ztip, ztip + G.TIP_H)
    mv["ARM"] = C.bar((G.PX, G.PZ), (C.X_PICK, ztip + G.TIP_H / 2), G.ARM_T, -G.ARM_Y / 2, G.ARM_Y / 2)
    mv["ARM_HUB"] = C.cyl(11, G.ARM_Y, (G.PX, -G.ARM_Y / 2, G.PZ), (0, 1, 0))
    mv["SHAFT_8"] = C.cyl(G.SHAFT_R, 50, (G.PX, -44, G.PZ), (0, 1, 0))
    mv["GEAR_ARM_15T"] = C.GC.pinion_m1(G.GEAR_ARM_T, G.Y_GEAR[1] - G.Y_GEAR[0], (G.PX, sum(G.Y_GEAR) / 2, G.PZ), "y")
    # fixed: bearing block, servo with its 18T gear on the horn
    b = G.BLOCK
    fx["BEARING_BLOCK_2x608"] = C.box(G.PX - b, G.PX + b, G.Y_BLOCK[0], G.Y_BLOCK[1], G.PZ - b, G.PZ + b).cut(
        C.cyl(4.2, 40, (G.PX, -40, G.PZ), (0, 1, 0)))
    cd = (G.GEAR_ARM_T + G.GEAR_SERVO_T) / 2.0          # centre distance, m1
    sx = G.PX - cd
    fx["GEAR_SERVO_18T"] = C.GC.pinion_m1(G.GEAR_SERVO_T, G.Y_GEAR[1] - G.Y_GEAR[0], (sx, sum(G.Y_GEAR) / 2, G.PZ), "y")
    sv, hn = C.servo_mg996r(sx, G.PZ, G.Y_GEAR[0], body="-x")
    fx["SERVO_MG996R"], fx["SERVO_HORN"] = sv, hn
    for n, s in mv.items():
        C.add(doc, n, s, "MOVING_pick_pose", groups)
    for n, s in fx.items():
        C.add(doc, n, s, "FIXED", groups)
    g, plate = C.grail()
    C.add(doc, "GRAIL", g, "GRAIL_pick", groups)
    C.add(doc, "GRAIL_PLATE", plate, "GRAIL_pick", groups)
    return mv, fx, (g, plate)


def main():
    doc = App.newDocument("A_PIVOT")
    groups = {}
    mv, fx, gr = build(doc, groups)
    P = (G.PX, G.PZ)
    steps = []
    for a in list(range(0, 180, 10)) + [175, 178]:
        pl = C.rot_pl(P, a)
        steps.append(dict(label="turn %3d (Grail held)" % a, pls={"arm": pl}, held=True, gpl=pl))
    steps.sort(key=lambda s: float(s["label"].split()[1]))
    fin = C.rot_pl(P, 180)
    steps.append(dict(label="turn 180 = place", pls={"arm": fin}, held=True, gpl=fin, final=True))
    for a in range(185, 181 + int(G.PARK), 5):
        steps.append(dict(label="turn %3d (released)" % a, pls={"arm": C.rot_pl(P, a)}, held=False, gpl=fin))
    parts = {n: (s, "arm") for n, s in mv.items()}
    fixed_top = max(C.bb(s).ZMax for s in fx.values())
    lines, worst = C.run_cycle(steps, parts, fixed_top)
    park = C.rot_pl(P, 180 + G.PARK)
    start_out = max(max(C.bb(C.moved(s, park)).XMax for s in mv.values()), max(C.bb(s).XMax for s in fx.values())) - C.FACE

    # ghosts: place pose and park pose
    for n, s in mv.items():
        C.add(doc, "PLACE_" + n, C.moved(s, fin), "GHOST_place_180", groups)
    C.add(doc, "PLACE_GRAIL", C.moved(gr[0].fuse(gr[1]), fin), "GHOST_place_180", groups)
    for n, s in mv.items():
        C.add(doc, "PARK_" + n, C.moved(s, park), "GHOST_park_start", groups)

    # roof slot: where the moving parts cross the roof plate (x < FACE) between place and park
    xs, ys = [], []
    for a in range(170, 181 + int(G.PARK), 2):
        for s in mv.values():
            b = C.bb(C.moved(s, C.rot_pl(P, a)))
            if b.ZMin < C.ROOF_TOP and b.ZMax > C.ROOF_BOT and b.XMin < C.FACE:
                xs += [b.XMin, min(b.XMax, C.FACE)]
                ys += [b.YMin, b.YMax]
    slot = (min(xs) - 2, C.FACE + 1, min(ys) - 2, max(ys) + 2) if xs else None
    for n, s in C.robot_context(slot).items():
        C.add(doc, n, s, "ROBOT_CONTEXT", groups)

    # torque on the arm shaft (Grail + magnet + arm) over the held turn
    arm_m = sum(C.mass_of(mv[n]) for n in ("ARM", "ARM_TIP", "ARM_HUB"))
    arm_c = C.com(mv["ARM"].fuse(mv["ARM_TIP"]))
    mag_c = C.com(mv["MAGNET"])
    g_c = Vector(C.X_PICK, 0, C.G_H / 2)
    tmax, tang = 0.0, 0
    for a in range(0, 181, 5):
        pl = C.rot_pl(P, a)
        t = C.torque_kgcm([(C.G_MASS, pl.multVec(g_c).x), (C.MAG_MASS, pl.multVec(mag_c).x),
                           (arm_m, pl.multVec(arm_c).x)], G.PX)
        if t > tmax:
            tmax, tang = t, a
    ratio = G.GEAR_SERVO_T / float(G.GEAR_ARM_T)
    t_servo = tmax * ratio
    L_mag = math.hypot(C.X_PICK - G.PX, C.G_H - G.PZ)

    # release: magnet face motion just after the place pose (keeps turning forward)
    face_c = Vector(C.X_PICK, 0, C.G_H)
    p0, p1 = fin.multVec(face_c), C.rot_pl(P, 182).multVec(face_c)
    d = p1 - p0
    rel_ang = math.degrees(math.atan2(-d.z, abs(d.x)))

    r = ["GRAIL v2 - A PIVOT (one MG996R, no lift) - fc/a_pivot_fc.py",
         "Grail %.0f x %.0f x %.0f, %.0f g, picked by its top at x %.1f (floor), placed upside down at x %.1f on the roof (top %.0f)"
         % (C.G_W, C.G_W, C.G_H, C.G_MASS * 1000, C.X_PICK, C.X_PLACE, C.ROOF_TOP),
         "Pivot (axis along y): x %.1f (%.1f past the face), z %.1f. Magnet face %.1f mm from the pivot."
         % (G.PX, G.PX - C.FACE, G.PZ, L_mag),
         "",
         "CYCLE (bounding boxes, no clash check). act.out = actuator x past the right face (x %.0f)" % C.FACE]
    r += lines
    r += ["", "SUMMARY"] + C.summary_lines(worst, start_out)
    r += ["  roof slot for the arm: %s" % ("x %.1f..%.1f, y %.1f..%.1f" % slot if slot else "none"),
          "  arm range: %.0f deg (pick -> place -> park) = servo %.0f deg through %d T -> %d T (x%.2f); MG996R ~180 deg"
          % (180 + G.PARK, (180 + G.PARK) / ratio, G.GEAR_SERVO_T, G.GEAR_ARM_T, ratio),
          "  torque: arm shaft max %.1f kg.cm at turn %d deg -> servo %.1f kg.cm (MG996R ~9.4 at 6 V: %.1fx margin)"
          % (tmax, tang, t_servo, 9.4 / t_servo if t_servo else 0),
          "  release: magnet off at 180, arm keeps turning: the magnet face leaves the Grail going %.0f deg below "
          "horizontal, inward (slides under it: sprung magnet / small gap needed)" % rel_ang,
          "  landing: the Grail arrives on the roof moving mostly sideways (tangent of the turn): see the 175/178 rows",
          "",
          "PARTS (📦 library · 🇹🇳 local · ✈️ import)",
          "  MG996R + round horn 📦 · gears m1 18T / 15T printed · Ø8 shaft 📦 (Ender rod, cut) · 2 x 608 📦 · "
          "electromagnet 12 V 5 kg 🇹🇳 · arm + tip + bearing block printed ABS",
          "  arm (bar + tip + hub) ~%.0f g ABS" % (arm_m * 1000)]
    C.save(doc, "A_PIVOT", r)


main()
