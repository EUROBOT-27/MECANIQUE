# Post odometry-calibration workflow:

Once the robot is calibrated ,put this in the HAL_TIM_PeriodElapsedCallback function in main.c
```
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim){
	if (htim==&htim6){

	//Nav_vTestPathStateMachine();
		//Nav_vFeedbackRoutine();

			//Nav_vStandaloneStateMachine_Routine();
		Nav_vStateMachine_Routine();
		Nav_vNavigationRoutine();
			if(currentPeriode == 0){
			CAN_sendCurrentState(Nav_CurrentX_mm_d ,  Nav_CurrentY_mm_d, Nav_CurrentAngle_deg_d , (uint8_t)Nav_NavigatorCurrentState_en);
		}
			currentPeriode = (currentPeriode + 1) % 20;

	}}
```
In NavStateMachineTest.c Replace `Nav_vIndependantTrajectoryStateMachine` in `NavStateMachineTest.c` with the third version of the same function found in `CalibratingFunctions.c`.

Then Test CAN connection by putting the CAN_RX_Message buffer in live expressions and verifying if anything is received by the master(raspberry) end once a message is sent.

Change these constants NAV_LINEAR_NORMAL_SPEED,NAV_ANGULAR_NORMAL_SPEED,NAV_LINEAR_NORMAL_ACC,NAV_ANGULAR_NORMAL_ACC with the values you found after tuning.

Now your code should be ready.