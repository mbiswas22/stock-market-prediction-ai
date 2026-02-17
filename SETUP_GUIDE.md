# Setup and Usage Guide

## Initial Setup

### 1. Environment Setup

```bash
# Clone or navigate to project directory
cd stock-market-prediction-ai

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Finnhub API Key

1. Visit https://finnhub.io/
2. Sign up for a free account
3. Copy your API key from the dashboard
4. Free tier includes: 60 API calls/minute

### 3. Configure Environment Variables

```bash
# Copy example file
copy .env.example .env

# Edit .env file and add your key:
FINNHUB_API_KEY=your_actual_api_key_here
```

### 4. Prepare Data and Model

```bash
# Fetch stock data (uses yfinance)
python data/fetch_data.py

# Generate features (MA20, MA50, RSI, MACD, etc.)
python data/feature_engineering.py

# Train RandomForest model
python model/train_model.py

# Build RAG vectorstore (optional, for legacy explain feature)
python rag/build_vectorstore.py
```

### 5. Run Application

```bash
streamlit run app/streamlit_app.py
```

The app will open in your browser at http://localhost:8501

## Using the Application

### Main Interface

**Left Column - Prediction & Technicals:**
1. Select a stock ticker (AAPL, MSFT, TSLA, GOOGL, AMZN)
2. View prediction (UP 📈 or DOWN 📉)
3. Check confidence percentage
4. Review technical indicators
5. Optional: Enable price chart

**Right Column - News & Sentiment Intelligence:**
1. Click "🧠 Run Intelligence" button
2. Wait for agents to analyze (5-10 seconds)
3. Review:
   - Event Risk Level
   - Sentiment Analysis
   - Top 3 Headlines
   - AI Explanation

### Understanding the Output

**RSI Indicators:**
- 🐂 Bull: RSI > 70 (overbought)
- 🐻 Bear: RSI ≤ 30 (oversold)
- — Neutral: RSI between 30-70

**Event Risk Levels:**
- 🔴 HIGH: Earnings within ±3 days
- 🟠 MEDIUM: Earnings 4-14 days away
- 🟢 LOW: No immediate earnings risk

**Sentiment:**
- Positive: More positive keywords in headlines
- Negative: More negative keywords in headlines
- Neutral: Balanced or no strong signals

## Troubleshooting

### "FINNHUB_API_KEY not found"
- Ensure .env file exists in project root
- Check that FINNHUB_API_KEY is set correctly
- Restart Streamlit app after adding key

### "features.csv not found"
- Run: `python data/feature_engineering.py`
- Ensure data/raw_stock_data.csv exists first

### "model.pkl not found"
- Run: `python model/train_model.py`
- Ensure data/features.csv exists first

### Rate Limit Errors
- Free tier: 60 calls/minute
- App caches results for 15 minutes
- Wait a minute and try again

### No Headlines Showing
- Check if ticker has recent news
- Try a different ticker (AAPL usually has most news)
- Verify API key is valid

## Performance Notes

- First run may be slow (loading models)
- Subsequent runs are cached
- Intelligence results cached for 15 minutes
- Model loaded once at startup

## Development Tips

### Adding New Tickers
Edit `app/streamlit_app.py`:
```python
ticker = st.selectbox("Select Stock", ["AAPL", "MSFT", "YOUR_TICKER"])
```

### Adjusting Cache TTL
Edit `app/streamlit_app.py`:
```python
@st.cache_data(ttl=900)  # 900 seconds = 15 minutes
```

### Modifying Sentiment Keywords
Edit `agents/sentiment_indicator_agent.py`:
```python
POSITIVE_KEYWORDS = ["beat", "growth", ...]
NEGATIVE_KEYWORDS = ["miss", "lawsuit", ...]
```

## Architecture Overview

```
User Input (Ticker)
    ↓
Prediction Model (RandomForest)
    ↓
Intelligence Button Clicked
    ↓
Orchestrator
    ├── News Agent → Finnhub API
    ├── Earnings Agent → Finnhub API
    └── Sentiment Agent → Rule-based Analysis
    ↓
Combined Intelligence Report
    ↓
Display in UI
```

## File Responsibilities

- **agents/**: Simple Python modules (NOT autonomous loops)
- **services/**: External API clients with retry logic
- **schemas/**: Pydantic models for type safety
- **app/**: Streamlit UI with caching
- **data/**: Feature engineering with RSI/MACD
- **model/**: RandomForest training and prediction

## Next Steps

1. Experiment with different tickers
2. Observe how sentiment affects predictions
3. Check event risk before trading decisions
4. Compare technical indicators with news sentiment

Remember: This is for educational purposes only. Not financial advice.
