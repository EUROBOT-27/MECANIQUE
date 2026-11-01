// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from oussema:srv/SetVariables.idl
// generated code does not contain a copyright notice

#ifndef OUSSEMA__SRV__DETAIL__SET_VARIABLES__STRUCT_H_
#define OUSSEMA__SRV__DETAIL__SET_VARIABLES__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'functions'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/SetVariables in the package oussema.
typedef struct oussema__srv__SetVariables_Request
{
  rosidl_runtime_c__String functions;
  int32_t arg1;
  int32_t arg2;
  int32_t arg3;
  int32_t arg4;
  int32_t arg5;
  int32_t arg6;
  int32_t arg7;
  int32_t arg8;
  int32_t arg9;
  int32_t arg10;
} oussema__srv__SetVariables_Request;

// Struct for a sequence of oussema__srv__SetVariables_Request.
typedef struct oussema__srv__SetVariables_Request__Sequence
{
  oussema__srv__SetVariables_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} oussema__srv__SetVariables_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/SetVariables in the package oussema.
typedef struct oussema__srv__SetVariables_Response
{
  bool result;
} oussema__srv__SetVariables_Response;

// Struct for a sequence of oussema__srv__SetVariables_Response.
typedef struct oussema__srv__SetVariables_Response__Sequence
{
  oussema__srv__SetVariables_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} oussema__srv__SetVariables_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OUSSEMA__SRV__DETAIL__SET_VARIABLES__STRUCT_H_
