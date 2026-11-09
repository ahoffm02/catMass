"""The Release 1 calculator rules (catmass.calculator), checked against v3 and known answers.

1. Every golden case, entered the way a Release 1 user would, gives v3's result except where an
   agreed rule changes it. The main agreed change is finding 9 (full precision, decided
   2026-11-08): v3 rounded the area and the angle-mode AL to 2 decimals and calculated with the
   rounded text. Mass is proportional to AL x area and the edge step to AL, so the expected
   Release 1 values follow from v3's raw values exactly; E0 is unchanged.
2. The agreed defaults and required fields (vault plan, "UI defaults").
Values are computed, not measured.
"""
import math

import pytest

from catmass import calculator as calc
from catmass import physics
from tests.parity import golden
from tests.test_parity_v3 import CALC_CASES, calc_groups

REL = 1e-12  # floating-point reordering only; same backends as the golden files


def inputs_from_golden(g):
    """The inputs a Release 1 user would enter to repeat a golden case (final screen)."""
    mw = g["snapshots"][-1]["main_window"]
    t = lambda name: mw[name]["text"]  # noqa: E731
    typed = {s[1] for s in g["case"]["steps"] if s[0] == "type"}
    inp = calc.CalculatorInputs()
    inp.sample = calc.SampleInputs(t("textbox_dil01"), t("textbox_dil02"), t("textbox_dil03"),
                                   t("textbox_dil04"))
    if mw["combo"]["text"] == "Other":
        inp.scan = calc.ScanInputs("", "Other", t("textbox14"))
    else:
        inp.scan = calc.ScanInputs(t("textbox2"), mw["combo"]["text"], "")
    h = calc.HolderInputs()
    if mw["radioButton1"]["checked"]:
        bed_cm = t("textbox13")
        h = calc.HolderInputs("capillary", capillary_mm=mw["combo_cap"]["text"],
                              bed_mm=repr(float(bed_cm) * 10) if bed_cm else "")
    elif mw["radioButton2"]["checked"]:
        h = calc.HolderInputs("pellet", pellet_mm=mw["combo_pel"]["text"])
    else:
        h = calc.HolderInputs("other", other_area_cm2=t("textbox16"))
    if mw["b2"]["checked"]:
        h.angle_on, h.angle_deg = True, str(mw["slider_deg"]["value"])
    inp.holder = h
    inp.absorption_length = t("textbox15") if "textbox15" in typed else ""
    return inp


# v3 behaviors the agreed Release 1 rules replace with an explicit error
EXPECTED_ERRORS = {
    "H-area-cleared": "ERROR - Sample Area not Defined",                 # finding 5
    "H-dilution-no-ratio": "ERROR - Dilution Ratio Not Defined",         # finding 6
    "H-dilution-diluent-ratio-only": "ERROR - Dilution Ratio Not Defined",
}


@pytest.mark.parametrize("case_id", CALC_CASES)
def test_golden_case_through_release1_rules(case_id):
    g = golden(case_id)
    grp = calc_groups(g)[-1]  # the last "Calculate" click before the final screen
    main = grp["main"]
    result = calc.run_calculation(inputs_from_golden(g))

    if case_id in EXPECTED_ERRORS:
        assert not result.ok and result.error == EXPECTED_ERRORS[case_id]
        return
    if "raised" in main or "ERROR" in main["result"][0]:
        assert not result.ok and result.error.startswith("ERROR - "), result
        return
    assert result.ok, result.error

    Sample, Element, Edge, area_v3, al_v3 = main["args"]
    Enot_v3, ms_v3 = main["result"][1], main["result"][2]
    step_v3 = (grp["retries"][-1] if grp["retries"] else main)["result"][3]
    assert result.E0_eV == Enot_v3

    # Full precision (finding 9): mass ~ AL x area, edge step ~ AL
    ms_new = ms_v3 * (result.area_used_cm2 * result.al_used) / (float(area_v3) * float(al_v3))
    step_new = step_v3 * result.al_used / float(al_v3)
    assert result.shown["mass"] == "{0:0.2f}".format(ms_new)
    assert result.shown["step"] == "{0:0.4f}".format(step_new)
    r = physics.calculate_result(Sample, Element, Edge, repr(result.area_used_cm2),
                                 repr(result.al_used))
    assert math.isclose(r["ms"], ms_new, rel_tol=REL)
    assert math.isclose(r["stp"], step_new, rel_tol=REL)


def test_full_precision_shift_for_default_pellet():
    """Finding 9: the default 7 mm pellet is 0.3848 cm2, which v3 calculated as 0.38."""
    g = golden("core-PtL3-Al2O3-1wt")
    result = calc.run_calculation(inputs_from_golden(g))
    area = math.pi * 0.7 ** 2 / 4  # 7 mm disc, cm2
    assert math.isclose(result.area_used_cm2, area, rel_tol=1e-14)
    ms_v3 = calc_groups(g)[-1]["main"]["result"][2]  # v3 raw mass, computed with 0.38 cm2
    assert result.shown["mass"] == "{0:0.2f}".format(ms_v3 * area / 0.38) == "83.01"  # v3 81.97
    assert result.shown["step"] == "0.1858"  # area cancels in the edge step: unchanged


def test_angle_mode_mass_equals_normal_incidence_mass():
    """A tilted sample is the same sample: mass must not depend on the angle (it did in v3,
    by 0.56% at 45 deg, from rounding both the projected area and AL)."""
    base = inputs_from_golden(golden("core-PtL3-Al2O3-1wt"))
    normal = calc.run_calculation(base)
    base.holder.angle_on, base.holder.angle_deg = True, "30"
    tilted = calc.run_calculation(base)
    assert tilted.shown["mass"] == normal.shown["mass"]
    assert math.isclose(tilted.al_used, 2.6 / 0.5, rel_tol=1e-14)


# --- Agreed defaults and required fields ------------------------------------------------------
def pt_foil(**holder):
    inp = calc.CalculatorInputs()
    inp.sample.formula, inp.scan.element, inp.scan.edge = "Pt", "Pt", "L3"
    for k, v in holder.items():
        setattr(inp.holder, k, v)
    return inp


def used(result, quantity):
    return next(u for u in result.values_used if u.quantity == quantity)


def test_defaults_are_used_and_reported():
    r = calc.run_calculation(pt_foil())
    assert r.ok
    assert (used(r, "Pellet diameter").value, used(r, "Pellet diameter").source) == ("7 mm", "default")
    assert used(r, "Absorption length at E0 + 50 eV").value == "2.6"
    assert used(r, "Plot lower limit").value == "-200 eV from E0"
    assert used(r, "Plot upper limit").value == "1000 eV from E0"
    assert used(r, "Edge energy E0").source == "calculated"


def test_capillary_lengths_in_mm():
    r = calc.run_calculation(pt_foil(holder="capillary"))  # defaults 3 mm ID, 10 mm bed
    assert math.isclose(r.area_used_cm2, 0.3, rel_tol=1e-14)
    r = calc.run_calculation(pt_foil(holder="capillary", capillary_mm="1", bed_mm="5"))
    assert math.isclose(r.area_used_cm2, 0.05, rel_tol=1e-14)


def test_other_area_required_and_angle_limits():
    assert calc.run_calculation(pt_foil(holder="other")).error == "ERROR - Sample Area not Defined"
    assert calc.run_calculation(pt_foil(holder="other", other_area_cm2="0.5")).ok
    assert "at most 90" in calc.run_calculation(pt_foil(angle_on=True, angle_deg="95")).error
    assert "greater than 0" in calc.run_calculation(pt_foil(angle_on=True, angle_deg="0")).error


def test_dilution_rules():
    inp = pt_foil()
    inp.sample.sample_ratio, inp.sample.diluent_ratio = "1", "9"  # no diluent: ratios ignored
    r = calc.run_calculation(inp)
    assert r.ok and r.shown["diluent_mass"] == "0.00"
    assert used(r, "Dilution ratios").value == "ignored (no diluent)"
    inp.sample.diluent, inp.sample.sample_ratio = "BN", ""
    assert calc.run_calculation(inp).error == "ERROR - Dilution Ratio Not Defined"
    inp.sample.sample_ratio = "1"
    r = calc.run_calculation(inp)
    assert r.ok and used(r, "Diluted sample formula").source == "calculated"


def test_other_edge_requires_energy_and_defaults_to_al_26():
    inp = pt_foil()
    inp.scan.edge = "Other"
    assert calc.run_calculation(inp).error == "ERROR - Energy to calculate sample mass not Defined"
    inp.scan.other_energy_eV = "11564"
    r = calc.run_calculation(inp)
    assert r.ok and used(r, "Absorption length at E0 + 50 eV").value == "2.6"


def test_ion_chamber_default_is_15cm_pure_n2():
    """Default 15 cm, 100% N2, 760 torr; at Fe K this is golden case G-IC-15cm-N2-100."""
    E0 = calc_groups(golden("G-IC-15cm-N2-100"))[-1]["main"]["result"][1]
    assert calc.ion_chamber(calc.IonChamberInputs(), E0) == "18.32"
    assert calc.ion_chamber(calc.IonChamberInputs(), None).startswith("ERROR - E0 not defined")
    assert "at most 100" in calc.ion_chamber(calc.IonChamberInputs(gas1_percent="120"), E0)


def test_beam_path_rows_and_defaults():
    bp = calc.BeamPathInputs()
    assert [(k, r.material, r.unit) for k, r in bp.rows.items()] == [
        ("gas", "air", "cm"), ("material", "kapton", "μm"), ("solvent", "water", "cm"),
        ("metal", "aluminum", "mils")]
    bp.rows["solvent"].thickness = "0.1"
    assert calc.beam_path(bp, 7112.0) == {"solvent": "23.5%"}  # F1 value, at E0 + 50 eV
    assert "E0 not defined" in calc.beam_path(bp, None)["solvent"]


def test_plot_and_csv_export():
    r = calc.run_calculation(pt_foil())
    files = calc.plot_csv(r.plot)
    assert set(files) == {"catmass_absorption.csv", "catmass_edges.csv",
                          "catmass_fluorescence_lines.csv"}
    lines = files["catmass_edges.csv"].splitlines()
    assert lines[0].startswith("element,edge,edge_energy_eV")
    assert any(line.startswith("Pt,L3,") for line in lines)
    inp = pt_foil()
    inp.plot_lower_eV, inp.plot_upper_eV = "500", "100"
    r = calc.run_calculation(inp)
    assert r.ok and r.plot is None and "below the upper" in r.plot_error


def test_builders():
    b = calc.MetalSitesBuilder(support="Al2O3", site1="Pt", site1_wt_percent="1")
    assert calc.build_from_metal_sites(b) == golden("core-PtL3-Al2O3-1wt")["snapshots"][-1][
        "main_window"]["textbox_dil01"]["text"]
    assert calc.builder_failed(calc.build_from_metal_sites(calc.MetalSitesBuilder()))
    c = calc.ComplexBuilder(support="SiO2", complex="Rh(CO)2(C5H7O2)", complex_wt_percent="2",
                            metal_wt_percent="1", metal_center="Rh")
    assert calc.builder_failed(calc.build_from_complex(c))  # both loadings: v3's message
