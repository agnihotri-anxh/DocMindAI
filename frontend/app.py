from flask import Flask, render_template, request, flash, redirect, url_for, session
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
app.secret_key = os.urandom(24)  # Use a secure, random secret key
API_URL = os.environ.get("API_URL", "/api") # Use relative path for Vercel

# Log the API URL being used
logger.info(f"Frontend configured to connect to backend at: {API_URL}")

# Project name for branding
PROJECT_NAME = "DocMind Ai"

@app.route("/", methods=["GET", "POST"])
def index():
    if 'summary' not in session:
        session['summary'] = None
        session['doc_uploaded'] = False
        session['challenge_questions'] = []
        session['challenge_feedback'] = []
    
    answer = None
    challenge_mode = request.args.get("mode") == "challenge"

    if request.method == "GET" and not challenge_mode:
        # Reset session for a fresh start
        session.clear()

    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            summary_words = request.form.get("summary_words", 150)
            logger.info(f"Uploading file: {file.filename} to {API_URL}/upload-document")
            try:
                resp = requests.post(
                    f"{API_URL}/upload-document",
                    files={"file": (file.filename, file.read())},
                    data={"summary_words": summary_words},
                    timeout=60  # Increase timeout to 60 seconds
                )
                logger.info(f"Upload response status: {resp.status_code}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        session["summary"] = data.get("summary", "")
                        session["doc_uploaded"] = True
                        session["challenge_questions"] = []
                        session["challenge_feedback"] = []
                        flash(f"✅ {PROJECT_NAME}: Document processed successfully!", "success")
                    except ValueError:
                        logger.error(f"Invalid JSON response: {resp.text}")
                        flash("❌ Invalid response from server.", "danger")
                else:
                    try:
                        error_data = resp.json()
                        flash(error_data.get("error", "❌ Failed to upload document."), "danger")
                    except ValueError:
                        logger.error(f"Invalid error response: {resp.text}")
                        flash(f"❌ Server error (Status: {resp.status_code})", "danger")
            except requests.exceptions.Timeout:
                logger.error("Request timed out")
                flash("❌ Request timed out. Please try again.", "danger")
            except requests.exceptions.ConnectionError:
                logger.error("Connection error")
                flash("❌ Cannot connect to backend server. Please try again later.", "danger")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception: {str(e)}")
                flash(f"❌ Connection error: {str(e)}", "danger")
        elif "question" in request.form:
            question = request.form["question"]
            try:
                resp = requests.post(f"{API_URL}/ask", data={"query": question})
                if resp.status_code == 200:
                    try:
                        answer = resp.json().get("answer", "No answer returned.")
                    except ValueError:
                        flash("❌ Invalid response from server.", "danger")
                else:
                    try:
                        flash(resp.json().get("error", "❌ Failed to get answer."), "danger")
                    except ValueError:
                        flash(f"❌ Server error (Status: {resp.status_code})", "danger")
            except requests.exceptions.RequestException as e:
                flash(f"❌ Connection error: {str(e)}", "danger")
        elif "get_challenges" in request.form:
            try:
                resp = requests.post(f"{API_URL}/challenge")
                if resp.status_code == 200:
                    try:
                        session["challenge_questions"] = resp.json().get("questions", [])
                        session["challenge_feedback"] = [None] * len(session["challenge_questions"])
                    except ValueError:
                        flash("❌ Invalid response from server.", "danger")
                else:
                    try:
                        flash(resp.json().get("error", "❌ Failed to generate challenges."), "danger")
                    except ValueError:
                        flash(f"❌ Server error (Status: {resp.status_code})", "danger")
            except requests.exceptions.RequestException as e:
                flash(f"❌ Connection error: {str(e)}", "danger")

        elif "submit_all_answers" in request.form:
            session["challenge_feedback"] = []
            for i, question in enumerate(session.get("challenge_questions", [])):
                user_answer = request.form.get(f"user_answer_{i}", "")
                
                try:
                    resp = requests.post(
                        f"{API_URL}/evaluate",
                        data={"question": question, "answer": user_answer}
                    )
                    
                    if resp.status_code == 200:
                        feedback_data = resp.json()
                        session["challenge_feedback"].append(feedback_data.get("feedback", "No feedback."))
                    else:
                        session["challenge_feedback"].append("Error from server.")
                
                except requests.exceptions.RequestException:
                    session["challenge_feedback"].append("Connection error.")

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

@app.route("/debug")
def debug():
    try:
        resp = requests.get(f"{API_URL}/test")
        if resp.status_code == 200:
            return f"Backend connection successful: {resp.json()}"
        else:
            return f"Backend connection failed: Status {resp.status_code}"
    except Exception as e:
        return f"Backend connection error: {str(e)}"

@app.route("/health")
def health():
    return {"status": "ok", "api_url": API_URL}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
