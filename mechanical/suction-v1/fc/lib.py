# Module B (suction-v1) shared builders: primitives, bought-part models, tube with real bends, export.
# Every generator: `import lib` (adds this folder to sys.path), builds its parts, calls lib.save(...).
# Run a generator with:  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/<generator>.py   (from suction-v1/)
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import FreeCAD as App
import Part, MeshPart
from FreeCAD import Vector as V
import params as P

OUT_ROOT = os.path.normpath(os.path.join(HERE, "..", "CAD_FC"))
Y = V(0, 1, 0)


# ---------------------------------------------------------------- primitives (cup axis = Y)
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def ycyl(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), Y)


def xcyl(r, x0, x1, y=0.0, z=0.0):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def zcyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def ring_y(r_out, r_in, y0, y1):
    return ycyl(r_out, y0, y1).cut(ycyl(r_in, y0 - 1, y1 + 1))


def poly_xz(pts, y0, y1):
    """Closed outline (x, z) in the plane y = y0, extruded to y1."""
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, y1 - y0, 0))


def hex_y(af, y0, y1, x=0.0, z=0.0, rot=0.0):
    rc = af / math.sqrt(3)
    pts = [(x + rc * math.cos(math.radians(rot + 60 * k)), z + rc * math.sin(math.radians(rot + 60 * k))) for k in range(6)]
    return poly_xz(pts, y0, y1)


def revolve_y(profile):
    """profile = [(r, y), ...] closed in the half plane r >= 0; revolved around the Y axis."""
    w = Part.makePolygon([V(r, y, 0) for r, y in profile] + [V(profile[0][0], profile[0][1], 0)])
    return Part.Face(w).revolve(V(0, 0, 0), Y, 360)


def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()


def solid(add, cut=()):
    s = fuse(list(add))
    for c in cut:
        s = s.cut(c)
    return s.removeSplitter()


def polar(r, angles_deg):
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in angles_deg]


def bolt_holes(y0, y1, r=None, d=P.M3_CLEAR):
    r = P.STATION["bolt_r"] if r is None else r
    return [ycyl(d / 2, y0, y1, x, z) for x, z in polar(r, P.STATION["bolt_a"])]


def spiral_slots(r_in, r_out, y0, y1, n=3, sweep_deg=200.0, width=2.4, steps=24, a0_deg=0.0):
    """n spiral slots between r_in and r_out (TPU spring disc), as solids to cut."""
    out = []
    for k in range(n):
        a0 = math.radians(a0_deg) + 2 * math.pi * k / n
        inner, outer = [], []
        for i in range(steps + 1):
            t = i / steps
            r = r_in + (r_out - r_in) * t
            a = a0 + math.radians(sweep_deg) * t
            inner.append(((r - width / 2) * math.cos(a), (r - width / 2) * math.sin(a)))
            outer.append(((r + width / 2) * math.cos(a), (r + width / 2) * math.sin(a)))
        out.append(poly_xz(inner + list(reversed(outer)), y0, y1))
    return out


def spur_gear(n, m, y0, y1, bore_r=0.0, x=0.0, z=0.0, rot_deg=0.0):
    """Spur gear in the xz plane (axis along Y), trapezoid teeth (concept level; real involutes at fabrication)."""
    rp = n * m / 2.0
    ra, rf = rp + m, rp - 1.25 * m
    p = 2 * math.pi / n
    pts = []
    for k in range(n):
        a0 = math.radians(rot_deg) + k * p
        for r, f in ((rf, -0.30), (ra, -0.12), (ra, 0.12), (rf, 0.30)):
            pts.append((x + r * math.cos(a0 + f * p), z + r * math.sin(a0 + f * p)))
    g = poly_xz(pts, y0, y1)
    if bore_r > 0:
        g = g.cut(ycyl(bore_r, y0 - 1, y1 + 1, x, z))
    return g


def servo_mg996r():
    """Real MG996R model (GrabCAD, as in clapets v7): shaft axis = +z at the origin, body below (z -28..12),
    body x -30.2..10.2 (shaft 10.2 from the end), ears x -37..-30.2 / 10.2..17."""
    d = os.path.join(HERE, "..", "..", "resources", "mg996r-servo-3.snapshot.9")
    return Part.read(os.path.join(d, "mg996R_v2.step"))


# ---------------------------------------------------------------- bought parts (DATASHEET sizes in params.py)
def cup(y_back):
    """DP-S30 bellows cup, neck back face at y_back, lip towards +y. Returns (shape, y_lip)."""
    c = P.CUP
    h, R = c["h_free"], c["d_lip"] / 2
    yl = y_back + h
    prof = [(0, y_back), (c["d_neck"] / 2, y_back), (c["d_neck"] / 2, y_back + 4), (11.0, y_back + 5), (12.5, y_back + 8),
            (10.5, y_back + 10.5), (13.5, y_back + 13.5), (R, y_back + h - 1.0), (R, yl), (R - 2.0, yl), (R - 3.0, y_back + h - 1.5),
            (0, y_back + h - 3.0)]
    return revolve_y(prof), yl


def elbow(y_hex_front, out_dir=(1.0, 0.0)):
    """PL4-M5 swivel elbow: hex front face at y_hex_front, thread forward, outlet radial in the xz direction out_dir.
    Returns (shape, port_point, port_dir, outlet_axis_y)."""
    e = P.ELBOW_PL4_M5
    yh = y_hex_front
    dx, dz = out_dir
    n = math.hypot(dx, dz); dx, dz = dx / n, dz / n
    th = ycyl(2.5, yh, yh + e["thread_l"])
    hx = hex_y(e["hex_af"], yh - e["hex_h"], yh)
    body = ycyl(e["body_d"] / 2, yh - e["hex_h"] - e["body_l"], yh - e["hex_h"])
    ya = yh - e["axis_from_hex"]
    outlet = Part.makeCylinder(e["body_d"] / 2, e["reach"], V(0, ya, 0), V(dx, 0, dz))
    port = V(dx * e["reach"], ya, dz * e["reach"])
    return fuse([th, hx, body, outlet]), port, V(dx, 0, dz), ya


def m3_screw(p, d, length, head="SH"):
    """Socket head M3: head on p, shank along unit vector d."""
    d = V(*d) if not isinstance(d, V) else d
    hd = Part.makeCylinder(2.75, 3.0, p - d * 3.0, d)
    sh = Part.makeCylinder(1.5, length, p, d)
    return hd.fuse(sh)


def screw(p, d, length, m=3):
    """Socket head screw M<m>: head on p (outside), shank along unit vector d."""
    d = V(*d) if not isinstance(d, V) else d
    return Part.makeCylinder(0.8 * m, m, p - d * m, d).fuse(Part.makeCylinder(m / 2, length, p, d))


def nut(p, d, m=3):
    d = V(*d) if not isinstance(d, V) else d
    af, h = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 5.0)}[m]
    rc = af / math.sqrt(3)
    pts = [V(rc * math.cos(math.radians(60 * k)), rc * math.sin(math.radians(60 * k)), 0) for k in range(6)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, h))
    f.Placement = App.Placement(p, App.Rotation(V(0, 0, 1), d))
    return f


def poly_yz(pts, x0, x1):
    """Closed outline (y, z) in the plane x = x0, extruded to x1."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))


def m3_nut(p, d):
    d = V(*d) if not isinstance(d, V) else d
    rc = 5.5 / math.sqrt(3)
    pts = [V(rc * math.cos(math.radians(60 * k)), rc * math.sin(math.radians(60 * k)), 0) for k in range(6)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, 2.4))
    f.Placement = App.Placement(p, App.Rotation(V(0, 0, 1), d))
    return f


def pump_370(origin=V(0, 0, 0), axis=V(1, 0, 0)):
    """12 V 370 vacuum pump (DATASHEET class size): motor can + pump head, axis along `axis`."""
    p = P.PUMP_370
    a = V(axis); a.normalize()
    can = Part.makeCylinder(p["body_d"] / 2, 30.0, origin, a)
    head = Part.makeCylinder(p["head_w"] / 2, p["body_l"] - 30.0, origin + a * 30.0, a)
    nip = Part.makeCylinder(p["port_od"] / 2, 8.0, origin + a * p["body_l"], a)
    return fuse([can, head, nip])


def valve(origin=V(0, 0, 0)):
    """2-pos 3-way 12 V valve, body along +x from origin, 3 ports on the +x end (z +4 = cup, 0 = vent, -4 = pump).
    Returns (shape, {"cup": tip, "vent": tip, "pump": tip})."""
    v = P.VALVE
    b = Part.makeBox(v["l"], v["w"], v["h"], origin)
    tips, ports = {}, []
    for key, dz in (("pump", -4), ("vent", 0), ("cup", 4)):
        p = origin + V(v["l"], v["w"] / 2, v["h"] / 2 + dz)
        ports.append(Part.makeCylinder(v["port_od"] / 2, 6.0, p, V(1, 0, 0)))
        tips[key] = p + V(6.0, 0, 0)
    return fuse([b] + ports), tips


# ---------------------------------------------------------------- tube with real bend radius
def tube(points, r_bend, od=None):
    """PU tube along a polyline, every corner rounded with r_bend. Returns (shape, length, min_radius)."""
    od = P.TUBE["od"] if od is None else od
    pts = [V(*p) if not isinstance(p, V) else p for p in points]
    pts = [p for i, p in enumerate(pts) if i == 0 or (p - pts[i - 1]).Length > 1e-3]
    edges, cur, length, r_min = [], pts[0], 0.0, r_bend
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        d1 = b - a; d1.normalize()
        d2 = c - b; d2.normalize()
        ang = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        if ang < 1e-4:
            continue
        # adaptive: the bend may use at most half of each neighbouring straight (the report shows the smallest radius)
        t = min(r_bend * math.tan(ang / 2), 0.5 * (b - cur).Length if i > 1 else (b - cur).Length, 0.5 * (c - b).Length)
        r = t / math.tan(ang / 2)
        r_min = min(r_min, r)
        p1, p2 = b - d1 * t, b + d2 * t
        if (p1 - cur).Length > 1e-6:
            edges.append(Part.LineSegment(cur, p1).toShape()); length += (p1 - cur).Length
        bis = d2 - d1; bis.normalize()
        centre = b + bis * (r / math.cos(ang / 2))
        mid = centre - bis * r
        edges.append(Part.Arc(p1, mid, p2).toShape()); length += r * ang
        cur = p2
    if (pts[-1] - cur).Length > 1e-6:
        edges.append(Part.LineSegment(cur, pts[-1]).toShape()); length += (pts[-1] - cur).Length
    d0 = pts[1] - pts[0]; d0.normalize()
    prof = Part.Wire(Part.makeCircle(od / 2, pts[0], d0))
    shape = Part.Wire(edges).makePipeShell([prof], True, True)
    return shape, length, r_min


def place(shape, alpha_deg=0.0, at=V(0, 0, 0)):
    """Station frame -> module frame: turn about Y so the station's +x tube direction points at alpha_deg in the xz
    plane (0 = +x, 90 = +z up), then move to `at`."""
    s = shape.copy()
    s.rotate(V(0, 0, 0), Y, -alpha_deg)
    s.translate(at)
    return s


def place_point(p, alpha_deg=0.0, at=V(0, 0, 0)):
    return App.Rotation(Y, -alpha_deg).multVec(V(*p)) + at


def export_dxf_flat(shape, path, normal=Y):
    """Laser-cut DXF of a plate: its largest face turned so `normal` points to +Z (lies flat on XY), moved to the
    origin. Returns the flat face's (x, y) size, to check it is not edge-on (clapets v7 A_TOLE_PORTE bug)."""
    import importDXF
    face = max([f for f in shape.Faces if abs(f.normalAt(0, 0).dot(normal)) > 0.99], key=lambda f: f.Area).copy()
    face.Placement = App.Placement(V(0, 0, 0), App.Rotation(normal, V(0, 0, 1))).multiply(face.Placement)
    bb = face.BoundBox
    face.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    doc = App.newDocument("dxf_tmp")
    o = doc.addObject("Part::Feature", "plate")
    o.Shape = face
    importDXF.export([o], path)
    App.closeDocument(doc.Name)
    bb = face.BoundBox
    assert bb.XLength > 1 and bb.YLength > 1 and bb.ZLength < 0.01, "DXF face not flat"
    return round(bb.XLength, 1), round(bb.YLength, 1)


# ---------------------------------------------------------------- station helpers (station frame, see params.STATION)
def bulkhead_cuts(y_h, back_to, slot_r):
    """Cuts for the bulkhead cup mount: hex pocket (open behind), M5 hole through the wall, elbow body clearance down to
    back_to, and the outlet slot towards +x (open to the back, so the elbow slides in from behind)."""
    e, w = P.ELBOW_PL4_M5, P.BULKHEAD_WALL
    r = e["body_d"] / 2 + 0.4
    ya = y_h - e["axis_from_hex"]
    return [hex_y(e["hex_af"] + P.HEX_POCKET_CLEAR, y_h - e["hex_h"] - 0.2, y_h + 0.01),
            ycyl(2.75, y_h - 1, y_h + w + 1),
            ycyl(r, back_to, y_h - e["hex_h"] + 0.1),
            box(0, slot_r, back_to, ya + r, -r, r)]


def carrier_ref():
    """A 100 x 100 piece of carrier around one station (reference only): y -car_t..0, Ø hole + bolt holes."""
    S = P.STATION
    c = box(-50, 50, -S["car_t"], 0, -50, 50).cut(ycyl(S["hole_d"] / 2, -S["car_t"] - 1, 1))
    for h in bolt_holes(-S["car_t"] - 1, 1):
        c = c.cut(h)
    return c


def stone_ref(y_face):
    """The stone held against the station: its face at y_face (a 120 x 110 slice, reference only)."""
    return box(-60, 60, y_face, y_face + 30, -55, 55)


def station_screws(y_head, length):
    """3 x M3 socket head from the station front (head on y_head) through the carrier, nut behind it."""
    S, out = P.STATION, []
    for i, (x, z) in enumerate(polar(S["bolt_r"], S["bolt_a"])):
        out.append(("FIX_M3x%d_%d" % (length, i + 1), m3_screw(V(x, y_head, z), V(0, -1, 0), length), "fastener"))
        out.append(("FIX_NUT_M3_%d" % (i + 1), m3_nut(V(x, -S["car_t"], z), V(0, -1, 0)), "fastener"))
    return out


def station_tube(port, ya, r_bend=None):
    """Tube from the elbow port: 15 mm straight out (+x), bend, then down along the carrier (-z) 50 mm."""
    r_bend = P.TUBE["r_min_moving"] if r_bend is None else r_bend
    s = P.TUBE["straight_after_fitting"]
    p0 = V(port.x, ya, port.z)
    p1 = V(port.x + s + r_bend, ya, port.z)
    p2 = V(port.x + s + r_bend, ya, port.z - r_bend - 50)
    return tube([p0, p1, p2], r_bend)


# ---------------------------------------------------------------- module A interface + cup stations (module frame)
ZC = [P.table_to_module(z) for z in P.STONE_CZ_TABLE]       # stone centres at lift 0, module z: 29, 139, 249
BOLT_Z = (P.PL_ZC - 37.5, P.PL_ZC + 37.5)                    # the butterfly plate's wheel bolts (x +-60)


def load_station(name):
    """Build cup station `name` (S1 / S3) and return its parts (without its reference carrier / stone / tube) + info."""
    import importlib
    mod = importlib.import_module("station_" + name.lower())
    parts, info, notes = mod.build()
    keep = [(n, s, k) for n, s, k in parts if n not in ("REF_CARRIER", "REF_STONE", "REF_TUBE_4x2.5")]
    return keep, info


def put_station(parts, info, tag, alpha, at):
    """Station parts placed in the module frame; returns (parts, port point, port direction)."""
    out = [("%s_%s" % (n, tag), place(s, alpha, at), k) for n, s, k in parts]
    port = place_point(info["port"], alpha, at)
    d = App.Rotation(Y, -alpha).multVec(V(*info["port_dir"]))
    return out, port, d


def station_cuts(alpha, at):
    """Carrier holes for one station: Ø50 + 3 x M3, turned with the station (built in the station frame)."""
    S = P.STATION
    lo, hi = -S["car_t"] - 1.0, 1.0
    return [place(ycyl(S["hole_d"] / 2, lo, hi), alpha, at)] + [place(h, alpha, at) for h in bolt_holes(lo, hi)]


def plate_head_pockets():
    """Pockets in a bracket's back face for module A's 2 x M4 button heads on the plate's centre holes (x 0, z +-10)."""
    return [ycyl(5.0, P.PL_Y1 - 1, P.PL_Y1 + 3.5, 0, P.PL_ZC + dz) for dz in (-10.0, 10.0)]


def plate_ref():
    """The real butterfly plate outline (from clapets v7), reference only."""
    j = json.load(open(os.path.join(HERE, "..", "..", "clapets", "clapets-v7", "fc", "plaque_papillon_reelle.json")))
    return poly_xz([(x, P.PL_ZC + v) for x, v in j["outer"]], P.PL_Y0, P.PL_Y1)


# ---------------------------------------------------------------- export
def is_main(file):
    """True when `file` is the script freecadcmd was started with (freecadcmd names a script after its file, so
    `__name__ == "__main__"` doesn't work, and an import by another generator must not run it)."""
    me = os.path.normcase(os.path.abspath(file))
    return any(os.path.normcase(os.path.abspath(a)) == me for a in sys.argv if a.endswith(".py"))


MAT = {"print": P.RHO_ABS, "tpu": P.RHO_TPU, "mdf": 0.75}


def save(name, subdir, parts, info, notes=(), files=True):
    """parts = [(part_name, shape, kind)], kind in print / tpu / bought / fastener / ref.
    Writes CAD_FC/<subdir>/<name>/: <name>.FCStd, report.txt, info.json and (files=True, as clapets v7) STEP/ (every
    printed / TPU / MDF part), STL/ (printed + TPU), DXF/ (MDF, laid flat). A posed copy uses files=False."""
    out = os.path.join(OUT_ROOT, subdir, name)
    os.makedirs(out, exist_ok=True)
    def sub(d, fname):
        os.makedirs(os.path.join(out, d), exist_ok=True)
        return os.path.join(out, d, fname)
    doc = App.newDocument(name.replace("-", "_"))
    groups = {}
    rep = ["%s  (%s)" % (name, info.get("title", "")), ""]
    total = 0.0
    for pname, sh, kind in parts:
        if kind not in groups:
            groups[kind] = doc.addObject("App::DocumentObjectGroup", "G_" + kind)
        o = doc.addObject("Part::Feature", pname)
        o.Shape = sh
        groups[kind].addObject(o)
        bb = sh.BoundBox
        line = "%-26s %-8s size %6.1f x %6.1f x %6.1f" % (pname, kind, bb.XLength, bb.YLength, bb.ZLength)
        if kind in MAT:
            m = sh.Volume * 1e-3 * MAT[kind]
            total += m
            line += "  %6.1f g  %s" % (m, "valid" if sh.isValid() else "INVALID")
            if files:
                sh.exportStep(sub("STEP", pname + ".step"))
        if kind == "mdf" and files:
            line += "  DXF %s x %s" % export_dxf_flat(sh, sub("DXF", pname + ".dxf"))
        if kind in ("print", "tpu") and files:
            MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.02, AngularDeflection=0.0349, Relative=False).write(
                sub("STL", pname + ".stl"))
        rep.append(line)
    rep += ["", "printed + TPU mass: %.1f g" % total, ""]
    for k, v in info.items():
        rep.append("%-22s %s" % (k, v))
    if notes:
        rep += ["", "Notes:"] + ["- " + n for n in notes]
    doc.recompute()
    doc.saveAs(os.path.join(out, name + ".FCStd"))
    App.closeDocument(doc.Name)
    info = dict(info, printed_mass_g=round(total, 1))
    with open(os.path.join(out, "info.json"), "w") as f:
        json.dump(info, f, indent=1)
    with open(os.path.join(out, "report.txt"), "w") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return out
