aux_source_directory(src M2_DIR)

add_library(M2 STATIC ${M2_DIR})

target_include_directories(M2
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(M2
    PUBLIC
        A1
        A2
        kalman
)
