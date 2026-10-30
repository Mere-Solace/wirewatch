cmake_minimum_required(VERSION 3.20)

# the vcpkg toolchain must be set before project(), otherwise
# find_package can't see anything vcpkg installed.
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE AND DEFINED ENV{VCPKG_ROOT})
	set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
endif()

project(wirewatch LANGUAGES CXX)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_CXX_STANDARD 20)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(PYBIND11_FINDPYTHON ON)

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
find_package(nlohmann_json 
	CONFIG 
	REQUIRED
)

# 
set(CMAKE_POSITION_INDEPENDENT_CODE ON) 

add_subdirectory(src/core)
add_subdirectory(src/capture)
add_subdirectory(src/app)


find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY
)

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_wirewatch src/bindings.cxx)

target_link_libraries(_wirewatch PRIVATE capture core)

# scikit-build-core sets SKBUILD; install() is how the module 
# gets into the wheel. 
# plain cmake builds keep dropping it next to the python sources.
if(SKBUILD)
	install(TARGETS _wirewatch LIBRARY DESTINATION wirewatch/backend)
else()
	set_target_properties(_wirewatch PROPERTIES
	    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../src/wirewatch/backend"
	)
endif()
