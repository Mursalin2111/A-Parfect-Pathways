"""
Dynamic Danger Zone Detection using Unsupervised Learning (DBSCAN Clustering).
"""

import numpy as np
import random
from sklearn.cluster import DBSCAN
from math import radians, cos, sin, asin, sqrt


def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculates distance in meters between two lat/lon points."""
    R = 6371000  # Radius of Earth in meters
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def generate_synthetic_incidents(center_lat, center_lon, radius_m=2000, num_points=120):
    """Generates synthetic incident locations around the map center with natural spatial clustering."""
    np.random.seed(42)
    random.seed(42)

    incidents = []
    # Create 3 natural hotspots
    hotspots = [
        (center_lat + 0.002, center_lon + 0.003),
        (center_lat - 0.003, center_lon - 0.002),
        (center_lat + 0.001, center_lon - 0.004),
    ]

    for lat_h, lon_h in hotspots:
        for _ in range(num_points // 4):
            # Normal distribution around hotspot
            lat_p = float(np.random.normal(lat_h, 0.0008))
            lon_p = float(np.random.normal(lon_h, 0.0008))
            incidents.append([lat_p, lon_p])

    # Add uniform random noise
    for _ in range(num_points // 4):
        lat_p = center_lat + random.uniform(-0.015, 0.015)
        lon_p = center_lon + random.uniform(-0.015, 0.015)
        incidents.append([lat_p, lon_p])

    return np.array(incidents)


def discover_danger_clusters(center_lat, center_lon, radius_m=2000, eps_meters=180, min_samples=4):
    """
    Uses DBSCAN clustering to dynamically discover danger zones from raw incident points.

    Returns:
        list of tuples: [(lat, lon, radius_meters, label_name), ...]
    """
    incidents = generate_synthetic_incidents(center_lat, center_lon, radius_m)

    # Convert coordinates to radians for BallTree / Haversine in DBSCAN
    coords_rad = np.radians(incidents)

    # Earth radius in meters
    kms_per_radian = 6371000.0
    epsilon = eps_meters / kms_per_radian

    db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="haversine")
    labels = db.fit_predict(coords_rad)

    cluster_zones = []
    unique_labels = set(labels)

    for cluster_id in unique_labels:
        if cluster_id == -1:
            # Noise points
            continue

        class_member_mask = (labels == cluster_id)
        cluster_points = incidents[class_member_mask]

        # Calculate cluster center
        mean_lat = float(np.mean(cluster_points[:, 0]))
        mean_lon = float(np.mean(cluster_points[:, 1]))

        # Calculate radius (max distance from center to any point in cluster + buffer)
        max_dist = 50.0
        for pt in cluster_points:
            dist = haversine_distance_meters(mean_lat, mean_lon, pt[0], pt[1])
            if dist > max_dist:
                max_dist = dist

        radius = min(max(round(max_dist + 30.0), 80), 250)
        zone_label = f"ML Danger Cluster #{cluster_id + 1} ({len(cluster_points)} incidents)"
        cluster_zones.append((mean_lat, mean_lon, radius, zone_label))

    return cluster_zones
