# steps.py - assembly steps of clapets v7 module A (right side; the left side is its mirror).
# Plain Python (no FreeCAD): read by fc/assembly_images_v7.py (renders the views) and assembly/make_guide.py (PDF).
# Part spec: (CAD label without the -N suffix, a trailing * = any label starting with it; filter, explode vector mm, balloon text). Filter: None = whole part, or a dict
# {"z": (z0, z1)} / {"x": ...} / {"y": ...} on the centre of each solid/screw (keeps the ones inside).
# Views: "iso" = from the front-right, above (front = the stack side, +y). Detail: 2D orthographic view along an axis,
# optionally cut (section) by a plane through the given point, cropped to a box.

ISO = (1.0, 1.5, 0.9)          # camera direction (from the model toward the eye)
ISO_BACK = (1.0, -1.5, 0.9)    # from the back-right, above

STEPS = [
    dict(
        id=1, title="Heat-set inserts in the socle",
        intro="Press the 4 M3 threaded inserts into the socle's rail blocks, from the top. PLA: iron at ~225 C, let "
              "them sink with light pressure, stop flush.",
        context=[],
        new=[("A_SOCLE", None, (0, 0, 0), "Socle"), ("FIX_INSERT_SOCLE", None, (0, 0, 18), "M3 insert x4")],
        view=ISO,
        detail=dict(axis="x", labels=["A_SOCLE", "FIX_INSERT_SOCLE"], section=(33.45, 0, 0),
                    box=(20, 60, 30, 62, 0, 40), caption="Section through an M3 insert hole: 5.4 x 7 deep, mouth cone 6.2 x 1.5"),
        parts=[("4", "M3 heat-set insert")],
        tools="Soldering iron with an insert tip (~225 C for PLA), flat metal tool to press them flush",
    ),
    dict(
        id=2, title="Motor into the socle",
        intro="Put the NEMA 17 in the socle's notch, connector toward the back (the notch is open there). It does not "
              "rest on anything: in step 4 it hangs from the motor plate by its 4 screws, 1 mm above the floor.",
        context=["A_SOCLE", "FIX_INSERT_SOCLE"],
        new=[("REF_NEMA17", None, (0, 0, 70), "NEMA 17")],
        view=ISO_BACK,
        detail=dict(axis="z", labels=["A_SOCLE", "REF_NEMA17"], section=None,
                    box=(-70, 70, -5, 65, -25, 45), caption="Top view: motor in the notch, connector to the back (open side)"),
        parts=[("1", "NEMA 17 (17HS4401S, from the printer)")],
        tools="-",
    ),
    dict(
        id=3, title="2020 rails into the socle",
        intro="Slide an M5 T-nut into the back slot of each profile, push both profiles down into the rail blocks and "
              "fix each one from the back with an M5 x 8 into its T-nut.",
        context=["A_SOCLE", "REF_NEMA17"],
        new=[("REF_RAILS_2020", None, (0, 0, 60), "2020 profile x2"),
             ("FIX_TNUT_RAILS", {"z": (0, 100)}, (0, 0, 60), "M5 T-nut x2"),
             ("FIX_VIS_RAILS", {"z": (0, 100)}, (0, -25, 0), "M5 x 8 x2")],
        view=ISO_BACK,
        detail=dict(axis="x", labels=["A_SOCLE", "REF_RAILS_2020", "FIX_TNUT_RAILS", "FIX_VIS_RAILS"], section=(40.45, 0, 0),
                    box=(25, 60, 5, 62, 0, 60), caption="Section through a rail screw: M5 x 8 from the back into the T-nut"),
        parts=[("2", "2020 profile 350 mm (printer)"), ("2", "M5 T-nut"), ("2", "M5 x 8 button head")],
        tools="3 mm hex key",
    ),
    dict(
        id=4, title="Motor clamp plate",
        intro="Lower the motor plate over the rails onto the motor and the two rail blocks. 4 x M3 x 10 into the motor, "
              "4 x M3 x 12 into the inserts.",
        context=["A_SOCLE", "REF_NEMA17", "REF_RAILS_2020"],
        new=[("A_PLATINE_MOTEUR", None, (0, 0, 50), "Motor plate"),
             ("FIX_VIS_MOTEUR", None, (0, 0, 80), "M3 x 10 x4"), ("FIX_VIS_PLATINE", None, (0, 0, 80), "M3 x 12 x4")],
        view=ISO,
        detail=dict(axis="z", labels=["A_PLATINE_MOTEUR", "FIX_VIS_MOTEUR", "FIX_VIS_PLATINE", "REF_RAILS_2020"], section=None,
                    box=(-60, 60, 5, 60, 30, 50), caption="Top view: 4 screws into the motor (centre), 4 into the rail blocks"),
        parts=[("1", "Motor plate (printed)"), ("4", "M3 x 10 socket head (motor)"), ("4", "M3 x 12 button head (inserts)")],
        tools="2.5 mm hex key (M3 socket head), 2 mm hex key (M3 button head)",
    ),
    dict(
        id=5, title="TR8 nut and nut support on the carriage plate",
        intro="Put the TR8 nut UNDER the support's shelf (flange up against the shelf), 4 x M3 x 10 from below (they cut "
              "their own thread). Push the 2 M4 nuts into the pockets in the back face of the support's wall, hold the "
              "support behind the butterfly plate and screw the 2 M4 x 8 from the front (the printer's own: they held "
              "the Y belt clamp under this plate).",
        context=["REF_PLAQUE_PAPILLON", "REF_ROUES_V", "REF_ENTRETOISES*", "REF_RONDELLES*"],
        new=[("A_SUPPORT_ECROU", None, (0, -35, 0), "Nut support"),
             ("REF_ECROU_T8", None, (0, -35, -30), "TR8 nut"),
             ("FIX_VIS_SUPPORT_ECROU", None, (0, -35, -55), "M3 x 10 x4"),
             ("FIX_ECROU_SUPPORT_ECROU", None, (0, -60, 0), "M4 nut x2"),
             ("FIX_VIS_PLAQUE_ECROU", None, (0, 30, 0), "M4 x 8 x2")],
        view=ISO_BACK,
        detail=dict(axis="x", labels=["A_SUPPORT_ECROU", "REF_ECROU_T8", "FIX_VIS_SUPPORT_ECROU", "REF_PLAQUE_PAPILLON", "FIX_VIS_PLAQUE_ECROU", "FIX_ECROU_SUPPORT_ECROU"],
                    section=(0, 0, 0), box=(-30, 30, 15, 55, 100, 172), caption="Section on the lead screw axis: nut flange under the shelf; M4 x 8 through the plate into the nuts in the wall"),
        parts=[("1", "TR8 x 8 brass nut (printer)"), ("4", "M3 x 10 button head (self-tapping into the 2.5 pilots)"),
               ("2", "M4 x 8 button head (printer, from the Y belt clamp)"), ("2", "M4 nut")],
        tools="2 mm hex key, 2.5 mm hex key, 7 mm wrench",
    ),
    dict(
        id=6, title="Coupler, carriage, lead screw",
        intro="Coupler on the motor shaft (~13 mm of shaft inside). Slide the carriage (butterfly plate with its V-wheels, "
              "as on the printer) down onto the rails; set the eccentric spacers so the wheels roll without play. Screw "
              "the lead screw down through the TR8 nut into the coupler and tighten the coupler.",
        context=["A_SOCLE", "REF_NEMA17", "REF_RAILS_2020", "A_PLATINE_MOTEUR"],
        new=[("REF_COUPLEUR_5x8", None, (0, 0, 40), "Coupler 5-8"),
             ("REF_PLAQUE_PAPILLON", None, (0, 0, 130), "Carriage plate"), ("REF_ROUES_V", None, (0, 0, 130), "V-wheels"),
             ("REF_ENTRETOISES*", None, (0, 0, 130), ""), ("REF_RONDELLES*", None, (0, 0, 130), ""),
             ("A_SUPPORT_ECROU", None, (0, 0, 130), "Nut support"), ("REF_ECROU_T8", None, (0, 0, 130), ""),
             ("REF_VIS_T8", None, (0, 0, 260), "Lead screw 303 mm")],
        view=ISO_BACK,
        detail=dict(axis="x", labels=["REF_NEMA17", "REF_COUPLEUR_5x8", "REF_VIS_T8", "A_PLATINE_MOTEUR", "A_SOCLE"], section=(0, 0, 0),
                    box=(-30, 30, 5, 60, 0, 90), caption="Section on the axis: motor shaft and lead screw in the coupler (gap ~0.1 mm)"),
        parts=[("1", "5 x 8 coupler (printer)"), ("1", "Carriage: butterfly plate + 4 V-wheels + spacers (printer)"),
               ("1", "TR8 lead screw, cut to 303 mm")],
        tools="Coupler hex key (printer), eccentric spacer wrench",
    ),
    dict(
        id=7, title="Top crossbar",
        intro="Press the 608 into the top crossbar from below, slide it onto the two rails and over the lead screw's top "
              "end. Fix with 2 x M5 x 8 into T-nuts (back slots).",
        context=["A_SOCLE", "REF_RAILS_2020", "REF_VIS_T8", "REF_PLAQUE_PAPILLON", "A_PLATINE_MOTEUR"],
        new=[("A_TRAVERSE_HAUT", None, (0, 0, 50), "Top crossbar"), ("REF_608ZZ", {"z": (300, 400)}, (0, 0, 30), "608"),
             ("FIX_TNUT_RAILS", {"z": (300, 400)}, (0, 0, 50), "M5 T-nut x2"),
             ("FIX_VIS_RAILS", {"z": (300, 400)}, (0, -25, 50), "M5 x 8 x2")],
        view=ISO_BACK,
        detail=dict(axis="x", labels=["A_TRAVERSE_HAUT", "REF_608ZZ", "REF_VIS_T8", "REF_RAILS_2020"], section=(0, 0, 0),
                    box=(-30, 30, 10, 55, 330, 370), caption="Section on the axis: lead screw top end in the 608"),
        parts=[("1", "608ZZ bearing"), ("2", "M5 T-nut"), ("2", "M5 x 8 button head")],
        tools="3 mm hex key",
    ),
    dict(
        id=8, title="Door unit: servo",
        intro="1) Pinion on the servo horn: 4 x M2 x 10 self-tapping. 2) Push the 3 M3 nuts up into their hex recesses "
              "through the windows (2 on the outer side, 1 from the front). 3) Thread the servo connector through the "
              "cable hole in the outer wall. 4) Slide the servo in from the front, ears on the posts. 5) 3 x M3 x 8.",
        context=["A_AILE_D"],
        new=[("FIX_ECROU_AILE_D", {"z": (70, 78)}, (12, 0, -4), "M3 nut x3"),
             ("REF_MG996R_D", None, (0, 75, 0), "MG996R"), ("A_PIGNON_PORTE_20T", {"x": (0, 300)}, (0, 75, 0), "20T pinion"),
             ("FIX_VIS_PIGNON_PORTE", {"x": (0, 300)}, (0, 75, 18), "M2 x 10 x4"),
             ("FIX_VIS_AILE_D", {"z": (75, 90)}, (0, 0, 30), "M3 x 8 x3")],
        view=ISO,
        detail=dict(axis="x", labels=["A_AILE_D", "REF_MG996R_D", "FIX_ECROU_AILE_D", "FIX_VIS_AILE_D"], section=None, from_plus=True,
                    box=(140, 152, 30, 70, 40, 100), caption="Outer side (robot side): 2 nut windows under the ears, cable hole"),
        parts=[("1", "MG996R servo"), ("1", "20T pinion (printed)"), ("4", "M2 x 10 self-tapping (servo kit / horn)"),
               ("3", "M3 nut"), ("3", "M3 x 8 button head")],
        tools="Small screwdriver (M2), 2 mm ball-end hex key (from the front, at an angle)",
    ),
    dict(
        id=9, title="Door unit on the carriage plate",
        intro="Put an M4 nut in the pocket of the keel's front face. Hold the door unit against the plate's front face and "
              "screw the lower M4 x 16 from behind the plate. Leave it a bit loose: the slot lets the door unit move "
              "+/-1.5 mm sideways to centre the doors.",
        context=["REF_PLAQUE_PAPILLON", "A_SUPPORT_ECROU", "REF_RAILS_2020"],
        new=[("A_AILE_D", None, (0, 40, 0), "Door unit"), ("REF_MG996R_D", None, (0, 40, 0), ""),
             ("FIX_ECROU_AILE_D", {"z": (55, 70)}, (0, 60, 0), "M4 nut"),
             ("FIX_VIS_AILE_D", {"z": (55, 70)}, (0, -30, 0), "M4 x 16")],
        view=ISO,
        detail=dict(axis="z", labels=["A_AILE_D", "REF_PLAQUE_PAPILLON", "FIX_ECROU_AILE_D", "FIX_VIS_AILE_D"], section=(0, 0, 65),
                    box=(60, 110, 40, 70, 55, 75), caption="Section at z 65: M4 from behind the plate, nut in the keel pocket, slot +/-1.5"),
        parts=[("1", "M4 nut"), ("1", "M4 x 16 button head")],
        tools="2.5 mm hex key, 7 mm wrench",
    ),
    dict(
        id=10, title="Rod, arms and 28T gear",
        intro="Bottom 608 into its seat. Hold, from the bottom up: spacer 3 mm, lower arm, 28T gear (meshing with the "
              "pinion), upper arm, spacer 4 mm. Push the Ø8 rod down from the top through all of them into the bottom 608. "
              "Do not tighten the clamps yet (step 12).",
        context=["A_AILE_D", "REF_MG996R_D", "A_PIGNON_PORTE_20T"],
        new=[("REF_608ZZ", {"z": (25, 40), "x": (0, 300)}, (0, 0, 20), "608"),
             ("A_ENTRETOISE_608_BAS", {"x": (0, 300)}, (0, 35, 0), "Spacer 3"),
             ("A_BRAS_PORTE_D_BAS", None, (0, 45, 0), "Lower arm"),
             ("A_ROUE_PORTE_28T", {"x": (0, 300)}, (0, 45, 0), "28T gear"),
             ("A_BRAS_PORTE_D_HAUT", None, (0, 45, 0), "Upper arm"),
             ("A_ENTRETOISE_608_HAUT", {"x": (0, 300)}, (0, 35, 0), "Spacer 4"),
             ("REF_TIGE_PORTE_D8", {"x": (0, 300)}, (0, 0, 150), "Rod Ø8 x 203")],
        view=ISO,
        detail=dict(axis="y", labels=["A_AILE_D", "REF_608ZZ", "A_ENTRETOISE_608_BAS", "A_BRAS_PORTE_D_BAS", "A_ROUE_PORTE_28T",
                                       "A_BRAS_PORTE_D_HAUT", "A_ENTRETOISE_608_HAUT", "REF_TIGE_PORTE_D8", "A_CAPOT_AILE_D"],
                    section=(0, 82, 0), box=(105, 160, 60, 100, 20, 245), caption="Section on the rod axis: the stack order on the rod"),
        parts=[("1", "608ZZ bearing"), ("1", "Ø8 rod, 203 mm"), ("2", "Printed spacers (3 and 4 mm)")],
        tools="-",
    ),
    dict(
        id=11, title="Cap",
        intro="Top 608 into the cap from below. Put the M4 nut in the cap's front pocket. Lower the cap over the rod's top "
              "end onto the spine. 2 x M3 x 16 from the top into nuts pushed into the pockets under the top shelf. "
              "Upper M4 x 16 from behind the plate into the cap.",
        context=["A_AILE_D", "REF_TIGE_PORTE_D8", "A_BRAS_PORTE_D_HAUT", "REF_PLAQUE_PAPILLON"],
        new=[("A_CAPOT_AILE_D", None, (0, 0, 45), "Cap"), ("REF_608ZZ", {"z": (220, 240), "x": (0, 300)}, (0, 0, 25), "608"),
             ("FIX_VIS_AILE_D", {"z": (215, 245), "y": (35, 62)}, (0, 0, 80), "M3 x 16 x2"),
             ("FIX_ECROU_AILE_D", {"z": (210, 225)}, (0, 0, -15), "M3 nut x2"),
             ("FIX_ECROU_AILE_D", {"z": (230, 240)}, (0, 30, 45), "M4 nut"),
             ("FIX_VIS_AILE_D", {"z": (230, 240), "y": (40, 75)}, (0, -30, 0), "M4 x 16")],
        view=ISO,
        detail=dict(axis="x", labels=["A_CAPOT_AILE_D", "A_AILE_D", "FIX_VIS_AILE_D", "FIX_ECROU_AILE_D"], section=(143, 0, 0),
                    box=(130, 160, 30, 70, 205, 245), caption="Section through a cap screw: nut in its pocket under the top shelf"),
        parts=[("1", "608ZZ bearing"), ("2", "M3 x 16 button head"), ("2", "M3 nut"), ("1", "M4 x 16 button head"), ("1", "M4 nut")],
        tools="2 mm hex key, 2.5 mm hex key",
    ),
    dict(
        id=12, title="Set the door angle, tighten the clamps",
        intro="Power the servo to its reference angle (90 deg). Turn the door to the clamp position (arms pointing at the "
              "stack, door sheet parallel to the stack face). Tighten the 28T clamp (2 x M3 x 12 + nuts) and the two arm "
              "clamps (M3 x 12 + nut each): nuts slide into their pockets from the outer side.",
        context=["A_AILE_D", "A_CAPOT_AILE_D", "REF_TIGE_PORTE_D8", "A_PIGNON_PORTE_20T", "REF_MG996R_D"],
        new=[("A_ROUE_PORTE_28T", {"x": (0, 300)}, (0, 0, 0), "28T"),
             ("A_BRAS_PORTE_D_BAS", None, (0, 0, 0), ""), ("A_BRAS_PORTE_D_HAUT", None, (0, 0, 0), ""),
             ("FIX_VIS_ROUE_28T", {"x": (0, 300)}, (-25, 0, 0), "M3 x 12 x2"),
             ("FIX_ECROU_ROUE_28T", {"x": (0, 300)}, (18, 0, 0), "M3 nut x2"),
             ("FIX_VIS_BRAS_D", {"x": (110, 145)}, (-25, 0, 0), "M3 x 12 x2"),
             ("FIX_ECROU_BRAS_D", {"x": (130, 140)}, (25, 0, 0), "M3 nut x2")],
        view=ISO,
        detail=dict(axis="z", labels=["A_ROUE_PORTE_28T", "FIX_VIS_ROUE_28T", "FIX_ECROU_ROUE_28T", "REF_TIGE_PORTE_D8"], section=(0, 0, 113),
                    box=(108, 152, 60, 104, 100, 125), caption="Section through the 28T clamp: nut pocket open to the outside, key from the left"),
        parts=[("4", "M3 x 12 socket head"), ("4", "M3 nut")],
        tools="2.5 mm hex key, servo tester or the robot board",
    ),
    dict(
        id=13, title="Door sheet and pads",
        intro="Glue the 3 foam pads on the door sheet's inner face. Fix the sheet on the two arm tabs: 4 x M3 x 16 from "
              "the outside, nuts on the tabs' inner face (free, above and below each arm). The slots let you set the "
              "pads +/-1.5 mm against the stack.",
        context=["A_AILE_D", "A_CAPOT_AILE_D", "REF_TIGE_PORTE_D8", "A_BRAS_PORTE_D_BAS", "A_BRAS_PORTE_D_HAUT", "A_ROUE_PORTE_28T"],
        new=[("A_TOLE_PORTE", {"x": (0, 300)}, (35, 0, 0), "Door sheet (MDF 3)"),
             ("REF_MOUSSE_PORTE", {"x": (0, 300)}, (35, 0, 0), "Foam pad x3"),
             ("FIX_VIS_BRAS_D", {"x": (150, 180)}, (60, 0, 0), "M3 x 16 x4"),
             ("FIX_ECROU_BRAS_D", {"x": (150, 165)}, (-20, 0, 0), "M3 nut x4")],
        view=ISO,
        detail=dict(axis="x", labels=["A_BRAS_PORTE_D_BAS", "A_TOLE_PORTE", "FIX_VIS_BRAS_D", "FIX_ECROU_BRAS_D"], section=None, from_plus=True,
                    box=(150, 175, 120, 145, 20, 70), caption="Lower tab from outside: one screw under and one over the arm"),
        parts=[("1", "Door sheet, MDF 3 mm (laser cut, A_TOLE_PORTE.dxf)"), ("3", "Foam pad"), ("4", "M3 x 16 button head"),
               ("4", "M3 nut")],
        tools="2 mm hex key, 5.5 mm wrench or pliers",
    ),
]

FINAL = dict(
    title="Left door unit and final checks",
    text=["Repeat steps 8 to 13 for the left door unit: every part is the mirror of the right one (files *_G).",
          "Centre the two doors: loosen the 2 M4 per door unit, slide them (+/-1.5 mm) until both doors close on the stack "
          "at the same time, tighten.",
          "Check by hand: the carriage runs the whole 75 mm without play; each door turns freely from fold (+90) to open (-38).",
          "Run the servos slowly the first time and watch the gears and the arms (CAD door sweep: no contact over the travel).",
          "PLA creeps: re-tighten the rod clamps and the servo screws after the first runs."],
)
