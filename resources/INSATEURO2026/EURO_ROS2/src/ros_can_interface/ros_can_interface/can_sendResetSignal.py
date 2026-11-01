import rclpy
import can
import struct
from rclpy.node import Node
from ros_custom_messages.msg import MasterResetSignal

class CanSendResetSignal(Node):
    def __init__(self):
        super().__init__('can_sendResetSignal')
        
        # Initialize CAN bus
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')  # Initialize bus here
        
        self.get_logger().info("can_sendResetSignal node has started.")
        
        # Create subscription to 'master_acknowledgSignal'
        self.res_subscription = self.create_subscription(
            MasterResetSignal,
            'ros_can_interface/master_reset',
            self.reset_callback,
            10
        )

    def reset_callback(self, msg):
        if msg.master_reset_signal == True:
            # Declare a 64bit integer
            resetSignal = 0xFFFFFFFFFFFFFFFF
            
            # Convert the 64-bit integer to bytes
            data_bytes = struct.pack('>Q', resetSignal)
            
            # Create a CAN message object
            message_obj = can.Message(arbitration_id=0x003, data=list(data_bytes[:8]), is_extended_id=False)
            
            # Send the CAN message
            self.bus.send(message_obj)
            
            # Log the data for demonstration purposes
            self.get_logger().info("Transmitted RESET Signal.")

def main(args=None):
    rclpy.init(args=args)
    node = CanSendResetSignal()  
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

