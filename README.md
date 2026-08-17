# 🗺️ Perfect Pathway: AI & Machine Learning-Assisted Path Optimization & Tactical Decision System

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.60%2B-FF4B4B.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML%20Engine-F7931E.svg)](https://scikit-learn.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20A*-000000.svg)](https://networkx.org/)
[![OSMnx](https://img.shields.io/badge/OSMnx-OpenStreetMap-green.svg)](https://osmnx.readthedocs.io/)

An intelligent simulation platform that combines **Geospatial Graph Theory**, **Multi-Algorithm Supervised Machine Learning**, **Unsupervised Spatial Clustering (DBSCAN)**, **Role-Based Heuristic Pathfinding (A\*)**, and **Large Language Models (Google Gemini)** to compute optimal routes under dynamic risk conditions.

---

## ❓ Why This Project Is Needed (Problem Statement & Purpose)

Standard navigation tools (like Google Maps or Waze) are built for everyday civilian driving. They prioritize **shortest distance** or **fastest travel time based on standard traffic flow**.

However, in **critical real-world scenarios**—such as military tactical movements, disaster rescue operations, and emergency supply distribution—traveling on the fastest or shortest road can be dangerous or disastrous:
- **High-Risk Zones & Checkpoints:** Main expressways may contain checkpoints, enemy positions, or severe hazard zones.
- **Environmental Volatility:** Heavy rain or fog alters road risk non-linearly depending on road type, bridges, and speed limits.
- **Diverse Strategic Objectives:**
  - An **Army Unit** must prioritize **maximum safety**, even if the route takes longer, avoiding hostile areas entirely.
  - An **Emergency Rescuer** must balance **speed vs. acceptable risk** to save lives quickly.
  - A **Humanitarian Volunteer** must optimize **fuel & supply cost efficiency**.

### 🎯 Core Purpose
**Perfect Pathway** solves this problem by providing a dynamic **AI Decision-Making Engine** that transforms raw OpenStreetMap street networks into intelligence-enriched graphs, predicting risk per road segment, discovering hazard clusters automatically, and calculating role-tailored optimal pathways.

---

## 🏗️ How It Works (System Architecture & Pipeline)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   OpenStreetMap Data (via OSMnx)                         │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                   NetworkX MultiDiGraph Construction                     │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
         ┌───────────────────────────┴──────────────────────────┐
         ▼                                                      ▼
┌──────────────────────────────────────┐     ┌─────────────────────────────┐
│ Supervised ML Risk Engine            │     │ Unsupervised DBSCAN         │
│ - Random Forest / Gradient Boosting  │     │ - Spatial Incident          │
│ - 8 Road & Environmental Features    │     │   Clustering                │
└──────────────────┬───────────────────┘     └──────────────┬──────────────┘
                   │                                        │
                   └───────────────────┬────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│               Graph Enrichment (Edge Risk & Resource Costs)              │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              Role-Based A* Pathfinding (Army/Rescuer/Volunteer)          │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
         ┌───────────────────────────┴──────────────────────────┐
         ▼                                                      ▼
┌──────────────────────────────────────┐     ┌─────────────────────────────┐
│ Interactive Streamlit Dashboard      │     │ LLM Mission Narrator        │
│ - Live Animated Folium Map           │     │ - Tactical Gemini           │
│ - ML Analytics & Feature Importance  │     │   Briefings                 │
└──────────────────────────────────────┘     └─────────────────────────────┘
```

### Operational Workflow:
1. **Map Download & Parsing:** Real street networks are extracted for any global latitude/longitude coordinate using `OSMnx` and converted into a `NetworkX MultiDiGraph`.
2. **ML Risk Prediction:** Each road segment's features are parsed and passed into a trained Machine Learning Classifier to compute a probabilistic danger score (0.0 to 1.0).
3. **Hazard Clustering:** Raw incident coordinates are processed using **DBSCAN** to dynamically form spatial danger zones.
4. **Graph Weight Enrichment:** Edge costs are updated dynamically based on predicted risk, environmental multipliers (weather/time of day), and resource consumption.
5. **Path Optimization:** The A\* algorithm calculates the optimal path according to the active role's strategic objective function.
6. **Visualization & Briefing:** The route is rendered on an interactive map with path animation, performance analytics, and AI-generated mission briefings.

---

## 🧠 Algorithms & Machine Learning Deep-Dive

### 1. Supervised Machine Learning (Road Segment Risk Assessment)
- **Algorithms Implemented:**
  - **Random Forest Classifier** (`RandomForestClassifier`, 100 estimators, max depth=8)
  - **Gradient Boosting Classifier** (`GradientBoostingClassifier`, learning rate=0.1)
  - **Logistic Regression** (`LogisticRegression`)
- **8 Feature Vector Evaluated:**
  1. `Highway Rank` (0=footway to 5=motorway)
  2. `Max Speed` (km/h)
  3. `Lanes` (number of lanes)
  4. `Segment Length` (meters)
  5. `Is Bridge` (1/0)
  6. `Is Tunnel` (1/0)
  7. `Weather Impact Multiplier` (1.0x - 1.6x)
  8. `Time of Day Multiplier` (1.0x - 1.4x)
- **Performance Evaluation:** Evaluates model quality on train-test splits producing real-time **Accuracy**, **Precision**, **Recall**, **F1-Score**, and **Feature Importance** rankings displayed directly in the UI.

### 2. Unsupervised Machine Learning (Automated Hazard Clustering)
- **Algorithm:** **DBSCAN** (*Density-Based Spatial Clustering of Applications with Noise*)
- **Distance Metric:** Haversine Great-Circle Geographic Distance.
- **Function:** Scans spatial incident coordinates around the operation area, identifies dense spatial clusters, calculates cluster centroids and bounding radii, and automatically generates dynamic **ML Danger Zones**.

### 3. Pathfinding & Graph Optimization
- **Algorithm:** **A\* (A-Star) Search Algorithm**
- **Heuristic Function:** Haversine distance from current node $n$ to target node $g$.
- **Role Objective Functions:**
  - 🛡️ **Army Role (Safety-First):**
    $$\text{Cost}(e) = \text{Length}(e) \times (1 + 100 \times \text{RiskLevel}(e))$$
    *Note: Enemy & Danger zones are set as completely impassable barriers.*
  - 🚑 **Rescuer Role (Balanced Speed & Safety):**
    $$\text{Cost}(e) = \text{Length}(e) \times (1 + 5 \times \text{RiskLevel}(e))$$
  - 📦 **Volunteer Role (Resource Efficiency):**
    $$\text{Cost}(e) = \text{Length}(e) \times (1 + \text{ResourceCost}(e))$$

### 4. Natural Language Processing & Mission Briefings
- **Technology:** Google Gemini API (`google-generativeai`) with template fallback.
- **Function:** Generates dynamic, context-aware tactical mission briefings in military, emergency response, or humanitarian tones based on route length, role, street names, and active danger zone counts.

---

## ✨ Features Summary

| Component | Technology / Algorithm | Function |
|---|---|---|
| **Geospatial Graph** | OSMnx, NetworkX | Real-world road network downloading & graph modeling |
| **Risk Classifier** | Random Forest / Gradient Boosting / Logistic Regression | Predicts segment risk score (0.0 - 1.0) based on 8 features |
| **Hazard Clustering** | DBSCAN (Haversine Distance) | Automated spatial incident discovery & danger zone formation |
| **Pathfinding** | A\* Algorithm (Haversine Heuristic) | Role-customized optimal path finding |
| **Role Decision Logic** | Custom Strategy Classes | Defines risk multipliers & impassable barrier rules |
| **Web Dashboard** | Streamlit | Control panel, ML analytics, metrics, & controls |
| **Map Rendering** | Folium & Leaflet.js | Static layers & real-time path marker animation |
| **AI Narrator** | Google Gemini API | Automated tactical mission briefing generation |

---

## 📁 Project Structure

```
A Perfect Pathway/
├── src/
│   ├── ai/
│   │   ├── risk_model.py          # Multi-Algorithm ML Risk Engine (RF, GB, Logistic)
│   │   ├── pathfinding.py         # Role-Weighted A* Search Algorithm
│   │   └── mission_narrator.py    # LLM (Gemini) Mission Briefing Generator
│   ├── environment/
│   │   ├── map_downloader.py      # OpenStreetMap (OSMnx) Network Extractor
│   │   ├── graph_enricher.py      # Feature Parser & Edge Risk Injector
│   │   └── danger_clusterer.py    # DBSCAN Unsupervised Spatial Hazard Clusterer
│   ├── roles/
│   │   ├── base_role.py           # Abstract Strategy Interface
│   │   ├── army.py                # Army Role (Safety-First & Barrier Blocking)
│   │   ├── rescuer.py             # Rescuer Role (Speed & Risk Balance)
│   │   └── volunteer.py           # Volunteer Role (Resource Efficiency)
│   └── utils/
│       └── visualizer.py          # Folium Map Renderer & Leaflet Animation Engine
├── config.py                      # Global settings & preset coordinates
├── app.py                         # Streamlit Interactive Web Application
└── requirements.txt               # Dependencies list
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Setup Virtual Environment
```bash
# Clone or navigate to the repository
cd A-Parfect-Pathways

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux / macOS (Bash/Zsh):
source .venv/bin/activate

# On Linux (Fish shell):
source .venv/bin/activate.fish

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Gemini API Key
For AI-generated mission briefings, create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 5. Launch the Web Application
```bash
streamlit run app.py
```
Or run directly via virtualenv binary:
```bash
./.venv/bin/streamlit run app.py
```

---

## 💡 How to Use the Application

1. **Configure Location & Environment:** Use the sidebar to set latitude/longitude center coordinates and search radius.
2. **Select ML Risk Model & Parameters:** Choose between **Random Forest**, **Gradient Boosting**, or **Logistic Regression**, and set weather and time of day multipliers.
3. **Choose Danger Detection Mode:** Toggle between **Dynamic ML Clusters (DBSCAN)** and **Preset Config Zones**.
4. **Select Role Strategy:** Choose **Army**, **Rescuer**, or **Volunteer**.
5. **Plan Mission:** Pick a Source Street and Destination Street, then click **Plan Mission** (or **Random**).
6. **Analyze & Animate:** View the path on the operational map, check the **ML Model Performance** panel, inspect the **Intel Feed**, enable **Path Animation**, and read the **Mission Briefing**.

---

## 💡 Ideas & Inspiration You Can Take From This Project

If you are an academic student, AI researcher, or software developer, this project serves as a comprehensive blueprint for:
1. **Combining Machine Learning with Graph Theory:** Showing how ML predictions can serve as dynamic edge weights for traditional shortest-path algorithms ($A^*$, Dijkstra).
2. **Integrating Unsupervised Spatial Clustering with GIS:** Using DBSCAN on lat/lon incident logs to automate spatial hazard boundaries instead of hardcoding geographical zones.
3. **Multi-Role Strategy Pattern in AI:** Implementing strategy design patterns where different agents operate under different cost/utility functions over the same environment graph.
4. **Interactive GIS Dashboards in Python:** Combining Streamlit, Folium, Leaflet JavaScript animation, and scikit-learn metrics into a cohesive single-page web application.

---

## 📄 License

Academic project developed for AI and Decision Support System demonstration purposes.
