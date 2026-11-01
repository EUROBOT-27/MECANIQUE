/*
 * NavConstants.h
 *
 *  Created on: Nov 17, 2023
 *      Author: Dhia Mnasri
 */

#ifndef INC_NAVCONSTANTS_H_
#define INC_NAVCONSTANTS_H_
#define M_2PI			6.28318530717958647692
#define SAMPLING_PERIOD   		0.005
#define MAXIMUM_MOTOR_COMMAND  					5000
#define MINIMUM_SATURATION_COMMAND_LINEAR				30
#define MINIMUM_SATURATION_COMMAND_ANGULAR			30
//19 angular
#define Nav_No_Rotate_After 	655
#define ROBOT_Going_Backward 	0
#define ROBOT_Going_Forward		1

#define ROBOT_With_Platforms 	1
#define ROBOT_Without_Platforms		0

#define MINIMUM_COMMANDS_WITHOUT_PLATFORMS \
					MINIMUM_RIGHT_MOTOR_FORWARD_COMMAND	=350; \
		MINIMUM_RIGHT_MOTOR_REVERSE_COMMAND	=400;\
		MINIMUM_LEFT_MOTOR_FORWARD_COMMAND    =440;\
		MINIMUM_LEFT_MOTOR_REVERSE_COMMAND	=330;

#define MINIMUM_COMMANDS_WITH_PLATFORMS \
					MINIMUM_RIGHT_MOTOR_FORWARD_COMMAND	=370; \
		MINIMUM_RIGHT_MOTOR_REVERSE_COMMAND	=450;\
		MINIMUM_LEFT_MOTOR_FORWARD_COMMAND    =440;\
		MINIMUM_LEFT_MOTOR_REVERSE_COMMAND	=360;

#define LINEAR_BLOCKAGE_MOTOR_COMMAND_THRESHOLD		3250
#define ANGULAR_BLOCKAGE_MOTOR_COMMAND_THRESHOLD		3250
#define BLOCKAGE_LINEAR_VELOCITY_THRESHOLD		2.0
#define BLOCKAGE_ANGULAR_VELOCITY_THRESHOLD		1.0
#define BLOCKAGE_DURATION_THRESHOLD				1

#define LINEAR_SLOW_BLOCKAGE_MOTOR_COMMAND_THRESHOLD		900
#define ANGULAR_SLOW_BLOCKAGE_MOTOR_COMMAND_THRESHOLD		900
#define SLOW_BLOCKAGE_LINEAR_VELOCITY_THRESHOLD		0.5
#define SLOW_BLOCKAGE_ANGULAR_VELOCITY_THRESHOLD		0.1
#define SLOW_BLOCKAGE_DURATION_THRESHOLD				1

#define TRACK_MM     					297.97//285.1
#define WHEEL_LEFT_DIAMETER_MM  		64.0
#define WHEEL_RIGHT_DIAMETER_MM   	    64.0
#define WHEEL_DIAMETER_MM  			61//61.275//62.3  //61.1
#define LEFT_WHEEL_GAIN						1//1.001//1.00073//1.0007
#define ENCODER_RESOLUTION		2048.0

#define FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING 201.00*0.005
//PID

#define FORWARD_LINEAR_VELOCITY_THRESH_4_GAIN_SCHEDULING 201.00*0.005
//PID

#define FORWARD_LINEAR_TRAJECTORY_PID_LOW_VELOCITY	      \
		Nav_KpDistance_d    = 110;   \
		Nav_KiDistance_d    = 0.0;	 	\
		Nav_KdDistance_d    = 920;   \
		Nav_KpAngle_d       = 125		  ;  \
		Nav_KiAngle_d       = 0.00000 ;     \
		Nav_KdAngle_d       = 1700 ;

#define REVERSE_LINEAR_TRAJECTORY_PID_LOW_VELOCITY  \
		Nav_KpDistance_d    = 0;   \
		Nav_KiDistance_d    = 0.0;	 	\
		Nav_KdDistance_d    = 0;   \
		Nav_KpAngle_d       = 0		  ;  \
		Nav_KiAngle_d       = 0.00000 ;     \
		Nav_KdAngle_d       = 0 ;
#define FORWARD_ANGULAR_TRAJECTORY_PID \
		Nav_KpDistance_d = 40; \
		Nav_KiDistance_d = 0.00; \
		Nav_KdDistance_d = 500; \
		Nav_KpAngle_d = 125; \
		Nav_KiAngle_d = 0.0 ; \
		Nav_KdAngle_d =2700;
// 70 0 200 85 0 1600
#define REVERSE_ANGULAR_TRAJECTORY_PID \
		Nav_KpDistance_d    = 0;   \
		Nav_KiDistance_d    = 0.00;   \
		Nav_KdDistance_d    = 0 ;     \
		Nav_KpAngle_d       = 0 ;  \
		Nav_KiAngle_d       = 0.000 ;    \
		Nav_KdAngle_d       = 0;

#define FORWARD_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY	     \
		Nav_KpDistance_d    =50; \
		Nav_KiDistance_d    = 0;	 	\
		Nav_KdDistance_d    =200;   \
		Nav_KpAngle_d       =90;  \
		Nav_KiAngle_d       = 0;     \
		Nav_KdAngle_d       =2400;
//70 0 200 145 0 1600
#define REVERSE_LINEAR_TRAJECTORY_PID_HIGH_VELOCITY  \
		Nav_KpDistance_d    =50; \
		Nav_KiDistance_d    = 0;	 	\
		Nav_KdDistance_d    =200;   \
		Nav_KpAngle_d       =90;  \
		Nav_KiAngle_d       = 0;     \
		Nav_KdAngle_d       =2400;

//high velocity pid

#endif /* INC_NAVCONSTANTS_H_ */


