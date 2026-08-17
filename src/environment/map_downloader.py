import osmnx as ox
import networkx as nx
import pickle
import os
from config import MAP_CENTER_LAT, MAP_CENTER_LON, MAP_DEFAULT_RADIUS


def download_graph(location=None, dist=None, network_type="drive"):
    if location is None:
        location = (MAP_CENTER_LAT, MAP_CENTER_LON)

    if dist is None:
        dist = MAP_DEFAULT_RADIUS

    print(f"Downloading graph for {location} with radius {dist}m...")
    try:
        if isinstance(location, (tuple, list)) and len(location) == 2:
            # Input is (latitude, longitude)
            print(f"Using coordinates: {location}")
            G = ox.graph_from_point(location, dist=dist, network_type=network_type)
        else:
            # Input is address string
            print(f"Using address: {location}")
            G = ox.graph_from_address(location, dist=dist, network_type=network_type)

        print("Graph downloaded successfully.")
        return G
    except Exception as e:
        print(f"Error downloading graph: {e}")
        return None


def download_boundaries(location=None, dist=None):
    """
    Downloads administrative boundaries (polygons) for a given location.

    Args:
        location (tuple, optional): (lat, lon) tuple. Defaults to config constants.
        dist (int, optional): Distance in meters (unused in current geocode implementation but kept for API compatibility).

    Returns:
        geopandas.GeoDataFrame: Geometries of administrative boundaries.
    """
    if location is None:
        location = (MAP_CENTER_LAT, MAP_CENTER_LON)

    # Format coordinates as a string for geocode_to_gdf
    # This is more reliable for finding the containing administrative area than features_from_point
    query = f"{location[0]}, {location[1]}"

    print(f"Downloading administrative boundaries for {query}...")
    try:
        # Get boundaries for the area containing the point
        boundaries = ox.geocode_to_gdf(query)

        if not boundaries.empty:
            print(
                f"Found administrative boundary: {boundaries['display_name'].iloc[0] if 'display_name' in boundaries.columns else 'Unknown'}"
            )
        else:
            print("No administrative boundaries found.")

        return boundaries
    except Exception as e:
        print(f"Error downloading boundaries: {e}")
        return None


def save_custom_graph(graph, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(graph, f)
        print(f"Graph saved to {filepath}")
    except Exception as e:
        print(f"Error saving graph: {e}")


def load_custom_graph(filepath):
    try:
        with open(filepath, "rb") as f:
            graph = pickle.load(f)
        print(f"Graph loaded from {filepath}")
        return graph
    except Exception as e:
        print(f"Error loading graph: {e}")
        return None
