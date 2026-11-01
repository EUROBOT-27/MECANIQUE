/*
 * navigation.c
 *
 *  Created on: Aug 27, 2025
 *      Author: monji
 */
#include "navigation.h"

robot_state robot_status;
enum Wheel_state wheel_state_R = DEAD_STOP;
enum Wheel_state wheel_state_L = DEAD_STOP;
enum Trajectory trajectory = STRAIGHT;
enum Control_loop control_loop_state = DISACTIVATED;
float ramping_acceleration = 10;
float acc_linearization_coef = 0;
float dec_linearization_coef = 0;

float breaking_acceleration = -1.7;
float breaking_acceleration_speed = -1.7;
float breaking_acceleration_smooth = -1.55;

float deceleration_offset = 40;
float deceleration_offset_fast = 10;
float deceleration_offset_smooth = 80; //-80 fel 1000, -30 fel 300

float speed_offset = 150;
float speed_offset_fast = 150;
float speed_offset_smooth = 80;

float rotating_speed = 1000;
float creep_speed = 200;
int8_t direction_R;
int8_t direction_L;
float cruise_speed_R;
float cruise_speed_L;
float starting_phi;
float turning_radius;
float filtered_target_speed_R = 0;
float filtered_target_speed_L = 0;
float speed_filter = 0.95;
float clearance_from_crates = 9;

int8_t reached_destination = 1;
int command_history = 0;

int target_command_x = 0;
int target_command_y = 0;
int target_command_phi = 0;
int emergency_recieved = 0;
int stopped_because_of_collision = 0;
float reached_destination_time = 0.30;

int creep_forward(float max_distance, float target_x, float target_y){
	float direction = SGN(max_distance);
	float distance = fabs(max_distance);
	float speed = creep_speed;
	wait_for_idle();
	reset_speed_control_variables();
	direction_R = 1;
	direction_L = 1;

	float starting_x = current_x;
	float starting_y = current_y;

	// all of these formulas are derived from a ramp graph: speed = f(distance)
	float x1 = speed/ramping_acceleration;
	float x2 = speed/breaking_acceleration + distance + deceleration_offset;

	if (x2 <= x1){ // correcting the cruising speed if it is too high to reach using the current ramp and break
		float intersection_x = (breaking_acceleration*(distance+deceleration_offset))/(breaking_acceleration - ramping_acceleration);
		float intersection_speed = ramping_acceleration * intersection_x;
		speed = intersection_speed*0.9;
		x1 = speed/ramping_acceleration;
		x2 = speed/breaking_acceleration + distance + deceleration_offset;
	}
	acc_linearization_coef = sqrt(x1);
	dec_linearization_coef = sqrt(distance - x2);

	cruise_speed_R = speed;
	cruise_speed_L = speed;
	float distance_to_target = distance;
	float x = 0;

	wheel_state_R = ACCELERATING;
	wheel_state_L = ACCELERATING;
	trajectory = STRAIGHT;
	control_loop_state = SPEED;
	starting_phi = absolute_phi;
	int collision_counter = 0;
	float lane_correction_term;
	while (distance_to_target > 1 ){
		x = MAX(distance - distance_to_target, 0);
		if (wheel_state_R == ACCELERATING && x > x1 ){
			wheel_state_R = CRUISING;
			wheel_state_L = CRUISING;
		}else if (wheel_state_R == CRUISING && x > x2){
			wheel_state_R = CONTROLLED_BREAK;
			wheel_state_L = CONTROLLED_BREAK;
		}else if (wheel_state_R == EMERGENCY_BREAK){
			emergency_break();
			return 0;
		}
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}

		float deviation_angle = normalize_angle(atan2(current_y - starting_y, current_x - starting_x) - atan2(target_y - starting_y, target_x - starting_x) );
		float deviation_distance = -direction * sqrt(SQR(current_y - starting_y) + SQR(current_x - starting_x)) * sin(deviation_angle); // positive to the left and negative to the right
		float phi_correction_term = direction * (calculate_instant_target_phi(x, distance) - absolute_phi) * ( 3 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0) ); // the first coefficient is tunable
		lane_correction_term = (deviation_distance) * ( 0.01 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0)); // the first coefficient is tunable
		lane_correction_term +=  + phi_correction_term;
		lane_correction_term = MIN(MAX(lane_correction_term, -0.2), 0.2);
		if(x < 10){
			lane_correction_term = 0;
		}

		set_target_speeds(direction*calculate_instant_target_speed(x, distance)*(1 + lane_correction_term) ,direction*calculate_instant_target_speed(x, distance)* (1 - lane_correction_term));
		delay(4);
		distance_to_target = fabs(distance - get_distance_to(starting_x, starting_y));

		if ( (fabs(PWM_R) > STOP_PWM_THRESHOLD && fabs(current_speed_R) < STOP_SPEED_THRESHOLD)
			|| (fabs(PWM_L) > STOP_PWM_THRESHOLD && fabs(current_speed_L) < STOP_SPEED_THRESHOLD) ){
				// EMERGENCY STOP
			 collision_counter++;
			 if(collision_counter > 35){
				 stop_motors();
				 reached_destination = 1;
				 set_target_encoder_counts(encoder_count_R - direction * distance_to_ticks(clearance_from_crates, wheel_diameter_R), encoder_count_L - direction * distance_to_ticks(clearance_from_crates, wheel_diameter_L));
				 wheel_state_R = DEAD_STOP;
				 wheel_state_L = DEAD_STOP;
				 return 0;
			 }
		}
		else {
			 collision_counter = 0;
		}

		//send_values_to_usart(current_speed_L, current_speed_R, target_speed_L, target_speed_R);
	}
	stop_motors();
	reached_destination = 1;
	set_target_encoder_counts(encoder_count_R, encoder_count_L - (calculate_instant_target_phi(distance, distance) - absolute_phi)*dead_wheels_spacing*CPR / (wheel_diameter_L*PI) ); // the second part is there to fix any last minute fuck ups, concerning the phi
	wheel_state_R = DEAD_STOP;
	wheel_state_L = DEAD_STOP;
	return 0;
}

float estimate_time_remaining_profile(float x, float distance, float x1, float x2)
{
    float D = distance + deceleration_offset;
    float t = 0;

    if(x < x1) {
        t += 2.0 / (ramping_acceleration * acc_linearization_coef) * (sqrt(x1) - sqrt(x));
        t += (x2 - x1) / cruise_speed_R;
        t += (1.0 / fabs(breaking_acceleration)) * log((D - x1)/(D - x2));
    }
    else if(x < x2) {
        t += (x2 - x) / cruise_speed_R;
        t += (1.0 / fabs(breaking_acceleration)) * log((D - x)/(D - x2));
    }
    else {
        t += (1.0 / fabs(breaking_acceleration)) * log((D - x)/(D - x2));
    }
    return t;
}
float hybrid_arrival_time(float x, float distance, float x1, float x2, float distance_to_target)
{
    float alpha = 0.8;
    float t_profile = estimate_time_remaining_profile(x, distance,x1, x2);
//    float v_robot = (fabs(current_speed_R) + fabs(current_speed_L))/2.0;
//    v_robot = MAX(v_robot, 10.0);
    float t_measured = distance_to_target / speed_offset;
    float t_1 = alpha * t_profile + (1.0 - alpha) * t_measured;
    return t_1;
}
int move_forward_full(float distance, float speed, float target_x, float target_y, int8_t is_smooth){
	apply_smooth_or_not(fabs(distance), is_smooth);
	float direction = SGN(distance);
	distance = fabs(distance);
	if (distance < 400){
		breaking_acceleration = -3;
	}
	speed = fabs(speed);
	wait_for_idle();
	reset_speed_control_variables();
	direction_R = 1;
	direction_L = 1;

	float starting_x = current_x;
	float starting_y = current_y;

	// all of these formulas are derived from a ramp graph: speed = f(distance)
	float x1 = speed/ramping_acceleration;
	float x2 = speed/breaking_acceleration + distance + deceleration_offset;

	if (x2 <= x1){ // correcting the cruising speed if it is too high to reach using the current ramp and break
		float intersection_x = (breaking_acceleration*(distance+deceleration_offset))/(breaking_acceleration - ramping_acceleration);
		float intersection_speed = ramping_acceleration * intersection_x;
		speed = intersection_speed*0.9;
		x1 = speed/ramping_acceleration;
		x2 = speed/breaking_acceleration + distance + deceleration_offset;
	}
	acc_linearization_coef = sqrt(x1);
	dec_linearization_coef = sqrt(distance - x2);

	cruise_speed_R = speed;
	cruise_speed_L = speed;
	float distance_to_target = distance;
	float previous_distance_to_target = distance;
	float x = 0;

	wheel_state_R = ACCELERATING;
	wheel_state_L = ACCELERATING;
	trajectory = STRAIGHT;
	control_loop_state = SPEED;
	starting_phi = absolute_phi;
	float lane_correction_term;
	float phase_two_distance = 10 * (distance/300.0);
	while (distance_to_target > phase_two_distance){
		x = MAX(distance - distance_to_target, 0);
		if (wheel_state_R == ACCELERATING && x > x1 ){
			wheel_state_R = CRUISING;
			wheel_state_L = CRUISING;
		}else if (wheel_state_R == CRUISING && x > x2){
			wheel_state_R = CONTROLLED_BREAK;
			wheel_state_L = CONTROLLED_BREAK;
		}else if (wheel_state_R == EMERGENCY_BREAK){
			emergency_break();
			return 0;
		}
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}

		float deviation_angle = normalize_angle(atan2(current_y - starting_y, current_x - starting_x) - atan2(target_y - starting_y, target_x - starting_x) );
		float deviation_distance = -direction * sqrt(SQR(current_y - starting_y) + SQR(current_x - starting_x)) * sin(deviation_angle); // positive to the left and negative to the right
		float phi_correction_term = direction * (calculate_instant_target_phi(x, distance) - absolute_phi) * ( 3 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0) ); // the first coefficient is tunable
		lane_correction_term = (deviation_distance) * ( 0.01 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0)); // the first coefficient is tunable
		float slow_down_factor = 1 - fabs(lane_correction_term)*0.3;
		lane_correction_term +=  + phi_correction_term;
		lane_correction_term = MIN(MAX(lane_correction_term, -0.2), 0.2);
		if (x<10){
			lane_correction_term = 0;
		}

		set_target_speeds(direction*calculate_instant_target_speed(x, distance)*(1 + lane_correction_term) * slow_down_factor ,direction*calculate_instant_target_speed(x, distance)* (1 - lane_correction_term) * slow_down_factor );
		delay(4);
		previous_distance_to_target = distance_to_target;
		distance_to_target = fabs(distance - get_distance_to(starting_x, starting_y));
		if(hybrid_arrival_time(x, distance, x1, x2, distance_to_target) < reached_destination_time){
			reached_destination = 1;
		}

		//send_values_to_usart(current_speed_L, current_speed_R, target_speed_L, target_speed_R);
	}
	// completing the last part of distance separately, so the break happens on point
	// calculating the distance to move that  results in the robot being the closest to target point, i can't explain the math in code unfortunately
	float backwards_offset = PI*(1 - direction)/2;
	float x_closest = ( target_y - current_y + tan(current_phi + backwards_offset)*current_x - tan(current_phi + backwards_offset - PI/2)*target_x ) / ( tan(current_phi + backwards_offset) - tan(current_phi + backwards_offset - PI/2) );
	float y_closest = tan(current_phi)*(x_closest - current_x) + current_y;
	speed = (target_speed_R + target_speed_L)/ 2;
	speed = direction*MAX(fabs(speed), speed_offset);// handling the case where the robot skips the first while loop, being too close to target_distance
	
	distance_to_target = get_distance_to(x_closest, y_closest);
	previous_distance_to_target = distance_to_target;
	int32_t phase_two_start_time = micros();
	while (distance_to_target >0.1 && distance_to_target <= previous_distance_to_target){
		float deviation_angle = normalize_angle(atan2(current_y - starting_y, current_x - starting_x) - atan2(target_y - starting_y, target_x - starting_x) );
		float deviation_distance = -direction * sqrt(SQR(current_y - starting_y) + SQR(current_x - starting_x)) * sin(deviation_angle);
		float phi_correction_term = direction * (calculate_instant_target_phi(x, distance) - absolute_phi) * ( 1 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0) ); // the first coefficient is tunable
		lane_correction_term = (deviation_distance) * ( 0.01 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0) ) + phi_correction_term;
		lane_correction_term = MIN(MAX(lane_correction_term, -0.1), 0.1);
		//lane_correction_term = (calculate_instant_target_phi(x, distance) - absolute_phi) * ( 0.7 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0) ); // the coefficient is tunable
		set_target_speeds(speed*(1 + lane_correction_term) ,speed* (1 - lane_correction_term));
		speed = MAX(fabs(speed)*0.99, speed_offset) * direction;
		previous_distance_to_target = distance_to_target;
		distance_to_target = get_distance_to(x_closest, y_closest);
		delay(2);

		if(micros() - phase_two_start_time> 4000000){
			break;
		}
		if(hybrid_arrival_time(x, distance, x1, x2, distance_to_target) < reached_destination_time){
			reached_destination = 1;
		}
		if (wheel_state_R == EMERGENCY_BREAK){
			emergency_break();
			return 0;
		}
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}

		//send_values_to_usart(current_speed_L, current_speed_R, target_speed_L, target_speed_R);
	}
	stop_motors();
	reached_destination = 1;
	set_target_encoder_counts(encoder_count_R, encoder_count_L - (calculate_instant_target_phi(distance, distance) - absolute_phi)*dead_wheels_spacing*CPR / (wheel_diameter_L*PI) ); // the second part is there to fix any last minute fuck ups, concerning the phi
	wheel_state_R = DEAD_STOP;
	wheel_state_L = DEAD_STOP;
	return 0;
}
int move_forward(float distance, float speed, int8_t is_smooth){
	float target_x = current_x + distance*cos(current_phi);
	float target_y = current_y + distance*sin(current_phi);
	return move_forward_full(distance, speed, target_x, target_y, is_smooth);
}
float calculate_instant_target_speed_full(float x, float distance, float ramping__acceleration, float breaking__acceleration){
	if (wheel_state_R == ACCELERATING){
		if (direction_R == 1){
			filtered_target_speed_R = filtered_target_speed_R * speed_filter + (1 - speed_filter) * MAX(MIN(ramping__acceleration*sqrt(x)*acc_linearization_coef, cruise_speed_R), 20);
			return filtered_target_speed_R;
		}else{
			filtered_target_speed_R = filtered_target_speed_R * speed_filter + (1 - speed_filter) * MIN(MAX(-ramping__acceleration*sqrt(x)*acc_linearization_coef, cruise_speed_R), -20);;
			return filtered_target_speed_R;
		}

	}else if (wheel_state_R == CRUISING){
		filtered_target_speed_R = filtered_target_speed_R * speed_filter + (1 - speed_filter) * cruise_speed_R;
		return filtered_target_speed_R;

	}else if (wheel_state_R == CONTROLLED_BREAK){
		float pretend_x = distance - sqrt(distance - x) * dec_linearization_coef;
		if (direction_R == 1){
			filtered_target_speed_R = filtered_target_speed_R * speed_filter + (1 - speed_filter) * MIN(MAX(breaking__acceleration*(pretend_x - ((trajectory == ROTATING)?0:deceleration_offset)-distance), speed_offset), cruise_speed_R);
			return filtered_target_speed_R;
		}else{
			filtered_target_speed_R = filtered_target_speed_R * speed_filter + (1 - speed_filter) * MAX(MIN(-breaking__acceleration*(pretend_x - ((trajectory == ROTATING)?0:deceleration_offset)-distance), -speed_offset), cruise_speed_R);
			return filtered_target_speed_R;
		}
	}
	return 0; // just to prevent debugger error, will be erased once a definitive else is added
}

float calculate_instant_target_speed(float x, float distance){
	return calculate_instant_target_speed_full( x, distance, ramping_acceleration, breaking_acceleration);
}
float calculate_instant_target_phi(float x, float distance){
	if (trajectory == STRAIGHT){
		return starting_phi;
	}else if ( trajectory == CIRCLE_CURVE ){
		return starting_phi - x/turning_radius;
	}
	return 0;
}
int rotate(float angle, int8_t is_radian, int8_t is_smooth){
	wait_for_idle();
	reset_speed_control_variables();
	angle = is_radian? angle: deg_to_rad(angle);
	float rotating_ramping_acceleration = 20; // high acceleration for small angle and low for large
	float rotating_breaking_acceleration = -MIN(MAX(150.0/fabs(rad_to_deg(angle) - 4.1) + 1.5, 2.5), 25.0);; // same logic
	float arc_length = (dead_wheels_spacing/2) * angle;

	direction_R = SGN(arc_length);

	direction_L = -direction_R;

	// all of these formulas are derived from a ramp graph: speed = f(distance)
	float speed = rotating_speed;
	float distance = fabs(arc_length);
	apply_smooth_or_not(fabs(distance), is_smooth);
	float x1 = speed/rotating_ramping_acceleration;
	float x2 = speed/rotating_breaking_acceleration + distance;

	if (x2 <= x1){ // correcting the cruising speed if it is too high to reach using the current ramp and break
		float intersection_x = (rotating_breaking_acceleration*distance)/(rotating_breaking_acceleration - rotating_ramping_acceleration);
		float intersection_speed = rotating_ramping_acceleration * intersection_x;
		speed = 0.95 * intersection_speed;
		x1 = speed/rotating_ramping_acceleration;
		x2 = speed/rotating_breaking_acceleration + distance;
	}
	acc_linearization_coef = sqrt(x1);
	dec_linearization_coef = sqrt(distance - x2);

	cruise_speed_R = speed * direction_R;
	cruise_speed_L = speed * direction_L;

	// I will track only the right wheel cause both wheels need to be in sync
	float distance_to_target = distance;
	float previous_distance_to_target = distance;
	float x = 0;
	float target_phi = absolute_phi + angle;

	// Yaw centering, preventing that a wheel goes faster than the other and moves the rotation axis away from center
	float distance_traveled_R;
	float distance_traveled_L;
	const int32_t starting_encoder_count_R = encoder_count_R;
	const int32_t starting_encoder_count_L = encoder_count_L;
	float yaw_centering_term;

	float phase_two_angle = 6* (fabs(angle)/PI);

	wheel_state_R = ACCELERATING;
	wheel_state_L = ACCELERATING;
	trajectory = ROTATING;
	control_loop_state = SPEED;
	while ( fabs(target_phi - absolute_phi) > deg_to_rad(phase_two_angle)  && !(distance_to_target > previous_distance_to_target && distance_to_target< distance/2) ){
		x = distance - distance_to_target;
		x = MAX(distance - distance_to_target, 0);
		if (wheel_state_R == ACCELERATING && x > x1 ){
			wheel_state_R = CRUISING;
			wheel_state_L = CRUISING;
		}else if (wheel_state_R == CRUISING && x > x2){
			wheel_state_R = CONTROLLED_BREAK;
			wheel_state_L = CONTROLLED_BREAK;
		}else if (wheel_state_R == EMERGENCY_BREAK){
			emergency_break();
			return 0;
		}
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}


		distance_traveled_R = fabs(encoder_count_R - starting_encoder_count_R) * wheel_diameter_R * PI / CPR;
		distance_traveled_L = fabs(encoder_count_L - starting_encoder_count_L) * wheel_diameter_L * PI / CPR;


		speed = calculate_instant_target_speed_full(x, distance, rotating_ramping_acceleration, rotating_breaking_acceleration);
		yaw_centering_term = ( distance_traveled_R - distance_traveled_L ) * 0.1 / ( MAX(fabs(speed), 100)/100.0); //0.02 // the coefficient is tunable
		if (x < 0.1*x1){
			yaw_centering_term = 0;
		}
		set_target_speeds(speed*(1 - yaw_centering_term) ,-speed* (1 + yaw_centering_term));
		delay(4);
		previous_distance_to_target = distance_to_target;
		distance_to_target = (dead_wheels_spacing/2) * fabs(target_phi - absolute_phi);

		send_values_to_usart(current_speed_L, current_speed_R, target_speed_L, target_speed_R);
		//send_values_to_usart(absolute_phi*100, current_phi*100, 0, 0);
	}
	// completing the last part of distance separately, so the break happens on point

	speed = fabs(target_speed_R - target_speed_L)/ 2; // one of the speeds is negative, that's why there is a minus
	speed = MAX(fabs(speed), speed_offset)*direction_R;// handling the case where the robot skips the first while loop, being too close to target_distance
	distance_to_target = dead_wheels_spacing * fabs(target_phi - absolute_phi);
	previous_distance_to_target = distance_to_target;

	uint32_t phase_two_start_time = micros();
	while (fabs(target_phi - absolute_phi) > deg_to_rad(0.2) && !(distance_to_target > previous_distance_to_target && distance_to_target< distance/2) ){
		distance_traveled_R = (encoder_count_R - starting_encoder_count_R) * wheel_diameter_R * PI / CPR;
		distance_traveled_L = (encoder_count_L - starting_encoder_count_L) * wheel_diameter_L * PI / CPR;
		yaw_centering_term = ( fabs(distance_traveled_R) - fabs(distance_traveled_L) ) * 0.1 / ( MAX(fabs(speed), 100)/100.0); // 0.05

		set_target_speeds(speed*(1 - yaw_centering_term) ,-speed* (1 + yaw_centering_term));
		speed = MAX(fabs(speed)*0.95, speed_offset) * direction_R;
		previous_distance_to_target = distance_to_target;
		delay(2);
		distance_to_target = dead_wheels_spacing * fabs(target_phi - absolute_phi);
		if (wheel_state_R == EMERGENCY_BREAK){
			emergency_break();
			return 0;
		}
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}

		if(micros() - phase_two_start_time > 2000000){
			break;
		}

		send_values_to_usart(current_speed_L, current_speed_R, target_speed_L, target_speed_R);
		//send_values_to_usart(absolute_phi*100, current_phi*100, 0, 0);
	}
	stop_motors();
	reached_destination = (robot_status.status == ORIENTATIN)? 1 : 0;
	int32_t position_correction = (target_phi - absolute_phi)*dead_wheels_spacing*CPR / ( ( (wheel_diameter_R + wheel_diameter_L) / 2 )*PI) / 2.0;
	set_target_encoder_counts(encoder_count_R + position_correction, encoder_count_L - position_correction ); // the second part is there to fix any last minute fuck ups, concerning phi
	wheel_state_R = DEAD_STOP;
	wheel_state_L = DEAD_STOP;
	return 0;
}
int orientate(float orientation, int8_t is_radian, int8_t is_smooth){
	orientation = (is_radian)? orientation : deg_to_rad(orientation);
	wait_for_idle();
	if (fabs(orientation - current_phi) > deg_to_rad(0.5) ){
		float angle = orientation - current_phi;
		if (angle > PI){
			angle -= 2*PI;
		}else if (angle < -PI){
			angle += 2*PI;
		}
		previous_speed_control_time = micros();
		return rotate(angle, 1, is_smooth);
	}
	return 0;
}
int bezier_curve(float x1, float y1, float x2, float y2, float x3, float y3, float speed, int direction, int8_t is_smooth){
	float max_speed = 800.0f;
	float x0 = current_x;
	float y0 = current_y;

	float distance =  get_bezier_distance(0, x0, y0, x1, y1, x2, y2, x3, y3);
	if (distance < 400){
		breaking_acceleration = -3;
	}
	float d_1 = speed/ramping_acceleration;
	float d_2 = speed/breaking_acceleration + distance + deceleration_offset;

	if (d_2 <= d_1){ // correcting the cruising speed if it is too high to reach using the current ramp and break
		float intersection_x = (breaking_acceleration*distance + deceleration_offset)/(breaking_acceleration - ramping_acceleration);
		float intersection_speed = ramping_acceleration * intersection_x;
		speed = 0.9 * intersection_speed;
		d_1 = speed/ramping_acceleration;
		d_2 = speed/breaking_acceleration + distance + deceleration_offset;
	}

	orientate(atan2(y1-y0, x1-x0) + PI*(-direction+1)/2, 1, 0);
	if(wheel_state_L == EMERGENCY_BREAK){
		return 0;
	}
	apply_smooth_or_not(fabs(distance), is_smooth);

	acc_linearization_coef = sqrt(d_1);
	dec_linearization_coef = sqrt(distance - d_2);

	wait_for_idle();
	reset_speed_control_variables();

	direction_R = 1;
	direction_L = 1;
	cruise_speed_R = speed;
	cruise_speed_L = speed;
	float distance_to_target = distance;
	float d = 0;
	wheel_state_R = ACCELERATING;
	wheel_state_L = ACCELERATING;
	control_loop_state = SPEED;
	trajectory = BEZIER_CURVE;

	float lane_correction_term;
	float t = 0;
	float speed_R , speed_L;

	while (distance_to_target >= 1.0f && t < 1.0000f){
		d = distance - distance_to_target;

		if (wheel_state_R == ACCELERATING && d > d_1 ){
			wheel_state_R = CRUISING;
			wheel_state_L = CRUISING;
		}else if (wheel_state_R == CRUISING && d > d_2){
			wheel_state_R = CONTROLLED_BREAK;
			wheel_state_L = CONTROLLED_BREAK;
		}else if (wheel_state_R == EMERGENCY_BREAK){
			emergency_break();
			return 0;
		}
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}


		t = project_bezier(current_x, current_y, x0, y0, x1, y1, x2, y2, x3, y3);

		float radius = get_bezier_radius(t, x0, y0, x1, y1, x2, y2, x3, y3);

	    speed = direction * calculate_instant_target_speed(d, distance);

	    float signed_distance =  signed_distance_to_bezier(current_x, current_y, x0, y0, x1, y1, x2, y2, x3, y3, t);
		float phi_error = get_target_phi(t, x0, y0, x1, y1, x2, y2, x3, y3) + (PI*(1-direction) )/2 - current_phi ;
		if(phi_error > PI)
			phi_error -= 2*PI ;
		else if (phi_error < -PI)
			phi_error += 2*PI ;
		float phi_correction_term = (phi_error) * ( 3 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0) ); // 3 the first coefficient is tunable

		lane_correction_term = signed_distance * ( 0.01 / ( MAX( ( abs(target_speed_R) + abs(target_speed_L) )/2, 100.0) /500.0) ) + phi_correction_term;// this coefficient is tunable
		lane_correction_term = MIN(MAX(lane_correction_term, -0.5), 0.5);
		if (d < 0.1*d_1){ // 0.002f;
			lane_correction_term = 0;
		}

		if (fabs(radius) < 100000){
			speed_R = ( speed * (radius + direction * (dead_wheels_spacing / 2.0f)) / radius );
			speed_L = ( speed * (radius - direction * (dead_wheels_spacing / 2.0f)) / radius );
		}
		else {
			speed_R = speed ;
			speed_L = speed ;
		}
		if ((fabs(speed_R)>max_speed) || (fabs(speed_L) > max_speed)){
			speed = direction * max_speed/ MAX((radius + (dead_wheels_spacing / 2.0f)) / (radius), (radius - (dead_wheels_spacing / 2.0f)) / (radius));
			speed_R = ( speed * (radius + direction * (dead_wheels_spacing / 2.0f)) / (radius));
			speed_L = ( speed * (radius - direction * (dead_wheels_spacing / 2.0f)) / (radius));
		}

		distance_to_target = get_bezier_distance(t, x0, y0, x1, y1, x2, y2,x3 ,y3);
		if(hybrid_arrival_time(d, distance, d_1, d_2, distance_to_target) < reached_destination_time){
			reached_destination = 1;
		}
		set_target_speeds(speed_R*(1 + SGN(speed_R)* lane_correction_term) ,speed_L* (1 - SGN(speed_L)*lane_correction_term));
		//send_values_to_usart(current_speed_L, current_speed_R, target_speed_L, target_speed_R);
		send_values_to_usart(current_x, current_y, current_phi, 0);
		delay(4);
	}
	stop_motors();
	reached_destination = 1;
	float target_angle = atan2(y3-y2 , x3-x2) + PI*(-direction+1)/2;
	float diff = absolute_phi - target_angle;

	while (diff >  PI) { target_angle += 2*PI; diff -= 2*PI; }
	while (diff < -PI) { target_angle -= 2*PI; diff += 2*PI; }

	float position_correction = ( ( (target_angle - absolute_phi) * dead_wheels_spacing*CPR / ( ((wheel_diameter_L + wheel_diameter_R)/2)*PI) ) ) / 2.0f;
	set_target_encoder_counts(encoder_count_R + position_correction, encoder_count_L - position_correction); // the second part is there to fix any last minute fuck ups, concerning the phi
	wheel_state_R = DEAD_STOP;
	wheel_state_L = DEAD_STOP;
	return 0;
}
int go_to(float x, float y, float speed, int direction, int8_t is_smooth){
	wait_for_idle();
	float angle = normalize_angle( get_angle_to(x, y) + PI*(1 - direction)/2 );
	while (fabs(normalize_angle(angle - current_phi)) > deg_to_rad(1)){
		orientate(angle, 1 , 0);
		if(emergency_recieved == 1){
			return 0;
		}
		wait_for_idle();
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}

	}
	if (get_distance_to(x, y) > 2){
		move_forward_full(direction * get_distance_to(x, y), speed, x, y, is_smooth);
	}
	return 0;
}
int creep_to(float x, float y, int direction){
	wait_for_idle();
	float angle = normalize_angle( get_angle_to(x, y) + PI*(1 - direction)/2 );
	while (fabs(normalize_angle(angle - current_phi)) > deg_to_rad(1)){
		orientate(angle, 1 , 0);
		if(emergency_recieved == 1){
			return 0;
		}
		wait_for_idle();
		if (control_loop_state == SHUTDOWN ){
			return 0;
		}

	}
	if (get_distance_to(x, y) > 2){
		creep_forward(direction * get_distance_to(x, y), x, y);
	}
	return 0;
}
void prepare_go_to(float x, float y, float speed, int direction, int8_t is_smooth){
	robot_status.status = (direction == 1)? GOIN_TO : GOIN_TO_BACKWARDS;
	reached_destination = 0;
	emergency_recieved = 0;
	stopped_because_of_collision = 0;
	robot_status.arguments[0] = x;
	robot_status.arguments[1] = y;
	robot_status.arguments[2] = speed;
	robot_status.arguments[3] = is_smooth;
	target_command_x = x;
	target_command_y = y;
	target_command_phi = atan2(y - current_y, x - current_x);
}
void prepare_creep_to(float x, float y, int direction){
	robot_status.status = (direction == 1)?CREEPIN_TO : CREEPIN_TO_BACKWARDS;
	reached_destination = 0;
	emergency_recieved = 0;
	stopped_because_of_collision = 0;
	robot_status.arguments[0] = x;
	robot_status.arguments[1] = y;
	target_command_x = x;
	target_command_y = y;
	target_command_phi = atan2(y - current_y, x - current_x);
}
void prepare_bezier_curve(float x1, float y1, float x2, float y2, float x3, float y3, float speed, int direction, int8_t is_smooth){
	robot_status.status = (direction == 1)? BEZIER_CURVIN : BEZIER_CURVIN_BACKWARDS;
	reached_destination = 0;
	emergency_recieved = 0;
	stopped_because_of_collision = 0;
	robot_status.arguments[0] = x1;//x1
	robot_status.arguments[1] = y1;//y1
	robot_status.arguments[2] = x2;//x2
	robot_status.arguments[3] = y2;//y2
	robot_status.arguments[4] = x3;//x3
	robot_status.arguments[5] = y3;//y3
	robot_status.arguments[6] = speed;//speed
	robot_status.arguments[7] = is_smooth;
}
void prepare_orientate(float orientation, int8_t is_radian, int8_t is_smooth){
	robot_status.status = ORIENTATIN;
	reached_destination = 0;
	emergency_recieved = 0;
	stopped_because_of_collision = 0;
	robot_status.arguments[0] = orientation;
	robot_status.arguments[1] = is_radian;
	robot_status.arguments[2] = is_smooth;
}
void prepare_emergency_break(){
	stopped_because_of_collision = 0;
	emergency_recieved = 0;
	wheel_state_L = EMERGENCY_BREAK;
	wheel_state_R = EMERGENCY_BREAK;
}
void emergency_break(){
	emergency_recieved = 1;
	int saved_encoder_count_R = encoder_count_R;
	int saved_encoder_count_L = encoder_count_L;
	control_loop_state = ACTIVATED;
	PWM_L = 0;
	PWM_R = 0;
	if (!stopped_because_of_collision){
		while((fabs(current_speed_R) > 200) || (fabs(current_speed_L) > 200) ){
			delay(10);
		}
		int speed_sign_R = SGN(current_speed_R);
		int speed_sign_L = SGN(current_speed_L);
		position_max_response = PWM_max*0.25;
		set_target_encoder_counts(saved_encoder_count_R - speed_sign_R * 1500, saved_encoder_count_L - speed_sign_L * 1500);
		int right_stopped = 0;
		int left_stopped = 0;
		while((!right_stopped) || (!left_stopped)){
			delay(10);
			if ((SGN(current_speed_R) != speed_sign_R) || (fabs(current_speed_R) < 10)){
				right_stopped = 1;
			}
			if ((SGN(current_speed_L) != speed_sign_L) || (fabs(current_speed_L) < 10)){
				left_stopped = 1;
			}
		}
		position_max_response = default_position_max_response;
		set_target_encoder_counts(saved_encoder_count_R - SGN(target_speed_R) * 1500, saved_encoder_count_L - SGN(target_speed_L) * 1500);
	}else{
		set_target_encoder_counts(saved_encoder_count_R - SGN(target_speed_R) * 1500, saved_encoder_count_L - SGN(target_speed_L) * 1500);
		stopped_because_of_collision = 0;
	}
	wheel_state_R = DEAD_STOP;
	wheel_state_L = DEAD_STOP;
}
void prepare_reset(){
	reached_destination = 0;
	robot_status.status = RESETIN;
}
void prepare_set_position(float x, float y, float phi, float absolute_phi){
	robot_status.status = SETTIN_POSITION;
	robot_status.arguments[0] = x;
	robot_status.arguments[1] = y;
	robot_status.arguments[2] = phi;
	robot_status.arguments[3] = absolute_phi;
}
void set_target_encoder_counts(int32_t encoder__count_R, int32_t encoder__count_L){
	reset_position_control_variables();
	target_encoder_count_R = encoder__count_R;
	target_encoder_count_L = encoder__count_L;
	position_integral_R = 0;
	position_derivative_R = 0;
	position_integral_L = 0;
	position_derivative_L = 0;
	control_loop_state = POSITION;
}

int8_t is_idle(){
	int encoder_tolerance = 35;
	int pwm_tolerance = 150;
	int8_t right_wheel_idle = (fabs(target_encoder_count_R - encoder_count_R) < encoder_tolerance) && (fabs(PWM_R) < pwm_tolerance) && (fabs(previous_position_error_R) < encoder_tolerance);
	int8_t left_wheel_idle = (fabs(target_encoder_count_L - encoder_count_L) < encoder_tolerance) && (fabs(PWM_L) < pwm_tolerance) && (fabs(previous_position_error_L) < encoder_tolerance);
	return right_wheel_idle && left_wheel_idle;
}

void wait_for_idle(){
	while(control_loop_state == POSITION && !is_idle() && (fabs(current_speed_R) > 5) && (fabs(current_speed_L) > 5)){
		delay(10);
	}
	control_loop_state = ACTIVATED;
	stop_motors();
	delay(3);
}
void reset_speed_control_variables(){
	previous_speed_control_time = micros()-999;
	speed_integral_L = 0;
	speed_integral_R = 0;
	speed_derivative_L = 0;
	speed_derivative_R = 0;
	PWM_L = 0;
	PWM_R = 0;
	previous_speed_error_L = 0;
	previous_speed_error_R = 0;
	filtered_target_speed_R = 0;
	filtered_target_speed_L = 0;
}
void apply_smooth_or_not(float distance, int8_t is_smooth){
	deceleration_offset = (is_smooth)? -((MAX(MIN(distance, 800), 100)/800) * 90 - 10 ): deceleration_offset_fast;
	speed_offset = (is_smooth)? speed_offset_smooth : speed_offset_fast;
	breaking_acceleration = (is_smooth)? breaking_acceleration_smooth : breaking_acceleration_speed;
	position_max_response = default_position_max_response;
}
void reset_navigation_vars(){
	wheel_state_R = DEAD_STOP;
	wheel_state_L = DEAD_STOP;
	trajectory = STRAIGHT;
	control_loop_state = DISACTIVATED;
	ramping_acceleration = 10;
	acc_linearization_coef = 0;
	dec_linearization_coef = 0;
	breaking_acceleration = -2;
	deceleration_offset = 40;
	speed_offset = 150;
	deceleration_offset_fast = 40;
	speed_offset_fast = 150;
	deceleration_offset_smooth = 30;
	speed_offset_smooth = 80;
	rotating_speed = 650;
	filtered_target_speed_R = 0;
	filtered_target_speed_L = 0;
	speed_filter = 0.95;
	reached_destination = 1;
}
