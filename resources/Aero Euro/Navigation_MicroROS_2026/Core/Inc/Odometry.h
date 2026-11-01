/*
 * odometry.h
 *
 *  Created on: Aug 27, 2025
 */

#ifndef INC_ODOMETRY_H_
#define INC_ODOMETRY_H_

#include <math.h>
#include "Motors.h"

#define SQR(x) ((x) * (x))
#define SGN(x) ( ( (x)<0 ) ? -1 : 1)
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

extern float driven_wheels_spacing;
extern float dead_wheels_spacing;
extern float current_x;
extern float current_y;
extern float current_phi; // angle between x axis and the robot's center axis, in radians
extern float absolute_phi; // phi without modulo 2PI
extern float inner_plane_x;
extern float inner_plane_y;
extern float inner_plane_phi;
extern float inner_plane_absolute_phi;
extern int8_t skip_position_update;
extern int8_t block_get_position;
extern int8_t is_inside_inner_plane;
extern float imu_yaw_offset;
extern float current_imu_yaw;
extern float absolute_imu_yaw;
extern float current_imu_gyro_z;
extern int8_t imu_yaw_new;
extern int8_t imu_gyro_z_new;
extern float front_aruco_relative_x;
extern float front_aruco_relative_y;
extern float back_aruco_relative_x;
extern float back_aruco_relative_y;


void setup_wheels_spacing(float driven__wheels_spacing, float dead__wheels_spacing);
void setup_aruco_positions(float front_x, float front_y, float back_x, float back_y);
void update_position(int8_t skip);
void reset_position();
void set_position(float current__x, float current__y, float current__phi, float absolute__phi);
float get_distance_to(float x, float y);
float get_arc_distance_to(float target_point_x, float target_point_y, float center_point_x, float center_point_y, float radius);
float get_angle_to(float x, float y);
float get_bezier_distance(float t ,float x0, float y0,float x1, float y1,float x2 , float y2 ,float x3, float y3);
void bezier(float t, float x0, float y0, float x1, float y1, float x2, float y2, float x3, float y3, float *x, float *y);
void bezier_derivative(float t, float x0, float y0, float x1, float y1, float x2, float y2, float x3, float y3, float *x, float *y);
double signed_distance_to_bezier(double px, double py, double x0, double y0, double x1, double y1, double x2, double y2, double x3, double y3, double t);
float get_bezier_radius(float t,float x0, float y0,float x1, float y1, float x2, float y2,float x3, float y3);
float project_bezier(float px, float py, float x0,float y0, float x1,float y1, float x2,float y2, float x3,float y3);
float get_target_phi(float t,float x0, float y0,float x1, float y1,float x2, float y2,float x3, float y3);
float ticks_to_distance(int32_t ticks, float wheel_diameter);
int32_t distance_to_ticks(float distance, float wheel_diameter);
float rad_to_deg(float radian);
float deg_to_rad(float degrees);
void set_new_plane();
void revert_to_original_plane();
void convert_point_coordinates_to_inner(float x, float y, float* result);
float convert_phi_to_inner(float phi);
float convert_phi_to_original(float phi);
float normalize_angle(float angle);
void get_position(float* position);
void reset_odometry_vars();

#endif /* INC_ODOMETRY_H_ */
