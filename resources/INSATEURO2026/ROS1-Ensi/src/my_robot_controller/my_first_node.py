#!/usr/bin/env python3
#ros1
"""
Competition State Machine
-------------------------
Simplified version of the Euro2025 SMACH logic for a robot
with these ordered tasks:
1. Number_Detection
2. Color Read
3. Detect Cubes & Triangles
4. Cans Task
5. Blue & Red Bars
6. Fingerprint Task
"""
import rospy
from enum import Enum
import smach
import smach_ros
from std_msgs.msg import (Bool, Float32MultiArray, Int8, Int8MultiArray,
                          Int32MultiArray, String, Int32)
from geometry_msgs.msg import Pose2D
from ros_can_interface.msg import master_acknowledgSignal, master_navigationMessage, lidar_stopSignal, master_resetSignal
import math
import signal
from ensi1.srv import color_service, color_serviceResponse, number_service, number_serviceResponse, number__triangles_cubes_service, number__triangles_cubes_serviceResponse
import threading
import time
import RPi.GPIO as GPIO

#this is a comment

"""STM32 State:

    0:MASTER_NavigatorIdle_en,                        
    1:MASTER_NavigatorReady_en,                       
    2:MASTER_NavigatorBusy_en,                        
	3:MASTER_NavigatorWaitToReceiveAcknowledge_en,        
    4:MASTER_NavigatorReachedDest_en,                
	5:MASTER_NavigatorOrderSuddenStop_en,             
	6:MASTER_NavigatorSuddenStop_en,                  
	7:MASTER_NavigatorConfirmedStop_en,              
	8:MASTER_NavigatorInit_en,                        
	9:MASTER_NavigatorBlockageDetected_en,           
	10:MASTER_NavigatorWallBlockageDetected_en         
    """


TOTAL_PLAYING_TIME = 300
WAIT_TIME = 0.05
rospy.set_param('current_playing_time', 0)
BUTTON_PIN=17
LED_PIN = 26
button_state = False

GPIO.setup(BUTTON_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

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
         ####we should fix coordinates and changes their ids here
        if(target_counter == 1 ):
            current_task=TaskType.DETECT_Number
        elif (target_counter == 2):
            current_task=TaskType.DETECT_COLOR
        elif(target_counter == 3 or target_counter == 4 or target_counter == 5 or target_counter == 6):
            current_task=TaskType.DETECT_CUBE_Triangle
        elif(target_counter == 7 ):
            current_task=TaskType.Push_Cans
        elif(target_counter == 8 ):
            current_task=TaskType.Push_Bars
        elif(target_counter == 19):
            current_task=TaskType.Fingerprint_Task
        else:
            current_task=TaskType.NORMAL_NAV

class MASTER_SMachineStates_ten (Enum):

    MASTER_SMachine_Idle_en = 0
    MASTER_SMachine_WaitForSignal_en = 1
    MASTER_SMachine_MoveOn_en = 2
    MASTER_SMachine_WaitToReach_en = 3
    MASTER_SMachine_DestinationReached_en = 4
    MASTER_SMachine_Finish_en = 7
    MASTER_SMachine_Init_en = 11

class MASTER_NavigatorStates_ten (Enum):

    MASTER_NavigatorIdle_en = 0
    MASTER_NavigatorReady_en = 1
    MASTER_NavigatorBusy_en = 2
    MASTER_NvigatorWaitToReceiveAcknowledge_en = 3
    MASTER_NavigatorReachedDest_en = 4
    MASTER_NavigatorConfirmedStop_en = 5
    MASTER_NavigatorInit_en = 6

##################################### BUTTON FUNCTION  ###############################


def button_state():
    while True:
        input_state = GPIO.input(17)
        if input_state==GPIO.HIGH:
            print("press!")
            time.sleep(0.2)
            return True
        time.sleep(0.01)


##################################### DECLARE VARIABLES HERE INIT #####################################

MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Idle_en
MASTER_NavigatorCurrentState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorIdle_en
current_task = TaskType.NORMAL_NAV
current_direction = True # True: forward, False: backward
next_direction = True
task_entry_direction = True
target_counter = 0
cube_id = -1
x_can=0
y_can=0
theta_can=0
x_bar=0
y_bar=0
theta_bar=0
robot_blocked = 0
number_target_counter = 0
color_target_counter = 0

coordinates_list = [
    (500, 1300, 0, True),#0 #number detection spot
    (281.01, 1517.68, 132.95, True),#1 #color detection spot
    (712.81, 1154.53, 132.95, False),#2 #detect cubes and triangles spot
    (704.24, 926.71, 180, True),#3 #detect cubes and triangles spot
    (591.15, 925, 180, True),#4  #detect cubes and triangles spot
    (591.15, 925, 180, True),#5   #detect cubes and triangles spot
    (1691.22, 630.37, 270, False), #6 position can 1
    (750, 400, 100, True),#7 first (blue) bar 
    (700, 500, 150, True),#8 #11 fingerprint task
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


##initial coordinates
rospy.set_param('nav_currentX', 102)
rospy.set_param('nav_currentY', 1300)
rospy.set_param('nav_currentAngle', 0)
rospy.set_param('current_state', 0)
rospy.set_param('next_direction', True)
rospy.set_param('next_target_X', 0)
rospy.set_param('next_target_Y', 0)
rospy.set_param('current_direction', current_direction)
rospy.set_param('next_direction', next_direction)
rospy.set_param('jack', False)


##################################### GAME TIMER FUNCTION ##########################################
def timer_thread():
    global current_playing_time
    rate = rospy.Rate(1)  # 1 Hz

    while not rospy.is_shutdown():
        jack = rospy.get_param('jack')
        if (jack == 1):
            current_playing_time += 1.0  # Increment by 1 second
            rospy.set_param('current_playing_time', current_playing_time)
            rate.sleep()

#################################### CREATE A CLASS OF PUBLISHERS #################################

class Publishers:
    globalNavigator_Acknowledge_Publisher = rospy.Publisher('/ros_can_interface/master_acknowledge', master_acknowledgSignal, queue_size=10)
    Navigator_Target_Publisher = rospy.Publisher('/ros_can_interface/navigation_data', master_navigationMessage, queue_size=10)
    globalNavigator_Reset_Publisher = rospy.Publisher('/ros_can_interface/master_reset', master_resetSignal, queue_size=10)


##################################### COLOR REQUEST FUNCTION #######################################
def color_request():
    global color_response
    print("got into server request")
    rospy.wait_for_service('detect_color')
    print("got into server request")
    try:
        print("got into try loop")
        get_color = rospy.ServiceProxy('detect_color', color_service)
        color_response = get_color() 
        rospy.loginfo(f"Received color: {color_response.response_color}")
        returned_resp= "got color"
        return returned_resp
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)

##################################### Number REQUEST FUNCTION #######################################
def number_request():
    global number_response
    print("got into server request")
    rospy.wait_for_service('detect_number')
    print("got into server request")
    try:
        print("got into try loop")
        get_number = rospy.ServiceProxy('detect_number', number_service)
        number_response = get_number() 
        rospy.loginfo(f"Received number: {number_response.response_number}")
        returned_resp = str(number_response.response_number)[0]  # Store as single char
        return returned_resp
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)

##################################### Number of triangles and cubes REQUEST FUNCTION #######################################
def number_triangles_cubes_request():
    global number_triangles_cubes_response
    print("got into server request")
    rospy.wait_for_service('detect_triangles_cubes')
    print("got into server request")
    try:
        print("got into try loop")
        get_Number_triangles_cubes = rospy.ServiceProxy('detect_triangles_cubes', number__triangles_cubes_service)
        number_triangles_cubes_response = get_Number_triangles_cubes() 
        rospy.loginfo(f"Received color: {number_triangles_cubes_response.response_number_triangles_cubes}")
        returned_resp= "got number of triangles and cubes"
        return returned_resp
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)

##################################### NAV COORDINATES FUNTCION #######################################

def coordinates_generator():
    global target_counter
    global current_task
    global coordinates_list
    if(current_task == TaskType.NORMAL_NAV ):
            next_target_x=coordinates_list[target_counter][0]
            next_target_y=coordinates_list[target_counter][1]
            next_target_angle=coordinates_list[target_counter][2]
            next_direction = set_direction()
            navigation_target = master_navigationMessage(next_target_x,
                                            next_target_y,
                                            next_target_angle,
                                            next_direction,
                                            1,
                                            1,
                                            0,
                                            0
                                            )
    if(current_task == TaskType.Push_Cans and number == 3):
            next_target_x=coordinates_list_3[number_target_counter][0]
            next_target_y=coordinates_list_3[number_target_counter][1]
            next_target_angle=coordinates_list_3[number_target_counter][2]
            next_direction = number_set_direction()
            navigation_target = master_navigationMessage(next_target_x,
                                            next_target_y,
                                            next_target_angle,
                                            next_direction,
                                            1,
                                            1,
                                            0,
                                            0
                                            )           #should treat blockage direction
    if(current_task == TaskType.Push_Cans and number== 5):
            next_target_x=coordinates_list_5[number_target_counter][0]
            next_target_y=coordinates_list_5[number_target_counter][1]
            next_target_angle=coordinates_list_5[number_target_counter][2]
            next_direction = number_set_direction()
            navigation_target = master_navigationMessage(next_target_x,
                                            next_target_y,
                                            next_target_angle,
                                            next_direction,
                                            1,
                                            1,
                                            0,
                                            0
                                            )           #should treat blockage direction
    if(current_task == TaskType.Push_Cans and number== 6):
            next_target_x=coordinates_list_6[number_target_counter][0]
            next_target_y=coordinates_list_6[number_target_counter][1]
            next_target_angle=coordinates_list_6[number_target_counter][2]
            next_direction = number_set_direction()
            navigation_target = master_navigationMessage(next_target_x,
                                            next_target_y,
                                            next_target_angle,
                                            next_direction,
                                            1,
                                            1,
                                            0,
                                            0
                                            )           #should treat blockage direction
    if(current_task == TaskType.Push_Cans and number== 9):
            next_target_x=coordinates_list_3[number_target_counter][0]
            next_target_y=coordinates_list_3[number_target_counter][1]
            next_target_angle=coordinates_list_3[number_target_counter][2]
            next_direction = number_set_direction()
            navigation_target = master_navigationMessage(next_target_x,
                                            next_target_y,
                                            next_target_angle,
                                            next_direction,
                                            1,
                                            1,
                                            0,
                                            0
                                            )           #should treat blockage direction
    if(current_task == TaskType.Push_Bars and color_response.response_color == "blue"):
            next_target_x=coordinates_list_blue[color_target_counter][0]
            next_target_y=coordinates_list_blue[color_target_counter][1]
            next_target_angle=coordinates_list_blue[color_target_counter][2]
            next_direction = color_set_direction() #?????????????????????????????????????????????
            navigation_target = master_navigationMessage(next_target_x,
                                            next_target_y,
                                            next_target_angle,
                                            next_direction,
                                            1,
                                            1,
                                            0,
                                            0
                                            )       
    if(current_task == TaskType.Push_Bars and color_response.response_color == "red"):
            next_target_x=coordinates_list_red[color_target_counter][0]
            next_target_y=coordinates_list_red[color_target_counter][1]
            next_target_angle=coordinates_list_red[color_target_counter][2]
            next_direction = color_set_direction()
            navigation_target = master_navigationMessage(next_target_x,
                                            next_target_y,
                                            next_target_angle,
                                            next_direction,
                                            1,
                                            1,
                                            0,
                                            0
                                            )       
    else:
        rospy.logerr("Error with detecting TaskType")
        return 'Go to: MoveOn'   
    return navigation_target  

################################# MECHANISME FUNCTION CALLS ###############################

    
class Navigation:
    # Constants
    communication_wait_time = 0.2
    
    @staticmethod
    def acknowledge_order():
        acknowlegeSignal = master_acknowledgSignal()
        acknowlegeSignal.master_acknowledgeSignal = True
        Publishers.globalNavigator_Acknowledge_Publisher.publish(acknowlegeSignal)

    @staticmethod
    def target_order(navigation_target):
        Publishers.Navigator_Target_Publisher.publish(navigation_target)
        
    @staticmethod
    def check_current_state():
        return rospy.get_param('nav_currentState')
    
    @staticmethod
    def init_order():
        init_status = (102,1300,0) #must be changed
        return master_navigationMessage(init_status[0],
                                        init_status[1],
                                        init_status[2],
                                        True,
                                        0,
                                        0,
                                        0,
                                        0
                                        )
    
    @staticmethod
    def reset_order():
        resetSignal = master_resetSignal()
        resetSignal.master_resetSignal = True
        Publishers.globalNavigator_Reset_Publisher.publish(resetSignal)

#################################### SPECIAL EXIT HANDLING #######################################


def exit_handler(sig, frame) -> None:

    print('Ctrl+C pressed. Exiting...')

    rospy.signal_shutdown('State machine execution completed')


##################################### UTILITY FUNCTIONS ###############################



def Order_Finish_Stop():
    current_playing_time = rospy.get_param('current_playing_time')

    if current_playing_time >= TOTAL_PLAYING_TIME:
        Navigation.reset_order()

#####################################  SETTING ROBOT DIRECTION FUNTCION #######################################
def set_direction():
    global target_counter
    global robot_blocked
    global coordinates_list
    

    if (robot_blocked == True):
        next_direction = not (coordinates_list[target_counter + 1][3])
    else :
        next_direction = coordinates_list[target_counter][3]
    robot_blocked == False
    return next_direction   

def number_set_direction():
    global number_target_counter
    global robot_blocked
    global coordinates_list
    

    if (robot_blocked == True):
        next_direction = not (coordinates_list[number_target_counter + 1][3])
    else :
        next_direction = coordinates_list[number_target_counter][3]
    robot_blocked == False
    return next_direction          
    

##################################### STATE MACHINE CLASSES #######################################

class Idle(smach.State):    
     
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Idle',
                                             'Go to: Init'])

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        Navigation.acknowledge_order()
        rospy.sleep(Navigation.communication_wait_time)
        if ( Navigation.check_current_state() == 8 ):  
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorReady_en 
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitForSignal_en
                        
            return 'Go to: Init'
        
        else:
            return 'Go to: Idle'

class Init(smach.State):    
     
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Init',
                                             'Go to: WaitForSignal'])

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)

        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en

        
        if ( Navigation.check_current_state() == 1 ):  
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorReady_en 
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitForSignal_en
                        
            return 'Go to: WaitForSignal'
        
        else:
            return 'Go to: Init'
        
class WaitForSignal(smach.State):
  
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn', 'Go to: WaitForSignal'],
                             )

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        global button_state
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        rospy.sleep(0.1)
        button_state = button_state()
	#adem:should return jack_state into True
        if ( ( button_state == True ) and ( MASTER_CurrentNavigatorState_en == MASTER_NavigatorStates_ten.MASTER_NavigatorReady_en  ) ):
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_MoveOn_en
            rospy.sleep(1)
            
            return 'Go to: MoveOn'
          
        else:
            return 'Go to: WaitForSignal'
        
class MoveOn(smach.State):
    
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['Go to: WaitToReach', 'Go to: MoveOn','Go to: MoveOn_Push_Cans_3'])

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)

        global current_task
        global coordinates_list 
        global MASTER_SMachineCurrentState_en    
        global MASTER_CurrentNavigatorState_en
        global color_response
        global target_counter
        global number

        Order_Finish_Stop()
        current_state = rospy.get_param('nav_currentState')

        if current_state == 9 or current_state == 10 or current_state == 7:
            Navigation.acknowledge_order()
            rospy.sleep(Navigation.communication_wait_time)

        if(current_task == TaskType.NORMAL_NAV or current_task== TaskType.Push_Cans or current_task== TaskType.Push_Bars):
            navigation_target=coordinates_generator()

        elif(current_task == TaskType.DETECT_Number):
           #el conversion dyel el numero tsir hna
           
           number = number_request() #e number lezem yetsava !
           current_task=TaskType.NORMAL_NAV
           return 'Go to: MoveOn'

        elif(current_task == TaskType.DETECT_COLOR):
           color_request()
           if(color_response.response_color == "Red"):
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(3)  
                # Turn LED off
                GPIO.output(LED_PIN, GPIO.LOW)

           elif(color_response.response_color == "blue"): 
                #we must add another led for blue
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(3)  
                # Turn LED off
                GPIO.output(LED_PIN, GPIO.LOW)

           elif((color_response.response_color == "blue") or (color_response.response_color == "Red")):
               return'Go to: MoveOn'
               
           current_task=TaskType.NORMAL_NAV
           return 'Go to: MoveOn'
        
        elif(current_task == TaskType.DETECT_CUBE_Triangle):
           
           number_triangles_cubes_request()
           current_task=TaskType.NORMAL_NAV
           return 'Go to: MoveOn'
                
        elif(current_task == TaskType.Push_Cans):
           ######à MODIFIEEEERRRRR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
           #selon le nombre detecté return to different move ons
           return 'Go to: MoveOn_Push_Cans_3'
        
        else:
            rospy.logerr("Error with detecting TaskType")
            return 'Go to: MoveOn'

        Navigation.target_order(navigation_target) 
        rospy.sleep(Navigation.communication_wait_time)
        
        current_state = rospy.get_param('nav_currentState')
        
        # Update navigation stateNavigation.target_order(navigation_target) 
        rospy.sleep(Navigation.communication_wait_time)
        
        if( current_state == 2 ):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitToReach_en
            return 'Go to: WaitToReach'
        elif ( current_state == 3 ):
            Navigation.acknowledge_order()        
            rospy.sleep(Navigation.communication_wait_time)
            return 'Go to: MoveOn'
        
        else:
            return 'Go to: MoveOn'
        
class WaitToReach(smach.State):  # starts moving here

    def __init__(self):
        smach.State.__init__(self, outcomes=[ 'Go to: DestinationReached', 'Go to: WaitToReach', 'Go to: BlockageDetected', 'Go to: CansDestinationReached', 'Go to: BarDestinationReached'],
                            )
        
    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        rospy.sleep(0.05)
        Order_Finish_Stop()
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        #listener()
        current_state = rospy.get_param('nav_currentState')
        if ( current_state == 3 and target_counter != 7 ): ##a verifier target_counter!!!!!!!!!! the tasktype verif was added so when the robot navigates from the final can to push to the bar push position
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NvigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_DestinationReached_en
            return 'Go to: DestinationReached'
        elif ( current_state == 3 and target_counter == 7): ##a verifier tarhet_counter!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NvigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_DestinationReached_en
            return 'Go to: CansDestinationReached'
        elif ( current_state == 3 and target_counter == 8): ##a verifier tarhet_counter!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NvigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_DestinationReached_en
            return 'Go to: BarDestinationReached'
        elif ( current_state == 9 or current_state == 10 ):
            return 'Go to: BlockageDetected'
        else:
            return 'Go to: WaitToReach'


class BlockageDetected(smach.State):
    

    def __init__(self):
        smach.State.__init__(self, outcomes=[ 'Go to: MoveOn', 'Go to: BlockageDetected'])

    def execute(self, userdata):
        
        signal.signal(signal.SIGINT, exit_handler)
        rospy.sleep(0.05)
        global target_counter
        global robot_blocked
        robot_blocked= True
        Order_Finish_Stop()
        if(target_counter >= 1):
            target_counter=target_counter-1
            return 'Go to: MoveOn' 
        else:
            rospy.loginfo("error target counter = 0 ")
            return 'Go to: BlockageDetected'    

class DestinationReached(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: DestinationReached',
                                             'Go to: Finished',
                                             'Go to: MoveOn_bars',
                                             ]
                            )

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        Order_Finish_Stop()
        
        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global target_counter
        global current_task
        global number_target_counter
        
        #listener()
        length_of_list = len(coordinates_list)
        Navigation.acknowledge_order()
        rospy.sleep(Navigation.communication_wait_time)
        rospy.sleep(0.05)
        if (Navigation.check_current_state() == 1):
            if (current_task != TaskType.Push_Bars and current_task != TaskType.Push_Cans):
                target_counter = target_counter + 1
                number_target_counter=0
                TaskType.task_handler()
                if(current_task == TaskType.Push_Bars):
                    return 'Go to: MoveOn_bars'

                if (target_counter >= length_of_list):
                    return 'Go to: Finished'
                else:
                    return 'Go to: MoveOn'
        else:
            return 'Go to: DestinationReached'
        
class MoveOn_Push_Cans_3(smach.State):
    
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['Go to: WaitToReach', 'Go to: MoveOn_Push_Cans_3'])

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)

        global current_task
        global coordinates_list 
        global MASTER_SMachineCurrentState_en    
        global MASTER_CurrentNavigatorState_en

        Order_Finish_Stop()
        current_state = rospy.get_param('nav_currentState')
        
        if current_state == 9 or current_state == 10 or current_state == 7:
            Navigation.acknowledge_order()
            rospy.sleep(Navigation.communication_wait_time)
            
        navigation_target=coordinates_generator()
        
        Navigation.target_order(navigation_target) 
        rospy.sleep(Navigation.communication_wait_time)
        
        current_state = rospy.get_param('nav_currentState')
        
        # Update navigation stateNavigation.target_order(navigation_target) 
        rospy.sleep(Navigation.communication_wait_time)
        
        if( current_state == 2 ):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitToReach_en
            return 'Go to: WaitToReach'
        elif ( current_state == 3 ):
            Navigation.acknowledge_order()        
            rospy.sleep(Navigation.communication_wait_time)
            return 'Go to: MoveOn_Push_Cans_3'
        
        else:
            return 'Go to: MoveOn_Push_Cans_3'
        
class MoveOn_bars(smach.State):
    
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['Go to: WaitToReach','Go to: MoveOn_bars'])

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)

        global current_task
        global coordinates_list 
        global MASTER_SMachineCurrentState_en    
        global MASTER_CurrentNavigatorState_en

        Order_Finish_Stop()
        current_state = rospy.get_param('nav_currentState')
        
        if current_state == 9 or current_state == 10 or current_state == 7:
            Navigation.acknowledge_order()
            rospy.sleep(Navigation.communication_wait_time)
            
        navigation_target=coordinates_generator()
        
        Navigation.target_order(navigation_target) 
        rospy.sleep(Navigation.communication_wait_time)
        
        current_state = rospy.get_param('nav_currentState')
        
        # Update navigation stateNavigation.target_order(navigation_target) 
        rospy.sleep(Navigation.communication_wait_time)
        
        if( current_state == 2 ):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitToReach_en
            return 'Go to: WaitToReach'
        elif ( current_state == 3 ):
            Navigation.acknowledge_order()        
            rospy.sleep(Navigation.communication_wait_time)
            return 'Go to: MoveOn_bars'
        
        else:
            return 'Go to: MoveOn_bars'       
class CansDestinationReached(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: CansDestinationReached',
                                             'Go to: Finished',
                                             'Go to:MoveOn_Push_Cans_5',
                                             'Go to:MoveOn_Push_Cans_3',
                                             'Go to:MoveOn_Push_Cans_6',
                                             'Go to:MoveOn_Push_Cans_9',
                                             ]
                            )

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        Order_Finish_Stop()
        
        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global target_counter
        global current_task
        global number_target_counter
        global length_of_list_3
        global length_of_list_6
        global length_of_list_9
        global length_of_list_5

        length_of_list_3= len(coordinates_list_3)
        length_of_list_6= len(coordinates_list_6)
        length_of_list_9= len(coordinates_list_9)
        length_of_list_5= len(coordinates_list_5)
        Navigation.acknowledge_order()
        rospy.sleep(Navigation.communication_wait_time)
        rospy.sleep(0.05)
        if (Navigation.check_current_state() == 1):
            if (current_task == TaskType.Push_Bars):
                number_target_counter = number_target_counter + 1
                TaskType.task_handler()
                if(number == 3):
                    if (number_target_counter >= length_of_list_3):
                        current_task=TaskType.NORMAL_NAV
                        ####INCREAMENT TARGET COUNTER???????????? manestha9ouuch
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans_3'
                if(number == 6):
                    if (number_target_counter >= length_of_list_6):
                        current_task=TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans_6'
                if(number == 9):
                    if (number_target_counter >= length_of_list_9):
                        current_task=TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans_9'
                if(number == 5):
                    if (number_target_counter >= length_of_list_5):
                        current_task=TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_Push_Cans_5'
                                        
            else:
                    rospy.logerr('Unknown or missing color for Push_Bars logic.')
                    return 'Go to: DestinationReached'
        else:
            return 'Go to: CansDestinationReached'
        
class BarDestinationReached(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: DestinationReached',
                                             'Go to: Finished',
                                             'Go to:MoveOn_bars',
                                             'Go to: BarDestinationReached',
                                             ]
                            )

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        Order_Finish_Stop()
        
        global coordinates_list
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global target_counter
        global current_task
        global color_target_counter
        global length_of_list_red
        global length_of_list_blue


        length_of_list_red= len(coordinates_list_red)
        length_of_list_blue= len(coordinates_list_blue)

        Navigation.acknowledge_order()
        rospy.sleep(Navigation.communication_wait_time)
        rospy.sleep(0.05)
        if (Navigation.check_current_state() == 1):
            if (current_task == TaskType.Push_Bars):
                color_target_counter = color_target_counter + 1
                TaskType.task_handler()
                if(color == 'red'):
                    ######mecanisme servooooooooooooo heeeeree
                    if (color_target_counter >= length_of_list_red ):
                        current_task=TaskType.NORMAL_NAV
                        ####INCREAMENT TARGET COUNTER???????????? manestha9ouch 
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_bars'
                if(color == 'blue'):
                     ######mecanisme servooooooooooooo heeeeree
                    if (color_target_counter >= length_of_list_blue ): 
                        current_task=TaskType.NORMAL_NAV
                        return 'Go to: MoveOn'
                    else:
                        return 'Go to:MoveOn_bars'
            else:
                    rospy.logerr('Unknown or missing color for Push_Bars logic.')
                    return 'Go to: DestinationReached'
        else:
            return 'Go to: BarDestinationReached'
        

        

class Finished(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Finished'])

    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)

        rospy.sleep(0.05)

        return 'Go to: Finished'

      
def main():
 
    rospy.init_node('hafnaoui', anonymous=True)
    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['NavigatorReached'])
    
    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('Idle', Idle(),
                               transitions={'Go to: Idle': 'Idle',
                                            'Go to: Init': 'Init'
                                            })
        
        smach.StateMachine.add('Init', Init(),
                               transitions={'Go to: Init': 'Init',
                                            'Go to: WaitForSignal': 'WaitForSignal'
                                            })
        
        smach.StateMachine.add('WaitForSignal', WaitForSignal(),
                               transitions={'Go to: WaitForSignal': 'WaitForSignal',
                                            'Go to: MoveOn': 'MoveOn'
                                            })
        
        smach.StateMachine.add('MoveOn', MoveOn(),
                               transitions={'Go to: WaitToReach': 'WaitToReach',
                                            'Go to: MoveOn': 'MoveOn'
                                            })

        smach.StateMachine.add('WaitToReach', WaitToReach(),
                               transitions={ 'Go to: DestinationReached': 'DestinationReached',
                                            'Go to: WaitToReach': 'WaitToReach',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            })
        smach.StateMachine.add('BlockageDetected', BlockageDetected(),
                               transitions={ 'Go to: MoveOn': 'MoveOn',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            })                                        
        
        smach.StateMachine.add('DestinationReached', DestinationReached(),
                               transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: DestinationReached': 'DestinationReached',
                                            'Go to: Finished': 'Finished',
                                           })
        
        smach.StateMachine.add('Finished', Finished(),
                               transitions={'Go to: Finished': 'Finished'
                                    })
        
    sis = smach_ros.IntrospectionServer('server_name', sm, '/Hafnaoui_Jr')
    sis.start()

    # Execute SMACH plan
    outcome = sm.execute()
    
    signal.signal(signal.SIGINT, exit_handler)
    
    Order_Finish_Stop()
    rospy.spin()
    sis.stop()

if __name__ == '__main__':
    main()


#number set direction???
#color set direction???
#najmou naamlou move on push can khw moch lezem naamlou move on lkol number normalement 
#no need for length of lists we already know the number of elements in each list 