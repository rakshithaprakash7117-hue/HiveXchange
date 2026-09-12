import os

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()


def build_user(username_key, password_key, display_name_key):
    username = os.getenv(username_key)
    password = os.getenv(password_key)
    display_name = os.getenv(display_name_key)

    if not username or not password:
        return None

    return {
        "username": username,
        "password_hash": generate_password_hash(password),
        "display_name": display_name or username
    }


_users = [
    build_user(
        "SYNTH_USER_1_USERNAME",
        "SYNTH_USER_1_PASSWORD",
        "SYNTH_USER_1_DISPLAY_NAME"
    ),
    build_user(
        "SYNTH_USER_2_USERNAME",
        "SYNTH_USER_2_PASSWORD",
        "SYNTH_USER_2_DISPLAY_NAME"
    )
]

SYNTHETIC_USERS = {
    user["username"]: user
    for user in _users
    if user is not None
}


def validate_synthetic_user(username, password):
    user = SYNTHETIC_USERS.get(username)

    if not user:
        return False

    return check_password_hash(
        user["password_hash"],
        password
    )


def get_display_name(username):
    user = SYNTHETIC_USERS.get(username)

    if not user:
        return username

    return user["display_name"]