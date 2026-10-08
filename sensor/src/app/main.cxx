#include <iostream>
#include <pcapplusplus/PcapLiveDeviceList.h>

#include <capture.hxx>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
// Npcap installs to System32\Npcap, which isn't on the DLL search path
// unless it was installed in WinPcap-compatible mode.
static bool loadNpcap() {
  char dir[MAX_PATH];
  UINT len = GetSystemDirectoryA(dir, MAX_PATH);
  if (len == 0 || len >= MAX_PATH) {
    return false;
  }
  strcat_s(dir, "\\Npcap");
  SetDllDirectoryA(dir);
  return LoadLibraryA("wpcap.dll") != nullptr;
}
#endif

int main(int argc, char *argv[]) {
  #ifdef _WIN32
  if (!loadNpcap()) {
    std::cerr << "Npcap not found. Install it from https://npcap.com\n";
    return 1;
  }
  #endif

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
