# Quick Reference Card

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Setup environment
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 2. Get API key from https://finnhub.io/ (free)
copy .env.example .env
# Add your FINNHUB_API_KEY to .env

# 3. Prepare data & model
python data/fetch_data.py
python data/feature_engineering.py
python model/train_model.py
python rag/build_vectorstore.py

# 4. Run
streamlit run app/streamlit_app.py
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `agents/orchestrator.py` | Coordinates 3 agents |
| `services/finnhub_client.py` | API client with retry logic |
| `app/streamlit_app.py` | Two-column UI |
| `data/feature_engineering.py` | RSI & MACD calculation |
| `model/train_model.py` | RandomForest with 4-7 features |

## 🤖 Agent System

```python
# Usage example
from agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
report = orchestrator.run_intelligence(
    ticker="AAPL",
    prediction="UP 📈",
    indicators={"MA20": 150.0, "RSI": 65.0, ...}
)

print(report.news.top_headlines)
print(report.earnings.event_risk_level)
print(report.sentiment.explanation_markdown)
```

## 📊 Technical Indicators

| Indicator | Formula | Interpretation |
|-----------|---------|----------------|
| **RSI** | (Avg Gain / Avg Loss) | >70: Overbought 🐂<br>≤30: Oversold 🐻 |
| **MACD** | EMA(12) - EMA(26) | Positive: Bullish<br>Negative: Bearish |
| **MA20** | 20-day moving avg | Short-term trend |
| **MA50** | 50-day moving avg | Long-term trend |

## 🎯 Event Risk Levels

| Level | Condition | Days from Earnings |
|-------|-----------|-------------------|
| 🔴 **HIGH** | Imminent volatility | -2 to +3 days |
| 🟠 **MEDIUM** | Moderate risk | -7 to +14 days |
| 🟢 **LOW** | Normal conditions | Outside risk window |

## 🔧 Common Customizations

### Add New Ticker
```python
# app/streamlit_app.py, line ~30
ticker = st.selectbox("Select Stock", ["AAPL", "MSFT", "TSLA", "YOUR_TICKER"])
```

### Adjust Cache Duration
```python
# app/streamlit_app.py, line ~20
@st.cache_data(ttl=900)  # 900 sec = 15 min
```

### Modify Sentiment Keywords
```python
# agents/sentiment_indicator_agent.py, line ~10
POSITIVE_KEYWORDS = ["beat", "growth", "upgrade", ...]
NEGATIVE_KEYWORDS = ["miss", "lawsuit", "downgrade", ...]
```

### Change RSI Thresholds
```python
# app/streamlit_app.py, line ~90
if rsi > 70:  # Change to 75 for stricter overbought
    rsi_indicator = "🐂"
elif rsi <= 30:  # Change to 25 for stricter oversold
    rsi_indicator = "🐻"
```

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| `FINNHUB_API_KEY not found` | Create .env file with API key |
| `features.csv not found` | Run `python data/feature_engineering.py` |
| `model.pkl not found` | Run `python model/train_model.py` |
| Rate limit (429) | Wait 1 minute, results cached 15 min |
| No headlines | Try different ticker (AAPL has most news) |

## 📈 Performance Tips

1. **First run is slow** - Models loading (~5-10 sec)
2. **Use caching** - Results cached 15 minutes
3. **Avoid spam clicking** - Intelligence button has rate limits
4. **Free tier limits** - 60 API calls/minute on Finnhub

## 🔍 Code Structure

```
User Input → Prediction Model → Intelligence Button
                                        ↓
                                  Orchestrator
                                        ↓
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
              News Agent        Earnings Agent      Sentiment Agent
                    ↓                   ↓                   ↓
              Finnhub API        Finnhub API        Rule-based Logic
                    ↓                   ↓                   ↓
                    └───────────────────┴───────────────────┘
                                        ↓
                              Intelligence Report
                                        ↓
                                  Display in UI
```

## 📚 Documentation Files

- **README.md** - Project overview & features
- **SETUP_GUIDE.md** - Detailed setup instructions
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **QUICK_REFERENCE.md** - This file

## ⚠️ Important Notes

- **Not financial advice** - Educational purposes only
- **Free tier friendly** - No paid services required
- **No autonomous trading** - Manual analysis tool only
- **Cached results** - 15-minute TTL to reduce API usage
- **Rule-based sentiment** - No heavy ML models

## 🎓 Learning Resources

- Finnhub API Docs: https://finnhub.io/docs/api
- Streamlit Docs: https://docs.streamlit.io/
- RSI Explained: https://www.investopedia.com/terms/r/rsi.asp
- MACD Explained: https://www.investopedia.com/terms/m/macd.asp

## 💡 Next Steps

1. ✅ Run the application
2. ✅ Test with different tickers
3. ✅ Observe sentiment vs prediction
4. ✅ Check event risk before decisions
5. ✅ Experiment with custom keywords
6. ✅ Add your favorite tickers

---

**Version:** 2.0 (3-Agent Intelligence System)  
**Last Updated:** 2025  
**Python:** 3.12+  
**License:** Educational Use
