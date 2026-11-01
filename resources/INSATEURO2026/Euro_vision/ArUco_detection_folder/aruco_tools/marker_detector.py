"""
ArUco Marker Detector
Detects ArUco markers in images/video and estimates their pose.
"""

import cv2
import numpy as np


class MarkerDetector:
    """Detect ArUco markers and estimate their pose."""
    
    def __init__(self, dictionary_type=cv2.aruco.DICT_4X4_50, 
                 camera_matrix=None, dist_coeffs=None, marker_length=0.05):
        """
        Initialize the marker detector.
        
        Args:
            dictionary_type: OpenCV ArUco dictionary type
            camera_matrix: Camera intrinsic matrix (3x3)
            dist_coeffs: Camera distortion coefficients
            marker_length: Physical size of marker in meters (default: 0.05m = 5cm)
        """
        self.dictionary = cv2.aruco.getPredefinedDictionary(dictionary_type)
        self.parameters = cv2.aruco.DetectorParameters()
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.marker_length = marker_length
        
        # Use default camera parameters if none provided
        if self.camera_matrix is None:
            self.camera_matrix = self._default_camera_matrix()
        if self.dist_coeffs is None:
            self.dist_coeffs = np.zeros((5, 1))
    
    def _default_camera_matrix(self, image_shape=(640, 480)):
        """Generate default camera matrix (for testing without calibration)."""
        focal_length = max(image_shape)
        center = (image_shape[0] / 2, image_shape[1] / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float32)
        return camera_matrix
    
    def detect_markers(self, image):
        """
        Detect ArUco markers in an image.
        
        Args:
            image: Input image (BGR or grayscale)
        
        Returns:
            corners: List of marker corners
            ids: List of marker IDs
            rejected: List of rejected candidates
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray,
            self.dictionary,
            parameters=self.parameters
        )
        
        return corners, ids, rejected
    
    def estimate_pose(self, corners):
        """
        Estimate pose (rotation and translation) of detected markers.
        
        Args:
            corners: Marker corners from detection
        
        Returns:
            rvecs: Rotation vectors
            tvecs: Translation vectors
        """
        if len(corners) == 0:
            return None, None
        
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners,
            self.marker_length,
            self.camera_matrix,
            self.dist_coeffs
        )
        
        return rvecs, tvecs
    
    def draw_detected_markers(self, image, corners, ids, border_color=(0, 255, 0), show_distance=False, pose_info=None):
        """
        Draw bounding boxes and IDs on detected markers.
        
        Args:
            image: Input image
            corners: Marker corners
            ids: Marker IDs
            border_color: Color for drawing (BGR format)
            show_distance: Whether to show distance information
            pose_info: Pose information for distance display
        
        Returns:
            image_with_markers: Image with drawn markers
        """
        image_copy = image.copy()
        
        if ids is not None and len(ids) > 0:
            # Draw marker boundaries
            cv2.aruco.drawDetectedMarkers(image_copy, corners, ids, border_color)
            
            # Add additional information
            for i, marker_id in enumerate(ids):
                # Get marker corners
                corner = corners[i][0]
                
                # Calculate center
                center_x = int(np.mean(corner[:, 0]))
                center_y = int(np.mean(corner[:, 1]))
                
                # Prepare text lines
                text_lines = [f"ID: {marker_id[0]}"]
                
                # Add distance information if available
                if show_distance and pose_info and i < len(pose_info):
                    info = pose_info[i]
                    text_lines.append(f"Cal: {info['distance_calibrated_mm']:.0f}mm")
                    if 'distance_uncalibrated_size_mm' in info:
                        text_lines.append(f"Est: {info['distance_uncalibrated_size_mm']:.0f}mm")
                
                # Draw text with background
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                thickness = 2
                line_height = 25
                
                # Calculate total text area
                max_width = 0
                for text in text_lines:
                    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                    max_width = max(max_width, text_size[0])
                
                total_height = len(text_lines) * line_height
                
                # Draw background rectangle
                bg_top_left = (center_x - max_width // 2 - 5, center_y - total_height // 2 - 5)
                bg_bottom_right = (center_x + max_width // 2 + 5, center_y + total_height // 2 + 5)
                cv2.rectangle(image_copy, bg_top_left, bg_bottom_right, (0, 0, 0), -1)
                
                # Draw each text line
                for j, text in enumerate(text_lines):
                    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                    text_y = center_y - total_height // 2 + (j + 1) * line_height - 5
                    text_org = (center_x - text_size[0] // 2, text_y)
                    cv2.putText(image_copy, text, text_org, font, font_scale, (255, 255, 255), thickness)
        
        return image_copy
    
    def draw_axis(self, image, rvecs, tvecs, length=0.03):
        """
        Draw 3D axis on detected markers to visualize pose.
        
        Args:
            image: Input image
            rvecs: Rotation vectors
            tvecs: Translation vectors
            length: Length of axis in meters
        
        Returns:
            image_with_axis: Image with drawn axis
        """
        image_copy = image.copy()
        
        if rvecs is not None and tvecs is not None:
            for i in range(len(rvecs)):
                # Draw axis for each marker
                cv2.drawFrameAxes(
                    image_copy,
                    self.camera_matrix,
                    self.dist_coeffs,
                    rvecs[i],
                    tvecs[i],
                    length
                )
        
        return image_copy
    
    def calculate_distance_from_marker_size(self, corners, real_marker_size_mm=50):
        """
        Calculate distance using marker pixel size (without camera calibration).
        This is an approximation method that works reasonably well for rough distance estimation.
        
        Args:
            corners: Marker corners from detection
            real_marker_size_mm: Real size of the marker in millimeters (default: 50mm)
        
        Returns:
            List of estimated distances in millimeters
        """
        distances = []
        
        if corners is not None and len(corners) > 0:
            for corner in corners:
                # Calculate marker width and height in pixels
                corner_points = corner[0]
                
                # Calculate distances between corners
                width_pixels = np.linalg.norm(corner_points[1] - corner_points[0])
                height_pixels = np.linalg.norm(corner_points[3] - corner_points[0])
                
                # Use average of width and height for more stability
                avg_size_pixels = (width_pixels + height_pixels) / 2
                
                # Simple focal length approximation (works for many webcams)
                # This assumes a typical webcam with ~60° field of view
                focal_length_approx = 600  # pixels (rough approximation)
                
                # Distance calculation using similar triangles
                # distance = (real_size * focal_length) / pixel_size
                distance_mm = (real_marker_size_mm * focal_length_approx) / avg_size_pixels
                
                distances.append(distance_mm)
        
        return distances
    
    def calculate_distance_from_area(self, corners, real_marker_size_mm=50):
        """
        Calculate distance using marker area (alternative method without calibration).
        
        Args:
            corners: Marker corners from detection
            real_marker_size_mm: Real size of the marker in millimeters (default: 50mm)
        
        Returns:
            List of estimated distances in millimeters
        """
        distances = []
        
        if corners is not None and len(corners) > 0:
            for corner in corners:
                # Calculate marker area in pixels
                corner_points = corner[0]
                
                # Calculate area using shoelace formula
                x = corner_points[:, 0]
                y = corner_points[:, 1]
                area_pixels = 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] for i in range(-1, 3)))
                
                # Real marker area
                real_area_mm2 = real_marker_size_mm ** 2
                
                # Approximate focal length and distance calculation
                # This is a rough approximation based on typical webcam parameters
                focal_length_approx = 600  # pixels
                
                # Distance calculation using area ratio
                # Assumes area scales with 1/distance²
                distance_mm = focal_length_approx * np.sqrt(real_area_mm2 / area_pixels)
                
                distances.append(distance_mm)
        
        return distances

    def get_pose_info(self, rvecs, tvecs, ids, corners=None, include_uncalibrated_distance=True):
        """
        Get pose information as a list of dictionaries.
        
        Args:
            rvecs: Rotation vectors
            tvecs: Translation vectors
            ids: Marker IDs
            corners: Marker corners (for uncalibrated distance calculation)
            include_uncalibrated_distance: Whether to include distance estimates without calibration
        
        Returns:
            List of pose information dictionaries
        """
        pose_info = []
        
        if rvecs is not None and tvecs is not None and ids is not None:
            # Calculate uncalibrated distances if requested
            distances_size = []
            distances_area = []
            if include_uncalibrated_distance and corners is not None:
                distances_size = self.calculate_distance_from_marker_size(corners)
                distances_area = self.calculate_distance_from_area(corners)
            
            for i in range(len(ids)):
                # Convert rotation vector to rotation matrix
                rmat, _ = cv2.Rodrigues(rvecs[i])
                
                # Calculate yaw angle (rotation around Z-axis)
                yaw = np.arctan2(rmat[1, 0], rmat[0, 0])
                
                # Calibrated distance from translation vector
                calibrated_distance_m = np.linalg.norm(tvecs[i][0])
                calibrated_distance_mm = calibrated_distance_m * 1000
                
                info = {
                    'id': int(ids[i][0]),
                    'rvec': rvecs[i][0].tolist(),
                    'tvec': tvecs[i][0].tolist(),
                    'position': {
                        'x': float(tvecs[i][0][0]),
                        'y': float(tvecs[i][0][1]),
                        'z': float(tvecs[i][0][2])
                    },
                    'yaw_rad': float(yaw),
                    'yaw_deg': float(np.degrees(yaw)),
                    'distance_calibrated_mm': float(calibrated_distance_mm),
                    'distance_calibrated_m': float(calibrated_distance_m)
                }
                
                # Add uncalibrated distance estimates if available
                if include_uncalibrated_distance and i < len(distances_size):
                    info['distance_uncalibrated_size_mm'] = float(distances_size[i])
                    info['distance_uncalibrated_size_m'] = float(distances_size[i] / 1000)
                    
                if include_uncalibrated_distance and i < len(distances_area):
                    info['distance_uncalibrated_area_mm'] = float(distances_area[i])
                    info['distance_uncalibrated_area_m'] = float(distances_area[i] / 1000)
                
                pose_info.append(info)
        
        return pose_info
    
    def process_frame(self, image, draw_markers=True, draw_axis=True, include_uncalibrated_distance=True):
        """
        Process a single frame: detect markers, estimate pose, and draw visualizations.
        
        Args:
            image: Input image
            draw_markers: Whether to draw marker boundaries and IDs
            draw_axis: Whether to draw 3D axis
            include_uncalibrated_distance: Whether to include uncalibrated distance estimates
        
        Returns:
            processed_image: Image with visualizations
            pose_info: List of pose information dictionaries
        """
        # Detect markers
        corners, ids, rejected = self.detect_markers(image)
        
        # Estimate pose
        rvecs, tvecs = self.estimate_pose(corners)
        
        # Get pose information (now includes uncalibrated distance estimates)
        pose_info = self.get_pose_info(rvecs, tvecs, ids, corners, include_uncalibrated_distance)
        
        # Draw visualizations
        processed_image = image.copy()
        
        if draw_markers and ids is not None:
            processed_image = self.draw_detected_markers(processed_image, corners, ids, 
                                                       show_distance=include_uncalibrated_distance, 
                                                       pose_info=pose_info)
        
        if draw_axis and rvecs is not None:
            processed_image = self.draw_axis(processed_image, rvecs, tvecs)
        
        return processed_image, pose_info
    
    def classify_marker(self, marker_id):
        """
        Classify marker type based on ID ranges.
        
        Args:
            marker_id: Marker ID
        
        Returns:
            Marker type string
        """
        if 0 <= marker_id <= 3:
            return "MAP"
        elif 10 <= marker_id <= 20:
            return "CAISSE"
        elif marker_id >= 30:
            return "ENEMY"
        else:
            return "UNKNOWN"


def main():
    """Example usage of the MarkerDetector."""
    import sys
    
    # Initialize detector
    detector = MarkerDetector(
        dictionary_type=cv2.aruco.DICT_4X4_50,
        marker_length=0.05  # 5cm markers
    )
    
    # Try to open webcam
    cap = cv2.VideoCapture(2)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        print("Please run with an image file as argument:")
        print("  python marker_detector.py image.jpg")
        sys.exit(1)
    
    print("ArUco Marker Detector with Distance Comparison")
    print("=" * 60)
    print("This detector compares distance measurements:")
    print("  • Calibrated: Uses camera calibration and pose estimation")
    print("  • Uncalibrated: Uses pixel-based approximations")
    print("=" * 60)
    print("Controls:")
    print("  Press 'q' to quit")
    print("  Press 's' to save current frame")
    print("  Press 'd' to toggle distance display on image")
    print("=" * 60)
    
    frame_count = 0
    show_distance_on_image = True
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Process frame
        processed_frame, pose_info = detector.process_frame(frame, include_uncalibrated_distance=show_distance_on_image)
        
        # Display pose information
        if pose_info:
            for info in pose_info:
                marker_type = detector.classify_marker(info['id'])
                print(f"\n[{marker_type}] Marker ID: {info['id']}")
                print(f"  Position: x={info['position']['x']:.4f}m, "
                      f"y={info['position']['y']:.4f}m, z={info['position']['z']:.4f}m")
                print(f"  Yaw: {info['yaw_deg']:.2f}°")
                
                # Display distance comparison
                print(f"  Distance Comparison:")
                print(f"    Calibrated (pose estimation): {info['distance_calibrated_mm']:.1f}mm ({info['distance_calibrated_m']:.3f}m)")
                
                if 'distance_uncalibrated_size_mm' in info:
                    print(f"    Uncalibrated (marker size):   {info['distance_uncalibrated_size_mm']:.1f}mm ({info['distance_uncalibrated_size_m']:.3f}m)")
                    
                if 'distance_uncalibrated_area_mm' in info:
                    print(f"    Uncalibrated (marker area):   {info['distance_uncalibrated_area_mm']:.1f}mm ({info['distance_uncalibrated_area_m']:.3f}m)")
                
                # Calculate and display differences
                if 'distance_uncalibrated_size_mm' in info:
                    diff_size = abs(info['distance_calibrated_mm'] - info['distance_uncalibrated_size_mm'])
                    diff_size_percent = (diff_size / info['distance_calibrated_mm']) * 100
                    print(f"    Difference (size method):     {diff_size:.1f}mm ({diff_size_percent:.1f}%)")
                    
                if 'distance_uncalibrated_area_mm' in info:
                    diff_area = abs(info['distance_calibrated_mm'] - info['distance_uncalibrated_area_mm'])
                    diff_area_percent = (diff_area / info['distance_calibrated_mm']) * 100
                    print(f"    Difference (area method):     {diff_area:.1f}mm ({diff_area_percent:.1f}%)")
        
        # Display frame
        cv2.imshow('ArUco Detection', processed_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"output/detected_frame_{frame_count:04d}.jpg"
            cv2.imwrite(filename, processed_frame)
            print(f"\nSaved frame to: {filename}")
            frame_count += 1
        elif key == ord('d'):
            show_distance_on_image = not show_distance_on_image
            status = "ON" if show_distance_on_image else "OFF"
            print(f"\nDistance display on image: {status}")
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
