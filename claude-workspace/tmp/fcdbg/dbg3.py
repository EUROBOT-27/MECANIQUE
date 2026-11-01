src = open(r"C:/Projects/EUROBOT/Mecanique/module_clapets_poc/fc/poc_fc.py", encoding="utf-8").read().replace("\nmain()\n", "\n")
exec(compile(src, "poc_fc", "exec"))
moyeu(-1, "G"); refs()
for n in ("G", "REF_PLAQUE_PAPILLON"):
    sh = PARTS[n][0]
    print("==", n, sh.isValid(), round(sh.Volume, 1), "shells", len(sh.Shells), "solids", len(sh.Solids))
    try:
        sh.check(True)
        print("check: ok")
    except Exception as e:
        print("check:", str(e)[:600])
    fx = sh.copy(); r = fx.fix(1e-7, 1e-7, 1e-7)
    print("after fix:", fx.isValid(), round(fx.Volume, 1))
