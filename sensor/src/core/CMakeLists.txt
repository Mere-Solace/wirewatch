add_library(core)

target_sources(core
	PRIVATE 
		packet.c
		
	PUBLIC
	FILE_SET HEADERS
		FILES
			packet.h
)