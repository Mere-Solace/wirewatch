add_library(core)

target_sources(core
	PRIVATE 
		packet.cxx
		
	PUBLIC
	FILE_SET HEADERS
		FILES
			packet.hxx
)