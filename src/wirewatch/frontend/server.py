"""Local web dashboard. Analysis code pushes records in with the add_/set_ functions; the page reads GET /api/state."""

import json
import threading
from collections import deque
from collections.abc import Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
	# a runtime import would load the compiled extension; only the type is needed here
	from wirewatch.backend import Packet

STATIC = Path(__file__).parent / "static"
RECENT = 500  # packets and alerts kept for the page; older ones drop off

Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class Alert(TypedDict):
	ts: float  # epoch seconds
	severity: Severity
	rule: str  # "port_scan", "arp_spoof", "syn_flood", "isolation_forest", ...
	device: str  # IP the alert is about
	what: str  # what happened, one sentence
	why: str  # why it got this severity
	next: str  # what the user should do


class Health(TypedDict):
	ts: float
	score: int  # 0-100
	cause: str  # one sentence on what is lowering the score
	handshake_ms: float
	retransmissions: int
	dns_failures: int


class Conversation(TypedDict):
	device: str  # local IP
	maker: str  # from the MAC address, "" if unknown
	name: str  # remote name from DNS or TLS SNI, else the remote IP
	proto: str
	bytes: int
	packets: int


_lock = threading.Lock()
_packets: "deque[Packet]" = deque(maxlen=RECENT)
_alerts: deque[Alert] = deque(maxlen=RECENT)
_health: Health | None = None
_conversations: list[Conversation] = []


def _check(record: Mapping[str, object], kind: type) -> bool:
	"""Return True to keep the record, False to drop it (or raise)."""
	# TODO(Kai): decide what happens when a teammate sends a record in the wrong format
	return True


def add_packet(packet: "Packet") -> None:
	with _lock:
		_packets.append(packet)


def add_alert(alert: Alert) -> None:
	if _check(alert, Alert):
		with _lock:
			_alerts.append(alert)


def set_health(health: Health) -> None:
	global _health
	if _check(health, Health):
		with _lock:
			_health = health


def set_conversations(conversations: list[Conversation]) -> None:
	global _conversations
	kept = [c for c in conversations if _check(c, Conversation)]
	with _lock:
		_conversations = kept


def _state() -> bytes:
	with _lock:
		state = {
			"health": _health,
			"alerts": list(_alerts),
			"conversations": _conversations,
			"packets": list(_packets),
		}
	return json.dumps(state).encode()


class _Handler(BaseHTTPRequestHandler):
	def do_GET(self) -> None:
		if self.path == "/":
			body, content_type = (STATIC / "index.html").read_bytes(), "text/html"
		elif self.path == "/api/state":
			body, content_type = _state(), "application/json"
		else:
			self.send_error(404)
			return

		self.send_response(200)
		self.send_header("Content-Type", f"{content_type}; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
		self.end_headers()
		_ = self.wfile.write(body)

	def log_message(self, format: str, *args: object) -> None:
		pass  # the page polls every second, which would flood the terminal


def serve(port: int = 8000) -> ThreadingHTTPServer:
	"""Start the dashboard in a background thread and return the server (port 0 picks a free port)."""
	# 127.0.0.1 only, so captured traffic is never reachable from the rest of the network
	server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
	threading.Thread(target=server.serve_forever, daemon=True).start()
	return server


if __name__ == "__main__":
	# self-check with made-up records, then keep serving so the page can be built against them
	from urllib.request import urlopen

	server = serve(0)
	url = f"http://127.0.0.1:{server.server_port}"

	add_packet({"src": "192.168.1.20", "dst": "142.250.80.46", "frame_len": 78, "cap_len": 78,
	            "tv_sec": 1793383349, "tv_nsec": 357346000})
	add_alert({"ts": 1793383349.9, "severity": "MEDIUM", "rule": "port_scan", "device": "192.168.1.50",
	           "what": "192.168.1.50 tried 214 different ports on this laptop in 5 seconds.",
	           "why": "Ranked Medium: reconnaissance only, no connection succeeded.",
	           "next": "Find out what 192.168.1.50 is. If you don't recognize it, block it on the router."})
	set_health({"ts": 1793383350.0, "score": 82, "cause": "DNS lookups are failing more than usual.",
	            "handshake_ms": 24.5, "retransmissions": 3, "dns_failures": 7})
	set_conversations([{"device": "192.168.1.20", "maker": "Apple", "name": "www.google.com",
	                    "proto": "tcp", "bytes": 51200, "packets": 64}])

	with urlopen(f"{url}/api/state") as response:
		state = json.load(response)
	assert len(state["packets"]) == 1 and len(state["alerts"]) == 1
	assert state["health"]["score"] == 82 and state["conversations"][0]["name"] == "www.google.com"
	with urlopen(url) as response:
		assert b"/api/state" in response.read()
	print(f"self-check passed. Sample data at {url} (Ctrl+C to stop)")

	try:
		threading.Event().wait()
	except KeyboardInterrupt:
		server.shutdown()
