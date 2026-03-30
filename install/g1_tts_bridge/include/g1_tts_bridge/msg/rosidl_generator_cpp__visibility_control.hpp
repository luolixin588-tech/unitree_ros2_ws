// generated from rosidl_generator_cpp/resource/rosidl_generator_cpp__visibility_control.hpp.in
// generated code does not contain a copyright notice

#ifndef G1_TTS_BRIDGE__MSG__ROSIDL_GENERATOR_CPP__VISIBILITY_CONTROL_HPP_
#define G1_TTS_BRIDGE__MSG__ROSIDL_GENERATOR_CPP__VISIBILITY_CONTROL_HPP_

#ifdef __cplusplus
extern "C"
{
#endif

// This logic was borrowed (then namespaced) from the examples on the gcc wiki:
//     https://gcc.gnu.org/wiki/Visibility

#if defined _WIN32 || defined __CYGWIN__
  #ifdef __GNUC__
    #define ROSIDL_GENERATOR_CPP_EXPORT_g1_tts_bridge __attribute__ ((dllexport))
    #define ROSIDL_GENERATOR_CPP_IMPORT_g1_tts_bridge __attribute__ ((dllimport))
  #else
    #define ROSIDL_GENERATOR_CPP_EXPORT_g1_tts_bridge __declspec(dllexport)
    #define ROSIDL_GENERATOR_CPP_IMPORT_g1_tts_bridge __declspec(dllimport)
  #endif
  #ifdef ROSIDL_GENERATOR_CPP_BUILDING_DLL_g1_tts_bridge
    #define ROSIDL_GENERATOR_CPP_PUBLIC_g1_tts_bridge ROSIDL_GENERATOR_CPP_EXPORT_g1_tts_bridge
  #else
    #define ROSIDL_GENERATOR_CPP_PUBLIC_g1_tts_bridge ROSIDL_GENERATOR_CPP_IMPORT_g1_tts_bridge
  #endif
#else
  #define ROSIDL_GENERATOR_CPP_EXPORT_g1_tts_bridge __attribute__ ((visibility("default")))
  #define ROSIDL_GENERATOR_CPP_IMPORT_g1_tts_bridge
  #if __GNUC__ >= 4
    #define ROSIDL_GENERATOR_CPP_PUBLIC_g1_tts_bridge __attribute__ ((visibility("default")))
  #else
    #define ROSIDL_GENERATOR_CPP_PUBLIC_g1_tts_bridge
  #endif
#endif

#ifdef __cplusplus
}
#endif

#endif  // G1_TTS_BRIDGE__MSG__ROSIDL_GENERATOR_CPP__VISIBILITY_CONTROL_HPP_
