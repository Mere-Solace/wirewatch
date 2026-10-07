add_library(capture)
target_include_directories(capture PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

if(WIN32)
    target_sources(capture PRIVATE capture_windows.cpp)
elseif(APPLE)
    target_sources(capture PRIVATE capture_macos.cpp)
elseif(UNIX)
    target_sources(capture PRIVATE capture_linux.cpp)
endif()

target_link_libraries(capture PUBLIC core)