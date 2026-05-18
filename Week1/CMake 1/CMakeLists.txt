cmake_minimum_required(VERSION 3.19)

project(Test)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(FORCED_INCLUDE_HEADER "${CMAKE_BINARY_DIR}/cmake_forced_include.hpp")

file(WRITE "${FORCED_INCLUDE_HEADER}"
"#include <array>\n"
"#include <cstddef>\n"
"#include <cstdint>\n"
"#include <type_traits>\n"
)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-include "${FORCED_INCLUDE_HEADER}")
endif()

add_subdirectory(common)
add_subdirectory(modules)

add_executable(test main.cpp)

target_link_libraries(test
    PRIVATE
        M1
        M2
        math
)
