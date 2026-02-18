## Stock Trend Predictor + AI Analyst (Educational Project)

### Requirements

- Python 3.12 or later
- Finnhub API Key (free tier available at https://finnhub.io/)

### Features

- ML-based trend prediction with RSI & MACD indicators
- **Realized Volatility Analysis** - 30/60/90 day rolling volatility trends with quantitative insights
- 3-Agent Intelligence System:
  - News Ingestion Agent
  - Earnings & Event Awareness Agent
  - Sentiment + Indicator Explanation Agent
- Three-page Streamlit UI (Prediction | Volatility Analysis | Chatbot)
- Explainable AI using RAG
- Interactive chatbot with stock analysis tools
- Free-tier friendly with smart caching

### Run Instructions

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Finnhub API key
copy .env.example .env
# Edit .env and add your FINNHUB_API_KEY

# 4. Fetch and prepare data
python data/fetch_data.py
python data/feature_engineering.py
python model/train_model.py
python rag/build_vectorstore.py

# 5. Run Streamlit app
streamlit run app/streamlit_app.py
```

⚠️ **Not financial advice. For educational purposes only.**

### UI Screenshot

<img width="2554" height="1201" alt="image" src="https://github.com/user-attachments/assets/923d57a2-34eb-4aa8-a311-4d18cba5631e" />

### Project Structure

```
stock-market-prediction-ai/
├── agents/                      # 3-Agent Intelligence System
│   ├── news_ingestion_agent.py
│   ├── earnings_event_agent.py
│   ├── sentiment_indicator_agent.py
│   └── orchestrator.py
├── services/                    # External API clients
│   └── finnhub_client.py
├── schemas/                     # Pydantic data models
│   └── agent_schemas.py
├── app/
│   └── streamlit_app.py        # Three-page UI (Prediction | Volatility | Chatbot)
├── utils/
│   ├── volatility_analyzer.py  # Realized volatility calculations
│   └── tools.py
├── data/
│   ├── fetch_data.py
│   └── feature_engineering.py  # Now includes RSI & MACD
├── model/
│   ├── train_model.py          # Handles 4-7 features
│   ├── predict.py
│   └── model.pkl
├── rag/
│   ├── build_vectorstore.py
│   └── rag_chain.py
└── .env                         # API keys (create from .env.example)
```

### Architecture

**Left Window - Prediction & Technicals:**

- Model prediction (UP/DOWN)
- Confidence score
- Technical indicators: MA20, MA50, Return, Volume, RSI, MACD
- RSI visual indicators: 🐂 (>70), 🐻 (≤30)
- Optional price chart

**Right Window - News & Sentiment Intelligence:**

- Event Risk Level (LOW/MEDIUM/HIGH)
- Sentiment Analysis (Positive/Neutral/Negative)
- Top 3 headlines with clickable links
- AI-generated explanation with citations

**Volatility Analysis Page:**

- 📊 30/60/90 day rolling realized volatility calculations
- 📈 Time-series visualization of volatility trends
- 🔍 Volatility trend interpretation (rising/falling)
- 📉 Market regime assessment (expansion/compression/stable)
- 🧮 Quantitative reasoning with percentile rankings
- 💡 Probabilistic options-style insights
- 📅 12-month historical analysis using free data (yfinance)
- ⚡ Annualized volatility metrics (√252 scaling)

### Performance Optimizations

- `@st.cache_data` for Finnhub API calls (15-min TTL)
- Model loaded once at module level
- No runtime FAISS rebuilding
- Rule-based sentiment (no heavy NLP models)
- Retry logic with exponential backoff

### Agent System Details

**Agent 1 - News Ingestion:**

- Fetches last 7 days of company news
- Tags by reason: earnings, product, analyst, macro, regulatory
- Deduplicates similar headlines
- Returns top 3 most relevant

**Agent 2 - Earnings & Event Awareness:**

- Checks earnings calendar (±30 days)
- Risk levels based on proximity:
  - HIGH: ±3 days from earnings
  - MEDIUM: 4-14 days or last week
  - LOW: Otherwise

**Agent 3 - Sentiment + Indicator Explanation:**

- Rule-based sentiment scoring
- Generates markdown explanation
- Inline citations from top headlines
- Combines news + technicals + prediction
