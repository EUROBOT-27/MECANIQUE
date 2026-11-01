// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from oussema:srv/SetVariables.idl
// generated code does not contain a copyright notice
#include "oussema/srv/detail/set_variables__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `functions`
#include "rosidl_runtime_c/string_functions.h"

bool
oussema__srv__SetVariables_Request__init(oussema__srv__SetVariables_Request * msg)
{
  if (!msg) {
    return false;
  }
  // functions
  if (!rosidl_runtime_c__String__init(&msg->functions)) {
    oussema__srv__SetVariables_Request__fini(msg);
    return false;
  }
  // arg1
  // arg2
  // arg3
  // arg4
  // arg5
  // arg6
  // arg7
  // arg8
  // arg9
  // arg10
  return true;
}

void
oussema__srv__SetVariables_Request__fini(oussema__srv__SetVariables_Request * msg)
{
  if (!msg) {
    return;
  }
  // functions
  rosidl_runtime_c__String__fini(&msg->functions);
  // arg1
  // arg2
  // arg3
  // arg4
  // arg5
  // arg6
  // arg7
  // arg8
  // arg9
  // arg10
}

bool
oussema__srv__SetVariables_Request__are_equal(const oussema__srv__SetVariables_Request * lhs, const oussema__srv__SetVariables_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // functions
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->functions), &(rhs->functions)))
  {
    return false;
  }
  // arg1
  if (lhs->arg1 != rhs->arg1) {
    return false;
  }
  // arg2
  if (lhs->arg2 != rhs->arg2) {
    return false;
  }
  // arg3
  if (lhs->arg3 != rhs->arg3) {
    return false;
  }
  // arg4
  if (lhs->arg4 != rhs->arg4) {
    return false;
  }
  // arg5
  if (lhs->arg5 != rhs->arg5) {
    return false;
  }
  // arg6
  if (lhs->arg6 != rhs->arg6) {
    return false;
  }
  // arg7
  if (lhs->arg7 != rhs->arg7) {
    return false;
  }
  // arg8
  if (lhs->arg8 != rhs->arg8) {
    return false;
  }
  // arg9
  if (lhs->arg9 != rhs->arg9) {
    return false;
  }
  // arg10
  if (lhs->arg10 != rhs->arg10) {
    return false;
  }
  return true;
}

bool
oussema__srv__SetVariables_Request__copy(
  const oussema__srv__SetVariables_Request * input,
  oussema__srv__SetVariables_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // functions
  if (!rosidl_runtime_c__String__copy(
      &(input->functions), &(output->functions)))
  {
    return false;
  }
  // arg1
  output->arg1 = input->arg1;
  // arg2
  output->arg2 = input->arg2;
  // arg3
  output->arg3 = input->arg3;
  // arg4
  output->arg4 = input->arg4;
  // arg5
  output->arg5 = input->arg5;
  // arg6
  output->arg6 = input->arg6;
  // arg7
  output->arg7 = input->arg7;
  // arg8
  output->arg8 = input->arg8;
  // arg9
  output->arg9 = input->arg9;
  // arg10
  output->arg10 = input->arg10;
  return true;
}

oussema__srv__SetVariables_Request *
oussema__srv__SetVariables_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  oussema__srv__SetVariables_Request * msg = (oussema__srv__SetVariables_Request *)allocator.allocate(sizeof(oussema__srv__SetVariables_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(oussema__srv__SetVariables_Request));
  bool success = oussema__srv__SetVariables_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
oussema__srv__SetVariables_Request__destroy(oussema__srv__SetVariables_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    oussema__srv__SetVariables_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
oussema__srv__SetVariables_Request__Sequence__init(oussema__srv__SetVariables_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  oussema__srv__SetVariables_Request * data = NULL;

  if (size) {
    data = (oussema__srv__SetVariables_Request *)allocator.zero_allocate(size, sizeof(oussema__srv__SetVariables_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = oussema__srv__SetVariables_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        oussema__srv__SetVariables_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
oussema__srv__SetVariables_Request__Sequence__fini(oussema__srv__SetVariables_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      oussema__srv__SetVariables_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

oussema__srv__SetVariables_Request__Sequence *
oussema__srv__SetVariables_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  oussema__srv__SetVariables_Request__Sequence * array = (oussema__srv__SetVariables_Request__Sequence *)allocator.allocate(sizeof(oussema__srv__SetVariables_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = oussema__srv__SetVariables_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
oussema__srv__SetVariables_Request__Sequence__destroy(oussema__srv__SetVariables_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    oussema__srv__SetVariables_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
oussema__srv__SetVariables_Request__Sequence__are_equal(const oussema__srv__SetVariables_Request__Sequence * lhs, const oussema__srv__SetVariables_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!oussema__srv__SetVariables_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
oussema__srv__SetVariables_Request__Sequence__copy(
  const oussema__srv__SetVariables_Request__Sequence * input,
  oussema__srv__SetVariables_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(oussema__srv__SetVariables_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    oussema__srv__SetVariables_Request * data =
      (oussema__srv__SetVariables_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!oussema__srv__SetVariables_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          oussema__srv__SetVariables_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!oussema__srv__SetVariables_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
oussema__srv__SetVariables_Response__init(oussema__srv__SetVariables_Response * msg)
{
  if (!msg) {
    return false;
  }
  // result
  return true;
}

void
oussema__srv__SetVariables_Response__fini(oussema__srv__SetVariables_Response * msg)
{
  if (!msg) {
    return;
  }
  // result
}

bool
oussema__srv__SetVariables_Response__are_equal(const oussema__srv__SetVariables_Response * lhs, const oussema__srv__SetVariables_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // result
  if (lhs->result != rhs->result) {
    return false;
  }
  return true;
}

bool
oussema__srv__SetVariables_Response__copy(
  const oussema__srv__SetVariables_Response * input,
  oussema__srv__SetVariables_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // result
  output->result = input->result;
  return true;
}

oussema__srv__SetVariables_Response *
oussema__srv__SetVariables_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  oussema__srv__SetVariables_Response * msg = (oussema__srv__SetVariables_Response *)allocator.allocate(sizeof(oussema__srv__SetVariables_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(oussema__srv__SetVariables_Response));
  bool success = oussema__srv__SetVariables_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
oussema__srv__SetVariables_Response__destroy(oussema__srv__SetVariables_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    oussema__srv__SetVariables_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
oussema__srv__SetVariables_Response__Sequence__init(oussema__srv__SetVariables_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  oussema__srv__SetVariables_Response * data = NULL;

  if (size) {
    data = (oussema__srv__SetVariables_Response *)allocator.zero_allocate(size, sizeof(oussema__srv__SetVariables_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = oussema__srv__SetVariables_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        oussema__srv__SetVariables_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
oussema__srv__SetVariables_Response__Sequence__fini(oussema__srv__SetVariables_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      oussema__srv__SetVariables_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

oussema__srv__SetVariables_Response__Sequence *
oussema__srv__SetVariables_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  oussema__srv__SetVariables_Response__Sequence * array = (oussema__srv__SetVariables_Response__Sequence *)allocator.allocate(sizeof(oussema__srv__SetVariables_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = oussema__srv__SetVariables_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
oussema__srv__SetVariables_Response__Sequence__destroy(oussema__srv__SetVariables_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    oussema__srv__SetVariables_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
oussema__srv__SetVariables_Response__Sequence__are_equal(const oussema__srv__SetVariables_Response__Sequence * lhs, const oussema__srv__SetVariables_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!oussema__srv__SetVariables_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
oussema__srv__SetVariables_Response__Sequence__copy(
  const oussema__srv__SetVariables_Response__Sequence * input,
  oussema__srv__SetVariables_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(oussema__srv__SetVariables_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    oussema__srv__SetVariables_Response * data =
      (oussema__srv__SetVariables_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!oussema__srv__SetVariables_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          oussema__srv__SetVariables_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!oussema__srv__SetVariables_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
