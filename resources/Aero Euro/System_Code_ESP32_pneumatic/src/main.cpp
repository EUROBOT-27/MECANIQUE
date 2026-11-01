#include <Arduino.h>
#include <micro_ros_arduino.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/int32.h>
#include <std_msgs/msg/int64.h>
#include <rmw_microros/rmw_microros.h>

// Agent status enum
typedef enum {
    AGENT_WAIT = 0,
    AGENT_AVAILABLE,
    AGENT_CONNECTED,
    AGENT_DISCONNECTED
} AgentStatus;

AgentStatus agent_status = AGENT_WAIT;

// micro-ROS variables
rcl_subscription_t forward_subscriber;
rcl_subscription_t backward_subscriber;
rcl_publisher_t status_publisher;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;
std_msgs__msg__Int32 forward_msg;
std_msgs__msg__Int32 backward_msg;
std_msgs__msg__Int64 status_msg;

// Function declarations
void forward_pneumatic_callback(const void *msgin);
void backward_pneumatic_callback(const void *msgin);

int front_electrovalve_pins[] = {16, 17, 12, 13};
int back_electrovalve_pins[] = {5, 21, 22, 33};
int front_pump_pin = 19;
int back_pump_pin = 18;

void activateElectrovalve(int front_0_back_1, int cup_index) {
  if (front_0_back_1 == 0) {
    digitalWrite(front_electrovalve_pins[cup_index], HIGH);
  } else {
    digitalWrite(back_electrovalve_pins[cup_index], HIGH);
  }
}
void activateAllElectrovalves(int front_0_back_1) {
  if (front_0_back_1 == 0) {
    for (int pin : front_electrovalve_pins) {
      digitalWrite(pin, HIGH);
    }
  } else {
    for (int pin : back_electrovalve_pins) {
      digitalWrite(pin, HIGH);
    }
  }
}
void deactivateElectrovalve(int front_0_back_1, int cup_index) {
  if (front_0_back_1 == 0) {
    digitalWrite(front_electrovalve_pins[cup_index], LOW);
  } else {
    digitalWrite(back_electrovalve_pins[cup_index], LOW);
  }
}
void deactivateAllElectrovalves(int front_0_back_1) {
  if (front_0_back_1 == 0) {
    for (int pin : front_electrovalve_pins) {
      digitalWrite(pin, LOW);
    }
  } else {
    for (int pin : back_electrovalve_pins) {
      digitalWrite(pin, LOW);
    }
  }
}
void activatePump(int front_0_back_1) {
  if (front_0_back_1 == 0) {
    digitalWrite(front_pump_pin, HIGH);
  } else {
    digitalWrite(back_pump_pin, HIGH);
  }
}
void deactivatePump(int front_0_back_1) {
  if (front_0_back_1 == 0) {
    digitalWrite(front_pump_pin, LOW);
  } else {
    digitalWrite(back_pump_pin, LOW);
  }
}

// Callback function for /forward/pneumatic topic
void forward_pneumatic_callback(const void *msgin) {
  const std_msgs__msg__Int32 *msg = (const std_msgs__msg__Int32 *)msgin;
  int32_t value = msg->data;
  if (value==20){
    ESP.restart();
    return;
  }
  if (value >= 16){
    deactivateAllElectrovalves(0);
    deactivatePump(0);
    return;
  }

  // 1 activates the electrovalve, ordered from MSB to LSB
  int inactive_valves = 0;
  for (int i = 0; i < 4; i++) {
    int bit = ((value << i) & 0x08) >> 3;
    if (bit == 1) {
      activateElectrovalve(0, i);
    } else {
      inactive_valves++;
      deactivateElectrovalve(0, i);
    }
    if (inactive_valves == 0){
      deactivatePump(0);
    }else{
      activatePump(0);
    }
  }
}

// Callback function for /backward/pneumatic topic
void backward_pneumatic_callback(const void *msgin) {
  const std_msgs__msg__Int32 *msg = (const std_msgs__msg__Int32 *)msgin;
  int32_t value = msg->data;
   if (value==20){
    ESP.restart();
    return;
  }
  if (value >= 16){
    deactivateAllElectrovalves(1);
    deactivatePump(1);
    return;
  }

  // 1 activates the electrovalve, ordered from MSB to LSB
  int inactive_valves = 0;
  for (int i = 0; i < 4; i++) {
    int bit = ((value << i) & 0x08) >> 3;
    if (bit == 1) {
      activateElectrovalve(1, i);
    } else {
      inactive_valves++;
      deactivateElectrovalve(1, i);
    }
    if (inactive_valves == 0){
      deactivatePump(1);
    }else{
      activatePump(1);
    }
  }
}

void test_with_serial(){
  if (Serial.available()) {
    String s = Serial.readStringUntil('\n');
    s.trim();
    if (s.length() > 0) {
      int n = s.toInt();
      Serial.print("Received: ");
      Serial.println(n);

      if (n >= 0 && n <= 3) {
        Serial.println("Activating front suction cup");
        activateElectrovalve(0, n);
        delay(500);
        deactivateElectrovalve(0, n);
      } else if (n >= 4 && n <= 7) {
        int idx = n - 4;
        Serial.println("Activating back suction cup");
        activateElectrovalve(1, idx);
        delay(500);
        deactivateElectrovalve(1, idx);
      } else if (n == 20) {
        Serial.println("Activating all front suction cups");
        activateAllElectrovalves(0);
      } else if (n == 21) {
        Serial.println("Activating all back suction cups");
        activateAllElectrovalves(1);
      } else if (n == 30) {
        Serial.println("Activating front pump");
        activatePump(0);
      } else if (n == 31) {
        Serial.println("Activating back pump");
        activatePump(1);
      } else if (n == 50) {
        Serial.println("Deactivating front pump");
        deactivatePump(0);
      } else if (n == 51) {
        Serial.println("Deactivating back pump");
        deactivatePump(1);
      } else if (n == 40) {
        Serial.println("Deactivating all front suction cups");
        deactivateAllElectrovalves(0);
      } else if (n == 41) {
        Serial.println("Deactivating all back suction cups");
        deactivateAllElectrovalves(1);
      } else {
        Serial.println("Unknown command");
      }
    }
  }
}

// ============================================================================
// Agent Connection Management Functions
// ============================================================================
bool pingAgent() {
    // Ping the agent to check if it's still alive
    rcl_ret_t ping_result = rmw_uros_ping_agent(100, 1); // 100ms timeout, 1 attempt
    return ping_result == RCL_RET_OK;
}

void cleanupMicroROS() {
    // Clean up executor
    rclc_executor_fini(&executor);

  // Clean up publisher
  rcl_publisher_fini(&status_publisher, &node);
    
    // Clean up subscriptions
    rcl_subscription_fini(&forward_subscriber, &node);
    rcl_subscription_fini(&backward_subscriber, &node);
    
    // Clean up node
    rcl_node_fini(&node);
    
    // Clean up support
    rclc_support_fini(&support);
}

bool initializeMicroROS() {
    allocator = rcl_get_default_allocator();
    
    // Initialize support
    rcl_ret_t ret = rclc_support_init(&support, 0, NULL, &allocator);
    if (ret != RCL_RET_OK) {
        return false;
    }
    
    // Initialize node
    ret = rclc_node_init_default(&node, "esp32_pneumatic_node", "", &support);
    if (ret != RCL_RET_OK) {
        rclc_support_fini(&support);
        return false;
    }
    
    // Create subscriptions
    ret = rclc_subscription_init_default(
        &forward_subscriber,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
        "/front/pneumatic");
    if (ret != RCL_RET_OK) {
        rcl_node_fini(&node);
        rclc_support_fini(&support);
        return false;
    }
    
    ret = rclc_subscription_init_default(
        &backward_subscriber,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
        "/back/pneumatic");
    if (ret != RCL_RET_OK) {
        rcl_subscription_fini(&forward_subscriber, &node);
        rcl_node_fini(&node);
        rclc_support_fini(&support);
        return false;
    }

    // Create status publisher for dashboard heartbeat
    ret = rclc_publisher_init_default(
      &status_publisher,
      &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int64),
      "/pneumatic/status");
    if (ret != RCL_RET_OK) {
      rcl_subscription_fini(&forward_subscriber, &node);
      rcl_subscription_fini(&backward_subscriber, &node);
      rcl_node_fini(&node);
      rclc_support_fini(&support);
      return false;
    }
    
    // Create executor
    ret = rclc_executor_init(&executor, &support.context, 2, &allocator);
    if (ret != RCL_RET_OK) {
        rcl_subscription_fini(&forward_subscriber, &node);
        rcl_subscription_fini(&backward_subscriber, &node);
        rcl_node_fini(&node);
        rclc_support_fini(&support);
        return false;
    }
    
    // Add subscriptions to executor
    rclc_executor_add_subscription(&executor, &forward_subscriber, &forward_msg,
                                    &forward_pneumatic_callback, ON_NEW_DATA);
    rclc_executor_add_subscription(&executor, &backward_subscriber, &backward_msg,
                                    &backward_pneumatic_callback, ON_NEW_DATA);

    return true;
}

bool setup_uros() {
  allocator = rcl_get_default_allocator();
  rcl_ret_t ret = rclc_support_init(&support, 0, NULL, &allocator);
  
  if (ret != RCL_RET_OK) {
    delay(2000);
    return false;
  }
  
  ret = rclc_node_init_default(&node, "esp32_pneumatic_node", "", &support);
  if (ret != RCL_RET_OK) {
    delay(2000);
    return false;
  }

  // Create QoS profile with reliable settings
  rcl_subscription_options_t sub_opts = rcl_subscription_get_default_options();
  sub_opts.qos.reliability = RMW_QOS_POLICY_RELIABILITY_RELIABLE;
  sub_opts.qos.history = RMW_QOS_POLICY_HISTORY_KEEP_LAST;
  sub_opts.qos.depth = 1;

  // Create subscriptions with reliable QoS
  ret = rclc_subscription_init(
      &forward_subscriber,
      &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
      "/front/pneumatic",
      &sub_opts.qos);
  if (ret != RCL_RET_OK) {
  }

  ret = rclc_subscription_init(
      &backward_subscriber,
      &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
      "/back/pneumatic",
      &sub_opts.qos);
  if (ret != RCL_RET_OK) {
  }

  // Create executor
  ret = rclc_executor_init(&executor, &support.context, 2, &allocator);
  if (ret != RCL_RET_OK) {
    delay(2000);
    return false;
  }
  
  rclc_executor_add_subscription(&executor, &forward_subscriber, &forward_msg,
                                  &forward_pneumatic_callback, ON_NEW_DATA);
  rclc_executor_add_subscription(&executor, &backward_subscriber, &backward_msg,
                                  &backward_pneumatic_callback, ON_NEW_DATA);

  return true;
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  set_microros_transports();
  digitalWrite(2, HIGH); // Turn on built-in LED to indicate startup
  
  // Initialize GPIO pins
  for (int pin : front_electrovalve_pins) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  for (int pin : back_electrovalve_pins) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  pinMode(front_pump_pin, OUTPUT);
  digitalWrite(front_pump_pin, LOW);
  pinMode(back_pump_pin, OUTPUT);
  digitalWrite(back_pump_pin, LOW);
}

void loop() {
    static unsigned long last_ping_time = 0;
  static unsigned long last_status_time = 0;
    const unsigned long PING_INTERVAL = 500; // Ping every 0.5 second
  const unsigned long STATUS_INTERVAL = 1000; // Publish status every 1 second
    const unsigned long RECONNECT_DELAY = 500; // Wait 0.5 second before reconnect
    
    switch (agent_status) {
        case AGENT_WAIT:
        case AGENT_DISCONNECTED:
            agent_status = AGENT_WAIT;
            
            // Check if agent is available
            if (pingAgent()) {
                agent_status = AGENT_AVAILABLE;
            } else {
                delay(RECONNECT_DELAY);
            }
            break;
            
        case AGENT_AVAILABLE:
            // Try to initialize micro-ROS
            if (initializeMicroROS()) {
                agent_status = AGENT_CONNECTED;
                last_ping_time = millis();
            last_status_time = millis();
            } else {
                agent_status = AGENT_WAIT;
                delay(RECONNECT_DELAY);
            }
            break;
            
        case AGENT_CONNECTED:
            // Spin executor to process messages
            rcl_ret_t ret = rclc_executor_spin_some(&executor, RCL_MS_TO_NS(20));

          // Publish status heartbeat for dashboard
          if (millis() - last_status_time > STATUS_INTERVAL) {
            status_msg.data = 1;
            rcl_publish(&status_publisher, &status_msg, NULL);
            last_status_time = millis();
          }
            
            // Periodic ping to check agent health
            if (millis() - last_ping_time > PING_INTERVAL) {
                if (!pingAgent()) {
                    cleanupMicroROS();
                    agent_status = AGENT_DISCONNECTED;
                }
                last_ping_time = millis();
            }
            
            delay(20);
            break;
    }
}
