# DocuMind AI: LangChain-Powered Document QA

## Prerequisites
- Python 3.9+
- pip

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Set up environment variables

Create a `.env` file in the project root (or backend directory) with your LLM API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

## 3. Start the backend (FastAPI)

```bash
uvicorn backend.main:app --reload
```

This will start the backend at `http://localhost:8000`.

## 4. Start the frontend (Streamlit)

In a new terminal:

```bash
streamlit run frontend/app.py
```

This will open the web UI in your browser.

## Usage
- Upload a PDF document.
- Ask questions about the document in the UI.

---

### Troubleshooting
- Make sure both backend and frontend are running.
- If you change the backend port, update `API_URL` in `frontend/app.py` or set the `API_URL` environment variable. 