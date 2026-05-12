import osmnx as ox
import folium
import os
import json


def add_animated_path(m, path_coords, path_color="#FF4B4B", speed=50):
    """
    Adds an animated marker moving along the path with a visual trail.
    
    Args:
        m (folium.Map): The folium map object.
        path_coords (list): List of (lat, lon) tuples.
        path_color (str): Hex color for the path.
        speed (int): Animation speed in milliseconds per segment (lower = faster).
    """
    if not path_coords or len(path_coords) < 2:
        return m
    
    # Convert path_coords to JSON for JavaScript
    path_json = json.dumps(path_coords)
    
    # Create the animated path JavaScript
    animation_js = f"""
    <script>
        let pathCoords = {path_json};
        let currentIndex = 0;
        let animationMarker = null;
        let polylineTrail = null;
        let trailCoords = [];
        let animationRunning = true;
        
        function initializeAnimation() {{
            if (!window.map) return;
            
            // Remove existing marker and trail
            if (animationMarker) {{ window.map.removeLayer(animationMarker); }}
            if (polylineTrail) {{ window.map.removeLayer(polylineTrail); }}
            
            currentIndex = 0;
            trailCoords = [];
            animationMarker = L.marker(pathCoords[0], {{
                icon: L.icon({{
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }}),
                title: 'Agent in Motion'
            }}).addTo(window.map);
            
            // Start animation loop
            animateMarker();
        }}
        
        function animateMarker() {{
            if (!animationRunning || currentIndex >= pathCoords.length) {{
                if (currentIndex >= pathCoords.length) {{
                    animationRunning = false;
                }}
                return;
            }}
            
            if (currentIndex > 0) {{
                // Update marker position
                animationMarker.setLatLng(pathCoords[currentIndex]);
                
                // Add to trail
                trailCoords.push(pathCoords[currentIndex]);
                
                // Remove old trail if too long
                if (trailCoords.length > 30) {{
                    trailCoords.shift();
                }}
                
                // Update trail visualization
                if (polylineTrail) {{ window.map.removeLayer(polylineTrail); }}
                if (trailCoords.length > 1) {{
                    polylineTrail = L.polyline(trailCoords, {{
                        color: '{path_color}',
                        weight: 4,
                        opacity: 0.6,
                        dashArray: '5, 5',
                        lineCap: 'round',
                        lineJoin: 'round'
                    }}).addTo(window.map);
                }}
            }}
            
            currentIndex++;
            
            // Continue animation
            setTimeout(animateMarker, {speed});
        }}
        
        // Wait for map to be ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', () => {{
                setTimeout(() => {{
                    window.map = Object.values(window)[Object.keys(window).find(k => 
                        typeof window[k] === 'object' && window[k]._container && 
                        window[k]._zoom !== undefined
                    )] || null;
                    if (window.map) {{ initializeAnimation(); }}
                }}, 500);
            }});
        }} else {{
            setTimeout(() => {{
                window.map = Object.values(window)[Object.keys(window).find(k => 
                    typeof window[k] === 'object' && window[k]._container && 
                    window[k]._zoom !== undefined
                )] || null;
                if (window.map) {{ initializeAnimation(); }}
            }}, 500);
        }}
    </script>
    """
    
    # Inject JavaScript into the map
    m.get_root().html.add_child(folium.Element(animation_js))
    
    return m


# 1. Add color parameter with a default
def visualize_graph_static(
    graph,
    filename="output/map.html",
    edge_color="blue",
    boundaries_gdf=None,
    center_coords=None,
    radius=None,
    enemy_zones=None,
):
    """
    Generates a static HTML map visualization.
    Args:
        graph (networkx.MultiDiGraph): The graph to visualize.
        filename (str): The output filename.
        edge_color (str): The color of the edges (e.g., 'red', '#ff0000').
        boundaries_gdf (geopandas.GeoDataFrame, optional): Geometries of administrative boundaries.
        center_coords (tuple, optional): (lat, lon) for the radius circle.
        radius (int, optional): Radius in meters for the circle.
    Returns:
        folium.Map: The generated map object.
    """
    print(f"Generating map visualization to {filename}...")
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        gdf_nodes, gdf_edges = ox.graph_to_gdfs(graph)

        center_y = gdf_nodes.geometry.y.mean()
        center_x = gdf_nodes.geometry.x.mean()

        m = folium.Map(
            location=[center_y, center_x],
            zoom_start=14,
            tiles="cartodbpositron",
            attribution_control=False,
        )

        # Custom styling is now handled by assets/style.css

        # Plot boundaries first (so they are in the background)
        if boundaries_gdf is not None and not boundaries_gdf.empty:
            print(f"Adding {len(boundaries_gdf)} administrative boundaries to map...")
            folium.GeoJson(
                boundaries_gdf,
                name="Administrative Boundaries",
                style_function=lambda feature: {
                    "fillColor": "#f2f2f2",
                    "color": "#666666",
                    "weight": 1,
                    "dashArray": "5, 5",
                    "fillOpacity": 0.2,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["name"] if "name" in boundaries_gdf.columns else []
                ),
            ).add_to(m)

        # Plot radius circle
        if center_coords is not None and radius is not None:
            # OSMnx downloads a square box with side 2*radius.
            # A circle with original radius will cut off corners.
            # To cover the full street network, we can calculate the distance to the furthest node
            # or simply use radius * sqrt(2). Calculating actual furthest node is more precise.
            try:
                # OSMnx downloads a square box with side 2*radius.
                # A circle with original radius will cut off corners.
                # To cover the full street network, we use a 1.45 multiplier (approx sqrt(2) + buffer).
                visual_radius = radius * 1.45

                print(
                    f"Adding radius circle ({visual_radius:.0f}m) at {center_coords}..."
                )
                folium.Circle(
                    location=center_coords,
                    radius=visual_radius,
                    color="#666666",
                    weight=1,
                    fill=True,
                    fill_color="#666666",
                    fill_opacity=0.05,
                    dash_array="10, 10",
                    name="Operation Area",
                ).add_to(m)
            except Exception as circle_err:
                print(f"Error adding radius circle: {circle_err}")

        # Plot enemy/danger zones
        if enemy_zones:
            for idx, zone in enumerate(enemy_zones, start=1):
                lat, lon, zone_radius, name = zone
                # Create the danger zone circle
                folium.Circle(
                    location=[lat, lon],
                    radius=zone_radius,
                    color="#FF0000",
                    weight=2,
                    fill=True,
                    fill_color="#FF0000",
                    fill_opacity=0.3,
                    popup=f"{name}",
                ).add_to(m)

                # Add permanent label marker for the zone name
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="
                            background-color: white;
                            border: 1px solid #ccc;
                            border-radius: 4px;
                            padding: 4px 8px;
                            font-size: 12px;
                            font-weight: 500;
                            white-space: nowrap;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                            transform: translate(-50%, -100%);
                            text-align: center;
                        ">{idx}. {name}</div>
                        """,
                        icon_size=(150, 36),
                        icon_anchor=(75, 36),
                    ),
                ).add_to(m)
            print(f"Added {len(enemy_zones)} enemy zones to map.")

        # Plot edges
        folium.GeoJson(
            gdf_edges,
            name="Street Network",
            style_function=lambda feature: {
                "color": edge_color,
                "weight": 2,
                "opacity": 0.7,
            },
        ).add_to(m)

        folium.LayerControl().add_to(m)

        m.save(filename)
        print("Map visualization saved.")
        return m
    except Exception as e:
        print(f"Error visualizing graph: {e}")
        return None
