// =============================================================================================== parameters
// Robot frame (mm): x right, y towards the stack, z up, z = 0 = table / bench board. The stack face is y = 143.
// [PH] = PLACEHOLDER: printer part not measured yet (Two Trees, no CAD found). Measure, edit, rerun "swpoc.exe all".
static class G
{
    public const double YF = 140, BOX_Y0 = 143;                   // module face, stack face
    // ---- printer parts (Two Trees) [PH] ----
    public const double RAIL_W = 20, RAIL_DX = 40;                // [PH] 2 Y rails = 2020 profiles, centres x ±40
    public const double RAIL_YC = 58.5, RAIL_Z0 = 6, RAIL_L = 330;   // rail centre y; rails stand on the base (z 6 .. 336)
    public const double PL_Y0 = 70, PL_T = 3;                     // butterfly plate, vertical: rear face y 70, front 73
    public const double PL_HW = 110, PL_Z0 = 80, PL_Z1 = 260;     // [PH] outline modelled as a rectangle x ±110, z 80..260
    public const double WH_X = RAIL_DX + RAIL_W / 2 + 10.15;      // [PH] wheels ride the rails' outer slots: x ±60.15
    public const double WH_R = 10.15, WH_W = 10.2, WH_Z0 = 100, WH_Z1 = 240;    // [PH] wheel heights on the plate
    // bolt holes through the plate (existing plate holes to match) [PH]
    public static readonly double[][] WING_BOLTS = { new[] { 78.0, 112 }, new[] { 98.0, 112 }, new[] { 78.0, 190 }, new[] { 98.0, 190 } };  // (x, z) right wing
    public static readonly double[][] NUT_BOLTS = { new[] { -15.0, 140 }, new[] { 15.0, 140 }, new[] { -15.0, 168 }, new[] { 15.0, 168 } };
    // ---- lift: NEMA17 standing on the base, coupler, T8 screw up the middle between the rails, 608 at the top ----
    public const double MOT_Z1 = 46, SHELF_T = 6;                 // motor face (top of the body) z 46, shelf 46..52
    public const double CPL_Z0 = 58, CPL_Z1 = 83, SCREW_Z0 = 71, SCREW_Z1 = 343;   // coupler; screw 272 mm (cut to length)
    public const double NUT_Z = 150;                              // nut shelf bottom (shelf 150..156, flange on top)
    public const double TOP_Z0 = 324, TOP_Z1 = 344;               // top tie (rail tops at 336), 608 for the screw end
    public const double LIFT = 18;                                // max travel (software); 15 mm used
    // ---- door units (one per side, bolted on the plate's wings) ----
    public const double PX = 125, PY = 116;                       // fixed hinge shaft axis (right)
    public const double LOW = 96, UP = 200, PT = 6;               // wing plates
    public const double W_X0 = 66, W_X1 = 146, W_Y0 = PL_Y0 + PL_T, W_Y1 = 131;
    public const double HUB_R = 14, HUB_Z0 = 103.8, HUB_Z1 = 198.2;   // door hub, turns on 2x 608ZZ (M8 washer each end)
    public const double BRG_R = 11.05, BRG_T = 7.1;
    // gears m1.25: 20T pinion on the MG996R (hanging under the upper plate, horn down) -> 32T ring on the hub, x1.6
    public const double GM = 1.25; public const int GZ1 = 20, GZ2 = 32;
    public const double GC = GM * (GZ1 + GZ2) / 2, SVY = PY - GC;            // servo axis (125, 83.5)
    public const double SV_L = 40.7, SV_W = 19.7, SV_H = 37.0, SV_FL = 26.6, SV_OUT = 10.0, SV_HORN = 43.5;
    public const double SV_X0 = PX - SV_OUT, SV_X1 = SV_X0 + SV_L, SV_XC = (SV_X0 + SV_X1) / 2;   // body x 115..155.7
    public const double SV_TOP = UP;                              // servo body "bottom" (cable end) against the plate
    public const double SV_FLZ = SV_TOP - SV_FL;                  // flange face on the body side (posts end here)
    public const double GZB = SV_TOP - SV_HORN, GZA = GZB - 8;    // gears z 148.5..156.5
    // door: longer than v1 so the pads grip around the box centre (no backstop)
    public const double SHEET_T = 3, PAD_T = 10;                  // 3 mm plywood/alu sheet
    public const double SX0 = 170, SX1 = SX0 + SHEET_T;           // pad face at x 160 = box end
    public const double SY0 = BOX_Y0 + 2, SY1 = 225, TAB_Y0 = PY + 14;   // sheet y 145..225, tabs back to 130
    public const double PAD_Y0 = 172, PAD_Y1 = 220;
    public const double DZ0 = 15, DZ1 = 320;
    public const double ARM1_Z0 = 104, ARM1_Z1 = 114, ARM2_Z0 = 188, ARM2_Z1 = 198;
    public const double FL1_Z0 = 100, FL1_Z1 = 118, FL2_Z0 = 180, FL2_Z1 = 198;
    public const double NUT_W = 5.6, NUT_L = 6.4, NUT_T = 2.6;    // M3 nut trap
    // reserved block for the future suction head (design principle: reserve space)
    public const double HEAD_X = 60, HEAD_Y0 = W_Y0 + 3, HEAD_Z0 = 90, HEAD_Z1 = 330;
}

// =============================================================================================== parts
static class Parts
{
    public static readonly double[] PETG = { 0.95, 0.45, 0.10 }, PETG2 = { 0.20, 0.45, 0.85 }, ALU = { 0.78, 0.80, 0.83 },
        STEEL = { 0.62, 0.63, 0.66 }, DARK = { 0.13, 0.13, 0.15 }, FOAM = { 0.25, 0.65, 0.35 }, WOOD = { 0.80, 0.65, 0.45 },
        BRASS = { 0.80, 0.62, 0.25 }, BOX = { 0.85, 0.72, 0.48 }, SERVO = { 0.10, 0.10, 0.12 }, GHOST = { 0.30, 0.80, 0.40 };

    public static readonly List<string> Printed = new List<string>();

    static void Finish(PB pb, string name, double rho, double[] rgb, bool printed, double transp = 0)
    {
        var bodies = pb.Solve();
        var m = P.NewDoc(false);
        foreach (var b in bodies) ((PartDoc)m).CreateFeatureFromBody3(b, false, 0);
        m.Extension.SetUserPreferenceDouble((int)swUserPreferenceDoubleValue_e.swMaterialPropertyDensity, 0, rho);
        m.MaterialPropertyValues = new double[] { rgb[0], rgb[1], rgb[2], 0.6, 0.6, 0.4, 0.3, transp, 0 };
        m.ForceRebuild3(false);
        var mp = (MassProperty)m.Extension.CreateMassProperty();
        var bx = (double[])((PartDoc)m).GetPartBox(true);
        Console.WriteLine(string.Format(P.CI, "{0,-24} bodies {1}  mass {2,7:F1} g   size {3:F1} x {4:F1} x {5:F1} mm (x, y, z)",
            name, bodies.Count, mp.Mass * 1000, (bx[3] - bx[0]) * 1000, (bx[5] - bx[2]) * 1000, (bx[4] - bx[1]) * 1000));
        m.ShowNamedView2("*Isometric", 7); m.ViewZoomtofit2();
        P.SaveAs(m, P.F(name + ".SLDPRT"), false);
        P.SaveAs(m, Path.Combine(P.Cad, "STEP", name + ".STEP"), true);
        if (printed) { P.SaveAs(m, Path.Combine(P.Cad, "STL", name + ".STL"), true); Printed.Add(name); }
        P.App.CloseDoc(m.GetTitle());
    }

    static void StlPrefs()
    {
        var a = P.App;
        a.SetUserPreferenceIntegerValue((int)swUserPreferenceIntegerValue_e.swSTLQuality, (int)swSTLQuality_e.swSTLQuality_Custom);
        a.SetUserPreferenceDoubleValue((int)swUserPreferenceDoubleValue_e.swSTLDeviation, 0.00001);
        a.SetUserPreferenceDoubleValue((int)swUserPreferenceDoubleValue_e.swSTLAngleTolerance, 0.0349);
        a.SetUserPreferenceToggle((int)swUserPreferenceToggle_e.swSTLBinaryFormat, true);
        a.SetUserPreferenceIntegerValue((int)swUserPreferenceIntegerValue_e.swExportStlUnits, (int)swLengthUnit_e.swMM);
    }

    public static void Test()
    {
        var pb = new PB(1);
        pb.Prism(new List<double[]> { new[] { 0.0, 20 }, new[] { 10.0, 20 }, new[] { 10.0, 30 }, new[] { 0.0, 30 } }, 5, 8);
        pb.Add(Geo.Box(1, 0, 10, 20, 30, 8, 10));
        pb.Cut(Geo.VCyl(1, 5, 25, 0, 20, 2));
        Console.WriteLine("bodies " + pb.Solve().Count);
    }

    public static void All()
    {
        StlPrefs();
        Socle(); Haut(); SupportEcrou(); Aile(1, "AILE_D"); Aile(-1, "AILE_G"); Moyeu(1, "MOYEU_PORTE_D"); Moyeu(-1, "MOYEU_PORTE_G");
        Pignon(); Tole(); Mousse(); Refs();
        File.WriteAllLines(Path.Combine(P.Cad, "STL", "printed_parts.txt"), Printed);
    }

    // M3 nut trap (nut axis along 'axis': 0 x, 1 y, 2 z) centred at (x, y, z), open along 'open' by 'ext' mm
    static Body2 Nut(double s, int axis, double x, double y, double z, int open, double ext)
    {
        double[] lo = { x, y, z }, hi = { x, y, z };
        double[] half = new double[3];
        half[axis] = G.NUT_T / 2;
        int a1 = (axis + 1) % 3, a2 = (axis + 2) % 3;
        half[a1] = G.NUT_W / 2; half[a2] = G.NUT_L / 2;
        if (open == a1) { half[a1] = G.NUT_L / 2; half[a2] = G.NUT_W / 2; }
        for (int i = 0; i < 3; i++) { lo[i] -= half[i]; hi[i] += half[i]; }
        if (ext > 0) hi[open] += ext; else if (ext < 0) lo[open] += ext;
        return Geo.Box(s, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]);
    }

    // ---------------------------------------------------------------- printed: fixed frame
    // base: screwed to the bench board; 2 rail sockets (M5 + T-nut into each rail's rear slot); motor shelf between them
    static void Socle()
    {
        var pb = new PB(1);
        double ry0 = G.RAIL_YC - G.RAIL_W / 2, ry1 = G.RAIL_YC + G.RAIL_W / 2;
        pb.Add(Geo.Box(1, -62, 62, 34, 86, 0, G.RAIL_Z0));
        foreach (var s in new[] { 1.0, -1.0 })
        {
            pb.Add(Geo.Box(s, G.RAIL_DX - 14, G.RAIL_DX + 14, ry0 - 4, ry1 + 4, G.RAIL_Z0, G.MOT_Z1 + G.SHELF_T));   // socket
            pb.Cut(Geo.Box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, ry0 - 0.2, ry1 + 0.2, G.RAIL_Z0, 100));          // rail pocket
            pb.Cut(Geo.YCyl(s, G.RAIL_DX, ry0 - 5, ry0 + 1, 30, 2.75));                                             // M5x10 + T-nut
            foreach (var y in new[] { 40.0, 80 }) pb.Cut(Geo.VCyl(s, 55, y, -1, G.RAIL_Z0 + 1, 2.2));               // wood screws
        }
        pb.Add(Geo.Box(1, -26.5, 26.5, 36, 81, G.MOT_Z1, G.MOT_Z1 + G.SHELF_T));                                  // motor shelf
        pb.Cut(Geo.VCyl(1, 0, G.RAIL_YC, G.MOT_Z1 - 1, G.MOT_Z1 + G.SHELF_T + 1, 11.5));                           // Ø22 pilot
        foreach (var dx in new[] { -15.5, 15.5 }) foreach (var dy in new[] { -15.5, 15.5 })
                pb.Cut(Geo.VCyl(1, dx, G.RAIL_YC + dy, G.MOT_Z1 - 1, G.MOT_Z1 + G.SHELF_T + 1, 1.7));              // M3x10 into the motor
        Finish(pb, "SOCLE", 1270, PETG, true);
    }

    // top tie: caps both rail tops (M5 + T-nut), 608ZZ for the top end of the screw
    static void Haut()
    {
        var pb = new PB(1);
        double ry0 = G.RAIL_YC - G.RAIL_W / 2, ry1 = G.RAIL_YC + G.RAIL_W / 2, top = G.RAIL_Z0 + G.RAIL_L;
        pb.Add(Geo.Box(1, -G.RAIL_DX - 14, G.RAIL_DX + 14, ry0 - 4, ry1 + 4, G.TOP_Z0, G.TOP_Z1));
        foreach (var s in new[] { 1.0, -1.0 })
        {
            pb.Cut(Geo.Box(s, G.RAIL_DX - 10.2, G.RAIL_DX + 10.2, ry0 - 0.2, ry1 + 0.2, G.TOP_Z0 - 1, top));
            pb.Cut(Geo.YCyl(s, G.RAIL_DX, ry0 - 5, ry0 + 1, G.TOP_Z0 + 6, 2.75));
        }
        pb.Cut(Geo.VCyl(1, 0, G.RAIL_YC, G.TOP_Z0 - 1, top + G.BRG_T, G.BRG_R));                                  // 608 from below
        Finish(pb, "TRAVERSE_HAUT", 1270, PETG, true);
    }

    // ---------------------------------------------------------------- printed: on the moving plate
    // nut shelf: bolted to the plate's rear face, between the rails; floating T8 nut (4x M3, Ø4 holes)
    static void SupportEcrou()
    {
        var pb = new PB(1);
        pb.Add(Geo.Box(1, -25, 25, G.PL_Y0 - 5, G.PL_Y0, 130, 178));                                               // web on the plate
        pb.Add(Geo.Box(1, -25, 25, 38, G.PL_Y0 - 5, G.NUT_Z, G.NUT_Z + 6));                                        // shelf
        foreach (var s in new[] { 1.0, -1.0 }) pb.Add(Geo.Box(s, 19, 25, 40, G.PL_Y0 - 5, G.NUT_Z + 6, 178));      // ribs
        pb.Cut(Geo.VCyl(1, 0, G.RAIL_YC, G.NUT_Z - 1, G.NUT_Z + 7, 5.6));
        foreach (var q in new[] { new[] { 8.0, 0 }, new[] { -8.0, 0 }, new[] { 0.0, 8 }, new[] { 0.0, -8 } })
            pb.Cut(Geo.VCyl(1, q[0], G.RAIL_YC + q[1], G.NUT_Z - 1, G.NUT_Z + 7, 2.0));
        foreach (var b in G.NUT_BOLTS)
        {
            pb.Cut(Geo.YCyl(1, b[0], G.PL_Y0 - 6, G.PL_Y0 + 1, b[1], 1.7));                                         // M3 through the plate
            pb.Cut(Nut(1, 1, b[0], G.PL_Y0 - 5 + G.NUT_T / 2 - 0.1, b[1], 1, -3));                                  // nut from the back
        }
        Finish(pb, "SUPPORT_ECROU", 1270, PETG, true);
    }

    // door unit frame: 2 plates holding the FIXED Ø8 hinge shaft, back wall bolted to the plate, 2 posts for the MG996R
    static void Aile(double s, string name)
    {
        var pb = new PB(s);
        foreach (var z in new[] { G.LOW, G.UP })
        {
            pb.Add(Geo.Box(s, G.W_X0, G.W_X1, G.W_Y0, G.W_Y1, z, z + G.PT));
            pb.Add(Geo.VCyl(s, G.PX, G.PY, z, z + G.PT, 12));                                                     // shaft boss
        }
        pb.Add(Geo.Box(s, G.W_X1, 166, G.W_Y0, 95, G.UP, G.UP + G.PT));                                          // servo extension
        pb.Add(Geo.Box(s, G.W_X0, 105, G.W_Y0, G.W_Y0 + 6, G.LOW, G.UP + G.PT));                                 // back wall (on the plate)
        pb.Add(Geo.Box(s, G.W_X0, G.W_X0 + 6, G.W_Y0, G.W_Y1, G.LOW, G.UP + G.PT));                              // inner side wall
        // fixed shaft: Ø8 press fit in both plates + M3 lock screw (captive nut) in the lower plate
        pb.Cut(Geo.VCyl(s, G.PX, G.PY, G.LOW - 1, G.UP + G.PT + 1, 4.0));
        pb.Cut(Geo.XCyl(s, G.PX, G.PX + 13, G.PY, G.LOW + G.PT / 2, 1.7));
        pb.Cut(Nut(s, 0, G.PX + 7.5, G.PY, G.LOW + G.PT / 2, 1, -10));
        // MG996R posts (flange screws 49 mm apart, 10 mm across): M3 from below through the flange, nut slid in from the side
        foreach (var side in new[] { -1, 1 })
        {
            double hx = G.SV_XC + side * 24.375, px0 = hx - 3.8, px1 = hx + 3.8;   // clears the body end by 0.2
            pb.Add(Geo.Box(s, px0, px1, G.SVY - 9, G.SVY + 9, G.SV_FLZ, G.UP));
            foreach (var dy in new[] { -5.0, 5 })
            {
                pb.Cut(Geo.VCyl(s, hx, G.SVY + dy, G.SV_FLZ - 1, G.SV_FLZ + 13, 1.7));
                pb.Cut(Nut(s, 2, hx, G.SVY + dy, G.SV_FLZ + 8, 0, side * 10));
            }
        }
        foreach (var b in G.WING_BOLTS)
        {
            pb.Cut(Geo.YCyl(s, b[0], G.W_Y0 - 1, G.W_Y0 + 7, b[1], 1.7));                                         // M3 through the plate
            pb.Cut(Nut(s, 1, b[0], G.W_Y0 + 6 - G.NUT_T / 2 + 0.1, b[1], 1, 3));                                  // nut from the front
        }
        Finish(pb, name, 1270, PETG2, true);
    }

    // door hub: turns on the fixed shaft (2x 608ZZ), 32T ring gear printed on it, 2 arms to the door sheet tabs
    static void Moyeu(double s, string name)
    {
        var pb = new PB(s);
        pb.Add(Geo.VCyl(s, G.PX, G.PY, G.HUB_Z0, G.HUB_Z1, G.HUB_R));
        pb.Prism(Geo.Gear(G.PX, G.PY, G.GM, G.GZ2, -90 + 180.0 / G.GZ2, 0.15), G.GZA, G.GZB);
        var hub = Geo.Circle(G.PX, G.PY, G.HUB_R, 48);
        var fl = new List<double[]> { new[] { G.PX + 38, G.PY + 14 }, new[] { G.SX0, G.PY + 14 }, new[] { G.SX0, G.PY + 26 }, new[] { G.PX + 38, G.PY + 26 } };
        var arm = Geo.Hull(hub.Concat(fl).ToList());
        pb.Prism(arm, G.ARM1_Z0, G.ARM1_Z1).Prism(arm, G.ARM2_Z0, G.ARM2_Z1);
        foreach (var f in new[] { new[] { G.FL1_Z0, G.FL1_Z1 }, new[] { G.FL2_Z0, G.FL2_Z1 } })
        {
            pb.Add(Geo.Box(s, G.PX + 38, G.SX0, G.PY + 14, G.PY + 26, f[0], f[1]));                               // flange behind the tab
            foreach (var z in new[] { f[0] + 3.5, f[1] - 3.5 })
            {
                pb.Cut(Geo.XCyl(s, G.PX + 37, G.SX0 + 0.1, G.PY + 20, z, 1.7));
                pb.Cut(Nut(s, 0, G.PX + 38 + G.NUT_T / 2 - 0.1, G.PY + 20, z, 0, 0));
            }
        }
        pb.Cut(Geo.VCyl(s, G.PX, G.PY, G.HUB_Z0 - 1, G.HUB_Z0 + G.BRG_T, G.BRG_R));                               // 608 bottom
        pb.Cut(Geo.VCyl(s, G.PX, G.PY, G.HUB_Z1 - G.BRG_T, G.HUB_Z1 + 1, G.BRG_R));                               // 608 top
        pb.Cut(Geo.VCyl(s, G.PX, G.PY, G.HUB_Z0 - 1, G.HUB_Z1 + 1, 5.0));                                          // shaft clearance
        Finish(pb, name, 1270, PETG, true);
    }

    static void Pignon()     // 20T m1.25 under the MG996R round horn (4x M2 self-tapping through the horn holes)
    {
        var pb = new PB(1);
        pb.Prism(Geo.Gear(G.PX, G.SVY, G.GM, G.GZ1, 90, 0.15), G.GZA, G.GZB);
        pb.Cut(Geo.VCyl(1, G.PX, G.SVY, G.GZA - 1, G.GZB + 1, 3.2));
        for (int k = 0; k < 4; k++)
        {
            double a = Math.PI / 2 * k;
            pb.Cut(Geo.VCyl(1, G.PX + 7.5 * Math.Cos(a), G.SVY + 7.5 * Math.Sin(a), G.GZA - 1, G.GZB + 1, 1.1));
        }
        Finish(pb, "PIGNON_SERVO_20T", 1270, PETG2, true);
    }

    // ---------------------------------------------------------------- cut / bought
    static void Tole()       // door sheet: 3 mm plywood or aluminium, 80 mm deep (right; the left one is the same part moved)
    {
        var pb = new PB(1);
        pb.Add(Geo.Box(1, G.SX0, G.SX1, G.SY0, G.SY1, G.DZ0, G.DZ1));
        foreach (var f in new[] { new[] { G.FL1_Z0, G.FL1_Z1 }, new[] { G.FL2_Z0, G.FL2_Z1 } })
        {
            pb.Add(Geo.Box(1, G.SX0, G.SX1, G.TAB_Y0, G.SY0, f[0], f[1]));
            foreach (var z in new[] { f[0] + 3.5, f[1] - 3.5 }) pb.Cut(Geo.XCyl(1, G.SX0 - 1, G.SX1 + 1, G.PY + 20, z, 1.7));
        }
        Finish(pb, "TOLE_PORTE", 700, WOOD, false);
    }

    static void Mousse() { Finish(new PB(1).Add(Geo.Box(1, 160, G.SX0, G.PAD_Y0, G.PAD_Y1, 25, 85)), "MOUSSE_60x48x10", 50, FOAM, false); }

    static void Refs()       // reference parts, simplified (not made)
    {
        double ry0 = G.RAIL_YC - G.RAIL_W / 2, ry1 = G.RAIL_YC + G.RAIL_W / 2;
        Finish(new PB(1).Add(Geo.Box(1, G.RAIL_DX - 10, G.RAIL_DX + 10, ry0, ry1, G.RAIL_Z0, G.RAIL_Z0 + G.RAIL_L)), "REF_RAIL_2020", 2700, DARK, false);
        Finish(new PB(1).Add(Geo.Box(1, -G.PL_HW, G.PL_HW, G.PL_Y0, G.PL_Y0 + G.PL_T, G.PL_Z0, G.PL_Z1)), "REF_PLAQUE_PAPILLON", 7850, DARK, false);
        Finish(new PB(1).Add(Geo.YCyl(1, G.WH_X, G.RAIL_YC - G.WH_W / 2, G.RAIL_YC + G.WH_W / 2, G.WH_Z0, G.WH_R)), "REF_ROUE_V", 1400, DARK, false);
        Finish(new PB(1).Add(Geo.VCyl(1, G.PX, G.PY, G.LOW, G.UP + G.PT, 4)), "REF_AXE_D8x110", 7850, STEEL, false);
        Finish(new PB(1).Add(Geo.VCyl(1, G.PX, G.PY, G.HUB_Z0, G.HUB_Z0 + 7, 11)).Cut(Geo.VCyl(1, G.PX, G.PY, 0, 400, 4)), "REF_608ZZ", 7850, STEEL, false);
        Finish(new PB(1).Add(Geo.Box(1, -21.15, 21.15, G.RAIL_YC - 21.15, G.RAIL_YC + 21.15, G.MOT_Z1 - 40, G.MOT_Z1))
                        .Add(Geo.VCyl(1, 0, G.RAIL_YC, G.MOT_Z1, G.MOT_Z1 + 2, 11)).Add(Geo.VCyl(1, 0, G.RAIL_YC, G.MOT_Z1 + 2, G.MOT_Z1 + 24, 2.5)),
            "REF_NEMA17", 3500, DARK, false);
        Finish(new PB(1).Add(Geo.VCyl(1, 0, G.RAIL_YC, G.CPL_Z0, G.CPL_Z1, 9.5)).Cut(Geo.VCyl(1, 0, G.RAIL_YC, G.SCREW_Z0, G.CPL_Z1 + 1, 4))
                        .Cut(Geo.VCyl(1, 0, G.RAIL_YC, G.CPL_Z0 - 1, G.MOT_Z1 + 24, 2.5)), "REF_COUPLEUR_5x8", 2700, ALU, false);
        Finish(new PB(1).Add(Geo.VCyl(1, 0, G.RAIL_YC, G.SCREW_Z0, G.SCREW_Z1, 4)), "REF_VIS_T8", 7850, STEEL, false);
        Finish(new PB(1).Add(Geo.VCyl(1, 0, G.RAIL_YC, G.NUT_Z + 6, G.NUT_Z + 9.5, 11)).Add(Geo.VCyl(1, 0, G.RAIL_YC, G.NUT_Z - 5.5, G.NUT_Z + 6, 5.1))
                        .Cut(Geo.VCyl(1, 0, G.RAIL_YC, 0, 400, 4)), "REF_ECROU_T8", 8500, BRASS, false);
        foreach (var s in new[] { 1.0, -1.0 })   // MG996R upside down: body against the upper plate, horn + pinion below
        {
            var pb = new PB(s).Add(Geo.Box(s, G.SV_X0, G.SV_X1, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_TOP - G.SV_H, G.SV_TOP))
                .Add(Geo.Box(s, G.SV_XC - 27.25, G.SV_XC + 27.25, G.SVY - G.SV_W / 2, G.SVY + G.SV_W / 2, G.SV_FLZ - 2.4, G.SV_FLZ))
                .Add(Geo.VCyl(s, G.PX, G.SVY, G.GZB + 2, G.SV_TOP - G.SV_H, 3)).Add(Geo.VCyl(s, G.PX, G.SVY, G.GZB, G.GZB + 2, 10.5));
            Finish(pb, s > 0 ? "REF_MG996R_D" : "REF_MG996R_G", 1200, SERVO, false);
        }
        var pile = new PB(1);
        for (int i = 0; i < 3; i++) pile.Add(Geo.Box(1, -160, 160, G.BOX_Y0, G.BOX_Y0 + 110, 110 * i + 0.5, 110 * (i + 1) - 0.5));
        Finish(pile, "REF_PILE_3_PIERRES", 100, BOX, false);
        Finish(new PB(1).Add(Geo.Box(1, -G.HEAD_X, G.HEAD_X, G.HEAD_Y0, G.YF, G.HEAD_Z0, G.HEAD_Z1)), "RESERVE_TETE_VENTOUSES", 10, GHOST, false, 0.75);
    }
}

// =============================================================================================== assembly
static class Build
{
    static double[] T(double dx, double dy, double dz)
    {
        return new double[] { 1, 0, 0, 0, 1, 0, 0, 0, 1, dx * Geo.MM, dz * Geo.MM, -dy * Geo.MM, 1, 0, 0, 0 };
    }

    public static void Assembly()
    {
        var asmDoc = P.NewDoc(true);
        var asm = (AssemblyDoc)asmDoc;
        string asmTitle = asmDoc.GetTitle();
        var mu = (MathUtility)P.App.GetMathUtility();
        var opened = new HashSet<string>();
        Action<string, double, double, double> add = (name, dx, dy, dz) =>
        {
            string full = P.F(name + ".SLDPRT");
            var d = P.Open(full); opened.Add(d.GetTitle());
            int er = 0; P.App.ActivateDoc3(asmTitle, false, 0, ref er);
            var c = asm.AddComponent5(full, 0, "", false, "", 0, 0, 0);
            if (c == null) throw new Exception("AddComponent5 failed " + name);
            c.Transform2 = (MathTransform)mu.CreateTransform(T(dx, dy, dz));
        };
        double L = -2 * G.PX;
        // fixed frame
        add("SOCLE", 0, 0, 0); add("TRAVERSE_HAUT", 0, 0, 0); add("REF_NEMA17", 0, 0, 0); add("REF_COUPLEUR_5x8", 0, 0, 0); add("REF_VIS_T8", 0, 0, 0);
        add("REF_608ZZ", -G.PX, -G.PY + G.RAIL_YC, G.RAIL_Z0 + G.RAIL_L - G.HUB_Z0);                     // screw top bearing
        add("REF_RAIL_2020", 0, 0, 0); add("REF_RAIL_2020", -2 * G.RAIL_DX, 0, 0);
        // moving carriage (shown DOWN)
        add("REF_PLAQUE_PAPILLON", 0, 0, 0); add("SUPPORT_ECROU", 0, 0, 0); add("REF_ECROU_T8", 0, 0, 0);
        foreach (var dx in new[] { 0.0, -2 * G.WH_X }) foreach (var dz in new[] { 0.0, G.WH_Z1 - G.WH_Z0 }) add("REF_ROUE_V", dx, 0, dz);
        add("AILE_D", 0, 0, 0); add("AILE_G", 0, 0, 0); add("MOYEU_PORTE_D", 0, 0, 0); add("MOYEU_PORTE_G", 0, 0, 0);
        add("REF_MG996R_D", 0, 0, 0); add("REF_MG996R_G", 0, 0, 0);
        foreach (var dx in new[] { 0.0, L })
        {
            add("REF_AXE_D8x110", dx, 0, 0); add("PIGNON_SERVO_20T", dx, 0, 0);
            add("REF_608ZZ", dx, 0, 0); add("REF_608ZZ", dx, 0, G.HUB_Z1 - 7 - G.HUB_Z0);
        }
        foreach (var dx in new[] { 0.0, -(G.SX0 + G.SX1) }) add("TOLE_PORTE", dx, 0, 0);
        foreach (var dx in new[] { 0.0, -(160 + G.SX0) }) foreach (var dz in new[] { 0.0, 110, 220 }) add("MOUSSE_60x48x10", dx, 0, dz);
        add("REF_PILE_3_PIERRES", 0, 0, 0);
        add("RESERVE_TETE_VENTOUSES", 0, 0, 0);

        asmDoc.ForceRebuild3(false);
        foreach (var t in opened) P.App.CloseDoc(t);
        string path = P.F("MODULE_CLAPETS_POC.SLDASM");
        P.SaveAs(asmDoc, path, false);

        var idm = (InterferenceDetectionMgr)asm.InterferenceDetectionManager;
        idm.TreatCoincidenceAsInterference = false; idm.TreatSubAssembliesAsComponents = true;
        idm.IncludeMultibodyPartInterferences = true; idm.UseTransform = true;
        var ints = (object[])idm.GetInterferences();
        int n = 0;
        if (ints != null) foreach (IInterference it in ints)
            {
                var names = ((object[])it.Components).Select(c => ((Component2)c).Name2).ToList();
                n++;
                Console.WriteLine(string.Format(P.CI, "  {0,9:F2} mm3  {1}", it.Volume * 1e9, string.Join(" / ", names)));
            }
        Console.WriteLine("interferences: " + n + "   (includes the suction-head reserved block: it must stay at 0)");
        idm.Done();

        int era = 0; P.App.ActivateDoc3(asmDoc.GetTitle(), false, 0, ref era);
        asmDoc.ShowNamedView2("*Isometric", 7); asmDoc.ViewZoomtofit2();
        foreach (var v in new[] { new[] { "*Isometric", "iso" }, new[] { "*Top", "top" }, new[] { "*Back", "front" }, new[] { "*Right", "side" }, new[] { "*Front", "rear" } })
        {
            asmDoc.ShowNamedView2(v[0], -1); asmDoc.ViewZoomtofit2(); asmDoc.GraphicsRedraw2();
            P.SaveAs(asmDoc, Path.Combine(P.Cad, "images", "poc_" + v[1] + ".png"), true);
        }
        P.SaveAs(asmDoc, Path.Combine(P.Cad, "STEP", "MODULE_CLAPETS_POC.STEP"), true);
        asmDoc.ShowNamedView2("*Isometric", 7); asmDoc.ViewZoomtofit2();
        P.SaveAs(asmDoc, path, false);
    }
}
