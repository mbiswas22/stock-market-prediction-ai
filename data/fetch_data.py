import yfinance as yf
 
def fetch_stock_data(ticker="AAPL", period="5y"):
    df = yf.download(ticker, period=period)
    df.dropna(inplace=True)
    return df
 
if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "GE"]
    for ticker in tickers:
        print(f"Fetching {ticker}...")
        df = fetch_stock_data(ticker)
        df.reset_index(inplace=True)  # Convert Date index to column
        df.to_csv(f"data/{ticker}_raw.csv", index=False)
        print(f"✅ {ticker} data saved")
