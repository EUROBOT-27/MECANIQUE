# c_rolling_fc.py - Grail v2, variant C "ROLLING": ONE NEMA17, no servo.
# A half gear (sector, pitch radius R_S) is fixed to the arm. It rolls on a FIXED vertical rack while the carriage
# goes up, so the arm angle is tied to the height: angle = (z - z_pick) / R_S. A 180 deg turn takes pi * R_S of travel.
# The flip axis is at the same x as A/B; the pivot height at the pick / place follows from
#   (ROOF_TOP - LZ) - (G_H + LZ) = pi * R_S   ->   LZ = (ROOF_TOP - G_H - pi * R_S) / 2.
# Release: magnet off, carriage down REL mm: the arm rolls back a little, the magnet goes down + outward.
# The arm can never be at the wrong angle for its height (no lock, no servo); one motor does everything.
#   ARCHIVED 2026-11-20 (not chosen, see ../README.md). Run (from mechanical/Grail_v2): "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" archive/c_rolling_fc.py
#   -> CAD_FC/C_ROLLING.FCStd, CAD_FC/C_ROLLING_report.txt
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fc"))   # archived: common.py is in ../fc
import FreeCAD as App
from FreeCAD import Vector

import common as C


class G:
    R_S = 60.0                               # sector pitch radius (m1 -> 120 teeth on the full circle)
    LZ = (C.ROOF_TOP - C.G_H - math.pi * R_S) / 2
    PX = (C.X_PICK + C.X_PLACE) / 2
    Z_PICK = C.G_H + LZ
    Z_PLACE = C.ROOF_TOP - LZ
    REL = 6.0
    ARM_T, ARM_Y = 14.0, 10.0
    TIP_H = 10.0
    Y_SECTOR = (-50.0, -42.0)                # sector + fixed rack plane (behind the Grail, which spans y +-35)
    COL_X, COL_Y = 118.0, -76.0              # lift column (plate y -64..-58, behind the sector)
    MARGIN_DEG = 8.0                         # extra teeth at each end of the sector


def sector():
    """Half gear: upper half at the pick pose (+ margin), rim + hub + 3 spokes, on the axle."""
    yc = sum(G.Y_SECTOR) / 2
    w = G.Y_SECTOR[1] - G.Y_SECTOR[0]
    full = C.GC.pinion_m1(int(2 * G.R_S), w, (G.PX, yc, G.Z_PICK), "y")
    rim = full.cut(C.cyl(G.R_S - 8, w + 2, (G.PX, G.Y_SECTOR[0] - 1, G.Z_PICK), (0, 1, 0)))
    s = rim.fuse(C.cyl(12, w, (G.PX, G.Y_SECTOR[0], G.Z_PICK), (0, 1, 0)))
    for ang in (30, 90, 150):
        sp = C.box(0, G.R_S - 6, G.Y_SECTOR[0], G.Y_SECTOR[1], -4, 4)
        sp.rotate(Vector(0, 0, 0), Vector(0, -1, 0), ang)
        sp.translate(Vector(G.PX, 0, G.Z_PICK))
        s = s.fuse(sp)
    m = math.radians(G.MARGIN_DEG)
    keep = C.box(G.PX - 80, G.PX + 80, G.Y_SECTOR[0] - 1, G.Y_SECTOR[1] + 1,
                 G.Z_PICK - (G.R_S + 2) * math.sin(m), G.Z_PICK + 80)
    return s.common(keep).removeSplitter()


def build(doc, groups):
    arm, lift, fixed = {}, {}, {}
    zf = C.G_H
    arm["MAGNET"] = C.magnet_down(C.X_PICK, zf)
    ztip = zf + C.MAG_L
    arm["ARM_TIP"] = C.box(C.X_PICK - 16, C.X_PICK + 16, -G.ARM_Y / 2, G.ARM_Y / 2, ztip, ztip + G.TIP_H)
    arm["ARM"] = C.bar((G.PX, G.Z_PICK), (C.X_PICK, ztip + G.TIP_H / 2), G.ARM_T, -G.ARM_Y / 2, G.ARM_Y / 2)
    arm["ARM_HUB"] = C.cyl(12, G.ARM_Y, (G.PX, -G.ARM_Y / 2, G.Z_PICK), (0, 1, 0))
    arm["SECTOR_R60"] = sector()
    plate_y0 = G.COL_Y + 12
    arm["AXLE_8"] = C.cyl(4, G.ARM_Y / 2 - plate_y0 + 2, (G.PX, plate_y0 - 2, G.Z_PICK), (0, 1, 0))
    zr1 = G.Z_PLACE + 37.5
    fx, car = C.lift_unit(G.COL_X, G.COL_Y, 21.0, zr1 + 3, G.Z_PICK, 31.0, zr1, plate_x=(G.COL_X - 35, G.PX + 14))
    lift.update(car)
    lift["BEARING_BLOCK_2x608"] = C.box(G.PX - 14, G.PX + 14, plate_y0 + 6, G.Y_SECTOR[0] - 1.5,
                                        G.Z_PICK - 14, G.Z_PICK + 14).cut(C.cyl(4.2, 40, (G.PX, plate_y0, G.Z_PICK), (0, 1, 0)))
    fixed.update(fx)
    fixed["FLIP_RACK_FIXED"] = C.rack_x(G.Z_PICK - 15, G.Z_PLACE + 15, G.PX - G.R_S, G.Y_SECTOR[0], G.Y_SECTOR[1], +1)
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


def pose(lz):
    a = math.degrees(lz / G.R_S)
    return {"arm": C.rot_pl((G.PX, G.Z_PICK), a, lz), "lift": App.Placement(Vector(0, 0, lz), App.Rotation())}, a


def main():
    doc = App.newDocument("C_ROLLING")
    groups = {}
    arm, lift, fixed, gr = build(doc, groups)
    travel = G.Z_PLACE - G.Z_PICK
    steps = []
    n = 18
    for i in range(n + 1):
        lz = travel * i / n
        pls, a = pose(lz)
        steps.append(dict(label="z %5.1f turn %5.1f" % (G.Z_PICK + lz, a), pls=pls, held=True, gpl=pls["arm"],
                          final=(i == n)))
    for lz in (travel - 0.5, travel - 1.5):
        pass
    fin = steps[-1]["gpl"]
    for d in (2.0, G.REL):
        pls, a = pose(travel - d)
        steps.append(dict(label="off, down %.0f (turn %5.1f)" % (d, a), pls=pls, held=False, gpl=fin))
    parts = {n_: (s, "arm") for n_, s in arm.items()}
    parts.update({n_: (s, "lift") for n_, s in lift.items()})
    fixed_top = max(C.bb(s).ZMax for s in fixed.values())
    lines, worst = C.run_cycle(steps, parts, fixed_top)
    stow = steps[-1]["pls"]
    start_out = max(max(C.bb(C.moved(s, stow[g])).XMax for s, g in parts.values()),
                    max(C.bb(s).XMax for s in fixed.values())) - C.FACE

    for n_, s in arm.items():
        C.add(doc, "PLACE_" + n_, C.moved(s, fin), "GHOST_place", groups)
    for n_, s in lift.items():
        C.add(doc, "PLACE_" + n_, C.moved(s, steps[n]["pls"]["lift"]), "GHOST_place", groups)
    C.add(doc, "PLACE_GRAIL", C.moved(gr[0].fuse(gr[1]), fin), "GHOST_place", groups)
    mid, _ = pose(travel / 2)
    for n_, s in arm.items():
        C.add(doc, "MID_" + n_, C.moved(s, mid["arm"]), "GHOST_mid_90", groups)
    C.add(doc, "MID_GRAIL", C.moved(gr[0].fuse(gr[1]), mid["arm"]), "GHOST_mid_90", groups)

    xs, ys = [], []
    for s_ in steps[-6:]:
        for n_, (s, g) in parts.items():
            b = C.bb(C.moved(s, s_["pls"][g]))
            if b.ZMin < C.ROOF_TOP and b.ZMax > C.ROOF_BOT and b.XMin < C.FACE:
                xs += [b.XMin, min(b.XMax, C.FACE)]
                ys += [b.YMin, b.YMax]
    slot = (min(xs) - 2, C.FACE + 1, min(ys) - 2, max(ys) + 2) if xs else None
    for n_, s in C.robot_context(slot).items():
        C.add(doc, n_, s, "ROBOT_CONTEXT", groups)

    # torque about the axle (Grail + magnet + arm + sector) -> rack force -> lift pinion torque
    arm_parts = ("ARM", "ARM_TIP", "ARM_HUB", "SECTOR_R60")
    arm_m = sum(C.mass_of(arm[k]) for k in arm_parts)
    arm_c = C.com(arm["ARM"].fuse(arm["ARM_TIP"]))
    arm_m1 = sum(C.mass_of(arm[k]) for k in ("ARM", "ARM_TIP", "ARM_HUB"))
    sec_m, sec_c = C.mass_of(arm["SECTOR_R60"]), C.com(arm["SECTOR_R60"])
    mag_c = C.com(arm["MAGNET"])
    g_c = Vector(C.X_PICK, 0, C.G_H / 2)
    tmax, tz = 0.0, 0
    for i in range(0, 37):
        lz = travel * i / 36
        pl = pose(lz)[0]["arm"]
        t = C.torque_kgcm([(C.G_MASS, pl.multVec(g_c).x), (C.MAG_MASS, pl.multVec(mag_c).x),
                           (arm_m1, pl.multVec(arm_c).x), (sec_m, pl.multVec(sec_c).x)], G.PX)
        if t > tmax:
            tmax, tz = t, G.Z_PICK + lz
    m_moving = C.G_MASS + C.MAG_MASS + arm_m + 0.28 + 0.12 + 0.03
    f_rack = tmax / (G.R_S / 10.0)                 # kg-force at the sector teeth
    pin_t = (m_moving + f_rack) * 1.0              # kg.cm on the 20T (r 10 mm) lift pinion

    face_c = Vector(C.X_PICK, 0, C.G_H)
    p0 = fin.multVec(face_c)
    p1 = pose(travel - 1.0)[0]["arm"].multVec(face_c)
    d = p1 - p0
    rel = math.degrees(math.atan2(-d.z, abs(d.x)))
    q0 = steps[0]["gpl"].multVec(face_c)
    q1 = pose(1.0)[0]["arm"].multVec(face_c)
    dq = q1 - q0
    app = math.degrees(math.atan2(abs(dq.x), abs(dq.z)))

    r = ["GRAIL v2 - C ROLLING (one NEMA17: lift + flip by a half gear rolling on a fixed rack) - fc/c_rolling_fc.py",
         "Grail %.0f x %.0f x %.0f, %.0f g, picked by its top at x %.1f, placed upside down at x %.1f on the roof (top %.0f)"
         % (C.G_W, C.G_W, C.G_H, C.G_MASS * 1000, C.X_PICK, C.X_PLACE, C.ROOF_TOP),
         "Sector pitch radius %.0f (m1, %d teeth on 180 + 2 x %.0f deg); fixed rack pitch line x %.1f, y %.0f..%.0f"
         % (G.R_S, int(G.R_S * math.pi * (180 + 2 * G.MARGIN_DEG) / 180 / math.pi), G.MARGIN_DEG, G.PX - G.R_S,
            G.Y_SECTOR[0], G.Y_SECTOR[1]),
         "Axle x %.1f; z %.1f (pick) -> %.1f (place), travel %.1f = pi x %.0f. LZ = %.1f (axle above the Grail top at the pick)."
         % (G.PX, G.Z_PICK, G.Z_PLACE, travel, G.R_S, G.LZ),
         "",
         "CYCLE (bounding boxes, no clash check). act.out = actuator x past the right face (x %.0f)" % C.FACE]
    r += lines
    r += ["", "SUMMARY"] + C.summary_lines(worst, start_out)
    r += ["  roof slot for the arm: %s" % ("x %.1f..%.1f, y %.1f..%.1f" % slot if slot else "none"),
          "  pick: the magnet comes down onto the Grail %.0f deg off vertical (rolling path)" % app,
          "  release: magnet off, carriage down: the magnet face leaves the Grail %.0f deg below horizontal" % rel,
          "  torque about the axle max %.1f kg.cm (z %.0f) -> %.2f kg at the sector teeth; lift pinion ~%.1f kg.cm "
          "(NEMA17 ~4)" % (tmax, tz, f_rack, pin_t),
          "  at 100 s / e-stop the carriage can drop: the arm rolls back down with it (Grail already released)",
          "",
          "PARTS (📦 library · 🇹🇳 local · ✈️ import)",
          "  NEMA17 📦 · 2020 + V-wheels 📦 · lift rack m1 + 20T pinion printed (Seif's print fits) · fixed flip rack m1 "
          "printed · half gear R60 printed ABS · Ø8 axle + 2 x 608 📦 · electromagnet 🇹🇳 · NO servo",
          "  arm + sector ~%.0f g ABS (sector %.0f g)" % (arm_m * 1000, sec_m * 1000)]
    C.save(doc, "C_ROLLING", r)


main()
