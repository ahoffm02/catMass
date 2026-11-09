"""Independent checks of each approved change (tests/approved_changes.py).

A change is accepted only if its new values agree with a calculation that does not go through
catmass.physics (Software Standard 4), or, for changes that must not move any number, if the
result is shown to be identical to v3's behavior.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import xraydb

from tests.approved_changes import CHANGES
from tests.parity import golden

REPO = Path(__file__).resolve().parents[1]
CM_PER_UNIT = {"in": 2.54, "mils": 2.54e-3, "cm": 1.0, "mm": 0.1, "μm": 1e-4}


def test_F1_rows_use_their_own_material():
    """Each new value = Beer-Lambert with the row's own material at E0 + 50 eV, via xraydb."""
    row_of = {"textboxP06": ("combo4", "textbox_P04", "combo_U4"),   # solvent row
              "textboxP07": ("combo5", "textbox_P05", "combo_U5")}   # metal row
    for v in CHANGES["F1"]["values"]:
        snap = next(s for s in golden(v["case"])["snapshots"] if s["label"] == v["snapshot"])
        mw = snap["main_window"]
        material, thickness, unit = (mw[w] for w in row_of[v["field"]])
        t_cm = float(thickness["text"]) * CM_PER_UNIT[unit["text"]]
        mux = t_cm * xraydb.material_mu(material["text"], float(mw["textbox9"]["text"]) + 50)
        if v["new"].endswith("%"):
            assert math.isclose(float(v["new"][:-1]), 100 * math.exp(-mux), abs_tol=0.05), v
        else:
            assert math.isclose(float(v["new"]), mux, abs_tol=0.05), v


def test_F2_matches_xraydb_ionchamber_fluxes():
    """Each new value = 100 x (1 - transmitted/incident) from xraydb.ionchamber_fluxes, an
    independent implementation of gas-mix attenuation. It assumes 1 atm; mu scales linearly with
    density, so pressure P enters as an effective length L x P/760."""
    for v in CHANGES["F2"]["values"]:
        mw = next(s for s in golden(v["case"])["snapshots"]
                  if s["label"] == v["snapshot"])["main_window"]
        x1 = -mw["slider"]["value"] / 100
        gas1, gas2 = mw["combo6"]["text"], mw["combo7"]["text"]
        gas = {gas1: x1} if gas1 == gas2 else {gas1: x1, gas2: 1 - x1}
        gas = {k: f for k, f in gas.items() if f > 0}
        length = float(mw["textboxP12"]["text"] if mw["combo_C1"]["text"] == "Other"
                       else mw["combo_C1"]["text"])
        flux = xraydb.ionchamber_fluxes(gas=gas, length=length * mw["slider2"]["value"] / 760,
                                        energy=float(mw["textbox9"]["text"]))
        absorbed = 100 * (1 - flux.transmitted / flux.incident)
        assert math.isclose(float(v["new"]), absorbed, abs_tol=0.005), (v, absorbed)


V3_REGISTRATION = """
import xraydb
xraydb.add_material('PEEK', 'C19H14O3', 1.32, categories=['polymer'])
xraydb.add_material('Glossy Carbon', 'C', 1.5, categories=['polymer'])
xraydb.add_material('Kanthal A-1', 'Cr1.83AlFe6.139', 7.1, categories=['polymer'])
xraydb.add_material('Nichrome', 'CrNi3.544', 8.4, categories=['polymer'])
xraydb.add_material('Carbon Fiber', 'C3HN', 1.184, categories=['polymer'])
"""

DUMP = """
import json, xraydb
table = [[k, m.formula, m.density, m.name, m.categories]
         for k, m in xraydb.get_materials().items()]
mu = {k: [xraydb.material_mu(k, e) for e in (5000.0, 8000.0, 20000.0)]
      for k in ('peek', 'glossy carbon', 'kanthal a-1', 'nichrome', 'carbon fiber')}
print(json.dumps({'table': table, 'mu': mu}))
"""


def run_isolated(registration, user_file):
    """Run in a fresh process with xraydb's user materials file redirected to user_file."""
    redirect = ("import xraydb.materials as m\n"
                f"m.get_user_materialsfile = lambda create_folder=False: {str(user_file)!r}\n")
    proc = subprocess.run([sys.executable, "-c", redirect + registration + DUMP], cwd=REPO,
                          capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def test_F11_in_memory_materials_identical_to_v3(tmp_path):
    for existing in (False, True):  # fresh machine, and a machine v3 has already run on
        v3_file, new_file = tmp_path / f"v3_{existing}.dat", tmp_path / f"new_{existing}.dat"
        if existing:
            seed = "".join(f" {n} | {d} | polymer | {f}\n" for n, f, d in [
                ("PEEK", "C19H14O3", 1.32), ("Glossy Carbon", "C", 1.5),
                ("Kanthal A-1", "Cr1.83AlFe6.139", 7.1), ("Nichrome", "CrNi3.544", 8.4),
                ("Carbon Fiber", "C3HN", 1.184)])
            v3_file.write_text(seed)
            new_file.write_text(seed)
        before = new_file.read_bytes() if existing else None
        v3 = run_isolated(V3_REGISTRATION, v3_file)
        new = run_isolated("import catmass.physics\n", new_file)
        assert new == v3, f"materials differ from v3 (existing user file: {existing})"
        assert v3_file.exists(), "redirect check: v3's add_material should have written"
        if existing:
            assert new_file.read_bytes() == before, "catmass.physics modified the user file"
        else:
            assert not new_file.exists(), "catmass.physics created a user materials file"


# --- F7: invalid input never crashes; each gives a specific message -----------------------
from catmass import physics  # noqa: E402

PT = ("O568.390524Al378.927016Pt1.000000", "Pt", "L3", "0.38", "2.6")
BAD_CALCULATIONS = [
    # (arguments to calculate_result, expected message fragment)
    (("al2o3", "Al", "K", "0.38", "2.6"), "Sample 'al2o3' is not a valid chemical formula"),
    (("Al2O3)", "Al", "K", "0.38", "2.6"), "Brackets not matching"),
    (("Xx2O3", "Al", "K", "0.38", "2.6"), "unknown symbol Xx"),
    (("Al2O3", "Xx", "K", "0.38", "2.6"), "'Xx' is not an element symbol"),
    (("Fe2O3", "fe", "K", "0.38", "2.6"), "'fe' is not an element symbol"),
    (("H2O", "H", "L3", "0.38", "2.6"), "H has no L3 edge"),
    (("Al2O3", "O", "L3", "0.38", "2.6"), "below the 2000 eV minimum"),
    # v3 computed these; below the 2000 eV minimum (researcher decision 2026-11-08)
    (("SiO2", "Si", "K", "0.38", "2.6"), "Si K edge (1839 eV) is below the 2000 eV minimum"),
    (("Al2O3", "Al", "K", "0.38", "2.6"), "Al K edge (1560 eV) is below the 2000 eV minimum"),
    (("Al2O3", "N/A", "1999", "0.38", "2.6"), "must be at least 2000 eV"),
    (("Al2O3", "N/A", "abc", "0.38", "2.6"), "'abc' is not a number"),
    (("Al2O3", "N/A", "", "0.38", "2.6"), "Energy to calculate sample mass not Defined"),
    (("Al2O3", "N/A", "100", "0.38", "2.6"), "must be at least 2000 eV"),
    (PT[:3] + ("abc", "2.6"), "Sample area 'abc' is not a number"),
    (PT[:3] + ("0", "2.6"), "Sample area must be greater than 0"),
    (PT[:3] + ("-0.38", "2.6"), "Sample area must be greater than 0"),
    (PT[:3] + ("0.38", "nan"), "Absorption length 'nan' is not a finite number"),
    (PT[:3] + ("0.38", "0"), "Absorption length must be greater than 0"),
    (PT + ("0", "0"), "Sample ratio must be greater than 0"),
    (PT + ("1", "-9"), "Diluent ratio must be at least 0"),
    (PT + ("1", "x"), "Diluent ratio 'x' is not a number"),
]


def test_F7_minimum_energy_boundary():
    """2000 eV is accepted; S K (2472 eV), the lowest edge in use, still calculates."""
    assert physics.calculation_input_error("Al2O3", "N/A", "2000", "0.38", "2.6") is None
    r = physics.calculate_result("ZnS", "S", "K", "0.38", "2.6")
    assert r["Result"] == "None" and r["Enot"] > 2000 and r["ms"] > 0


def test_F7_calculation_errors_instead_of_crashes():
    for args, fragment in BAD_CALCULATIONS:
        r = physics.calculate_result(*args)  # must not raise
        assert r["Result"].startswith("ERROR - ") and fragment in r["Result"], (args, r["Result"])
        assert physics.result_display(r) is None
        assert physics.diagnostic_text(r, plot=True) == r["Result"]  # v3 showed "Background..."


def test_F7_builder_and_dilution_errors_instead_of_crashes():
    cases = [
        (physics.dilute_sample, ("Fe2O3", "bn", "1", "9"), "Diluent 'bn' is not a valid"),
        (physics.dilute_sample, ("Fe2O3", "BN", "x", "9"), "Sample ratio 'x' is not a number"),
        (physics.build_metal_sample, ("pt", "1", "", "", "SiO2"), "Metal site 1 'pt'"),
        (physics.build_metal_sample, ("Pt", "1", "", "", "sio2"), "Support 'sio2'"),
        (physics.build_metal_sample, ("Pt", "abc", "", "", "SiO2"), "'abc' is not a number"),
        (physics.build_metal_sample, ("Pt", "100", "", "", "SiO2"), "must be less than 100"),
        (physics.build_metal_sample, ("Pt", "60", "Sn", "50", "SiO2"), "add up to 110 wt%"),
        (physics.build_metal_sample, ("Pt", "50", "Sn", "50", "SiO2"), "add up to 100 wt%"),
        (physics.build_complex_sample, ("SiO2", "Si(CH3)4Pt", "", "1", "S"),
         "Metal Center not in Complex"),
        (physics.build_complex_sample, ("SiO2", "Rh(CO)2(C5H7O2)", "", "50", "Rh"),
         "needs 125.4 wt% of this complex"),  # C7H7O4Rh: Rh 39.88 wt%
        (physics.build_complex_sample, ("SiO2", "Rh(CO)2(C5H7O2)", "", "1", "rh"),
         "Metal center 'rh' is not an element symbol"),
    ]
    for fn, args, fragment in cases:
        result = fn(*args)  # must not raise
        text = result[0] if isinstance(result, tuple) else result
        assert text.startswith("ERROR - ") and fragment in text, (fn.__name__, args, text)


def test_F7_panels_and_plot_errors_instead_of_crashes():
    shown = physics.transmission_panel("7112", "air", "abc", 2, "kapton", "-5", 4, "water", "",
                                       2, "aluminum", "1", 1)
    assert "'abc' is not a number" in shown["gas"] and "at least 0" in shown["material"]
    assert "solvent" not in shown and shown["metal"].endswith("%")
    shown = physics.transmission_panel("", "air", "10", 2, "kapton", "", 4, "water", "", 2,
                                       "aluminum", "", 1)
    assert shown == {"gas": "ERROR - E0 not defined; calculate the sample mass first"}
    assert "is not a number" in physics.ion_chamber_absorbed("7112", "nitrogen", "helium", -50,
                                                             760, "Other", "abc")
    for lower, upper, fragment in (("", "1000", "Lower plot limit not defined"),
                                   ("-200", "x", "'x' is not a number"),
                                   ("500", "100", "must be below the upper"),
                                   ("-20000", "1000", "below 0 eV")):
        pd = physics.plot_data(*PT, 81.97, 11563.8, lower, upper)
        assert pd["error"] and fragment in pd["error"], (lower, upper, pd["error"])
    pd = physics.plot_data(PT[0], "N/A", "11564.5", "0.38", "2.6", 81.98, 11564.5, "-200", "1000")
    assert pd["error"] is None and pd["fluorescence"]["xlim"] == [10764.5, 12364.5]
