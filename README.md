# Wirewatch

A descriptive network health monitor that shows you why your network is slowing down.

Packet-level network health monitor. Captures traffic, measures network health, and provides descriptive reports and analysis. Explanations are in plain language and don't assume you already understand what's being shown.

---


## Quickstart

Wirewatch has two parts: a C++20 **sensor** that captures packets, and a Python package that runs the sensor and works with its output. The sensor's dependencies ([PcapPlusPlus](https://pcapplusplus.github.io/) and [fmt](https://fmt.dev/)) are installed automatically by [vcpkg](https://vcpkg.io/) the first time you build.

Once the prerequisites below are installed, one command builds everything, gives the sensor permission to capture, and starts Wirewatch on any OS:

```sh
uv run scripts/dev.py
```

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

Then install [uv](https://docs.astral.sh/uv/getting-started/installation/), which manages Python and builds the package:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
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

#### 3. Build and run

From the repository root:

```sh
uv run scripts/dev.py
```

The first build takes a few minutes while vcpkg builds the dependencies. Later builds are cached.

> **Linux:** the script runs `sudo setcap cap_net_raw,cap_net_admin=eip` on the sensor so it can capture without running as root, so it may ask for your password. Rebuilding the sensor removes these capabilities, so the script checks for them on every run.
>
> **macOS:** capturing needs access to `/dev/bpf*`, which only root has by default. Install Wireshark's ChmodBPF helper with `brew install --cask wireshark-chmodbpf` and restart your Mac. The Wireshark app (`brew install --cask wireshark-app`) already includes the helper, so skip the separate cask if you install that. The script stops with a message if it can't open `/dev/bpf0`.

### Windows

#### 1. Install the prerequisites

- [Visual Studio](https://visualstudio.microsoft.com/) 2022 or newer with the **Desktop development with C++** workload (this includes CMake and vcpkg)
- [Npcap](https://npcap.com/#download), the packet capture driver. The default install options are fine.
- [uv](https://docs.astral.sh/uv/getting-started/installation/): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

#### 2. Build and run

Open **Developer PowerShell for VS** from the Start menu. It already has `VCPKG_ROOT` set to the copy of vcpkg that ships with Visual Studio. From the repository root:

```powershell
uv run scripts/dev.py
```

The first build takes a few minutes while vcpkg builds the dependencies. Later builds are cached.

> Using your own vcpkg clone instead? Set a `VCPKG_ROOT` user environment variable pointing at it and you can build from any PowerShell window.

> **No interfaces listed?** Make sure Npcap is installed. If you installed it with *Restrict Npcap driver's access to Administrators only*, run from an administrator terminal.

### Building the sensor on its own

To work on the C++ sensor without the Python package, build it directly with CMake from the `sensor/` directory:

```sh
cmake --preset default            # Windows: cmake --preset windows
cmake --build build               # Windows: cmake --build --preset windows
```

Then run it with the interface to capture on, the maximum number of packets, and a timeout:

```sh
./build/bin/sensor <iface> <max_packets> <timeout>
```

> **Linux:** a plain CMake build runs `sudo setcap` on the sensor after linking, so it may ask for your password. If that fails, or you configured with `-DWIREWATCH_SETCAP=OFF`, grant it yourself after every build: `sudo setcap cap_net_raw,cap_net_admin=eip build/bin/sensor`.

---


---

## Development

Don't run uv with sudo.

Calling the C++ functions from python does not retain (or ever grant) the proper capture priviledges. 

**Currently in development** 

---

>Initialized for CS4622 (Computer Networks) at Kennesaw State University.

### Team:

**Capture & Metrics:**

Capture & Metrics:

`Mere-Solace` -
`cjusino13`


**Threat Detection:**

`EvanMc1` -
`KaiJGlaza` -
`maitrip7`


**Data & Dashboard:**

`Aveon` -
`NanoFerreira`
