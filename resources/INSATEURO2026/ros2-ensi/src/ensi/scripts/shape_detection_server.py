#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ensi.srv import NumberTrianglesCubesService
import cv2
import numpy as np
import random

class ShapeDetectionServer(Node):
    def __init__(self):
        super().__init__('shape_detection_server')
        self.srv = self.create_service(
            NumberTrianglesCubesService, 
            'detect_triangles_cubes', 
            self.detect_shapes_callback
        )
        self.get_logger().info('Shape Detection Service Server Ready')

    def detect_shapes_callback(self, request, response):
        """
        Callback function for shape detection service.
        In a real implementation, this would:
        1. Get image from camera
        2. Process image for shape detection
        3. Count triangles and cubes
        4. Return the total count
        
        For now, this is a mock implementation.
        """
        try:
            # Mock shape detection - replace with actual computer vision logic
            triangle_count = random.randint(0, 5)
            cube_count = random.randint(0, 5)
            total_count = triangle_count + cube_count
            
            # In real implementation, you would:
            # 1. Subscribe to camera topic or get image
            # 2. Preprocess image (grayscale, blur, threshold)
            # 3. Find contours using cv2.findContours()
            # 4. Analyze contour properties:
            #    - For triangles: approxPolyDP() should give 3 vertices
            #    - For cubes/squares: approxPolyDP() should give 4 vertices + aspect ratio ≈ 1
            # 5. Count valid shapes and return total
            
            response.response_number_triangles_cubes = total_count
            self.get_logger().info(f'Detected shapes: {triangle_count} triangles, {cube_count} cubes, total: {total_count}')
            
        except Exception as e:
            self.get_logger().error(f'Shape detection failed: {str(e)}')
            response.response_number_triangles_cubes = 0
            
        return response

def main(args=None):
    rclpy.init(args=args)
    shape_detection_server = ShapeDetectionServer()
    
    try:
        rclpy.spin(shape_detection_server)
    except KeyboardInterrupt:
        pass
    finally:
        shape_detection_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()