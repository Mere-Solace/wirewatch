# Schemas

JSON Schemas for every record in Wirewatch. These are the source of truth; `src/wirewatch/records.py` and the sensor's C++ structs mirror them.

- `wire/`: records the sensor sends to Python (`packet`, `flow`, `stats`, `dns`, `arp`)
- `app/`: records made in Python (`alert`, `health`, `wifi`, `conversation`)

See [docs/design/records.md](../docs/design/records.md) for conventions and how to change a record.
