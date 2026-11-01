#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import functools

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        
        # Publisher
        self.image_publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        
        # CV Bridge for image conversion
        self.bridge = CvBridge()
        
        # Camera setup
        self.camera_id = 0  # Default camera ID (changed from 0 to 1)
        self.declare_parameter('camera_id', 0) #change it to 1 if it doesn't work
        self.declare_parameter('fps', 30)
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)
        
        camera_id = self.get_parameter('camera_id').value
        fps = self.get_parameter('fps').value
        width = self.get_parameter('width').value
        height = self.get_parameter('height').value
        
        # Initialize camera
        try:
            self.cap = cv2.VideoCapture(camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            
            if not self.cap.isOpened():
                self.get_logger().error(f'Cannot open camera {camera_id}')
                return
                
            self.get_logger().info(f'Camera {camera_id} opened successfully: {width}x{height} @ {fps}fps')
            
        except Exception as e:
            self.get_logger().error(f'Camera initialization failed: {str(e)}')
            return
        
        # Timer for publishing images
        timer_period = 1.0 / fps  # seconds
        self.timer = self.create_timer(timer_period, self.capture_and_publish)

        # Timer to automatically call detection services and log results
        # Commented out to prevent continuous service calls - services should only be called by state machine
        #self.detection_timer = self.create_timer(1.0, self._periodic_detection_call)
        
    def capture_and_publish(self):
        """Capture frame and publish as ROS Image message"""
        try:
            ret, frame = self.cap.read()
            if ret:
                # Convert OpenCV image to ROS Image message
                ros_image = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
                ros_image.header.stamp = self.get_clock().now().to_msg()
                ros_image.header.frame_id = 'camera_frame'
                
                # Publish the image
                self.image_publisher.publish(ros_image)
            else:
                self.get_logger().warning('Failed to capture frame')
                
        except Exception as e:
            self.get_logger().error(f'Error capturing/publishing frame: {str(e)}')
    
    def destroy_node(self):
        """Clean up resources"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    camera_publisher = CameraPublisher()
    
    try:
        rclpy.spin(camera_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        camera_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
