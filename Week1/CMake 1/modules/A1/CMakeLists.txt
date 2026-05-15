aux_source_directory(src A1_DIR)

add_library(A1 STATIC ${A1_DIR})

target_include_directories(A1
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/include
)
