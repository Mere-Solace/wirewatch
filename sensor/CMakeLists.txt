cmake_minimum_required(VERSION 3.20)
project(wirewatch C CXX)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_CXX_STANDARD 20)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# find packages must come before calling 
# add_subdirectory on a dir that needs the package.
find_package(PcapPlusPlus
	CONFIG 
	REQUIRED
)
find_package(fmt
	CONFIG
	REQUIRED
)

add_subdirectory(src/core)
add_subdirectory(src/capture)
add_subdirectory(src/app)

