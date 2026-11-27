import json
import os
import sys
from pathlib import Path

from .score import health_score

INPUT_KEYS = ("handshake_ms", "retransmit_pct", "dns_fail_pct", "ping_ms")


def find_testdata():
    override = os.environ.get("WIREWATCH_TESTDATA")
    if override:
        return Path(override)
    here = Path(__file__).resolve().parent
    for folder in (here, *here.parents):
        candidate = folder / "testdata"
        if candidate.is_dir():
            return candidate
    return None


def data_files():
    folder = find_testdata()
    return sorted(folder.glob("*.json")) if folder else []


def load_case(path):
    case = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    inputs = case.get("inputs", {})
    return {k: inputs.get(k) for k in INPUT_KEYS}, case.get("expect", {})


if __name__ == "__main__":
    files = [Path(a) for a in sys.argv[1:]] or data_files()
    if not files:
        print(f"No data files found. Looked in: {find_testdata() or 'no testdata folder'}")
        sys.exit(2)
    for f in files:
        inputs, _ = load_case(f)
        score, cause = health_score(**inputs)
        print(f"{f.name}: {score}  {cause}")