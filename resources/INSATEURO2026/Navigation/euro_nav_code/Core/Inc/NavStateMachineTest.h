
#ifndef INC_NAVSTATEMACHINETEST_H_
#define INC_NAVSTATEMACHINETEST_H_

#include "main.h"
/*
typedef enum Nav_NavigatorCurrentStates_ten{
	Nav_NavigatorIsIdle_en,
	Nav_NavigatorReadyToReceiveTarget_en,
	Nav_NavigatorWaitToReachDestination_en,
	Nav_NavigatorDestinationReached_en,
	Nav_NvigatorWaitToReceiveAcknowledge_en,
	Nav_NavigatorSuddenStopConfirmed
}Nav_NavigatorCurrentStates_ten;
*/
//typedef enum Nav_NavigatorCurrentStates_ten{
//    MASTER_NavigatorIdle_en,
//    MASTER_NavigatorReady_en,
//    MASTER_NavigatorBusy_en,
//	Nav_NvigatorWaitToReceiveAcknowledge_en,
//    MASTER_NavigatorReachedDest_en,
//	MASTER_NavigatorConfirmedStop_en
//}Nav_NavigatorCurrentStates_ten;

void Nav_vStateMachine_Routine(void);
void Nav_vNavigatorStateMachineInit(void);
void Nav_navigationSimulation( double* Nav_currentX, double* Nav_currentY, double* Nav_currentAngle, uint8_t* ROBOT_Direction,uint8_t* Nav_withPlatforms);
void Nav_vDetectBlockage(void);

void Nav_navigationSimulationTest(double *Nav_CurrentX_mm_d, double *Nav_CurrentY_mm_d, double *Nav_CurrentAngle_deg_d);

void Nav_vNavigatorPositionInit(
		double* Nav_CurrentX_mm_d,
		double* Nav_CurrentY_mm_d,
		double* Nav_CurrentAngle_deg_d,
		double* Nav_CurrentAngle_rad_d,
		double* Nav_CurrentTargetAngle_deg_d,
		double* Nav_PrevTargetAngle_deg_d);
#endif /* INC_NAVSTATEMACHINETEST_H_ */
