# Algorithm Deep Dive: AI & Machine Learning on Real Map Data

This document provides the technical details of the algorithms used in the "Perfect Pathway" project. It explains how we leverage **real-world OpenStreetMap (OSM) data** to power our AI agents.

## 1. Pathfinding: A\* (A-Star) Search

The "Army" and "Volunteer" agents use the A* algorithm to find optimal paths. Unlike a standard GPS that searches for the *shortest* distance, our agents search for the *safest* or *most efficient\* path based on their role.

### The Core Equation

A\* selects the next node to visit by minimizing the function:
$$f(n) = g(n) + h(n)$$

- **$g(n)$ (Actual Cost)**: The cost to reach node $n$ from the start.
- **$h(n)$ (Heuristic)**: The estimated cost from node $n$ to the goal.

### Custom Cost Function: $g(n)$

We don't just use distance. We modify the edge weight based on the predicted **Risk Level** of the real-world road segment.

$$Cost_{edge} = \text{Length}_{meters} \times (1 + \alpha \times \text{RiskProbability})$$

- **$\text{Length}_{meters}$**: The actual physical length of the road segment (from OSM data).
- **$\text{RiskProbability}$**: A value between 0.0 and 1.0 predicted by our ML model (see below).
- **$\alpha$ (Risk Factor)**: A multiplier defined by the role.
  - **Army**: $\alpha = 100$ (Extremely risk-averse).
  - **Volunteer**: $\alpha = 5$ (Balanced).

### Heuristic: $h(n)$

We use the **Haversine Distance** (Great-circle distance) between the current node and the goal node. This provides an admissible heuristic that works effectively on the curved surface of the Earth.

---

## 2. Machine Learning: Risk Prediction (Logistic Regression)

The "Scout" component of our system uses Machine Learning to predict the safety of a road segment. Instead of random values, we use **attributes from the real-world map** as features.

### The Model

We use a **Logistic Regression** classifier. It outputs a probability $P(Y=1|X)$ that a specific edge is "Dangerous".

### Feature Engineering (Inputs from OSM)

For every edge in the downloaded graph, we extract the following real-world tags to create our feature vector $X$:

1.  **Highway Type** (`highway`):
    - _Primary/Trunk_: Often wider but potentially more monitored or crowded.
    - _Residential_: Quieter, narrow.
    - _Service/Alley_: potentially higher blockage risk.
    - _One-hot encoded_ for the model.
2.  **Physical Properties**:
    - `lanes`: Number of lanes (e.g., 2, 4).
    - `maxspeed`: Speed limit (e.g., 40, 60 km/h).
    - `length`: Length of the segment.
3.  **Proximity Features** (Calculated):
    - `distance_to_poi`: Distance to nearest Hospital/Police Station.
    - `is_bridge`: Boolean (from `bridge` tag).
    - `is_tunnel`: Boolean (from `tunnel` tag).

### Prediction

$$P(\text{Danger}) = \frac{1}{1 + e^{-(\beta_0 + \beta_1 X_1 + ... + \beta_n X_n)}}$$

This probability is dynamically assigned to the graph edges and fed into the Pathfinding algorithm described above.

---

## 3. Reinforcement Learning: Q-Learning (The Rescuer)

The "Rescuer" agent uses Reinforcement Learning to learn routes in unknown or changing environments.

### The Problem

The agent does not know the full cost map initially. It must explore to find the quickest route to a victim while avoiding hidden dangers.

### Components

- **State ($s$)**: The current Node ID in the OSM graph.
- **Action ($a$)**: Choose a neighbor Node ID to move to.
- **Q-Table**: A lookup table storing the value of taking action $a$ in state $s$.

### Reward Structure ($R$)

- **+100**: Successfully reaching the Goal Node.
- **-1**: Per step (Penalty to encourage speed).
- **-50**: Entering an edge classified as "High Risk" by the ML model.

### Update Rule (Bellman Equation)

$$Q(s, a) \leftarrow Q(s, a) + \alpha [R + \gamma \max_{a'} Q(s', a') - Q(s, a)]$$

Over hundreds of simulated episodes (run via the "Train" button in the UI), the agent learns a policy $\pi(s)$ that maps every intersection in the city to the optimal turn to take.
