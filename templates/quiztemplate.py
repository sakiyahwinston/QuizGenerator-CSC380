import customtkinter as ctk
import webbrowser
import AIBot
from question import quiz_questions

# === UTILS ===

def open_link(url):
    if url:
        webbrowser.open_new(url)

def truncate_text(text, max_length=70):
    return text[:max_length - 3] + "..." if len(text) > max_length else text


# === APP SETUP ===

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Astronomy Quiz Helper 🌌")
app.geometry("900x650")
app.resizable(False, False)

current_quiz = []
current_question_index = None
current_quiz_name = ""
quiz_url = ""


# === LAYOUT ===

main_frame = ctk.CTkFrame(app, fg_color="#f8f9fa")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Header
header_frame = ctk.CTkFrame(main_frame, fg_color="white", height=60, corner_radius=12)
header_frame.pack(fill="x", padx=10, pady=(0, 10))

title_label = ctk.CTkLabel(
    header_frame, 
    text="🌌  Astronomy Quiz Helper", 
    font=ctk.CTkFont(size=22, weight="bold"),
    text_color="#1e293b"
)
title_label.pack(pady=10)

# Body split (Left: quizzes / Right: question)
body_frame = ctk.CTkFrame(main_frame, fg_color="#ffffff", corner_radius=12)
body_frame.pack(fill="both", expand=True, padx=10, pady=10)

left_frame = ctk.CTkScrollableFrame(body_frame, width=250, label_text="📘 Quizzes")
left_frame.pack(side="left", fill="y", padx=(10, 0), pady=10)

right_frame = ctk.CTkFrame(body_frame, fg_color="#f1f5f9", corner_radius=12)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Footer
footer_frame = ctk.CTkFrame(main_frame, fg_color="white", height=50, corner_radius=12)
footer_frame.pack(fill="x", padx=10, pady=(10, 0))

# === RIGHT PANEL CONTENT ===
question_label = ctk.CTkLabel(
    right_frame,
    text="Select a quiz and question to begin!",
    font=ctk.CTkFont(size=16, weight="bold"),
    wraplength=550,
    justify="left"
)
question_label.pack(pady=(30, 10))

answer_entry = ctk.CTkEntry(right_frame, width=400, placeholder_text="Type your answer here...")
submit_button = ctk.CTkButton(right_frame, text="Submit Answer", width=200)
feedback_label = ctk.CTkLabel(right_frame, text="", font=ctk.CTkFont(size=14), wraplength=550)
similar_btn = ctk.CTkButton(right_frame, text="🧠 Try a Similar Question", width=200)
link_button = ctk.CTkButton(
    right_frame,
    text="🌐 Learn More",
    fg_color="transparent",
    hover_color="lightgray",
    text_color="#3b82f6",
    command=lambda: open_link(quiz_url)
)

# Navigation
nav_frame = ctk.CTkFrame(right_frame, fg_color="#f1f5f9")
back_button = ctk.CTkButton(nav_frame, text="⬅ Back to Questions", width=180)
back_to_quiz_list_button = ctk.CTkButton(nav_frame, text="🏠 Back to Quizzes", width=180, fg_color="gray30")

nav_frame.pack(side="bottom", pady=20)
back_button.pack(side="left", padx=10)
back_to_quiz_list_button.pack(side="left", padx=10)

# === LOGIC ===

def rebuild_quiz_buttons():
    for widget in left_frame.winfo_children():
        widget.destroy()

    for quiz_name in quiz_questions.keys():
        btn = ctk.CTkButton(
            left_frame,
            text=quiz_name,
            command=lambda name=quiz_name: load_quiz(name),
            fg_color="#2563eb",
            text_color="white",
            corner_radius=8
        )
        btn.pack(pady=5, fill="x")

def show_question_widgets():
    answer_entry.pack(pady=5)
    submit_button.pack(pady=5)
    feedback_label.pack(pady=10)

def hide_question_widgets():
    answer_entry.pack_forget()
    submit_button.pack_forget()
    feedback_label.pack_forget()
    similar_btn.pack_forget()

def show_quiz_selection():
    hide_question_widgets()
    question_label.configure(text="📘 Select a quiz from the left to begin.")
    link_button.pack_forget()

def load_quiz(quiz_name):
    global current_quiz, current_question_index, current_quiz_name, quiz_url
    quiz_data = quiz_questions.get(quiz_name)
    if not quiz_data:
        feedback_label.configure(text="⚠️ Invalid quiz selected.", text_color="red")
        return

    current_quiz = quiz_data["questions"]
    current_quiz_name = quiz_name
    current_question_index = None
    quiz_url = quiz_data.get("url", "")

    question_label.configure(text=f"✅ {quiz_name} loaded.\nSelect a question below:")
    hide_question_widgets()

    for widget in right_frame.winfo_children():
        if isinstance(widget, ctk.CTkButton) and widget not in [submit_button, back_button, back_to_quiz_list_button, similar_btn, link_button]:
            widget.destroy()

    # Add Learn More link
    if quiz_url:
        link_button.pack(pady=(5, 10))

    for idx, q in enumerate(current_quiz):
        display_text = f"Q{idx + 1}: {truncate_text(q['question'])}"
        btn = ctk.CTkButton(
            right_frame,
            text=display_text,
            width=500,
            fg_color="#1f6aa5",
            text_color="white",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=lambda i=idx: select_question(i)
        )
        btn.pack(pady=4)

def select_question(index):
    global current_question_index
    current_question_index = index
    q = current_quiz[index]
    question_label.configure(text=f"❓ {q['question']}")
    feedback_label.configure(text="")
    show_question_widgets()

def back_to_questions():
    hide_question_widgets()
    load_quiz(current_quiz_name)

def check_answer():
    global current_question_index
    if current_question_index is None:
        feedback_label.configure(text="Select a question first!", text_color="red")
        return

    user_answer = answer_entry.get().strip()
    q = current_quiz[current_question_index]
    question = q["question"]
    correct_answer = q.get("correct_answer", "")

    feedback_label.configure(text="⏳ Checking answer...", text_color="gray")
    app.update_idletasks()

    try:
        ai_feedback = AIBot.ask_ai_for_feedback(question, correct_answer, user_answer)
        if ai_feedback == "CORRECT_ANSWER":
            feedback_label.configure(text="🎉 Correct! Well done!", text_color="green")
            similar_btn.pack(pady=5)
        else:
            feedback_label.configure(text=f"💡 Hint: {ai_feedback}", text_color="orange")
            similar_btn.pack_forget()
    except Exception as e:
        feedback_label.configure(text=f"⚠️ Error: {e}", text_color="red")

def generate_similar_question():
    global current_question_index, current_quiz
    if current_question_index is None:
        feedback_label.configure(text="Select a question first!", text_color="red")
        return

    q = current_quiz[current_question_index]
    question = q["question"]

    feedback_label.configure(text="⏳ Generating similar question...", text_color="gray")
    app.update_idletasks()

    try:
        system_message = {"role": "system", "content": "You are an astronomy tutor who creates quiz questions."}
        user_message = {"role": "user", "content": f"Create a new astronomy question similar to:\n{question}"}
        new_question_text = AIBot.query_AI([system_message, user_message])

        current_quiz.append({"question": new_question_text, "correct_answer": ""})
        select_question(len(current_quiz) - 1)
        feedback_label.configure(text="🔄 Here's a similar question to try!", text_color="blue")
        similar_btn.pack_forget()
    except Exception as e:
        feedback_label.configure(text=f"⚠️ Error: {e}", text_color="red")


# Bind logic
submit_button.configure(command=check_answer)
similar_btn.configure(command=generate_similar_question)
back_button.configure(command=back_to_questions)
back_to_quiz_list_button.configure(command=show_quiz_selection)

# Load quizzes
rebuild_quiz_buttons()

app.mainloop()
