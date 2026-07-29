import sys, os

site_packages_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'venv', 'Lib', 'site-packages'))
if os.path.exists(site_packages_path) and site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from flask import Flask, jsonify, render_template_string, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from marketing_agent.db import User, get_conn, init_db
from marketing_agent.campaign_manager import CampaignManager
from marketing_agent.governance import audit_tracer
from marketing_agent.dashboard import dashboard
try:
    from marketing_agent.google_ads_client import google_ads_client
except ModuleNotFoundError:
    google_ads_client = None # Handle case where google-ads library is not installed
    print("Warning: google-ads library not found. Google Ads integration will be limited.")

from google_auth_oauthlib.flow import Flow
import google.oauth2.credentials
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
        # Use the improved User.get which checks both ID and username
        user = User.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login failed. Check your username and password.')
    return render_template_string(HTML_LOGIN)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    overview = dashboard.get_overview()
    # Ensure summary has all expected keys with defaults
    summary = {
        'total_campaigns': overview.get('campaigns', {}).get('total_campaigns', 0),
        'total_budget': overview.get('campaigns', {}).get('total_budget_allocated', 0),
        'planned': overview.get('campaigns', {}).get('planned', 0),
        'executing': overview.get('campaigns', {}).get('executing', 0),
    }
    return render_template_string(HTML_DASHBOARD, current_user=current_user, summary=summary)

@app.route('/campaigns')
@login_required
def campaigns_page():
    cm = CampaignManager()
    campaigns = cm.get_all_campaigns()
    rows = "".join([f"<tr><td>{c['name']}</td><td>{c['status']}</td><td><form method='post' action='/api/execute_campaign'><input type='hidden' name='campaign_id' value='{c['id']}'><button class='bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded'>Execute</button></form></td></tr>" for c in campaigns])
    return render_template_string(HTML_CAMPAIGNS, rows=rows)

@app.route('/analytics')
@login_required
def analytics_page():
    # Fetch some analytics data to pass to template
    conn = get_conn()
    total_campaigns = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
    total_budget = conn.execute("SELECT COALESCE(SUM(budget), 0) FROM campaigns").fetchone()[0]
    conn.close()
    
    analytics_data = {
        'total_campaigns': total_campaigns,
        'total_budget': total_budget
    }
    return render_template_string(HTML_ANALYTICS, current_user=current_user, analytics_data=analytics_data)

@app.route('/integrations')
@login_required
def integrations_page():
    conn = get_conn()
    row = conn.execute("SELECT * FROM integrations WHERE platform = ?", ('google_ads',)).fetchone()
    conn.close()
    google_ads_connected = bool(row)

    auth_url = None
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
    developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
    google_ads_customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    credentials_available = all([client_id, client_secret, developer_token, google_ads_customer_id])

    if not google_ads_connected:
        if credentials_available:
            try:
                from google_auth_oauthlib.flow import Flow
                flow = Flow.from_client_config(
                    {
                        "installed": {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost:5000/google/auth/callback"],
                        }
                    },
                    scopes=["https://www.googleapis.com/auth/adwords"],
                )
                flow.redirect_uri = "http://localhost:5000/google/auth/callback"
                auth_url, _ = flow.authorization_url(prompt="consent")
            except Exception as e:
                flash(f"Error getting auth URL: {e}", "error")

    return render_template_string(HTML_INTEGRATIONS, current_user=current_user, google_ads_connected=google_ads_connected, auth_url=auth_url, credentials_available=credentials_available)

@app.route('/api/plan_campaign', methods=['POST'])
@login_required
def api_plan_campaign():
    data = request.get_json()
    cm = CampaignManager()
    try:
        campaign_id = cm.plan_campaign(data['name'], data['objective'], data['target_audience'], data['budget'])
        audit_tracer.add_trace('plan_campaign_ui', {'campaign_id': campaign_id})
        return jsonify({'status': 'success', 'campaign_id': campaign_id}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/execute_campaign', methods=['POST'])
@login_required
def api_execute_campaign():
    campaign_id = request.form['campaign_id']
    cm = CampaignManager()
    campaign = cm.get_campaign_by_id(campaign_id)
    if campaign and campaign['status'] == 'planned':
        result = cm.execute_campaign(campaign_id)
        audit_tracer.add_trace('execute_campaign_ui', {'campaign_id': campaign_id, 'result': result})
        flash("Executed")
    elif campaign and campaign['status'] == 'executing':
         flash(f"Campaign {campaign_id} is already executing.")
    else:
        flash(f"Invalid campaign status or ID. Status: {campaign.get('status') if campaign else 'Not found'}")
    return redirect(url_for('campaigns_page'))

@app.route('/api/campaigns', methods=['GET'])
@login_required
def api_campaigns():
    cm = CampaignManager()
    campaigns = cm.get_all_campaigns()
    return jsonify(campaigns)

@app.route('/api/analyze_keywords', methods=['POST'])
@login_required
def api_analyze_keywords():
    from marketing_agent.data_analyzer import data_analyzer
    data = request.get_json()
    keywords = data.get('keywords')
    if not keywords:
        return jsonify({'status': 'error', 'message': 'No keywords provided'}), 400
    try:
        analysis_results = data_analyzer.analyze_keywords(keywords.split())
        audit_tracer.add_trace('analyze_keywords_ui', {'keywords': keywords})
        return jsonify(analysis_results)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    overview = dashboard.get_overview()
    return jsonify(overview)

@app.route('/api/google-ads/list-campaigns', methods=['POST'])
@login_required
def api_google_ads_list_campaigns():
    if google_ads_client is None:
        return jsonify({'status': 'error', 'message': 'Google Ads client not available. Please ensure google-ads library is installed.'}), 500
    try:
        campaigns = google_ads_client.list_campaigns()
        return jsonify(campaigns)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/google/auth/callback')
def google_ads_callback():
    try:
        client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
        developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
        google_ads_customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")

        if not all([client_id, client_secret, developer_token, google_ads_customer_id]):
            flash('Google Ads integration not fully configured. Please check .env variables.', 'warning')
            return redirect(url_for('integrations_page'))

        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:5000/google/auth/callback"],
                }
            },
            scopes=["https://www.googleapis.com/auth/adwords"],
            state=session.get('_oauth_state') # Use Flask session for state
        )
        
        session.pop('_oauth_state', None) # Clean up state from session
        
        flow.redirect_uri = "http://localhost:5000/google/auth/callback"
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO integrations (platform, client_id, client_secret, developer_token, refresh_token, customer_id, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       ('google_ads', client_id, client_secret, developer_token, credentials.refresh_token, google_ads_customer_id, credentials.expiry.isoformat()))
        conn.commit()
        conn.close()

        flash('Successfully connected to Google Ads!', 'success')
        return redirect(url_for('integrations_page'))

    except Exception as e:
        flash(f'Error during Google Ads authentication: {e}', 'error')
        return redirect(url_for('integrations_page'))

# --- HTML Templates (Inline) ---
HTML_LOGIN = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-300 font-sans flex items-center justify-center min-h-screen">
    <div class="bg-gray-800 p-8 rounded-lg shadow-lg max-w-sm w-full">
        <h1 class="text-2xl font-bold mb-4 text-center text-teal-400">Login</h1>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="bg-red-700 text-white p-3 rounded mb-4">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
        <form method="post">
            <div class="mb-4">
                <label for="username" class="block text-gray-300 text-sm font-bold mb-2">Username:</label>
                <input type="text" id="username" name="username" class="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline" required>
            </div>
            <div class="mb-6">
                <label for="password" class="block text-gray-300 text-sm font-bold mb-2">Password:</label>
                <input type="password" id="password" name="password" class="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white mb-3 leading-tight focus:outline-none focus:shadow-outline" required>
            </div>
            <div class="flex items-center justify-between">
                <button type="submit" class="bg-teal-600 hover:bg-teal-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full transition duration-300">
                    Login
                </button>
            </div>
        </form>
    </div>
</body>
</html>
"""

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - Marketing Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #1a202c; color: #cbd5e0; }
        .sidebar { background-color: #2d3748; padding: 1rem; height: 100vh; }
        .main-content { padding: 2rem; }
        .card { background-color: #2d3748; padding: 1.5rem; border-radius: 0.5rem; }
        .text-teal-400 { color: #4fd1c5; }
        .text-gray-300 { color: #cbd5e0; }
        .border-teal-400 { border-color: #4fd1c5; }
        .border-gray-700 { border-color: #4a5568; }
        .bg-gray-700 { background-color: #4a5568; }
        .nav-link:hover { background-color: #4a5568; }
    </style>
</head>
<body class="flex h-screen bg-gray-900 text-gray-300 font-sans">
    <aside class="sidebar w-64">
        <div class="p-4 mb-4 border-b border-gray-700">
            <h2 class="text-xl font-bold text-teal-400">Marketing Agent</h2>
            <p class="text-sm text-gray-400">Welcome, {{ current_user.username }}!</p>
        </div>
        <nav>
            <ul>
                <li><a href="/" class="nav-link block py-2 px-4 rounded transition duration-200">Dashboard</a></li>
                <li><a href="/campaigns" class="nav-link block py-2 px-4 rounded transition duration-200">Campaigns</a></li>
                <li><a href="/analytics" class="nav-link block py-2 px-4 rounded transition duration-200">Analytics</a></li>
                <li><a href="/integrations" class="nav-link block py-2 px-4 rounded transition duration-200">Integrations</a></li>
            </ul>
        </nav>
        <div class="absolute bottom-4 px-4">
            <a href="/logout" class="block py-2 px-4 rounded bg-red-600 hover:bg-red-700 text-white text-center transition duration-200">Logout</a>
        </div>
    </aside>
    <main class="main-content flex-1 overflow-y-auto">
        <h1 class="text-3xl font-bold mb-6 text-teal-400">Dashboard Overview</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="card text-center">
                <h3 class="text-lg mb-2">Total Campaigns</h3>
                <p class="text-4xl font-bold text-blue-400">{{ summary.total_campaigns if summary else 'N/A' }}</p>
            </div>
            <div class="card text-center">
                <h3 class="text-lg mb-2">Total Budget</h3>
                <p class="text-4xl font-bold text-green-400">${{ '{:,.0f}'.format(summary.total_budget) if summary and summary.total_budget else 'N/A' }}</p>
            </div>
            <div class="card text-center">
                <h3 class="text-lg mb-2">Planned</h3>
                <p class="text-4xl font-bold text-yellow-400">{{ summary.planned if summary else 'N/A' }}</p>
            </div>
            <div class="card text-center">
                <h3 class="text-lg mb-2">Executing</h3>
                <p class="text-4xl font-bold text-red-400">{{ summary.executing if summary else 'N/A' }}</p>
            </div>
        </div>
        <div class="mt-8">
            <h2 class="text-2xl font-bold mb-4">Recent Activity</h2>
            <div class="card p-0 overflow-hidden">
                <div class="p-4 border-b border-gray-700 flex justify-between items-center">
                    <h3 class="text-xl">Latest Audit Logs</h3>
                    <a href="#" class="text-sm text-teal-400 hover:underline">View All</a>
                </div>
                <div class="p-4">
                    <ul class="space-y-2">
                        <li><span class="font-semibold">1. Execute campaign</span> - Yesterday</li>
                        <li><span class="font-semibold">2. Plan campaign</span> - 2 days ago</li>
                        <li><span class="font-semibold">3. Analyze keywords</span> - 3 days ago</li>
                    </ul>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
"""

HTML_CAMPAIGNS = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Campaigns - Marketing Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #1a202c; color: #cbd5e0; }
        .sidebar { background-color: #2d3748; padding: 1rem; height: 100vh; }
        .main-content { padding: 2rem; }
        .card { background-color: #2d3748; padding: 1.5rem; border-radius: 0.5rem; }
        .text-teal-400 { color: #4fd1c5; }
        .text-gray-300 { color: #cbd5e0; }
        .border-teal-400 { border-color: #4fd1c5; }
        .border-gray-700 { border-color: #4a5568; }
        .bg-gray-700 { background-color: #4a5568; }
        .nav-link:hover { background-color: #4a5568; }
        .status-planned { color: #3b82f6; }
        .status-executing { color: #10b981; }
        .status-completed { color: #6b7280; }
    </style>
</head>
<body class="flex h-screen bg-gray-900 text-gray-300 font-sans">
    <aside class="sidebar w-64">
        <div class="p-4 mb-4 border-b border-gray-700">
            <h2 class="text-xl font-bold text-teal-400">Marketing Agent</h2>
            <p class="text-sm text-gray-400">Welcome, {{ current_user.username }}!</p>
        </div>
        <nav>
            <ul>
                <li><a href="/" class="nav-link block py-2 px-4 rounded transition duration-200">Dashboard</a></li>
                <li><a href="/campaigns" class="nav-link block py-2 px-4 rounded transition duration-200">Campaigns</a></li>
                <li><a href="/analytics" class="nav-link block py-2 px-4 rounded transition duration-200">Analytics</a></li>
                <li><a href="/integrations" class="nav-link block py-2 px-4 rounded transition duration-200">Integrations</a></li>
            </ul>
        </nav>
        <div class="absolute bottom-4 px-4">
            <a href="/logout" class="block py-2 px-4 rounded bg-red-600 hover:bg-red-700 text-white text-center transition duration-200">Logout</a>
        </div>
    </aside>
    <main class="main-content flex-1 overflow-y-auto">
        <h1 class="text-3xl font-bold mb-6 text-teal-400">Campaign Management</h1>
        <div class="card mb-6 p-6">
            <h2 class="text-2xl font-bold mb-4">Plan New Campaign</h2>
            <form id="plan-campaign-form">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label for="name" class="block text-sm font-medium mb-1">Campaign Name</label>
                        <input type="text" id="name" name="name" class="w-full p-2 rounded bg-gray-700 border border-gray-600" required>
                    </div>
                    <div>
                        <label for="objective" class="block text-sm font-medium mb-1">Objective</label>
                        <input type="text" id="objective" name="objective" class="w-full p-2 rounded bg-gray-700 border border-gray-600" required>
                    </div>
                    <div>
                        <label for="target_audience" class="block text-sm font-medium mb-1">Target Audience</label>
                        <input type="text" id="target_audience" name="target_audience" class="w-full p-2 rounded bg-gray-700 border border-gray-600" required>
                    </div>
                    <div>
                        <label for="budget" class="block text-sm font-medium mb-1">Budget ($)</label>
                        <input type="number" id="budget" name="budget" class="w-full p-2 rounded bg-gray-700 border border-gray-600" required>
                    </div>
                </div>
                <button type="submit" class="mt-6 px-4 py-2 bg-teal-600 hover:bg-teal-700 rounded transition duration-200">Plan Campaign</button>
            </form>
        </div>
        <div class="card p-6">
            <h2 class="text-2xl font-bold mb-4">All Campaigns</h2>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-700">
                            <th class="p-2 text-left">Name</th>
                            <th class="p-2 text-left">Objective</th>
                            <th class="p-2 text-left">Status</th>
                            <th class="p-2 text-left">Budget</th>
                            <th class="p-2 text-left">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{ rows }}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
    <script>
        document.getElementById('plan-campaign-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                name: formData.get('name'),
                objective: formData.get('objective'),
                target_audience: formData.get('target_audience'),
                budget: parseFloat(formData.get('budget'))
            };
            try {
                const response = await fetch('/api/plan_campaign', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.status === 'success') {
                    alert('Campaign planned successfully!');
                    window.location.reload();
                } else {
                    alert('Failed to plan campaign: ' + result.message);
                }
            } catch (error) {
                alert('Error planning campaign: ' + error);
            }
        });
    </script>
</body>
</html>
"""

HTML_ANALYTICS = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Analytics - Marketing Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #1a202c; color: #cbd5e0; }
        .sidebar { background-color: #2d3748; padding: 1rem; height: 100vh; }
        .main-content { padding: 2rem; }
        .card { background-color: #2d3748; padding: 1.5rem; border-radius: 0.5rem; }
        .text-teal-400 { color: #4fd1c5; }
        .text-gray-300 { color: #cbd5e0; }
        .border-teal-400 { border-color: #4fd1c5; }
        .border-gray-700 { border-color: #4a5568; }
        .bg-gray-700 { background-color: #4a5568; }
        .nav-link:hover { background-color: #4a5568; }
        .chart-container { height: 300px; }
    </style>
</head>
<body class="flex h-screen bg-gray-900 text-gray-300 font-sans">
    <aside class="sidebar w-64">
        <div class="p-4 mb-4 border-b border-gray-700">
            <h2 class="text-xl font-bold text-teal-400">Marketing Agent</h2>
            <p class="text-sm text-gray-400">Welcome, {{ current_user.username }}!</p>
        </div>
        <nav>
            <ul>
                <li><a href="/" class="nav-link block py-2 px-4 rounded transition duration-200">Dashboard</a></li>
                <li><a href="/campaigns" class="nav-link block py-2 px-4 rounded transition duration-200">Campaigns</a></li>
                <li><a href="/analytics" class="nav-link block py-2 px-4 rounded transition duration-200">Analytics</a></li>
                <li><a href="/integrations" class="nav-link block py-2 px-4 rounded transition duration-200">Integrations</a></li>
            </ul>
        </nav>
        <div class="absolute bottom-4 px-4">
            <a href="/logout" class="block py-2 px-4 rounded bg-red-600 hover:bg-red-700 text-white text-center transition duration-200">Logout</a>
        </div>
    </aside>
    <main class="main-content flex-1 overflow-y-auto">
        <h1 class="text-3xl font-bold mb-6 text-teal-400">Analytics</h1>
        <div class="card mb-6 p-6">
            <h2 class="text-2xl font-bold mb-4">Keyword Analysis</h2>
            <form id="keyword-analysis-form">
                <div class="flex gap-4 mb-4">
                    <input type="text" id="keywords" name="keywords" class="flex-grow p-2 rounded bg-gray-700 border border-gray-600" placeholder="Enter keywords (e.g., 'summer sale discount')" required>
                    <button type="submit" class="px-4 py-2 bg-teal-600 hover:bg-teal-700 rounded transition duration-200">Analyze</button>
                </div>
            </form>
            <div id="analysis-results" class="mt-4 p-4 bg-gray-800 rounded border border-gray-700 min-h-[100px]">
                <p>Enter keywords above and click Analyze.</p>
            </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="card chart-container">
                <h3 class="text-xl font-bold mb-4">Campaign Performance</h3>
                <div id="campaign-performance-chart">[Chart Placeholder]</div>
            </div>
            <div class="card chart-container">
                <h3 class="text-xl font-bold mb-4">Budget Allocation</h3>
                <div id="budget-allocation-chart">[Chart Placeholder]</div>
            </div>
        </div>
    </main>
    <script>
        document.getElementById('keyword-analysis-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const keywordsInput = document.getElementById('keywords');
            const analysisResultsDiv = document.getElementById('analysis-results');
            const keywords = keywordsInput.value;
            if (!keywords) return;
            try {
                analysisResultsDiv.innerHTML = '<p>Analyzing...</p>';
                const response = await fetch('/api/analyze_keywords', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ keywords: keywords })
                });
                const result = await response.json();
                if (result.status === 'success') {
                    analysisResultsDiv.innerHTML = `<pre>${JSON.stringify(result.data, null, 2)}</pre>`;
                } else {
                    analysisResultsDiv.innerHTML = `<p class='text-red-500'>Error: ${result.message}</p>`;
                }
            } catch (error) {
                analysisResultsDiv.innerHTML = `<p class='text-red-500'>Network or parsing error: ${error}</p>`;
            }
        });
    </script>
</body>
</html>
"""

HTML_INTEGRATIONS = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Integrations - Marketing Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #1a202c; color: #cbd5e0; }
        .sidebar { background-color: #2d3748; padding: 1rem; height: 100vh; }
        .main-content { padding: 2rem; }
        .card { background-color: #2d3748; padding: 1.5rem; border-radius: 0.5rem; }
        .text-teal-400 { color: #4fd1c5; }
        .text-gray-300 { color: #cbd5e0; }
        .border-teal-400 { border-color: #4fd1c5; }
        .border-gray-700 { border-color: #4a5568; }
        .bg-gray-700 { background-color: #4a5568; }
        .nav-link:hover { background-color: #4a5568; }
        .status-connected { color: #10b981; }
        .status-not-connected { color: #f59e0b; }
    </style>
</head>
<body class="flex h-screen bg-gray-900 text-gray-300 font-sans">
    <aside class="sidebar w-64">
        <div class="p-4 mb-4 border-b border-gray-700">
            <h2 class="text-xl font-bold text-teal-400">Marketing Agent</h2>
            <p class="text-sm text-gray-400">Welcome, {{ current_user.username }}!</p>
        </div>
        <nav>
            <ul>
                <li><a href="/" class="nav-link block py-2 px-4 rounded transition duration-200">Dashboard</a></li>
                <li><a href="/campaigns" class="nav-link block py-2 px-4 rounded transition duration-200">Campaigns</a></li>
                <li><a href="/analytics" class="nav-link block py-2 px-4 rounded transition duration-200">Analytics</a></li>
                <li><a href="/integrations" class="nav-link block py-2 px-4 rounded transition duration-200">Integrations</a></li>
            </ul>
        </nav>
        <div class="absolute bottom-4 px-4">
            <a href="/logout" class="block py-2 px-4 rounded bg-red-600 hover:bg-red-700 text-white text-center transition duration-200">Logout</a>
        </div>
    </aside>
    <main class="main-content flex-1 overflow-y-auto">
        <h1 class="text-3xl font-bold mb-6 text-teal-400">Integrations</h1>
        <div class="card p-6 mb-6">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-2xl font-bold">Google Ads</h2>
                <span class="text-lg font-semibold {{ 'status-connected' if google_ads_connected else 'status-not-connected' }}">
                    {{ 'Connected' if google_ads_connected else 'Not Connected' }}
                </span>
            </div>
            {% if not google_ads_connected %}
                {% if auth_url %}
                    <a href="{{ auth_url }}" class="px-4 py-2 bg-teal-600 hover:bg-teal-700 rounded transition duration-200 inline-block">
                        Connect Google Ads
                    </a>
                {% elif not (client_id and client_secret and developer_token and google_ads_customer_id) %}
                    <p class="text-yellow-500">Please set GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_DEVELOPER_TOKEN, and GOOGLE_ADS_CUSTOMER_ID in your .env file to enable connection.</p>
                {% endif %}
            {% else %}
                <p>You are connected to Google Ads.</p>
                <form method="post" action="/api/google-ads/list-campaigns" class="mt-4">
                    <button type="submit" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition duration-200">List Google Ads Campaigns</button>
                </form>
            {% endif %}
        </div>
    </main>
</body>
</html>
"""

if __name__ == '__main__':
    init_db()
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE username = ?", ('admin',)).fetchone()
    if not user:
        User.create('admin', 'admin123')
        print("Admin user created.")
    conn.close()
    app.run(debug=True, port=5000)
