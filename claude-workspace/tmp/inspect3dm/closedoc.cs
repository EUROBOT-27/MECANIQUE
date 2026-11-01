// closedoc.cs - closes one open SOLIDWORKS document by title (no save), if it is open
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;

static class C
{
    static int Main(string[] a)
    {
        SldWorks app;
        try { app = (SldWorks)Marshal.GetActiveObject("SldWorks.Application"); }
        catch { Console.WriteLine("SOLIDWORKS not running"); return 0; }
        var docs = (object[])app.GetDocuments();
        bool found = false;
        foreach (ModelDoc2 d in docs ?? new object[0])
        {
            Console.WriteLine("open: " + d.GetTitle());
            if (d.GetTitle().StartsWith(a[0])) { app.CloseDoc(d.GetTitle()); found = true; }
        }
        Console.WriteLine(found ? "closed " + a[0] : "not open: " + a[0]);
        return 0;
    }
}
