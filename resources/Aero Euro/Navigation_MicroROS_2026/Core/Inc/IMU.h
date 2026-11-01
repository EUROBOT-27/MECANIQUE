/*
 * IMU.h
 *
 *  Created on: Nov 22, 2025
 *      Author: monji
 */

#ifndef INC_IMU_H_
#define INC_IMU_H_

#include "stm32f4xx_hal.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define BNO055_I2C_ADDR_LO   (0x28 << 1)
#define BNO055_I2C_ADDR_HI   (0x29 << 1)

#define BNO055_CHIP_ID       0x00
#define BNO055_OPR_MODE      0x3D
#define BNO055_PWR_MODE      0x3E
#define BNO055_SYS_TRIGGER   0x3F
#define BNO055_UNIT_SEL      0x3B
#define BNO055_PAGE_ID       0x07

// operation modes
#define OPERATION_MODE_CONFIG     0x00

// Sensor-only modes
#define OPERATION_MODE_ACCONLY    0x01
#define OPERATION_MODE_MAGONLY    0x02
#define OPERATION_MODE_GYRONLY    0x03
#define OPERATION_MODE_ACCMAG     0x04
#define OPERATION_MODE_ACCGYRO    0x05
#define OPERATION_MODE_MAGGYRO    0x06
#define OPERATION_MODE_AMG        0x07   // Accel + Mag + Gyro (NO fusion)

// Fusion modes
#define OPERATION_MODE_IMU        0x08   // Accel + Gyro fusion
#define OPERATION_MODE_COMPASS    0x09   // Accel + Mag fusion
#define OPERATION_MODE_M4G        0x0A   // Mag + Accel fusion (no gyro)
#define OPERATION_MODE_NDOF_FMC_OFF 0x0B // NDOF with FastMagComp OFF
#define OPERATION_MODE_NDOF       0x0C   // FULL FUSION MODE

typedef struct {
    float x;
    float y;
    float z;
} bno055_vector_t;

void bno055_init(I2C_HandleTypeDef *hi2c, uint8_t address, int8_t mode);
uint8_t bno055_read8(uint8_t reg);
void bno055_write8(uint8_t reg, uint8_t value);

bno055_vector_t bno055_readGyro(void);
bno055_vector_t bno055_readAccel(void);
bno055_vector_t bno055_readMag(void);
bno055_vector_t bno055_readEuler(void);

#endif /* INC_IMU_H_ */
