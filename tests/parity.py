"""Comparison helpers for the v3 parity tests.

Tier A tolerance (set 2026-11-08, before any comparison; vault plan "Tolerance"): the rebuild
runs on the same backend versions as the golden files, so displayed text must match exactly and
raw floats within relative 1e-9 (floating-point reordering only). Tier B (current backends) is a
separate run with its own reporting and is not handled here.
"""
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent / "golden" / "v3"
sys.path.insert(0, str(GOLDEN_DIR.parent))
from generate_golden import jsonable  # noqa: E402  (same JSON conversion as the golden files)

REL_TOL = 1e-9

STATS = {"floats": 0, "bit_identical": 0, "max_rel": 0.0, "strings": 0}


def case_ids():
    return sorted(p.stem for p in GOLDEN_DIR.glob("*.json") if p.name != "manifest.json")


@lru_cache(maxsize=None)
def golden(case_id):
    return json.loads((GOLDEN_DIR / f"{case_id}.json").read_text(encoding="utf-8"))


def assert_same(actual, expected, where="value"):
    """Recursive comparison of a rebuild value with a golden value at Tier A tolerance."""
    actual, expected = jsonable(actual), jsonable(expected)
    if isinstance(expected, bool) or expected is None:
        assert actual == expected, f"{where}: {actual!r} != golden {expected!r}"
    elif isinstance(expected, (int, float)) and not isinstance(actual, (str, list, dict)):
        assert actual is not None and not isinstance(actual, bool), \
            f"{where}: {actual!r} != golden {expected!r}"
        STATS["floats"] += 1
        if actual == expected:
            STATS["bit_identical"] += 1
            return
        rel = abs(actual - expected) / abs(expected) if expected else math.inf
        STATS["max_rel"] = max(STATS["max_rel"], rel)
        assert rel <= REL_TOL, f"{where}: {actual!r} != golden {expected!r} (rel {rel:.3g})"
    elif isinstance(expected, str):
        STATS["strings"] += 1
        assert actual == expected, f"{where}: {actual!r} != golden {expected!r}"
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(actual) == len(expected), \
            f"{where}: length {len(actual) if isinstance(actual, list) else type(actual)} " \
            f"!= golden {len(expected)}"
        for i, (a, e) in enumerate(zip(actual, expected)):
            assert_same(a, e, f"{where}[{i}]")
    elif isinstance(expected, dict):
        assert isinstance(actual, dict) and actual.keys() == expected.keys(), \
            f"{where}: keys differ"
        for k in expected:
            assert_same(actual[k], expected[k], f"{where}.{k}")
    else:
        raise TypeError(f"{where}: unexpected golden type {type(expected)}")
