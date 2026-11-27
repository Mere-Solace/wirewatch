"""Lightweight network anomaly detector (CS 4622 honors contract).

Watches TCP connection attempts (SYN packets) and prints an alert for:
  1. a port scan: one source trying many different ports in a short window
  2. a canary hit: any connection attempt to a trap port that nothing listens on

Capture uses tcpdump, which ships with macOS and Linux, so there is nothing to
pip install. Capturing needs root, or on macOS membership in the access_bpf
group (Wireshark's ChmodBPF installs it).

Usage:
  python3 detector.py -i lo0                 # live, loopback (scan localhost to test)
  python3 detector.py -i en0 --canary 23,2323
  python3 detector.py -r capture.pcap        # replay a saved capture
  python3 detector.py --self-test
"""

import argparse
import subprocess
import sys
import time
from collections import defaultdict, deque

# Alert when one source hits this many distinct ports inside the window.
PORT_SCAN_THRESHOLD = 10
PORT_SCAN_WINDOW_SECONDS = 5.0

# Telnet is a good default trap: nothing on a modern laptop listens there, and
# it is in nmap's default top-1000 ports, so a scan trips it as well.
DEFAULT_CANARY_PORTS = "23"

# SYN set, ACK clear: the first packet of a connection attempt.
# shortcut: IPv4 only (tcp[] offsets don't apply to IPv6), add an ip6 filter if scans over IPv6 matter.
SYN_FILTER = "tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn"


def format_alert(timestamp, severity, text):
    clock = time.strftime("%H:%M:%S", time.localtime(timestamp))
    return f"[{clock}] [{severity}] {text}"


class PortScanRule:
    def __init__(self, threshold=PORT_SCAN_THRESHOLD, window=PORT_SCAN_WINDOW_SECONDS):
        self.threshold = threshold
        self.window = window
        self.hits = defaultdict(deque)  # src_ip -> deque of (timestamp, dst_port)
        self.alerted = set()            # src_ips already alerted in their current burst

    def observe(self, timestamp, src_ip, dst_port):
        """Record one connection attempt. Returns an alert string or None."""
        hits = self.hits[src_ip]
        hits.append((timestamp, dst_port))

        # Drop attempts that fell out of the window.
        while hits and timestamp - hits[0][0] > self.window:
            hits.popleft()

        distinct_ports = len({port for _, port in hits})
        if distinct_ports < self.threshold:
            # Burst is over (or never started), so the next scan alerts again.
            self.alerted.discard(src_ip)
            return None
        if src_ip in self.alerted:
            return None
        self.alerted.add(src_ip)
        return format_alert(timestamp, "MEDIUM",
                            f"port scan from {src_ip}: {distinct_ports} distinct ports "
                            f"in {self.window:g}s")


class CanaryRule:
    def __init__(self, ports):
        self.ports = set(ports)

    def observe(self, timestamp, src_ip, dst_port):
        """Any attempt on a trap port is suspicious, since no real service lives there."""
        if dst_port not in self.ports:
            return None
        return format_alert(timestamp, "HIGH",
                            f"canary port {dst_port} touched by {src_ip}")


def parse_syn(line):
    """Turn one tcpdump -tt -n line into (timestamp, src_ip, dst_port), or None.

    Example: 1793383349.357346 IP 127.0.0.1.57989 > 127.0.0.1.23: Flags [S], ...
    """
    fields = line.split()
    if len(fields) < 5 or fields[1] != "IP" or fields[3] != ">":
        return None
    try:
        src_ip = fields[2].rsplit(".", 1)[0]
        dst_port = int(fields[4].rstrip(":").rsplit(".", 1)[1])
        return float(fields[0]), src_ip, dst_port
    except (ValueError, IndexError):
        return None


def syn_events(interface=None, pcap_file=None):
    """Yield (timestamp, src_ip, dst_port) for each SYN tcpdump sees."""
    cmd = ["tcpdump", "-tt", "-n", "-l"]
    cmd += ["-r", pcap_file] if pcap_file else (["-i", interface] if interface else [])
    cmd.append(SYN_FILTER)
    # tcpdump's stderr passes through, so "listening on ..." and permission errors show up.
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as proc:
        for line in proc.stdout:
            event = parse_syn(line)
            if event:
                yield event
    if proc.returncode not in (0, None, -2):
        sys.exit(f"tcpdump exited with code {proc.returncode}")


def port_list(text):
    ports = [int(p) for p in text.split(",")]
    if not all(1 <= p <= 65535 for p in ports):
        raise argparse.ArgumentTypeError("ports must be between 1 and 65535")
    return ports


def _self_test():
    rule = PortScanRule(threshold=3, window=2.0)

    # Three ports within the window fires once.
    assert rule.observe(0.0, "10.0.0.5", 22) is None
    assert rule.observe(0.5, "10.0.0.5", 80) is None
    alert = rule.observe(1.0, "10.0.0.5", 443)
    assert alert and "10.0.0.5" in alert and "3 distinct ports" in alert

    # Repeat hits on the same port are not a scan.
    assert rule.observe(1.2, "10.0.0.9", 22) is None
    assert rule.observe(1.3, "10.0.0.9", 22) is None
    assert rule.observe(1.4, "10.0.0.9", 22) is None

    # Slow scanning outside the window does not fire.
    assert rule.observe(10.0, "10.0.0.7", 1) is None
    assert rule.observe(20.0, "10.0.0.7", 2) is None
    assert rule.observe(30.0, "10.0.0.7", 3) is None

    # The already-alerted source does not alert again while the burst continues.
    assert rule.observe(1.5, "10.0.0.5", 8080) is None

    # A second scan from the same source after the first one ended alerts again.
    assert rule.observe(100.0, "10.0.0.5", 1) is None
    assert rule.observe(100.1, "10.0.0.5", 2) is None
    assert rule.observe(100.2, "10.0.0.5", 3) is not None

    canary = CanaryRule([23])
    assert canary.observe(0.0, "10.0.0.5", 22) is None
    alert = canary.observe(0.0, "10.0.0.5", 23)
    assert alert and "HIGH" in alert and "10.0.0.5" in alert

    line = ("1793383349.357346 IP 127.0.0.1.57989 > 127.0.0.1.23: Flags [S], "
            "seq 3531526294, win 65535, length 0")
    assert parse_syn(line) == (1793383349.357346, "127.0.0.1", 23)
    assert parse_syn("reading from file x.pcap, link-type EN10MB") is None
    print("self-test passed")


def main():
    parser = argparse.ArgumentParser(description="Alert on port scans and canary-port hits.")
    parser.add_argument("-i", "--interface", help="interface to capture on, e.g. lo0 or en0")
    parser.add_argument("-r", "--read", metavar="PCAP", help="replay a saved capture instead")
    parser.add_argument("--canary", type=port_list, default=port_list(DEFAULT_CANARY_PORTS),
                        help=f"comma-separated trap ports (default {DEFAULT_CANARY_PORTS})")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checks and exit")
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        return

    rules = [PortScanRule(), CanaryRule(args.canary)]
    print(f"watching for port scans ({PORT_SCAN_THRESHOLD} ports in "
          f"{PORT_SCAN_WINDOW_SECONDS:g}s) and canary ports {sorted(args.canary)}")
    try:
        for timestamp, src_ip, dst_port in syn_events(args.interface, args.read):
            for rule in rules:
                alert = rule.observe(timestamp, src_ip, dst_port)
                if alert:
                    print(alert, flush=True)
    except FileNotFoundError:
        sys.exit("tcpdump not found; install it (it ships with macOS and most Linux distros)")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
