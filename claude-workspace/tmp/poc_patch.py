# Replaces whole functions in swpoc.cs (found by name + brace matching) and a few assembly lines.
import sys, re

path = sys.argv[1]
src = open(path, encoding="utf-8").read()

def replace_func(text, name, new):
    i = text.index("    static void " + name + "(")
    j = text.index("{", i)
    depth, k = 0, j
    while True:
        if text[k] == "{": depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0: break
        k += 1
    # keep a leading comment line on the same line as the signature out of the match: replace signature..closing brace
    return text[:i] + new.rstrip("\n") + text[k + 1:]

NEW = {}

NEW["Plaque"] = r'''    // PoC module plate: the 2040 rail goes through it and is clamped by 2x M5 + T-nuts (rail rear face);
    // 2 legs at (±70, 134) to the bench board (M4 threaded rod + nuts, 70 mm)
    static void Plaque()
    {
        var pb = new PB(1);
        pb.Add(Geo.Box(1, -80, 80, 65, G.YF, G.ZIF, G.ZIF + 6)).Add(Geo.Box(1, -35, 35, 30, 65, G.ZIF, G.ZIF + 6));
        pb.Add(Geo.Box(1, -16, 16, 30, G.RAIL_Y0 - 0.2, G.ZIF + 6, 100));                               // clamp lip behind the rail
        pb.Cut(Geo.Box(1, -G.RAIL_X - 0.3, G.RAIL_X + 0.3, G.RAIL_Y0 - 0.2, G.RAIL_Y1 + 0.3, G.ZIF - 1, G.ZIF + 7));   // rail opening
        foreach (var s in new[] { 1.0, -1.0 })
        {
            pb.Cut(Geo.VCyl(s, 70, G.YF - 6, G.ZIF - 1, G.ZIF + 7, 2.25));                               // M4 leg (±70, 134)
            pb.Cut(Geo.YCyl(s, 10, 29, G.RAIL_Y0 + 1, 88, 2.75));                                         // M5x16 into a T-nut (rail slot x ±10)
        }
        Finish(pb, "PLAQUE_MODULE", 1270, PETG, true);
    }
'''

NEW["Chariot"] = r'''    // PoC carriage: 4 V-wheels on the 2040 rail (bolted through the back wall), floating T8 nut, backstop tabs; bolted to the 2 wings
    static void Chariot()
    {
        var pb = new PB(1);
        foreach (var z in new[] { G.LOW, G.UP })
        {
            pb.Add(Geo.Box(1, -60, 60, G.CY0, G.CY1, z, z + G.PT)).Add(Geo.Box(1, -50, 50, G.CY1, G.BIB_Y0, z, z + G.PT));
        }
        pb.Add(Geo.Box(1, -60, 60, G.BW_Y0, G.CY0 + 6, G.LOW, G.UP + G.PT));                              // back wall, 14 mm thick
        foreach (var s in new[] { 1.0, -1.0 })
        {
            pb.Add(Geo.Box(s, 54, 60, G.CY0, G.CY1, G.LOW + G.PT, G.UP));                                  // junction wall
            pb.Add(Geo.Box(s, 30, 45, G.BIB_Y0 - 6, G.BIB_Y0, G.LOW + G.PT, 118));                        // backstop tabs
            pb.Add(Geo.Box(s, 30, 45, G.BIB_Y0 - 6, G.BIB_Y0, 182, G.UP));
            foreach (var z in new[] { G.WH_Z0, G.WH_Z1 })                                                  // wheel bolts M5x30, heads inside
                pb.Cut(Geo.YCyl(s, G.WH_X, G.BW_Y0 - 1, G.CY0 + 7, z, s > 0 ? 2.6 : 3.56));               // -x side: eccentric spacer Ø7.12
            foreach (var yz in new[] { new[] { 85.0, 115 }, new[] { 115.0, 115 }, new[] { 85.0, 185 }, new[] { 115.0, 185 } })
                pb.Cut(Geo.XCyl(s, 50, 61, yz[0], yz[1], 1.7));                                              // M3x16 + nut to the wing
            foreach (var z in new[] { 110.0, 191 })
            {
                pb.Cut(Geo.YCyl(s, 37.5, G.BIB_Y0 - 7, G.BIB_Y0 + 1, z, 1.7));                             // M3x10 backstop...
                pb.Cut(Nut(s, 1, 37.5, G.BIB_Y0 - 6 + G.NUT_T / 2 - 0.1, z, 1, 0));                         // ...nut pressed in from the back
            }
        }
        pb.Cut(Geo.VCyl(1, 0, G.RODY, G.UP - 1, G.UP + G.PT + 1, 5.6));                                    // T8 nut body Ø10.2, 0.5 mm float
        foreach (var q in new[] { new[] { 8.0, 0 }, new[] { -8.0, 0 }, new[] { 0.0, 8 }, new[] { 0.0, -8 } })
            pb.Cut(Geo.VCyl(1, q[0], G.RODY + q[1], G.UP - 1, G.UP + G.PT + 1, 2.0));                      // M3 + nut below, Ø4: nut floats
        pb.Cut(Geo.VCyl(1, 0, G.RODY, G.LOW - 1, G.LOW + G.PT + 1, 5.0));                                  // screw clearance (if left longer)
        Finish(pb, "CHARIOT_CENTRE", 1270, PETG, true);
    }
'''

NEW["Aile"] = r'''    // wing: door hinge (2x 608ZZ in bosses) + seat of the servo bracket; bolted to the centre
    static void Aile(double s, string name)
    {
        var pb = new PB(s);
        pb.Add(Geo.Box(s, 60, 66, G.CY0, G.CY1, G.LOW, G.UP + G.PT));                                // junction wall
        pb.Add(Geo.Box(s, 60, G.CX, G.CY0, G.CY1, G.LOW, G.LOW + G.PT));                             // lower plate
        pb.Add(Geo.Box(s, 60, G.CX, G.CY0, G.CY1, G.UP, G.UP + G.PT));                               // upper plate
        pb.Add(Geo.Box(s, 66, 120, G.CY0, G.CY0 + 6, G.LOW + G.PT, G.UP));                           // back web
        pb.Add(Geo.VCyl(s, G.PX, G.PY, G.LOW - 3, G.LOW + G.PT, G.BOSS_R));                          // 608 boss under the lower plate
        pb.Add(Geo.VCyl(s, G.PX, G.PY, G.UP, G.UP + G.PT + 3, G.BOSS_R));                            // 608 boss over the upper plate
        pb.Cut(Geo.VCyl(s, G.PX, G.PY, G.LOW + G.PT + 0.1 - G.BRG_T - 0.1, G.LOW + G.PT + 0.1, G.BRG_R));   // 608ZZ from the top
        pb.Cut(Geo.VCyl(s, G.PX, G.PY, G.UP - 0.1, G.UP - 0.1 + G.BRG_T + 0.1, G.BRG_R));                // 608ZZ from below
        pb.Cut(Geo.VCyl(s, G.PX, G.PY, G.LOW - 4, G.UP + G.PT + 4, 5.0));                            // shaft clearance
        foreach (var yz in new[] { new[] { 85.0, 115 }, new[] { 115.0, 115 }, new[] { 85.0, 185 }, new[] { 115.0, 185 } })
            pb.Cut(Geo.XCyl(s, 59, 70, yz[0], yz[1], 1.7));
        foreach (var dx in new[] { -12.0, 12 })                                                     // servo bracket: 2x M3 + nut below
        {
            pb.Cut(Geo.VCyl(s, G.SV_XC + dx, G.SVY, G.UP - 1, G.UP + G.PT + 1, 1.7));
            pb.Cut(Nut(s, 2, G.SV_XC + dx, G.SVY, G.UP + G.NUT_T / 2 - 0.1, 2, 0));
        }
        Finish(pb, name, 1270, PETG2, true);
    }
'''

NEW["Traverse"] = r'''    // PoC crossbar: sits on the rail top, clamped by 2x M5 + T-nuts; NEMA17 on top (screw down through a coupler);
    // 2 posts are the +18 mm up stop on the carriage top
    static void Traverse()
    {
        var pb = new PB(1);
        pb.Add(Geo.Box(1, -55, 55, 30, 124, G.XB_Z0, G.XB_Z1));
        pb.Add(Geo.Box(1, -16, 16, 30, G.RAIL_Y0 - 0.2, 240, G.XB_Z0));                                  // clamp lip behind the rail
        foreach (var s in new[] { 1.0, -1.0 })
        {
            pb.Add(Geo.VCyl(s, 40, G.RODY, G.STOP_Z, G.XB_Z0, 9));                                       // up stop posts
            pb.Cut(Geo.YCyl(s, 10, 29, G.RAIL_Y0 + 1, 255, 2.75));                                       // M5x16 into a T-nut
            foreach (var d in new[] { -15.5, 15.5 }) pb.Cut(Geo.VCyl(s, 15.5, G.RODY + d, G.XB_Z0 - 1, G.XB_Z1 + 1, 1.7));   // NEMA17 M3x10
        }
        pb.Cut(Geo.VCyl(1, 0, G.RODY, G.XB_Z0 - 1, G.XB_Z1 + 1, 11.5));                                  // Ø22 motor pilot
        Finish(pb, "TRAVERSE_MOTEUR", 1270, PETG, true);
    }
'''

NEW["Refs"] = r'''    static void Refs()       // reference parts, simplified (not made)
    {
        Finish(new PB(1).Add(Geo.Box(1, -G.RAIL_X, G.RAIL_X, G.RAIL_Y0, G.RAIL_Y1, 0, G.RAIL_TOP)), "REF_PROFIL_2040x270", 2700, DARK, false);
        Finish(new PB(1).Add(Geo.YCyl(1, G.WH_X, G.RY - G.WH_W / 2, G.RY + G.WH_W / 2, G.WH_Z0, G.WH_R)), "REF_ROUE_V", 1400, DARK, false);
        Finish(new PB(1).Add(Geo.Sub(Geo.VCyl(1, G.PX, G.PY, 96, G.GZB, 4), Geo.Box(1, G.PX - 5, G.PX + 5, G.PY - 5, G.PY - 3.5, 90, 270))),
            "REF_AXE_D8x166", 7850, STEEL, false);
        Finish(new PB(1).Add(Geo.VCyl(1, G.PX, G.PY, G.LOW + G.PT - 7, G.LOW + G.PT, 11)).Cut(Geo.VCyl(1, G.PX, G.PY, 0, 300, 4)),
            "REF_608ZZ", 7850, STEEL, false);
        Finish(new PB(1).Add(Geo.Box(1, -21.15, 21.15, G.RODY - 21.15, G.RODY + 21.15, G.XB_Z1, G.XB_Z1 + 40))
                        .Add(Geo.VCyl(1, 0, G.RODY, G.XB_Z1 - 2, G.XB_Z1, 11)).Add(Geo.VCyl(1, 0, G.RODY, 252, G.XB_Z1 - 2, 2.5)),
            "REF_NEMA17", 3500, DARK, false);
        Finish(new PB(1).Add(Geo.VCyl(1, 0, G.RODY, G.CPL_Z0, G.CPL_Z1, 9.5)).Cut(Geo.VCyl(1, 0, G.RODY, G.CPL_Z0 - 1, G.SCREW_Z1, 4))
                        .Cut(Geo.VCyl(1, 0, G.RODY, G.CPL_Z0 - 1, G.CPL_Z1 + 1, 2.5)), "REF_COUPLEUR_5x8", 2700, ALU, false);
        Finish(new PB(1).Add(Geo.VCyl(1, 0, G.RODY, G.SCREW_Z1 - G.SCREW_L, G.SCREW_Z1, 4)), "REF_VIS_T8x130", 7850, STEEL, false);
        Finish(new PB(1).Add(Geo.VCyl(1, 0, G.RODY, G.UP + G.PT, G.UP + G.PT + 3.5, 11)).Add(Geo.VCyl(1, 0, G.RODY, G.UP + G.PT - 11.5, G.UP + G.PT, 5.1))
                        .Cut(Geo.VCyl(1, 0, G.RODY, 0, 300, 4)), "REF_ECROU_T8", 8500, BRASS, false);
        foreach (var s in new[] { 1.0, -1.0 })
        {
            double b = G.SV_Z0;
            var pb = new PB(s).Add(Geo.Box(s, G.SV_X0, G.SV_X1, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, b, b + G.SV_H))
                .Add(Geo.Box(s, G.SV_XC - 27.25, G.SV_XC + 27.25, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, b + G.SV_FL, b + G.SV_FL + 2.4))
                .Add(Geo.VCyl(s, G.PX, G.SVY, b + G.SV_H, G.GZA - 2, 3)).Add(Geo.VCyl(s, G.PX, G.SVY, G.GZA - 2, G.GZA, 10.5));
            Finish(pb, s > 0 ? "REF_MG996R_D" : "REF_MG996R_G", 1200, SERVO, false);
        }
        var pile = new PB(1);
        for (int i = 0; i < 3; i++) pile.Add(Geo.Box(1, -160, 160, G.BIB_Y1, G.BIB_Y1 + 110, 110 * i + 0.5, 110 * (i + 1) - 0.5));
        Finish(pile, "REF_PILE_3_PIERRES", 100, BOX, false);
    }
'''

for name, body in NEW.items():
    src = replace_func(src, name, body)

# assembly + render: line-level swaps (each must match exactly once)
swaps = [
    ('add("TRAVERSE_MOTEUR", 0, 0, 0); add("REF_NEMA17_VIS_TR8x2", 0, 0, 0); add("REF_ECROU_T8x2", 0, 0, 0);',
     'add("TRAVERSE_MOTEUR", 0, 0, 0); add("REF_NEMA17", 0, 0, 0); add("REF_COUPLEUR_5x8", 0, 0, 0);\n'
     '        add("REF_VIS_T8x130", 0, 0, 0); add("REF_ECROU_T8", 0, 0, 0); add("REF_PROFIL_2040x270", 0, 0, 0);'),
    ('foreach (var dx in new[] { 0.0, -2 * G.RODX })', 'foreach (var dx in new[] { 0.0, -2 * G.WH_X })'),
    ('add("REF_TIGE_D8x176", dx, 0, 0);', 'add("REF_ROUE_V", dx, 0, 0);'),
    ('add("REF_LM8UU", dx, 0, 0); add("REF_LM8UU", dx, 0, G.UP - 24 - (G.LOW + G.PT));', 'add("REF_ROUE_V", dx, 0, G.WH_Z1 - G.WH_Z0);'),
    ('add("REF_688ZZ", dx, 0, 0); add("REF_688ZZ", dx, 0, G.UP - (G.LOW + 1));', 'add("REF_608ZZ", dx, 0, 0); add("REF_608ZZ", dx, 0, G.UP - (G.LOW + G.PT - 7));'),
    ('add(dx == 0 ? "REF_MG995_D" : "REF_MG995_G", 0, 0, 0);', 'add(dx == 0 ? "REF_MG996R_D" : "REF_MG996R_G", 0, 0, 0);'),
    ('string path = P.F("MODULE_CLAPETS.SLDASM");', 'string path = P.F("MODULE_CLAPETS_POC.SLDASM");'),
    ('var m = P.Open(P.F("MODULE_CLAPETS.SLDASM"));', 'var m = P.Open(P.F("MODULE_CLAPETS_POC.SLDASM"));'),
    ('Path.Combine(P.Cad, "STEP", "MODULE_CLAPETS.STEP")', 'Path.Combine(P.Cad, "STEP", "MODULE_CLAPETS_POC.STEP")'),
    ('"images", "module_" + v[1] + ".png"', '"images", "poc_" + v[1] + ".png"'),
]
for a, b in swaps:
    n = src.count(a)
    if n != 1: sys.exit("swap matched %d times: %s" % (n, a))
    src = src.replace(a, b)

open(path, "w", encoding="utf-8").write(src)
print("patched")
