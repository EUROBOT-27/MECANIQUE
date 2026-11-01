import rclpy
import can
import struct
from rclpy.node import Node
from ros_custom_messages.msg import MasterNavigationMessage, MechanismCommand

class CanSendNavigationMessage(Node):
    def __init__(self):
        super().__init__('can_sendNavigationMessage')
        
        # Initialize CAN bus
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        
        self.get_logger().info("can_sendNavigationMessage node has started.")
        
        # Create subscription to '/ros_can_interface/master_nav' for STM32
        self.Nav_subscription = self.create_subscription(
            MasterNavigationMessage,
            'ros_can_interface/master_nav',
            self.NavigationMessage_callback,
            10
        )
        
        # Create subscription to '/ros_can_interface/mechanism_command' for ESP32
        self.servo_subscription = self.create_subscription(
            MechanismCommand,
            'ros_can_interface/mechanism_command',
            self.mechanism_callback,
            10
        )

    def encode_navigationMessage(self, msg):
        """Encode navigation message into a 64-bit integer."""
        nav_targetX_bits = int(msg.nav_target_x * 100) & 0x7FFFF  # 19 bits
        nav_targetY_bits = int(msg.nav_target_y * 100) & 0x3FFFF  # 18 bits
        nav_targetAngle_bits = int(msg.nav_target_angle * 100) & 0xFFFF  # 16 bits
        nav_isForward_bits = int(msg.nav_is_forward) & 0x1  # 1 bit (bool)
        nav_linearVilocityChoice_bits = int(msg.nav_linear_velocity_choice) & 0x3  # 2 bits
        nav_angularVilocityChoice_bits = int(msg.nav_angular_velocity_choice) & 0x3  # 2 bits
        nav_linearAccelerationChoice_bits = int(msg.nav_linear_acceleration_choice) & 0x3  # 2 bits
        nav_angularAccelerationChoice_bits = int(msg.nav_angular_acceleration_choice) & 0x3  # 2 bits
        nav_isWith_Platforms = int(msg.nav_is_with_platforms) & 0x1 #1 bit (bool)
        # Combine the bits into a 64-bit integer
        combined_value = (
            (nav_targetX_bits << 45)
            | (nav_targetY_bits << 27)
            | (nav_targetAngle_bits << 11)
            | (nav_isForward_bits << 10)
            | (nav_linearVilocityChoice_bits << 8)
            | (nav_angularVilocityChoice_bits << 6)
            | (nav_linearAccelerationChoice_bits << 4)
            | (nav_angularAccelerationChoice_bits << 2)
            | (nav_isWith_Platforms << 1  ))
        return combined_value

    def NavigationMessage_callback(self, msg):
        """Callback to handle navigation messages."""
        encoded_message = self.encode_navigationMessage(msg)
        
        # Convert the 64-bit integer to bytes
        data_bytes = struct.pack('>Q', encoded_message)
        
        # Create a CAN message object
        message_obj = can.Message(arbitration_id=0x002, data=list(data_bytes[:8]), is_extended_id=False)
        
        # Send the CAN message
        self.bus.send(message_obj)
        
        # Log the data for demonstration purposes
        self.get_logger().info(
    "Transmitted Navigation Data: targetX: {:.2f}, targetY: {:.2f}, targetA: {:.2f},"
    "direction: {:.2f},"
    "nav_linearVelocityChoice: {}, nav_angularVelocityChoice: {}, "
    "nav_linearAccelerationChoice: {}, nav_angularAccelerationChoice: {}".format(
        msg.nav_target_x,
        msg.nav_target_y,
        msg.nav_target_angle,
        int(msg.nav_is_forward),
        int(msg.nav_linear_velocity_choice),
        int(msg.nav_angular_velocity_choice),
        int(msg.nav_linear_acceleration_choice),
        int(msg.nav_angular_acceleration_choice)
)

             )

    def mechanism_callback(self, msg):
        """Callback to handle mechanism control commands for ESP32.
        
        Expected message format (MechanismCommand):
        - servos: Array of ServoCommand messages
        """
        if len(msg.servos) == 0:
            self.get_logger().warn("Received empty servo command list")
            return
        
        if len(msg.servos) > 12:
            self.get_logger().warn(f"Maestro 12x supports max 12 servos, got {len(msg.servos)}. Using first 12.")
        
        # Initialize 8 bytes for CAN (4 servos for now, expandable)
        # Format: [en1, angle1, en2, angle2, en3, angle3, en4, angle4]
        data_bytes = [0, 0, 0, 0, 0, 0, 0, 0]
        
        # Process up to 4 servos (can be expanded with multi-frame CAN)
        num_servos = min(len(msg.servos), 4)
        
        for i in range(num_servos):
            servo = msg.servos[i]
            
            # Validate servo_id (should match position for simple mapping)
            if servo.servo_id >= 12:
                self.get_logger().error(f"Invalid servo_id {servo.servo_id}, must be 0-11")
                return
            
            # Validate angle (0-180)
            if servo.target_angle > 180:
                self.get_logger().error(f"Servo {servo.servo_id} angle must be 0-180, got {servo.target_angle}")
                return
            
            # Encode into CAN data
            enable_byte = 1 if servo.enabled else 0
            angle_byte = int(servo.target_angle)
            
            data_bytes[i * 2] = enable_byte
            data_bytes[i * 2 + 1] = angle_byte
        
        # Create CAN message with 8 bytes
        message_obj = can.Message(
            arbitration_id=0x100,
            data=data_bytes,
            is_extended_id=False
        )
        
        try:
            self.bus.send(message_obj)
            # Format log message
            log_msg = "Transmitted Mechanism Commands to ESP32: "
            for servo in msg.servos[:4]:  # Log first 4
                status = f"{servo.target_angle}°" if servo.enabled else "OFF"
                log_msg += f"S{servo.servo_id}={status}, "
            self.get_logger().info(log_msg.rstrip(", "))
        except can.CanError as e:
            self.get_logger().error(f"Failed to send CAN message to ESP32: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = CanSendNavigationMessage()  
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

