# Full robot model (always rebuilt from the mechanisms) + Gazebo export

The whole robot, assembled by a script from the **current** mechanism files. It is never edited by hand. When a
mechanism changes (its generator rewrites its FCStd), rebuild and the robot follows. The same run writes the
Gazebo model for `eurobot2027/Simulation-Euro27`.

```
python tools/sync_robot.py            # from the hub root: rebuild if something changed + copy into the LOCAL sim clone
python tools/sync_robot.py --push     # same + commit/push the model to Simulation-Euro27 on GitHub (BY HAND ONLY)
python tools/sync_robot.py --check    # is the robot stale? (exit code 1 = stale)
python tools/sync_robot.py --force    # rebuild even if nothing changed
python tools/install_hooks.py         # once per clone (and again after the hooks change): auto-sync after git pull / commit
```

### Automatic sync: local only (2026-11-13, Maatoug)
Every automatic sync **rebuilds the robot and copies it into your local sim clone**. **Nothing is pushed to GitHub
automatically.** Publishing the model to Simulation-Euro27 is a deliberate step: `python tools/sync_robot.py --push`.
(Until 2026-11-13 the Claude Stop hook and post-commit pushed on their own; changed so that an unfinished or uncommitted
mechanism never reaches the shared sim repo by accident.)

| When | What happens | Set up by |
|---|---|---|
| End of each Claude turn, if a watched file changed | rebuild in the background (~3 min) + copy `excalibot_fc` into `eurobot2027/Simulation-Euro27`; a line in the Claude UI says so | `.claude/settings.json` (Stop hook), shared |
| `git commit` in the hub | same (catches changes made outside Claude, e.g. saved in the FreeCAD GUI) | `tools/install_hooks.py`, once per clone |
| `git pull` in the hub | same (your local robot + sim follow the other lead's mechanism changes) | same |
| You want the team's sim to have it | `python tools/sync_robot.py --push` | by hand |

**Watched files ("a mechanism changed"):** `robot/fc/layout.py`, `robot/fc/build_robot.py`, `robot/fc/robot.urdf.xacro`,
the clapets model named by `L.CLAPETS` (`clapets/<version>/CAD_FC/MODULE_<VERSION>.FCStd`) and the Grail lift model named
by `L.GRAIL_LIFT` (`grail-lift/CAD_FC/GRAIL_LIFT_<v>.FCStd` + `joints_<v>.json`). Change detection = file hashes against
`sim/excalibot_fc/manifest.json` (the hashes of the last build).
- **Editing a generator `.py` is not a change** until you run it and it rewrites its FCStd.
- **Which version of a mechanism is used is set in `layout.py`, never guessed** (e.g. `CLAPETS = "clapets-v8"`). A new
  version folder (clapets-v9…) is picked up only when `layout.py` names it. Changing that line is a team choice
  (v7 is the printed version, v8 is proposed).
- **A new mechanism** (e.g. the ball launcher) is not in the robot until it gets a placement in `layout.py`, a loader in
  `build_robot.py` and a line in `sources()` of `tools/sync_robot.py`.
- Placement numbers don't follow a mechanism's own geometry: if a mechanism changes its reference (e.g. its z 0), fix
  the number in `layout.py` (see `CLAPETS_Z0`).

**Safety rules built in** (`tools/hooks/sync_bg.py` → `tools/sync_robot.py`, output in `CAD_FC/sync.log`):
- Runs in the background and always exits 0: never blocks a Claude turn or a commit.
- One run at a time (lock `CAD_FC/.sync.lock`, a lock older than 30 min = a crashed run). A mechanism saved during a
  build → rebuilt again (max 3 times).
- A failed build, or no FreeCAD found (`freecadcmd`, FreeCAD 1.1 default path, or `FREECADCMD`), is remembered
  (`CAD_FC/.sync.failed`) and **not retried until a watched file changes**; the Claude UI says so **once** per failed state.
- No sim clone at `eurobot2027/Simulation-Euro27` → the build still runs, the copy is skipped (no error).
- The local copy replaces `src/eb27_description/robots/excalibot_fc` in the sim clone (that folder is 100 % generated:
  never edit it there). Nothing else in the sim clone is touched, nothing is committed there.

**Manual push (`--push`)**: the sim clone's copy of `excalibot_fc` is thrown away, the clone is pulled, the export is
copied on top, committed and pushed; only that folder is committed (no merge conflicts when both hub clones push). The
commit message names the hub commit and lists robot sources still uncommitted in the hub, so **commit the hub first**.
It refuses (and says why) if the sim clone is not on `main` or has unpushed commits of your own.

**Things to know**
- The local sim copy always equals **your hub's** robot. After the other lead pushes a newer model to the sim repo,
  pull the hub too (the post-merge hook then rebuilds the same robot), or your next local sync overwrites their model
  in your sim clone with your older one (only locally, never on GitHub).
- The robot outputs (`CAD_FC/ROBOT.*`, `sim/excalibot_fc/`) are generated binaries in git (LFS). If both leads commit
  a rebuild, a pull can conflict on them: never merge them, take either side and rebuild
  (`git checkout --theirs -- mechanical/robot` then `python tools/sync_robot.py --force`).
- After a pull that changed `tools/hooks/post-*`, run `python tools/install_hooks.py` again (it copies them into
  `.git/hooks`).

Then, in the sim: `./sim build`, and use robot model **`excalibot_fc`** (scenario `robot: excalibot_fc` or the menu).
The existing `excalibot` (SolidWorks export) is not touched.

## What is in it

| Module | Source | Notes |
|---|---|---|
| Layout numbers | `fc/layout.py` | **the only place to move things**: footprint, wheels, clapets placement, Grail lift side, mast… |
| Drive | generated (`build_robot.py`) | 2 × Pololu 37D 30:1 (#4742, dims from the Pololu drawing), JSUMO wheels Ø74 × 44, track 252 mm, gearbox 7 mm above the axle |
| Odometry | **reserve** | 2 free wheels Ø30 + AMT102 (datasheet dims), CDR-2027 style; design TBD |
| Casters | generated | 4 ball casters Ø12 (for the sim) |
| Clapets front + back | `mechanical/clapets/<L.CLAPETS>/CAD_FC/MODULE_*.FCStd` | doors folded at start; moving groups read from each part's `MotionGroup` |
| Grail lift | `mechanical/grail-lift/CAD_FC/GRAIL_LIFT_<v>.FCStd` + `joints_<v>.json` | v3 (compact) on the left side, above the wheel; T8 screw + NEMA17 on the roof |
| Base plate, roof, beacon support | generated | roof at 305 with the Grail lift's slot; beacon support Ø80, top 430 |
| Battery, electronics | **reserves** | boxes in the middle |

Outputs: `CAD_FC/ROBOT.FCStd`, `CAD_FC/ROBOT.step`, `CAD_FC/robot_report.txt` (start perimeter, parts above
350 mm, interferences **between** modules), `sim/excalibot_fc/`.

## Gazebo model (`sim/excalibot_fc/`)
- `robot.yaml`: the sim's format (body mesh, collisions, diff drive from the layout, casters, lidar in the beacon
  support, IMU) + **`actuators:`** = the moving parts.
- `robot.urdf.xacro`: the sim's generic robot + one link and one position-controlled joint per actuator.
- `meshes/*.stl` (mm, scaled 0.001): `body.stl` = everything fixed; one mesh per moving part (the sim builds the
  collision boxes from these).
- **Colours = the FreeCAD colours.** Each link is also split into one mesh per colour, `<link>_<rrggbb>.stl`, listed
  in `robot.yaml` as `visuals: [{mesh, rgba}]` and drawn by `robot.urdf.xacro`. Where the colours come from:
  clapets = the colours saved in the module's FCStd (read from its `GuiDocument.xml`, so set and save them in the
  FreeCAD GUI); Grail lift = the generator's `colors` table in `joints_<v>.json` (its FCStd is saved headless, no
  colours inside); drive, plates, roof, beacon support = `GEN_COLORS` in `fc/build_robot.py`; anything else =
  FreeCAD grey.
- Joints (zero = start pose, everything folded). Command one with
  `ros2 topic pub /<ns>/<joint>/cmd std_msgs/msg/Float64 "{data: <m or rad>}"`:
  - `clapets_front_lift`, `clapets_back_lift` (prismatic, 0 … 0.075 m)
  - `clapets_*_door_left/right` (revolute, 0 = folded … open)
  - `clapets_*_head` (revolute ±90°)
  - `grail_lift` (prismatic), `grail_flip` (revolute, 0 = folded under the roof, −π = arm out)
- **Sim repo change needed (done locally in your clone, not committed):** `eb27_bringup/robot_config.py` bridges
  every `actuators:` entry (`/<ns>/<name>/cmd`, Float64). Commit it in Simulation-Euro27 when you're happy with it.
- Not simulated yet: grabbing the Grail or stones (needs a detachable-joint "magnet" / suction plugin); moving parts
  have no collision shapes (visual only).

## Robot frame
Same as the sim: X forward, Y left, Z up, origin = middle of the wheel axle on the table (`base_footprint`).
