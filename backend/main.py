from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uuid
import sys
import os
import asyncio
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "documind-backend"}

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    max_words: int = Query(default=150, description="Maximum number of words for summary")
):
    try:
        print(f"Received upload request with max_words: {max_words}")
        
        # Validate file type
        if not file.filename.lower().endswith((".pdf", ".txt")):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        # Validate file size (10MB limit)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        print(f"Processing file: {file.filename}, size: {len(content)} bytes")
        
        # Process file based on type
        if file.filename.lower().endswith(".pdf"):
            text = document_processor.extract_pdf_text(content)
        else:
            text = document_processor.extract_txt_text(content)
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Could not extract text from file. Please ensure the file contains readable text.")
        
        print(f"Extracted text length: {len(text)} characters")
        
        # Generate document ID and store
        doc_id = str(uuid.uuid4())
        documents[doc_id] = {"text": text, "filename": file.filename}
        
        print(f"Calling generate_summary with max_words: {max_words}")
        
        # Run AI processing in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(None, ai_assistant.generate_summary, text, max_words)
        
        # Check if summary generation failed
        if summary.startswith("Error:"):
            raise HTTPException(status_code=500, detail=f"AI processing failed: {summary}")
        
        documents[doc_id]["summary"] = summary
        print(f"Successfully processed document {doc_id}")
        
        return {"document_id": doc_id, "summary": summary, "filename": file.filename}
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/ask-question")
async def ask_question(data: dict):
    try:
        doc_id = data.get("document_id")
        question = data.get("question")
        if doc_id not in documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Run AI processing in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None, 
            ai_assistant.answer_question, 
            str(question), 
            documents[doc_id]["text"]
        )
        return {"answer": answer}
    except Exception as e:
        print(f"Error in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/generate-challenges/{document_id}")
async def generate_challenges(document_id: str):
    try:
        if document_id not in documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Run AI processing in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        questions = await loop.run_in_executor(
            None, 
            ai_assistant.generate_challenges, 
            documents[document_id]["text"]
        )
        return {"challenges": questions}
    except Exception as e:
        print(f"Error in generate_challenges: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/evaluate-challenge")
async def evaluate_challenge(data: dict):
    try:
        doc_id = data.get("document_id")
        question = data.get("question")
        answer = data.get("answer")
        if doc_id not in documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Run AI processing in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        feedback = await loop.run_in_executor(
            None, 
            ai_assistant.evaluate_challenge_response, 
            str(answer), 
            str(question), 
            documents[doc_id]["text"]
        )
        return {"feedback": feedback}
    except Exception as e:
        print(f"Error in evaluate_challenge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    try:
        if document_id in documents:
            del documents[document_id]
            return {"message": "Document deleted"}
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        print(f"Error in delete_document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 