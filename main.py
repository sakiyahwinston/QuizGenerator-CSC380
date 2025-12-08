# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import os
import json
import AIBot
import random
from datetime import datetime, timedelta
from functools import wraps
from emailVerification import sendMessage
import mysql.connector 


# ------------------------------
# Flask app setup
# ------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")  # use a real secret in production

# ------------------------------
# Database connection
# ------------------------------
db_config = {
    "host": "altair.cs.oswego.edu",
    "user": "csc380_25f_t4",
    "password": "csc380_25f",   
    "database": "csc380_25f_t4",
    "port": 3306
}

def get_db_connection():
    """Return a new MySQL database connection."""
    return mysql.connector.connect(**db_config)



# ------------------------------
# Data and storage
# ------------------------------
quiz_questions = {}  # In-memory quiz store
DATA_FILE = "user_data.json"  # Persistent store


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


def sync_quizzes_to_db():
    """Ensure every quiz JSON file exists in the SQL 'quiz' table."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    for quiz_name in quiz_questions.keys():
        cursor.execute(
            "SELECT quizID FROM quiz WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))",
            (quiz_name,)
        )
        existing = cursor.fetchone()

        if not existing:
            cursor.execute("INSERT INTO quiz (name) VALUES (%s)", (quiz_name,))
            conn.commit()
            print(f"Inserted new quiz into DB: {quiz_name}")
        else:
            print(f"Quiz already exists in DB: {quiz_name}")

    cursor.close()
    conn.close()


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
    email = session.get("email")
    if not email:
        flash("No email found. Please login again.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        code_entered = request.form.get("code", "").strip()

        record = pending_verifications.get(email)

        # No record or expired
        if not record or datetime.utcnow() > record["expires"]:
            flash("Verification code expired. Please request a new one.", "error")
            return redirect(url_for("login"))

        # Wrong code
        if code_entered != record["code"]:
            flash("Incorrect code.", "error")
            return redirect(url_for("verify"))

        # ---- CODE IS CORRECT ----
        # Check if user exists in SQL
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            # Mark verified
            cursor.execute("UPDATE student SET verified = 1 WHERE email=%s", (email,))
            conn.commit()
            conn.close()

            # Login user
            session["user_id"] = user["email"]

            flash("Verification successful!", "success")
            return redirect(url_for("home"))

        else:
            # Email not in database → go to signup
            conn.close()
            session["signup_email"] = email
            flash("We need a bit more info to finish creating your account.", "info")
            return redirect(url_for("signup"))

    return render_template("verify.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    email = session.get("signup_email")
    if not email:
        flash("You must verify your email first.")
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if not name or not password:
            flash("All fields are required.")
            return render_template("signup.html", email=email)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "INSERT INTO student (name, email, password, verified) VALUES (%s, %s, %s, 1)",
                (name, email, password)
            )
            conn.commit()

            # Log user in
            session["user_id"] = email
            return redirect("/home")

        except mysql.connector.IntegrityError:
            flash("Account already exists.")
            return redirect("/login")

        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html", email=email)



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
    """Display quiz completion page and save score to database."""
    user_email = session.get("user_id")
    if not user_email:
        flash("You must log in first.", "error")
        return redirect(url_for("login"))

    # Retrieve answers stored in session
    quiz_data = quiz_questions.get(quiz_name, {})
    questions = quiz_data.get("questions", [])
    answers = session.get("quiz_answers", {}).get(quiz_name, {})

    total_questions = len(questions)
    correct_count = sum(1 for correct in answers.values() if correct)
    percentage = int(round((correct_count / total_questions) * 100))

    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # 1️⃣ Get studentID
            cursor.execute("SELECT studentID FROM student WHERE email = %s", (user_email,))
            student_row = cursor.fetchone()
            if not student_row:
                flash("Error: student not found in database.", "error")
                return redirect(url_for("dashboard"))

            student_id = student_row["studentID"]

            # 2️⃣ Get quizID by name
            cursor.execute("""
                SELECT quizID FROM quiz
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                LIMIT 1
            """, (quiz_name,))
            quiz_row = cursor.fetchone()
            if not quiz_row:
                flash("Error: quiz not found in database.", "error")
                return redirect(url_for("dashboard"))

            quiz_id = quiz_row["quizID"]

            # 3️⃣ Insert or update score with timestamp
            cursor.execute("""
                INSERT INTO quiz_scores (quizID, studentID, grade)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE grade = VALUES(grade)
            """, (quiz_id, student_id, str(percentage)))

            conn.commit()

            # Clear stored answers for this quiz
            #session.get("quiz_answers", {}).pop(quiz_name, None)
            #session.modified = True

            flash(
                f"Score saved: {correct_count}/{total_questions} ({round(percentage, 2)}%)",
                "success"
            )

        except Exception as e:
            flash(f"Error saving score: {e}", "error")

        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("dashboard"))

    # GET request: show quiz complete page
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
    """Display quizzes, scores, and attempt count."""
    user_email = session.get("user_id")
    if not user_email:
        flash("You must log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1️⃣ Get student ID
        cursor.execute("SELECT studentID FROM student WHERE email = %s", (user_email,))
        student = cursor.fetchone()
        if not student:
            flash("Error: Student not found.", "error")
            return redirect(url_for("login"))
        student_id = student["studentID"]

        # 2️⃣ Get quizzes + score + number of attempts
        cursor.execute("""
            SELECT 
               quiz.name AS quizName,
                quiz_scores.grade
            FROM quiz
            LEFT JOIN quiz_scores
                ON quiz.quizID = quiz_scores.quizID
                AND quiz_scores.studentID = %s
            ORDER BY quiz.quizID;
        """, (student_id,))

        quizzes = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "dashboard.html",
        user_email=user_email,
        quizzes=quizzes
    )


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
    sync_quizzes_to_db()
    print("Quiz app running locally at http://127.0.0.1:5000/")
    app.run(debug=True)

