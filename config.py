"""Project configuration settings for Perfect Pathway."""

import os

# Environment Settings
ENVIRONMENT_WIDTH = 10
ENVIRONMENT_HEIGHT = 10
MAP_CENTER_LAT = 23.738113
MAP_CENTER_LON = 90.395857
MAP_DEFAULT_RADIUS = 2000

# AI Settings
A_STAR_WEIGHT = "combined"  # distance, time, risk, combined
RISK_PREDICTION_THRESHOLD = 0.5  # Classify as unsafe if > threshold

# Role Settings
ARMY_SAFETY_THRESHOLD = 0.7  # Min safety score for Army
RESCUER_SPEED_PRIORITY = 0.7  # Speed vs safety ratio
VOLUNTEER_EFFICIENCY_RATIO = 0.8  # Efficiency priority

# Training Settings
ML_TRAINING_SAMPLES = 500
ML_MODEL_TYPE = "logistic"  # logistic or decision_tree
Q_LEARNING_EPISODES = 100
Q_LEARNING_LEARNING_RATE = 0.1
Q_LEARNING_DISCOUNT_RATE = 0.95

# Visualization
MAP_ZOOM_LEVEL = 13
MAP_TILES = "OpenStreetMap"

# Enemy/Danger Zones (lat, lon, radius_meters, name)
ENEMY_ZONES = [
    (23.7400, 90.3920, 150, "Enemy Camp Alpha"),
    (23.7350, 90.3980, 100, "Hostile Checkpoint"),
    (23.7420, 90.4000, 120, "Danger Zone Bravo"),
    (23.7380, 90.3850, 80, "Sniper Position"),
    (23.7360, 90.3900, 100, "Sniper Position"),
    (23.7370, 90.3950, 120, "Danger Zone Charlie"),
    (23.7390, 90.3920, 150, "Enemy Camp Delta"),
    (23.7340, 90.3970, 100, "Hostile Checkpoint"),
    (23.7320, 90.3930, 120, "Danger Zone Echo"),
    (23.7310, 90.3980, 150, "Enemy Camp Hotel"),
    (23.7300, 90.4020, 100, "Hostile Checkpoint"),
    (23.7290, 90.4050, 120, "Danger Zone Hotel"),
]

# Logging
LOG_LEVEL = "INFO"
SAVE_PLOTS = True
PLOT_DPI = 300

# LLM Settings (for Mission Briefings)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", " ")
LLM_ENABLED = bool(GEMINI_API_KEY)
