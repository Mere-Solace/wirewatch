"""Record types shared by every module. The JSON Schemas in schemas/ are the source of truth; each type here mirrors one.

Wire records come from the sensor as NDJSON, one per line. App records are made in Python and never reach the sensor.
Every record carries "type" (what it is) and "v" (its schema version). Timestamps are epoch seconds as float.
A field that does not apply is present and None, never missing.
"""

from typing import Literal, TypedDict

SCHEMA_VERSION = 1

Proto = Literal["tcp", "udp", "icmp", "icmpv6", "other"]
Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
FlowEndReason = Literal["fin", "rst", "idle", "active", "shutdown"]
ArpOp = Literal["request", "reply"]
SegmentName = Literal["this_pc", "wifi", "router", "internet", "dns"]
SegmentStatus = Literal["ok", "degraded", "bad"]


# ---- wire records: sensor -> Python ----


class Packet(TypedDict):
	"""One sampled packet. schemas/wire/packet.schema.json"""

	type: Literal["packet"]
	v: Literal[1]
	ts: float
	src_ip: str
	dst_ip: str
	proto: Proto
	src_port: int | None  # None when proto has no ports
	dst_port: int | None
	tcp_flags: str | None  # set flags in FSRPAUEC order, e.g. "S", "SA"; None when not tcp
	frame_len: int  # bytes on the wire
	cap_len: int  # bytes captured, at most frame_len


class Flow(TypedDict):
	"""One bidirectional flow, emitted when it ends; src_* is the originator. schemas/wire/flow.schema.json"""

	type: Literal["flow"]
	v: Literal[1]
	flow_id: str
	ts: float  # first packet
	ts_end: float  # last packet
	src_ip: str
	dst_ip: str
	proto: Proto
	src_port: int | None
	dst_port: int | None
	orig_bytes: int
	orig_packets: int
	resp_bytes: int
	resp_packets: int
	handshake_rtt_ms: float | None  # None when not tcp or no handshake was seen
	retransmissions: int
	resets: int
	end_reason: FlowEndReason


class Stats(TypedDict):
	"""Sensor counters for one interval, not running totals. schemas/wire/stats.schema.json"""

	type: Literal["stats"]
	v: Literal[1]
	ts: float  # end of the interval
	interval_seconds: float
	packets: int
	bytes: int
	drops_kernel: int
	drops_interface: int  # 0 where the platform does not report it
	decode_errors: int
	sampled_out: int  # counted but not emitted as Packet


class Dns(TypedDict):
	"""One query matched to its response, or unanswered after a timeout. schemas/wire/dns.schema.json"""

	type: Literal["dns"]
	v: Literal[1]
	ts: float  # query time
	client_ip: str
	server_ip: str
	txid: int
	qname: str  # no trailing dot
	qtype: str  # "A", "AAAA", ...
	rcode: str | None  # "NOERROR", "NXDOMAIN", ...; None when unanswered
	answers: list[str]
	response_ms: float | None  # None when unanswered


class Arp(TypedDict):
	"""One ARP request or reply, unsampled. schemas/wire/arp.schema.json"""

	type: Literal["arp"]
	v: Literal[1]
	ts: float
	op: ArpOp
	sender_mac: str  # lowercase, colon-separated
	sender_ip: str
	target_mac: str  # 00:00:00:00:00:00 in a request
	target_ip: str


WireRecord = Packet | Flow | Stats | Dns | Arp


# ---- app records: made in Python ----


class Alert(TypedDict):
	"""One detection in plain language. schemas/app/alert.schema.json"""

	type: Literal["alert"]
	v: Literal[1]
	ts: float  # time of the triggering record
	severity: Severity
	rule: str  # detector name, e.g. "port_scan"
	device: str  # IP the alert is about
	title: str
	what: str  # what happened, one sentence
	why: str  # why it got this severity
	next: str  # what the user should do
	flow_ids: list[str]
	evidence: dict[str, str | float | bool]


class Segment(TypedDict):
	"""One hop of the health path. Part of Health."""

	name: SegmentName
	status: SegmentStatus
	rtt_ms: float | None  # None until probed
	loss_pct: float | None


class Health(TypedDict):
	"""Network health score with its explanation; segments holds only those that apply. schemas/app/health.schema.json"""

	type: Literal["health"]
	v: Literal[1]
	ts: float
	score: int  # 0-100
	cause: str  # one sentence naming the worst segment and the evidence
	segments: list[Segment]
	handshake_rtt_ms: float | None
	retransmissions: int
	dns_failures: int


class Conversation(TypedDict):
	"""Traffic between one local device and one remote name. schemas/app/conversation.schema.json"""

	type: Literal["conversation"]
	v: Literal[1]
	device: str  # local IP
	maker: str  # from the MAC address, "" if unknown
	name: str  # remote name from DNS or TLS SNI, else the remote IP
	proto: Proto
	bytes: int  # both directions
	packets: int


class Wifi(TypedDict):
	"""One reading of the Wi-Fi link from the OS; None where the platform does not report a field. schemas/app/wifi.schema.json"""

	type: Literal["wifi"]
	v: Literal[1]
	ts: float
	interface: str
	ssid: str | None
	rssi_dbm: int | None  # closer to 0 is stronger
	tx_rate_mbps: float | None
	channel: int | None
	band_ghz: Literal["2.4", "5", "6"] | None


AppRecord = Alert | Health | Conversation | Wifi
