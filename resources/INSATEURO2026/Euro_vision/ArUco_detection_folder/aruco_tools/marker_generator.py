"""
ArUco Marker Generator
Generates ArUco markers from a dictionary and saves them as images.
"""

import cv2
import numpy as np
import os


class MarkerGenerator:
    """Generate ArUco markers from a specific dictionary."""
    
    def __init__(self, dictionary_type=cv2.aruco.DICT_4X4_50, marker_size=200):
        """
        Initialize the marker generator.
        
        Args:
            dictionary_type: OpenCV ArUco dictionary type
            marker_size: Size of the marker in pixels
        """
        self.dictionary = cv2.aruco.getPredefinedDictionary(dictionary_type)
        self.marker_size = marker_size
        self.dictionary_name = self._get_dictionary_name(dictionary_type)
    
    def _get_dictionary_name(self, dict_type):
        """Get human-readable name for dictionary type."""
        dict_names = {
            cv2.aruco.DICT_4X4_50: "DICT_4X4_50",
            cv2.aruco.DICT_4X4_100: "DICT_4X4_100",
            cv2.aruco.DICT_4X4_250: "DICT_4X4_250",
            cv2.aruco.DICT_4X4_1000: "DICT_4X4_1000",
            cv2.aruco.DICT_5X5_50: "DICT_5X5_50",
            cv2.aruco.DICT_5X5_100: "DICT_5X5_100",
            cv2.aruco.DICT_5X5_250: "DICT_5X5_250",
            cv2.aruco.DICT_5X5_1000: "DICT_5X5_1000",
            cv2.aruco.DICT_6X6_50: "DICT_6X6_50",
            cv2.aruco.DICT_6X6_100: "DICT_6X6_100",
            cv2.aruco.DICT_6X6_250: "DICT_6X6_250",
            cv2.aruco.DICT_6X6_1000: "DICT_6X6_1000",
            cv2.aruco.DICT_7X7_50: "DICT_7X7_50",
            cv2.aruco.DICT_7X7_100: "DICT_7X7_100",
            cv2.aruco.DICT_7X7_250: "DICT_7X7_250",
            cv2.aruco.DICT_7X7_1000: "DICT_7X7_1000",
        }
        return dict_names.get(dict_type, "UNKNOWN")
    
    def generate_marker(self, marker_id, output_path=None, border_bits=1):
        """
        Generate a single ArUco marker.
        
        Args:
            marker_id: ID of the marker to generate
            output_path: Path to save the marker image (optional)
            border_bits: Number of border bits (default: 1)
        
        Returns:
            marker_image: Generated marker as numpy array
        """
        marker_image = cv2.aruco.generateImageMarker(
            self.dictionary, 
            marker_id, 
            self.marker_size,
            borderBits=border_bits
        )
        
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, marker_image)
            print(f"Marker ID {marker_id} saved to: {output_path}")
        
        return marker_image
    
    def generate_markers_batch(self, marker_ids, output_dir="markers", border_bits=1):
        """
        Generate multiple ArUco markers.
        
        Args:
            marker_ids: List of marker IDs to generate
            output_dir: Directory to save markers
            border_bits: Number of border bits (default: 1)
        
        Returns:
            List of generated marker images
        """
        os.makedirs(output_dir, exist_ok=True)
        markers = []
        
        for marker_id in marker_ids:
            output_path = os.path.join(
                output_dir, 
                f"marker_{self.dictionary_name}_id_{marker_id}.png"
            )
            marker = self.generate_marker(marker_id, output_path, border_bits)
            markers.append(marker)
        
        print(f"\nGenerated {len(markers)} markers in '{output_dir}' directory")
        print(f"Dictionary: {self.dictionary_name}")
        print(f"Marker size: {self.marker_size}x{self.marker_size} pixels")
        
        return markers
    
    def generate_marker_sheet(self, marker_ids, output_path, cols=4, spacing=20):
        """
        Generate a sheet with multiple markers for printing.
        
        Args:
            marker_ids: List of marker IDs to include
            output_path: Path to save the sheet
            cols: Number of columns in the sheet
            spacing: Spacing between markers in pixels
        """
        rows = (len(marker_ids) + cols - 1) // cols
        
        # Calculate sheet dimensions
        sheet_width = cols * self.marker_size + (cols + 1) * spacing
        sheet_height = rows * self.marker_size + (rows + 1) * spacing
        
        # Create white sheet
        sheet = np.ones((sheet_height, sheet_width), dtype=np.uint8) * 255
        
        # Place markers on sheet
        for idx, marker_id in enumerate(marker_ids):
            row = idx // cols
            col = idx % cols
            
            x = col * (self.marker_size + spacing) + spacing
            y = row * (self.marker_size + spacing) + spacing
            
            marker = self.generate_marker(marker_id)
            sheet[y:y+self.marker_size, x:x+self.marker_size] = marker
            
            # Add ID label below marker
            text = f"ID: {marker_id}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = x + (self.marker_size - text_size[0]) // 2
            text_y = y + self.marker_size + 15
            cv2.putText(sheet, text, (text_x, text_y), font, font_scale, 0, thickness)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, sheet)
        print(f"\nMarker sheet saved to: {output_path}")
        print(f"Sheet size: {sheet_width}x{sheet_height} pixels")
        print(f"Contains {len(marker_ids)} markers")
        
        return sheet


def main():
    """Example usage of the MarkerGenerator."""
    # Create generator with DICT_4X4_50 (suitable for Eurobot)
    generator = MarkerGenerator(
        dictionary_type=cv2.aruco.DICT_4X4_50,
        marker_size=200
    )
    
    # Generate map markers (IDs 20-23 - Eurobot 2026)
    print("=" * 60)
    print("Generating MAP markers (IDs 20-23 - Eurobot 2026)")
    print("=" * 60)
    generator.generate_markers_batch(
        marker_ids=[20, 21, 22, 23],
        output_dir="markers/map_markers"
    )
    
    # Generate caisse markers (IDs 36, 47, 41 - Eurobot 2026)
    print("\n" + "=" * 60)
    print("Generating CAISSE markers (IDs 36, 47, 41 - Eurobot 2026)")
    print("=" * 60)
    generator.generate_markers_batch(
        marker_ids=[36, 47, 41],  # blue, yellow, black
        output_dir="markers/caisse_markers"
    )
    
    # Generate enemy markers (IDs 30-35)
    print("\n" + "=" * 60)
    print("Generating ENEMY markers (IDs 30-35)")
    print("=" * 60)
    generator.generate_markers_batch(
        marker_ids=list(range(30, 36)),
        output_dir="markers/enemy_markers"
    )
    
    # Generate printable sheets
    print("\n" + "=" * 60)
    print("Generating printable sheets")
    print("=" * 60)
    
    generator.generate_marker_sheet(
        marker_ids=[20, 21, 22, 23],
        output_path="markers/map_markers_sheet.png",
        cols=2
    )
    
    generator.generate_marker_sheet(
        marker_ids=[36, 47, 41],  # Caisse markers
        output_path="markers/caisse_markers_sheet.png",
        cols=4
    )
    
    generator.generate_marker_sheet(
        marker_ids=list(range(30, 36)),
        output_path="markers/enemy_markers_sheet.png",
        cols=3
    )
    
    print("\n" + "=" * 60)
    print("All markers generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
