from wirewatch.analysis.detection.window import DistinctWindow


def test_counts_distinct_ports():
    w = DistinctWindow(seconds=10)
    for i in range(5):
        w.add("10.0.0.5", 1000 + i, ts=float(i))
    assert w.count("10.0.0.5", now=5.0) == 5


def test_repeated_port_counts_once():
    w = DistinctWindow(seconds=10)
    for i in range(5):
        w.add("10.0.0.5", 80, ts=float(i))
    assert w.count("10.0.0.5", now=5.0) == 1


def test_old_events_expire():
    w = DistinctWindow(seconds=10)
    w.add("10.0.0.5", 22, ts=0.0)
    assert w.count("10.0.0.5", now=20.0) == 0