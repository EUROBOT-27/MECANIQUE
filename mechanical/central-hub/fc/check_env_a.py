# check_env_a.py - extra clash check for option A (complements the check inside hub_a_fc.py).
#  1. gaps between the fixed parts (turn servos, cradles, hub wall, other rings' pinions)
#  2. every level + stone vs base_330 (plate, drive motors, wheels, bridge) over the full sequence
#  3. minimum clearance between levels (every 4th step)
# Run: "<FreeCAD>/bin/freecadcmd.exe" fc/check_env_a.py   (from mechanical/central-hub/) -> hub_a_env_report.txt
# base_330 numbers: same as hub_gif.py / concepts/central-hub-builder.md. Not modelled: cables, hoses, the rest of the
# robot (layout-v1 modules). Fixed fasteners are not checked against the bridge (they go through it by design).
import os, sys
os.environ["HUB_A_NO_MAIN"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hub_a_fc as H
import Part
import FreeCAD as App
V = App.Vector
out = []
def P(*a): out.append(" ".join(str(x) for x in a))
vol = H.common_vol

fx = H.fixed_parts()
ts, cr = fx["turn_servos"], fx["cradles"]
P("Central hub option A - extra clash check (fixed parts, base_330, clearances)", "")
P("== 1. fixed parts: clashes and gaps (mm) ==")
bad = H.check_fixed(fx)
P("clashes: " + ("none" if not bad else "; ".join(bad)))
for i in range(3):
    P("turn servo %-6s (with ears) - hub wall gap %.2f" % (H.NAMES[i], ts[i].distToShape(fx["hub"])[0]))
    P("cradle     %-6s - hub wall gap %.2f" % (H.NAMES[i], cr[i].distToShape(fx["hub"])[0]))
    for k in range(3):
        if k != i:
            p = H.pinion(k, 0)
            P("turn servo %-6s - %-6s pinion gap %.2f; cradle %-6s - %-6s pinion gap %.2f" %
              (H.NAMES[i], H.NAMES[k], ts[i].distToShape(p)[0], H.NAMES[i], H.NAMES[k], cr[i].distToShape(p)[0]))

base = {
    "plate": Part.makeBox(330, 280, 5, V(-165, -140, 13.5)),
    "motors": Part.makeCylinder(18.5, 123, V(-61.5, 0, 45), V(1, 0, 0)),
    "wheel_L": Part.makeCylinder(45, 20, V(-104, 0, 45), V(1, 0, 0)),
    "wheel_R": Part.makeCylinder(45, 20, V(84, 0, 45), V(1, 0, 0)),
    "bridge": Part.makeBox(140, 110, 5, V(-70, -55, 68)).fuse([Part.makeBox(140, 5, 49.5, V(-70, s, 18.5)) for s in (50, -55)]),
}
seq = H.sequence()
hits, mind = {}, {}
for n, (label, st) in enumerate(seq):
    L = []
    for k in range(3):
        mech, ss = H.level(k, st[k]); L.append(mech)
        for name, b in base.items():
            if vol(mech, b) > 1: hits.setdefault((H.NAMES[k], "mechanism", name), []).append(label)
            for s in ss:
                if vol(s, b) > 1: hits.setdefault((H.NAMES[k], "stone", name), []).append(label)
    if n % 4 == 0:
        for k in range(3):
            for j in range(k + 1, 3):
                d = L[k].distToShape(L[j])[0]
                if (k, j) not in mind or d < mind[(k, j)][0]: mind[(k, j)] = (d, label)
P("", "== 2. sequence (%d steps) vs base_330 ==" % len(seq))
if not hits: P("no clashes")
for (lv, what, part), labels in hits.items():
    P("%s %s hits %s in %d steps (%s ... %s)" % (lv, what, part, len(labels), labels[0], labels[-1]))
P("", "== 3. min clearance between levels (every 4th step) ==")
for (k, j), (d, label) in mind.items(): P("%s / %s: %.2f mm at '%s'" % (H.NAMES[k], H.NAMES[j], d, label))
txt = "\n".join(out)
open(os.path.join(os.path.dirname(HERE), "hub_a_env_report.txt"), "w", encoding="utf-8").write(txt + "\n")
print(txt)
