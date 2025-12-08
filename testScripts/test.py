import mysql.connector
from mysql.connector import Error

def test_mysql_connection(host, port, user, password, database):
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
            print("✔ Successfully connected to the MySQL database!")
            print("Server version:", connection.get_server_info())
        else:
            print("✘ Connection failed.")
    except Error as e:
        print("❌ Error:", e)
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Connection closed.")

if __name__ == "__main__":
    # ✏️ Replace these with your remote DB details
    test_mysql_connection(
        host="altair.cs.oswego.edu",
        port=3306,
        user="csc380_25f_t4",
        password="csc380_25f",
        database="csc380_25f_t4"
    )
