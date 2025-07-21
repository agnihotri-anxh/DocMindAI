# DocMind AI

A full-stack document Q&A and challenge generator powered by FastAPI (backend), Flask (frontend), and Groq LLM API.

## Features
- Upload PDF documents and get AI-generated summaries
- Ask questions about your document
- Generate and answer challenge questions
- All answers evaluated by an LLM

## Project Structure

```
backend/
  main.py            # FastAPI backend
  requirements.txt   # Backend dependencies
frontend/
  app.py             # Flask frontend
  requirements.txt   # Frontend dependencies
  templates/
    index.html       # Main UI template
LICENSE              # Apache 2.0 License
```

## Local Development

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <your-repo>
```

### 2. Set up your environment
- Create a `.env` file in the project root with:
  ```
  GROQ_API_KEY=your_groq_api_key_here
  ```

### 3. Start the backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend will run at `http://localhost:8000`.

### 4. Start the frontend
```bash
cd ../frontend
pip install -r requirements.txt
python app.py
```
Frontend will run at `http://localhost:5000`.



This project is licensed under the Apache License 2.0. See the LICENSE file for details. 
