"""
Market summary utilities for sidebar display
"""
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_market_summary():
    """Get summary of top stock tickers"""
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
    summary = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                price = data['Close'].iloc[-1]
                change = data['Close'].iloc[-1] - data['Open'].iloc[0]
                change_pct = (change / data['Open'].iloc[0]) * 100
                
                summary.append({
                    'ticker': ticker,
                    'price': price,
                    'change': change,
                    'change_pct': change_pct
                })
        except:
            continue
    
    return summary
