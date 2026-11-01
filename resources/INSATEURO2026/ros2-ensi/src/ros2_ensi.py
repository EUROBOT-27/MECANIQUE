#!/usr/bin/env python3
"""
Competition State Machine (ROS2 Version)
----------------------------------------
Simplified version of the Euro2025 SMACH logic for a robot
with these ordered tasks:
1. Number_Detection
2. Color Read
3. Detect Cubes & Triangles
4. Cans Task
5. Blue & Red Bars
6. Fingerprint Task
"""
import rclpy
from rclpy.node import Node
from enum import Enum
import smach
from std_msgs.msg import Int32
from geometry_msgs.msg import Pose2D
from ros_can_interface.msg import MasterAcknowledgSignal, MasterNavigationMessage, MasterResetSignal
import math
import signal
from ensi.srv import ColorService, NumberService, NumberTrianglesCubesService
import threading
import time
import RPi.GPIO as GPIO

TOTAL_PLAYING_TIME = 300
WAIT_TIME = 0.05
BUTTON_PIN = 17
LED_PIN = 26

GPIO.setup(BUTTON_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

# Global variables (replace ROS1 param server)
current_playing_time = 0
button_state_val = False
nav_currentX = 102
nav_currentY = 1300
nav_currentAngle = 0
current_nav_state = 0  # Global variable for navigation state from topic
next_direction = True
next_target_X = 0
next_target_Y = 0
current_direction = True



number = '0'  # single-character string for detected number
color = ''    # string variable for detected color

target_counter = 0
cube_id = -1
x_can = 0
y_can = 0
theta_can = 0
x_bar = 0
y_bar = 0
theta_bar = 0
robot_blocked = 0
number_target_counter = 0
color_target_counter = 0

# Counters for triangles and cubes detection
triangles_count = 0
cubes_count = 0

coordinates_list = [
    (500, 1300, 0, True),  # number detection spot
    (281.01, 1517.68, 132.95, True),  # color detection spot
    (712.81, 1154.53, 132.95, False),  # detect cubes and triangles spot
    (704.24, 926.71, 180, True),  # detect cubes and triangles spot
    (591.15, 925, 180, True),  # detect cubes and triangles spot
    (591.15, 925, 180, True),  # detect cubes and triangles spot
    (1691.22, 630.37, 270, False),  # position can 1
    (750, 400, 100, True),  # first (blue) bar
    (700, 500, 150, True),  # fingerprint task
]
coordinates_list_3 = [
    (500, 1300, 0, True),#0 initial position first can to push
    (281.01, 1517.68, 132.95, True),#1 final position first can to push
    (712.81, 1154.53, 132.95, False),#2 initial position second can to push
    (704.24, 926.71, 180, True),#3 final position second can to push
]
coordinates_list_5= [
    (500, 1300, 0, True),#0 initial position first can to push
    (281.01, 1517.68, 132.95, True),#1 final position first can to push
    (712.81, 1154.53, 132.95, False),#2 initial position second can to push
    (704.24, 926.71, 180, True),#3 final position second can to push
]
coordinates_list_6 = [
    (500, 1300, 0, True),#0 initial position first can to push
    (281.01, 1517.68, 132.95, True),#1 final position first can to push
    (712.81, 1154.53, 132.95, False),#2 initial position second can to push
    (704.24, 926.71, 180, True),#3 final position second can to push
]

coordinates_list_9= [
    (500, 1300, 0, True),#0 initial position first can to push
    (281.01, 1517.68, 132.95, True),#1 final position first can to push
    (712.81, 1154.53, 132.95, False),#2 initial position second can to push
    (704.24, 926.71, 180, True),#3 final position second can to push 
]
coordinates_list_red= [
    (500, 1300, 0, True),#0 first bar to push
    (281.01, 1517.68, 132.95, True),#1 second bar to push
]
coordinates_list_blue= [
    (500, 1300, 0, True),#0 first bar to push
    (281.01, 1517.68, 132.95, True),#1 second to push

]


class TaskType(Enum):
    NORMAL_NAV = 0
    DETECT_Number = 1
    DETECT_COLOR = 2
    DETECT_CUBE_Triangle = 3
    Push_Cans = 4
    Push_Bars = 5
    Fingerprint_Task = 6

    @staticmethod
    def task_handler():
        global target_counter
        global current_task
        if(target_counter == 1):
            current_task = TaskType.DETECT_Number
        elif (target_counter == 2):
            current_task = TaskType.DETECT_COLOR
        elif(target_counter in [3, 4, 5, 6]):
            current_task = TaskType.DETECT_CUBE_Triangle
        elif(target_counter == 7):
            current_task = TaskType.Push_Cans
        elif(target_counter == 8):
            current_task = TaskType.Push_Bars
        elif(target_counter == 9):
            current_task = TaskType.Fingerprint_Task
        else:
            current_task = TaskType.NORMAL_NAV

class MASTER_SMachineStates_ten(Enum):
    MASTER_SMachine_Idle_en = 0
    MASTER_SMachine_WaitForSignal_en = 1
    MASTER_SMachine_MoveOn_en = 2
    MASTER_SMachine_WaitToReach_en = 3
    MASTER_SMachine_DestinationReached_en = 4
    MASTER_SMachine_Finish_en = 7
    MASTER_SMachine_Init_en = 11

class MASTER_NavigatorStates_ten(Enum):
    MASTER_NavigatorIdle_en = 0
    MASTER_NavigatorReady_en = 1
    MASTER_NavigatorBusy_en = 2
    MASTER_NvigatorWaitToReceiveAcknowledge_en = 3
    MASTER_NavigatorReachedDest_en = 4
    MASTER_NavigatorConfirmedStop_en = 5
    MASTER_NavigatorInit_en = 6

global MASTER_SMachineCurrentState_en 
global MASTER_CurrentNavigatorState_en 
global current_task 

MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Idle_en
MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorIdle_en
current_task = TaskType.NORMAL_NAV


def button_state():
    while True:
        input_state = GPIO.input(BUTTON_PIN)
        if input_state == GPIO.HIGH:
            print("press!")
            time.sleep(0.2)
            return True
        time.sleep(0.01)

def nav_state_callback(msg):
    """Callback function for navigation state topic subscriber"""
    global current_nav_state
    current_nav_state = msg.data


class Publishers:
    def __init__(self, node):
        self.globalNavigator_Acknowledge_Publisher = node.create_publisher(MasterAcknowledgSignal, '/ros_can_interface/master_acknowledge', 10)
        self.Navigator_Target_Publisher = node.create_publisher(MasterNavigationMessage, '/ros_can_interface/navigation_data', 10)
        self.globalNavigator_Reset_Publisher = node.create_publisher(MasterResetSignal, '/ros_can_interface/master_reset', 10)
        
        # Subscribe to navigation state topic
        self.nav_state_subscriber = node.create_subscription(
            Int32,
            '/ros_can_interface/nav_currentState',
            nav_state_callback,
            10
        )

def color_request(node, max_retries=3, service_timeout=5.0):
    global color
    client = node.create_client(ColorService, 'detect_color')
    
    # Wait for service with timeout
    service_wait_count = 0
    while not client.wait_for_service(timeout_sec=1.0):
        service_wait_count += 1
        if service_wait_count > 5:  # Wait max 5 seconds for service
            node.get_logger().error('Color detection service not available after 5 seconds')
            return ''
        node.get_logger().info('Color detection service not available, waiting...')
    
    # Retry logic for service calls
    for attempt in range(max_retries):
        try:
            req = ColorService.Request()
            future = client.call_async(req)
            
            # Use timeout for service call
            start_time = time.time()
            while not future.done():
                rclpy.spin_once(node, timeout_sec=0.1)
                if time.time() - start_time > service_timeout:
                    node.get_logger().warning(f'Color service call timeout on attempt {attempt + 1}')
                    break
            
            if future.done() and future.result() is not None:
                detected_color = str(future.result().response_color).lower().strip()
                node.get_logger().info(f"Received color: {detected_color}")
                
                # Validate that color is red or blue
                if detected_color in ['red', 'blue']:
                    color = detected_color
                    return color
                else:
                    node.get_logger().warning(f'Invalid color detected: {detected_color}. Expected red or blue.')
                    if attempt < max_retries - 1:
                        node.get_logger().info(f'Retrying color detection... (attempt {attempt + 2}/{max_retries})')
                        time.sleep(0.5)  # Brief delay before retry
                    continue
            else:
                node.get_logger().warning(f'Color service call failed on attempt {attempt + 1}')
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Brief delay before retry
                    
        except Exception as e:
            node.get_logger().error(f'Color service call exception on attempt {attempt + 1}: {str(e)}')
            if attempt < max_retries - 1:
                time.sleep(0.5)
    
    # All retries failed
    node.get_logger().error(f'Color detection failed after {max_retries} attempts')
    return ''

def number_request(node, max_retries=3, service_timeout=5.0):
    global number
    client = node.create_client(NumberService, 'detect_number')
    
    # Wait for service with timeout
    service_wait_count = 0
    while not client.wait_for_service(timeout_sec=1.0):
        service_wait_count += 1
        if service_wait_count > 5:  # Wait max 5 seconds for service
            node.get_logger().error('Number detection service not available after 5 seconds')
            return '0'
        node.get_logger().info('Number detection service not available, waiting...')
    
    # Retry logic for service calls
    for attempt in range(max_retries):
        try:
            req = NumberService.Request()
            future = client.call_async(req)
            
            # Use timeout for service call
            start_time = time.time()
            while not future.done():
                rclpy.spin_once(node, timeout_sec=0.1)
                if time.time() - start_time > service_timeout:
                    node.get_logger().warning(f'Number service call timeout on attempt {attempt + 1}')
                    break
            
            if future.done() and future.result() is not None:
                detected_number = str(future.result().response_number).strip()
                node.get_logger().info(f"Received number: {detected_number}")
                
                # Validate that we got a valid number (first character)
                if detected_number and detected_number[0].isdigit():
                    number = detected_number[0]
                    return number
                else:
                    node.get_logger().warning(f'Invalid number detected: {detected_number}')
                    if attempt < max_retries - 1:
                        node.get_logger().info(f'Retrying number detection... (attempt {attempt + 2}/{max_retries})')
                        time.sleep(0.5)  # Brief delay before retry
                    continue
            else:
                node.get_logger().warning(f'Number service call failed on attempt {attempt + 1}')
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Brief delay before retry
                    
        except Exception as e:
            node.get_logger().error(f'Number service call exception on attempt {attempt + 1}: {str(e)}')
            if attempt < max_retries - 1:
                time.sleep(0.5)
    
    # All retries failed
    node.get_logger().error(f'Number detection failed after {max_retries} attempts')
    return '0'

def number_triangles_cubes_request(node, max_retries=3, service_timeout=5.0):
    global triangles_count, cubes_count
    client = node.create_client(NumberTrianglesCubesService, 'detect_triangles_cubes')
    
    # Wait for service with timeout
    service_wait_count = 0
    while not client.wait_for_service(timeout_sec=1.0):
        service_wait_count += 1
        if service_wait_count > 5:  # Wait max 5 seconds for service
            node.get_logger().error('Triangles/cubes detection service not available after 5 seconds')
            return ''
        node.get_logger().info('Triangles/cubes detection service not available, waiting...')
    
    # Retry logic for service calls
    for attempt in range(max_retries):
        try:
            req = NumberTrianglesCubesService.Request()
            future = client.call_async(req)
            
            # Use timeout for service call
            start_time = time.time()
            while not future.done():
                rclpy.spin_once(node, timeout_sec=0.1)
                if time.time() - start_time > service_timeout:
                    node.get_logger().warning(f'Triangles/cubes service call timeout on attempt {attempt + 1}')
                    break
            
            if future.done() and future.result() is not None:
                response = str(future.result().response_number_triangles_cubes).lower().strip()
                node.get_logger().info(f"Received triangles/cubes detection: {response}")
                
                # Count triangles and cubes
                if 'triangle' in response:
                    triangles_count += 1
                    node.get_logger().info(f"Triangle detected! Total triangles: {triangles_count}")
                    return 'triangle'
                elif 'cube' in response:
                    cubes_count += 1
                    node.get_logger().info(f"Cube detected! Total cubes: {cubes_count}")
                    return 'cube'
                else:
                    node.get_logger().warning(f'Invalid shape detected: {response}. Expected triangle or cube.')
                    if attempt < max_retries - 1:
                        node.get_logger().info(f'Retrying triangles/cubes detection... (attempt {attempt + 2}/{max_retries})')
                        time.sleep(0.5)  # Brief delay before retry
                    continue
            else:
                node.get_logger().warning(f'Triangles/cubes service call failed on attempt {attempt + 1}')
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Brief delay before retry
                    
        except Exception as e:
            node.get_logger().error(f'Triangles/cubes service call exception on attempt {attempt + 1}: {str(e)}')
            if attempt < max_retries - 1:
                time.sleep(0.5)
    
    # All retries failed
    node.get_logger().error(f'Triangles/cubes detection failed after {max_retries} attempts')
    return ''

def get_triangles_cubes_summary():
    """Return a summary of detected triangles and cubes"""
    global triangles_count, cubes_count
    return f"Triangles: {triangles_count}, Cubes: {cubes_count}"

def reset_triangles_cubes_counters():
    """Reset the triangles and cubes counters"""
    global triangles_count, cubes_count
    triangles_count = 0
    cubes_count = 0

def coordinates_generator(node):
    global target_counter
    global current_task
    global coordinates_list
    global number
    global color
    navigation_target = None
    if(current_task == TaskType.NORMAL_NAV):
        next_target_x = coordinates_list[target_counter][0]
        next_target_y = coordinates_list[target_counter][1]
        next_target_angle = coordinates_list[target_counter][2]
        next_direction = set_direction()
        navigation_target = MasterNavigationMessage(next_target_x,
                                                     next_target_y,
                                                     next_target_angle,
                                                     next_direction,
                                                     1, 1, 0, 0)
    elif(current_task == TaskType.Push_Cans and number == '3'):
        next_target_x = coordinates_list_3[number_target_counter][0]
        next_target_y = coordinates_list_3[number_target_counter][1]
        next_target_angle = coordinates_list_3[number_target_counter][2]
        next_direction = number_set_direction('3')
        navigation_target = MasterNavigationMessage(next_target_x,
                                                     next_target_y,
                                                     next_target_angle,
                                                     next_direction,
                                                     1, 1, 0, 0)
    elif(current_task == TaskType.Push_Cans and number == '5'):
        next_target_x = coordinates_list_5[number_target_counter][0]
        next_target_y = coordinates_list_5[number_target_counter][1]
        next_target_angle = coordinates_list_5[number_target_counter][2]
        next_direction = number_set_direction('5')
        navigation_target = MasterNavigationMessage(next_target_x,
                                                     next_target_y,
                                                     next_target_angle,
                                                     next_direction,
                                                     1, 1, 0, 0)
    elif(current_task == TaskType.Push_Cans and number == '6'):
        next_target_x = coordinates_list_6[number_target_counter][0]
        next_target_y = coordinates_list_6[number_target_counter][1]
        next_target_angle = coordinates_list_6[number_target_counter][2]
        next_direction = number_set_direction('6')
        navigation_target = MasterNavigationMessage(next_target_x,
                                                     next_target_y,
                                                     next_target_angle,
                                                     next_direction,
                                                     1, 1, 0, 0)
    elif(current_task == TaskType.Push_Cans and number == '9'):
        next_target_x = coordinates_list_9[number_target_counter][0]
        next_target_y = coordinates_list_9[number_target_counter][1]
        next_target_angle = coordinates_list_9[number_target_counter][2]
        next_direction = number_set_direction('9')
        navigation_target = MasterNavigationMessage(next_target_x,
                                                     next_target_y,
                                                     next_target_angle,
                                                     next_direction,
                                                     1, 1, 0, 0)
    elif(current_task == TaskType.Push_Bars and color == "blue"):
        next_target_x = coordinates_list_blue[color_target_counter][0]
        next_target_y = coordinates_list_blue[color_target_counter][1]
        next_target_angle = coordinates_list_blue[color_target_counter][2]
        next_direction = set_direction()
        navigation_target = MasterNavigationMessage(next_target_x,
                                                     next_target_y,
                                                     next_target_angle,
                                                     next_direction,
                                                     1, 1, 0, 0)
    elif(current_task == TaskType.Push_Bars and color == "red"):
        next_target_x = coordinates_list_red[color_target_counter][0]
        next_target_y = coordinates_list_red[color_target_counter][1]
        next_target_angle = coordinates_list_red[color_target_counter][2]
        next_direction = set_direction()
        navigation_target = MasterNavigationMessage(next_target_x,
                                                     next_target_y,
                                                     next_target_angle,
                                                     next_direction,
                                                     1, 1, 0, 0)
    else:
        node.get_logger().error("Error with detecting TaskType")
        return None
    return navigation_target

class Navigation:
    communication_wait_time = 0.2

    @staticmethod
    def acknowledge_order(node, publishers):
        acknowlegeSignal = MasterAcknowledgSignal()
        acknowlegeSignal.master_acknowledge_signal = True
        publishers.globalNavigator_Acknowledge_Publisher.publish(acknowlegeSignal)

    @staticmethod
    def target_order(node, publishers, navigation_target):
        publishers.Navigator_Target_Publisher.publish(navigation_target)

    @staticmethod
    def init_order():
        init_status = (102, 1300, 0)
        return MasterNavigationMessage(init_status[0],
                                        init_status[1],
                                        init_status[2],
                                        True,
                                        0, 0, 0, 0)

    @staticmethod
    def reset_order(node, publishers):
        resetSignal = MasterResetSignal()
        resetSignal.master_reset_signal = True
        publishers.globalNavigator_Reset_Publisher.publish(resetSignal)

def exit_handler(sig, frame):
    print('Ctrl+C pressed. Exiting...')
    rclpy.shutdown()

def Order_Finish_Stop(node, publishers):
    global current_playing_time
    if current_playing_time >= TOTAL_PLAYING_TIME:
        Navigation.reset_order(node, publishers)

def set_direction():
    global target_counter
    global robot_blocked
    global coordinates_list
    if robot_blocked:
        next_direction = not coordinates_list[target_counter + 1][3]
    else:
        next_direction = coordinates_list[target_counter][3]
    robot_blocked = False
    return next_direction

def number_set_direction(number):
    global number_target_counter
    global robot_blocked
    if robot_blocked:
        if number == '3':
            next_direction = not coordinates_list_3[number_target_counter + 1][3]
        if number == '5':
            next_direction = not coordinates_list_5[number_target_counter + 1][3]
        if number == '6':
            next_direction = not coordinates_list_6[number_target_counter + 1][3]
        if number == '9':
            next_direction = not coordinates_list_9[number_target_counter + 1][3]
    else:
        if number == '3':
            next_direction = coordinates_list_3[number_target_counter][3]
        if number == '5':
            next_direction = coordinates_list_5[number_target_counter][3]
        if number == '6':
            next_direction = coordinates_list_6[number_target_counter][3]
        if number == '9':
            next_direction = coordinates_list_9[number_target_counter][3]
    robot_blocked = False
    return next_direction

# SMACH States (updated with proper publishers parameter)
class Idle(smach.State):
    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: Idle', 'Go to: Init'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        global current_nav_state
        signal.signal(signal.SIGINT, exit_handler)
        Navigation.acknowledge_order(self.node, self.publishers)
        time.sleep(Navigation.communication_wait_time)
        if current_nav_state == 8:
            return 'Go to: Init'
        else:
            return 'Go to: Idle'

class Init(smach.State):
    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: Init', 'Go to: WaitForSignal'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        global current_nav_state
        signal.signal(signal.SIGINT, exit_handler)
        if current_nav_state == 1:
            return 'Go to: WaitForSignal'
        else:
            return 'Go to: Init'

class WaitForSignal(smach.State):
    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: MoveOn', 'Go to: WaitForSignal'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        global current_nav_state
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.1)
        global button_state_val
        button_state_val = button_state()
        if button_state_val and current_nav_state == 1:
            time.sleep(1)
            return 'Go to: MoveOn'
        else:
            return 'Go to: WaitForSignal'

class MoveOn(smach.State):
    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: WaitToReach', 'Go to: MoveOn', 'Go to: MoveOn_Push_Cans'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        global current_nav_state
        signal.signal(signal.SIGINT, exit_handler)
        global current_task, number, color
        Order_Finish_Stop(self.node, self.publishers)
        if current_nav_state in [9, 10, 7]:
            Navigation.acknowledge_order(self.node, self.publishers)
            time.sleep(Navigation.communication_wait_time)
        if current_task in [TaskType.NORMAL_NAV, TaskType.Push_Cans, TaskType.Push_Bars]:
            navigation_target = coordinates_generator(self.node)
        elif current_task == TaskType.DETECT_Number:
            number = number_request(self.node)
            if number == '0' or number == '':  # Service failed or invalid number
                self.node.get_logger().warning("Number detection failed, retrying...")
                return 'Go to: MoveOn'  # Stay in current state to retry
            current_task = TaskType.NORMAL_NAV
            return 'Go to: MoveOn'
        elif current_task == TaskType.DETECT_COLOR:
            color = color_request(self.node)
            if color == '':  # Service failed
                self.node.get_logger().warning("Color detection failed, retrying...")
                return 'Go to: MoveOn'  # Stay in current state to retry
            elif color == "red":
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(3)
                GPIO.output(LED_PIN, GPIO.LOW)
                self.node.get_logger().info("Red color detected - LED activated")
            elif color == "blue":
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(3)
                GPIO.output(LED_PIN, GPIO.LOW)
                self.node.get_logger().info("Blue color detected - LED activated")
            else:
                self.node.get_logger().warning(f"Unexpected color detected: {color}. Continuing without LED activation.")
            current_task = TaskType.NORMAL_NAV
            return 'Go to: MoveOn'
        elif current_task == TaskType.DETECT_CUBE_Triangle:
            detection_result = number_triangles_cubes_request(self.node)
            if detection_result == '':  # Service failed
                self.node.get_logger().warning("Triangles/cubes detection failed, retrying...")
                return 'Go to: MoveOn'  # Stay in current state to retry
            self.node.get_logger().info(f"Shape detection completed: {detection_result}")
            self.node.get_logger().info(f"Current count - {get_triangles_cubes_summary()}")
            current_task = TaskType.NORMAL_NAV
            return 'Go to: MoveOn'
        elif current_task == TaskType.Push_Cans:
            return 'Go to: MoveOn_Push_Cans'
        else:
            self.node.get_logger().error("Error with detecting TaskType")
            return 'Go to: MoveOn'
        if navigation_target:
            Navigation.target_order(self.node, self.publishers, navigation_target)
            time.sleep(Navigation.communication_wait_time)
        if current_nav_state == 2:
            return 'Go to: WaitToReach'
        elif current_nav_state == 3:
            Navigation.acknowledge_order(self.node, self.publishers)
            time.sleep(Navigation.communication_wait_time)
            return 'Go to: MoveOn'
        else:
            return 'Go to: MoveOn'
        
class WaitToReach(smach.State):  # starts moving here

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=[
            'Go to: DestinationReached',
            'Go to: WaitToReach',
            'Go to: BlockageDetected',
            'Go to: CansDestinationReached',
            'Go to: BarDestinationReached',
        ])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.1)
        self.node.get_clock().sleep_for(rclpy.duration.Duration(seconds=0.05))
        Order_Finish_Stop(self.node, self.publishers)
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global target_counter
        global current_nav_state

        if current_nav_state == 3 and target_counter != 7:
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NvigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_DestinationReached_en
            return 'Go to: DestinationReached'
        elif current_nav_state == 3 and target_counter == 7:
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NvigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_DestinationReached_en
            return 'Go to: CansDestinationReached'
        elif current_nav_state == 3 and target_counter == 8:
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NvigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_DestinationReached_en
            return 'Go to: BarDestinationReached'
        elif current_nav_state == 9 or current_nav_state == 10:
            return 'Go to: BlockageDetected'
        else:
            return 'Go to: WaitToReach'

class BlockageDetected(smach.State):

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: MoveOn', 'Go to: BlockageDetected'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        global target_counter
        global robot_blocked
        robot_blocked = True
        Order_Finish_Stop(self.node, self.publishers)
        if target_counter >= 1:
            target_counter = target_counter - 1
            return 'Go to: MoveOn'
        else:
            self.node.get_logger().info("error target counter = 0")
            return 'Go to: BlockageDetected'

class DestinationReached(smach.State):

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=[
            'Go to: MoveOn',
            'Go to: DestinationReached',
            'Go to: Finished',
            'Go to: MoveOn_bars',
        ])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)
        Order_Finish_Stop(self.node, self.publishers)

        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global target_counter
        global current_task
        global number_target_counter

        length_of_list = len(coordinates_list)
        Navigation.acknowledge_order(self.node, self.publishers)
        time.sleep(Navigation.communication_wait_time)
        time.sleep(0.05)

        if current_nav_state == 1:
            if current_task != TaskType.Push_Bars and current_task != TaskType.Push_Cans:
                target_counter += 1
                number_target_counter = 0
                TaskType.task_handler()
                if current_task == TaskType.Push_Bars:
                    return 'Go to: MoveOn_bars'

                if target_counter >= length_of_list:
                    return 'Go to: Finished'
                else:
                    return 'Go to: MoveOn'
        else:
            return 'Go to: DestinationReached'

class MoveOn_Push_Cans(smach.State):

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: WaitToReach', 'Go to: MoveOn_Push_Cans'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)

        global current_task
        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en

        Order_Finish_Stop(self.node, self.publishers)

        if current_nav_state in [9, 10, 7]:
            Navigation.acknowledge_order(self.node, self.publishers)
            time.sleep(Navigation.communication_wait_time)

        navigation_target = coordinates_generator(self.node)

        Navigation.target_order(self.node, self.publishers, navigation_target)
        time.sleep(Navigation.communication_wait_time)

        time.sleep(Navigation.communication_wait_time)

        if current_nav_state == 2:
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitToReach_en
            return 'Go to: WaitToReach'
        elif current_nav_state == 3:
            Navigation.acknowledge_order(self.node, self.publishers)
            time.sleep(Navigation.communication_wait_time)
            return 'Go to: MoveOn_Push_Cans'
        else:
            return 'Go to: MoveOn_Push_Cans'

class MoveOn_bars(smach.State):

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: WaitToReach', 'Go to: MoveOn_bars'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)

        global current_task
        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en

        Order_Finish_Stop(self.node, self.publishers)

        if current_nav_state in [9, 10, 7]:
            Navigation.acknowledge_order(self.node, self.publishers)
            time.sleep(Navigation.communication_wait_time)

        navigation_target = coordinates_generator(self.node)

        Navigation.target_order(self.node, self.publishers, navigation_target)
        time.sleep(Navigation.communication_wait_time)

        time.sleep(Navigation.communication_wait_time)

        if current_nav_state == 2:
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitToReach_en
            return 'Go to: WaitToReach'
        elif current_nav_state == 3:
            Navigation.acknowledge_order(self.node, self.publishers)
            time.sleep(Navigation.communication_wait_time)
            return 'Go to: MoveOn_bars'
        else:
            return 'Go to: MoveOn_bars'

class CansDestinationReached(smach.State):

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=[
            'Go to: MoveOn',
            'Go to: CansDestinationReached',
            'Go to: Finished',
            'Go to:MoveOn_Push_Cans',
        ])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)
        Order_Finish_Stop(self.node, self.publishers)

        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global target_counter
        global current_task
        global number_target_counter
        global number
        global coordinates_list_3, coordinates_list_5, coordinates_list_6, coordinates_list_9

        length_of_list_3 = len(coordinates_list_3)
        length_of_list_6 = len(coordinates_list_6)
        length_of_list_9 = len(coordinates_list_9)
        length_of_list_5 = len(coordinates_list_5)

        Navigation.acknowledge_order(self.node, self.publishers)
        time.sleep(Navigation.communication_wait_time)
        time.sleep(0.05)

        if current_nav_state == 1:
            if current_task == TaskType.Push_Cans:
                number_target_counter += 1
                TaskType.task_handler()
                if number == '3':
                    if number_target_counter >= length_of_list_3:
                        current_task = TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans'
                if number == '6':
                    if number_target_counter >= length_of_list_6:
                        current_task = TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans'
                if number == '9':
                    if number_target_counter >= length_of_list_9:
                        current_task = TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans'
                if number == '5':
                    if number_target_counter >= length_of_list_5:
                        current_task = TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans'
            else:
                self.node.get_logger().error('Unknown or missing number for Push_Cans logic.')
                return 'Go to: CansDestinationReached'
        else:
            return 'Go to: CansDestinationReached'

class BarDestinationReached(smach.State):

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=[
            'Go to: MoveOn',
            'Go to: DestinationReached',
            'Go to: Finished',
            'Go to:MoveOn_bars',
            'Go to: BarDestinationReached',
        ])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)
        Order_Finish_Stop(self.node, self.publishers)

        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global target_counter
        global current_task
        global color_target_counter
        global color  # Use color instead of color_response
        global coordinates_list_red
        global coordinates_list_blue

        length_of_list_red = len(coordinates_list_red)
        length_of_list_blue = len(coordinates_list_blue)

        Navigation.acknowledge_order(self.node, self.publishers)
        time.sleep(Navigation.communication_wait_time)
        time.sleep(0.05)

        if current_nav_state == 1:
            if current_task == TaskType.Push_Bars:
                color_target_counter += 1
                TaskType.task_handler()
                if color == 'red':
                    # TODO: Add servo mechanism here if needed
                    if color_target_counter >= length_of_list_red:
                        current_task = TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_bars'
                if color == 'blue':
                    # TODO: Add servo mechanism here if needed
                    if color_target_counter >= length_of_list_blue:
                        current_task = TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_bars'
            else:
                self.node.get_logger().error('Unknown or missing color for Push_Bars logic.')
                return 'Go to: BarDestinationReached'
        else:
            return 'Go to: BarDestinationReached'

class Finished(smach.State):

    def __init__(self, node, publishers):
        smach.State.__init__(self, outcomes=['Go to: Finished'])
        self.node = node
        self.publishers = publishers

    def execute(self, userdata):
        import signal
        signal.signal(signal.SIGINT, exit_handler)
        import time
        time.sleep(0.05)
        return 'Go to: Finished'

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('hafnaoui')
    
    publishers = Publishers(node)
    
    # Initialize global variables
    global current_task, MASTER_SMachineCurrentState_en, MASTER_CurrentNavigatorState_en
    current_task = TaskType.NORMAL_NAV
    MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Idle_en
    MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorIdle_en
    
    # Start timer thread if needed
    
    sm = smach.StateMachine(outcomes=['NavigatorReached'])
    with sm:
        smach.StateMachine.add('Idle', Idle(node, publishers),
                               transitions={'Go to: Idle': 'Idle',
                                            'Go to: Init': 'Init'})
        smach.StateMachine.add('Init', Init(node, publishers),
                               transitions={'Go to: Init': 'Init',
                                            'Go to: WaitForSignal': 'WaitForSignal'})
        smach.StateMachine.add('WaitForSignal', WaitForSignal(node, publishers),
                               transitions={'Go to: WaitForSignal': 'WaitForSignal',
                                            'Go to: MoveOn': 'MoveOn'})
        smach.StateMachine.add('MoveOn', MoveOn(node, publishers),
                               transitions={'Go to: WaitToReach': 'WaitToReach',
                                            'Go to: MoveOn': 'MoveOn',
                                            'Go to: MoveOn_Push_Cans': 'MoveOn_Push_Cans'})
        smach.StateMachine.add('WaitToReach', WaitToReach(node, publishers),
                               transitions={'Go to: DestinationReached': 'DestinationReached',
                                            'Go to: WaitToReach': 'WaitToReach',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            'Go to: CansDestinationReached': 'CansDestinationReached',
                                            'Go to: BarDestinationReached': 'BarDestinationReached'})
        smach.StateMachine.add('BlockageDetected', BlockageDetected(node, publishers),
                               transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: BlockageDetected': 'BlockageDetected'})
        smach.StateMachine.add('DestinationReached', DestinationReached(node, publishers),
                               transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: DestinationReached': 'DestinationReached',
                                            'Go to: Finished': 'Finished',
                                            'Go to: MoveOn_bars': 'MoveOn_bars'})
        smach.StateMachine.add('MoveOn_Push_Cans', MoveOn_Push_Cans(node, publishers),
                               transitions={'Go to: WaitToReach': 'WaitToReach',
                                            'Go to: MoveOn_Push_Cans': 'MoveOn_Push_Cans'})
        smach.StateMachine.add('MoveOn_bars', MoveOn_bars(node, publishers),
                               transitions={'Go to: WaitToReach': 'WaitToReach',
                                            'Go to: MoveOn_bars': 'MoveOn_bars'})
        smach.StateMachine.add('CansDestinationReached', CansDestinationReached(node, publishers),
                               transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: CansDestinationReached': 'CansDestinationReached',
                                            'Go to: Finished': 'Finished',
                                            'Go to:MoveOn_Push_Cans': 'MoveOn_Push_Cans',
                                            })
        smach.StateMachine.add('BarDestinationReached', BarDestinationReached(node, publishers),
                               transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: DestinationReached': 'DestinationReached',
                                            'Go to: Finished': 'Finished',
                                            'Go to:MoveOn_bars': 'MoveOn_bars',
                                            'Go to: BarDestinationReached': 'BarDestinationReached'})
        smach.StateMachine.add('Finished', Finished(node, publishers),
                               transitions={'Go to: Finished': 'Finished'})
    
    # Visualization: smach_ros.IntrospectionServer is not available in ROS2
    outcome = sm.execute()
    signal.signal(signal.SIGINT, exit_handler)
    Order_Finish_Stop(node, publishers)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


