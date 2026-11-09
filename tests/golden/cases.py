"""Golden-file case set for the catMass v3 reference (parity-rebuild Stage 3).

Each case is a fresh launch of the unchanged v3 GUI followed by a list of user actions. Steps name
v3's own widget attributes, so the same list later drives the end-to-end check of the new UI.
Case set agreed with the researcher 2026-11-08 (vault: projects/catMass/plan.md, "Case set").

Step vocabulary (executed by generate_golden.py):
    ["type", widget, text]     clear the line edit, then type text key by key (fires textEdited)
    ["click", widget]          click a button, checkbox, or radio button
    ["select", widget, text]   pick a combo-box entry by its text
    ["slider", widget, value]  move a slider to value
    ["dtype", widget, text]    as "type", in the open Sample Builder window
    ["dclick", widget]         as "click", in the open Sample Builder window
    ["dtab", index]            switch Sample Builder tab (0 = metals on support, 1 = complexes)
    ["snapshot", label]        record every output at this point (a final snapshot is automatic)

Assumption (stated per HC16; confirmed 2026-11-08 by the agreed case set): unless a case says
otherwise, v3 launch defaults hold: 7 mm pellet, AL 2.6, no plot, angle mode off, plot limits
-200/1000 eV.
"""

CALC = ["click", "button_Input02"]  # "Calculate Sample Mass" (dilution formula, then result)
PLOT = ["click", "b1"]              # "Show Plot" checkbox: the plot path also computes all edges


def metal_sample(support, site1, load1, site2="", load2=""):
    """Sample Builder, tab 1 ("x wt% Metals on Support"), then Update Sample."""
    steps = [["click", "button_dil00"],
             ["dtype", "textbox_tab101", support],
             ["dtype", "textbox_tab102", site1],
             ["dtype", "textbox_tab103", load1]]
    if site2:
        steps.append(["dtype", "textbox_tab104", site2])
    if load2:
        steps.append(["dtype", "textbox_tab105", load2])
    return steps + [["dclick", "button_tab1_01"]]


def complex_sample(support, complex_, complex_load="", metal_load="", center=""):
    """Sample Builder, tab 2 ("Supported Metal Complexes"), then Update Sample."""
    steps = [["click", "button_dil00"], ["dtab", 1],
             ["dtype", "textbox_tab2_01", support],
             ["dtype", "textbox_tab2_02", complex_]]
    if complex_load:
        steps.append(["dtype", "textbox_tab2_03", complex_load])
    if metal_load:
        steps.append(["dtype", "textbox_tab2_04", metal_load])
    if center:
        steps.append(["dtype", "textbox_tab2_05", center])
    return steps + [["dclick", "button_tab2_01"]]


def typed_sample(formula, diluent="", sample_ratio="", diluent_ratio=""):
    """Sample formula (and optional diluent) typed straight into the left panel."""
    steps = [["type", "textbox_dil01", formula]]
    if diluent:
        steps.append(["type", "textbox_dil02", diluent])
    if sample_ratio:
        steps.append(["type", "textbox_dil03", sample_ratio])
    if diluent_ratio:
        steps.append(["type", "textbox_dil04", diluent_ratio])
    return steps


def scan(element, edge):
    """Element and edge to scan. edge is 'K'/'L1'/'L2'/'L3', or an energy in eV ("Other")."""
    if edge in ("K", "L1", "L2", "L3"):
        return [["type", "textbox2", element], ["select", "combo", edge]]
    # "Other" makes the element box read-only ("N/A") and shows the energy box
    return [["select", "combo", "Other"], ["type", "textbox14", edge]]


def ic_panel():
    """Open the beam-path / ion-chamber panel ("X-ray transmission through media")."""
    return [["click", "b3"]]


CASES = []


def case(case_id, group, description, steps):
    CASES.append({"id": case_id, "group": group, "description": description, "steps": steps})


# --- Core matrix: {Fe K, Pt L3, Mo K, Rh K} x {Al2O3, SiO2, CeO2} x {0.1, 1, 3 wt%} -------------
# Plot on, so every core case also records the all-edges (competing absorption) table and the
# glitch overlay.
for metal, edge in [("Fe", "K"), ("Pt", "L3"), ("Mo", "K"), ("Rh", "K")]:
    for support in ["Al2O3", "SiO2", "CeO2"]:
        for load in ["0.1", "1", "3"]:
            case(f"core-{metal}{edge}-{support}-{load}wt", "core",
                 f"{load} wt% {metal}/{support}, {metal} {edge}, default pellet, plot on",
                 metal_sample(support, metal, load) + scan(metal, edge) + [PLOT, CALC])

# --- A. Edges ---------------------------------------------------------------------------------
for e in ["L3", "L2", "L1"]:
    case(f"A-Pt-foil-{e}", "A", f"Pt foil (single-element path), Pt {e}",
         typed_sample("Pt") + scan("Pt", e) + [CALC])
case("A-Pt-foil-L3-plot", "A", "Pt foil, Pt L3, plot on (single-element plot path)",
     typed_sample("Pt") + scan("Pt", "L3") + [PLOT, CALC])
case("A-Fe-foil-K", "A", "Fe foil (single-element path), Fe K",
     typed_sample("Fe") + scan("Fe", "K") + [CALC])
case("A-other-at-edge", "A",
     "1 wt% Pt/Al2O3, 'Other' E0 = 11564 eV (Pt L3). v3 shows AL 1.5 after choosing Other",
     metal_sample("Al2O3", "Pt", "1") + scan(None, "11564") + [CALC])
case("A-other-at-edge-AL-retyped", "A",
     "As A-other-at-edge, but the user retypes AL 1.5 (fires setAL)",
     metal_sample("Al2O3", "Pt", "1") + scan(None, "11564")
     + [["type", "textbox15", "1.5"], CALC])

# --- B. Builders --------------------------------------------------------------------------------
case("B-PtSn-SiO2-PtL3", "B", "2-site builder: 1 wt% Pt + 1 wt% Sn on SiO2, Pt L3, plot on",
     metal_sample("SiO2", "Pt", "1", "Sn", "1") + scan("Pt", "L3") + [PLOT, CALC])
case("B-PtSn-SiO2-SnK", "B", "2-site builder: 1 wt% Pt + 1 wt% Sn on SiO2, Sn K (29.2 keV), plot on",
     metal_sample("SiO2", "Pt", "1", "Sn", "1") + scan("Sn", "K") + [PLOT, CALC])
case("B-PtO2-Al2O3-PtL3", "B", "Builder with a compound site: 2 wt% PtO2 on Al2O3, Pt L3",
     metal_sample("Al2O3", "PtO2", "2") + scan("Pt", "L3") + [CALC])
case("B-complex-loading", "B",
     "Complex builder, complex loading: 2 wt% Rh(CO)2(acac) on SiO2, Rh K",
     complex_sample("SiO2", "Rh(CO)2(C5H7O2)", complex_load="2") + scan("Rh", "K") + [CALC])
case("B-complex-metal-loading", "B",
     "Complex builder, metal loading: Rh(CO)2(acac) on SiO2 at 1 wt% Rh, Rh K",
     complex_sample("SiO2", "Rh(CO)2(C5H7O2)", metal_load="1", center="Rh")
     + scan("Rh", "K") + [CALC])

# --- C. Competing absorption (plot on: all-edges table, edges in the EXAFS range) -------------
case("C-PtAu-SiO2-PtL3", "C", "1 wt% Pt + 1 wt% Au on SiO2, Pt L3 (Au L3 355 eV above)",
     metal_sample("SiO2", "Pt", "1", "Au", "1") + scan("Pt", "L3") + [PLOT, CALC])
case("C-MnFe2O4-BN-MnK", "C", "MnFe2O4 diluted 10:90 in BN, Mn K (Fe K 573 eV above)",
     typed_sample("MnFe2O4", "BN", "10", "90") + scan("Mn", "K") + [PLOT, CALC])

# --- D. Energy range (Ti K 4.97 keV to Sn K 29.2 keV; Sn K is B-PtSn-SiO2-SnK) ---------------
case("D-Pt-TiO2-TiK", "D", "1 wt% Pt/TiO2, Ti K (low end of range), plot on",
     metal_sample("TiO2", "Pt", "1") + scan("Ti", "K") + [PLOT, CALC])

# --- E. Geometry and AL input -------------------------------------------------------------------
PT = metal_sample("Al2O3", "Pt", "1") + scan("Pt", "L3")
CAP = ["click", "radioButton1"]
for dia, bed in [("1", "1"), ("2", "1"), ("3", "1"), ("3", "2.5"), ("1", "0.5")]:
    case(f"E-cap-{dia}mm-bed-{bed}cm", "E", f"1 wt% Pt/Al2O3, capillary {dia} mm, bed {bed} cm",
         PT + [CAP, ["select", "combo_cap", dia], ["type", "textbox13", bed], CALC])
for dia in ["5", "7", "10", "13"]:
    case(f"E-pellet-{dia}mm", "E",
         f"1 wt% Pt/Al2O3, pellet {dia} mm (area box rounds to 0.01 cm2)",
         PT + [["select", "combo_pel", dia], CALC])
case("E-other-area-0.5", "E", "1 wt% Pt/Al2O3, 'Other' area 0.5 cm2",
     PT + [["click", "radioButton3"], ["type", "textbox16", "0.5"], CALC])
case("E-other-area-0.125", "E", "1 wt% Pt/Al2O3, 'Other' area 0.125 cm2 (rounding-sensitive)",
     PT + [["click", "radioButton3"], ["type", "textbox16", "0.125"], CALC])
case("E-AL-1.5", "E", "1 wt% Pt/Al2O3, AL typed 1.5",
     PT + [["type", "textbox15", "1.5"], CALC])
case("E-AL-2.555", "E", "1 wt% Pt/Al2O3, AL typed 2.555 (rounding-sensitive)",
     PT + [["type", "textbox15", "2.555"], CALC])
case("E-angle45-before-calc", "E", "1 wt% Pt/Al2O3, angle mode 45 deg checked before calculating",
     PT + [["click", "b2"], CALC])
case("E-angle45-after-calc", "E",
     "1 wt% Pt/Al2O3, calculate at 90 deg, then check angle mode 45 deg (no recalculation)",
     PT + [CALC, ["snapshot", "before-angle"], ["click", "b2"]])
case("E-angle45-after-calc-recalc", "E",
     "1 wt% Pt/Al2O3, calculate, check angle mode 45 deg, calculate again",
     PT + [CALC, ["click", "b2"], CALC])
case("E-angle30", "E", "1 wt% Pt/Al2O3, angle mode, slider to 30 deg, calculate",
     PT + [["click", "b2"], ["slider", "slider_deg", 30], CALC])
case("E-angle45-plot", "E", "1 wt% Pt/Al2O3, angle mode 45 deg, plot on (AL45 plot path)",
     PT + [["click", "b2"], PLOT, CALC])

# --- F. Dilution (XASStoichCalc); cellulose entered as C (researcher's convention) ------------
for dil in ["BN", "C", "SiO2"]:
    for s, d in [("10", "90"), ("50", "50")]:
        case(f"F-Fe2O3-{dil}-{s}to{d}", "F", f"Fe2O3 diluted {s}:{d} in {dil}, Fe K",
             typed_sample("Fe2O3", dil, s, d) + scan("Fe", "K") + [CALC])

# --- G. Beam-path transmission and ion-chamber panel -------------------------------------------
FE = metal_sample("Al2O3", "Fe", "1") + scan("Fe", "K") + [CALC] + ic_panel()
case("G-materials-defaults", "G",
     "After 1 wt% Fe/Al2O3 Fe K: 10 cm air, 50 um kapton, 0.1 cm water, 1 mil aluminum; "
     "Percent Transmitted, then Beam Absorbed",
     FE + [["type", "textbox_P02", "10"], ["type", "textbox_P03", "50"],
           ["type", "textbox_P04", "0.1"], ["type", "textbox_P05", "1"],
           ["click", "button_P00"], ["snapshot", "transmitted"], ["click", "button_P02"]])
case("G-materials-units", "G",
     "After 1 wt% Fe/Al2O3 Fe K: 4 in helium, 0.5 mm sapphire, 500 um ethanol, "
     "0.001 cm platinum; Percent Transmitted, then Beam Absorbed",
     FE + [["select", "combo3", "helium"], ["select", "combo_U3", "in"],
           ["type", "textbox_P02", "4"],
           ["select", "combo2", "sapphire"], ["select", "combo_U2", "mm"],
           ["type", "textbox_P03", "0.5"],
           ["select", "combo4", "ethanol"], ["select", "combo_U4", "μm"],
           ["type", "textbox_P04", "500"],
           ["select", "combo5", "platinum"], ["select", "combo_U5", "cm"],
           ["type", "textbox_P05", "0.001"],
           ["click", "button_P00"], ["snapshot", "transmitted"], ["click", "button_P02"]])
case("G-IC-10cm-He-N2-50", "G", "Ion chamber 10 cm, 50% He / 50% N2, 760 torr (default mix)",
     FE + [["select", "combo_C1", "10"]])
case("G-IC-15cm-N2-100", "G", "Ion chamber 15 cm, 100% N2, 760 torr",
     FE + [["select", "combo6", "nitrogen"], ["slider", "slider", -100]])
case("G-IC-30cm-Ar20-N2", "G", "Ion chamber 30 cm, 20% Ar / 80% N2, 760 torr",
     FE + [["select", "combo6", "argon"], ["select", "combo7", "nitrogen"],
           ["slider", "slider", -20], ["select", "combo_C1", "30"]])
case("G-IC-45cm-Ar-He-50", "G", "Ion chamber 45 cm, 50% Ar / 50% He, 760 torr",
     FE + [["select", "combo6", "argon"], ["select", "combo7", "helium"],
           ["select", "combo_C1", "45"]])
case("G-IC-60cm-N2-30-He-1500torr", "G", "Ion chamber 60 cm, 30% N2 / 70% He, 1500 torr",
     FE + [["select", "combo6", "nitrogen"], ["select", "combo7", "helium"],
           ["slider", "slider", -30], ["slider", "slider2", 1500], ["select", "combo_C1", "60"]])
case("G-IC-other-20cm", "G", "Ion chamber 'Other' length typed 20 cm, 50% Ar / 50% N2",
     FE + [["select", "combo6", "argon"], ["select", "combo7", "nitrogen"],
           ["select", "combo_C1", "Other"], ["type", "textboxP12", "20"]])

# --- H. Errors, silent fallbacks, and the retry loop --------------------------------------------
case("H-empty", "H", "Calculate with nothing entered", [CALC])
case("H-no-element", "H", "Al2O3 typed, no element", typed_sample("Al2O3") + [CALC])
case("H-AL-cleared", "H", "1 wt% Pt/Al2O3, AL box cleared before calculating",
     PT + [["type", "textbox15", ""], CALC])
case("H-area-cleared", "H", "1 wt% Pt/Al2O3, 'Other' area selected and cleared",
     PT + [["click", "radioButton3"], ["type", "textbox16", ""], CALC])
case("H-element-not-in-sample", "H", "Al2O3, Fe K (element absent from sample)",
     typed_sample("Al2O3") + scan("Fe", "K") + [CALC])
case("H-off-edge", "H", "Al2O3, 'Other' E0 = 8000 eV (no edge there)",
     typed_sample("Al2O3") + scan(None, "8000") + [CALC])
case("H-other-at-edge-plot", "H", "1 wt% Pt/Al2O3, 'Other' E0 = 11564 eV, plot on",
     metal_sample("Al2O3", "Pt", "1") + scan(None, "11564") + [PLOT, CALC])
case("H-other-decimal-plot", "H", "1 wt% Pt/Al2O3, 'Other' E0 = 11564.5 eV, plot on",
     metal_sample("Al2O3", "Pt", "1") + scan(None, "11564.5") + [PLOT, CALC])
case("H-bad-symbol", "H", "Al2O3, element typed 'Xx'",
     typed_sample("Al2O3") + scan("Xx", "K") + [CALC])
case("H-bad-formula", "H", "Sample typed 'al2o3' (lower case), Al K",
     typed_sample("al2o3") + scan("Al", "K") + [CALC])
case("H-FeCeO2-retry-noplot", "H", "0.1 wt% Fe/CeO2, Fe K, plot off (retry-loop note text)",
     metal_sample("CeO2", "Fe", "0.1") + scan("Fe", "K") + [CALC])
case("H-FeCeO2-retry-angle", "H", "0.1 wt% Fe/CeO2, Fe K, angle mode 45 deg (note variant)",
     metal_sample("CeO2", "Fe", "0.1") + scan("Fe", "K") + [["click", "b2"], CALC])
case("H-dilution-no-ratio", "H", "Fe2O3 + BN diluent, no ratios",
     typed_sample("Fe2O3", "BN") + scan("Fe", "K") + [CALC])
case("H-dilution-diluent-ratio-only", "H", "Fe2O3 + BN, only diluent ratio 90",
     typed_sample("Fe2O3", "BN", "", "90") + scan("Fe", "K") + [CALC])
case("H-builder-no-support", "H", "Metal builder without support",
     [["click", "button_dil00"], ["dtype", "textbox_tab102", "Pt"],
      ["dtype", "textbox_tab103", "1"], ["dclick", "button_tab1_01"]])
case("H-builder-no-site1", "H", "Metal builder without metal site 1",
     [["click", "button_dil00"], ["dtype", "textbox_tab101", "Al2O3"],
      ["dtype", "textbox_tab103", "1"], ["dclick", "button_tab1_01"]])
case("H-builder-no-loading1", "H", "Metal builder without site 1 loading",
     [["click", "button_dil00"], ["dtype", "textbox_tab101", "Al2O3"],
      ["dtype", "textbox_tab102", "Pt"], ["dclick", "button_tab1_01"]])
case("H-builder-site2-no-loading", "H", "Metal builder with site 2 but no site 2 loading",
     metal_sample("SiO2", "Pt", "1", "Sn", ""))
case("H-complex-center-not-in-complex", "H", "Complex builder, metal center Pt not in Rh complex",
     complex_sample("SiO2", "Rh(CO)2(C5H7O2)", metal_load="1", center="Pt"))
case("H-complex-both-loadings", "H", "Complex builder with complex and metal loading both set",
     complex_sample("SiO2", "Rh(CO)2(C5H7O2)", complex_load="2", metal_load="1", center="Rh"))
case("H-complex-no-support", "H", "Complex builder without support",
     [["click", "button_dil00"], ["dtab", 1],
      ["dtype", "textbox_tab2_02", "Rh(CO)2(C5H7O2)"], ["dtype", "textbox_tab2_04", "1"],
      ["dtype", "textbox_tab2_05", "Rh"], ["dclick", "button_tab2_01"]])
case("H-complex-no-complex", "H", "Complex builder without complex formula",
     [["click", "button_dil00"], ["dtab", 1], ["dtype", "textbox_tab2_01", "SiO2"],
      ["dtype", "textbox_tab2_04", "1"], ["dtype", "textbox_tab2_05", "Rh"],
      ["dclick", "button_tab2_01"]])
case("H-IC-before-calc", "H", "Ion-chamber panel used before any calculation (no E0)",
     ic_panel() + [["select", "combo_C1", "30"]])

# --- I. Glitch overlay (Si(220) 0/90 deg, Si(111) 0/90 deg) ------------------------------------
# File coverage: Si(220) 90: 5001-18000 eV; Si(220) 0: 6000-13000; Si(111) 0/90: 2400-14500.
# In range for all four: core Fe K cases. Out of range for all four: core Mo K, Rh K; Sn K (B).
# Partial: D-Pt-TiO2-TiK (window starts below Si(220) files). Truncated ends below:
case("I-PtL3-limits-100-1500", "I",
     "1 wt% Pt/Al2O3, Pt L3, plot limits -100/+1500 eV (Si(220) 0 deg file ends at 13000 eV)",
     PT + [PLOT, ["type", "textbox11", "-100"], ["type", "textbox12", "1500"], CALC])
case("I-Pt-ZrO2-ZrK", "I", "1 wt% Pt/ZrO2, Zr K (Si(220) 90 deg file ends at 18000 eV)",
     metal_sample("ZrO2", "Pt", "1") + scan("Zr", "K") + [PLOT, CALC])

CASES_BY_ID = {c["id"]: c for c in CASES}
assert len(CASES_BY_ID) == len(CASES), "duplicate case id"
