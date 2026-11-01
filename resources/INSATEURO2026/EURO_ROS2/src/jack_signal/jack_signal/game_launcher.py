import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ros_custom_messages.msg import MasterNavigationMessage
"""
This module defines the GameLauncher ROS2 node for initializing and publishing the robot's starting position and color.

Classes:
    GameLauncher(Node): 
        A ROS2 node that publishes the robot's initial navigation position and color based on user input.

Functions:
    main(args=None):
        Initializes the ROS2 node, prompts the user for the robot color, and starts spinning the node.

Global Variables:
    robot_color (str or None): 
        Stores the selected robot color ("blue" or "yellow") as provided by the user.

Topics Published:
    - 'init_position' (MasterNavigationMessage): Publishes the initial navigation position for the robot.
    - 'robot_color' (String): Publishes the selected robot color.
"""

robot_color = None

class GameLauncher(Node):
    def __init__(self):
        super().__init__('game_launcher')
        self.publisher_ = self.create_publisher(MasterNavigationMessage, 'init_position', 10)
        self.robot_color_publisher_ = self.create_publisher(String, 'robot_color', 10)
        self.get_logger().info('GameLauncher node has been started.')
        self.timer = self.create_timer(0.5, self.publish_init_position)
        self.timer = self.create_timer(0.5, self.publish_robot_color)

    def publish_init_position(self):
        global robot_color
        if robot_color is None:
            return

        init_position = MasterNavigationMessage()
        if robot_color == "yellow":
            init_position.nav_target_x = 1200.0
            init_position.nav_target_y = 195.5 #315.5
            init_position.nav_target_angle = 90.0
        elif robot_color == "blue":
            init_position.nav_target_x = 1800.0
            init_position.nav_target_y = 195.5 #315.5
            init_position.nav_target_angle = 90.0
        else:
            self.get_logger().error('Invalid color input. Please use "blue" or "yellow".')
            return

        init_position.nav_is_forward = True
        init_position.nav_linear_velocity_choice = 0
        init_position.nav_angular_velocity_choice = 0
        init_position.nav_linear_acceleration_choice = 0
        init_position.nav_angular_acceleration_choice = 0
        init_position.nav_is_with_platforms = False

        self.publisher_.publish(init_position)
        self.get_logger().info(f'Published initial position for {robot_color} robot.')

    def publish_robot_color(self):
        global robot_color
        if robot_color is None:
            return

        robot_color_msg = String()
        robot_color_msg.data = robot_color
        self.robot_color_publisher_.publish(robot_color_msg)
        self.get_logger().info(f'Published robot color: {robot_color}')

def main(args=None):
    global robot_color
    rclpy.init(args=args)
    game_launcher = GameLauncher()

    robot_color = input("Enter the robot color (blue/yellow): ").strip().lower()

    rclpy.spin(game_launcher)
    game_launcher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()