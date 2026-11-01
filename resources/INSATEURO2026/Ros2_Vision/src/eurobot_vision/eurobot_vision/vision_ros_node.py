import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import os
import cv2
import sys
import numpy as np

# Import your existing tracker from the eurobot_vision package
from eurobot_vision.vision_tracker import FullPipelineTracker

from ament_index_python.packages import get_package_share_directory

from rclpy.qos import QoSProfile, ReliabilityPolicy

qos_profile = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    depth=10
)


class EurobotVisionNode(Node):
    def __init__(self):
        super().__init__('eurobot_vision_node')
        
        # --- Parameters - DECLARE FIRST ---
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('camera_id', 0) #change it to 1 if it doesn't work
        self.declare_parameter('config_dir', '')
        self.declare_parameter('enable_kalman', True)
        self.declare_parameter('enemy_id', 13)
        
        # --- Get parameter values ---
        self.image_topic = self.get_parameter('image_topic').value
        self.camera_id = self.get_parameter('camera_id').value
        config_dir = self.get_parameter('config_dir').value
        self.enable_kalman = self.get_parameter('enable_kalman').value
        self.enemy_id = self.get_parameter('enemy_id').value

        # --- Set default config_dir if not provided ---
        if not config_dir:
            config_dir = os.path.join(get_package_share_directory('eurobot_vision'), 'config')
            self.get_logger().info(f"Using default config directory: {config_dir}")
        
        # --- Path Setup ---
        intrinsics_path = os.path.join(config_dir, 'camera_calibration.json')
        extrinsics_path = os.path.join(config_dir, 'camera_extrinsics.json')
        
        self.get_logger().info(f"Vision Node Config Loaded: {config_dir}")
        # ...existing code...

        # --- Initialize Vision Tracker ---
        try:
            self.tracker = FullPipelineTracker(
                camera_id=self.camera_id,
                intrinsics_file=intrinsics_path,
                extrinsics_file=extrinsics_path,
                enable_kalman=self.enable_kalman
            )
            self.get_logger().info("Tracker initialized successfully.")
        except Exception as e:
            self.get_logger().error(f"Failed to initialize tracker: {e}")
            sys.exit(1)

        # --- Publishers ---
        # Publishes the enemy robot position to the map
        self.enemy_pub = self.create_publisher(PoseStamped, '/vision/enemy_pose', qos_profile)

        # --- Subscribers ---
        self.bridge = CvBridge()
        
        # Subscribe to the topic defined in 'image_topic' parameter
        self.subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10 # QoS History depth matches your publisher
        )
        self.get_logger().info(f"Listening for images on: {self.image_topic}")

    def image_callback(self, msg):
        """
        Callback function triggered every time the CameraPublisher sends an image.
        """
        try:
            # Convert ROS Image message to OpenCV image
            # Your camera node sends 'bgr8', so we convert to the same.
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Could not convert image: {e}")
            return

        # --- Core Vision Logic ---
        # Pass the frame to your existing vision_tracker.py logic
        display, detections = self.tracker.process_frame(frame)

        # --- Publish Data ---
        # We use the timestamp from the CAMERA frame, not the current time.
        # This ensures synchronization between when the event happened and the data we publish.
        timestamp = msg.header.stamp 

        if self.enemy_id in detections:
            enemy_data = detections[self.enemy_id]
            self.publish_marker_pose(enemy_data, self.enemy_pub, timestamp)

        # Optional: If you want to see the processed output (with drawings) in ROS:
        # self.debug_pub.publish(self.bridge.cv2_to_imgmsg(display, "bgr8"))

    def publish_marker_pose(self, data, publisher, timestamp):
        msg = PoseStamped()
        msg.header.stamp = timestamp
        msg.header.frame_id = "map" # We are publishing coordinates relative to the map

        # Select filtered (Kalman) or raw coordinates
        if data.get('filtered', False):
            pos = data['kalman_pos']
            theta = data['kalman_theta']
        else:
            pos = data['world_pos']
            theta = data['theta']

        # Position (x, y, z in meters)
        msg.pose.position.x = float(pos[0])
        msg.pose.position.y = float(pos[1])
        msg.pose.position.z = float(pos[2])

        # Orientation (Yaw to Quaternion)
        q = self.yaw_to_quaternion(theta)
        msg.pose.orientation.x = q[0]
        msg.pose.orientation.y = q[1]
        msg.pose.orientation.z = q[2]
        msg.pose.orientation.w = q[3]

        publisher.publish(msg)

    def yaw_to_quaternion(self, yaw):
        """Helper to convert 2D rotation (yaw) to 3D Quaternion"""
        import math
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        return [0.0, 0.0, sy, cy]

def main(args=None):
    rclpy.init(args=args)
    node = EurobotVisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()