import sys

from .data import data_files, find_testdata, load_case
from .score import health_score

files = data_files()
if not files:
    print(f"SKIPPED, NOT A PASS: no .json data files in {find_testdata() or 'any testdata folder'}")
    sys.exit(2)

for f in files:
    inputs, expect = load_case(f)
    score, cause = health_score(**inputs)

    # always true for any data
    assert score is None or (isinstance(score, int) and 0 <= score <= 100), (f.name, score)
    assert isinstance(cause, str) and cause, f.name

    # only what the data file asks for
    if "min_score" in expect:
        assert score >= expect["min_score"], (f.name, score, expect)
    if "max_score" in expect:
        assert score <= expect["max_score"], (f.name, score, expect)
    if "cause_contains" in expect:
        assert expect["cause_contains"] in cause, (f.name, cause, expect)

    print("ok:", f.name, score, cause)

print(f"all ok ({len(files)} data files)")