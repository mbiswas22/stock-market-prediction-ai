import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]
for ticker in tickers:
 df = pd.read_csv(f"data/{ticker}_features.csv")

# Base features
feature_cols = ["MA20", "MA50", "Return", "Volume"]

# Add RSI and MACD if they exist
if "RSI" in df.columns:
    feature_cols.append("RSI")
if "MACD" in df.columns:
    feature_cols.append("MACD")
if "MACD_Hist" in df.columns:
    feature_cols.append("MACD_Hist")

X = df[feature_cols]
y = df["Target"]
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)
 
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"✅ Model trained with features: {feature_cols}")
print(f"✅ Test accuracy: {accuracy:.2%}")
 
dump(model, "model/model.pkl")
print("✅ Model saved to model/model.pkl")
