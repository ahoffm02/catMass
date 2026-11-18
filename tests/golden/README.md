# Golden files — catMass v3 reference outputs

`v3/` holds what the unchanged v3 reference (`legacy/catMass_2023v3_singlefile_EXE-REFERENCE.py`)
reports for 108 cases. The rebuild must reproduce these numbers. All values are **computed** by v3,
not measured.

## Files
- `cases.py`: the case set, as user actions on v3's own widgets (groups: core matrix, A edges,
  B builders, C competing absorption, D energy range, E geometry, F dilution, G beam path and ion
  chambers, H errors and silent fallbacks, I glitch overlay).
- `generate_golden.py`: drives v3 headless (Qt offscreen), one fresh process per case.
- `summarize.py`: prints the displayed results of every case as a table, for review.
- `v3/<case>.json`: one file per case. `v3/manifest.json`: run date, environment, case list.

Each case file holds the case definition, the environment and reference hashes, every widget
state at each snapshot, module-level state, all plot data, the raw inputs and outputs of every
physics call made from GUI code, and any exception (`v3_would_terminate`: the exe would close).

## Regenerating
Only in the reference environment (the generator refuses anything else):

    conda activate catmass-v3-ref        # Python 3.9, xraylib 4.1.1, xraydb 4.5.4, matplotlib 3.5.2
    python tests/golden/generate_golden.py
    python tests/golden/summarize.py

Case files contain no timestamps, so a re-run must reproduce them byte for byte; any difference
means the environment or the reference changed. Regenerating is never a way to make a test pass:
a golden-file change is its own commit with a stated reason (parity-rebuild Stage 4.3).

## Verified 2026-11-08
- Two independent full runs produced byte-identical case files.
- The env's xraylib 4.1.1 matches the `_xraylib` + `xrl-11.dll` bundled in the v3 exe exactly on
  231,658 values (EdgeEnergy, CS_Photo at and beside every edge, AtomicWeight, ElementDensity,
  CompoundParser). The env's xraydb database is byte-identical to the exe's (SHA-256).

## Tolerance (set 2026-11-08, before any comparison)
- Same backend versions: displayed values exact; raw floats relative <= 1e-9.
- Current backends: <= 0.05% relative passes; 0.05-0.1% only with an attributed data-table
  change; > 0.1% investigated, never accepted by loosening the tolerance.
