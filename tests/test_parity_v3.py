"""Parity of catmass.physics with the v3 golden files (parity-rebuild Stage 4).

Run in the reference environment (Tier A: same backends as the golden files):

    python -m pytest tests/test_parity_v3.py

Per golden case:
1. replay       every physics call v3's GUI made, re-run through catmass.physics: same result
2. calculation  each "Calculate Sample Mass" click: calculate_result, result_display and
                diagnostic_text vs. the results panel right after that click
3. plot         plot_data vs. the figure v3 drew
4. geometry     holder_area / projected_area / projected_al vs. the area and AL boxes
5. beam path    transmission_panel and ion_chamber_absorbed vs. the panel boxes
6. builder      Sample Builder tabs vs. the builder diagnostic or the sample box
Plus: the verbatim-port check, the glitch data, and "no GUI imports".

Not checked here (UI behavior; Stage 5 end-to-end): NOT_CORE below.
"""
import ast
import hashlib
import inspect
import subprocess
import sys
from pathlib import Path

import pytest
import xraydb

from catmass import physics
from tests.parity import assert_same, case_ids, golden

REPO = Path(__file__).resolve().parents[1]
REFERENCE = REPO / "legacy" / "catMass_2023v3_singlefile_EXE-REFERENCE.py"
CASES = case_ids()

# UI behaviors visible in the golden files that the physics core does not (and should not)
# reproduce. Each is decided or pending in the vault plan; Stage 5 checks the new UI's handling.
NOT_CORE = {
    "H-area-cleared": "area box cleared, v3 computes with the previous area (finding 5, UI)",
    "H-AL-cleared": "AL box cleared, v3 computes with the previous AL (finding 5, UI); the "
                    "calculation itself is checked with the AL v3 actually used",
    "A-other-at-edge": "AL box shows 1.5, v3 computes with the hidden 2.6 (finding 4, UI)",
    "E-angle45-after-calc": "after toggling angle mode v3 rescales the old step without "
                            "recalculating (UI state); the calculation is checked before it",
    "H-dilution-no-ratio": "dilution error text replaced by a blank (finding 6, UI)",
    "H-dilution-diluent-ratio-only": "dilution error text replaced by a blank (finding 6, UI)",
}

VERBATIM = ["XASMassCalc", "XASPLOTTER", "XASStoichCalc", "metalCalculateSample",
            "ComplexCalculateSample", "kspacecalc", "BeamTrans", "XASEZero", "XASEZeroList",
            "unitconvert", "ionchamberdensity"]
LIBRARY_CALLS = {"material_mu": xraydb.material_mu, "xray_lines": xraydb.xray_lines}
CALC_FNS = {"XASMassCalc", "XASEZero", "XASEZeroList", "xray_lines"}


def fmt2(v):
    return '{0:0.2f}'.format(v)


def raised(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return None


# ---------------------------------------------------------------------------------------------
# Structure of the port
# ---------------------------------------------------------------------------------------------
def test_verbatim_functions_match_reference():
    """Every ported v3 function is character-for-character the reference function."""
    src = REFERENCE.read_text(encoding="utf-8")
    lines = src.splitlines()
    nodes = {n.name: n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}
    for name in VERBATIM:
        n = nodes[name]
        ref = "\n".join(lines[n.lineno - 1:n.end_lineno]).rstrip()
        assert inspect.getsource(getattr(physics, name)).rstrip() == ref, name


def test_no_gui_imports():
    code = ("import sys; import catmass.physics; "
            "bad = [m for m in sys.modules if m.split('.')[0] in ('PyQt5', 'matplotlib')]; "
            "print(bad); sys.exit(1 if bad else 0)")
    proc = subprocess.run([sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_glitch_library_matches_reference():
    expected = golden(CASES[0])["reference"]["glitch_files_sha256"]
    for fname, _, _ in physics.GLITCH_LIBRARY:
        data = (Path(physics.GLITCH_DIR) / fname).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected[fname], fname


# ---------------------------------------------------------------------------------------------
# 1. Replay of every recorded physics call
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("case_id", CASES)
def test_replay(case_id):
    calls = golden(case_id)["physics_calls"]
    for n, call in enumerate(calls):
        fn = LIBRARY_CALLS.get(call["fn"]) or getattr(physics, call["fn"])
        where = f"call {n} {call['fn']}{tuple(call['args'])}"
        if "raised" in call:
            assert raised(fn, *call["args"], **call["kwargs"]) == call["raised"], where
        else:
            assert_same(fn(*call["args"], **call["kwargs"]), call["result"], where)


# ---------------------------------------------------------------------------------------------
# 2 + 3. Calculations and plots
# ---------------------------------------------------------------------------------------------
def calc_groups(g):
    """Split the recorded calls into one group per "Calculate Sample Mass" click."""
    calls = g["physics_calls"]
    starts = [i for i, c in enumerate(calls) if c["fn"] == "XASStoichCalc"]
    groups = []
    for k, s in enumerate(starts):
        nxt = starts[k + 1] if k + 1 < len(starts) else len(calls)
        main = calls[s + 1]
        assert main["fn"] == "XASMassCalc" and len(main["args"]) == 5
        retries = []
        for c in calls[s + 2:nxt]:
            if c["fn"] == "XASMassCalc" and len(c["args"]) == 7:
                retries.append(c)
            else:
                break
        end = max(i for i in range(s, nxt) if calls[i]["fn"] in CALC_FNS | {"XASStoichCalc"}) + 1
        snap = next((sn for sn in g["snapshots"] if end <= sn["physics_calls_so_far"]
                     and (k + 1 == len(starts) or sn["physics_calls_so_far"] <= starts[k + 1])),
                    None)
        groups.append({"main": main, "retries": retries, "snapshot": snap})
    return groups


CALC_CASES = [c for c in CASES if calc_groups(golden(c))]


def check_figure(fig, pd):
    ax_e, ax_k, ax_f, ax_g = fig["axes"]
    e, k, f, gl = pd["energy"], pd["k"], pd["fluorescence"], pd["glitches"]

    assert_same(e["x"], ax_e["lines"][0]["x"], "energy.x")
    assert_same(e["y"], ax_e["lines"][0]["y"], "energy.y")
    assert_same(e["edges_E"], ax_e["lines"][1]["x"], "energy.edges_E")
    assert_same(e["edges_absorption"], ax_e["lines"][1]["y"], "energy.edges_absorption")
    notes = [t for t in ax_e["texts"] if t["kind"] == "annotation"]
    assert_same(e["edges_step_label"], [t["text"] for t in notes], "energy.edges_step_label")
    assert_same([[x, y] for x, y in zip(e["edges_E"], e["edges_absorption"])],
                [t["xy"] for t in notes], "energy.xy")
    assert_same(e["xlim"], ax_e["xlim"], "energy.xlim")
    assert_same(e["ylim"], ax_e["ylim"], "energy.ylim")

    assert_same(k["x"], ax_k["lines"][0]["x"], "k.x")
    assert_same(k["y"], ax_k["lines"][0]["y"], "k.y")
    assert_same(k["edges_k"], ax_k["lines"][1]["x"], "k.edges_k")
    assert_same(k["edges_y"], ax_k["lines"][1]["y"], "k.edges_y")
    notes = [t for t in ax_k["texts"] if t["kind"] == "annotation"]
    assert_same(k["edge_labels"] + k["element_labels"], [t["text"] for t in notes], "k.labels")
    assert_same([[x, y] for x, y in zip(k["edges_k"], k["edges_y"])] * 2,
                [t["xy"] for t in notes], "k.label_xy")
    assert_same(k["xlim"], ax_k["xlim"], "k.xlim")

    segments = next(c for c in ax_f["collections"] if c["type"] == "LineCollection")["paths"]
    assert_same([[[x, 0], [x, y]] for x, y in zip(f["x"], f["y"])], segments, "fluor.lines")
    notes = [t for t in ax_f["texts"] if t["kind"] == "annotation"]
    assert_same(f["names"], [t["text"] for t in notes], "fluor.names")
    assert_same([[x, y] for x, y in zip(f["x"], f["y"])], [t["xy"] for t in notes], "fluor.xy")
    assert_same(f["xlim"], ax_f["xlim"], "fluor.xlim")
    assert_same(f["ylim"], ax_f["ylim"], "fluor.ylim")
    band = [c for c in ax_f["collections"] if c["type"] == "PolyCollection"]
    if f["band"] is None:
        assert not band, "fluorescence band drawn by v3 but not by the rebuild"
    else:
        verts = band[0]["paths"][0]
        xs, ys = [v[0] for v in verts], [v[1] for v in verts]
        assert_same(f["band"], [min(xs), max(xs), max(ys)], "fluor.band")

    if gl is None:
        assert len(ax_k["lines"]) == 2 and not ax_g["lines"], "glitch overlay mismatch"
    else:
        for ax, xs, ys in ((ax_g, "E_x", "E_y"), (ax_k, "k_x", "k_y")):
            drawn = ax["lines"] if ax is ax_g else ax["lines"][2:]
            assert_same([o["label"] for o in gl], [ln["label"] for ln in drawn],
                        "glitch.labels")
            assert_same([o["visible"] for o in gl], [ln["visible"] for ln in drawn],
                        "glitch.visible")
            for ln, o in zip(drawn, gl):
                assert_same(o[xs], ln["x"], f"glitch.{o['file']}.{xs}")
                assert_same(o[ys], ln["y"], f"glitch.{o['file']}.{ys}")


@pytest.mark.parametrize("case_id", CALC_CASES)
def test_calculation_and_plot(case_id):
    g = golden(case_id)
    plots_so_far = 0
    for n, grp in enumerate(calc_groups(g)):
        main, snap = grp["main"], grp["snapshot"]
        Sample, Element, Edge, Area, AL = main["args"]
        final = g["snapshots"][-1]["main_window"]
        mw = snap["main_window"] if snap else final
        ratios = (mw["textbox_dil03"]["text"], mw["textbox_dil04"]["text"])
        where = f"click {n}"

        if "raised" in main:
            assert raised(physics.calculate_result, *main["args"], *ratios) == main["raised"]
            continue
        r = physics.calculate_result(*main["args"], *ratios)
        for key, i in (("Result", 0), ("Enot", 1), ("ms", 2), ("muave", 4)):
            assert_same(r[key], main["result"][i], f"{where} {key}")
        last = grp["retries"][-1] if grp["retries"] else main
        assert_same(r["stp"], last["result"][3], f"{where} stp")
        assert r["whilecount"] == 1 + len(grp["retries"]), f"{where} retry count"

        if snap is None:
            continue  # display overwritten before any snapshot; values checked above
        angle, plot = mw["b2"]["checked"], mw["b1"]["checked"]
        shown = physics.result_display(r, angle)
        boxes = {"mass": "textbox5", "step": "textbox6", "sample_mass": "textbox7",
                 "diluent_mass": "textbox8", "E0": "textbox9"}
        for key, box in boxes.items():
            assert_same("" if shown is None else shown[key], mw[box]["text"], f"{where} {box}")
        if shown is not None:
            red = mw["textbox6"]["style"].replace(" ", "").endswith("rgb(255,0,0)")
            assert red == shown["step_red"], f"{where} red step flag"
        assert_same(physics.diagnostic_text(r, plot, angle), mw["textbox_Xray_05"]["text"],
                    f"{where} diagnostic")

        if plot and shown is not None:
            AL_plot = AL if not angle else str(float(AL))
            args = (Sample, Element, Edge, Area, AL_plot, r["ms"], r["Enot"],
                    mw["textbox11"]["text"], mw["textbox12"]["text"])
            v3_crash = [e for e in g["exceptions"]
                        if any("calculateResult" in fr for fr in e["frames"])]
            if v3_crash:
                assert raised(physics.plot_data, *args) == \
                    f"{v3_crash[0]['type']}: {v3_crash[0]['message']}", f"{where} plot crash"
            else:
                check_figure(snap["figures"][plots_so_far], physics.plot_data(*args))
            plots_so_far += 1


# ---------------------------------------------------------------------------------------------
# 4. Geometry
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("case_id", CASES)
def test_geometry(case_id):
    if case_id == "H-area-cleared":
        pytest.skip(NOT_CORE[case_id])
    for snap in golden(case_id)["snapshots"]:
        mw = snap["main_window"]
        holder = ("capillary" if mw["radioButton1"]["checked"] else
                  "pellet" if mw["radioButton2"]["checked"] else "other")
        area = physics.holder_area(holder, mw["combo_cap"]["text"], mw["textbox13"]["text"],
                                   mw["combo_pel"]["text"], mw["textbox16"]["text"])
        where = f"{snap['label']} {holder}"
        if holder != "other":
            assert_same(fmt2(area), mw["textbox16"]["text"], f"{where} area at 90 deg")
        if not mw["b2"]["checked"]:
            assert_same(fmt2(area), mw["textbox4"]["text"], f"{where} area used")
        else:
            angle = mw["slider_deg"]["value"]
            assert_same(fmt2(physics.projected_area(area, angle)), mw["textbox4"]["text"],
                        f"{where} projected area")
            assert_same(fmt2(physics.projected_al(mw["textbox15"]["text"], angle)),
                        mw["textbox3"]["text"], f"{where} projected AL")


def test_geometry_known_values():
    """Known-answer checks (Software Standard 4). v3 only ever shows areas to 2 decimals, so the
    golden files cannot catch a small error in the unrounded area, which Release 1 will use."""
    import math
    for d_mm in (5, 7, 10, 13, 6.35):
        expected = math.pi * (d_mm / 10) ** 2 / 4  # disc area in cm^2
        assert math.isclose(physics.holder_area("pellet", pellet_mm=str(d_mm)), expected,
                            rel_tol=1e-14), d_mm
    for id_mm, bed_cm in ((1, 1), (3, 2.5), (1, 0.5)):
        expected = (id_mm / 10) * bed_cm  # projected area of the bed, cm^2
        assert math.isclose(physics.holder_area("capillary", str(id_mm), str(bed_cm)),
                            expected, rel_tol=1e-14), (id_mm, bed_cm)
    assert physics.holder_area("other", other_cm2="0.125") == 0.125
    assert math.isclose(physics.projected_area(1.0, 30), 0.5, rel_tol=1e-14)
    assert math.isclose(physics.projected_area(1.0, 45), math.sqrt(0.5), rel_tol=1e-14)
    assert physics.projected_area(1.0, 90) == 1.0 and physics.projected_al("2.6", 90) == 2.6
    assert math.isclose(physics.projected_al("2.6", 30), 5.2, rel_tol=1e-14)
    # v3 rounds the slider angle to whole degrees
    assert math.isclose(physics.projected_area(1.0, 44.6), math.sqrt(0.5), rel_tol=1e-14)


# ---------------------------------------------------------------------------------------------
# 5. Beam-path panel and ion chambers
# ---------------------------------------------------------------------------------------------
IC_CONTROLS = {"combo6", "combo7", "combo_C1", "slider", "slider2", "textboxP12"}


def panel_modes(case):
    """Which panel button ('transmitted'/'absorbed') was clicked last before each snapshot."""
    mode, modes = None, []
    for step in case["steps"]:
        if step[:2] == ["click", "button_P00"]:
            mode = "transmitted"
        elif step[:2] == ["click", "button_P02"]:
            mode = "absorbed"
        elif step[0] == "snapshot":
            modes.append(mode)
    return modes + [mode]


PANEL_CASES = [c for c in CASES if "textboxP11" in golden(c)["snapshots"][-1]["main_window"]]


def record_calls(monkeypatch, calls):
    """Record the physics calls the core makes, in the golden files' format.

    The panel shows 0.1% / 0.01% precision, which hides small errors (e.g. evaluating at E0 + 40
    instead of + 50 eV). v3's raw calls are in the golden files, so the core must make the same
    calls with the same arguments and results.
    """
    from tests.parity import jsonable
    targets = [(physics.xraydb, "material_mu"), (physics, "unitconvert"),
               (physics, "ionchamberdensity")]
    for owner, name in targets:
        original = getattr(owner, name)

        def spy(*args, _orig=original, _name=name, **kwargs):
            result = _orig(*args, **kwargs)
            calls.append({"fn": _name, "args": jsonable(args), "kwargs": jsonable(kwargs),
                          "result": jsonable(result)})
            return result
        monkeypatch.setattr(owner, name, spy)


def assert_last_calls(made, g, snap, where):
    """The core's calls equal the last calls v3 made before this snapshot."""
    upto = snap["physics_calls_so_far"]
    v3_calls = g["physics_calls"][upto - len(made):upto]
    assert_same(made, v3_calls, f"{where} physics calls")


@pytest.mark.parametrize("case_id", PANEL_CASES)
def test_beam_path_and_ion_chambers(case_id, monkeypatch):
    g = golden(case_id)
    calls = []
    record_calls(monkeypatch, calls)
    touched_ic = any(s[0] in ("select", "slider", "type") and s[1] in IC_CONTROLS
                     for s in g["case"]["steps"])
    for snap, mode in zip(g["snapshots"], panel_modes(g["case"])):
        mw = snap["main_window"]
        t = lambda name: mw[name]["text"]  # noqa: E731
        u = lambda name: mw[name]["index"]  # noqa: E731
        if mode:
            calls.clear()
            shown = physics.transmission_panel(
                t("textbox9"), t("combo3"), t("textbox_P02"), u("combo_U3"),
                t("combo2"), t("textbox_P03"), u("combo_U2"), t("combo4"), t("textbox_P04"),
                u("combo_U4"), t("combo5"), t("textbox_P05"), u("combo_U5"),
                absorbed=(mode == "absorbed"))
            for row, box in (("gas", "textboxP04"), ("material", "textboxP05"),
                             ("solvent", "textboxP06"), ("metal", "textboxP07")):
                assert_same(shown.get(row, ""), t(box), f"{snap['label']} {mode} {row}")
            assert_last_calls(calls, g, snap, f"{snap['label']} {mode}")
        if touched_ic:
            calls.clear()
            ic = physics.ion_chamber_absorbed(t("textbox9"), t("combo6"), t("combo7"),
                                              mw["slider"]["value"], mw["slider2"]["value"],
                                              t("combo_C1"), t("textboxP12"))
            assert_same("" if ic is None else ic, t("textboxP11"), f"{snap['label']} IC")
            assert_last_calls(calls, g, snap, f"{snap['label']} IC")
        else:
            assert t("textboxP11") == "", "v3 computed the ion chamber without a control change"


# ---------------------------------------------------------------------------------------------
# 6. Sample Builder
# ---------------------------------------------------------------------------------------------
BUILDER_CASES = [c for c in CASES
                 if any(s[0] == "dclick" for s in golden(c)["case"]["steps"])]


@pytest.mark.parametrize("case_id", BUILDER_CASES)
def test_sample_builder(case_id):
    g = golden(case_id)
    final = g["snapshots"][-1]
    sb, mw = final["sample_builder"], final["main_window"]
    t = lambda name: sb[name]["text"]  # noqa: E731
    button = [s[1] for s in g["case"]["steps"] if s[0] == "dclick"][-1]
    if button == "button_tab1_01":
        res = physics.metalCalculateSample(t("textbox_tab102"), t("textbox_tab103"),
                                           t("textbox_tab104"), t("textbox_tab105"),
                                           t("textbox_tab101"))
        message = "ERROR" in res
        diag = "textbox_tab106"
    else:
        res = physics.build_complex_sample(t("textbox_tab2_01"), t("textbox_tab2_02"),
                                           t("textbox_tab2_03"), t("textbox_tab2_04"),
                                           t("textbox_tab2_05"))
        message = "ERROR" in res or res.startswith("COMPLEX LODAING")
        diag = "textbox_tab2_06"
    if message:
        assert_same(res, t(diag), "builder diagnostic")
        assert sb["open"], "v3 keeps the builder open on an error"
    else:
        assert_same(res, mw["textbox_dil01"]["text"], "sample formula")
        assert not sb["open"], "v3 closes the builder on success"
