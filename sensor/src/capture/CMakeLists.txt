add_library(capture)

target_link_libraries(capture
	PUBLIC 
		core
		PcapPlusPlus::Pcap++
		nlohmann_json::nlohmann_json
)

target_sources(capture
	PRIVATE
		capture.cxx

	PUBLIC
		FILE_SET HEADERS
		FILES
			capture.hxx
)