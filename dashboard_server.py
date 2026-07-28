import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from flask import Flask, jsonify, render_template_string
from marketing_agent.dashboard import dashboard
from marketing_agent.campaign_manager import campaign_manager

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Agent Dashboard</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:#0f0f0f; color:#e0e0e0; padding:40px; }
        h1 { font-size:2rem; margin-bottom:10px; color:#fff; }
        .subtitle { color:#888; margin-bottom:30px; }
        .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; margin-bottom:30px; }
        .card { background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:20px; }
        .card h3 { color:#aaa; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; }
        .card .value { font-size:2rem; font-weight:700; color:#fff; }
        .card .value.green { color:#4ade80; }
        .card .value.blue { color:#60a5fa; }
        .card .value.yellow { color:#fbbf24; }
        table { width:100%; border-collapse:collapse; margin-top:10px; }
        th, td { text-align:left; padding:10px 12px; border-bottom:1px solid #2a2a2a; }
        th { color:#888; font-size:0.8rem; text-transform:uppercase; }
        .status { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.8rem; }
        .status.planned { background:#1e3a5f; color:#60a5fa; }
        .status.executing { background:#1e3a1f; color:#4ade80; }
        .label { color:#888; font-size:0.9rem; }
        .refresh { display:inline-block; padding:8px 16px; background:#2563eb; color:#fff; border:none; border-radius:8px; cursor:pointer; font-size:0.9rem; margin-bottom:20px; }
        .refresh:hover { background:#1d4ed8; }
    </style>
</head>
<body>
    <h1>Marketing Agent Dashboard</h1>
    <p class="subtitle">Real-time overview of campaigns, budget, and audit activity</p>
    <button class="refresh" onclick="location.reload()">Refresh</button>
    
    <div class="grid" id="stats">
        <div class="card"><h3>Total Campaigns</h3><div class="value blue" id="total_campaigns">-</div></div>
        <div class="card"><h3>Remaining Budget</h3><div class="value green" id="budget">-</div></div>
        <div class="card"><h3>Audit Events</h3><div class="value yellow" id="audit_count">-</div></div>
        <div class="card"><h3>Budget Allocated</h3><div class="value" id="budget_allocated">-</div></div>
    </div>

    <div class="card">
        <h3>Campaigns</h3>
        <table>
            <thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Budget</th><th>Audience</th></tr></thead>
            <tbody id="campaigns_body"></tbody>
        </table>
    </div>

    <script>
        fetch('/api/dashboard').then(r=>r.json()).then(d=>{
            document.getElementById('total_campaigns').textContent = d.campaigns.total_campaigns;
            document.getElementById('budget').textContent = '$' + d.budget_remaining;
            document.getElementById('audit_count').textContent = d.audit_log_count;
            document.getElementById('budget_allocated').textContent = '$' + d.campaigns.total_budget_allocated;
        });
        fetch('/api/campaigns').then(r=>r.json()).then(campaigns=>{
            const tbody = document.getElementById('campaigns_body');
            tbody.innerHTML = '';
            Object.entries(campaigns).forEach(([id, c]) => {
                tbody.innerHTML += '<tr><td class="label">' + id + '</td><td>' + c.name + '</td><td><span class="status ' + c.status + '">' + c.status + '</span></td><td>$' + c.budget + '</td><td>' + c.target_audience + '</td></tr>';
            });
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/dashboard')
def get_dashboard():
    return jsonify(dashboard.get_overview())

@app.route('/api/campaigns')
def get_campaigns():
    return jsonify(campaign_manager.campaigns)

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(port=5000, debug=False)
