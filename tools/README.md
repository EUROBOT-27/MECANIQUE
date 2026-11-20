# Tools

Small helper scripts used with Claude for the prompt-to-CAD workflow. They were one-off tools: the input paths
at the top of each file point to Maatoug's PC (`C:/Projects/EUROBOT/...`). Change `ROOT` / `FILES` before running.

| Tool | What it does | Run with |
|---|---|---|
| `freecad/render_any.py` | Opens FreeCAD files in the GUI and saves iso / front / top / right PNG views | FreeCAD GUI (macro) |
| `freecad/dump_fcstd.py` | Headless dump of FreeCAD files: objects, types, bounding boxes, key dimensions, spreadsheets | `freecadcmd dump_fcstd.py` |
| `solidworks/inspect3dm.cs` | Opens a Rhino `.3dm` in SOLIDWORKS and lists the components / bodies / boxes | compile with `csc`, needs the SOLIDWORKS interop DLLs |
| `solidworks/dump_asm.cs` | Opens a SOLIDWORKS assembly (or one part, `.SLDPRT` or a foreign part) and writes `sw_dump.json` (components + transforms, mates with their geometry, part masses + dimensions, missing files) and STEP of every part + the assembly. Used for `mechanical/grail2/` | `csc -platform:x64 -r:SolidWorks.Interop.sldworks.dll -r:SolidWorks.Interop.swconst.dll dump_asm.cs`, then `dump_asm.exe <file.SLDASM> <out_dir>` with SOLIDWORKS running |
| `solidworks/import_to_step.cs` | Imports a foreign part (Inventor `.ipt`, …) into the running SOLIDWORKS with `LoadFile4` and saves it as STEP AP214 (for files `OpenDoc6` refuses) | same build as `dump_asm`, then `import_to_step.exe <in_file> <out.step>` |
| `solidworks/feats.cs`, `closedoc.cs` | Related SOLIDWORKS API helpers (feature list, close document) | same |

The main generator scripts for the clapets v5 design are in `mechanical/clapets/clapets-v5/fc/`.

## Robot sync
| Tool | What it does | Run with |
|---|---|---|
| `sync_robot.py` | Rebuilds `mechanical/robot` (full robot + Gazebo export) when a mechanism changed and copies the model into the local `eurobot2027/Simulation-Euro27`; `--push` (by hand only) commits + pushes it to GitHub | `python tools/sync_robot.py [--check/--force/--push]` |
| `hooks/sync_bg.py` | Runs the sync in the background, local only (never pushes). Called by the Claude Stop hook (`.claude/settings.json`) and the git hooks | automatic |
| `install_hooks.py` + `hooks/post-*` | git post-commit / post-merge hooks (rebuild + local copy, no push), chained with Git LFS | `python tools/install_hooks.py` (once per clone, again when `hooks/post-*` change) |

The Claude Stop hook (`.claude/settings.json`) runs `hooks/sync_bg.py --claude` after each turn: a mechanism changed →
rebuild + copy into the local sim clone. **No hook pushes to GitHub** (since 2026-11-13); publish with
`python tools/sync_robot.py --push`. Full rules (what counts as a change, failures, conflicts): `mechanical/robot/README.md`.
