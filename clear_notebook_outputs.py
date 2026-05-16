"""
Clears all stored cell outputs from si-centrality.ipynb so VS Code
can open it without freezing. The code is untouched — only the
cached visualizations and print outputs are removed.

Run from the aia-gml folder:
    python clear_notebook_outputs.py
"""

import json
import os

NOTEBOOKS = [
    r"phase-02-spatial-analysis\notebooks\si-centrality.ipynb",
    r"phase-02-spatial-analysis\notebooks\si-community.ipynb",
    r"phase-02-spatial-analysis\notebooks\si-isovist.ipynb",
    r"phase-02-spatial-analysis\notebooks\obj-to-brep.ipynb",
    r"phase-01-graph-generation\notebooks\graph-gen.ipynb",
]

base = os.path.dirname(os.path.abspath(__file__))

for rel_path in NOTEBOOKS:
    path = os.path.join(base, rel_path)
    if not os.path.exists(path):
        print(f"  skipped (not found): {rel_path}")
        continue

    before_kb = os.path.getsize(path) // 1024

    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb.get("cells", []):
        cell["outputs"] = []
        cell["execution_count"] = None

    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    after_kb = os.path.getsize(path) // 1024
    print(f"✓ {os.path.basename(rel_path):40s}  {before_kb:>6} KB  →  {after_kb:>5} KB")

print("\nDone. Re-run cells in VS Code to regenerate outputs.")
