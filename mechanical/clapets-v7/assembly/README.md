# Clapets v7 module A: assembly guide

**[`clapets_v7_moduleA_assembly.pdf`](clapets_v7_moduleA_assembly.pdf)**: 15 A4 sheets (cover, 13 steps, left side + final
checks). Right door unit drawn; the left one is its mirror. Each step: exploded view (numbered balloons, one arrow per
part for the assembly direction), a 2D detail (section or orthographic view, 10 mm scale bar), how-to, parts and
fasteners, tools, title block. English, PLA. Made 2026-11-10 from the CAD.

## Regenerate (after any CAD change, e.g. after the tolerance tests)
From `mechanical/clapets-v7`:
```
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/v7_fc.py              # the CAD (if it changed)
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe"    fc/assembly_images_v7.py # images -> assembly/img/ (~3 min, GUI)
python assembly/make_guide.py                                               # the PDF
```
The steps (parts, explode directions, details, text, parts lists, tools) are in [`steps.py`](steps.py): edit there,
never in the PDF.
