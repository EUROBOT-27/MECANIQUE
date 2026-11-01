# dump_fcstd.py - headless dump of FreeCAD files: objects, types, bounding boxes, key dimensions, spreadsheets.
# Usage: freecadcmd dump_fcstd.py  (files listed in FILES; output next to this script)
import os

import FreeCAD as App

ROOT = r"C:/Projects/EUROBOT/Eurobot 2027-ALL/resources/CDR-2027/MCAD"
FILES = ["actuator-parts/suction-cup-prototype.FCStd", "actuator-parts/box-manipulator.FCStd", "mechanical-parts/molding_parts.FCStd"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dump_cdr.txt")
KEYS = ("Length", "Length2", "Width", "Height", "Radius", "Radius1", "Radius2", "Angle", "Depth", "Diameter", "Offset",
        "Type", "Reversed", "Midplane", "Occurrences")


def fmt(v):
    try:
        return "%.2f" % float(v)
    except Exception:
        return str(v)


with open(OUT, "w", encoding="utf-8") as f:
    for rel in FILES:
        path = os.path.join(ROOT, rel)
        doc = App.openDocument(path)
        f.write("=" * 100 + "\n%s  (%d objects)\n" % (rel, len(doc.Objects)))
        for o in doc.Objects:
            line = "%-28s %-26s %-40s" % (o.Name[:28], o.TypeId[:26], o.Label[:40])
            sh = getattr(o, "Shape", None)
            if sh is not None and not sh.isNull() and sh.Volume > 0.01:
                bb = sh.BoundBox
                line += " vol %9.0f  box %.1f x %.1f x %.1f @ (%.1f,%.1f,%.1f)" % (sh.Volume, bb.XLength, bb.YLength, bb.ZLength, bb.XMin, bb.YMin, bb.ZMin)
            props = []
            for k in KEYS:
                if k in o.PropertiesList:
                    try:
                        props.append("%s=%s" % (k, fmt(o.getPropertyByName(k))))
                    except Exception:
                        pass
            if props:
                line += "  [" + ", ".join(props) + "]"
            f.write(line + "\n")
            if o.TypeId == "Sketcher::SketchObject":
                dims = []
                for c in o.Constraints:
                    if c.Type in ("Distance", "DistanceX", "DistanceY", "Radius", "Diameter", "Angle"):
                        v = c.Value
                        dims.append("%s%s=%.2f" % (c.Type, ("(" + c.Name + ")") if c.Name else "", v * 57.29578 if c.Type == "Angle" else v))
                if dims:
                    f.write("      sketch dims: " + ", ".join(dims) + "\n")
            if o.TypeId == "Spreadsheet::Sheet":
                for cell in sorted(o.getUsedCells()):
                    try:
                        f.write("      %s = %s\n" % (cell, o.getContents(cell)))
                    except Exception:
                        pass
        App.closeDocument(doc.Name)
print("written", OUT)
