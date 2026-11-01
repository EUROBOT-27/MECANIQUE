# v4_patch2.py - door servos standing on the bottom plate (gears out of the head sweep) + motion sequence with the stack
# appearing only on approach and leaving after release.
import os
import sys

D = sys.argv[1]
p = os.path.join(D, "v4_fc.py")
s = open(p, encoding="utf-8").read()


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, "count %d: %s" % (s.count(old), old[:90])
    s = s.replace(old, new)


rep('''    SV_TOP = UP                                             # servo hangs under the top plate (body bottom against it)
    SV_FLZ = SV_TOP - SV_FL
    GZB = SV_TOP - SV_HORN                                  # horn face 182.5
    GZA = GZB - 8                                           # gears 174.5..182.5''',
'''    # servo STANDS on the bottom plate: the gear pair sits at z 82.5..90.5, 142 mm from the head axis, outside the
    # head carrier's sweep (R 126). (Hanging under the top plate put the gears at the head-axis height: collision.)
    SV_BOT = LOW + PT + 3                                   # body bottom 39 (3 mm above the plate)
    SV_FLZ = SV_BOT + SV_FL                                 # flange underside 65.6 (posts end here)
    GZA = SV_BOT + SV_HORN                                  # horn top = gears bottom 82.5
    GZB = GZA + 8                                           # gears 82.5..90.5''')
rep('''    a.append(box(s, 99, 150, G.SVY - 11, G.SVY + 11, G.UP, G.UP + G.PT))                              # servo area (x >= 99: clear of the lobe)''',
    '''    a.append(box(s, 99, 150, G.SVY - 11, G.SVY + 11, G.LOW, G.LOW + G.PT))                            # servo area on the bottom plate''')
rep('''    a.append(box(s, G.W_X1 - 1, 106, G.PL_Y1, 89, G.LOW + G.PT, G.LOW + G.PT + 10))                   # gussets rib <-> wall
    a.append(box(s, G.W_X1 - 1, 106, G.PL_Y1, 89, G.SV_TOP - 46, G.SV_TOP - 37))''',
'''    a.append(box(s, G.W_X1 - 1, 106, G.PL_Y1, 89, 110, 120))                                          # gussets rib <-> wall
    a.append(box(s, G.W_X1 - 1, 106, G.PL_Y1, 89, 200, 210))''')
rep('''        a.append(box(s, hx - 3.8, hx + 3.8, y0, G.SVY + 11, G.SV_FLZ, G.UP))
        for dy in hy:
            yy0, yy1 = G.SVY + dy - G.SV_SLOT, G.SVY + dy + G.SV_SLOT
            c += [vcyl(s, hx, yy0, G.SV_FLZ - 1, G.SV_FLZ + 13, 1.7), vcyl(s, hx, yy1, G.SV_FLZ - 1, G.SV_FLZ + 13, 1.7),
                  box(s, hx - 1.7, hx + 1.7, yy0, yy1, G.SV_FLZ - 1, G.SV_FLZ + 13)]
            nb = nut(s, 2, hx, G.SVY + dy, G.SV_FLZ + 8, 0, side * 10)''',
'''        a.append(box(s, hx - 3.8, hx + 3.8, y0, G.SVY + 11, G.LOW + G.PT, G.SV_FLZ))                  # posts up to the flange
        for dy in hy:
            yy0, yy1 = G.SVY + dy - G.SV_SLOT, G.SVY + dy + G.SV_SLOT
            c += [vcyl(s, hx, yy0, G.SV_FLZ - 13, G.SV_FLZ + 1, 1.7), vcyl(s, hx, yy1, G.SV_FLZ - 13, G.SV_FLZ + 1, 1.7),
                  box(s, hx - 1.7, hx + 1.7, yy0, yy1, G.SV_FLZ - 13, G.SV_FLZ + 1)]
            nb = nut(s, 2, hx, G.SVY + dy, G.SV_FLZ - 8, 0, side * 10)''')
rep('''    hz0 = G.GZA - 14
    a = [prism(1, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.PY, hz0, G.GZA, 10)]
    ca, cc = split_clamp_z(1, G.PX, G.PY, hz0, G.GZA, [hz0 + 4, G.GZA - 4], lug_dir=1)
    a += ca
    part("ROUE_PORTE_24T", solid(a, cc + [vcyl(1, G.PX, G.PY, hz0 - 1, G.GZB + 1, 4.05)]), 1270, PETG2, "print")''',
'''    hz1 = G.GZB + 14                                                                                  # clamp hub above the gear
    a = [prism(1, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.PY, G.GZB, hz1, 10)]
    ca, cc = split_clamp_z(1, G.PX, G.PY, G.GZB, hz1, [G.GZB + 4, hz1 - 4], lug_dir=1)
    a += ca
    part("ROUE_PORTE_24T", solid(a, cc + [vcyl(1, G.PX, G.PY, G.GZA - 1, hz1 + 1, 4.05)]), 1270, PETG2, "print")''')
rep('''def pignon_porte():  # 20T under the hanging MG996R, horn in a pocket on top
    a = [prism(1, gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.SVY, G.GZB, G.GZB + G.HORN_T, G.HORN_R + 3)]
    c = [vcyl(1, G.PX, G.SVY, G.GZB, G.GZB + G.HORN_T + 1, G.HORN_R + 0.2), vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2)]''',
'''def pignon_porte():  # 20T on the standing MG996R, horn in a pocket underneath
    a = [prism(1, gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R + 3)]
    c = [vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T - 1, G.GZA, G.HORN_R + 0.2), vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2)]''')
rep('''    for s, name in ((1, "REF_MG996R_D"), (-1, "REF_MG996R_G")):            # door servos, hanging under the top plate
        part(name, solid([box(s, G.SV_X0, G.SV_X1, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_TOP - G.SV_H, G.SV_TOP),
                          box(s, G.SV_XC - 27.25, G.SV_XC + 27.25, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_FLZ - 2.4, G.SV_FLZ),
                          vcyl(s, G.PX, G.SVY, G.GZB + 2, G.SV_TOP - G.SV_H, 3), vcyl(s, G.PX, G.SVY, G.GZB, G.GZB + 2, G.HORN_R)]), 1200, SERVO, "ref")''',
'''    for s, name in ((1, "REF_MG996R_D"), (-1, "REF_MG996R_G")):            # door servos, standing on the bottom plate
        b = G.SV_BOT
        part(name, solid([box(s, G.SV_X0, G.SV_X1, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, b, b + G.SV_H),
                          box(s, G.SV_XC - 27.25, G.SV_XC + 27.25, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_FLZ, G.SV_FLZ + 2.4),
                          vcyl(s, G.PX, G.SVY, b + G.SV_H, G.GZA - G.HORN_T, 3), vcyl(s, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R)]), 1200, SERVO, "ref")''')
open(p, "w", encoding="utf-8").write(s)

q = os.path.join(D, "motion_v4.py")
t = open(q, encoding="utf-8").read()
i = t.index("TIMELINE = [")
j = t.index("]\n", i) + 2
t = t[:i] + '''TIMELINE = [   # (duration, lift, doors, head, stack follows lift, stack follows head, stack present, label) at step END
    (0.5, 0, A_FOLD, 0, 0, 0, 0, "start: doors folded inside the base"),
    (1.5, 0, A_OPEN_APPROACH, 0, 0, 0, 0, "doors open"),
    (1.0, 0, A_OPEN_APPROACH, 0, 0, 0, 1, "approach: stack at the face"),
    (1.0, 0, A_CLAMP, 0, 0, 0, 1, "doors clamp the stack"),
    (1.0, 15, A_CLAMP, 0, 1, 0, 1, "carry: lift 15 mm"),
    (0.5, 15, A_CLAMP, 0, 1, 0, 1, "carry"),
    (1.0, 0, A_CLAMP, 0, 1, 0, 1, "in the castle: lower"),
    (1.0, 0, A_OPEN, 0, 1, 1, 1, "cups hold, doors open -48 deg"),
    (2.0, 72, A_OPEN, 0, 1, 1, 1, "lift 72 mm with the stack"),
    (2.0, 72, A_OPEN, 90, 1, 1, 1, "turn the stack 90 deg"),
    (1.5, 0, A_OPEN, 90, 1, 1, 1, "lower (towers 15 mm above the table)"),
    (0.5, 0, A_OPEN, 90, 0, 0, 1, "release: cups vent"),
    (1.0, 0, A_OPEN, 90, 0, 0, 0, "robot backs away"),
    (1.5, 0, A_OPEN, 0, 0, 0, 0, "head back"),
    (1.5, 0, A_FOLD, 0, 0, 0, 0, "doors fold"),
]
''' + t[j:]


def rept(old, new):
    global t
    assert t.count(old) >= 1, "motion: " + old[:80]
    t = t.replace(old, new)


rept('''    for dur, h, a, ph, sl, sh, label in TIMELINE:''', '''    for dur, h, a, ph, sl, sh, pres, label in TIMELINE:''')
rept('''    last = TIMELINE[-1]
    return last[1], last[2], last[3], last[4], last[5], last[6]''',
'''    last = TIMELINE[-1]
    return last[1], last[2], last[3], last[4], last[5], last[7]


def present(t):
    t0 = 0.0
    for step in TIMELINE:
        if t <= t0 + step[0] + 1e-9:
            return step[6]
        t0 += step[0]
    return TIMELINE[-1][6]''')
rept('''    if grp == "stack":
        rot = App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), phs), Vector(0, 0, HZ))''',
'''    if grp == "stack":
        if hs is None:                                       # stack not there (before the approach / after backing away)
            return App.Placement(Vector(0, 2000, 0), App.Rotation()).multiply(base)
        rot = App.Placement(Vector(), App.Rotation(Vector(0, 1, 0), phs), Vector(0, 0, HZ))''')
rept('''        hs, phs = stack_state(t)
''', '''        hs, phs = stack_state(t)
        if not present(t):
            hs = None
''')
rept('''    for dur, _, _, _, _, _, lab in TIMELINE:''', '''    for dur, _, _, _, _, _, _, lab in TIMELINE:''')
open(q, "w", encoding="utf-8").write(t)
print("patched; stack-absent hooks:", t.count("hs = None"))
