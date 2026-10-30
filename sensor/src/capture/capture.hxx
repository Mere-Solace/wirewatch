#pragma once

#include <pcapplusplus/PcapLiveDevice.h>

#include <packet.hxx>

namespace wirewatch {
	
	std::vector<std::pair<std::string, std::string>> listDevices();

	bool capturePackets(const std::string devName, int maxPackets, int timeoutSeconds);

	bool capturePackets(pcpp::PcapLiveDevice* dev, int maxPackets, int timeoutSeconds);

} // namespace wirewatch