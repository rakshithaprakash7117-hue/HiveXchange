import sqlite3
from datetime import datetime, timedelta

from config import (
    DATABASE_PATH,
    HARD_TRIGGER_PATHS,
    SENSITIVE_PROBE_PATHS,
    PROBE_WINDOW_SECONDS,
    PROBE_COUNT_THRESHOLD,
    SUSPICIOUS_METHODS
)

from services.event_logger import (
    create_visitor,
    log_event,
    register_hard_trigger
)


def handle_probe(ip_address, path, method, user_agent):
    """
    Analyse suspicious endpoint/method probing.

    Returns:
        "HARD_TRIGGER"
        "SENSITIVE_PROBE"
        "UNUSUAL_METHOD"
        None
    """

    create_visitor(ip_address)

    # Immediate high-confidence trigger
    if path in HARD_TRIGGER_PATHS:

        log_event(
            ip_address=ip_address,
            event_type="HARD_PATH_PROBE",
            endpoint=path,
            user_agent=user_agent,
            details=f"High-confidence probe: {path}"
        )

        register_hard_trigger(
            ip_address,
            "HARD_PATH_PROBE"
        )

        return "HARD_TRIGGER"

    # Suspicious method against interesting endpoint
    if method in SUSPICIOUS_METHODS:

        log_event(
            ip_address=ip_address,
            event_type="UNUSUAL_METHOD_PROBE",
            endpoint=path,
            user_agent=user_agent,
            details=f"{method} request sent to {path}"
        )

        if path in SENSITIVE_PROBE_PATHS:
            register_hard_trigger(
                ip_address,
                "UNUSUAL_METHOD_PROBE"
            )

        return "UNUSUAL_METHOD"

    # Ordinary sensitive route probe
    if path in SENSITIVE_PROBE_PATHS:

        log_event(
            ip_address=ip_address,
            event_type="SENSITIVE_PATH_PROBE",
            endpoint=path,
            user_agent=user_agent,
            details=f"Sensitive-looking endpoint requested: {path}"
        )

        evaluate_probe_sequence(ip_address)

        return "SENSITIVE_PROBE"

    return None

def evaluate_probe_sequence(ip_address):

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cutoff = (
        datetime.now()
        - timedelta(seconds=PROBE_WINDOW_SECONDS)
    ).isoformat()

    cursor.execute("""
        SELECT COUNT(DISTINCT endpoint)
        FROM events
        WHERE ip_address = ?
        AND event_type = 'SENSITIVE_PATH_PROBE'
        AND timestamp >= ?
    """, (
        ip_address,
        cutoff
    ))

    probe_count = cursor.fetchone()[0]

    if probe_count >= PROBE_COUNT_THRESHOLD:

        cursor.execute("""
            UPDATE visitor_state
            SET deception_candidate = 1
            WHERE ip_address = ?
        """, (ip_address,))

    conn.commit()
    conn.close()