import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from flask import Flask, jsonify, render_template_string, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from marketing_agent.dashboard import dashboard
from marketing_agent.campaign_manager import campaign_manager
from marketing_agent.db import User, init_db

app = Flask(__name__)
app.secret_key = 'hermes-marketing-agent-secret-key-2026'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

init_db()
if not User.find_by_username('admin'):
    User.create('admin', 'admin123')

HTML_LOGIN = '''<!DOCTYPE html>
<html>
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-900 flex items-center justify-center h-screen">
    <div class="bg-gray-800 p-8 rounded-xl text-white w-96">
        <h1 class="text-2xl font-bold mb-6">Marketing Agent Login</h1>
        <form method="POST">
            <input name="username" placeholder="Username" class="w-full p-2 mb-4 bg-gray-700 rounded"/>
            <input name="password" type="password" placeholder="Password" class="w-full p-2 mb-4 bg-gray-700 rounded"/>
            <button class="w-full bg-teal-500 p-2 rounded font-bold">Login</button>
        </form>
        <p class="text-gray-400 mt-4 text-sm text-center">
            Default: admin / admin123
        </p>
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
        flash('Invalid username or password')
    return render_template_string(HTML_LOGIN)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

HTML_DASHBOARD = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Marketing Agent Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-900 text-white">
    <div class="flex">
        <!-- Sidebar -->
        <div class="w-64 bg-gray-800 p-6 min-h-screen">
            <div class="flex justify-between items-center mb-8">
                <h2 class="text-xl font-bold text-teal-400">Hermes AI</h2>
                <a href="/logout" class="text-sm text-gray-400 hover:text-white">Logout</a>
            </div>
            <nav class="space-y-2">
                <div class="p-2 bg-gray-700 rounded text-teal-400">Dashboard</div>
                <div class="p-2 text-gray-400 hover:bg-gray-700 rounded">Campaigns</div>
                <div class="p-2 text-gray-400 hover:bg-gray-700 rounded">Analytics</div>
                <div class="p-2 text-gray-400 hover:bg-gray-700 rounded">Settings</div>
            </nav>
        </div>
        <!-- Main Content -->
        <div class="flex-1 p-8">
            <h1 class="text-2xl mb-8">Welcome, {{ current_user.username }}!</h1>
            <div class="grid grid-cols-4 gap-4 mb-8">
                <div class="bg-gray-800 p-6 rounded-xl"><h3 class="text-gray-400 text-sm uppercase">Total Campaigns</h3><p class="text-3xl font-bold text-blue-400" id="total_campaigns">-</p></div>
                <div class="bg-gray-800 p-6 rounded-xl"><h3 class="text-gray-400 text-sm uppercase">Remaining Budget</h3><p class="text-3xl font-bold text-green-500" id="budget">$-</p></div>
                <div class="bg-gray-800 p-6 rounded-xl"><h3 class="text-gray-400 text-sm uppercase">Audit Events</h3><p class="text-3xl font-bold text-yellow-400" id="audit_count">-</p></div>
                <div class="bg-gray-800 p-6 rounded-xl"><h3 class="text-gray-400 text-sm uppercase">Budget Allocated</h3><p class="text-3xl font-bold" id="budget_allocated">$-</p></div>
            </div>
            <div class="grid grid-cols-3 gap-8">
                <div class="col-span-2 bg-gray-800 p-6 rounded-xl">
                    <h3 class="mb-4">Active Campaigns</h3>
                    <table class="w-full text-sm">
                        <thead><tr class="text-gray-500 uppercase text-xs"><th class="text-left pb-3">ID</th><th class="text-left pb-3">Name</th><th class="text-left pb-3">Status</th><th class="text-left pb-3">Budget</th></tr></thead>
                        <tbody id="campaigns_body"></tbody>
                    </table>
                </div>
                <div class="bg-gray-800 p-6 rounded-xl">
                    <h3 class="mb-4">Security & Budget</h3>
                    <div class="mb-4">
                        <div class="flex justify-between text-sm mb-1">
                            <span class="text-gray-400">Monthly Budget</span>
                            <span id="budget-pct" class="text-gray-400">0% Used</span>
                        </div>
                        <div class="w-full bg-gray-700 rounded-full h-2">
                            <div id="budget-bar" class="bg-teal-500 h-2 rounded-full" style="width:0%"></div>
                        </div>
                    </div>
                    <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-green-500"></div><span class="text-green-400">ACTIVE</span></div>
                </div>
            </div>
        </div>
    </div>
    <script>
        function update() {
            fetch('/api/dashboard').then(r=>r.json()).then(d=>{
                document.getElementById('total_campaigns').textContent=d.campaigns.total_campaigns;
                document.getElementById('budget').textContent='$'+d.budget_remaining;
                document.getElementById('audit_count').textContent=d.audit_log_count;
                document.getElementById('budget_allocated').textContent='$'+d.campaigns.total_budget_allocated;
                let pct=d.campaigns.total_budget_allocated/(d.campaigns.total_budget_allocated+d.budget_remaining)*100||0;
                document.getElementById('budget-bar').style.width=pct.toFixed(0)+'%';
                document.getElementById('budget-pct').textContent=pct.toFixed(0)+'% Used';
            });
            fetch('/api/campaigns').then(r=>r.json()).then(c=>{
                const tbody=document.getElementById('campaigns_body');
                tbody.innerHTML='';
                Object.entries(c).forEach(([id,data])=>{
                    let color=data.status==='executing'?'bg-green-900 text-green-300':'bg-blue-900 text-blue-300';
                    tbody.innerHTML+='<tr class="border-b border-gray-700"><td class="py-3 text-gray-500">'+id+'</td><td class="py-3">'+data.name+'</td><td class="py-3"><span class="px-2 py-1 rounded-full text-xs '+color+'">'+data.status+'</span></td><td class="py-3">$'+data.budget+'</td></tr>';
                });
            });
        }
        update();
        setInterval(update,15000);
    </script>
</body>
</html>'''

@app.route('/')
@login_required
def index():
    return render_template_string(HTML_DASHBOARD, current_user=current_user)

@app.route('/api/dashboard')
@login_required
def get_dashboard():
    return jsonify(dashboard.get_overview())

@app.route('/api/campaigns')
@login_required
def get_campaigns():
    return jsonify(campaign_manager.campaigns)

if __name__ == '__main__':
    app.run(port=5000, debug=False)