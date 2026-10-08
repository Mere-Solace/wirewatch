add_executable(sensor)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  option(WIREWATCH_SETCAP "Grant packet-capture capabilities to
		sensor after linking (uses sudo)" ON)
  if(WIREWATCH_SETCAP)
    add_custom_command(TARGET sensor POST_BUILD
      COMMAND ${CMAKE_COMMAND} -DBINARY=$<TARGET_FILE:sensor>
              -P ${PROJECT_SOURCE_DIR}/cmake/setcap.cmake
      COMMENT "Granting CAP_NET_RAW/CAP_NET_ADMIN to sensor"
      VERBATIM)
  endif()
endif()

target_sources(sensor
  PRIVATE
		main.cxx
)

target_link_libraries(sensor 
	PRIVATE
		capture
		fmt::fmt
)

if(WIN32)
  target_link_options(sensor
    PRIVATE
      "/DELAYLOAD:wpcap.dll"
      "/DELAYLOAD:Packet.dll"
  )
  target_link_libraries(sensor
    PRIVATE
      delayimp
  )
endif()
