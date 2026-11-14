"""catMass browser app (NiceGUI). Run with `catmass` or `python -m catmass`.

Display only: every rule and number comes from catmass.calculator (and through it the physics
core). Tabs agreed 2026-11-08: Calculator | Sample Builder | Plots | Beam path & ion chambers |
About. Runs locally; the only network call is the optional "Check for updates" button.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import socket
import urllib.error
import urllib.request
from dataclasses import fields, is_dataclass
from pathlib import Path

from nicegui import app, run, ui

from catmass import __version__
from catmass import calculator as calc
from catmass import physics, savefile

ASSETS = Path(__file__).parent / 'assets'
REPO_URL = 'https://github.com/ahoffm02/catMass'
RELEASES_API = 'https://api.github.com/repos/ahoffm02/catMass/releases/latest'
# Verified via Crossref, 2026-11-08 (Hard Constraint 6)
PAPER = ('J. E. Perez-Aguilar, A. Caine, S. R. Bare, A. S. Hoffman, "CatMass: software for '
         'calculating optimal sample masses for X-ray absorption spectroscopy experiments '
         'involving complex sample compositions", J. Synchrotron Rad. 30(5), 1023-1029 (2023).')
PAPER_DOI = 'https://doi.org/10.1107/S160057752300615X'
WIDE = 'w-full'
# Side by side on wide screens or zoomed out, stacked when narrow or zoomed in (researcher
# 2026-11-14, option a: inputs left, results right). lg = 1024 CSS px; at 200% browser zoom a
# 1920 px screen is 960 CSS px wide, so it stacks.
BAND = 'grid grid-cols-1 lg:grid-cols-2 gap-4 w-full max-w-screen-2xl mx-auto items-start'
SINGLE = 'w-full max-w-5xl mx-auto'

# Colours (researcher 2026-11-14: SLAC red). Stanford Cardinal Red, CMYK 0-100-65-34, is
# #8C1515 on screen (identity.stanford.edu, primary colours); its "light" variant #B83A4B is
# used for fills in dark mode. In dark mode red is a fill colour only: as text on the dark page
# it would fall below 4.5:1 contrast. tests/test_app.py checks the text colour pairs.
THEMES = {
    False: {'primary': '#8C1515', 'negative': '#C10015', 'warning': '#8A5A00'},   # light
    True: {'primary': '#B83A4B', 'negative': '#FF8A80', 'warning': '#F2C037'},    # dark
}


def copy_into(target, source):
    """Copy dataclass values in place, so widgets bound to `target` see the new values."""
    for f in fields(target):
        value = getattr(source, f.name)
        current = getattr(target, f.name)
        if is_dataclass(current):
            copy_into(current, value)
        elif isinstance(current, dict):
            for k in current:
                copy_into(current[k], value[k])
        else:
            setattr(target, f.name, value)


def free_port(preferred=8080):
    """The preferred port if free, else any free port (several catMass windows can run)."""
    for port in (preferred, 0):
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', port))
                return s.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError('no free port')


def latest_release():
    """Tag of the newest GitHub release, or None if there is none. Raises when offline."""
    request = urllib.request.Request(RELEASES_API, headers={'Accept': 'application/vnd.github+json'})
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return json.load(response).get('tag_name')
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


class CatMassPage:
    """One browser tab's state and widgets."""

    def __init__(self):
        self.s = savefile.Session()
        self.result = None          # last calc.Calculation
        self.beam_result = None     # last beam-path {row: text}
        self.ic_result = None       # last ion-chamber text
        self.stale = False
        self.dark = ui.dark_mode(False)
        ui.colors(**THEMES[False])
        self.glitch_shown = {f: shown for f, _, shown in physics.GLITCH_LIBRARY}
        self.materials = calc.material_options()
        self.build()

    # --- layout --------------------------------------------------------------------------
    def build(self):
        # The header stays pinned to the top, with the tabs in it (researcher 2026-11-14)
        with ui.header(elevated=True).classes('column items-stretch gap-0 q-pa-none'):
            with ui.row().classes('w-full items-center justify-between px-4 pt-2'):
                with ui.row().classes('items-center gap-3'):
                    ui.label('catMass').classes('text-h5')
                    ui.label(f'XAS Sample Mass Calculator · {__version__}').classes(
                        'text-caption').mark('title')
                    # The logos are red and black, so they sit on a white chip (readable on the
                    # red header and in dark mode)
                    with ui.row().classes('items-center gap-2 bg-white rounded-borders px-2 py-1'):
                        ui.image(ASSETS / 'SSRL_logo_2021.png').classes('h-6 w-16').props(
                            'fit=contain alt="SSRL"')
                        ui.image(ASSETS / 'co_access_logo_text.png').classes('h-6 w-20').props(
                            'fit=contain alt="Co-ACCESS"')
                with ui.row().classes('items-center'):
                    ui.button('Open', icon='folder_open', on_click=self.open_dialog).props(
                        'flat color=white')
                    ui.button('Save', icon='save', on_click=self.save).props('flat color=white')
                    ui.button('Quit', icon='power_settings_new', on_click=self.quit).props(
                        'flat color=white').mark('quit')
                    ui.switch('Dark', on_change=self.set_dark).props(
                        'color=white keep-color').mark('dark')
            with ui.tabs().classes('w-full').props(
                    'dense align=left indicator-color=white active-color=white') as self.tabs:
                self.t_calc = ui.tab('Calculator', icon='calculate')
                self.t_builder = ui.tab('Sample Builder', icon='science')
                self.t_plots = ui.tab('Plots', icon='show_chart')
                self.t_beam = ui.tab('Beam path & ion chambers', icon='straighten')
                self.t_about = ui.tab('About', icon='info')
        with ui.tab_panels(self.tabs, value=self.t_calc).classes('w-full'):
            with ui.tab_panel(self.t_calc):
                with ui.element('div').classes(BAND):
                    self.build_calculator()
            with ui.tab_panel(self.t_builder):
                with ui.element('div').classes(BAND):
                    self.build_builder()
            with ui.tab_panel(self.t_plots):
                with ui.column().classes(SINGLE):
                    self.build_plots()
            with ui.tab_panel(self.t_beam):
                with ui.element('div').classes(BAND):
                    self.build_beam_path()
            with ui.tab_panel(self.t_about):
                with ui.column().classes(SINGLE):
                    self.build_about()

    def text_input(self, obj, attr, label, placeholder='', marker=None, track=True, **kwargs):
        """Text field bound to a dataclass attribute; `track` marks results out of date."""
        field = ui.input(label, placeholder=placeholder,
                         on_change=self.inputs_changed if track else None,
                         **kwargs).bind_value(obj, attr).classes('min-w-[12rem] grow')
        if marker:
            field.mark(marker)
        return field

    def build_calculator(self):
        c = self.s.calculator
        inputs = ui.column().classes('w-full gap-4')
        outputs = ui.column().classes('w-full gap-4')
        with inputs:
            self.build_calculator_inputs(c)
        with outputs:
            self.results = ui.card().classes(WIDE).props('role=status aria-live=polite')
            self.render_results()

    def build_calculator_inputs(self, c):
        with ui.card().classes(WIDE):
            ui.label('Sample and dilution').classes('text-h6')
            with ui.row().classes('w-full items-center'):
                self.text_input(c.sample, 'formula', 'Sample formula',
                                'e.g. Pt0.01Al2O3, or use the Sample Builder', 'formula')
                ui.button('Sample Builder', icon='science',
                          on_click=lambda: self.tabs.set_value(self.t_builder)).props('outline')
            with ui.row().classes('w-full'):
                # Common diluents, or type any formula (researcher 2026-11-14). Cellulose is
                # (C6H10O5)n, not C: O absorbs more per gram than C.
                ui.select(calc.DILUENTS, label='Diluent', with_input=True,
                          new_value_mode='add-unique', on_change=self.inputs_changed).bind_value(
                    c.sample, 'diluent', forward=lambda v: v or '',
                    backward=lambda v: v).classes('min-w-[12rem] grow').mark('diluent')
                self.text_input(c.sample, 'sample_ratio', 'Sample mass ratio', 'e.g. 1',
                                'sample_ratio')
                self.text_input(c.sample, 'diluent_ratio', 'Diluent mass ratio', 'e.g. 9',
                                'diluent_ratio')
        with ui.card().classes(WIDE):
            ui.label('Edge').classes('text-h6')
            with ui.row().classes('w-full items-center'):
                ui.select(calc.EDGES, label='Edge', on_change=self.inputs_changed).bind_value(
                    c.scan, 'edge').classes('min-w-[8rem]').mark('edge')
                self.text_input(c.scan, 'element', 'Element to be scanned', 'e.g. Pt',
                                'element').bind_visibility_from(c.scan, 'edge',
                                                                backward=lambda e: e != 'Other')
                self.text_input(c.scan, 'other_energy_eV', 'Energy for mass and edge step [eV]',
                                'required for "Other"', 'other_energy').bind_visibility_from(
                    c.scan, 'edge', value='Other')
        with ui.card().classes(WIDE):
            ui.label('Sample holder and absorption').classes('text-h6')
            ui.radio(calc.HOLDERS, on_change=self.inputs_changed).bind_value(
                c.holder, 'holder').props('inline').mark('holder')
            with ui.row().classes('w-full').bind_visibility_from(c.holder, 'holder', value='pellet'):
                self.text_input(c.holder, 'pellet_mm', 'Pellet diameter [mm]',
                                f'{calc.DEFAULT_PELLET_MM} (default)', 'pellet_mm',
                                autocomplete=calc.PELLET_DIAMETERS_MM)
            with ui.row().classes('w-full').bind_visibility_from(c.holder, 'holder',
                                                                 value='capillary'):
                self.text_input(c.holder, 'capillary_mm', 'Capillary inner diameter [mm]',
                                f'{calc.DEFAULT_CAPILLARY_MM} (default)', 'capillary_mm',
                                autocomplete=calc.CAPILLARY_IDS_MM)
                self.text_input(c.holder, 'bed_mm', 'Bed length [mm]',
                                f'{calc.DEFAULT_BED_MM} (default)', 'bed_mm')
            with ui.row().classes('w-full').bind_visibility_from(c.holder, 'holder', value='other'):
                self.text_input(c.holder, 'other_area_cm2', 'Sample area ⊥ beam [cm²]',
                                f'{calc.DEFAULT_OTHER_AREA_CM2} (default)', 'other_area')
            with ui.row().classes('w-full items-center'):
                ui.switch('Sample tilted to the beam', on_change=self.inputs_changed).bind_value(
                    c.holder, 'angle_on').mark('angle_on')
                self.text_input(c.holder, 'angle_deg', 'Angle to beam [°]',
                                f'{calc.DEFAULT_ANGLE_DEG} (default)', 'angle_deg'
                                ).bind_visibility_from(c.holder, 'angle_on')
            with ui.row().classes('w-full'):
                self.text_input(c, 'absorption_length', 'Total absorption μx at E0 + 50 eV',
                                f'{calc.DEFAULT_AL} (default)', 'absorption_length')
        ui.button('Calculate sample mass', icon='play_arrow', on_click=self.calculate).props(
            'size=lg').classes('self-center').mark('calculate')

    def build_builder(self):
        b = self.s.sample_builder
        with ui.card().classes(WIDE):
            ui.label('Metals on a support').classes('text-h6')
            ui.label('wt% must reflect the entire metal site. Metal site 2 is optional.').classes(
                'text-caption')
            with ui.row().classes('w-full'):
                self.text_input(b.metals, 'support', 'Support', 'e.g. Al2O3', 'b_support', track=False)
            with ui.row().classes('w-full'):
                self.text_input(b.metals, 'site1', 'Metal site 1', 'e.g. Pt, PtO2, Pt1Sn3', 'b_site1', track=False)
                self.text_input(b.metals, 'site1_wt_percent', 'Site 1 loading [wt%]', '', 'b_wt1', track=False)
            with ui.row().classes('w-full'):
                self.text_input(b.metals, 'site2', 'Metal site 2', 'optional', 'b_site2', track=False)
                self.text_input(b.metals, 'site2_wt_percent', 'Site 2 loading [wt%]', '', 'b_wt2', track=False)
            self.metals_message = ui.label().classes('text-negative')
            ui.button('Use this sample', icon='check',
                      on_click=lambda: self.use_builder('metals')).mark('use_metals')
        with ui.card().classes(WIDE):
            ui.label('Supported metal complexes').classes('text-h6')
            ui.label('Give the complex loading, or the metal loading and metal center '
                     '(not both).').classes('text-caption')
            with ui.row().classes('w-full'):
                self.text_input(b.complex, 'support', 'Support', 'e.g. SiO2', 'c_support', track=False)
                self.text_input(b.complex, 'complex', 'Metal complex', 'e.g. Rh(CO)2(C5H7O2)',
                                'c_complex', track=False)
            with ui.row().classes('w-full'):
                self.text_input(b.complex, 'complex_wt_percent', 'Complex loading [wt%]', '',
                                'c_complex_wt', track=False)
                self.text_input(b.complex, 'metal_wt_percent', 'Metal loading [wt%]', '',
                                'c_metal_wt', track=False)
                self.text_input(b.complex, 'metal_center', 'Metal center', 'e.g. Rh', 'c_center', track=False)
            self.complex_message = ui.label().classes('text-negative')
            ui.button('Use this sample', icon='check',
                      on_click=lambda: self.use_builder('complex')).mark('use_complex')

    def build_beam_path(self):
        bp, ic = self.s.beam_path, self.s.ion_chamber
        options = {'gas': self.materials['gas'], 'material': self.materials['material'],
                   'solvent': self.materials['solvent'], 'metal': self.materials['metal']}
        names = {'gas': 'Gas', 'material': 'Window / wall material', 'solvent': 'Solvent',
                 'metal': 'Metal'}
        with ui.card().classes(WIDE):
            ui.label('X-ray transmission through materials at E0 + 50 eV').classes('text-h6')
            ui.label('Values are for the beam perpendicular to each layer. A row is calculated '
                     'when its thickness is filled in.').classes('text-caption')
            self.beam_labels = {}
            for key, row in bp.rows.items():
                with ui.row().classes('w-full items-center'):
                    ui.select(options[key], label=names[key], with_input=True).bind_value(
                        row, 'material').classes('min-w-[12rem]').mark(f'{key}_material')
                    ui.input('Thickness', placeholder='blank = skip').bind_value(
                        row, 'thickness').classes('w-32').mark(f'{key}_thickness')
                    ui.select(calc.UNITS, label='Unit').bind_value(row, 'unit').classes('w-24')
                    self.beam_labels[key] = ui.label().classes('text-subtitle1').mark(f'{key}_result')
            with ui.row():
                ui.button('% Transmitted', on_click=lambda: self.update_beam(False)).mark('transmitted')
                ui.button('Absorbed (μx)', on_click=lambda: self.update_beam(True)).mark('absorbed')
        with ui.card().classes(WIDE):
            ui.label('X-ray absorption in an ion chamber at E0').classes('text-h6')
            with ui.row().classes('w-full items-center'):
                ui.select(self.materials['gas'], label='Gas 1').bind_value(ic, 'gas1').classes(
                    'min-w-[10rem]').mark('ic_gas1')
                ui.input('Gas 1 [%]', placeholder=f'{calc.DEFAULT_IC_GAS1_PERCENT} (default)'
                         ).bind_value(ic, 'gas1_percent').classes('w-32').mark('ic_percent')
                ui.select(self.materials['gas'], label='Gas 2 (rest)').bind_value(
                    ic, 'gas2').classes('min-w-[10rem]').mark('ic_gas2')
            with ui.row().classes('w-full items-center'):
                ui.input('Total pressure [torr]',
                         placeholder=f'{calc.DEFAULT_IC_PRESSURE_TORR} (default)').bind_value(
                    ic, 'pressure_torr').classes('w-40').mark('ic_pressure')
                ui.select(calc.IC_LENGTHS_CM, label='Chamber length [cm]').bind_value(
                    ic, 'length_cm').classes('w-40').mark('ic_length')
                ui.input('Length [cm]', placeholder='required for "Other"').bind_value(
                    ic, 'other_length_cm').bind_visibility_from(ic, 'length_cm', value='Other'
                                                                ).classes('w-32').mark('ic_other')
            with ui.row().classes('items-center'):
                ui.button('Update', icon='refresh', on_click=self.update_ion_chamber).mark('ic_update')
                self.ic_label = ui.label().classes('text-subtitle1').mark('ic_result')

    def build_about(self):
        with ui.card().classes(WIDE):
            ui.label(f'catMass {__version__}').classes('text-h6')
            ui.markdown(
                'Calculates the sample mass for a transmission XAS measurement from the sample '
                'composition, the sample holder and a target total absorption, together with the '
                'estimated edge step, competing edges in the scan range, fluorescence lines and '
                'monochromator glitches.\n\n'
                f'**Please cite:** {PAPER} [doi:10.1107/S160057752300615X]({PAPER_DOI})\n\n'
                'Authors: Jorge E. Perez-Aguilar, Adam S. Hoffman. Co-ACCESS is supported by the '
                'U.S. Department of Energy, Office of Basic Energy Sciences, Chemical Sciences, '
                'Geosciences and Biosciences. We thank the SSRL Spectroscopy Staff for providing '
                'the [crystal glitch library](https://www-ssrl.slac.stanford.edu/smbin/dataextractnew.pl).'
                '\n\n[Co-ACCESS information](https://web.slac.stanford.edu/coaccess) · '
                f'[Source code]({REPO_URL})\n\n'
                f'Physics libraries: xraylib {physics.xraylib.__version__}, '
                f'xraydb {physics.xraydb.__version__}. Values are calculated, not measured.')
        with ui.card().classes(WIDE):
            ui.label('Common Co-ACCESS XAS cells: wall thickness [μm]').classes('text-h6')
            ui.table(columns=[{'name': c, 'label': c, 'field': c} for c in
                              ('Capillary diameter', 'Kapton', 'Quartz')],
                     rows=[{'Capillary diameter': '1 mm', 'Kapton': '80', 'Quartz': '10 or 20'},
                           {'Capillary diameter': '3 mm', 'Kapton': '87', 'Quartz': '200'}])
            ui.label('Other: Kapton shield 2 mils; Mylar 3.5 μm.')
        with ui.card().classes(WIDE):
            with ui.row().classes('items-center'):
                ui.button('Check for updates', icon='update', on_click=self.check_updates).mark(
                    'check_updates')
                self.update_label = ui.label().classes('text-body2')
            ui.label('Checking contacts GitHub once; catMass makes no other network '
                     'connections.').classes('text-caption')

    # --- results ---------------------------------------------------------------------------
    def render_results(self):
        self.results.clear()
        r = self.result
        with self.results:
            ui.label('Results').classes('text-h6')
            if r is None:
                ui.label('Enter a sample and press "Calculate sample mass".').classes('text-body2')
                return
            if self.stale:
                ui.label('Inputs have changed since this calculation; press Calculate again.'
                         ).classes('text-warning').mark('stale')
            if not r.ok:
                with ui.row().classes('items-center'):
                    ui.icon('error', color='negative')
                    ui.label(r.error).classes('text-negative').mark('error')
            else:
                shown = r.shown
                rows = [('Diluted sample mass', f"{shown['mass']} mg", 'mass'),
                        ('Estimated edge step', shown['step'] + (
                            '  (above 1: consider diluting)' if shown['step_red'] else ''), 'step'),
                        ('Sample mass', f"{shown['sample_mass']} mg", 'sample_mass'),
                        ('Diluent mass', f"{shown['diluent_mass']} mg", 'diluent_mass'),
                        ('Edge energy E0', f"{shown['E0']} eV", 'E0')]
                with ui.grid(columns=2).classes('gap-x-6'):
                    for name, value, marker in rows:
                        ui.label(name)
                        label = ui.label(value).classes('text-weight-bold').mark(marker)
                        if marker == 'step' and shown['step_red']:
                            label.classes('text-negative')
                if r.diagnostic:
                    ui.label(r.diagnostic).classes('text-body2').mark('diagnostic')
                if r.plot_error:
                    ui.label(r.plot_error).classes('text-negative').mark('plot_error')
            with ui.expansion('Values used in this calculation', value=False).classes(
                    'w-full').mark('values_expansion'):
                ui.table(columns=[{'name': 'quantity', 'label': 'Quantity', 'field': 'quantity',
                                   'align': 'left'},
                                  {'name': 'value', 'label': 'Value', 'field': 'value',
                                   'align': 'left'},
                                  {'name': 'source', 'label': 'Source', 'field': 'source',
                                   'align': 'left'}],
                         rows=[vars(u) for u in r.values_used]).classes('w-full').props(
                    'dense flat').mark('values_used')

    def build_plots(self):
        """Plots tab: controls built once (they must not be deleted by their own handlers);
        messages and figures are redrawn by render_plots."""
        c = self.s.calculator
        with ui.column().classes(WIDE):
            self.plot_messages = ui.column().classes('w-full')
            with ui.column().classes('w-full') as self.plot_controls:
                with ui.row().classes('items-center'):
                    ui.input('Plot from [eV from E0]',
                             placeholder=f'{calc.DEFAULT_PLOT_LOWER_EV} (default)').bind_value(
                        c, 'plot_lower_eV').classes('w-44').mark('plot_lower')
                    ui.input('Plot to [eV from E0]',
                             placeholder=f'{calc.DEFAULT_PLOT_UPPER_EV} (default)').bind_value(
                        c, 'plot_upper_eV').classes('w-44').mark('plot_upper')
                    ui.button('Update plots', icon='refresh', on_click=self.update_plots).mark(
                        'update_plots')
                with ui.row().classes('items-center'):
                    ui.label('Glitch overlay:')
                    for f, label, _ in physics.GLITCH_LIBRARY:
                        ui.checkbox(label, value=self.glitch_shown[f],
                                    on_change=lambda e, f=f: self.set_glitch(f, e.value))
            self.figures = ui.column().classes('w-full')
        self.render_plots()

    def render_plots(self):
        r = self.result
        ok = r is not None and r.ok
        self.plot_controls.set_visibility(ok)  # stays usable when only the plot range is bad
        self.plot_messages.clear()
        self.figures.clear()
        with self.plot_messages:
            if r is None:
                ui.label('Calculate a sample to see its plots.')
            elif not r.ok:
                ui.label('No plots: the last calculation did not succeed.')
            else:
                if self.stale:
                    ui.label('Inputs have changed since these plots were made.').classes(
                        'text-warning')
                if r.plot_error:
                    ui.label(r.plot_error).classes('text-negative').mark('plot_range_error')
        if not ok or r.plot is None:
            return
        with self.figures:
            for figure in plot_figures(r.plot, self.glitch_shown, self.dark.value):
                ui.plotly(figure).classes('w-full h-96')
            with ui.row():
                for name, text in calc.plot_csv(r.plot).items():
                    ui.button(name, icon='download',
                              on_click=lambda n=name, t=text: ui.download.content(
                                  t.encode('utf-8'), n, 'text/csv')).props('outline')

    def set_dark(self, e):
        self.dark.set_value(e.value)
        ui.colors(**THEMES[bool(e.value)])
        self.render_plots()  # plot colours follow the theme

    def update_plots(self):
        c = self.s.calculator
        calc.replot(self.result, c.plot_lower_eV, c.plot_upper_eV)
        self.render_plots()

    def set_glitch(self, file, shown):
        self.glitch_shown[file] = shown
        self.render_plots()

    # --- actions ---------------------------------------------------------------------------
    def inputs_changed(self, *_):
        if self.result is not None and not self.stale:
            self.stale = True
            self.render_results()
            self.render_plots()

    def calculate(self):
        self.result = calc.run_calculation(self.s.calculator)
        self.stale = False
        self.ic_result = None
        if self.result.ok:
            self.update_ion_chamber()  # agreed: calculated with the mass, plus its Update button
        self.render_results()
        self.render_plots()

    def use_builder(self, which):
        b = self.s.sample_builder
        if which == 'metals':
            formula, message = calc.build_from_metal_sites(b.metals), self.metals_message
        else:
            formula, message = calc.build_from_complex(b.complex), self.complex_message
        if calc.builder_failed(formula):
            message.set_text(formula)
            return
        message.set_text('')
        self.s.calculator.sample.formula = formula
        self.inputs_changed()
        ui.notify('Sample formula updated from the Sample Builder', type='positive')
        self.tabs.set_value(self.t_calc)

    def E0(self):
        return self.result.E0_eV if self.result is not None and self.result.ok else None

    def update_beam(self, absorbed):
        self.beam_result = calc.beam_path(self.s.beam_path, self.E0(), absorbed)
        for key, label in self.beam_labels.items():
            label.set_text(self.beam_result.get(key, ''))

    def update_ion_chamber(self):
        self.ic_result = calc.ion_chamber(self.s.ion_chamber, self.E0())
        text = self.ic_result if self.ic_result.startswith('ERROR') else \
            f'{self.ic_result} % beam absorbed'
        self.ic_label.set_text(text)

    def quit(self):
        """Stop catMass. The tab is replaced by a note first, since the page cannot update
        once the server has stopped."""
        ui.run_javascript(
            "document.body.innerHTML = '<div style=\"font-family:sans-serif;margin:4rem\">"
            "<h2>catMass has stopped.</h2><p>You can close this browser tab.</p></div>'")
        ui.timer(0.5, app.shutdown, once=True)

    def save(self):
        text = savefile.dumps(self.s, self.result, self.beam_result, self.ic_result)
        ui.download.content(text.encode('utf-8'), 'catmass_calculation.json', 'application/json')

    def open_dialog(self):
        with ui.dialog() as dialog, ui.card():
            ui.label('Open a catMass file (.json)').classes('text-h6')
            ui.upload(on_upload=lambda e: self.load(e, dialog), auto_upload=True).props(
                'accept=.json').mark('upload')
            ui.button('Cancel', on_click=dialog.close).props('flat')
        dialog.open()

    async def load(self, e, dialog):
        text = e.file.text()
        if inspect.isawaitable(text):
            text = await text
        try:
            loaded = savefile.loads(text)
        except savefile.SaveFileError as exc:
            ui.notify(str(exc), type='negative', multi_line=True)
            return
        copy_into(self.s, loaded)
        dialog.close()
        self.calculate()  # agreed: opening restores the inputs and recalculates
        ui.notify('File opened and recalculated', type='positive')

    async def check_updates(self):
        self.update_label.set_text('Checking...')
        try:
            tag = await run.io_bound(latest_release)
        except Exception:
            self.update_label.set_text('Could not check for updates (offline?).')
            return
        if tag is None:
            self.update_label.set_text('No releases published yet.')
        elif tag.lstrip('v') == __version__:
            self.update_label.set_text(f'catMass {__version__} is the latest version.')
        else:
            self.update_label.set_text(f'catMass {tag} is available at {REPO_URL}/releases')


# Categorical colours: the dataviz reference palette, unchanged (validated there, light and dark
# columns). Colour follows the element (order of first appearance in the sample), never its rank.
# Only the first three slots stay distinct in every pairing (colour-vision deficiency included),
# so each element also gets its own marker shape, and the legend names every element.
SERIES = {False: ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7',
                  '#e34948'],
          True: ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9',
                 '#e66767']}
OTHER_GRAY = {False: '#8a8987', True: '#9a9993'}  # beyond eight elements: one "Other" series
SYMBOLS = ['circle', 'square', 'diamond', 'triangle-up', 'triangle-down', 'star', 'hexagon',
           'cross']
GREEK = {'a': 'α', 'b': 'β', 'g': 'γ', 'l': 'ℓ', 'n': 'η', 'e': 'ε', 's': 'σ', 't': 'τ', 'u': 'υ',
         'v': 'ν'}


def line_label(name):
    """xraydb line name to the usual notation, e.g. 'Ka1' -> 'Kα1', 'Lb2,15' -> 'Lβ2,15'."""
    if len(name) > 1 and name[1] in GREEK:
        return name[0] + GREEK[name[1]] + name[2:]
    return name


def plot_figures(pd, glitch_shown, dark=False):
    """Three Plotly figures (energy, k, fluorescence) from physics.plot_data output."""
    template = 'plotly_dark' if dark else 'plotly_white'
    colours = SERIES[dark]
    config = {'displaylogo': False, 'responsive': True,
              'toImageButtonOptions': {'format': 'png', 'filename': 'catmass_plot', 'scale': 2}}
    e, k, f, gl = pd['energy'], pd['k'], pd['fluorescence'], pd['glitches'] or []
    shown = [g for g in gl if glitch_shown.get(g['file'])]
    # each glitch file keeps its own colour (slots 3-6), whether or not the others are shown
    glitch_colour = {fname: colours[2 + i] for i, (fname, _, _) in enumerate(physics.GLITCH_LIBRARY)}

    data = [{'type': 'scatter', 'mode': 'lines', 'x': list(e['x']), 'y': list(e['y']),
             'name': 'Total sample absorption', 'line': {'color': colours[0], 'width': 2},
             'hovertemplate': '%{x:.1f} eV<br>absorption %{y:.3f}<extra></extra>'},
            {'type': 'scatter', 'mode': 'markers+text', 'x': list(e['edges_E']),
             'y': list(e['edges_absorption']), 'text': list(e['edges_step_label']),
             'textposition': 'top center', 'name': 'Estimated edge step(s)',
             'marker': {'color': colours[1], 'size': 9},
             'customdata': [f'{el} {sh}' for el, sh in zip(e['edges_element'], e['edges_shell'])],
             'hovertemplate': '%{customdata} edge, %{x:.1f} eV<br>step %{text}<extra></extra>'}]
    data += [{'type': 'scatter', 'mode': 'lines', 'x': g['E_x'], 'y': g['E_y'], 'yaxis': 'y2',
              'name': g['label'], 'line': {'width': 1, 'color': glitch_colour[g['file']]},
              'hoverinfo': 'skip'} for g in shown]
    energy = {'data': data, 'config': config, 'layout': {
        'template': template, 'title': {'text': 'Sample absorption'},
        'xaxis': {'title': {'text': 'Photon energy (eV)'}, 'tickformat': '.0f', 'range': e['xlim']},
        'yaxis': {'title': {'text': 'Sample absorption (μ<sub>average</sub> · mass/area)'},
                  'range': e['ylim']},
        'yaxis2': {'overlaying': 'y', 'side': 'right', 'range': [-7, 7], 'showticklabels': False,
                   'showgrid': False},
        'legend': {'orientation': 'h', 'y': -0.25}, 'margin': {'t': 40}}}

    labels = [f'{el} {ed}' for el, ed in zip(k['element_labels'], k['edge_labels'])]
    data = [{'type': 'scatter', 'mode': 'markers+text', 'x': list(k['edges_k']),
             'y': list(k['edges_y']), 'text': labels, 'textposition': 'top center',
             'name': 'Other edges in the scan range', 'marker': {'color': colours[1], 'size': 9},
             'hovertemplate': '%{text} edge, k = %{x:.2f} Å⁻¹<extra></extra>'}]
    data += [{'type': 'scatter', 'mode': 'lines', 'x': g['k_x'], 'y': g['k_y'], 'name': g['label'],
              'line': {'width': 1, 'color': glitch_colour[g['file']]}, 'hoverinfo': 'skip'}
             for g in shown]
    kspace = {'data': data, 'config': config, 'layout': {
        'template': template, 'title': {'text': 'Edges and glitches in k'},
        'xaxis': {'title': {'text': 'k (Å<sup>-1</sup>)'}, 'range': k['xlim']},
        'yaxis': {'title': {'text': 'Glitch amplitude (%)'}, 'range': [-7, 7]},
        'legend': {'orientation': 'h', 'y': -0.25}, 'margin': {'t': 40}}}

    # Fluorescence lines: one series per element (researcher 2026-11-14). Intensities are only
    # relative, so the y axis has no values and the hover text gives line and energy only.
    # Only elements with a line inside the plotted window get a series (and a legend entry);
    # colours follow the order of first appearance among those.
    lo, hi = f['xlim']
    in_view = [j for j, x in enumerate(f['x']) if lo <= x <= hi]
    elements = list(dict.fromkeys(f['element'][j] for j in in_view))
    data, annotations = [], []
    for i, element in enumerate(elements):
        if i < len(colours):
            name, colour, symbol, members = element, colours[i], SYMBOLS[i], {element}
        elif i == len(colours):
            name, colour, symbol, members = 'Other elements', OTHER_GRAY[dark], 'circle-open', \
                set(elements[len(colours):])
        else:
            break
        idx = [j for j in in_view if f['element'][j] in members]
        top = max(idx, key=lambda j: f['y'][j])  # direct label on the strongest line in view
        annotations.append({'x': f['x'][top], 'y': f['y'][top], 'yshift': 14, 'showarrow': False,
                            'text': f"{f['element'][top]} {line_label(f['line'][top])}"})
        xs, ys = [], []
        for j in idx:
            xs += [f['x'][j], f['x'][j], None]
            ys += [0, f['y'][j], None]
        data.append({'type': 'scatter', 'mode': 'lines', 'x': xs, 'y': ys, 'name': name,
                     'legendgroup': name, 'line': {'color': colour, 'width': 2},
                     'hoverinfo': 'skip'})
        data.append({'type': 'scatter', 'mode': 'markers', 'x': [f['x'][j] for j in idx],
                     'y': [f['y'][j] for j in idx], 'name': name, 'legendgroup': name,
                     'showlegend': False, 'marker': {'color': colour, 'size': 9, 'symbol': symbol},
                     'customdata': [f"{f['element'][j]} {line_label(f['line'][j])} "
                                    f"({f['edge'][j]} edge)" for j in idx],
                     'hovertemplate': '%{customdata}<br>%{x:.0f} eV<extra></extra>'})
    shapes = []
    if f['band']:
        shapes.append({'type': 'rect', 'x0': f['band'][0], 'x1': f['band'][1], 'y0': 0,
                       'y1': f['band'][2], 'fillcolor': 'gray', 'opacity': 0.15,
                       'line': {'width': 0}, 'layer': 'below'})
    fluorescence = {'data': data, 'config': config, 'layout': {
        'template': template, 'title': {'text': 'Fluorescence lines of the sample'},
        'xaxis': {'title': {'text': 'Photon energy (eV)'}, 'tickformat': '.0f', 'range': f['xlim']},
        'yaxis': {'title': {'text': 'Relative line intensity'}, 'range': f['ylim'],
                  'showticklabels': False},
        'shapes': shapes, 'annotations': annotations, 'legend': {'title': {'text': 'Element'}},
        'margin': {'t': 40}}}
    return [energy, kspace, fluorescence]


class AutoStop:
    """Stop catMass when no browser tab has been connected for `grace` seconds (researcher
    2026-11-14). The delay lets a page reload or a brief network drop reconnect first."""

    def __init__(self, shutdown, grace=15.0):
        self.shutdown, self.grace, self.clients = shutdown, grace, set()

    def connected(self, client):
        self.clients.add(client.id)

    async def disconnected(self, client):
        self.clients.discard(client.id)
        await asyncio.sleep(self.grace)
        if not self.clients:
            self.shutdown()


def root():
    # Keep labels above the fields so the grey "(default)" placeholders are always visible;
    # Quasar otherwise shows a placeholder only while the field has focus.
    ui.input.default_props('stack-label')
    CatMassPage()


def main():
    """Entry point of the `catmass` command: serve locally and open the browser."""
    auto_stop = AutoStop(app.shutdown)
    app.on_connect(auto_stop.connected)
    app.on_disconnect(auto_stop.disconnected)
    ui.run(root, title='catMass', favicon=ASSETS / 'CoACCESSScale_v6.ico', host='127.0.0.1',
           port=free_port(), reload=False, show=True, show_welcome_message=False)
