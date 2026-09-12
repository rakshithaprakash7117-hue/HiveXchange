from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from services.event_logger import init_db, log_login_attempt, log_event, get_visitor, create_visitor, register_failed_attempt, should_decieve, evaluate_deception, reset_visitor, register_hard_trigger, update_visitor_state, apply_risk_decay
from config import DATABASE_PATH
from services.data import get_system_status, get_account_summary, get_market_data
import os
from services.detection_engine import handle_probe
from services.synthetic_users import validate_synthetic_user,get_display_name
from services.auth import normal_user_required, decoy_user_required


app = Flask(__name__)

print("DATABASE:", DATABASE_PATH)

init_db()

app.secret_key = os.environ.get("SECRET_KEY")

@app.route('/', methods=['GET'])
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username=request.form.get('username', '')
    password=request.form.get('password', '')

    ip_address=request.remote_addr
    user_agent=request.headers.get('User-Agent')

    if should_decieve(ip_address):
        log_login_attempt(
            ip_address=ip_address,
            username=username,
            password_length=len(password),
            user_agent=user_agent,
            request_method=request.method,
            endpoint=request.path,
            outcome="DECOY_ACCEPTED"
        )

        session["decoy_authenticated"] = True
        session["username"] = username
        session["auth_mode"] = "DECOY"

        return redirect(url_for("dashboard"))

    if validate_synthetic_user(username, password):
        log_login_attempt(
            ip_address=ip_address,
            username=username,
            password_length=len(password),
            user_agent=user_agent,
            request_method=request.method,
            endpoint=request.path,
            outcome="VALID_USER"
        )

        session["user_authenticated"] = True
        session["username"] = username
        session["display_name"] = get_display_name(username)
        session["auth_mode"] = "NORMAL_USER"

        return redirect(url_for("user_dashboard"))

    apply_risk_decay(ip_address)
    register_failed_attempt(ip_address, username)
    evaluate_deception(ip_address)
    update_visitor_state(ip_address)

    log_login_attempt(
        ip_address=ip_address,
        username=username,
        password_length=len(password),
        user_agent=user_agent,
        request_method=request.method,
        endpoint=request.path,
        outcome="FAILED"
    )

    return render_template(
        "login.html",
        error="Email or password is incorrect."
    )


@app.route("/dashboard")
@decoy_user_required
def dashboard():
    log_event(
        ip_address=request.remote_addr,
        event_type="DECOY_ACCESS",
        endpoint=request.path,
        user_agent=request.headers.get("User-Agent"),
        details="Visitor entered decoy trading environment"
    )

    return render_template(
        "dashboard.html",
        username=session.get("decoy_user")
    )


@app.route('/wallet')
def wallet():
    log_event(ip_address=request.remote_addr, event_type='WALLET_ACCESS', endpoint=request.path,
              user_agent=request.headers.get('User-Agent'), details='User accessed synthetic wallet')

    return render_template('wallet.html')

@app.route("/admin")
def admin():
    handle_probe(
        ip_address=request.remote_addr,
        path=request.path,
        method=request.method,
        user_agent=request.headers.get("User-Agent")
    )

    return render_template("404.html"), 404

@app.errorhandler(404)
def page_not_found(error):

    handle_probe(
        ip_address=request.remote_addr,
        path=request.path,
        method=request.method,
        user_agent=request.headers.get("User-Agent")
    )

    return render_template("404.html"), 404

@app.errorhandler(405)
def method_not_allowed(error):

    handle_probe(
        ip_address=request.remote_addr,
        path=request.path,
        method=request.method,
        user_agent=request.headers.get("User-Agent")
    )

    return {
        "error": "Method not allowed"
    }, 405

@app.route("/user_dashboard")
@normal_user_required
def user_dashboard():
    log_event(
        ip_address=request.remote_addr,
        event_type="VALID_USER_ACCESS",
        endpoint=request.path,
        user_agent=request.headers.get("User-Agent"),
        details="Synthetic valid user accessed standard dashboard"
    )

    return render_template(
        "user_dashboard.html",
        display_name=session.get("display_name")
    )

@app.route("/system/status")
def system_status():
    ip_address = request.remote_addr

    log_event(
        ip_address=ip_address,
        event_type="CANARY_ENDPOINT_PROBE",
        endpoint=request.path,
        user_agent=request.headers.get("User-Agent"),
        details="Visitor accessed unlinked system-status canary endpoint"
    )

    register_hard_trigger(
        ip_address=ip_address,
        event_type="CANARY_ENDPOINT_PROBE"
    )

    return jsonify(get_system_status())

@app.route("/api/markets")
def api_markets():
    log_event(
        ip_address=request.remote_addr,
        event_type="API_ACCESS",
        endpoint=request.path,
        user_agent=request.headers.get("User-Agent"),
        details="Synthetic market API requested"
    )

    return jsonify(get_market_data())

@app.route("/api/account/summary")
def api_account_summary():
    log_event(
        ip_address=request.remote_addr,
        event_type="ACCOUNT_API_ACCESS",
        endpoint=request.path,
        user_agent=request.headers.get("User-Agent"),
        details="Synthetic account summary requested"
    )

    return jsonify(get_account_summary())

@app.route("/logout")
def logout():
    ip_address = request.remote_addr
    auth_mode = session.get("auth_mode")

    session.clear()

    if auth_mode == "DECOY":
        reset_visitor(ip_address)

    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
