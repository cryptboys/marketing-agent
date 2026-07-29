import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from flask import Flask, jsonify, render_template_string, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from marketing_agent.db import User, get_conn, init_db
from marketing_agent.campaign_manager import CampaignManager
from marketing_agent.governance import audit_tracer
from marketing_agent.dashboard import dashboard
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-123')
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def user_loader(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get(username) # Note: User.get currently needs ID, let's fix this for username login
        # Simplified for now: assuming username IS ID as per User.create implementation
        user = User.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Login failed')
    return "<html><body><form method='post'><input name='username'><input name='password' type='password'><button>Login</button></form></body></html>"

@app.route('/')
@login_required
def index():
    return f"Hello {current_user.username}. <a href='/logout'>Logout</a> | <a href='/campaigns'>Campaigns</a>"

@app.route('/campaigns')
@login_required
def campaigns_page():
    cm = CampaignManager()
    campaigns = cm.get_all_campaigns()
    rows = "".join([f"<tr><td>{c['name']}</td><td>{c['status']}</td><td><form method='post' action='/api/execute_campaign'><input type='hidden' name='campaign_id' value='{c['id']}'><button>Execute</button></form></td></tr>" for c in campaigns])
    return f"<html><body><a href='/'>Back</a><table>{rows}</table></body></html>"

@app.route('/api/execute_campaign', methods=['POST'])
@login_required
def api_execute_campaign():
    campaign_id = request.form['campaign_id']
    cm = CampaignManager()
    campaign = cm.get_campaign_by_id(campaign_id)
    if campaign and campaign['status'] == 'planned':
        cm.execute_campaign(campaign_id)
        flash("Executed")
    return redirect(url_for('campaigns_page'))

if __name__ == '__main__':
    init_db()
    # Create admin if needed
    conn = get_conn()
    if not conn.execute("SELECT * FROM users").fetchone():
        User.create('admin', 'admin123')
    conn.close()
    app.run(debug=True, port=5000)
