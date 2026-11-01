#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ensi.srv import NumberService
import cv2
import numpy as np
import random

class NumberDetectionServer(Node):
    def __init__(self):
        super().__init__('number_detection_server')
        self.srv = self.create_service(
            NumberService, 
            'detect_number', 
            self.detect_number_callback
        )
        self.get_logger().info('Number Detection Service Server Ready')

    def detect_number_callback(self, request, response):
        """
        Callback function for number detection service.
        In a real implementation, this would:
        1. Get image from camera
        2. Process image for number/digit recognition
        3. Return the detected number
        
        For now, this is a mock implementation.
        """
        try:
            # Mock number detection - replace with actual OCR/ML logic
            detected_number = random.randint(0, 9)
            
            # In real implementation, you would:
            # 1. Subscribe to camera topic or get image
            # 2. Preprocess image (grayscale, threshold, etc.)
            # 3. Use OCR (Tesseract) or trained ML model
            # 4. Extract and recognize digits
            # 5. Return the detected number
            
            response.response_number = detected_number
            self.get_logger().info(f'Detected number: {detected_number}')
            
        except Exception as e:
            self.get_logger().error(f'Number detection failed: {str(e)}')
            response.response_number = -1  # Error indicator
            
        return response

def main(args=None):
    rclpy.init(args=args)
    number_detection_server = NumberDetectionServer()
    
    try:
        rclpy.spin(number_detection_server)
    except KeyboardInterrupt:
        pass
    finally:
        number_detection_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()