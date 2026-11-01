import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
import os
import cv2
import sys

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
        
        # --- Parameters ---
        self.declare_parameter('camera_id', 5)
        self.declare_parameter('config_dir', '')
        self.declare_parameter('enable_kalman', True)
        self.declare_parameter('enemy_id', 47)  # Added enemy ID parameter
        
        # --- Get parameter values ---
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

        # --- Initialize Vision Tracker ---
        try:
            self.tracker = FullPipelineTracker(
                camera_id=self.camera_id,
                intrinsics_file=intrinsics_path,
                extrinsics_file=extrinsics_path,
                enable_kalman=self.enable_kalman
            )
            self.get_logger().info(f"Tracker initialized successfully")
        except Exception as e:
            self.get_logger().error(f"Failed to initialize tracker: {e}")
            sys.exit(1)

        # --- Open Camera ---
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            self.get_logger().error(f"Cannot open camera {self.camera_id}")
            sys.exit(1)
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.get_logger().info(f"Camera {self.camera_id} opened successfully")

        # --- Publishers ---
        self.enemy_pub = self.create_publisher(PointStamped, '/vision/enemy_pose', qos_profile)

        # --- Timer to process frames (30 FPS) ---
        self.timer = self.create_timer(0.033, self.process_frame_callback)
        
        self.get_logger().info(f"Vision node ready - tracking enemy marker (ID {self.enemy_id}) at 30 FPS")

    def process_frame_callback(self):
        """Capture and process frame directly from camera"""
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warning('Failed to capture frame', throttle_duration_sec=5.0)
            return

        # --- Process frame through tracker ---
        try:
            display, detections = self.tracker.process_frame(frame)
        except Exception as e:
            self.get_logger().error(f'Error processing frame: {e}', throttle_duration_sec=5.0)
            return

        # --- Publish Data ---
        timestamp = self.get_clock().now().to_msg()

        # Publish ONLY enemy marker (ID 13)
        if self.enemy_id in detections:
            enemy_data = detections[self.enemy_id]
            self.publish_enemy_position(enemy_data, timestamp)

    def publish_enemy_position(self, data, timestamp):
        """Publish enemy marker position"""
        msg = PointStamped()
        msg.header.stamp = timestamp
        msg.header.frame_id = f"marker_{self.enemy_id}"

        # Use Kalman-filtered position if available, otherwise use raw
        if data.get('filtered', False) and 'kalman_pos' in data:
            pos = data['kalman_pos']
        else:
            pos = data['world_pos']

        # Publish X and Y position
        msg.point.x = float(pos[0])
        msg.point.y = float(pos[1])
        msg.point.z = 0.0

        self.enemy_pub.publish(msg)
        
        # Log for debugging (throttled to once per second)
        self.get_logger().info(
            f"Enemy at: ({msg.point.x:.3f}, {msg.point.y:.3f})",
            throttle_duration_sec=1.0
        )
    
    def destroy_node(self):
        """Clean up camera resources"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            self.get_logger().info("Camera released")
        super().destroy_node()


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