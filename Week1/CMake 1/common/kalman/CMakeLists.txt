find_package(OpenCV REQUIRED)

add_library(kalman INTERFACE)

target_include_directories(kalman
    INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/include
        ${OpenCV_INCLUDE_DIRS}
)

target_link_libraries(kalman
    INTERFACE
        ${OpenCV_LIBS}
)
