import rclpy
from rclpy.node import Node
from ros_custom_messages.msg import (
    MasterNavigationMessage,
    MasterAcknowledgeSignal,
    MasterStopSignal,
    MasterResetSignal,
)


class CanInteractive(Node):
    def __init__(self):
        super().__init__('can_send_stop_signal')

        self.get_logger().info("can_masterSenderInteractive node has started.")

        # Create publishers for the topics
        self.nav_pub = self.create_publisher(
            MasterNavigationMessage, '/ros_can_interface/master_nav', 10
        )
        self.ack_pub = self.create_publisher(
            MasterAcknowledgeSignal, '/ros_can_interface/master_acknowledge', 10
        )
        self.reset_pub = self.create_publisher(
            MasterResetSignal, '/ros_can_interface/master_reset', 10
        )
        self.stop_pub = self.create_publisher(
            MasterStopSignal, '/ros_can_interface/stop_signal', 10
        )

        # Timer to periodically check for user input
        self.timer = self.create_timer(1.0, self.send_messages)

    def send_messages(self):
        # Ask the user for the type of message
        message_type = input(
            "Enter message type (nav/ack/stop/reset): "
        ).lower()

        if message_type == 'nav':
            # Create and publish a navigation message
            nav_msg = MasterNavigationMessage()
            nav_msg.nav_target_x = float(input("Enter targetX: "))
            nav_msg.nav_target_y = float(input("Enter targetY: "))
            nav_msg.nav_target_angle = float(input("Enter targetAngle: "))
            nav_msg.nav_is_forward = input(
                "Is it forward? (True/False): "
            ).lower() == 'true'
            nav_msg.nav_linear_velocity_choice = int(
                input("Enter linearVelocityChoice (0 to 3): ")
            )
            nav_msg.nav_angular_velocity_choice = int(
                input("Enter angularVelocityChoice (0 to 3): ")
            )
            nav_msg.nav_linear_acceleration_choice = int(
                input("Enter linearAccelerationChoice (0 to 3): ")
            )
            nav_msg.nav_angular_acceleration_choice = int(
                input("Enter angularAccelerationChoice (0 to 3): ")
            )
            nav_msg.nav_is_with_platforms = input("Is it with platforms? (True/False): ").lower()=='true'

            self.nav_pub.publish(nav_msg)
            self.get_logger().info(f"Published Navigation Data: {nav_msg}")

        elif message_type == 'ack':
            # Create and publish an acknowledgment signal
            ack_msg = MasterAcknowledgeSignal()
            ack_msg.master_acknowledge_signal = True
            self.ack_pub.publish(ack_msg)
            self.get_logger().info(f"Published Acknowledgment Signal: {ack_msg}")

        elif message_type == 'stop':
            # Create and publish a lidar stop signal
            stop_msg = MasterStopSignal()
            stop_msg.stop_signal_state = True
            self.stop_pub.publish(stop_msg)
            self.get_logger().info(f"Published Lidar Stop Signal: {stop_msg}")

        elif message_type == 'reset':
            # Create and publish a reset signal
            reset_msg = MasterResetSignal()
            reset_msg.master_reset_signal = True
            self.reset_pub.publish(reset_msg)
            self.get_logger().info(f"Published Reset Signal: {reset_msg}")

        else:
            self.get_logger().warn("Invalid message type. Please enter 'nav', 'ack', 'stop', or 'reset'.")


def main(args=None):
    rclpy.init(args=args)

    node = CanInteractive()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

