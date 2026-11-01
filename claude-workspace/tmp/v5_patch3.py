# v5_patch3.py - v5 changes (2026-10-29): middle cup on the head axis (axis z 165, cups 85/165/245, flange = middle
# station mount), longer doors (+7 mm), servo strap for the door servos, tube notches, motion study updated.
import os
import sys

D = sys.argv[1]
p = os.path.join(D, "v5_fc.py")
s = open(p, encoding="utf-8").read()


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, "v5_fc count %d: %s" % (s.count(old), old[:100])
    s = s.replace(old, new)


# ---------------------------------------------------------------- parameters
rep("    LIFT_CARRY, LIFT_TURN = 15, 72", "    LIFT_CARRY, LIFT_TURN = 15, 75                          # turn: axis 165 + 75 = 240 >= 229.8 (stack half-diagonal) + 10")
rep("    HZ = 175                                                # head axis along y at x 0, z 175",
    "    HZ = 165                                                # head axis along y at x 0, z 165 = middle box centre (middle cup on it)")
rep("    RES_ROT_R, RES_ROT_Y0 = 140, 108.0                      # turning disc: R 140 (needs 126), from the carrier rear to the face",
    "    RES_ROT_R, RES_ROT_Y0 = 140, 108.0                      # turning disc: R 140 (head needs R 108), from the carrier rear to the face")
rep("    RES_REST_X = 36                                         # rest envelope: cups vertical, x ±36 (doors fold in front of it)",
    "    RES_REST_X = 30                                         # rest envelope: carrier/rings x ±28 + 2 (folded door tips stop at x 30)")
rep("    SY0, SY1, TAB_Y0 = 141, 176, 128\n    PAD_Y0, PAD_Y1 = 145, 175",
    "    SY0, SY1, TAB_Y0 = 141, 183, 128                        # doors +7 mm (max: folded tips must stop at x 30)\n    PAD_Y0, PAD_Y1 = 145, 182")
rep("    A_FOLD, A_CLAMP, A_OPEN = 90.0, 3.0, -35.0             # open -35: the whole door is behind the face (stack turns clear)",
    "    A_FOLD, A_CLAMP, A_OPEN = 90.0, 3.0, -38.0             # open -38: the whole door is behind the face; servo 128 x 1.4 = 179 deg")
rep("    CUPS_Z = (77, 135, 240)                                 # one cup per box",
    "    CUPS_Z = (85, 165, 245)                                 # one cup per box, the middle one ON the head axis (box centre)")
rep('''    HB_Y0, HB_Y1 = PL_Y1, 92.0                              # bearing tube; 608 at both ends (35 mm apart)
    HG_Y0, HG_Y1 = 94.5, 102.5                              # gear plane (head 30T on the shaft, 20T on the servo horn)
    HF_Y0, HF_Y1 = HG_Y1, 108.5                             # flange (same part as the 30T gear), split clamp on the shaft
    CA_Y0, CA_Y1 = HF_Y1, HF_Y1 + 6                         # MDF 6 carrier 108.5..114.5
    RIM_Y1, RING_Y1 = CA_Y1 + 3, CA_Y1 + 6
    TH_Y0, TH_Y1 = CA_Y1 - 3.3, 122.0''',
'''    HB_Y0, HB_Y1 = PL_Y1, 86.0                              # bearing tube; floor 50.3..54 (pocket for module A's M3 head)
    HBR_Y0 = 54.0                                           # 608s at y 54..61 and 79..86 (25 mm apart), bore Ø22.1 from the front
    HC_Y0, HC_Y1 = 86.5, 94.5                               # shaft clamp hub, behind the gear
    HG_Y0, HG_Y1 = 94.5, 102.5                              # gear plane (head 30T on the shaft, 20T on the servo horn)
    HF_Y0, HF_Y1 = 103.0, 109.0                             # flange Ø56 = mount of the middle cup station (its 3 screws)
    CA_Y0, CA_Y1 = HF_Y1, HF_Y1 + 6                         # MDF 6 carrier 109..115
    RIM_Y1, RING_Y1 = CA_Y1 + 3, CA_Y1 + 6
    TH_Y0, TH_Y1 = CA_Y1 - 3.0, 122.0                       # TPU hub can move back 3 mm into the carrier hole''')
rep('''    HS_ANG = 45                                             # head servo axis 45 deg down-left of the head axis''',
    '''    HS_ANG = 25                                             # head servo axis 25 deg down-left of the head axis''')
rep('''G.HS_ANG = 25                                       # (set after the clearance check: body clear of the boss + M3 heads)
G.HS_X = -G.HGC * math.sin(math.radians(G.HS_ANG))  # (-13.2, 146.7)''',
'''G.HS_X = -G.HGC * math.sin(math.radians(G.HS_ANG))  # (-13.2, 136.7): clear of the boss and module A's M3 heads''')

# ---------------------------------------------------------------- door unit: posts extended above the flange + strap
rep('''    for bz in (G.PL_ZC - G.SPRING_V, G.PL_ZC + G.SPRING_V):
        c.append(ycyl(s, G.SPRING_U, G.PL_Y1 - 1, G.PL_Y1 + 7, bz, 2.25))
        c.append(box(s, G.SPRING_U - 4.1, G.SPRING_U + 4.1, G.PL_Y1 + 2.4, G.PL_Y1 + 9, bz - 3.6, bz + 3.6))
    part(name, solid(a, c), 1270, PETG2, "print", "A")''',
'''    for bz in (G.PL_ZC - G.SPRING_V, G.PL_ZC + G.SPRING_V):
        c.append(ycyl(s, G.SPRING_U, G.PL_Y1 - 1, G.PL_Y1 + 7, bz, 2.25))
        c.append(box(s, G.SPRING_U - 4.1, G.SPRING_U + 4.1, G.PL_Y1 + 2.4, G.PL_Y1 + 9, bz - 3.6, bz + 3.6))
    # servo strap seats: both posts continue above the flange to the body top (z 86); the outer one through a web outside
    # the flange ear. The strap (A_BRIDE_SERVO) screws on them and presses the servo down onto its flange screws.
    ztop = G.SV_BOT + G.SV_H
    for side in (-1, 1):
        hx = G.SV_XC + side * 24.375
        y0 = G.SVY - 11 if side > 0 else G.PL_Y1
        a.append(box(s, hx - 3.8, hx + 3.8, y0, G.SVY + 11, G.SV_FLZ + 2.4, ztop))
        c += [vcyl(s, hx, G.SVY, ztop - 9, ztop + 1, 1.7), nut(s, 2, hx, G.SVY, ztop - 4.5, 0, side * 10)]
    a.append(box(s, 148.5, 150, G.SVY - 11, G.SVY + 11, G.LOW + G.PT, ztop))
    part(name, solid(a, c), 1270, PETG2, "print", "A")


def bride_servo():      # strap over the door servo body (the same part left and right): 2x M3 into the post tops
    ztop = G.SV_BOT + G.SV_H
    xa, xb = G.SV_XC - 24.375, G.SV_XC + 24.375
    a = [box(1, xa - 3.8, xb + 3.8, G.SVY - 6, G.SVY + 6, ztop, ztop + 4)]
    c = [vcyl(1, G.PX, G.SVY, ztop - 1, ztop + 5, 6.5)]                                            # output shaft passes
    c += [vcyl(1, x, G.SVY, ztop - 1, ztop + 5, 1.7) for x in (xa, xb)]
    part("A_BRIDE_SERVO", solid(a, c), 1270, PETG, "print", "A")''')

# ---------------------------------------------------------------- head bracket: bearing bore from the front, floor + pocket
rep('''    c = [ycyl(1, 0, G.HB_Y0 - 1, G.HB_Y0 + G.BRG_T, hz, G.BRG_R), ycyl(1, 0, G.HB_Y1 - G.BRG_T, G.HB_Y1 + 1, hz, G.BRG_R),
         ycyl(1, 0, G.HB_Y0 - 1, G.HB_Y1 + 1, hz, 5.0)]''',
'''    c = [ycyl(1, 0, G.HBR_Y0, G.HB_Y1 + 1, hz, G.BRG_R),                                              # both 608 slide in from the front
         ycyl(1, 0, G.HB_Y0 - 1, G.HB_Y1 + 1, hz, 5.0)]''')

# ---------------------------------------------------------------- head hub: clamp hub behind the 30T, flange = middle station mount
i = s.index("def tete_moyeu():")
j = s.index("def tete_pignon():")
s = s[:i] + '''def tete_moyeu():       # clamp hub + 30T gear + Ø56 flange in one part. The middle cup station screws INTO the flange
    hz = G.HZ                                    # (3x M3, nuts in pockets at the back): it also holds the carrier.
    ang_to_servo = math.degrees(math.atan2(G.HS_Z - hz, G.HS_X))
    a = [ycyl(1, 0, G.HC_Y0, G.HC_Y1, hz, 10),                                                       # clamp hub
         box(1, -6, 6, G.HC_Y0, G.HC_Y1, hz + 4, hz + 14),                                           # its lug (up: away from the pinion)
         prism_y(gear(0, hz, G.GM, G.HGZ2, ang_to_servo + 180.0 / G.HGZ2, 0.15), G.HG_Y0, G.HG_Y1),
         ycyl(1, 0, G.HG_Y1 - 0.1, G.HF_Y0 + 0.1, hz, 12),                                          # neck gear -> flange
         ycyl(1, 0, G.HF_Y0, G.HF_Y1, hz, G.ST_R_RING)]
    c = [ycyl(1, 0, G.HC_Y0 - 1, G.HF_Y0 + 1.5, hz, 4.05),                                          # shaft (blind: ends in the flange)
         box(1, -0.6, 0.6, G.HC_Y0 - 1, G.HC_Y1 + 0.01, hz, hz + 15),                                # clamp slot
         xcyl(1, -7, 7, (G.HC_Y0 + G.HC_Y1) / 2, hz + 9.5, 1.7), xcyl(1, -7, -4.5, (G.HC_Y0 + G.HC_Y1) / 2, hz + 9.5, 3.0),
         box(1, 6 - G.NUT_T, 6 + 0.01, G.HC_Y0 - 1, G.HC_Y1 + 0.01, hz + 9.5 - 2.8, hz + 9.5 + 2.8),
         ycyl(1, 0, G.HF_Y1 - 3, G.HF_Y1 + 1, hz, 10)]                                              # room for the TPU hub to move back
    for ang in G.ST_BOLT_A:
        t = math.radians(ang)
        x, z = G.ST_BOLT_R * math.cos(t), hz + G.ST_BOLT_R * math.sin(t)
        c += [ycyl(1, x, G.HF_Y0 - 1, G.HF_Y1 + 1, z, 1.7), prism_y(circle(x, z, 3.25, 6), G.HF_Y0 - 1, G.HF_Y0 + 2.6)]
    part("B_MOYEU_TETE_30T", solid(a, c), 1270, PETG2, "print", "B")


''' + s[j:]

# ---------------------------------------------------------------- carrier: middle station screws into the flange; tube notches
i = s.index("def tete_plateau():")
j = s.index("def tete_station_tpu():")
s = s[:i] + '''def tete_plateau():     # MDF 6 carrier: 3 stations (middle on the axis, clamped onto the hub flange), tube notches
    a = [prism_y(stadium(G.CA_Z0, G.CA_Z1, G.ST_R_RING), G.CA_Y0, G.CA_Y1)]
    c = []
    for cz in G.CUPS_Z:
        c.append(ycyl(1, 0, G.CA_Y0 - 1, G.CA_Y1 + 1, cz, G.ST_R_HOLE))
        for ang in G.ST_BOLT_A:
            t = math.radians(ang)
            c.append(ycyl(1, G.ST_BOLT_R * math.cos(t), G.CA_Y0 - 1, G.CA_Y1 + 1, cz + G.ST_BOLT_R * math.sin(t), 1.7))
        # tube notch: from the station hole to the +x edge, in the carrier's thickness (the tube leaves sideways, then back)
        c.append(box(1, G.ST_R_HOLE - 1, G.ST_R_RING + 1, G.CA_Y0 - 1, G.CA_Y1 + 1, cz - 2.6, cz + 2.6))
    part("B_PLATEAU_TETE", solid(a, c), 750, MDF, "mdf", "B")


''' + s[j:]

# ---------------------------------------------------------------- refs + placements + build
rep('''    part("REF_608ZZ_TETE", solid([ycyl(1, 0, G.HB_Y0, G.HB_Y0 + 7, G.HZ, 11)], [ycyl(1, 0, 0, 200, G.HZ, 4)]), 7850, STEEL, "ref", "B")''',
    '''    part("REF_608ZZ_TETE", solid([ycyl(1, 0, G.HBR_Y0, G.HBR_Y0 + 7, G.HZ, 11)], [ycyl(1, 0, 0, 200, G.HZ, 4)]), 7850, STEEL, "ref", "B")''')
rep('''    part("REF_AXE_TETE_D8", ycyl(1, 0, G.HB_Y0 + 0.5, G.HF_Y1, G.HZ, 4), 7850, STEEL, "ref", "B")''',
    '''    part("REF_AXE_TETE_D8", ycyl(1, 0, G.HBR_Y0 + 0.5, G.HF_Y0 + 1.5, G.HZ, 4), 7850, STEEL, "ref", "B")''')
rep('''         ("REF_608ZZ_TETE", 0, G.HB_Y1 - 7 - G.HB_Y0, 0, "carriage"),''',
    '''         ("REF_608ZZ_TETE", 0, G.HB_Y1 - 7 - G.HBR_Y0, 0, "carriage"),
         ("A_BRIDE_SERVO", 0, 0, 0, "carriage"), ("A_BRIDE_SERVO", -2 * G.PX, 0, 0, "carriage"),''')
rep('''    roue_porte(); pignon_porte(); tole()''', '''    roue_porte(); pignon_porte(); tole(); bride_servo()''')
open(p, "w", encoding="utf-8").write(s)

q = os.path.join(D, "motion_v5.py")
t = open(q, encoding="utf-8").read()


def rept(old, new):
    global t
    assert t.count(old) == 1, "motion: " + old[:80]
    t = t.replace(old, new)


rept("PX, PY, SVY, HZ = 131.0, 82.0, 52.0, 175.0        # = v5_fc.py class G", "PX, PY, SVY, HZ = 131.0, 82.0, 52.0, 165.0        # = v5_fc.py class G")
rept("A_FOLD, A_OPEN_APPROACH, A_CLAMP, A_OPEN = 90.0, -30.0, 3.0, -35.0", "A_FOLD, A_OPEN_APPROACH, A_CLAMP, A_OPEN = 90.0, -30.0, 3.0, -38.0")
rept('''    (1.0, 0, A_OPEN, 0, 1, 1, 1, "cups hold, doors open -35 deg"),''', '''    (1.0, 0, A_OPEN, 0, 1, 1, 1, "cups hold, doors open -38 deg"),''')
rept('''    (2.0, 72, A_OPEN, 0, 1, 1, 1, "lift 72 mm with the stack"),
    (2.0, 72, A_OPEN, 90, 1, 1, 1, "turn the stack 90 deg"),''', '''    (2.0, 75, A_OPEN, 0, 1, 1, 1, "lift 75 mm with the stack"),
    (2.0, 75, A_OPEN, 90, 1, 1, 1, "turn the stack 90 deg"),''')
rept('''    (1.5, 0, A_OPEN, 90, 1, 1, 1, "lower (towers 15 mm above the table)"),''', '''    (1.5, 0, A_OPEN, 90, 1, 1, 1, "lower (towers 5 mm above the table)"),''')
open(q, "w", encoding="utf-8").write(t)
print("patched")
