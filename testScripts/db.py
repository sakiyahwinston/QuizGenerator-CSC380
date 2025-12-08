# db.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "altair.cs.oswego"),
    "user": os.environ.get("DB_USER", "csc380_25f_t4"),
    "password": os.environ.get("DB_PASSWORD", "csc380_25f"),
    "database": os.environ.get("DB_NAME", "csc380_25f_t4"),
}

def get_connection():
    """
    Returns a MySQL connection object.
    Returns None if connection fails.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
