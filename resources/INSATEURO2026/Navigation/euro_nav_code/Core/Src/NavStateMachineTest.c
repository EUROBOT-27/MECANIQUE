
#include "NavStateMachineTest.h"
#include "CAN_Driver.h"
#include "NavConfig.h"
#include "NavTypes.h"
#include "NavConstants.h"
#include "Navigation.h"
#include "math.h"
extern uint8_t CAN_messageReceivedFlag;
extern uint8_t CAN_stopSignalFlag;
extern uint8_t CAN_master_acknowledgeFlag;
extern uint8_t CAN_resetSignalFlag;

// General Navigator States

extern double Nav_TargetX_mm_d , Nav_TargetY_mm_d , Nav_TargetArrivingAngle_deg_d ;
extern double Nav_CurrentX_mm_d,Nav_CurrentY_mm_d, Nav_CurrentAngle_deg_d;
extern Nav_GoToXY_States_ten Nav_GoToXY_State_en;
extern double Nav_CurrentTargetX_mm_d ;
extern double Nav_CurrentTargetY_mm_d ;
extern double Nav_CurrentX_mm_d;
//extern Nav_NavigatorCurrentStates_ten Nav_Navigator_CurrentState_en 	;
extern Nav_TrajectoryStates_ten Nav_TrajectoryState_en 		;
extern Nav_TrajectoryModes_ten  Nav_TrajectoryMode_en 			;
extern Nav_TrapezePhases_ten Nav_TrapezePhase_en 				;
extern Nav_GoToXY_States_ten Nav_GoToXY_State_en 	;
extern Nav_NavigatorCurrentStates_ten  Nav_NavigatorCurrentState_en  ;
extern double Nav_ConvertLeft_Ticks2mm_d     ;
extern double Nav_ConvertRight_Ticks2mm_d    ;
extern double Nav_MeasuredDistanceLeft_mm_d  ;
extern double Nav_MeasuredDistanceRight_mm_d ;
extern double Nav_MeasuredDistance_mm_d      ;
extern double Nav_PrevMeasuredDistance_mm_d  ;
extern double Nav_LimitDistance_mm_d         ;
extern double Nav_ReferenceAngle_deg_d ;
extern double Nav_ReferenceDistance_d ;
extern double Nav_MeasuredAngle_rad_d        ;
extern double Nav_PrevMeasuredAngle_rad_d    ;
extern double Nav_RemainingAngle_deg_d		  ;
extern int32_t Nav_RightTicks_i32;
extern int32_t Nav_LeftTicks_i32;
extern int32_t Nav_OverflowLeftEncoder_i32  ;
extern int32_t Nav_PrevLeftEncoderCNT_i32   ;
extern double Nav_TargetArrivingAngle_deg_d  ;
extern uint32_t Nav_Test_enter_2  ;
extern double Nav_TargetDistance_mm_d;
extern double Nav_RemainingDistance_mm_d  ;
extern double Nav_CurrentTargetDistance_mm_d ;
extern double Nav_PrevTargetDistance_mm_d ;
extern double Nav_TargetAngle_deg_d ;
extern double Nav_CurrentTargetAngle_deg_d    ;
extern double Nav_PrevTargetAngle_deg_d       ;
extern double Nav_TargetLinearVelocity_d    ;
extern double Nav_TargetAngularVelocity_d    ;
extern double Nav_ReferenceAngularVelocity_d ;
extern double Nav_MeasuredVelocity_mm_d     ;
extern double Nav_MeasuredAngularVelocity_rad_d ;
extern double Nav_MeasuredAngularVelocity_deg_d     ;
extern double Nav_ReferenceLinearVelocity_d  ;
extern double Nav_DistanceError_d            ;
extern double Nav_SumDistanceError_d         ;
extern double Nav_PID_DistanceOutput_d       ;
extern double Nav_AngleError_d               ;
extern double Nav_SumAngleError_d            ;
extern double Nav_PID_AngleOutput_d          ;
extern double Nav_Going_BackwardTargetX_mm_d ;
extern double Nav_Going_BackwardTargetY_mm_d ;
extern double Nav_GoingBackwardCurrentTargetX_mm_d   ;
extern double Nav_GoingBackwardCurrentTargetY_mm_d   ;
extern int32_t Nav_RightMotorCommand_i32  ;
extern int32_t Nav_LeftMotorCommand_i32   ;
extern int8_t Nav_RightMotorDirection_i8 ;
extern int8_t Nav_LeftMotorDirection_i8  ;
extern int32_t MONITOR_RightMotorCommand_i32 ;
extern int32_t MONITOR_LeftMotorCommand_i32  ;
extern double Nav_Acc_d           ;
extern double Nav_MaxVelocity_d   ;
extern double Nav_CurrentAngle_rad_d ;
extern double Nav_AngularAcc_d    ;
extern double Nav_PrevAngle_rad_d;
extern double Nav_MaxAngularVelocity_d  ;
extern double Nav_AverageAngle_rad_d;

extern uint32_t Nav_CurrentSample_u32   ;
extern uint32_t Nav_AccelerationSamples_u32   ;
extern uint32_t Nav_Counter_u32 ;
extern uint8_t Nav_BlockageCounter_u8 ;

extern double Nav_KpDistance_d    ;
extern double Nav_KiDistance_d    ;
extern double Nav_KdDistance_d    ;
extern double Nav_KpAngle_d       ;
extern double Nav_KiAngle_d       ;
extern double Nav_KdAngle_d       ;
extern double Nav_DeltaY_mm_d;
extern double Nav_DeltaX_mm_d;
extern double Nav_CurveCoefficient_d;
double Nav_vitessemax;
double Nav_MaxAngularVitesse;
double	Nav_Accel;
double Nav_AngularAccel;
uint8_t ROBOT_Direction = ROBOT_Going_Forward;
uint8_t Nav_withPlatforms = 2;

int32_t MINIMUM_RIGHT_MOTOR_FORWARD_COMMAND	=0;
int32_t MINIMUM_RIGHT_MOTOR_REVERSE_COMMAND	=	0;
int32_t MINIMUM_LEFT_MOTOR_FORWARD_COMMAND    = 0;
int32_t MINIMUM_LEFT_MOTOR_REVERSE_COMMAND	=	0;
int testB=0;
double MINIMUM_SATURATION_COMMAND=MINIMUM_SATURATION_COMMAND_LINEAR;

double Nav_PrevAngularVelocity_rad_d = 0;
double  Nav_Jerk_d =2025; /* max jerk — set by caller, scaled in SetPath */
double  Nav_SCurve_CurrentAccel_d = 0.0; /* running acceleration (per sample, post-scaling) */
double scaled_accel=0;
uint8_t Nav_SCurve_Phase_u8       = 0;   /* 1–7, 0 = idle */
double Nav_ProfileTargetDistance_mm_d=0;

void S_CurveLinearVelocity(void)
{
    /* Velocity gained (or lost) during one full jerk phase = A_max² / (2·J).
     * Used to decide when to start reducing / stop reducing acceleration. */
    double vel_per_jerk_phase = (Nav_Acc_d * Nav_Acc_d) / (2.0 * Nav_Jerk_d);

    switch (Nav_SCurve_Phase_u8)
    {
        /* ------------------------------------------------------------------ */
        /* Phase I — Jerk positive: acceleration ramps from 0 up to A_max     */
        /* ------------------------------------------------------------------ */
        case 1:
        {
            Nav_SCurve_CurrentAccel_d += Nav_Jerk_d;

            if (Nav_SCurve_CurrentAccel_d >= Nav_Acc_d)
            {
                Nav_SCurve_CurrentAccel_d = Nav_Acc_d;

                double vel_remaining = Nav_MaxVelocity_d - Nav_TargetLinearVelocity_d;

                if (vel_remaining <= vel_per_jerk_phase + Nav_Acc_d)
                {
                    Nav_SCurve_Phase_u8 = 3;
                }
                else
                {
                    Nav_SCurve_Phase_u8 = 2;
                }
            }

            else if (Nav_TargetLinearVelocity_d + Nav_SCurve_CurrentAccel_d
                     >= Nav_MaxVelocity_d / 2.0)
            {
                Nav_SCurve_Phase_u8 = 3;
            }

            Nav_TargetLinearVelocity_d += Nav_SCurve_CurrentAccel_d;
            break;
        }

        /* ------------------------------------------------------------------ */
        /* Phase II — Constant acceleration at A_max                          */
        /* ------------------------------------------------------------------ */
        case 2:
        {
            double vel_remaining = Nav_MaxVelocity_d - Nav_TargetLinearVelocity_d;

            if (vel_remaining <= vel_per_jerk_phase + Nav_Acc_d)
            {
                Nav_SCurve_Phase_u8 = 3;
            }

            Nav_TargetLinearVelocity_d += Nav_Acc_d;
            break;
        }

        /* ------------------------------------------------------------------ */
        /* Phase III — Jerk negative: acceleration ramps from A_max down to 0 */
        /* ------------------------------------------------------------------ */
        case 3:
        {
            Nav_SCurve_CurrentAccel_d -= Nav_Jerk_d;

            if (Nav_SCurve_CurrentAccel_d <= 0.0)
            {
                Nav_SCurve_CurrentAccel_d = 0.0;
                Nav_TargetLinearVelocity_d = Nav_MaxVelocity_d;
                Nav_SCurve_Phase_u8 = 4;
                break;
            }

            Nav_TargetLinearVelocity_d += Nav_SCurve_CurrentAccel_d;
            break;
        }

        /* ------------------------------------------------------------------ */
        /* Phase IV — Constant velocity: cruise at Vmax                       */
        /* Transition to deceleration when remaining distance equals the full  */
        /* S-curve decel distance:                                             */
        /*   D_decel = Vmax²/(2·A_max)  +  Vmax·A_max/(2·J)                  */
        /*             └─ trapeze term ─┘  └─ S-curve correction ─┘           */
        /* ------------------------------------------------------------------ */
        case 4:
        {
            Nav_TargetLinearVelocity_d = Nav_MaxVelocity_d;

            double dist_decel =
                  (Nav_MaxVelocity_d * Nav_MaxVelocity_d) / (2.0 * Nav_Acc_d)
                + (Nav_MaxVelocity_d * Nav_Acc_d)          / (2.0 * Nav_Jerk_d);

            if (Nav_RemainingDistance_mm_d <= dist_decel + 2.0)
            {
                Nav_SCurve_CurrentAccel_d = 0.0;
                Nav_SCurve_Phase_u8 = 5;
            }
            break;
        }

        /* ------------------------------------------------------------------ */
        /* Phase V — Jerk negative: deceleration ramps from 0 to –A_max       */
        /* (Mirror of Phase I)                                                 */
        /* ------------------------------------------------------------------ */
        case 5:
        {
            Nav_SCurve_CurrentAccel_d -= Nav_Jerk_d;

            if (Nav_SCurve_CurrentAccel_d <= -Nav_Acc_d)
            {
                Nav_SCurve_CurrentAccel_d = -Nav_Acc_d;

                double vel_remaining = Nav_TargetLinearVelocity_d
                                     + Nav_SCurve_CurrentAccel_d;
                if (vel_remaining <= vel_per_jerk_phase)
                {
                    Nav_SCurve_Phase_u8 = 7;
                }
                else
                {
                    Nav_SCurve_Phase_u8 = 6;
                }
            }
            /* Triangle case (mirror of Phase I) */
            else if (Nav_TargetLinearVelocity_d + Nav_SCurve_CurrentAccel_d
                     <= Nav_MaxVelocity_d / 2.0)
            {
                Nav_SCurve_Phase_u8 = 7;
            }

            Nav_TargetLinearVelocity_d += Nav_SCurve_CurrentAccel_d;

            if (Nav_TargetLinearVelocity_d <= 0.0)
            {
                Nav_TargetLinearVelocity_d = 0.0;
                Nav_SCurve_Phase_u8        = 0;
                Nav_TrapezePhase_en        = Nav_Trapeze_Finished_en;
            }
            break;
        }

        /* ------------------------------------------------------------------ */
        /* Phase VI — Constant deceleration at –A_max                         */
        /* ------------------------------------------------------------------ */
        case 6:
        {
            double vel_after_this_step = Nav_TargetLinearVelocity_d + Nav_SCurve_CurrentAccel_d;
            if (vel_after_this_step <= vel_per_jerk_phase)
            {
                Nav_SCurve_Phase_u8 = 7;
            }

            Nav_TargetLinearVelocity_d += Nav_SCurve_CurrentAccel_d; /* = –A_max */

            if (Nav_TargetLinearVelocity_d <= 0.03)
            {
                Nav_TargetLinearVelocity_d = 0.0;
                Nav_SCurve_Phase_u8        = 0;
                Nav_TrapezePhase_en        = Nav_Trapeze_Finished_en;
            }
            break;
        }

        /* ------------------------------------------------------------------ */
        /* Phase VII — Jerk positive: deceleration ramps from –A_max back to 0*/
        /* (Mirror of Phase III)                                               */
        /* ------------------------------------------------------------------ */
        case 7:
        {
            Nav_SCurve_CurrentAccel_d += Nav_Jerk_d;

            if (Nav_SCurve_CurrentAccel_d >= 0.0)
            {
                Nav_SCurve_CurrentAccel_d  = 0.0;
                Nav_TargetLinearVelocity_d = 0.0;
                Nav_SCurve_Phase_u8        = 0;
                Nav_TrapezePhase_en        = Nav_Trapeze_Finished_en;
                break;
            }

            Nav_TargetLinearVelocity_d += Nav_SCurve_CurrentAccel_d;

          /*  if (Nav_TargetLinearVelocity_d <= 0.03)
            {
                Nav_TargetLinearVelocity_d = 0.0;
                Nav_SCurve_Phase_u8        = 0;
                Nav_TrapezePhase_en        = Nav_Trapeze_Finished_en;
            }*/
            break;
        }

        default:
            break;
    }
}

void Nav_vStateMachine_Routine(void)
{
	if( 1 == CAN_messageReceivedFlag && 1 == CAN_stopSignalFlag ){
		Nav_NavigatorCurrentState_en = MASTER_NavigatorOrderSuddenStop_en;
		CAN_stopSignalFlag = 0;

	}

	if( 1 == CAN_messageReceivedFlag && 1 == CAN_resetSignalFlag ){

		CAN_resetSignalFlag = 0;
		SCB->AIRCR = 0x05FA0004;

	}

	switch ( Nav_NavigatorCurrentState_en )
	{
	case MASTER_NavigatorIdle_en:
	{
		if( ( 1 == CAN_messageReceivedFlag ) && ( 1 == CAN_master_acknowledgeFlag ) )
		{
			Nav_NavigatorCurrentState_en = MASTER_NavigatorInit_en;

			CAN_messageReceivedFlag = 0;
			CAN_master_acknowledgeFlag = 0;
		}
	}break;

	case MASTER_NavigatorInit_en:
	{

		if( ( 1 == CAN_messageReceivedFlag ) && ( 0 == CAN_master_acknowledgeFlag ) )
		{
			Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;

			Nav_vNavigatorPositionInit(
					&Nav_CurrentX_mm_d,
					&Nav_CurrentY_mm_d,
					&Nav_CurrentAngle_deg_d,
					&Nav_CurrentAngle_rad_d,
					&Nav_CurrentTargetAngle_deg_d,
					&Nav_PrevTargetAngle_deg_d);

			CAN_messageReceivedFlag = 0;
		}
	}break;

	case MASTER_NavigatorReady_en:
	{

		if( ( 1 == CAN_messageReceivedFlag )  && ( 0 ==  CAN_master_acknowledgeFlag ) )
		{
			Nav_NavigatorCurrentState_en = MASTER_NavigatorBusy_en;

			CAN_receiveNewTarget(
					&Nav_TargetX_mm_d,
					&Nav_TargetY_mm_d,
					&Nav_TargetArrivingAngle_deg_d,
					&ROBOT_Direction,
					&Nav_vitessemax,
					&Nav_MaxAngularVitesse,
					&Nav_Accel,
					&Nav_AngularAccel,
					&Nav_withPlatforms);

			CAN_messageReceivedFlag = 0;
		}

	}break;


	case MASTER_NavigatorBusy_en:
	{
		 Nav_vDetectBlockage(); // Needs to be before navigation simulation!!!!!!!
		Nav_navigationSimulation(&Nav_TargetX_mm_d, &Nav_TargetY_mm_d, &Nav_TargetArrivingAngle_deg_d, &ROBOT_Direction,&Nav_withPlatforms);

		// in case of s
		//Nav_navigationSimulationTest(&Nav_CurrentX_mm_d, &Nav_CurrentY_mm_d, &Nav_CurrentAngle_deg_d);
		/*
		if ( ( (int)Nav_CurrentX_mm_d == (int)Nav_TargetX_mm_d && (int)Nav_CurrentY_mm_d == (int)Nav_TargetY_mm_d ) || ( (int)Nav_CurrentX_mm_d+1 == (int)Nav_TargetX_mm_d && (int)Nav_CurrentY_mm_d+1 == (int)Nav_TargetY_mm_d ) )
			Nav_NavigatorCurrentState_en = MASTER_NavigatorReachedDest_en;
		 */

		/*
		 if ( Nav_GoToXY_State_en == Nav_GoToXY_BlockageDetected_en ){
			Nav_NavigatorCurrentState_en = MASTER_NavigatorBlockageDetected_en;
		}
		 */

		if( Nav_GoToXY_State_en == Nav_GoToXY_Idle_en  )
		{
			Nav_NavigatorCurrentState_en = MASTER_NavigatorReachedDest_en;
		}

	}break;

	case MASTER_NavigatorReachedDest_en:
	{

		Nav_NavigatorCurrentState_en = Nav_NvigatorWaitToReceiveAcknowledge_en;

	}break;

	case Nav_NvigatorWaitToReceiveAcknowledge_en:
	{
		if( ( 1 == CAN_messageReceivedFlag ) && ( 1 == CAN_master_acknowledgeFlag ) )

		{
			Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
			CAN_messageReceivedFlag = 0;
			CAN_master_acknowledgeFlag = 0;
		}

	}break;

	case MASTER_NavigatorOrderSuddenStop_en :
	{
		Nav_NavigatorCurrentState_en = MASTER_NavigatorSuddenStop_en;

		if ( ( Nav_GoToXY_Rotate_en == Nav_GoToXY_State_en )
				|| (Nav_GoToXY_Forward_en == Nav_GoToXY_State_en )
				|| (Nav_GoToXY_RotateAfter_en == Nav_GoToXY_State_en )  )
		{
			Nav_GoToXY_State_en = Nav_GoToXY_OrderSuddenStop_en;
		}

	}break;
	case MASTER_NavigatorSuddenStop_en :
	{


		//Nav_NavigatorCurrentState_en =  MASTER_NavigatorConfirmedStop_en ; // Call this only in case of testing otherwise comment it

		if ( Nav_GoToXY_State_en == Nav_GoToXY_Idle_en )
		{

			Nav_NavigatorCurrentState_en =  MASTER_NavigatorConfirmedStop_en ;
			Nav_GoToXY_State_en = Nav_GoToXY_Idle_en ;

		}
		else {
			Nav_navigationSimulation(&Nav_TargetX_mm_d, &Nav_TargetY_mm_d, &Nav_TargetArrivingAngle_deg_d, &ROBOT_Direction,&Nav_withPlatforms );
		}

	}break;


	case MASTER_NavigatorConfirmedStop_en:
	{
		if( ( 1 == CAN_messageReceivedFlag ) && ( 1 == CAN_master_acknowledgeFlag ) )
			Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
	}break;

	case MASTER_NavigatorBlockageDetected_en:
	{
		if( ( 1 == CAN_messageReceivedFlag ) && ( 1 == CAN_master_acknowledgeFlag ) ){
			Nav_navigationSimulation(&Nav_TargetX_mm_d, &Nav_TargetY_mm_d, &Nav_TargetArrivingAngle_deg_d, &ROBOT_Direction,&Nav_withPlatforms);
			Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
		}

	}break;

	case MASTER_NavigatorWallBlockageDetected_en:
	{
		Nav_navigationSimulation(&Nav_TargetX_mm_d, &Nav_TargetY_mm_d, &Nav_TargetArrivingAngle_deg_d, &ROBOT_Direction,&Nav_withPlatforms);
		if( ( 1 == CAN_messageReceivedFlag ) && ( 1 == CAN_master_acknowledgeFlag ) )
			Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
	}break;

	}

}

void Nav_vNavigatorStateMachineInit(void){
	TIM5->CNT=TIM5->ARR/2;
	TIM2->CNT=TIM2->ARR/2;

	Nav_NavigatorCurrentState_en = MASTER_NavigatorIdle_en;
	Nav_ConvertRight_Ticks2mm_d = ( M_PI * WHEEL_DIAMETER_MM ) / ENCODER_RESOLUTION  ;
	Nav_ConvertLeft_Ticks2mm_d  = (  M_PI * WHEEL_DIAMETER_MM * LEFT_WHEEL_GAIN ) / ENCODER_RESOLUTION  ;

	CAN_messageReceivedFlag = 0;
	CAN_stopSignalFlag = 0;
	CAN_master_acknowledgeFlag = 0;

	Nav_CurrentX_mm_d = 0.0 ;
	Nav_CurrentY_mm_d = 0.0 ;
	Nav_CurrentAngle_rad_d	=  0;
	Nav_CurrentAngle_deg_d = 0 ;
	Nav_CurrentTargetAngle_deg_d = 0 ;
	Nav_PrevTargetAngle_deg_d = 0 ;
}

void Nav_vNavigatorPositionInit(
		double* Nav_CurrentX_mm_d,
		double* Nav_CurrentY_mm_d,
		double* Nav_CurrentAngle_deg_d,
		double* Nav_CurrentAngle_rad_d,
		double* Nav_CurrentTargetAngle_deg_d,
		double* Nav_PrevTargetAngle_deg_d){

	CAN_receiveInitPosition(
			Nav_CurrentX_mm_d,
			Nav_CurrentY_mm_d,
			Nav_CurrentAngle_deg_d);
	// need to be fixed
	(*Nav_CurrentAngle_rad_d) = ( 3.1415 / 180.0 ) * (*Nav_CurrentAngle_deg_d);
	(*Nav_CurrentTargetAngle_deg_d) = (*Nav_CurrentAngle_deg_d) ;
	(*Nav_PrevTargetAngle_deg_d) = (*Nav_CurrentAngle_deg_d) ;

}

void Nav_navigationSimulation( double* Nav_TargetX_mm_d, double* Nav_TargetY_mm_d, double* Nav_TargetArrivingAngle_deg_d, uint8_t* ROBOT_Direction,uint8_t* Nav_withPlatforms)

{
	switch( Nav_GoToXY_State_en )
	{
	case Nav_GoToXY_Idle_en :
	{
		if ( MASTER_NavigatorBusy_en == Nav_NavigatorCurrentState_en )
		{
			if(*Nav_withPlatforms == ROBOT_With_Platforms){
				MINIMUM_COMMANDS_WITH_PLATFORMS
			}
			else{
				MINIMUM_COMMANDS_WITHOUT_PLATFORMS
			}
			if((*Nav_TargetX_mm_d==3200 )&&(*Nav_TargetY_mm_d==2200))
			{
				Nav_GoToXY_State_en = Nav_GoToXY_RotateAfter_en;
			}

			else{
				Nav_GoToXY_State_en = Nav_GoToXY_Rotate_en;}
		}
	}break;

	case Nav_GoToXY_Rotate_en :
	{
		if ( Nav_TrajectoryState_en == Nav_Trajectory_Idle_en )
		{

			if ( *ROBOT_Direction == ROBOT_Going_Forward )
			{
				Nav_TargetAngle_deg_d = ( atan2( (*Nav_TargetY_mm_d  - Nav_CurrentY_mm_d) ,(*Nav_TargetX_mm_d - Nav_CurrentX_mm_d) ) * 180.0 ) / M_PI;
				Nav_RemainingAngle_deg_d =  Nav_TargetAngle_deg_d  - Nav_CurrentTargetAngle_deg_d ;
				Nav_vSaturateRemainingAngle();
			}
			else if ( *ROBOT_Direction == ROBOT_Going_Backward )
			{
				Nav_TargetAngle_deg_d = ( atan2( (Nav_CurrentY_mm_d - *Nav_TargetY_mm_d ) ,(Nav_CurrentX_mm_d - *Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				Nav_RemainingAngle_deg_d =  Nav_TargetAngle_deg_d  - Nav_CurrentTargetAngle_deg_d ;
				Nav_vSaturateRemainingAngle();

			}

			if( Nav_RemainingAngle_deg_d  > 0.0 )
			{
				Nav_MaxAngularVelocity_d= Nav_MaxAngularVitesse;


				Nav_AngularAcc_d = Nav_AngularAccel ;
				Nav_TrajectoryMode_en = Nav_ForwardAngularTrajectory_en;
			}
			else
			{
				Nav_MaxAngularVelocity_d = -Nav_MaxAngularVitesse;
				Nav_AngularAcc_d = -Nav_AngularAccel;
				Nav_TrajectoryMode_en = Nav_ReverseAngularTrajectory_en;
			}

			Nav_TrajectoryState_en = Nav_Trajectory_ResetVariables_en;
		}
		else if ( Nav_TrajectoryState_en == Nav_Trajectory_Finish_en)
		{
			Nav_GoToXY_State_en = Nav_GoToXY_Forward_en;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;
		}
		else
		{
			Nav_vIndependantTrajectoryStateMachine();
		}
	}break;

	case Nav_GoToXY_Forward_en :
	{
		if ( Nav_TrajectoryState_en == Nav_Trajectory_Idle_en )
		{
			if (*ROBOT_Direction == ROBOT_Going_Forward)
			{
				Nav_TrajectoryMode_en = Nav_ForwardLinearTrajectory_en;
				Nav_MaxVelocity_d = Nav_vitessemax ; //400 ; //300 ;//700
				Nav_Acc_d = Nav_Accel ;//1500
				//Nav_TargetDistance_mm_d = sqrt ( pow( *Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( *Nav_TargetY_mm_d  -Nav_CurrentY_mm_d , 2 ) ) ;
				Nav_TrajectoryState_en = Nav_Trajectory_ResetVariables_en;
			}
			else if ( *ROBOT_Direction == ROBOT_Going_Backward)
			{
				Nav_TrajectoryMode_en = Nav_ReverseLinearTrajectory_en;
				Nav_MaxVelocity_d = - Nav_vitessemax ; //400 ; //300 ;//700
				Nav_Acc_d = - Nav_Accel ;//1500
				//Nav_TargetDistance_mm_d = sqrt ( pow( *Nav_TargetX_mm_d  - Nav_CurrentX_mm_d ,2 ) + pow( *Nav_TargetY_mm_d  -Nav_CurrentY_mm_d , 2 ) ) ;
				Nav_TrajectoryState_en = Nav_Trajectory_ResetVariables_en;

			}
		}
		else if ((Nav_TrajectoryState_en == Nav_Trajectory_Finish_en  ) && ( *Nav_TargetArrivingAngle_deg_d != Nav_No_Rotate_After))
		{
			Nav_GoToXY_State_en = Nav_GoToXY_RotateAfter_en;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;
		}
		else if ((Nav_TrajectoryState_en == Nav_Trajectory_Finish_en ) && ( *Nav_TargetArrivingAngle_deg_d == Nav_No_Rotate_After))
		{
			Nav_GoToXY_State_en = Nav_GoToXY_Finished_en ;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;


		}
		else
		{
			Nav_vIndependantTrajectoryStateMachine();
		}
	}break;

	case Nav_GoToXY_RotateAfter_en :
	{

		if ( Nav_TrajectoryState_en == Nav_Trajectory_Idle_en )
		{
			Nav_TargetAngle_deg_d = *Nav_TargetArrivingAngle_deg_d;
			Nav_RemainingAngle_deg_d =  Nav_TargetAngle_deg_d  - Nav_CurrentAngle_deg_d ;
			Nav_vSaturateRemainingAngle();
			if( Nav_RemainingAngle_deg_d > 0.0 )
			{
				Nav_MaxAngularVelocity_d = Nav_MaxAngularVitesse;
				Nav_AngularAcc_d = Nav_AngularAccel ;
				Nav_TrajectoryMode_en = Nav_ForwardAngularTrajectory_en;
			}
			else
			{
				Nav_MaxAngularVelocity_d = - Nav_MaxAngularVitesse; ;
				Nav_AngularAcc_d = - Nav_AngularAccel  ;
				Nav_TrajectoryMode_en = Nav_ReverseAngularTrajectory_en;
			}

			Nav_TrajectoryState_en = Nav_Trajectory_ResetVariables_en;
		}
		else if ( Nav_TrajectoryState_en == Nav_Trajectory_Finish_en)
		{
			Nav_GoToXY_State_en = Nav_GoToXY_Finished_en;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;
		}
		else
		{
			Nav_vIndependantTrajectoryStateMachine();
		}
	}break;
	case Nav_GoToXY_BlockageDetected_en :
	{
		Nav_TrapezePhase_en = Nav_Trapeze_Idle_en ;
		Nav_TargetLinearVelocity_d = 0 ;
		Nav_TargetAngularVelocity_d = 0 ;
		Nav_TrajectoryState_en = Nav_Trajectory_Finish_en ;
		Nav_CurrentTargetDistance_mm_d =  Nav_MeasuredDistance_mm_d ;
		Nav_CurrentTargetAngle_deg_d = Nav_CurrentAngle_deg_d ;
		Nav_GoToXY_State_en = Nav_GoToXY_Finished_en;

	}break;
	case Nav_GoToXY_OrderSuddenStop_en :
	{
		Nav_GoToXY_State_en = Nav_GoToXY_ExecuteSuddenStop_en;

		if ( 	( Nav_Trajectory_ResetVariables_en == Nav_TrajectoryState_en )
				|| ( Nav_Trajectory_SetPath_en == Nav_TrajectoryState_en )
				|| ( Nav_Trajectory_WaitToExecute_en == Nav_TrajectoryState_en)
				|| ( Nav_Trajectory_Execute_en == Nav_TrajectoryState_en) )
		{
			Nav_TrajectoryState_en =  Nav_Trajectory_OrderSuddenStop_en ;
		}


		if(Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en)
		{
			Nav_Acc_d = 900 ;
		}
		else if(Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en)
		{
			Nav_Acc_d = - 900;
		}
		else if(Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en)
		{
			Nav_AngularAcc_d = 200;
		}
		else if(Nav_TrajectoryMode_en == Nav_ReverseAngularTrajectory_en)
		{
			Nav_AngularAcc_d = -200;
		}
	}break;

	case Nav_GoToXY_ExecuteSuddenStop_en :
	{
		if ( Nav_TrajectoryState_en == Nav_Trajectory_Finish_en) // Is it necessary to 	do this checking ?
		{
			Nav_GoToXY_State_en = Nav_GoToXY_Finished_en;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;
		}
		else
		{
			Nav_vIndependantTrajectoryStateMachine();
		}

	}break;

	case Nav_GoToXY_Finished_en :
	{

		Nav_GoToXY_State_en = Nav_GoToXY_Idle_en ;
	}break;
	}
}
void Nav_TrapezeLinearVelocity2()
{
	switch( Nav_TrapezePhase_en )
	{
	case Nav_Trapeze_Idle_en:
	{

	}break;
	case Nav_Trapeze_Accelerating_en:
	{
		Nav_ReferenceDistance_d = (Nav_TargetLinearVelocity_d * Nav_TargetLinearVelocity_d) / ( 2 * Nav_Acc_d ) ;

			if( Nav_RemainingDistance_mm_d > ( Nav_ReferenceDistance_d  ) )
			{
				if ( Nav_TargetLinearVelocity_d < Nav_MaxVelocity_d )
				{
					Nav_TargetLinearVelocity_d = Nav_Acc_d * Nav_CurrentSample_u32 ;
				}
				else
				{
					Nav_TrapezePhase_en = Nav_Trapeze_ConstantVelocity_en;
				}
			}
			else
			{
				Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
				Nav_ReferenceLinearVelocity_d = Nav_TargetLinearVelocity_d;
				Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
			}

	}break;

	case Nav_Trapeze_ConstantVelocity_en:
	{
		Nav_ReferenceDistance_d = (Nav_TargetLinearVelocity_d * Nav_TargetLinearVelocity_d) / ( 2 * Nav_Acc_d ) ;
		if( Nav_RemainingDistance_mm_d > ( Nav_ReferenceDistance_d ) )
		{
			Nav_TargetLinearVelocity_d = Nav_MaxVelocity_d ;
		}
		else
		{
			Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
			Nav_ReferenceLinearVelocity_d = Nav_TargetLinearVelocity_d;
			Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
		}
	}break;

	case Nav_Trapeze_Decelerating_en:
	{
		Nav_ReferenceDistance_d = (Nav_TargetLinearVelocity_d * Nav_TargetLinearVelocity_d) / ( 2 * Nav_Acc_d ) ;


			Nav_TargetLinearVelocity_d = Nav_ReferenceLinearVelocity_d - ( Nav_Acc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;

		    if( Nav_CurrentTargetDistance_mm_d + Nav_TargetLinearVelocity_d >= Nav_ProfileTargetDistance_mm_d )
		    {
		        Nav_TargetLinearVelocity_d = Nav_ProfileTargetDistance_mm_d - Nav_CurrentTargetDistance_mm_d;
		        Nav_TrapezePhase_en = Nav_Trapeze_Finished_en;
		    }
		if( ( Nav_RemainingDistance_mm_d <= 0.0) || ( Nav_TargetLinearVelocity_d <= 0.03 ) )
		{
			Nav_TargetLinearVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}

	}break;
	case Nav_Trapeze_OrderUrgentDecelerating_en:
	{
		Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
		Nav_ReferenceLinearVelocity_d = Nav_TargetLinearVelocity_d;
		Nav_TrapezePhase_en = Nav_Trapeze_UrgentDecelerating_en;
	}break;
	case Nav_Trapeze_UrgentDecelerating_en:
	{
		Nav_TargetLinearVelocity_d = Nav_ReferenceLinearVelocity_d - ( Nav_Acc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;
		if( Nav_TargetLinearVelocity_d  <= 0.02 )
		{
			Nav_TargetLinearVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}
	}break;


	case Nav_Trapeze_Finished_en:
	{
		Nav_TargetLinearVelocity_d = 0.0 ;
		Nav_TrapezePhase_en = Nav_Trapeze_Idle_en ;
	}break;

	}
}

void Nav_TrapezeReverseLinearVelocity2()
{
	switch( Nav_TrapezePhase_en )
	{
	case Nav_Trapeze_Idle_en:
	{

	}break;
	case Nav_Trapeze_Accelerating_en:
	{

		Nav_ReferenceDistance_d = (Nav_TargetLinearVelocity_d * Nav_TargetLinearVelocity_d) / ( 2 * Nav_Acc_d ) ;

			if( Nav_RemainingDistance_mm_d <  Nav_ReferenceDistance_d  )
			{
				if ( Nav_TargetLinearVelocity_d > Nav_MaxVelocity_d )
				{
					Nav_TargetLinearVelocity_d = Nav_Acc_d * Nav_CurrentSample_u32 ;
				}
				else
				{
					Nav_TrapezePhase_en = Nav_Trapeze_ConstantVelocity_en;
				}
			}
			else
			{
				Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
				Nav_ReferenceLinearVelocity_d = Nav_TargetLinearVelocity_d;
				Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
			}



	}break;

	case Nav_Trapeze_ConstantVelocity_en:
	{
		Nav_ReferenceDistance_d = (Nav_TargetLinearVelocity_d * Nav_TargetLinearVelocity_d) / ( 2 * Nav_Acc_d ) ;
		if( Nav_RemainingDistance_mm_d < ( Nav_ReferenceDistance_d) )
		{
			Nav_TargetLinearVelocity_d = Nav_MaxVelocity_d ;
		}
		else
		{
			Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
			Nav_ReferenceLinearVelocity_d = Nav_TargetLinearVelocity_d;
			Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
		}
	}break;

	case Nav_Trapeze_Decelerating_en:
	{
		Nav_ReferenceDistance_d = (Nav_TargetLinearVelocity_d * Nav_TargetLinearVelocity_d) / ( 2 * Nav_Acc_d ) ;

			Nav_TargetLinearVelocity_d = Nav_ReferenceLinearVelocity_d - ( Nav_Acc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;

	    if( Nav_CurrentTargetDistance_mm_d + Nav_TargetLinearVelocity_d <= Nav_ProfileTargetDistance_mm_d )
	    {
	        Nav_TargetLinearVelocity_d = Nav_ProfileTargetDistance_mm_d - Nav_CurrentTargetDistance_mm_d;
	        Nav_TrapezePhase_en = Nav_Trapeze_Finished_en;
	    }
		if( ( Nav_RemainingDistance_mm_d >= 0.0 ) || ( Nav_TargetLinearVelocity_d  >= (-0.01) ) )
		{
			Nav_TargetLinearVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}

	}break;
	case Nav_Trapeze_OrderUrgentDecelerating_en:
	{
		Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
		Nav_ReferenceLinearVelocity_d = Nav_TargetLinearVelocity_d;
		Nav_TrapezePhase_en = Nav_Trapeze_UrgentDecelerating_en;
	}break;
	case Nav_Trapeze_UrgentDecelerating_en:
	{
		Nav_TargetLinearVelocity_d = Nav_ReferenceLinearVelocity_d - ( Nav_Acc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;
		if(  Nav_TargetLinearVelocity_d  >= ( -0.01) )
		{
			Nav_TargetLinearVelocity_d = 0.0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}
	}break;


	case Nav_Trapeze_Finished_en:
	{
		Nav_TargetLinearVelocity_d = 0.0 ;
		Nav_TrapezePhase_en = Nav_Trapeze_Idle_en ;
	}break;

	}
}


void Nav_TrapezeAngularVelocity2()
{
	switch( Nav_TrapezePhase_en )
	{

	case Nav_Trapeze_Idle_en:
	{

	}break;
	case Nav_Trapeze_Accelerating_en:
	{
		Nav_ReferenceAngle_deg_d = ( Nav_TargetAngularVelocity_d * Nav_TargetAngularVelocity_d) / ( 2 * Nav_AngularAcc_d ) ;

		if( Nav_RemainingAngle_deg_d < 2.0 )
		{
			if( Nav_RemainingAngle_deg_d > Nav_ReferenceAngle_deg_d )
			{
				if ( Nav_TargetAngularVelocity_d < Nav_MaxAngularVelocity_d  )
				{
					Nav_TargetAngularVelocity_d = Nav_AngularAcc_d * Nav_CurrentSample_u32 ;
				}
				else
				{
					Nav_TrapezePhase_en = Nav_Trapeze_ConstantVelocity_en;
				}
			}
			else
			{
				Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
				Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
				Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
			}
		}

		else
		{
			if( Nav_RemainingAngle_deg_d > ( Nav_ReferenceAngle_deg_d + 2.0 ) )
			{
				if ( Nav_TargetAngularVelocity_d < Nav_MaxAngularVelocity_d  )
				{
					Nav_TargetAngularVelocity_d = Nav_AngularAcc_d * Nav_CurrentSample_u32 ;
				}
				else
				{
					Nav_TrapezePhase_en = Nav_Trapeze_ConstantVelocity_en;
				}
			}
			else
			{
				Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
				Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
				Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
			}
		}


	}break;

	case Nav_Trapeze_ConstantVelocity_en:
	{
		Nav_ReferenceAngle_deg_d = ( Nav_TargetAngularVelocity_d * Nav_TargetAngularVelocity_d) / ( 2 * Nav_AngularAcc_d ) ;
		if( Nav_RemainingAngle_deg_d > ( Nav_ReferenceAngle_deg_d + 2.0 ) )
		{
			Nav_TargetAngularVelocity_d = Nav_MaxAngularVelocity_d ;
		}
		else
		{
			Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
			Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
			Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
		}
	}break;

	case Nav_Trapeze_Decelerating_en:
	{
		Nav_ReferenceAngle_deg_d = ( Nav_TargetAngularVelocity_d * Nav_TargetAngularVelocity_d) / ( 2 * Nav_AngularAcc_d ) ;
		if( Nav_RemainingAngle_deg_d > Nav_ReferenceAngle_deg_d )
		{
			Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
			Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
		}
		else
		{
			Nav_TargetAngularVelocity_d = Nav_ReferenceAngularVelocity_d - ( Nav_AngularAcc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;
		}

		if( ( Nav_RemainingAngle_deg_d <= 0 ) || (Nav_TargetAngularVelocity_d <= 0.01) )
		{
			Nav_TargetAngularVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}
	}break;
	case Nav_Trapeze_OrderUrgentDecelerating_en:
	{
		Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
		Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
		Nav_TrapezePhase_en = Nav_Trapeze_UrgentDecelerating_en;
	}break;
	case Nav_Trapeze_UrgentDecelerating_en :
	{
		Nav_TargetAngularVelocity_d = Nav_ReferenceAngularVelocity_d - ( Nav_AngularAcc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;

		if( ( Nav_RemainingAngle_deg_d <= 0.0) || ( Nav_TargetAngularVelocity_d <= 0.002) )
		{
			Nav_TargetAngularVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}
	}break ;
	case Nav_Trapeze_Finished_en:
	{
		Nav_TargetAngularVelocity_d = 0.0 ;
		Nav_TrapezePhase_en = Nav_Trapeze_Idle_en ;
	}break;

	}
}

void Nav_TrapezeReverseAngularVelocity2()
{
	switch( Nav_TrapezePhase_en )
	{

	case Nav_Trapeze_Idle_en:
	{

	}break;
	case Nav_Trapeze_Accelerating_en:
	{
		Nav_ReferenceAngle_deg_d = ( Nav_TargetAngularVelocity_d * Nav_TargetAngularVelocity_d) / ( 2 * Nav_AngularAcc_d ) ;

		if( Nav_RemainingAngle_deg_d > (-2.0) )
		{
			if( Nav_RemainingAngle_deg_d < Nav_ReferenceAngle_deg_d )
			{
				if ( Nav_TargetAngularVelocity_d > Nav_MaxAngularVelocity_d  )
				{
					Nav_TargetAngularVelocity_d = Nav_AngularAcc_d * Nav_CurrentSample_u32 ;
				}
				else
				{
					Nav_TrapezePhase_en = Nav_Trapeze_ConstantVelocity_en;
				}
			}
			else
			{
				Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
				Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
				Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
			}
		}
		else
		{
			if( Nav_RemainingAngle_deg_d < ( Nav_ReferenceAngle_deg_d - 2.0 ) )
			{
				if ( Nav_TargetAngularVelocity_d > Nav_MaxAngularVelocity_d  )
				{
					Nav_TargetAngularVelocity_d = Nav_AngularAcc_d * Nav_CurrentSample_u32 ;
				}
				else
				{
					Nav_TrapezePhase_en = Nav_Trapeze_ConstantVelocity_en;
				}
			}
			else
			{
				Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
				Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
				Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
			}
		}


	}break;

	case Nav_Trapeze_ConstantVelocity_en:
	{
		Nav_ReferenceAngle_deg_d = ( Nav_TargetAngularVelocity_d * Nav_TargetAngularVelocity_d) / ( 2 * Nav_AngularAcc_d ) ;
		if( Nav_RemainingAngle_deg_d < ( Nav_ReferenceAngle_deg_d /*- 2.0*/ ))
		{
			Nav_TargetAngularVelocity_d = Nav_MaxAngularVelocity_d ;
		}
		else
		{
			Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
			Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
			Nav_TrapezePhase_en = Nav_Trapeze_Decelerating_en;
		}
	}break;

	case Nav_Trapeze_Decelerating_en:
	{
		Nav_ReferenceAngle_deg_d = ( Nav_TargetAngularVelocity_d * Nav_TargetAngularVelocity_d) / ( 2 * Nav_AngularAcc_d ) ;
		if( Nav_RemainingAngle_deg_d < Nav_ReferenceAngle_deg_d )
		{
			Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
			Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
		}
		else
		{
			Nav_TargetAngularVelocity_d = Nav_ReferenceAngularVelocity_d - ( Nav_AngularAcc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;
		}

		if( ( Nav_RemainingAngle_deg_d >= 0.0 ) || (Nav_TargetAngularVelocity_d >= (-0.01) ) )
		{
			Nav_TargetAngularVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}
	}break;
	case Nav_Trapeze_OrderUrgentDecelerating_en:
	{
		Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
		Nav_ReferenceAngularVelocity_d = Nav_TargetAngularVelocity_d;
		Nav_TrapezePhase_en = Nav_Trapeze_UrgentDecelerating_en;
	}break;
	case Nav_Trapeze_UrgentDecelerating_en :
	{
		Nav_TargetAngularVelocity_d = Nav_ReferenceAngularVelocity_d - ( Nav_AngularAcc_d * ( Nav_CurrentSample_u32 -Nav_AccelerationSamples_u32 ) )  ;
		if( ( Nav_RemainingAngle_deg_d >= 0.0 ) || (  Nav_TargetAngularVelocity_d ) >= (-0.002) )
		{
			Nav_TargetAngularVelocity_d = 0 ;
			Nav_TrapezePhase_en = Nav_Trapeze_Finished_en ;
		}

	}break;

	case Nav_Trapeze_Finished_en:
	{
		Nav_TargetAngularVelocity_d = 0.0 ;
		Nav_TrapezePhase_en = Nav_Trapeze_Idle_en ;
	}break;

	}

}



void Nav_vTargetDistanceCalculationRoutine()
{
	Nav_CurrentTargetDistance_mm_d = Nav_PrevTargetDistance_mm_d + Nav_TargetLinearVelocity_d ;
	Nav_PrevTargetDistance_mm_d = Nav_CurrentTargetDistance_mm_d ;

}

void Nav_vTargetAngleCalculationRoutine()
{
	Nav_CurrentTargetAngle_deg_d = Nav_PrevTargetAngle_deg_d + Nav_TargetAngularVelocity_d ;
	Nav_PrevTargetAngle_deg_d = Nav_CurrentTargetAngle_deg_d;
}



void Nav_vSaturateRemainingAngle()
{
	if( Nav_RemainingAngle_deg_d > 180 )
	{
		Nav_RemainingAngle_deg_d -= 360;
	}
	else if ( Nav_RemainingAngle_deg_d < -180 )
	{
		Nav_RemainingAngle_deg_d += 360;
	}
	if( (  Nav_RemainingAngle_deg_d > 177 )|| ( Nav_RemainingAngle_deg_d < -177 ) )
	{
		Nav_RemainingAngle_deg_d = 177;
	}
}

void Nav_vCurrentTargetAngleFollower()
{

	if( (Nav_CurrentTargetAngle_deg_d - Nav_CurrentAngle_deg_d) > 340.0  )
	{
		Nav_CurrentAngle_deg_d += 360.0;
		Nav_CurrentAngle_rad_d += M_2PI ;
		Nav_PrevAngle_rad_d += M_2PI ;
	}
	else if( ( Nav_CurrentAngle_deg_d - Nav_CurrentTargetAngle_deg_d) > 340.0 )
	{

		Nav_CurrentAngle_deg_d -=  (double) 360.0;
		Nav_CurrentAngle_rad_d -=((double) M_2PI) ;
		Nav_PrevAngle_rad_d -=  ((double) M_2PI );
	}
}

void Nav_vNavigationRoutine()
{
	Nav_vFeedbackRoutine();
	Nav_vPidDistance();
	Nav_vPidAngle();
	Nav_vCalculateMotorsCommand();
	Nav_vMotorsRoutine();
}


void Nav_vFeedbackRoutine()
{
	//Read ticks from encoder mode timers
	if  ( ENCODER_RIGHT->CNT > 0 )
	{
		Nav_RightTicks_i32 = ( (int32_t) ( ENCODER_RIGHT->CNT - ( ENCODER_RIGHT->ARR / 2 ) ) )   ;
	}

	if( ENCODER_LEFT->CNT > 0 )
	{

		Nav_LeftTicks_i32 =( (int32_t) ( ENCODER_LEFT->CNT - ( ENCODER_LEFT->ARR / 2 ) ) )   ;
	}

	//convert measured distance from ticks to mm for every encoder
	Nav_MeasuredDistanceRight_mm_d = (double) ( Nav_RightTicks_i32 * Nav_ConvertRight_Ticks2mm_d ) ;
	Nav_MeasuredDistanceLeft_mm_d  = (double) ( Nav_LeftTicks_i32  * Nav_ConvertLeft_Ticks2mm_d  ) ;

	//Measure distance of robot center ( (right + left)/2 )
	Nav_MeasuredDistance_mm_d = (double) ( ( Nav_MeasuredDistanceRight_mm_d   +  Nav_MeasuredDistanceLeft_mm_d ) / 2.0  ) ;

	//Measure linear velocity
	Nav_MeasuredVelocity_mm_d = Nav_MeasuredDistance_mm_d - Nav_PrevMeasuredDistance_mm_d ;
	Nav_PrevMeasuredDistance_mm_d = Nav_MeasuredDistance_mm_d;

	//Measure local angle of robot center
	Nav_MeasuredAngle_rad_d =  ( double ) ( ( Nav_MeasuredDistanceRight_mm_d   -  Nav_MeasuredDistanceLeft_mm_d ) / TRACK_MM )   ;

	//Measure angular velocity
	Nav_MeasuredAngularVelocity_rad_d = Nav_MeasuredAngle_rad_d - Nav_PrevMeasuredAngle_rad_d ;
	Nav_PrevMeasuredAngle_rad_d = Nav_MeasuredAngle_rad_d ;

	Nav_MeasuredAngularVelocity_deg_d = (double) ( ( Nav_MeasuredAngularVelocity_rad_d / M_PI ) * 180.0 ) ;

	//Measure global angle of robot center
	Nav_CurrentAngle_rad_d += Nav_MeasuredAngularVelocity_rad_d ;
	//Nav_CurrentAngle_rad_d += 0.5 * (Nav_MeasuredAngularVelocity_rad_d + Nav_PrevAngularVelocity_rad_d);

	Nav_CurrentAngle_deg_d =  (double) ( ( Nav_CurrentAngle_rad_d / M_PI ) * 180.0 ) ;

	Nav_AverageAngle_rad_d = ( ( Nav_CurrentAngle_rad_d + Nav_PrevAngle_rad_d ) / 2 ) ;
	Nav_PrevAngle_rad_d = Nav_CurrentAngle_rad_d;

	if ( Nav_MeasuredAngularVelocity_rad_d ==0 )
	{
		Nav_CurveCoefficient_d = 1;
	}
	else
	{
		Nav_CurveCoefficient_d = ( sin( Nav_MeasuredAngularVelocity_rad_d / 2 ) ) / (Nav_MeasuredAngularVelocity_rad_d / 2 ) ;
	}

	//	Measure X and Y of robot center
	Nav_DeltaX_mm_d = ( Nav_CurveCoefficient_d * Nav_MeasuredVelocity_mm_d )*cos( Nav_AverageAngle_rad_d ) ;
	Nav_DeltaY_mm_d = ( Nav_CurveCoefficient_d * Nav_MeasuredVelocity_mm_d )*sin( Nav_AverageAngle_rad_d ) ;

	Nav_CurrentX_mm_d +=  Nav_DeltaX_mm_d  ;
	Nav_CurrentY_mm_d +=  Nav_DeltaY_mm_d  ;

}


void Nav_vPidDistance()
{
	//Calculate Distance Error
	Nav_DistanceError_d = Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d ;

	//Calculate the sum of distance Error using the Integral Term of the PID
	Nav_SumDistanceError_d = Nav_KiDistance_d * Nav_DistanceError_d + Nav_SumDistanceError_d ;

	//Calculate the Output of the distance PID block
	Nav_PID_DistanceOutput_d = ( double ) ( ( Nav_KpDistance_d *  Nav_DistanceError_d ) - ( Nav_KdDistance_d * Nav_MeasuredVelocity_mm_d ) + Nav_SumDistanceError_d  );
}

void Nav_vPidAngle()
{
	//Calculate Angle Error
	Nav_AngleError_d =  Nav_CurrentTargetAngle_deg_d - Nav_CurrentAngle_deg_d ;

	//Calculate the sum of Angle Error using the Integral Term of the PID
	Nav_SumAngleError_d = Nav_KiAngle_d * Nav_AngleError_d + Nav_SumAngleError_d ;

	//Calculate the Output of the Angle PID block
	Nav_PID_AngleOutput_d = ( double ) ( ( Nav_KpAngle_d *  Nav_AngleError_d ) - ( Nav_KdAngle_d * Nav_MeasuredAngularVelocity_deg_d ) + Nav_SumAngleError_d  ) ;
}


void Nav_vCalculateMotorsCommand()
{
	//Calculate each motor command using the output of the distance PID and Angle PID blocks
	Nav_RightMotorCommand_i32 = ( int32_t ) ( Nav_PID_DistanceOutput_d + Nav_PID_AngleOutput_d )   ;
	Nav_LeftMotorCommand_i32  = ( int32_t ) ( Nav_PID_DistanceOutput_d - Nav_PID_AngleOutput_d )   ;

	// Right Motor Direction Settings
	if( Nav_RightMotorCommand_i32 >= 0.0 )
	{
		Nav_RightMotorDirection_i8 = MOTOR_DIRECTION_FORWARD ;
	}
	else
	{
		Nav_RightMotorDirection_i8 = MOTOR_DIRECTION_REVERSE ;
		Nav_RightMotorCommand_i32 = fabs( Nav_RightMotorCommand_i32 );
	}
	//Left Motor Direction Settings
	if( Nav_LeftMotorCommand_i32 >= 0.0 )
	{
		Nav_LeftMotorDirection_i8 = MOTOR_DIRECTION_FORWARD ;
	}
	else
	{
		Nav_LeftMotorDirection_i8 = MOTOR_DIRECTION_REVERSE ;
		Nav_LeftMotorCommand_i32 = fabs( Nav_LeftMotorCommand_i32 );
	}

	//Right Motor Maximum Command Settings
	if(Nav_RightMotorCommand_i32 > MAXIMUM_MOTOR_COMMAND )
	{
		Nav_RightMotorCommand_i32 = MAXIMUM_MOTOR_COMMAND ;
	}
	//Left Motor Maximum Command Settings
	if(Nav_LeftMotorCommand_i32 > MAXIMUM_MOTOR_COMMAND )
	{
		Nav_LeftMotorCommand_i32 = MAXIMUM_MOTOR_COMMAND ;
	}

	Nav_RightMotorCommand_i32 = ( int32_t ) ( ( (double) ( (MOTOR_PWM->ARR )  *  Nav_RightMotorCommand_i32 )  / MAXIMUM_MOTOR_COMMAND )  ) ;
	Nav_LeftMotorCommand_i32  = ( int32_t ) ( ( (double) ( (MOTOR_PWM->ARR )  *  Nav_LeftMotorCommand_i32 )   / MAXIMUM_MOTOR_COMMAND )  ) ;

	if ( Nav_RightMotorDirection_i8 == MOTOR_DIRECTION_FORWARD )
	{
		if ( ( Nav_RightMotorCommand_i32 > MINIMUM_SATURATION_COMMAND)
				&& ( Nav_RightMotorCommand_i32 < MINIMUM_RIGHT_MOTOR_FORWARD_COMMAND ) )
		{
			Nav_RightMotorCommand_i32 = MINIMUM_RIGHT_MOTOR_FORWARD_COMMAND;
		}
	}
	else
	{
		if ((Nav_RightMotorCommand_i32 > MINIMUM_SATURATION_COMMAND)
				&& (Nav_RightMotorCommand_i32 < MINIMUM_RIGHT_MOTOR_REVERSE_COMMAND))
		{
			Nav_RightMotorCommand_i32 = MINIMUM_RIGHT_MOTOR_REVERSE_COMMAND;
		}
	}


	if (  Nav_LeftMotorDirection_i8 == MOTOR_DIRECTION_FORWARD )
	{
		if(( Nav_LeftMotorCommand_i32 > MINIMUM_SATURATION_COMMAND )
				&& (Nav_LeftMotorCommand_i32 < MINIMUM_LEFT_MOTOR_FORWARD_COMMAND)  )
		{
			Nav_LeftMotorCommand_i32 = MINIMUM_LEFT_MOTOR_FORWARD_COMMAND;
		}
	}
	else
	{
		if( ( Nav_LeftMotorCommand_i32 > MINIMUM_SATURATION_COMMAND )
				&& (Nav_LeftMotorCommand_i32 < MINIMUM_LEFT_MOTOR_REVERSE_COMMAND)  )
		{
			Nav_LeftMotorCommand_i32 = MINIMUM_LEFT_MOTOR_REVERSE_COMMAND;
		}
	}

	//MONITORING
	MONITOR_RightMotorCommand_i32 = Nav_RightMotorDirection_i8 * Nav_RightMotorCommand_i32 ;
	MONITOR_LeftMotorCommand_i32  = Nav_LeftMotorDirection_i8 * Nav_LeftMotorCommand_i32  ;
}


void Nav_vMotorsRoutine()
{

	if (Nav_LeftMotorDirection_i8 == MOTOR_DIRECTION_FORWARD)
	{
		MOTOR_PWM->LEFT_FORWARD = Nav_LeftMotorCommand_i32 ;
		MOTOR_PWM->LEFT_REVERSE = 0 ;
	}
	else if ( Nav_LeftMotorDirection_i8 == MOTOR_DIRECTION_REVERSE )
	{
		MOTOR_PWM->LEFT_REVERSE= Nav_LeftMotorCommand_i32  ;
		MOTOR_PWM->LEFT_FORWARD = 0 ;
	}

	if (Nav_RightMotorDirection_i8 == MOTOR_DIRECTION_FORWARD )
	{
		MOTOR_PWM->RIGHT_FORWARD = Nav_RightMotorCommand_i32 ;
		MOTOR_PWM->RIGHT_REVERSE = 0;
	}
	else if (Nav_RightMotorDirection_i8 == MOTOR_DIRECTION_REVERSE )
	{
		MOTOR_PWM->RIGHT_REVERSE =  Nav_RightMotorCommand_i32  ;
		MOTOR_PWM->RIGHT_FORWARD = 0 ;
	}

}

void Nav_vDetectBlockage()
{
	if ( (Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en)||(Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en) ){
		if(Nav_vitessemax == 650 ){
			if (
					(
							( Nav_LeftMotorCommand_i32 > LINEAR_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
							|| ( Nav_RightMotorCommand_i32 > LINEAR_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
					)
					&&( Nav_MeasuredVelocity_mm_d < BLOCKAGE_LINEAR_VELOCITY_THRESHOLD )
					&&( Nav_MeasuredAngularVelocity_deg_d < BLOCKAGE_ANGULAR_VELOCITY_THRESHOLD )
			)
			{
				Nav_BlockageCounter_u8 ++;
			}
			else
			{
				Nav_BlockageCounter_u8 = 0 ;
			}

			if ( Nav_BlockageCounter_u8 > 100)
			{
				Nav_BlockageCounter_u8 = 0 ;
				Nav_GoToXY_State_en = Nav_GoToXY_BlockageDetected_en ;
				Nav_NavigatorCurrentState_en = MASTER_NavigatorBlockageDetected_en;
			}
		}

		else {
			if (
					(
							( Nav_LeftMotorCommand_i32 > LINEAR_SLOW_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
							|| ( Nav_RightMotorCommand_i32 > LINEAR_SLOW_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
					)
					&&( Nav_MeasuredVelocity_mm_d < SLOW_BLOCKAGE_LINEAR_VELOCITY_THRESHOLD )
					&&( Nav_MeasuredAngularVelocity_deg_d < SLOW_BLOCKAGE_ANGULAR_VELOCITY_THRESHOLD )
			)
			{
				Nav_BlockageCounter_u8 ++;
			}
			else
			{
				Nav_BlockageCounter_u8 = 0 ;
			}

			if ( Nav_BlockageCounter_u8 > SLOW_BLOCKAGE_DURATION_THRESHOLD )
			{
				Nav_BlockageCounter_u8 = 0 ;
				Nav_GoToXY_State_en = Nav_GoToXY_BlockageDetected_en ;
				Nav_NavigatorCurrentState_en = MASTER_NavigatorWallBlockageDetected_en;
			}
		}

	}
	else{
		if(Nav_MaxAngularVitesse == 180 ){
			if (
					(
							( Nav_LeftMotorCommand_i32 > ANGULAR_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
							|| ( Nav_RightMotorCommand_i32 > ANGULAR_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
					)
					&&( Nav_MeasuredVelocity_mm_d < BLOCKAGE_LINEAR_VELOCITY_THRESHOLD )
					&&( Nav_MeasuredAngularVelocity_deg_d < BLOCKAGE_ANGULAR_VELOCITY_THRESHOLD )
			)
			{
				Nav_BlockageCounter_u8 ++;
			}
			else
			{
				Nav_BlockageCounter_u8 = 0 ;
			}

			if ( Nav_BlockageCounter_u8 > 100 )
			{
				Nav_BlockageCounter_u8 = 0 ;
				Nav_GoToXY_State_en = Nav_GoToXY_BlockageDetected_en ;
				Nav_NavigatorCurrentState_en = MASTER_NavigatorBlockageDetected_en;
			}
		}

		else {
			if (
					(
							( Nav_LeftMotorCommand_i32 > ANGULAR_SLOW_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
							|| ( Nav_RightMotorCommand_i32 > ANGULAR_SLOW_BLOCKAGE_MOTOR_COMMAND_THRESHOLD )
					)
					&&( Nav_MeasuredVelocity_mm_d < SLOW_BLOCKAGE_LINEAR_VELOCITY_THRESHOLD )
					&&( Nav_MeasuredAngularVelocity_deg_d < SLOW_BLOCKAGE_ANGULAR_VELOCITY_THRESHOLD )
			)
			{
				Nav_BlockageCounter_u8 ++;
			}
			else
			{
				Nav_BlockageCounter_u8 = 0 ;
			}

			if ( Nav_BlockageCounter_u8 > SLOW_BLOCKAGE_DURATION_THRESHOLD )
			{
				Nav_BlockageCounter_u8 = 0 ;
				Nav_GoToXY_State_en = Nav_GoToXY_BlockageDetected_en ;
				Nav_NavigatorCurrentState_en = MASTER_NavigatorWallBlockageDetected_en;
			}
		}

	}



}


void Nav_navigationSimulationTest(double * Nav_CurrentX_mm_d, double * Nav_CurrentY_mm_d, double * Nav_CurrentAngle_deg_d){

	float direction_vector_x, direction_vector_y;
	float target_angle;
	direction_vector_x = Nav_TargetX_mm_d - (*Nav_CurrentX_mm_d);
	direction_vector_y = Nav_TargetY_mm_d - (*Nav_CurrentY_mm_d);
	target_angle = atan2(direction_vector_y, direction_vector_x) * 180.0 / M_PI ;

	(*Nav_CurrentAngle_deg_d) = target_angle;

	if ( *Nav_CurrentX_mm_d < Nav_TargetX_mm_d ){
		(*Nav_CurrentX_mm_d) ++;
	}

	if (*Nav_CurrentY_mm_d < Nav_TargetY_mm_d ){
		(*Nav_CurrentY_mm_d) ++;
	}

	if( *Nav_CurrentX_mm_d > Nav_TargetX_mm_d ){
		(*Nav_CurrentX_mm_d) --;
	}

	if( *Nav_CurrentY_mm_d > Nav_TargetY_mm_d ){
		(*Nav_CurrentY_mm_d) --;
	}

}
void Nav_vIndependantTrajectoryStateMachine()
{
	switch(Nav_TrajectoryState_en)
	{

	case Nav_Trajectory_Idle_en :
	{

	}break;

	case Nav_Trajectory_ResetVariables_en :
	{
		//reset the current sample
		Nav_CurrentSample_u32 = 0;
		Nav_TrapezePhase_en = Nav_Trapeze_Accelerating_en;
		//reset measuring variables
		ENCODER_RIGHT->CNT = ENCODER_RIGHT->ARR / 2 ;
		ENCODER_LEFT->CNT = ENCODER_LEFT->ARR / 2 ;
		Nav_PrevMeasuredDistance_mm_d = 0.0 ;
		Nav_PrevMeasuredAngle_rad_d   = 0.0 ;
		//Nav_PrevMeasuredAngle_deg_d   = 0.0 ;
		Nav_vFeedbackRoutine();

		//reset the Target Distance variables
		Nav_CurrentTargetDistance_mm_d = 0.0 ;
		Nav_PrevTargetDistance_mm_d = 0.0 ;

		Nav_PrevTargetAngle_deg_d = Nav_CurrentTargetAngle_deg_d;

		//reset the pid variables
		Nav_SumDistanceError_d = 0.0 ;
		Nav_SumAngleError_d = 0.0 ;
		Nav_SCurve_Phase_u8       = 1;   /* start at Phase I */
		Nav_SCurve_CurrentAccel_d = 0.0;
		Nav_TrajectoryState_en = Nav_Trajectory_SetPath_en;
	}break;

	case Nav_Trajectory_SetPath_en :
	{

		Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d-Nav_MeasuredDistance_mm_d  );
		if ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{Nav_ProfileTargetDistance_mm_d=sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;

			Nav_MaxVelocity_d = Nav_MaxVelocity_d * SAMPLING_PERIOD ;
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;
			Nav_Jerk_d = Nav_Jerk_d * SAMPLING_PERIOD * SAMPLING_PERIOD * SAMPLING_PERIOD;

			if(Nav_MaxVelocity_d>FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING)
			{FORWARD_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY}
			else{FORWARD_LINEAR_TRAJECTORY_PID_LOW_VELOCITY}
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{Nav_ProfileTargetDistance_mm_d=-sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;

			Nav_MaxVelocity_d = Nav_MaxVelocity_d * SAMPLING_PERIOD ;
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;
			if(Nav_MaxVelocity_d< (-FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING)  )
			{REVERSE_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY}
			else{REVERSE_LINEAR_TRAJECTORY_PID_LOW_VELOCITY}
		}
		else if ( Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en )
		{
			Nav_MaxAngularVelocity_d = Nav_MaxAngularVelocity_d * SAMPLING_PERIOD ;
			Nav_AngularAcc_d = Nav_AngularAcc_d * SAMPLING_PERIOD * SAMPLING_PERIOD;
			FORWARD_ANGULAR_TRAJECTORY_PID
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseAngularTrajectory_en )
		{
			Nav_MaxAngularVelocity_d = Nav_MaxAngularVelocity_d * SAMPLING_PERIOD ;
			Nav_AngularAcc_d = Nav_AngularAcc_d * SAMPLING_PERIOD * SAMPLING_PERIOD;
			FORWARD_ANGULAR_TRAJECTORY_PID
		}
		Nav_Counter_u32 = 0 ;

		Nav_TrajectoryState_en = Nav_Trajectory_WaitToExecute_en;
	}break;

	case Nav_Trajectory_WaitToExecute_en :
	{
		Nav_Counter_u32++;
		if (Nav_Counter_u32 > 2)
		{
			Nav_TrajectoryState_en = Nav_Trajectory_Execute_en;
			Nav_Counter_u32 =0;
		}
	}break;

	case Nav_Trajectory_Execute_en :
	{
		Nav_CurrentSample_u32++;
		if  ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_TargetDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
		if( Nav_LimitDistance_mm_d > 20.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ) ) * 180.0 ) / M_PI;

				Nav_vCurrentTargetAngleFollower();
			}
			else{
				Nav_CurrentTargetAngle_deg_d=Nav_TargetAngle_deg_d;
				Nav_vCurrentTargetAngleFollower();

			}
			//S_CurveLinearVelocity();
			Nav_TrapezeLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
			Nav_TargetDistance_mm_d = - sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
			if( Nav_LimitDistance_mm_d > 20.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_CurrentTargetY_mm_d - Nav_TargetY_mm_d ) ,(Nav_CurrentTargetX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				Nav_Test_enter_2 ++ ;
				Nav_vCurrentTargetAngleFollower();

			}
			else{
				Nav_CurrentTargetAngle_deg_d=Nav_TargetAngle_deg_d;
				Nav_vCurrentTargetAngleFollower();

			}
			Nav_TrapezeReverseLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();

			Nav_Going_BackwardTargetX_mm_d = 2 * Nav_CurrentX_mm_d - Nav_TargetX_mm_d ;
			Nav_Going_BackwardTargetY_mm_d = 2 * Nav_CurrentY_mm_d - Nav_TargetY_mm_d ;
			//Nav_TargetAngle_deg_d = ( atan2( (Nav_Going_BackwardTargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_Going_BackwardTargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;


		}
		else if ( Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en )
		{
			if ( Nav_GoToXY_State_en == Nav_GoToXY_Rotate_en ) // because in the rotate after state we need to go to a constant target angle
			{
				if (ROBOT_Direction == ROBOT_Going_Forward)
				{
					Nav_TargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;
				}
				else
				{
					Nav_TargetAngle_deg_d = ( atan2( (Nav_CurrentY_mm_d - Nav_TargetY_mm_d) ,(Nav_CurrentX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				}
			}
			Nav_RemainingAngle_deg_d =  Nav_TargetAngle_deg_d - Nav_CurrentTargetAngle_deg_d  ;
			Nav_vSaturateRemainingAngle();
			Nav_TrapezeAngularVelocity2();
			Nav_vTargetAngleCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseAngularTrajectory_en )
		{
			if ( Nav_GoToXY_State_en == Nav_GoToXY_Rotate_en )
			{
				if (ROBOT_Direction == ROBOT_Going_Forward)
				{
					Nav_TargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;
				}
				else
				{
					Nav_TargetAngle_deg_d = ( atan2( (Nav_CurrentY_mm_d - Nav_TargetY_mm_d) ,(Nav_CurrentX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				}
			}
			Nav_RemainingAngle_deg_d =  Nav_TargetAngle_deg_d - Nav_CurrentTargetAngle_deg_d  ;
			Nav_vSaturateRemainingAngle();
			Nav_TrapezeReverseAngularVelocity2();
			Nav_vTargetAngleCalculationRoutine();
		}

		if  ( ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en ) || ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en ) )
		{
			if( ( Nav_CurrentSample_u32 > Nav_AccelerationSamples_u32 )
					&& ( Nav_TargetLinearVelocity_d == 0 )
					&& ( fabs (Nav_TargetAngularVelocity_d) < 0.0001 )
					&& ( Nav_MeasuredVelocity_mm_d == 0 )
					&& ( Nav_MeasuredAngularVelocity_deg_d == 0 )
					&& ( fabs( Nav_DistanceError_d ) < 1.5 ) )
			{
				Nav_Counter_u32 ++ ;
			}
			else
			{
				Nav_Counter_u32 = 0 ;
			}
		}
		else if ( ( Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en ) ||  ( Nav_TrajectoryMode_en == Nav_ReverseAngularTrajectory_en  ) )
		{
			if( ( Nav_CurrentSample_u32 > Nav_AccelerationSamples_u32 )
					&& ( Nav_TargetLinearVelocity_d == 0 )
					&& ( fabs (Nav_TargetAngularVelocity_d) < 0.0001 )
					&& ( Nav_MeasuredVelocity_mm_d == 0 )
					&& ( Nav_MeasuredAngularVelocity_deg_d == 0 )
					&& ( fabs( Nav_AngleError_d ) < 1.5 ) )
			{
				Nav_Counter_u32 ++ ;

			}
			else
			{
				Nav_Counter_u32 = 0 ;
			}

		}

		if (Nav_Counter_u32>5)
		{


			Nav_TrajectoryState_en=Nav_Trajectory_WaitAfterArriving_en;
			Nav_Counter_u32=0;
		}

	}break;
	case Nav_Trajectory_OrderSuddenStop_en :
	{

		Nav_TrajectoryState_en = Nav_Trajectory_ExecuteSuddenStop_en ;

		if ( ( Nav_Trapeze_Accelerating_en == Nav_TrapezePhase_en )
				||( Nav_Trapeze_ConstantVelocity_en == Nav_TrapezePhase_en )
				||( Nav_Trapeze_Decelerating_en == Nav_TrapezePhase_en ) )
		{
			Nav_TrapezePhase_en = Nav_Trapeze_OrderUrgentDecelerating_en ;
		}
		else
		{
			Nav_AccelerationSamples_u32 = Nav_CurrentSample_u32 - 1;
		}


		if ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;//4000
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;
		}
		else if ( Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en )
		{
			Nav_AngularAcc_d = Nav_AngularAcc_d * SAMPLING_PERIOD * SAMPLING_PERIOD;
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseAngularTrajectory_en )
		{
			Nav_AngularAcc_d = Nav_AngularAcc_d * SAMPLING_PERIOD * SAMPLING_PERIOD;
		}

		Nav_CurrentSample_u32++;
		if (  Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_TrapezeLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
			Nav_TrapezeReverseLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en )
		{
			Nav_TrapezeAngularVelocity2();
			Nav_vTargetAngleCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseAngularTrajectory_en )
		{
			Nav_TrapezeReverseAngularVelocity2();
			Nav_vTargetAngleCalculationRoutine();
		}

	}break;

	case Nav_Trajectory_ExecuteSuddenStop_en :
	{
		Nav_CurrentSample_u32++;
		if ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_TrapezeLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
			Nav_TrapezeReverseLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}

		else if ( Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en )
		{
			Nav_TrapezeAngularVelocity2();
			Nav_vTargetAngleCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseAngularTrajectory_en )
		{
			Nav_TrapezeReverseAngularVelocity2();
			Nav_vTargetAngleCalculationRoutine();
		}
		if( ( Nav_CurrentSample_u32 > Nav_AccelerationSamples_u32 )
				&& ( Nav_TargetLinearVelocity_d == 0 )
				&& ( Nav_TargetAngularVelocity_d == 0 )
				&& ( Nav_MeasuredVelocity_mm_d == 0 )
				&& ( Nav_MeasuredAngularVelocity_deg_d == 0 ) )
		{
			Nav_Counter_u32 = 0 ;
			Nav_TrajectoryState_en = Nav_Trajectory_WaitAfterArriving_en;
		}

	}break;

	case Nav_Trajectory_WaitAfterArriving_en :
	{
		Nav_Counter_u32++;
		if (Nav_Counter_u32 > 2)
		{
			Nav_TrajectoryState_en = Nav_Trajectory_Finish_en;

		}
	}break;

	case Nav_Trajectory_Finish_en :
	{

	}break;
	}

}




Nav_TestPathStates_ten Nav_TestPathState_en = Nav_Test_Idle_en ;
void Nav_vTestPathStateMachine()
{	MINIMUM_COMMANDS_WITHOUT_PLATFORMS
	switch( Nav_TestPathState_en )
	{

	case Nav_Test_Idle_en :
	{
		Nav_TestPathState_en = Nav_Test_Rotate_360deg_en;
	}break;

	case Nav_Test_Forward_1000mm_en :
	{
		if ( Nav_TrajectoryState_en == Nav_Trajectory_Idle_en )
		{
			Nav_TrajectoryMode_en = Nav_ForwardLinearTrajectory_en;
			Nav_MaxVelocity_d =450 ; //400 ; //300 ;
			Nav_Acc_d =675 ;
			Nav_TargetDistance_mm_d =1000;
			Nav_TrajectoryState_en = Nav_Trajectory_ResetVariables_en;
		}
		else if ( Nav_TrajectoryState_en == Nav_Trajectory_Finish_en)
		{
			Nav_TestPathState_en = Nav_Test_Finished_en;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;
		}
		else
		{
			Nav_vIndependantTrajectoryStateMachine();
		}
	}break;

	case Nav_Test_Rotate_360deg_en :
	{
		if ( Nav_TrajectoryState_en == Nav_Trajectory_Idle_en )
		{
			Nav_TrajectoryMode_en =Nav_ForwardAngularTrajectory_en;
			Nav_MaxAngularVelocity_d = 180; //70 ;
			Nav_AngularAcc_d = 200 ;
			Nav_TargetAngle_deg_d = 3600;
			Nav_TrajectoryState_en = Nav_Trajectory_ResetVariables_en;
		}
		else if ( Nav_TrajectoryState_en == Nav_Trajectory_Finish_en)
		{
			Nav_TestPathState_en = Nav_Test_Finished_en;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;
		}
		else
		{
			Nav_vIndependantTrajectoryStateMachine();
		}
	}break;

	case Nav_Test_Reverse_1000mm_en :
	{
		if ( Nav_TrajectoryState_en == Nav_Trajectory_Idle_en )
		{
			Nav_TrajectoryMode_en = Nav_ReverseLinearTrajectory_en;
			Nav_MaxVelocity_d = -450 ; //-400 ; //-300 ;
			Nav_Acc_d = -500 ;
			Nav_TargetDistance_mm_d =-1000;
			Nav_TrajectoryState_en = Nav_Trajectory_ResetVariables_en;
		}
		else if ( Nav_TrajectoryState_en == Nav_Trajectory_Finish_en)
		{
			Nav_TestPathState_en = Nav_Test_Finished_en;
			Nav_TrajectoryState_en = Nav_Trajectory_Idle_en;
		}
		else
		{
			Nav_vIndependantTrajectoryStateMachine();
		}
	}break;

	case Nav_Test_Finished_en :
	{
		//Nav_TestPathState_en = Nav_Test_Idle_en;
	}break;
	}
	Nav_vNavigationRoutine();
}






