"""Local web dashboard. Analysis code pushes records in with the add_/set_ functions; the page reads GET /api/state."""

import json
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, override

from wirewatch.records import Alert, Conversation, Health

if TYPE_CHECKING:
	# a runtime import would load the compiled extension; only the type is needed here
	from wirewatch.backend import Packet

STATIC = Path(__file__).parent / "static"
RECENT = 500  # packets and alerts kept for the page; older ones drop off

_lock = threading.Lock()
_packets: "deque[Packet]" = deque(maxlen=RECENT)
_alerts: deque[Alert] = deque(maxlen=RECENT)
_health: Health | None = None
_conversations: list[Conversation] = []


def add_packet(packet: "Packet") -> None:
	with _lock:
		_packets.append(packet)


def add_alert(alert: Alert) -> None:
	with _lock:
		_alerts.append(alert)


def set_health(health: Health) -> None:
	global _health
	with _lock:
		_health = health


def set_conversations(conversations: list[Conversation]) -> None:
	global _conversations
	with _lock:
		_conversations = list(conversations)


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

	@override
	def log_message(self, format: str, *args: object) -> None:
		pass  # the page polls every second, which would flood the terminal


def serve(port: int = 8000) -> ThreadingHTTPServer:
	"""Start the dashboard in a background thread and return the server (port 0 picks a free port)."""
	# 127.0.0.1 only, so captured traffic is never reachable from the rest of the network
	server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
	threading.Thread(target=server.serve_forever, daemon=True).start()
	return server

