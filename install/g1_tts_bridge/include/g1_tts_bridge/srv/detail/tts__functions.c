// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from g1_tts_bridge:srv/TTS.idl
// generated code does not contain a copyright notice
#include "g1_tts_bridge/srv/detail/tts__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `text`
#include "rosidl_runtime_c/string_functions.h"

bool
g1_tts_bridge__srv__TTS_Request__init(g1_tts_bridge__srv__TTS_Request * msg)
{
  if (!msg) {
    return false;
  }
  // text
  if (!rosidl_runtime_c__String__init(&msg->text)) {
    g1_tts_bridge__srv__TTS_Request__fini(msg);
    return false;
  }
  // speaker_id
  return true;
}

void
g1_tts_bridge__srv__TTS_Request__fini(g1_tts_bridge__srv__TTS_Request * msg)
{
  if (!msg) {
    return;
  }
  // text
  rosidl_runtime_c__String__fini(&msg->text);
  // speaker_id
}

bool
g1_tts_bridge__srv__TTS_Request__are_equal(const g1_tts_bridge__srv__TTS_Request * lhs, const g1_tts_bridge__srv__TTS_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // text
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->text), &(rhs->text)))
  {
    return false;
  }
  // speaker_id
  if (lhs->speaker_id != rhs->speaker_id) {
    return false;
  }
  return true;
}

bool
g1_tts_bridge__srv__TTS_Request__copy(
  const g1_tts_bridge__srv__TTS_Request * input,
  g1_tts_bridge__srv__TTS_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // text
  if (!rosidl_runtime_c__String__copy(
      &(input->text), &(output->text)))
  {
    return false;
  }
  // speaker_id
  output->speaker_id = input->speaker_id;
  return true;
}

g1_tts_bridge__srv__TTS_Request *
g1_tts_bridge__srv__TTS_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  g1_tts_bridge__srv__TTS_Request * msg = (g1_tts_bridge__srv__TTS_Request *)allocator.allocate(sizeof(g1_tts_bridge__srv__TTS_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(g1_tts_bridge__srv__TTS_Request));
  bool success = g1_tts_bridge__srv__TTS_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
g1_tts_bridge__srv__TTS_Request__destroy(g1_tts_bridge__srv__TTS_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    g1_tts_bridge__srv__TTS_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
g1_tts_bridge__srv__TTS_Request__Sequence__init(g1_tts_bridge__srv__TTS_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  g1_tts_bridge__srv__TTS_Request * data = NULL;

  if (size) {
    data = (g1_tts_bridge__srv__TTS_Request *)allocator.zero_allocate(size, sizeof(g1_tts_bridge__srv__TTS_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = g1_tts_bridge__srv__TTS_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        g1_tts_bridge__srv__TTS_Request__fini(&data[i - 1]);
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
g1_tts_bridge__srv__TTS_Request__Sequence__fini(g1_tts_bridge__srv__TTS_Request__Sequence * array)
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
      g1_tts_bridge__srv__TTS_Request__fini(&array->data[i]);
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

g1_tts_bridge__srv__TTS_Request__Sequence *
g1_tts_bridge__srv__TTS_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  g1_tts_bridge__srv__TTS_Request__Sequence * array = (g1_tts_bridge__srv__TTS_Request__Sequence *)allocator.allocate(sizeof(g1_tts_bridge__srv__TTS_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = g1_tts_bridge__srv__TTS_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
g1_tts_bridge__srv__TTS_Request__Sequence__destroy(g1_tts_bridge__srv__TTS_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    g1_tts_bridge__srv__TTS_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
g1_tts_bridge__srv__TTS_Request__Sequence__are_equal(const g1_tts_bridge__srv__TTS_Request__Sequence * lhs, const g1_tts_bridge__srv__TTS_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!g1_tts_bridge__srv__TTS_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
g1_tts_bridge__srv__TTS_Request__Sequence__copy(
  const g1_tts_bridge__srv__TTS_Request__Sequence * input,
  g1_tts_bridge__srv__TTS_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(g1_tts_bridge__srv__TTS_Request);
    g1_tts_bridge__srv__TTS_Request * data =
      (g1_tts_bridge__srv__TTS_Request *)realloc(output->data, allocation_size);
    if (!data) {
      return false;
    }
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!g1_tts_bridge__srv__TTS_Request__init(&data[i])) {
        /* free currently allocated and return false */
        for (; i-- > output->capacity; ) {
          g1_tts_bridge__srv__TTS_Request__fini(&data[i]);
        }
        free(data);
        return false;
      }
    }
    output->data = data;
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!g1_tts_bridge__srv__TTS_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
g1_tts_bridge__srv__TTS_Response__init(g1_tts_bridge__srv__TTS_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    g1_tts_bridge__srv__TTS_Response__fini(msg);
    return false;
  }
  return true;
}

void
g1_tts_bridge__srv__TTS_Response__fini(g1_tts_bridge__srv__TTS_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
g1_tts_bridge__srv__TTS_Response__are_equal(const g1_tts_bridge__srv__TTS_Response * lhs, const g1_tts_bridge__srv__TTS_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
g1_tts_bridge__srv__TTS_Response__copy(
  const g1_tts_bridge__srv__TTS_Response * input,
  g1_tts_bridge__srv__TTS_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

g1_tts_bridge__srv__TTS_Response *
g1_tts_bridge__srv__TTS_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  g1_tts_bridge__srv__TTS_Response * msg = (g1_tts_bridge__srv__TTS_Response *)allocator.allocate(sizeof(g1_tts_bridge__srv__TTS_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(g1_tts_bridge__srv__TTS_Response));
  bool success = g1_tts_bridge__srv__TTS_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
g1_tts_bridge__srv__TTS_Response__destroy(g1_tts_bridge__srv__TTS_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    g1_tts_bridge__srv__TTS_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
g1_tts_bridge__srv__TTS_Response__Sequence__init(g1_tts_bridge__srv__TTS_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  g1_tts_bridge__srv__TTS_Response * data = NULL;

  if (size) {
    data = (g1_tts_bridge__srv__TTS_Response *)allocator.zero_allocate(size, sizeof(g1_tts_bridge__srv__TTS_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = g1_tts_bridge__srv__TTS_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        g1_tts_bridge__srv__TTS_Response__fini(&data[i - 1]);
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
g1_tts_bridge__srv__TTS_Response__Sequence__fini(g1_tts_bridge__srv__TTS_Response__Sequence * array)
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
      g1_tts_bridge__srv__TTS_Response__fini(&array->data[i]);
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

g1_tts_bridge__srv__TTS_Response__Sequence *
g1_tts_bridge__srv__TTS_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  g1_tts_bridge__srv__TTS_Response__Sequence * array = (g1_tts_bridge__srv__TTS_Response__Sequence *)allocator.allocate(sizeof(g1_tts_bridge__srv__TTS_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = g1_tts_bridge__srv__TTS_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
g1_tts_bridge__srv__TTS_Response__Sequence__destroy(g1_tts_bridge__srv__TTS_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    g1_tts_bridge__srv__TTS_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
g1_tts_bridge__srv__TTS_Response__Sequence__are_equal(const g1_tts_bridge__srv__TTS_Response__Sequence * lhs, const g1_tts_bridge__srv__TTS_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!g1_tts_bridge__srv__TTS_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
g1_tts_bridge__srv__TTS_Response__Sequence__copy(
  const g1_tts_bridge__srv__TTS_Response__Sequence * input,
  g1_tts_bridge__srv__TTS_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(g1_tts_bridge__srv__TTS_Response);
    g1_tts_bridge__srv__TTS_Response * data =
      (g1_tts_bridge__srv__TTS_Response *)realloc(output->data, allocation_size);
    if (!data) {
      return false;
    }
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!g1_tts_bridge__srv__TTS_Response__init(&data[i])) {
        /* free currently allocated and return false */
        for (; i-- > output->capacity; ) {
          g1_tts_bridge__srv__TTS_Response__fini(&data[i]);
        }
        free(data);
        return false;
      }
    }
    output->data = data;
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!g1_tts_bridge__srv__TTS_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
