import pandas as pd
from joblib import load
from pathlib import Path

# Load model once at module level
model_path = Path(__file__).parent / "model.pkl"
model = load(model_path)
 
def predict_trend(latest_row):
    """
    Predict stock trend from latest features.
    Handles both old (4 features) and new (7 features) models.
    """
    prob = model.predict_proba(latest_row)[0][1]
    trend = "UP" if prob > 0.5 else "DOWN"
    confidence = round(prob * 100, 2) if prob > 0.5 else round((1 - prob) * 100, 2)
    return trend, confidence