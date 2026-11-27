# AGENTS.md

Instructions for any coding agent working in this repository. Teammates: this is also the shortest accurate map of the project.

Wirewatch is a network health monitor for CS4622 at KSU, built by three sub-teams. A C++20 **sensor** captures packets and writes NDJSON to stdout. A Python package starts the sensor as a subprocess, reads its output, runs metrics and detectors on it, and serves a local dashboard.

## Before you write any code

Most wasted work on this team comes from building something that already exists on another branch. Before starting a task:

1. Run `git fetch --all`, then `git branch -r` and `gh pr list`. Read any branch or PR whose name or files overlap your task.
2. Search for an existing type or helper before writing one: `git grep -n "class <Name>\|TypedDict"` across `dev` and the open branches.
3. If your task overlaps someone else's branch, PR, or team area (table below), **stop and tell the user** instead of writing a parallel version.

## Rules files

Read the relevant file in full before editing. Both are binding.

- C++ (`sensor/`): `sensor/enforcement.txt`
- Python (`src/wirewatch/`, `tests/`, `scripts/`): `src/wirewatch/enforcement.txt`

If a rule blocks the task, say so to the user. Do not work around it or weaken it.

## Data flow

```
sensor (C++ subprocess, needs capture privileges)
  └─ NDJSON on stdout: packets now; flows, stats, dns, arp planned
       └─ wirewatch.backend.capture_packets()  (Python generator, one record per line)
            └─ analysis/: metrics and detectors, pure functions of the records
                 └─ frontend/: local dashboard
```

- Per-packet work belongs in the sensor. Python receives aggregated records (flows, per-second stats) and a sampled packet feed, never every packet at line rate.
- Capture must run through the sensor executable. Calling capture through the pybind extension does not get capture privileges.

## Record types are a contract

Records that cross a boundary (sensor → Python, module → module) are defined once and imported everywhere else.

- Schemas in `schemas/` are the source of truth, `src/wirewatch/records.py` mirrors them in Python, and `docs/design/records.md` explains the conventions.
- `backend/__init__.py` still has its own `Packet` matching what the sensor emits today. It goes away once the sensor emits the new `packet` record.
- **Do not invent a new record shape or rename keys in a feature PR.** If you need a field that doesn't exist, tell the user. The change goes to the C++ emitter, `schemas/`, the Python type, and the parser together (see "Wire types stay in sync" in both rules files).

## Where things go

| Path | What | Owning team |
|---|---|---|
| `sensor/src/core/`, `capture/`, `app/` | C++ capture, parsing, flow and metric aggregation | Capture & Metrics |
| `src/wirewatch/backend/` | Starting the sensor, parsing its output | Capture & Metrics |
| `src/wirewatch/analysis/` | Health metrics, and detectors in `analysis/detection/` | Capture & Metrics (health), Threat Detection (detection) |
| `src/wirewatch/frontend/` | Dashboard and the entry point | Data & Dashboard |
| `src/wirewatch/lab/` | Test traffic generation, Docker lab | Threat Detection |
| `schemas/` | Wire and storage schemas | whoever changes a record, reviewed by Capture & Metrics |
| `tests/` | pytest tests, `test_<module>.py` | author of the module |
| `testdata/` | Small committed pcap fixtures | anyone |
| `honors/` | An individual honors contract. Must stay independent; never import it or copy from it into the app | Kai only |

Do not add files at the repository root. If nothing in the table fits, ask.

## Build and run

```sh
uv run scripts/dev.py          # build everything, grant capture permission, run the app
uv run pytest                  # Python tests
```

Sensor only: see "Building the sensor on its own" in `README.md`. Never run `uv` with `sudo`.

## Done means

- It runs from `uv run scripts/dev.py`, not only from a test.
- Tests and checks from the relevant rules file pass.
- The PR says what it changes, how to reach it in the running app, and whether any record type changed.

## Git and GitHub

### Branches

- Name branches `<type>/<topic>`: `feat/`, `fix/`, `ref/`, `docs/`, `chore/`, then a few lowercase words joined by hyphens that name the change, e.g. `feat/flow-records`, `fix/dns-timeout`. Not a person's name, not a team name.
- One branch is one change. If a second, unrelated change comes up, it gets its own branch.
- Branch from an up-to-date `main` (`git fetch origin && git switch -c <branch> origin/main`).
- If you truly need someone's unmerged work, branch from their branch, not from `dev` or another catch-all, and put `Depends on #NN` at the top of the PR. Rebase onto `main` once that PR merges.
- No long-lived branches. A branch older than about a week should be merged, split, or closed.
- Delete a branch once its PR merges.

### Commits

- Message: `<type>: <what changed>`, lowercase, imperative, no trailing period. Types are `add`, `fix`, `ref`, `docs`, `chore`. Example: `fix: flush cout in capture.cxx`.
- Keep unrelated changes in separate commits, and don't mix formatting with logic.
- Never commit build output, `.venv/`, captures with real traffic, or secrets.

### Pull requests

- PRs target `main` and are small enough to review in one sitting. Never push to `main` directly.
- Open a draft PR early if others will build on your work, so it shows up in `gh pr list`.
- A record type change goes in its own PR, before the feature that uses it (see "Record types are a contract").
- Keep the PR current by rebasing onto `main`. Resolve conflicts on your own branch, never in someone else's.

### Other people's branches

- Never push to, rebase, or force-push a branch you didn't create. To suggest a change, comment on the PR or open a PR into their branch.
- `git push --force-with-lease` is fine on your own branch. Never use plain `--force`.
- Agents: never push, open, merge, or close a PR, or delete a branch, without the user asking for that specific action.
