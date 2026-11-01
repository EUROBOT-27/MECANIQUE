#!/usr/bin/env python3
"""
Generate a chessboard calibration pattern for camera calibration.
This script creates a PDF file with a chessboard pattern that can be printed.
"""

import cv2
import numpy as np

# Chessboard parameters
CHESSBOARD_SIZE = (9, 6)  # Internal corners (width, height)
SQUARE_SIZE_MM = 25  # Size of each square in millimeters

def generate_chessboard_pattern(filename="chessboard_pattern.png", 
                                 board_size=CHESSBOARD_SIZE,
                                 square_size_px=100):
    """
    Generate a chessboard pattern image.
    
    Args:
        filename: Output filename for the pattern
        board_size: Tuple of (width, height) for internal corners
        square_size_px: Size of each square in pixels
    """
    # Add 1 to get the number of squares (internal corners + 1)
    width_squares = board_size[0] + 1
    height_squares = board_size[1] + 1
    
    # Calculate image dimensions
    img_width = width_squares * square_size_px
    img_height = height_squares * square_size_px
    
    # Create white image
    img = np.ones((img_height, img_width), dtype=np.uint8) * 255
    
    # Draw black squares in checkerboard pattern
    for i in range(height_squares):
        for j in range(width_squares):
            if (i + j) % 2 == 1:  # Alternating pattern
                x1 = j * square_size_px
                y1 = i * square_size_px
                x2 = x1 + square_size_px
                y2 = y1 + square_size_px
                img[y1:y2, x1:x2] = 0
    
    # Add border
    border_size = 50
    img_with_border = np.ones((img_height + 2*border_size, img_width + 2*border_size), 
                               dtype=np.uint8) * 255
    img_with_border[border_size:border_size+img_height, 
                    border_size:border_size+img_width] = img
    
    # Add text information
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"Chessboard: {board_size[0]}x{board_size[1]} corners, {SQUARE_SIZE_MM}mm squares"
    cv2.putText(img_with_border, text, (10, 30), font, 0.7, 0, 2)
    
    # Save the image
    cv2.imwrite(filename, img_with_border)
    print(f"Chessboard pattern saved to: {filename}")
    print(f"Pattern size: {board_size[0]}x{board_size[1]} internal corners")
    print(f"Square size: {SQUARE_SIZE_MM}mm (print at actual size)")
    print(f"Image dimensions: {img_with_border.shape[1]}x{img_with_border.shape[0]} pixels")
    print("\nInstructions:")
    print("1. Print this pattern on A4 or larger paper")
    print("2. Glue it to a flat, rigid surface (cardboard or wood)")
    print("3. Ensure the pattern is completely flat")
    print("4. Measure the printed square size and update SQUARE_SIZE_MM if needed")

if __name__ == "__main__":
    output_file = "calibration/chessboard_pattern.png"
    generate_chessboard_pattern(output_file)
    print(f"\n✓ Pattern generation complete!")
