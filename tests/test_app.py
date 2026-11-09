"""End-to-end checks of the browser app (parity-rebuild Stage 5), headless.

A simulated user types into the real widgets. Each test checks that the screen shows exactly
what catmass.calculator computes for the same inputs; tests/test_calculator.py ties the
calculator to v3's golden values. No socket may be opened during these tests (no network calls).
"""
import asyncio
import json
import socket

import pytest
from nicegui import ui
from nicegui.testing.user_simulation import user_simulation

from catmass import app as catmass_app
from catmass import calculator as calc
from catmass import savefile
from tests.parity import golden
from tests.test_calculator import inputs_from_golden


LOOPBACK = {"127.0.0.1", "::1", "localhost"}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Refuse and record any connection that would leave this machine. Loopback is allowed:
    on Windows, asyncio's event loop connects a socket pair over 127.0.0.1 internally."""
    attempts = []
    connect = socket.socket.connect

    def guarded(self, address, *args, **kwargs):
        host = address[0] if isinstance(address, tuple) else address
        if host not in LOOPBACK:
            attempts.append(address)
            raise OSError("network disabled in tests")
        return connect(self, address, *args, **kwargs)
    monkeypatch.setattr(socket.socket, "connect", guarded)
    yield
    assert not attempts, f"the app tried to open network connections: {attempts}"


async def settle():
    """Widgets bound to plain Python objects refresh on NiceGUI's binding cycle (0.1 s)."""
    await asyncio.sleep(0.3)


def text(user, marker):
    (element,) = user.find(marker=marker).elements
    return element.text


async def fill(user, marker, value):
    if value:
        user.find(marker=marker).type(value)


def choose(user, marker, option):
    """Pick an option of the one select or radio with this marker (by its visible label).
    find(option) alone would also match other widgets showing the same text, e.g. 'Other'."""
    widget = user.find(marker=marker)
    if any(isinstance(e, ui.select) for e in widget.elements):
        widget.click()  # open the dropdown
    widget.target = option
    widget.click()


async def enter(user, inp: calc.CalculatorInputs):
    """Type the inputs into the Calculator tab like a user."""
    s, sc, h = inp.sample, inp.scan, inp.holder
    for marker, value in (("formula", s.formula), ("diluent", s.diluent),
                          ("sample_ratio", s.sample_ratio), ("diluent_ratio", s.diluent_ratio)):
        await fill(user, marker, value)
    if sc.edge != "K":
        choose(user, "edge", sc.edge)
    await fill(user, "element" if sc.edge != "Other" else "other_energy",
               sc.element if sc.edge != "Other" else sc.other_energy_eV)
    if h.holder != "pellet":
        choose(user, "holder", calc.HOLDERS[h.holder])
    for marker, value in (("pellet_mm", h.pellet_mm), ("capillary_mm", h.capillary_mm),
                          ("bed_mm", h.bed_mm)):
        await fill(user, marker, value)
    if h.holder == "other":  # the UI pre-fills the area from the previous holder
        user.find(marker="other_area").clear().type(h.other_area_cm2)
    if h.angle_on:
        user.find(marker="angle_on").click()
        await fill(user, "angle_deg", h.angle_deg)
    await fill(user, "absorption_length", inp.absorption_length)


def assert_screen_matches(user, expected: calc.Calculation):
    if not expected.ok:
        assert text(user, "error") == expected.error
        return
    shown = expected.shown
    assert text(user, "mass") == f"{shown['mass']} mg"
    assert text(user, "step").startswith(shown["step"])
    assert text(user, "sample_mass") == f"{shown['sample_mass']} mg"
    assert text(user, "diluent_mass") == f"{shown['diluent_mass']} mg"
    assert text(user, "E0") == f"{shown['E0']} eV"
    (table,) = user.find(marker="values_used").elements
    assert table.rows == [vars(u) for u in expected.values_used]


SCREEN_CASES = ["core-PtL3-Al2O3-1wt", "core-FeK-CeO2-0.1wt", "A-Pt-foil-L1",
                "A-other-at-edge", "E-cap-3mm-bed-2.5cm", "E-other-area-0.125", "E-angle30",
                "F-Fe2O3-BN-10to90", "H-dilution-no-ratio", "H-bad-symbol", "D-Pt-TiO2-TiK"]


@pytest.mark.parametrize("case_id", SCREEN_CASES)
async def test_screen_shows_the_calculation(case_id):
    inp = inputs_from_golden(golden(case_id))
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        await enter(user, inp)
        user.find(marker="calculate").click()
        await user.should_see("Values used in this calculation")
        assert_screen_matches(user, calc.run_calculation(inp))


async def test_sample_builder_fills_the_calculator():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        for marker, value in (("b_support", "Al2O3"), ("b_site1", "Pt"), ("b_wt1", "1")):
            user.find(marker=marker).type(value)
        user.find(marker="use_metals").click()
        await settle()
        expected = golden("core-PtL3-Al2O3-1wt")["snapshots"][-1]["main_window"][
            "textbox_dil01"]["text"]
        (formula,) = user.find(marker="formula").elements
        assert formula.value == expected
        user.find(marker="b_wt1").type("00")  # "100" wt%: an error, formula unchanged
        user.find(marker="use_metals").click()
        await user.should_see("must be less than 100")
        await settle()
        assert formula.value == expected


async def test_ion_chamber_calculated_with_the_mass_and_on_update():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        await enter(user, inputs_from_golden(golden("G-IC-15cm-N2-100")))
        user.find(marker="calculate").click()
        assert text(user, "ic_result") == "18.32 % beam absorbed"  # default 15 cm, 100% N2
        user.find(marker="ic_percent").type("50")
        user.find(marker="ic_update").click()
        assert text(user, "ic_result").endswith("% beam absorbed")
        assert text(user, "ic_result") != "18.32 % beam absorbed"


async def test_beam_path_needs_a_calculation_first():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        user.find(marker="solvent_thickness").type("0.1")
        user.find(marker="transmitted").click()
        assert "calculate the sample mass first" in text(user, "solvent_result")
        await enter(user, inputs_from_golden(golden("G-materials-defaults")))
        user.find(marker="calculate").click()
        user.find(marker="transmitted").click()
        assert text(user, "solvent_result") == "23.5%"  # change F1


async def test_results_marked_out_of_date_after_an_input_changes():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        await enter(user, inputs_from_golden(golden("A-Pt-foil-L3")))
        user.find(marker="calculate").click()
        await user.should_not_see(marker="stale")
        user.find(marker="absorption_length").type("1")
        await user.should_see(marker="stale")


async def test_other_area_prefilled_once_from_previous_holder():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        choose(user, "holder", "Other area")
        await settle()
        (area,) = user.find(marker="other_area").elements
        assert area.value == "0.3848451"  # 7 mm pellet, the default holder


async def test_save_and_open_round_trip():
    inp = inputs_from_golden(golden("F-Fe2O3-BN-10to90"))
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        await enter(user, inp)
        user.find(marker="calculate").click()
        user.find("Save").click()
        response = await user.download.next()
    text = response.content.decode("utf-8")
    data = json.loads(text)
    assert data["results_at_save"]["note"] == savefile.RESULTS_NOTE
    loaded = savefile.loads(text)
    assert loaded.calculator.sample == inp.sample
    assert calc.run_calculation(loaded.calculator).shown == calc.run_calculation(inp).shown
