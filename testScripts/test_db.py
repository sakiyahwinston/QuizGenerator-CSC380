# test.py
import mysql.connector

# ------------------------------
# Database connection config
# ------------------------------
db_config = {
    "host": "altair.cs.oswego.edu",
    "user": "csc380_25f_t4",
    "password": "csc380_25f",
    "database": "csc380_25f_t4",
    "port": 3306
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def check_student_scores(email):
    """Print all quiz scores for a given student email."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1️⃣ Get student ID
        cursor.execute("SELECT studentID, name FROM student WHERE email = %s", (email,))
        student = cursor.fetchone()
        if not student:
            print(f"No student found with email {email}")
            return

        student_id = student["studentID"]
        student_name = student["name"]
        print(f"Scores for {student_name} ({email}):")

        # 2️⃣ Get all quiz scores for this student
        cursor.execute("""
            SELECT q.quizID, q.name AS quiz_name, qs.grade
            FROM quiz q
            LEFT JOIN quiz_scores qs
            ON q.quizID = qs.quizID AND qs.studentID = %s
        """, (student_id,))

        results = cursor.fetchall()
        if not results:
            print("No quizzes found.")
            return

        for row in results:
            quiz_id = row["quizID"]
            quiz_name = row["quiz_name"]
            grade = row["grade"]
            grade_str = f"{grade}%" if grade is not None else "Not taken"
            print(f"- Quiz {quiz_id}: {quiz_name} → {grade_str}")

    except mysql.connector.Error as e:
        print("Error accessing database:", e)

    finally:
        cursor.close()
        conn.close()


def insert_dummy_score(email, quiz_name, grade):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get studentID
        cursor.execute("SELECT studentID FROM student WHERE email=%s", (email,))
        student_row = cursor.fetchone()
        if not student_row:
            print("Student not found")
            return
        student_id = student_row["studentID"]

        # Get quizID
        cursor.execute("SELECT quizID FROM quiz WHERE name=%s LIMIT 1", (quiz_name,))
        quiz_row = cursor.fetchone()
        if not quiz_row:
            print("Quiz not found")
            return
        quiz_id = quiz_row["quizID"]

        # Insert score
        cursor.execute("""
            INSERT INTO quiz_scores (quizID, studentID, grade)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE grade = VALUES(grade)
        """, (quiz_id, student_id, grade))
        conn.commit()
        print(f"Inserted {grade}% for {email} on quiz '{quiz_name}'")

    finally:
        cursor.close()
        conn.close()



if __name__ == "__main__":
    #test_email = input("Enter student email to check scores: ").strip()
    insert_dummy_score("swinston@oswego.edu", "quiz1", 85)
    check_student_scores("swinston@oswego.edu")

