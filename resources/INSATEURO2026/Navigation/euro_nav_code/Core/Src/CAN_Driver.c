/**
  ******************************************************************************
  * @file    CAN_Driver.c
  * @author  Mohamed Karim Ben Boubaker
  * @brief   CAN Driver for sending and receiving special ROS messages
  *
  *                     ##### Project Description #####
  *
  * This CAN Driver is specifically designed for a robotic navigation system, providing
  * functionalities to send and receive positional data and special triggers over the CAN bus.
  * The driver supports encoding and decoding messages for robotic positions
  * and angles with high precision.
  *
  * Note: Adjust the IDs, filter configurations, and other settings to fit your
  * specific project requirements.
  ******************************************************************************
  */

#include "CAN_Driver.h"

#define STOP_SIGNAL_MESSAGE			0x000
#define MASTER_ACKNOWLEDGE_MESSAGE  0x001
#define MASTER_NAV_MESSAGE			0x002
#define MASTER_RESET_MESSAGE		0x003
#define NAVIGATOR_NAV_MESSAGE		0x004

// Linear speeds (mm/s)
const float NAV_LINEAR_SLOW_SPEED = 150;
const float NAV_LINEAR_NORMAL_SPEED = 650;
const float NAV_LINEAR_FAST_SPEED = 160;
const float NAV_LINEAR_SUPERFAST_SPEED = 800;

// Angular speeds (degrees/s)
const float NAV_ANGULAR_SLOW_SPEED = 200;
const float NAV_ANGULAR_NORMAL_SPEED = 180;
const float NAV_ANGULAR_FAST_SPEED = 200;
const float NAV_ANGULAR_SUPERFAST_SPEED = 600;

// Linear accelerations (mm/s^2)
const float NAV_LINEAR_SLOW_ACC = 150;
const float NAV_LINEAR_NORMAL_ACC = 900;
const float NAV_LINEAR_FAST_ACC = 400;
const float NAV_LINEAR_SUPERFAST_ACC = 500;

// Angular accelerations (degrees/s^2)
const float NAV_ANGULAR_SLOW_ACC = 200;
const float NAV_ANGULAR_NORMAL_ACC = 200;
const float NAV_ANGULAR_FAST_ACC = 400;
const float NAV_ANGULAR_SUPERFAST_ACC = 350;

CAN_TxHeaderTypeDef CAN_TxHeader; // Stores the CAN Tx frame header
CAN_RxHeaderTypeDef CAN_RxHeader; // Stores the CAN Rx frame header
uint32_t CAN_TxMailbox;           // CAN Tx mailbox
uint8_t CAN_RX_Message[8];        // Received message buffer before decoding
uint8_t CAN_TX_Message[8];        // Message buffer to be transmitted after encoding
uint8_t CAN_messageReceivedFlag;   // Flag indicating a received message
uint8_t CAN_stopSignalFlag;        // Flag indicating a stop signal received
uint8_t CAN_master_acknowledgeFlag;// Flag indicating a master acknowledge signal received
uint8_t CAN_resetSignalFlag;       // Flag indicating a reset signal received


/*
 ===============================================================================
                       ##### CAN operation functions #####
 ===============================================================================
 */

/**
  * @brief  Send current state information over CAN.
  * @param  Nav_currentX_mm_d: X position in millimeters (double)
  * @param  Nav_currentY_mm_d: Y position in millimeters (double)
  * @param  Nav_currentAngle_deg_d: Theta angle in degrees (double)
  * @param  Nav_currentState: Current state information
  * @retval None
  */
void CAN_sendCurrentState(double Nav_currentX_mm_d, double Nav_currentY_mm_d, double Nav_currentAngle_deg_d, uint8_t Nav_currentState){
	CAN_TxHeader.DLC = 8;
	CAN_TxHeader.StdId = NAVIGATOR_NAV_MESSAGE;
	CAN_TxHeader.IDE = CAN_ID_STD;
	CAN_TxHeader.RTR = CAN_RTR_DATA;

	double Nav_currentAnglePos_deg_d = Nav_currentAngle_deg_d;
	//Check if the angle is negative, convert it into a positive angle:
	if( Nav_currentAngle_deg_d < 0 ){
		Nav_currentAnglePos_deg_d = Nav_currentAngle_deg_d + 360.0;
	}
	// Encode the message and obtain a pointer to the memory block
	uint64_t CAN_TX_Message = CAN_encodeMessage(Nav_currentX_mm_d, Nav_currentY_mm_d, Nav_currentAnglePos_deg_d, Nav_currentState);

	// Allocate memory for the dynamic message
	uint64_t* dynamic_message = malloc(sizeof(uint64_t));
	if (dynamic_message == NULL) {
		Error_Handler(); // Handle memory allocation failure
	}

	// Copy the encoded message to the dynamically allocated memory
	memcpy(dynamic_message, &CAN_TX_Message, sizeof(uint64_t));

	// Pass the pointer to the memory block to HAL_CAN_AddTxMessage
	HAL_CAN_AddTxMessage(CAN_Handler, &CAN_TxHeader, (uint8_t*)dynamic_message, &CAN_TxMailbox);

	// Free the allocated memory when done
	free(dynamic_message);
}

/**
  * @brief  Receive initial position information over CAN.
  * @param  Nav_CurrentX_mm_d: Pointer to store X position in millimeters (double)
  * @param  Nav_CurrentY_mm_d: Pointer to store Y position in millimeters (double)
  * @param  Nav_CurrentAngle_deg_d: Pointer to store Theta angle in degrees (double)
  * @retval None
  */
void CAN_receiveInitPosition(
		double* Nav_CurrentX_mm_d,
		double* Nav_CurrentY_mm_d,
		double* Nav_CurrentAngle_deg_d
		){

    uint8_t *Nav_linearVilocityChoice = 0;
    uint8_t *Nav_angularVilocityChoice = 0;
    uint8_t *Nav_linearAccelerationChoice = 0;
    uint8_t *Nav_angularAccelerationChoice = 0;
    uint8_t* Nav_isForward_b = 0;
    uint8_t* Nav_withPlatforms=0;

    CAN_decodeMessage(
    	Nav_CurrentX_mm_d,
		Nav_CurrentY_mm_d,
		Nav_CurrentAngle_deg_d,
        Nav_isForward_b,
        Nav_linearVilocityChoice,
        Nav_angularVilocityChoice,
        Nav_linearAccelerationChoice,
        Nav_angularAccelerationChoice,
		Nav_withPlatforms
    );

}

/**
  * @brief  Receive new target information over CAN.
  * @param  Nav_targetX_mm_d: Pointer to store target X position in millimeters (double)
  * @param  Nav_targetY_mm_d: Pointer to store target Y position in millimeters (double)
  * @param  Nav_targetAngle_deg_d: Pointer to store target Theta angle in degrees (double)
  * @param  Nav_isForward_b: Pointer to store forward/backward information
  * @param  Nav_MaxVelocity_d: Pointer to store maximum linear velocity (mm/s)
  * @param  Nav_MaxAngularVelocity_d: Pointer to store maximum angular velocity (degrees/s)
  * @param  Nav_Acc_d: Pointer to store linear acceleration (mm/s^2)
  * @param  Nav_AngularAcc_d: Pointer to store angular acceleration (degrees/s^2)
  * @retval None
  */
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
) {
    uint8_t Nav_linearVilocityChoice;
    uint8_t Nav_angularVilocityChoice;
    uint8_t Nav_linearAccelerationChoice;
    uint8_t Nav_angularAccelerationChoice;

    CAN_decodeMessage(
        Nav_targetX_mm_d,
        Nav_targetY_mm_d,
        Nav_targetAngle_deg_d,
        Nav_isForward_b,
        &Nav_linearVilocityChoice,
        &Nav_angularVilocityChoice,
        &Nav_linearAccelerationChoice,
        &Nav_angularAccelerationChoice,
		Nav_withPlatforms
    );


    // Map velocity and acceleration choices to corresponding values
    switch (Nav_linearVilocityChoice) {
        case Nav_NavigatorSlowSpeed_en:
            *Nav_MaxVelocity_d = NAV_LINEAR_SLOW_SPEED;
            break;
        case Nav_NavigatorNormalSpeed_en:
            *Nav_MaxVelocity_d = NAV_LINEAR_NORMAL_SPEED;
            break;
        case Nav_NavigatorFastSpeed_en:
            *Nav_MaxVelocity_d = NAV_LINEAR_FAST_SPEED;
            break;
        case Nav_NavigatorSuperFastSpeed_en:
            *Nav_MaxVelocity_d = NAV_LINEAR_SUPERFAST_SPEED;
            break;
        default:
            *Nav_MaxVelocity_d = NAV_LINEAR_SLOW_SPEED;
            break;
    }

    switch (Nav_angularVilocityChoice) {
        case Nav_NavigatorSlowSpeed_en:
            *Nav_MaxAngularVelocity_d = NAV_ANGULAR_SLOW_SPEED;
            break;
        case Nav_NavigatorNormalSpeed_en:
            *Nav_MaxAngularVelocity_d = NAV_ANGULAR_NORMAL_SPEED;
            break;
        case Nav_NavigatorFastSpeed_en:
            *Nav_MaxAngularVelocity_d = NAV_ANGULAR_FAST_SPEED;
            break;
        case Nav_NavigatorSuperFastSpeed_en:
            *Nav_MaxAngularVelocity_d = NAV_ANGULAR_SUPERFAST_SPEED;
            break;
        default:
            *Nav_MaxAngularVelocity_d = NAV_ANGULAR_SLOW_SPEED;
            break;
    }

    switch (Nav_linearAccelerationChoice) {
        case Nav_NavigatorSlowSpeed_en:
            *Nav_Acc_d = NAV_LINEAR_SLOW_ACC;
            break;
        case Nav_NavigatorNormalSpeed_en:
            *Nav_Acc_d = NAV_LINEAR_NORMAL_ACC;
            break;
        case Nav_NavigatorFastSpeed_en:
            *Nav_Acc_d = NAV_LINEAR_FAST_ACC;
            break;
        case Nav_NavigatorSuperFastSpeed_en:
            *Nav_Acc_d = NAV_LINEAR_SUPERFAST_ACC;
            break;
        default:
            *Nav_Acc_d = NAV_LINEAR_SLOW_ACC;
            break;
    }

    switch (Nav_angularAccelerationChoice) {
        case Nav_NavigatorSlowSpeed_en:
            *Nav_AngularAcc_d = NAV_ANGULAR_SLOW_ACC;
            break;
        case Nav_NavigatorNormalSpeed_en:
            *Nav_AngularAcc_d = NAV_ANGULAR_NORMAL_ACC;
            break;
        case Nav_NavigatorFastSpeed_en:
            *Nav_AngularAcc_d = NAV_ANGULAR_FAST_ACC;
            break;
        case Nav_NavigatorSuperFastSpeed_en:
            *Nav_AngularAcc_d = NAV_ANGULAR_SUPERFAST_ACC;
            break;
        default:
            *Nav_AngularAcc_d = NAV_ANGULAR_SLOW_ACC;
            break;
    }
}

/*
 ===============================================================================
                       ##### CAN utility functions #####
 ===============================================================================
 */

/**
  * @brief  Decode a CAN message into positional data.
  *
  * This function extracts positional information from a 64-bit CAN message
  * and decodes it into variables representing X and Y positions in
  * millimeters, and Theta angle in degrees.
  *
  * @param  Nav_targetX_mm_d: Pointer to store decoded X position in millimeters.
  * @param  Nav_targetY_mm_d: Pointer to store decoded Y position in millimeters.
  * @param  Nav_targetAngle_deg_d: Pointer to store decoded Theta angle in degrees.
  * @param  Nav_isForward_b: Pointer to store forward/backward information.
  * @param  Nav_linearVilocityChoice: Pointer to store linear velocity choice.
  * @param  Nav_angularVilocityChoice: Pointer to store angular velocity choice.
  * @param  Nav_linearAccelerationChoice: Pointer to store linear acceleration choice.
  * @param  Nav_angularAccelerationChoice: Pointer to store angular acceleration choice.
  * @retval None
  */

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
		)
{
    // Extract the 64-bit integer from the received message
    uint64_t combined_value;


    memcpy(&combined_value, CAN_RX_Message, sizeof(uint64_t));

    // Reverse byte order (for little-endian systems)
    combined_value = __builtin_bswap64(combined_value);

    // Decode the combined value into the original variables
    *Nav_targetX_mm_d = (double)((int64_t)((combined_value >> 45) & 0x7FFFF)) * 0.01;
    *Nav_targetY_mm_d = (double)((int64_t)((combined_value >> 27) & 0x3FFFF)) * 0.01;
    *Nav_targetAngle_deg_d = (double)((int64_t)((combined_value >> 11) & 0xFFFF)) * 0.01;
    *Nav_isForward_b = (uint8_t)((combined_value >> 10) & 0x1);
    *Nav_linearVilocityChoice = (uint8_t)((combined_value >> 8) & 0x3);
    *Nav_angularVilocityChoice = (uint8_t)((combined_value >> 6) & 0x3);
    *Nav_linearAccelerationChoice = (uint8_t)((combined_value >> 4) & 0x3);
    *Nav_angularAccelerationChoice = (uint8_t)((combined_value >> 2) & 0x3);
    *Nav_withPlatforms=(uint8_t)((combined_value >> 1) & 0x01);
}

void CAN_filterConfig() {
    CAN_FilterTypeDef canfilterconfig;

    canfilterconfig.FilterActivation = CAN_FILTER_ENABLE;
    canfilterconfig.FilterBank = 0;  // which filter bank to use from the assigned ones
    canfilterconfig.FilterFIFOAssignment = CAN_FILTER_FIFO0;
    canfilterconfig.FilterIdHigh = 0x0000;
    canfilterconfig.FilterIdLow = 0x0000;

    // Set the mask filter values to reject only ID 0x003
    canfilterconfig.FilterMaskIdHigh = 0x000;  // Set the mask for ID high
    canfilterconfig.FilterMaskIdLow = 0x0000;        // Set the mask for ID low

    canfilterconfig.FilterMode = CAN_FILTERMODE_IDMASK;  // Use ID mask mode
    canfilterconfig.FilterScale = CAN_FILTERSCALE_32BIT;

    if (HAL_CAN_ConfigFilter(CAN_Handler, &canfilterconfig) != HAL_OK) {
        Error_Handler();
    }
}


/**
  * @brief  Encode positional data into a CAN message.
  *
  * This function encodes X and Y positions in millimeters, and Theta angle
  * in degrees, into a 64-bit CAN message with specific precision.
  *
  * @param  Nav_currentX: X position in millimeters to be encoded.
  * @param  Nav_currentY: Y position in millimeters to be encoded.
  * @param  Nav_currentAngle: Theta angle in degrees to be encoded.
  * @param  Nav_currentState: Current state information to be encoded.
  * @retval uint64_t: The 64-bit encoded CAN message.
  */
uint64_t CAN_encodeMessage(double Nav_currentX, double Nav_currentY, double Nav_currentAngle, uint8_t Nav_currentState) {
    // Encode float values with precision 0.01
    uint64_t Nav_currentX_bits = (uint64_t)(Nav_currentX * 100.0) & 0x7FFFF;      // 19 bits
    uint64_t Nav_currentY_bits = (uint64_t)(Nav_currentY * 100.0) & 0x3FFFF;      // 18 bits
    uint64_t Nav_currentAngle_bits = (uint64_t)(Nav_currentAngle * 100.0) & 0xFFFF;    // 16 bits

    // Encode int8_t value
    uint64_t Nav_currentState_bits = (uint64_t)(Nav_currentState) & 0xFF;       // 8 bits

    // Combine the segmented values into a 64-bit integer
    uint64_t combined_value = (Nav_currentX_bits << 45) | (Nav_currentY_bits << 27) | (Nav_currentAngle_bits << 11) | Nav_currentState_bits << 3;

    return combined_value;
}


/**
  * @brief  Check if a stop signal is received.
  * @retval 1 if stop signal is received, otherwise 0.
  */
uint8_t CAN_isStopSignal_b(void){
    // Check the received arbitration ID
    if (CAN_RxHeader.StdId == STOP_SIGNAL_MESSAGE) {
        return 1;
    }

    return 0;
}

/**
  * @brief  Check if an acknowledge signal is received.
  * @retval 1 if acknowledge signal is received, otherwise 0.
  */
uint8_t CAN_isAcknowledgeSignal_b(void){
    // Check the received arbitration ID
    if (CAN_RxHeader.StdId == MASTER_ACKNOWLEDGE_MESSAGE) {
        return 1;
    }

    return 0;
}

/**
  * @brief  Check if a reset signal is received.
  * @retval 1 if reset signal is received, otherwise 0.
  */
uint8_t CAN_isResetSignal_b(void){
    // Check the received arbitration ID
    if (CAN_RxHeader.StdId == MASTER_RESET_MESSAGE) {
        return 1;
    }

    return 0;
}




