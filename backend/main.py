from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from contextlib import asynccontextmanager
import os
import tempfile
import logging
from dotenv import load_dotenv
import re

# Construct the path to the .env file in the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Load environment variables from the specified .env file
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    logging.warning(f".env file not found at {env_path}. Please ensure it exists.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Environment and API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found. Please set it as an environment variable.")

# Vector store configuration
USE_PINECONE = os.getenv("USE_PINECONE", "false").lower() in ("1", "true", "yes")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "docmind-index")
PINECONE_HOST = os.getenv("PINECONE_HOST")  # optional: serverless host URL

# Embedding providers
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "hf_inference").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# --- Global Variables & In-memory Storage ---
embeddings = None
vectorstore = None
all_docs = []

# --- AI Model and Assistant ---
MODEL_NAME = "sentence-transformers/paraphrase-TinyBERT-L6-v2"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the sentence transformer model at startup."""
    global embeddings, vectorstore, all_docs, USE_PINECONE
    
    # Initialize Pinecone if enabled
    if USE_PINECONE:
        try:
            from pinecone import Pinecone
            # Initialize with new Pinecone API
            pc = Pinecone(api_key=PINECONE_API_KEY)
            logger.info("Pinecone initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            USE_PINECONE = False
    
    logger.info("Initializing embeddings provider: %s", EMBEDDING_PROVIDER)
    if EMBEDDING_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. OpenAI embeddings will fail.")
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        logger.info("OpenAIEmbeddings initialized.")
    elif EMBEDDING_PROVIDER in ("hf", "hf_inference", "huggingface"):
        logger.info("Using HuggingFace embeddings with model: %s", HF_EMBEDDING_MODEL)
        embeddings = HuggingFaceEmbeddings(
            model_name=HF_EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}
        )
        logger.info("HuggingFaceEmbeddings initialized successfully")
    else:
        logger.warning("Unknown EMBEDDING_PROVIDER '%s'. Falling back to default HF embeddings.", EMBEDDING_PROVIDER)
        embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            model_kwargs={"device": "cpu"}
        )
        logger.info("Default HF embeddings model loaded successfully.")
    yield
    # Clean up on shutdown
    vectorstore = None
    embeddings = None
    all_docs = []
    logger.info("Resources cleaned up.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Functions ---
def get_llm(model="llama3-8b-8192"):
    return ChatGroq(groq_api_key=GROQ_API_KEY, model=model)

# --- API Endpoints ---
@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to the optimized DocMind Ai Backend!"}

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...), summary_words: int = Form(150)):
    global vectorstore, all_docs
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        all_docs = text_splitter.split_documents(documents)

        if not all_docs:
            return JSONResponse(status_code=400, content={"error": "Could not extract text from the document."})
            
        if USE_PINECONE:
            # Persist to Pinecone index (assumes index already exists)
            logger.info(f"Upserting {len(all_docs)} chunks to Pinecone index '{PINECONE_INDEX}'...")
            try:
                if PINECONE_HOST:
                    vectorstore = PineconeVectorStore.from_documents(
                        documents=all_docs,
                        embedding=embeddings,
                        index_name=PINECONE_INDEX,
                        host=PINECONE_HOST,
                    )
                else:
                    vectorstore = PineconeVectorStore.from_documents(
                        documents=all_docs,
                        embedding=embeddings,
                        index_name=PINECONE_INDEX,
                    )
                logger.info("Pinecone upsert complete.")
            except Exception as e:
                logger.error(f"Pinecone upsert failed: {e}", exc_info=True)
                return JSONResponse(status_code=500, content={"error": "Vector store upsert failed."})
        else:
            vectorstore = FAISS.from_documents(all_docs, embeddings)

        # Generate summary from the first few pages
        summary_text = " ".join([doc.page_content for doc in all_docs[:3]])
        llm = get_llm()
        prompt = f"Summarize this document in approximately {summary_words} words: {summary_text}"
        response = llm.invoke(prompt)
        summary = response.content

        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error in upload_document: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Failed to process document."})
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/ask")
async def ask_question(query: str = Form(...)):
    if not vectorstore and not USE_PINECONE:
        return JSONResponse(status_code=400, content={"error": "No document has been uploaded yet."})
    
    try:
        llm = get_llm(model="llama3-70b-8192")
        if USE_PINECONE:
            # Reconnect to Pinecone-backed vector store on-demand
            try:
                if PINECONE_HOST:
                    pinecone_vs = PineconeVectorStore(
                        index_name=PINECONE_INDEX,
                        embedding=embeddings,
                        host=PINECONE_HOST,
                    )
                else:
                    pinecone_vs = PineconeVectorStore(
                        index_name=PINECONE_INDEX,
                        embedding=embeddings,
                    )
                retriever = pinecone_vs.as_retriever()
            except Exception as e:
                logger.error(f"Failed to connect to Pinecone index: {e}", exc_info=True)
                return JSONResponse(status_code=500, content={"error": "Vector store unavailable."})
        else:
            retriever = vectorstore.as_retriever()

        qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
        answer = qa_chain.run(query)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error in ask: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Failed to get an answer."})

@app.post("/challenge")
async def generate_challenges():
    if not all_docs:
        return JSONResponse(status_code=400, content={"error": "No document has been uploaded yet."})
        
    try:
        context = " ".join([doc.page_content for doc in all_docs[:5]])
        llm = get_llm()
        prompt = f"Generate 3 simple, numbered questions based on this text. Each question must end with a question mark. \n\nText: {context}\n\nQuestions:"
        response = llm.invoke(prompt)
        content = response.content
        
        # Split questions and strip any leading numbering (e.g., "1. ", "2- ") and trailing question marks
        raw_questions = [q.strip() for q in content.split('\n') if '?' in q]
        questions = [re.sub(r'^\d+[\.\-\)\:]?\s*', '', q).rstrip(' ?') for q in raw_questions]
        
        return {"questions": questions[:3]}
    except Exception as e:
        logger.error(f"Error in challenge: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Failed to generate challenges."})

@app.post("/evaluate")
async def evaluate_answer(question: str = Form(...), answer: str = Form(...)):
    if not all_docs:
        return JSONResponse(status_code=400, content={"error": "No document has been uploaded yet."})

    try:
        context = " ".join([doc.page_content for doc in all_docs[:5]])
        llm = get_llm()
        prompt = f"Based on the text: '{context}', evaluate this answer: '{answer}' for the question: '{question}'."
        response = llm.invoke(prompt)
        feedback = response.content
        return {"feedback": feedback}
    except Exception as e:
        logger.error(f"Error in evaluate: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Failed to evaluate the answer."})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 