#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped  # Changed from PoseStamped

class Subscriber(Node):
    def __init__(self):
        super().__init__('subscriber_node')
        
        # Subscribe to enemy position from laptop
        self.enemy_sub = self.create_subscription(
            PointStamped,  # Changed message type
            '/vision/enemy_pose',
            self.enemy_callback,
            10
        )
        self.get_logger().info("Robot controller waiting for enemy position...")
    
    def enemy_callback(self, msg):
        # Extract marker ID from frame_id
        marker_id = int(msg.header.frame_id.split('_')[1])  # "marker_13" → 13
        
        # Extract enemy position
        enemy_x = msg.point.x  # Changed from msg.pose.position.x
        enemy_y = msg.point.y  # Changed from msg.pose.position.y
        
        self.get_logger().info(f"Marker {marker_id} at: ({enemy_x:.2f}, {enemy_y:.2f})")
        
        # Your robot logic here:
        # - Avoid enemy
        # - Track enemy
        # - Plan strategy
        
def main(args=None):
    rclpy.init(args=args)
    subscriber = Subscriber()
    rclpy.spin(subscriber)
    subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()