/*
 * micro_ros.c
 *
 *  Created on: Jan 16, 2026
 *      Author: aminebensaid66
 */
#include "micro_ros.h"
#include "main.h"

//  ROS 2 Core Components
rcl_node_t node;
rclc_support_t support;
rcl_allocator_t allocator;

//  Publisher Components
rcl_publisher_t pose_publisher;
rcl_publisher_t debugger_publisher;
// Subscriber Components
rcl_subscription_t bool_subscriber;
std_msgs__msg__Bool bool_msg;

//  Service Components
rcl_service_t service;
rclc_executor_t executor ;
service__srv__NaviStm_Request request_msg;
service__srv__NaviStm_Response response_msg;

bool create_rcl_entities(void)
{
  rcl_ret_t ret;

  ret = rclc_support_init(&support, 0, NULL, &allocator);
  if (ret != RCL_RET_OK) return false;

  ret = rclc_node_init_default(&node, "cubemx_node", "", &support);
  if (ret != RCL_RET_OK) return false;

  ret = rclc_publisher_init_default(
      &pose_publisher,
      &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Vector3),
      "/robot_pose_raw"
  );
  ret = rclc_publisher_init_default(
        &debugger_publisher,
        &node,
		ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, String),
        "/debug"
    );
  if (ret != RCL_RET_OK) return false;

  const rosidl_message_type_support_t *service_type_support =
      ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(
        rosidl_typesupport_microxrcedds_c, service, srv, NaviStm)();

  ret = rclc_service_init_default(
      &service,
      &node,
      service_type_support,
      "/stm/navi_stm"
  );
  if (ret != RCL_RET_OK) return false;

  ret = rclc_executor_init(&executor, &support.context, 5, &allocator);
  if (ret != RCL_RET_OK) return false;

  ret = rclc_executor_add_service(
      &executor,
      &service,
      &request_msg,
      &response_msg,
      service_callback
  );
  if (ret != RCL_RET_OK) return false;
  return true;
}

void execute_every_n_ms(int64_t ms, SystemState system_state) {
    // Method for periodically pinging the micro_ros_agent
    do {
        static volatile int64_t init = -1;
        if (init == -1) {
            init = uxr_millis();
        }
        if (uxr_millis() - init > ms) {
            // system_state;
            init = uxr_millis();
        }
    }
    while (0);
}
void destroy_rcl_entities(void)
{
  rcl_ret_t ret;

  ret = rclc_executor_fini(&executor);
  ret = rcl_service_fini(&service, &node);
  ret = rcl_publisher_fini(&pose_publisher, &node);
  ret = rcl_node_fini(&node);
  ret = rclc_support_fini(&support);

  rmw_uros_set_context_entity_destroy_session_timeout(&support.context, 0);
}
