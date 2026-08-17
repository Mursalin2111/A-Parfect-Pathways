# Under the Hood: The "Generate Random Mission" Button

This document explains the technical workflow that triggers when you click the **"Generate Random Mission"** button in the application.

## 1. The Trigger (User Action)

**File**: `app.py`
When you click the button, Streamlit executes the code block inside `if st.button("🎲 Generate Random Mission"):`.

## 2. Target Selection (Randomization)

**File**: `app.py`
The system needs to define a "Mission" (Start A -> End B).

- It accesses the list of all nodes in the downloaded graph: `G.nodes()`.
- It randomly picks two distinct nodes:
  ```python
  start_node = random.choice(nodes)
  end_node = random.choice(nodes)
  ```

## 3. The "Brain" (AI Pathfinding)

**File**: `src/ai/pathfinding.py`
The app calls the `find_path_astar` function:
`find_path_astar(G, start_node, end_node, weight_mode='safe')`

### What happens inside?

1.  **A\* Algorithm Starts**: It explores neighbors starting from `start_node`.
2.  **Cost Calculation**: For every road segment (edge), it calculates a "Cost":
    - It reads the **Real Distance** (in meters).
    - It reads the **Risk Level** (predicted by our ML model, stored in the graph).
    - **Formula**: `Cost = Distance * (1 + 100 * Risk)`
    - _Result_: Usage of risky roads becomes "expensive", so the AI tries to find a way around them.
3.  **Optimization**: The algorithm finds the sequence of nodes that has the lowest Total Cost.
4.  **Geometry Extraction**: It converts the abstract Node IDs back into a list of GPS coordinates (Latitude, Longitude) that follow the actual curves of the streets.

## 4. The "Eyes" (Reverse Geocoding)

**File**: `app.py`
Once the path coordinates are returned, the app needs to know "Where is this?".

- It takes the **Start Coordinate** and **End Coordinate**.
- It uses `osmnx.geocode_to_gdf` to query the OpenStreetMap database.
- It retrieves the nearest address or place name (e.g., "Main Street", "Dhaka Medical College").
- These names are assigned to the Green and Red markers.

## 5. Visualization (Rendering)

**File**: `app.py` -> `folium`
Finally, the app updates the Map:

- **PolyLine**: Draws the path as a thick red line using the geometry from Step 3.
- **Markers**: Places pins at Start and End with the named labels from Step 4.
- **Display**: The updated map object is sent to the browser via `st_folium`.

---

**Summary Flow**:
`Click` -> `Random Nodes` -> `AI Calculates Safe Path + Geometry` -> `Reverse Geocode Names` -> `Draw Map`
