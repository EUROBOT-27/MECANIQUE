# flipper_s_fc.py - FLIPPER-S (was B2): the Flipper flip on a lead-screw lift, made real with the hardware of "essai vis ecrou corrige"
# (../Grail_v1/essai vise ecrou corrigé/): T8 lead screw + flange nut (self-locking-ish, no drop), 2 x Ø8 rods +
# 4 LM8UU, 608 at both screw ends, flip arm held on BOTH sides (servo horn + 625 bearing).
# Changes vs the corrigé, forced by layout-v1 (right side bay x 66..150, y +-40, z 78..300; right wheel + drive motor
# under it; roof at 300..306):
#   * motor NOT under the screw (wheel + drive motor there): NEMA17 upside down in the bay's inner half, GT2 belt 1:1
#     to a pulley under the bottom plate (room above the wheel at y -28: wheel top there ~61);
#   * column (2 rods + screw) in a line along x at y COL_Y, behind the arm's path (the arm crosses the roof at |y| <= 16);
#   * top grip (magnet) instead of the tray; the Grail is turned 180 deg onto the roof like option B;
#   * servo body pointing DOWN (stays out of the column and inside the Grail's free radius).
# Cycle as B: lift (arm at the pick angle) -> flip 180 at the top -> lower OVER onto the roof -> magnet off ->
# lower REL (magnet leaves straight down) = stowed pose.
#   Run (from mechanical/Grail_v2): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/flipper_s_fc.py
#   -> CAD_FC/FLIPPER_S.FCStd, CAD_FC/FLIPPER_S_report.txt   (bounding boxes only, no clash check)
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
import Part
from FreeCAD import Vector

import common as C


class G:
    # --- flip geometry (as B)
    LZ = 50.0                                # pivot above the Grail top at the pick = under the roof top at the place
    PX = (C.X_PICK + C.X_PLACE) / 2
    Z_PICK = C.G_H + LZ
    Z_PLACE = C.ROOF_TOP - LZ
    OVER = 6.0
    REL = 6.0
    ARM_T, ARM_Y = 14.0, 10.0                # arm plate y -5..5
    TIP_H = 10.0
    # --- column (rods + screw), all at y = COL_Y
    COL_Y = -28.0
    ROD_X = (77.0, 125.0)
    SCREW_X = 97.0                           # screw pulley (r 8) stays at x <= 105: off the wheel (x >= 106)
    Z_BOT_PLATE = (78.0, 88.0)               # bottom plate (rods, 608), on the bay floor
    Z_TOP_PLATE = (290.0, 300.0)             # top plate (rods, 608), under the roof plate
    Z_PULLEY = (64.0, 78.0)                  # GT2 pulleys under the bottom plate, above the drive motor (55.5)
    # --- carriage: 2 LM8UU per rod + flange nut; pivot H_P above the carriage bottom
    CAR_H = 48.0
    H_P = 22.0
    CAR_X = (66.0, 137.0)
    CAR_Y = (-40.0, -17.0)
    # --- motor (upside down, shaft down, belt to the screw)
    MOT_X, MOT_Y = 87.5, 18.5                # NEMA17 standing on the bottom plate, shaft down through it
    # --- arm support
    HORN_FACE_Y = -5.0
    Y_625 = (8.0, 13.0)                      # 625 (Ø16 x 5) in the +y cheek
    SHAFT_R = 2.5                            # Ø5 shaft through the hub into the 625


def build(doc, groups):
    arm, lift, fixed = {}, {}, {}
    zp = G.Z_PICK
    # ---------------- arm (pick pose)
    zf = C.G_H
    arm["MAGNET"] = C.magnet_down(C.X_PICK, zf)
    ztip = zf + C.MAG_L
    arm["ARM_TIP"] = C.box(C.X_PICK - 16, C.X_PICK + 16, -G.ARM_Y / 2, G.ARM_Y / 2, ztip, ztip + G.TIP_H)
    arm["ARM"] = C.bar((G.PX, zp), (C.X_PICK, ztip + G.TIP_H / 2), G.ARM_T, -G.ARM_Y / 2, G.ARM_Y / 2)
    arm["ARM_HUB"] = C.cyl(12, G.ARM_Y, (G.PX, -G.ARM_Y / 2, zp), (0, 1, 0))
    arm["SHAFT_5"] = C.cyl(G.SHAFT_R, G.Y_625[1] - G.HORN_FACE_Y, (G.PX, G.HORN_FACE_Y, zp), (0, 1, 0))
    sv, hn, _ = C.servo_mg996r(G.PX, zp, G.HORN_FACE_Y, body="-z")
    arm["SERVO_HORN"] = hn
    # ---------------- carriage (pick pose: bottom at zp - H_P)
    zc0 = zp - G.H_P
    zc1 = zc0 + G.CAR_H
    car = C.box(G.CAR_X[0], G.CAR_X[1], G.CAR_Y[0], G.CAR_Y[1], zc0, zc1)
    for rx in G.ROD_X:
        car = car.cut(C.cyl(7.6, G.CAR_H + 2, (rx, G.COL_Y, zc0 - 1), (0, 0, 1)))
    car = car.cut(C.cyl(5.5, G.CAR_H + 2, (G.SCREW_X, G.COL_Y, zc0 - 1), (0, 0, 1)))
    lift["CARRIAGE"] = car
    lm = []
    for rx in G.ROD_X:
        for z0 in (zc0, zc1 - 24):
            lm.append(C.cyl(7.5, 24, (rx, G.COL_Y, z0), (0, 0, 1)).cut(C.cyl(4.0, 26, (rx, G.COL_Y, z0 - 1), (0, 0, 1))))
    lift["LM8UU_x4"] = Part.makeCompound(lm)
    nut = C.cyl(11, 3.5, (G.SCREW_X, G.COL_Y, zc0 - 3.5), (0, 0, 1)).fuse(
        C.cyl(5.1, 15, (G.SCREW_X, G.COL_Y, zc0 - 3.5), (0, 0, 1))).cut(C.cyl(4, 20, (G.SCREW_X, G.COL_Y, zc0 - 5), (0, 0, 1)))
    lift["T8_FLANGE_NUT"] = nut
    lift["SERVO_MG996R"] = sv
    sb = C.bb(sv)
    # servo bracket: plate behind the servo (y < servo) from the carriage to the servo, servo screwed through its ears
    lift["SERVO_BRACKET"] = C.box(G.CAR_X[1] - 10, sb.XMax, sb.YMin - 3.4, sb.YMin, sb.ZMin, zp + 12).fuse(
        C.box(G.CAR_X[1] - 10, G.CAR_X[1], sb.YMin - 3.4, G.CAR_Y[1], zc0, zc1))
    # +y cheek with the 625, joined under the pivot to the bracket (zone the arm and the Grail never reach)
    cz0 = zp - 44
    cheek = C.box(G.PX - 12, G.PX + 5.5, G.Y_625[0] - 1, G.Y_625[1] + 2, cz0, zp + 9).fuse(
        C.cyl(10, G.Y_625[1] + 2 - G.Y_625[0] + 1, (G.PX, G.Y_625[0] - 1, zp), (0, 1, 0)))
    cheek = cheek.fuse(C.box(G.PX - 12, G.PX + 5.5, sb.YMin - 3.4, G.Y_625[1] + 2, cz0, cz0 + 6))
    cheek = cheek.cut(C.cyl(8.0, 10, (G.PX, G.Y_625[0], zp), (0, 1, 0))).cut(C.cyl(G.SHAFT_R + 0.3, 30, (G.PX, -10, zp), (0, 1, 0)))
    lift["CHEEK_625"] = cheek
    lift["BEARING_625"] = C.cyl(8, 5, (G.PX, G.Y_625[0], zp), (0, 1, 0)).cut(C.cyl(2.5, 7, (G.PX, G.Y_625[0] - 1, zp), (0, 1, 0)))
    # ---------------- fixed column
    zb0, zb1 = G.Z_BOT_PLATE
    zt0, zt1 = G.Z_TOP_PLATE
    for i, rx in enumerate(G.ROD_X):
        fixed["ROD_8_%d" % (i + 1)] = C.cyl(4, zt1 - zb0, (rx, G.COL_Y, zb0), (0, 0, 1))
    fixed["SCREW_T8"] = C.cyl(4, zt1 - 2 - G.Z_PULLEY[0], (G.SCREW_X, G.COL_Y, G.Z_PULLEY[0]), (0, 0, 1))
    for nm, (z0, z1) in (("BOTTOM_PLATE", G.Z_BOT_PLATE), ("TOP_PLATE", G.Z_TOP_PLATE)):
        y1 = G.CAR_Y[1] - 1 if nm == "TOP_PLATE" else G.MOT_Y + 21.15      # bottom plate = bay floor, carries the motor
        p = C.box(G.CAR_X[0], G.CAR_X[1] - 6 if nm == "TOP_PLATE" else C.BAY["x1"] - 10, G.CAR_Y[0], y1, z0, z1)
        if nm == "BOTTOM_PLATE":
            p = p.cut(C.cyl(11.5, 20, (G.MOT_X, G.MOT_Y, z0 - 1), (0, 0, 1)))      # motor pilot / shaft
        for rx in G.ROD_X:
            p = p.cut(C.cyl(4, 20, (rx, G.COL_Y, z0 - 1), (0, 0, 1)))
        fixed[nm] = p.cut(C.cyl(11, 20, (G.SCREW_X, G.COL_Y, z0 - 1), (0, 0, 1)))
        fixed["608_" + nm.split("_")[0]] = C.cyl(11, 7, (G.SCREW_X, G.COL_Y, z0 + 1.5), (0, 0, 1)).cut(
            C.cyl(4, 9, (G.SCREW_X, G.COL_Y, z0), (0, 0, 1)))
    zpu0, zpu1 = G.Z_PULLEY
    fixed["PULLEY_SCREW_GT2_20T"] = C.cyl(8, zpu1 - zpu0, (G.SCREW_X, G.COL_Y, zpu0), (0, 0, 1))
    fixed["PULLEY_MOTOR_GT2_20T"] = C.cyl(8, zpu1 - zpu0, (G.MOT_X, G.MOT_Y, zpu0), (0, 0, 1))
    a, b = Vector(G.MOT_X, G.MOT_Y, 0), Vector(G.SCREW_X, G.COL_Y, 0)
    d = b - a
    belt = C.box(0, d.Length, -6.6, 6.6, zpu0 + 4, zpu0 + 10).cut(C.box(0, d.Length, -5.6, 5.6, zpu0 + 3, zpu0 + 11))
    belt.rotate(Vector(0, 0, 0), Vector(0, 0, 1), math.degrees(math.atan2(d.y, d.x)))
    belt.translate(a)
    fixed["GT2_BELT"] = belt
    fixed["NEMA17_upside_down"] = C.box(G.MOT_X - 21.15, G.MOT_X + 21.15, G.MOT_Y - 21.15, G.MOT_Y + 21.15, zb1, zb1 + 40)
    fixed["NEMA17_SHAFT"] = C.cyl(2.5, zb1 - zpu0, (G.MOT_X, G.MOT_Y, zpu0), (0, 0, 1))
    for n, s in arm.items():
        C.add(doc, n, s, "ARM_pick_pose", groups)
    for n, s in lift.items():
        C.add(doc, n, s, "CARRIAGE_pick_pose", groups)
    for n, s in fixed.items():
        C.add(doc, n, s, "FIXED_column", groups)
    g, plate = C.grail()
    C.add(doc, "GRAIL", g, "GRAIL_pick", groups)
    C.add(doc, "GRAIL_PLATE", plate, "GRAIL_pick", groups)
    return arm, lift, fixed, (g, plate)


def overlap(b1, b2):
    dx = min(b1.XMax, b2.XMax) - max(b1.XMin, b2.XMin)
    dy = min(b1.YMax, b2.YMax) - max(b1.YMin, b2.YMin)
    dz = min(b1.ZMax, b2.ZMax) - max(b1.ZMin, b2.ZMin)
    return (dx, dy, dz) if dx > 0 and dy > 0 and dz > 0 else None


def main():
    doc = App.newDocument("FLIPPER_S")
    groups = {}
    arm, lift, fixed, gr = build(doc, groups)
    P = (G.PX, G.Z_PICK)
    top = G.Z_PLACE + G.OVER - G.Z_PICK
    steps = []

    def st(label, lz, a, held, final=False, grail_lz=None, grail_a=None):
        pl_arm = C.rot_pl(P, a, lz)
        gpl = pl_arm if held else C.rot_pl(P, grail_a, grail_lz)
        steps.append(dict(label=label, pls={"arm": pl_arm, "lift": App.Placement(Vector(0, 0, lz), App.Rotation())},
                          held=held, gpl=gpl, final=final))

    for i in range(0, 5):
        st("lift %5.1f, flip 0" % (G.Z_PICK + top * i / 4.0), top * i / 4.0, 0, True)
    for a in list(range(15, 180, 15)) + [170, 175, 180]:
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

    # roof slot (arm parts only, inside the roof strip)
    xs, ys = [], []
    for s_ in steps[-5:]:
        for n, s in arm.items():
            b = C.bb(C.moved(s, s_["pls"]["arm"]))
            if b.ZMin < C.ROOF_TOP and b.ZMax > C.ROOF_BOT and b.XMin < C.FACE:
                xs += [b.XMin, min(b.XMax, C.FACE)]
                ys += [b.YMin, b.YMax]
    slot = (min(xs) - 2, C.FACE + 1, min(ys) - 2, max(ys) + 2) if xs else None
    for n, s in C.robot_context(slot).items():
        C.add(doc, n, s, "ROBOT_CONTEXT", groups)
    drive = C.box(38, 106, -18.5, 18.5, 18.5, 55.5)
    C.add(doc, "CTX_DRIVE_MOTOR_R", drive, "ROBOT_CONTEXT", groups)

    # ---- layout envelope checks (bounding boxes against reserved volumes; not a clash check)
    env = []
    bay = App.BoundBox(C.BAY["x0"], -C.BAY["y"], C.BAY["z0"], C.BAY["x1"], C.BAY["y"], C.BAY["z1"])
    wheel_bb = App.BoundBox(C.WHEEL["x0"], -C.WHEEL["r"], 0, C.WHEEL["x1"], C.WHEEL["r"], 2 * C.WHEEL["r"])
    wheel_c = (0.0, C.WHEEL["z"], C.WHEEL["r"])
    zone_parts = [(n, C.bb(s)) for n, s in fixed.items()]
    for s_ in (steps[0], steps[4], steps[-1]):
        for n, (s, g) in parts.items():
            if g == "lift" or n in ("SERVO_HORN", "SHAFT_5", "ARM_HUB"):
                zone_parts.append(("%s @%s" % (n, s_["label"].split(",")[0]), C.bb(C.moved(s, s_["pls"][g]))))
    for n, b in zone_parts:
        out = []
        if b.YMin < -C.BAY["y"] - 0.1 or b.YMax > C.BAY["y"] + 0.1:
            out.append("y %.1f..%.1f (bay +-%.0f)" % (b.YMin, b.YMax, C.BAY["y"]))
        if b.XMin < C.BAY["x0"] - 0.1:
            out.append("x from %.1f (bay from %.0f)" % (b.XMin, C.BAY["x0"]))
        if b.ZMin < C.BAY["z0"] - 0.1 and not n.startswith(("PULLEY", "GT2", "SCREW", "NEMA")):
            out.append("z from %.1f (bay from %.0f)" % (b.ZMin, C.BAY["z0"]))
        if b.ZMax > C.ROOF_BOT + 0.1:
            out.append("z to %.1f (roof plate from %.0f)" % (b.ZMax, C.ROOF_BOT))
        if out:
            env.append("  %-40s %s" % (n[:40], "; ".join(out)))
    # wheel (cylinder) vs the parts under the bay
    for n in ("PULLEY_SCREW_GT2_20T", "PULLEY_MOTOR_GT2_20T", "GT2_BELT", "NEMA17_upside_down", "NEMA17_SHAFT", "SCREW_T8",
              "BOTTOM_PLATE"):
        b = C.bb(fixed[n])
        if b.XMax > C.WHEEL["x0"] and b.XMin < C.WHEEL["x1"]:
            yy = min(abs(b.YMin), abs(b.YMax)) if b.YMin * b.YMax > 0 else 0.0
            top_wheel = wheel_c[1] + math.sqrt(max(0.0, wheel_c[2] ** 2 - yy ** 2)) if yy < wheel_c[2] else -1
            env.append("  %-40s over the wheel: bottom %.1f vs wheel top %.1f at |y| %.1f -> %s"
                       % (n, b.ZMin, top_wheel, yy, "OK" if b.ZMin > top_wheel + 1 else "CLASH"))
        else:
            env.append("  %-40s x %.1f..%.1f: not over the wheel (x %.0f..%.0f)" % (n, b.XMin, b.XMax, C.WHEEL["x0"], C.WHEEL["x1"]))
        ov = overlap(b, C.bb(drive))
        if ov:
            env.append("  %-40s overlaps the drive motor envelope by %.1f x %.1f x %.1f" % (n, ov[0], ov[1], ov[2]))
    # carriage travel margins
    car_top_flip = G.Z_PICK - G.H_P + G.CAR_H + top
    car_bot_pick = G.Z_PICK - G.H_P - 3.5            # flange below the carriage
    margins = ["  carriage top at the flip %.1f vs top plate %.1f -> %.1f mm" % (car_top_flip, G.Z_TOP_PLATE[0], G.Z_TOP_PLATE[0] - car_top_flip),
               "  nut flange bottom at the pick %.1f vs bottom plate %.1f -> %.1f mm" % (car_bot_pick, G.Z_BOT_PLATE[1], car_bot_pick - G.Z_BOT_PLATE[1])]

    # torques, lengths
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
    m_moving = C.G_MASS + C.MAG_MASS + arm_m + 0.055 + C.mass_of(lift["CARRIAGE"]) + 0.07 + 0.03
    f_n = m_moving * 9.81
    t_screw = f_n * 0.008 / (2 * math.pi * 0.35)    # T8 lead 8, efficiency ~35 %
    grail_r = math.hypot(C.X_PICK - C.G_W / 2 - G.PX, C.G_H - G.Z_PICK)
    sb = C.bb(lift["SERVO_MG996R"])
    servo_r = max(math.hypot(x - G.PX, z - G.Z_PICK) for x in (sb.XMin, sb.XMax) for z in (sb.ZMin, sb.ZMax))
    cb = C.bb(lift["CHEEK_625"])
    cheek_r = max(math.hypot(x - G.PX, z - G.Z_PICK) for x in (cb.XMin, cb.XMax) for z in (cb.ZMin, cb.ZMax))
    belt_cd = math.hypot(G.SCREW_X - G.MOT_X, G.COL_Y - G.MOT_Y)
    belt_len = 2 * belt_cd + math.pi * 12.73          # 20T GT2 pitch Ø 12.73

    r = ["FLIPPER-S (lead-screw lift from the corrige) - fc/flipper_s_fc.py",
         "Grail %.0f x %.0f x %.0f, picked by its top at x %.1f, placed upside down at x %.1f (roof top %.0f)"
         % (C.G_W, C.G_W, C.G_H, C.X_PICK, C.X_PLACE, C.ROOF_TOP),
         "Flip axis x %.1f; pivot z %.1f (pick) -> %.1f (flip) -> %.1f (place) -> %.1f (stowed); lift travel %.1f"
         % (G.PX, G.Z_PICK, G.Z_PICK + top, G.Z_PLACE, G.Z_PLACE - G.REL, top + G.REL),
         "Column at y %.0f: rods x %s, screw x %.1f, plates z %s / %s; carriage %.0f tall, pivot %.0f above its bottom"
         % (G.COL_Y, G.ROD_X, G.SCREW_X, G.Z_BOT_PLATE, G.Z_TOP_PLATE, G.CAR_H, G.H_P),
         "",
         "CYCLE (bounding boxes, no clash check). act.out = actuator x past the right face (x %.0f)" % C.FACE]
    r += lines
    r += ["", "SUMMARY"] + C.summary_lines(worst, start_out)
    r += ["  roof slot for the arm: %s" % ("x %.1f..%.1f, y %.1f..%.1f" % slot if slot else "none")]
    r += margins
    r += ["  Grail nearest point to the axis %.1f; servo reaches %.1f, 625 cheek %.1f (both must stay below)"
          % (grail_r, servo_r, cheek_r),
          "  flip torque max %.1f kg.cm at %d deg (MG996R ~9.4: %.1fx). Lift: ~%.2f kg moving -> %.3f N.m on the screw "
          "(NEMA17 ~0.4)" % (tmax, tang, 9.4 / tmax if tmax else 0, m_moving, t_screw),
          "  GT2 belt 1:1: centre distance %.1f -> closed loop ~%.0f mm (pick the nearest stock loop, tensioner or "
          "slotted motor plate)" % (belt_cd, belt_len),
          "",
          "LAYOUT ENVELOPE (bounding boxes vs layout-v1 volumes; the right bay is x %.0f..%.0f, y +-%.0f, z %.0f..%.0f)"
          % (C.BAY["x0"], C.BAY["x1"], C.BAY["y"], C.BAY["z0"], C.BAY["z1"])]
    r += env or ["  everything inside the bay"]
    r += ["",
          "PARTS (📦 library · 🇹🇳 local · ✈️ import)",
          "  T8 screw ~%.0f mm (Ender T8x8, cut) 📦 · T8 flange nut 📦 · 2 x Ø8 rod %.0f mm 📦 · 4 x LM8UU 🇹🇳 (or from the "
          "3 SCS8UU 📦) · 2 x 608 📦 · 2 x GT2 20T pulley 📦 + closed GT2 loop 🇹🇳 · NEMA17 📦 · MG996R + horn 📦 · "
          "625 + Ø5 shaft 📦/🇹🇳 · electromagnet 🇹🇳"
          % (G.Z_TOP_PLATE[1] - 2 - G.Z_PULLEY[0], G.Z_TOP_PLATE[1] - G.Z_BOT_PLATE[0]),
          "  printed ABS: carriage, top/bottom plates, motor plate, servo bracket + 625 cheek, arm (~%.0f g) + tip" % (arm_m * 1000)]
    C.save(doc, "FLIPPER_S", r)


main()
