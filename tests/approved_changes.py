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
    "F2": {
        "finding": 2,
        "approved": "researcher, 2026-11-08 (fix if partial densities are correct; confirmed "
                    "against xraydb.ionchamber_fluxes)",
        "title": "Ion chambers: each gas at its own partial density",
        "why": "v3 applied the mixture's average density to each gas's mu/rho, under-counting "
               "the denser gas in a mix. Exact only for a single gas.",
        "numbers_changed": True,
        "values": [
            # % beam absorbed at E0 = 7112 eV (Fe K)
            {'case': 'G-IC-10cm-He-N2-50', 'snapshot': 'final', 'field': 'textboxP11', 'v3': '3.89', 'new': '6.55'},
            # single gas: value unchanged, listed because the underlying calls changed
            {'case': 'G-IC-15cm-N2-100', 'snapshot': 'final', 'field': 'textboxP11', 'v3': '18.32', 'new': '18.32'},
            {'case': 'G-IC-30cm-Ar20-N2', 'snapshot': 'final', 'field': 'textboxP11', 'v3': '81.38', 'new': '87.40'},
            {'case': 'G-IC-45cm-Ar-He-50', 'snapshot': 'final', 'field': 'textboxP11', 'v3': '97.30', 'new': '99.86'},
            {'case': 'G-IC-60cm-N2-30-He-1500torr', 'snapshot': 'final', 'field': 'textboxP11', 'v3': '18.57', 'new': '38.38'},
            {'case': 'G-IC-other-20cm', 'snapshot': 'final', 'field': 'textboxP11', 'v3': '92.87', 'new': '95.25'},
        ],
    },
    "F7": {
        "finding": 7,
        "approved": "researcher, 2026-11-08 (validation in the parsing layer, UI only displays)",
        "title": "Invalid input returns an 'ERROR - ...' message instead of crashing",
        "why": "v3 raised (the exe would close) on invalid formulas, element symbols, missing "
               "edges, non-numeric or out-of-range numbers, loadings over 100 wt%, and an 'Other' "
               "energy with a decimal when plotting (int() of the energy text).",
        "numbers_changed": False,  # valid input is unchanged; only former crashes change
        "minimum_energy": "2000 eV for edges and 'Other' energies (researcher, 2026-11-08). "
                          "Rejects inputs v3 computed between ~430 and 2000 eV (e.g. Si K, Al K); "
                          "no golden case lies in that range.",
        "values": [
            {'case': 'H-bad-formula', 'snapshot': 'final', 'field': 'dilute_sample', 'v3': ['None', 'al2o3'], 'new': ["ERROR - Sample 'al2o3' is not a valid chemical formula (Found a lowercase character or digit where not allowed). Element symbols are case-sensitive, e.g. Al2O3", '']},
            {'case': 'H-bad-formula', 'snapshot': 'final', 'field': 'calculate_result raises', 'v3': 'ValueError: Invalid chemical formula: Found a lowercase character or digit where not allowed', 'new': None},
            {'case': 'H-bad-formula', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': '', 'new': "ERROR - Sample 'al2o3' is not a valid chemical formula (Found a lowercase character or digit where not allowed). Element symbols are case-sensitive, e.g. Al2O3"},
            {'case': 'H-bad-symbol', 'snapshot': 'final', 'field': 'calculate_result raises', 'v3': 'ValueError: Invalid chemical symbol', 'new': None},
            {'case': 'H-bad-symbol', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': '', 'new': "ERROR - Element to be Scanned 'Xx' is not an element symbol. Symbols are case-sensitive, e.g. Fe"},
            # "Other" E0 = 11564.5 eV: the fluorescence panel is centred on it (v3 crashed)
            {'case': 'H-other-decimal-plot', 'snapshot': 'final', 'field': 'plot', 'v3': "ValueError: invalid literal for int() with base 10: '11564.5'", 'new': {'fluorescence_xlim': [10764.5, 12364.5]}},
        ],
    },
    "F3a": {
        "finding": 3,
        "approved": "researcher, 2026-11-14 (fix the note text in Release 1; the retry algorithm "
                    "stays for Release 2, Upgrade 3)",
        "title": "Retry-loop note states the edge-step window actually used",
        "why": "v3's note printed its loop counter (50 - whilecount, e.g. '± 43') instead of the "
               "window used (-10 eV in that case), contradicting the 'values used' list.",
        "numbers_changed": False,  # displayed note text only; no calculated value changes
        "values": [
            {'case': 'H-FeCeO2-retry-angle', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable)'},
            {'case': 'H-FeCeO2-retry-noplot', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'H-element-not-in-sample', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'H-off-edge', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'core-FeK-Al2O3-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'core-FeK-CeO2-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'core-FeK-CeO2-1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 45 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± 10 eV, consider fluorescence'},
            {'case': 'core-FeK-CeO2-3wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 47 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± 30 eV, consider fluorescence'},
            {'case': 'core-FeK-SiO2-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'core-MoK-CeO2-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'core-PtL3-Al2O3-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 46 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± 20 eV, consider fluorescence'},
            {'case': 'core-PtL3-CeO2-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 43 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± -10 eV (below/above swapped; step not reliable), consider fluorescence'},
            {'case': 'core-PtL3-CeO2-1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 46 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± 20 eV, consider fluorescence'},
            {'case': 'core-PtL3-SiO2-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 45 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± 10 eV, consider fluorescence'},
            {'case': 'core-RhK-CeO2-0.1wt', 'snapshot': 'final', 'field': 'textbox_Xray_05', 'v3': 'Note: Edge step at: E0 ± 45 eV, consider fluorescence', 'new': 'Note: Edge step at: E0 ± 10 eV, consider fluorescence'},
        ],
    },
    "P1": {
        "finding": None,  # researcher request, not a v3 defect
        "approved": "researcher, 2026-11-14",
        "title": "Fluorescence plot: grey band around an 'Other' energy, as for K/L edges",
        "why": "Consistency: v3 shaded +/-250 eV around the scanned edge's main line, but drew no "
               "band for an 'Other' energy.",
        "numbers_changed": False,  # plot shading only
        "values": [
            # 'Other' E0 = 11564 eV: band 11564 +/- 250 eV, up to the strongest line (Pt La1)
            {'case': 'H-other-at-edge-plot', 'snapshot': 'final', 'field': 'fluorescence band', 'v3': None, 'new': [11314.0, 11814.0, 0.818656]},
        ],
    },
    "M8": {
        "finding": 8,
        "approved": "researcher, 2026-11-14 (M edges needed in Release 1)",
        "title": "M1-M5 edges in the competing-edge table, k panel and fluorescence lines",
        "why": "v3 listed K and L1-L3 only. M edges of heavy elements lie at 2-5.5 keV (e.g. Pb "
               "M5 2484 eV, 12 eV above S K; Pt M 2.1-3.3 keV) and their M lines (e.g. Pb Ma "
               "2342 eV next to S Ka) compete in low-energy work.",
        "numbers_changed": True,  # added entries; every v3 entry is unchanged
        "rule": "With v3's edges (K to L3) every value equals the golden file. The full output is "
                "v3's entries plus the M entries, in v3's order; each M edge energy equals "
                "xraylib EdgeEnergy and each M line equals xraydb xray_lines.",
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
