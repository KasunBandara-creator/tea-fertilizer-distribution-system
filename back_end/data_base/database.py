# database.py
import mysql.connector
from mysql.connector import Error

def create_database_if_not_exists():
    """Database එක නැත්නම් Python හරහාම එය නිර්මාණය කිරීම සඳහා"""
    try:
        # මුලින්ම Database නම සඳහන් නොකර MySQL Server එකට සම්බන්ධ වෙමු
        server_connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        if server_connection.is_connected():
            cursor = server_connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS tea_fertilizer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.close()
            server_connection.close()
    except Error as e:
        print(f"Error creating database: {e}")

def create_connection():
    """සාදන ලද tea_fertilizer_db සමඟ සම්බන්ධ වීම සඳහා"""
    # මුලින්ම Database එක තියෙනවද බලා, නැත්නම් සාදා ගනී
    create_database_if_not_exists()
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='tea_fertilizer_db',
            user='root',       
            password=''        
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# මෙම ගොනුව කෙලින්ම Run කළ විට සම්බන්ධතාවය පරීක්ෂා කිරීම සඳහා
if __name__ == "__main__":
    conn = create_connection()
    if conn and conn.is_connected():
        print("Database connection test passed successfully!")
        conn.close()
    else:
        print("Database connection test failed!")