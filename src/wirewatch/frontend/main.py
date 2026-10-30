
from wirewatch.backend import list_devices, capture_packets

if __name__ == "__main__":
	devices = list_devices()
	for dev in devices:
		print(dev)

	print("\n| capture_packets:\n\n")

	for packet in capture_packets(devices[0][0], 100, 60):
		print(packet)

	