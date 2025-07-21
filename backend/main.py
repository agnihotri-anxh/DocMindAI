from dotenv import load_dotenv
import os
import psutil

# Load .env file from the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

try:
    load_dotenv(env_path)
    print(f"✅ .env file loaded from: {env_path}")
except Exception as e:
    print(f"⚠️  Warning: Could not load .env file from {env_path}: {e}")
    print("   You can set GROQ_API_KEY as an environment variable instead")

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key = os.getenv("GROQ_API_KEY")
print("GROQ_API_KEY:", "✅ Set" if api_key else "❌ Not found")
if not api_key:
    print("   Please set GROQ_API_KEY environment variable or create a .env file")

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import TokenTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import shutil
import tempfile
import sys
import os

# Add the current directory to Python path to fix import issues
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_assistant import AIAssistant

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorstore = None
retriever = None
all_docs = None
ai_assistant = AIAssistant()

# Helper: Load and split document
def load_and_split(file_path, file_type):
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)
    return docs

@app.post("/upload-document")
def upload_document(file: UploadFile = File(...), summary_words: int = Form(150)):
    logger.info("Received upload-document request")
    global all_docs, vectorstore, retriever
    
    def log_memory(stage):
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"[MEMORY] {stage}: {mem_mb:.2f} MB used")

    try:
        log_memory("Start upload-document")
        logger.info(f"Processing file: {file.filename}, size: {getattr(file, 'size', 'unknown')}")
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
        contents = file.file.read()
        logger.info(f"File contents read, length: {len(contents)}")
        log_memory("After file read")
        
        if len(contents) > MAX_FILE_SIZE:
            logger.warning(f"File too large: {len(contents)} bytes")
            return JSONResponse(status_code=400, content={"error": "File too large. Max 2MB allowed."})
        
        # Save contents to a temp file
        ext = file.filename.split(".")[-1].lower()
        logger.info(f"File extension: {ext}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
            logger.info(f"Temporary file created: {tmp_path}")
        log_memory("After temp file write")
        
        logger.info("Loading and splitting document...")
        docs = load_and_split(tmp_path, ext)
        logger.info(f"Document split into {len(docs)} chunks")
        log_memory("After document split")
        
        all_docs = docs[:10]  # Only keep first 10 chunks/pages
        logger.info(f"Keeping first {len(all_docs)} chunks")
        
        logger.info("Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
        vectorstore = FAISS.from_documents(all_docs, embeddings)
        retriever = vectorstore.as_retriever()
        logger.info("Vector store and retriever created successfully")
        log_memory("After embeddings and vectorstore")
        
        os.remove(tmp_path)
        logger.info("Temporary file removed")
        
        # Limit to first 10 chunks/pages for summary
        summary_docs = all_docs
        # Concatenate the text for summary
        summary_text = "\n".join([doc.page_content for doc in summary_docs])
        logger.info(f"Summary text length: {len(summary_text)}")
        log_memory("Before summary generation")
        
        logger.info("Generating summary...")
        summary = ai_assistant.generate_summary(summary_text, max_words=summary_words)
        logger.info(f"Summary generated, length: {len(summary)}")
        log_memory("After summary generation")
        
        # Release memory after processing
        import gc
        del docs, summary_docs, summary_text, contents
        gc.collect()
        log_memory("After memory cleanup")
        
        response_data = {"message": "Document uploaded and processed.", "summary": summary}
        logger.info("Returning successful response")
        return response_data
        
    except MemoryError:
        logger.error("MemoryError: The server ran out of memory while processing the document.", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Server ran out of memory. Please try a smaller file or contact support."})
    except Exception as e:
        logger.error(f"Error in upload_document: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Failed to process document: {str(e)}"})

@app.post("/ask")
def ask_question(query: str = Form(...)):
    print("Received ask_question request")
    global retriever, all_docs
    
    try:
        if retriever is None:
            return JSONResponse(status_code=400, content={"error": "No document uploaded yet."})
        
        llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama3-70b-8192")
        # Custom prompt to require justification and reference
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a careful assistant. Answer the question using ONLY the provided document context. "
                "Always justify your answer with a reference to the section or paragraph.\n"
                "\nContext:\n{context}\n\nQuestion: {question}\n\n"
                "Answer (with justification and reference):"
            ),
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )
        result = qa_chain({"query": query})
        answer = result["result"]
        
        # Optionally, extract reference from source docs
        sources = result.get("source_documents", [])
        if sources:
            ref = sources[0].metadata.get("source", "")
            answer += f"\n\n[Reference: {ref}]"
        
        return {"answer": answer}
    except Exception as e:
        print(f"Error in ask_question: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Failed to process question: {str(e)}"})

@app.post("/challenge")
def challenge():
    global all_docs
    
    try:
        if not all_docs:
            return JSONResponse(status_code=400, content={"error": "No document uploaded yet."})
        
        # Use the first 5 chunks for better context
        context = "\n".join([doc.page_content for doc in all_docs[:5]]) if all_docs else ""
        questions = ai_assistant.generate_challenges(context)
        # Clean up and return only non-empty, question-like lines
        questions_list = [q.strip("- ").strip() for q in questions if q.strip() and "?" in q]
        return {"questions": questions_list[:3]}
    except Exception as e:
        print(f"Error in challenge: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Failed to generate challenges: {str(e)}"})

@app.post("/evaluate")
def evaluate(answer: str = Form(...), question: str = Form(...)):
    global all_docs
    
    try:
        if not all_docs:
            return JSONResponse(status_code=400, content={"error": "No document uploaded yet."})
        
        llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama3-70b-8192")
        # Prompt to evaluate answer and provide feedback with justification
        prompt = PromptTemplate(
            input_variables=["context", "question", "answer"],
            template=(
                "You are an expert evaluator. Given the document context, the question, and the user's answer, "
                "evaluate the answer for correctness and provide feedback. Always justify your feedback with a reference to the document.\n"
                "\nContext:\n{context}\n\nQuestion: {question}\nUser Answer: {answer}\n\nFeedback (with justification and reference):"
            ),
        )
        chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
        context = all_docs[0].page_content if all_docs else ""
        feedback = chain.run([{"page_content": context}], question=question, answer=answer)
        return {"feedback": feedback}
    except Exception as e:
        print(f"Error in evaluate: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Failed to evaluate answer: {str(e)}"})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"message": "Backend is working!", "timestamp": "2025-07-20"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
