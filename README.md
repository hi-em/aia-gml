# Spatial Syntax of the Salt Police Station
**Computational Graph Analysis using TopologicPy**
MACAD 2026 · Module 03: Graph Machine Learning · Assignment 01

---

## Overview

This project translates the Police Station in Salt, Jordan into a series of mathematical graphs using `topologicpy`. The goal is to move beyond standard 3D modeling and make the building's spatial logic computable — encoding security hierarchy, physical access, and visual control as graph structures that can be queried and analyzed.

Three graphs are produced, each answering a distinct spatial question:
1. **Primal Graph** — which rooms are geometrically adjacent?
2. **Movement Graph** — which rooms can physically reach each other?
3. **Visual Graph** — which rooms have a line of sight to each other?

---

## Case Study: Why a Police Station?

A police station is an extreme case of **designed spatial control**. Its floor plan is not arbitrary — it is a security protocol encoded in architecture. The building deliberately separates three user groups (public, staff, detainees) whose paths must never accidentally intersect. Visual control is weaponized: officers need to survey multiple zones without physically occupying every room. Access is rationed through apertures: every door is a checkpoint.

This makes it an ideal subject for graph analysis. The gap between geometric adjacency (primal) and actual access (movement graph) is precisely where the security design lives. The visual graph then tests whether the surveillance logic holds up computationally.

---

## Project Structure

```
assets/
├── ROOMS-GEO.obj        # Extruded room volumes from Rhino
├── DOORS-GEO.obj        # Solid door apertures
├── GLASS-DOORS-GEO.obj  # Glass door apertures
└── WINDOWS-GEO.obj      # Window apertures

gml-assign-01.ipynb      # Main analysis notebook
README.md
```

---

## Requirements

```
topologicpy >= 0.9.18
```

Run in VS Code, Jupyter, or Google Colab. Set the renderer at the top of the notebook:

```python
renderer = "vscode"   # or "colab" / "browser"
```

---

## Spatial Classification

Each room is classified by keyword match on its Rhino object name. Classification controls node color across all graphs.

| Category | Keyword Match | Color | Description |
|---|---|---|---|
| `public` | `lobby`, `public`, `security` | Green gradient | Entry and publicly accessible spaces |
| `circulation` | `circulation`, `vertical` | Red (flat) | Corridors, stairwells, the operational spine |
| `cell` | `cell` | Black (flat) | Detainee holding spaces |
| `private` | *(fallback)* | Yellow gradient | Staff offices, administrative areas |

The gradient within `public` and `private` categories is computed with a linear interpolation (`lerp_color`) across the number of rooms in that category, giving each room a unique shade while keeping the zone visually coherent.

**To change node size for rooms:** edit `SIZE_ROOM` in Cell 02.
**To change node size for apertures:** edit `SIZE_DOOR`, `SIZE_GLASS_DOOR`, `SIZE_WINDOW` in Cell 07.

---

## Code Walkthrough

### Cell 01 — Load Geometry
```python
objects = Topology.ByOBJPath("ROOMS-GEO.obj")
```
Imports the OBJ as a list of `Cluster` topology objects. Each object carries a dictionary with its Rhino layer-based `name`.

---

### Cell 02 — Classify & Color Rooms
Two-pass loop:
- **Pass 1**: classify each room by name keyword, collect into `room_data`
- **Pass 2**: assign color (gradient or flat) and `vertex_size`, build `cells` and `selectors` lists

The two-pass approach is necessary because gradient coloring requires knowing the total count per category before assigning individual values.

```python
Cell.ByFaces(faces)                  # builds a closed solid from the OBJ faces
Topology.RemoveCollinearEdges(c)     # cleans up redundant vertices
Topology.InternalVertex(c)           # places selector point guaranteed inside the volume
Dictionary.SetValuesAtKeys(...)      # attaches color and vertex_size to the selector
```

---

### Cell 03 — Build CellComplex
```python
house = CellComplex.ByCells(cells)
house = Topology.TransferDictionariesBySelectors(house, selectors, tranCells=True)
```
`CellComplex.ByCells` merges all room solids into a single topology where shared faces are detected automatically. `TransferDictionariesBySelectors` pushes the color/size dictionaries from the selector points onto the correct cells using spatial containment — this is what makes node colors survive into the graph.

---

### Cell 05 — Primal Graph
```python
g = Graph.ByTopology(house, useInternalVertex=True)
```

| Parameter | Value | Effect |
|---|---|---|
| `useInternalVertex` | `True` | Node placed inside the volume (not at centroid, which can fall outside non-convex shapes) |

Default behavior connects any two cells sharing a face — regardless of apertures. This is geometric adjacency only.

**Node size** is set to degree normalized to a fixed range (10–30):
```python
degrees = [Graph.VertexDegree(g, v) for v in verts]
size = 10 + (degree - min_deg) / max(max_deg - min_deg, 1) * 20
```
More connected rooms appear larger. This makes the circulation spine visually dominant and peripheral cells visually recessive.

---

### Cell 07 — Load Apertures
Three aperture types are loaded as separate lists so they can be combined selectively:

```python
doors        → DOORS-GEO.obj        # burgundy (#800020)
glass_doors  → GLASS-DOORS-GEO.obj  # cyan
windows      → WINDOWS-GEO.obj      # dark blue
```

Each aperture face gets a `type`, `color`, and `vertex_size` dictionary entry. Aperture nodes are intentionally smaller than room nodes to maintain visual hierarchy.

---

### Cell 08 — Build Two House Models
```python
house_movement = Topology.AddApertures(house, doors + glass_doors, subTopologyType="face")
house_visual   = Topology.AddApertures(house, glass_doors + windows, subTopologyType="face")
```
Two versions of the same building, each loaded with only the apertures relevant to that analysis. `subTopologyType="face"` attaches apertures to the faces (walls) they belong to, which is what `Graph.ByTopology` uses to detect connections.

---

### Cell 09 — Movement Graph
```python
g_movement = Graph.ByTopology(house_movement,
    direct=False,
    viaSharedApertures=True,
    toExteriorApertures=False)
```

| Parameter | Value | Effect |
|---|---|---|
| `direct` | `False` | Rooms sharing only a wall get **no edge** — adjacency alone is not access |
| `viaSharedApertures` | `True` | Edges form only where an aperture (door/glass door) sits on the shared face |
| `toExteriorApertures` | `False` | No exterior connections — movement is internal only |

The aperture face itself becomes a node in the graph, sitting between the two rooms it connects. This makes doors and glass doors first-class spatial entities in the graph, not just edge weights.

---

### Cell 11 — Visual Graph
```python
g_visual = Graph.ByTopology(house_visual,
    direct=False,
    viaSharedApertures=True,
    toExteriorApertures=True)
```

| Parameter | Value | Effect |
|---|---|---|
| `toExteriorApertures` | `True` | Windows also connect rooms to an exterior node — reveals surveillance reach to outside |

Glass doors appear in both graphs: they allow passage (movement graph) and sight (visual graph). Windows appear only in the visual graph.

---

## Node & Edge Reference

| Node type | Color | Size | Appears in |
|---|---|---|---|
| Public room | Green gradient | `SIZE_ROOM` | All graphs |
| Circulation room | Red | `SIZE_ROOM` | All graphs |
| Private room | Yellow gradient | `SIZE_ROOM` | All graphs |
| Cell room | Black | `SIZE_ROOM` | All graphs |
| Solid door | Burgundy `#800020` | `SIZE_DOOR` | Movement graph |
| Glass door | Cyan | `SIZE_GLASS_DOOR` | Movement + Visual graphs |
| Window | Dark blue | `SIZE_WINDOW` | Visual graph |

**Default sizes:** `SIZE_ROOM = 35` · `SIZE_DOOR = SIZE_GLASS_DOOR = SIZE_WINDOW = 10`

---

## Future Analyses

| # | Name | Method | Question |
|---|---|---|---|
| 05 | Escape Distance | `Graph.ShortestPath` | How many doors between each cell and an exit? |
| 06 | Betweenness Centrality | Graph centrality algorithms | Which spaces are mandatory chokepoints? |
| 07 | Visibility Reach | N-hop traversal on visual graph | Where are the optimal guard positions? |
| 08 | Zone Permeability | Cross-zone edge count | How many boundary violations exist? |
| 09 | Geometry vs. Access Delta | Primal minus movement graph | Where are the intentional barriers? |

---

## Key TopologicPy Concepts Used

| Concept | TopologicPy class | Role |
|---|---|---|
| Closed solid | `Cell` | Represents one room |
| Multi-room topology | `CellComplex` | Detects shared faces automatically |
| Point inside solid | `Topology.InternalVertex` | Correct node placement |
| Metadata on topology | `Dictionary` | Stores color, size, type, category |
| Graph from topology | `Graph.ByTopology` | Core graph construction |
| Aperture attachment | `Topology.AddApertures` | Links doors/windows to wall faces |
| Node connectivity count | `Graph.VertexDegree` | Drives degree-based node sizing |
