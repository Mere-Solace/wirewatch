from scapy.all import IP, TCP, UDP, wrpcap, rdpcap
import random
import os

pcap_input = input("Enter a .pcap filename to load (or press Enter to generate synthetic traffic): ").strip()

if pcap_input:
    if os.path.exists(pcap_input):
        packets = rdpcap(pcap_input)
        print(f"Loaded {len(packets)} packets from {pcap_input}")
    else:
        print(f"Error: '{pcap_input}' not found.")
        packets = []
else:
    packets = []
    target_ip = "127.0.0.1"

    # Generate normal HTTP-like packets
    for _ in range(50):
        pkt = IP(src="192.168.1.10", dst=target_ip)/TCP(sport=random.randint(1024, 65535), dport=80, flags="PA")/b"GET / HTTP/1.1"
        packets.append(pkt)

    # Generate anomalous port-scan packets
    for port in range(20, 45):
        pkt = IP(src="10.0.0.99", dst=target_ip)/TCP(sport=54321, dport=port, flags="S")
        packets.append(pkt)

    # Save directly to a PCAP file in Colab's local storage
    wrpcap("synthetic_traffic.pcap", packets)
    print(f"Saved {len(packets)} packets to synthetic_traffic.pcap")
