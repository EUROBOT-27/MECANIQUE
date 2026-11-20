# ARCHIVED 2026-11-20: concept of option B, superseded by fc/flipper_fc.py (real parts).
# b_lift_flip_fc.py - Grail v2, variant B "LIFT + FLIP": rack lift (NEMA17, Baha's tested rack) + MG996R flip.
# The column stands BESIDE the flip plane (behind it in -y), so the Grail never turns into its own lift (Baha's v1
# mistake). The flip axis is at the same x as in A (halfway between the pick and the place), but the lift lets the
# arm be short: pivot LZ above the Grail's top at the pick, LZ under the roof top at the place.
# Cycle: lift with the arm at the pick angle -> flip 180 deg OVER mm above the place height -> lower onto the roof ->
# magnet off -> lower REL mm more (the magnet leaves the Grail straight down) = stowed pose (arm in the roof slot).
#   Run (from mechanical/Grail_v2): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/b_lift_flip_fc.py
#   -> CAD_FC/B_LIFT_FLIP.FCStd, CAD_FC/B_LIFT_FLIP_report.txt
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fc"))   # archived: common.py is in ../fc
import FreeCAD as App
from FreeCAD import Vector

import common as C


class G:
    LZ = 45.0                                # pivot height above the Grail top (pick) = under the roof top (place)
    PX = (C.X_PICK + C.X_PLACE) / 2
    Z_PICK = C.G_H + LZ                      # pivot z at the pick
    Z_PLACE = C.ROOF_TOP - LZ                # pivot z at the place
    OVER = 8.0                               # flip this far above the place height, then lower
    REL = 6.0                                # lower after the magnet is off
    ARM_T, ARM_Y = 14.0, 10.0
    TIP_H = 10.0
    COL_X, COL_Y = 118.0, -70.0              # 2020 column (beside the flip plane, -y)
    HORN_FACE_Y = -5.0                       # servo horn outer face; arm plate y -5..5


def build(doc, groups):
    arm, lift, fixed = {}, {}, {}
    zf = C.G_H
    arm["MAGNET"] = C.magnet_down(C.X_PICK, zf)
    ztip = zf + C.MAG_L
    arm["ARM_TIP"] = C.box(C.X_PICK - 16, C.X_PICK + 16, -G.ARM_Y / 2, G.ARM_Y / 2, ztip, ztip + G.TIP_H)
    arm["ARM"] = C.bar((G.PX, G.Z_PICK), (C.X_PICK, ztip + G.TIP_H / 2), G.ARM_T, -G.ARM_Y / 2, G.ARM_Y / 2)
    arm["ARM_HUB"] = C.cyl(13, G.ARM_Y, (G.PX, -G.ARM_Y / 2, G.Z_PICK), (0, 1, 0))
    sv, hn = C.servo_mg996r(G.PX, G.Z_PICK, G.HORN_FACE_Y, body="-x")
    arm["SERVO_HORN"] = hn
    lift["SERVO_MG996R"] = sv
    sb = C.bb(sv)
    zr0 = 21.0 + 10
    fx, car = C.lift_unit(G.COL_X, G.COL_Y, 21.0, G.Z_PLACE + G.OVER + 37.5 + 3, G.Z_PICK, zr0,
                          G.Z_PLACE + G.OVER + 37.5, plate_x=(G.COL_X - 35, C.FACE))
    lift.update(car)
    py1 = G.COL_Y + 12                      # plate front face
    lift["SERVO_BRACKET"] = C.box(sb.XMin - 2, min(sb.XMax, C.FACE), py1, sb.YMin, G.Z_PICK - 14, G.Z_PICK + 14)
    fixed.update(fx)
    for n, s in arm.items():
        C.add(doc, n, s, "ARM_pick_pose", groups)
    for n, s in lift.items():
        C.add(doc, n, s, "CARRIAGE_pick_pose", groups)
    for n, s in fixed.items():
        C.add(doc, n, s, "FIXED", groups)
    g, plate = C.grail()
    C.add(doc, "GRAIL", g, "GRAIL_pick", groups)
    C.add(doc, "GRAIL_PLATE", plate, "GRAIL_pick", groups)
    return arm, lift, fixed, (g, plate)


def main():
    doc = App.newDocument("B_LIFT_FLIP")
    groups = {}
    arm, lift, fixed, gr = build(doc, groups)
    P = (G.PX, G.Z_PICK)
    top = G.Z_PLACE + G.OVER - G.Z_PICK            # lift (from the pick) where the flip happens
    steps = []

    def st(label, lz, a, held, final=False, grail_lz=None, grail_a=None):
        pl_arm = C.rot_pl(P, a, lz)
        gpl = pl_arm if held else C.rot_pl(P, grail_a, grail_lz)
        steps.append(dict(label=label, pls={"arm": pl_arm, "lift": App.Placement(Vector(0, 0, lz), App.Rotation())},
                          held=held, gpl=gpl, final=final))

    for i in range(0, 7):
        lz = top * i / 6.0
        st("lift %5.1f, flip 0" % (G.Z_PICK + lz), lz, 0, True)
    for a in list(range(15, 180, 15)) + [170, 175, 178, 180]:
        st("flip %3d at %5.1f" % (a, G.Z_PICK + top), top, a, True)
    st("lower to place %5.1f" % G.Z_PLACE, top - G.OVER, 180, True, final=True)
    st("magnet off, lower %.0f" % G.REL, top - G.OVER - G.REL, 180, False, grail_lz=top - G.OVER, grail_a=180)
    parts = {n: (s, "arm") for n, s in arm.items()}
    parts.update({n: (s, "lift") for n, s in lift.items()})
    fixed_top = max(C.bb(s).ZMax for s in fixed.values())
    lines, worst = C.run_cycle(steps, parts, fixed_top)

    stow = steps[-1]["pls"]
    start_out = max(max(C.bb(C.moved(s, stow[g])).XMax for s, g in parts.values()),
                    max(C.bb(s).XMax for s in fixed.values())) - C.FACE
    fin = steps[-2]["gpl"]
    for n, s in arm.items():
        C.add(doc, "PLACE_" + n, C.moved(s, fin), "GHOST_place", groups)
    for n, s in lift.items():
        C.add(doc, "PLACE_" + n, C.moved(s, steps[-2]["pls"]["lift"]), "GHOST_place", groups)
    C.add(doc, "PLACE_GRAIL", C.moved(gr[0].fuse(gr[1]), fin), "GHOST_place", groups)

    # roof slot: arm parts crossing the roof plate inside the face, from the late flip to the stowed pose
    xs, ys = [], []
    for s_ in steps[-6:]:
        for n, (s, g) in parts.items():
            b = C.bb(C.moved(s, s_["pls"][g]))
            if b.ZMin < C.ROOF_TOP and b.ZMax > C.ROOF_BOT and b.XMin < C.FACE:
                xs += [b.XMin, min(b.XMax, C.FACE)]
                ys += [b.YMin, b.YMax]
    slot = (min(xs) - 2, C.FACE + 1, min(ys) - 2, max(ys) + 2) if xs else None
    for n, s in C.robot_context(slot).items():
        C.add(doc, n, s, "ROBOT_CONTEXT", groups)

    # servo torque over the flip, lift force
    arm_m = sum(C.mass_of(arm[n]) for n in ("ARM", "ARM_TIP", "ARM_HUB"))
    arm_c = C.com(arm["ARM"].fuse(arm["ARM_TIP"]))
    mag_c = C.com(arm["MAGNET"])
    g_c = Vector(C.X_PICK, 0, C.G_H / 2)
    tmax, tang = 0.0, 0
    for a in range(0, 181, 5):
        pl = C.rot_pl(P, a)
        t = C.torque_kgcm([(C.G_MASS, pl.multVec(g_c).x), (C.MAG_MASS, pl.multVec(mag_c).x),
                           (arm_m, pl.multVec(arm_c).x)], G.PX)
        if t > tmax:
            tmax, tang = t, a
    m_moving = C.G_MASS + C.MAG_MASS + arm_m + 0.055 + 0.28 + 0.12   # + servo, NEMA17, carriage (estimates)
    servo_r = max(math.hypot(x - G.PX, z - G.Z_PICK) for x in (C.bb(lift["SERVO_MG996R"]).XMin, C.bb(lift["SERVO_MG996R"]).XMax)
                  for z in (C.bb(lift["SERVO_MG996R"]).ZMin, C.bb(lift["SERVO_MG996R"]).ZMax))
    grail_r = math.hypot(C.X_PICK - C.G_W / 2 - G.PX, C.G_H - G.Z_PICK)
    sb = C.bb(lift["SERVO_MG996R"])

    face_c = Vector(C.X_PICK, 0, C.G_H)
    p0 = fin.multVec(face_c)
    r = ["GRAIL v2 - B LIFT + FLIP (NEMA17 rack lift + MG996R flip) - fc/b_lift_flip_fc.py",
         "Grail %.0f x %.0f x %.0f, %.0f g, picked by its top at x %.1f, placed upside down at x %.1f on the roof (top %.0f)"
         % (C.G_W, C.G_W, C.G_H, C.G_MASS * 1000, C.X_PICK, C.X_PLACE, C.ROOF_TOP),
         "Flip axis x %.1f; pivot z %.1f (pick) -> %.1f (flip) -> %.1f (place) -> %.1f (stowed). Lift travel %.1f mm."
         % (G.PX, G.Z_PICK, G.Z_PICK + top, G.Z_PLACE, G.Z_PLACE - G.REL, top + G.REL),
         "Column 2020 at x %.0f, y %.0f (beside the flip plane: the Grail spans y +-%.0f)." % (G.COL_X, G.COL_Y, C.G_W / 2),
         "",
         "CYCLE (bounding boxes, no clash check). act.out = actuator x past the right face (x %.0f)" % C.FACE]
    r += lines
    r += ["", "SUMMARY"] + C.summary_lines(worst, start_out)
    r += ["  roof slot for the arm: %s" % ("x %.1f..%.1f, y %.1f..%.1f" % slot if slot else "none"),
          "  servo reach around the axis %.1f mm vs Grail nearest point %.1f mm (servo body y %.1f..%.1f overlaps "
          "the Grail's y, so it must stay inside that radius)" % (servo_r, grail_r, sb.YMin, sb.YMax),
          "  flip torque max %.1f kg.cm at %d deg (MG996R direct, ~9.4 at 6 V: %.1fx margin); servo range 180 deg"
          % (tmax, tang, 9.4 / tmax if tmax else 0),
          "  lift: ~%.2f kg moving -> %.2f kg.cm on the 20T pinion (NEMA17 ~4 kg.cm). The rack can be back-driven: "
          "at 100 s the carriage drops (Grail already released, arm in the slot)" % (m_moving, m_moving * 1.0),
          "  release: magnet off, carriage down %.0f mm: the magnet leaves the Grail straight down (clean); "
          "magnet face then at z %.1f" % (G.REL, p0.z - G.REL),
          "",
          "PARTS (📦 library · 🇹🇳 local · ✈️ import)",
          "  NEMA17 📦 · 2020 profile 📦 · V-wheels + eccentric 📦 (Ender carriage) · rack m1 + 20T pinion printed "
          "(Seif's print fits) · MG996R + round horn 📦 · electromagnet 🇹🇳 · arm, servo bracket printed ABS",
          "  arm (bar + tip + hub) ~%.0f g ABS. To detail: second support of the arm (steel U bracket + rear pin)." % (arm_m * 1000)]
    C.save(doc, "B_LIFT_FLIP", r)


main()
