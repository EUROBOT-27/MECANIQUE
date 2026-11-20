// dump_asm.cs - opens a SOLIDWORKS assembly (starts SOLIDWORKS if needed), writes a JSON dump of every
// component (path, missing/suppressed, fixed, transform, box), every mate (type, values, entities with their
// geometry in assembly coordinates) and every part (mass, material, bodies, box, named dimensions), and exports
// the assembly and each part to STEP AP214.  All lengths in mm, angles in degrees.
//
// Build: csc /nologo /r:"<SW>\api\redist\SolidWorks.Interop.sldworks.dll" /r:"<SW>\api\redist\SolidWorks.Interop.swconst.dll" dump_asm.cs
// Run:   dump_asm.exe <assembly.SLDASM> <out_dir>      -> <out_dir>/sw_dump.json + <out_dir>/*.step
//        dump_asm.exe <part.SLDPRT|.ipt|...> <out_dir> -> <out_dir>/<part>_dump.json + <out_dir>/<part>.step (part mode)
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

static class D
{
    static readonly CultureInfo IC = CultureInfo.InvariantCulture;
    static string N(double v) { return Math.Round(v, 6).ToString("R", IC); }
    static string S(string s) { return "\"" + (s ?? "").Replace("\\", "/").Replace("\"", "'") + "\""; }
    static string Arr(IEnumerable<double> a) { return "[" + string.Join(", ", a.Select(N)) + "]"; }
    static double[] Mm(double[] a) { return a == null ? null : a.Select(v => v * 1000.0).ToArray(); }

    static int Main(string[] a)
    {
        if (a.Length < 2) { Console.WriteLine("usage: dump_asm <asm.SLDASM> <out_dir>"); return 1; }
        string asmPath = Path.GetFullPath(a[0]), outDir = Path.GetFullPath(a[1]);
        Directory.CreateDirectory(outDir);

        SldWorks app;
        bool started = false;
        try { app = (SldWorks)Marshal.GetActiveObject("SldWorks.Application"); }
        catch { app = (SldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")); started = true; }
        app.Visible = false;
        app.SetUserPreferenceIntegerValue((int)swUserPreferenceIntegerValue_e.swStepAP, 214);

        int er = 0, wr = 0;
        // anything that is not an assembly is opened as a part: .SLDPRT, or a foreign part SOLIDWORKS reads through
        // 3D Interconnect (Inventor .ipt, Creo .prt, STEP ...)
        bool isPart = !(asmPath.EndsWith(".SLDASM", StringComparison.OrdinalIgnoreCase)
                        || asmPath.EndsWith(".iam", StringComparison.OrdinalIgnoreCase));
        var doc = (ModelDoc2)app.OpenDoc6(asmPath, isPart ? (int)swDocumentTypes_e.swDocPART : (int)swDocumentTypes_e.swDocASSEMBLY,
            (int)swOpenDocOptions_e.swOpenDocOptions_Silent, "", ref er, ref wr);
        if (doc == null) { Console.WriteLine("open failed, error " + er + " warning " + wr); return 2; }
        Console.WriteLine("opened " + doc.GetTitle() + " (errors " + er + ", warnings " + wr + ")");
        var asm = isPart ? null : (AssemblyDoc)doc;
        if (asm != null) asm.ResolveAllLightWeightComponents(false);
        doc.ForceRebuild3(false);

        var js = new StringBuilder();
        js.Append("{\n  \"assembly\": " + S(asmPath) + ",\n  \"open_errors\": " + er + ", \"open_warnings\": " + wr + ",\n");
        js.Append("  \"config\": " + S(((Configuration)doc.GetActiveConfiguration()).Name) + ",\n");

        // ---- components
        var comps = asm == null ? new List<Component2>() : ((object[])asm.GetComponents(false) ?? new object[0]).Cast<Component2>().ToList();
        var parts = new Dictionary<string, ModelDoc2>(StringComparer.OrdinalIgnoreCase);
        if (isPart) parts[asmPath] = doc;
        js.Append("  \"components\": [\n");
        for (int i = 0; i < comps.Count; i++)
        {
            var c = comps[i];
            string p = c.GetPathName();
            bool exists = !string.IsNullOrEmpty(p) && File.Exists(p);
            var t = c.Transform2 == null ? null : (double[])((MathTransform)c.Transform2).ArrayData;
            double[] box = null;
            try { box = (double[])c.GetBox(false, false); } catch { }
            var md = c.GetModelDoc2() as ModelDoc2;
            if (md != null && md.GetType() == (int)swDocumentTypes_e.swDocPART && !parts.ContainsKey(p)) parts[p] = md;
            js.Append("    {\"name\": " + S(c.Name2) + ", \"path\": " + S(p) + ", \"file_found\": " + (exists ? "true" : "false")
                + ", \"virtual\": " + (c.IsVirtual ? "true" : "false")
                + ", \"suppressed\": " + (c.IsSuppressed() ? "true" : "false") + ", \"fixed\": " + (c.IsFixed() ? "true" : "false")
                + ", \"config\": " + S(c.ReferencedConfiguration)
                + ", \"loaded\": " + (md != null ? "true" : "false"));
            if (t != null)
                js.Append(",\n     \"rot\": " + Arr(t.Take(9)) + ", \"pos\": " + Arr(Mm(t.Skip(9).Take(3).ToArray())) + ", \"scale\": " + N(t[12]));
            if (box != null) js.Append(",\n     \"box\": " + Arr(Mm(box)));
            js.Append("}" + (i < comps.Count - 1 ? "," : "") + "\n");
        }
        js.Append("  ],\n");

        // ---- mates
        js.Append("  \"mates\": [\n");
        var mates = new List<string>();
        var f = (Feature)doc.FirstFeature();
        while (f != null)
        {
            if (f.GetTypeName2() == "MateGroup")
            {
                var sf = (Feature)f.GetFirstSubFeature();
                while (sf != null)
                {
                    mates.Add(MateJson(sf));
                    sf = (Feature)sf.GetNextSubFeature();
                }
            }
            f = (Feature)f.GetNextFeature();
        }
        js.Append(string.Join(",\n", mates) + "\n  ],\n");

        // ---- parts
        js.Append("  \"parts\": [\n");
        var pj = new List<string>();
        foreach (var kv in parts)
        {
            var md = kv.Value;
            var sb = new StringBuilder();
            sb.Append("    {\"path\": " + S(kv.Key) + ", \"title\": " + S(md.GetTitle()));
            try
            {
                string db;
                string mat = ((PartDoc)md).GetMaterialPropertyName2("", out db);
                sb.Append(", \"material\": " + S(mat));
            }
            catch { }
            try
            {
                var mp = (MassProperty)md.Extension.CreateMassProperty();
                sb.Append(", \"mass_g\": " + N(mp.Mass * 1000) + ", \"volume_cm3\": " + N(mp.Volume * 1e6)
                    + ", \"com\": " + Arr(Mm((double[])mp.CenterOfMass)));
            }
            catch { }
            var bodies = (object[])((PartDoc)md).GetBodies2((int)swBodyType_e.swSolidBody, true);
            sb.Append(", \"solid_bodies\": " + (bodies == null ? 0 : bodies.Length));
            try { sb.Append(", \"box\": " + Arr(Mm((double[])((PartDoc)md).GetPartBox(true)))); } catch { }
            // features + dimensions
            sb.Append(",\n     \"features\": [");
            var fl = new List<string>();
            var pf = (Feature)md.FirstFeature();
            while (pf != null)
            {
                string tn = pf.GetTypeName2();
                var dims = new List<string>();
                var dd = (DisplayDimension)pf.GetFirstDisplayDimension();
                while (dd != null)
                {
                    var dm = (Dimension)dd.GetDimension2(0);
                    if (dm != null)
                    {
                        double v = dm.SystemValue;
                        bool ang = dm.GetType() == (int)swDimensionParamType_e.swDimensionParamTypeDoubleAngular;
                        dims.Add(S(dm.Name) + ": " + N(ang ? v * 180 / Math.PI : v * 1000));
                    }
                    dd = (DisplayDimension)pf.GetNextDisplayDimension(dd);
                }
                bool skip = tn == "OriginProfileFeature" || tn == "RefPlane" && dims.Count == 0 || tn == "MaterialFolder"
                    || tn.EndsWith("Folder") || tn == "HistoryFolder" || tn == "SensorFolder" || tn == "DetailCabinet"
                    || tn == "EqnFolder" || tn == "CommentsFolder" || tn == "FavoriteFolder" || tn == "SelectionSetFolder"
                    || tn == "BlockFolder" || tn == "LiveSection" || tn == "SurfaceBodyFolder" || tn == "SolidBodyFolder";
                if (!skip)
                    fl.Add("\n       {\"type\": " + S(tn) + ", \"name\": " + S(pf.Name)
                        + (pf.IsSuppressed() ? ", \"suppressed\": true" : "") + ", \"dims\": {" + string.Join(", ", dims) + "}}");
                // sketch features inside (their dims are what define the profile)
                var sub = (Feature)pf.GetFirstSubFeature();
                while (sub != null)
                {
                    if (sub.GetTypeName2() == "ProfileFeature")
                    {
                        var sd = new List<string>();
                        var d2 = (DisplayDimension)sub.GetFirstDisplayDimension();
                        while (d2 != null)
                        {
                            var dm = (Dimension)d2.GetDimension2(0);
                            if (dm != null)
                            {
                                double v = dm.SystemValue;
                                bool ang = dm.GetType() == (int)swDimensionParamType_e.swDimensionParamTypeDoubleAngular;
                                sd.Add(S(dm.Name) + ": " + N(ang ? v * 180 / Math.PI : v * 1000));
                            }
                            d2 = (DisplayDimension)sub.GetNextDisplayDimension(d2);
                        }
                        fl.Add("\n       {\"type\": \"sketch\", \"name\": " + S(sub.Name) + ", \"of\": " + S(pf.Name) + ", \"dims\": {" + string.Join(", ", sd) + "}}");
                    }
                    sub = (Feature)sub.GetNextSubFeature();
                }
                pf = (Feature)pf.GetNextFeature();
            }
            sb.Append(string.Join(",", fl) + "]}");
            pj.Add(sb.ToString());

            // STEP of the part, in part coordinates
            string stepName = Path.GetFileNameWithoutExtension(kv.Key) + ".step";
            int e2 = 0, w2 = 0;
            bool ok = md.Extension.SaveAs3(Path.Combine(outDir, stepName), (int)swSaveAsVersion_e.swSaveAsCurrentVersion,
                (int)swSaveAsOptions_e.swSaveAsOptions_Silent | (int)swSaveAsOptions_e.swSaveAsOptions_Copy, null, null, ref e2, ref w2);
            Console.WriteLine("part " + md.GetTitle() + " -> " + stepName + (ok ? "" : "  FAILED " + e2));
        }
        js.Append(string.Join(",\n", pj) + "\n  ]\n}\n");

        // STEP of the whole assembly (keeps the tree)
        int e3 = 0, w3 = 0;
        if (!isPart) {
        string asmStep = Path.Combine(outDir, Path.GetFileNameWithoutExtension(asmPath) + ".step");
        bool ok3 = doc.Extension.SaveAs3(asmStep, (int)swSaveAsVersion_e.swSaveAsCurrentVersion,
            (int)swSaveAsOptions_e.swSaveAsOptions_Silent | (int)swSaveAsOptions_e.swSaveAsOptions_Copy, null, null, ref e3, ref w3);
        Console.WriteLine("assembly -> " + Path.GetFileName(asmStep) + (ok3 ? "" : "  FAILED " + e3));
        }

        File.WriteAllText(Path.Combine(outDir, isPart ? Path.GetFileNameWithoutExtension(asmPath) + "_dump.json" : "sw_dump.json"), js.ToString(), new UTF8Encoding(false));
        Console.WriteLine(comps.Count + " components, " + mates.Count + " mates, " + parts.Count + " parts -> " + (isPart ? Path.GetFileNameWithoutExtension(asmPath) + "_dump.json" : "sw_dump.json"));

        app.CloseAllDocuments(true);
        if (started) app.ExitApp();
        return 0;
    }

    static string MateJson(Feature sf)
    {
        var sb = new StringBuilder();
        sb.Append("    {\"name\": " + S(sf.Name) + ", \"feature_type\": " + S(sf.GetTypeName2())
            + (sf.IsSuppressed() ? ", \"suppressed\": true" : ""));
        var m = sf.GetSpecificFeature2() as Mate2;
        if (m != null)
        {
            sb.Append(", \"type\": " + S(((swMateType_e)m.Type).ToString().Replace("swMate", ""))
                + ", \"align\": " + S(((swMateAlign_e)m.Alignment).ToString().Replace("swMateAlign", "")) + ", \"flipped\": " + (m.Flipped ? "true" : "false"));
            try { if (m.MinimumVariation != 0 || m.MaximumVariation != 0) sb.Append(", \"min\": " + N(m.MinimumVariation) + ", \"max\": " + N(m.MaximumVariation)); } catch { }
        }
        var dims = new List<string>();
        var dd = (DisplayDimension)sf.GetFirstDisplayDimension();
        while (dd != null)
        {
            var dm = (Dimension)dd.GetDimension2(0);
            if (dm != null)
            {
                bool ang = dm.GetType() == (int)swDimensionParamType_e.swDimensionParamTypeDoubleAngular;
                dims.Add(S(dm.Name) + ": " + N(ang ? dm.SystemValue * 180 / Math.PI : dm.SystemValue * 1000));
            }
            dd = (DisplayDimension)sf.GetNextDisplayDimension(dd);
        }
        sb.Append(", \"dims\": {" + string.Join(", ", dims) + "}");
        try
        {
            var def = sf.GetDefinition();
            var sc = def as ScrewMateFeatureData;
            if (sc != null) sb.Append(", \"screw\": {\"revolution_type\": " + sc.RevolutionType + ", \"value\": " + N(sc.RevolutionVal) + ", \"reverse\": " + (sc.Reverse ? "true" : "false") + "}");  // type 0 = distance per revolution (m), 1 = revolutions per m
        }
        catch { }
        if (m != null)
        {
            sb.Append(",\n     \"entities\": [");
            var el = new List<string>();
            for (int i = 0; i < m.GetMateEntityCount(); i++)
            {
                var me = (MateEntity2)m.MateEntity(i);
                var rc = me.ReferenceComponent;
                string rt = ((swMateEntity2ReferenceType_e)me.ReferenceType2).ToString().Replace("swMateEntity2ReferenceType_", "");
                double[] p = (double[])me.EntityParams;
                // EntityParams: point (3, m) + vector (3) + radius 1 + radius 2 (m)
                string geo = "";
                if (p != null && p.Length >= 6)
                    geo = ", \"point\": " + Arr(Mm(p.Take(3).ToArray())) + ", \"vector\": " + Arr(p.Skip(3).Take(3))
                        + (p.Length >= 7 ? ", \"r1\": " + N(p[6] * 1000) : "") + (p.Length >= 8 ? ", \"r2\": " + N(p[7] * 1000) : "");
                el.Add("\n       {\"component\": " + S(rc == null ? "(assembly)" : rc.Name2) + ", \"ref\": " + S(rt) + geo + "}");
            }
            sb.Append(string.Join(",", el) + "]");
        }
        sb.Append("}");
        return sb.ToString();
    }
}
