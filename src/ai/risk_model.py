import os
import random
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class RiskModel:
    """
    Advanced ML Risk Prediction Engine for Road Networks.

    Supported algorithms:
    - random_forest (default)
    - gradient_boosting
    - logistic

    Features evaluated per road segment:
    1. highway_type_rank: (0=footway to 5=motorway)
    2. maxspeed: Speed limit (km/h)
    3. lanes: Number of lanes
    4. length: Road segment length (meters)
    5. is_bridge: Flag for bridges (1/0)
    6. is_tunnel: Flag for tunnels (1/0)
    7. weather_factor: Weather risk multiplier (1.0 - 2.0)
    8. time_factor: Time-of-day risk multiplier (1.0 - 1.8)
    """

    FEATURE_NAMES = [
        "Highway Rank",
        "Max Speed",
        "Lanes",
        "Segment Length",
        "Is Bridge",
        "Is Tunnel",
        "Weather Impact",
        "Time Impact",
    ]

    def __init__(self, model_type="random_forest"):
        self.model_type = model_type
        self.scaler = StandardScaler()
        self.is_trained = False
        self.metrics = {}
        self.feature_importances = {}

        if model_type == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
        else:
            self.model = LogisticRegression(random_state=42)

        self.highway_ranks = {
            "motorway": 5,
            "trunk": 5,
            "primary": 4,
            "secondary": 4,
            "tertiary": 3,
            "residential": 2,
            "living_street": 2,
            "service": 1,
            "track": 1,
            "footway": 0,
            "cycleway": 0,
            "path": 0,
        }

    def _extract_features(self, edge_data, weather_factor=1.0, time_factor=1.0):
        """Extracts an 8-dimensional feature vector from an edge's attributes."""
        highway = edge_data.get("highway", "residential")
        if isinstance(highway, list):
            highway = highway[0]
        rank = float(self.highway_ranks.get(highway, 2))

        maxspeed = edge_data.get("maxspeed", 30)
        try:
            if isinstance(maxspeed, list):
                maxspeed = float(maxspeed[0])
            else:
                maxspeed = float(maxspeed)
        except (ValueError, TypeError):
            maxspeed = 30.0

        lanes = edge_data.get("lanes", 1)
        try:
            if isinstance(lanes, list):
                lanes = float(lanes[0])
            else:
                lanes = float(lanes)
        except (ValueError, TypeError):
            lanes = 1.0

        length = float(edge_data.get("length", 50.0))
        is_bridge = 1.0 if "bridge" in edge_data else 0.0
        is_tunnel = 1.0 if "tunnel" in edge_data else 0.0

        return [
            rank,
            maxspeed,
            lanes,
            length,
            is_bridge,
            is_tunnel,
            float(weather_factor),
            float(time_factor),
        ]

    def train(self, dataset_size=1500):
        """
        Trains the ML model using structured multi-feature risk distribution.
        Evaluates performance on a test split.
        """
        if self.is_trained:
            return

        X, y = [], []

        for _ in range(dataset_size):
            rank = random.randint(0, 5)
            maxspeed = float(random.choice([30, 40, 50, 60, 80, 100]))
            lanes = float(random.randint(1, 4))
            length = random.uniform(10.0, 600.0)
            bridge = float(random.choice([0, 0, 0, 1]))
            tunnel = float(random.choice([0, 0, 0, 1]))
            weather = random.choice([1.0, 1.2, 1.5, 1.8])
            time_fac = random.choice([1.0, 1.3, 1.6])

            # Ground truth risk probability function
            risk_score = 0.05
            if rank >= 4:
                risk_score += 0.35
            if maxspeed >= 60:
                risk_score += 0.25
            if bridge or tunnel:
                risk_score += 0.15
            risk_score *= (weather * time_fac * 0.5)

            label = 1 if (risk_score > 0.45 or random.random() < risk_score) else 0

            X.append([rank, maxspeed, lanes, length, bridge, tunnel, weather, time_fac])
            y.append(label)

        X = np.array(X)
        y = np.array(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model.fit(X_train_scaled, y_train)
        y_pred = self.model.predict(X_test_scaled)

        # Store evaluation metrics
        self.metrics = {
            "Accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
            "Precision": round(precision_score(y_test, y_pred, zero_division=0) * 100, 2),
            "Recall": round(recall_score(y_test, y_pred, zero_division=0) * 100, 2),
            "F1-Score": round(f1_score(y_test, y_pred, zero_division=0) * 100, 2),
        }

        # Store Feature Importances if available
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            self.feature_importances = dict(
                zip(self.FEATURE_NAMES, [round(float(imp), 4) for imp in importances])
            )
        elif hasattr(self.model, "coef_"):
            coefs = np.abs(self.model.coef_[0])
            norm_coefs = coefs / np.sum(coefs)
            self.feature_importances = dict(
                zip(self.FEATURE_NAMES, [round(float(c), 4) for c in norm_coefs])
            )

        self.is_trained = True

    def predict_risk(self, edge_data, weather_factor=1.0, time_factor=1.0):
        """Returns risk probability (0.0 to 1.0) for a given edge."""
        if not self.is_trained:
            self.train()

        features = np.array(
            self._extract_features(edge_data, weather_factor, time_factor)
        ).reshape(1, -1)
        features_scaled = self.scaler.transform(features)

        prob = self.model.predict_proba(features_scaled)[0][1]
        return round(float(prob), 2)

