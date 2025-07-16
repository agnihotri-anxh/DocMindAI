from dotenv import load_dotenv
load_dotenv()
import os
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))

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
from backend.ai_assistant import AIAssistant

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
    global vectorstore, retriever, all_docs
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "txt"]:
        return JSONResponse(status_code=400, content={"error": "Only PDF and TXT files are supported."})
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    docs = load_and_split(tmp_path, ext)
    all_docs = docs
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cuda"})
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()
    os.remove(tmp_path)
    # Limit to first 10 chunks/pages for summary
    summary_docs = docs[:10]
    # Concatenate the text for summary
    summary_text = "\n".join([doc.page_content for doc in summary_docs])
    summary = ai_assistant.generate_summary(summary_text, max_words=summary_words)
    return {"message": "Document uploaded and processed.", "summary": summary}

@app.post("/ask")
def ask_question(query: str = Form(...)):
    global retriever, all_docs
    if retriever is None:
        return JSONResponse(status_code=400, content={"error": "No document uploaded yet."})
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama3-70b-8192")    # Custom prompt to require justification and reference
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

@app.post("/challenge")
def challenge():
    global all_docs
    if not all_docs:
        return JSONResponse(status_code=400, content={"error": "No document uploaded yet."})
    # Use the first 5 chunks for better context
    context = "\n".join([doc.page_content for doc in all_docs[:5]]) if all_docs else ""
    questions = ai_assistant.generate_challenges(context)
    # Clean up and return only non-empty, question-like lines
    questions_list = [q.strip("- ").strip() for q in questions if q.strip() and "?" in q]
    return {"questions": questions_list[:3]}

@app.post("/evaluate")
def evaluate(answer: str = Form(...), question: str = Form(...)):
    global all_docs
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

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 