import mysql.connector
from mysql.connector import Error

def test_mysql_connection_and_fetch(host, port, user, password, database, table):
    try:
        print("Attempting to connect...")
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=5,
            ssl_disabled=True
        )
        if connection.is_connected():
            print("✔ Successfully connected to MySQL!")
            print("Server version:", connection.get_server_info())

            cursor = connection.cursor()
            query = f"SELECT * FROM {table};"
            cursor.execute(query)

            rows = cursor.fetchall()
            print(f"\n📌 Records in table `{table}` ({len(rows)} rows):")
            for row in rows:
                print(row)

    except Error as e:
        print("❌ Error:", e)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    # ✏️ Replace these with your DB details and table name
    test_mysql_connection_and_fetch(
        host="altair.cs.oswego.edu",
        port=3306,
        user="csc380_25f_t4",
        password="csc380_25f",
        database="csc380_25f_t4",
        table="professor"
    )
