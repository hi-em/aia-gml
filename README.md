# AIA GML — Spatial Intelligence (Part 1)

MaCAD Module 03 exercise exploring **graph-based spatial intelligence** on architectural geometry using [topologicpy](https://topologicpy.com/).

## What the notebook does

[notebooks/aia-gml-01.ipynb](notebooks/aia-gml-01.ipynb) walks through turning a Rhino/Grasshopper model of a building into graph representations of its spaces:

1. **Import geometry** — loads `assets/rhino_geometry.obj` (exported from Rhino) and rebuilds it as a `CellComplex` where each cell represents a room.
2. **Visualize the building** — renders the cell complex in the notebook.
3. **Primal graph** — builds a graph from the raw vertices and edges of the geometry.
4. **Dual graph** — builds the *adjacency* graph where each node is a room and each edge is a shared wall between two rooms.
5. **Doors as apertures** — imports `assets/doors.obj`, attaches the door faces as apertures on the cell complex, and rebuilds the dual graph so edges only exist between rooms that are actually connected by a door (a circulation graph).

The output is a graph suitable for downstream graph-ML tasks on spatial/architectural data.

## Repo layout

- [notebooks/](notebooks/) — Jupyter notebook(s)
- [assets/](assets/) — source geometry
  - `rhino_geometry.3dm` — original Rhino model
  - `gh-graph-ml.gh` — Grasshopper definition used to export the OBJs
  - `rhino_geometry.obj` / `.mtl` — room/cell geometry consumed by the notebook
  - `doors.obj` — door faces used as apertures

## Requirements

- Python 3.10+
- `topologicpy` ≥ 0.9.18 (`pip install topologicpy`)
- Jupyter (VS Code, browser, or Colab — set `renderer` in the notebook accordingly)

## Running

```bash
pip install topologicpy jupyter
jupyter notebook notebooks/aia-gml-01.ipynb
```

The OBJ paths in the notebook are currently absolute — update them to your local path, or change them to relative paths (`../assets/rhino_geometry.obj`) before running.
