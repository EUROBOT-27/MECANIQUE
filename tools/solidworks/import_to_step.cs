// import_to_step.cs - opens a foreign CAD part in the running SOLIDWORKS with LoadFile4 (import: Inventor .ipt, Creo,
// Parasolid ...) and saves it as STEP AP214 next to the output path given. For files OpenDoc6 refuses
// ("swFileRequiresRepairError" on an .ipt). Closes only the document it opened.
// Build: csc -platform:x64 -r:SolidWorks.Interop.sldworks.dll -r:SolidWorks.Interop.swconst.dll import_to_step.cs
// Run:   import_to_step.exe <in_file> <out.step>      (SOLIDWORKS must be running)
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

static class I
{
    static int Main(string[] a)
    {
        if (a.Length < 2) { Console.WriteLine("usage: import_to_step <in_file> <out.step>"); return 1; }
        string src = Path.GetFullPath(a[0]), dst = Path.GetFullPath(a[1]);
        var app = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");
        app.SetUserPreferenceIntegerValue((int)swUserPreferenceIntegerValue_e.swStepAP, 214);
        object imp = app.GetImportFileData(src);
        int err = 0;
        var doc = (ModelDoc2)app.LoadFile4(src, "r", imp, ref err);
        if (doc == null) { Console.WriteLine("LoadFile4 failed, error " + err + " (" + (swFileLoadError_e)err + ")"); return 2; }
        Console.WriteLine("imported " + doc.GetTitle() + " (error code " + err + ")");
        var part = doc as PartDoc;
        if (part != null)
        {
            var bodies = (object[])part.GetBodies2((int)swBodyType_e.swSolidBody, true);
            var box = (double[])part.GetPartBox(true);
            Console.WriteLine("solid bodies " + (bodies == null ? 0 : bodies.Length) + ", box mm: "
                + string.Join(" ", Array.ConvertAll(box, v => (v * 1000).ToString("0.###"))));
        }
        int e2 = 0, w2 = 0;
        bool ok = doc.Extension.SaveAs3(dst, (int)swSaveAsVersion_e.swSaveAsCurrentVersion,
            (int)swSaveAsOptions_e.swSaveAsOptions_Silent | (int)swSaveAsOptions_e.swSaveAsOptions_Copy, null, null, ref e2, ref w2);
        Console.WriteLine(ok ? "saved " + dst : "save FAILED " + e2);
        app.CloseDoc(doc.GetTitle());
        return ok ? 0 : 3;
    }
}
