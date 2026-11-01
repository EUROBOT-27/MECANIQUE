// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from service:srv/SetVariables.idl
// generated code does not contain a copyright notice
#include "service/srv/detail/set_variables__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
service__srv__SetVariables_Request__init(service__srv__SetVariables_Request * msg)
{
  if (!msg) {
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
service__srv__SetVariables_Request__fini(service__srv__SetVariables_Request * msg)
{
  if (!msg) {
    return;
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
}

bool
service__srv__SetVariables_Request__are_equal(const service__srv__SetVariables_Request * lhs, const service__srv__SetVariables_Request * rhs)
{
  if (!lhs || !rhs) {
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
service__srv__SetVariables_Request__copy(
  const service__srv__SetVariables_Request * input,
  service__srv__SetVariables_Request * output)
{
  if (!input || !output) {
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

service__srv__SetVariables_Request *
service__srv__SetVariables_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  service__srv__SetVariables_Request * msg = (service__srv__SetVariables_Request *)allocator.allocate(sizeof(service__srv__SetVariables_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(service__srv__SetVariables_Request));
  bool success = service__srv__SetVariables_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
service__srv__SetVariables_Request__destroy(service__srv__SetVariables_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    service__srv__SetVariables_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
service__srv__SetVariables_Request__Sequence__init(service__srv__SetVariables_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  service__srv__SetVariables_Request * data = NULL;

  if (size) {
    data = (service__srv__SetVariables_Request *)allocator.zero_allocate(size, sizeof(service__srv__SetVariables_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = service__srv__SetVariables_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        service__srv__SetVariables_Request__fini(&data[i - 1]);
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
service__srv__SetVariables_Request__Sequence__fini(service__srv__SetVariables_Request__Sequence * array)
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
      service__srv__SetVariables_Request__fini(&array->data[i]);
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

service__srv__SetVariables_Request__Sequence *
service__srv__SetVariables_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  service__srv__SetVariables_Request__Sequence * array = (service__srv__SetVariables_Request__Sequence *)allocator.allocate(sizeof(service__srv__SetVariables_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = service__srv__SetVariables_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
service__srv__SetVariables_Request__Sequence__destroy(service__srv__SetVariables_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    service__srv__SetVariables_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
service__srv__SetVariables_Request__Sequence__are_equal(const service__srv__SetVariables_Request__Sequence * lhs, const service__srv__SetVariables_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!service__srv__SetVariables_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
service__srv__SetVariables_Request__Sequence__copy(
  const service__srv__SetVariables_Request__Sequence * input,
  service__srv__SetVariables_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(service__srv__SetVariables_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    service__srv__SetVariables_Request * data =
      (service__srv__SetVariables_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!service__srv__SetVariables_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          service__srv__SetVariables_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!service__srv__SetVariables_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
service__srv__SetVariables_Response__init(service__srv__SetVariables_Response * msg)
{
  if (!msg) {
    return false;
  }
  // result
  return true;
}

void
service__srv__SetVariables_Response__fini(service__srv__SetVariables_Response * msg)
{
  if (!msg) {
    return;
  }
  // result
}

bool
service__srv__SetVariables_Response__are_equal(const service__srv__SetVariables_Response * lhs, const service__srv__SetVariables_Response * rhs)
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
service__srv__SetVariables_Response__copy(
  const service__srv__SetVariables_Response * input,
  service__srv__SetVariables_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // result
  output->result = input->result;
  return true;
}

service__srv__SetVariables_Response *
service__srv__SetVariables_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  service__srv__SetVariables_Response * msg = (service__srv__SetVariables_Response *)allocator.allocate(sizeof(service__srv__SetVariables_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(service__srv__SetVariables_Response));
  bool success = service__srv__SetVariables_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
service__srv__SetVariables_Response__destroy(service__srv__SetVariables_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    service__srv__SetVariables_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
service__srv__SetVariables_Response__Sequence__init(service__srv__SetVariables_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  service__srv__SetVariables_Response * data = NULL;

  if (size) {
    data = (service__srv__SetVariables_Response *)allocator.zero_allocate(size, sizeof(service__srv__SetVariables_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = service__srv__SetVariables_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        service__srv__SetVariables_Response__fini(&data[i - 1]);
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
service__srv__SetVariables_Response__Sequence__fini(service__srv__SetVariables_Response__Sequence * array)
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
      service__srv__SetVariables_Response__fini(&array->data[i]);
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

service__srv__SetVariables_Response__Sequence *
service__srv__SetVariables_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  service__srv__SetVariables_Response__Sequence * array = (service__srv__SetVariables_Response__Sequence *)allocator.allocate(sizeof(service__srv__SetVariables_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = service__srv__SetVariables_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
service__srv__SetVariables_Response__Sequence__destroy(service__srv__SetVariables_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    service__srv__SetVariables_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
service__srv__SetVariables_Response__Sequence__are_equal(const service__srv__SetVariables_Response__Sequence * lhs, const service__srv__SetVariables_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!service__srv__SetVariables_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
service__srv__SetVariables_Response__Sequence__copy(
  const service__srv__SetVariables_Response__Sequence * input,
  service__srv__SetVariables_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(service__srv__SetVariables_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    service__srv__SetVariables_Response * data =
      (service__srv__SetVariables_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!service__srv__SetVariables_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          service__srv__SetVariables_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!service__srv__SetVariables_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
