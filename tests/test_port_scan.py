from wirewatch.analysis.detection.port_scan import PortScanRule


def syn(ts, port, src="10.0.0.5", dst="10.0.0.9"):
    return {"ts": ts, "src_ip": src, "dst_ip": dst, "dst_port": port, "flags": "S"}


def run(rule, events):
    alerts = []
    for ev in events:
        alerts += rule.process(ev)
    return alerts


def test_fast_scan_raises_one_alert():
    events = [syn(i * 0.1, 1000 + i) for i in range(30)]
    assert len(run(PortScanRule(), events)) == 1


def test_slow_traffic_is_quiet():
    events = [syn(float(i), 1000 + i) for i in range(30)]   # 1 port per second
    assert run(PortScanRule(), events) == []


def test_same_port_repeated_is_quiet():
    events = [syn(i * 0.1, 80) for i in range(100)]
    assert run(PortScanRule(), events) == []


def test_non_syn_packets_ignored():
    events = [dict(syn(i * 0.1, 1000 + i), flags="A") for i in range(30)]
    assert run(PortScanRule(), events) == []


def test_continuing_scan_alerts_once():
    events = [syn(i * 0.1, 1000 + i) for i in range(200)]
    assert len(run(PortScanRule(), events)) == 1