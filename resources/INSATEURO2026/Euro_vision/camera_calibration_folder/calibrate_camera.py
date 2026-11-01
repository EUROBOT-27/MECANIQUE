#!/usr/bin/env python3
"""
Camera Calibration Script for Eurobot 2026 Vision System.

This script performs intrinsic camera calibration using a chessboard pattern.
It computes the camera matrix (K) and distortion coefficients (D) and saves
them to a JSON file for later use in ArUco marker detection and pose estimation.

Usage:
    python calibrate_camera.py --images calibration_images/*.jpg
    python calibrate_camera.py --camera 0  # Live calibration from camera
"""
#Just added a comment to keep the commit history updated and not to lose my streak :D 
import cv2
import numpy as np
import json
import glob
import argparse
import os
from datetime import datetime

# Chessboard parameters (must match the printed pattern)
CHESSBOARD_SIZE = (9, 6)  # Internal corners (width, height)
SQUARE_SIZE_MM = 25.0  # Size of each square in millimeters

class CameraCalibrator:
    def __init__(self, chessboard_size=CHESSBOARD_SIZE, square_size=SQUARE_SIZE_MM):
        """
        Initialize camera calibrator.
        
        Args:
            chessboard_size: Tuple of (width, height) for internal corners
            square_size: Size of each square in millimeters
        """
        self.chessboard_size = chessboard_size
        self.square_size = square_size
        
        # Prepare object points (3D points in real world space)
        self.objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:chessboard_size[0], 
                                      0:chessboard_size[1]].T.reshape(-1, 2)
        self.objp *= square_size
        
        # Arrays to store object points and image points
        self.objpoints = []  # 3D points in real world space
        self.imgpoints = []  # 2D points in image plane
        self.image_size = None
        
    def find_chessboard_corners(self, image):
        """
        Find chessboard corners in an image.
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            tuple: (success, corners, gray_image)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
        
        if ret:
            # Refine corner positions for better accuracy
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
        return ret, corners, gray
    
    def add_calibration_image(self, image, show_corners=False):
        """
        Process a calibration image and add it to the calibration dataset.
        
        Args:
            image: Input image
            show_corners: Whether to display detected corners
            
        Returns:
            bool: True if corners were found, False otherwise
        """
        ret, corners, gray = self.find_chessboard_corners(image)
        
        if ret:
            self.objpoints.append(self.objp)
            self.imgpoints.append(corners)
            
            if self.image_size is None:
                self.image_size = gray.shape[::-1]
            
            if show_corners:
                img_with_corners = cv2.drawChessboardCorners(
                    image.copy(), self.chessboard_size, corners, ret
                )
                cv2.imshow('Chessboard Corners', img_with_corners)
                cv2.waitKey(500)
            
            return True
        
        return False
    
    def calibrate(self):
        """
        Perform camera calibration.
        
        Returns:
            dict: Calibration results containing camera matrix, distortion coefficients,
                  rotation vectors, translation vectors, and reprojection error
        """
        if len(self.objpoints) < 3:
            raise ValueError(f"Need at least 3 valid images for calibration. Got {len(self.objpoints)}")
        
        print(f"\nPerforming calibration with {len(self.objpoints)} images...")
        print("This may take 10-30 seconds depending on image count and resolution...")
        
        # Calibrate camera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints, self.imgpoints, self.image_size, None, None
        )
        
        print("Calibration complete! Computing reprojection error...")
        
        # Calculate reprojection error
        mean_error = 0
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(
                self.objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
            )
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error
        
        mean_error /= len(self.objpoints)
        
        results = {
            'camera_matrix': camera_matrix,
            'distortion_coefficients': dist_coeffs,
            'rotation_vectors': rvecs,
            'translation_vectors': tvecs,
            'reprojection_error': mean_error,
            'num_images': len(self.objpoints),
            'image_size': self.image_size
        }
        
        return results
    
    def save_calibration(self, results, filename='calibration/zghibi_camera_calibration.json'):
        """
        Save calibration results to a JSON file.
        
        Args:
            results: Calibration results dictionary
            filename: Output filename
        """
        # Convert numpy arrays to lists for JSON serialization
        calibration_data = {
            'calibration_date': datetime.now().isoformat(),
            'camera_matrix': results['camera_matrix'].tolist(),
            'distortion_coefficients': results['distortion_coefficients'].tolist(),
            'reprojection_error': float(results['reprojection_error']),
            'num_calibration_images': results['num_images'],
            'image_size': list(results['image_size']),
            'chessboard_size': list(self.chessboard_size),
            'square_size_mm': float(self.square_size)
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save to JSON
        with open(filename, 'w') as f:
            json.dump(calibration_data, f, indent=2)
        
        print(f"\n✓ Calibration data saved to: {filename}")
        
        return calibration_data

def calibrate_from_images(image_paths, output_file='calibration/camera_calibration.json'):
    """
    Calibrate camera from a set of images.
    
    Args:
        image_paths: List of image file paths or glob pattern
        output_file: Output JSON file path
    """
    # Expand glob pattern if needed
    if isinstance(image_paths, str):
        image_paths = glob.glob(image_paths)
    
    if not image_paths:
        raise ValueError("No images found")
    
    print(f"Found {len(image_paths)} images")
    
    # Create calibrator
    calibrator = CameraCalibrator()
    
    # Process images
    successful_images = 0
    for i, img_path in enumerate(image_paths):
        print(f"Processing image {i+1}/{len(image_paths)}: {img_path}")
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"  ✗ Failed to load image")
            continue
        
        if calibrator.add_calibration_image(img):
            print(f"  ✓ Corners found")
            successful_images += 1
        else:
            print(f"  ✗ Corners not found")
    
    print(f"\nSuccessfully processed {successful_images}/{len(image_paths)} images")
    
    # Perform calibration
    results = calibrator.calibrate()
    
    # Print results
    print_calibration_results(results)
    
    # Save results
    calibrator.save_calibration(results, output_file)
    
    cv2.destroyAllWindows()

def calibrate_from_camera(camera_id=1, num_images=20, output_file='calibration/zghibi_camera_calibration.json'):
    """
    Calibrate camera by capturing images from a live camera feed.
    
    Args:
        camera_id: Camera device ID
        num_images: Number of images to capture for calibration
        output_file: Output JSON file path
    """
    import time
    
    # Try CAP_MSMF first (better for virtual cameras like Camo Studio), fallback to CAP_DSHOW
    print(f"Opening camera {camera_id} with MSMF backend...")
    cap = cv2.VideoCapture(camera_id, cv2.CAP_MSMF)
    
    if not cap.isOpened():
        print("MSMF failed, trying DSHOW backend...")
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open camera {camera_id}. Try: python test_camera.py to find available cameras")
    
    # Set resolution explicitly (virtual cameras often need this)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Aggressive buffer clearing for virtual cameras (Camo Studio, OBS, etc.)
    print("Warming up camera and clearing buffer...")
    for i in range(30):  # Increased from 10 to 30
        ret, frame = cap.read()
        if i % 10 == 0:
            print(f"  Buffer clear {i}/30...")
    
    time.sleep(1.0)  # Increased warmup time
    
    # Verify we're getting actual frames
    ret, test_frame = cap.read()
    if ret and test_frame is not None:
        mean_val = test_frame.mean()
        print(f"Camera ready! Frame size: {test_frame.shape}, Mean pixel value: {mean_val:.2f}")
        if mean_val < 1.0:
            print("⚠ WARNING: Camera feed appears black! Check Camo Studio settings.")
    else:
        raise ValueError("Camera opened but cannot read frames!")
    
    print(f"\nLive calibration mode")
    print(f"Target: {num_images} images")
    print("Press SPACE to capture an image, ESC to finish\n")
    
    calibrator = CameraCalibrator()
    captured = 0
    
    while captured < num_images:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Warning: Failed to read frame from camera")
            continue
        
        # Check if frame is black (common DroidCam issue)
        if frame.mean() < 1.0:
            print("Warning: Camera feed appears black. Check DroidCam connection.")
            cv2.imshow('Camera Calibration', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            continue
        
        # Try to find chessboard in current frame
        ret_chess, corners, _ = calibrator.find_chessboard_corners(frame)
        
        # Draw corners if found
        display_frame = frame.copy()
        if ret_chess:
            cv2.drawChessboardCorners(display_frame, calibrator.chessboard_size, corners, ret_chess)
            cv2.putText(display_frame, "Chessboard detected - Press SPACE to capture", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame, "Position chessboard in view", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.putText(display_frame, f"Captured: {captured}/{num_images}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Camera Calibration', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32 and ret_chess:  # SPACE
            if calibrator.add_calibration_image(frame):
                captured += 1
                print(f"✓ Captured image {captured}/{num_images}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    if captured < 3:
        raise ValueError(f"Need at least 3 valid images for calibration. Got {captured}")
    
    # Perform calibration
    results = calibrator.calibrate()
    
    # Print results
    print_calibration_results(results)
    
    # Save results
    calibrator.save_calibration(results, output_file)

def print_calibration_results(results):
    """Print calibration results in a readable format."""
    print("\n" + "="*60)
    print("CALIBRATION RESULTS")
    print("="*60)
    print(f"\nNumber of images used: {results['num_images']}")
    print(f"Image size: {results['image_size']}")
    print(f"\nReprojection error: {results['reprojection_error']:.4f} pixels")
    
    print("\nCamera Matrix (K):")
    print(results['camera_matrix'])
    
    print("\nDistortion Coefficients (D):")
    print(results['distortion_coefficients'].ravel())
    
    # Extract focal lengths and principal point
    fx = results['camera_matrix'][0, 0]
    fy = results['camera_matrix'][1, 1]
    cx = results['camera_matrix'][0, 2]
    cy = results['camera_matrix'][1, 2]
    
    print(f"\nFocal lengths: fx={fx:.2f}, fy={fy:.2f}")
    print(f"Principal point: cx={cx:.2f}, cy={cy:.2f}")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Camera calibration using chessboard pattern',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calibrate from image files
  python calibrate_camera.py --images "calibration_images/*.jpg"
  
  # Calibrate from live camera (camera ID 0)
  python calibrate_camera.py --camera 0
  
  # Calibrate from live camera with 25 images
  python calibrate_camera.py --camera 0 --num-images 25
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--images', type=str, help='Path to calibration images (supports wildcards)')
    group.add_argument('--camera', type=int, help='Camera device ID for live calibration')
    
    parser.add_argument('--num-images', type=int, default=40,
                       help='Number of images to capture in live mode (default: 30)')
    parser.add_argument('--output', type=str, default='calibration/camera_calibration.json',
                       help='Output JSON file path (default: calibration/camera_calibration.json)')
    
    args = parser.parse_args()
    
    try:
        if args.images:
            calibrate_from_images(args.images, args.output)
        else:
            calibrate_from_camera(args.camera, args.num_images, args.output)
        
        print("\n✓ Calibration complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Camera Calibration Script for Eurobot 2026 Vision System.
This script performs intrinsic camera calibration using a chessboard pattern.
It computes the camera matrix (K) and distortion coefficients (D) and saves
them to a JSON file for later use in ArUco marker detection and pose estimation.
Usage:
    python calibrate_camera.py --images calibration_images/*.jpg
    python calibrate_camera.py --camera 0  # Live calibration from camera
"""
