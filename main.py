import customtkinter as ctk
import AIBot
import webbrowser
import os
import json



def open_link(url):
    if url:
        webbrowser.open_new(url)


# Utility functions
def truncate_text(text, max_length=70):
    return text[:max_length - 3] + "..." if len(text) > max_length else text


def hide_question_widgets():
    question_label.pack_forget()
    answer_entry.pack_forget()
    submit_button.pack_forget()
    feedback_label.pack_forget()
    similar_btn.pack_forget()
    back_button.pack_forget()
    back_to_quiz_list_button.pack_forget()
    next_button.pack_forget()


def show_question_widgets():
    quiz_frame.pack_forget()
    title_label.configure(text="Answer the Question")
    question_label.pack(pady=20)
    answer_entry.pack(pady=5)
    submit_button.pack(pady=5)
    feedback_label.pack(pady=10)
    similar_btn.pack_forget()


# Main view transitions
def show_quiz_selection():
    hide_question_widgets()
    link_button.pack_forget()
    rebuild_quiz_buttons()
    title_label.configure(text="Select a Quiz")
    quiz_frame.pack(pady=10, fill="both", expand=True)
    back_to_quiz_list_button.pack_forget()


def load_quiz(quiz_name):
    global current_quiz, current_question_index, current_quiz_name, quiz_url

    if quiz_name not in quiz_questions:
        feedback_label.configure(text="Please select a valid quiz.", text_color="red")
        return

    quiz_data = quiz_questions[quiz_name]
    current_quiz = quiz_data["questions"]
    current_quiz_name = quiz_name
    current_question_index = 0
    quiz_url = quiz_data.get("url", "")

    if quiz_url:
        link_button.configure(command=lambda: open_link(quiz_url))
        link_button.pack(pady=5)
    else:
        link_button.pack_forget()

    show_question(current_question_index)



def show_question(index):
    global current_question_index
    current_question_index = index

    if index >= len(current_quiz):
        # Quiz complete 
        hide_question_widgets()
        title_label.configure(text="🎉 Quiz Complete!")
        feedback_label.configure(text=f"You finished '{current_quiz_name}'!", text_color="green")
        feedback_label.pack(pady=20)
        back_to_quiz_list_button.pack(pady=10)
        return

    q = current_quiz[index]
    question_label.configure(text=q["question"])
    answer_entry.delete(0, 'end')
    feedback_label.configure(text="")
    show_question_widgets()

    next_button.pack_forget()
    back_to_quiz_list_button.pack(pady=10)


#def select_question(index):
#    global current_question_index
#    current_question_index = index
#    q = current_quiz[index]
#    question_label.configure(text=q["question"])
#    answer_entry.delete(0, 'end')
#    feedback_label.configure(text="")
#    show_question_widgets()
#
#    for widget in quiz_frame.winfo_children():
#        widget.pack_forget()
#
#    back_button.pack(pady=10)
#
#
#def back_to_questions():
#    for widget in quiz_frame.winfo_children():
#        widget.pack(pady=5)
#    hide_question_widgets()
#    quiz_frame.pack(pady=10, fill="both", expand=True)
#    title_label.configure(text="Select a Question")
#    back_to_quiz_list_button.pack(pady=(10, 5))


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
            answer_entry.delete(0, 'end')
            next_button.pack(pady=5)
            similar_btn.pack_forget()
        else:
            feedback_label.configure(text=f"💡 Hint: {ai_feedback}", text_color="orange")
            similar_btn.pack_forget()

    except Exception as e:
        feedback_label.configure(text=f"⚠️ Error: {e}", text_color="red")

def next_question():
    global current_question_index
    next_button.pack_forget()
    show_question(current_question_index + 1)

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
        system_message = {
            "role": "system",
            "content": "You are an astronomy tutor who creates quiz questions."
        }
        user_message = {
            "role": "user",
            "content": f"Create a new astronomy question that is similar to:\n{question}\nDo NOT give the answer."
        }

        new_question_text = AIBot.query_AI([system_message, user_message])

        current_quiz.append({
            "question": new_question_text,
            "correct_answer": ""
        })

        select_question(len(current_quiz) - 1)
        feedback_label.configure(text="🔄 Here's a similar question to try!", text_color="blue")
        similar_btn.pack_forget()

    except Exception as e:
        feedback_label.configure(text=f"⚠️ Error generating similar question: {e}", text_color="red")


def rebuild_quiz_buttons():
    for widget in quiz_frame.winfo_children():
        widget.destroy()

    for quiz_name in quiz_questions.keys():
        btn = ctk.CTkButton(
            quiz_frame,
            text=quiz_name,
            command=lambda name=quiz_name: load_quiz(name),
            width=200,
            fg_color="#1f6aa5",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        btn.pack(pady=5)


def load_quizzes_from_files():
    quiz_questions.clear()
    for nm in os.listdir("quizzes"):
        with open("quizzes" + os.sep + nm, "r", encoding="utf-8", errors="replace") as file:
            data = json.load(file)
            quiz_questions[data["name"]] = {"url": data["url"],
                                            "questions": data["questions"]}


#   Load Quizzes
global quiz_questions
quiz_questions = {}
load_quizzes_from_files()


#   Begin Interface Construction

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Astronomy Quiz Helper")
app.geometry("700x700")
app.bind('<Return>', lambda event: check_answer())

current_quiz = []
current_question_index = None
current_quiz_name = ""
quiz_url = ""

# Title
title_label = ctk.CTkLabel(app, text="Select a Quiz", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=20)

# Scrollable quiz/question frame
quiz_frame = ctk.CTkScrollableFrame(app, height=420, border_color="lightblue", border_width=2)
quiz_frame.pack(pady=10)

# Buttons
question_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=16, weight="bold"),
                              wraplength=600, justify="left")
answer_entry = ctk.CTkEntry(app, width=400)
submit_button = ctk.CTkButton(app, text="Submit Answer")
feedback_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=14), wraplength=600)
similar_btn = ctk.CTkButton(app, text="Try a similar question", command=lambda: generate_similar_question())
back_button = ctk.CTkButton(app, text="⬅ Back to Questions", command=lambda: back_to_questions())
next_button = ctk.CTkButton(app, text="Next Question ➡", command=lambda: next_question())


# Back to Quizzes Button
back_to_quiz_list_button = ctk.CTkButton(
    app,
    text="⬅ Back to Quizzes",
    command=lambda: show_quiz_selection(),
    fg_color="gray30",
    text_color="white",
    corner_radius=8
)
back_to_quiz_list_button.pack_forget()

link_button = ctk.CTkButton(
    app,
    text="🌐 Learn More",
    text_color="skyblue",
    fg_color="transparent",
    hover_color="lightgray",
    font=ctk.CTkFont(size=14, underline=True),
    cursor="hand2",
    corner_radius=0,
    command=lambda: open_link(quiz_url)
)
link_button.pack(pady=5)
link_button.pack_forget()

submit_button.configure(command=check_answer)

# Initial quiz selection buttons
for quiz_name in quiz_questions.keys():
    btn = ctk.CTkButton(
        quiz_frame,
        text=quiz_name,
        command=lambda name=quiz_name: load_quiz(name),
        width=200,
        fg_color="#1f6aa5",
        text_color="white",
        font=ctk.CTkFont(size=14, weight="bold"),
        corner_radius=8
    )
    btn.pack(pady=5)


app.mainloop()