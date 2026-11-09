# Crystal glitch library

Monochromator glitch patterns shown on catMass plots: Si(220) and Si(111), Φ = 0° and 90°.
Provided by the SSRL Spectroscopy Staff
(https://www-ssrl.slac.stanford.edu/smbin/dataextractnew.pl). The patterns are roughly constant
across beamlines; the beamline labels in the file names are a guideline.

Byte-identical copies of the files in `legacy/` that the v3 reference reads (checked by
`tests/test_parity_v3.py::test_glitch_library_matches_reference`). Each line: energy [eV], value.

| File | Crystal | Φ | Shown by default |
|---|---|---|---|
| si2209093.txt | Si(220) | 90° | yes |
| si220093.txt | Si(220) | 0° | yes |
| si1119043.txt | Si(111) | 90° | no |
| si111043.txt | Si(111) | 0° | no |
