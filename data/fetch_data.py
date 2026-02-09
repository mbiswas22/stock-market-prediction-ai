import yfinance as yf
 
def fetch_stock_data(ticker="AAPL", period="5y"):
    df = yf.download(ticker, period=period)
    df.dropna(inplace=True)
    return df
 
if __name__ == "__main__":
    df = fetch_stock_data()
    df.to_csv("data/raw_stock_data.csv")
