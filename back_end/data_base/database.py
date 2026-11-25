# back_end/data_base/database.py
import os
import mysql.connector
from mysql.connector import Error


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME", "tea_fertilizer_db"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def create_database_if_not_exists():
    """Local/permitted MySQL server එකක database එක නැත්නම් පමණක් සාදයි"""
    cfg = get_db_config()
    try:
        server_connection = mysql.connector.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
        )
        if server_connection.is_connected():
            cursor = server_connection.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.close()
            server_connection.close()
    except Error as e:
        # Cloud DB වල database කලින්ම සාදා තිබෙන විට මෙය skip වීම සාමාන්‍යයි
        print(f"Note on database creation: {e}")


def create_connection():
    """Database එක සමඟ සම්බන්ධ වීම සඳහා"""
    cfg = get_db_config()
    if os.getenv("SKIP_CREATE_DB", "false").lower() != "true":
        create_database_if_not_exists()

    try:
        connection = mysql.connector.connect(
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
            user=cfg["user"],
            password=cfg["password"],
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None


if __name__ == "__main__":
    conn = create_connection()
    if conn and conn.is_connected():
        print("Database connection test passed successfully!")
        conn.close()
    else:
        print("Database connection test failed!")