# 🧠📋 DocuMind AI

A powerful AI-powered document analysis and interaction system that transforms your documents into intelligent insights. Upload PDFs and TXT files to get comprehensive summaries, detailed answers, and interactive learning challenges.

## 🌐 Live Demo

**Try it now:** [https://docmindai.onrender.com](https://docmindai.onrender.com)

## ✨ Features

- **📄 Document Upload**: Support for PDF and TXT files with intelligent text extraction
- **🤔 AI-Powered Q&A**: Ask any question about your documents and get detailed, contextual answers
- **🎯 Learning Challenges**: Generate interactive questions to test your understanding
- **📝 Smart Summaries**: Customizable document summaries (150-800 words)
- **🧠 Advanced AI**: Powered by Groq API for fast, intelligent document analysis
- **🎨 Modern UI**: Beautiful, responsive interface with tabbed navigation
- **🔒 Secure**: Environment-based API key management

## 🚀 Quick Start

### Option 1: Use the Live Demo
Visit [https://docmindai.onrender.com](https://docmindai.onrender.com) and start analyzing documents immediately!

### Option 2: Local Development

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/agnihotri-anxh/DocMindAI.git
   cd DocMindAI
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Create a `.env` file in the root directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the Application**:
   ```bash
   # Start the FastAPI backend
   cd backend
   python main.py
   
   # In another terminal, start the Streamlit frontend
   cd frontend
   streamlit run app.py
   ```

5. **Access the Application**:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Groq API for fast AI inference
- Streamlit for the web framework
- FastAPI for the backend API
- Render for deployment platform

---

**Transform your research workflow with intelligent document analysis!** 🧠✨ 