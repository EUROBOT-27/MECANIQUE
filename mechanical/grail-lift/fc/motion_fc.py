# motion_fc.py - plays the planned Grail-lift sequence (CAD_FC/joints_<v>.json) and checks every step.
#   Checks (headless):  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/motion_fc.py          (~2 min)
#     -> CAD_FC/motion/motion_report_<v>.txt : actuator height <= 350, collisions (moving vs fixed / robot body, arm vs
#        servo/cradle), Grail clear of the robot below the roof, release (nothing touches the Grail at the end)
#   GIF (GUI):          "C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/motion_fc.py
#     -> CAD_FC/motion/grail_lift_<v>.gif (side view + 3D), copied to mechanical/simulations/grail_lift/
#   Version: set GRAIL_V=v1 / v3 / v4 (default v2).
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App
from FreeCAD import Vector

import grail_common as C

V = os.environ.get("GRAIL_V", "v2")
J = C.load_joints(os.path.join(C.CAD, "joints_%s.json" % V))
OUT = os.path.join(C.CAD, "motion")
SIM = os.path.normpath(os.path.join(C.ROOT, "..", "simulations", "grail_lift"))
GUI = App.GuiUp
# pairs that touch by design in these simplified models (gear mesh, wheels in the slot, pin in its cap, horn on shaft)
EXPECTED = {frozenset(p) for p in (("CAR_PINION_20T", "RACK_M1"), ("CAR_VWHEELS", "COL_2020"), ("CAR_SLIDERS", "COL_2020"), ("SCREW_T8", "NUT_T8_brass"), ("SCREW_T8", "BEARING_608_BLOCK"), ("SCREW_T8", "COUPLER_5x8"), ("COUPLER_5x8", "NEMA17_LIFT"),
                                   ("CAR_BELT_ARM", "BELT_CLAMP_bracket"), ("CAR_BELT_ARM", "CAR_SLIDE_FRAME"), ("BELT_CLAMP_bracket", "BELT_GT2_loop"),
                                   ("CAR_BELT_ARM", "BELT_GT2_loop"), ("BELT_GT2_loop", "PULLEY_GT2_20T"), ("BELT_GT2_loop", "IDLER_GT2_20T"),
                                   ("BELT_GT2_free_run", "PULLEY_GT2_20T"), ("BELT_GT2_free_run", "IDLER_GT2_20T"),
                                   ("TENSIONER_X_printer", "IDLER_GT2_20T"), ("TENSIONER_X_printer", "BELT_GT2_loop"),
                                   ("TENSIONER_X_printer", "BELT_GT2_free_run"), ("NEMA17_BELT", "PULLEY_GT2_20T"), ("GUIDE_RODS_D8", "SCS8UU_x2"), ("GUIDE_RODS_D8", "ROD2_BUSHING_printed"), ("CAR_BELT_ARM", "SCS8UU_x2"),
                                   ("PIVOT_PIN_M3", "CRADLE_printed"), ("SERVO_HORN_ROUND", "SERVO_MG996R"),
                                   ("PIVOT_PIN_M3", "U_BRACKET_steel"), ("SERVO_HORN_ROUND", "U_BRACKET_steel"),
                                   ("REAL_RACK_1M_280", "REAL_PINION_20T_1M"), ("REAL_NEMA14_SHAFT", "REAL_COUPLING_liaison"),
                                   ("REAL_PINION_20T_1M", "REAL_COUPLING_liaison"), ("CAR_SPACERS", "CAR_VWHEELS"),
                                   ("CAR_SPACERS", "CAR_PLATE"))}


def open_doc():
    path = os.path.join(C.CAD, J["fcstd"])
    for d in App.listDocuments().values():
        if os.path.normcase(d.FileName) == os.path.normcase(path):
            return d
    return App.openDocument(path)


def placements(t):
    lift, ang, on, gpl, label = C.simulate(J, t)
    pl = {}
    lp = C.lift_pl(J, lift)
    fp = C.flip_pl(J, lift, ang)
    for n in J["lift"]["objects"]:
        pl[n] = lp
    for n in J["flip"]["objects"]:
        pl[n] = fp
    for n in J["grail"]["objects"]:
        pl[n] = gpl
    return pl, lift, ang, on, label


def moved(base, p):
    s = base.copy()
    s.Placement = p.multiply(base.Placement)
    return s


def vol(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def check(doc):
    base = {o.Name: o.Shape.copy() for o in doc.Objects if hasattr(o, "Shape") and not o.Shape.isNull()}
    act = [n for n in J["actuators"] if n in base]
    fixed = [n for n in J["fixed"] if n in base]
    grail = [n for n in J["grail"]["objects"] if n in base]
    lim = J["limits"]
    T = C.seq_duration(J)
    n_steps = int(T / 0.05) + 1
    rep = ["Grail lift %s - motion check over the planned sequence (%.1f s, %d steps of 0.05 s)" % (V, T, n_steps), ""]
    worst_h, worst_hit, max_x = None, {}, -1e9
    grail_issue = {}
    last = None
    for k in range(n_steps + 1):
        t = min(T, k * 0.05)
        pl, lift, ang, on, label = placements(t)
        S = {n: moved(base[n], pl.get(n, App.Placement())) for n in base}
        top = max(S[n].BoundBox.ZMax for n in act)
        if worst_h is None or top > worst_h[0]:
            worst_h = (top, t, label)
        max_x = max(max_x, max(S[n].BoundBox.XMax for n in act))
        pairs = [(a, f) for a in act for f in fixed]
        pairs += [(a, b) for a in J["flip"]["objects"] for b in J["lift"]["objects"] if b not in J["flip"]["objects"]]
        for a, b in pairs:
            if a not in S or b not in S or frozenset((a, b)) in EXPECTED:
                continue
            v = vol(S[a], S[b])
            if v > 0.5:
                key = (a, b)
                if key not in worst_hit or v > worst_hit[key][0]:
                    worst_hit[key] = (v, t, label)
        for g in grail:
            others = fixed + ([] if on else act)
            for b in others:
                if b == "ENV_TABLE":
                    continue
                v = vol(S[g], S[b])
                if v > 0.5:
                    key = (g, b)
                    if key not in grail_issue or v > grail_issue[key][0]:
                        grail_issue[key] = (v, t, label)
        last = (S, on, label)
        if k % 20 == 0:
            print("t %.2f  lift %.1f  flip %.1f  top %.1f  %s" % (t, lift, ang, top, label))
    rep.append("Highest actuator point: %.1f mm at t %.2f s (%s)  -> %s (limit %.0f)"
               % (worst_h[0], worst_h[1], worst_h[2], "OK" if worst_h[0] <= lim["h_max"] else "TOO HIGH", lim["h_max"]))
    rep.append("Max protrusion beyond the face (actuators): x %.1f mm" % max_x)
    rep.append("")
    rep.append("Collisions of moving parts (volume > 0.5 mm3, worst moment):")
    if not worst_hit:
        rep.append("  none")
    for (a, b), (v, t, lab) in sorted(worst_hit.items(), key=lambda q: -q[1][0]):
        rep.append("  %-20s x %-18s %9.1f mm3 at t %.2f (%s)" % (a, b, v, t, lab))
    rep.append("")
    rep.append("Grail against the robot / a free Grail hit by the arm (volume > 0.5 mm3):")
    if not grail_issue:
        rep.append("  none")
    for (a, b), (v, t, lab) in sorted(grail_issue.items(), key=lambda q: -q[1][0]):
        rep.append("  %-12s x %-18s %9.1f mm3 at t %.2f (%s)" % (a, b, v, t, lab))
    S, on, label = last
    if grail:
        g = S[grail[0]]
        gap = min(g.distToShape(S[n])[0] for n in act)
        rep.append("")
        rep.append("End (%s): magnet %s, Grail bottom z %.2f (roof %.1f), Grail x %.1f..%.1f, nearest actuator %.2f mm"
                   % (label, "ON" if on else "OFF", g.BoundBox.ZMin, lim["roof"], g.BoundBox.XMin, g.BoundBox.XMax, gap))
        ok = (not on) and g.BoundBox.ZMin > C.ROOF_MIN and gap > 0.5 and (lim["edge_x"] is None or g.BoundBox.XMax < lim["edge_x"])
        rep.append("L4 end state: %s" % ("OK - Grail free on the roof, nothing touching it" if ok else "NOT OK"))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "motion_report_%s.txt" % V)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return path


def gif(doc):
    import FreeCADGui as Gui
    from PIL import Image
    colors = J.get("colors", {})
    for o in doc.Objects:
        vo = getattr(o, "ViewObject", None)
        if vo is None:
            continue
        vo.Visibility = o.Name not in ("ENV_BODY", "ENV_FACE_SKIN")   # body stand-in would hide the mechanism
        if o.Name in colors:
            vo.ShapeColor = tuple(colors[o.Name])
        if o.Name in J.get("transparent", {}):
            vo.Transparency = J["transparent"][o.Name]
    App.setActiveDocument(doc.Name)
    Gui.ActiveDocument = Gui.getDocument(doc.Name)
    v = Gui.getDocument(doc.Name).activeView()
    frames_dir = os.path.join(OUT, "frames_%s" % V)
    os.makedirs(frames_dir, exist_ok=True)
    T = C.seq_duration(J)
    dt = 0.15
    n = int(T / dt) + 1
    base = {o.Name: o.Placement for o in doc.Objects if hasattr(o, "Placement")}
    imgs = []
    for k in range(n + 6):
        t = min(T, k * dt)
        pl, lift, ang, on, label = placements(t)
        for name, p in pl.items():
            o = doc.getObject(name)
            if o is not None:
                o.Placement = p.multiply(base[name])
        doc.recompute()
        pair = []
        for view, fn in (("front", "side"), ("iso", "iso")):
            if view == "front":
                v.viewFront()                  # looking along +y: x (out) to the right, z up
            else:
                v.viewIsometric()
            v.fitAll()
            p = os.path.join(frames_dir, "%s_%03d.png" % (fn, k))
            v.saveImage(p, 640, 480, "White")
            pair.append(Image.open(p).convert("RGB"))
        im = Image.new("RGB", (1280, 500), "white")
        im.paste(pair[0], (0, 20))
        im.paste(pair[1], (640, 20))
        try:
            from PIL import ImageDraw
            ImageDraw.Draw(im).text((10, 4), "t %.1f s  lift %.0f  flip %.0f deg  magnet %s  -  %s"
                                    % (t, lift, ang, "ON" if on else "off", label), fill=(0, 0, 0))
        except Exception:
            pass
        imgs.append(im)
    for name, p in base.items():
        o = doc.getObject(name)
        if o is not None:
            o.Placement = p
    out = os.path.join(OUT, "grail_lift_%s.gif" % V)
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=int(dt * 1000), loop=0, optimize=True)
    os.makedirs(SIM, exist_ok=True)
    shutil.copy(out, os.path.join(SIM, os.path.basename(out)))
    shutil.rmtree(frames_dir, ignore_errors=True)
    print("GIF:", out)


doc = open_doc()
if os.environ.get("GRAIL_GIF_ONLY") != "1":            # set GRAIL_GIF_ONLY=1 to skip the (slow) checks in the GUI
    rp = check(doc)
    os.makedirs(SIM, exist_ok=True)
    shutil.copy(rp, os.path.join(SIM, os.path.basename(rp)))
if GUI:
    gif(doc)
    if os.environ.get("GRAIL_QUIT") == "1":           # batch use: quit FreeCAD without saving the moved document
        os._exit(0)
