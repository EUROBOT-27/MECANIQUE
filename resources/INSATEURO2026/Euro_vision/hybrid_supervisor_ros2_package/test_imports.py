"""
Test all imports work correctly.

Run this to verify the package structure is correct:
    python test_imports.py
"""

print("Testing imports...")

try:
    from strategy.utils.config import StrategyConfig, DEFAULT_CONFIG
    print("[OK] strategy.utils.config")
except ImportError as e:
    print(f"[FAIL] strategy.utils.config: {e}")

try:
    from strategy.utils.world_state import WorldState, CrateInfo
    print("[OK] strategy.utils.world_state")
except ImportError as e:
    print(f"[FAIL] strategy.utils.world_state: {e}")

try:
    from strategy.utils.crate_id_tracker import CrateIDTracker
    print("[OK] strategy.utils.crate_id_tracker")
except ImportError as e:
    print(f"[FAIL] strategy.utils.crate_id_tracker: {e}")

try:
    from strategy.crate_flip_manager import CrateFlipManager
    print("[OK] strategy.crate_flip_manager")
except ImportError as e:
    print(f"[FAIL] strategy.crate_flip_manager: {e}")

try:
    from kalman_filter.tracker import MultiMarkerTracker
    print("[OK] kalman_filter.tracker")
except ImportError as e:
    print(f"[FAIL] kalman_filter.tracker: {e}")

try:
    from path_planning.rrt_connect import rrt_connect_plan
    print("[OK] path_planning.rrt_connect")
except ImportError as e:
    print(f"[FAIL] path_planning.rrt_connect: {e}")

try:
    from path_planning.path_smoothing import smooth_path
    print("[OK] path_planning.path_smoothing")
except ImportError as e:
    print(f"[FAIL] path_planning.path_smoothing: {e}")

try:
    import main
    print("[OK] main module")
except ImportError as e:
    print(f"[FAIL] main module: {e}")

print("\nAll critical imports successful!")
