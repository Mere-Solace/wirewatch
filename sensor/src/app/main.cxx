#include <cstdlib>
#include <iostream>
#include <csignal>
#include <pcapplusplus/PcapLiveDeviceList.h>
// =========================================
// This implementation uses Pcap++.
// Please refer to 
// https://pcapplusplus.github.io/api-docs/v26.07/
// ========================================= 

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

// expection to the global variable avoidance rule - used for interruption.
volatile std::sig_atomic_t stop{0};

extern "C" void handler(int signal){
  (void)signal;
  stop = 1;
}

// Command Line arguments: 
// $ sensor <device_name> <max_packets> <timeout_milliseconds>
//  
int main(int argc, char *argv[]) {
  #ifdef _WIN32
  if (!loadNpcap()) {
    std::cerr << "Npcap not found. Install it from https://npcap.com\n";
    return 1;
  }
  #endif

  if (argc < 4) { // for now, need 
    return 1;
  }

  std::string devName = argv[1];
  int maxPackets = atoi(argv[2]);
  int timeoutSeconds = atoi(argv[3]);


  std::cerr << "blocking capture has begun." << std::endl;

  wirewatch::capturePackets(devName, maxPackets, timeoutSeconds);


  struct sigaction sigIntAction{};
  sigIntAction.sa_handler = handler;
  sigemptyset(&sigIntAction.sa_mask);
  sigIntAction.sa_flags = 0;
  sigaction(SIGINT, &sigIntAction, nullptr);

  return 0;
}
