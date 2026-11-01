# Crate ID Tracking System - Solution for Same ArUco ID Problem

## Problem

All blue crates share ArUco ID **36**, and all yellow crates share ArUco ID **47**. This causes tracking issues:
- When one crate moves, the system couldn't distinguish it from other crates with the same ID
- Multiple crates at different positions would overwrite each other's data
- Task planning would treat all blue crates (or yellow crates) as a single entity

## Solution

Implemented **spatial-based unique ID assignment** using `CrateIDTracker`:

### Blue Crates
- First detected: `unique_id = 1001`
- Second detected: `unique_id = 1002`
- Third detected: `unique_id = 1003`
- etc.

### Yellow Crates
- First detected: `unique_id = 2001`
- Second detected: `unique_id = 2002`
- Third detected: `unique_id = 2003`
- etc.

## How It Works

1. **Position-based Matching**: Tracks crates across frames using 2D distance
   - If a detected crate is within 15cm of a previously tracked crate → same crate, update position
   - If no match found → new crate, assign new unique ID

2. **Temporal Filtering**: 
   - Exponential Moving Average (EMA) smooths positions to reduce jitter
   - Timeout mechanism (2 seconds) removes crates that leave field of view

3. **Persistent Tracking**: Unique IDs remain constant even as crates move

## Files Modified

### Core Tracking Module
- **`strategy/crate_id_tracker.py`** - NEW: Main tracking logic
- **`full_pipeline/scripts/crate_id_tracker.py`** - Copy for full_pipeline

### Updated Files
1. **`strategy/world_state.py`**
   - `CrateInfo` now has `unique_id` (1001, 1002, ...) and `aruco_id` (36 or 47)

2. **`strategy/strategy_manager.py`**
   - Initializes `CrateIDTracker`
   - Calls `assign_unique_ids()` before processing crates

3. **`strategy/visualize_strategy.py`**
   - Uses tracker in `detect_markers()` method
   - Assigns unique IDs before passing to strategy manager

4. **`full_pipeline/scripts/crate_obstacle_manager.py`**
   - Initializes `CrateIDTracker`
   - Assigns unique IDs in `process_detected_crates()`
   - Returns `unique_id` and `aruco_id` for each crate

## Usage Example

```python
from strategy.crate_id_tracker import CrateIDTracker

# Initialize tracker (do this once)
tracker = CrateIDTracker()

# For each frame of detections:
detections = [
    {'id': 36, 'pos': (0.5, 0.3, 0.0), 'ownership': 'ours'},
    {'id': 36, 'pos': (1.2, 0.8, 0.0), 'ownership': 'ours'},
    {'id': 47, 'pos': (2.1, 1.5, 0.0), 'ownership': 'opponent'},
]

# Assign unique IDs
unique_crates = tracker.assign_unique_ids(detections)

# Result:
# [
#   {'unique_id': 1001, 'aruco_id': 36, 'pos': (0.5, 0.3, 0.0), ...},
#   {'unique_id': 1002, 'aruco_id': 36, 'pos': (1.2, 0.8, 0.0), ...},
#   {'unique_id': 2001, 'aruco_id': 47, 'pos': (2.1, 1.5, 0.0), ...},
# ]
```

## Configuration Parameters

In `crate_id_tracker.py`:

```python
BLUE_CRATE_ID_START = 1000  # Blue unique IDs start at 1001
YELLOW_CRATE_ID_START = 2000  # Yellow unique IDs start at 2001
POSITION_MATCH_THRESHOLD = 0.15  # 15cm - distance to match crates
CRATE_TIMEOUT = 2.0  # 2 seconds - remove unseen crates
```

## Benefits

✓ Each crate maintains its own identity across frames  
✓ Moving one crate doesn't affect others with same ArUco ID  
✓ Strategy system can track individual crate states  
✓ Path planning knows which specific crate is an obstacle  
✓ Task selection can target specific crates  

## Testing

The tracker automatically handles:
- Crates entering/leaving field of view
- Temporary occlusions
- Position noise (with EMA smoothing)
- Multiple crates detected in single frame

Get tracker statistics:
```python
stats = tracker.get_stats()
print(f"Active blue crates: {stats['active_blue_crates']}")
print(f"Active yellow crates: {stats['active_yellow_crates']}")
```
