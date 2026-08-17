# Phase 3: Role-Based Logic

## **Objective**

Define distinct personalities/strategies for the different actors in the system. Each role will utilize the AI core (Phase 2) differently to achieve their specific goals.

## **Roles**

### 1. **The Army (Strategic & Cautious)**

- **Goal**: Move from A to B safely. Avoid conflict.
- **Configuration**:
  - Uses **A\*** with a massive penalty for high `RiskLevel`.
  - Uses the **ML Risk Model** to pre-validate edges. If an edge is predicted "Dangerous", it is treated as an obstacle (infinite cost).
- **Output**: A path that might be longer but steers clear of red zones.

### 2. **The Rescuer (Adaptive & Fast)**

- **Goal**: Reach victims quickly and rescue them.
- **Configuration**:
  - Uses **Q-Learning** (Reinforcement Learning).
  - It explores the map in episodes.
    - **Reward**: +100 for reaching goal, -10 per time step (encourages speed), -50 for hitting a danger zone.
  - Over time, it learns the "shortcuts" that are safe enough but fast.
- **Output**: An optimized route based on learned experience.

### 3. **The Volunteer (Balanced & Efficient)**

- **Goal**: Distribute resources to as many nodes as possible or reach a destination with minimal resource burn.
- **Configuration**:
  - Uses **A\*** with a balanced weight (Distance 50%, Risk 50%).
  - Constraints: Cannot traverse edges that require high resource consumption (e.g., fuel heavy "muddy roads").
- **Output**: A balanced "middle ground" path.

## **Implementation Steps**

1.  Create `src/roles/base_role.py` (Abstract class).
2.  Create `src/roles/army.py`, `src/roles/rescuer.py`, `src/roles/volunteer.py`.
3.  Implement the `decide_path(graph, start, end)` method for each.
    - Army calls `pathfinding.astar` with high risk weights.
    - Volunteer calls `pathfinding.astar` with balanced weights.
    - Rescuer will interface with the RL agent (Phase 4).

## **Deliverables**

- Python classes for each role.
- **Integration**: Roles will be selectable via the **Streamlit Sidebar** in `app.py`.
- **Visualization Specs**:
  - **Army**: Display with a `fa-shield` icon (FontAwesome) and Green path.
  - **Rescuer**: Display with a `fa-medkit` icon and Red/Orange animated path (`AntPath`).
  - **Volunteer**: Display with a `fa-hand-peace-o` icon and Blue path.
