import yfinance as yf
 
def fetch_stock_data(ticker="AAPL", period="5y"):
    df = yf.download(ticker, period=period)
    df.dropna(inplace=True)
    return df
 
if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]
    for ticker in tickers:
        print(f"Fetching {ticker}...")
        df = fetch_stock_data(ticker)
        df.to_csv(f"data/{ticker}_raw.csv")
        print(f"✅ {ticker} data saved")
