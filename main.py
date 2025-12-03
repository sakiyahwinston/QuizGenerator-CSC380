# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import os
import json
import AIBot
import random
from datetime import datetime, timedelta
from functools import wraps
from emailVerification import sendMessage

# ------------------------------
# Flask app setup
# ------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")  # use a real secret in production

# ------------------------------
# Data and storage
# ------------------------------
quiz_questions = {}  # In-memory quiz store
DATA_FILE = "user_data.json"  # Persistent store

def load_persistent():
    """Load persistent user and result data from JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "results": [], "next_user_id": 1}

def save_persistent(data):
    """Save persistent data to JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, default=str, indent=2)

persistent = load_persistent()
pending_verifications = {}  # Temporary in-memory verification codes {email: {"code": str, "expires": datetime}}

# ------------------------------
# Decorators
# ------------------------------
def login_required(f):
    """Protect routes so only logged-in users can access."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped

# ------------------------------
# Quiz loading
# ------------------------------
def load_quizzes_from_files():
    """Load quizzes from JSON files in 'quizzes' folder."""
    quiz_questions.clear()
    quizzes_path = os.path.join(os.getcwd(), "quizzes")

    if not os.path.exists(quizzes_path):
        print("No 'quizzes' folder found.")
        return

    for file in os.listdir(quizzes_path):
        if file.endswith(".json"):
            try:
                with open(os.path.join(quizzes_path, file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("name", file.replace(".json", ""))
                    quiz_questions[name] = {
                        "url": data.get("url", ""),
                        "questions": data.get("questions", [])
                    }
            except Exception as e:
                print(f"Error loading {file}: {e}")

    print(f"Loaded {len(quiz_questions)} quizzes.")

# ------------------------------
# Authentication Routes
# ------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    """Login page; request verification code via email."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            flash("Enter a valid email.", "error")
            return redirect(url_for("login"))

        code = ''.join(random.choice("0123456789") for _ in range(4))
        expires = datetime.utcnow() + timedelta(minutes=3)
        pending_verifications[email] = {"code": code, "expires": expires}

        try:
            sendMessage(email, code)
            flash("Verification code sent to your email.", "info")
            session["email"] = email
            return redirect(url_for("verify"))
        except Exception as e:
            flash(f"Failed to send verification: {e}", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    """Verify code submitted by the user."""
    email = session.get("email")
    if not email:
        flash("No email in session. Enter your email first.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        code_entered = request.form.get("code", "").strip()
        record = pending_verifications.get(email)

        if not record:
            flash("No code requested for this email or it expired.", "error")
            return redirect(url_for("login"))

        if datetime.utcnow() > record["expires"]:
            pending_verifications.pop(email, None)
            flash("Code expired. Request a new one.", "error")
            return redirect(url_for("login"))

        if code_entered != record["code"]:
            flash("Incorrect code.", "error")
            return redirect(url_for("verify"))

        # Verified → Create or fetch user
        users = persistent["users"]
        found_id = None
        for uid_str, info in users.items():
            if info.get("email") == email:
                found_id = int(uid_str)
                break

        if found_id is None:
            user_id = persistent["next_user_id"]
            persistent["next_user_id"] += 1
            users[str(user_id)] = {"email": email, "created_at": datetime.utcnow().isoformat()}
        else:
            user_id = found_id

        session["user_id"] = user_id
        pending_verifications.pop(email, None)
        save_persistent(persistent)
        flash("Login successful!", "success")
        return redirect(url_for("home"))

    return render_template("verify.html")


@app.route("/logout")
def logout():
    """Log out the user."""
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ------------------------------
# Main UI Routes
# ------------------------------
@app.route("/home")
@login_required
def home():
    """Home page after login."""
    return render_template("homeTemplate.html")

@app.route("/quiz_list")
@login_required
def quiz_list():
    """Display list of quizzes."""
    return render_template("quizTemplate.html", quizzes=quiz_questions)

@app.route("/question/<quiz_name>/<int:q_index>", methods=["GET", "POST"])
@login_required
def question_page(quiz_name, q_index):
    quiz = quiz_questions.get(quiz_name)
    if not quiz:
        return f"<h3>Quiz '{quiz_name}' not found.</h3>", 404

    questions = quiz["questions"]
    if q_index < 0 or q_index >= len(questions):
        return "<h3>Invalid question index.</h3>", 404

    question = questions[q_index]
    feedback = None

    if request.method == "POST":
        student_answer = request.form.get("student_answer", "").strip()
        correct_answer = question.get("correct_answer", "")

        # Save whether the answer is correct in session
        if "quiz_answers" not in session:
            session["quiz_answers"] = {}
        if quiz_name not in session["quiz_answers"]:
            session["quiz_answers"][quiz_name] = {}
        session["quiz_answers"][quiz_name][str(q_index)] = (student_answer == correct_answer)
        session.modified = True  # tell Flask to save session

        try:
            feedback = AIBot.ask_ai_for_feedback(question["question"], correct_answer, student_answer)
        except Exception as e:
            feedback = f"Error: {e}"

        # Redirect to next question automatically
        if q_index + 1 < len(questions):
            return redirect(url_for("question_page", quiz_name=quiz_name, q_index=q_index + 1))
        else:
            # Last question → go to quiz_complete
            return redirect(url_for("quiz_complete", quiz_name=quiz_name))

    return render_template(
        "question.html",
        quiz_name=quiz_name,
        quiz=quiz,
        question=question,
        feedback=feedback,
        q_index=q_index
    )

@app.route("/quiz_complete/<quiz_name>", methods=["GET", "POST"])
@login_required
def quiz_complete(quiz_name):
    user_id = session["user_id"]
    answers = session.get("quiz_answers", {}).get(quiz_name, {})

    # calculate score
    total_questions = len(quiz_questions.get(quiz_name, {}).get("questions", []))
    correct_count = sum(1 for correct in answers.values() if correct)
    percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    if request.method == "POST":
        # Save score in persistent JSON
        persistent["results"].append({
            "user_id": user_id,
            "quiz": quiz_name,
            "score": correct_count,
            "total": total_questions,
            "percentage": round(percentage, 2),
            "completed_at": datetime.utcnow().isoformat()
        })
        save_persistent(persistent)
        flash(f"Score saved: {correct_count}/{total_questions} ({round(percentage,2)}%)", "success")
        # Clear temporary quiz answers
        session["quiz_answers"].pop(quiz_name, None)
        return redirect(url_for("dashboard"))

    # Render template with score info
    return render_template(
        "quiz_complete.html",
        quiz_name=quiz_name,
        score=correct_count,
        total=total_questions,
        percentage=round(percentage, 2)
    )

@app.route("/dashboard")
@login_required
def dashboard():
    """Display dashboard with user's results."""
    user_id = session["user_id"]
    # Gather results for this user
    results = [r for r in persistent["results"] if r.get("user_id") == user_id]
    # Sort newest first
    results.sort(key=lambda r: r.get("completed_at"), reverse=True)
    return render_template("dashboard.html", results=results, email=session.get("email"))

# ------------------------------
# Study Routes
# ------------------------------
@app.route("/study")
@login_required
def study_list():
    """Display study quiz list."""
    return render_template("studyTemplate.html", quizzes=quiz_questions)

@app.route("/study/<quiz_name>/<int:q_index>", methods=["GET", "POST"])
@login_required
def study_question(quiz_name, q_index):
    """Display AI-generated study question and feedback."""
    quiz = quiz_questions.get(quiz_name)
    if not quiz:
        return f"<h3>Quiz '{quiz_name}' not found.</h3>", 404

    questions = quiz["questions"]
    if q_index < 0 or q_index >= len(questions):
        return "<h3>Invalid question index.</h3>", 404

    original_question = questions[q_index]
    ai_question = None
    feedback = None

    if request.method == "POST":
        ai_question = request.form.get("ai_question")
        student_answer = request.form.get("student_answer", "").strip()
        correct_answer = original_question.get("correct_answer", "")

        try:
            feedback = AIBot.ask_ai_for_feedback(ai_question, correct_answer, student_answer)
        except Exception as e:
            feedback = f"Error: {e}"
    else:
        ai_question = AIBot.query_AI([
            {"role": "system", "content": "You are a tutor generating challenging study questions."},
            {"role": "user", "content":
                f"Create a slightly harder version of this question. "
                f"Keep it around the same length as the original question. "
                f"Do NOT include the answer:\n{original_question['question']}"
            }
        ])

    return render_template(
        "study_question.html",
        quiz_name=quiz_name,
        quiz=quiz,
        ai_question=ai_question,
        feedback=feedback,
        q_index=q_index
    )

# ------------------------------
# API Endpoints
# ------------------------------
@app.route("/get_quiz/<quiz_name>")
@login_required
def get_quiz(quiz_name):
    """Return quiz data as JSON."""
    quiz = quiz_questions.get(quiz_name)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify(quiz)

@app.route("/check_answer", methods=["POST"])
@login_required
def check_answer():
    """Check an answer via AI and return feedback."""
    data = request.json or {}
    question = data.get("question", "")
    correct = data.get("correct", "")
    user = data.get("answer", "")

    try:
        feedback = AIBot.ask_ai_for_feedback(question, correct, user)
        return jsonify({"feedback": feedback})
    except Exception as e:
        return jsonify({"feedback": f"Error: {e}"})


# ------------------------------
# Run the app
# ------------------------------
if __name__ == "__main__":
    load_quizzes_from_files()
    print("Quiz app running locally at http://127.0.0.1:5000/")
    app.run(debug=True)

