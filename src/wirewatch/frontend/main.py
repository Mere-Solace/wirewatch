"""Entry point: start the dashboard, run the sensor, and pass every record to the analysis modules."""

import argparse
import sys
from collections.abc import Callable

from wirewatch.backend import Packet, capture_packets, list_devices
from wirewatch.frontend import server
from wirewatch.records import Alert

# Every packet goes to each detector's process method. Empty for now: the port scan rule
# needs dst_port and flags, and the sensor doesn't send those yet.
DETECTORS: list[Callable[[Packet], list[Alert]]] = []
NO_PACKET_LIMIT = 2**31 - 1


def main() -> None:
	parser = argparse.ArgumentParser(description="Wirewatch network health monitor.")
	_ = parser.add_argument("-i", "--interface", help="interface to capture on (default: the first one listed)")
	_ = parser.add_argument("--port", type=int, help="dashboard port on 127.0.0.1 (default: 8000, or a free port if 8000 is taken)")
	args = parser.parse_args()

	names = [name for name, _ in list_devices()]
	if not names:
		sys.exit("No capture interfaces found. On Windows install Npcap; elsewhere check capture permission (see README).")
	# On macOS the first interface listed is usually an idle one like ap1, so default to en0 (Wi-Fi).
	# Picking the interface that has an IP address would be better once list_devices returns addresses.
	default = "en0" if sys.platform == "darwin" and "en0" in names else names[0]
	interface: str = args.interface or default
	if interface not in names:
		sys.exit(f"No interface named {interface!r}. Pick one of: {', '.join(names)}")

	dashboard = server.serve(args.port)
	print(f"Capturing on {interface}. Dashboard: http://127.0.0.1:{dashboard.server_port} (Ctrl+C to stop)", flush=True)

	try:
		# A timeout of 0 means no timeout. The sensor stops once it hits the packet limit, so pass the largest C int.
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
