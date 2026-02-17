import yfinance as yf

def get_stock_price(ticker: str) -> str:
    """Get current stock price for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            return f"Current price of {ticker}: ${price:.2f}"
        return f"Could not fetch price for {ticker}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_stock_info(ticker: str) -> str:
    """Get basic stock information"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return f"{ticker} - {info.get('longName', 'N/A')}\nSector: {info.get('sector', 'N/A')}\nMarket Cap: ${info.get('marketCap', 0):,.0f}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_stock_history(ticker: str) -> str:
    """Get 30-day stock price history"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")
        if not data.empty:
            high = data['High'].max()
            low = data['Low'].min()
            avg = data['Close'].mean()
            return f"{ticker} 30-day stats:\nHigh: ${high:.2f}\nLow: ${low:.2f}\nAverage: ${avg:.2f}"
        return f"No history available for {ticker}"
    except Exception as e:
        return f"Error: {str(e)}"
