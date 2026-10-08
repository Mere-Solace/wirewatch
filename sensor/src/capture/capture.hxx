#pragma once
#include <pcapplusplus/PcapLiveDevice.h>

namespace wirewatch {
	
	bool capturePackets(pcpp::PcapLiveDevice* dev, int maxPackets, double timeoutSec);

} // namespace wirewatch