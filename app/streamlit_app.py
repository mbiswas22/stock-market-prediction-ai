"""
Stock Trend Predictor with AI Intelligence System
Two-column UI: Prediction + Technicals | News & Sentiment Intelligence
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

st.title("📈 Stock Trend Predictor + AI Analyst")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["Prediction", "Chatbot"])

if page == "Prediction":

    # Ticker selection
    ticker = st.selectbox("Select Stock", ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"])

    # Load features data
    try:
        df = pd.read_csv("data/features.csv")
    except FileNotFoundError:
        st.error("❌ features.csv not found. Please run feature_engineering.py first.")
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

    # ============================================================================
    # LEFT WINDOW - Prediction & Technicals
    # ============================================================================
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
            st.metric("MA20", f"{ma20:.2f}")
            st.metric("Return", f"{ret:.4f}")
        
        with col2:
            st.metric("MA50", f"{ma50:.2f}")
            st.metric("Volume", f"{vol:,.0f}")
        
        # RSI indicator with emoji
        if "RSI" in df.columns:
            rsi = latest["RSI"].values[0]
            if rsi > 70:
                rsi_indicator = "🐂"  # Bull
            elif rsi <= 30:
                rsi_indicator = "🐻"  # Bear
            else:
                rsi_indicator = "—"
            
            st.metric("RSI", f"{rsi:.2f} {rsi_indicator}")
        
        # MACD
        if "MACD" in df.columns:
            macd = latest["MACD"].values[0]
            st.metric("MACD", f"{macd:.4f}")
        
        # Optional: Line chart
        if st.checkbox("Show Price Chart"):
            chart_data = df[["Close", "MA20", "MA50"]].tail(100)
            st.line_chart(chart_data)

    # ============================================================================
    # RIGHT WINDOW - News & Sentiment Intelligence
    # ============================================================================
    with col_news:
        st.header("📰 News & Sentiment Intelligence")
        
        # Check if API key exists
        api_key_exists = os.getenv("FINNHUB_API_KEY") is not None
        
        if not api_key_exists:
            st.warning("⚠️ FINNHUB_API_KEY not found in .env file. Intelligence features disabled.")
            st.info("Get a free API key at https://finnhub.io/ and add it to your .env file.")
        
        # UPDATED SECTION - Button renamed from "Run Intelligence" to "Generate Insights"
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
                # UPDATED SECTION - All sections converted to collapsible expanders
                
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
#Chat Bot
elif page == "Chatbot":
    st.header("🤖 AI Stock Analysis Chatbot")
    st.write("Powered by Finnhub API - Get real-time news, earnings, and sentiment analysis!")
    
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
        if st.button("📧 Send AAPL Report"):
            if email_input:
                import os
                api_key = os.getenv('SENDGRID_API_KEY')
                sender = os.getenv('EMAIL_USER')
                result = AGENT_TOOLS['email']("AAPL", email_input, api_key, sender)
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
    except:
        st.caption("⚠️ Market data unavailable")