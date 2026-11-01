/*
 * navigation.h
 *
 *  Created on: Aug 27, 2025
 *      Author: monji
 */

#ifndef INC_NAVIGATION_H_
#define INC_NAVIGATION_H_

#include "Odometry.h"

enum Wheel_state{
	DEAD_STOP,
	ACCELERATING,
	CONTROLLED_BREAK,
	EMERGENCY_BREAK,
	CRUISING // holding the same speed
}; // other states will be added, like doing a curve

enum Trajectory{
	STRAIGHT,
	ROTATING,
	CIRCLE_CURVE,
	BEZIER_CURVE
};

enum Control_loop {
	DISACTIVATED, // blocks the main PID until the Raspberry activates the STM
	ACTIVATED,
	SPEED,
	POSITION,
	SHUTDOWN
};

enum Robot_state_enum{
	IDLE,
	MOVIN_FORWARD,
	MOVIN_BACKWARD,
	GOIN_TO,
	GOIN_TO_BACKWARDS,
	ROTATIN,
	ORIENTATIN,
	BEZIER_CURVIN,
	BEZIER_CURVIN_BACKWARDS,
	RESETIN,
	SETTIN_POSITION,
	CREEPIN_TO,
	CREEPIN_TO_BACKWARDS
};

typedef struct{
	enum Robot_state_enum status;
	float arguments[9];
}robot_state;

extern robot_state robot_status;
extern enum Wheel_state wheel_state_R;
extern enum Wheel_state wheel_state_L;
extern enum Control_loop control_loop_state;
extern enum Trajectory trajectory;
extern float ramping_acceleration; // !!! these accelerations marks the rate of change in velocity with respect to the distance traveled, not time!!!
extern float breaking_acceleration;
extern float emergency_breaking_acceleration;
extern float deceleration_offset;
extern float deceleration_offset_fast;
extern float speed_offset_fast;
extern float deceleration_offset_smooth;
extern float breaking_acceleration_speed;
extern float breaking_acceleration_smooth;
extern float speed_offset_smooth;
extern float rotating_speed;
extern int8_t direction_R; // 1 if going forward, -1 if backwards
extern int8_t direction_L;
extern float cruise_speed_R; // the speed which the right wheel is accelerating towards
extern float cruise_speed_L;
extern float creep_speed;
extern float clearance_from_crates;
extern float speed_offset;
extern float starting_phi;
extern float turning_radius;
extern int8_t reached_destination;
extern int command_history;
extern int target_command_x;
extern int target_command_y;
extern int target_command_phi;
extern int emergency_recieved;
extern int stopped_because_of_collision;

int move_forward(float distance, float speed, int8_t is_smooth); // will return 0 if target has been reached successfully or 1 if it could not be reached
int move_forward_full(float distance, float speed, float target_x, float target_y, int8_t is_smooth);
int creep_forward(float max_distance, float target_x, float target_y);
float calculate_instant_target_speed_full(float x, float distance, float ramping__acceleration, float breaking__acceleration);
float calculate_instant_target_speed(float x, float distance);
float calculate_instant_target_phi(float x, float distance);
int rotate(float angle, int8_t is_radian, int8_t is_smooth);// is_radian should be set to 1 if the angle is expressed in radians and to 0 if in degrees
int orientate(float orientation, int8_t is_radian, int8_t is_smooth);// will return 0 if target has been reached successfully or 1 if it could not be reached
int bezier_curve(float x1, float y1, float x2, float y2, float x3, float y3, float speed, int direction, int8_t is_smooth); // sa77a maram
int go_to(float x, float y, float speed, int direction, int8_t is_smooth);// will return 0 if target has been reached successfully or 1 if some error happened in rotation, 2 if some error happened in moving forward
void emergency_break();
int creep_to(float x, float y, int direction);
void set_target_encoder_counts(int32_t encoder__count_R, int32_t encoder__count_L);
int8_t is_idle();
void wait_for_idle();
void reset_speed_control_variables();
void apply_smooth_or_not(float distance, int8_t is_smooth);
void prepare_go_to(float x, float y, float speed, int direction, int8_t is_smooth);
void prepare_creep_to(float x, float y, int direction);
void prepare_orientate(float orientation, int8_t is_radian, int8_t is_smooth);
void prepare_bezier_curve(float x1, float y1, float x2, float y2, float x3, float y3, float speed, int direction, int8_t is_smooth);
void prepare_emergency_break();
void prepare_reset();
void prepare_set_position(float x, float y, float phi, float absolute_phi);
void reset_navigation_vars();
float estimate_time_remaining_profile(float x, float distance, float x1, float x2);
float hybrid_arrival_time(float x, float distance, float x1, float x2, float distance_to_target);
#endif /* INC_NAVIGATION_H_ */
