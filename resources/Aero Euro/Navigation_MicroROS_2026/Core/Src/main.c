/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdbool.h>
#include "../Inc/micro_ros.h"
#include "Motors.h"
#include "Odometry.h"
#include "navigation.h"
#include "EKF.h"

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

bool cubemx_transport_open(struct uxrCustomTransport * transport);
bool cubemx_transport_close(struct uxrCustomTransport * transport);
size_t cubemx_transport_write(struct uxrCustomTransport* transport, const uint8_t * buf, size_t len, uint8_t * err);
size_t cubemx_transport_read(struct uxrCustomTransport* transport, uint8_t* buf, size_t len, int timeout, uint8_t* err);

void * microros_allocate(size_t size, void * state);
void microros_deallocate(void * pointer, void * state);
void * microros_reallocate(void * pointer, size_t size, void * state);
void * microros_zero_allocate(size_t number_of_elements, size_t size_of_element, void * state);

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

//  Service Callback
int8_t first_forward_recieved = 0;
// speed control parameters
float kpS_R = 15; // 5
float kdS_R = 0; // at this frequency, derivative is too noisy to be utilized
float kiS_R = 200; //

float kpS_L = 15; // 15
float kdS_L = 0; //
float kiS_L = 200; // 90

int timer_flag = 0;


// position control parameters
float kpP_R = 15;
float kdP_R = 1.4;
float kiP_R = 75;

float kpP_L = 15;
float kdP_L = 1.4;
float kiP_L = 75;

float error = 0;
float dt = 0.0001;

int step = 0;

int accepted_new_go_to = 0;
int command_count = 0;
int fail_safe_activated = 1;
int fail_safe_counter = 0;

int8_t in_tornado = 0;
int32_t tornado_start_time = 0;


float last_set_position_x = 0;
float last_set_position_y = 0;
float last_set_position_phi = 0;

int8_t tornado_condition(){
	 return (
			 ((fabs(current_speed_R) + fabs(current_speed_L)) > 900)
			 &&
			 (SGN(current_speed_R) != SGN(current_speed_L))
			);
}

void reset_everything(){
	reset_motors_vars();
	reset_odometry_vars();
	reset_navigation_vars();
	current_speed_R = 0;
	current_speed_L = 0;
	previous_speed_R = 0;
	previous_speed_L = 0;
	target_speed_R = 0;
	target_speed_L = 0;
	current_acceleration_R = 0;
	current_acceleration_L = 0;
	previous_speed_calculation_time = 0;

	speed_integral_R = 0;
	speed_derivative_R = 0;
	previous_speed_error_R = 0;
	speed_integral_L = 0;
	speed_derivative_L = 0;
	previous_speed_error_L = 0;
	current_x = 0;
	current_y = 0;
	current_phi = 0;
	absolute_phi = 0;

	PWM_R = 0;
	PWM_L = 0;
	current_imu_yaw = 0;
	current_imu_gyro_z = 0;
	absolute_imu_yaw = 0;

	control_loop_state = DISACTIVATED;
	reset_speed_control_variables();
	reset_position_control_variables();
	reset_position();

	set_position(last_set_position_x, last_set_position_y, last_set_position_phi, last_set_position_phi);

	communication_state = PC;

	robot_status.status = IDLE;
	set_target_speeds(0, 0);
	control_loop_state = SPEED;

	communication_state = RASPBERRY;
}
void shutdown(){
	control_loop_state = SHUTDOWN;
	delay(1);
	control_loop_state = SHUTDOWN;
	delay(1); // 3awedt'ha marrtin 5ater faza ta3 synchro
	PWM_R = 0;
	PWM_L = 0;
}

void service_callback(const void *request_msg, void *response_msg) {
    service__srv__NaviStm_Request *req_in = (service__srv__NaviStm_Request *)request_msg;
    service__srv__NaviStm_Response *res_out = (service__srv__NaviStm_Response *)response_msg;
    communication_state = RASPBERRY;

    switch ((int)req_in->arg1) {
									 case 4: //orientate
										prepare_orientate(req_in->arg2, req_in->arg3, req_in->arg4);
										res_out->result = true;  // orientation, is_radian
										break;

									 case 5: // go to
										prepare_go_to(req_in->arg2, req_in->arg3, req_in->arg4, 1, req_in->arg5);
										res_out->result = true;  // x, y, speed
										break;

									 case 6: // Reset
										prepare_reset();
										res_out->result = true;
										break;

									 case 10: // emergency break
										prepare_emergency_break();
										res_out->result = true;
										break;

									 case 11: // is the robot idle
										res_out->result = (robot_status.status == IDLE)? true: false;
										break;

									 case 12: // go to backwards
										prepare_go_to(req_in->arg2, req_in->arg3, req_in->arg4, -1, req_in->arg5);
										res_out->result = true;  // x, y, speed
										break;
									 case 13: // bezier curve
										prepare_bezier_curve(req_in->arg2, req_in->arg3, req_in->arg4, req_in->arg5, req_in->arg6, req_in->arg7, req_in->arg8, 1, req_in->arg9);
										res_out->result = true;  // x, y, speed
										break;
									 case 14: // bezier curve backwards
										prepare_bezier_curve(req_in->arg2, req_in->arg3, req_in->arg4, req_in->arg5, req_in->arg6, req_in->arg7, req_in->arg8, -1, req_in->arg9);
										res_out->result = true;  // x, y, speed
										break;
									 case 15: // set_position
										last_set_position_x = req_in->arg2;
										last_set_position_y = req_in->arg3;
										last_set_position_phi = req_in->arg4;
										prepare_set_position(req_in->arg2, req_in->arg3, req_in->arg4, req_in->arg4);
										res_out->result = true;  // x, y, speed
										break;
									 case 16:
										 res_out->result = (
												 	 	 		 (robot_status.status == IDLE)
															 	 ||
															 	 reached_destination
															)? true: false;
										 break;
									 case 17://fix x and y
										 __disable_irq();
										 control_loop_state = DISACTIVATED;
										 float front1_back2 = req_in->arg2; // should be one if front aruco detected, 2 if back is detected, 0 if none,
										 float front_aruco_x = req_in->arg3;
										 float front_aruco_y = req_in->arg4;
										 float back_aruco_x = req_in->arg3;
										 float back_aruco_y = req_in->arg4;
										 float backup_x = req_in->arg3;
										 float backup_y = req_in->arg4;
										 float robot_phi = current_phi;
										 //reset_everything();
										 command_count = 0;
										 robot_status.status = IDLE;
										 if (!front1_back2){
											reset_position();
											set_position(backup_x, backup_y, rad_to_deg(robot_phi), rad_to_deg(robot_phi));
										 }else if (front1_back2 == 1){
											 float x = front_aruco_x + front_aruco_relative_y*sin(robot_phi) - front_aruco_relative_x*cos(robot_phi);
											 float y = front_aruco_y - front_aruco_relative_x*sin(robot_phi) - front_aruco_relative_y*cos(robot_phi);
											 set_position(x, y, rad_to_deg(robot_phi), rad_to_deg(robot_phi));
										 }else{
											 float x = back_aruco_x + back_aruco_relative_y*sin(robot_phi) - back_aruco_relative_x*cos(robot_phi);
											 float y = back_aruco_y - back_aruco_relative_x*sin(robot_phi) - back_aruco_relative_y*cos(robot_phi);
											 set_position(x, y, rad_to_deg(robot_phi), rad_to_deg(robot_phi));
										 }
										 control_loop_state = ACTIVATED;
										 __enable_irq();
										 res_out->result = true;
										 break;
									 case 18:
										 res_out->result = stopped_because_of_collision? true: false;
										 break;
									 case 19: // shutdown
										 shutdown();
										 res_out->result = true;
										 break;
									 case 20: // creep to
										 prepare_creep_to(req_in->arg2, req_in->arg3, 1);
										 res_out->result = true;  // x, y, speed
										 break;
									 case 21: // creep to backwards
										 prepare_creep_to(req_in->arg2, req_in->arg3, -1);
										 res_out->result = true;  // x, y, speed
										 break;
									 default:
										  res_out->result = false;
										  break;

    			    	  		}
}
geometry_msgs__msg__Vector3 pose_msg;
void publish_odom(void){
	float pos[3];
	get_position(pos);
	pose_msg.x = pos[0]/1000.0;
	pose_msg.y = pos[1]/1000.0;
	pose_msg.z = pos[2];

	rcl_publish(&pose_publisher, &pose_msg, NULL);
}
std_msgs__msg__String debug_msg;
void publish_debug(const char * text)
{
    rosidl_runtime_c__String__assign(&debug_msg.data, text);
    rcl_publish(&debugger_publisher, &debug_msg, NULL);
}



/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim4;
TIM_HandleTypeDef htim5;
TIM_HandleTypeDef htim7;
TIM_HandleTypeDef htim14;

UART_HandleTypeDef huart2;
DMA_HandleTypeDef hdma_usart2_rx;
DMA_HandleTypeDef hdma_usart2_tx;

/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .stack_size = 2050 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for executor */
osThreadId_t executorHandle;
const osThreadAttr_t executor_attributes = {
  .name = "executor",
  .stack_size = 750 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for IMU_update_task */
osThreadId_t IMU_update_taskHandle;
const osThreadAttr_t IMU_update_task_attributes = {
  .name = "IMU_update_task",
  .stack_size = 400 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM4_Init(void);
static void MX_TIM7_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_TIM14_Init(void);
static void MX_TIM5_Init(void);
static void MX_I2C1_Init(void);
void StartDefaultTask(void *argument);
void executor_function(void *argument);
void IMU_update_function(void *argument);

/* USER CODE BEGIN PFP */


/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */


  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_TIM1_Init();
  MX_TIM3_Init();
  MX_TIM4_Init();
  MX_TIM7_Init();
  MX_USART2_UART_Init();
  MX_TIM14_Init();
  MX_TIM5_Init();
  MX_I2C1_Init();
  /* USER CODE BEGIN 2 */
  // setting up timers and stuff
  // TODO: configure correct parameters
  setup_motor_channels(&htim1, TIM_CHANNEL_4, TIM_CHANNEL_3, TIM_CHANNEL_2, TIM_CHANNEL_1);
  setup_encoder_timers(&htim3, &htim4, 14400);
  //setup_wheel_diameters(79.67706788, 80.9302886);
  setup_wheel_diameters(64.408532262731481481481481481482, 64.34127197265625);

  setup_wheels_spacing(188.5, 284.65674156305276595831931407686);

  setup_aruco_positions(61, 96.85, -76.9, -97.35);
  //setup_wheels_spacing(188.5, 342.5);
  setup_PWM_min_max(4499, 805, 835, -805, -835);

  // starting timers
  HAL_TIM_Base_Start_IT(&htim7); // interrupt timer

  TIM5->CNT = 0;
  HAL_TIM_Base_Start(&htim5); // main clock timer

  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1); // PWM timer
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4);

  HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL); // encoder timer
  HAL_TIM_Encoder_Start(&htim4, TIM_CHANNEL_ALL); // encoder timer

  //set_IMU_I2C_channel(&hi2c1); // set I²C channel of the IMU, abandoned

  // hedhom lezem ykounou hnee, tes2elch 3leech
  current_speed_R = 0;
  current_speed_L = 0;
  previous_speed_R = 0;
  previous_speed_L = 0;
  target_speed_R = 0;
  target_speed_L = 0;
  current_acceleration_R = 0;
  current_acceleration_L = 0;
  previous_speed_calculation_time = 0;

  speed_integral_R = 0;
  speed_derivative_R = 0;
  previous_speed_error_R = 0;
  speed_integral_L = 0;
  speed_derivative_L = 0;
  previous_speed_error_L = 0;
  current_x = 0;
  current_y = 0;
  current_phi = 0;
  absolute_phi = 0;

  PWM_R = 0;
  PWM_L = 0;
  current_imu_yaw = 0;
  current_imu_gyro_z = 0;
  absolute_imu_yaw = 0;
  communication_state = PC;

  reset_position();
  set_position(0, 0, 0, 0);
  control_loop_state = DISACTIVATED;

  robot_status.status = IDLE;
  set_target_speeds(0, 0);
  control_loop_state = SPEED;

//  rotating_speed = 300;
//  rotate(3600, 0, 0);
//
//  set_target_encoder_counts(0, 0);
//  while(1){
//	  send_values_to_usart(encoder_count_R, encoder_count_L, 0, 0);
//	  delay(10);
//  }
  /* USER CODE END 2 */

  /* Init scheduler */
  osKernelInitialize();

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of defaultTask */
  defaultTaskHandle = osThreadNew(StartDefaultTask, NULL, &defaultTask_attributes);

  /* creation of executor */
  executorHandle = osThreadNew(executor_function, NULL, &executor_attributes);

  /* creation of IMU_update_task */
  IMU_update_taskHandle = osThreadNew(IMU_update_function, NULL, &IMU_update_task_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

  /* Start scheduler */
  osKernelStart();

  /* We should never get here as control is now taken by the scheduler */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 2;
  RCC_OscInitStruct.PLL.PLLR = 2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 400000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 0;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 4500;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_3) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_4) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 65535;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 0;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 0;
  if (HAL_TIM_Encoder_Init(&htim3, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief TIM4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM4_Init(void)
{

  /* USER CODE BEGIN TIM4_Init 0 */

  /* USER CODE END TIM4_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM4_Init 1 */

  /* USER CODE END TIM4_Init 1 */
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 0;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 65535;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 0;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 0;
  if (HAL_TIM_Encoder_Init(&htim4, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM4_Init 2 */

  /* USER CODE END TIM4_Init 2 */

}

/**
  * @brief TIM5 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM5_Init(void)
{

  /* USER CODE BEGIN TIM5_Init 0 */

  /* USER CODE END TIM5_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM5_Init 1 */

  /* USER CODE END TIM5_Init 1 */
  htim5.Instance = TIM5;
  htim5.Init.Prescaler = 83;
  htim5.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim5.Init.Period = 4294967295;
  htim5.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim5.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim5) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim5, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim5, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM5_Init 2 */

  /* USER CODE END TIM5_Init 2 */

}

/**
  * @brief TIM7 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM7_Init(void)
{

  /* USER CODE BEGIN TIM7_Init 0 */

  /* USER CODE END TIM7_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM7_Init 1 */
  __HAL_RCC_TIM7_CLK_ENABLE();
  /* USER CODE END TIM7_Init 1 */
  htim7.Instance = TIM7;
  htim7.Init.Prescaler = 83;
  htim7.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim7.Init.Period = 999;
  htim7.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim7) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim7, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM7_Init 2 */

  /* USER CODE END TIM7_Init 2 */

}

/**
  * @brief TIM14 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM14_Init(void)
{

  /* USER CODE BEGIN TIM14_Init 0 */

  /* USER CODE END TIM14_Init 0 */

  /* USER CODE BEGIN TIM14_Init 1 */

  /* USER CODE END TIM14_Init 1 */
  htim14.Instance = TIM14;
  htim14.Init.Prescaler = 0;
  htim14.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim14.Init.Period = 840-1;
  htim14.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim14.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim14) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM14_Init 2 */

  /* USER CODE END TIM14_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMA1_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA1_Stream5_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Stream5_IRQn, 5, 0);
  HAL_NVIC_EnableIRQ(DMA1_Stream5_IRQn);
  /* DMA1_Stream6_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Stream6_IRQn, 5, 0);
  HAL_NVIC_EnableIRQ(DMA1_Stream6_IRQn);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(trig_GPIO_Port, trig_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : PC13 echo_Pin */
  GPIO_InitStruct.Pin = GPIO_PIN_13|echo_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : trig_Pin */
  GPIO_InitStruct.Pin = trig_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(trig_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : LD2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
/* USER CODE END 4 */

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */

void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN 5 */

  SystemState system_state = AGENT_WAIT;
  rcl_ret_t ret;

  // Set Micro-ROS transport ONCE
  rmw_uros_set_custom_transport(
      true,
      (void *)&huart2,
      cubemx_transport_open,
      cubemx_transport_close,
      cubemx_transport_write,
      cubemx_transport_read
  );

  allocator = rcl_get_default_allocator();

  for (;;)
  {
    switch (system_state)
    {
      case AGENT_WAIT:
        // Ping agent every 500 ms
        execute_every_n_ms(
          500,
          system_state =
            (rmw_uros_ping_agent(100, 1) == RMW_RET_OK)
              ? AGENT_AVAILABLE
              : AGENT_WAIT
        );
        break;

      case AGENT_AVAILABLE:
        if (create_rcl_entities())
        {
          system_state = AGENT_CONNECTED;
          std_msgs__msg__String__init(&debug_msg);
        }
        else
        {
          system_state = AGENT_WAIT;
        }

        break;

      case AGENT_CONNECTED:
        // Check agent health every 100 ms
    	  if (rmw_uros_ping_agent(100, 1) != RMW_RET_OK)
    	    {
    	      system_state = AGENT_DISCONNECTED;
    	      break;
    	    }
		  ret = rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10));

		  if (ret == RCL_RET_OK)
		  {
			publish_odom();
			char buf[20];
			snprintf(buf, sizeof(buf), "%d", (int)(robot_status.status + control_loop_state*100 + (int)rad_to_deg(current_phi)*10000));
			publish_debug(buf);
		  }
		  break;
      case AGENT_DISCONNECTED:
              destroy_rcl_entities();     // clean old session
              system_state = AGENT_WAIT; // start pinging again
              break;


      default:
        system_state = AGENT_WAIT;
        break;
    }

    osDelay(1);
  }

  /* USER CODE END 5 */
}

//en of micro ros

/* USER CODE BEGIN Header_executor_function */
/**
* @brief Function implementing the executor thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_executor_function */
void executor_function(void *argument)
{
  /* USER CODE BEGIN executor_function */
  /* Infinite loop */
  for(;;)
  {
	if ( robot_status.status != IDLE){
		if ( robot_status.status == MOVIN_FORWARD){
			move_forward(robot_status.arguments[0], robot_status.arguments[1], robot_status.arguments[2]);
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == MOVIN_BACKWARD){
			move_forward((-1)*robot_status.arguments[0], robot_status.arguments[1], robot_status.arguments[2]);
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == ROTATIN){
			rotate(robot_status.arguments[0], robot_status.arguments[1], robot_status.arguments[2]);
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == ORIENTATIN){
			orientate(roundf(robot_status.arguments[0]), roundf(robot_status.arguments[1]), roundf(robot_status.arguments[2]));
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == GOIN_TO){
			accepted_new_go_to++;
			go_to(roundf(robot_status.arguments[0]), roundf(robot_status.arguments[1]), roundf(robot_status.arguments[2]), 1, roundf(robot_status.arguments[3]));
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == GOIN_TO_BACKWARDS){
			go_to(roundf(robot_status.arguments[0]), roundf(robot_status.arguments[1]), roundf(robot_status.arguments[2]), -1, roundf(robot_status.arguments[3]));
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == BEZIER_CURVIN){
			if (get_distance_to(robot_status.arguments[4], robot_status.arguments[5]) < 2000){
				bezier_curve(roundf(robot_status.arguments[0]), roundf(robot_status.arguments[1]), roundf(robot_status.arguments[2]), roundf(robot_status.arguments[3]), roundf(robot_status.arguments[4]), roundf(robot_status.arguments[5]), roundf(robot_status.arguments[6]), 1, roundf(robot_status.arguments[7]));
			}
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == BEZIER_CURVIN_BACKWARDS){
			if (get_distance_to(robot_status.arguments[4], robot_status.arguments[5]) < 2000){
				bezier_curve(roundf(robot_status.arguments[0]), roundf(robot_status.arguments[1]), roundf(robot_status.arguments[2]), roundf(robot_status.arguments[3]), roundf(robot_status.arguments[4]), roundf(robot_status.arguments[5]), roundf(robot_status.arguments[6]), -1, roundf(robot_status.arguments[7]));
			}
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == SETTIN_POSITION){
			set_position(robot_status.arguments[0], robot_status.arguments[1], robot_status.arguments[2], robot_status.arguments[3]);
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == RESETIN){
			reset_everything();
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == CREEPIN_TO){
			creep_to(roundf(robot_status.arguments[0]), roundf(robot_status.arguments[1]), 1);
			robot_status.status = IDLE;
		}
		else if ( robot_status.status == CREEPIN_TO_BACKWARDS){
			creep_to(roundf(robot_status.arguments[0]), roundf(robot_status.arguments[1]), -1);
			robot_status.status = IDLE;
		}
		if (robot_status.status == IDLE && command_history%10 != 0){
			command_history = command_history*10;
		}
	}
    osDelay(10);
  }
  /* USER CODE END executor_function */
}

/* USER CODE BEGIN Header_IMU_update_function */
/**
* @brief Function implementing the IMU_update_task thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_IMU_update_function */
void IMU_update_function(void *argument)
{
  /* USER CODE BEGIN IMU_update_function */
  /* Infinite loop */
  for(;;)
  {
	// IMU abandoned, bhim yeser brojla, a7wel
	//update_current_yaw();
	//send_values_to_usart(absolute_imu_yaw*100, absolute_phi*100, current_imu_yaw*100, current_imu_gyro_z*100);
//	 prepare_bezier_curve(100, 0, 200, 0, 1000, 0, 1100, 1, 0);
//	rotating_speed = 300;
//	set_position(1750, 1845, 180, 180);
//	prepare_go_to(1000, 0, 300, 1, 0);
//	delay(10000);
//	prepare_go_to(2400, 0, 300, 1, 0);
//	delay(15000);
//	prepare_go_to(2400, -800, 300, 1, 0);
//	delay(6000);
//	prepare_go_to(1750, 1845, 1100, 1, 0);
//	delay(6000);
//	prepare_orientate(180, 0, 0);
//	delay(700);
//	prepare_emergency_break();
//
//	prepare_creep_to(100, 0, 1);

    delay(60000000);
  }
  /* USER CODE END IMU_update_function */
}


/**
  * @brief  Period elapsed callback in non blocking mode
  * @note   This function is called  when TIM2 interrupt took place, inside
  * HAL_TIM_IRQHandler(). It makes a direct call to HAL_IncTick() to increment
  * a global variable "uwTick" used as application time base.
  * @param  htim : TIM handle
  * @retval None
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  /* USER CODE BEGIN Callback 0 */
	if (htim-> Instance == TIM7){
		if(control_loop_state == DISACTIVATED){
			PWM_L = 0;
			PWM_R = 0;
		}else{
			//update_position(skip_position_update);
			update_position(0);
			if (control_loop_state == SPEED){
				dt = (micros() - previous_speed_control_time);
				if (dt > 100){
					// right motor speed control
					float error = target_speed_R - current_speed_R;

					speed_derivative_R = speed_derivative_R*0.999 + 0.001*(error - previous_speed_error_R)*1000000/dt; // unit = mm/s²
					speed_integral_R += error*(dt/1000000);

					previous_speed_error_R = error;

					PWM_R = PWM_R*0.2 + 0.8 * (PWM_offset_R + kpS_R*error + kdS_R*speed_derivative_R + kiS_R*speed_integral_R); // the first part is a simple filter to reduce jitter
					PWM_R = (PWM_R > PWM_max)? PWM_max : (PWM_R < -PWM_max)? -PWM_max : PWM_R;
					PWM_R = (target_speed_R == 0)?0: PWM_R;

					speed_integral_R = ( (PWM_R == PWM_max) || (PWM_R == -PWM_max) || (fabs(speed_integral_R*kiS_R) > PWM_max) )? (speed_integral_R - 2*error*(dt/1000000)) : speed_integral_R;

					// left motor speed control
					error = target_speed_L - current_speed_L;
					speed_derivative_L = speed_derivative_L*0.999 + 0.001*(error - previous_speed_error_L)*1000000/dt; // unit = mm/s²
					speed_integral_L += error*(dt/1000000);

					previous_speed_error_L = error;
					previous_speed_control_time = micros();

					PWM_L = PWM_L*0.2 + 0.8 * (PWM_offset_L + kpS_L*error + kdS_L*speed_derivative_L + kiS_L*speed_integral_L);
					PWM_L = (PWM_L > PWM_max)? PWM_max : (PWM_L < -PWM_max)? -PWM_max : PWM_L;
					PWM_L = (target_speed_L == 0)?0: PWM_L;

					speed_integral_L = ( (PWM_L == PWM_max) || (PWM_L == -PWM_max) || (fabs(speed_integral_L*kiS_L) > PWM_max) )? (speed_integral_L - 2*error*(dt/1000000)) : speed_integral_L;
				}

			}else if (control_loop_state == POSITION){
				dt = (micros() - previous_position_control_time);
				if (dt > 100){
					// right motor position control
					error = (target_encoder_count_R - encoder_count_R)/3; // /3 because it was 1000ticks encoders but now it is 3600, i don't wanna tune it again

					position_derivative_R = (error - previous_position_error_R)*1000000/dt; // unit = tick/s²

					position_integral_R = ( SGN(error) == SGN( previous_position_error_R ) )? position_integral_R + error*(dt/1000000) : 0;

					previous_position_error_R = error;

					PWM_R = kpP_R*error + kdP_R*position_derivative_R + kiP_R*position_integral_R; // the first part is a simple filter to reduce jitter
					PWM_R = (PWM_R > PWM_R_forward_min + position_max_response)? PWM_R_forward_min + position_max_response : (PWM_R < PWM_R_backward_min - position_max_response)? PWM_R_backward_min - position_max_response : PWM_R;

					position_integral_R = ( (PWM_R == PWM_max) || (PWM_R == -PWM_max) )? (position_integral_R - 2*error*(dt/1000000)) : position_integral_R;

					// left motor position control
					error = (target_encoder_count_L - encoder_count_L)/3;

					position_derivative_L = (error - previous_position_error_L)*1000000/dt; // unit = mm/s²
					position_integral_L = ( SGN(error) == SGN( previous_position_error_L) )? position_integral_L + error*(dt/1000000) : 0;

					previous_position_error_L = error;

					PWM_L = kpP_L*error + kdP_L*position_derivative_L + kiP_L*position_integral_L; // the first part is a simple filter to reduce jitter
					PWM_L = (PWM_L > PWM_L_forward_min + position_max_response)? PWM_L_forward_min + position_max_response : (PWM_L < PWM_L_backward_min - position_max_response)? PWM_L_backward_min - position_max_response : PWM_L;

					position_integral_L = ( (PWM_L == PWM_max) || (PWM_L == -PWM_max) )? (position_integral_L - 2*error*(dt/1000000)) : position_integral_L;

					previous_position_error_L = error;
					previous_position_control_time = micros();

					if (
							(
								(wheel_state_L == EMERGENCY_BREAK)
								&&
								(abs(encoder_count_R - target_encoder_count_R) > 10000 )
								&&
								(abs(target_encoder_count_L - encoder_count_L) > 10000 )
							)
							||
							(
								(wheel_state_L != EMERGENCY_BREAK)
								&&
								(abs(encoder_count_R - target_encoder_count_R) > 5000 )
								&&
								(abs(target_encoder_count_L - encoder_count_L) > 5000 )
							)
						){
						set_target_encoder_counts(encoder_count_R, encoder_count_L);
					}
				}
			}
			// collision failsafe
			if (
					(robot_status.status != CREEPIN_TO)
					&&
					(robot_status.status != CREEPIN_TO_BACKWARDS)
					&&
					fail_safe_activated
					&&
					(
						(fabs(PWM_R) > STOP_PWM_THRESHOLD &&
						 fabs(current_speed_R) < STOP_SPEED_THRESHOLD)

						||

						(fabs(PWM_L) > STOP_PWM_THRESHOLD &&
						 fabs(current_speed_L) < STOP_SPEED_THRESHOLD)
					)
				)
				{
					// EMERGENCY STOP
                 fail_safe_counter++;
                 if(fail_safe_counter >250){
                	 prepare_emergency_break();
                	 stopped_because_of_collision = 1;
                 }
			}
			else {
				 fail_safe_counter = 0;
			}
			///////////////////////////
			////// tornado failsafe
			if(in_tornado){
				if (tornado_condition()){
					if ((micros() - tornado_start_time) > 1200000){
						//////////
						if (control_loop_state == POSITION){
							emergency_break();
							robot_status.status = IDLE;
						}else{
							prepare_emergency_break();
						}
						in_tornado = 0;
					}
				}else{
					in_tornado = 0;
				}
			}else{
				if (tornado_condition()){
					in_tornado = 1;
					tornado_start_time = micros();
				}
			}
		}
		run_right_motor();
		run_left_motor();
	}
  /* USER CODE END Callback 0 */
  if (htim->Instance == TIM2) {
    HAL_IncTick();
  }
  /* USER CODE BEGIN Callback 1 */

  /* USER CODE END Callback 1 */
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
