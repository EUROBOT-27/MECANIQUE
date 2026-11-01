import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class EnemyPositionFusion(Node):
    def __init__(self):
        super().__init__('enemy_position_fusion')
        # Subscribe to vision and lidar enemy position topics
        self.vision_sub = self.create_subscription(
            Point,
            'enemy_pose',
            self.vision_callback,
            10
        )
        self.lidar_sub = self.create_subscription(
            Point,
            'Enemy_Robot_Position',
            self.lidar_callback,
            10
        )
        # Publisher for fused position
        self.fused_pub = self.create_publisher(
            Point,
            'fused_enemy_position',
            10
        )
        self.vision_msg = None
        self.lidar_msg = None

    def vision_callback(self, msg):
        self.vision_msg = msg
        self.fuse_and_publish()

    def lidar_callback(self, msg):
        self.lidar_msg = msg
        self.fuse_and_publish()

    def fuse_and_publish(self):
        # Only fuse if both messages are available
        if self.vision_msg is not None and self.lidar_msg is not None:
            fused = Point()
            fused.x = (self.vision_msg.x + self.lidar_msg.x) / 2.0
            fused.y = (self.vision_msg.y + self.lidar_msg.y) / 2.0
            fused.z = (self.vision_msg.z + self.lidar_msg.z) / 2.0
            self.fused_pub.publish(fused)
            self.get_logger().info(f"Fused enemy position: x={fused.x}, y={fused.y}, z={fused.z}")


def main(args=None):
    rclpy.init(args=args)
    node = EnemyPositionFusion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
