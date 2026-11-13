# Suction v1: module B (suction head) reworked (Seif)

> **Where we are (2026-11-13):** folder created, nothing designed yet. Owner: **Seif**.

Rework of the clapets module B (the suction head that turns the 3-stone stack), after D-021 (confirmed 2026-11-13).
Starting point: Maatoug's [clapets v8](../clapets-v8/README.md) (strike: carriage on 2 Ø8 rods, 3rd MG996R, scotch
yoke, 8 mm forward). Mounts on module A of [clapets v7](../clapets-v7/README.md) (the version being printed).

## Requirements (D-021)
1. **Simpler:** fewer parts and fewer special parts; nothing that needs fine tuning to work.
2. **Reliable:** no binding guides, no fragile press fits, no loads that depend on print tolerances.
3. **Buildable:** every part printable or in hand / local, every fastener reachable with a tool, an assembly order
   that works (`../design-principles.md`).
4. **Works without the doors:** mounted on module A's butterfly plate (rides the lift), but holds, lifts and turns
   the stack **by suction alone** if the doors are removed (fallback if the perimeter budget forces them out).
   Own frame, bench-testable, one simple interface to the butterfly plate.
5. **Pneumatics, cables and fixings designed in:** pumps, valves, tube routing through the rotation and the strike,
   servo cables with strain relief, zip-tie anchors.
6. Fits the current v7 module A (2026-11-12 state), insert holes per D-025, height ≤ 350 mm re-checked (v7 margin
   2.3 mm), press force tuned on real stones.

## Open (left open by Seif, 2026-11-13)
- Release: valves, or pump off only?
- Pumps on the turning head, or fixed with the tubes going through the rotation?
