import streamlit as st
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from model.predict import predict_trend
from rag.rag_chain import get_rag_chain
 
st.title("📈 Stock Trend Predictor")
 
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