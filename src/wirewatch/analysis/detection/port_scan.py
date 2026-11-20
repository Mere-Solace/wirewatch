from wirewatch.analysis.detection.window import DistinctWindow

PORT_THRESHOLD = 20      # distinct ports before we alert (starting guess, tune later)
WINDOW_SECONDS = 10      # how far back we look
COOLDOWN_SECONDS = 60    # don't repeat the same alert for a continuing scan


class PortScanRule:
    def __init__(self, threshold=PORT_THRESHOLD, window=WINDOW_SECONDS,
                 cooldown=COOLDOWN_SECONDS):
        self.threshold = threshold
        self.window = window
        self.cooldown = cooldown
        self._ports = DistinctWindow(window)
        self._last_alert = {}

    def process(self, event):
        # Only count connection attempts: SYN set, nothing else
        if event.get("flags") != "S":
            return []

        key = (event["src_ip"], event["dst_ip"])
        ts = event["ts"]
        self._ports.add(key, event["dst_port"], ts)
        count = self._ports.count(key, ts)

        if count < self.threshold:
            return []

        last = self._last_alert.get(key)
        if last is not None and ts - last < self.cooldown:
            return []                       # already alerted, stay quiet
        self._last_alert[key] = ts

        src, dst = key
        return [{
            "type": "port_scan",
            "severity": "Medium",           # placeholder, ranking not decided yet
            "device": src,
            "time": ts,
            "title": "Port scan detected",
            "what_happened": (f"{src} tried {count} different ports on {dst} "
                              f"within {self.window} seconds."),
            "why_this_severity": ("Trying many ports quickly is typical of a tool "
                                  "searching for open services."),
            "next_step": ("Check whether you recognize this device. "
                          "If not, disconnect it from the network."),
            "evidence": {"ports": count, "seconds": self.window, "target": dst},
        }]