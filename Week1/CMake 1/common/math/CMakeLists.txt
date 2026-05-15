aux_source_directory(src Math_DIR)

add_library(math STATIC ${Math_DIR})

target_include_directories(math
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(math
    PUBLIC
        kalman
)
