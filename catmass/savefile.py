"""catMass save files: JSON, file version 1 (decided 2026-11-08; no import of v3 files).

A file holds every input as typed (blank = default) and, separately, a read-only record of the
results shown when it was saved. Opening a file restores the inputs and recalculates; the record
is never read back. Unknown keys are ignored and missing keys take their defaults, so later
versions can add fields without breaking older files.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from datetime import datetime
from typing import Optional

from catmass import __version__
from catmass.calculator import (BeamPathInputs, BuilderInputs, Calculation, CalculatorInputs,
                                IonChamberInputs)

FILE_VERSION = 1
RESULTS_NOTE = ("Record only: what catMass showed when this file was saved. Not used when the "
                "file is opened; catMass recalculates from the inputs above.")


class SaveFileError(ValueError):
    """The file cannot be opened as a catMass save file; the message says why."""


@dataclass
class Session:
    calculator: CalculatorInputs = field(default_factory=CalculatorInputs)
    sample_builder: BuilderInputs = field(default_factory=BuilderInputs)
    beam_path: BeamPathInputs = field(default_factory=BeamPathInputs)
    ion_chamber: IonChamberInputs = field(default_factory=IonChamberInputs)


def dumps(session: Session, calc: Optional[Calculation] = None, beam: Optional[dict] = None,
          ion_chamber: Optional[str] = None, saved: Optional[str] = None) -> str:
    data = {'catmass_file_version': FILE_VERSION,
            'saved_with': f'catMass {__version__}',
            'saved': saved or datetime.now().isoformat(timespec='seconds')}
    data.update(asdict(session))
    if calc is not None:
        data['results_at_save'] = {
            'note': RESULTS_NOTE,
            'ok': calc.ok, 'error': calc.error, 'shown': calc.shown,
            'diagnostic': calc.diagnostic,
            'values_used': [asdict(u) for u in calc.values_used],
            'beam_path': beam, 'ion_chamber': ion_chamber,
        }
    return json.dumps(data, indent=2, ensure_ascii=False) + '\n'


def _fill(default, data, where):
    """A copy of the dataclass `default` with values from `data` (dict) where present."""
    if not isinstance(data, dict):
        raise SaveFileError(f"'{where}' should be a group of settings")
    values = {}
    for f in fields(default):
        current = getattr(default, f.name)
        if f.name not in data:
            values[f.name] = current
            continue
        value, here = data[f.name], f"{where}.{f.name}"
        if is_dataclass(current):
            values[f.name] = _fill(current, value, here)
        elif isinstance(current, bool):
            if not isinstance(value, bool):
                raise SaveFileError(f"'{here}' should be true or false")
            values[f.name] = value
        elif isinstance(current, dict):  # beam-path rows
            if not isinstance(value, dict):
                raise SaveFileError(f"'{here}' should be a group of settings")
            values[f.name] = {k: _fill(row, value.get(k, {}), f"{here}.{k}")
                              for k, row in current.items()}
        else:  # text field; numbers are accepted and kept as typed text
            if value is None:
                value = ''
            if not isinstance(value, (str, int, float)) or isinstance(value, bool):
                raise SaveFileError(f"'{here}' should be text or a number")
            values[f.name] = str(value)
    return type(default)(**values)


def loads(text: str) -> Session:
    """Inputs from a save file (the results record is ignored)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SaveFileError(f"Not a catMass save file (not valid JSON: {exc.msg}, "
                            f"line {exc.lineno})") from None
    if not isinstance(data, dict) or 'catmass_file_version' not in data:
        raise SaveFileError("Not a catMass save file (no 'catmass_file_version')")
    version = data['catmass_file_version']
    if not isinstance(version, int) or version < 1:
        raise SaveFileError(f"Unknown catMass file version {version!r}")
    if version > FILE_VERSION:
        raise SaveFileError(f"This file was saved by a newer catMass "
                            f"({data.get('saved_with', 'unknown version')}); please update")
    return _fill(Session(), {k: v for k, v in data.items() if k != 'results_at_save'}, 'file')
