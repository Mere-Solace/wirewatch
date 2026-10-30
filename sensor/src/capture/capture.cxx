#include <ProtocolType.h>
#include <iostream>
#include <nlohmann/json_fwd.hpp>
#include <ostream>
#include <pcapplusplus/Layer.h>
#include <pcapplusplus/PcapLiveDeviceList.h>
#include <pcapplusplus/PcapLiveDevice.h>
#include <pcapplusplus/PcapFileDevice.h>
#include <pcapplusplus/RawPacket.h>
#include <pcapplusplus/Packet.h>
#include <pcapplusplus/IPv4Layer.h>
#include <pcapplusplus/TcpLayer.h>
#include <nlohmann/json.hpp>

#include <capture.hxx>
#include <string>


namespace wirewatch {

	std::vector<std::pair<std::string, std::string>> listDevices() {
		std::vector<std::pair<std::string, std::string>> devices{};

		for (auto *dev: pcpp::PcapLiveDeviceList::getInstance().getPcapLiveDevicesList()) {
			devices.push_back(std::make_pair(dev->getName(), dev->getDesc()));
		}

		return devices;
	}

	bool capturePackets(pcpp::PcapLiveDevice* dev, const int maxPackets, const int timeoutSeconds) {
		int count = 0;	

		if (!dev) {
			std::cerr << "that device does not exist.";
			return 1;
		}

		if (!dev->open()) {
			std::cerr << "Unable to open device (need root or setcap?)\n";
			return 1;
		}

		dev->setFilter("tcp");

		int returnCode = dev->startCaptureBlockingMode(
			[&](pcpp::RawPacket* raw, pcpp::PcapLiveDevice*, void*) {
				pcpp::Packet packet{raw};

				const auto* IPv4Layer = packet.getLayerOfType<pcpp::IPv4Layer>();
				// const auto* IPv6Layer = packet.getLayerOfType<pcpp::IPv6>();
				if (!IPv4Layer) {
					return false;
				}

				nlohmann::json jsonObject{};

				jsonObject["src"] = IPv4Layer->getSrcIPAddress().toString();
				jsonObject["dst"] = IPv4Layer->getDstIPAddress().toString();
				jsonObject["frame_len"] = raw->getFrameLength();
				jsonObject["cap_len"] = raw->getRawDataLen();
				jsonObject["tv_sec"] = raw->getPacketTimeStamp().tv_sec;
				jsonObject["tv_nsec"] = raw->getPacketTimeStamp().tv_nsec;
			
				std::cout << jsonObject.dump() << std::endl;

				return count >= maxPackets;
	 		},
	 		nullptr, timeoutSeconds);

			dev->close();

		return returnCode != 0; 
	}

	bool capturePackets(const std::string devName, const int maxPackets, const int timeoutSeconds) {
		pcpp::PcapLiveDevice* dev = pcpp::PcapLiveDeviceList::getInstance().getDeviceByName(devName);
		
		if (!dev) {
			std::cerr << "No such interface: " << devName << "\n";
			return 1;
		}

		return capturePackets(dev, maxPackets, timeoutSeconds);
	}
} // namespace wirewatch 