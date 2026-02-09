## Stock Trend Predictor (Educational Project)

### Features

- ML-based trend prediction
- Explainable AI using RAG
- Streamlit UI
- Free-tier friendly

### Run Instructions

```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
python data/fetch_data.py
python data/feature_engineering.py
python model/train_model.py
python rag/build_vectorstore.py
streamlit run app/streamlit_app.py
⚠️ Not financial advice.
```
