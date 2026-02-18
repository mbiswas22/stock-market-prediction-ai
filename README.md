## Stock Trend Predictor + AI Analyst (Educational Project)

### Requirements

- Python 3.12 or later
- Finnhub API Key (free tier available at https://finnhub.io/)

### Features

- ML-based trend prediction with RSI & MACD indicators
- **Multi-Ticker Support** - Separate data files for AAPL, MSFT, TSLA, GOOGL, AMZN with dynamic loading
- **Realized Volatility Analysis** - 30/60/90 day rolling volatility trends with quantitative insights
- 3-Agent Intelligence System:
  - News Ingestion Agent
  - Earnings & Event Awareness Agent
  - Sentiment + Indicator Explanation Agent
- **Interactive AI Chatbot** with 7 agent tools:
  - 💰 Real-time stock prices
  - 🏢 Company information
  - 📰 Latest news from Finnhub
  - 📅 Earnings calendar
  - 📊 Sentiment analysis
  - 📈 Historical price data
  - 📧 Email stock reports (SendGrid)
- Three-tab Streamlit UI (Volatility Analysis | Prediction | Chatbot)
- Explainable AI using RAG
- Free-tier friendly with smart caching

### Run Instructions

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup API keys
# Edit .env and add your FINNHUB_API_KEY
# Optional: Add SENDGRID_API_KEY and EMAIL_USER for email reports

# 4. Fetch and prepare data (creates separate files for each ticker)
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
│   └── finnhub_client.py        # Finnhub API integration
├── schemas/                     # Pydantic data models
│   └── agent_schemas.py
├── app/
│   ├── streamlit_app.py        # Two-page UI (Prediction | Chatbot)
│   └── chatbot.py               # AI chatbot with 6 agent tools
│   └── streamlit_app.py        # Three-page UI (Prediction | Volatility | Chatbot)
├── utils/
│   ├── volatility_analyzer.py  # Realized volatility calculations
│   └── tools.py
├── data/
│   ├── fetch_data.py            # Fetches data for all 5 tickers
│   ├── feature_engineering.py   # Includes RSI & MACD
│   ├── AAPL_raw.csv             # Raw data per ticker
│   ├── AAPL_features.csv        # Processed features per ticker
│   └── ... (MSFT, TSLA, GOOGL, AMZN)
├── model/
│   ├── train_model.py          # Handles 4-7 features
│   ├── predict.py
│   └── model.pkl
├── rag/
│   ├── build_vectorstore.py
│   └── rag_chain.py
└── .env                         # API keys (FINNHUB_API_KEY, SENDGRID_API_KEY, EMAIL_USER)
```

### Architecture

**Prediction Page - Stock Trend Analysis:**

- Ticker dropdown selector (AAPL, MSFT, TSLA, GOOGL, AMZN)
- Dynamic data loading from ticker-specific CSV files
- Model prediction (UP/DOWN)
- Confidence score
- Technical indicators: MA20, MA50, Return, Volume, RSI, MACD
- RSI visual indicators: 🐂 (>70), 🐻 (≤30)
- Optional price chart
- AI-powered insights with Finnhub integration

**Chatbot Page - Interactive AI Assistant:**

- 💬 Natural language query processing
- 🤖 7 specialized agent tools:
  - **Price Tool**: Real-time quotes with change %
  - **Info Tool**: Company profile and market cap
  - **News Tool**: Latest headlines from Finnhub API
  - **Earnings Tool**: Earnings calendar and EPS data
  - **Sentiment Tool**: AI-powered news sentiment analysis
  - **History Tool**: 30-day price statistics
  - **Email Tool**: Send comprehensive stock reports via SendGrid
- ⚡ Quick action buttons for common queries
- 📝 Example queries and help
- 💾 Chat history with session state
- 🎯 Smart ticker extraction from natural language

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

### Chatbot Agent Tools

**Tool 1 - Price Agent:**

- Real-time stock quotes using yfinance
- Shows current price with change % and dollar amount
- Triggers on: "price", "cost", "trading", "quote", "worth"

**Tool 2 - Info Agent:**

- Company profile and basic information
- Displays sector and market capitalization
- Triggers on: "info", "about", "company", "profile", "what"

**Tool 3 - News Agent:**

- Latest company news from Finnhub API (7 days)
- Shows top 3 headlines with sources
- Triggers on: "news", "headlines", "articles", "latest"

**Tool 4 - Earnings Agent:**

- Earnings calendar from Finnhub API (±30 days)
- EPS estimates and actual results
- Triggers on: "earnings", "eps", "report"

**Tool 5 - Sentiment Agent:**

- AI-powered sentiment analysis from news
- Analyzes positive/negative signals in headlines
- Triggers on: "sentiment", "feeling", "mood", "opinion"

**Tool 6 - History Agent:**

- 30-day price statistics using yfinance
- Shows high, low, and average prices
- Triggers on: "history", "past", "trend", "stats"

**Tool 7 - Email Agent:**

- Generates comprehensive stock summary reports
- Sends via SendGrid API (requires verified sender email)
- Includes price, company info, history, sentiment, news, and earnings
- Triggers on: "email", "send", "mail"
- Falls back to report preview if SendGrid not configured

### Data Management

**Multi-Ticker Architecture:**

- Each ticker has separate raw and features CSV files
- `fetch_data.py` downloads 5 years of data for all tickers
- `feature_engineering.py` processes each ticker independently
- Streamlit app dynamically loads data based on dropdown selection
- Supported tickers: AAPL, MSFT, TSLA, GOOGL, AMZN

**Email Configuration (Optional):**

- Requires SendGrid API key (free tier available)
- Set `SENDGRID_API_KEY` and `EMAIL_USER` in .env
- Sender email must be verified at https://app.sendgrid.com/settings/sender_auth
- If not configured, email tool shows report preview instead
