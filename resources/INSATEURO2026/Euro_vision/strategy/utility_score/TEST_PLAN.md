# Strategy System Test Plan

## Test Setup
- **Team Color**: Blue (our crate ID: 36, enemy crate ID: 47)
- **Robot ID**: 17
- **Field Size**: 3.0m × 2.0m
- **Game Duration**: 100 seconds

---

## Test Case 1: Basic Pantry Placement (Close)
**Goal**: Verify robot picks closest free crate and places in empty pantry

### Setup:
- Robot position: **(1.5, 1.0)** - center field
- Our crate (ID 36): **(1.3, 0.9)** - 0.22m from robot (CLOSE)
- Our crate (ID 36): **(2.5, 0.5)** - 1.12m from robot (FAR)
- Pantry 1: **(1.15-1.35, 0.45-0.65)** - EMPTY
- Time remaining: **80s** (mid-game)

### Expected Output:
- **Selected Task**: Place hazelnut crate in pantry 1
- **Target Crate**: ID 36 at (1.3, 0.9) - closest one
- **Expected Score**: 3 points
- **Path**: Robot → (1.3, 0.9) → Pantry 1 center (1.25, 0.55)
- **Action**: PICKUP then PLACE
- **Reasoning**: Closest crate, highest utility (low distance cost)

---

## Test Case 2: Flip vs Place Priority
**Goal**: Verify flip tasks (6pts) rank higher than place tasks (3pts)

### Setup:
- Robot position: **(1.5, 1.0)**
- Our free crate (ID 36): **(1.3, 0.9)** - 0.22m from robot
- Enemy crate in pantry (ID 47): **(1.25, 0.55)** - 0.48m from robot
- Pantry 1: Contains enemy crate (OCCUPIED)
- Pantry 2: **(1.65-1.85, 0.45-0.65)** - EMPTY
- Time remaining: **80s**

### Expected Output:
- **Selected Task**: Flip enemy crate in pantry 1
- **Target**: (1.25, 0.55) - enemy crate position
- **Expected Score**: 6 points (deny 3 + gain 3)
- **Action**: FLIP
- **Task Rankings**:
  1. Flip enemy crate - 6pts, utility ~4-5
  2. Place our crate in pantry 2 - 3pts, utility ~2-3
- **Reasoning**: Double score makes flip higher utility despite similar distance

---

## Test Case 3: Occupied Pantry Skip
**Goal**: Verify system skips pantries already containing our crates

### Setup:
- Robot position: **(1.5, 1.0)**
- Our free crate (ID 36): **(1.3, 0.9)** - free
- Our crate in pantry (ID 36): **(1.25, 0.55)** - ALREADY SCORED
- Pantry 1: Contains our crate (OCCUPIED - SKIP THIS)
- Pantry 2: **(1.65-1.85, 0.45-0.65)** - EMPTY
- Time remaining: **80s**

### Expected Output:
- **Selected Task**: Place hazelnut crate in pantry 2 (NOT pantry 1)
- **Target**: Pantry 2 center (1.75, 0.55)
- **Expected Score**: 3 points
- **Debug Log**: Should show "Pantry pantry1 already has our crate, skipping"
- **Reasoning**: System avoids duplicate placements in occupied pantries

---

## Test Case 4: Distance-Based Selection
**Goal**: Verify utility calculation favors closer targets

### Setup:
- Robot position: **(1.2, 0.5)**
- Our crate A (ID 36): **(1.3, 0.6)** - 0.14m from robot (VERY CLOSE)
- Our crate B (ID 36): **(2.2, 1.2)** - 1.14m from robot (FAR)
- Pantry 1: **(1.15-1.35, 0.45-0.65)** - 0.1m from crate A
- Pantry 3: **(1.40-1.60, 1.10-1.30)** - 0.6m from crate B
- Time remaining: **80s**

### Expected Output:
- **Selected Task**: Place crate A in pantry 1
- **Path Length**: ~0.4m total (robot→crate→pantry)
- **Time Cost**: ~1.3s (0.4m / 0.3m/s)
- **Utility**: Higher due to lower distance_cost
- **Task Rankings**:
  1. Crate A → Pantry 1: distance ~0.4m, utility ~2.5
  2. Crate B → Pantry 3: distance ~1.7m, utility ~1.2
- **Reasoning**: Lower distance cost = higher utility

---

## Test Case 5: Nest vs Pantry Scoring
**Goal**: Verify pantry tasks (3pts) rank higher than nest tasks (2pts)

### Setup:
- Robot position: **(0.5, 0.2)** - near nest
- Our crate (ID 36): **(0.4, 0.3)** - 0.14m from robot
- Nest (blue): **(0.0-0.6, 0.0-0.4)** - 0.1m from crate
- Pantry 1: **(1.15-1.35, 0.45-0.65)** - 0.9m from crate
- Time remaining: **80s**

### Expected Output:
- **Selected Task**: Place hazelnut crate in pantry 1 (NOT nest)
- **Expected Score**: 3 points (pantry) > 2 points (nest)
- **Task Rankings**:
  1. Pantry task: 3pts, even with longer distance
  2. Nest task: 2pts, despite being closer
- **Reasoning**: Higher score outweighs distance penalty (weight_expected_score = 1.5)

---

## Test Case 6: Endgame Behavior (Early Game)
**Goal**: Verify return-to-nest has 0 score in first 75 seconds

### Setup:
- Robot position: **(1.5, 1.0)** - center field
- No crates available
- Time remaining: **80s** (early/mid-game)

### Expected Output:
- **Return-to-Nest Score**: 0 points
- **Task Rankings**: Return-to-nest should NOT appear (utility = 0)
- **Selected Task**: None (or other available tasks)
- **Debug Log**: "No feasible tasks" if no crates
- **Reasoning**: Return-to-nest disabled until last 25 seconds

---

## Test Case 7: Endgame Behavior (Final 25s)
**Goal**: Verify return-to-nest becomes relevant in last quarter

### Setup:
- Robot position: **(1.5, 1.0)** - center field
- Our crate (ID 36): **(1.3, 0.9)** - available but far from scoring
- Pantry 1: EMPTY
- Time remaining: **20s** (endgame!)

### Expected Output:
- **Return-to-Nest Score**: 5 or 10 points (partial/full)
- **Expected Task**: Return to nest (fully) - 10pts
- **Endgame Boost**: Utility × 5.0 multiplier
- **Task Rankings**:
  1. Return to nest: 10pts × 5.0 boost, utility very high
  2. Pantry placement: 3pts, normal utility
- **Reasoning**: Endgame positioning becomes critical in last 25s

---

## Test Case 8: Multiple Enemy Crates in Pantries
**Goal**: Verify flip task selection prioritizes closest enemy crate

### Setup:
- Robot position: **(1.5, 1.0)**
- Enemy crate in pantry 1 (ID 47): **(1.25, 0.55)** - 0.58m from robot
- Enemy crate in pantry 2 (ID 47): **(1.75, 0.55)** - 0.58m from robot (same distance)
- Enemy crate in pantry 3 (ID 47): **(1.50, 1.20)** - 0.20m from robot (CLOSEST)
- Time remaining: **80s**

### Expected Output:
- **Selected Task**: Flip enemy crate in pantry 3 (closest)
- **Target**: (1.50, 1.20)
- **Path Length**: ~0.20m
- **Expected Score**: 6 points each, but closest has highest utility
- **Reasoning**: All flips worth 6pts, distance breaks the tie

---

## Test Case 9: Mixed Container States
**Goal**: Verify system correctly identifies container types by position

### Setup:
- Robot position: **(1.5, 1.0)**
- Crate A (ID 36): **(0.3, 0.2)** - in nest zone → container='nest'
- Crate B (ID 36): **(1.25, 0.55)** - in pantry zone → container='pantry'
- Crate C (ID 36): **(0.3, 0.9)** - in fridge zone → container='fridge'
- Crate D (ID 36): **(1.5, 0.8)** - open field → container='free'
- Time remaining: **80s**

### Expected Output:
- **Debug Log** (every 30 frames):
  ```
  ID 36: ours in nest at (0.3, 0.2)
  ID 36: ours in pantry at (1.25, 0.55)
  ID 36: ours in fridge at (0.3, 0.9)
  ID 36: ours in free at (1.5, 0.8)
  ```
- **Selected Task**: Place free crate (D) in empty pantry
- **Reasoning**: Only free crates can be picked up for scoring

---

## Test Case 10: Path Visualization
**Goal**: Verify path planning avoids obstacles and shows waypoints

### Setup:
- Robot position: **(0.5, 0.5)**
- Our crate (ID 36): **(0.6, 0.6)** - free
- Enemy robot obstacle: **(1.0, 0.7)** - blocks direct path
- Pantry 1 target: **(1.25, 0.55)**
- Time remaining: **80s**

### Expected Output:
- **Path**: Should curve around enemy robot
- **Waypoints**: 5-10 waypoints displayed with numbers
- **Visual**:
  - START label at robot position (green)
  - GOAL label at pantry (purple)
  - Yellow path line with numbered waypoints
  - SOURCE circle around crate being picked
  - DESTINATION highlight on target pantry
- **Safety Factor**: < 1.0 due to enemy proximity

---

## Test Case 11: Camera Pose Verification
**Goal**: Verify camera coordinates match expected reference setup

### Setup:
- Reference markers visible: IDs 20, 21, 22, 23
- Known positions:
  - ID 21: (0.6, 0.6, 0)
  - ID 23: (0.6, 1.4, 0)
  - ID 22: (2.4, 1.4, 0)
  - ID 20: (2.4, 0.6, 0)

### Expected Output:
- **Extrinsics**: "Extrinsics computed from 4 reference markers (16 points)"
- **Camera Pose Display** (bottom right):
  ```
  Camera Pose:
  X: [value]m
  Y: [value]m  
  Z: [value]m
  Yaw: [value]deg
  ```
- **Reference Markers**: Labeled "REF M20", "REF M21", etc. with coordinates
- **Reasoning**: Validates calibration quality

---

## Test Case 12: Robot Marker Size Verification
**Goal**: Verify robot (ID 17) has correct world coordinates (3cm marker)

### Setup:
- Robot marker (ID 17) visible with 3cm physical size
- Reference markers visible for calibration
- Robot at known position on field

### Expected Output:
- **Robot Coordinates**: Should match physical position on field (±5cm error)
- **Marker Label**: "ROBOT | (x.xxx, y.yyy)m" in purple
- **Coordinates Match**: Crate coordinates at similar distances should be consistent
- **Visual**: Robot marker not offset from crates at same position
- **Reasoning**: Verifies ROBOT_MARKER_SIZE = 0.03 fix

---

## Quick Test Checklist

Run through these quick checks:

- [ ] **Robot Detection**: Place ID 17 → sees "Ally robot detected"
- [ ] **Crate Detection**: Place ID 36 → labeled "OUR CRATE" (green)
- [ ] **Enemy Detection**: Place ID 47 → labeled "ENEMY CRATE" (red)
- [ ] **Container Free**: Crate in open → container='free'
- [ ] **Container Pantry**: Crate in pantry zone → container='pantry'
- [ ] **Flip Priority**: Enemy in pantry → shows "FLIP" task ranked #1
- [ ] **Occupied Skip**: Our crate in pantry → doesn't generate duplicate task
- [ ] **Close vs Far**: Two crates → picks closest one
- [ ] **Pantry vs Nest**: Equal distance → picks pantry (3pts > 2pts)
- [ ] **Early Game**: Time > 75s → no return-to-nest tasks
- [ ] **Endgame**: Time < 25s → return-to-nest appears with high utility
- [ ] **Path Display**: Task selected → yellow path with waypoints appears
- [ ] **Zone Highlights**: Pantry task → SOURCE + DESTINATION labeled

---

## Debug Output Format

Every 30 frames, check console for:
```
[DEBUG] Detected X crates:
  ID 36: ours in free at (x.xx, y.yy)
  ID 47: opponent in pantry at (x.xx, y.yy)
[DEBUG] Generated X tasks, Y feasible
  #1: [Task description] - Score: Xpts, Utility: X.XXX
  #2: [Task description] - Score: Xpts, Utility: X.XXX
  #3: [Task description] - Score: Xpts, Utility: X.XXX
```

## Expected Utility Ranges

| Task Type | Score | Distance | Expected Utility Range |
|-----------|-------|----------|------------------------|
| Flip enemy crate | 6pts | 0.5m | 4.0 - 6.0 |
| Place in pantry | 3pts | 0.5m | 2.0 - 3.5 |
| Place in nest | 2pts | 0.5m | 1.5 - 2.5 |
| Return to nest (endgame) | 10pts | 1.0m | 15.0+ (with 5× boost) |
| Return to nest (early) | 0pts | - | 0.0 (disabled) |

## Common Issues to Check

1. **All tasks show 0 utility** → Check time_remaining is being updated
2. **Return-to-nest always ranked #1** → Check time_remaining > 75s
3. **Flip tasks never appear** → Check enemy crates are in pantry zones
4. **Robot coords way off** → Check ROBOT_MARKER_SIZE = 0.03
5. **Path goes through obstacles** → Check enemy_positions list is populated
6. **Same pantry selected twice** → Check occupied_pantries tracking

---

## Test Execution Order

1. **Test 11**: Camera calibration first
2. **Test 12**: Robot detection verification
3. **Test 9**: Container detection validation
4. **Test 1**: Basic functionality
5. **Test 4**: Distance-based selection
6. **Test 5**: Score-based priority
7. **Test 2**: Flip vs place priority
8. **Test 3**: Occupied pantry logic
9. **Test 6**: Early game (no endgame tasks)
10. **Test 7**: Endgame behavior
11. **Test 8**: Multiple target selection
12. **Test 10**: Path visualization

Run each test, verify output matches expectations, document any deviations.
