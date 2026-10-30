"""Packet-capture backend: device listing (pybind11) + capture (sensor subprocess)."""

import json
import os
import subprocess
from collections.abc import Iterator
from importlib import resources
from pathlib import Path
from typing import TypedDict, cast

from ._wirewatch import list_devices

__all__ = ["list_devices", "capture_packets"]

def _sensor_path() -> Path:
	override = os.environ.get("WIREWATCH_SENSOR")
	if override:
		return Path(override)
	else:
		return Path(str(resources.files("wirewatch.backend") / "bin" / "sensor"))


class Packet(TypedDict):
	src: str
	dst: str
	frame_len: int
	cap_len: int
	tv_sec: int
	tv_nsec: int

def capture_packets(device_name: str, max_packets: int, timeout_seconds: int) -> Iterator[Packet]:
	command = [str(_sensor_path()), device_name, str(max_packets), str(timeout_seconds)]
	print("-----------------------------------------")
	with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as proc:
		assert proc.stdout is not None
		for line in proc.stdout:
			print(line)
			yield cast(Packet, json.loads(line))

	if proc.returncode != 0:
		raise RuntimeError(f"sensor exited with code {proc.returncode}")
