// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from g1_tts_bridge:srv/TTS.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "g1_tts_bridge/srv/detail/tts__rosidl_typesupport_introspection_c.h"
#include "g1_tts_bridge/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "g1_tts_bridge/srv/detail/tts__functions.h"
#include "g1_tts_bridge/srv/detail/tts__struct.h"


// Include directives for member types
// Member `text`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  g1_tts_bridge__srv__TTS_Request__init(message_memory);
}

void TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_fini_function(void * message_memory)
{
  g1_tts_bridge__srv__TTS_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_member_array[2] = {
  {
    "text",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(g1_tts_bridge__srv__TTS_Request, text),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "speaker_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(g1_tts_bridge__srv__TTS_Request, speaker_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_members = {
  "g1_tts_bridge__srv",  // message namespace
  "TTS_Request",  // message name
  2,  // number of fields
  sizeof(g1_tts_bridge__srv__TTS_Request),
  TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_member_array,  // message members
  TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_type_support_handle = {
  0,
  &TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_g1_tts_bridge
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Request)() {
  if (!TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_type_support_handle.typesupport_identifier) {
    TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &TTS_Request__rosidl_typesupport_introspection_c__TTS_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "g1_tts_bridge/srv/detail/tts__rosidl_typesupport_introspection_c.h"
// already included above
// #include "g1_tts_bridge/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "g1_tts_bridge/srv/detail/tts__functions.h"
// already included above
// #include "g1_tts_bridge/srv/detail/tts__struct.h"


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  g1_tts_bridge__srv__TTS_Response__init(message_memory);
}

void TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_fini_function(void * message_memory)
{
  g1_tts_bridge__srv__TTS_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_member_array[2] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(g1_tts_bridge__srv__TTS_Response, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(g1_tts_bridge__srv__TTS_Response, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_members = {
  "g1_tts_bridge__srv",  // message namespace
  "TTS_Response",  // message name
  2,  // number of fields
  sizeof(g1_tts_bridge__srv__TTS_Response),
  TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_member_array,  // message members
  TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_type_support_handle = {
  0,
  &TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_g1_tts_bridge
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Response)() {
  if (!TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_type_support_handle.typesupport_identifier) {
    TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &TTS_Response__rosidl_typesupport_introspection_c__TTS_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "g1_tts_bridge/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "g1_tts_bridge/srv/detail/tts__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_service_members = {
  "g1_tts_bridge__srv",  // service namespace
  "TTS",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_Request_message_type_support_handle,
  NULL  // response message
  // g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_Response_message_type_support_handle
};

static rosidl_service_type_support_t g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_service_type_support_handle = {
  0,
  &g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_g1_tts_bridge
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS)() {
  if (!g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_service_type_support_handle.typesupport_identifier) {
    g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Response)()->data;
  }

  return &g1_tts_bridge__srv__detail__tts__rosidl_typesupport_introspection_c__TTS_service_type_support_handle;
}
