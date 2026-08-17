# Phase 2: AI Core Implementation

## **Objective**

Develop the intelligent algorithms that will power the decision-making process. This includes the search algorithm for pathfinding and the Machine Learning model for risk assessment.

## **Key Components**

### 1. **Search Algorithm (Path Optimization)**

- **Algorithm**: A\* (A-Star) Search.
- **Why A\*?**: It is efficient and allows the use of **heuristics**.
- **Heuristic Function**:
  - $f(n) = g(n) + h(n)$
  - $g(n)$: actual cost from start to node $n$ (combination of distance + risk).
  - $h(n)$: estimated cost from $n$ to goal (Euclidean distance).
- **Custom Cost Function**:
  - The "cost" of an edge isn't just distance.
  - $Cost = Distance \times (1 + \alpha \times RiskLevel)$
  - By adjusting $\alpha$, we can make agents risk-averse or risk-tolerant.

### 2. **Machine Learning (Risk Prediction)**

- **Goal**: Predict if a specific path segment (edge) is "Safe" or "Dangerous" based on its features.
- **Model**: Logistic Regression (Simple, explainable, effectively binary classification).
- **Training Data**:
  - We will generate synthetic training data.
  - **Features**: `distance`, `enemy_probability`, `proximity_to_base`, `terrain_difficulty`.
  - **Label**: `0` (Safe) or `1` (Dangerous).
- **Workflow**:
  1.  Generate a CSV dataset of hypothetical edge stats.
  2.  Train the model using `scikit-learn`.
  3.  Save the model (`risk_model.pkl`).
  4.  At runtime, the "Army" agent uses this model to "scan" a path before taking it.

## **Implementation Steps**

1.  **Pathfinding**: Create `src/ai/pathfinding.py`.
    - Implement `find_path_astar(graph, start, end, weights)`.
2.  **Risk Model**: Create `src/ai/risk_model.py`.
    - Function `generate_training_data()`.
    - Function `train_model()`.
    - Function `predict_risk(edge_features)`.
3.  **Test**: Run a pathfinding test between two nodes and compare "Shortest Path" (Dijkstra/BFS) vs "Safest Path" (My A\*).

## **Deliverables**

- A working A\* pathfinder that respects risk weights and **returns full edge geometry** for visualization.
- A trained ML model that predicts edge safety.
- **Integration**: The pathfinding module will be called directly by `app.py`.
- **UI Requirements**:
  - `app.py` must provide inputs for Start/End node selection (or map clicks).
  - The returned path must be compatible with `folium.PolyLine` or `AntPath`.
