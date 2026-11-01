import rclpy
from rclpy.node import Node
import RPi.GPIO as GPIO
import time
from std_msgs.msg import Bool

"""
This module defines a ROS2 node for publishing the state of a "jack" signal using Raspberry Pi GPIO.

Classes:
    JackPublisher(Node): 
        A ROS2 node that monitors a GPIO pin for a rising edge event (jack insertion/removal)
        and publishes a Bool message on the 'jack_signal' topic. The node uses a timer to
        periodically check for the event and publish the signal state.

Functions:
    main(args=None):
        Initializes the ROS2 node, starts spinning, and ensures proper cleanup of GPIO resources
        on shutdown or interruption.
"""

class JackPublisher(Node):
    def __init__(self):
        super().__init__('jack_publisher')
        self.publisher_ = self.create_publisher(Bool, 'jack_signal', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10hz
        self.msg = Bool()
        self.msg.data = False # should return it to false
        self.counter = 0
        # Set up GPIO pins
        GPIO.setmode(GPIO.BCM)
        self.JACK_PIN = 17
        GPIO.setup(self.JACK_PIN, GPIO.IN, GPIO.PUD_UP)

        # Set up edge detection
        GPIO.add_event_detect(self.JACK_PIN, GPIO.RISING, bouncetime=2000)

    def timer_callback(self):
        if GPIO.event_detected(self.JACK_PIN) :
            self.counter = self.counter + 1
            print("counter :",self.counter)
            if self.counter == 1 :##WAAAAAAAAS TWOOOOOooo need now to put the jack first
                self.get_logger().info("Rising edge detected!")
                self.msg.data = True
                time.sleep(0.01)


        self.publisher_.publish(self.msg)
        self.get_logger().info(f'Jack state: {self.msg.data}')

def main(args=None):
    rclpy.init(args=args)
    jack_publisher = JackPublisher()

    try:
        rclpy.spin(jack_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        jack_publisher.destroy_node()
        rclpy.shutdown()
        GPIO.cleanup()

if __name__ == '__main__':
    main()

