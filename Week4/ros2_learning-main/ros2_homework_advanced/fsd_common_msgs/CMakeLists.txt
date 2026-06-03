# fsd_common_msgs 的接口生成构建脚本。
# 当前作业只生成 Cone.idl 和 Map.idl，其他 .msg 文件作为公共消息定义保留。

cmake_minimum_required(VERSION 3.8)
project(fsd_common_msgs)

# 对支持的编译器开启常用警告选项，便于接口生成和相关代码暴露问题。
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ament_cmake 提供 ROS2 CMake 包构建能力。
find_package(ament_cmake REQUIRED)

# rosidl_default_generators 用于根据 .idl/.msg 文件生成 C++/Python 等语言接口。
find_package(rosidl_default_generators REQUIRED)

# Cone 和 Map 消息字段引用了 std_msgs/Header 和 geometry_msgs/Point。
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# 当前实际参与 rosidl 生成的接口文件。
set(MSG_FILES
  "msg/Cone.idl"
  "msg/Map.idl"
)

# 生成本包消息接口，并声明字段中依赖到的外部消息包。
rosidl_generate_interfaces(${PROJECT_NAME}
  ${MSG_FILES}
  DEPENDENCIES std_msgs geometry_msgs
)

# 让依赖本包的其他包在运行期能找到生成后的消息类型。
ament_export_dependencies(rosidl_default_runtime)

# 注册 ament 包。
ament_package()
