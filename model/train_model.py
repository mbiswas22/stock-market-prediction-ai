import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from joblib import dump
 
df = pd.read_csv("data/features.csv")
 
X = df[["MA20", "MA50", "Return", "Volume"]]
y = df["Target"]
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)
 
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
 
dump(model, "model/model.pkl")
