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
    "F1": {
        "finding": 1,
        "approved": "researcher, 2026-11-08",
        "title": "Beam-path panel: each row uses its own material",
        "why": "v3 computed the Solvents row with the gas dropdown's material and the Metals row "
               "with the solvent dropdown's (Calculatetransbeam / Calculateabsbeam_materials).",
        "numbers_changed": True,
        "values": [
            # E0 = 7112 eV (Fe K), evaluated at E0 + 50 eV
            # 0.1 cm water (v3 used air) / 1 mil aluminum (v3 used water)
            {'case': 'G-materials-defaults', 'snapshot': 'transmitted', 'field': 'textboxP06', 'v3': '99.8%', 'new': '23.5%'},
            {'case': 'G-materials-defaults', 'snapshot': 'transmitted', 'field': 'textboxP07', 'v3': '96.4%', 'new': '62.2%'},
            {'case': 'G-materials-defaults', 'snapshot': 'final', 'field': 'textboxP06', 'v3': '0.0', 'new': '1.4'},
            {'case': 'G-materials-defaults', 'snapshot': 'final', 'field': 'textboxP07', 'v3': '0.0', 'new': '0.5'},
            # 500 um ethanol (v3 used helium) / 0.001 cm platinum (v3 used ethanol)
            {'case': 'G-materials-units', 'snapshot': 'transmitted', 'field': 'textboxP06', 'v3': '100.0%', 'new': '70.1%'},
            {'case': 'G-materials-units', 'snapshot': 'transmitted', 'field': 'textboxP07', 'v3': '99.3%', 'new': '0.4%'},
            {'case': 'G-materials-units', 'snapshot': 'final', 'field': 'textboxP06', 'v3': '0.0', 'new': '0.4'},
            {'case': 'G-materials-units', 'snapshot': 'final', 'field': 'textboxP07', 'v3': '0.0', 'new': '5.6'},
        ],
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
