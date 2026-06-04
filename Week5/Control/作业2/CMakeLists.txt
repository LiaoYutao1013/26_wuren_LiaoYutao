cmake_minimum_required(VERSION 3.20)

project(robot_dog_optimization LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Eigen3 CONFIG QUIET)

if(NOT Eigen3_FOUND)
  include(FetchContent)
  FetchContent_Declare(
    eigen
    URL https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
  )
  FetchContent_MakeAvailable(eigen)
endif()

add_executable(robot_dog_optimization
  src/main.cpp
)

if(TARGET Eigen3::Eigen)
  target_link_libraries(robot_dog_optimization PRIVATE Eigen3::Eigen)
elseif(DEFINED Eigen3_INCLUDE_DIRS)
  target_include_directories(robot_dog_optimization PRIVATE ${Eigen3_INCLUDE_DIRS})
elseif(DEFINED EIGEN3_INCLUDE_DIR)
  target_include_directories(robot_dog_optimization PRIVATE ${EIGEN3_INCLUDE_DIR})
else()
  target_include_directories(robot_dog_optimization PRIVATE ${eigen_SOURCE_DIR})
endif()
