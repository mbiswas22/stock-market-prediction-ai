import pandas as pd

def add_features(df):
    # Ensure numeric columns
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Feature engineering
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["Return"] = df["Close"].pct_change()

    # Target: next-day direction
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    df.dropna(inplace=True)
    return df

if __name__ == "__main__":
    df = pd.read_csv("data/raw_stock_data.csv")

    # Drop accidental index column if present
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    df = add_features(df)
    df.to_csv("data/features.csv", index=False)
    print("✅ Feature engineering complete")