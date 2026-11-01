#ifndef MICRO_ROS_H
#define MICRO_ROS_H

#ifdef __cplusplus
extern "C" {
#endif

#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <geometry_msgs/geometry_msgs/msg/vector3.h>
#include <std_msgs/msg/bool.h>
#include <rcl/error_handling.h>
#include <rclc/executor.h>
#include <uxr/client/transport.h>
#include <rmw_microxrcedds_c/config.h>
#include <rmw_microros/rmw_microros.h>
#include <std_msgs/msg/int32.h>
#include <service/srv/navi_stm.h>
#include <service/srv/set_variables.h>
#include <std_msgs/msg/string.h>
#include <rosidl_runtime_c/string_functions.h>
// micro-ROS system state
typedef enum {
    AGENT_WAIT = 0,
    AGENT_AVAILABLE,
    AGENT_CONNECTED,
    AGENT_DISCONNECTED
} SystemState;

//  ROS 2 Core Components
extern rcl_node_t node;
extern rclc_support_t support;
extern rcl_allocator_t allocator;

//  Publisher Components
extern rcl_publisher_t pose_publisher;
extern rcl_publisher_t debugger_publisher;
// Subscriber Components
extern rcl_subscription_t bool_subscriber;
extern std_msgs__msg__Bool bool_msg;

//  Service Components
extern rcl_service_t service;
extern rclc_executor_t executor ;
extern service__srv__NaviStm_Request request_msg;
extern service__srv__NaviStm_Response response_msg;
bool create_rcl_entities(void);
void execute_every_n_ms(int64_t ms, SystemState system_state);
void service_callback(const void *request_msg, void *response_msg);
void destroy_rcl_entities(void);
/*bool create_rcl_entities(void);
void execute_every_n_ms(int64_t ms, SystemState system_state);
void service_callback(const void *request_msg, void *response_msg);*/

#ifdef __cplusplus
}
#endif

#endif // MICRO_ROS_STATE_H
