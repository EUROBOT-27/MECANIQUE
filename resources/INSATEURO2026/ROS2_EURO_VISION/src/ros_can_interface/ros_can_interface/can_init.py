import can
import rclpy
from rclpy.node import Node
import os

class CanInit(Node):
    def __init__(self):
        super().__init__('can_init')
        self.get_logger().info("can_init node has started.")
        
        # Configure the CAN interface using os.system
        try:
            cmd0= f" sudo  ip link set can0 down"
            cmd1 = f" sudo ip link set can0 type can bitrate 500000 restart-ms 100"
            cmd2 = f" sudo ip link set up can0 "

            if os.system(cmd0) !=0:
                raise RuntimeError(f"Command failed: {cmd0}")
            if os.system(cmd1) != 0:
                raise RuntimeError(f"Command failed: {cmd1}")
            if os.system(cmd2) != 0:
                raise RuntimeError(f"Command failed: {cmd2}")
            else:
                 self.get_logger().info("CAN Peripheral has been successfully started.")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = CanInit()
#    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

