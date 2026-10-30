# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Build wirewatch, give the sensor capture permission, and run the frontend.

Usage (from anywhere in the repo):  uv run scripts/dev.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

REPO = Path(__file__).resolve().parent.parent
FRONTEND = REPO / "src" / "wirewatch" / "frontend" / "main.py"


def fail(message: str) -> NoReturn:
	print(f"dev.py: {message}", file=sys.stderr)
	sys.exit(1)


def check_tools() -> None:
	if shutil.which("uv") is None:
		fail("uv is not on PATH")

	vcpkg_root = os.environ.get("VCPKG_ROOT")
	if not vcpkg_root or not Path(vcpkg_root).is_dir():
		fail("VCPKG_ROOT is not set to a vcpkg checkout (see README Quickstart)")


def project_env() -> dict[str, str]:
	# uv runs this script in its own throwaway venv and sets VIRTUAL_ENV to it;
	# drop it so the uv commands below use the project's .venv instead
	env = os.environ.copy()
	_ = env.pop("VIRTUAL_ENV", None)
	return env


def build() -> None:
	# uv sync builds the project: scikit-build-core runs CMake, which builds
	# both the _wirewatch extension module and the sensor executable.
	result = subprocess.run(["uv", "sync"], cwd=REPO, env=project_env())
	if result.returncode != 0:
		fail("build failed")


def find_sensor() -> Path:
	name = "sensor.exe" if sys.platform == "win32" else "sensor"
	candidates = list((REPO / "build").glob(f"*/bin/{name}"))
	if not candidates:
		fail(f"no {name} under build/*/bin after building")
	# several wheel-tag dirs can exist (e.g. after a Python upgrade); take the newest
	return max(candidates, key=lambda p: p.stat().st_mtime)


def grant_linux(sensor: Path) -> None:
	# relinking replaces the file, which drops its capabilities, so check every run
	current = subprocess.run(["getcap", str(sensor)], capture_output=True, text=True)
	if "cap_net_raw" in current.stdout and "cap_net_admin" in current.stdout:
		return

	print(f"Granting cap_net_raw,cap_net_admin to {sensor} (sudo may ask for your password)")
	result = subprocess.run(["sudo", "setcap", "cap_net_raw,cap_net_admin=eip", str(sensor)])
	if result.returncode != 0:
		fail("setcap failed")


def check_macos() -> None:
	# macOS has no file capabilities; libpcap needs read/write access to /dev/bpf*
	if not os.access("/dev/bpf0", os.R_OK | os.W_OK):
		fail("no access to /dev/bpf*. Run: brew install --cask wireshark-chmodbpf"
		     + " and restart your Mac")


def check_windows() -> None:
	system_root = os.environ.get("SystemRoot", r"C:\Windows")
	if not (Path(system_root) / "System32" / "Npcap" / "wpcap.dll").is_file():
		fail("Npcap is not installed. Get it from https://npcap.com")


def main() -> None:
	check_tools()
	build()
	sensor = find_sensor()

	if sys.platform == "linux":
		grant_linux(sensor)
	elif sys.platform == "darwin":
		check_macos()
	elif sys.platform == "win32":
		check_windows()

	# a script can't change its parent shell's environment; it can only pass
	# variables down to the processes it starts
	env = project_env()
	env["WIREWATCH_SENSOR"] = str(sensor)

	result = subprocess.run(["uv", "run", "--no-sync", str(FRONTEND)], cwd=REPO, env=env)
	sys.exit(result.returncode)


if __name__ == "__main__":
	main()
