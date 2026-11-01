"""
ArUco Marker Generator
Generates ArUco markers with specific IDs for testing caisse detection.
"""

import cv2
import numpy as np
import argparse
from pathlib import Path


def generate_aruco_marker(marker_id: int, size_pixels: int = 500, 
                          dictionary_name: str = 'DICT_4X4_50',
                          output_dir: str = 'markers'):
    """
    Generate and save an ArUco marker with specific ID.
    
    Args:
        marker_id: The ID of the marker to generate
        size_pixels: Size of the marker image in pixels
        dictionary_name: ArUco dictionary name
        output_dir: Directory to save markers
    """
    # Get ArUco dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(
        getattr(cv2.aruco, dictionary_name)
    )
    
    # Generate marker
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size_pixels)
    
    # Add border for easier printing
    border_size = 50
    bordered_image = cv2.copyMakeBorder(
        marker_image, 
        border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, 
        value=255
    )
    
    # Add text label
    label = f"ArUco ID: {marker_id} ({dictionary_name})"
    cv2.putText(bordered_image, label, (border_size, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 2)
    
    # Add size information (assuming 40mm as per config)
    size_label = f"Print size: 40mm x 40mm"
    cv2.putText(bordered_image, size_label, (border_size, bordered_image.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save marker
    filename = output_path / f"aruco_{dictionary_name}_id_{marker_id}.png"
    cv2.imwrite(str(filename), bordered_image)
    
    print(f"✓ Generated marker ID {marker_id}: {filename}")
    return filename


def generate_caisse_markers():
    """Generate all markers needed for caisse detection."""
    print("=== Generating ArUco Markers for Caisses de Noisettes ===\n")
    
    markers = [
        (36, "BLUE team marker"),
        (47, "YELLOW team marker"),
        (41, "BLACK rotten box marker")
    ]
    
    for marker_id, description in markers:
        print(f"Generating {description}...")
        generate_aruco_marker(marker_id, size_pixels=500)
    
    print("\n=== Marker Generation Complete ===")
    print("Print the markers at 40mm x 40mm size")
    print("Attach them to the vinyl bands on the caisses")


def main():
    parser = argparse.ArgumentParser(description='Generate ArUco markers for caisse detection')
    parser.add_argument('--ids', type=int, nargs='+', 
                       default=[36, 47, 41],
                       help='Marker IDs to generate')
    parser.add_argument('--size', type=int, default=500,
                       help='Marker size in pixels')
    parser.add_argument('--dict', type=str, default='DICT_4X4_50',
                       help='ArUco dictionary name')
    parser.add_argument('--output', type=str, default='markers',
                       help='Output directory')
    parser.add_argument('--all', action='store_true',
                       help='Generate all caisse markers (36, 47, 41)')
    
    args = parser.parse_args()
    
    if args.all:
        generate_caisse_markers()
    else:
        print(f"Generating markers: {args.ids}")
        for marker_id in args.ids:
            generate_aruco_marker(marker_id, args.size, args.dict, args.output)
        print("\nDone!")


if __name__ == '__main__':
    main()
