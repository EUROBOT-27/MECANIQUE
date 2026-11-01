# Rewrites the door units of poc_fc.py to the v1 layout: turning Ø8 rod in 2x 608ZZ (one per plate), 40T gear on the rod
# top above the plate, MG996R standing on the top plate (slotted bracket), arms clamped on the rod (printed split clamps).
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, "not found once: " + old[:90]
    s = s.replace(old, new)


# ---------------------------------------------------------------- header + parameters
i = s.index("#   Doors: one FIXED plain Ø8 rod per door")
j = s.index("\n", s.index("\n", i) + 1)
s = s[:i] + ("#   Doors (v1 layout): one TURNING plain Ø8 rod per door in 2x 608ZZ (one per plate); 40T gear clamped on the rod top\n"
             "#   above the plate, MG996R standing on the top plate (slotted bracket) with the 20T pinion; arms clamped on the rod.") + s[j:]

i = s.index("    PX, PY = 125, 113")
j = s.index("    HEAD_X, HEAD_Y0, HEAD_Z0, HEAD_Z1")
s = s[:i] + '''    PX, PY = 125, 113                                       # door rod axis (right); 40T gear stays 3.75 mm behind the stack
    LOW, UP, PT = 96, 200, 6                                # unit plates
    W_X0, W_X1, W_Y0, W_Y1 = 66, 146, PL_Y0 + PL_T, 131
    BRG_R, BRG_T, BOSS_R = 11.05, 7.1, 14.5                 # 608ZZ (8 x 22 x 7) seats in bosses under / over the plates
    ROD_Z0, ROD_Z1 = 96, 262                                # turning plain Ø8 rod, 166 mm (lab rods, cut)
    CLAMP_SLOT = 1.2                                        # split clamps on the rod (no flat): slot width, M3 squeeze screws
    # gears m1.25: 20T pinion on the MG996R horn -> 40T gear clamped on the rod, x2
    # x2: holding ~0.96 N.m at the hinge (3 pads x 4 N x 80 mm) -> 0.48 N.m at the servo, ~45-50 % of MG996R stall.
    # Door travel is limited to ~90 deg (servo 180 deg / 2): enough for open -21 / clamp +5; no full fold on the PoC.
    GM, GZ1, GZ2 = 1.25, 20, 40
    GC = GM * (GZ1 + GZ2) / 2
    SVY = PY - GC                                           # servo axis (125, 75.5), behind the rod
    SV_L, SV_W, SV_H, SV_FL, SV_OUT, SV_HORN = 40.7, 19.7, 37.0, 26.6, 10.0, 43.5   # MG996R (= MG995), CHECK
    SV_X0 = PX - SV_OUT                                     # body x 115..155.7, output 10 mm from its inner end
    SV_X1 = SV_X0 + SV_L
    SV_XC = (SV_X0 + SV_X1) / 2
    BR_T = 4                                                # servo bracket base on the top plate
    SV_Z0 = UP + PT + BR_T + 0.5                            # servo body bottom 210.5
    SV_FLZ = SV_Z0 + SV_FL                                  # flange underside 237.1
    GZA = SV_Z0 + SV_HORN                                   # horn top = gears bottom 254
    GZB = GZA + 8                                           # gears 254..262
    SV_SLOT = 2                                             # bracket slides ±2 mm along the gear line = mesh adjustment
    HORN_R, HORN_T = 10.5, 2.0                              # MG996R round horn Ø21 x 2 (CHECK): pocket in the pinion
    SHEET_T, PAD_T = 3, 10                                  # 3 mm plywood / alu sheet
    SX0 = 170
    SX1 = SX0 + SHEET_T                                     # pad face at x 160 = box end
    SY0, SY1, TAB_Y0 = BOX_Y0 + 2, 225, PY + 14             # sheet y 145..225, tabs back to 127
    PAD_Y0, PAD_Y1 = 172, 220
    DZ0, DZ1 = 15, 320
    ARM1, ARM2 = (104, 114), (188, 198)                     # arms between the bearings (M8 washer 1.6 each side)
    FL1, FL2 = (103, 118), (180, 198)
    NUT_W, NUT_L, NUT_T = 5.6, 6.4, 2.6                     # M3 nut trap
''' + s[j:]

# ---------------------------------------------------------------- door parts
i = s.index("def aile(s, name):")
j = s.index("def tole():")
s = s[:i] + '''def split_clamp(s, x, y, z0, z1, screws_z):
    """Printed split clamp on the round Ø8 rod (no flat): lug on the -y side, slot through the bore, M3 screws along x.
    Returns (adds, cuts)."""
    a = [box(s, x - 7, x + 7, y - 21, y - 4, z0, z1)]                                              # lug behind the rod
    c = [box(s, x - G.CLAMP_SLOT / 2, x + G.CLAMP_SLOT / 2, y - 22, y, z0 - 1, z1 + 1)]             # slot through the bore
    for z in screws_z:
        c.append(xcyl(s, x - 8, x + 8, y - 13, z, 1.7))                                            # M3 x 16 squeeze screw...
        c.append(nut(s, 0, x + 7 - G.NUT_T / 2 + 0.1, y - 13, z, 0, 0))                            # ...nut pressed in, far side
        c.append(xcyl(s, x - 8, x - 4.5, y - 13, z, 3.0))                                          # head counterbore
    return a, c


def aile(s, name):      # door unit frame: 2 plates with the 608ZZ seats, back wall bolted to the plate; servo bracket on top
    a, c = [], []
    for z in (G.LOW, G.UP):
        a.append(box(s, G.W_X0, G.W_X1, G.W_Y0, G.W_Y1, z, z + G.PT))
    a.append(vcyl(s, G.PX, G.PY, G.LOW - 3, G.LOW + G.PT, G.BOSS_R))                                  # 608 boss under the bottom plate
    a.append(vcyl(s, G.PX, G.PY, G.UP, G.UP + G.PT + 3, G.BOSS_R))                                    # 608 boss over the top plate
    a.append(box(s, 100, 166, G.SVY - 14, G.W_Y0 + 1, G.UP, G.UP + G.PT))                            # bracket seat (behind)
    a.append(box(s, G.W_X1, 166, G.W_Y0, G.SVY + 14, G.UP, G.UP + G.PT))
    a.append(box(s, G.W_X0, 105, G.W_Y0, G.W_Y0 + 6, G.PL_ZC - G.SPRING_V - 9, G.PL_ZC + G.SPRING_V + 9))   # back wall
    a.append(box(s, G.W_X0, G.W_X0 + 6, G.W_Y0, G.W_Y1, G.LOW, G.UP + G.PT))                             # inner side wall
    c.append(vcyl(s, G.PX, G.PY, G.LOW + G.PT + 0.1 - G.BRG_T - 0.1, G.LOW + G.PT + 0.1, G.BRG_R))     # 608 from the top
    c.append(vcyl(s, G.PX, G.PY, G.UP - 0.1, G.UP - 0.1 + G.BRG_T + 0.1, G.BRG_R))                     # 608 from below
    c.append(vcyl(s, G.PX, G.PY, G.LOW - 4, G.UP + G.PT + 4, 5.0))                                    # rod clearance
    for dx in (-12, 12):                                                                             # bracket: 2x M3 + nut below
        c.append(vcyl(s, G.SV_XC + dx, G.SVY, G.UP - 1, G.UP + G.PT + 1, 1.7))
        c.append(nut(s, 2, G.SV_XC + dx, G.SVY, G.UP + G.NUT_T / 2 - 0.1, 2, 0))
    for bx, bz in G.WING_BOLTS:
        c.append(ycyl(s, bx, G.W_Y0 - 1, G.W_Y0 + 7, bz, 2.25))                                          # M4 through the spring hole
        c.append(box(s, bx - 4.1, bx + 4.1, G.W_Y0 + 2.4, G.W_Y0 + 9, bz - 3.6, bz + 3.6))               # M4 nut, from the front
    part(name, solid(a, c), 1270, PETG2, True)


def slot(s, x0, y0, x1, y1, z0, z1, r):     # vertical obround, centres (x0, y0) -> (x1, y1)
    c = [vcyl(s, x0, y0, z0, z1, r), vcyl(s, x1, y1, z0, z1, r)]
    if abs(x1 - x0) > 1e-6:
        c.append(box(s, min(x0, x1), max(x0, x1), y0 - r, y0 + r, z0, z1))
    if abs(y1 - y0) > 1e-6:
        c.append(box(s, x0 - r, x0 + r, min(y0, y1), max(y0, y1), z0, z1))
    return c


def support_servo(s, name):     # v1 bracket: base slides ±2 mm along y (gear mesh), 2 posts carry the MG996R flange
    b0, b1, fz = G.UP + G.PT, G.UP + G.PT + G.BR_T, G.SV_FLZ
    xa0, xa1, xb0, xb1 = G.SV_X0 - 9.4, G.SV_X0 - 0.8, G.SV_X1 + 0.8, G.SV_X1 + 9.4
    a = [box(s, xa0, xb1, G.SVY - 11.5, G.SVY + 11.5, b0, b1),
         box(s, xa0, xa1, G.SVY - 9, G.SVY + 9, b1, fz), box(s, xb0, xb1, G.SVY - 9, G.SVY + 9, b1, fz)]
    c = []
    for dx in (-12, 12):                                                                             # M3 x 10 cap screws, heads flush
        c += slot(s, G.SV_XC + dx, G.SVY - G.SV_SLOT, G.SV_XC + dx, G.SVY + G.SV_SLOT, b0 - 1, b1 + 1, 1.7)
        c += slot(s, G.SV_XC + dx, G.SVY - G.SV_SLOT, G.SV_XC + dx, G.SVY + G.SV_SLOT, b1 - 3, b1 + 1, 3.2)
    for side in (-1, 1):
        hx = G.SV_XC + side * 24.375                                                                 # flange holes 48 - 49.5 apart
        for dy in (-5, 5):
            c += slot(s, hx - 0.75, G.SVY + dy, hx + 0.75, G.SVY + dy, fz - 13, fz + 1, 1.7)        # M3 x 12 through the flange
            c.append(nut(s, 2, hx, G.SVY + dy, fz - 8, 0, side * 12))                              # nut slid in from outside
        px0, px1 = (xa0, xa1) if side < 0 else (xb0, xb1)
        c.append(box(s, px0 - 1, px1 + 1, G.SVY - 3.5, G.SVY + 3.5, b1 - 0.1, b1 + 5))               # cable exit
    part(name, solid(a, c), 1270, PETG, True)


def bras(s, name):      # door arm (2 per door): split clamp on the turning rod, L to the door sheet tab
    hub = circle(G.PX, G.PY, 11, 48)
    fl = [(G.PX + 38, G.PY + 14), (G.SX0, G.PY + 14), (G.SX0, G.PY + 26), (G.PX + 38, G.PY + 26)]
    z0, z1 = G.ARM1
    a = [prism(s, hull(hub + fl), z0, z1), box(s, G.PX + 38, G.SX0, G.PY + 14, G.PY + 26, G.FL1[0], G.FL1[1])]
    ca, cc = split_clamp(s, G.PX, G.PY, z0, z1, [(z0 + z1) / 2])
    a += ca
    c = cc + [vcyl(s, G.PX, G.PY, z0 - 1, z1 + 1, 4.05)]                                             # Ø8 bore (snug, clamp closes it)
    for z in (G.FL1[0] + 3.5, G.FL1[1] - 3.5):
        c.append(xcyl(s, G.PX + 37, G.SX0 + 0.1, G.PY + 20, z, 1.7))                                 # sheet tab: M3 button head
        c.append(nut(s, 0, G.PX + 38 + G.NUT_T / 2 - 0.1, G.PY + 20, z, 0, 0))
    part(name, solid(a, c), 1270, PETG, True)


def roue():     # 40T m1.25 on the rod top, tall hub with a 2-screw split clamp (it carries the whole door torque)
    hz0 = G.GZA - 16
    a = [prism(1, gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB), vcyl(1, G.PX, G.PY, hz0, G.GZA, 11)]
    ca, cc = split_clamp(1, G.PX, G.PY, hz0, G.GZA, [hz0 + 4.5, G.GZA - 4.5])
    a += ca
    c = cc + [vcyl(1, G.PX, G.PY, hz0 - 1, G.GZB + 1, 4.05)]
    part("ROUE_PORTE_40T", solid(a, c), 1270, PETG2, True)


def pignon():   # 20T m1.25 on the MG996R round horn: the horn sits in a pocket underneath (centres it), 4x M2 through it
    a = [prism(1, gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB),
         vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R + 3)]                                 # collar around the horn
    c = [vcyl(1, G.PX, G.SVY, G.GZA - G.HORN_T - 1, G.GZA, G.HORN_R + 0.2),                         # horn pocket (open downwards)
         vcyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2)]                                            # horn screw, from the top
    c += [vcyl(1, G.PX + 7.5 * math.cos(math.pi / 2 * k), G.SVY + 7.5 * math.sin(math.pi / 2 * k), G.GZA - 1, G.GZB + 1, 0.8) for k in range(4)]
    part("PIGNON_SERVO_20T", solid(a, c), 1270, PETG2, True)


''' + s[j:]

# ---------------------------------------------------------------- references
rep('''    part("REF_TIGE_D8x110", vcyl(1, G.PX, G.PY, G.LOW, G.LOW + G.ROD_L, 4), 7850, STEEL, False)
''', '''    part("REF_TIGE_D8x166", vcyl(1, G.PX, G.PY, G.ROD_Z0, G.ROD_Z1, 4), 7850, STEEL, False)
''')
rep('''    part("REF_608ZZ", solid([vcyl(1, G.PX, G.PY, G.HUB_Z0, G.HUB_Z0 + 7, 11)], [vcyl(1, G.PX, G.PY, 0, 400, 4)]), 7850, STEEL, False)''',
    '''    part("REF_608ZZ", solid([vcyl(1, G.PX, G.PY, G.LOW + G.PT - 7, G.LOW + G.PT, 11)], [vcyl(1, G.PX, G.PY, 0, 400, 4)]), 7850, STEEL, False)''')
i = s.index("    for s, name in ((1, \"REF_MG996R_D\"), (-1, \"REF_MG996R_G\")):")
j = s.index("    part(\"REF_PILE_3_PIERRES\"")
s = s[:i] + '''    for s, name in ((1, "REF_MG996R_D"), (-1, "REF_MG996R_G")):     # standing on the bracket, horn up (v1)
        b = G.SV_Z0
        part(name, solid([box(s, G.SV_X0, G.SV_X1, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, b, b + G.SV_H),
                          box(s, G.SV_XC - 27.25, G.SV_XC + 27.25, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, b + G.SV_FL, b + G.SV_FL + 2.4),
                          vcyl(s, G.PX, G.SVY, b + G.SV_H, G.GZA - G.HORN_T, 3), vcyl(s, G.PX, G.SVY, G.GZA - G.HORN_T, G.GZA, G.HORN_R)]),
             1200, SERVO, False)
''' + s[j:]

# ---------------------------------------------------------------- main + placements
rep("    socle(); haut(); support_ecrou(); aile(1, \"AILE_D\"); aile(-1, \"AILE_G\"); moyeu(1, \"MOYEU_PORTE_D\"); moyeu(-1, \"MOYEU_PORTE_G\")",
    "    socle(); haut(); support_ecrou(); aile(1, \"AILE_D\"); aile(-1, \"AILE_G\"); support_servo(1, \"SUPPORT_SERVO_D\"); support_servo(-1, \"SUPPORT_SERVO_G\")\n"
    "    bras(1, \"BRAS_PORTE_D\"); bras(-1, \"BRAS_PORTE_G\"); roue()")
rep("    pignon(); bouchon(); tole(); refs()", "    pignon(); tole(); refs()")
rep('''         ("AILE_D", 0, 0, 0), ("AILE_G", 0, 0, 0), ("MOYEU_PORTE_D", 0, 0, 0), ("MOYEU_PORTE_G", 0, 0, 0),''',
    '''         ("AILE_D", 0, 0, 0), ("AILE_G", 0, 0, 0), ("SUPPORT_SERVO_D", 0, 0, 0), ("SUPPORT_SERVO_G", 0, 0, 0),
         ("BRAS_PORTE_D", 0, 0, 0), ("BRAS_PORTE_D", 0, 0, G.ARM2[0] - G.ARM1[0]),
         ("BRAS_PORTE_G", 0, 0, 0), ("BRAS_PORTE_G", 0, 0, G.ARM2[0] - G.ARM1[0]),''')
rep('''        p += [("REF_TIGE_D8x110", dx, 0, 0), ("BOUCHON_TIGE", dx, 0, 0), ("PIGNON_SERVO_20T", dx, 0, 0),
              ("REF_608ZZ", dx, 0, 0), ("REF_608ZZ", dx, 0, G.HUB_Z1 - 7 - G.HUB_Z0)]''',
    '''        p += [("REF_TIGE_D8x166", dx, 0, 0), ("ROUE_PORTE_40T", dx, 0, 0), ("PIGNON_SERVO_20T", dx, 0, 0),
              ("REF_608ZZ", dx, 0, 0), ("REF_608ZZ", dx, 0, G.UP - (G.LOW + G.PT - 7))]''')
# screw-top bearing placement used HUB_Z0 as the 608 reference height
rep('''         ("REF_608ZZ", -G.PX, G.RAIL_YC - G.PY, G.RAIL_Z0 + G.RAIL_L - G.HUB_Z0),             # screw top bearing''',
    '''         ("REF_608ZZ", -G.PX, G.RAIL_YC - G.PY, G.RAIL_Z0 + G.RAIL_L - (G.LOW + G.PT - 7)),    # screw top bearing''')
open(p, "w", encoding="utf-8").write(s)
print("patched")
