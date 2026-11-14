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


def choose_diluent(user, formula):
    """Pick a listed diluent from the dropdown, or enter a new formula. For a typed formula the
    select adds it as a new option and selects it (new-value-mode 'add-unique'); the simulated
    user does the same, since typing into a select's input box is a browser-side action."""
    if formula in calc.DILUENTS:
        choose(user, "diluent", calc.DILUENTS[formula])
        return
    (select,) = user.find(marker="diluent").elements
    with user.client:
        select.options[formula] = formula
        select.update()
        select.value = formula


async def enter(user, inp: calc.CalculatorInputs):
    """Type the inputs into the Calculator tab like a user."""
    s, sc, h = inp.sample, inp.scan, inp.holder
    await fill(user, "formula", s.formula)
    if s.diluent:
        choose_diluent(user, s.diluent)
    for marker, value in (("sample_ratio", s.sample_ratio), ("diluent_ratio", s.diluent_ratio)):
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
    if h.holder == "other":  # blank means the 1 cm2 default; type the case's area
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


async def test_other_area_defaults_to_1_cm2():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        await enter(user, inputs_from_golden(golden("A-Pt-foil-L3")))
        choose(user, "holder", "Other area")
        await settle()
        (area,) = user.find(marker="other_area").elements
        assert area.value == "" and area.props["placeholder"] == "1 (default)"
        user.find(marker="calculate").click()
        await user.should_see("Values used in this calculation")
        (table,) = user.find(marker="values_used").elements
        assert {"quantity": "Sample area", "value": "1 cm²", "source": "default"} in table.rows


async def test_header_title_and_values_used_collapsed():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        assert text(user, "title").startswith("XAS Sample Mass Calculator")
        await enter(user, inputs_from_golden(golden("A-Pt-foil-L3")))
        user.find(marker="calculate").click()
        (expansion,) = user.find(marker="values_expansion").elements
        assert expansion.value is False  # starts collapsed (researcher 2026-11-14)


async def test_plot_range_set_on_plots_tab():
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        await enter(user, inputs_from_golden(golden("A-Pt-foil-L3")))
        user.find(marker="calculate").click()
        user.find(marker="plot_upper").type("2500")
        user.find(marker="update_plots").click()
        await settle()
        # find() returns an unordered set: pick the energy figure by its title
        (energy,) = [p for p in user.find(ui.plotly).elements
                     if p.figure["layout"]["title"]["text"] == "Sample absorption"]
        E0 = calc.run_calculation(inputs_from_golden(golden("A-Pt-foil-L3"))).E0_eV
        assert energy.figure["layout"]["xaxis"]["range"][1] == E0 + 2500


async def test_diluent_dropdown_cellulose_and_typed_formula():
    """Cellulose from the list is C6H10O5 (researcher 2026-11-14); any formula can be typed."""
    for formula in ("C6H10O5", "C"):
        inp = inputs_from_golden(golden("F-Fe2O3-C-10to90"))
        inp.sample.diluent = formula
        async with user_simulation(catmass_app.root) as user:
            await user.open("/")
            await enter(user, inp)
            user.find(marker="calculate").click()
            await user.should_see("Values used in this calculation")
            expected = calc.run_calculation(inp)
            assert_screen_matches(user, expected)
            (table,) = user.find(marker="values_used").elements
            label = "Cellulose (C6H10O5)" if formula == "C6H10O5" else "C"
            assert {"quantity": "Diluent", "value": label, "source": "entered"} in table.rows


async def test_quit_button_stops_the_app(monkeypatch):
    calls = []
    monkeypatch.setattr(catmass_app.app, "shutdown", lambda: calls.append("shutdown"))
    async with user_simulation(catmass_app.root) as user:
        await user.open("/")
        user.find(marker="quit").click()
        await asyncio.sleep(0.8)  # the app stops 0.5 s after replacing the page with a note
    assert calls == ["shutdown"]


async def test_auto_stop_waits_for_reconnect():
    """Stops only when no tab is connected after the grace period (page reloads survive)."""
    class Client:
        def __init__(self, id):
            self.id = id
    calls = []
    stop = catmass_app.AutoStop(lambda: calls.append("shutdown"), grace=0.05)
    stop.connected(Client("a"))
    reload = asyncio.ensure_future(stop.disconnected(Client("a")))
    stop.connected(Client("b"))  # the reloaded page reconnects within the grace period
    await reload
    assert calls == []
    await stop.disconnected(Client("b"))  # last tab closed
    assert calls == ["shutdown"]


def contrast(a, b):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_theme_text_contrast():
    """WCAG AA (4.5:1) for every theme colour used as text or behind white text."""
    page = {False: "#FFFFFF", True: "#121212"}  # Quasar light page / dark page
    for dark, colours in catmass_app.THEMES.items():
        assert contrast("#FFFFFF", colours["primary"]) >= 4.5   # header, buttons
        assert contrast(colours["negative"], page[dark]) >= 4.5  # error text
        assert contrast(colours["warning"], page[dark]) >= 4.5   # out-of-date text


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
