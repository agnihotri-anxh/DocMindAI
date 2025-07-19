from flask import Flask, render_template, request, flash, redirect, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Project name for branding
PROJECT_NAME = "DocMind Ai"

# Simple in-memory session (for demo)
SESSION = {"summary": None, "doc_uploaded": False, "challenge_questions": [], "challenge_feedback": []}

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    feedback = None
    challenge_mode = request.args.get("mode") == "challenge"
    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            summary_words = request.form.get("summary_words", 150)
            resp = requests.post(
                f"{API_URL}/upload-document",
                files={"file": (file.filename, file.read())},
                data={"summary_words": summary_words}
            )
            if resp.status_code == 200:
                data = resp.json()
                SESSION["summary"] = data.get("summary", "")
                SESSION["doc_uploaded"] = True
                SESSION["challenge_questions"] = []
                SESSION["challenge_feedback"] = []
                flash(f"✅ {PROJECT_NAME}: Document processed successfully!", "success")
            else:
                flash(resp.json().get("error", "❌ Failed to upload document."), "danger")
        elif "question" in request.form:
            question = request.form["question"]
            resp = requests.post(f"{API_URL}/ask", data={"query": question})
            if resp.status_code == 200:
                answer = resp.json().get("answer", "No answer returned.")
            else:
                flash(resp.json().get("error", "❌ Failed to get answer."), "danger")
        elif "get_challenges" in request.form:
            resp = requests.post(f"{API_URL}/challenge")
            if resp.status_code == 200:
                SESSION["challenge_questions"] = resp.json().get("questions", [])
                SESSION["challenge_feedback"] = [None] * len(SESSION["challenge_questions"])
            else:
                flash(resp.json().get("error", "❌ Failed to generate challenges."), "danger")
        elif "submit_answer" in request.form:
            idx = int(request.form["submit_answer"])  # which question
            user_answer = request.form.get(f"user_answer_{idx}", "")
            question = SESSION["challenge_questions"][idx]
            resp = requests.post(f"{API_URL}/evaluate", data={"question": question, "answer": user_answer})
            if resp.status_code == 200:
                feedback = resp.json().get("feedback", "No feedback returned.")
                SESSION["challenge_feedback"][idx] = feedback
            else:
                flash(resp.json().get("error", "❌ Failed to evaluate answer."), "danger")
    return render_template(
        "index.html",
        summary=SESSION["summary"],
        doc_uploaded=SESSION["doc_uploaded"],
        answer=answer,
        challenge_mode=challenge_mode,
        challenge_questions=SESSION["challenge_questions"],
        challenge_feedback=SESSION["challenge_feedback"]
    )

@app.route("/challenge")
def challenge():
    return redirect(url_for("index", mode="challenge"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
