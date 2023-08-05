cmake_minimum_required(VERSION 3.1)
project(leddar_utils_lcax LANGUAGES C)
add_library(leddar_utils_lcax SHARED mathematics.c )

if(UNIX)
    target_compile_options(leddar_utils_lcax PRIVATE -fPIC -Wall -Wextra -O2 -g )
elseif(WIN32)
    target_compile_definitions(leddar_utils_lcax PRIVATE -D_USE_CVI_GUI -D_DLL_EXPORT)
endif()

target_compile_definitions(leddar_utils_lcax PRIVATE -D_LCA3_MEMS)
target_include_directories(leddar_utils_lcax PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

