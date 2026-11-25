"""Entry point: start the dashboard, run the sensor, and pass every record to the analysis modules."""

import argparse
import sys
from collections.abc import Callable

from wirewatch.backend import Packet, capture_packets, list_devices
from wirewatch.frontend import server
from wirewatch.records import Alert

# Each detector's process method. Add a rule here once the records it reads exist.
# shortcut: empty until the sensor emits ports and TCP flags (PortScanRule needs dst_port and flags)
DETECTORS: list[Callable[[Packet], list[Alert]]] = []
NO_PACKET_LIMIT = 2**31 - 1


def main() -> None:
	parser = argparse.ArgumentParser(description="Wirewatch network health monitor.")
	_ = parser.add_argument("-i", "--interface", help="interface to capture on (default: the first one listed)")
	_ = parser.add_argument("--port", type=int, default=8000, help="dashboard port on 127.0.0.1 (default 8000)")
	args = parser.parse_args()

	names = [name for name, _ in list_devices()]
	if not names:
		sys.exit("No capture interfaces found. On Windows install Npcap; elsewhere check capture permission (see README).")
	# macOS lists idle interfaces like ap1 before en0, its primary interface.
	# shortcut: name-based default; pick by IPv4 address once list_devices returns addresses
	default = "en0" if sys.platform == "darwin" and "en0" in names else names[0]
	interface: str = args.interface or default
	if interface not in names:
		sys.exit(f"No interface named {interface!r}. Pick one of: {', '.join(names)}")

	dashboard = server.serve(args.port)
	print(f"Capturing on {interface}. Dashboard: http://127.0.0.1:{dashboard.server_port} (Ctrl+C to stop)", flush=True)

	try:
		# timeout 0 means none in PcapPlusPlus; the packet limit is the largest C int, since the sensor stops when count >= limit
		for packet in capture_packets(interface, NO_PACKET_LIMIT, 0):
			server.add_packet(packet)
			for detect in DETECTORS:
				for alert in detect(packet):
					server.add_alert(alert)
	except KeyboardInterrupt:
		pass
	finally:
		dashboard.shutdown()


if __name__ == "__main__":
	main()
