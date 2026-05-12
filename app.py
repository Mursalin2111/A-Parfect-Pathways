import streamlit as st
from streamlit_folium import st_folium
import osmnx as ox
import folium
import random
from src.environment.map_downloader import download_graph, download_boundaries
from src.environment.graph_enricher import enrich_graph
from src.utils.visualizer import visualize_graph_static, add_animated_path
from src.ai.pathfinding import find_path_astar
from src.roles import ArmyRole, RescuerRole, VolunteerRole
from src.ai.mission_narrator import generate_briefing
from config import MAP_CENTER_LAT, MAP_CENTER_LON, MAP_DEFAULT_RADIUS

st.set_page_config(page_title="A Perfect Pathway", layout="wide")

st.title("A Perfect Pathway - Simulation Environment")
st.markdown("Real-world street network enriched with **AI-driven risk prediction**.")


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


try:
    local_css("assets/style.css")
except FileNotFoundError:
    pass

# Sidebar for configuration
st.sidebar.header("Map Configuration")
lat = st.sidebar.number_input("Center Latitude", value=MAP_CENTER_LAT, format="%.6f")
lon = st.sidebar.number_input("Center Longitude", value=MAP_CENTER_LON, format="%.6f")
radius = st.sidebar.slider("Radius (meters)", 500, 5000, MAP_DEFAULT_RADIUS)
st.sidebar.markdown("---")

st.sidebar.header("Role Selection")

# Initialize roles
ROLES = {
    "Army": ArmyRole(),
    "Rescuer": RescuerRole(),
    "Volunteer": VolunteerRole(),
}

selected_role_name = st.sidebar.selectbox("Mission Role", list(ROLES.keys()))
selected_role = ROLES[selected_role_name]
st.sidebar.caption(selected_role.description)


@st.cache_resource
def load_and_enrich_graph(lat, lon, radius):
    """Downloads and enriches the graph. Cached to avoid re-downloading."""
    location = (lat, lon)
    G = download_graph(location=location, dist=radius)
    if G:
        G = enrich_graph(G)
        return G
    return None


@st.cache_resource
def load_boundaries(lat, lon):
    return download_boundaries(location=(lat, lon))


def get_map(_G, _boundaries, lat, lon, radius, path_coords=None, path_color="#FF4B4B"):
    """
    Generates the folium map object.
    Not cached to allow dynamic path updates.
    """
    from config import ENEMY_ZONES

    m = visualize_graph_static(
        _G,
        filename="outputs/streamlit_map.html",
        edge_color="#5474D0",
        boundaries_gdf=_boundaries,
        center_coords=(lat, lon),
        radius=radius,
        enemy_zones=ENEMY_ZONES,
    )

    if path_coords:
        # Reverse geocode to get place names
        try:
            start_address = ox.geocode_to_gdf(
                f"{path_coords[0][0]}, {path_coords[0][1]}", which_result=1
            )
            start_name = (
                start_address.iloc[0].get("display_name", "Start").split(",")[0]
            )
        except:
            start_name = "Start Point"

        try:
            end_address = ox.geocode_to_gdf(
                f"{path_coords[-1][0]}, {path_coords[-1][1]}", which_result=1
            )
            end_name = (
                end_address.iloc[0].get("display_name", "Destination").split(",")[0]
            )
        except:
            end_name = "Destination"

        # Draw the calculated path
        folium.PolyLine(
            path_coords,
            color=path_color,
            weight=5,
            opacity=0.8,
            tooltip="AI Calculated Path",
        ).add_to(m)

        # Start Marker (Green) with place name
        folium.Marker(
            path_coords[0],
            popup=f"{start_name}",
            tooltip=start_name,
            icon=folium.Icon(color="green", icon="play"),
        ).add_to(m)

        # End Marker (Red) with place name
        folium.Marker(
            path_coords[-1],
            popup=f"{end_name}",
            tooltip=end_name,
            icon=folium.Icon(color="red", icon="flag"),
        ).add_to(m)

    return m


def add_preview_markers(m, _G, start_node, end_node, start_name, end_name):
    """Add preview markers for selected locations (before path is calculated)."""
    if start_node and start_node in _G.nodes:
        node_data = _G.nodes[start_node]
        folium.Marker(
            location=[node_data["y"], node_data["x"]],
            popup=f"Start: {start_name}",
            tooltip=f"Source: {start_name}",
            icon=folium.Icon(color="green", icon="play"),
        ).add_to(m)

    if end_node and end_node in _G.nodes:
        node_data = _G.nodes[end_node]
        folium.Marker(
            location=[node_data["y"], node_data["x"]],
            popup=f"End: {end_name}",
            tooltip=f"Destination: {end_name}",
            icon=folium.Icon(color="red", icon="flag"),
        ).add_to(m)


# Main logic
G = load_and_enrich_graph(lat, lon, radius)
boundaries = load_boundaries(lat, lon)

# Pathfinding State
if "path_coords" not in st.session_state:
    st.session_state["path_coords"] = None
if "animate_path" not in st.session_state:
    st.session_state["animate_path"] = False
if "animation_speed" not in st.session_state:
    st.session_state["animation_speed"] = 50

if G:
    # Navigation Controls
    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("Mission Control")

        # Extract unique street names from the graph
        gdf_nodes_temp, gdf_edges_temp = ox.graph_to_gdfs(G)
        # Get all names, filter for strings only (some are lists)
        all_names = gdf_edges_temp["name"].dropna().tolist()
        street_names = [s for s in all_names if isinstance(s, str)]
        street_names = ["-- Select a Street --"] + sorted(set(street_names))

        # Create a mapping of street names to node IDs
        street_node_map = {}
        for idx, row in gdf_edges_temp.iterrows():
            name = row.get("name")
            if isinstance(name, str) and name not in street_node_map:
                street_node_map[name] = idx[0]  # idx is (u, v, key)

        # Create reverse mapping: node ID -> street name
        node_street_map = {v: k for k, v in street_node_map.items()}

        # Initialize session state for selections
        if "selected_source" not in st.session_state:
            st.session_state["selected_source"] = "-- Select a Street --"
        if "selected_destination" not in st.session_state:
            st.session_state["selected_destination"] = "-- Select a Street --"

        # Source Selection
        source_index = 0
        if st.session_state["selected_source"] in street_names:
            source_index = street_names.index(st.session_state["selected_source"])
        start_selection = st.selectbox(
            "Source Street", street_names, index=source_index
        )
        st.session_state["selected_source"] = start_selection
        if start_selection == "-- Select a Street --":
            start_node = None
        else:
            start_node = street_node_map.get(start_selection)

        # Destination Selection
        dest_index = 0
        if st.session_state["selected_destination"] in street_names:
            dest_index = street_names.index(st.session_state["selected_destination"])
        end_selection = st.selectbox(
            "Destination Street", street_names, index=dest_index
        )
        st.session_state["selected_destination"] = end_selection
        if end_selection == "-- Select a Street --":
            end_node = None
        else:
            end_node = end_selection

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            plan_mission = st.button(
                "Plan Mission", type="primary", use_container_width=True
            )
        with col_btn2:
            random_mission = st.button("Random", use_container_width=True)
        with col_btn3:
            clear_mission = st.button("Clear", use_container_width=True)

        # Clear Mission Logic
        if clear_mission:
            st.session_state["path_coords"] = None
            st.session_state["selected_source"] = "-- Select a Street --"
            st.session_state["selected_destination"] = "-- Select a Street --"
            st.rerun()

        # Plan Mission Logic
        if plan_mission:
            # Get actual end_node from street_node_map
            actual_end_node = street_node_map.get(end_selection)
            if start_node and actual_end_node:
                # Army blocks enemy zones
                from config import ENEMY_ZONES

                zones_to_block = ENEMY_ZONES if selected_role.name == "Army" else None

                with st.spinner("AI calculating optimal path..."):
                    path_nodes, path_coords = find_path_astar(
                        G,
                        start_node,
                        actual_end_node,
                        weight_mode=selected_role.weight_mode,
                        blocked_zones=zones_to_block,
                    )
                    st.session_state["path_coords"] = path_coords
                    if path_coords:
                        st.success(f"Path Found! Steps: {len(path_nodes)}")
                    else:
                        st.error("No path found between these streets.")
            else:
                st.warning("Please select both Source and Destination streets.")

        # Random Mission Logic
        if random_mission:
            nodes = list(G.nodes())
            if len(nodes) > 1:
                start_node = random.choice(nodes)
                end_node = random.choice(nodes)

                # Find street names for these nodes (if they exist)
                start_street = node_street_map.get(start_node, None)
                end_street = node_street_map.get(end_node, None)

                # Update dropdowns if we found matching streets
                if start_street:
                    st.session_state["selected_source"] = start_street
                if end_street:
                    st.session_state["selected_destination"] = end_street

                # Army blocks enemy zones
                from config import ENEMY_ZONES

                zones_to_block = ENEMY_ZONES if selected_role.name == "Army" else None

                with st.spinner("AI calculating optimal path..."):
                    path_nodes, path_coords = find_path_astar(
                        G,
                        start_node,
                        end_node,
                        weight_mode=selected_role.weight_mode,
                        blocked_zones=zones_to_block,
                    )
                    st.session_state["path_coords"] = path_coords
                    if path_coords:
                        st.success(f"Path Found! Steps: {len(path_nodes)}")
                    else:
                        st.error("No path found.")
            else:
                st.error("Graph has too few nodes.")

        st.metric("Nodes", G.number_of_nodes())
        st.metric("Edges", G.number_of_edges())

        st.markdown("### Risk Analysis")
        if st.session_state["path_coords"]:
            # Simple metric: number of segments
            st.info(f"Route Segments: {len(st.session_state['path_coords'])}")
            st.caption(f"Role: {selected_role.name}")
            
            # Animation Controls
            st.markdown("---")
            st.markdown("### Path Animation")
            st.session_state["animate_path"] = st.checkbox(
                "🎬 Animate Path", 
                value=st.session_state["animate_path"],
                help="Visualize the agent moving along the calculated path"
            )
            
            if st.session_state["animate_path"]:
                st.session_state["animation_speed"] = st.slider(
                    "Animation Speed",
                    min_value=10,
                    max_value=200,
                    value=st.session_state["animation_speed"],
                    step=10,
                    help="Lower values = faster animation"
                )

        # Display some edge data
        st.subheader("Intel Feed")
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
        if not gdf_edges.empty:
            sample_data = gdf_edges[
                ["risk_level", "enemy_probability", "resource_cost"]
            ].head(5)
            st.dataframe(sample_data, hide_index=True)

    with col1:
        st.subheader("Live Operational Map")
        m = get_map(
            G,
            boundaries,
            lat,
            lon,
            radius,
            st.session_state["path_coords"],
            path_color=selected_role.path_color,
        )
        
        # Add animation if enabled and path exists
        if st.session_state["path_coords"] and st.session_state["animate_path"]:
            m = add_animated_path(
                m, 
                st.session_state["path_coords"],
                path_color=selected_role.path_color,
                speed=st.session_state["animation_speed"]
            )

        # Add preview markers if locations selected but no path yet
        if m and not st.session_state["path_coords"]:
            add_preview_markers(
                m,
                G,
                start_node,
                street_node_map.get(end_selection)
                if end_selection != "-- Select a Street --"
                else None,
                start_selection,
                end_selection,
            )

        if m:
            st_folium(
                m,
                height=600,
                use_container_width=True,
                key="main_map",
                returned_objects=[],
            )

            # Auto-generate Mission Briefing when path exists
            if st.session_state["path_coords"]:
                from config import ENEMY_ZONES

                st.markdown("---")
                st.subheader("Mission Briefing")
                briefing = generate_briefing(
                    role_name=selected_role.name,
                    source=st.session_state.get("selected_source", "Unknown"),
                    destination=st.session_state.get("selected_destination", "Unknown"),
                    steps=len(st.session_state["path_coords"]),
                    danger_zones_count=len(ENEMY_ZONES),
                )
                if briefing:
                    st.info(briefing)
                else:
                    st.warning(
                        "Mission briefing could not be generated. Proceed with caution."
                    )
        else:
            st.error("Failed to generate map object.")

else:
    st.error("Could not load the graph. Please check your coordinates or try again.")
