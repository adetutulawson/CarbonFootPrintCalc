import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from modules.database import get_db_connection

# DATABASE_FILE = r"C:\Users\User\Documents\FinalMSCProject\database\CARBON_FOOTPRINT.db"

def register_user(username, password):
    # Use 'pbkdf2:sha256' instead of 'sha256'
    password = generate_password_hash(password, method='pbkdf2:sha256')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()


def login_user(username, password):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            return check_password_hash(result[0], password)
        else:
            return False
        
