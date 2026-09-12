from functools import wraps
from flask import session, redirect, url_for


def normal_user_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if session.get("auth_mode") != "NORMAL_USER":
            return redirect(url_for("home"))

        return view_function(*args, **kwargs)

    return wrapped


def decoy_user_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if session.get("auth_mode") != "DECOY":
            return redirect(url_for("home"))

        return view_function(*args, **kwargs)

    return wrapped