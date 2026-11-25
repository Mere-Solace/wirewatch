# Honors detector

Kai's individual honors contract for CS 4622 (Dr. Pei). `detector.py` watches TCP connection attempts and prints an alert for a port scan (10 distinct ports from one source within 5 seconds) or any attempt on a canary port (default 23).

The contract requires this to be written and tested apart from the Wirewatch app, so nothing here imports `wirewatch` or the sensor, and the Wirewatch build does not include this folder.

## How to run

Needs Python 3 and tcpdump (ships with macOS and most Linux distros). Live capture needs root, or on macOS the `access_bpf` group from Wireshark's ChmodBPF.

```sh
python3 detector.py --self-test            # rule checks, no capture
python3 detector.py -i lo0                 # live on loopback (Linux: -i lo)
python3 detector.py -r capture.pcap        # replay a saved capture
python3 detector.py -i en0 --canary 23,2323
```

`traffic.py` sends test traffic to localhost (`scan`, `slow`, `canary`) for the screenshots in the report.
