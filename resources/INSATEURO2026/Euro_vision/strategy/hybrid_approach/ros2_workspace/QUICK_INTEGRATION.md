# Quick ROS2 Integration Guide

## 🚀 Fast Track: Get Package Ready for ROS Team

### Option 1: Automated Collection (Recommended)

```bash
# Navigate to ros2_workspace
cd strategy/hybrid_approach/ros2_workspace

# Run the collector script
python collect_package.py --output ../../hybrid_supervisor_ros2

# This creates a clean package with all dependencies
```

**Output structure:**
```
hybrid_supervisor_ros2/
├── main.py                           # ← ROS2 supervisor node
├── requirements.txt                  # ← Python dependencies
├── README.md                         # ← Architecture docs
├── PACKAGE_CONTENTS.md               # ← Complete file list & integration guide
├── test_imports.py                   # ← Verify all imports work
├── __init__.py
│
├── strategy/                         # ← Strategy modules
│   ├── crate_flip_manager.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py                 # ← All configuration parameters
│       ├── world_state.py            # ← Data classes (WorldState, CrateInfo, etc.)
│       └── crate_id_tracker.py       # ← Spatial ArUco tracking
│
├── kalman_filter/                    # ← Enemy tracking
│   ├── __init__.py
│   └── tracker.py                    # ← MultiMarkerTracker
│
└── path_planning/                    # ← Path optimization
    ├── __init__.py
    ├── rrt_connect.py                # ← RRT-Connect algorithm
    └── path_smoothing.py             # ← Path smoothing
```

### Option 2: Manual Collection

If the script doesn't work, copy these files manually:

**Copy from current workspace to a new folder:**

```
Source → Destination in package
──────────────────────────────────────────────────────────────

Main supervisor:
strategy/hybrid_approach/ros2_workspace/main.py
  → main.py

Strategy modules:
strategy/hybrid_approach/src/crate_flip_manager.py
  → strategy/crate_flip_manager.py

strategy/utils/__init__.py
  → strategy/utils/__init__.py

strategy/utils/config.py
  → strategy/utils/config.py

strategy/utils/world_state.py
  → strategy/utils/world_state.py

strategy/utils/crate_id_tracker.py
  → strategy/utils/crate_id_tracker.py

Kalman filter:
kalman_filter/src/kalman_filter/__init__.py
  → kalman_filter/__init__.py

kalman_filter/src/kalman_filter/tracker.py
  → kalman_filter/tracker.py

Path planning:
path_planning/utils/__init__.py
  → path_planning/__init__.py

path_planning/utils/rrt_connect.py
  → path_planning/rrt_connect.py

path_planning/utils/path_smoothing.py
  → path_planning/path_smoothing.py

Documentation:
strategy/hybrid_approach/README.md
  → README.md

strategy/hybrid_approach/requirements.txt
  → requirements.txt
```

---

## 🧪 Testing the Package

### Step 1: Verify Imports
```bash
cd hybrid_supervisor_ros2
python test_imports.py
```

Expected output:
```
Testing imports...
✓ strategy.utils.config
✓ strategy.utils.world_state
✓ strategy.utils.crate_id_tracker
✓ strategy.crate_flip_manager
✓ kalman_filter.tracker
✓ path_planning.rrt_connect
✓ path_planning.path_smoothing

✅ All critical imports successful!
```

### Step 2: Test Supervisor Logic (No ROS2)
```bash
python main.py --test --team blue
```

This runs the full decision-making logic with simulated data.

Expected output:
```
⚠️  Running in TEST MODE - ROS2 disabled
🧪 Test mode active - using console I/O instead of ROS2

##########################################################
# Test Case 1: collect_crate
##########################################################
📍 Simulated destination from Raspberry Pi: (1.50, 1.00)
...
🎯 DECISION: ACCEPT
   Reason: No enemy detected - path clear
   ...
```

---

## 🔌 ROS2 Integration Checklist

Once you hand off the package to your ROS team:

### They need to:

1. **Create ROS2 Package Structure**
   - Add `package.xml`
   - Add `setup.py` 
   - Define launch files

2. **Implement ROS2 Placeholders in main.py**
   
   Current placeholders to replace:
   ```python
   # Line ~145: _init_ros2()
   # Line ~165: destination_callback()
   # Line ~405: _publish_decision()
   ```

3. **Create Custom ROS2 Message**
   
   Define `NavigationDecision.msg`:
   ```
   std_msgs/Header header
   string status              # "ACCEPT" or "REJECT"
   string reason              # Human-readable
   string threat_level        # "NONE", "LOW", "MODERATE", "HIGH", "CRITICAL"
   float32 confidence
   geometry_msgs/Point[] waypoints
   string[] flip_positions    # For crate flipping
   ```

4. **Set Up Vision Data Stream**
   
   The supervisor needs ArUco detections at ~30Hz:
   ```python
   # In ROS2 callback for vision data:
   detections = {marker_id: (x, y, theta), ...}
   supervisor.update_vision(detections)
   ```

5. **Configure Topics**
   
   Subscribe to:
   - `/navigation/destination` (from Raspberry Pi)
   - `/vision/aruco_detections` (from vision system)
   
   Publish to:
   - `/navigation/decision` (decision + waypoints)

---

## 📋 Key Files for ROS Team to Understand

| File | Purpose | ROS Team Should... |
|------|---------|-------------------|
| `main.py` | Main supervisor logic | Replace ROS2 placeholders with real implementations |
| `strategy/utils/config.py` | All tunable parameters | Adjust for competition (speeds, safety thresholds) |
| `strategy/crate_flip_manager.py` | Crate counting logic | Understand but don't modify |
| `kalman_filter/tracker.py` | Enemy tracking | Use as-is, just call update() |
| `path_planning/*` | Path planning algorithms | Use as-is |
| `PACKAGE_CONTENTS.md` | Complete integration guide | Read for ROS2 message definitions |

---

## 🐛 Common Integration Issues

### Issue: Import errors in ROS2
**Solution**: Adjust import paths in `main.py` to match ROS2 package name:
```python
# Change from:
from strategy.utils.config import StrategyConfig

# To (if package name is 'hybrid_supervisor'):
from hybrid_supervisor.strategy.utils.config import StrategyConfig
```

### Issue: Kalman filter requires filterpy
**Check**: Open `kalman_filter/tracker.py` and see if it imports `filterpy`
**Solution**: Add to `requirements.txt` if needed

### Issue: Path planning fails with "no valid path"
**Cause**: Forbidden zone or obstacles blocking all routes
**Debug**: Check `config.forbidden_zone` parameters in `config.py`

---

## 📞 Support

For integration help:
1. Read `README.md` for architecture overview
2. Check `PACKAGE_CONTENTS.md` for complete file list and ROS2 topics
3. Run `python main.py --test` to verify logic works
4. Check imports match ROS2 package structure

---

## ⚡ Quick Commands Reference

```bash
# Collect package
python collect_package.py -o ros2_package

# Test imports
cd ros2_package && python test_imports.py

# Test supervisor logic
python main.py --test --team blue

# Check configuration
python -c "from strategy.utils.config import DEFAULT_CONFIG; print(DEFAULT_CONFIG)"

# Zip for transfer
zip -r hybrid_supervisor.zip ros2_package/
```

---

**Ready to hand off to ROS team! 🚀**
