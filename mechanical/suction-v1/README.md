# Module B (suction): T1 turning plate

> **Status (2026-11-19): design done, Seif's final review + caliper checks before printing.** Owner: **Seif**.
> **Open (check 2026-11-19): in A+B, module A's doors can't fold fully: the right door touches module B past 46° (S3) /
> 52° (S1).** Choose: doors fold less at the start (~+35–45 mm start perimeter) or reshape module B. B alone: clean.
> D-027 (one design front + back, walls + towers), D-028 (v1 turns the whole stack; pumps in the robot).

**What it is:** a plate with 3 suction cups (one per stone) bolted on the butterfly plate (module A's lift). A servo
turns the plate 90°: a lying quarry stack becomes 3 standing stones (towers). Not turned, it holds a stack for walls.
The same module goes at the **front** (on module A, between its doors) and at the **back** (alone on its own
butterfly plate + lift, no doors). Pumps and valves are in the robot; 3 tubes reach the cups through a hollow shaft.

Full description, numbers, bearings, tube route, assembly order: **`CAD_FC/turn/README.md`**.

## Folders
| Path | What |
|---|---|
| `fc/params.py` | every shared number: butterfly plate interface, lift, stone, bought parts (datasheet values marked `DATASHEET`) |
| `fc/lib.py` | shared builders: primitives, bought parts (cup, elbow, tube with real bends, servo, pump, valve), module A interface, export |
| `fc/station_s1.py`, `station_s3.py` | the two cup stations (same holes, swap on the bench) |
| `fc/turn_t1.py` | **T1**: the whole module (bracket, bearings, hollow shaft, hub, plate, stations, tubes) + height math |
| `fc/colour_t1.py` | colours every FCStd (GUI, see below) |
| `fc/check_t1.py` | motion + collision + height check of the full cycle, A+B and B alone |
| `CAD_FC/turn/` | T1 builds: `T1_S3/`, `T1_S1/` = grab pose, FCStd + `STEP/` `STL/` `DXF/` (as clapets v7); `*_a90/` = after the turn (FCStd only); `check_report.txt` |
| `CAD_FC/stations/` | the stations alone, for a bench test |
| `research.md` | references (Barbatronic, Aerobotix, our earlier heads), pneumatics practice |

## Run
```
cd mechanical/suction-v1
FC="C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe"
"$FC" fc/turn_t1.py & STATION=S1 "$FC" fc/turn_t1.py & ANGLE=90 "$FC" fc/turn_t1.py & STATION=S1 ANGLE=90 "$FC" fc/turn_t1.py; wait
"$FC" fc/check_t1.py                                              # -> CAD_FC/turn/check_report.txt
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe" fc/colour_t1.py    # GUI opens, colours, saves, closes
```

## Numbers that drive the design
- **Stone** 320 × 110 × 110 (±4/5), ~90 g. **Quarry stack** = 3 lying stones, 320 wide × 330 tall, centres at table
  55 / 165 / 275.
- **Height ≤ 350** for robot + held objects [GR F.3]. A held stone may pass 350 inside the castle (FAQ Q9, yes):
  the stack reaches ~465 mid-turn, so **turn only in the castle**. The turning plate itself stays ≤ 350 (343.8).
- **Lift-turn:** the lift rises while the plate turns so the stack's low corner skims the table: peak 70 mm at 44°
  (module A's lift: 75).
- **Perimeter:** front A+B 1318 deployed (layout-v1); budget 1400 with everything open (FAQ Q10).

## History
- 2026-11-13: folder created as a rework of Maatoug's clapets v8 strike head (D-021). Dropped.
- 2026-11-18: fresh start (D-027). Studied: 4 cup stations, 3 carriers (pumps on the head / in the robot / 2 cups per
  stone), M1 tower unit (one cup on its own carriage to turn one stone at a time). Then D-028: v1 turns the whole
  stack → T1. Pumps moved to the robot, tubes through a hollow shaft (6002 + Ø15 tube).
- 2026-11-19: cleanup. Carriers, M1 and stations S2 / S4 removed; they are in git history (commit `a902498`,
  `fc/carrier_*.py`, `fc/mech_m1.py`, `CAD_FC/carriers/`, `CAD_FC/mechanisms/`). One stone at a time = a later version.
