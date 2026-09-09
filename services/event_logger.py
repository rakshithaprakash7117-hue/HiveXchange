import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def init_db():
    print("INIT_DB CALLED")
    print("DATABASE PATH:", DATABASE_PATH)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip_address TEXT,
            username TEXT,
            password_length INTEGER,
            user_agent TEXT,
            request_method TEXT,
            endpoint TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip_address TEXT,
            event_type TEXT NOT NULL,
            endpoint TEXT,
            user_agent TEXT,
            details TEXT
        )
    """)

    conn.commit()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
    """)

    print("TABLES CREATED:", cursor.fetchall())

    conn.close()

def log_login_attempt(ip_address, username, password_length, user_agent, request_method, endpoint):

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""insert into login_attempts (timestamp, ip_address, username, password_length, user_agent, request_method, endpoint)
        values (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), ip_address, username, password_length, user_agent, request_method, endpoint))

    conn.commit()
    conn.close()

def log_event(ip_address, event_type, endpoint, user_agent, details=""):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""insert into events (timestamp, ip_address, event_type, endpoint, user_agent, details)
        values (?, ?, ?, ?, ?, ?)""",
        (datetime.now().isoformat(), ip_address, event_type, endpoint, user_agent, details))

    conn.commit()
    conn.close()



