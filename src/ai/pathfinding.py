import networkx as nx
import math


def haversine(u, v, G):
    """
    Heuristic function for A* Search.
    Calculates the great-circle distance between two nodes.
    """
    x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
    x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
    R = 6371000  # radius of Earth in meters

    phi1, phi2 = math.radians(y1), math.radians(y2)
    dphi = math.radians(y2 - y1)
    dlambda = math.radians(x2 - x1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d


def calculate_single_edge_weight(edge_data, mode="safe", blocked_zones=None, u_node=None, v_node=None):
    """
    Calculates the weight for a single edge dictionary.
    """
    # Check if edge is inside any blocked zone
    if blocked_zones and u_node and v_node:
        edge_lat = (u_node["y"] + v_node["y"]) / 2
        edge_lon = (u_node["x"] + v_node["x"]) / 2

        for zone_lat, zone_lon, zone_radius, _ in blocked_zones:
            # Simple distance check (approximate, good enough for small areas)
            dist = haversine_coords(edge_lat, edge_lon, zone_lat, zone_lon)
            if dist <= zone_radius:
                return float("inf")  # Impassable

    length = float(edge_data.get("length", 1.0))
    risk = float(edge_data.get("risk_level", 0.0))
    resource_cost = float(edge_data.get("resource_cost", 0.0))

    if mode == "safe":
        # Army Logic: Avoid risk at all costs.
        # Cost = Length * (1 + 100 * Risk)
        # If risk is 0.1, multiplier is 11x
        return length * (1 + 100 * risk)

    elif mode == "balanced":
        # Rescuer Logic: Balance
        # Cost = Length * (1 + 5 * Risk)
        return length * (1 + 5 * risk)

    elif mode == "efficient":
        # Volunteer Logic: Efficiency
        # Cost = Length * (1 + Resource Cost)
        # Assuming resource_cost is already scaled (e.g. 1.0 - 10.0)
        return length * (1 + resource_cost)

    else:
        # Fast / Default
        return length


def calculate_weight(u, v, d, mode="safe", blocked_zones=None, G=None):
    """
    Calculates the weight of the transition between u and v.
    Handles MultiDiGraph by finding the minimum weight among parallel edges.
    """
    u_node = G.nodes[u] if G else None
    v_node = G.nodes[v] if G else None

    # d contains all edges between u and v keyed by edge key (if MultiGraph)
    # or just attributes (if DiGraph, though G is MultiDiGraph here)
    # NetworkX passes a dict of edges for MultiGraph: {key1: attr1, key2: attr2}

    if G and G.is_multigraph() and isinstance(d, dict):
        min_weight = float("inf")
        # Check if d is actually the dict of edges.
        # For MultiGraph, 'd' passed to weight func is the dict of edges {key: {attrs}}
        # We need to iterate over values.

        # Defensive check: if d looks like edge attributes (has 'length'), treat as single edge
        if "length" in d:
             return calculate_single_edge_weight(d, mode, blocked_zones, u_node, v_node)

        # Iterate over all parallel edges
        for key, edge_data in d.items():
            w = calculate_single_edge_weight(edge_data, mode, blocked_zones, u_node, v_node)
            if w < min_weight:
                min_weight = w
        return min_weight
    else:
        # Single edge case
        return calculate_single_edge_weight(d, mode, blocked_zones, u_node, v_node)


def haversine_coords(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in meters."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_path_astar(G, start_node, end_node, weight_mode="safe", blocked_zones=None):
    """
    Finds the optimal path using A* Search.

    Args:
        G (networkx.MultiDiGraph): The graph.
        start_node (int): Source node ID.
        end_node (int): Target node ID.
        weight_mode (str): 'safe', 'balanced', 'efficient', or 'fast'.
        blocked_zones (list): Optional list of (lat, lon, radius, name) zones to avoid.

    Returns:
        tuple: (path_nodes, path_coords)
            path_nodes: List of node IDs.
            path_coords: List of (lat, lon) tuples following the street geometry.
    """
    try:
        # Define a lambda for the weight to pass context
        path_nodes = nx.astar_path(
            G,
            start_node,
            end_node,
            heuristic=lambda u, v: haversine(u, v, G),
            weight=lambda u, v, d: calculate_weight(
                u, v, d, weight_mode, blocked_zones, G
            ),
        )

        # Extract full geometry
        path_coords = []
        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i + 1]

            # Find the best edge key that matches the calculated weight logic
            # (Re-evaluate to find which edge we actually took)
            best_edge_data = None
            min_weight = float("inf")

            edges_data = G.get_edge_data(u, v) # returns {key: attrs}

            if edges_data:
                for key, data in edges_data.items():
                    u_node = G.nodes[u]
                    v_node = G.nodes[v]
                    w = calculate_single_edge_weight(data, weight_mode, blocked_zones, u_node, v_node)
                    if w < min_weight:
                        min_weight = w
                        best_edge_data = data

            # Fallback if something went wrong
            if best_edge_data is None:
                # Should not happen if path exists
                best_edge_data = next(iter(edges_data.values())) if edges_data else {}

            if "geometry" in best_edge_data:
                # Use the actual shape of the road
                # Geometry is usually a Shapely LineString -> list of (x, y)
                # We need (y, x) for Folium
                coords = [(lat, lon) for lon, lat in best_edge_data["geometry"].coords]
                path_coords.extend(coords)
            else:
                # Fallback to straight line
                u_node = G.nodes[u]
                v_node = G.nodes[v]
                path_coords.append((u_node["y"], u_node["x"]))
                path_coords.append((v_node["y"], v_node["x"]))

        return path_nodes, path_coords

    except nx.NetworkXNoPath:
        print(f"No path found between {start_node} and {end_node}")
        return None, None
    except Exception as e:
        print(f"Error in pathfinding: {e}")
        import traceback
        traceback.print_exc()
        return None, None
