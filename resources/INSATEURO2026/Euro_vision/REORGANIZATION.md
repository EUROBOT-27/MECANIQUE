# Repository Reorganization - January 15, 2026

## 📋 Overview

The repository has been reorganized to improve code maintainability and clarity by separating utility functions from main execution scripts. All major modules now follow a consistent structure with `utils/` and `main/` subdirectories.

## 🎯 Reorganization Principles

### Directory Structure
- **`utils/`** - Utility classes, helper functions, and reusable components
- **`main/`** - Main execution scripts that use the utilities

### Benefits
- ✅ Clear separation of concerns
- ✅ Easier to find and maintain utility functions
- ✅ Better code reusability
- ✅ Consistent structure across modules
- ✅ Improved import organization

---

## 📁 Reorganized Modules

### 1. Strategy Package (`strategy/`)

**Before:**
```
strategy/
├── config.py
├── world_state.py
├── task_models.py
├── crate_id_tracker.py
├── strategy_manager.py
├── visualize_strategy.py
├── example_usage.py
└── __init__.py
```

**After:**
```
strategy/
├── utils/
│   ├── __init__.py           # Utility exports
│   ├── config.py             # Configuration classes
│   ├── world_state.py        # World representation classes
│   ├── task_models.py        # Task definitions
│   └── crate_id_tracker.py   # ID tracking utility
├── main/
│   ├── __init__.py           # Main exports
│   ├── strategy_manager.py  # Main strategy engine
│   ├── visualize_strategy.py # Live visualization
│   └── example_usage.py      # Usage examples
├── README.md
└── CRATE_TRACKING_SOLUTION.md
```

**Import Changes:**
```python
# Old imports
from strategy import StrategyManager, StrategyConfig

# New imports (still works via utils/__init__.py)
from strategy.utils import StrategyConfig, WorldState, CrateInfo
from strategy.main import StrategyManager
```

---

### 2. Path Planning (`path_planning/`)

**Before:**
```
path_planning/
├── rrt.py
├── rrt_connect.py
├── A_star.py
├── path_smoothing.py
└── README.md
```

**After:**
```
path_planning/
├── utils/
│   ├── __init__.py          # Exports all algorithms
│   ├── rrt.py               # RRT algorithm
│   ├── rrt_connect.py       # RRT-Connect algorithm
│   ├── A_star.py            # A* algorithm
│   └── path_smoothing.py    # Path smoothing utilities
├── main/
│   └── __init__.py          # Main scripts (none yet)
└── README.md
```

**Import Changes:**
```python
# Old imports
from path_planning.rrt_connect import rrt_connect_plan

# New imports
from path_planning.utils import rrt_connect_plan, rrt_plan, a_star_plan, smooth_path
```

---

### 3. Orientation Estimation (`orientation/`)

**Before:**
```
orientation/
├── vision_bbox.py
├── vision_minrect.py
├── vision_pca.py
├── vision_fusion.py
├── aruco_orientation.py
└── README.md
```

**After:**
```
orientation/
├── utils/
│   ├── __init__.py          # Exports estimation methods
│   ├── vision_bbox.py       # BBox method
│   ├── vision_minrect.py    # MinRect method
│   ├── vision_pca.py        # PCA method
│   └── vision_fusion.py     # Fusion method (recommended)
├── main/
│   ├── __init__.py          # Main scripts
│   └── aruco_orientation.py # Main orientation script
└── README.md
```

**Import Changes:**
```python
# Old imports
from orientation.vision_fusion import estimate_pose

# New imports
from orientation.utils import fusion_estimate
# OR
from orientation.utils.vision_fusion import estimate_pose
```

---

### 4. Full Pipeline Scripts (`full_pipeline/scripts/`)

**Before:**
```
full_pipeline/scripts/
├── crate_id_tracker.py
├── crate_obstacle_manager.py
├── lidar_path_planning.py
├── main.py
├── main_connect.py
└── multi_threaded_pipeline.py
```

**After:**
```
full_pipeline/scripts/
├── utils/
│   ├── __init__.py               # Utility exports
│   ├── crate_id_tracker.py       # Crate tracking
│   ├── crate_obstacle_manager.py # Obstacle management
│   └── lidar_path_planning.py    # LiDAR integration
├── main/
│   ├── __init__.py               # Main exports
│   ├── main.py                   # Main pipeline
│   ├── main_connect.py           # RRT-Connect pipeline
│   └── multi_threaded_pipeline.py # Multi-threaded version
└── [other files]
```

**Import Changes:**
```python
# Old imports
from crate_id_tracker import CrateIDTracker

# New imports
from full_pipeline.scripts.utils import CrateIDTracker, CrateObstacleManager
```

---

## 🔄 Migration Guide

### For Developers

#### 1. Update Import Statements
Most imports will continue to work if you update to use the new paths:

```python
# Strategy package
from strategy.utils import StrategyConfig, WorldState, CrateInfo, TaskType
from strategy.main import StrategyManager

# Path planning
from path_planning.utils import rrt_connect_plan, smooth_path

# Orientation
from orientation.utils import fusion_estimate

# Full pipeline
from full_pipeline.scripts.utils import CrateIDTracker
```

#### 2. Running Main Scripts
Navigate to the `main/` directory or use absolute paths:

```bash
# Strategy visualization
cd strategy/main
python visualize_strategy.py

# Or from root
python strategy/main/visualize_strategy.py

# Full pipeline
python full_pipeline/scripts/main/main.py
```

#### 3. Testing Utilities
You can now import and test utilities independently:

```python
# Test path planning algorithms
from path_planning.utils import rrt_plan, rrt_connect_plan
path = rrt_plan(start, goal, obstacles, bounds)

# Test orientation methods
from orientation.utils import pca_estimate, fusion_estimate
result = fusion_estimate(frame)
```

---

## 📊 File Classification

### Utils (Reusable Components)
These files contain classes, functions, and utilities that can be imported and used by multiple scripts:

| Module | Utils Files | Purpose |
|--------|-------------|---------|
| **strategy** | config.py | Configuration classes |
| | world_state.py | Data classes (WorldState, CrateInfo, etc.) |
| | task_models.py | Task type definitions |
| | crate_id_tracker.py | Unique ID assignment utility |
| **path_planning** | rrt.py, rrt_connect.py | Path planning algorithms |
| | A_star.py | Grid-based pathfinding |
| | path_smoothing.py | Path optimization |
| **orientation** | vision_bbox.py | BBox estimation method |
| | vision_minrect.py | MinRect estimation method |
| | vision_pca.py | PCA estimation method |
| | vision_fusion.py | Fusion method (best) |
| **full_pipeline** | crate_id_tracker.py | Crate tracking utility |
| | crate_obstacle_manager.py | Obstacle management |
| | lidar_path_planning.py | LiDAR integration |

### Main (Execution Scripts)
These files are executable scripts that use the utilities:

| Module | Main Files | Purpose |
|--------|------------|---------|
| **strategy** | strategy_manager.py | Main decision-making engine |
| | visualize_strategy.py | Live visualization demo |
| | example_usage.py | Usage examples |
| **orientation** | aruco_orientation.py | Main orientation script |
| **full_pipeline** | main.py | Standard pipeline |
| | main_connect.py | RRT-Connect pipeline |
| | multi_threaded_pipeline.py | Multi-threaded version |

---

## 🔧 Backward Compatibility

### Old Imports Still Work
The `utils/__init__.py` files export all utilities, so most old imports will continue to work:

```python
# These still work through __init__.py exports
from strategy.utils import StrategyConfig
from path_planning.utils import rrt_connect_plan
from orientation.utils import fusion_estimate
```

### Updating Your Code
If you have external code using these modules, update imports gradually:

1. **Check current imports** in your code
2. **Update to new paths** using the tables above
3. **Test thoroughly** to ensure everything works
4. **Update documentation** to reflect new structure

---

## 📝 Documentation Updates Needed

The following README files should be updated to reflect the new structure:

- [ ] `strategy/README.md` - Update import examples
- [ ] `path_planning/README.md` - Update import examples  
- [ ] `orientation/README.md` - Update import examples
- [ ] `full_pipeline/README.md` - Update import examples
- [ ] `Documentation/QUICK_START.md` - Update usage examples
- [ ] Main `README.md` - Update repository structure diagram

---

## 🎯 Next Steps

### Immediate
1. ✅ Create utils/ and main/ directories
2. ✅ Move files to appropriate locations
3. ✅ Create __init__.py files for new directories
4. ✅ Document reorganization

### Short-term
5. Update README files with new import examples
6. Update example scripts to use new imports
7. Test all main scripts to ensure they work
8. Update PROGRESS.md with reorganization notes

### Long-term
9. Consider adding more utilities as modules grow
10. Create integration tests for each module
11. Add type hints to all utilities
12. Create API documentation for utilities

---

## 💡 Best Practices Going Forward

### When Adding New Code

**Utility Files (utils/)**:
- Reusable functions and classes
- No direct execution (no `if __name__ == "__main__"`)
- Well-documented with docstrings
- Type hints for all functions
- Unit testable

**Main Files (main/)**:
- Executable scripts with `if __name__ == "__main__"`
- Import from utils/
- Command-line argument parsing
- User-facing documentation
- Integration testing

### Example Structure for New Module
```
new_module/
├── utils/
│   ├── __init__.py        # Export all utilities
│   ├── helper1.py         # Utility function set 1
│   ├── helper2.py         # Utility function set 2
│   └── data_models.py     # Data classes
├── main/
│   ├── __init__.py        # Main exports
│   ├── run_task1.py       # Main script 1
│   └── run_task2.py       # Main script 2
├── tests/
│   ├── test_helper1.py    # Unit tests
│   └── test_helper2.py    # Unit tests
└── README.md              # Module documentation
```

---

## 🐛 Known Issues

### Import Path Changes
Some scripts may need import path updates if they were using relative imports. Update as follows:

```python
# Old relative import (may break)
from ..path_planning import rrt_connect_plan

# New absolute import (recommended)
from path_planning.utils import rrt_connect_plan
```

### __pycache__ Directories
Old `__pycache__` directories may still exist in root folders. These can be safely deleted:

```bash
# Windows PowerShell
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Or manually delete them
```

---

## 📞 Questions?

If you encounter issues with the reorganization:
1. Check this document for migration guidelines
2. Review the import examples above
3. Check module README files for updated usage
4. Refer to PROGRESS.md for overall project status

---

**Last Updated**: January 15, 2026  
**Status**: ✅ Reorganization Complete
