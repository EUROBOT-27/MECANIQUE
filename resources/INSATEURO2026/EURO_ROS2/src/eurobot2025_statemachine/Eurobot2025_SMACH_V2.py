"""
Subscriber Classes:
    - Subscribers: Initializes and manages all subscriber nodes required for the state machine. 
      This includes subscribing to navigator position updates, LIDAR obstacle detection, 
      initial position, and jack signal. Acts as a container for all subscriber instances.
    - InitPositionSubscriber: Subscribes to the 'init_position' topic to receive the robot's 
      initial position as a MasterNavigationMessage.
    - JackSignalSubscriber: Subscribes to the 'jack_signal' topic to receive the state of the 
      jack (start signal) as a Bool message. 
    - Navigator_Receive_Position_Subscriber: Subscribes to the 'ros_can_interface/navigator_nav' 
      topic to receive the robot's current position and state from the NavigatorNavigationMessage. 
    - LidarObstacleDetectedSubscriber: Subscribes to the 'Obstacle_Enemy_Detected' topic to 
      receive LIDAR-based obstacle detection signals as Bool messages. 
    - NavigatorStateSubscriber: (For simulation/testing) Subscribes to the 'simulation_navigator_state' 
      topic to receive simulated navigator state .
Client Classes:
    - Clients: Container class that initializes all service client nodes required for task and 
      subtask management, including getting the next task point, getting the next subtask point, 
      and deleting tasks.
    - GetNextTaskPointClient: Client for the 'get_next_task_point_service' service. Sends requests 
      to obtain the next navigation task for the robot.
    - GetNextSubTaskPointClient: Client for the 'get_next_subtask' service. Sends requests to 
      obtain the next subtask for the current task, used for multi-step based tasks.
    - DeleteTaskClient: Client for the 'delete_task_service' service. Sends requests to delete a 
      completed task from the task list.

Author: <Adem Daly>

Description:
    This code conations the state machine logic for the Master node.
    The state machine is implemented using the smach library.

Classes:
    - MainStateMachine: The main state machine class that contains all the states and transitions.
    - Idle: The Idle state class.
    - Init: The Init state class.
    - WaitForSignal: The WaitForSignal state class.
    - MoveOn: The MoveOn state class.
    - WaitToReach: The WaitToReach state class.
    - DestinationReached: The DestinationReached state class.
    - Building_PickUp_Init: The Building_PickUp_Init state class.
    - Building_PickUp_MoveOn: The Building_PickUp_MoveOn state class.
    - Building_PickUp_WaitToReach: The Building_PickUp_WaitToReach state class.
    - Building_PickUp_DestinationReached: The Building_PickUp_DestinationReached state class.
    - Building_DropDown_Init: The Building_DropDown_Init state class.
    - Building_DropDown_MoveOn: The Building_DropDown_MoveOn state class.
    - Building_DropDown_WaitToReach: The Building_DropDown_WaitToReach state class.
    - Building_DropDown_DestinationReached: The Building_DropDown_DestinationReached state class.
    - Bonderole_Pose_Init: The Bonderole_Pose_Init state class.
    - Bonderole_Pose_MoveOn: The Bonderole_Pose_MoveOn state class.
    - Bonderole_Pose_WaitToReach: The Bonderole_Pose_WaitToReach state class.
    - Bonderole_Pose_DestinationReached: The Bonderole_Pose_DestinationReached state class.
    - BlockageDetected: The BlockageDetected state class.
    - SuddenStop: The SuddenStop state class.
    - WaitSuddenStop: The WaitSuddenStop state class.
    - ConfirmedStop: The ConfirmedStop state class.
    - Finished: The Finished state class.

    Explanation of classes structure decision:
        -from Idle class to DestinationReached class: these classes are for navigation tasks.
        -from Building_PickUp_Init class to Bonderole_Pose_DestinationReached class: these 
        classes are for building tasks: either going to intermediate tasks points or commanding mechanisms
        -BlockageDetected class: this class is when the robot gets blocked.(it contains the logic to handle banderole bloackage too)
        -From SuddenStop to ConfirmedStop:these classes are when the enemy robot is near and we need to stop our robot.
        -Finished class: this class is when the robot finishes all tasks or the allowed time ends.

Publishers:
    - Current_Direction_Publisher: Publishes the current direction of the robot.
    - EstimatedScorePublisher: Publishes the estimated score of the current task
    - Current_Task_Publisher: Publishes the current task.
    - Navigator_Acknowledge_Publisher: Publishes the acknowledge signal to the Navigator.
    - Navigator_Target_Publisher: Publishes the target position order to the Navigator.
    - Navigator_Stop_Publisher: Publishes the stop signal to the Navigator.
    - Navigator_Reset_Publisher: Publishes the reset signal to the Navigator.
    - Current_Position_Publisher: Publishes the current position of the robot.


    """

import rclpy
import smach
import threading
import time
import signal
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from enum import Enum
from geometry_msgs.msg import Pose2D
from ros_custom_messages.msg import MasterAcknowledgeSignal, MasterNavigationMessage, MasterResetSignal, MasterStopSignal, NavigatorNavigationMessage, CurrentTask
from ros_custom_messages.srv import GetNextTaskPoint, GetNextSubTaskPoint, DeleteTask
from strategy.static_task_generator import Task, TaskType ,Direction, TaskTypeScore, SpeedChoice
from std_msgs.msg import Int32, Bool
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_srvs.srv import Empty


##################################### TYPEDEF ENUMS HERE ####################################

"""
Enum for the Navigator states:
    these states represent the states of the STM32 Navigator StateMachine used 
    that the Master keeps track of the STM32 current state(there are more states in the STM32
    chip but we reduced to only what we need to know)
"""

class MASTER_NavigatorStates_ten(Enum):

    MASTER_NavigatorIdle_en = 0
    MASTER_NavigatorReady_en = 1
    MASTER_NavigatorBusy_en = 2
    MASTER_NavigatorWaitToReceiveAcknowledge_en = 3
    MASTER_NavigatorReachedDest_en = 4
    MASTER_NavigatorConfirmedStop_en = 5
    MASTER_NavigatorInit_en = 6

"""
Enum for the Master states:
   these states represent the states of the Raspberry (Master) StateMachine used
   to keep track of the current state of the Master
"""

class MASTER_SMachineStates_ten(Enum):

    MASTER_SMachine_Idle_en = 0
    MASTER_SMachine_WaitForSignal_en = 1
    MASTER_SMachine_MoveOn_en = 2
    MASTER_SMachine_WaitToReach_en = 3
    MASTER_SMachine_DestinationReached_en = 4
    MASTER_SMachine_SuddenStop_en = 5
    MASTER_SMachine_ConfirmedStop_en = 6
    MASTER_SMachine_Finish_en = 7
    MASTER_SMachine_Building_PickUp_Init_en = 8
    MASTER_SMachine_Building_PickUp_MoveOn_en = 9
    MASTER_SMachine_Building_PickUp_WaitToReach_en = 10
    MASTER_SMachine_Building_PickUp_DestinationReached_en = 11
    MASTER_SMachine_Building_PickUp_Finish_en = 12
    MASTER_SMachine_Building_DropDown_Init_en = 13
    MASTER_SMachine_Building_DropDown_MoveOn_en = 14
    MASTER_SMachine_Building_DropDown_WaitToReach_en = 15
    MASTER_SMachine_Building_DropDown_DestinationReached_en = 16
    MASTER_SMachine_Bonderole_Pose_Init_en = 17
    MASTER_SMachine_Bonderole_Pose_MoveOn_en = 18
    MASTER_SMachine_Bonderole_Pose_WaitToReach_en = 19
    MASTER_SMachine_Bonderole_Pose_DestinationReached_en = 20
    MASTER_SMachine_Building_DropDown_Finish_en = 21

"""
STM32 State: These states are the states that the can returns to the state machine
we use them to transition between states
"""

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
##################################### GLOBAL VARIABLES ####################################
####GLOBAL VARIABLES#####
TOTAL_PLAYING_TIME = 100 #in seconds 40 just for test need to return it to 100 !!!!!!!!!!!!!!!!!!!!!
publishers_instance = None
subscribers_instance = None
clients_instance = None
servers_instance = None
current_position = None #Pose2D format
current_task = None
next_task = None
current_playing_time = 0
current_subtask_order = 0
next_subtask_order = 0
estimated_score = 0
return_to_finish_spot_flag = False
jack_state = False
currently_doing_subtask = None #The differnce between current task and currently_doing_subtask is that even if current task is 
# decided even before entering the statemachine of the task itself...but the currently_doing_subtask is decided when we actually
# enter the statemachine of the task itself (this helps us distinguish when to go to moveon or task moveon after going to a suddenstop)
lidar_obstacle_detected = False
robot_stuck_wait_to_reach = False
"""current_task = Task(id=-100,position=Pose2D(x=100.0,y=100.0,theta=90),
                    type=TaskType.NORMAL_NAV,direction=Direction.BACKWARD,
                    score=TaskTypeScore.BONDEROLE_POSE, linear_velocity=SpeedChoice.SLOW,
                    angular_velocity=SpeedChoice.SLOW,linear_acceleration=0,angular_acceleration=0,
                    subtask_list=[])"""
current_subtask = None
current_navigator_state = None
MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorIdle_en
MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Idle_en

"""init_position = MasterNavigationMessage(nav_target_x=1200.0,
                                        nav_target_y=275.5,
                                        nav_target_angle=90.0,
                                        nav_is_forward=True,
                                        nav_linear_velocity_choice=0,
                                        nav_angular_velocity_choice=0,
                                        nav_linear_acceleration_choice=0,
                                        nav_angular_acceleration_choice=0,
                                        nav_is_with_platforms = False,
                                        )#yellow init position"""

init_position = None

"""init_position = MasterNavigationMessage(nav_target_x=1800.0,
                                        nav_target_y=195.5,
                                        nav_target_angle=90.0,
                                        nav_is_forward=True,
                                        nav_linear_velocity_choice=0,
                                        nav_angular_velocity_choice=0,
                                        nav_linear_acceleration_choice=0,
                                        nav_angular_acceleration_choice=0,
                                        nav_is_with_platforms = False,
                                        )#blue init_position"""

#this init position was used before adding game_launcher node to decide teh initposition
########################

communication_wait_time = 0.2  #used to wait until the message is transmited to the Navigator

###################################### CLASSES #########################################






####################################### GENERAL STATE MACHINE CLASSES ################################################

class MainStateMachine(smach.StateMachine):
    def __init__(self):
        super().__init__(outcomes=['End'])
        with self:
            smach.StateMachine.add('Idle', Idle(),
                               transitions={'Go to: Init': 'Init',
                                            'Go to: Idle': 'Idle'})
        
            smach.StateMachine.add('Init', Init(),
                                transitions={'Go to: WaitForSignal': 'WaitForSignal',
                                            'Go to: Init': 'Init',})
                                                
            smach.StateMachine.add('WaitForSignal', WaitForSignal(),
                                transitions={'Go to: MoveOn': 'MoveOn',
                                             'Go to: WaitForSignal': 'WaitForSignal',})
                                                
            smach.StateMachine.add('MoveOn', MoveOn(),
                                transitions={'Go to: WaitToReach': 'WaitToReach',
                                             'Go to: MoveOn': 'MoveOn',
                                             'Go to: BlockageDetected': 'BlockageDetected',})
                                                
            smach.StateMachine.add('WaitToReach', WaitToReach(),
                                transitions={'Go to: DestinationReached': 'DestinationReached',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            'Go to: SuddenStop': 'SuddenStop',
                                            'Go to: WaitToReach': 'WaitToReach', })
                                                
            smach.StateMachine.add('BlockageDetected', BlockageDetected(),
                                transitions={ 'Go to: MoveOn': 'MoveOn',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            'Go to: Bonderole_Pose_Init': 'Bonderole_Pose_Init',
                                            'Go to: Building_PickUp_DestinationReached': 'Building_PickUp_DestinationReached',
                                            'Go to: Building_DropDown_MoveOn': 'Building_DropDown_MoveOn',
                                            'Go to: Building_PickUp_MoveOn': 'Building_PickUp_MoveOn',})

            smach.StateMachine.add('SuddenStop', SuddenStop(),
                               transitions={'Go to: WaitSuddenStop': 'WaitSuddenStop',
                                            'Go to: SuddenStop': 'SuddenStop'
                                            })
        
            smach.StateMachine.add('WaitSuddenStop', WaitSuddenStop(),
                               transitions={'Go to: ConfirmedStop': 'ConfirmedStop',
                                            'Go to: WaitSuddenStop': 'WaitSuddenStop'
                                            })

            smach.StateMachine.add('ConfirmedStop', ConfirmedStop(),
                               transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: ConfirmedStop': 'ConfirmedStop',
                                            'Go to: Building_PickUp_MoveOn': 'Building_PickUp_MoveOn',
                                            'Go to: Building_DropDown_MoveOn': 'Building_DropDown_MoveOn',
                                            'Go to: Bonderole_Pose_MoveOn': 'Bonderole_Pose_MoveOn',
                                            })                                         
                                               
            smach.StateMachine.add('DestinationReached', DestinationReached(),
                                transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: Finished': 'Finished',
                                            'Go to: Building_PickUp_Init': 'Building_PickUp_Init',
                                            'Go to: Building_DropDown_Init': 'Building_DropDown_Init',
                                            'Go to: Bonderole_Pose_Init': 'Bonderole_Pose_Init',
                                            'Go to: DestinationReached': 'DestinationReached',})
                                            
            smach.StateMachine.add('Building_PickUp_Init',Building_PickUp_Init(),
                                transitions={'Go to: Building_PickUp_MoveOn': 'Building_PickUp_MoveOn',
                                            'Go to: Building_PickUp_Init': 'Building_PickUp_Init',})
            
            smach.StateMachine.add('Building_PickUp_MoveOn',Building_PickUp_MoveOn(),
                                transitions={'Go to: Building_PickUp_WaitToReach': 'Building_PickUp_WaitToReach',
                                            'Go to: Building_PickUp_MoveOn': 'Building_PickUp_MoveOn',
                                            'Go to: Building_PickUp_DestinationReached': 'Building_PickUp_DestinationReached',
                                            'Go to: MoveOn': 'MoveOn',
                                            'Go to: BlockageDetected': 'BlockageDetected',})
            
            smach.StateMachine.add('Building_PickUp_WaitToReach',Building_PickUp_WaitToReach(),
                                transitions={'Go to: Building_PickUp_DestinationReached': 'Building_PickUp_DestinationReached',
                                             'Go to: SuddenStop': 'SuddenStop',
                                            'Go to: Building_PickUp_WaitToReach': 'Building_PickUp_WaitToReach',
                                            'Go to: BlockageDetected': 'BlockageDetected',})

            smach.StateMachine.add('Building_PickUp_DestinationReached',Building_PickUp_DestinationReached(),
                                transitions={'Go to: Building_PickUp_MoveOn': 'Building_PickUp_MoveOn',
                                            'Go to: Building_PickUp_DestinationReached': 'Building_PickUp_DestinationReached',})

            smach.StateMachine.add('Building_DropDown_Init',Building_DropDown_Init(),
                                transitions={'Go to: Building_DropDown_MoveOn': 'Building_DropDown_MoveOn',
                                            'Go to: Building_DropDown_Init': 'Building_DropDown_Init',})
            
            smach.StateMachine.add('Building_DropDown_MoveOn',Building_DropDown_MoveOn(),
                                transitions={'Go to: Building_DropDown_WaitToReach': 'Building_DropDown_WaitToReach',
                                            'Go to: Building_DropDown_MoveOn': 'Building_DropDown_MoveOn',
                                            'Go to: Building_DropDown_DestinationReached': 'Building_DropDown_DestinationReached',
                                            'Go to: MoveOn': 'MoveOn',
                                            'Go to: BlockageDetected': 'BlockageDetected',})
            
            smach.StateMachine.add('Building_DropDown_WaitToReach',Building_DropDown_WaitToReach(),
                                transitions={'Go to: Building_DropDown_DestinationReached': 'Building_DropDown_DestinationReached',
                                            'Go to: Building_DropDown_WaitToReach': 'Building_DropDown_WaitToReach',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            'Go to: SuddenStop': 'SuddenStop'})
            
            smach.StateMachine.add('Building_DropDown_DestinationReached',Building_DropDown_DestinationReached(),
                                transitions={'Go to: Building_DropDown_MoveOn': 'Building_DropDown_MoveOn',
                                            'Go to: Building_DropDown_DestinationReached': 'Building_DropDown_DestinationReached',})

            smach.StateMachine.add('Bonderole_Pose_Init',Bonderole_Pose_Init(),
                                transitions={'Go to: Bonderole_Pose_MoveOn': 'Bonderole_Pose_MoveOn',
                                            'Go to: Bonderole_Pose_Init': 'Bonderole_Pose_Init',})
            
            smach.StateMachine.add('Bonderole_Pose_MoveOn',Bonderole_Pose_MoveOn(),
                                transitions={'Go to: Bonderole_Pose_WaitToReach': 'Bonderole_Pose_WaitToReach',
                                            'Go to: Bonderole_Pose_MoveOn': 'Bonderole_Pose_MoveOn',
                                            'Go to: Bonderole_Pose_DestinationReached': 'Bonderole_Pose_DestinationReached',
                                            'Go to: MoveOn': 'MoveOn',
                                            'Go to: BlockageDetected': 'BlockageDetected',})
            
            smach.StateMachine.add('Bonderole_Pose_WaitToReach',Bonderole_Pose_WaitToReach(),
                                transitions={'Go to: Bonderole_Pose_DestinationReached': 'Bonderole_Pose_DestinationReached',
                                            'Go to: Bonderole_Pose_WaitToReach': 'Bonderole_Pose_WaitToReach',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            'Go to: SuddenStop': 'SuddenStop'})
            
            smach.StateMachine.add('Bonderole_Pose_DestinationReached',Bonderole_Pose_DestinationReached(),
                                transitions={'Go to: Bonderole_Pose_MoveOn': 'Bonderole_Pose_MoveOn',
                                            'Go to: Bonderole_Pose_DestinationReached': 'Bonderole_Pose_DestinationReached',})

            smach.StateMachine.add('Finished', Finished(),
                                transitions={'Go to: Finished': 'Finished'})  



############################################ EACH STATE MACHINE CLASS ###############################################

class Idle(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Init',
                                             'Go to: Idle'])
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        signal.signal(signal.SIGINT, exit_handler)
        send_acknowledge_signal()
        time.sleep(communication_wait_time)
        time.sleep(1)
        print("SLEEEEEP MORE")
        if(current_navigator_state == 8):
            MASTER_CurrentNavigatorState_en == MASTER_NavigatorStates_ten.MASTER_NavigatorReady_en
            MASTER_SMachineCurrentState_en == MASTER_SMachineStates_ten.MASTER_SMachine_WaitForSignal_en
            return 'Go to: Init'
        else:
            return 'Go to: Idle'
        

class Init(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: WaitForSignal',
                                             'Go to: Init'])
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global init_position
        signal.signal(signal.SIGINT, exit_handler)
        send_target_order(init_position)
        time.sleep(0.5)

        if(current_navigator_state == 1):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorReady_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitForSignal_en
            return 'Go to: WaitForSignal'
        else:
            return 'Go to: Init'        


class WaitForSignal(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: WaitForSignal'])
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global jack_state
        print(jack_state)
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.1)
        if(MASTER_CurrentNavigatorState_en == MASTER_NavigatorStates_ten.MASTER_NavigatorReady_en and jack_state == True):
            #time.sleep(1) #Maybe i need to add the sleep function 
            return 'Go to: MoveOn'
        else:
            return 'Go to: WaitForSignal'   

        
class MoveOn(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: WaitToReach',
                                             'Go to: MoveOn',
                                             'Go to: BlockageDetected',
                                             ])
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_task
        global next_task
        global current_subtask_order
        global next_subtask_order
        global currently_doing_subtask 
        global return_to_finish_spot_flag
        global current_playing_time
        current_subtask_order = 0
        next_subtask_order = 0
        order_finish_stop()
        currently_doing_subtask = TaskType.NORMAL_NAV.value
        signal.signal(signal.SIGINT, exit_handler)
        get_next_task_point()
        #print("Nav Roder Details:")
        print(f"nav_target_x: {next_task.position.x}")
        print(f"nav_target_y: {next_task.position.y}")
        print(f"nav_target_angle: {next_task.position.theta}")
        print("current navigation state:",current_navigator_state)
        #print(f"nav_is_forward: {next_task.direction}")
        #print(f"nav_linear_velocity_choice: {next_task.linear_velocity}")
        #print(f"nav_angular_velocity_choice: {next_task.angular_velocity}")
        #print(f"nav_linear_acceleration_choice: {next_task.linear_acceleration}")
        #print(f"nav_angular_acceleration_choice: {next_task.angular_acceleration}")
        nav_order = convert_next_task_to_nav_order(next_task)
        if next_task.type == TaskType.RETURN_TO_FINISH_SPOT.value : 
            while current_playing_time < 91: # was 90
                time.sleep(0.5)
                print("waiting for PAMIS to leave")

        send_target_order(nav_order)
        time.sleep(communication_wait_time)
        #or current_navigator_state == 7  :return 'Go to: BlockageDetected'
        if(current_navigator_state == 7):
            send_acknowledge_signal()
            time.sleep(communication_wait_time)
            return 'Go to: MoveOn'
        
        if(current_navigator_state == 9 or current_navigator_state == 10 ):
            """send_acknowledge_signal()
            time.sleep(communication_wait_time)
            return 'Go to: MoveOn'"""
            return 'Go to: BlockageDetected'
        elif (current_navigator_state == 3):#Added  the wait to receive acknowledge condition
            send_acknowledge_signal()
            time.sleep(communication_wait_time)  # Use time.sleep in ROS 2
            return 'Go to: MoveOn'    
        elif (current_navigator_state == 2):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_WaitToReach_en
            publishers_instance.Current_Direction_Publisher.publish(Bool(data=next_task.direction))  
            print("Direction",next_task.direction)          
            return 'Go to: WaitToReach'
        else:
            return 'Go to: MoveOn'


class WaitToReach(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: DestinationReached',
                                             'Go to: BlockageDetected',
                                             'Go to: SuddenStop',
                                             'Go to: WaitToReach'])
    
    def execute(self, userdata):
        global current_playing_time
        global robot_stuck_wait_to_reach
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global current_task
        global subscribers_instance
        global lidar_obstacle_detected
        global next_task
        order_finish_stop()
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        # Maybe i need to add time.sleep(0.05)
        if lidar_obstacle_detected or robot_stuck_wait_to_reach:
            #maybe i need to sleep a bit and than check again
            print('STTTTTTTTTTTTTTTTTTTOOOOOOOOOOOOOOOOOOOP')
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_SuddenStop_en
            return 'Go to: SuddenStop'

        elif(current_navigator_state == 3):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_DestinationReached_en
            return 'Go to: DestinationReached'
        
        elif ( current_navigator_state == 9 or current_navigator_state == 10 ):
            return 'Go to: BlockageDetected'
        
        else:
            return 'Go to: WaitToReach'         
        
    
class DestinationReached(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: Finished',
                                             'Go to: Building_PickUp_Init',
                                             'Go to: Building_DropDown_Init',
                                             'Go to: Bonderole_Pose_Init',
                                             'Go to: DestinationReached']) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_task
        global next_task
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        send_acknowledge_signal()
        current_task = next_task #i changed the location of current_task = next_task from wait to reach
        #to DestinationReached to handle the SuddenStop case in optimal way
        if(current_navigator_state == 1):
            if (current_task.type == TaskType.RETURN_TO_FINISH_SPOT.value):
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Finish_en
                return 'Go to: Finished' 
            elif (current_task.type == TaskType.BUILDING_PICKUP.value):
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_Init_en
                return 'Go to: Building_PickUp_Init'
            elif (current_task.type == TaskType.BUILDING_DROPDOWN.value):
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_Init_en
                return 'Go to: Building_DropDown_Init'    
            elif (current_task.type == TaskType.BONDEROLE_POSE.value):
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_Init_en
                return 'Go to: Bonderole_Pose_Init'
            else:
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_MoveOn_en
                return 'Go to: MoveOn'

        else:
            return 'Go to: DestinationReached' 


class Building_PickUp_Init(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_MoveOn',
                                             'Go to: Building_PickUp_Init']) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global currently_doing_subtask
        currently_doing_subtask = TaskType.BUILDING_PICKUP.value
        #here i should initialize the mechanism if it is not ready
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)

        if(True):
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_MoveOn_en
            return 'Go to: Building_PickUp_MoveOn'
        else:
            return 'Go to: Building_PickUp_Init'


class Building_PickUp_MoveOn(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_WaitToReach',
                                             'Go to: Building_PickUp_MoveOn',
                                             'Go to: Building_PickUp_DestinationReached',
                                             'Go to: MoveOn',
                                             'Go to: BlockageDetected',]) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_subtask_order
        global current_task
        global next_subtask_order
        global clients_instance
        global return_to_finish_spot_flag
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        response = get_next_subtask()
        if (response.current_subtask_order == -1):
            """
            the subtask generator node returns -1 if all subtasks are done
            so we need to return to normal navigation
            """
            clients_instance.delete_task_client.send_request(current_task.id)
            return 'Go to: MoveOn'

        elif(response.nav_target_x == 0.0 and response.nav_target_y == 0.0):
            """
            here if the subtask is a mechanism command.the subtask generator node will return
            an absurd positiion(0.0) so we know we will comamnd a mechanism
            """
            #wait_mechanism_mouvement()
            #the wait for mechanism to end his function should block until the mechanism is done
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_DestinationReached_en
            next_subtask_order = current_subtask_order + 1 
            return 'Go to: Building_PickUp_DestinationReached'

        elif(response.nav_target_x != 0.0 or response.nav_target_y != 0.0): 
            nav_order = convert_next_subtask_to_nav_order(response)
            send_target_order(nav_order)
            time.sleep(communication_wait_time)  
            if(current_navigator_state == 9 or current_navigator_state == 10 or current_navigator_state == 7 ):
                """send_acknowledge_signal()
                time.sleep(communication_wait_time)
                return 'Go to: Building_PickUp_MoveOn'"""
                return 'Go to: BlockageDetected'
            elif (current_navigator_state == 3):
                send_acknowledge_signal()
                time.sleep(communication_wait_time)
                return 'Go to: Building_PickUp_MoveOn'
            elif (current_navigator_state == 2):
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_WaitToReach_en
                MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
                next_subtask_order = current_subtask_order + 1 
                publishers_instance.Current_Direction_Publisher.publish(Bool(data=response.nav_is_forward)) 
                print("Direction",next_task.direction) 
                return 'Go to: Building_PickUp_WaitToReach'
            else:
                return 'Go to: Building_PickUp_MoveOn'

        else:
            return 'Go to: Building_PickUp_MoveOn'            


class Building_PickUp_WaitToReach(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_DestinationReached',
                                             'Go to: Building_PickUp_WaitToReach',
                                             'Go to: SuddenStop',
                                             'Go to: BlockageDetected']) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global robot_stuck_wait_to_reach
        global lidar_obstacle_detected
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        if lidar_obstacle_detected or robot_stuck_wait_to_reach:
            #maybe i need to sleep a bit and than check again
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_SuddenStop_en
            return 'Go to: SuddenStop'
        
        elif ( current_navigator_state == 9 or current_navigator_state == 10 ):
            return 'Go to: BlockageDetected'
        
        if(current_navigator_state == 3):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_DestinationReached_en
            return 'Go to: Building_PickUp_DestinationReached'

        else:
            return 'Go to: Building_PickUp_WaitToReach'

    
class Building_PickUp_DestinationReached(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_MoveOn',
                                             'Go to: Building_PickUp_DestinationReached']) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_subtask_order
        global next_subtask_order
        current_subtask_order = next_subtask_order
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        send_acknowledge_signal()
        time.sleep(communication_wait_time)
        if(current_navigator_state == 1):
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_MoveOn_en
            return 'Go to: Building_PickUp_MoveOn'

        else:
            return 'Go to: Building_PickUp_DestinationReached'    


class Building_DropDown_Init(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_MoveOn',
                                             'Go to: Building_DropDown_Init']) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global currently_doing_subtask
        currently_doing_subtask = TaskType.BUILDING_DROPDOWN.value
        #here i should initialize the mechanism if it is not ready
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)

        if(True):
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_MoveOn_en
            return 'Go to: Building_DropDown_MoveOn'

        else:
            return 'Go to: Building_DropDown_Init'

class Building_DropDown_MoveOn(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_WaitToReach',
                                             'Go to: Building_DropDown_MoveOn',
                                             'Go to: Building_DropDown_DestinationReached',
                                             'Go to: MoveOn',
                                             'Go to: BlockageDetected',]) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_subtask_order
        global next_subtask_order
        global clients_instance
        global current_task
        global estimated_score
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        response = get_next_subtask()
        if (response.current_subtask_order == -1):
            estimated_score = estimated_score + 12 #4
            clients_instance.delete_task_client.send_request(current_task.id)
            return 'Go to: MoveOn'

        elif(response.nav_target_x == 0.0 and response.nav_target_y == 0.0):
            #wait_mechanism_mouvement()
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_DestinationReached_en
            next_subtask_order = current_subtask_order + 1 
            return 'Go to: Building_DropDown_DestinationReached'
        
        elif(response.nav_target_x != 0.0 or response.nav_target_y != 0.0): 
            nav_order = convert_next_subtask_to_nav_order(response)
            send_target_order(nav_order)
            time.sleep(communication_wait_time)  
            if(current_navigator_state == 9 or current_navigator_state == 10 or current_navigator_state == 7 ):
                """send_acknowledge_signal()
                time.sleep(communication_wait_time)
                return 'Go to: Building_DropDown_MoveOn'"""
                return 'Go to: BlockageDetected'
            elif (current_navigator_state == 3):
                send_acknowledge_signal()
                time.sleep(communication_wait_time)
                return 'Go to: Building_DropDown_MoveOn'
            elif (current_navigator_state == 2):
                MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_WaitToReach_en
                next_subtask_order = current_subtask_order + 1 
                publishers_instance.Current_Direction_Publisher.publish(Bool(data=response.nav_is_forward)) 
                print("Direction",next_task.direction) 
                return 'Go to: Building_DropDown_WaitToReach'
            else:
                return 'Go to: Building_DropDown_MoveOn'
                    
        else:
            return 'Go to: Building_DropDown_MoveOn'            
    
class Building_DropDown_WaitToReach(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_DestinationReached',
                                             'Go to: Building_DropDown_WaitToReach',
                                             'Go to: SuddenStop',
                                             'Go to: BlockageDetected']) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global lidar_obstacle_detected
        global robot_stuck_wait_to_reach
        time.sleep(0.05)
        order_finish_stop()
        signal.signal(signal.SIGINT, exit_handler)

        if lidar_obstacle_detected or robot_stuck_wait_to_reach:
            #maybe i need to sleep a bit and than check again
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_SuddenStop_en
            return 'Go to: SuddenStop'

        elif ( current_navigator_state == 9 or current_navigator_state == 10 ):
            return 'Go to: BlockageDetected'

        if(current_navigator_state == 3):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_DestinationReached_en
            return 'Go to: Building_DropDown_DestinationReached'

        else:
            return 'Go to: Building_DropDown_WaitToReach'

    
class Building_DropDown_DestinationReached(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_MoveOn',
                                             'Go to: Building_DropDown_DestinationReached']) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_subtask_order
        global next_subtask_order
        time.sleep(0.05)
        order_finish_stop()
        current_subtask_order = next_subtask_order
        signal.signal(signal.SIGINT, exit_handler)
        send_acknowledge_signal()
        time.sleep(communication_wait_time)
        if(current_navigator_state == 1):
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_MoveOn_en
            return 'Go to: Building_DropDown_MoveOn'

        else:
            return 'Go to: Building_DropDown_DestinationReached'    


class Bonderole_Pose_Init(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Bonderole_Pose_MoveOn',
                                             'Go to: Bonderole_Pose_Init'])

    def execute(self, userdata):
        global current_navigator_state    
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global currently_doing_subtask
        currently_doing_subtask = TaskType.BONDEROLE_POSE.value
        #here i should initialize the mechanism if it is not ready
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)

        if(True):
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_MoveOn_en
            return 'Go to: Bonderole_Pose_MoveOn'
        else:
            return 'Go to: Bonderole_Pose_Init'


class Bonderole_Pose_MoveOn(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Bonderole_Pose_WaitToReach',
                                             'Go to: Bonderole_Pose_MoveOn',
                                             'Go to: Bonderole_Pose_DestinationReached',
                                             'Go to: MoveOn',
                                             'Go to: BlockageDetected'])
    def execute(self, userdata):
        global current_navigator_state    
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_subtask_order
        global next_subtask_order
        global clients_instance
        global current_task
        global estimated_score
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        response = get_next_subtask()
        if (response.current_subtask_order == -1):
            #estimated_score = estimated_score + 20
            clients_instance.delete_task_client.send_request(current_task.id)
            return 'Go to: MoveOn'
        
        elif(response.nav_target_x == 0.0 and response.nav_target_y == 0.0):
            #wait_mechanism_mouvement()
            estimated_score = estimated_score + 20
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_DestinationReached_en
            next_subtask_order = current_subtask_order + 1 
            return 'Go to: Bonderole_Pose_DestinationReached'
        
        elif(response.nav_target_x != 0.0 or response.nav_target_y != 0.0):
            nav_order = convert_next_subtask_to_nav_order(response)
            send_target_order(nav_order)
            time.sleep(communication_wait_time)  
            if(current_navigator_state == 9 or current_navigator_state == 10 or current_navigator_state == 7 ):
                """send_acknowledge_signal()
                time.sleep(communication_wait_time)
                return 'Go to: Bonderole_Pose_MoveOn'"""
                return 'Go to: BlockageDetected'
            elif (current_navigator_state == 3):
                send_acknowledge_signal()
                time.sleep(communication_wait_time)
                return 'Go to: Bonderole_Pose_MoveOn'
            elif (current_navigator_state == 2):
                MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorBusy_en
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_WaitToReach_en
                next_subtask_order = current_subtask_order + 1 
                publishers_instance.Current_Direction_Publisher.publish(Bool(data=response.nav_is_forward))         
                print("Direction",next_task.direction)        
                return 'Go to: Bonderole_Pose_WaitToReach'
            else:
                return 'Go to: Bonderole_Pose_MoveOn'
                    
        else:
            return 'Go to: Bonderole_Pose_MoveOn'            

class Bonderole_Pose_WaitToReach(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Bonderole_Pose_DestinationReached',
                                             'Go to: Bonderole_Pose_WaitToReach',
                                             'Go to: SuddenStop',
                                             'Go to: BlockageDetected',
                                             ]) 
    
    def execute(self, userdata):
        global current_navigator_state #returned as a msg
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global lidar_obstacle_detected
        global robot_stuck_wait_to_reach
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        #here i need to check of blockage maybe there is confustion 
        if lidar_obstacle_detected or robot_stuck_wait_to_reach:
            #maybe i need to sleep a bit and than check again
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_SuddenStop_en
            return 'Go to: SuddenStop'
            
        if(current_navigator_state == 3):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorWaitToReceiveAcknowledge_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_DestinationReached_en
            return 'Go to: Bonderole_Pose_DestinationReached'

        elif ( current_navigator_state == 9 or current_navigator_state == 10 ):
            return 'Go to: BlockageDetected'

        else:
            return 'Go to: Bonderole_Pose_WaitToReach'
                

class Bonderole_Pose_DestinationReached(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Bonderole_Pose_MoveOn',
                                             'Go to: Bonderole_Pose_DestinationReached'])
    
    def execute(self, userdata):
        global current_navigator_state
        global MASTER_CurrentNavigatorState_en       
        global MASTER_SMachineCurrentState_en
        global communication_wait_time
        global current_subtask_order
        global next_subtask_order
        current_subtask_order = next_subtask_order
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        order_finish_stop()
        send_acknowledge_signal()
        time.sleep(communication_wait_time)
        if(current_navigator_state == 1):
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_MoveOn_en
            return 'Go to: Bonderole_Pose_MoveOn'
        
        else:
            return 'Go to: Bonderole_Pose_DestinationReached'


class BlockageDetected(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: BlockageDetected',
                                             'Go to: Bonderole_Pose_Init',
                                             'Go to: Building_PickUp_DestinationReached',
                                             'Go to: Building_DropDown_MoveOn',
                                             'Go to: Building_PickUp_MoveOn']) 

    def execute(self, userdata):
        global next_task
        global MASTER_SMachineCurrentState_en
        global current_task
        global currently_doing_subtask
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global current_navigator_state
        signal.signal(signal.SIGINT, exit_handler)
        time.sleep(0.05)
        send_acknowledge_signal()
        time.sleep(communication_wait_time)
        print("#############################################")
        print(currently_doing_subtask)
        print(current_task)
        print("############################################")
        if(current_navigator_state == 1):
            if next_task.type == TaskType.BONDEROLE_POSE.value:
                current_task = next_task
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_Init_en
                return 'Go to: Bonderole_Pose_Init'
            
            elif (current_task.type == TaskType.BUILDING_PICKUP.value and currently_doing_subtask == TaskType.BUILDING_PICKUP.value):
                
                if (current_task.id == 5 or current_task.id == 7 or current_task.id == 9 or current_task.id == 11 ):
                    MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorWaitToReceiveAcknowledge_en
                    MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_DestinationReached_en
                    return 'Go to: Building_PickUp_DestinationReached'
                else :
                    MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorWaitToReceiveAcknowledge_en
                    MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_MoveOn_en
                    return 'Go to: Building_PickUp_MoveOn'

            elif (current_task.type == TaskType.BUILDING_DROPDOWN.value and currently_doing_subtask == TaskType.BUILDING_DROPDOWN.value):
                MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorWaitToReceiveAcknowledge_en
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_MoveOn_en
                time.sleep(3)
                return 'Go to: Building_DropDown_MoveOn'

            else:    
                time.sleep(3)
                return 'Go to: MoveOn'
        #the time.sleep(1) i added it to fix the problem of the robot get's stuck and oscilates between moveon blockage and wait to reach
        else:
            return 'Go to: BlockageDetected'


class SuddenStop(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: WaitSuddenStop',
                                             'Go to: SuddenStop']) 
    
    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        global MASTER_CurrentNavigatorState_en
        global MASTER_SMachineCurrentState_en
        global current_navigator_state
        send_stop_signal()
        order_finish_stop()
        time.sleep(0.5) #added it so we don't loop too fast  
        if(current_navigator_state == 6 or current_navigator_state == 7):
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorConfirmedStop_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_ConfirmedStop_en
            return 'Go to: WaitSuddenStop'
        else:
            return 'Go to: SuddenStop'


class WaitSuddenStop(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: ConfirmedStop',
                                             'Go to: WaitSuddenStop']) 
    
    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        global communication_wait_time
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        time.sleep(0.05)
        order_finish_stop()
        # Check if the current navigator state is confirmed stop
        if current_navigator_state == 7:
            MASTER_CurrentNavigatorState_en = MASTER_NavigatorStates_ten.MASTER_NavigatorConfirmedStop_en
            MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_ConfirmedStop_en
            return 'Go to: ConfirmedStop'
        else:
            return 'Go to: WaitSuddenStop'


class ConfirmedStop(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: ConfirmedStop',
                                             'Go to: Building_PickUp_MoveOn',
                                             'Go to: Building_DropDown_MoveOn',
                                             'Go to: Bonderole_Pose_MoveOn']) 
    
    def execute(self, userdata):
        signal.signal(signal.SIGINT, exit_handler)
        global communication_wait_time
        global MASTER_SMachineCurrentState_en
        global MASTER_CurrentNavigatorState_en
        global currently_doing_subtask
        global lidar_obstacle_detected
        time.sleep(0.05)
        order_finish_stop()
        if(not lidar_obstacle_detected):
            if currently_doing_subtask == TaskType.NORMAL_NAV.value:
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_MoveOn_en
                return 'Go to: MoveOn'
            elif currently_doing_subtask == TaskType.BUILDING_PICKUP.value:
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_MoveOn_en
                return 'Go to: Building_PickUp_MoveOn'
            elif currently_doing_subtask == TaskType.BUILDING_DROPDOWN.value:
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_MoveOn_en
                return 'Go to: Building_DropDown_MoveOn'
            elif currently_doing_subtask == TaskType.BONDEROLE_POSE.value:
                MASTER_SMachineCurrentState_en = MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_MoveOn_en
                return 'Go to: Bonderole_Pose_MoveOn'
        else:
            return 'Go to: ConfirmedStop'


class Finished(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Finished']) 
        self.counter = 0

    def execute(self, userdata):
        global estimated_score
        order_finish_stop()
        signal.signal(signal.SIGINT, exit_handler)
        if(True):
            if (self.counter == 0):
                #estimated_score = estimated_score + 10
                #here i removed encrimenting the score because i will do it in wait to reach when the robot is close to the position
                self.counter = self.counter + 1
            return 'Go to: Finished'
        

########################################## PUBLISHERS CLASS ###############################################

class Publishers(Node):

    def __init__(self):
        super().__init__('publishers')

        # Create publishers as attributes
        self.Navigator_Acknowledge_Publisher = self.create_publisher(MasterAcknowledgeSignal, 'ros_can_interface/master_acknowledge', 10)
        self.Navigator_Target_Publisher = self.create_publisher(MasterNavigationMessage, 'ros_can_interface/master_nav', 10)
        self.Navigator_Stop_Publisher = self.create_publisher(MasterStopSignal, 'ros_can_interface/stop_signal', 10)
        self.Navigator_Reset_Publisher = self.create_publisher(MasterResetSignal, 'ros_can_interface/master_reset', 10)
        self.Current_Direction_Publisher = self.create_publisher(Bool, 'current_direction',10)
        self.get_logger().info(f"Initialised all publishers ")    

class EstimatedScorePublisher(Node):
    def __init__(self):
        super().__init__('estimated_score_publisher')
        self.estimated_score_publisher = self.create_publisher(Int32, 'estimated_score',10)
        self.create_timer(1, self.estimated_score_callback)
        self.return_to_finish_spot_incrementing_counter = 0

    def estimated_score_callback(self):
        global estimated_score
        need_to_incerement_score = increment_score_returned_to_finish_spot_checker()
        if need_to_incerement_score == True and self.return_to_finish_spot_incrementing_counter == 0 :
            estimated_score = estimated_score + 10
            self.return_to_finish_spot_incrementing_counter = self.return_to_finish_spot_incrementing_counter + 1

        msg = Int32()
        msg.data = estimated_score
        self.estimated_score_publisher.publish(msg)
        print("estimated score", estimated_score)

class CurrentTaskPublisher(Node):
    def __init__(self):
        super().__init__('estimated_score_publisher')
        self.current_task_publisher = self.create_publisher(CurrentTask, 'current_task',10)
        
        self.create_timer(0.1, self.current_task_callback)

    def current_task_callback(self):
        global currently_doing_subtask
        global next_task
        msg = CurrentTask()
        if currently_doing_subtask == None or next_task == None:
            msg.current_task_id = -50
            msg.currently_doing_subtask = -50
        else:     
            msg.current_task_id = next_task.id
            msg.currently_doing_subtask = currently_doing_subtask
        self.current_task_publisher.publish(msg)

########################################## SUBSCRIBERS CLASS ###############################################
    
class Subscribers(Node):
    def __init__(self):
        super().__init__('subscribers')
        self.navigator_receive_position_subscriber = Navigator_Receive_Position_Subscriber()
        self.lidar_obstacle_detected_subscriber = LidarObstacleDetectedSubscriber()
        self.init_position_subscriber = InitPositionSubscriber()
        self.jack_signal_subscriber = JackSignalSubscriber()
        self.get_logger().info(f"Initialised all subscribers ")   
        
class InitPositionSubscriber(Node):
    def __init__(self):
        super().__init__('statemachine_init_position_subscriber')
        self.create_subscription(MasterNavigationMessage,'init_position',self.init_position_callback ,10)
    
    def init_position_callback(self, msg):
        global init_position
        init_position = msg
        #print("JEEEEEEEEEEEEEEEEEEEEEEEEEEEERE")
        #print(init_position.nav_target_x)
        #print(init_position.nav_target_y)
        #self.get_logger().info(f'Robot init_position: {init_position}')

class JackSignalSubscriber(Node):
    def __init__(self):
        super().__init__('statemachine_jack_signal_subscriber')
        self.create_subscription(Bool,'jack_signal',self.jack_signal_callback ,10)
    
    def jack_signal_callback(self, msg):
        global jack_state
        jack_state = msg.data
        #self.get_logger().info(f'jack_state: {jack_state}')

class Navigator_Receive_Position_Subscriber(Node):
    def __init__(self):
        super().__init__('navigator_receive_position_subscriber')
        self.navigator_receive_position_subscriber = self.create_subscription(NavigatorNavigationMessage, 'ros_can_interface/navigator_nav', self.navigator_receive_position_callback, 10)
        self.get_logger().info('NavigatorReceivePositionSubscriber node has been started.')

    def navigator_receive_position_callback(self ,nav_data: NavigatorNavigationMessage):
        global current_position
        global current_navigator_state
        #self.get_logger().info(f"Received: navigation data")    
        current_position = Pose2D(x=nav_data.nav_current_x, y=nav_data.nav_current_y, theta=nav_data.nav_current_angle)
        current_navigator_state = nav_data.nav_current_state


class LidarObstacleDetectedSubscriber(Node):
    def __init__(self):
        super().__init__('Obstacle_Enemy_Detected')
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            depth=10
        )   
        self.lidar_obstacle_detected_subscriber = self.create_subscription(Bool, 'Obstacle_Enemy_Detected', self.lidar_obstacle_detected_callback, qos_profile)
        self.get_logger().info('LidarObstacleDetectedSubscriber node has been started.')

    def lidar_obstacle_detected_callback(self, msg):
        global lidar_obstacle_detected
        lidar_obstacle_detected = msg.data
        #self.get_logger().warn(f'Obstacle Detected or not: {lidar_obstacle_detected}')

#for testing without the stm32 returning the real robot state
class NavigatorStateSubscriber(Node):
    def __init__(self):
        super().__init__('navigator_state_subscriber')
        self.nav_current_state_simulation = self.create_subscription(Int32,'simulation_navigator_state',
                                                     self.navigator_state_callback,10)#for testing 

        self.get_logger().info('NavigatorStateSubscriber node has been started.')

    def navigator_state_callback(self, msg):
        
        global current_navigator_state
        #self.get_logger().info('NavigatorStateSubscriber node has been started.')
        # Assign the received value to the global variable
        current_navigator_state = msg.data   
        print("navigator state:",current_navigator_state)    

       
########################################## CLIENTS CLASSES ##############################################

class Clients():
    global clients_instance

    def __init__(self):
        self.get_next_task_point_client = GetNextTaskPointClient()
        self.get_next_subtask_client = GetNextSubTaskPointClient()
        self.delete_task_client = DeleteTaskClient()

class DeleteTaskClient(Node):
    def __init__(self):
        super().__init__('delete_task_client')
        self.client = self.create_client(DeleteTask, 'delete_task_service')
        while not self.client.wait_for_service(timeout_sec=1.0):        
            self.get_logger().info('Delete Task Service not available, waiting again...')
        self.get_logger().warn('Delete Task Service is available, ready to send request!')
    
    def send_request(self, task_id):
        request = DeleteTask.Request()
        request.id = task_id
        self.get_logger().info('Sending request to delete task...')
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.done():
            try:
                response = future.result()
                self.get_logger().info(f"Task with id {task_id} has been deleted")
            except Exception as e:
                self.get_logger().error(f"Service call failed: {e}")
                return None
            

class GetNextTaskPointClient(Node):
    def __init__(self):
        super().__init__('get_next_task_point_client')
        self.client = self.create_client(GetNextTaskPoint, 'get_next_task_point_service')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Get_Next_Task_Point_Service not available, waiting again...')
        self.get_logger().warn('GetNextTaskPoint Service is available, ready to send request!')

    def send_request(self):
        global current_task
        global next_task
        global return_to_finish_spot_flag
        #return_to_finish_spot_checker() commented this so it doesnt return from abd poistion
        request = GetNextTaskPoint.Request()  # Create a request object
        
        self.get_logger().info('Sending request for next task point...')
        if (current_task is None):
            #here send -100 so the strategy node knows that the current_stask = None: we start the match now
            request.task_id = -100
        elif return_to_finish_spot_flag == True:
            request.task_id = -1000    
        # Send the request and block until a response is received
        else:
            request.nav_target_x = current_task.position.x
            request.nav_target_y = current_task.position.y
            request.nav_target_angle = current_task.position.theta
            request.task_id = current_task.id
            request.task_type = current_task.type
            """print("Request Details:")
            print(f"nav_target_x: {request.nav_target_x}")
            print(f"nav_target_y: {request.nav_target_y}")
            print(f"nav_target_angle: {request.nav_target_angle}")
            print(f"task_id: {request.task_id}")
            print(f"task_type: {request.task_type}")"""
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)  # Wait until the service call is completed

        if future.done():
            try:
                response = future.result()  # Get the response
                """print("Response Details:")
                print(f"task_id: {response.task_id}")
                print(f"nav_target_x: {response.nav_target_x}")
                print(f"nav_target_y: {response.nav_target_y}")
                print(f"nav_target_angle: {response.nav_target_angle}")
                print(f"task_type: {response.task_type}")
                print(f"nav_is_forward: {response.nav_is_forward}")
                print(f"score: {response.score}")
                print(f"nav_linear_velocity_choice: {response.nav_linear_velocity_choice}")
                print(f"nav_angular_velocity_choice: {response.nav_angular_velocity_choice}")
                print(f"nav_linear_acceleration_choice: {response.nav_linear_acceleration_choice}")
                print(f"nav_angular_acceleration_choice: {response.nav_angular_acceleration_choice}")
                print(f"nav_with_platforms: {response.nav_is_with_platforms}")"""
                # Update current_task with the received data
                next_task = Task(
                    id=response.task_id,
                    position=Pose2D(x=response.nav_target_x, y=response.nav_target_y, theta=response.nav_target_angle),
                    type=response.task_type,
                    direction=response.nav_is_forward,
                    score=response.score,
                    linear_velocity=response.nav_linear_velocity_choice,
                    angular_velocity=response.nav_angular_velocity_choice,
                    linear_acceleration=response.nav_linear_acceleration_choice,
                    angular_acceleration=response.nav_angular_acceleration_choice,
                    is_with_platforms = response.nav_is_with_platforms,
                    subtask_list=[],
                )
                return next_task
            except Exception as e:
                self.get_logger().error(f"Service call failed: {e}")
                return None


class GetNextSubTaskPointClient(Node):
    def __init__(self):
        super().__init__('get_next_subtask_client')
        self.client = self.create_client(GetNextSubTaskPoint, 'get_next_subtask')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.get_logger().warn('GetNextSubTaskPoint Service is available, ready to send request!')

    def send_request(self):
        global current_subtask_order
        global current_task
        request = GetNextSubTaskPoint.Request()  # Create a request object
        request.current_subtask_order = current_subtask_order
        request.current_task_id = current_task.id
        self.get_logger().info('Sending request for available subtasks...')
        self.future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, self.future)  # Wait until the service call is completed

        if self.future.done():
            try:
                response = self.future.result()
                return response
            except Exception as e:
                self.get_logger().error(f"Service call failed: {e}")
                return None      

########################################## TIMER CLASS ############################################

class TimeCounter(Node):
    """
        this Node is used to count the time the robot is playing
    """
    def __init__(self):
        super().__init__('time_counter')
        self.create_timer(1, self.time_callback)
        self.current_playing_time_pub = self.create_publisher(Int32, 'current_playing_time', 10)
        self.get_logger().info('Time Counter Node has been started.')

    def time_callback(self):
        global jack_state
        global current_playing_time
        if jack_state == True:
            current_playing_time += 1
            print("playing time", current_playing_time)
        # Publish the current_playing_time
        msg = Int32()
        msg.data = current_playing_time
        self.current_playing_time_pub.publish(msg)
    
class Robot_Stuck_Checker_WaitToReach(Node):
    """
        this Node is used to check if the robot is stuck in stm32 state WaitToReach because of tuning problems
        if nor the angle or the position of the robot is changing for more than 3 seconds than the robot is stuck
        so the treatment is to send a stop signal to the navigator and than resends the point to make the robot accelerates 
        and destuck fom that position
    """
    def __init__(self):
        super().__init__('robot_stuck_checker_wait_to_reach')
        self.create_timer(0.1, self.robot_stuck_checker_wait_to_reach_callback)
        self.first_time_entering_state = False
        self.local_time = 0
        self.initial_test_x = None
        self.initial_test_y = None
        self.initial_test_theta = None
        self.get_logger().info('Robot Stuck Checker WaitToReach Node has been started.')

    def robot_stuck_checker_wait_to_reach_callback(self):
        global MASTER_SMachineCurrentState_en
        global robot_stuck_wait_to_reach
        global current_playing_time
        if (MASTER_SMachineCurrentState_en == MASTER_SMachineStates_ten.MASTER_SMachine_WaitToReach_en
        or MASTER_SMachineCurrentState_en == MASTER_SMachineStates_ten.MASTER_SMachine_Building_PickUp_WaitToReach_en
        or MASTER_SMachineCurrentState_en == MASTER_SMachineStates_ten.MASTER_SMachine_Building_DropDown_WaitToReach_en
        or MASTER_SMachineCurrentState_en == MASTER_SMachineStates_ten.MASTER_SMachine_Bonderole_Pose_WaitToReach_en):
            
            if not self.first_time_entering_state:
                self.local_time = current_playing_time
                self.initial_test_x = current_position.x 
                self.initial_test_y = current_position.y
                self.initial_test_theta = current_position.theta
                self.first_time_entering_state = True
            else :     
                if (current_playing_time - self.local_time) >= 3:#was 4
                    if (abs(current_position.x-self.initial_test_x) < 0.3 and abs(current_position.y-self.initial_test_y) < 0.3 and abs(current_position.theta-self.initial_test_theta) < 0.3):
                        robot_stuck_wait_to_reach = True
                        self.get_logger().warn('Robot is stuck!!!!!!!!!!!!!!!!!!!!!!!!')
                    else:
                        robot_stuck_wait_to_reach = False
                    
                    self.local_time = current_playing_time
                    self.initial_test_x = current_position.x 
                    self.initial_test_y = current_position.y
                    self.initial_test_theta = current_position.theta    
                else:
                    robot_stuck_wait_to_reach = False
        else:
            robot_stuck_wait_to_reach = False
            self.first_time_entering_state = False

########################################## UTILITY FUNCTIONS ############################################

def increment_score_returned_to_finish_spot_checker():
    global current_position
    global estimated_score
    global next_task
    if ((current_position.x >= 2400.0 or current_position.x <= 600.0 ) and current_position.y >= 1400.0 and next_task.type == TaskType.RETURN_TO_FINISH_SPOT.value):#y was 1500
        return True
    else :
        return False

def convert_next_task_to_nav_order(current_task: Task):
    nav_order = MasterNavigationMessage()
    nav_order.nav_target_x = current_task.position.x
    nav_order.nav_target_y = current_task.position.y
    nav_order.nav_target_angle = current_task.position.theta  
    nav_order.nav_is_forward = current_task.direction
    nav_order.nav_linear_velocity_choice = current_task.linear_velocity
    nav_order.nav_angular_velocity_choice = current_task.angular_velocity
    nav_order.nav_linear_acceleration_choice = current_task.linear_acceleration
    nav_order.nav_angular_acceleration_choice = current_task.angular_acceleration
    nav_order.nav_is_with_platforms = current_task.is_with_platforms
    return nav_order

def convert_next_subtask_to_nav_order(current_subtask_msg: GetNextSubTaskPoint.Response):
    nav_order = MasterNavigationMessage()
    nav_order.nav_target_x = current_subtask_msg.nav_target_x
    nav_order.nav_target_y = current_subtask_msg.nav_target_y
    nav_order.nav_target_angle = current_subtask_msg.nav_target_angle
    nav_order.nav_is_forward = current_subtask_msg.nav_is_forward
    nav_order.nav_linear_velocity_choice = current_subtask_msg.nav_linear_velocity_choice
    nav_order.nav_angular_velocity_choice = current_subtask_msg.nav_angular_velocity_choice
    nav_order.nav_linear_acceleration_choice = current_subtask_msg.nav_linear_acceleration_choice
    nav_order.nav_angular_acceleration_choice = current_subtask_msg.nav_angular_acceleration_choice
    nav_order.nav_is_with_platforms = current_subtask_msg.nav_is_with_platforms
    return nav_order

def wait_mechanism_mouvement():
    time.sleep(5)
    #here i can block until the subtask generator node returns publishes that the mechanism ended his action
    #than i go to destination reached
    #should implement wait time for each mechanism mouvement type

def communication_instances_init():
    global publishers_instance
    global subscribers_instance
    global clients_instance
    global servers_instance

    publishers_instance = Publishers()
    subscribers_instance= Subscribers()
    clients_instance = Clients()
    
def order_finish_stop():
    global current_playing_time
    global TOTAL_PLAYING_TIME
    if current_playing_time >= TOTAL_PLAYING_TIME:
        """print("NEEEEEEEEEEEEEEEEEED TO STOOOOOOOP")
        print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")"""
        send_reset_signal()

def return_to_finish_spot_checker():
    global current_task
    global return_to_finish_spot_flag
    global current_playing_time
    """print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
    print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
    print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")"""
    print("current_playing_time from FINIIIIIIIIIIIISH SPOTTTTT", current_playing_time)
    if current_playing_time >= (TOTAL_PLAYING_TIME - 25) and current_task.type == TaskType.BUILDING_DROPDOWN.value:
        #here im not acutally doing a dropdown task...but based on the table: a dropdown is followed by a pickup
        #and this funtion is called in moveon so if current_task is a dropdown than the next is pickup but i don't have the next task yet
        #maybe need to change it to use next_task instead
        """print("RETURN TO FINISH SPOT IS TRIGERRED BECAUSENEXT TASK IS BUILDING PICKUP!!!!!!!!!!!!!!!!!!!!!!!!")
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")"""
        return_to_finish_spot_flag = True #to disable this shit need to return it to True

########################################## SUBTASK FUNCTION  ############################################

def get_next_subtask():#
    global clients_instance
    response = clients_instance.get_next_subtask_client.send_request()
    """
    response type:
    int32 current_subtask_order
    float32 nav_target_x
    float32 nav_target_y
    float32 nav_target_angle
    bool nav_is_forward
    int8 nav_linear_velocity_choice
    int8 nav_angular_velocity_choice
    """
    """
    the form i want to use :
    float32 nav_target_x
    float32 nav_target_y
    float32 nav_target_angle
    bool nav_is_forward
    int8 nav_linear_velocity_choice
    int8 nav_angular_velocity_choice
    int8 nav_linear_acceleration_choice
    int8 nav_angular_acceleration_choice

    """
    return response 

########################################## COMMUNICATION FUNCTIONS ############################################

def get_next_task_point():
    global clients_instance
    clients_instance.get_next_task_point_client.send_request()

def send_target_order(nav_order):
    global publishers_instance
    publishers_instance.Navigator_Target_Publisher.publish(nav_order)

def send_reset_signal():
    global publishers_instance
    ResetSignal = MasterResetSignal()
    ResetSignal.master_reset_signal = True
    publishers_instance.Navigator_Reset_Publisher.publish(ResetSignal)

def send_stop_signal():
    global publishers_instance
    StopSignal = MasterStopSignal()
    StopSignal.stop_signal_state = True
    publishers_instance.Navigator_Stop_Publisher.publish(StopSignal)

def send_acknowledge_signal():
    global publishers_instance
    AcknowledgeSignal = MasterAcknowledgeSignal()
    AcknowledgeSignal.master_acknowledge_signal = True
    publishers_instance.Navigator_Acknowledge_Publisher.publish(AcknowledgeSignal)

########################################## SPECIAL EXIT HANDLING ###########################################

def exit_handler(sig, frame) -> None:
    print('Ctrl+C pressed. Exiting...')
    rclpy.shutdown()

########################################## MAIN FUNCTION ####################################################

def main(args=None):
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    global clients_instance
    global subscribers_instance
    # Initialize ROS 2
    rclpy.init(args=args)
    communication_instances_init()

    # Create all nodes
    current_nav_state_sub = NavigatorStateSubscriber()
    executor = MultiThreadedExecutor()
    time_counter = TimeCounter()
    robot_stuck_wait_to_reach = Robot_Stuck_Checker_WaitToReach()
    estimated_score_node = EstimatedScorePublisher()
    current_task__publisher_node = CurrentTaskPublisher()
    # Add nodes to the executor
    executor.add_node(clients_instance.get_next_task_point_client)
    executor.add_node(clients_instance.get_next_subtask_client)
    executor.add_node(subscribers_instance.navigator_receive_position_subscriber)
    executor.add_node(current_nav_state_sub)
    executor.add_node(subscribers_instance.lidar_obstacle_detected_subscriber)
    executor.add_node(clients_instance.delete_task_client)
    executor.add_node(time_counter)
    executor.add_node(estimated_score_node)
    executor.add_node(current_task__publisher_node)
    executor.add_node(robot_stuck_wait_to_reach)
    executor.add_node(subscribers_instance.jack_signal_subscriber)
    executor.add_node(subscribers_instance.init_position_subscriber)
    # Register signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, exit_handler)

    # Spin the executor in a separate thread to handle callbacks
    spin_thread = threading.Thread(target=executor.spin)
    spin_thread.start()

    try:
        # Run the state machine logic here in the main thread
        sm = MainStateMachine()
        sm.execute()  # Execute the state machine in the main thread

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        # Clean up and destroy all nodes when done
        clients_instance.get_next_task_point_client.destroy_node()
        clients_instance.get_next_subtask_client.destroy_node()
        subscribers_instance.navigator_receive_position_subscriber.destroy_node()
        current_nav_state_sub.destroy_node()
        subscribers_instance.lidar_obstacle_detected_subscriber.destroy_node()
        clients_instance.delete_task_client.destroy_node()
        time_counter.destroy_node()
        estimated_score_node.destroy_node()
        current_task__publisher_node.destroy_node()
        robot_stuck_wait_to_reach.destroy_node()
        subscribers_instance.jack_signal_subscriber.destroy_node()
        subscribers_instance.init_position_subscriber.destroy_node()
        # Shutdown ROS 2
        rclpy.shutdown()

        # Wait for the executor's spin thread to finish
        spin_thread.join()

if __name__ == '__main__':
    main()

