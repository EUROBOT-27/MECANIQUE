#!/usr/bin/env python3
"""
Interactive publisher for sending servo commands to ESP32 via CAN bus.
Allows user to control 4 servos simultaneously with custom angles.
"""

import rclpy
from rclpy.node import Node
from ros_custom_messages.msg import MechanismCommand, ServoCommand


class TestServoPublisher(Node):
    def __init__(self):
        super().__init__('test_servo_publisher')
        
        # Create publisher for mechanism commands
        self.publisher = self.create_publisher(
            MechanismCommand,
            'ros_can_interface/mechanism_command',
            10
        )
        
        self.get_logger().info("Interactive Servo Publisher node started.")
        self.get_logger().info("Publishing to 'ros_can_interface/mechanism_command'")
        self.get_logger().info("Controlling 4 servos on Maestro 12x controller")
        
        # Start interactive session immediately
        self.send_servo_commands()

    def send_servo_commands(self):
        """
        Interactively send servo commands for 4 servos.
        Creates MechanismCommand with ServoCommand array.
        """
        self.get_logger().info("\n=== Mechanism Control (4 Servos) ===")
        
        msg = MechanismCommand()
        msg.servos = []
        
        try:
            # Get input for each of the 4 servos
            for i in range(4):
                self.get_logger().info(f"\n--- Servo {i} (Channel {i}) ---")
                
                servo_cmd = ServoCommand()
                servo_cmd.servo_id = i
                
                # Get enable state
                while True:
                    enable_input = input(f"Servo {i} enabled? (1=ON, 0=OFF): ").strip()
                    if enable_input in ['0', '1']:
                        servo_cmd.enabled = (enable_input == '1')
                        break
                    else:
                        print("Invalid input. Please enter 0 or 1.")
                
                # Get angle if enabled
                if servo_cmd.enabled:
                    while True:
                        try:
                            angle_input = input(f"Servo {i} angle (0-180 degrees): ").strip()
                            angle = int(angle_input)
                            if 0 <= angle <= 180:
                                servo_cmd.target_angle = angle
                                break
                            else:
                                print("Angle must be between 0 and 180.")
                        except ValueError:
                            print("Invalid input. Please enter a number.")
                else:
                    servo_cmd.target_angle = 90  # Safe default position
                
                msg.servos.append(servo_cmd)
            
            # Publish the command
            self.publisher.publish(msg)
            
            # Format log message
            log_msg = "Published Mechanism Command: "
            for servo in msg.servos:
                status = f"{servo.target_angle}°" if servo.enabled else "OFF"
                log_msg += f"S{servo.servo_id}={status}, "
            self.get_logger().info(log_msg.rstrip(", "))
            
        except Exception as e:
            self.get_logger().error(f"Error: {e}")
        
        # Ask if user wants to send another command
        another = input("\nSend another command? (y/n): ").lower()
        if another == 'y' or another == 'yes':
            self.send_servo_commands()
        else:
            self.get_logger().info("Exiting...")
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = TestServoPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
