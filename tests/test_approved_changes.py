"""Independent checks of each approved change (tests/approved_changes.py).

A change is accepted only if its new values agree with a calculation that does not go through
catmass.physics (Software Standard 4), or, for changes that must not move any number, if the
result is shown to be identical to v3's behavior.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

V3_REGISTRATION = """
import xraydb
xraydb.add_material('PEEK', 'C19H14O3', 1.32, categories=['polymer'])
xraydb.add_material('Glossy Carbon', 'C', 1.5, categories=['polymer'])
xraydb.add_material('Kanthal A-1', 'Cr1.83AlFe6.139', 7.1, categories=['polymer'])
xraydb.add_material('Nichrome', 'CrNi3.544', 8.4, categories=['polymer'])
xraydb.add_material('Carbon Fiber', 'C3HN', 1.184, categories=['polymer'])
"""

DUMP = """
import json, xraydb
table = [[k, m.formula, m.density, m.name, m.categories]
         for k, m in xraydb.get_materials().items()]
mu = {k: [xraydb.material_mu(k, e) for e in (5000.0, 8000.0, 20000.0)]
      for k in ('peek', 'glossy carbon', 'kanthal a-1', 'nichrome', 'carbon fiber')}
print(json.dumps({'table': table, 'mu': mu}))
"""


def run_isolated(registration, user_file):
    """Run in a fresh process with xraydb's user materials file redirected to user_file."""
    redirect = ("import xraydb.materials as m\n"
                f"m.get_user_materialsfile = lambda create_folder=False: {str(user_file)!r}\n")
    proc = subprocess.run([sys.executable, "-c", redirect + registration + DUMP], cwd=REPO,
                          capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def test_F11_in_memory_materials_identical_to_v3(tmp_path):
    for existing in (False, True):  # fresh machine, and a machine v3 has already run on
        v3_file, new_file = tmp_path / f"v3_{existing}.dat", tmp_path / f"new_{existing}.dat"
        if existing:
            seed = "".join(f" {n} | {d} | polymer | {f}\n" for n, f, d in [
                ("PEEK", "C19H14O3", 1.32), ("Glossy Carbon", "C", 1.5),
                ("Kanthal A-1", "Cr1.83AlFe6.139", 7.1), ("Nichrome", "CrNi3.544", 8.4),
                ("Carbon Fiber", "C3HN", 1.184)])
            v3_file.write_text(seed)
            new_file.write_text(seed)
        before = new_file.read_bytes() if existing else None
        v3 = run_isolated(V3_REGISTRATION, v3_file)
        new = run_isolated("import catmass.physics\n", new_file)
        assert new == v3, f"materials differ from v3 (existing user file: {existing})"
        assert v3_file.exists(), "redirect check: v3's add_material should have written"
        if existing:
            assert new_file.read_bytes() == before, "catmass.physics modified the user file"
        else:
            assert not new_file.exists(), "catmass.physics created a user materials file"
