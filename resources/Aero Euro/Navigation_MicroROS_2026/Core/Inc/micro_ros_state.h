#ifndef MICRO_ROS_STATE_H
#define MICRO_ROS_STATE_H

#ifdef __cplusplus
extern "C" {
#endif

// micro-ROS system state
typedef enum {
    AGENT_WAIT = 0,
    AGENT_AVAILABLE,
    AGENT_CONNECTED,
    AGENT_DISCONNECTED
} SystemState;

#ifdef __cplusplus
}
#endif

#endif // MICRO_ROS_STATE_H
