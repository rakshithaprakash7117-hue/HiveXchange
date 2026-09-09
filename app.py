from flask import Flask, render_template, request, redirect, url_for, session
from services.event_logger import init_db, log_login_attempt, log_event
from config import DATABASE_PATH
import os

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

    log_login_attempt(ip_address=ip_address, username=username, password_length=len(password),
                      user_agent=user_agent, request_method=request.method, endpoint=request.path)


    return render_template('login.html', error='Login Failed')


@app.route('/dashboard')
def dashboard():
    log_event(ip_address=request.remote_addr, event_type='DECOY_ACCESS', endpoint=request.path,
              user_agent=request.headers.get('User-Agent'), details='User accessed synthetic training dashboard')

    return render_template('dashboard.html')

@app.route('/wallet')
def wallet():
    log_event(ip_address=request.remote_addr, event_type='WALLET_ACCESS', endpoint=request.path,
              user_agent=request.headers.get('User-Agent'), details='User accessed synthetic wallet')

    return render_template('wallet.html')

@app.route('/admin')
def admin():
    log_event(ip_address=request.remote_addr, event_type='ADMIN_PROBE', endpoint=request.path,
              user_agent=request.headers.get('User-Agent'), details='Visitor attempted access to decoy admin endpoint')

    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
