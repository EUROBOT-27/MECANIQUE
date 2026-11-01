
# 8. Additional Notes:

* If you want to test the navigation code without CAN connection, go into the periodic callback replace Nav_vStateMachine_Routine() with Nav_vStandaloneStateMachine_Routine() then go to Nav_Standalone.c and set the waypoints you'd like the robot to follow .Also, in that same file go into MASTER_NavigatorIdle_en state and set the current coordinates.

* The people responsible for the ROS2 codebase should be aware of these things:
    * When simulating the robot,they should note that its position(current x,current y,theta) is calculated from the center of l'entraxe which is the line linking the two encoder wheels' centers.
    * current_angle=0 corresponds to when the robot is on the X_axis and all of the coordinates sent to the stm32 should follow a fixed reference on the map.
    * They can only send positive X,Y,angles to the stm32.For example if they want to rotate the robot -90° they should send 270° as a target angle (the stm32 will normalize the angle and rotate the robot the intended way).
    * If they want the robot to reach a destination and then not rotate(meaning not enter the rotateafterstate and go straight back to idle state waiting for new coordinates),they should give a target angle=655.
    * In the case where the robot reaches a target and rotates then they want it to  rotate again a certain angle ,they should give those exact coordinates to the person with the nav codebase and they should add those x,y coordinates in the xy idle case in this if condition 
    ```
    if((*Nav_TargetX_mm_d==3200 )&&(*Nav_TargetY_mm_d==2200))
			{
				Nav_GoToXY_State_en = Nav_GoToXY_RotateAfter_en;
			}  
    ```


    
* If the robot is getting stuck **repeatedly** in wait_to_reach state recheck if the minimum commands are still able to move the robot or check batteries.

* if the robot gets to a destination and then start moving very slowly even though it looks like it reached the target,check Nav_TargetLinearVelocity_d threshhold in this if condition:
```
		if( ( Nav_RemainingDistance_mm_d <= 0.0) || ( Nav_TargetLinearVelocity_d <= 0.03 ) )
		{
			Nav_TargetLinearVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}
```



    
* If the robot is getting stuck **repeatedly** in wait_to_reach state recheck if the minimum commands are still able to move the robot or check batteries.

* if the robot gets to a destination and then start moving very slowly even though it reached the target,check Nav_TargetLinearVelocity_d threshhold in this if condition:
```
		if( ( Nav_RemainingDistance_mm_d <= 0.0) || ( Nav_TargetLinearVelocity_d <= 0.03 ) )
		{
			Nav_TargetLinearVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}
```


