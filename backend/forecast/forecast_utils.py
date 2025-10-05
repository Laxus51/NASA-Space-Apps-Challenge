# forecast_utils.py
import numpy as np
import pandas as pd
import joblib
from datetime import datetime

# Horizons we trained
HORIZONS = [1, 6, 12, 24]

def load_models():
    """Load trained models from disk into a dict."""
    import os
    models = {}
    # Get the directory where this script is located (forecast directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for h in HORIZONS:
        filename = f"forecast_{h}h.pkl"
        filepath = os.path.join(script_dir, filename)
        models[h] = joblib.load(filepath)
    return models


def make_features(latest_datetime, pm25, t2m, wind_speed, relative_humidity):
    """Build feature vector from latest observation."""
    dt = pd.to_datetime(latest_datetime)

    hour = dt.hour
    dow = dt.dayofweek

    return pd.DataFrame([{
        "pm25": pm25,
        "t2m": t2m,
        "wind_speed": wind_speed,
        "relative_humidity": relative_humidity,
        "hour_sin": np.sin(2 * np.pi * hour / 24),
        "hour_cos": np.cos(2 * np.pi * hour / 24),
        "dow_sin": np.sin(2 * np.pi * dow / 7),
        "dow_cos": np.cos(2 * np.pi * dow / 7),
    }])


def forecast_pm25(models, latest_datetime, pm25, t2m, wind_speed, relative_humidity):
    """Run forecasts for all horizons using the trained models."""
    features = make_features(latest_datetime, pm25, t2m, wind_speed, relative_humidity)

    predictions = {}
    for h in HORIZONS:
        pred = models[h].predict(features)[0]
        predictions[f"+{h}h"] = round(pred, 2)

    return predictions
