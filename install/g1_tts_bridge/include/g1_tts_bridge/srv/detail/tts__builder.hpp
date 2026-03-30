// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from g1_tts_bridge:srv/TTS.idl
// generated code does not contain a copyright notice

#ifndef G1_TTS_BRIDGE__SRV__DETAIL__TTS__BUILDER_HPP_
#define G1_TTS_BRIDGE__SRV__DETAIL__TTS__BUILDER_HPP_

#include "g1_tts_bridge/srv/detail/tts__struct.hpp"
#include <rosidl_runtime_cpp/message_initialization.hpp>
#include <algorithm>
#include <utility>


namespace g1_tts_bridge
{

namespace srv
{

namespace builder
{

class Init_TTS_Request_speaker_id
{
public:
  explicit Init_TTS_Request_speaker_id(::g1_tts_bridge::srv::TTS_Request & msg)
  : msg_(msg)
  {}
  ::g1_tts_bridge::srv::TTS_Request speaker_id(::g1_tts_bridge::srv::TTS_Request::_speaker_id_type arg)
  {
    msg_.speaker_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::g1_tts_bridge::srv::TTS_Request msg_;
};

class Init_TTS_Request_text
{
public:
  Init_TTS_Request_text()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TTS_Request_speaker_id text(::g1_tts_bridge::srv::TTS_Request::_text_type arg)
  {
    msg_.text = std::move(arg);
    return Init_TTS_Request_speaker_id(msg_);
  }

private:
  ::g1_tts_bridge::srv::TTS_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::g1_tts_bridge::srv::TTS_Request>()
{
  return g1_tts_bridge::srv::builder::Init_TTS_Request_text();
}

}  // namespace g1_tts_bridge


namespace g1_tts_bridge
{

namespace srv
{

namespace builder
{

class Init_TTS_Response_message
{
public:
  explicit Init_TTS_Response_message(::g1_tts_bridge::srv::TTS_Response & msg)
  : msg_(msg)
  {}
  ::g1_tts_bridge::srv::TTS_Response message(::g1_tts_bridge::srv::TTS_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::g1_tts_bridge::srv::TTS_Response msg_;
};

class Init_TTS_Response_success
{
public:
  Init_TTS_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TTS_Response_message success(::g1_tts_bridge::srv::TTS_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_TTS_Response_message(msg_);
  }

private:
  ::g1_tts_bridge::srv::TTS_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::g1_tts_bridge::srv::TTS_Response>()
{
  return g1_tts_bridge::srv::builder::Init_TTS_Response_success();
}

}  // namespace g1_tts_bridge

#endif  // G1_TTS_BRIDGE__SRV__DETAIL__TTS__BUILDER_HPP_
