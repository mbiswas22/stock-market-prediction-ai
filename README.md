## Stock Trend Predictor (Educational Project)

### Requirements

- Python 3.12 or later

### Features

- ML-based trend prediction
- Explainable AI using RAG
- Interactive chatbot with stock analysis tools
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

### UI Screenshot

<img width="2554" height="1201" alt="image" src="https://github.com/user-attachments/assets/923d57a2-34eb-4aa8-a311-4d18cba5631e" />
