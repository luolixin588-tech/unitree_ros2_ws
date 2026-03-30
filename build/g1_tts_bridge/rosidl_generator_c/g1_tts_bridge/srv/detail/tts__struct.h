// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from g1_tts_bridge:srv/TTS.idl
// generated code does not contain a copyright notice

#ifndef G1_TTS_BRIDGE__SRV__DETAIL__TTS__STRUCT_H_
#define G1_TTS_BRIDGE__SRV__DETAIL__TTS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'text'
#include "rosidl_runtime_c/string.h"

// Struct defined in srv/TTS in the package g1_tts_bridge.
typedef struct g1_tts_bridge__srv__TTS_Request
{
  rosidl_runtime_c__String text;
  int32_t speaker_id;
} g1_tts_bridge__srv__TTS_Request;

// Struct for a sequence of g1_tts_bridge__srv__TTS_Request.
typedef struct g1_tts_bridge__srv__TTS_Request__Sequence
{
  g1_tts_bridge__srv__TTS_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} g1_tts_bridge__srv__TTS_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

// Struct defined in srv/TTS in the package g1_tts_bridge.
typedef struct g1_tts_bridge__srv__TTS_Response
{
  bool success;
  rosidl_runtime_c__String message;
} g1_tts_bridge__srv__TTS_Response;

// Struct for a sequence of g1_tts_bridge__srv__TTS_Response.
typedef struct g1_tts_bridge__srv__TTS_Response__Sequence
{
  g1_tts_bridge__srv__TTS_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} g1_tts_bridge__srv__TTS_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // G1_TTS_BRIDGE__SRV__DETAIL__TTS__STRUCT_H_
