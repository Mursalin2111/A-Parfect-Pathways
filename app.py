import streamlit as st
from streamlit_folium import st_folium
import osmnx as ox
import folium
import random
from src.environment.map_downloader import download_graph, download_boundaries
from src.environment.graph_enricher import enrich_graph
from src.environment.danger_clusterer import discover_danger_clusters
from src.utils.visualizer import visualize_graph_static, add_animated_path
from src.ai.pathfinding import find_path_astar
from src.roles import ArmyRole, RescuerRole, VolunteerRole
from src.ai.mission_narrator import generate_briefing
from config import MAP_CENTER_LAT, MAP_CENTER_LON, MAP_DEFAULT_RADIUS, ENEMY_ZONES

st.set_page_config(page_title="A Perfect Pathway", layout="wide")

st.title("A Perfect Pathway - AI & ML Simulation Environment")
st.markdown(
    "Real-world street network enriched with **Multi-Algorithm Machine Learning & DBSCAN Hazard Clustering**."
)


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

st.sidebar.header("🤖 Machine Learning Engine")
ml_model_name = st.sidebar.selectbox(
    "Risk ML Model",
    ["Random Forest", "Gradient Boosting", "Logistic Regression"],
    index=0,
    help="Select the classification algorithm used to predict road segment danger levels.",
)
model_type_map = {
    "Random Forest": "random_forest",
    "Gradient Boosting": "gradient_boosting",
    "Logistic Regression": "logistic",
}
model_type_key = model_type_map[ml_model_name]

weather_opt = st.sidebar.selectbox(
    "Weather Condition",
    ["Clear (1.0x)", "Rain (1.3x)", "Heavy Fog (1.6x)"],
    index=0,
)
weather_val = 1.0 if "Clear" in weather_opt else (1.3 if "Rain" in weather_opt else 1.6)

time_opt = st.sidebar.selectbox(
    "Time of Day",
    ["Daytime (1.0x)", "Nighttime (1.4x)"],
    index=0,
)
time_val = 1.0 if "Daytime" in time_opt else 1.4

hazard_mode = st.sidebar.radio(
    "Danger Zone Detection",
    ["Dynamic ML Clusters (DBSCAN)", "Preset Config Zones"],
    index=0,
    help="DBSCAN automatically clusters spatial incident data into dynamic danger zones.",
)
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
def load_and_enrich_graph(lat, lon, radius, model_type_key, weather_val, time_val):
    """Downloads and enriches the graph using ML Risk Engine."""
    location = (lat, lon)
    G = download_graph(location=location, dist=radius)
    if G:
        G, risk_model = enrich_graph(
            G,
            model_type=model_type_key,
            weather_factor=weather_val,
            time_factor=time_val,
        )
        return G, risk_model
    return None, None


@st.cache_resource
def load_boundaries(lat, lon):
    return download_boundaries(location=(lat, lon))


@st.cache_data
def get_danger_zones(lat, lon, radius, mode):
    if mode == "Dynamic ML Clusters (DBSCAN)":
        return discover_danger_clusters(lat, lon, radius)
    return ENEMY_ZONES


def get_map(_G, _boundaries, lat, lon, radius, danger_zones, path_coords=None, path_color="#FF4B4B"):
    """Generates the folium map object."""
    m = visualize_graph_static(
        _G,
        filename="outputs/streamlit_map.html",
        edge_color="#5474D0",
        boundaries_gdf=_boundaries,
        center_coords=(lat, lon),
        radius=radius,
        enemy_zones=danger_zones,
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
G, risk_model = load_and_enrich_graph(lat, lon, radius, model_type_key, weather_val, time_val)
boundaries = load_boundaries(lat, lon)
danger_zones = get_danger_zones(lat, lon, radius, hazard_mode)

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
        all_names = gdf_edges_temp["name"].dropna().tolist()
        street_names = [s for s in all_names if isinstance(s, str)]
        street_names = ["-- Select a Street --"] + sorted(set(street_names))

        street_node_map = {}
        for idx, row in gdf_edges_temp.iterrows():
            name = row.get("name")
            if isinstance(name, str) and name not in street_node_map:
                street_node_map[name] = idx[0]

        node_street_map = {v: k for k, v in street_node_map.items()}

        if "selected_source" not in st.session_state:
            st.session_state["selected_source"] = "-- Select a Street --"
        if "selected_destination" not in st.session_state:
            st.session_state["selected_destination"] = "-- Select a Street --"

        source_index = 0
        if st.session_state["selected_source"] in street_names:
            source_index = street_names.index(st.session_state["selected_source"])
        start_selection = st.selectbox("Source Street", street_names, index=source_index)
        st.session_state["selected_source"] = start_selection
        start_node = None if start_selection == "-- Select a Street --" else street_node_map.get(start_selection)

        dest_index = 0
        if st.session_state["selected_destination"] in street_names:
            dest_index = street_names.index(st.session_state["selected_destination"])
        end_selection = st.selectbox("Destination Street", street_names, index=dest_index)
        st.session_state["selected_destination"] = end_selection
        end_node = end_selection

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            plan_mission = st.button("Plan Mission", type="primary", use_container_width=True)
        with col_btn2:
            random_mission = st.button("Random", use_container_width=True)
        with col_btn3:
            clear_mission = st.button("Clear", use_container_width=True)

        if clear_mission:
            st.session_state["path_coords"] = None
            st.session_state["selected_source"] = "-- Select a Street --"
            st.session_state["selected_destination"] = "-- Select a Street --"
            st.rerun()

        if plan_mission:
            actual_end_node = street_node_map.get(end_selection)
            if start_node and actual_end_node:
                zones_to_block = danger_zones if selected_role.name == "Army" else None

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

        if random_mission:
            nodes = list(G.nodes())
            if len(nodes) > 1:
                start_node = random.choice(nodes)
                end_node = random.choice(nodes)

                start_street = node_street_map.get(start_node, None)
                end_street = node_street_map.get(end_node, None)

                if start_street:
                    st.session_state["selected_source"] = start_street
                if end_street:
                    st.session_state["selected_destination"] = end_street

                zones_to_block = danger_zones if selected_role.name == "Army" else None

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
        st.caption(f"Active Hazard Zones: {len(danger_zones)} ({hazard_mode})")

        # ML Model Performance Panel
        if risk_model and hasattr(risk_model, "metrics"):
            with st.expander("📊 ML Model Performance", expanded=False):
                st.markdown(f"**Algorithm:** {ml_model_name}")
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("Accuracy", f"{risk_model.metrics.get('Accuracy', 0)}%")
                m_col2.metric("F1 Score", f"{risk_model.metrics.get('F1-Score', 0)}%")

                if hasattr(risk_model, "feature_importances") and risk_model.feature_importances:
                    st.markdown("**Feature Importances:**")
                    import pandas as pd
                    df_imp = pd.DataFrame(
                        list(risk_model.feature_importances.items()),
                        columns=["Feature", "Importance"],
                    ).sort_values(by="Importance", ascending=True)
                    st.bar_chart(df_imp.set_index("Feature"), horizontal=True)

        st.markdown("### Risk Analysis")
        if st.session_state["path_coords"]:
            st.info(f"Route Segments: {len(st.session_state['path_coords'])}")
            st.caption(f"Role: {selected_role.name}")
            
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
            danger_zones,
            st.session_state["path_coords"],
            path_color=selected_role.path_color,
        )
        
        if st.session_state["path_coords"] and st.session_state["animate_path"]:
            m = add_animated_path(
                m, 
                st.session_state["path_coords"],
                path_color=selected_role.path_color,
                speed=st.session_state["animation_speed"]
            )

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

            if st.session_state["path_coords"]:
                st.markdown("---")
                st.subheader("Mission Briefing")
                briefing = generate_briefing(
                    role_name=selected_role.name,
                    source=st.session_state.get("selected_source", "Unknown"),
                    destination=st.session_state.get("selected_destination", "Unknown"),
                    steps=len(st.session_state["path_coords"]),
                    danger_zones_count=len(danger_zones),
                )
                if briefing:
                    st.info(briefing)
                else:
                    st.warning("Mission briefing could not be generated. Proceed with caution.")
        else:
            st.error("Failed to generate map object.")

else:
    st.error("Could not load the graph. Please check your coordinates or try again.")

