"""
Stock Trend Predictor with AI Intelligence System
Four-tab UI: Dashboard | Volatility Analysis | Prediction | Chatbot
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from model.predict import predict_trend
from rag.rag_chain import get_rag_chain
from app.chatbot import get_stock_price, get_stock_info, get_stock_history, AGENT_TOOLS, process_query
from app.market_summary import get_market_summary
from agents.orchestrator import AgentOrchestrator
from utils.volatility_analyzer import analyze_stock_volatility

# Page config
st.set_page_config(page_title="Stock Trend Predictor", layout="wide")

# Cache the orchestrator
@st.cache_resource
def get_orchestrator():
    return AgentOrchestrator()

# Cache Finnhub results for 15 minutes
@st.cache_data(ttl=900)
def run_intelligence_cached(ticker, prediction, indicators, confidence):
    orchestrator = get_orchestrator()
    return orchestrator.run_intelligence(ticker, prediction, indicators, confidence)

st.title("📈 TrendPulse AI")

# Global ticker selection in sidebar
with st.sidebar:
    st.header("🎯 Stock Selection")
    selected_ticker = st.selectbox(
        "Select Stock",
        ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "GE"],
        key="global_ticker"
    )
    
    # Display prediction for selected ticker
    try:
        pred_df = pd.read_csv(f"data/{selected_ticker}_features.csv")
        pred_latest = pred_df.tail(1)
        
        # Determine features
        pred_base_features = ["MA20", "MA50", "Return", "Volume"]
        pred_optional_features = []
        if "RSI" in pred_df.columns:
            pred_optional_features.append("RSI")
        if "MACD" in pred_df.columns:
            pred_optional_features.append("MACD")
        if "MACD_Hist" in pred_df.columns:
            pred_optional_features.append("MACD_Hist")
        
        pred_all_features = pred_base_features + pred_optional_features
        pred_latest_features = pred_latest[pred_all_features]
        
        # Get prediction
        pred_trend, pred_confidence = predict_trend(pred_latest_features)
        
        st.divider()
        st.subheader("🔮 Prediction")
        
        if pred_trend == "UP":
            st.success(f"📈 **{pred_trend}**")
        else:
            st.error(f"📉 **{pred_trend}**")
        
        st.metric("Confidence", f"{pred_confidence}%")
        
    except Exception as e:
        st.caption("⚠️ Prediction unavailable")
    
    st.divider()

# Create Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "📈 Volatility Analysis",
    "📋 Prediction",
    "🤖 Chatbot"
])

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
with tab1:
    st.header("📊 Stock Market Dashboard")
    
    # Use global ticker selection
    dash_ticker = selected_ticker
    
    # Load data
    try:
        dash_df = pd.read_csv(f"data/{dash_ticker}_features.csv")
        
        # Check if Date column exists, otherwise use index
        if 'Date' in dash_df.columns:
            dash_df['Date'] = pd.to_datetime(dash_df['Date'])
            dash_df.set_index('Date', inplace=True)
        elif dash_df.index.name != 'Date':
            # If no Date column, try to parse the first column or index
            if pd.api.types.is_numeric_dtype(dash_df.index):
                # Reset index and try to find date column
                dash_df = dash_df.reset_index()
                if 'index' in dash_df.columns:
                    dash_df['Date'] = pd.to_datetime(dash_df['index'])
                    dash_df.set_index('Date', inplace=True)
                    dash_df.drop('index', axis=1, inplace=True, errors='ignore')
        
        # Display key metrics
        st.subheader(f"{dash_ticker} Key Metrics")
        latest_dash = dash_df.tail(1)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${latest_dash['Close'].values[0]:.2f}")
        with col2:
            st.metric("MA20", f"${latest_dash['MA20'].values[0]:.2f}")
        with col3:
            st.metric("MA50", f"${latest_dash['MA50'].values[0]:.2f}")
        with col4:
            if "RSI" in dash_df.columns:
                st.metric("RSI", f"{latest_dash['RSI'].values[0]:.2f}")
        
        st.divider()
        
        # Charts in 2 columns
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📈 Price & Moving Averages")
            price_data = dash_df[["Close", "MA20", "MA50"]].tail(180)
            st.line_chart(price_data)
            
            st.subheader("📊 Volume Trend")
            volume_data = dash_df[["Volume"]].tail(180)
            st.bar_chart(volume_data)
        
        with col_right:
            if "RSI" in dash_df.columns:
                st.subheader("📉 RSI Indicator")
                rsi_data = dash_df[["RSI"]].tail(180)
                st.line_chart(rsi_data)
            
            if "MACD" in dash_df.columns:
                st.subheader("🔄 MACD")
                macd_data = dash_df[["MACD", "MACD_Signal"]].tail(180)
                st.line_chart(macd_data)
        
        st.divider()
        
        # Returns distribution
        st.subheader("📊 Returns Distribution")
        returns_data = dash_df[["Return"]].tail(180)
        st.area_chart(returns_data)
        
    except FileNotFoundError:
        st.error(f"❌ {dash_ticker}_features.csv not found. Please run fetch_data.py and feature_engineering.py first.")

# ============================================================================
# VOLATILITY ANALYSIS PAGE
# ============================================================================
with tab2:
    st.header("📊 Realized Volatility Analysis")
    st.write("Quantitative equity analysis: 30/60/90 day rolling realized volatility trends")

     # Use global ticker selection
    s_ticker = selected_ticker
    
    ticker_input = st.text_input("Enter Stock Symbol", value=f"{s_ticker}").upper()
    
    if st.button("🔍 Analyze Volatility", type="primary"):
        with st.spinner(f"Analyzing {ticker_input} volatility patterns..."):
            try:
                fig, report = analyze_stock_volatility(ticker_input)
                st.pyplot(fig)
                st.markdown(report)
            except Exception as e:
                st.error(f"❌ Error analyzing {ticker_input}: {str(e)}")
                st.info("Please verify the ticker symbol and try again.")

# ============================================================================
# PREDICTION PAGE
# ============================================================================
with tab3:
    st.subheader("Prediction Result")

    # Use global ticker selection
    ticker = selected_ticker

    # Load features data for selected ticker
    try:
        df = pd.read_csv(f"data/{ticker}_features.csv")
    except FileNotFoundError:
        st.error(f"❌ {ticker}_features.csv not found. Please run fetch_data.py and feature_engineering.py first.")
        st.stop()

    # Get latest row
    latest = df.tail(1)

    # Determine which features to use
    base_features = ["MA20", "MA50", "Return", "Volume"]
    optional_features = []

    if "RSI" in df.columns:
        optional_features.append("RSI")
    if "MACD" in df.columns:
        optional_features.append("MACD")
    if "MACD_Hist" in df.columns:
        optional_features.append("MACD_Hist")

    all_features = base_features + optional_features
    latest_features = latest[all_features]

    # Create two columns
    col_pred, col_news = st.columns([1, 1])

    # LEFT WINDOW - Prediction & Technicals
    with col_pred:
        st.header("📈 Prediction & Technicals")
        
        st.markdown(f"**Ticker:** {ticker}")
        
        # Generate prediction
        trend, confidence = predict_trend(latest_features)
        
        # Display prediction
        st.markdown(f"### Prediction: {trend}")
        st.markdown(f"**Confidence:** {confidence}%")
        
        st.divider()
        
        # Display indicators
        st.subheader("Latest Indicators")
        
        ma20 = latest["MA20"].values[0]
        ma50 = latest["MA50"].values[0]
        ret = latest["Return"].values[0]
        vol = latest["Volume"].values[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("MA20", f"{ma20:.2f}", help="20-day moving average — average stock price over the past 20 trading days. Helps show short-term trend direction.")
            st.metric("Return", f"{ret:.4f}", help="Recent price change percentage. Positive means the stock gained value, negative means it declined.")
        
        with col2:
            st.metric("MA50", f"{ma50:.2f}", help="50-day moving average — average stock price over the past 50 trading days. Helps show medium-term trend direction.")
            st.metric("Volume", f"{vol:,.0f}", help="Number of shares traded in the latest period. Higher volume can indicate stronger buying or selling interest.")
        
        # RSI indicator with emoji
        if "RSI" in df.columns:
            rsi = latest["RSI"].values[0]
            if rsi > 70:
                rsi_indicator = "🐂"
            elif rsi <= 30:
                rsi_indicator = "🐻"
            else:
                rsi_indicator = "—"
            
            st.metric("RSI", f"{rsi:.2f} {rsi_indicator}", help="Relative Strength Index (0–100). Above 70 may indicate overbought conditions. Below 30 may indicate oversold conditions.")
        
        # MACD
        if "MACD" in df.columns:
            macd = latest["MACD"].values[0]
            st.metric("MACD", f"{macd:.4f}", help="Momentum indicator comparing two moving averages. Crossovers can suggest trend shifts.")
        
        # Optional: Line chart
        if st.checkbox("Show Price Chart"):
            chart_data = df[["Close", "MA20", "MA50"]].tail(100)
            st.line_chart(chart_data)

    # RIGHT WINDOW - News & Sentiment Intelligence
    with col_news:
        st.header("📰 News & Sentiment Intelligence")
        
        # Check if API key exists
        api_key_exists = os.getenv("FINNHUB_API_KEY") is not None
        
        if not api_key_exists:
            st.warning("⚠️ FINNHUB_API_KEY not found in .env file. Intelligence features disabled.")
            st.info("Get a free API key at https://finnhub.io/ and add it to your .env file.")
        
        if st.button("🧠 Generate Insights", type="primary", disabled=not api_key_exists):
            with st.spinner("Running AI agents..."):
                # Prepare indicators dict
                indicators = {
                    "MA20": ma20,
                    "MA50": ma50,
                    "Return": ret,
                    "Volume": vol
                }
                
                if "RSI" in df.columns:
                    indicators["RSI"] = latest["RSI"].values[0]
                if "MACD" in df.columns:
                    indicators["MACD"] = latest["MACD"].values[0]
                
                # Run intelligence system
                try:
                    report = run_intelligence_cached(ticker, trend, indicators, confidence)
                    
                    # Store in session state
                    st.session_state["intelligence_report"] = report
                    st.success("✅ Intelligence analysis complete!")
                except Exception as e:
                    st.error(f"❌ Error running intelligence: {str(e)}")
        
        # Display intelligence report if available
        if "intelligence_report" in st.session_state:
            report = st.session_state["intelligence_report"]
            
            with st.container(border=True):
                # Event Risk (AUTO-EXPANDED)
                with st.expander("🚨 Event Risk", expanded=True):
                    risk_level = report.earnings.event_risk_level
                    risk_colors = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}
                    
                    st.markdown(f"**Level:** :{risk_colors.get(risk_level, 'gray')}[{risk_level}]")
                    st.caption(report.earnings.event_risk_reason)
                    
                    if report.earnings.earnings_date:
                        st.caption(f"Earnings Date: {report.earnings.earnings_date}")
                
                # Sentiment Analysis (COLLAPSED)
                with st.expander("📊 Sentiment Analysis", expanded=False):
                    sentiment = report.sentiment.overall_sentiment
                    sentiment_colors = {"Positive": "green", "Neutral": "gray", "Negative": "red"}
                    
                    st.markdown(f"**Sentiment:** :{sentiment_colors.get(sentiment, 'gray')}[{sentiment}]")
                    st.caption(f"Score: {report.sentiment.sentiment_score:.2f}")
                
                # Supportive Context (COLLAPSED)
                with st.expander("✅ Supportive Context", expanded=False):
                    st.caption("Factors that may strengthen confidence in the model prediction")
                    for item in report.sentiment.supportive_context:
                        st.markdown(f"- {item}")
                
                # Risk Factors (COLLAPSED)
                with st.expander("⚠️ Risk Factors", expanded=False):
                    st.caption("Conditions that may reduce confidence or introduce uncertainty")
                    for item in report.sentiment.risk_factors:
                        st.markdown(f"- {item}")
                
                # Confidence Impact Summary (AUTO-EXPANDED)
                with st.expander("📊 Confidence Impact Summary", expanded=True):
                    st.info(report.sentiment.confidence_summary)
                
                # Top Headlines (COLLAPSED)
                with st.expander("📰 Top Headlines", expanded=False):
                    if report.news.top_headlines:
                        # Create dataframe for display
                        headlines_data = []
                        for h in report.news.top_headlines:
                            headlines_data.append({
                                "Datetime": h.datetime,
                                "Source": h.source,
                                "Tag": h.reason_tag.upper(),
                                "Headline": h.headline[:60] + "...",
                                "Link": f"[Open]({h.url})" if h.url else ""
                            })
                        
                        df_headlines = pd.DataFrame(headlines_data)
                        st.dataframe(df_headlines, use_container_width=True, hide_index=True)
                        
                        # Fallback: clickable links
                        st.markdown("**Full Headlines:**")
                        for h in report.news.top_headlines:
                            st.markdown(f"- [{h.source}] {h.headline} [Open]({h.url})")
                        
                        st.caption(f"Total headlines analyzed: {report.news.headline_count}")
                    else:
                        st.info("No recent headlines found.")
                
                # Detailed Technical Analysis (COLLAPSED)
                with st.expander("📖 Detailed Technical Analysis", expanded=False):
                    st.markdown(report.sentiment.explanation_markdown)

        st.divider()
        st.caption("⚠️ Not financial advice. For educational purposes only.")

# ============================================================================
# CHATBOT PAGE
# ============================================================================
with tab4:
    st.header("🤖 AI Stock Analysis Chatbot")
    st.write("Powered by Finnhub API - Get real-time news, earnings, and sentiment analysis!")

     # Use global ticker selection
    c_ticker = selected_ticker
    
    # Quick action buttons
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 AAPL Price"):
            st.info(AGENT_TOOLS['price']("AAPL"))
        if st.button("📰 AAPL News"):
            st.info(AGENT_TOOLS['news']("AAPL"))
    
    with col2:
        if st.button("🏢 MSFT Info"):
            st.info(AGENT_TOOLS['info']("MSFT"))
        if st.button("📅 MSFT Earnings"):
            st.info(AGENT_TOOLS['earnings']("MSFT"))
    
    with col3:
        if st.button("📈 TSLA History"):
            st.info(AGENT_TOOLS['history']("TSLA"))
        if st.button("📊 TSLA Sentiment"):
            st.info(AGENT_TOOLS['sentiment']("TSLA"))
    
    # Email tool button
    st.markdown("---")
    col_email1, col_email2 = st.columns([3, 1])
    with col_email1:
        email_input = st.text_input("📧 Email Address (for stock reports)", placeholder="your-email@example.com")
    with col_email2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"📧 Send {c_ticker} Report"):
            if email_input:
                import os
                api_key = os.getenv('SENDGRID_API_KEY')
                sender = os.getenv('EMAIL_USER')
                result = AGENT_TOOLS['email'](f"{c_ticker}", email_input, api_key, sender)
                st.info(result)
            else:
                st.warning("Please enter an email address")
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Chat with AI Agent")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Price & Info:**
        - "What is the price of AAPL?"
        - "Tell me about MSFT"
        
        **News & Sentiment:**
        - "Show me news for TSLA"
        - "Analyze sentiment for GOOGL"
        
        **Earnings & History:**
        - "When is NVDA earnings?"
        - "Show me AMZN history"
        
        **Email Reports:**
        - "Send AAPL report to user@example.com"
        - "Email MSFT summary to investor@company.com"
        """)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask about any stock (e.g., 'What is the price of AAPL?')")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Process query with agent
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing..."):
                response = process_query(user_input)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Sidebar with market summary
with st.sidebar:
    st.header("📊 Market Overview")
    
    try:
        market_data = get_market_summary()
        
        if market_data:
            st.caption("Top Stocks (Live)")
                
            for stock in market_data:
                ticker = stock['ticker']
                price = stock['price']
                change_pct = stock['change_pct']
                    
                if change_pct > 0:
                    st.markdown(f"**{ticker}** ${price:.2f} :green[↑ {change_pct:+.2f}%]")
                elif change_pct < 0:
                    st.markdown(f"**{ticker}** ${price:.2f} :red[↓ {change_pct:+.2f}%]")
                else:
                    st.markdown(f"**{ticker}** ${price:.2f} :gray[→ {change_pct:.2f}%]")
                
            st.caption("🔄 Updates every 5 min")
        else:
            st.info("Market data unavailable")
    except Exception as e:
        st.caption("⚠️ Market data unavailable")