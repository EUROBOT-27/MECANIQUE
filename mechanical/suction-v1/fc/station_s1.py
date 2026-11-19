# Station S1: RIGID holder. One printed part: flange on the carrier + round body + bulkhead wall for the cup.
# Compliance = the bellows only (stroke ~6). No stone stop: the stone sits on the squashed bellows.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import V, ycyl, ring_y, box, solid, bolt_holes, bulkhead_cuts, elbow, cup
import params as P

S, E, W = P.STATION, P.ELBOW_PL4_M5, P.BULKHEAD_WALL
YH = 21.0          # hex front face = back of the 2 mm wall (outlet clears the flange)
R_BODY = 13.0      # round body Ø26
FL_T = 4.0         # flange on the carrier


def build():
    add = [ycyl(R_BODY, 0, YH + W), ring_y(S["od_max"] / 2, R_BODY - 1, 0, FL_T)]
    cut = bulkhead_cuts(YH, back_to=-1, slot_r=R_BODY + 1) + bolt_holes(-1, FL_T + 1)
    cut.append(box(0, S["od_max"] / 2 + 1, -1, FL_T + 0.01, -5.6, 5.6))   # insertion notch: the elbow comes in from behind
    holder = solid(add, cut)
    el, port, _, ya = elbow(YH)
    cp, ylip = cup(YH + W)
    tb, tlen, trad = lib.station_tube(port, ya)
    y_stone = ylip - P.CUP["stroke"]
    parts = [("S1_HOLDER", holder, "print"), ("REF_ELBOW_PL4_M5", el, "bought"), ("REF_CUP_DPS30", cp, "bought"),
             ("REF_TUBE_4x2.5", tb, "bought"), ("REF_CARRIER", lib.carrier_ref(), "ref"), ("REF_STONE", lib.stone_ref(y_stone), "ref")]
    parts += lib.station_screws(FL_T, 16)
    port_info = dict(port=[round(port.x, 2), round(ya, 2), round(port.z, 2)], port_dir=[1.0, 0.0, 0.0], tube_side="front")
    info = dict(title="S1 rigid holder", lip_y_free=round(ylip, 1), stone_face_y_held=round(y_stone, 1),
                compliance="bellows only, ~%.0f mm" % P.CUP["stroke"], stone_stop="none (squashed bellows)",
                tube_exit="y %.1f, +x, in front of the carrier" % ya, tube_bend_r=trad,
                carrier_hole_d=S["hole_d"], fixing="3 x M3 x 16 + nut behind the carrier", printed_parts=1, tpu_parts=0,
                print_orientation="flange on the bed (body up), no support",
                assembly="elbow in from behind the carrier (hex into the pocket), cup screwed on from the front, tube on")
    notes = ["Cheapest and stiffest; the stone can rock on the bellows (no rigid seat).",
             "Bulkhead: check the real M5 thread length of the elbow (2 mm wall + cup insert)."]
    info.update(port_info)
    return parts, info, notes


if lib.is_main(__file__):
    parts, info, notes = build()
    lib.save("S1_rigid", "stations", parts, info, notes)
