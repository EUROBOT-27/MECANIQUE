# Cup stations S1 and S3

One generator each (`../../fc/station_s1.py`, `station_s3.py`). T1 builds them itself; these folders are the
stations alone (to print one and test it on the bench):
```
cd mechanical/suction-v1
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/station_s1.py   # -> S1_rigid/
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" fc/station_s3.py   # -> S3_tpu_ring/
```
Each folder: `<name>.FCStd`, STEP of every printed part, STL of the printed / TPU parts, `report.txt`, `info.json`.

**Same interface for both:**
- carrier hole **Ø50**, **3 × M3 on r 34**, nuts behind the carrier; they swap on the same plate
- cup mounted as a **bulkhead**: the PL4-M5 swivel elbow's hex sits in a pocket behind a 2 mm wall, and the cup
  screws onto its thread from the front
- the tube leaves sideways in front of the carrier
- cup / elbow / tube sizes are datasheet values (`params.py`)

| | S1 rigid | S3 TPU + ring (as the flip-bar) |
|---|---|---|
| Parts | 1 ABS | 2 ABS + 1 TPU |
| Mass (printed) | 24.8 g | 75.7 g |
| Cup lip (free), from carrier front | 41.0 | 39.5 |
| Stone face when held | 35.0 (bellows squashed) | 36.5 |
| Stone seat | none: rocks on the bellows | ring rim Ø62, rigid |
| Compliance | bellows ~6 | bellows 6 + TPU 3, tilts |
| Screws | 3 × M3 × 16 | 3 × M3 × 35 |

S2 (TPU + pot, tube behind the carrier) and S4 (spring plunger) were dropped on 2026-11-19: S2's tube needs the
space where T1's hub is, and S4 pushes the stack out 10 mm. Their generators are in git history (commit `a902498`).
