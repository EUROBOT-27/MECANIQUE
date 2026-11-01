// feats.cs - counts feature types in the active SOLIDWORKS document and lists the non-"Imported" ones with their names
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

static class F
{
    static int Main(string[] a)
    {
        var app = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");
        int er = 0; var m = a.Length > 0 ? (ModelDoc2)app.ActivateDoc3(a[0], false, 0, ref er) : (ModelDoc2)app.ActiveDoc;
        Console.WriteLine("active: " + m.GetTitle());
        var count = new Dictionary<string, int>();
        var f = (Feature)m.FirstFeature();
        while (f != null)
        {
            string t = f.GetTypeName2();
            count[t] = (count.ContainsKey(t) ? count[t] : 0) + 1;
            if (t != "BaseBody" && t != "ImportedBody" && !f.Name.StartsWith("Imported") && !f.Name.StartsWith("Surface-Imported"))
                Console.WriteLine("  " + t + "  " + f.Name);
            f = (Feature)f.GetNextFeature();
        }
        foreach (var kv in count.OrderByDescending(k => k.Value)) Console.WriteLine(kv.Value + "  " + kv.Key);
        foreach (int bt in new[] { 0, 1, 2, 3, 4, 5, 6, 7 })
        {
            var b = (object[])((PartDoc)m).GetBodies2(bt, false);
            Console.WriteLine("bodytype " + bt + ": " + (b == null ? 0 : b.Length));
        }
        return 0;
    }
}
