# Linear-motion parts (lab stock)

Models of the lab's linear-motion parts (`../../parts-library.md`, photos `../a45eb9fd-….jfif`, `../71b33ca8-….jfif`),
used by the generators through `linear_parts.py` (`LP.scs8uu()`, `LP.sk8()`).

## Vendor models (used since 2026-11-20)
Maatoug downloaded them; converted to STEP with SOLIDWORKS (`tools/solidworks/`).

| File | Part | Source | Notes |
|---|---|---|---|
| `vendor/SCS8UU.step` | SCS8UU linear block | `vendor/SCS8UU.SLDPRT` (`dump_asm.exe`, part mode) | 34.06 × 22 × 30, one solid, Ø8 bore; 4 × M4 holes on **24 × 16** in the flat face (the other face is crowned); render `vendor/SCS8UU_render.jpg` |
| `vendor/SoporteVertical_SK8.step` | SK8 rod support | `vendor/SoporteVertical_SK8.ipt` (Inventor, imported with `import_to_step.exe`) | 42 × 32.8 × 14, rod axis 20 above the base, 2 × M5 on 32, body + clamp screw (2 solids); picture `vendor/SoporteVertical_SK8.png` |

`linear_parts.py` moves them into one frame: rod axis = z through (0, 0), centred on z = 0; SCS8UU flat (holes) face
at y = −11; SK8 base face at y = −20.

## Catalogue models (fallback)
`SCS8UU_catalogue.step`, `SK8_catalogue.step`: built from catalogue sizes by `linear_parts.py` before the vendor files
came (used only if a vendor file is missing). Same frame.

Still to measure on our parts: the real hole spacing / height (sellers differ by 1–2 mm). Seen in the photos but not
modelled: a flange rod support (probably **SHF8**, stands a vertical rod on a horizontal plate), 2 KP08 pillow blocks.

Run `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" linear_parts.py` to rewrite the catalogue STEPs and print both
sets of sizes.
