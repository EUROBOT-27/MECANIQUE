import sys, math
src = open(r"C:/Projects/EUROBOT/Mecanique/module_clapets_poc/fc/poc_fc.py", encoding="utf-8").read().replace("\nmain()\n", "\n")
exec(compile(src, "poc_fc", "exec"))
for s in (1, -1):
    hubc = vcyl(s, G.PX, G.PY, G.HUB_Z0, G.HUB_Z1, G.HUB_R)
    g = prism(s, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB)
    fl = [(G.PX + 38, G.PY + 14), (G.SX0, G.PY + 14), (G.SX0, G.PY + 26), (G.PX + 38, G.PY + 26)]
    arm = prism(s, hull(circle(G.PX, G.PY, G.HUB_R, 48) + fl), *G.ARM1)
    for n, sh in (("hub", hubc), ("gear", g), ("arm", arm), ("hub+gear", hubc.fuse(g)), ("hub+arm", hubc.fuse(arm))):
        print(s, n, round(sh.Volume, 1), sh.isValid())
