# Record types

A record is a JSON object with a fixed set of fields. There are two kinds:

- **Wire records** are produced by the C++ sensor and sent to Python as NDJSON, one per line on stdout. They are mirrored in both languages.
- **App records** are produced in Python and never reach the sensor. They are defined in Python only.

## Records

| Kind | `type` | What it is |
|---|---|---|
| wire | `packet` | one sampled packet: addresses, ports, protocol, TCP flags, lengths |
| wire | `flow` | one bidirectional flow, emitted when it ends: bytes and packets per direction, handshake RTT, retransmissions, resets |
| wire | `stats` | sensor counters for about one second: packets, bytes, drops, decode errors, sampled-out |
| wire | `dns` | one query matched to its response: name, type, response code, answers, response time |
| wire | `arp` | one ARP request or reply, unsampled |
| app | `alert` | one detection in plain language: severity, rule, device, what / why / next, evidence |
| app | `health` | 0-100 score, the sentence explaining it, and per-segment status (`this_pc`, `wifi`, `router`, `internet`, `dns`) |
| app | `wifi` | one reading of the Wi-Fi link: signal, tx rate, channel, band |
| app | `conversation` | traffic between one local device and one remote name |

Per-flow metrics (handshake RTT, retransmissions) are computed in the sensor and travel in `flow`. Health metrics are computed in Python.

## Where they are defined

| Layer | Location |
|---|---|
| Schema (**source of truth**) | `schemas/wire/*.schema.json`, `schemas/app/*.schema.json`, JSON Schema 2020-12 |
| Python | `src/wirewatch/records.py`: one `TypedDict` per schema, plus the shared `Literal`s |
| C++ | `sensor/src/core/`: one struct per wire record, serialized with nlohmann-json's `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE` in a single TU |

## Conventions

- Every record has `"type"` and `"v"` (schema version). Unknown `type` or `v` is logged and dropped.
- Timestamps are `ts`, epoch seconds as a float. A second timestamp gets a suffix: `ts_end`.
- Names are `snake_case`, with one name per concept across records: `src_ip`, `dst_ip`, `src_port`, `dst_port`, `proto`, `tcp_flags`.
- A field with a unit has it in the name: `handshake_rtt_ms`, `interval_seconds`, `loss_pct`, `rssi_dbm`.
- A field that doesn't apply is `null`, never missing. Every field is required.
- No extra fields: every schema sets `additionalProperties: false`.
- TCP flags are the set flags as letters in `FSRPAUEC` order: `"S"` is SYN, `"SA"` is SYN-ACK.
- MAC addresses are lowercase and colon-separated.
- Severity is `LOW`, `MEDIUM`, `HIGH` or `CRITICAL`.

## Enforcement

| Check | Python | C++ |
|---|---|---|
| Field names and types while writing code | basedpyright against the `TypedDict`s | compiler; designated initializers with `-Werror` |
| Lossless encode and decode | pytest round-trip test | doctest round-trip test with every field set to a distinct non-default value |
| Malformed input at runtime | `backend` checks `type`, `v` and required keys per line; logs and drops bad lines | n/a, producer |
| Mirrors match the schemas | parity test: `TypedDict` keys and `Literal`s equal schema properties and enums | boundary test |
| Both sides agree | boundary test: sensor output from a `testdata/` pcap validates against `schemas/` and parses into the `TypedDict`s | same test |

## Changing a record

One PR changes every mirror: schema, `records.py`, the C++ struct and its serialization, and the tests. A breaking change increments `v`. See "Wire types stay in sync" in `sensor/enforcement.txt` and `src/wirewatch/enforcement.txt`.
