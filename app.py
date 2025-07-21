from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os
import tempfile
import logging
import re
import atexit

# --- Application Setup ---
load_dotenv()
app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
app.secret_key = os.urandom(24)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- API Keys & Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in environment variables.")

# --- In-memory Storage for Embeddings (loaded once) ---
MODEL_NAME = "sentence-transformers/paraphrase-TinyBERT-L6-v2"
embeddings = None
vectorstore = None

def initialize_embeddings():
    """Load the sentence transformer model into memory."""
    global embeddings
    if embeddings is None:
        logger.info(f"Loading sentence transformer model: {MODEL_NAME}...")
        embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            model_kwargs={"device": "cpu"}
        )
        logger.info("Model loaded successfully.")

# --- Helper Functions ---
def get_llm(model="llama3-8b-8192"):
    return ChatGroq(groq_api_key=GROQ_API_KEY, model=model)

# --- Main Frontend Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if 'doc_uploaded' not in session:
        session.clear() # Start fresh
        session['doc_uploaded'] = False

    challenge_mode = request.args.get("mode") == "challenge"
    answer = None

    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            # This is a UI-only action, the real upload happens via JS
            pass
        elif "question" in request.form:
            answer = ask_question_api().get_json().get('answer', 'Error.')
        elif "get_challenges" in request.form:
            generate_challenges_api()
        elif "submit_all_answers" in request.form:
            evaluate_all_answers_api()
            
    return render_template(
        "index.html",
        summary=session.get("summary"),
        doc_uploaded=session.get("doc_uploaded"),
        answer=answer,
        challenge_mode=challenge_mode,
        challenge_questions=session.get("challenge_questions", []),
        challenge_feedback=session.get("challenge_feedback", [])
    )

@app.route("/challenge")
def challenge():
    return redirect(url_for("index", mode="challenge"))

# --- API Routes (replaces the separate backend) ---
@app.route("/api/upload-document", methods=["POST"])
def upload_document_api():
    global vectorstore
    initialize_embeddings()

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp)
            tmp_path = tmp.name
        
        atexit.register(lambda: os.remove(tmp_path))

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)

        if not docs:
            return jsonify({"error": "Could not extract text from the document."}), 400
        
        vectorstore = Chroma.from_documents(docs, embeddings)
        session['doc_uploaded'] = True
        
        summary_text = " ".join([doc.page_content for doc in docs[:3]])
        llm = get_llm()
        prompt = f"Summarize this document in approximately 150 words: {summary_text}"
        response = llm.invoke(prompt)
        summary = response.content
        session['summary'] = summary

        return jsonify({"summary": summary})
    except Exception as e:
        logger.error(f"Error in upload_document_api: {e}", exc_info=True)
        return jsonify({"error": "Failed to process document."}), 500

@app.route("/api/ask", methods=["POST"])
def ask_question_api():
    if not session.get('doc_uploaded') or vectorstore is None:
        return jsonify({"error": "No document has been uploaded yet."}), 400
    
    query = request.form.get("query")
    if not query:
        return jsonify({"error": "No query provided."}), 400

    try:
        llm = get_llm(model="llama3-70b-8192")
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())
        answer = qa_chain.run(query)
        return jsonify({"answer": answer})
    except Exception as e:
        logger.error(f"Error in ask_question_api: {e}", exc_info=True)
        return jsonify({"error": "Failed to get an answer."}), 500

@app.route("/api/challenge", methods=["POST"])
def generate_challenges_api():
    if not session.get('doc_uploaded') or vectorstore is None:
        return jsonify({"error": "No document uploaded yet."}), 400
        
    try:
        docs = vectorstore.similarity_search("", k=5)
        context = " ".join([doc.page_content for doc in docs])
        llm = get_llm()
        prompt = f"Generate 3 simple questions based on this text. Do not number the questions. Each question must end with a single question mark. \n\nText: {context}\n\nQuestions:"
        response = llm.invoke(prompt)
        content = response.content
        
        raw_questions = [q.strip() for q in content.split('\n') if '?' in q]
        questions = [re.sub(r'^\s*\d+[\.\-]?\s*', '', q).strip().rstrip('?').strip() + '?' for q in raw_questions]
        
        session['challenge_questions'] = questions[:3]
        session['challenge_feedback'] = [None] * len(questions[:3])
        return jsonify({"questions": questions[:3]})
    except Exception as e:
        logger.error(f"Error in generate_challenges_api: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate challenges."}), 500

@app.route("/api/evaluate", methods=["POST"])
def evaluate_answer_api():
    if not session.get('doc_uploaded') or vectorstore is None:
        return jsonify({"error": "No document has been uploaded yet."}), 400

    question = request.form.get("question")
    user_answer = request.form.get("answer")

    try:
        docs = vectorstore.similarity_search(question, k=5)
        context = " ".join([doc.page_content for doc in docs])
        llm = get_llm()
        prompt = f"Based on the text: '{context}', evaluate this answer: '{user_answer}' for the question: '{question}'."
        response = llm.invoke(prompt)
        feedback = response.content
        return jsonify({"feedback": feedback})
    except Exception as e:
        logger.error(f"Error in evaluate_answer_api: {e}", exc_info=True)
        return jsonify({"error": "Failed to evaluate the answer."}), 500

def evaluate_all_answers_api():
    """Helper to evaluate all answers from the form."""
    feedback_list = []
    questions = session.get("challenge_questions", [])
    for i, question in enumerate(questions):
        user_answer = request.form.get(f"user_answer_{i}", "")
        
        docs = vectorstore.similarity_search(question, k=5)
        context = " ".join([doc.page_content for doc in docs])
        llm = get_llm()
        prompt = f"Based on the text: '{context}', evaluate this answer: '{user_answer}' for the question: '{question}'."
        response = llm.invoke(prompt)
        feedback = response.content
        feedback_list.append(feedback)
    
    session['challenge_feedback'] = feedback_list

if __name__ == "__main__":
    initialize_embeddings()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True) 