cmake_minimum_required(VERSION 3.5)
project(g1_tts_bridge)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 1. 查找 ROS 2 依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# 2. 尝试查找 Unitree SDK
# 即使这行报错，我们下面也有备用方案，所以这里加 QUIET 可选
find_package(unitree_sdk2 QUIET)

# 【核心修改 1】暴力指定头文件路径
# 不管 find_package 有没有成功，我都告诉编译器去这里找头文件
include_directories(
  include
  /usr/local/include
  /opt/unitree_robotics/include
)

# 3. 生成接口
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/TTS.srv"
  DEPENDENCIES std_msgs
)

# 4. 编译 ROS 服务节点
add_executable(g1_tts_service src/g1_tts_service.cpp)
target_include_directories(g1_tts_service PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(g1_tts_service rclcpp std_msgs)
target_link_libraries(g1_tts_service unitree_sdk2)
rosidl_target_interfaces(g1_tts_service
  ${PROJECT_NAME} "rosidl_typesupport_cpp")

# 5. 编译独立 CLI 工具（纯 SDK，不依赖 ROS，避免 DDS 冲突）
add_executable(g1_tts_cli src/g1_tts_cli.cpp)
target_include_directories(g1_tts_cli PUBLIC
  /usr/local/include
  /opt/unitree_robotics/include
)
target_link_libraries(g1_tts_cli unitree_sdk2)

# 6. 安装规则
install(TARGETS g1_tts_service g1_tts_cli
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY srv
  DESTINATION share/${PROJECT_NAME}
)

ament_package()