import sqlite3

from flask import Flask, render_template
from config import DATABASE_PATH

monitor_app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@monitor_app.route("/")
def dashboard():
    conn = get_db_connection()

    visitors = conn.execute("""
        SELECT *
        FROM visitor_state
        ORDER BY risk_score DESC
    """).fetchall()

    recent_events = conn.execute("""
        SELECT *
        FROM events
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    recent_logins = conn.execute("""
        SELECT *
        FROM login_attempts
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    total_logins = conn.execute("""
        SELECT COUNT(*) AS count
        FROM login_attempts
    """).fetchone()["count"]

    failed_logins = conn.execute("""
        SELECT COUNT(*) AS count
        FROM login_attempts
        WHERE outcome = 'FAILED'
    """).fetchone()["count"]

    decoy_logins = conn.execute("""
        SELECT COUNT(*) AS count
        FROM login_attempts
        WHERE outcome = 'DECOY_ACCEPTED'
    """).fetchone()["count"]

    hard_triggers = conn.execute("""
        SELECT COUNT(*) AS count
        FROM events
        WHERE event_type = 'HARD_PATH_PROBE'
    """).fetchone()["count"]

    conn.close()

    return render_template(
        "monitor/dashboard.html",
        visitors=visitors,
        recent_events=recent_events,
        recent_logins=recent_logins,
        total_logins=total_logins,
        failed_logins=failed_logins,
        decoy_logins=decoy_logins,
        hard_triggers=hard_triggers
    )

def display_ip(ip_address):
    if ip_address == "127.0.0.1":
        return "127.0.0.1 (Local test client)"
    return ip_address

monitor_app.jinja_env.globals.update(display_ip=display_ip)

if __name__ == "__main__":
    monitor_app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )