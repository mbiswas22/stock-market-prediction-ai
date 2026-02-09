import pandas as pd
from joblib import load
 
model = load("model/model.pkl")
 
def predict_trend(latest_row):
    prob = model.predict_proba(latest_row)[0][1]
    trend = "UP 📈" if prob > 0.5 else "DOWN 📉"
    return trend, round(prob * 100, 2)