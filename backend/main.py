from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import uuid
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_processor import DocumentProcessor
from ai_assistant import AIAssistant

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

documents = {}
document_processor = DocumentProcessor()
ai_assistant = AIAssistant()

@app.post("/upload-document")
def upload_document(
    file: UploadFile = File(...),
    max_words: int = Query(default=150, description="Maximum number of words for summary")
):
    print(f"Received upload request with max_words: {max_words}")
    if not file.filename.lower().endswith((".pdf", ".txt")):
        return {"error": "Only PDF and TXT files are supported"}
    content = file.file.read()
    if file.filename.lower().endswith(".pdf"):
        text = document_processor.extract_pdf_text(content)
    else:
        text = document_processor.extract_txt_text(content)
    doc_id = str(uuid.uuid4())
    documents[doc_id] = {"text": text, "filename": file.filename}
    print(f"Calling generate_summary with max_words: {max_words}")
    summary = ai_assistant.generate_summary(text, max_words)
    documents[doc_id]["summary"] = summary
    return {"document_id": doc_id, "summary": summary, "filename": file.filename}

@app.post("/ask-question")
def ask_question(data: dict):
    doc_id = data.get("document_id")
    question = data.get("question")
    if doc_id not in documents:
        return {"error": "Document not found"}
    answer = ai_assistant.answer_question(question, documents[doc_id]["text"])
    return {"answer": answer}

@app.get("/generate-challenges/{document_id}")
def generate_challenges(document_id: str):
    if document_id not in documents:
        return {"error": "Document not found"}
    questions = ai_assistant.generate_challenges(documents[document_id]["text"])
    return {"challenges": questions}

@app.post("/evaluate-challenge")
def evaluate_challenge(data: dict):
    doc_id = data.get("document_id")
    question = data.get("question")
    answer = data.get("answer")
    if doc_id not in documents:
        return {"error": "Document not found"}
    feedback = ai_assistant.evaluate_challenge_response(answer, question, documents[doc_id]["text"])
    return {"feedback": feedback}

@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    if document_id in documents:
        del documents[document_id]
        return {"message": "Document deleted"}
    return {"error": "Document not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 