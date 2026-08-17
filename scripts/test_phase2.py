import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ai.risk_model import RiskModel
from src.ai.pathfinding import find_path_astar
import networkx as nx


def test_risk_model():
    print("Testing Risk Model...")
    model = RiskModel()

    # Test Case 1: High Risk Scenario (Motorway, Fast)
    edge_high = {"highway": "motorway", "maxspeed": 100, "lanes": 4}
    risk_high = model.predict_risk(edge_high)
    print(f"Predicted Risk for Motorway: {risk_high}")

    # Test Case 2: Low Risk Scenario (Cycleway)
    edge_low = {"highway": "cycleway", "maxspeed": 20, "lanes": 1}
    risk_low = model.predict_risk(edge_low)
    print(f"Predicted Risk for Cycleway: {risk_low}")

    # Heuristic check
    if risk_high > risk_low:
        print("PASS: Motorway is riskier than Cycleway.")
    else:
        print("FAIL: Risk logic seems inverted or random.")


def test_pathfinding():
    print("\nTesting Pathfinding...")
    # Create a simple synthetic graph
    G = nx.MultiDiGraph()

    # 0 -> 1 -> 2 (Short but Dangerous)
    # 0 -> 3 -> 4 -> 2 (Long but Safe)

    # Add nodes with coordinates (scaled to be ~meters apart)
    # 0.0001 degrees is roughly 11 meters
    G.add_node(0, x=0.0000, y=0.0000)
    G.add_node(1, x=0.0001, y=0.0000)  # ~11m East
    G.add_node(2, x=0.0002, y=0.0000)  # ~22m East
    G.add_node(3, x=0.0000, y=0.0001)  # ~11m North
    G.add_node(4, x=0.0002, y=0.0001)  # ~22m East, 11m North

    # Add edges
    # Short path edges (High Risk)
    G.add_edge(0, 1, length=10, risk_level=0.9)
    G.add_edge(1, 2, length=10, risk_level=0.9)

    # Long path edges (Low Risk)
    G.add_edge(0, 3, length=10, risk_level=0.0)
    G.add_edge(3, 4, length=10, risk_level=0.0)
    G.add_edge(4, 2, length=10, risk_level=0.0)

    # Test Safe Mode (Should take long path 0-3-4-2)
    path_safe, _ = find_path_astar(G, 0, 2, weight_mode="safe")
    print(f"Safe Path: {path_safe}")

    if path_safe == [0, 3, 4, 2]:
        print("PASS: Logic chose the safer, longer route.")
    else:
        print(f"FAIL: Logic chose {path_safe}")

    # Test Fast Mode (Should take short path 0-1-2)
    path_fast, _ = find_path_astar(G, 0, 2, weight_mode="fast")
    print(f"Fast Path: {path_fast}")

    if path_fast == [0, 1, 2]:
        print("PASS: Logic chose the faster, riskier route.")
    else:
        print(f"FAIL: Logic chose {path_fast}")


if __name__ == "__main__":
    test_risk_model()
    test_pathfinding()
