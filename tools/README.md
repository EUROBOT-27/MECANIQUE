# Tools

Small helper scripts used with Claude for the prompt-to-CAD workflow. They were one-off tools: the input paths
at the top of each file point to Maatoug's PC (`C:/Projects/EUROBOT/...`). Change `ROOT` / `FILES` before running.

| Tool | What it does | Run with |
|---|---|---|
| `freecad/render_any.py` | Opens FreeCAD files in the GUI and saves iso / front / top / right PNG views | FreeCAD GUI (macro) |
| `freecad/dump_fcstd.py` | Headless dump of FreeCAD files: objects, types, bounding boxes, key dimensions, spreadsheets | `freecadcmd dump_fcstd.py` |
| `solidworks/inspect3dm.cs` | Opens a Rhino `.3dm` in SOLIDWORKS and lists the components / bodies / boxes | compile with `csc`, needs the SOLIDWORKS interop DLLs |
| `solidworks/feats.cs`, `closedoc.cs` | Related SOLIDWORKS API helpers (feature list, close document) | same |

The main generator scripts for the clapets v5 design are in `mechanical/clapets-v5/fc/`.
