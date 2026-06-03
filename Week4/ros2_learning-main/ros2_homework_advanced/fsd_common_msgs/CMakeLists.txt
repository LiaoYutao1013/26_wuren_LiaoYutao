cmake_minimum_required(VERSION 3.8)
project(fsd_common_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# rosidl_default_generators 用于根据 .idl/.msg 文件生成 C++/Python 等语言接口。
find_package(rosidl_default_generators REQUIRED)

# Cone 和 Map 消息字段引用了 std_msgs/Header 和 geometry_msgs/Point。
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

set(MSG_FILES
  "msg/Cone.idl"
  "msg/Map.idl"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${MSG_FILES}
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
