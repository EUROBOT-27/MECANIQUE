/*
 * EKF.c
 *
 *  Created on: Nov 23, 2025
 *      Author: monji
 */


#include "EKF.h"

void set_IMU_I2C_channel(I2C_HandleTypeDef *hi2c){
	bno055_init(hi2c, BNO055_I2C_ADDR_LO, OPERATION_MODE_IMU);
	uint8_t id = bno055_read8(BNO055_CHIP_ID);
//	while (id != 0xA0) {
//		bno055_init(hi2c, BNO055_I2C_ADDR_LO, OPERATION_MODE_MAGGYRO);
//	}
}

void update_position_EKF(int8_t skip){
	if (imu_yaw_new){
		imu_yaw_new = 0;
//		float supposed_encoder_absolute_phi = ( ticks_to_distance(encoder_count_R, wheel_diameter_R) - ticks_to_distance(encoder_count_L, wheel_diameter_L) )/dead_wheels_spacing;
////		if (fabs(absolute_imu_yaw) > 0.1 && fabs(supposed_encoder_absolute_phi) > 0.1){
////			dead_wheels_spacing = fabs(dead_wheels_spacing * (supposed_encoder_absolute_phi/absolute_imu_yaw));
////		}
//		if (fabs(absolute_imu_yaw) > 0.1 && ( ticks_to_distance(encoder_count_R, wheel_diameter_R) - ticks_to_distance(encoder_count_L, wheel_diameter_L) ) > 5 ){
//			dead_wheels_spacing = fabs( ( ticks_to_distance(encoder_count_R, wheel_diameter_R) - ticks_to_distance(encoder_count_L, wheel_diameter_L) ) / absolute_imu_yaw);
//		}
	}
	update_position(skip);
}

void set_position_IMU(float current__x, float current__y, float current__phi, float absolute__phi){
	set_position(current__x, current__y, current__phi, absolute__phi);
	update_current_yaw();
	imu_yaw_offset = normalize_angle(imu_yaw_offset + deg_to_rad(current__phi) - current_imu_yaw);
	HAL_Delay(10);
	for(int i=0; i<100; i++){ // kinda lezem hedhi bech l IMU ma yetmou3e9ch (ma44irha keen ydhayya3 0.1rad mellowel)
		update_current_yaw();
		update_current_z_angular_velocity();
		HAL_Delay(10);
	}
}

void reset_position_IMU(){
	update_current_yaw();
	imu_yaw_offset = -current_imu_yaw;
	set_position(0, 0, 0, 0);
}

void update_current_yaw(){
	bno055_vector_t v = bno055_readEuler();
	float yaw_rad = v.x * PI / 180.0;
	if (yaw_rad > PI) yaw_rad -= 2*PI;
	yaw_rad *= -1;

	float new_imu_yaw = normalize_angle(yaw_rad + imu_yaw_offset);
	float d_yaw = new_imu_yaw - current_imu_yaw;
	current_imu_yaw = new_imu_yaw;

	if (d_yaw>PI){
		d_yaw -= 2*PI;
	}
	else if (d_yaw < -2.5){
		d_yaw += 2*PI;
	}
	absolute_imu_yaw += d_yaw;
	imu_yaw_new = 1;
}
void update_current_z_angular_velocity(){ // returns in rad/s
	bno055_vector_t v = bno055_readGyro();
	current_imu_gyro_z = v.z;
	imu_gyro_z_new = 1;
}
