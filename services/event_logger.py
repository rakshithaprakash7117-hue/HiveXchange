import sqlite3
from datetime import datetime, timedelta, timezone
from config import DATABASE_PATH,RISK_DECAY_INTERVAL_SECONDS,RISK_DECAY_AMOUNT

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

    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
           INSERT OR IGNORE INTO visitor_state (
               ip_address,
               failed_attempts,
               distinct_usernames,
               risk_score,
               deception_candidate,
               state,
               first_seen,
               last_seen
           )
           VALUES (?, 0, 0, 0, 0, 'NORMAL', ?, ?)
       """, (
        ip_address,
        now,
        now
    ))

    conn.commit()
    conn.close()

def touch_visitor(ip_address):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        UPDATE visitor_state
        SET last_seen = ?
        WHERE ip_address = ?
    """, (
        now,
        ip_address
    ))

    conn.commit()
    conn.close()

def register_failed_attempt(ip_address, username):
    create_visitor(ip_address)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO attempted_usernames (
            ip_address,
            username
        )
        VALUES (?, ?)
    """, (
        ip_address,
        username
    ))

    cursor.execute("""
        SELECT COUNT(*)
        FROM attempted_usernames
        WHERE ip_address = ?
    """, (ip_address,))

    distinct_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT distinct_usernames
        FROM visitor_state
        WHERE ip_address = ?
    """, (ip_address,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return

    old_distinct_count = row[0]

    risk_increment = 1

    if old_distinct_count < 3 and distinct_count >= 3:
        risk_increment += 3

    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        UPDATE visitor_state
        SET failed_attempts = failed_attempts + 1,
            distinct_usernames = ?,
            risk_score = risk_score + ?,
            last_seen = ?
        WHERE ip_address = ?
    """, (
        distinct_count,
        risk_increment,
        now,
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
    touch_visitor(ip_address)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE visitor_state
        SET deception_candidate = 1
        WHERE ip_address = ?
    """, (ip_address,))

    conn.commit()
    conn.close()

def update_visitor_state(ip_address):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT risk_score, deception_candidate
        FROM visitor_state
        WHERE ip_address = ?
    """, (ip_address,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return

    risk_score, deception_candidate = row

    if deception_candidate == 1:
        state = "DECEPTION"
    elif risk_score >= 6:
        state = "SUSPICIOUS"
    elif risk_score >= 3:
        state = "WATCH"
    else:
        state = "NORMAL"

    cursor.execute("""
        UPDATE visitor_state
        SET state = ?
        WHERE ip_address = ?
    """, (state, ip_address))

    conn.commit()
    conn.close()

def apply_risk_decay(ip_address):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT risk_score, last_seen, deception_candidate
        FROM visitor_state
        WHERE ip_address = ?
    """, (ip_address,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return

    risk_score, last_seen, deception_candidate = row

    # Never decay an active deception decision
    if deception_candidate == 1 or not last_seen:
        conn.close()
        return

    last_seen_time = datetime.fromisoformat(last_seen)
    now = datetime.now(timezone.utc)

    elapsed_seconds = (now - last_seen_time).total_seconds()

    intervals = int(
        elapsed_seconds // RISK_DECAY_INTERVAL_SECONDS
    )

    if intervals > 0:
        reduction = intervals * RISK_DECAY_AMOUNT
        new_score = max(0, risk_score - reduction)

        cursor.execute("""
            UPDATE visitor_state
            SET risk_score = ?
            WHERE ip_address = ?
        """, (
            new_score,
            ip_address
        ))

        conn.commit()

    conn.close()


