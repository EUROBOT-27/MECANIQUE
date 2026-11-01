// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from service:srv/NaviStm.idl
// generated code does not contain a copyright notice

#ifndef SERVICE__SRV__DETAIL__NAVI_STM__STRUCT_H_
#define SERVICE__SRV__DETAIL__NAVI_STM__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/NaviStm in the package service.
typedef struct service__srv__NaviStm_Request
{
  float arg1;
  float arg2;
  float arg3;
  float arg4;
  float arg5;
  float arg6;
  float arg7;
  float arg8;
  float arg9;
  float arg10;
} service__srv__NaviStm_Request;

// Struct for a sequence of service__srv__NaviStm_Request.
typedef struct service__srv__NaviStm_Request__Sequence
{
  service__srv__NaviStm_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} service__srv__NaviStm_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/NaviStm in the package service.
typedef struct service__srv__NaviStm_Response
{
  bool result;
} service__srv__NaviStm_Response;

// Struct for a sequence of service__srv__NaviStm_Response.
typedef struct service__srv__NaviStm_Response__Sequence
{
  service__srv__NaviStm_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} service__srv__NaviStm_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SERVICE__SRV__DETAIL__NAVI_STM__STRUCT_H_
