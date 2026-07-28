import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from flask import Flask, jsonify, render_template_string, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from marketing_agent.dashboard import dashboard
from marketing_agent.campaign_manager import campaign_manager
from marketing_agent.db import User, init_db

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-marketing-agent'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Initialize DB and create admin user
init_db()
if not User.find_by_username('admin'):
    User.create('admin', 'admin123')

HTML_LOGIN = '''<!DOCTYPE html>
<html>
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-900 flex items-center justify-center h-screen">
    <div class="card p-8 rounded-xl bg-gray-800 text-white w-96">
        <h1 class="text-2xl font-bold mb-6">Login</h1>
        <form method="POST">
            <input name="username" placeholder="Username" class="w-full p-2 mb-4 bg-gray-700 rounded"/>
            <input name="password" type="password" placeholder="Password" class="w-full p-2 mb-4 bg-gray-700 rounded"/>
            <button class="w-full bg-teal-500 p-2 rounded">Login</button>
        </form>
    </div>
</body>
</html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = User.find_by_username(username)
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'])
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template_string(HTML_LOGIN)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# ... (rest of the dashboard code with @login_required)
HTML = '''...''' # (Dashboard HTML as before)

@app.route('/')
@login_required
def index():
    return render_template_string(HTML)

@app.route('/api/dashboard')
@login_required
def get_dashboard():
    return jsonify(dashboard.get_overview())

# ... (other protected routes)
