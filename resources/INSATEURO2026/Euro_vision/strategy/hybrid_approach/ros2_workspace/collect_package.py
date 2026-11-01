"""
Hybrid Approach Package Collector
==================================

Automatically copies all required files for the hybrid approach ROS2 package.

Usage:
    python collect_package.py [--output OUTPUT_DIR]

This script:
1. Creates a clean package directory structure
2. Copies all dependencies with correct folder hierarchy
3. Creates __init__.py files for Python packages
4. Generates a README with integration instructions

Output structure matches ROS2 package requirements.
"""

import os
import shutil
from pathlib import Path
import argparse


# Base directory (Euro_vision root)
BASE_DIR = Path(__file__).parent.parent.parent.parent

# Files to collect (relative to BASE_DIR)
FILES_TO_COLLECT = {
    # Main ROS2 supervisor
    "main.py": "strategy/hybrid_approach/ros2_workspace/main.py",
    
    # Strategy modules
    "strategy/crate_flip_manager.py": "strategy/hybrid_approach/src/crate_flip_manager.py",
    "strategy/utils/__init__.py": "strategy/utils/__init__.py",
    "strategy/utils/config.py": "strategy/utils/config.py",
    "strategy/utils/world_state.py": "strategy/utils/world_state.py",
    "strategy/utils/crate_id_tracker.py": "strategy/utils/crate_id_tracker.py",
    "strategy/utils/task_models.py": "strategy/utils/task_models.py",  # Required by __init__.py
    
    # Kalman filter
    "kalman_filter/__init__.py": "kalman_filter/src/kalman_filter/__init__.py",
    "kalman_filter/tracker.py": "kalman_filter/src/kalman_filter/tracker.py",
    
    # Path planning
    "path_planning/__init__.py": "path_planning/utils/__init__.py",
    "path_planning/rrt_connect.py": "path_planning/utils/rrt_connect.py",
    "path_planning/path_smoothing.py": "path_planning/utils/path_smoothing.py",
    
    # Documentation
    "README.md": "strategy/hybrid_approach/README.md",
    "requirements.txt": "strategy/hybrid_approach/requirements.txt",
}

# Additional docs to copy
DOCS_TO_COPY = {
    "PACKAGE_CONTENTS.md": "strategy/hybrid_approach/ros2_workspace/PACKAGE_CONTENTS.md",
}


def create_package(output_dir: Path):
    """Create the complete package structure."""
    
    print(f"\n{'='*60}")
    print("🚀 Hybrid Approach Package Collector")
    print(f"{'='*60}\n")
    
    # Create output directory
    output_dir = Path(output_dir)
    if output_dir.exists():
        response = input(f"⚠️  Directory '{output_dir}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled.")
            return
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(parents=True)
    print(f"✅ Created output directory: {output_dir}\n")
    
    # Copy files
    print("📁 Copying files...\n")
    copied_count = 0
    failed_files = []
    
    for dest_path, source_path in FILES_TO_COLLECT.items():
        source = BASE_DIR / source_path
        dest = output_dir / dest_path
        
        # Create parent directories
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        if source.exists():
            shutil.copy2(source, dest)
            print(f"   ✓ {source_path} → {dest_path}")
            copied_count += 1
        else:
            print(f"   ✗ MISSING: {source_path}")
            failed_files.append(source_path)
    
    # Copy documentation
    print("\n📄 Copying documentation...\n")
    for dest_path, source_path in DOCS_TO_COPY.items():
        source = BASE_DIR / source_path
        dest = output_dir / dest_path
        
        if source.exists():
            shutil.copy2(source, dest)
            print(f"   ✓ {source_path} → {dest_path}")
            copied_count += 1
        else:
            print(f"   ✗ MISSING: {source_path}")
            failed_files.append(source_path)
    
    # Create __init__.py for root package
    root_init = output_dir / "__init__.py"
    root_init.write_text('"""Hybrid Supervisor ROS2 Package"""\n')
    print(f"\n   ✓ Created {root_init.relative_to(output_dir)}")
    
    # Create a simple test script
    test_script = output_dir / "test_imports.py"
    with open(test_script, 'w', encoding='utf-8') as f:
        f.write('''"""
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

print("\\nAll critical imports successful!")
''')
    print(f"   ✓ Created test_imports.py")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"✅ Copied: {copied_count} files")
    if failed_files:
        print(f"❌ Failed: {len(failed_files)} files")
        print("\nMissing files:")
        for f in failed_files:
            print(f"   - {f}")
    else:
        print(f"✅ All files collected successfully!")
    
    print(f"\n📦 Package location: {output_dir.absolute()}")
    print(f"\n🔧 Next steps:")
    print(f"   1. cd {output_dir}")
    print(f"   2. python test_imports.py  # Verify imports")
    print(f"   3. python main.py --test   # Test the supervisor")
    print(f"   4. Read PACKAGE_CONTENTS.md for ROS2 integration")
    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Collect all files needed for hybrid approach ROS2 package"
    )
    parser.add_argument(
        '--output',
        '-o',
        default='hybrid_supervisor_package',
        help='Output directory name (default: hybrid_supervisor_package)'
    )
    args = parser.parse_args()
    
    create_package(args.output)


if __name__ == "__main__":
    main()
