#include <iostream>
#include <pcapplusplus/Layer.h>
#include <pcapplusplus/PcapLiveDevice.h>
#include <pcapplusplus/RawPacket.h>
#include <pcapplusplus/Packet.h>
#include <pcapplusplus/IPv4Layer.h>
#include <pcapplusplus/TcpLayer.h>

#include <capture.hxx>


namespace wirewatch {

	bool capturePackets(pcpp::PcapLiveDevice* dev, const int maxPackets, const double timeoutSec) {
		int count{0};
		int returnCode = dev->startCaptureBlockingMode(
			[&](pcpp::RawPacket* raw, pcpp::PcapLiveDevice*, void*) {
				pcpp::Packet packet{raw};
				std::cout << "\nPacket " << count << "\n" << packet.toString() << "\n";
				return ++count >= maxPackets;
	 		},
	 		nullptr, timeoutSec);

		return returnCode != 0; 
	}

} // namespace wirewatch