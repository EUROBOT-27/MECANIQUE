src = open(r"C:/Projects/EUROBOT/Mecanique/module_clapets_poc/fc/poc_fc.py", encoding="utf-8").read().replace("\nmain()\n", "\n")
exec(compile(src, "poc_fc", "exec"))
import Part
def stages(adds, cuts):
    f = adds[0].fuse(adds[1:]) if len(adds) > 1 else adds[0]
    print("  fused", round(f.Volume, 1), f.isValid())
    c = f.cut(list(cuts))
    print("  cut  ", round(c.Volume, 1), c.isValid())
    r = c.removeSplitter()
    print("  rs   ", round(r.Volume, 1), r.isValid())
orig = solid
def capture(adds, cuts=()):
    stages(adds, cuts); return orig(adds, cuts)
globals()["solid"] = capture
for s, n in ((1, "D"), (-1, "G")):
    print("moyeu", n); moyeu(s, "X")
