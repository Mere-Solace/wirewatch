# Kai: status

Last updated Nov 25, 2026. This branch holds one folder per person (Brendan's idea in GroupMe, Nov 24). It never merges into `main`.

## My parts
| Part | Where | State |
|---|---|---|
| Dashboard server + shared record types (`Alert`, `Health`, `Conversation`) | PR #20, branch `kai/dashboard-server` | Open. Needs #19 merged first, since it's based on `dev`. |
| `main.py` capture loop | PR #20 | Runs from `uv run scripts/dev.py`: live capture on en0, packets show up in `/api/state`. |
| Honors detector (separate by contract, nothing imports it) | PR #21, branch `kai/honors` | Open. Replaces `kai/honors-detector`, which also had an old copy of the dashboard server. |
| Team contributions slide (slide 9) | deck | Not started |
| Merging PRs | | Waiting on reviews |

## How to plug in
Your module's class has one `process(record)` method that returns a list of results. I add it to `DETECTORS` in `main.py`, and its alerts go to `server.add_alert`. Health and conversations go to `server.set_health` and `server.set_conversations`. Import record types from `wirewatch.records`, not from each other.

## Blocked on
- **Brendan:** the sensor sends only `src`, `dst`, lengths and timestamps. The port scan rule needs `dport` and TCP `flags`. Its filter is also `tcp`, so DNS and ARP never reach Python.
- **Maitri:** `PortScanRule` reads `src_ip`, `dst_ip`, `dst_port` and `time`. The sensor uses `src` and `dst`, and the Python rules file says timestamps are `ts`. We should pick one set of names when the new sensor fields land, then I'll add the rule to `DETECTORS`.
- **Juan:** `frontend/static/index.html` in #20 is a placeholder that prints the JSON. It's yours to replace.

## Demo plan I'm pushing for
One path that works live: capture, then a port scan alert, then the dashboard shows it, with nmap scanning the laptop on the video. Health score, site names, ARP and the Isolation Forest go on the "next steps" slide unless someone has them working by Dec 1.

## Dates (check D2L)
- Fri Dec 4: 10-minute pitch and live demo.
- Mon Dec 7: Phase 3 deck with the demo video due in D2L.
