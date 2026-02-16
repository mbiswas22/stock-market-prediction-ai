import streamlit as st
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from model.predict import predict_trend
from rag.rag_chain import get_rag_chain
from app.chatbot import get_stock_price, get_stock_info, get_stock_history
 
st.title("📈 Stock Trend Predictor")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["Prediction", "Chatbot"])

if page == "Prediction":
    st.header("Stock Trend Prediction")
    
    ticker = st.selectbox("Select Stock", ["AAPL", "MSFT", "TSLA"])
    
    df = pd.read_csv("data/features.csv")
    latest = df.tail(1)[["MA20", "MA50", "Return", "Volume"]]
    
    trend, confidence = predict_trend(latest)

    st.subheader(f"Prediction: {trend}")
    st.write(f"Confidence: {confidence}%")
    
    if st.button("Explain Prediction"):
        chain = get_rag_chain()
        result = chain.invoke({"input": "Explain the stock trend using technical indicators"})
        st.info(result["answer"])

elif page == "Chatbot":
    st.header("Stock Analysis Chatbot")
    st.write("Ask questions about stocks using natural language!")
    
    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Get AAPL Price"):
            st.info(get_stock_price("AAPL"))
    
    with col2:
        if st.button("Get MSFT Info"):
            st.info(get_stock_info("MSFT"))
    
    with col3:
        if st.button("Get TSLA History"):
            st.info(get_stock_history("TSLA"))
    
    # Chat interface
    st.subheader("Chat with Agent")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    user_input = st.chat_input("Ask about stocks (e.g., 'What is the price of AAPL?')")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Use tools directly for simple queries
                if "price" in user_input.lower():
                    ticker = user_input.upper().split()[-1].replace("?", "")
                    response = get_stock_price(ticker)
                elif "info" in user_input.lower() or "about" in user_input.lower():
                    ticker = user_input.upper().split()[-1].replace("?", "")
                    response = get_stock_info(ticker)
                elif "history" in user_input.lower():
                    ticker = user_input.upper().split()[-1].replace("?", "")
                    response = get_stock_history(ticker)
                else:
                    response = "I can help you with stock prices, info, and history. Try asking: 'What is the price of AAPL?'"
                
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})