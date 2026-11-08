# legacy/ — behavioral reference, do not edit

`catMass_2023v3_singlefile_EXE-REFERENCE.py` is the working single-file version ("CatMass 2023 v3
Staff only") used to build the Windows executable. It defines correct behavior for the rebuild:
the package in `catmass/` must reproduce its numbers.

- Source: `Documents/Code/legacy/CatMass/CatMass 2023 v3 Staff only.py` (last modified 2024-10-28),
  copied byte-identical on 2026-11-05.
- The images here are the logos/icons/workflow figure it loads via `resource_path()`.
- `si*.txt`: crystal glitch library (Si(220) and Si(111), Φ = 0° and 90°; from the SSRL Spectroscopy
  Staff, https://www-ssrl.slac.stanford.edu/smbin/dataextractnew.pl). The reference reads them from the
  working directory. `si220073.txt` is present but unused (commented out in the source).

This folder is not part of the installed package. Do not import from it.
