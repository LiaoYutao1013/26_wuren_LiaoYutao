cmake_minimum_required(VERSION 3.8)
project(cone_map_visualizer)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(fsd_common_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

add_executable(cone_map_visualizer src/cone_map_visualizer.cpp)

target_compile_features(cone_map_visualizer PUBLIC cxx_std_17)

ament_target_dependencies(
  cone_map_visualizer
  fsd_common_msgs
  rclcpp
  std_msgs
  visualization_msgs
)

install(TARGETS
  cone_map_visualizer
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch rviz
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../map_to_visualize
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
