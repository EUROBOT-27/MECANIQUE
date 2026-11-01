import rclpy
from  rclpy.node import Node
import can
import struct
from ros_custom_messages.msg import NavigatorNavigationMessage

class CanReceiveNavigationMessage(Node):
    def __init__(self):
        super().__init__('can_receiveNavigationMessage')
       # self.declare_parameter('Current_X', 0.0)
       #self.declare_parameter('Current_Y', 0.0 )
       #self.declare_parameter('Current_angle', 0.0)
       # self.declare_parameter('Current_state',0)

        # Initialize the CAN bus
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        
        self.get_logger().info("can_receiveNavigationMessage node has started.")
        
        # Create publisher for custom message type
        self.publisher_ = self.create_publisher(NavigatorNavigationMessage, 'ros_can_interface/navigator_nav', 10)
        
        # Create a timer to call the callback periodically
        rate_period = 30  # Hz
        self.timer = self.create_timer(1.0 / rate_period, self.Navigator_callback)
        
    def decode_message(self, can_msg):
        # Combine the received bytes into a 64-bit integer
        combined_value = struct.unpack('<Q', bytes(can_msg))[0]
        
        # Decode the combined value back into the original variables
        nav_currentX = ((combined_value >> 45) & 0x7FFFF) * 0.01
        nav_currentY = ((combined_value >> 27) & 0x3FFFF) * 0.01
        nav_currentAngle = ((combined_value >> 11) & 0xFFFF) * 0.01
        nav_currentState = (combined_value >> 3) & 0xFF

        #self.set_parameter('Current_X', nav_currentX)
        #self.set_parameter('Current_Y',nav_currentY )
        #self.set_parameter('Current_angle', nav_currentAngle)
        #self.set_parameter('Current_state',nav_currentState)
        # Create a NavigationMessage object
        nav_msg = NavigatorNavigationMessage()
        nav_msg.nav_current_x = nav_currentX
        nav_msg.nav_current_y = nav_currentY
        nav_msg.nav_current_angle = nav_currentAngle
        nav_msg.nav_current_state = nav_currentState
        
        return nav_msg

    def Navigator_callback(self):
        # Receive a CAN message
        can_msg = self.bus.recv(1)
        if can_msg is not None and can_msg.arbitration_id == 0x004:
            # Decode the message and publish it
            msg = self.decode_message(can_msg)
            self.publisher_.publish(msg)
            self.get_logger().info("Received CAN Message: Data: currentX: %f, currentY: %f, currentAngle %f, currentState %d" %
                                  (msg.nav_current_x, msg.nav_current_y,
                                  msg.nav_current_angle, msg.nav_current_state))

def main(args=None):
    rclpy.init(args=args)
    node = CanReceiveNavigationMessage()  
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

