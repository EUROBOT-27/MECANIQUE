# hub_d_fc.py - Central hub OPTION D, FreeCAD model (Ayoub, proposal 2026-11-18, not reviewed).
# One transfer actuator per stone: each of the 6 arms sits on its OWN ring on the hub axis, turned 0 -> 90 deg by its
# own N20 gear motor inside the hollow spine (pinion through a wall window, ring with internal teeth). The height
# change comes from a passive guide, so the one motor makes the whole move stack -> spin-safe position:
#   top: parallelogram + drag link (rod with 2 ball links) to a fixed anchor; middle: rigid arm.
#   bottom (cd.BOTTOM_FIXED, 2026-11-19): FIXED HOLDER - a bracket on a collar of the spine holds the bottom cup; no
#   ring, motor, spin, parallelogram or cam. The bottom stone is carried with the stack (walls) and left lying at the
#   start of tower mode, so each unit builds 2 towers (4 = the 4 tower zones [G D.4]).
#   With BOTTOM_FIXED = False: parallelogram + 623ZZ roller in the groove of a fixed cam sleeve (cam_sleeve(), earlier
#   one-sided ramp() kept for reference). Then the cup's MG90S stands the stone up and the shared hub lift sets it down.
# Every number comes from fc/check_d.py (which imports option C's fc/check_c.py), so this model and the box check agree.
# Concept-level parts: gears drawn as blocks / plain discs, no fasteners except the joint pins.
#
# Run (from mechanical/central-hub/option-d/):
#   "<FreeCAD>/bin/freecadcmd.exe" fc/hub_d_fc.py
# Writes CAD_FC/HUB_D_*.FCStd (poses), CAD_FC/HUB_D_HOME.step, hub_d_fc_report.txt (solid clash check of the poses).
# Frame: X = wheel axis (robot's left = -X), Y = forward, Z = up, origin = robot centre on the table. mm.
import os
import sys
import math
import numpy as np
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_d as cd            # noqa: E402
cc = cd.cc
V = App.Vector
OUT = os.path.join(ROOT, "CAD_FC")
NAMES = {"B": "bottom", "M": "middle", "T": "top"}
UNAME = {"F": "front", "R": "rear"}


# ---------------------------------------------------------------- helpers
def mat(Rm, off=(0, 0, 0)):
    return App.Matrix(Rm[0, 0], Rm[0, 1], Rm[0, 2], off[0],
                      Rm[1, 0], Rm[1, 1], Rm[1, 2], off[1],
                      Rm[2, 0], Rm[2, 1], Rm[2, 2], off[2],
                      0, 0, 0, 1)


def moved(shape, Rm, off=(0, 0, 0)):
    s = shape.copy(); s.transformShape(mat(np.asarray(Rm, float), off)); return s


def lbox(r0, r1, t0, t1, z0, z1):
    """box in a local (r, t, z) frame"""
    return Part.makeBox(r1 - r0, t1 - t0, z1 - z0, V(r0, t0, z0))


def obox(c, h, Rm):
    b = Part.makeBox(2 * h[0], 2 * h[1], 2 * h[2], V(-h[0], -h[1], -h[2]))
    return moved(b, Rm, c)


def cyl_between(p, q, r):
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = q - p
    return Part.makeCylinder(r, float(np.linalg.norm(d)), V(*p), V(*(d / np.linalg.norm(d))))


def pin_t(p, r=1.5, half=13.0):
    """joint pin along the local t axis through point p"""
    return Part.makeCylinder(r, 2 * half, V(p[0], -half, p[2]), V(0, 1, 0))


def comp(shapes):
    return Part.makeCompound([s for s in shapes if s is not None])


# ---------------------------------------------------------------- fixed robot (context, from option C's box model)
def robot():
    out = {}
    for b in cc.fixed_robot():
        if isinstance(b, cc.Cyl):
            out["mast"] = Part.makeCylinder(b.r, b.z1 - b.z0, V(0, 0, b.z0))
            continue
        lo, hi = b.c - b.h, b.c + b.h
        if b.name.startswith("wheel"):
            out[b.name] = Part.makeCylinder(38.5, hi[0] - lo[0], V(lo[0], 0, 38.5), V(1, 0, 0))
        else:
            out[b.name] = Part.makeBox(*(hi - lo), V(*lo))
    return out


# ---------------------------------------------------------------- hub (moves with the lift L)
def spine(L):
    z0, z1 = cc.SPINE_Z
    tube = Part.makeCylinder(cd.R_SPINE, z1 - z0, V(0, 0, z0)).cut(
        Part.makeCylinder(cd.R_SPINE - 4, z1 - z0, V(0, 0, z0)))
    for (u, lv), (rz0, rz1) in cd.RING_Z.items():
        pol, _ = cd.MOTOR[(u, lv)]
        tube = tube.cut(moved(lbox(cd.R_SPINE - 6, cd.R_SPINE + 2, -13, 13, rz0 - 0.5, rz1 + 0.5), cc.W(pol)))
    return moved(tube, np.eye(3), (0, 0, L))


def motor(key, L):
    """N20 (12 x 10) + gearbox + encoder, shaft up/down to the 22 T pinion in the ring band"""
    pol, where = cd.MOTOR[key]
    rz0, rz1 = cd.RING_Z[key]
    r = cd.MOT_R
    if where == "below":
        top = rz0 - 1
        gb, mo, en = (top - 9, top), (top - 24, top - 9), (top - 34, top - 24)
        shaft = (top, rz0 + 1)
    else:
        bot = rz1 + 1
        gb, mo, en = (bot, bot + 9), (bot + 9, bot + 24), (bot + 24, bot + 34)
        shaft = (rz1 - 1, bot)
    body = [lbox(r - 5, r + 5, -6, 6, *gb), lbox(r - 5, r + 5, -6, 6, *mo),
            Part.makeCylinder(6, en[1] - en[0], V(r, 0, en[0]))]
    sh = Part.makeCylinder(1.5, shaft[1] - shaft[0], V(r, 0, shaft[0]))
    pin = Part.makeCylinder(cd.PIN_R + 1, rz1 - rz0 - 2, V(r, 0, rz0 + 1))           # 22 T, m 1: tip r 12
    off = (0, 0, L)
    return moved(comp(body), cc.W(pol), off), moved(comp([sh, pin]), cc.W(pol), off)


def ramp(u, L):
    """fixed ramp for the bottom roller: 2.5 deg segments r 40-54 + a web back to the spine"""
    segs = []
    for ph in np.arange(cc.PARK - 5, 95.1, 2.5):
        rl = cc.roller_local(cc.bottom_alpha(min(max(ph, cc.PARK), 90)))
        segs.append(moved(lbox(40, 54, -1.4, 1.4, rl[2] + 5, rl[2] + 11), cc.W(cd.phi_abs(u, ph))))
        segs.append(moved(lbox(cd.R_SPINE, 40, -1.4, 1.4, rl[2] + 5, rl[2] + 11), cc.W(cd.phi_abs(u, ph))))
    return moved(comp(segs), np.eye(3), (0, 0, L))


SLEEVE_R = 54.0          # grooved cam sleeve: printed tube r R_SPINE..54 fixed on the spine (2026-11-19, replaces the ramps)
SLEEVE_CLEAR = 0.5      # roller clearance in the groove (each side, normal to the groove)
SLEEVE_WALL = 4.0        # sleeve material above the highest / below the lowest groove point


def groove_centre(phi):
    """roller centre (local r, z, hub at L = 0) and the groove slope (deg) at ring angle phi (clamped to the travel)"""
    p = min(max(phi, cc.PARK), 90.0)
    rl = cc.roller_local(cc.bottom_alpha(p))
    d = 0.25
    pa, pb = max(p - d, cc.PARK), min(p + d, 90.0)
    za = cc.roller_local(cc.bottom_alpha(pa))[2]; zb = cc.roller_local(cc.bottom_alpha(pb))[2]
    slope = 0.0 if pb <= pa else math.degrees(math.atan2(zb - za, rl[0] * math.radians(pb - pa)))
    if phi < cc.PARK or phi > 90.0:
        slope = 0.0
    return rl, slope


def cam_sleeve(L):
    """barrel cam: one printed tube on the spine with one groove per unit (front 0 -> 90, rear 180 -> 270 deg).
    The 623ZZ roller (axis along t, as before) runs in the groove, which is open toward the outside: the upper
    wall is the old ramp, the lower wall replaces the safety lip, so the roller is guided both ways."""
    ext = 9.0                                         # groove runs on past each end of the travel: roller radius + 3 deg
    phs = np.arange(cc.PARK - ext, 90.0 + ext + 0.01, 1.0)
    zs = [groove_centre(p)[0][2] for p in phs]
    hmax = 5.0 / math.cos(math.radians(34.0)) + SLEEVE_CLEAR
    z0, z1 = min(zs) - hmax - SLEEVE_WALL, max(zs) + hmax + SLEEVE_WALL
    tube = Part.makeCylinder(SLEEVE_R, z1 - z0, V(0, 0, z0)).cut(Part.makeCylinder(cd.R_SPINE, z1 - z0, V(0, 0, z0)))
    for u in "FR":
        wires = []
        for p in phs:
            rl, sl = groove_centre(p)
            h = 5.0 / math.cos(math.radians(sl)) + SLEEVE_CLEAR      # vertical half-gap for a Ø10 roller on a slope
            pts = [np.array([r, 0.0, rl[2] + dz]) for r, dz in ((39.0, -h), (SLEEVE_R + 3, -h), (SLEEVE_R + 3, h), (39.0, h))]
            Wm = cc.W(cd.phi_abs(u, p))
            pts = [V(*(Wm @ q)) for q in pts]
            wires.append(Part.makePolygon(pts + [pts[0]]))
        tube = tube.cut(Part.makeLoft(wires, True, True))
        # exact envelope on the tight bends (unpinch -> lift): the roller + clearance at every 0.5 deg of the travel
        c = SLEEVE_CLEAR
        rolls = []
        for p in np.arange(cc.PARK, 90.01, 0.5):
            rl = cc.roller_local(cc.bottom_alpha(p))
            cyl = Part.makeCylinder(5 + c, 4 + 2 * c, V(rl[0], -2 - c, rl[2]), V(0, 1, 0))
            rolls.append(moved(cyl, cc.W(cd.phi_abs(u, p))))
        tube = tube.cut(Part.makeCompound(rolls))
    return moved(tube, np.eye(3), (0, 0, L))


def collar(L):
    """fixed bottom holder: printed collar clamped on the spine, both units' brackets bolt to it"""
    z0, z1 = cd.COLLAR_Z
    c = Part.makeCylinder(cd.COLLAR_R, z1 - z0, V(0, 0, z0)).cut(Part.makeCylinder(cd.R_SPINE, z1 - z0, V(0, 0, z0)))
    return moved(c, np.eye(3), (0, 0, L))


def holder(u, L, held):
    """fixed bottom holder of unit u: bracket (beam + drop), fixed cup mount (no spin servo), cup; stone if held"""
    tip_r, cup = cc.TIP_R, cc.Z_STONE["B"]
    b0, b1 = cd.HOLD_BEAM_Z
    S = {"holder beam": lbox(cd.COLLAR_R, tip_r + 6, -12, 12, b0, b1),
         "holder drop": lbox(tip_r - 5, tip_r + 6, -16, 16, cup - 13, b0),
         "cup mount": comp([lbox(tip_r + 6, tip_r + 18, -11.5, 11.5, cup - 12, cup + 12),
                            Part.makeCylinder(12, 12, V(tip_r + 18, 0, cup), V(1, 0, 0))]),
         "cup": comp([Part.makeCylinder(4, 4, V(tip_r + 30, 0, cup), V(1, 0, 0)),
                      Part.makeCone(8, 15, 10.5, V(tip_r + 34, 0, cup), V(1, 0, 0))])}
    Wm = cc.W(cd.phi_abs(u, 0.0)); off = (0, 0, L)
    world = {"%sB %s" % (u, k): moved(v, Wm, off) for k, v in S.items()}
    stone = None
    if held:
        stone = moved(obox(np.array([tip_r + cc.CUP_OFF + 55.0, 0, cup]), (55.0, 160.0, 55.0), np.eye(3)), Wm, off)
    return world, stone


def anchor(u, L):
    A = cc.A_point(None, u)
    ang = math.atan2(A[1], A[0])
    s = np.array([math.cos(ang) * (cd.R_SPINE - 2), math.sin(ang) * (cd.R_SPINE - 2), A[2]])
    br = cyl_between(s, A, 5)
    ball = Part.makeSphere(4, V(*A))
    return moved(comp([br, ball]), np.eye(3), (0, 0, L))


def ring(key, phi, L):
    """ring r 35-48 with 72 internal teeth (blocks), turns with its arm"""
    rz0, rz1 = cd.RING_Z[key]
    body = Part.makeCylinder(cd.R_RING, rz1 - rz0, V(0, 0, rz0)).cut(
        Part.makeCylinder(cd.R_RING_IN + 1.2, rz1 - rz0, V(0, 0, rz0)))
    teeth = [moved(lbox(cd.R_RING_IN, cd.R_RING_IN + 1.3, -0.7, 0.7, rz0, rz1), cc.W(5.0 * i)) for i in range(72)]
    stop = lbox(cd.R_RING - 1, cd.R_RING + 4, -3, 3, rz0, rz1)                      # hard-stop lug (stops at -3 / 90)
    return moved(comp([body] + teeth + [stop]), cc.W(cd.phi_abs(key[0], phi)), (0, 0, L))


# ---------------------------------------------------------------- arm (local frame, then placed)
def arm(u, lv, phi, L, spin, held):
    """returns dict name -> world shape for the arm (incl. lug, pins, spin unit, cup) and the stone (or None)"""
    if lv == "B" and cd.BOTTOM_FIXED:
        return holder(u, L, held)
    key = (u, lv)
    rz0, rz1 = cd.RING_Z[key]
    S = {}
    if lv == "M":
        tip_r, zlt = cc.TIP_R, cc.CUP_END - cc.CUP_DZ["M"]
        S["lug"] = lbox(cd.R_RING - 2, 54, -12, 12, rz0, rz1)
        S["post"] = lbox(54, 74, -12, 12, rz0, cd.M_POST_TOP)                         # stops under the top rings' lugs
        S["beam"] = lbox(cd.M_BEAM_R0, tip_r - 5, -12, 12, cc.CUP_END + 8, cc.CUP_END + 20)
    else:
        a = cc.alpha_at(lv, phi)
        lr, lt, ur, ut = cc.link_pts(lv, a)
        tip_r, zlt = lt[0], lt[2]
        z0, z1 = (rz1, cc.ZR[lv] + cc.HP + 8) if lv == "T" else (cc.ZR[lv] - 8, rz1)
        S["lug"] = lbox(cd.R_RING - 2, cc.R0[lv] - 12, -12, 12, rz0, rz1)
        # post as a fork: 2 cheeks (t +-12 .. +-5) carry the root pins, a web joins them on the hub side
        S["post"] = comp([lbox(cc.R0[lv] - 12, cc.R0[lv] + 6, 5, 12, z0, z1), lbox(cc.R0[lv] - 12, cc.R0[lv] + 6, -12, -5, z0, z1),
                          lbox(cc.R0[lv] - 12, cc.R0[lv] - 7, -5, 5, z0, z1)])
        Rt = cc.R_t(a)
        S["lower link"] = obox((lr + lt) / 2, ((cc.LP + 12) / 2, 4.5, 4), Rt)
        S["upper link"] = obox((ur + ut) / 2, ((cc.LP + 12) / 2, 4.5, 4), Rt)
        S["pins"] = comp([pin_t(p) for p in (lr, lt, ur, ut)])
        if lv == "T":
            Bp = cc.B_local(a)
            base_ = np.array([Bp[0], 4.5, Bp[2]])
            S["ball stud"] = comp([cyl_between(base_, Bp, 2.5), Part.makeSphere(4, V(*Bp))])
        else:
            rl = cc.roller_local(a)
            lever_end = rl
            S["cam lever"] = comp([cyl_between(lr + [0, 0, 0], lever_end, 3)])
            S["roller"] = Part.makeCylinder(5, 4, V(rl[0], -2, rl[2]), V(0, 1, 0))       # 623ZZ: 10 x 4
    cup = zlt + cc.CUP_DZ[lv]
    # carrier: fork (2 cheeks) on the tip pins, plate toward the spin unit
    S["carrier"] = comp([lbox(tip_r - 5, tip_r + 6, 5, 16, zlt - 8, zlt + cc.HP + 8),
                         lbox(tip_r - 5, tip_r + 6, -16, -5, zlt - 8, zlt + cc.HP + 8),
                         lbox(tip_r + 2, tip_r + 6, -5, 5, zlt - 8, zlt + cc.HP + 8)])
    # spin: MG90S (output along r) + bearing housing (2 x MR/623 on the cup shaft) + VS2-S30 bellows cup
    S["spin servo"] = lbox(tip_r + 6, tip_r + 18, -11.5, 11.5, cup - 16, cup + 12.5)
    S["bearing housing"] = Part.makeCylinder(12, 12, V(tip_r + 18, 0, cup), V(1, 0, 0))
    S["cup"] = comp([Part.makeCylinder(4, 4, V(tip_r + 30, 0, cup), V(1, 0, 0)),
                     Part.makeCone(8, 15, 10.5, V(tip_r + 34, 0, cup), V(1, 0, 0))])
    Wm = cc.W(cd.phi_abs(u, phi)); off = (0, 0, L)
    world = {"%s%s %s" % (u, lv, k): moved(s, Wm, off) for k, s in S.items()}
    if lv == "T":
        Bw = Wm @ cc.B_local(cc.alpha_at("T", phi)) + np.array(off)
        A = cc.A_point(None, u) + np.array(off)
        d = (A - Bw) / np.linalg.norm(A - Bw)
        world["%sT rod" % u] = comp([cyl_between(Bw + 4.5 * d, A - 4.5 * d, 1.5),
                                     Part.makeSphere(4.5, V(*Bw)).cut(Part.makeSphere(4.05, V(*Bw))),
                                     Part.makeSphere(4.5, V(*A)).cut(Part.makeSphere(4.05, V(*A)))])
    stone = None
    if held:
        face = tip_r + cc.CUP_OFF
        dz = -cc.MID_CUP_DZ if lv == "M" else 0.0
        Rs = cc.R_r(spin)
        c = np.array([face, 0, cup]) + Rs @ np.array([55.0, 0, dz])
        stone = moved(obox(c, (55.0, 160.0, 55.0), Rs), Wm, off)
    return world, stone


# ---------------------------------------------------------------- pose -> named shapes
def pose(st):
    L = st["L"]
    P = {}                                           # name -> (group, shape)
    for k, s in robot().items(): P["robot " + k] = ("robot", s)
    P["spine"] = ("hub", spine(L))
    for key in cd.RING_Z:
        m, sp = motor(key, L)
        P["motor %s%s" % key] = ("hub", m); P["pinion %s%s" % key] = ("hub", sp)
        P["ring %s%s" % key] = (key[0] + key[1], ring(key, st["phi"][key], L))
    if cd.BOTTOM_FIXED:
        P["bottom collar"] = ("hub", collar(L))
    else:
        P["cam sleeve"] = ("hub", cam_sleeve(L))
    for u in ("F", "R"):
        P["anchor %sT" % u] = ("hub", anchor(u, L))
        for lv in ("B", "M", "T"):
            w, stone = arm(u, lv, st["phi"][(u, lv)], L, st["spin"][(u, lv)], st["held"][(u, lv)])
            for n, s in w.items():
                P[n] = ((u + lv + "rod") if n.endswith("rod") else (u + lv), s)
            if stone is not None: P["%s%s stone" % (u, lv)] = (u + lv + "stone", stone)
    return P


def allowed(na, ga, nb, gb, st):
    if ga == gb: return True                                         # inside one arm, or fixed hub parts together
    if {ga, gb} == {"hub", "robot"}: return "mast" in na + nb          # spine slides on the mast
    for (n1, g1, n2, g2) in ((na, ga, nb, gb), (nb, gb, na, ga)):
        if g1.endswith("stone") and g2 == g1[:2] and n2.endswith("cup"): return True
        if g1.endswith("rod"):
            if g2 == g1[:2] and n2.endswith(("ball stud", "lower link")): return True
            if n2 == "anchor %sT" % g1[0]: return True
        if n1 == "pinion " + g2 and n2.startswith("ring"): return True      # pinion meshes its own ring
        if g1.endswith("stone") and g2.endswith("stone") and g1[0] == g2[0]:
            if st["phi"][(g1[0], g1[1])] <= 0.01 and st["phi"][(g2[0], g2[1])] <= 0.01: return True
    return False


def common_vol(a, b):
    if not a.BoundBox.intersect(b.BoundBox): return 0.0
    v = 0.0
    for sa in a.Solids:
        if not sa.BoundBox.intersect(b.BoundBox): continue
        for sb in b.Solids:
            if sa.BoundBox.intersect(sb.BoundBox):
                try: v += sa.common(sb).Volume
                except Exception: pass
    return v


def check_pose(st):
    P = pose(st)
    names = list(P)
    bad = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            (ga, a), (gb, b) = P[na], P[nb]
            if allowed(na, ga, nb, gb, st): continue
            if ga.endswith("stone") and gb.endswith("stone"):
                a = a.copy(); a.scale(0.99, a.BoundBox.Center); b = b.copy(); b.scale(0.99, b.BoundBox.Center)
            v = common_vol(a, b)
            if v > 1.0: bad.append("%s x %s (%.0f mm3)" % (na, nb, v))
    zs = [s.BoundBox.ZMax for n, (g, s) in P.items() if g != "robot"]
    return P, bad, max(zs)


def save(name, P):
    doc = App.newDocument(name)
    groups = {}
    for n, (g, s) in P.items():
        if g not in groups:
            label = {"robot": "Robot_base330js", "hub": "Hub_fixed"}.get(g, None)
            if label is None:
                label = ("Stone_" if g.endswith("stone") else "Arm_") + UNAME[g[0]] + "_" + NAMES[g[1]] + ("_rod" if g.endswith("rod") else "")
            groups[g] = doc.addObject("App::DocumentObjectGroup", label)
        o = doc.addObject("Part::Feature", n.replace(" ", "_"))
        o.Shape = s
        groups[g].addObject(o)
    doc.recompute()
    path = os.path.join(OUT, name + ".FCStd")
    doc.saveAs(path)
    App.closeDocument(doc.Name)
    return path


def state(L=0.0, **kw):
    s = cd.new_state(); s["L"] = L
    for k, v in kw.items():
        u, lv, what = k[0], k[1], k[3:]
        s[what][(u, lv)] = v
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    LS = cc.L_SPIN
    poses = [
        ("HUB_D_HOME", "home: both stacks held, hub at 0", state()),
        ("HUB_D_1_FRONT_TOP_45", "front top stone half-way (turn 45, drag link), rear unit holds its stack",
         state(LS, FT_phi=45.0, FM_held=False, FB_held=False)),
        (("HUB_D_2_FRONT_TOP_SPIN", "front top stone at 90 spinning (45), front bottom left lying, rear holds its stack",
          state(LS, FT_phi=90.0, FT_spin=45.0, FM_held=False, FB_held=False)) if cd.BOTTOM_FIXED else
         ("HUB_D_2_FRONT_BOTTOM_SPIN", "front bottom stone at 90 spinning (45), rear unit holds its stack",
          state(LS, FB_phi=90.0, FB_spin=45.0, FM_held=False))),
        ("HUB_D_3_REAR_MIDDLE_UP", "rear middle stone at 90 and stood up, front unit holds its stack",
         state(LS, RM_phi=90.0, RM_spin=90.0)),
        ("HUB_D_DEPLOYED", "every arm at 90 and spun (perimeter pose, FAQ Q10), no stones",
         state(0.0, **{"%s%s_phi" % (u, lv): 90.0 for u in "FR" for lv in "BMT"},
               **{"%s%s_spin" % (u, lv): 90.0 for u in "FR" for lv in "BMT"},
               **{"%s%s_held" % (u, lv): False for u in "FR" for lv in "BMT"})),
    ]
    # extra check-only poses: every arm alone at 15 / 30 / 60 / 75 (the passive guides mid-way), in the build order
    # middle -> bottom -> top: the levels that went before are empty (their towers were left behind)
    extra = []
    before = {"M": "", "B": "M", "T": "MB"}
    if cd.BOTTOM_FIXED:
        before = {"M": "B", "T": "BM"}          # the bottom stone is left lying before the middle goes
    for u in "FR":
        for lv in cd.TRANSFER:
            for ph in (15.0, 30.0, 60.0, 75.0):
                kw = {"%s%s_phi" % (u, lv): ph}
                kw.update({"%s%s_held" % (u, x): False for x in before[lv]})
                extra.append(("%s %s at %g" % (UNAME[u], NAMES[lv], ph), state(LS, **kw)))
    R = ["Central hub - option D - FreeCAD model report (fc/hub_d_fc.py)", ""]
    R.append("Solid clash check (FreeCAD booleans, > 1 mm3) of the saved poses + every arm alone at 15/30/60/75 deg;")
    R.append("left out by design: parts of one arm, cup on its stone, rod on its stud + anchor, pinion in its ring,")
    R.append("stones of one stack, spine on the mast." + ("" if cd.BOTTOM_FIXED else
             " The bottom roller and lever ARE checked against the grooved cam sleeve."))
    if cd.BOTTOM_FIXED:
        R.append("BOTTOM_FIXED: bottom stone in a fixed holder (collar + bracket + cup), no ring / motor / spin; left lying")
        R.append("on the table at the start of tower mode, so 2 towers per unit (middle + top).")
    R.append("")
    allbad, ztop = 0, 0.0
    for name, label, st in poses:
        if name == "HUB_D_DEPLOYED":
            # the 3 arms of a unit all end at the same spot beside the robot: this pose never happens, it is the
            # envelope for the perimeter rule (every mechanism open at once, FAQ Q10). Saved, not clash-checked.
            P = pose(st); path = save(name, P)
            zmax = max(s.BoundBox.ZMax for g, s in P.values() if g != "robot"); ztop = max(ztop, zmax)
            R.append("%-28s %-80s highest %.1f  envelope only (3 arms of a unit share the end spot), not clash-checked" %
                     (name, label, zmax))
            continue
        P, bad, zmax = check_pose(st)
        ztop = max(ztop, zmax); allbad += len(bad)
        path = save(name, P)
        R.append("%-28s %-80s highest %.1f  %s" % (name, label, zmax, "no clashes" if not bad else "%d clashes" % len(bad)))
        R += ["    " + b for b in bad]
        if name == "HUB_D_HOME":
            Part.makeCompound([s for g, s in P.values() if g != "robot"]).exportStep(os.path.join(OUT, "HUB_D_HOME.step"))
    for label, st in extra:
        P, bad, zmax = check_pose(st)
        ztop = max(ztop, zmax); allbad += len(bad)
        if bad:
            R.append("%-28s highest %.1f  %d clashes" % (label, zmax, len(bad))); R += ["    " + b for b in bad]
    R.append("")
    R.append("extra poses (%d): %s" % (len(extra), "no clashes" if allbad == 0 else "see above"))
    R.append("highest point of hub + arms + held stones over all poses: %.1f mm (limit 350 [GR F.3])" % ztop)
    R.append("")
    if cd.BOTTOM_FIXED:
        R.append("Parts (both units): 4 rings (r 35-48, 72 T internal, m 1) + 4 N20 gear motors with encoder + 4 pinions 22 T;")
        R.append("hollow spine r 30/34 with 4 windows; 2 drag rods 157 mm (M3 + 2 ball links) + 2 anchors;")
        R.append("bottom: 1 collar (r %g/%g) + 2 fixed brackets + 2 fixed cup mounts;" % (cd.R_SPINE, cd.COLLAR_R))
        R.append("2 parallelogram arms (top, 2 links + 4 pins each) + 2 rigid arms (middle); 4 MG90S spin servos, 6 VS2-S30 cups;")
    else:
        R.append("Parts (both units): 6 rings (r 35-48, 72 T internal, m 1) + 6 N20 gear motors with encoder + 6 pinions 22 T;")
        R.append("hollow spine r 30/34 with 6 windows; 2 drag rods 157 mm (M3 + 2 ball links) + 2 anchors; 1 grooved cam sleeve")
        R.append("(r %g/%g, one groove per unit) + 2 x 623ZZ rollers;" % (cd.R_SPINE, SLEEVE_R))
        R.append("4 parallelogram arms (2 links + 4 pins each) + 2 rigid arms; 6 MG90S spin servos, 6 bearing housings, 6 VS2-S30 cups;")
    R.append("hub lift (MG996R + crank, from option C) and the mast are the robot's.")
    R.append("wrote CAD_FC/HUB_D_*.FCStd + CAD_FC/HUB_D_HOME.step")
    txt = "\n".join(R)
    with open(os.path.join(ROOT, "hub_d_fc_report.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)


main()
