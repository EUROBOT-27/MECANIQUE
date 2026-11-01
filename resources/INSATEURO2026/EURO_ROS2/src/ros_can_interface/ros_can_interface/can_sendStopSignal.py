import rclpy
import can
import struct
from rclpy.node import Node
from ros_custom_messages.msg import MasterStopSignal

class CanSendStopSignal(Node):
    def __init__(self):
        super().__init__('can_sendStopSignal')
        
        # Initialize CAN bus
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')  # Initialize bus here
        
        self.get_logger().info("can_sendStopSignal node has started.")
        
        # Create subscription to 'master_acknowledgSignal'
        self.stop_subscription = self.create_subscription(
            MasterStopSignal,
            'ros_can_interface/stop_signal',
            self.stop_callback,
            10
        )

    def stop_callback(self, msg):
        if msg.stop_signal_state == True:
            # Declare a 64bit integer
            stopSignal = 0xFFFFFFFFFFFFFFFF
            
            # Convert the 64-bit integer to bytes
            data_bytes = struct.pack('>Q', stopSignal)
            
            # Create a CAN message object
            message_obj = can.Message(arbitration_id=0x000, data=list(data_bytes[:8]), is_extended_id=False)
            
            # Send the CAN message
            self.bus.send(message_obj)
            
            # Log the data for demonstration purposes
            self.get_logger().info("Transmitted SUDDEN STOP Signal.")

def main(args=None):
    rclpy.init(args=args)
    node = CanSendStopSignal()  
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

