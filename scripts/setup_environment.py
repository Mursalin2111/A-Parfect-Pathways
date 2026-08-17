import sys
import os

# Add the project root to sys.path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment.map_downloader import (
    download_graph,
    save_custom_graph,
    # download_boundaries,
)
from src.environment.graph_enricher import enrich_graph
from src.utils.visualizer import visualize_graph_static
from config import MAP_CENTER_LAT, MAP_CENTER_LON, MAP_DEFAULT_RADIUS


def main():
    OUTPUT_GRAPH_PATH = "data/processed_graph.pkl"
    OUTPUT_MAP_PATH = "outputs/initial_map.html"

    print("=== Environment Setup Started ===")

    # 1. Download Graph (uses default coordinates from config)
    G = download_graph()

    # 2. Download Boundaries
    # boundaries = download_boundaries()

    if G is not None:
        # 3. Enrich
        G = enrich_graph(G)

        # 4. Save
        save_custom_graph(G, OUTPUT_GRAPH_PATH)

        # 5. Visualize
        visualize_graph_static(
            G,
            OUTPUT_MAP_PATH,
            edge_color="#5474D0",
            # boundaries_gdf=boundaries,
            center_coords=(MAP_CENTER_LAT, MAP_CENTER_LON),
            radius=MAP_DEFAULT_RADIUS,
        )

        print("=== Environment Setup Completed Successfully ===")
    else:
        print("=== Failed to download graph ===")


if __name__ == "__main__":
    main()
