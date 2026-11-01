/*
 * CalibratingFunctions.c
 *
 *  Created on: May 7, 2024
 *      Author: Dhia Mnasri
 */

//navigating versions

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
		Nav_TrajectoryState_en = Nav_Trajectory_SetPath_en;
	}break;

	case Nav_Trajectory_SetPath_en :
	{

		Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
		if ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_MaxVelocity_d = Nav_MaxVelocity_d * SAMPLING_PERIOD ;
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;
			if(Nav_MaxVelocity_d>FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING)
			{FORWARD_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY}
			else{FORWARD_LINEAR_TRAJECTORY_PID_LOW_VELOCITY}
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
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
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
			if( Nav_LimitDistance_mm_d > 10.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ) ) * 180.0 ) / M_PI;

				Nav_vCurrentTargetAngleFollower();
			}
			Nav_TrapezeLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
			Nav_TargetDistance_mm_d = - sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
			if( Nav_LimitDistance_mm_d > 10.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_CurrentTargetY_mm_d - Nav_TargetY_mm_d ) ,(Nav_CurrentTargetX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				Nav_Test_enter_2 ++ ;
				Nav_vCurrentTargetAngleFollower();

			}
			Nav_TrapezeReverseLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();

			Nav_Going_BackwardTargetX_mm_d = 2 * Nav_CurrentX_mm_d - Nav_TargetX_mm_d ;
			Nav_Going_BackwardTargetY_mm_d = 2 * Nav_CurrentY_mm_d - Nav_TargetY_mm_d ;
			Nav_TargetAngle_deg_d = ( atan2( (Nav_Going_BackwardTargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_Going_BackwardTargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;


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



// calibrating versions

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
		Nav_TrajectoryState_en = Nav_Trajectory_SetPath_en;
	}break;

	case Nav_Trajectory_SetPath_en :
	{

		Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d );
		if ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_MaxVelocity_d = Nav_MaxVelocity_d * SAMPLING_PERIOD ;
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;
			if(Nav_MaxVelocity_d>FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING)
			{FORWARD_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY}
			else{FORWARD_LINEAR_TRAJECTORY_PID_LOW_VELOCITY}
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
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
//			Nav_TargetDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d  );
//			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
//			if( Nav_LimitDistance_mm_d > 10.0)
//			{
//				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
//				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
//				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ) ) * 180.0 ) / M_PI;
//
//				Nav_vCurrentTargetAngleFollower();
//			}
			Nav_TrapezeLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
//			Nav_TargetDistance_mm_d = - sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d );
//			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
//			if( Nav_LimitDistance_mm_d > 10.0)
//			{
//				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
//				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
//				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_CurrentTargetY_mm_d - Nav_TargetY_mm_d ) ,(Nav_CurrentTargetX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
//				Nav_Test_enter_2 ++ ;
//				Nav_vCurrentTargetAngleFollower();
//
//			}
			Nav_TrapezeReverseLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
//
//			Nav_Going_BackwardTargetX_mm_d = 2 * Nav_CurrentX_mm_d - Nav_TargetX_mm_d ;
//			Nav_Going_BackwardTargetY_mm_d = 2 * Nav_CurrentY_mm_d - Nav_TargetY_mm_d ;
//			Nav_TargetAngle_deg_d = ( atan2( (Nav_Going_BackwardTargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_Going_BackwardTargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;


		}
		else if ( Nav_TrajectoryMode_en == Nav_ForwardAngularTrajectory_en )
		{
			if ( Nav_GoToXY_State_en == Nav_GoToXY_Rotate_en ) // because in the rotate after state we need to go to a constant target angle
			{
				if (ROBOT_Direction == ROBOT_Going_Forward)
				{
//					Nav_TargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;
				}
				else
				{
//					Nav_TargetAngle_deg_d = ( atan2( (Nav_CurrentY_mm_d - Nav_TargetY_mm_d) ,(Nav_CurrentX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				}
			}
			Nav_RemainingAngle_deg_d =  Nav_TargetAngle_deg_d - Nav_CurrentTargetAngle_deg_d  ;
//			Nav_vSaturateRemainingAngle();
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
//			Nav_vSaturateRemainingAngle();
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
//ekher wahda khdemna biha
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
		Nav_TrajectoryState_en = Nav_Trajectory_SetPath_en;
	}break;

	case Nav_Trajectory_SetPath_en :
	{

		Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
		if ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_MaxVelocity_d = Nav_MaxVelocity_d * SAMPLING_PERIOD ;
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;
			if(Nav_MaxVelocity_d>FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING)
			{FORWARD_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY}
			else{FORWARD_LINEAR_TRAJECTORY_PID_LOW_VELOCITY}
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
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
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
			if( Nav_LimitDistance_mm_d > 10.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ) ) * 180.0 ) / M_PI;

				Nav_vCurrentTargetAngleFollower();
			}
			Nav_TrapezeLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
			Nav_TargetDistance_mm_d = - sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
			if( Nav_LimitDistance_mm_d > 10.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_CurrentTargetY_mm_d - Nav_TargetY_mm_d ) ,(Nav_CurrentTargetX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				Nav_Test_enter_2 ++ ;
				Nav_vCurrentTargetAngleFollower();

			}
			Nav_TrapezeReverseLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();

			Nav_Going_BackwardTargetX_mm_d = 2 * Nav_CurrentX_mm_d - Nav_TargetX_mm_d ;
			Nav_Going_BackwardTargetY_mm_d = 2 * Nav_CurrentY_mm_d - Nav_TargetY_mm_d ;
			Nav_TargetAngle_deg_d = ( atan2( (Nav_Going_BackwardTargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_Going_BackwardTargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;


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
		Nav_TrajectoryState_en = Nav_Trajectory_SetPath_en;
	}break;

	case Nav_Trajectory_SetPath_en :
	{

		Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
		if ( Nav_TrajectoryMode_en == Nav_ForwardLinearTrajectory_en )
		{
			Nav_MaxVelocity_d = Nav_MaxVelocity_d * SAMPLING_PERIOD ;
			Nav_Acc_d = Nav_Acc_d * SAMPLING_PERIOD * SAMPLING_PERIOD ;
			if(Nav_MaxVelocity_d>FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING)
			{FORWARD_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY}
			else{FORWARD_LINEAR_TRAJECTORY_PID_LOW_VELOCITY}
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
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
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
			if( Nav_LimitDistance_mm_d > 10.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d) ,(Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ) ) * 180.0 ) / M_PI;
				Nav_vCurrentTargetAngleFollower();
			}
			Nav_TrapezeLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();
		}
		else if ( Nav_TrajectoryMode_en == Nav_ReverseLinearTrajectory_en )
		{
			Nav_TargetDistance_mm_d = - sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentY_mm_d , 2 ) ) ;
			Nav_RemainingDistance_mm_d = Nav_TargetDistance_mm_d - ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d );
			Nav_LimitDistance_mm_d = sqrt ( pow( Nav_TargetX_mm_d - Nav_CurrentTargetX_mm_d ,2 ) + pow( Nav_TargetY_mm_d - Nav_CurrentTargetY_mm_d , 2 ) ) ;
			if( Nav_LimitDistance_mm_d > 10.0)
			{
				Nav_CurrentTargetX_mm_d = Nav_CurrentX_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*cos( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetY_mm_d = Nav_CurrentY_mm_d + ( Nav_CurrentTargetDistance_mm_d -  Nav_MeasuredDistance_mm_d )*sin( Nav_CurrentAngle_rad_d ) ;
				Nav_CurrentTargetAngle_deg_d = ( atan2( (Nav_CurrentTargetY_mm_d - Nav_TargetY_mm_d ) ,(Nav_CurrentTargetX_mm_d - Nav_TargetX_mm_d ) ) * 180.0 ) / M_PI;
				Nav_Test_enter_2 ++ ;
				Nav_vCurrentTargetAngleFollower();

			}
			Nav_TrapezeReverseLinearVelocity2();
			Nav_vTargetDistanceCalculationRoutine();

			Nav_Going_BackwardTargetX_mm_d = 2 * Nav_CurrentX_mm_d - Nav_TargetX_mm_d ;
			Nav_Going_BackwardTargetY_mm_d = 2 * Nav_CurrentY_mm_d - Nav_TargetY_mm_d ;
			Nav_TargetAngle_deg_d = ( atan2( (Nav_Going_BackwardTargetY_mm_d - Nav_CurrentY_mm_d) ,(Nav_Going_BackwardTargetX_mm_d - Nav_CurrentX_mm_d ) ) * 180.0 ) / M_PI;


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
					&& ( fabs( Nav_DistanceError_d ) < 1.5 ))
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

