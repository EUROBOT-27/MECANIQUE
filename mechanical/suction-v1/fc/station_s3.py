# Station S3: FLIP-BAR style. ABS spacer on the carrier, TPU spiral disc on it, ABS support ring on top.
# The elbow sits between the carrier and the TPU, the tube leaves sideways through a window in the spacer:
# everything stays IN FRONT of the carrier (nothing behind it). The stone is pulled onto the support ring rim.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math
import lib
from lib import V, ycyl, ring_y, box, solid, bolt_holes, bulkhead_cuts, spiral_slots, elbow, cup
import params as P

S, E, W = P.STATION, P.ELBOW_PL4_M5, P.BULKHEAD_WALL
H_SP = 18.0                        # spacer height: room for the elbow behind the TPU hub + its 3 mm travel
R_HUB = 10.0
RIM = (24.0, 37.0, H_SP, H_SP + 3.0)
WEB = (9.5, 24.5, H_SP, H_SP + 2.5)
YH = H_SP + 1.5                    # wall y 19.5..21.5
TPU_TRAVEL = 3.0


def build():
    win = box(20.0, 40.0, 2.0, 16.5, -6.5, 6.5)                                  # tube window (+x)
    spacer = solid([ring_y(38.0, 25.0, 0, H_SP)], bolt_holes(-1, H_SP + 1) + [win])
    rim = ring_y(RIM[1], RIM[0], RIM[2], RIM[3])
    web = ring_y(WEB[1], WEB[0], WEB[2], WEB[3]).cut(spiral_slots(R_HUB + 1.5, WEB[1] - 1.5, WEB[2] - 1, WEB[3] + 1))
    hub = ycyl(R_HUB, YH - 12.0, YH + W)
    tpu = solid([rim, web, hub], bulkhead_cuts(YH, back_to=YH - 13.0, slot_r=R_HUB + 1) + bolt_holes(RIM[2] - 1, RIM[3] + 1))
    cp, ylip = cup(YH + W)
    y_stop = ylip - 3.0
    ring = solid([ring_y(38.0, RIM[0], RIM[3], RIM[3] + 3.0), ring_y(31.0, 28.0, RIM[3] + 3.0, y_stop)],
                 bolt_holes(RIM[3] - 1, RIM[3] + 4) +
                 [box(-7, 7, RIM[3] + 5.0, y_stop - 3.0, 26, 33).rotate(V(0, 0, 0), V(0, 1, 0), a) for a in (-30.0, 90.0, 210.0)])
    el, port, _, ya = elbow(YH)
    tb, tlen, trad = lib.station_tube(port, ya)
    parts = [("S3_SPACER", spacer, "print"), ("S3_TPU_DISC", tpu, "tpu"), ("S3_SUPPORT_RING", ring, "print"),
             ("REF_ELBOW_PL4_M5", el, "bought"), ("REF_CUP_DPS30", cp, "bought"), ("REF_TUBE_4x2.5", tb, "bought"),
             ("REF_CARRIER", lib.carrier_ref(), "ref"), ("REF_STONE", lib.stone_ref(y_stop), "ref")]
    parts += lib.station_screws(RIM[3] + 3.0, 35)
    port_info = dict(port=[round(port.x, 2), round(ya, 2), round(port.z, 2)], port_dir=[1.0, 0.0, 0.0], tube_side="front")
    info = dict(title="S3 flip-bar: spacer + TPU disc + support ring", lip_y_free=round(ylip, 1),
                stone_face_y_held=round(y_stop, 1), compliance="bellows ~%.0f + TPU ~%.0f back, tilt" % (P.CUP["stroke"], TPU_TRAVEL),
                stone_stop="support ring rim Ø62/Ø56, 3 windows (rigid)", tube_exit="y %.1f, +x, in front of the carrier (spacer window)" % ya,
                tube_bend_r=trad, carrier_hole_d="%s (only for the elbow going in; nothing behind)" % S["hole_d"],
                fixing="3 x M3 x 35 through ring + TPU rim + spacer + carrier, nut behind", printed_parts=2, tpu_parts=1,
                print_orientation="spacer and ring: flat face on the bed; TPU: rim on the bed",
                assembly="spacer + TPU + ring stacked, 3 long screws; elbow from behind through the carrier hole into the hub, cup on")
    notes = ["Nothing behind the carrier: best when the carrier's back is crowded (lift, plate).",
             "Longest station (+18 spacer): pushes the stone face 18 mm further out than S2.",
             "M3 x 35 is long: heat-set inserts in the spacer (D-025) would allow 2 short screws instead."]
    info.update(port_info)
    return parts, info, notes


if lib.is_main(__file__):
    parts, info, notes = build()
    lib.save("S3_tpu_ring", "stations", parts, info, notes)
