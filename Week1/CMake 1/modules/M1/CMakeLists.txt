aux_source_directory(src M1_DIR)

add_library(M1 STATIC ${M1_DIR})

target_include_directories(M1
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(M1
    PUBLIC
        A1
)
