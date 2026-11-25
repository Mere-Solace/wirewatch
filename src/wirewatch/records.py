"""Records that analysis modules produce and the dashboard shows.

Lowest layer: imports nothing from wirewatch, so analysis/ and frontend/ can both import it.
The wire record from the sensor (Packet) still lives in wirewatch.backend.
"""

from typing import Literal, TypedDict

# Order and spelling from the Design deck: Low -> Medium -> High -> Critical.
Severity = Literal["Low", "Medium", "High", "Critical"]


class Alert(TypedDict):
	"""One detection result. Keys follow the port scan rule on feat/detection-port-scan, with ts in place of time."""

	ts: float  # epoch seconds, from the packet that triggered it
	type: str  # rule name: "port_scan", "syn_flood", "arp_spoof", "isolation_forest", ...
	severity: Severity
	device: str  # IP address the alert is about
	title: str  # a few words for the alert list
	what_happened: str  # one plain-language sentence
	why_this_severity: str
	next_step: str  # what the user should do
	evidence: dict[str, int | float | str]  # numbers behind the alert, e.g. {"ports": 214, "seconds": 10}


class Health(TypedDict):
	ts: float
	score: int  # 0-100
	cause: str  # one sentence on what is lowering the score
	handshake_ms: float
	retransmissions: int
	dns_failures: int


class Conversation(TypedDict):
	device: str  # local IP address
	maker: str  # from the MAC address, "" if unknown
	name: str  # remote name from DNS or TLS SNI, else the remote IP address
	proto: str
	bytes: int
	packets: int
