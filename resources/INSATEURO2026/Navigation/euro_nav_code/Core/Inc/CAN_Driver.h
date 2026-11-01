#ifndef CAN_DRIVER_H_
#define CAN_DRIVER_H_

// Include dependencies
#include "main.h"
#include <string.h>
#include <stdlib.h>

typedef enum Nav_NavigatorSpeedingMode{
	Nav_NavigatorSlowSpeed_en,
	Nav_NavigatorNormalSpeed_en,
	Nav_NavigatorFastSpeed_en,
	Nav_NavigatorSuperFastSpeed_en
} Nav_NavigatorSpeedingMode_ten;

/* External declaration of CAN handler
 * You need to declare the Handler in the main.c
 * */
extern CAN_HandleTypeDef* CAN_Handler;

void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan);
void CAN_sendCurrentState(double Nav_currentX_mm_d, double Nav_currentY_mm_d, double Nav_currentAngle_deg_d,uint8_t Nav_currentState);
void CAN_receiveNewTarget(
	    double* Nav_targetX_mm_d,
	    double* Nav_targetY_mm_d,
	    double* Nav_targetAngle_deg_d,
	    uint8_t* Nav_isForward_b,
	    double* Nav_MaxVelocity_d,
	    double* Nav_MaxAngularVelocity_d,
	    double* Nav_Acc_d,
	    double* Nav_AngularAcc_d,
		uint8_t* Nav_withPlatforms
		);
void CAN_decodeMessage(
		double* Nav_targetX_mm_d,
		double* Nav_targetY_mm_d,
		double* Nav_targetAngle_deg_d,
		uint8_t* Nav_isForward_b,
		uint8_t* Nav_linearVilocityChoice,
		uint8_t* Nav_angularVilocityChoice,
		uint8_t* Nav_linearAccelerationChoice,
		uint8_t* Nav_angularAccelerationChoice,
		uint8_t* Nav_withPlatforms
		);
uint64_t CAN_encodeMessage(double Nav_currentX_mm_d, double Nav_currentY_mm_d, double Nav_currentAngle_deg_d,uint8_t Nav_currentState);
void CAN_filterConfig(void);
uint8_t  CAN_isStopSignal_b(void);
uint8_t CAN_isAcknowledgeSignal_b(void);
uint8_t CAN_isResetSignal_b(void);
void CAN_receiveInitPosition(
		double* Nav_CurrentX_mm_d,
		double* Nav_CurrentY_mm_d,
		double* Nav_CurrentAngle_deg_d
		);

#endif /* CAN_DRIVER_H_ */
