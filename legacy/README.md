# legacy/ — behavioral reference, do not edit

`catMass_2023v3_singlefile_EXE-REFERENCE.py` is the working single-file version ("CatMass 2023 v3
Staff only") used to build the Windows executable. It defines correct behavior for the rebuild:
the package in `catmass/` must reproduce its numbers.

- Source: `Documents/Code/legacy/CatMass/CatMass 2023 v3 Staff only.py` (last modified 2024-10-28),
  copied byte-identical on 2026-11-05.
- The images here are the logos/icons/workflow figure it loads via `resource_path()`.
- Not included yet: the `si*.txt` crystal files (BL 9-3 Si(220), BL 4-3 Si(111)) that the staff-only
  plot overlay reads from the working directory. Pending a decision on whether they belong in the
  public repo.

This folder is not part of the installed package. Do not import from it.
