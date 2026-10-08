# Wirewatch

A descriptive network health monitor that shows you why your network is slowing down.

Packet-level network health monitor. Captures traffic, measures network health, and provides descriptive reports and analysis. Explanations are in plain language and don't assume you already understand what's being shown.

---


## Quickstart

The sensor is C++20 and built with CMake. Its dependencies ([PcapPlusPlus](https://pcapplusplus.github.io/) and [fmt](https://fmt.dev/)) are installed automatically by [vcpkg](https://vcpkg.io/) the first time you configure.

### Linux / macOS

#### 1. Install the build tools

**Linux** (Debian/Ubuntu — use your distro's equivalents elsewhere):

```sh
sudo apt install build-essential git cmake curl zip unzip tar pkg-config bison flex
```

> `bison` and `flex` are needed to build libpcap.

**macOS** (with [Homebrew](https://brew.sh/)):

```sh
xcode-select --install
brew install cmake pkg-config
```

#### 2. Install vcpkg

Skip this if you already have vcpkg.

```sh
git clone https://github.com/microsoft/vcpkg ~/vcpkg
~/vcpkg/bootstrap-vcpkg.sh -disableMetrics
```

Then tell CMake where it is by adding this line to your shell config (`~/.bashrc` on most Linux distros, `~/.zshrc` on macOS) and opening a new terminal:

```sh
export VCPKG_ROOT="$HOME/vcpkg"
```

#### 3. Build

From the `sensor/` directory:

```sh
cmake --preset default
cmake --build build
```

The first configure takes a few minutes while vcpkg builds the dependencies. Later builds are cached.

> **Linux:** after linking, the build runs `sudo setcap` so the sensor can capture packets without running as root, so it may ask for your password. To skip that step, configure with `cmake --preset default -DWIREWATCH_SETCAP=OFF` and run the sensor with `sudo` instead.

#### 4. Run

```sh
./build/src/app/sensor            # list network interfaces
./build/src/app/sensor <iface>    # capture on an interface, e.g. eth0 or en0
```

> **macOS:** capturing requires access to `/dev/bpf*`. Run the sensor with `sudo`, or install Wireshark's *ChmodBPF* helper to capture as a regular user.

### Windows

_TBD._

<!--
Draft notes:
Compiler: Visual Studio 2026 Community with *Desktop Development with C++* workload
CMake: https://cmake.org/download/
Set VCPKG_ROOT:  $env:VCPKG_ROOT = "path to your vcpkg installation"
Then run:        cmake --preset default
-->

---
Currently in development 


Initialized for CS4622 (Computer Networks) at Kennesaw State University.

Team:

Capture & Metrics:

`Mere-Solace` -
`cjusino13`


Threat Detection:

`EvanMc1` -
`KaiJGlaza` -
`maitrip7`


Data & Dashboard:

`Aveon` -
`NanoFerreira`
