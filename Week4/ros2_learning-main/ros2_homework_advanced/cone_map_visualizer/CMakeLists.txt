# cone_map_visualizer 的 CMake 构建脚本。
# 该包编译一个 C++ ROS2 节点，并安装 launch、rviz 和示例 bag 资源。

cmake_minimum_required(VERSION 3.8)
project(cone_map_visualizer)

# 对 GCC/Clang 开启常用告警，帮助发现潜在 C++ 代码问题。
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找构建和运行所需的 ROS2 包。
find_package(ament_cmake REQUIRED)
find_package(fsd_common_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

# 定义可执行文件，源文件是 src/cone_map_visualizer.cpp。
add_executable(cone_map_visualizer src/cone_map_visualizer.cpp)

# 使用 C++17，满足现代 rclcpp 和代码风格需求。
target_compile_features(cone_map_visualizer PUBLIC cxx_std_17)

# 声明目标依赖，ament 会自动补全 include 路径和链接库。
ament_target_dependencies(
  cone_map_visualizer
  fsd_common_msgs
  rclcpp
  std_msgs
  visualization_msgs
)

# 安装可执行文件到 lib/${PROJECT_NAME}，这样 ros2 run 能找到它。
install(TARGETS
  cone_map_visualizer
  DESTINATION lib/${PROJECT_NAME}
)

# 安装 launch 和 rviz 目录，运行 ros2 launch 时会从 share 目录读取。
install(DIRECTORY launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# 安装作业提供的 rosbag 数据，launch 默认从这里播放锥桶地图。
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../map_to_visualize
  DESTINATION share/${PROJECT_NAME}
)

# BUILD_TESTING 开启时运行 ament lint；这里跳过版权和 cpplint 的强制检查。
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# 生成 ament 包元信息，必须放在 CMakeLists.txt 末尾附近。
ament_package()
