# GenAI Document Assistant

A powerful AI-powered document comprehension and interaction system that allows users to upload documents and engage in intelligent conversations about their content.

## Features

- **Document Upload**: Support for PDF and TXT files
- **Ask Anything Mode**: Free-form questions with contextual understanding
- **Challenge Me Mode**: Logic-based questions with evaluation and feedback
- **Auto Summary**: Concise document summaries (≤150 words)
- **Contextual Understanding**: All responses grounded in actual document content
- **Reference Citations**: Every answer includes document references

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the Application**:
   ```bash
   # Start the FastAPI backend
   python backend/main.py
   
   # In another terminal, start the Streamlit frontend
   streamlit run frontend/app.py
   ```

4. **Access the Application**:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

## Architecture

- **Backend**: FastAPI with document processing and AI integration
- **Frontend**: Streamlit for intuitive web interface
- **AI**: OpenAI GPT models for comprehension and reasoning
- **Document Processing**: PyPDF2 for PDF parsing and text extraction
- **Vector Storage**: ChromaDB for document embeddings and retrieval

## Usage

1. Upload a document (PDF or TXT)
2. View the auto-generated summary
3. Choose interaction mode:
   - **Ask Anything**: Ask free-form questions
   - **Challenge Me**: Answer logic-based questions and get feedback
4. All responses include document references and justifications 