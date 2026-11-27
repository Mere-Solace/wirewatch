"""Test traffic for detector.py (CS 4622 honors contract).

Run detector.py in one terminal and this in another:
  python3 detector.py -i lo0
  python3 traffic.py scan      # fast scan of 30 ports: expect a port-scan alert
  python3 traffic.py slow      # same ports, spread out: expect no alert
  python3 traffic.py canary    # one attempt on port 23: expect a canary alert
"""

import argparse
import socket
import time

TARGET = "127.0.0.1"


def scan(host, ports, delay):
    """Make one TCP connection attempt to each port, waiting `delay` seconds between them.

    Each attempt sends a SYN, which is what detector.py counts. Nothing needs to be
    listening: a closed port answers with RST, but the SYN was already on the wire.
    """
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            sock.connect_ex((host, port))  # returns an error code on a closed port instead of raising
        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="Generate test traffic for detector.py.")
    parser.add_argument("case", choices=["scan", "slow", "canary"])
    parser.add_argument("--host", default=TARGET)
    args = parser.parse_args()

    if args.case == "scan":
        scan(args.host, range(1, 31), delay=0.05)
    elif args.case == "slow":
        scan(args.host, range(1, 31), delay=0.6)  # 0.6 s apart: at most 9 ports in any 5 s window, under the threshold of 10
    else:
        scan(args.host, [23], delay=0)
    print(f"sent {args.case} traffic to {args.host}")


if __name__ == "__main__":
    main()
