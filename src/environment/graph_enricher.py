import random
from src.ai.risk_model import RiskModel


def enrich_graph(graph, model_type="random_forest", weather_factor=1.0, time_factor=1.0):
    """
    Adds simulation attributes to a real-world graph using the ML Risk Engine.

    Args:
        graph (networkx.MultiDiGraph): The input graph (modified in-place).
        model_type (str): ML model algorithm ('random_forest', 'gradient_boosting', 'logistic').
        weather_factor (float): Multiplier for weather condition severity.
        time_factor (float): Multiplier for time-of-day severity.

    Returns:
        tuple: (enriched_graph, risk_model_instance)
    """
    print(f"Enriching graph using ML Model ({model_type})...")

    risk_model = RiskModel(model_type=model_type)
    risk_model.train()

    for u, v, k, data in graph.edges(keys=True, data=True):
        # 1. Predict Risk using ML Engine
        predicted_risk = risk_model.predict_risk(
            data, weather_factor=weather_factor, time_factor=time_factor
        )

        # 2. Enemy Prob correlated with Risk
        enemy_prob = min(1.0, predicted_risk * random.uniform(0.75, 1.0))

        # 3. Resource Cost calculation
        length = float(data.get("length", 100))
        maxspeed = data.get("maxspeed", 30)
        try:
            if isinstance(maxspeed, list):
                maxspeed_val = float(maxspeed[0])
            else:
                maxspeed_val = float(maxspeed)
        except (ValueError, TypeError):
            maxspeed_val = 30.0

        cost_factor = 1.4 if maxspeed_val <= 30.0 else 1.0


        resource_cost = (length / 100) * cost_factor * weather_factor

        data["risk_level"] = predicted_risk
        data["enemy_probability"] = round(enemy_prob, 2)
        data["resource_cost"] = round(resource_cost, 2)

    print(f"Enriched {graph.number_of_edges()} edges using {model_type} model.")
    return graph, risk_model

