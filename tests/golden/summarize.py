"""Print the displayed v3 results of golden files as a table, for review.

    python tests/golden/summarize.py [golden_dir] [--fields textbox6 textboxP11 ...]

Values are v3's displayed text (computed, not measured), from each case's final snapshot.
Runs in any Python 3.9+, no dependencies.
"""
import argparse
import json
from pathlib import Path

DEFAULT_FIELDS = {
    "textbox1": "formula", "textbox3": "AL", "textbox4": "area", "textbox5": "mass_mg",
    "textbox6": "step", "textbox7": "sample_mg", "textbox8": "diluent_mg", "textbox9": "E0",
    "textbox_Xray_05": "diagnostic", "textbox_dil05": "dil_diag",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("golden_dir", nargs="?", type=Path, default=Path(__file__).parent / "v3")
    parser.add_argument("--fields", nargs="*", help="main-window widget names to show")
    args = parser.parse_args()
    fields = {f: f for f in args.fields} if args.fields else DEFAULT_FIELDS

    for path in sorted(args.golden_dir.glob("*.json")):
        if path.name == "manifest.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        final = data["snapshots"][-1]
        widgets = final["main_window"]
        parts = []
        for name, label in fields.items():
            text = widgets.get(name, {}).get("text", "")
            if text:
                parts.append(f"{label}={text}")
        if widgets.get("textbox6", {}).get("style", "").endswith("(255,0,0)"):
            parts.append("STEP-RED")
        builder = final.get("sample_builder", {})
        for name in ("textbox_tab106", "textbox_tab2_06"):
            if builder.get(name, {}).get("text"):
                parts.append(f"builder_diag={builder[name]['text']}")
        if final["figures"]:
            parts.append(f"figures={len(final['figures'])}")
        if data["exceptions"]:
            e = data["exceptions"][0]
            parts.append(f"EXCEPTION={e['type']}: {e['message']} @ {e['frames'][-1]}")
        print(f"{data['case']['id']:40s} " + " | ".join(parts))


if __name__ == "__main__":
    main()
