// inspect3dm.cs - opens a Rhino .3dm in SOLIDWORKS and lists what came in (components / bodies, names, boxes).
// Usage: inspect3dm.exe <file.3dm> [filter]
using System;
using System.Linq;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

static class I
{
    static int Main(string[] a)
    {
        SldWorks app;
        try { app = (SldWorks)Marshal.GetActiveObject("SldWorks.Application"); }
        catch { app = (SldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")); }
        app.Visible = true;
        string filter = a.Length > 1 ? a[1].ToLower() : null;
        int err = 0;
        var m = (ModelDoc2)app.LoadFile4(a[0], "r", null, ref err);
        if (m == null) { Console.WriteLine("LoadFile4 failed, err=" + err); return 1; }
        Console.WriteLine("type " + m.GetType() + "  title " + m.GetTitle());
        if (m.GetType() == (int)swDocumentTypes_e.swDocASSEMBLY)
        {
            var comps = (object[])((AssemblyDoc)m).GetComponents(false);
            Console.WriteLine("components: " + (comps == null ? 0 : comps.Length));
            foreach (Component2 c in comps ?? new object[0])
            {
                if (filter != null && !c.Name2.ToLower().Contains(filter)) continue;
                var bx = (double[])c.GetBox(false, false);
                Console.WriteLine(string.Format("{0}  box {1}", c.Name2, bx == null ? "-" : string.Join(" ", bx.Select(v => (v * 1000).ToString("F1")))));
            }
        }
        else
        {
            var bodies = (object[])((PartDoc)m).GetBodies2((int)swBodyType_e.swAllBodies, false);
            Console.WriteLine("bodies: " + (bodies == null ? 0 : bodies.Length));
            foreach (Body2 b in bodies ?? new object[0])
            {
                if (filter != null && !b.Name.ToLower().Contains(filter)) continue;
                var bx = (double[])b.GetBodyBox();
                Console.WriteLine(string.Format("{0}  type {1}  box {2}", b.Name, b.GetType(), string.Join(" ", bx.Select(v => (v * 1000).ToString("F1")))));
            }
        }
        return 0;
    }
}
