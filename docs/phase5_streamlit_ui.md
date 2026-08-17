# Phase 5: Advanced Interaction & Analytics

## **Objective**

Enhance the existing data-driven Streamlit dashboard (`app.py`) to support advanced user interactions, location searching, and dynamic simulations.

## **Key Features**

### 1. **Sidebar Enhancements**

- **Location Search**: Allow users to input a city name (e.g., "Dhaka") -> Geocode -> Download map for that area automatically.
- **Role Selector**: "Army", "Rescuer", "Volunteer", "Compare All".
- **Parameters**: Sliders for "Risk Tolerance", "Number of Training Episodes".

### 2. **Main Map Display**

- **Library**: `streamlit-folium`.
- **Visualization Specs**:
  - **Real Street Paths**: Ensure all lines drawn follow the actual road curvature from OSM data (geometry).
  - **Animation**: Use `folium.plugins.AntPath` for smooth flow visualization of paths.
  - **Custom Markers**: Use `folium.Icon` with custom prefixes (fa/glyphicon) for entities (e.g., Shield for Army).
  - **Overlays**: Toggleable layers for Risk Heatmap and Administrative Boundaries.

### 3. **Data & Metrics**

- **Charts**: Bar charts comparing Time vs. Risk for the selected path.
- **Text**: Explanation of _why_ the AI chose this path.

## **Implementation Steps**

1.  **Search Feature**: Update `app.py` to use `ox.geocode` for text-based location searching.
2.  **Path Rendering**: Modify `visualizer.py` to accept lists of coordinates (geometry) and render using `AntPath`.
3.  **Entity Icons**: Add support for passing icon classes to the visualizer.
4.  **Refinement**: Add "Train Model" button to trigger the ML/RL training loops in real-time.

## **Deliverables**

- A fully functional `app.py` with Search and Simulation capabilities.
- Live animation of agent movement on real street paths.
- Visual proof of different paths for different roles with distinct markers.
