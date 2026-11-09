"""catMass save files (catmass.savefile): JSON, version 1."""
import json

import pytest

from catmass import calculator as calc
from catmass import savefile


def example_session():
    s = savefile.Session()
    s.calculator.sample = calc.SampleInputs("Fe2O3", "BN", "10", "90")
    s.calculator.scan = calc.ScanInputs("Fe", "K", "")
    s.calculator.holder = calc.HolderInputs("capillary", capillary_mm="1", bed_mm="5",
                                            angle_on=True, angle_deg="30")
    s.sample_builder.metals = calc.MetalSitesBuilder("Al2O3", "Pt", "1")
    s.beam_path.rows["solvent"].thickness = "0.1"
    s.ion_chamber.gas1_percent = "80"
    return s


def test_round_trip_restores_every_input():
    s = example_session()
    assert savefile.loads(savefile.dumps(s)) == s


def test_file_layout_is_readable_json():
    data = json.loads(savefile.dumps(example_session(), saved="2026-11-08T16:40:00"))
    assert data["catmass_file_version"] == 1
    assert data["saved_with"].startswith("catMass 2026.11.1")
    assert data["saved"] == "2026-11-08T16:40:00"
    assert data["calculator"]["holder"]["bed_mm"] == "5"
    assert data["beam_path"]["rows"]["solvent"] == {"material": "water", "unit": "cm",
                                                    "thickness": "0.1"}
    assert "results_at_save" not in data  # only written when there are results


def test_results_record_is_written_but_never_read_back():
    s = example_session()
    result = calc.run_calculation(s.calculator)
    text = savefile.dumps(s, result, beam={"solvent": "23.5%"}, ion_chamber="18.32")
    data = json.loads(text)
    record = data["results_at_save"]
    assert record["note"] == savefile.RESULTS_NOTE
    assert record["shown"] == result.shown and record["ion_chamber"] == "18.32"
    record["shown"]["mass"] = "999"  # a tampered record must not matter
    assert savefile.loads(json.dumps(data)) == s


def test_blank_means_default_and_numbers_are_accepted():
    s = savefile.loads(json.dumps({"catmass_file_version": 1,
                                   "calculator": {"absorption_length": 1.5,
                                                  "holder": {"pellet_mm": 13}}}))
    assert s.calculator.absorption_length == "1.5"
    assert s.calculator.holder.pellet_mm == "13"
    assert s.calculator.scan == calc.ScanInputs()   # missing groups take their defaults
    assert s.beam_path == calc.BeamPathInputs()


def test_unknown_keys_are_ignored():  # a later catMass may add fields
    s = savefile.loads(json.dumps({"catmass_file_version": 1, "future_setting": 3,
                                   "calculator": {"new_field": "x"}}))
    assert s == savefile.Session()


@pytest.mark.parametrize("text, message", [
    ("not json", "not valid JSON"),
    ("[1, 2]", "no 'catmass_file_version'"),
    ('{"catmass_file_version": 2, "saved_with": "catMass 2027.1.1"}', "newer catMass"),
    ('{"catmass_file_version": "one"}', "Unknown catMass file version"),
    ('{"catmass_file_version": 1, "calculator": {"holder": {"angle_on": "yes"}}}',
     "should be true or false"),
    ('{"catmass_file_version": 1, "calculator": {"sample": {"formula": ["Pt"]}}}',
     "should be text or a number"),
])
def test_bad_files_give_a_clear_message(text, message):
    with pytest.raises(savefile.SaveFileError, match=message):
        savefile.loads(text)
