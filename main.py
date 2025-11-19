from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import AIBot

app = Flask(__name__)


quiz_questions = {}

def load_quizzes_from_files():
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


@app.route("/")
def login():
    """Default route → login page."""
    return render_template("login.html")

@app.route("/home")
def home():
    """Home page → homeTemplate.html."""
    return render_template("homeTemplate.html")

@app.route("/quiz_list")
def quiz_list():
    """Quiz list page → quizTemplate.html."""
    return render_template("quizTemplate.html", quizzes=quiz_questions)

@app.route("/question/<quiz_name>/<int:q_index>", methods=["GET", "POST"])
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
        try:
            feedback = AIBot.ask_ai_for_feedback(question["question"], correct_answer, student_answer)
        except Exception as e:
            feedback = f"Error: {e}"

    return render_template(
        "question.html",
        quiz_name=quiz_name,
        quiz=quiz,
        question=question,
        feedback=feedback,
        q_index=q_index
    )

@app.route("/study")
def study_list():
    return render_template("studyTemplate.html", quizzes=quiz_questions)

@app.route("/study/<quiz_name>/<int:q_index>", methods=["GET", "POST"])
def study_question(quiz_name, q_index):
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
            feedback = AIBot.ask_ai_for_feedback(
                ai_question,
                correct_answer,
                student_answer
            )
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


@app.route("/quiz_complete/<quiz_name>")
def quiz_complete(quiz_name):
    """Show the quiz completion page."""
    return render_template("quiz_complete.html", quiz_name=quiz_name)

@app.route("/study_complete/<quiz_name>")
def study_complete(quiz_name):
    """Show the study completion page."""
    return render_template("study_complete.html", quiz_name=quiz_name)


@app.route("/get_quiz/<quiz_name>")
def get_quiz(quiz_name):
    """Return a quiz’s data as JSON (for JS-based pages)."""
    quiz = quiz_questions.get(quiz_name)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify(quiz)

@app.route("/check_answer", methods=["POST"])
def check_answer():
    """AJAX endpoint to check answers dynamically."""
    data = request.json or {}
    question = data.get("question", "")
    correct = data.get("correct", "")
    user = data.get("answer", "")

    try:
        feedback = AIBot.ask_ai_for_feedback(question, correct, user)
        return jsonify({"feedback": feedback})
    except Exception as e:
        return jsonify({"feedback": f"Error: {e}"})



if __name__ == "__main__":
    load_quizzes_from_files()
    print("Astronomy Quiz Helper running locally")
    print("Open your browser and go to: http://127.0.0.1:5000/")
    app.run(debug=True)