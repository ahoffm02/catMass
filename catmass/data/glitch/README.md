# Crystal glitch library

Monochromator glitch patterns shown on catMass plots: Si(220) and Si(111), Φ = 0° and 90°.
Provided by the SSRL Spectroscopy Staff
(https://www-ssrl.slac.stanford.edu/smbin/dataextractnew.pl). The patterns are roughly constant
across beamlines; the beamline labels in the file names are a guideline.

Byte-identical copies of the files in `legacy/` that the v3 reference reads (checked by
`tests/test_parity_v3.py::test_glitch_library_matches_reference`).

| File | Crystal | Φ | Shown by default |
|---|---|---|---|
| si2209093.txt | Si(220) | 90° | yes |
| si220093.txt | Si(220) | 0° | yes |
| si1119043.txt | Si(111) | 90° | no |
| si111043.txt | Si(111) | 0° | no |

## This file does not control anything
Editing this README changes nothing in catMass. The list of glitch files, their legend labels
and which are shown by default live in one place: `GLITCH_LIBRARY` in `catmass/physics.py`.

    GLITCH_LIBRARY = [
        ('si2209093.txt', 'Si(220), Φ = 90°', True),    # (file, legend label, shown by default)
        ('si220093.txt', 'Si(220), Φ = 0°', True),
        ('si1119043.txt', 'Si(111), Φ = 90°', False),
        ('si111043.txt', 'Si(111), Φ = 0°', False),
    ]

On the Plots tab, the checkboxes turn each pattern on or off for the current session.

## Changing the defaults or adding your own file (Release 1, by editing the package)
1. **File format:** plain text, one point per line: photon energy in eV, then the glitch value,
   separated by **spaces** (not tabs). catMass reads the first and last space-separated fields of
   each line, as v3 did. Lines in eV order; no header line.
2. Copy the file into this folder (`catmass/data/glitch/`).
3. Add a line for it to `GLITCH_LIBRARY` in `catmass/physics.py`, or change the `True`/`False`
   of an existing line to change what is shown by default.
4. Reinstall (`pip install .` from the repository) or run from the source folder.

Caution (v3 behavior, kept for parity): if any one file cannot be read or contains a line
that is not two numbers separated by spaces (for example tab-separated values), the **whole**
glitch overlay disappears without a message.

Loading your own glitch files from inside the app, without editing the package, is Upgrade 1
(Release 2); it should also report unreadable files instead of hiding the overlay.
