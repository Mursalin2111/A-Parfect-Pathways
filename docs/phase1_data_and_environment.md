# Phase 1: Data Acquisition & Environment Modeling

## **Objective**

Build the foundation of the simulation by creating a realistic graph-based environment. We will use OpenStreetMap (OSM) data to represent the real world (e.g., roads, intersections) and enrich it with simulation attributes (risk, danger, resources).

## **Key Components**

### 1. **Map Data Fetching**

- **Library**: `osmnx`
- **Output**: A MultiDiGraph (Multi-directed graph) representing the street network.
- **Action**: Fetch the driveable street network for a specific location (e.g., "Dhaka, Bangladesh" or coordinates).

### 2. **Graph Conversion & Simplification**

- **Library**: `networkx`
- **Action**: Convert the complex OSM graph into a simplified NetworkX graph suitable for pathfinding.
- **Node Attributes**: `osmid`, `x` (longitude), `y` (latitude).
- **Edge Attributes**: `length` (distance).

### 3. **Attribute Enrichment (The "Simulation Layer")**

We need to add synthetic data to make the environment "alive" for the AI.

- **Risk Level**: assign a value (0.0 to 1.0) to each edge/node.
- **Enemy Probability**: Probability (0.0 to 1.0) of encountering hostility.
- **Population Density**: For rescue scenarios.
- **Traffic / Congestion**: Affects travel time.

### 4. **Data Persistence**

- **Action**: Save the processed graph to a file (e.g., `environment.pkl` or `.graphml`) so we don't need to re-download OSM data every time.

## **Implementation Steps**

1.  **Setup**: Install `osmnx`, `networkx`, `matplotlib`, `folium`.
2.  **Code**: Create `src/environment/map_manager.py`.
    - Function `download_graph(location)`
    - Function `enrich_graph(graph)` (adds random risk/enemy attributes)
    - Function `save_graph(graph, path)`
    - Function `load_graph(path)`
3.  **Test**: Write a script `tests/test_map_creation.py` to download a small area and inspect node/edge attributes.

## **Deliverables**

- A Python script that creates a `Graph` object with custom attributes.
- A saved graph file `data/processed_graph.pkl`.
- A simple map visualization (static .html or .png) showing the network.
- The map street data will be real data and the graph will be enriched with synthetic data.
- The path of the graph will be the real street network of the location and the visualization will be the real street network of the location.
