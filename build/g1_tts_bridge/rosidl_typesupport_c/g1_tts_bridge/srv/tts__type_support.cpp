// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from g1_tts_bridge:srv/TTS.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "g1_tts_bridge/msg/rosidl_typesupport_c__visibility_control.h"
#include "g1_tts_bridge/srv/detail/tts__struct.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace g1_tts_bridge
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _TTS_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _TTS_Request_type_support_ids_t;

static const _TTS_Request_type_support_ids_t _TTS_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _TTS_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _TTS_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _TTS_Request_type_support_symbol_names_t _TTS_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, g1_tts_bridge, srv, TTS_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Request)),
  }
};

typedef struct _TTS_Request_type_support_data_t
{
  void * data[2];
} _TTS_Request_type_support_data_t;

static _TTS_Request_type_support_data_t _TTS_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _TTS_Request_message_typesupport_map = {
  2,
  "g1_tts_bridge",
  &_TTS_Request_message_typesupport_ids.typesupport_identifier[0],
  &_TTS_Request_message_typesupport_symbol_names.symbol_name[0],
  &_TTS_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t TTS_Request_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_TTS_Request_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace g1_tts_bridge

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_C_EXPORT_g1_tts_bridge
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, g1_tts_bridge, srv, TTS_Request)() {
  return &::g1_tts_bridge::srv::rosidl_typesupport_c::TTS_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "g1_tts_bridge/msg/rosidl_typesupport_c__visibility_control.h"
// already included above
// #include "g1_tts_bridge/srv/detail/tts__struct.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace g1_tts_bridge
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _TTS_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _TTS_Response_type_support_ids_t;

static const _TTS_Response_type_support_ids_t _TTS_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _TTS_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _TTS_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _TTS_Response_type_support_symbol_names_t _TTS_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, g1_tts_bridge, srv, TTS_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS_Response)),
  }
};

typedef struct _TTS_Response_type_support_data_t
{
  void * data[2];
} _TTS_Response_type_support_data_t;

static _TTS_Response_type_support_data_t _TTS_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _TTS_Response_message_typesupport_map = {
  2,
  "g1_tts_bridge",
  &_TTS_Response_message_typesupport_ids.typesupport_identifier[0],
  &_TTS_Response_message_typesupport_symbol_names.symbol_name[0],
  &_TTS_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t TTS_Response_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_TTS_Response_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace g1_tts_bridge

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_C_EXPORT_g1_tts_bridge
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, g1_tts_bridge, srv, TTS_Response)() {
  return &::g1_tts_bridge::srv::rosidl_typesupport_c::TTS_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "g1_tts_bridge/msg/rosidl_typesupport_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/service_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace g1_tts_bridge
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _TTS_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _TTS_type_support_ids_t;

static const _TTS_type_support_ids_t _TTS_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _TTS_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _TTS_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _TTS_type_support_symbol_names_t _TTS_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, g1_tts_bridge, srv, TTS)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, g1_tts_bridge, srv, TTS)),
  }
};

typedef struct _TTS_type_support_data_t
{
  void * data[2];
} _TTS_type_support_data_t;

static _TTS_type_support_data_t _TTS_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _TTS_service_typesupport_map = {
  2,
  "g1_tts_bridge",
  &_TTS_service_typesupport_ids.typesupport_identifier[0],
  &_TTS_service_typesupport_symbol_names.symbol_name[0],
  &_TTS_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t TTS_service_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_TTS_service_typesupport_map),
  rosidl_typesupport_c__get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace g1_tts_bridge

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_C_EXPORT_g1_tts_bridge
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_c, g1_tts_bridge, srv, TTS)() {
  return &::g1_tts_bridge::srv::rosidl_typesupport_c::TTS_service_type_support_handle;
}

#ifdef __cplusplus
}
#endif
