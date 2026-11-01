for m in ("PIL", "imageio", "numpy"):
    try:
        mod = __import__(m); print(m, "OK", getattr(mod, "__version__", ""))
    except Exception as e:
        print(m, "missing")
