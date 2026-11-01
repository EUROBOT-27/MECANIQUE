import rclpy
from rclpy.node import Node
from ros_custom_messages.msg import MechanismCommand, ServoCommand


class ServoInteractive(Node):
    def __init__(self):
        super().__init__('servo_sender_interactive')

        self.get_logger().info("Servo Sender Interactive node has started.")

        # Create publisher for mechanism commands
        self.servo_pub = self.create_publisher(
            MechanismCommand, 'ros_can_interface/mechanism_command', 10
        )

        # Start interactive session immediately
        self.send_servo_commands()

    def send_servo_commands(self):
        """
        Send mechanism control commands interactively.
        Options:
        1. Quick ON/OFF for all servos
        2. Individual servo control
        """
        self.get_logger().info("\n--- Mechanism Control ---")
        
        mode = input("Mode: (1) Quick ALL ON/OFF, (2) Individual Control: ").strip()

        msg = MechanismCommand()
        msg.servos = []

        if mode == '1':
            # Quick mode - all servos on or off
            state = input("All servos state (1=ON at 90°, 0=OFF): ").strip()
            
            if state == '1':
                # Turn all 4 servos ON at 90 degrees
                for i in range(4):
                    servo = ServoCommand()
                    servo.servo_id = i
                    servo.enabled = True
                    servo.target_angle = 90
                    msg.servos.append(servo)
                self.servo_pub.publish(msg)
                self.get_logger().info("Published: All servos ON at 90°")

            elif state == '0':
                # Turn all servos OFF
                for i in range(4):
                    servo = ServoCommand()
                    servo.servo_id = i
                    servo.enabled = False
                    servo.target_angle = 90
                    msg.servos.append(servo)
                self.servo_pub.publish(msg)
                self.get_logger().info("Published: All servos OFF")
            else:
                self.get_logger().warn("Invalid input. Please enter '1' or '0'.")
                
        elif mode == '2':
            # Individual control mode
            servo_id = int(input("Servo ID (0-3): ").strip())
            if servo_id >= 0 and servo_id <= 3:
                enabled = input(f"Servo {servo_id} enabled? (1=ON, 0=OFF): ").strip() == '1'
                
                if enabled:
                    angle = int(input(f"Servo {servo_id} angle (0-180): ").strip())
                    if angle < 0 or angle > 180:
                        self.get_logger().warn("Angle must be 0-180.")
                        return
                else:
                    self.get_logger().info("Servo will be disabled; setting default angle to 90°.") 
                    angle = 90  # Default safe position
                
                servo = ServoCommand()
                servo.servo_id = servo_id
                servo.enabled = enabled
                servo.target_angle = angle
                msg.servos.append(servo)
                
                self.servo_pub.publish(msg)
                status = f"{angle}°" if enabled else "OFF"
                self.get_logger().info(f"Published: Servo {servo_id} = {status}")
            else:
                self.get_logger().warn("Invalid servo ID. Must be 0-3.")
        else:
            self.get_logger().warn("Invalid mode. Please enter '1' or '2'.")
        
        # Ask if user wants to send another command
        another = input("\nSend another command? (y/n): ").lower()
        if another == 'y' or another == 'yes' or another == 'Y' or another == 'YES' or another == '1':
            self.send_servo_commands()
        else:
            self.get_logger().info("Exiting...")
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    node = ServoInteractive()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
