import rclpy
import smach
import time
from rclpy.node import Node
from enum import Enum

#function to test

"""STM32 State:

    0:MASTER_NavigatorIdle_en,                        
    1:MASTER_NavigatorReady_en,                       
    2:MASTER_NavigatorBusy_en,                        
	3:Nav_NvigatorWaitToReceiveAcknowledge_en,        
    4:MASTER_NavigatorReachedDest_en,                
	5:MASTER_NavigatorOrderSuddenStop_en,             
	6:MASTER_NavigatorSuddenStop_en,                  
	7:MASTER_NavigatorConfirmedStop_en,              
	8:MASTER_NavigatorInit_en,                        
	9:MASTER_NavigatorBlockageDetected_en,           
	10:MASTER_NavigatorWallBlockageDetected_en         
    """

class MASTER_NavigatorStates_ten (Enum):

    MASTER_NavigatorIdle_en = 0
    MASTER_NavigatorReady_en = 1
    MASTER_NavigatorBusy_en = 2
    MASTER_NvigatorWaitToReceiveAcknowledge_en = 3
    MASTER_NavigatorReachedDest_en = 4
    MASTER_NavigatorConfirmedStop_en = 5
    MASTER_NavigatorInit_en = 6

class Master_SMachineStates_ten (Enum):

    MASTER_SMachine_Idle_en = 0
    MASTER_SMachine_WaitForSignal_en = 1
    MASTER_SMachine_MoveOn_en = 2
    MASTER_SMachine_WaitToReach_en = 3
    MASTER_SMachine_DestinationReached_en = 4
    MASTER_SMachine_SuddenStop_en = 5
    MASTER_SMachine_ConfirmedStop_en = 6
    MASTER_SMachine_Finish_en = 7
    Master_SMachine_Building_PickUp_en = 8
    Master_SMachine_Building_DropDown_en = 9

class Master_Sub_SMachineStates_ten (Enum):

    Master_SMachine_Building_PickUp_Init_en = 0
    Master_SMachine_Building_PickUp_MoveOn_en = 1
    Master_SMachine_Building_PickUp_WaitToReach_en = 2
    Master_SMachine_Building_PickUp_DestinationReached_en = 3
    Master_SMachine_Building_PickUp_Finish_en = 4
    Master_SMachine_Building_DropDown_Init_en = 5
    Master_SMachine_Building_DropDown_MoveOn_en = 6
    Master_SMachine_Building_DropDown_WaitToReach_en = 7
    Master_SMachine_Building_DropDown_DestinationReached_en = 8
    Master_SMachine_Building_DropDown_Finish_en = 9


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
                                             'Go to: MoveOn': 'MoveOn',})
                                                

            smach.StateMachine.add('WaitToReach', WaitToReach(),
                                transitions={'Go to: DestinationReached': 'DestinationReached',
                                            'Go to: BlockageDetected': 'BlockageDetected',
                                            'Go to: SuddenStop': 'SuddenStop',
                                            'Go to: WaitToReach': 'WaitToReach', })
                                                
            smach.StateMachine.add('BlockageDetected', BlockageDetected(),
                                transitions={ 'Go to: MoveOn': 'MoveOn',
                                            'Go to: BlockageDetected': 'BlockageDetected',})

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
                                            'Go to: ConfirmedStop': 'ConfirmedStop',})                                         
                                               
            smach.StateMachine.add('DestinationReached', DestinationReached(),
                                transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: Finished': 'Finished',
                                            'Go to: Building_PickUp': 'Building_PickUp',
                                            'Go to: Building_DropDown': 'Building_DropDown',
                                            'Go to: DestinationReached': 'DestinationReached',})
                                            
            smach.StateMachine.add('Building_PickUp', BuildingPickUp(),
                                transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: SuddenStop': 'SuddenStop',
                                            'Go to: Building_PickUp': 'Building_PickUp',})

            smach.StateMachine.add('Building_DropDown', BuildingDropDown(),
                                transitions={'Go to: MoveOn': 'MoveOn',
                                            'Go to: SuddenStop': 'SuddenStop',
                                            'Go to: Building_DropDown': 'Building_DropDown',})

            smach.StateMachine.add('Finished', Finished(),
                                transitions={'Go to: Finished': 'Finished'})                                                    


class BuildingPickUp(smach.StateMachine):
    def __init__(self):
        super().__init__(outcomes=['Go to: MoveOn',
                                   'Go to: SuddenStop',
                                   'Go to: Building_PickUp'])
        with self:
            smach.StateMachine.add('Building_PickUp_Init',Building_PickUp_Init(),
                                transitions={'Go to: Building_PickUp_MoveOn': 'Building_PickUp_MoveOn',
                                            'Go to: Building_PickUp_Init': 'Building_PickUp_Init',})
            
            smach.StateMachine.add('Building_PickUp_MoveOn',Building_PickUp_MoveOn(),
                                transitions={'Go to: Building_PickUp_WaitToReach': 'Building_PickUp_WaitToReach',
                                            'Go to: Building_PickUp_MoveOn': 'Building_PickUp_MoveOn',})
            
            smach.StateMachine.add('Building_PickUp_WaitToReach',Building_PickUp_WaitToReach(),
                                transitions={'Go to: Building_PickUp_DestinationReached': 'Building_PickUp_DestinationReached',
                                            'Go to: Building_PickUp_WaitToReach': 'Building_PickUp_WaitToReach',})
            
            smach.StateMachine.add('Building_PickUp_DestinationReached',Building_PickUp_DestinationReached(),
                                transitions={'Go to: Building_PickUp_Finished': 'Building_PickUp_Finished',
                                            'Go to: Building_PickUp_DestinationReached': 'Building_PickUp_DestinationReached',})
            
            smach.StateMachine.add('Building_PickUp_Finished',Building_PickUp_Finished(),
                                transitions={'Go to: MoveOn':'MoveOn'})


class BuildingDropDown(smach.StateMachine):
    def __init__(self):
        super().__init__(outcomes=['Go to: MoveOn',
                                   'Go to: SuddenStop',
                                   'Go to: Building_DropDown'])
        with self:
            smach.StateMachine.add('Building_DropDown_Init',Building_DropDown_Init(),
                                transitions={'Go to: Building_DropDown_MoveOn': 'Building_DropDown_MoveOn',
                                            'Go to: Building_DropDown_Init': 'Building_DropDown_Init',})
            
            smach.StateMachine.add('Building_DropDown_MoveOn',Building_DropDown_MoveOn(),
                                transitions={'Go to: Building_DropDown_WaitToReach': 'Building_DropDown_WaitToReach',
                                            'Go to: Building_DropDown_MoveOn': 'Building_DropDown_MoveOn',})
            
            smach.StateMachine.add('Building_DropDown_WaitToReach',Building_DropDown_WaitToReach(),
                                transitions={'Go to: Building_DropDown_DestinationReached': 'Building_DropDown_DestinationReached',
                                            'Go to: Building_DropDown_WaitToReach': 'Building_DropDown_WaitToReach',})
            
            smach.StateMachine.add('Building_DropDown_DestinationReached',Building_DropDown_DestinationReached(),
                                transitions={'Go to: Building_DropDown_Finished': 'Building_DropDown_Finished',
                                            'Go to: Building_DropDown_DestinationReached': 'Building_DropDown_DestinationReached',})
            
            smach.StateMachine.add('Building_DropDown_Finished',Building_DropDown_Finished(),
                                transitions={'Go to: MoveOn':'MoveOn'})


class Idle(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Init',
                                             'Go to: Idle'])
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Init'
        else:
            return 'Go to: Idle'
        

class Init(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: WaitForSignal',
                                             'Go to: Init'])
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: WaitForSignal'
        else:
            return 'Go to: Init'        


class WaitForSignal(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: WaitForSignal'])
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: MoveOn'
        else:
            return 'Go to: WaitForSignal'   
        
class MoveOn(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: WaitToReach',
                                             'Go to: MoveOn'])
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
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
        time.sleep(1)  #()
        if(True):
            return 'Go to: DestinationReached'
        else:
            return 'Go to: WaitToReach'         
        #should handle sudden stop state transition
        
    
class DestinationReached(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: Finished',
                                             'Go to: Building_PickUp',
                                             'Go to: Building_DropDown',
                                             'Go to: DestinationReached']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_DropDown'
        else:
            return 'Go to: WaitToReach' 
        
class Building_PickUp_Init(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_MoveOn',
                                             'Go to: Building_PickUp_Init']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_PickUp_MoveOn'
        else:
            return 'Go to: Building_PickUp_Init'

class Building_PickUp_MoveOn(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_WaitToReach',
                                             'Go to: Building_PickUp_MoveOn']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_PickUp_WaitToReach'
        else:
            return 'Go to: Building_PickUp_MoveOn'
    
    
class Building_PickUp_WaitToReach(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_DestinationReached',
                                             'Go to: Building_PickUp_WaitToReach']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_PickUp_DestinationReached'
        else:
            return 'Go to: Building_PickUp_WaitToReach'
    #should handle sudden stop state transition

    
class Building_PickUp_DestinationReached(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_PickUp_Finished',
                                             'Go to: Building_PickUp_DestinationReached']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_PickUp_Finished'
        else:
            return 'Go to: Building_PickUp_DestinationReached'    


class Building_PickUp_Finished(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: MoveOn'


class Building_DropDown_Init(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_MoveOn',
                                             'Go to: Building_DropDown_Init']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_PickUp_Finished'


class Building_DropDown_MoveOn(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_WaitToReach',
                                             'Go to: Building_DropDown_MoveOn']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_DropDown_WaitToReach'
        else:
            return 'Go to: Building_DropDown_MoveOn'
    
    
class Building_DropDown_WaitToReach(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_DestinationReached',
                                             'Go to: Building_DropDown_WaitToReach']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: MoveOn'
        else:
            return 'Go to: Building_DropDown_WaitToReach'
        #should handle SuddenStop state transition

    
class Building_DropDown_DestinationReached(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Building_DropDown_Finished',
                                             'Go to: Building_DropDown_DestinationReached']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: Building_DropDown_Finished'
        else:
            return 'Go to: Building_DropDown_DestinationReached'    


class Building_DropDown_Finished(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: MoveOn'
        

class BlockageDetected(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: BlockageDetected']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: MoveOn'
        else:
            return 'Go to: BlockageDetected'  


class SuddenStop(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: WaitSuddenStop',
                                             'Go to: SuddenStop']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: WaitSuddenStop'
        else:
            return 'Go to: SuddenStop'


class WaitSuddenStop(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: ConfirmedStop',
                                             'Go to: WaitSuddenStop']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: ConfirmedStop'
        else:
            return 'Go to: WaitSuddenStop'


class ConfirmedStop(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: MoveOn',
                                             'Go to: ConfirmedStop']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: MoveOn'
        else:
            return 'Go to: ConfirmedStop'


class Finished(smach.State):
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['Go to: Finished']) 
    
    def execute(self, userdata):
        time.sleep(1)  #()
        if(True):
            return 'Go to: MoveOn'


def main(args=None):
    rclpy.init(args=args)
    sm = MainStateMachine()
    outcome = sm.execute()
    rclpy.shutdown()


if __name__ == '__main__':
    main()