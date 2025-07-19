# DocuMind AI: LangChain-Powered Document QA

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

<<<<<<< HEAD
This will open the web UI in your browser.

## Usage
- Upload a PDF document.
- Ask questions about the document in the UI.

---

### Troubleshooting
- Make sure both backend and frontend are running.
- If you change the backend port, update `API_URL` in `frontend/app.py` or set the `API_URL` environment variable. 
=======
## 🏗️ Architecture

- **Backend**: FastAPI with document processing and AI integration
- **Frontend**: Streamlit with modern, responsive UI design
- **AI Engine**: Groq API for high-speed inference and document analysis
- **Document Processing**: PyPDF2 for PDF parsing and text extraction
- **Security**: Environment-based API key management

## 🎯 How to Use

1. **Upload Document**: Choose a PDF or TXT file to analyze
2. **View Summary**: Get an AI-generated summary of your document
3. **Ask Questions**: Use the Q&A tab to ask specific questions about the content
4. **Take Challenges**: Generate learning questions to test your understanding
5. **Get Feedback**: Receive detailed AI feedback on your answers

## 🔧 Technology Stack

- **Backend**: FastAPI, Uvicorn, Python-multipart
- **Frontend**: Streamlit, Custom CSS
- **AI**: Groq API
- **Document Processing**: PyPDF2
- **Deployment**: Render (Backend & Frontend)

## 🌟 Key Features

### Document Analysis
- Multi-page PDF support
- Intelligent text extraction
- Configurable summary lengths
- Context-aware processing

### AI Integration
- Fast inference with Groq API
- Contextual question answering
- Intelligent challenge generation
- Real-time feedback and evaluation

### User Experience
- Modern, professional UI design
- Responsive layout with optimal spacing
- Tabbed interface for easy navigation
- Real-time processing feedback

## 🔒 Security

- API keys stored securely in environment variables
- No sensitive data committed to repository
- Secure deployment on Render platform
- Input validation and error handling

## 📦 Deployment

This application is deployed on Render:
- **Frontend**: Streamlit web service
- **Backend**: FastAPI web service
- **Environment Variables**: Secure API key management

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Groq API for fast AI inference
- Streamlit for the web framework
- FastAPI for the backend API
- Render for deployment platform

---

**Transform your research workflow with intelligent document analysis!** 🧠✨ 
>>>>>>> 309914eac995bd8822f3f2e85ee671d72f52bfae
