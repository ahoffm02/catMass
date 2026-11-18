# catMass

XAS transmission sample calculator from SSRL / Co-ACCESS. From the sample composition, the
sample holder and a target total absorption, catMass calculates the sample mass and the estimated
edge step, and shows the competing edges in the scan range, the sample's fluorescence lines,
monochromator glitches, and X-ray transmission through windows, gases, solvents and ion chambers.

Version 2026.11.1 (year.month.release) is a rebuild of the CatMass 2023 v3 Windows program as a
Python package with a browser interface. Its numbers are tested against v3 (see Testing).

## Install
catMass needs Python 3.9, 3.10, 3.11 or 3.12, and should be installed in **its own
environment**. It requires exact versions of numpy, xraylib and other packages; installing it
into an environment you use for other work can replace the versions that work needs.

Tested on Windows. macOS and Linux should work but have not been tested yet; please report
problems at https://github.com/ahoffm02/catMass/issues.

### With Miniconda or Anaconda (recommended)
1. If you do not have conda yet, install Miniconda (small) or Anaconda Distribution. Anaconda's
   install guide covers both: https://www.anaconda.com/docs/getting-started/installation
2. Open a conda prompt: on Windows, **Anaconda Prompt** from the Start menu; on macOS or Linux,
   a terminal.
3. Create an environment for catMass with Python 3.12 (answer `y` when asked to proceed):
   ```
   conda create -n catmass python=3.12
   ```
4. Activate it. The prompt then starts with `(catmass)`:
   ```
   conda activate catmass
   ```
5. Install catMass:
   ```
   pip install "catmass>=2026.11.1"
   ```
6. Check the installed version (it should say `Version: 2026.11.1` or later):
   ```
   pip show catmass
   ```

### With Python from python.org
Create and activate a new virtual environment with Python 3.9 to 3.12, then run steps 5 and 6
above in it.

## Launch
1. Open a conda prompt (Anaconda Prompt on Windows, a terminal on macOS or Linux).
2. Activate the environment:
   ```
   conda activate catmass
   ```
3. Start catMass:
   ```
   catmass
   ```

catMass opens in your web browser. It runs on this computer only, and the terminal shows its
address, for example `http://127.0.0.1:8080`. Closing the browser tab does not stop catMass:
open that address again to return to it. Running `catmass` again in another terminal starts a
second catMass at a different address.

**To stop catMass,** press **Ctrl+C** in the terminal where it is running, then close the
terminal.

Nothing is sent over the network. The only connection catMass can make is the optional "Check
for updates" button on the About tab.

## Update
In a conda prompt:
```
conda activate catmass
pip install --upgrade catmass
```

## Uninstall
Remove the environment and everything in it:
```
conda remove -n catmass --all
```
With a python.org virtual environment, delete the environment's folder.

## Troubleshooting
- **`catmass` is not recognized, or "command not found":** the environment is not active. Run
  `conda activate catmass` first; the prompt should start with `(catmass)`.
- **The browser did not open:** copy the address shown in the terminal into your browser.
- **`pip install` says catmass "requires a different Python" or finds no matching version, or
  `pip show catmass` says `Version: 0.1.0`:** the environment's Python is outside 3.9 to 3.12
  (check with `python --version`). Version 0.1.0 is the 2022 PyQt program, not this one; a plain
  `pip install catmass` on a newer Python installs it without warning. Create the environment
  again with `python=3.12` (Uninstall, then Install step 3).

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
From a clone of this repository, in a new environment with Python 3.9 to 3.12:
```
pip install -e ".[test]"
python -m pytest
```

- `tests/golden/v3/`: what the v3 reference program reports for 108 cases, recorded by driving
  the unchanged v3 code (`legacy/`). See `tests/golden/README.md`.
- `tests/test_parity_v3.py`: the physics core reproduces v3 (all compared values bit-identical).
- `tests/approved_changes.py`: every deliberate difference from v3, with v3 and new values, each
  checked independently in `tests/test_approved_changes.py`.
- `tests/test_calculator.py`, `tests/test_app.py`: the interface rules and the browser app.

## License
GNU General Public License v3 or later (see LICENSE).
