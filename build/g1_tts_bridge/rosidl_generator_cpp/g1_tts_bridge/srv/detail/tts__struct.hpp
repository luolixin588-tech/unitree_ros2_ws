// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from g1_tts_bridge:srv/TTS.idl
// generated code does not contain a copyright notice

#ifndef G1_TTS_BRIDGE__SRV__DETAIL__TTS__STRUCT_HPP_
#define G1_TTS_BRIDGE__SRV__DETAIL__TTS__STRUCT_HPP_

#include <rosidl_runtime_cpp/bounded_vector.hpp>
#include <rosidl_runtime_cpp/message_initialization.hpp>
#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>


#ifndef _WIN32
# define DEPRECATED__g1_tts_bridge__srv__TTS_Request __attribute__((deprecated))
#else
# define DEPRECATED__g1_tts_bridge__srv__TTS_Request __declspec(deprecated)
#endif

namespace g1_tts_bridge
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct TTS_Request_
{
  using Type = TTS_Request_<ContainerAllocator>;

  explicit TTS_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->text = "";
      this->speaker_id = 0l;
    }
  }

  explicit TTS_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : text(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->text = "";
      this->speaker_id = 0l;
    }
  }

  // field types and members
  using _text_type =
    std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other>;
  _text_type text;
  using _speaker_id_type =
    int32_t;
  _speaker_id_type speaker_id;

  // setters for named parameter idiom
  Type & set__text(
    const std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other> & _arg)
  {
    this->text = _arg;
    return *this;
  }
  Type & set__speaker_id(
    const int32_t & _arg)
  {
    this->speaker_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    g1_tts_bridge::srv::TTS_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const g1_tts_bridge::srv::TTS_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      g1_tts_bridge::srv::TTS_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      g1_tts_bridge::srv::TTS_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__g1_tts_bridge__srv__TTS_Request
    std::shared_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__g1_tts_bridge__srv__TTS_Request
    std::shared_ptr<g1_tts_bridge::srv::TTS_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TTS_Request_ & other) const
  {
    if (this->text != other.text) {
      return false;
    }
    if (this->speaker_id != other.speaker_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const TTS_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TTS_Request_

// alias to use template instance with default allocator
using TTS_Request =
  g1_tts_bridge::srv::TTS_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace g1_tts_bridge


#ifndef _WIN32
# define DEPRECATED__g1_tts_bridge__srv__TTS_Response __attribute__((deprecated))
#else
# define DEPRECATED__g1_tts_bridge__srv__TTS_Response __declspec(deprecated)
#endif

namespace g1_tts_bridge
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct TTS_Response_
{
  using Type = TTS_Response_<ContainerAllocator>;

  explicit TTS_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit TTS_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    g1_tts_bridge::srv::TTS_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const g1_tts_bridge::srv::TTS_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      g1_tts_bridge::srv::TTS_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      g1_tts_bridge::srv::TTS_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__g1_tts_bridge__srv__TTS_Response
    std::shared_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__g1_tts_bridge__srv__TTS_Response
    std::shared_ptr<g1_tts_bridge::srv::TTS_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TTS_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const TTS_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TTS_Response_

// alias to use template instance with default allocator
using TTS_Response =
  g1_tts_bridge::srv::TTS_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace g1_tts_bridge

namespace g1_tts_bridge
{

namespace srv
{

struct TTS
{
  using Request = g1_tts_bridge::srv::TTS_Request;
  using Response = g1_tts_bridge::srv::TTS_Response;
};

}  // namespace srv

}  // namespace g1_tts_bridge

#endif  // G1_TTS_BRIDGE__SRV__DETAIL__TTS__STRUCT_HPP_
