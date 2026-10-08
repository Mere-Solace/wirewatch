#include <iostream>
#include <pcapplusplus/PcapLiveDeviceList.h>

#include <capture.hxx>

int main(int argc, char *argv[]) {
  for (auto *dev: pcpp::PcapLiveDeviceList::getInstance().getPcapLiveDevicesList()) {
    std::cout <<  dev->getName() << "  " << dev->getDesc() << "\n--------------------\n";
  }

  if (argc < 2) {
    return 1;
  }

  pcpp::PcapLiveDevice* dev = 
    pcpp::PcapLiveDeviceList::getInstance().getDeviceByName(argv[1]);

  if (!dev) {
    std::cerr << "No such interface: " << argv[1] << "\n";
    return 1;
  }

  if (!dev->open()) {
    std::cerr << "Unable to open device (need root or setcap?)\n";
    return 1;
  }

  dev->setFilter("tcp");

  std::cout << "\ndevice ipv4: " << dev->getIPv4Address() << "\n";

  wirewatch::capturePackets(dev, 100, 10);

  return 0;
}
