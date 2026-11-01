"""
Example: Generate ArUco Markers
This script demonstrates how to generate ArUco markers for the Eurobot project.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aruco_tools import MarkerGenerator
import cv2


def main():
    print("=" * 70)
    print("ArUco Marker Generator for Eurobot 2026")
    print("=" * 70)
    
    # Create marker generator
    # Using DICT_4X4_50 which is suitable for the project
    generator = MarkerGenerator(
        dictionary_type=cv2.aruco.DICT_4X4_50,
        marker_size=200  # 200x200 pixels
    )
    
    # Generate map markers (corner markers for global coordinate system)
    print("\n[1/4] Generating MAP markers (IDs 20-23 - Eurobot 2026)...")
    generator.generate_markers_batch(
        marker_ids=[20, 21, 22, 23],
        output_dir="markers/map_markers"
    )
    
    # Generate caisse markers (wooden box markers - Eurobot 2026 IDs)
    print("\n[2/4] Generating CAISSE markers (IDs 36, 47, 41)...")
    generator.generate_markers_batch(
        marker_ids=[36, 47, 41],  # blue, yellow, black
        output_dir="markers/caisse_markers"
    )
    
    # Generate enemy robot markers
    print("\n[3/4] Generating ENEMY markers (IDs 30-35)...")
    generator.generate_markers_batch(
        marker_ids=list(range(30, 36)),
        output_dir="markers/enemy_markers"
    )
    
    # Generate printable sheets
    print("\n[4/4] Generating printable sheets...")
    
    # Map markers sheet (2x2 grid - Eurobot 2026)
    generator.generate_marker_sheet(
        marker_ids=[20, 21, 22, 23],
        output_path="markers/printable_map_markers.png",
        cols=2,
        spacing=30
    )
    
    # Caisse markers sheet (4 columns)
    generator.generate_marker_sheet(
        marker_ids=list(range(10, 21)),
        output_path="markers/printable_caisse_markers.png",
        cols=4,
        spacing=30
    )
    
    # Enemy markers sheet (3 columns)
    generator.generate_marker_sheet(
        marker_ids=list(range(30, 36)),
        output_path="markers/printable_enemy_markers.png",
        cols=3,
        spacing=30
    )
    
    print("\n" + "=" * 70)
    print("✓ All markers generated successfully!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  • Individual markers: markers/{map,caisse,enemy}_markers/")
    print("  • Printable sheets: markers/printable_*.png")
    print("\nYou can now print the sheets and use them for detection.")
    print("=" * 70)


if __name__ == "__main__":
    main()
