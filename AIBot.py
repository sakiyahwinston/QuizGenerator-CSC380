from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://models.inference.ai.azure.com")


def ask_ai_for_feedback(question, correct_answer, student_answer):
    system_message = {
        "role": "system",
        "content": (
            "You are an astronomy tutor. "
            "If the student's answer is correct or reasonably equivalent to the expected answer, "
            "respond with ONLY the exact text: CORRECT_ANSWER. "
            "If incorrect, give a helpful hint without revealing the answer."
        )
    }

    user_message = {
        "role": "user",
        "content": f"""
Question: {question}
Correct answer: {correct_answer}
Student's answer: {student_answer}

Respond as instructed.
"""
    }

    response = query_AI([system_message, user_message])
    return response


def ask_the_bot(prompt):
    system_message = {
        "role": "system",
        "content": (
            "You are an assistant that helps introductory astronomy students. "
            "Answer the question clearly but concisely."
        )
    }

    user_message = {
        "role": "user",
        "content": prompt
    }

    response = query_AI([system_message, user_message])
    return response


def query_AI(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=300,
        top_p=1,
    )
    return response.choices[0].message.content.strip()
