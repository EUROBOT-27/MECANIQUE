# Mechanical design principles

Our reference standard: **review every concept and every CAD against this list.**
Main source: Aerobotix INSAT's 2026 robot (2nd at the European final). Details in
`resources/_notes/aerobotix-2026-robot.md`.

✅ = Seif explicitly wants this · ◻ = proposed by Claude from the study; Maatoug keeps or drops it (with Seif)

## Architecture
- ✅ **Symmetry.** Aerobotix had identical picking faces front and back, so the robot never turns around to pick.
  For us: make it symmetric wherever that saves a rotation. It also helps us play either team colour.
- ◻ **Drive axle through the robot's centre**, so it turns on the spot without sweeping a big circle.
- ◻ **Low centre of gravity.** Heavy parts (motors, battery, base plates) go on the base plate. Light materials
  higher up (laser-cut MDF box). This matters even more for us: the Grail on the roof (> 300 mm) and stones held high.
- ◻ **Independent modules, one actuator per job.** If one module fails, the robot still scores with the others.
  Fewer shared mechanisms means fewer single points of failure.
- ◻ **Subassemblies that can be removed on their own** (drive, gripper, pneumatics, electronics), so fixes
  between matches take minutes.
- ◻ **Electronics in a top box with a hinged lid; battery in a pull-out drawer.** We need a fast battery swap
  anyway, because the rules require 3 matches in a row [GR F.4.b].

- ✅ **Reserve space for mechanisms that come later** (Seif, 2026-10-26). For each mechanism that isn't designed yet
  (lintel hand, launcher…), add to the top-level SolidWorks assembly:
  1. A **reserved block**: a simple transparent, coloured body with the mechanism's rough size, including the volume it
     sweeps when it moves. Nothing else may enter it. Check with Interference Detection before each CAD review.
  2. **Mounting points on the chassis now**: a 20×20 profile rail, or a hole pattern, where the mechanism will bolt on
     later. Profiles with T-nuts let the exact position change without re-cutting parts.
  3. **A cable path** (zip-tie anchors), plus a share of the **mass** and **power** budget and a spare motor/servo output (tell Hamza Bjaoui).
  The roof gets its own layout sketch: beacon support (within Ø200 of the centre), e-stop, Grail landing spot,
  launcher, lintel hand.

## Details
- ✅ **3D-printed zip-tie anchors designed into the CAD** (Aerobotix had 39). Cable routing is designed, not improvised.
- ◻ **Casters ~2 mm above the floor line**, so the drive wheels always carry the weight and keep grip.
- ◻ **Separate spring-loaded encoder wheels** next to the drive wheels, so position tracking doesn't suffer when the
  drive wheels slip (Aerobotix: 3 mm drift after 100 s).
- ◻ **Bearings as cam followers** wherever a part pushes on another moving part.
- ◻ **Everything mechanical bolts to one base plate**, and the structure goes up from it via 20×20 profiles.

## Process and testing
✅ Seif: *"their methodology of testing to reach a reliable goal"*.

1. **Several concepts per mechanism.** Compare them on simplicity, ease of manufacture, reliability and number of actuators.
   Write down why each rejected concept was rejected (Aerobotix rejected A–C for clear reasons).
2. **Cheap prototypes first** (MDF, 3D prints), tested on **real game elements**, before the final design.
3. **Choose the simplest concept that works.** Fewer actuators means fewer failures.
4. **Focused CAD of the whole robot** once the concepts are chosen (Aerobotix: about 1 week).
5. **Build step by step, testing each step:** chassis → motors → power wiring → sensors and boards.
   Don't move on until the current step works.
6. **Measurable unit tests with targets** (see the table below). "It works" is not a result; "19 out of 20" is.
7. **Full match runs**, aiming to finish our actions **with time to spare** (Aerobotix: ~60 s out of 100).
8. ◻ **Make every action checkable.** Their software only moved on once the actuator confirmed the action was done.
   Mechanically, that means planning where a sensor goes (limit switch, vacuum sensor, encoder) for each action.

## Test targets (fill in as mechanisms are defined)

| Test | Target | Latest result | Date |
|---|---|---|---|
| _e.g. pick a stone from a quarry stack_ | _≥ 19/20_ | | |
| _e.g. drive 2 m and return, position error_ | _≤ 5 mm_ | | |
