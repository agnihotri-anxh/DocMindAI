import streamlit as st
import requests
import os

# Set page to wide layout
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Get API URL from environment variable or use default
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# --- Light Theme CSS with Tabs ---
st.markdown(
    """
    <style>
    /* Light theme with soft colors */
    body {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #334155;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
    }
    
    .header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
    }
    
    .header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 2;
    }
    
    .header p {
        font-size: 1.3rem;
        color: #64748b;
        margin: 0 auto;
        max-width: 700px;
        line-height: 1.6;
        font-weight: 400;
        position: relative;
        z-index: 2;
    }
    
    /* Tab styling */
    .tab-container {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        overflow: hidden;
    }
    
    .tab-buttons {
        display: flex;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .tab-button {
        flex: 1;
        padding: 1.5rem 2rem;
        background: transparent;
        border: none;
        font-size: 1.1rem;
        font-weight: 600;
        color: #64748b;
        cursor: pointer;
        transition: all 0.3s ease;
        border-bottom: 3px solid transparent;
    }
    
    .tab-button:hover {
        background: #f1f5f9;
        color: #3b82f6;
    }
    
    .tab-button.active {
        background: white;
        color: #3b82f6;
        border-bottom-color: #3b82f6;
    }
    
    .tab-content {
        padding: 2.5rem;
        display: none;
    }
    
    .tab-content.active {
        display: block;
    }
    
    /* Card styling */
    .card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }
    
    .card h2 {
        color: #1e293b;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .card p {
        color: #64748b;
        margin-bottom: 1.5rem;
        line-height: 1.7;
        font-size: 1.1rem;
    }
    
    /* Upload section */
    .upload-section {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        border: 2px solid #bae6fd;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .upload-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 1rem 2.5rem !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: 3.5rem !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        font-size: 1.1rem !important;
        background: white !important;
        color: #1e293b !important;
        height: 3.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    .stSelectbox > div > div > div {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        background: white !important;
        color: #1e293b !important;
        height: 3.5rem !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        height: 3.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Message styling */
    .message {
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 500;
        font-size: 1.1rem;
        text-align: center;
        border: 1px solid;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message.success {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        border-color: #86efac;
    }
    
    .message.error {
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
        color: #dc2626;
        border-color: #fca5a5;
    }
    
    .message.info {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        border-color: #93c5fd;
    }
    
    /* Summary and content styling */
    .summary-text {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        line-height: 1.8;
        color: #1e293b;
        font-size: 1.1rem;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .question-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
        font-size: 1.1rem;
        color: #065f46;
        font-weight: 500;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header h1 { font-size: 2.5rem; }
        .tab-button { padding: 1rem; font-size: 1rem; }
        .card { padding: 1.5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown(
    """
    <div class="header">
        <h1>🧠📋 DocuMind AI</h1>
        <p>Transform your documents into intelligent insights with advanced AI analysis. Upload PDFs and TXT files to get comprehensive summaries, detailed answers, and interactive learning challenges.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Tab Navigation ---
tab1, tab2, tab3, tab4 = st.tabs(["📁 Document Upload", "💬 Ask Questions", "🎯 Learning Challenges", "⚙️ Document Management"])

# --- Tab 1: Document Upload ---
with tab1:
    st.markdown(
        """
        <div class="upload-section">
            <h2 style="color: #1e293b; font-size: 1.8rem; margin-bottom: 1rem; position: relative; z-index: 1;">📄 Upload Your Document</h2>
            <p style="color: #64748b; font-size: 1.1rem; position: relative; z-index: 1;">Select your document and customize the summary length to get started</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF or TXT file", 
            type=["pdf", "txt"],
            help="Supported formats: PDF, TXT"
        )
    
    with col2:
        summary_words = st.selectbox(
            "Summary Length:",
            options=[150, 250, 400, 600, 800],
            format_func=lambda x: f"{x} words",
            help="Choose summary detail level"
        )
    
    with col3:
        if uploaded_file and st.button("🚀 Upload & Generate Summary", use_container_width=True):
            with st.spinner("Processing your document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                url = f"{API_URL}/upload-document?max_words={summary_words}"
                resp = requests.post(url, files=files)
                
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state["document_id"] = data["document_id"]
                    st.session_state["summary"] = data["summary"]
                    st.session_state["filename"] = data["filename"]
                    
                    st.markdown(
                        """
                        <div class="message success">
                            ✅ Document processed successfully! You can now ask questions and generate challenges.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div class="message error">
                            ❌ Upload failed. Please try again.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    # Show summary if document is uploaded
    if "summary" in st.session_state:
        st.markdown(
            f"""
            <div class="card">
                <h2>📋 Document Summary</h2>
                <p><strong>File:</strong> {st.session_state['filename']}</p>
                <div class="summary-text">{st.session_state["summary"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- Tab 2: Ask Questions ---
with tab2:
    if "document_id" not in st.session_state:
        st.markdown(
            """
            <div class="card">
                <h2>📝 No Document Uploaded</h2>
                <p>Please upload a document first to start asking questions. Go to the "Document Upload" tab to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="card">
                <h2>🤔 Ask Questions About Your Document</h2>
                <p>Ask any question about the uploaded document and get detailed, AI-powered answers</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        question = st.text_input(
            "Your question:", 
            key="question_input", 
            placeholder="e.g., What are the main findings? What methodology was used?"
        )
        
        if st.button("🔍 Get Answer", use_container_width=True):
            with st.spinner("Analyzing your question..."):
                payload = {"question": question, "document_id": st.session_state["document_id"]}
                resp = requests.post(f"{API_URL}/ask-question", json=payload)
                
                if resp.status_code == 200:
                    data = resp.json()
                    st.markdown(
                        f"""
                        <div class="card">
                            <h2>💡 AI Answer</h2>
                            <div class="summary-text">{data["answer"]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div class="message error">
                            ❌ Error getting answer. Please try again.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# --- Tab 3: Learning Challenges ---
with tab3:
    if "document_id" not in st.session_state:
        st.markdown(
            """
            <div class="card">
                <h2>📝 No Document Uploaded</h2>
                <p>Please upload a document first to generate learning challenges. Go to the "Document Upload" tab to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="card">
                <h2>🧠 Test Your Understanding</h2>
                <p>Generate AI-powered questions to test your knowledge of the document content</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        if st.button("🎲 Generate Challenge Questions", use_container_width=True):
            with st.spinner("Creating learning challenges..."):
                resp = requests.get(f"{API_URL}/generate-challenges/{st.session_state['document_id']}")
                if resp.status_code == 200:
                    st.session_state["challenge_questions"] = resp.json()["challenges"]
                    st.markdown(
                        """
                        <div class="message success">
                        ✅ Challenge questions generated! Answer them below to test your understanding.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div class="message error">
                            ❌ Error generating challenges. Please try again.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        if "challenge_questions" in st.session_state:
            for i, q in enumerate(st.session_state["challenge_questions"]):
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="question-card">
                            <strong>Question {i+1}:</strong> {q}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                user_answer = st.text_input(f"Your answer to Question {i+1}:", key=f"ans_{i}")
                
                if st.button(f"✅ Check Answer {i+1}", key=f"check_{i}"):
                    with st.spinner("Evaluating your answer..."):
                        payload = {
                            "answer": user_answer, 
                            "question": q, 
                            "document_id": st.session_state["document_id"]
                        }
                        resp2 = requests.post(f"{API_URL}/evaluate-challenge", json=payload)
                        
                        if resp2.status_code == 200:
                            st.markdown(
                                f"""
                                <div class="message info">
                                    <strong>AI Feedback:</strong> {resp2.json()["feedback"]}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                """
                                <div class="message error">
                                    ❌ Error evaluating answer. Please try again.
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

# --- Tab 4: Document Management ---
with tab4:
    if "document_id" not in st.session_state:
        st.markdown(
            """
            <div class="card">
                <h2>📂 No Document to Manage</h2>
                <p>Upload a document first to access management options. Go to the "Document Upload" tab to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="card">
                <h2>📂 Document Management</h2>
                <p>Manage your uploaded document and system settings</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                f"""
                <div class="card">
                    <h2>📄 Current Document</h2>
                    <p><strong>Filename:</strong> {st.session_state.get('filename', 'Unknown')}</p>
                    <p><strong>Document ID:</strong> {st.session_state.get('document_id', 'Unknown')}</p>
                    <p><strong>Status:</strong> ✅ Active</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with col2:
            st.markdown(
                """
                <div class="card">
                    <h2>🗑️ Remove Document</h2>
                    <p>Delete the current document to upload a new one</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            if st.button("🗑️ Delete Current Document", use_container_width=True):
                resp = requests.delete(f"{API_URL}/documents/{st.session_state['document_id']}")
                if resp.status_code == 200:
                    st.markdown(
                        """
                        <div class="message success">
                            ✅ Document deleted successfully. You can now upload a new document.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.markdown(
                        """
                        <div class="message error">
                            ❌ Error deleting document. Please try again.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# --- Footer ---
st.markdown(
    """
    <div style="text-align: center; margin-top: 4rem; padding: 3rem; color: #64748b; background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">
        <p style="font-weight: 700; margin-bottom: 0.5rem; font-size: 1.3rem; color: #1e293b;">🧠📋 DocuMind AI</p>
        <p style="font-size: 1.1rem; color: #475569;">Powered by Advanced AI Technology</p>
        <p style="font-size: 1rem; margin-top: 0.5rem; color: #94a3b8;">Transform your research workflow with intelligent document analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
) 