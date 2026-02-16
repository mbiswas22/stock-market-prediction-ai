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
    
    # Run Intelligence button
    if st.button("🧠 Run Intelligence", type="primary", disabled=not api_key_exists):
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
            # Event Risk Badge
            st.subheader("🚨 Event Risk")
            
            risk_level = report.earnings.event_risk_level
            risk_colors = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}
            
            st.markdown(f"**Level:** :{risk_colors.get(risk_level, 'gray')}[{risk_level}]")
            st.caption(report.earnings.event_risk_reason)
            
            if report.earnings.earnings_date:
                st.caption(f"Earnings Date: {report.earnings.earnings_date}")
            
            st.divider()
            
            # Sentiment Badge
            st.subheader("📊 Sentiment Analysis")
            
            sentiment = report.sentiment.overall_sentiment
            sentiment_colors = {"Positive": "green", "Neutral": "gray", "Negative": "red"}
            
            st.markdown(f"**Sentiment:** :{sentiment_colors.get(sentiment, 'gray')}[{sentiment}]")
            st.caption(f"Score: {report.sentiment.sentiment_score:.2f}")
            
            st.divider()
            
            # Supportive Context (NEW)
            st.subheader("✅ Supportive Context")
            st.caption("Factors that may strengthen confidence in the model prediction")
            for item in report.sentiment.supportive_context:
                st.markdown(f"- {item}")
            
            st.divider()
            
            # Risk Factors (NEW)
            st.subheader("⚠️ Risk Factors")
            st.caption("Conditions that may reduce confidence or introduce uncertainty")
            for item in report.sentiment.risk_factors:
                st.markdown(f"- {item}")
            
            st.divider()
            
            # Confidence Impact Summary (NEW)
            st.subheader("📊 Confidence Impact Summary")
            st.info(report.sentiment.confidence_summary)
            
            st.divider()
            
            # Top 3 Headlines
            st.subheader("📰 Top Headlines")
            
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
            
            st.divider()
            
            # Legacy Explanation (kept for reference)
            with st.expander("📖 Detailed Technical Analysis"):
                st.markdown(report.sentiment.explanation_markdown)

st.divider()
st.caption("⚠️ Not financial advice. For educational purposes only.")