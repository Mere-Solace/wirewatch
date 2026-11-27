# name: (weight, value at which this metric counts as fully bad)
WEIGHTS = {
    "handshake_ms": (25, 200.0),
    "retransmit_pct": (35, 5.0),
    "dns_fail_pct": (20, 10.0),
    "ping_ms": (20, 150.0),
}

CAUSES = {
    "handshake_ms": "Connections are slow to start (median handshake {v:.0f} ms).",
    "retransmit_pct": "Packets are being resent ({v:.1f}% retransmissions), which usually means loss on the path.",
    "dns_fail_pct": "Name lookups are failing ({v:.1f}% of DNS queries), so sites may not load.",
    "ping_ms": "Round-trip time is high (ping {v:.0f} ms), so everything responds slowly.",
}


def health_score(handshake_ms, retransmit_pct, dns_fail_pct, ping_ms=None):
    """Return (score, cause). score is an int from 0 to 100.

    handshake_ms:   median TCP handshake time in milliseconds.
    retransmit_pct: share of TCP segments that were resends, 0 to 100.
    dns_fail_pct:   share of DNS queries that failed, 0 to 100.
    ping_ms:        median round-trip time (ping) in milliseconds.
    Pass None for an input that was not measured. It is left out of the
    score (the other inputs are rescaled) and named in the cause sentence.
    """
    values = {
        "handshake_ms": handshake_ms,
        "retransmit_pct": retransmit_pct,
        "dns_fail_pct": dns_fail_pct,
        "ping_ms": ping_ms,
    }
    measured = {n: v for n, v in values.items() if v is not None}
    missing = [n for n, v in values.items() if v is None]

    if not measured:
        return None, "No inputs were measured, so no score can be given."

    total_weight = sum(WEIGHTS[n][0] for n in measured)
    penalties = {
        n: WEIGHTS[n][0] * min(v / WEIGHTS[n][1], 1.0) for n, v in measured.items()
    }
    score = round(100 - 100 * sum(penalties.values()) / total_weight)

    worst = max(penalties, key=penalties.get)
    if penalties[worst] == 0:
        cause = "No problems detected."
    else:
        cause = CAUSES[worst].format(v=measured[worst])
    if missing:
        cause += " Not measured: " + ", ".join(missing) + "."
    return score, cause