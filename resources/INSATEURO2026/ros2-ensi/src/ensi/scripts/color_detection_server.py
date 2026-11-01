#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ensi.srv import ColorService
import cv2
import numpy as np
import random

class ColorDetectionServer(Node):
    def __init__(self):
        super().__init__('color_detection_server')
        self.srv = self.create_service(
            ColorService, 
            'detect_color', 
            self.detect_color_callback
        )
        self.get_logger().info('Color Detection Service Server Ready')

    def detect_color_callback(self, request, response):
        """
        Callback function for color detection service.
        In a real implementation, this would:
        1. Get image from camera
        2. Process image for color detection
        3. Return the detected color
        
        For now, this is a mock implementation.
        """
        try:
            # Mock color detection - replace with actual computer vision logic
            detected_colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple']
            detected_color = random.choice(detected_colors)
            
            # In real implementation, you would:
            # 1. Subscribe to camera topic or get image
            # 2. Convert image to HSV color space
            # 3. Define color ranges for detection
            # 4. Use cv2.inRange() to detect colors
            # 5. Return the most dominant color
            
            response.response_color = detected_color
            self.get_logger().info(f'Detected color: {detected_color}')
            
        except Exception as e:
            self.get_logger().error(f'Color detection failed: {str(e)}')
            response.response_color = 'unknown'
            
        return response

def main(args=None):
    rclpy.init(args=args)
    color_detection_server = ColorDetectionServer()
    
    try:
        rclpy.spin(color_detection_server)
    except KeyboardInterrupt:
        pass
    finally:
        color_detection_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()