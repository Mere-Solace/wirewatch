#include <iostream>
#include <pcapplusplus/PcapLiveDeviceList.h>


int main(int argc, char *argv[]) {
  for (auto *dev: pcpp::PcapLiveDeviceList::getInstance().getPcapLiveDevicesList()) {
    std::cout <<  dev->getName() << "  " << dev->getDesc() << "\n";
  }

    return 0;
}
