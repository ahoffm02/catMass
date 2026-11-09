"""Generate golden files from the unchanged catMass v3 reference (parity-rebuild Stage 3).

Run in the reference environment `catmass-v3-ref` (Python 3.9, xraylib 4.1.1, xraydb 4.5.4,
matplotlib 3.5.2), from anywhere:

    python tests/golden/generate_golden.py                 # all cases -> tests/golden/v3/
    python tests/golden/generate_golden.py --cases H-empty --out-dir some/dir

Each case runs in its own process: a fresh launch of the v3 GUI (Qt offscreen), driven through its
own widgets exactly as a user would (typing fires textEdited, buttons are clicked, combos picked).
The reference file is executed unchanged; nothing in it is patched except what is listed here.

What the generator adds around v3 (none of it changes a number):
- Pass-through tracing of v3's physics functions and of xraydb.material_mu / xray_lines. Calls
  made directly from GUI code are recorded with their raw inputs and outputs; calls nested inside
  other traced calls are not. XASPLOTTER and kspacecalc (thousands of calls per plot) are counted
  only; their values are in the recorded plot data.
- sys.excepthook records exceptions raised in GUI slots and lets the run continue. The real exe
  (default hook) would terminate at that point; the golden file marks where.
- Assumption (HC16, unconfirmed but low risk): network access is disabled (see disable_network).
  v3's launch-time version check then fails into its own `except: pass`, which only affects the
  "new version available" label, not any calculation.
- Assumption (HC16): the numpy BLAS backend does not affect any recorded number. v3's physics uses
  only elementwise numpy operations; matplotlib uses BLAS for screen transforms, and plot data is
  recorded untransformed. (The env was moved from MKL to OpenBLAS on 2026-11-08 because MKL
  2026.1 crashed every matrix product.)
- Assumption (HC16): the working directory is legacy/, so v3 finds its glitch files and images
  exactly as the exe did next to its executable.

Each output file holds the case definition, the environment, every widget state at each snapshot,
the module-level state, all plot data, the traced physics calls, and any exceptions. No timestamps
inside case files, so a re-run must reproduce them byte for byte; the run date is in manifest.json.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LEGACY = REPO / "legacy"
REFERENCE = LEGACY / "catMass_2023v3_singlefile_EXE-REFERENCE.py"
GLITCH_FILES = ["si2209093.txt", "si220093.txt", "si1119043.txt", "si111043.txt"]
DEFAULT_OUT = HERE / "v3"
SCHEMA = "catmass-golden/1"
GENERATOR_VERSION = "1"

# Reference build environment recovered from the v3 exe (vault plan, 2026-11-07). Generation is
# refused on anything else, so a golden file can never come from the wrong backend versions.
REQUIRED = {"python": "3.9", "xraylib": "4.1.1", "xraydb": "4.5.4", "matplotlib": "3.5.2"}

sys.path.insert(0, str(HERE))
from cases import CASES, CASES_BY_ID  # noqa: E402


# --------------------------------------------------------------------------------------------
# JSON helpers
# --------------------------------------------------------------------------------------------
def jsonable(o):
    """Convert numpy/Qt/namedtuple values to JSON types without rounding any float."""
    import numpy as np
    if o is None or isinstance(o, (bool, str)):
        return str(o) if isinstance(o, np.str_) else o
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        f = float(o)
        if math.isnan(f):
            return "NaN"
        if math.isinf(f):
            return "Infinity" if f > 0 else "-Infinity"
        return f  # json writes repr(float): shortest string that round-trips exactly
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if hasattr(o, "_asdict"):
        return {k: jsonable(v) for k, v in o._asdict().items()}
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return {"__repr__": repr(o), "__type__": type(o).__name__}


def dumps(o, indent=0):
    """Pretty JSON, but lists of scalars stay on one line (plot arrays would be 1000s of lines)."""
    pad, pad1 = " " * indent, " " * (indent + 1)
    if isinstance(o, dict):
        if not o:
            return "{}"
        items = [f"{pad1}{json.dumps(k, ensure_ascii=False)}: {dumps(v, indent + 1)}"
                 for k, v in o.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(o, list):
        if all(not isinstance(v, (dict, list)) for v in o):
            return json.dumps(o, ensure_ascii=False)
        return "[\n" + ",\n".join(pad1 + dumps(v, indent + 1) for v in o) + "\n" + pad + "]"
    return json.dumps(o, ensure_ascii=False)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # LF on every OS
        f.write(dumps(obj) + "\n")


# --------------------------------------------------------------------------------------------
# Worker: one case, one fresh process
# --------------------------------------------------------------------------------------------
class Tracer:
    def __init__(self):
        self.calls, self.counts, self.depth = [], {}, 0

    def wrap(self, owner, name, record=True):
        original = getattr(owner, name)

        def traced(*args, **kwargs):
            top = self.depth == 0
            self.depth += 1
            try:
                result = original(*args, **kwargs)
            except Exception as exc:
                if top and record:
                    self.calls.append({"fn": name, "args": jsonable(args),
                                       "kwargs": jsonable(kwargs),
                                       "raised": f"{type(exc).__name__}: {exc}"})
                raise
            finally:
                self.depth -= 1
            if top:
                if record:
                    self.calls.append({"fn": name, "args": jsonable(args),
                                       "kwargs": jsonable(kwargs), "result": jsonable(result)})
                else:
                    self.counts[name] = self.counts.get(name, 0) + 1
            return result

        setattr(owner, name, traced)


def environment(v3):
    import matplotlib
    import numpy
    import xraydb
    import xraylib
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QDesktopWidget
    geom = QDesktopWidget().availableGeometry(0)
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "xraylib": xraylib.__version__,
        "xraydb": xraydb.__version__,
        "xraydb_database": xraydb.get_xraydb().get_version(),
        "xraydb_sqlite_sha256": sha256(Path(xraydb.__file__).parent / "xraydb.sqlite"),
        "numpy": numpy.__version__,
        "matplotlib": matplotlib.__version__,
        "matplotlib_backend": matplotlib.get_backend(),
        "qt": QtCore.QT_VERSION_STR,
        "pyqt": QtCore.PYQT_VERSION_STR,
        "qt_platform": os.environ.get("QT_QPA_PLATFORM"),
        "screen_available": [geom.width(), geom.height()],  # sets v3's widget/font sizes only
    }


def widget_states(owner):
    from PyQt5.QtWidgets import (QAbstractButton, QComboBox, QLabel, QLineEdit, QPushButton,
                                 QSlider)
    out = {}
    for name, w in sorted(vars(owner).items()):
        if isinstance(w, QLineEdit):
            out[name] = {"text": w.text(), "style": w.styleSheet(), "hidden": w.isHidden(),
                         "enabled": w.isEnabled(), "readonly": w.isReadOnly()}
        elif isinstance(w, QComboBox):
            out[name] = {"index": w.currentIndex(), "text": w.currentText(),
                         "hidden": w.isHidden(), "enabled": w.isEnabled()}
        elif isinstance(w, QAbstractButton) and not isinstance(w, QPushButton):
            out[name] = {"checked": w.isChecked(), "text": w.text(), "hidden": w.isHidden(),
                         "enabled": w.isEnabled()}
        elif isinstance(w, QSlider):
            out[name] = {"value": w.value(), "hidden": w.isHidden()}
        elif isinstance(w, QLabel) and w.pixmap() is None:
            out[name] = {"text": w.text(), "hidden": w.isHidden()}
    return out


def figure_data():
    import matplotlib.pyplot as plt
    from matplotlib.text import Annotation
    figures = []
    for num in plt.get_fignums():
        fig = plt.figure(num)
        axes = []
        for ax in fig.axes:
            legend = ax.get_legend()
            axes.append({
                "xlabel": ax.get_xlabel(), "ylabel": ax.get_ylabel(),
                "xlim": jsonable(ax.get_xlim()), "ylim": jsonable(ax.get_ylim()),
                "lines": [{"label": ln.get_label(), "visible": ln.get_visible(),
                           "marker": str(ln.get_marker()), "linestyle": ln.get_linestyle(),
                           "x": jsonable(ln.get_xdata(orig=True)),
                           "y": jsonable(ln.get_ydata(orig=True))} for ln in ax.lines],
                "collections": [{"type": type(c).__name__, "label": c.get_label(),
                                 "paths": [jsonable(p.vertices) for p in c.get_paths()]}
                                for c in ax.collections],
                "texts": [{"kind": "annotation", "text": t.get_text(), "xy": jsonable(t.xy)}
                          if isinstance(t, Annotation) else
                          {"kind": "text", "text": t.get_text(),
                           "position": jsonable(t.get_position())} for t in ax.texts],
                "legend": None if legend is None else [t.get_text() for t in legend.get_texts()],
            })
        figures.append({"number": num, "axes": axes})
    return figures


def disable_network():
    """Refuse every outgoing connection from this process.

    Two callers would otherwise reach the internet: v3's launch-time version check, and xraylib
    4.1.1, which sends a Google Analytics "import" event from a background thread on every import.
    Both catch the failure themselves.
    """
    import socket

    def refuse(*args, **kwargs):
        raise OSError("network disabled during golden-file generation")
    socket.socket.connect = refuse
    socket.create_connection = refuse


def run_case(case_id, out_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.chdir(LEGACY)

    disable_network()
    exceptions = []

    def hook(exc_type, exc, tb):
        frames = [f"{Path(f.filename).name}:{f.lineno} in {f.name}"
                  for f in traceback.extract_tb(tb)]
        exceptions.append({"type": exc_type.__name__, "message": str(exc), "frames": frames})
    sys.excepthook = hook

    import importlib.util
    sys.argv = ["catmass-v3"]
    spec = importlib.util.spec_from_file_location("catmass_v3_reference", REFERENCE)
    v3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v3)  # creates the QApplication and registers v3's 5 custom materials

    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    import matplotlib.pyplot as plt

    tracer = Tracer()
    for name in ["XASMassCalc", "XASStoichCalc", "metalCalculateSample", "ComplexCalculateSample",
                 "XASEZero", "XASEZeroList", "unitconvert", "ionchamberdensity", "BeamTrans"]:
        tracer.wrap(v3, name)
    for name in ["XASPLOTTER", "kspacecalc"]:
        tracer.wrap(v3, name, record=False)
    for name in ["material_mu", "xray_lines"]:
        tracer.wrap(v3.xraydb, name)

    app = v3.app
    win = v3.XASCalcUI()
    win.show()
    app.processEvents()

    def builder():
        dialog = getattr(win, "dialog", None)
        if dialog is None or not hasattr(dialog, "table_widget"):
            raise RuntimeError("step needs the Sample Builder, but it is not open")
        return dialog, dialog.table_widget

    def usable(w, window):
        if not w.isEnabled() or not w.isVisibleTo(window):
            raise RuntimeError("widget is disabled or hidden; a user could not do this step")

    def type_into(w, text, window):
        usable(w, window)
        if w.isReadOnly():
            raise RuntimeError("line edit is read-only; a user could not type here")
        if w.text():
            w.selectAll()
            QTest.keyClick(w, Qt.Key_Backspace)
        if text:
            QTest.keyClicks(w, text)
        if w.text() != text:
            raise RuntimeError(f"typed {text!r} but the box holds {w.text()!r}")

    def snapshot(label):
        snap = {"label": label, "main_window": widget_states(win)}
        dialog = getattr(win, "dialog", None)
        if dialog is not None and hasattr(dialog, "table_widget"):
            snap["sample_builder"] = {"open": dialog.isVisible(),
                                      **widget_states(dialog.table_widget)}
        snap["module_state"] = jsonable({
            "angleconstants": v3.angleconstants, "calculateresult_num": v3.calculateresult_num,
            "samplesaver": v3.samplesaver, "complexsaver": v3.complexsaver})
        snap["figures"] = figure_data()
        snap["exceptions_so_far"] = len(exceptions)
        return snap

    def do_step(step, snapshots):
        op, args = step[0], step[1:]
        if op in ("type", "click", "select", "slider"):
            w = getattr(win, args[0])
            usable(w, win)
            if op == "type":
                type_into(w, args[1], win)
            elif op == "click":
                w.click()
            elif op == "select":
                idx = w.findText(args[1])
                if idx < 0:
                    raise RuntimeError(f"no entry {args[1]!r}")
                w.setCurrentIndex(idx)
            else:
                w.setValue(int(args[1]))
        elif op in ("dtype", "dclick", "dtab"):
            dialog, table = builder()
            if op == "dtab":
                table.tabs.setCurrentIndex(int(args[0]))
            elif op == "dtype":
                type_into(getattr(table, args[0]), args[1], dialog)
            else:
                w = getattr(table, args[0])
                usable(w, dialog)
                w.click()
        elif op == "snapshot":
            snapshots.append(snapshot(args[0]))
        else:
            raise RuntimeError("unknown step")

    case = CASES_BY_ID[case_id]
    snapshots = []
    for n, step in enumerate(case["steps"]):
        try:
            do_step(step, snapshots)
        except RuntimeError as exc:  # a case-definition error, never a v3 behavior
            raise RuntimeError(f"{case_id} step {n} {step!r}: {exc}") from None
        app.processEvents()
    snapshots.append(snapshot("final"))
    plt.close("all")

    result = {
        "schema": SCHEMA,
        "generator_version": GENERATOR_VERSION,
        "case": case,
        "reference": {"file": f"legacy/{REFERENCE.name}", "sha256": sha256(REFERENCE),
                      "glitch_files_sha256": {f: sha256(LEGACY / f) for f in GLITCH_FILES}},
        "environment": environment(v3),
        "value_kind": "computed (v3 reference calculation), not measured",
        "snapshots": snapshots,
        "physics_calls": tracer.calls,
        "call_counts": tracer.counts,
        "exceptions": exceptions,
        "v3_would_terminate": bool(exceptions),
    }
    write_json(out_path, result)



# --------------------------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------------------------
def check_environment():
    disable_network()
    import matplotlib
    import xraydb
    import xraylib
    found = {"python": platform.python_version(), "xraylib": xraylib.__version__,
             "xraydb": xraydb.__version__, "matplotlib": matplotlib.__version__}
    bad = {k: (v, REQUIRED[k]) for k, v in found.items() if not v.startswith(REQUIRED[k])}
    if bad:
        sys.exit(f"Refusing to generate: not the v3 reference environment {bad}. "
                 "Use the conda env catmass-v3-ref.")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cases", nargs="*", help="case ids (default: all)")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--jobs", type=int, default=4, help="cases run in parallel processes")
    parser.add_argument("--run-case", help=argparse.SUPPRESS)
    parser.add_argument("--out", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.run_case:
        run_case(args.run_case, args.out)
        return

    versions = check_environment()
    ids = args.cases or [c["id"] for c in CASES]
    unknown = [i for i in ids if i not in CASES_BY_ID]
    if unknown:
        sys.exit(f"unknown case ids: {unknown}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    def one(case_id):
        out = args.out_dir / f"{case_id}.json"
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                               "--run-case", case_id, "--out", str(out)],
                              capture_output=True, text=True, timeout=600)
        return case_id, proc.returncode, proc.stderr

    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for case_id, code, stderr in pool.map(one, ids):
            status = "ok" if code == 0 else f"FAILED ({code})"
            print(f"{status:12s} {case_id}", flush=True)
            if code != 0:
                failures.append({"id": case_id, "stderr": stderr[-4000:]})

    manifest = {
        "schema": SCHEMA, "generator_version": GENERATOR_VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reference_sha256": sha256(REFERENCE), "environment": versions,
        "cases": [{"id": c["id"], "group": c["group"]} for c in CASES if c["id"] in ids],
        "failures": [f["id"] for f in failures],
    }
    write_json(args.out_dir / "manifest.json", manifest)
    for f in failures:
        print(f"\n--- {f['id']} ---\n{f['stderr']}", file=sys.stderr)
    print(f"\n{len(ids) - len(failures)}/{len(ids)} cases written to {args.out_dir}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
