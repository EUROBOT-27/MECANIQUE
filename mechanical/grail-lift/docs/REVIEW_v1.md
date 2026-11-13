# Review of v1: "essai mecanisme 1" (Baha, SolidWorks, 2026-11-10)

Reviewed by Maatoug + Claude on 2026-11-10, against `CDC.md`, `parts-library.md` and `design-principles.md`.
Model: `sw/essai mecanisme 1.SLDASM`, rebuilt in FreeCAD as `CAD_FC/GRAIL_LIFT_V1.FCStd` (`fc/v1_fc.py`); numbers
below are from `CAD_FC/v1_report.txt`.

![v1 as saved in SolidWorks](v1_solidworks_preview.png)

## What it is
- A **vertical rack and pinion lift**: 280 mm profile, ISO rack 1M × 280, 20T M1 pinion on a coupling, **NEMA14**
  in a grey box ("support fixation").
- On that carriage, a blue box ("support en u extension lel bras") with an **MG996R** and a **5 kg electromagnet**
  facing sideways. The servo axis is horizontal, so it can tilt the magnet up/down.

## Missing from the files
3 custom parts were only on Baha's PC (`C:\Users\bahar\Downloads\...`): the profile, the grey box and the blue box.
They are **rebuilt approximately** from the assembly's preview image and the mates (marked `APPROX_` in the FreeCAD
file). The NEMA14 is a block model. The **Mini V Gantry Set was suppressed** in the assembly. To check against the
real files: ask Baha for the 3 SLDPRT and drop them into `sw/`, next to the assembly.

## Findings

| # | Finding | Severity |
|---|---|---|
| 1 | **It cannot reach L4.** The lift travel on the rack is 239 mm, and the moving block is 70 mm tall. CDC D1: a straight lift needs a moving block ≤ ~49 mm and ≥ 300 mm of travel. Even mounted perfectly, the Grail bottom tops out at ~239 mm. | blocking |
| 2 | **No guide for the carriage.** The V-gantry is suppressed and the boxes don't touch the profile. As built, the carriage would hang on the pinion and rack teeth and tilt or jam. | blocking |
| 3 | **Pinion on a 38 mm overhang** (25 mm coupling between motor face and gear). It bends and loses the mesh under load. Put the pinion **directly on the motor shaft**, ≤ 15 mm from the face. | major |
| 4 | **NEMA14 is not in the library** (we have 4 × NEMA17 from the printer). It probably needs importing. | major (sourcing) |
| 5 | **The arm hangs on the servo spline only.** Blue box + magnet are carried by the horn, with no second bearing. In the model the horn is also **3 mm off the servo shaft**, and nothing ties the servo body to the carriage (no torque path). → Use the club's steel U servo bracket (horn on one side, pivot pin on the other). | major |
| 6 | **Interference between real parts:** the NEMA14's connector runs into the servo (~139 mm³). The moving block is too crowded. Other overlaps in `v1_report.txt` involve the approximate boxes and need the real files. | minor |
| 7 | **The rack and pinion can be back-driven.** With the drivers off (100 s, e-stop) the carriage drops. Park it low before 100 s, or add a stop. | minor |
| 8 | The single 280 mm profile is only tied at its base in the model. Bolt it along its back (≥ 3 T-nuts) to a robot frame member. | minor |
| 9 | Good choices to keep: **electromagnet** (holds ≫ the Grail, clean release when off), **20T M1 rack and pinion** (fast, no end bearings, so the carriage can reach the table), **MG996R**. | — |

## Parts library check (v1)

| Part | In v1 | Status |
|---|---|---|
| 20-series profile 280 | yes | 📦 (Ender, cut) |
| NEMA14 | yes | ✈️ probably (not in the library) → NEMA17 📦 |
| Rack 1M + 20T pinion | yes | print (PLA/ABS) or 🇹🇳 |
| Coupling "liaison" Ø7 × 25 | yes | print/turn; not needed if the pinion sits on the shaft |
| MG996R + 4-pad horn | yes | 📦 |
| Electromagnet 5 kg (Ø27 × 20) | yes | 🇹🇳 (common module), to confirm |
| Mini V gantry plate + wheels | suppressed | 📦 equivalent: Ender carriage plates / V-wheels |
| M6 nut, M5 rod "tige articulation" 100, corner bracket 70×70×40 | files only, not used in the assembly | 📦 |

## What we changed → v2
See `../README.md`. v2 keeps the idea (rack and pinion + servo tilting a magnet) and makes it work. The tilt
becomes a **coordinated flip over the roof edge** (it solves D1 + D3). The arm sits in the **U bracket**, the
carriage gets **4 V-wheels**, and the drive is a **NEMA17 with the pinion on its shaft**.
