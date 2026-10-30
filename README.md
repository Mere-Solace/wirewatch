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

**macOS:**

1. Install Apple's Command Line Tools, which include clang, make, git, bison, and flex. A window pops up; let it finish before you continue. If the command says they're already installed, move on.

   ```sh
   xcode-select --install
   ```

2. Install [Homebrew](https://brew.sh/) if `brew --version` doesn't work yet:

   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

   When it finishes, run the commands it prints under **Next steps**. They put `brew` on your PATH, since Homebrew installs to `/opt/homebrew` and macOS doesn't look there by default. The installer only supports Apple Silicon Macs. On an Intel Mac, get CMake and pkg-config another way, such as [MacPorts](https://www.macports.org/).

3. Install CMake and pkg-config (Homebrew calls it `pkgconf`):

   ```sh
   brew install cmake pkgconf
   ```

#### 2. Install vcpkg

Skip this if you already have vcpkg.

```sh
git clone https://github.com/microsoft/vcpkg ~/vcpkg
~/vcpkg/bootstrap-vcpkg.sh -disableMetrics
```

Then tell CMake where it is by adding `VCPKG_ROOT` to your shell config. Run the line for your OS:

```sh
echo 'export VCPKG_ROOT="$HOME/vcpkg"' >> ~/.zshrc    # macOS (zsh is the default shell)
```

```sh
echo 'export VCPKG_ROOT="$HOME/vcpkg"' >> ~/.bashrc   # most Linux distros
```

Open a new terminal and check that `echo $VCPKG_ROOT` prints the path.

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
./build/bin/sensor            # list network interfaces
./build/bin/sensor <iface>    # capture on an interface, e.g. eth0 or en0
```

> **macOS:** listing interfaces works as a normal user, but capturing needs access to `/dev/bpf*`, which only root has by default. Capture with `sudo ./build/bin/sensor en0`, or install Wireshark's ChmodBPF helper with `brew install --cask wireshark-chmodbpf` and restart your Mac to capture without `sudo`. The Wireshark app (`brew install --cask wireshark-app`) already includes the helper, so skip the separate cask if you install that.

### Windows

#### 1. Install the prerequisites

- [Visual Studio](https://visualstudio.microsoft.com/) 2022 or newer with the **Desktop development with C++** workload (this includes CMake and vcpkg)
- [Npcap](https://npcap.com/#download), the packet capture driver. The default install options are fine.

#### 2. Build

Open **Developer PowerShell for VS** from the Start menu. It already has `VCPKG_ROOT` set to the copy of vcpkg that ships with Visual Studio. From the `sensor/` directory:

```powershell
cmake --preset windows
cmake --build --preset windows
```

The first configure takes a few minutes while vcpkg builds the dependencies. Later builds are cached.

> Using your own vcpkg clone instead? Set a `VCPKG_ROOT` user environment variable pointing at it and you can build from any PowerShell window.

#### 3. Run

```powershell
.\build\windows\bin\Debug\sensor.exe                  # list network interfaces
.\build\windows\bin\Debug\sensor.exe "\Device\NPF_{...}"  # capture on an interface
```

Copy an interface name from the list. Keep the quotes, because PowerShell treats `{...}` as a script block and cuts the name off.

> **No interfaces listed?** Make sure Npcap is installed. If you installed it with *Restrict Npcap driver's access to Administrators only*, run the sensor from an administrator terminal.

---

**Currently in development** 

---

>Initialized for CS4622 (Computer Networks) at Kennesaw State University.

### Team:

**Capture & Metrics:**

`Mere-Solace` -
`cjusino13`


**Threat Detection:**

`EvanMc1` -
`KaiJGlaza` -
`maitrip7`


**Data & Dashboard:**

`Aveon` -
`NanoFerreira`
