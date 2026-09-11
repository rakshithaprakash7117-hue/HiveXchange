import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "honeypot.db")

os.makedirs(DATABASE_DIR, exist_ok=True)

ADMIN_PROBE_WEIGHT = 4
DECEPTION_THRESHOLD = 6

HARD_TRIGGER_EVENTS = {
    "ADMIN_PROBE",
    "CANARY_ENDPOINT_PROBE"
}

DECEPTION_THRESHOLD = 6

HARD_TRIGGER_PATHS = {
    "/admin",
    "/system/status",
    "/.env",
    "/.git/config"
}

SENSITIVE_PROBE_PATHS = {
    "/config",
    "/backup",
    "/internal",
    "/debug",
    "/openapi.json",
    "/swagger.json"
}

PROBE_WINDOW_SECONDS = 60
PROBE_COUNT_THRESHOLD = 3

SUSPICIOUS_METHODS = {
    "PUT",
    "DELETE",
    "PATCH"
}