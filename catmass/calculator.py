"""catMass calculator: the Release 1 rules between the screen and the physics core.

Everything the UI decides lives here, with no UI code, so it can be tested directly: defaults,
required fields, unit conversions (lengths entered in mm), full-precision areas, which physics
functions run, and the list of every value used in a calculation. The NiceGUI layer (app.py)
only displays inputs and results.

Agreed rules: vault plan, "UI defaults (agreed 2026-11-08, Release 1 UI)". Inputs are kept as
the text the user typed; a blank field means "use the default" where a default exists, and the
physics core validates the text (change F7). Values are computed, not measured.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Optional

import xraydb

from catmass import physics

EDGES = ['K', 'L1', 'L2', 'L3', 'Other']
HOLDERS = {'pellet': 'Pellet', 'capillary': 'Capillary', 'other': 'Other area'}
PELLET_DIAMETERS_MM = ['5', '7', '10', '13']
CAPILLARY_IDS_MM = ['1', '2', '3']
UNITS = ['in', 'mils', 'cm', 'mm', 'μm']  # order = v3 unit-combo index used by physics.unitconvert
IC_LENGTHS_CM = ['10', '15', '30', '45', '60', 'Other']
# Diluent dropdown: formula -> label (researcher 2026-11-14). Any other formula can be typed.
# Cellulose is (C6H10O5)n; entering it as C underestimates the diluent's absorption, since O
# absorbs more per gram than C (Fe2O3 10:90 at Fe K: 29.60 mg as C vs 26.49 mg as C6H10O5).
DILUENTS = {'': 'None (no dilution)', 'C6H10O5': 'Cellulose (C6H10O5)',
            'BN': 'Boron nitride (BN)', 'SiO2': 'Silica (SiO2)'}

DEFAULT_AL = '2.6'
DEFAULT_PELLET_MM = '7'
DEFAULT_CAPILLARY_MM = '3'
DEFAULT_BED_MM = '10'
DEFAULT_OTHER_AREA_CM2 = '1'  # researcher 2026-11-14 (was: pre-fill from the previous holder)
DEFAULT_ANGLE_DEG = '45'
DEFAULT_PLOT_LOWER_EV = '-200'
DEFAULT_PLOT_UPPER_EV = '1000'
DEFAULT_IC_GAS1_PERCENT = '100'
DEFAULT_IC_PRESSURE_TORR = '760'


# --- Inputs, as typed ----------------------------------------------------------------------
@dataclass
class SampleInputs:
    formula: str = ''
    diluent: str = ''          # blank = no dilution
    sample_ratio: str = ''     # both ratios required when a diluent is given
    diluent_ratio: str = ''


@dataclass
class ScanInputs:
    element: str = ''
    edge: str = 'K'
    other_energy_eV: str = ''  # required when edge is "Other"


@dataclass
class HolderInputs:
    holder: str = 'pellet'     # key of HOLDERS
    pellet_mm: str = ''
    capillary_mm: str = ''
    bed_mm: str = ''
    other_area_cm2: str = ''   # blank = 1 cm2 default
    angle_on: bool = False
    angle_deg: str = ''


@dataclass
class CalculatorInputs:
    sample: SampleInputs = field(default_factory=SampleInputs)
    scan: ScanInputs = field(default_factory=ScanInputs)
    holder: HolderInputs = field(default_factory=HolderInputs)
    absorption_length: str = ''
    plot_lower_eV: str = ''
    plot_upper_eV: str = ''


@dataclass
class MetalSitesBuilder:
    support: str = ''
    site1: str = ''
    site1_wt_percent: str = ''
    site2: str = ''
    site2_wt_percent: str = ''


@dataclass
class ComplexBuilder:
    support: str = ''
    complex: str = ''
    complex_wt_percent: str = ''
    metal_wt_percent: str = ''
    metal_center: str = ''


@dataclass
class BuilderInputs:
    metals: MetalSitesBuilder = field(default_factory=MetalSitesBuilder)
    complex: ComplexBuilder = field(default_factory=ComplexBuilder)


@dataclass
class BeamRow:
    material: str
    unit: str
    thickness: str = ''        # blank = row not calculated (as v3)


def _default_rows():  # v3's default materials and units
    return {'gas': BeamRow('air', 'cm'), 'material': BeamRow('kapton', 'μm'),
            'solvent': BeamRow('water', 'cm'), 'metal': BeamRow('aluminum', 'mils')}


@dataclass
class BeamPathInputs:
    rows: dict = field(default_factory=_default_rows)


@dataclass
class IonChamberInputs:
    gas1: str = 'nitrogen'
    gas1_percent: str = ''     # default 100
    gas2: str = 'helium'
    pressure_torr: str = ''    # default 760
    length_cm: str = '15'
    other_length_cm: str = ''


# --- Results ----------------------------------------------------------------------------
@dataclass
class Used:
    quantity: str
    value: str
    source: str  # 'entered', 'default', or 'calculated'


@dataclass
class Calculation:
    ok: bool
    error: str = ''
    shown: Optional[dict] = None       # display strings (physics.result_display)
    diagnostic: str = ''
    values_used: list = field(default_factory=list)
    E0_eV: Optional[float] = None
    area_used_cm2: Optional[float] = None   # projected in angle mode; full precision
    al_used: Optional[float] = None         # projected (rotated sample) in angle mode
    tilt_deg: Optional[float] = None        # angle used (whole degrees, as v3), None if not rotated
    plot: Optional[dict] = None        # physics.plot_data, or None
    plot_error: str = ''
    plot_args: Optional[tuple] = None  # physics.plot_data inputs except the limits (replot)
    edge_table: list = field(default_factory=list)  # edge steps of all edges at this packing
    warnings: list = field(default_factory=list)    # e.g. another edge inside the step window


def _fail(message, used):
    return Calculation(ok=False, error=message, values_used=used)


def run_calculation(inp: CalculatorInputs) -> Calculation:
    """One "Calculate sample mass" click: inputs -> physics -> results and values used."""
    used = []

    def take(text, default, quantity, unit=''):
        text = text.strip()
        if text == '':
            used.append(Used(quantity, f"{default} {unit}".strip(), 'default'))
            return default
        used.append(Used(quantity, f"{text} {unit}".strip(), 'entered'))
        return text

    # Sample and dilution
    s = inp.sample
    formula, diluent = s.formula.strip(), s.diluent.strip()
    used.append(Used('Sample formula', formula, 'entered'))
    if diluent:
        ratios = (s.sample_ratio.strip(), s.diluent_ratio.strip())
        used.append(Used('Diluent', DILUENTS.get(diluent, diluent), 'entered'))
        used.append(Used('Sample : diluent (mass)', f"{ratios[0]} : {ratios[1]}", 'entered'))
    else:
        ratios = ('', '')  # blank diluent = no dilution; any typed ratios are ignored
        if s.sample_ratio.strip() or s.diluent_ratio.strip():
            used.append(Used('Dilution ratios', 'ignored (no diluent)', 'entered'))
    error, diluted = physics.dilute_sample(formula, diluent, *ratios)
    if 'ERROR' in error:
        return _fail(error, used)
    if diluent:
        used.append(Used('Diluted sample formula', diluted, 'calculated'))

    # Edge
    sc = inp.scan
    if sc.edge == 'Other':
        element, edge = 'N/A', sc.other_energy_eV.strip()
        used.append(Used('Energy for mass and edge step', f"{edge} eV", 'entered'))
    else:
        element, edge = sc.element.strip(), sc.edge
        used.append(Used('Element and edge', f"{element} {edge}", 'entered'))

    # Holder geometry (lengths entered in mm; physics takes v3's units)
    h = inp.holder
    if h.holder == 'pellet':
        d = take(h.pellet_mm, DEFAULT_PELLET_MM, 'Pellet diameter', 'mm')
        error = physics.number_error(d, 'Pellet diameter')
        if error:
            return _fail(error, used)
        area = physics.holder_area('pellet', pellet_mm=d)
    elif h.holder == 'capillary':
        d = take(h.capillary_mm, DEFAULT_CAPILLARY_MM, 'Capillary inner diameter', 'mm')
        bed = take(h.bed_mm, DEFAULT_BED_MM, 'Bed length', 'mm')
        error = (physics.number_error(d, 'Capillary inner diameter')
                 or physics.number_error(bed, 'Bed length'))
        if error:
            return _fail(error, used)
        area = physics.holder_area('capillary', d, repr(float(bed)/10))  # physics: bed in cm
    else:
        a = take(h.other_area_cm2, DEFAULT_OTHER_AREA_CM2, 'Sample area', 'cm²')
        error = physics.number_error(a, 'Sample area')
        if error:
            return _fail(error, used)
        area = physics.holder_area('other', other_cm2=a)
    if h.holder != 'other':
        used.append(Used('Sample area ⊥ beam', f"{area:.5g} cm² (full precision used)",
                         'calculated'))

    al = take(inp.absorption_length, DEFAULT_AL, 'Absorption length at E0 + 50 eV')
    al_used, area_used = al, repr(area)
    if h.angle_on:
        ang = take(h.angle_deg, DEFAULT_ANGLE_DEG, 'Sample angle to beam', '°')
        error = (physics.number_error(ang, 'Sample angle')
                 or physics.number_error(al, 'Absorption length'))
        if error:
            return _fail(error, used)
        if float(ang) > 90:
            return _fail('ERROR - Sample angle must be at most 90°', used)
        area_used = repr(physics.projected_area(area, float(ang)))
        al_used = repr(physics.projected_al(al, float(ang)))
        used.append(Used('Angle used (rounded to whole degrees, as v3)',
                         f"{round(float(ang)):.0f}°", 'calculated'))
        used.append(Used('Projected area seen by the beam', f"{float(area_used):.5g} cm²",
                         'calculated'))
        used.append(Used('Projected absorption length (sample rotated)', f"{float(al_used):.4g}",
                         'calculated'))

    r = physics.calculate_result(diluted, element, edge, area_used, al_used, *ratios)
    if 'ERROR' in r['Result']:
        return _fail(r['Result'], used)
    used.append(Used('Edge energy E0', f"{r['Enot']:.1f} eV", 'calculated'))
    if r['whilecount'] != 1:
        # Finding 3 (algorithm: Release 2): v3's retry loop shrinks the window, then goes
        # negative. Same text as the diagnostic note (change F3a).
        used.append(Used('Edge-step window (v3 retry loop)',
                         physics.retry_window_text(r['whilecount']), 'calculated'))

    calc = Calculation(ok=True, shown=physics.result_display(r, h.angle_on),
                       diagnostic=physics.diagnostic_text(r, plot=True, angle_mode=h.angle_on),
                       values_used=used, E0_eV=r['Enot'], area_used_cm2=float(area_used),
                       al_used=float(al_used),
                       tilt_deg=float(round(float(h.angle_deg.strip() or DEFAULT_ANGLE_DEG)))
                       if h.angle_on else None)

    calc.edge_table = edge_table(diluted, element, edge, area_used, al_used, r)
    calc.warnings = window_warnings(diluted, element, edge, r)

    # Plot range: set on the Plots tab, not part of the mass calculation, so not listed in
    # "values used" (researcher 2026-11-14)
    calc.plot_args = (diluted, element, edge, area_used, al_used, r['ms'], r['Enot'])
    replot(calc, inp.plot_lower_eV, inp.plot_upper_eV)
    return calc


def edge_table(diluted, element, edge, area_used, al_used, r):
    """Edge steps of every edge (K to M5) of every element at the calculated sample mass, for
    edges at or above the 2000 eV minimum, by energy (researcher request 2026-11-14: can one
    packing serve two edges?). Same numbers as the energy plot's edge-step markers."""
    t = physics.edge_steps_at_packing(diluted, area_used, al_used, r['ms'])
    rows = []
    for el, sh, E, mux, step, label in zip(t['element'], t['shell'], t['E'], t['absorption'],
                                           t['step'], t['step_label']):
        if E < physics.MIN_EDGE_ENERGY_EV:
            continue
        notes = []
        scanned = (el, sh) == (element, edge) if edge in physics.EDGE_SHELLS else             abs(E - r['Enot']) <= 1
        if scanned:
            notes.append('scanned edge' + ('' if r['whilecount'] == 1 else
                                            "; Results shows the step after v3's retry loop"))
        if step <= 0:
            notes.append('no positive step at ±50 eV: background slope larger than the jump')
        rows.append({'element': el, 'edge': sh, 'energy_eV': f'{E:.1f}',
                     'absorption': f'{mux:.2f}', 'step': label, 'note': '; '.join(notes),
                     '_E': E})
    rows.sort(key=lambda row: row['_E'])
    for row in rows:
        del row['_E']
    return rows


def window_warnings(diluted, element, edge, r):
    """Finding 13 (warning approved for Release 1, 2026-11-14): another edge inside the
    window used for the edge step adds its jump to the step."""
    window = physics.retry_window(r['whilecount'])
    return [f'{el} {sh} edge ({E:.0f} eV) lies within the ±{abs(window)} eV edge-step window, '
            f'so the edge step includes its jump'
            for el, sh, E in physics.edges_in_step_window(diluted, r['Enot'], window, element,
                                                          edge)]


def replot(calc: Calculation, lower: str = '', upper: str = '') -> None:
    """(Re)compute the plots of a successful calculation for a plot range in eV from E0
    (blank = -200 / +1000 eV). Sets calc.plot or calc.plot_error."""
    lower = lower.strip() or DEFAULT_PLOT_LOWER_EV
    upper = upper.strip() or DEFAULT_PLOT_UPPER_EV
    pd = physics.plot_data(*calc.plot_args, lower, upper)
    calc.plot, calc.plot_error = (None, pd['error']) if pd['error'] else (pd, '')


# --- Sample Builder -------------------------------------------------------------------------
def build_from_metal_sites(b: MetalSitesBuilder) -> str:
    """Formula or 'ERROR - ...' message (physics.build_metal_sample)."""
    return physics.build_metal_sample(b.site1.strip(), b.site1_wt_percent.strip(), b.site2.strip(),
                                      b.site2_wt_percent.strip(), b.support.strip())


def build_from_complex(b: ComplexBuilder) -> str:
    """Formula or v3's message (physics.build_complex_sample)."""
    return physics.build_complex_sample(b.support.strip(), b.complex.strip(),
                                        b.complex_wt_percent.strip(), b.metal_wt_percent.strip(),
                                        b.metal_center.strip())


def builder_failed(result: str) -> bool:
    return 'ERROR' in result or result.startswith('COMPLEX LODAING')


def scan_element_options(formula: str) -> list:
    """Choices for "Element to be scanned": the sample's elements with a K or L edge at or above
    2000 eV, in formula order (researcher 2026-11-18). Any element can still be typed."""
    return physics.scannable_elements(formula.strip()) if formula.strip() else []


# --- Beam path and ion chambers ---------------------------------------------------------------
def material_options():
    """Dropdown lists, as in v3 (xraydb categories, including v3's custom materials)."""
    return {'gas': list(xraydb.get_materials(categories='gas')),
            'material': list(xraydb.get_materials(categories=['ceramic', 'polymer'])),
            'solvent': list(xraydb.get_materials(categories='solvent')),
            'metal': list(xraydb.get_materials(categories='metal'))}


def beam_path(bp: BeamPathInputs, E0_eV: Optional[float], absorbed: bool = False) -> dict:
    """{row: text} at E0 + 50 eV (full-precision E0, decision 9)."""
    Enot = '' if E0_eV is None else repr(E0_eV)
    g, m, s, t = (bp.rows[k] for k in ('gas', 'material', 'solvent', 'metal'))
    return physics.transmission_panel(
        Enot, g.material, g.thickness.strip(), UNITS.index(g.unit),
        m.material, m.thickness.strip(), UNITS.index(m.unit),
        s.material, s.thickness.strip(), UNITS.index(s.unit),
        t.material, t.thickness.strip(), UNITS.index(t.unit), absorbed=absorbed)


def ion_chamber(ic: IonChamberInputs, E0_eV: Optional[float]) -> str:
    """'% beam absorbed' text at E0, or an 'ERROR - ...' message."""
    if E0_eV is None:
        return 'ERROR - E0 not defined; calculate the sample mass first'
    pct = ic.gas1_percent.strip() or DEFAULT_IC_GAS1_PERCENT
    pressure = ic.pressure_torr.strip() or DEFAULT_IC_PRESSURE_TORR
    error = (physics.number_error(pct, 'Gas 1 fraction [%]', allow_minimum=True)
             or physics.number_error(pressure, 'Total pressure [torr]'))
    if error:
        return error
    if float(pct) > 100:
        return 'ERROR - Gas 1 fraction must be at most 100%'
    result = physics.ion_chamber_absorbed(repr(E0_eV), ic.gas1, ic.gas2, -float(pct),
                                          float(pressure), ic.length_cm,
                                          ic.other_length_cm.strip())
    return 'ERROR - Ion chamber length not defined' if result is None else result


# --- Export -------------------------------------------------------------------------------
def plot_csv(pd: dict) -> dict:
    """CSV text for the three plot panels: {filename: text}."""
    def table(header, rows):
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)
        return buf.getvalue()
    e, f = pd['energy'], pd['fluorescence']
    return {
        'catmass_absorption.csv': table(['photon_energy_eV', 'sample_absorption_mu_x'],
                                        zip(e['x'], e['y'])),
        'catmass_edges.csv': table(['element', 'edge', 'edge_energy_eV',
                                    'sample_absorption_above_edge', 'estimated_edge_step'],
                                   zip(e['edges_element'], e['edges_shell'], e['edges_E'],
                                       e['edges_absorption'], e['edges_step_label'])),
        'catmass_fluorescence_lines.csv': table(['line', 'energy_eV', 'relative_intensity'],
                                                zip(f['names'], f['x'], f['y'])),
    }
