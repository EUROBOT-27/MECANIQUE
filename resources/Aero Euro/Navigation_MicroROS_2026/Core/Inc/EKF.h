/*
 * EKF.h
 *
 *  Created on: Nov 23, 2025
 *      Author: monji
 */

#ifndef CORE_INC_EKF_H_
#define CORE_INC_EKF_H_

#include "Odometry.h"
#include "IMU.h"

void set_IMU_I2C_channel(I2C_HandleTypeDef *hi2c);
void update_position_EKF(int8_t skip);
void set_position_IMU(float current__x, float current__y, float current__phi, float absolute__phi);
void reset_position_IMU();
void update_current_yaw();
void update_current_z_angular_velocity();


#endif /* CORE_INC_EKF_H_ */
