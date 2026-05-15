aux_source_directory(src A2_DIR)

add_library(A2 STATIC ${A2_DIR})

target_include_directories(A2
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/include
)
