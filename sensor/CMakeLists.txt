cmake_minimum_required(VERSION 3.20)
project(wirewatch CXX)
set(CMAKE_CXX_STANDARD 20)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_subdirectory(src/core)
add_subdirectory(src/capture)
add_subdirectory(src/app)