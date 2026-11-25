import importlib
import json
from collections.abc import Iterator
from types import ModuleType
from typing import cast
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

import wirewatch.frontend.server as server_module
from wirewatch.records import Alert, Conversation, Health


def make_alert(ts: float = 100.0) -> Alert:
	return {
		"ts": ts,
		"type": "port_scan",
		"severity": "Medium",
		"device": "192.168.1.50",
		"title": "Port scan detected",
		"what_happened": "192.168.1.50 tried 214 different ports on 192.168.1.20 within 10 seconds.",
		"why_this_severity": "Trying many ports quickly is typical of a tool searching for open services.",
		"next_step": "Check whether you recognize this device. If not, disconnect it from the network.",
		"evidence": {"ports": 214, "seconds": 10, "target": "192.168.1.20"},
	}


def make_health() -> Health:
	return {"ts": 100.0, "score": 82, "cause": "DNS lookups are failing more than usual.",
	        "handshake_ms": 24.5, "retransmissions": 3, "dns_failures": 7}


def make_conversation() -> Conversation:
	return {"device": "192.168.1.20", "maker": "Apple", "name": "www.google.com",
	        "proto": "tcp", "bytes": 51200, "packets": 64}


@pytest.fixture
def server() -> Iterator[tuple[ModuleType, str]]:
	# reload so each test starts with empty module state
	module = importlib.reload(server_module)
	http = module.serve(0)
	yield module, f"http://127.0.0.1:{http.server_port}"
	http.shutdown()


def get_state(url: str) -> dict[str, object]:
	with urlopen(f"{url}/api/state") as response:
		return json.load(response)


def test_state_is_empty_before_any_records(server: tuple[ModuleType, str]) -> None:
	_, url = server
	assert get_state(url) == {"health": None, "alerts": [], "conversations": [], "packets": []}


def test_state_returns_every_record_kind(server: tuple[ModuleType, str]) -> None:
	module, url = server
	module.add_alert(make_alert())
	module.set_health(make_health())
	module.set_conversations([make_conversation()])

	state = get_state(url)
	assert state["alerts"] == [make_alert()]
	assert state["health"] == make_health()
	assert state["conversations"] == [make_conversation()]


def test_alerts_keep_only_the_most_recent(server: tuple[ModuleType, str]) -> None:
	module, url = server
	for i in range(module.RECENT + 5):
		module.add_alert(make_alert(ts=float(i)))

	alerts = cast(list[Alert], get_state(url)["alerts"])
	assert len(alerts) == module.RECENT
	assert alerts[0]["ts"] == 5.0


def test_page_and_unknown_path(server: tuple[ModuleType, str]) -> None:
	_, url = server
	with urlopen(url) as response:
		assert b"/api/state" in response.read()
	with pytest.raises(HTTPError) as error:
		_ = urlopen(f"{url}/nope")
	assert error.value.code == 404
