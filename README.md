# catMass

XAS transmission sample calculator from SSRL / Co-ACCESS. From the sample composition, the
sample holder and a target total absorption, catMass calculates the sample mass and the estimated
edge step, and shows the competing edges in the scan range, the sample's fluorescence lines,
monochromator glitches, and X-ray transmission through windows, gases, solvents and ion chambers.

Version 2026.11.1 (year.month.release) is a rebuild of the CatMass 2023 v3 Windows program as a
Python package with a browser interface. Its numbers are tested against v3 (see Testing).

## Install and run
Needs Python 3.9, 3.10, 3.11 or 3.12.

    pip install catmass-2026.11.1-py3-none-any.whl
    catmass

`catmass` (or `python -m catmass`) starts catMass on this computer and opens it in your web
browser. Nothing is sent over the network; the only connection catMass can make is the optional
"Check for updates" button on the About tab.

## Using catMass
- **Calculator:** sample formula (or build one in the Sample Builder), optional diluent and mass
  ratio, element and edge (or an energy), sample holder, target absorption. Empty fields use the
  default shown in grey. The results list every value used in the calculation. Lengths are in mm.
- **Sample Builder:** metals on a support, or supported metal complexes.
- **Plots:** sample absorption around the edge with the estimated edge steps, other edges and
  glitches in k, and fluorescence lines; PNG and CSV export.
- **Beam path & ion chambers:** transmission through gases, windows, solvents and metals at
  E0 + 50 eV; absorption in an ion chamber gas mix at E0.
- **Save / Open:** a readable JSON file. Opening a file restores the inputs and recalculates.

Calculated values are estimates from tabulated cross sections, not measurements.

## Please cite
J. E. Perez-Aguilar, A. Caine, S. R. Bare, A. S. Hoffman, "CatMass: software for calculating
optimal sample masses for X-ray absorption spectroscopy experiments involving complex sample
compositions", *J. Synchrotron Rad.* **30**(5), 1023-1029 (2023).
https://doi.org/10.1107/S160057752300615X

## Testing (developers)
    pip install catmass[test]   # from a checkout: pip install -e .[test]
    python -m pytest

- `tests/golden/v3/`: what the v3 reference program reports for 108 cases, recorded by driving
  the unchanged v3 code (`legacy/`). See `tests/golden/README.md`.
- `tests/test_parity_v3.py`: the physics core reproduces v3 (all compared values bit-identical).
- `tests/approved_changes.py`: every deliberate difference from v3, with v3 and new values, each
  checked independently in `tests/test_approved_changes.py`.
- `tests/test_calculator.py`, `tests/test_app.py`: the interface rules and the browser app.

## License
GNU General Public License v3 or later (see LICENSE).
