import mysql.connector

# ----------------------------------------
# WARNING: Do NOT push real passwords to GitHub.
# This is only for local testing.
# ----------------------------------------

DB_HOST = "altair.cs.oswego.edu"
DB_USER = "csc380_25f_t4"       # team account
DB_PASSWORD = "csc380_25f"   # team account password
DB_NAME = "csc380_25f_t4"

def main():
    print("Attempting to connect to the database...")

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=3306
        )

        cursor = conn.cursor()


        if conn.is_connected():
            print("✅ SUCCESS: Connected to MySQL database!")
            print(f"Connected as user: {DB_USER}")
            print(f"Database: {DB_NAME}")

        cursor.execute("SELECT * FROM student;")
        rows = cursor.fetchall()

        if rows:
            print(f"Found {len(rows)} rows:\n")
            for row in rows:
                print(row)
        else:
            print("The table exists, but there are no rows.")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print("❌ Database error:", err)

if __name__ == "__main__":
    main()