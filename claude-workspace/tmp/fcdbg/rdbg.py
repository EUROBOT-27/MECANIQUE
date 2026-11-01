import os, FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore
LOG = r"C:/Projects/EUROBOT/Eurobot 2027-ALL/claude-workspace/tmp/fcdbg/rdbg.log"
def run():
    with open(LOG, "w") as f:
        try:
            doc = App.openDocument(r"C:/Projects/EUROBOT/Mecanique/module_clapets_poc/CAD_FC/MODULE_CLAPETS_POC.FCStd")
            gd = Gui.getDocument(doc.Name)
            f.write("objects %d\n" % len(doc.Objects))
            o = doc.Objects[0]
            f.write("vo %s vis %s\n" % (o.ViewObject, o.ViewObject.Visibility if o.ViewObject else None))
            v = gd.ActiveView
            f.write("view %s\n" % type(v))
            v.viewIsometric(); v.fitAll(); Gui.updateGui()
            v.saveImage(r"C:/Projects/EUROBOT/Eurobot 2027-ALL/claude-workspace/tmp/fcdbg/t1.png", 800, 500, "Current")
            f.write("saved\n")
        except Exception as e:
            import traceback; f.write(traceback.format_exc())
    Gui.getMainWindow().close()
QtCore.QTimer.singleShot(5000, run)
