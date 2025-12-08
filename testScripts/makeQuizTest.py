import mysql.connector
import json

# --------------------------
# Database connection
# --------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="altair.cs.oswego.edu",
        user="csc380_25f_t4",
        password="csc380_25f",
        database="csc380_25f_t4",
        port=3306
    )


# --------------------------
# Load quiz1.json
# --------------------------
def load_quiz_json():
    with open("quizzes/quiz1.json", "r") as f:
        return json.load(f)


# --------------------------
# Insert quiz into DB
# --------------------------
def insert_quiz():
    quiz_data = load_quiz_json()
    quiz_name = quiz_data["name"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if quiz exists
    cursor.execute("SELECT quizID FROM quiz WHERE name = %s", (quiz_name,))
    existing = cursor.fetchone()

    if existing:
        print(f"Quiz '{quiz_name}' already exists in database.")
        print(f"quizID = {existing['quizID']}")
        conn.close()
        return

    # Insert quiz
    cursor.execute("INSERT INTO quiz (name) VALUES (%s)", (quiz_name,))
    conn.commit()

    print(f"Quiz '{quiz_name}' successfully inserted!")

    cursor.execute("SELECT LAST_INSERT_ID() AS id")
    quiz_id = cursor.fetchone()["id"]

    print(f"New quizID = {quiz_id}")

    conn.close()


# --------------------------
# Run script
# --------------------------
if __name__ == "__main__":
    insert_quiz()
