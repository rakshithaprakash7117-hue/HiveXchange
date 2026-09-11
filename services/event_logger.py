import sqlite3
from datetime import datetime, timedelta
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

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitor_state (
                ip_address TEXT PRIMARY KEY,
                failed_attempts INTEGER DEFAULT 0,
                distinct_usernames INTEGER DEFAULT 0,
                risk_score INTEGER DEFAULT 0,
                deception_candidate INTEGER DEFAULT 0)
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempted_usernames (
            ip_address TEXT,
            username TEXT,
            PRIMARY KEY (ip_address, username))
        """)

    conn.commit()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
    """)

    print("TABLES CREATED:", cursor.fetchall())

    conn.close()

def log_login_attempt(ip_address, username, password_length, user_agent, request_method, endpoint, outcome="FAILED"):

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""insert into login_attempts (timestamp, ip_address, username, password_length, user_agent, request_method, endpoint, outcome)
        values (?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), ip_address, username, password_length, user_agent, request_method, endpoint, outcome))

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

def get_visitor(ip_address):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""SELECT failed_attempts, distinct_usernames, risk_score,deception_candidate
                            FROM visitor_state
                            WHERE ip_address = ?
        """, (ip_address,))

    row = cursor.fetchone()
    conn.close()

    return row

def create_visitor(ip_address):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""INSERT OR IGNORE INTO visitor_state (ip_address,failed_attempts,distinct_usernames,risk_score, deception_candidate
        )
        VALUES (?, 0, 0, 0, 0)
    """, (ip_address,))

    conn.commit()
    conn.close()

def register_failed_attempt(ip_address, username):
    create_visitor(ip_address)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""UPDATE visitor_state
        SET failed_attempts = failed_attempts + 1,risk_score = risk_score + 1
           WHERE ip_address = ?""", (ip_address,))

    cursor.execute("""INSERT OR IGNORE INTO attempted_usernames (
                ip_address,
                username
            )
            VALUES (?, ?)
        """, (ip_address, username))

    cursor.execute("""
            SELECT COUNT(*)
            FROM attempted_usernames
            WHERE ip_address = ?
        """, (ip_address,))

    distinct_count = cursor.fetchone()[0]

    extra_score = 0

    if distinct_count >= 3:
        extra_score = 3

    cursor.execute("""
            UPDATE visitor_state
            SET failed_attempts = failed_attempts + 1,
                distinct_usernames = ?,
                risk_score = failed_attempts + 1 + ?
            WHERE ip_address = ?
        """, (
        distinct_count,
        extra_score,
        ip_address
    ))

    conn.commit()
    conn.close()

def should_decieve(ip_address):
    visitor = get_visitor(ip_address)

    if visitor is None:
        return False

    failed_attempts, distinct_usernames, risk_score, deception_candidate = visitor

    return deception_candidate==1

def evaluate_deception(ip_address):
    conn=sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""SELECT failed_attempts,distinct_usernames,risk_score,deception_candidate
        FROM visitor_state WHERE ip_address = ?""", (ip_address,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return

    failed_attempts, distinct_usernames, risk_score, deception_candidate = row

    if deception_candidate == 1:
        conn.close()
        return

    cutoff = (datetime.now() - timedelta(seconds=60)).isoformat()

    cursor.execute("""SELECT COUNT(*)
            FROM login_attempts
            WHERE ip_address = ?
            AND timestamp >= ?
        """, (ip_address, cutoff))

    recent_attempts = cursor.fetchone()[0]

    username_enumeration = distinct_usernames >= 3
    rapid_attempts = recent_attempts >= 5
    repeated_failures = failed_attempts >= 6

    signal_count = sum([username_enumeration, rapid_attempts, repeated_failures])

    if risk_score >= 6 and signal_count >= 2:
        cursor.execute("""
                UPDATE visitor_state
                SET deception_candidate = 1
                WHERE ip_address = ?
            """, (ip_address,))

    conn.commit()
    conn.close()

def reset_visitor(ip_address):

    conn=sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""DELETE FROM visitor_state WHERE ip_address = ?""", (ip_address,))

    conn.commit()
    conn.close()

def register_hard_trigger(ip_address, event_type):
    create_visitor(ip_address)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE visitor_state
        SET deception_candidate = 1
        WHERE ip_address = ?
    """, (ip_address,))

    conn.commit()
    conn.close()








