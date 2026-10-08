add_executable(sensor)

target_sources(sensor
  PRIVATE
		main.cxx
)

target_link_libraries(sensor 
	PRIVATE
		fmt::fmt
)
