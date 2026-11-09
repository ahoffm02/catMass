"""Approved deviations from v3 (parity-rebuild Stage 4.3).

tests/golden/v3 is the permanent record of what v3 reports and is never edited for a change.
Each approved change is listed here: what it changes, why, who approved it, and for every golden
value it affects, the v3 value and the new value. tests/test_parity_v3.py compares those fields
with "new" instead of the golden value (and checks that the golden file still holds "v3"), so any
difference not listed here still fails. tests/test_approved_changes.py checks the new values
independently of catmass.physics wherever an independent check exists.

Values are computed (catMass calculations), not measured.
"""

CHANGES = {
    "F11": {
        "finding": 11,
        "approved": "researcher, 2026-11-08",
        "title": "Register v3's custom materials in memory; no writes to the user's xraydb file",
        "why": "xraydb.add_material rewrote the user's materials.dat on every launch, appending "
               "duplicate lines (70 on the development machine); parallel launches raced on it.",
        "numbers_changed": False,
        "values": [],
    },
}


def override(case_id, snapshot, field):
    """The approved change entry for one golden field, or None."""
    for change_id, change in CHANGES.items():
        for v in change["values"]:
            if (v["case"], v["snapshot"], v["field"]) == (case_id, snapshot, field):
                return change_id, v
    return None


def expected(case_id, snapshot, field, golden_value):
    """Value the rebuild must produce: the golden value, or an approved change's new value."""
    hit = override(case_id, snapshot, field)
    if hit is None:
        return golden_value
    change_id, v = hit
    assert golden_value == v["v3"], (f"{change_id}: golden {case_id}/{snapshot}/{field} is "
                                     f"{golden_value!r}, change record says v3 was {v['v3']!r}")
    return v["new"]
