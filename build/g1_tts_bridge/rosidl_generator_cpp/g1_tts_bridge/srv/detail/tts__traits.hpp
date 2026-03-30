// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from g1_tts_bridge:srv/TTS.idl
// generated code does not contain a copyright notice

#ifndef G1_TTS_BRIDGE__SRV__DETAIL__TTS__TRAITS_HPP_
#define G1_TTS_BRIDGE__SRV__DETAIL__TTS__TRAITS_HPP_

#include "g1_tts_bridge/srv/detail/tts__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<g1_tts_bridge::srv::TTS_Request>()
{
  return "g1_tts_bridge::srv::TTS_Request";
}

template<>
inline const char * name<g1_tts_bridge::srv::TTS_Request>()
{
  return "g1_tts_bridge/srv/TTS_Request";
}

template<>
struct has_fixed_size<g1_tts_bridge::srv::TTS_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<g1_tts_bridge::srv::TTS_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<g1_tts_bridge::srv::TTS_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<g1_tts_bridge::srv::TTS_Response>()
{
  return "g1_tts_bridge::srv::TTS_Response";
}

template<>
inline const char * name<g1_tts_bridge::srv::TTS_Response>()
{
  return "g1_tts_bridge/srv/TTS_Response";
}

template<>
struct has_fixed_size<g1_tts_bridge::srv::TTS_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<g1_tts_bridge::srv::TTS_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<g1_tts_bridge::srv::TTS_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<g1_tts_bridge::srv::TTS>()
{
  return "g1_tts_bridge::srv::TTS";
}

template<>
inline const char * name<g1_tts_bridge::srv::TTS>()
{
  return "g1_tts_bridge/srv/TTS";
}

template<>
struct has_fixed_size<g1_tts_bridge::srv::TTS>
  : std::integral_constant<
    bool,
    has_fixed_size<g1_tts_bridge::srv::TTS_Request>::value &&
    has_fixed_size<g1_tts_bridge::srv::TTS_Response>::value
  >
{
};

template<>
struct has_bounded_size<g1_tts_bridge::srv::TTS>
  : std::integral_constant<
    bool,
    has_bounded_size<g1_tts_bridge::srv::TTS_Request>::value &&
    has_bounded_size<g1_tts_bridge::srv::TTS_Response>::value
  >
{
};

template<>
struct is_service<g1_tts_bridge::srv::TTS>
  : std::true_type
{
};

template<>
struct is_service_request<g1_tts_bridge::srv::TTS_Request>
  : std::true_type
{
};

template<>
struct is_service_response<g1_tts_bridge::srv::TTS_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // G1_TTS_BRIDGE__SRV__DETAIL__TTS__TRAITS_HPP_
