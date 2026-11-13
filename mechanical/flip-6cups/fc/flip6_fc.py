# flip6_fc.py - FreeCAD model of the 6-cup flip mechanism (rebuilt from MECANISME_FLIP_V2, see README).
#
#   freecad flip6_fc.py           -> ../CAD/flip6.FCStd WITH colours + visibility (closes itself when done),
#                                    flip6.step (robot + the 3 stones in front, coloured), parts/*.step,
#                                    collision_report.txt
#   freecadcmd flip6_fc.py        -> same files, but the FCStd has no colours and opens with everything hidden
#                                    (no GUI = no display data saved): use it for the collision check only
#
# Actuators are the real parts we have or can buy in Tunisia (README "Actuators"), modelled from their datasheet
# dimensions: JGB37-520 gear motor + encoder on the crank, 3 x MG90S ejectors, 6 x DP-S30 cups in TPU holders,
# 6 x 12 V mini pumps + 6 vent valves, Ender endstop for homing. 688ZZ pins, stones 320 x 110 x 110. Kinematics in flip6_params.py, numeric checks in flip6_check.py.

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flip6_params as P  # noqa: E402

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402

V = App.Vector
ROOT = os.path.normpath(os.path.join(HERE, ".."))
BASE_STEP = os.path.normpath(os.path.join(ROOT, "..", "base_330", "base_330.step"))
BASE_Z = 13.5                     # base_330 bottom face above the table (base_330 README)
BASE_TOP = BASE_Z + 5.0

COLORS = {
    "table": (0.86, 0.88, 0.90), "base": (0.87, 0.78, 0.60), "wheel": (0.15, 0.15, 0.15),
    "column": (0.78, 0.80, 0.84), "bracket": (0.70, 0.72, 0.76), "motor": (0.25, 0.25, 0.28),
    "gearbox": (0.60, 0.62, 0.66), "crank": (0.85, 0.20, 0.15), "rocker": (0.20, 0.40, 0.85),
    "pin": (0.55, 0.55, 0.58), "plate": (0.50, 0.30, 0.80), "cup": (0.10, 0.10, 0.10),
    "servo": (0.20, 0.35, 0.80), "finger": (0.95, 0.55, 0.10), "stone": (0.82, 0.70, 0.52),
    "pump": (0.35, 0.35, 0.35), "valve": (0.85, 0.85, 0.80), "tpu": (0.95, 0.85, 0.20),
    "endstop": (0.15, 0.55, 0.25), "printed": (0.30, 0.30, 0.32),
}


def rot_y(deg):
    """Rotation turning the XZ plane like flip6_params.rot (u -> x, v -> z): about -Y."""
    return App.Rotation(V(0, -1, 0), deg)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_y(x, z, d, y0, y1):
    return Part.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))


def rounded_rect_xz(u0, u1, v0, v1, r, y0, y1):
    """Plate in the XZ plane (u along X, v along Z), extruded y0 -> y1."""
    core = box(u0 + r, u1 - r, y0, y1, v0, v1).fuse(box(u0, u1, y0, y1, v0 + r, v1 - r))
    for cu, cv in ((u0 + r, v0 + r), (u1 - r, v0 + r), (u0 + r, v1 - r), (u1 - r, v1 - r)):
        core = core.fuse(cyl_y(cu, cv, 2 * r, y0, y1))
    return core.removeSplitter()


def link(length, y0, y1, holes=True):
    """Bar from (0,0) to (length,0) in XZ, bosses Ø24 at both ends, Ø8 pin holes."""
    s = box(0, length, y0, y1, -P.LINK_W / 2, P.LINK_W / 2)
    s = s.fuse(cyl_y(0, 0, P.BOSS_D, y0, y1)).fuse(cyl_y(length, 0, P.BOSS_D, y0, y1))
    if holes:
        s = s.cut(cyl_y(0, 0, P.PIN_D, y0 - 1, y1 + 1)).cut(cyl_y(length, 0, P.PIN_D, y0 - 1, y1 + 1))
    return s.removeSplitter()


# ---------------------------------------------------------------- real actuators
def jgb_axis():
    """Gearbox / motor axis (x, z): 7 mm above the output shaft at O1."""
    return P.O1[0], P.O1[1] + P.JGB_OFFSET


def jgb_holes():
    ax, az = jgb_axis()
    return [(ax + P.JGB_HOLES_R * math.cos(math.radians(30 + 60 * i)),
             az + P.JGB_HOLES_R * math.sin(math.radians(30 + 60 * i))) for i in range(P.JGB_HOLES_N)]


def jgb37(face_y):
    """JGB37-520 with encoder, gearbox face at face_y, body going -Y, output shaft at O1 going +Y."""
    ax, az = jgb_axis()
    y = face_y
    s = cyl_y(ax, az, P.JGB_BOX_D, y - P.JGB_BOX_L, y)
    y -= P.JGB_BOX_L
    s = s.fuse(cyl_y(ax, az, P.JGB_MOT_D, y - P.JGB_MOT_L, y))
    y -= P.JGB_MOT_L
    s = s.fuse(cyl_y(ax, az, P.JGB_ENC_D, y - P.JGB_ENC_L, y))
    # encoder cable connector (6 pins) at the back, pointing up
    s = s.fuse(box(ax - 6, ax + 6, y - P.JGB_ENC_L + 3, y - 3, az + P.JGB_ENC_D / 2 - 2, az + P.JGB_ENC_D / 2 + 6))
    ox, oz = P.O1
    s = s.fuse(cyl_y(ox, oz, P.JGB_BOSS_D, face_y, face_y + P.JGB_BOSS_L))
    y1 = face_y + P.JGB_BOSS_L + P.JGB_SHAFT_L
    shaft = cyl_y(ox, oz, P.JGB_SHAFT_D, face_y + P.JGB_BOSS_L, y1)
    shaft = shaft.cut(box(ox - 5, ox + 5, face_y, y1 + 1, oz + 2.5, oz + 5))     # D flat (5.5 across)
    return s.fuse(shaft).removeSplitter()


def endstop():
    """Ender endstop (switch 20 x 10 x 6.5 on a 1.6 mm PCB) on the column front face, in the CRANK layer just past
    the crank's start angle (the crank never goes there): the crank edge presses the lever at s = 0 (home)."""
    a = P.PHI0 - math.copysign(math.radians(ENDSTOP_DEG), P.SWEEP)
    y = P.Y_COL[1]
    sw = box(-10, 10, y, y + 1.6 + 6.5, -5, 5)                  # radial x tangential, local
    sw = sw.fuse(box(-20, 14, y, y + 1.6, -8, 8))               # PCB, 2 x M3 into the column
    m = App.Placement(V(P.O1[0] + ENDSTOP_R * math.cos(a), 0, P.O1[1] + ENDSTOP_R * math.sin(a)),
                      rot_y(math.degrees(a))).toMatrix()
    return sw.transformGeometry(m)


ENDSTOP_R, ENDSTOP_DEG = 55.0, 18.0      # switch centre: radius from O1, angle past the crank's start position
PUMP_X0, PUMP_Y0 = 22.0, 50.0           # pump rack corner on the base (clear of the wheel y < 45, caster at x 0)


def pumps_valves():
    """6 pumps Ø31.8 x 66 (axis along Y) in 2 layers of 3, valves on top. Returns (pumps, valves) compounds."""
    pitch = P.PUMP_D + 2.0
    pumps, valves = [], []
    for layer in range(2):
        for i in range(3):
            x = PUMP_X0 + pitch / 2 + i * pitch
            z = BASE_TOP + 2 + P.PUMP_D / 2 + layer * pitch
            body = Part.makeCylinder(P.PUMP_D / 2, P.PUMP_L, V(x, PUMP_Y0, z), V(0, 1, 0))
            barb = Part.makeCylinder(2.5, 8, V(x, PUMP_Y0 + P.PUMP_L, z + 8), V(0, 1, 0))
            pumps.append(body.fuse(barb))
    ztop = BASE_TOP + 2 + 2 * pitch
    vx, vy, vz = P.VALVE
    for i in range(6):
        x = PUMP_X0 + 2 + (i % 3) * pitch
        y = PUMP_Y0 + 6 + (i // 3) * (vy + 14)
        valves.append(box(x, x + vx, y, y + vy, ztop, ztop + vz))
    return Part.makeCompound(pumps), Part.makeCompound(valves)


# ---------------------------------------------------------------- fixed parts (robot frame)
def fixed_parts():
    parts = {}
    parts["table"] = box(-500, 500, -350, 450, -2, 0)
    if os.path.exists(BASE_STEP):
        b = Part.read(BASE_STEP)
        b.translate(V(0, 0, BASE_Z))
        parts["base_330"] = b
    else:
        parts["base_330"] = box(-165, 165, -140, 140, BASE_Z, BASE_TOP)
    wheels = [Part.makeCylinder(45, 20, V(sx * 83.8, 0, 45), V(sx, 0, 0)) for sx in (1, -1)]
    parts["wheels"] = wheels[0].fuse(wheels[1])

    # column: 5 mm aluminium, F688ZZ seat at O1 (shaft), M6 tapped hole at O2 (ISO 7379 Ø8 shoulder screw)
    y0, y1 = P.Y_COL
    x0, x1 = min(P.O1[0], P.O2[0]) - 40, max(P.O1[0], P.O2[0]) + 45
    col = rounded_rect_xz(x0, x1, BASE_TOP, P.O2[1] + 28, 8, y0, y1)
    col = col.cut(cyl_y(P.O1[0], P.O1[1], P.JGB_BOSS_D + 1, y0 - 1, y1 + 1)).cut(cyl_y(P.O2[0], P.O2[1], 5, y0 - 1, y1 + 1))
    for hx, hz in jgb_holes():
        col = col.cut(cyl_y(hx, hz, 3.4, y0 - 1, y1 + 1))
    parts["column"] = col
    # two angle brackets, column -> base plate (clear of the gearbox)
    br = []
    for bx0, bx1 in ((x0 + 2, x0 + 22), (x1 - 22, x1 - 2)):
        br.append(box(bx0, bx1, y0 - 30, y0, BASE_TOP, BASE_TOP + 4).fuse(box(bx0, bx1, y0 - 4, y0, BASE_TOP, BASE_TOP + 30)))
    parts["brackets"] = br[0].fuse(br[1])

    # JGB37-520 + Hall encoder behind the column, DIRECT on the crank. Gearbox face bolted to the column back
    # (6 x M3 through the column), boss in a Ø13 hole, Ø6 D-shaft out to the crank hub. The output is 7 mm off the
    # gearbox axis: body placed ABOVE the shaft (bottom 38.9 mm, clear of the base plate).
    parts["motor"] = jgb37(y0)
    # rocker ground pin: Ø8 shaft fixed in the column, e-clip on the front (the plate sweeps over it, 4 mm gap)
    parts["pin_O2"] = cyl_y(P.O2[0], P.O2[1], P.PIN_D, y0, P.Y_ROCK[1] + 1)
    # homing: Ender endstop on the column front face, lever touched by the crank at s = 0
    parts["endstop"] = endstop()
    # vacuum: 6 pumps (one per cup) in 2 layers of 3, axis along Y, + 6 vent valves on top
    parts["pumps"], parts["valves"] = pumps_valves()
    return parts


# ---------------------------------------------------------------- moving parts, local frames
def crank_local():
    """Crank along +X from O1 (at origin), its pin at the far end reaching the plate."""
    s = link(P.R1, *P.Y_CRANK)
    s = s.fuse(cyl_y(0, 0, 22, P.Y_COL[1] + 0.5, P.Y_CRANK[0]))           # clamp hub on the D8 shaft
    return s.removeSplitter()


def crank_pin_local():
    return cyl_y(P.R1, 0, P.PIN_D, P.Y_CRANK[0], P.Y_PLATE[0])


def rocker_local():
    return link(P.R2, *P.Y_ROCK)


def rocker_pin_local():
    return cyl_y(P.R2, 0, P.PIN_D, P.Y_ROCK[0], P.Y_PLATE[0])


def plate_local():
    """Cup plate in the plate frame (u, v) = (x, z). 3 mm aluminium, 6 cup holes, 2 pin holes, 4 pockets."""
    y0, y1 = P.Y_PLATE
    s = rounded_rect_xz(-P.PLATE_U, P.PLATE_U, -P.PLATE_V, P.PLATE_V, P.PLATE_R, y0, y1)
    for u, v in P.CUPS:
        s = s.cut(cyl_y(u, v, 10.5, y0 - 1, y1 + 1))
    for u, v in (P.P1, P.P2):
        s = s.cut(cyl_y(u, v, P.PIN_D, y0 - 1, y1 + 1))
    # lightening pockets: keep >= 15 mm of metal around each cup base and pin boss
    pockets = [(-55, -18, -125, 125), (20, 55, -125, 125),            # between the cup columns
               (62, 98, -85, -25), (62, 98, 25, 85), (-98, -62, 25, 85)]   # between rows (not around P1)
    for u0, u1, v0, v1 in pockets:
        s = s.cut(rounded_rect_xz(u0, u1, v0, v1, 6, y0 - 1, y1 + 1))
    # pin bosses behind the plate (spacers to the links)
    for (u, v), yb in ((P.P1, P.Y_CRANK[1]), (P.P2, P.Y_ROCK[1])):
        s = s.fuse(cyl_y(u, v, 16, yb + 0.5, y0).cut(cyl_y(u, v, P.PIN_D, yb, y0 + 1)))
    return s.removeSplitter()


def cups_local():
    """DP-S30 in a printed TPU holder: holder Ø20 x 17 on the plate front (stem through the plate, 2.5 mm lock nut
    behind it: the rocker runs 4 mm behind the plate), Ø4 side barb (hose on the front face)."""
    y = P.Y_PLATE[1]
    out = []
    for u, v in P.CUPS:
        holder = cyl_y(u, v, 20.0, P.Y_PLATE[0] - 2.5, y + P.CUP_HOLDER)
        barb = Part.makeCylinder(2.0, 16, V(u + 6, y + 8, v), V(1, 0, 0))
        out.append(holder.fuse(barb))
    return out


def cup_bellows_local():
    """DP-S30 bellows: Ø18 neck, Ø24 fold, lip cone to Ø30 at the stone face."""
    y = P.Y_PLATE[1] + P.CUP_HOLDER
    out = []
    for u, v in P.CUPS:
        b = cyl_y(u, v, 18, y, y + 6).fuse(cyl_y(u, v, 24, y + 6, y + 12))
        out.append(b.fuse(Part.makeCone(12, P.CUP_D / 2, P.CUP_BELLOWS - 12, V(u, y + 12, v), V(0, 1, 0))))
    return out


EJ_V = [v + 20 for v in P.CUP_V]          # low-v end of each MG90S's ears (servo clear of the Ø30 cup)
EJ_U = -P.PLATE_U                         # left edge in the start pose = bottom edge when upright
EJECT_PUSH = 19.5                         # as V2: the roller pushes the stone 19.5 mm
FINGER_Y = P.Y_STONE + EJECT_PUSH - 29.0  # pivot: arm 25 + roller radius 4 reach the push distance at 90 deg
SERVO_UTOP = EJ_U + 4.5                   # case top 4.5 mm inside the plate edge: boss + spline + finger hub at the edge


def mg90s(u_top, y_c, v0):
    """MG90S lying with its spline along -u: case top at u_top, case from u_top to u_top + 28.5 (into the plate
    area), W 12.2 along y centred on y_c, ears from v0 to v0 + 32.2. Spline axis at v = mg90_shaft_v(v0), y = y_c."""
    eo = (P.MG90_EAR_L - P.MG90_L) / 2
    va = v0 + eo
    case = box(u_top, u_top + P.MG90_H, y_c - P.MG90_W / 2, y_c + P.MG90_W / 2, va, va + P.MG90_L)
    ue = u_top + P.MG90_H - P.MG90_EAR_Z - P.MG90_EAR_T
    ears = box(ue, ue + P.MG90_EAR_T, y_c - P.MG90_W / 2, y_c + P.MG90_W / 2, v0, v0 + P.MG90_EAR_L)
    vs = mg90_shaft_v(v0)
    boss = Part.makeCylinder(5.9, 2.5, V(u_top, y_c, vs), V(-1, 0, 0))
    spline = Part.makeCylinder(2.4, 1.5, V(u_top - 2.5, y_c, vs), V(-1, 0, 0))
    return case.fuse(ears).fuse(boss).fuse(spline).removeSplitter()


def mg90_shaft_v(v0):
    return v0 + (P.MG90_EAR_L - P.MG90_L) / 2 + P.MG90_SHAFT_E


def servos_local():
    return [mg90s(SERVO_UTOP, FINGER_Y, v) for v in EJ_V]


def servo_brackets_local():
    """Printed bracket per servo (PLA/ABS): flat foot screwed on the plate front (2 x M3, nuts behind), a wall under
    the ears (2 x M2 self-tapping into it), the case sits on the foot."""
    y = P.Y_PLATE[1]
    out = []
    ue = SERVO_UTOP + P.MG90_H - P.MG90_EAR_Z          # ear underside (u)
    for v in EJ_V:
        wall = box(ue, ue + 4, y, FINGER_Y + P.MG90_W / 2, v - 2, v + P.MG90_EAR_L + 2)
        foot = box(SERVO_UTOP, ue + 4, y, FINGER_Y - P.MG90_W / 2 - 0.3, v - 2, v + P.MG90_EAR_L + 2)
        out.append(wall.fuse(foot).removeSplitter())
    return out


def finger_local(i, angle):
    """Finger: 25 mm arm + Ø8 roller, pivot on the servo shaft (axis -u) at the plate edge.
    angle 0 = folded along -v (in the cup gap), 90 = pointing +y (roller tip 19.5 mm past the stone face)."""
    v = mg90_shaft_v(EJ_V[i])                   # on the MG90S spline axis
    yp = FINGER_Y
    arm = box(-4, 0, -3, 3, -25, 0)                 # local: pivot at origin, arm along -z (= -v), x = -u side
    arm = arm.fuse(Part.makeCylinder(4, 6, V(-5, 0, -25), V(1, 0, 0)))
    m = App.Placement(V(EJ_U - 1, yp, v), App.Rotation(V(1, 0, 0), -angle)).toMatrix()   # -z -> +y
    return arm.transformGeometry(m)


def stones_local(n_stacks):
    """Stones in the plate frame: long axis along u, faces touching the cups."""
    out = []
    for u, v in P.stones(n_stacks):
        out.append(box(u - P.STONE_L / 2, u + P.STONE_L / 2, P.Y_STONE, P.Y_STONE + P.STONE_W,
                       v - P.STONE_W / 2, v + P.STONE_W / 2))
    return out


# ---------------------------------------------------------------- placements for a crank progress s
def placements(s):
    pose, p1, p2 = P.pose_at(s)
    plate = App.Placement(V(pose[0], 0, pose[1]), rot_y(math.degrees(pose[2])))
    a1 = math.degrees(math.atan2(p1[1] - P.O1[1], p1[0] - P.O1[0]))
    a2 = math.degrees(math.atan2(p2[1] - P.O2[1], p2[0] - P.O2[0]))
    crank = App.Placement(V(P.O1[0], 0, P.O1[1]), rot_y(a1))
    rocker = App.Placement(V(P.O2[0], 0, P.O2[1]), rot_y(a2))
    return dict(plate=plate, crank=crank, rocker=rocker, pose=pose)


def build(doc, n_stacks=1, s=0.0):
    """Create all objects (with colours if a GUI is up). Returns {name: (obj, kind)} kind = fixed/plate/crank/rocker."""
    objs = {}

    def add(name, shape, color, kind):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        if App.GuiUp:
            o.ViewObject.ShapeColor = color
            if name.startswith("Stone"):
                o.ViewObject.LineColor = (0.45, 0.35, 0.22)
        objs[name] = (o, kind)
        return o

    for n, sh in fixed_parts().items():
        key = {"base_330": "base", "wheels": "wheel", "brackets": "bracket", "pin_O2": "pin",
               "pumps": "pump", "valves": "valve"}.get(n, n)
        add(n, sh, COLORS[key], "fixed")
    add("Crank", crank_local(), COLORS["crank"], "crank")
    add("Crank_pin", crank_pin_local(), COLORS["pin"], "crank")
    add("Rocker", rocker_local(), COLORS["rocker"], "rocker")
    add("Rocker_pin", rocker_pin_local(), COLORS["pin"], "rocker")
    add("Plate", plate_local(), COLORS["plate"], "plate")
    for i, c in enumerate(cups_local()):
        add("Cup_%d" % (i + 1), c, COLORS["tpu"], "plate")
    for i, c in enumerate(cup_bellows_local()):
        add("DPS30_%d" % (i + 1), c, COLORS["cup"], "plate")
    for i, (sv, bk) in enumerate(zip(servos_local(), servo_brackets_local())):
        add("Servo_%d" % (i + 1), sv, COLORS["servo"], "plate")
        add("Servo_bracket_%d" % (i + 1), bk, COLORS["printed"], "plate")
        add("Finger_%d" % (i + 1), finger_local(i, 0), COLORS["finger"], "plate")
    for i, st in enumerate(stones_local(2)):
        o = add("Stone_%d" % (i + 1), st, COLORS["stone"], "plate")
    set_stones(objs, n_stacks)
    pose(objs, s)
    doc.recompute()
    return objs


def stone_names(n_stacks):
    """Stone objects used: 1 stack = the 3 centred ones (built separately), 2 stacks = Stone_1..6."""
    return ["Stone_%d" % (i + 1) for i in range(6)] if n_stacks == 2 else ["StoneC_%d" % (i + 1) for i in range(3)]


def set_stones(objs, n_stacks):
    doc = next(iter(objs.values()))[0].Document
    if "StoneC_1" not in objs:
        for i, st in enumerate(stones_local(1)):
            o = doc.addObject("Part::Feature", "StoneC_%d" % (i + 1))
            o.Shape = st
            if App.GuiUp:
                o.ViewObject.ShapeColor = COLORS["stone"]
                o.ViewObject.LineColor = (0.45, 0.35, 0.22)
            objs[o.Name] = (o, "plate")
    used = set(stone_names(n_stacks))
    for n, (o, k) in objs.items():
        if n.startswith("Stone"):
            if App.GuiUp:
                o.ViewObject.Visibility = n in used
            o.Label = n if n in used else n + " (other case)"


def pose(objs, s):
    pl = placements(s)
    for n, (o, kind) in objs.items():
        if kind in ("plate", "crank", "rocker"):
            o.Placement = pl[kind]
    return pl


# ---------------------------------------------------------------- collisions
def collisions(objs, s, n_stacks, ignore=()):
    """Volume of every pair of solids that overlap (> 1 mm3) at crank progress s."""
    pose(objs, s)
    used = set(stone_names(n_stacks))
    shapes = [(n, o.Shape) for n, (o, k) in objs.items()
              if not (n.startswith("Stone") and n not in used) and n != "table"]
    pairs = []
    # expected contacts: pins in their holes / links, cups on stones, stones on each other
    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            (a, sa), (b, sb) = shapes[i], shapes[j]
            if (a, b) in ignore or (b, a) in ignore:
                continue
            if not sa.BoundBox.intersect(sb.BoundBox):
                continue
            v = sa.common(sb).Volume
            if v > 1.0:
                pairs.append((a, b, v))
    return pairs


EXPECTED = {("Crank", "Crank_pin"), ("Rocker", "Rocker_pin"), ("Plate", "Crank_pin"), ("Plate", "Rocker_pin"),
            ("column", "pin_O2"), ("Rocker", "pin_O2"), ("motor", "Crank"), ("column", "endstop"),
            ("Plate", "Cup_1"), ("Plate", "Cup_2"), ("Plate", "Cup_3"), ("Plate", "Cup_4"), ("Plate", "Cup_5"),
            ("Plate", "Cup_6"), ("column", "brackets"), ("base_330", "brackets"),
            ("Servo_1", "Finger_1"), ("Servo_2", "Finger_2"), ("Servo_3", "Finger_3")}
EXPECTED |= {("Cup_%d" % i, "DPS30_%d" % i) for i in range(1, 7)}
EXPECTED |= {("Servo_bracket_%d" % i, n) for i in range(1, 4) for n in ("Plate", "Servo_%d" % i)}


# names shown in the FreeCAD tree and in the STEP (object Names stay short: the GIF script uses them)
LABELS = {"base_330": "Base_plate_330", "wheels": "Drive_wheels", "column": "Column_alu_5mm",
          "brackets": "Column_angle_brackets", "motor": "Flip_motor_JGB37-520_encoder", "pin_O2": "Rocker_ground_pin_D8",
          "endstop": "Home_endstop_Ender", "pumps": "Vacuum_pumps_12V_x6", "valves": "Vent_valves_12V_x6",
          "Crank": "Crank", "Crank_pin": "Crank_pin_D8", "Rocker": "Rocker", "Rocker_pin": "Rocker_pin_D8",
          "Plate": "Cup_plate_alu_3mm"}
LABELS.update({"Cup_%d" % i: "Cup_holder_TPU_%d" % i for i in range(1, 7)})
LABELS.update({"DPS30_%d" % i: "Suction_cup_DP-S30_%d" % i for i in range(1, 7)})
LABELS.update({"Servo_%d" % i: "Ejector_servo_MG90S_%d" % i for i in range(1, 4)})
LABELS.update({"Servo_bracket_%d" % i: "Ejector_servo_bracket_%d" % i for i in range(1, 4)})
LABELS.update({"Finger_%d" % i: "Ejector_finger_%d" % i for i in range(1, 4)})
LABELS.update({"StoneC_%d" % i: "Stone_%d_320x110x110" % i for i in range(1, 4)})
GROUPS = [("Robot_base", ["base_330", "wheels"]),
          ("Flip_drive", ["column", "brackets", "motor", "endstop", "pin_O2"]),
          ("Four_bar", ["Crank", "Crank_pin", "Rocker", "Rocker_pin"]),
          ("Cup_plate", ["Plate"]),
          ("Suction_cups", ["Cup_", "DPS30_"]),
          ("Ejectors", ["Servo_", "Finger_"]),
          ("Vacuum", ["pumps", "valves"]),
          ("Stones_3_in_front", ["StoneC_"])]


def main():
    out = os.path.join(ROOT, "CAD")
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    if "flip6" in App.listDocuments():
        App.closeDocument("flip6")
    doc = App.newDocument("flip6")
    objs = build(doc, 1, 0.0)

    lines = []
    for n_stacks, ss in ((1, [i / 20 for i in range(21)]), (2, [0.0])):
        worst = []
        for s in ss:
            worst += [(s,) + p for p in collisions(objs, s, n_stacks, EXPECTED)]
        lines.append("%d stack(s): %d unexpected overlaps over %d poses" % (n_stacks, len(worst), len(ss)))
        for w in worst[:20]:
            lines.append("   s=%.2f  %s x %s  %.0f mm3" % w)
    pose(objs, 0.0)
    set_stones(objs, 1)                      # case A shown: the quarry stack (3 stones) in front of the robot
    if App.GuiUp:                            # see the cups through the stones
        for n, (o, k) in objs.items():
            if n.startswith("Stone"):
                o.ViewObject.Transparency = 50
    doc.recompute()
    # The FCStd and the STEP hold the SAME parts: robot + the 3 stones held in front (case A, start pose).
    # The table and the 6-stone set (case B) are only for the checks and the GIF: removed here.
    keep = [o for n, (o, k) in objs.items() if n != "table" and not n.startswith("Stone_")]
    for o in keep:
        o.Label = LABELS.get(o.Name, o.Name)
    step = os.path.join(out, "flip6.step")
    if App.GuiUp:
        import ImportGui                     # keeps the colours and names (SolidWorks reads them)
        ImportGui.export(keep, step)
    else:
        Part.makeCompound([o.Shape.copy() for o in keep]).exportStep(step)
    for n in ["table"] + ["Stone_%d" % i for i in range(1, 7)]:
        doc.removeObject(n)
    for gname, members in GROUPS:
        g = doc.addObject("App::DocumentObjectGroup", gname)
        for o in keep:
            if any(o.Name == m or (m.endswith("_") and o.Name.startswith(m)) for m in members):
                g.addObject(o)
    doc.recompute()
    doc.saveAs(os.path.join(out, "flip6.FCStd"))
    for n in ("column", "Crank", "Rocker", "Plate"):
        o = objs[n][0]
        sh = o.Shape.copy()
        sh.Placement = App.Placement()
        sh.exportStep(os.path.join(out, "parts", "%s.step" % n.lower()))
    plate_mass = objs["Plate"][0].Shape.Volume * 2.7e-6
    lines.append("plate (3 mm aluminium) mass %.0f g" % (plate_mass * 1000))
    print("\n".join(lines))
    with open(os.path.join(ROOT, "collision_report.txt"), "w") as f:
        f.write("6-cup flip - solid overlap check (flip6_fc.py), crank progress s = 0..1 in 0.05 steps\n"
                "Expected contacts ignored: pins in links/plate, cup holders in the plate, motor shaft in the crank hub,\n"
                "servo brackets on the plate, column brackets.\n\n")
        f.write("\n".join(lines) + "\n")


_LAUNCHED = any(os.path.basename(str(a)).lower() == "flip6_fc.py" for a in sys.argv)   # not when imported (GIF)
if _LAUNCHED and App.GuiUp:                       # freecad flip6_fc.py: build, save with colours, close
    import FreeCADGui as Gui
    from PySide import QtCore

    def _gui_run():
        try:
            main()
        except Exception:
            import tempfile
            import traceback
            with open(os.path.join(tempfile.gettempdir(), "flip6_fc_error.txt"), "w") as f:
                f.write(traceback.format_exc())
        Gui.getMainWindow().close()

    QtCore.QTimer.singleShot(2000, _gui_run)
elif __name__ in ("__main__", "flip6_fc") and not App.GuiUp:
    main()
