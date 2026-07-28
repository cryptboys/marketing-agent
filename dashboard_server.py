import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from flask import Flask, jsonify, render_template_string
from marketing_agent.dashboard import dashboard
from marketing_agent.campaign_manager import campaign_manager
from marketing_agent.governance import audit_tracer

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes AI Marketing Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: #0f0f0f; color: #e0e0e0; }
        .sidebar { background: #1a1a1a; border-right: 1px solid #2a2a2a; }
        .card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; }
        .active-tab { border-left: 4px solid #2dd4bf; background: #262626; }
        .bg-gray-800 { background: #1f2937; }
        .bg-gray-900 { background: #111827; }
    </style>
</head>
<body class="flex h-screen">
    <!-- Sidebar -->
    <div class="sidebar w-64 p-6 flex flex-col">
        <div class="flex items-center mb-8">
            <h2 class="text-xl font-bold text-teal-400">Hermes AI</h2>
        </div>
        <nav class="space-y-4 text-gray-400 flex-1">
            <div class="active-tab p-2 text-white cursor-pointer">Dashboard</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Campaigns</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Analytics</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Content</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Security</div>
        </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-1 p-8 overflow-y-auto">
        <header class="flex justify-between items-center mb-8">
            <h1 class="text-2xl font-semibold">Marketing Agent Dashboard</h1>
            <span class="text-gray-500 text-sm" id="last-updated">Loading...</span>
        </header>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-4 gap-4 mb-8">
            <div class="card p-6 rounded-xl">
                <h3 class="text-gray-400 text-sm uppercase mb-2">Total Campaigns</h3>
                <p class="text-3xl font-bold text-blue-400" id="total_campaigns">-</p>
            </div>
            <div class="card p-6 rounded-xl">
                <h3 class="text-gray-400 text-sm uppercase mb-2">Remaining Budget</h3>
                <p class="text-3xl font-bold text-green-500" id="budget">$-</p>
            </div>
            <div class="card p-6 rounded-xl">
                <h3 class="text-gray-400 text-sm uppercase mb-2">Audit Events</h3>
                <p class="text-3xl font-bold text-yellow-400" id="audit_count">-</p>
            </div>
            <div class="card p-6 rounded-xl">
                <h3 class="text-gray-400 text-sm uppercase mb-2">Budget Allocated</h3>
                <p class="text-3xl font-bold" id="budget_allocated">$-</p>
            </div>
        </div>

        <!-- Two Column Layout -->
        <div class="grid grid-cols-3 gap-8">
            <!-- Campaign Table -->
            <div class="col-span-2 card p-6 rounded-xl">
                <h3 class="text-lg mb-4">Active Campaigns</h3>
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-gray-500 uppercase text-xs">
                            <th class="text-left pb-3">ID</th>
                            <th class="text-left pb-3">Name</th>
                            <th class="text-left pb-3">Status</th>
                            <th class="text-left pb-3">Budget</th>
                            <th class="text-left pb-3">Audience</th>
                        </tr>
                    </thead>
                    <tbody id="campaigns_body"></tbody>
                </table>
            </div>

            <!-- Right Panel -->
            <div class="space-y-6">
                <!-- Budget Panel -->
                <div class="card p-6 rounded-xl">
                    <h3 class="mb-4">Security & Budget Panel</h3>
                    <div class="mb-4">
                        <div class="flex justify-between text-sm mb-1">
                            <span class="text-gray-400">Monthly Budget</span>
                            <span id="budget-pct" class="text-gray-400">0% Used</span>
                        </div>
                        <div class="w-full bg-gray-800 rounded-full h-2">
                            <div id="budget-bar" class="bg-teal-500 h-2 rounded-full" style="width: 0%"></div>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 mb-4">
                        <div class="w-3 h-3 rounded-full bg-green-500"></div>
                        <span class="text-green-400 text-sm font-semibold">ACTIVE & OPTIMIZING</span>
                    </div>
                    <p class="text-xs text-gray-500 mb-2">Focus: <span id="agent_focus">Q4 Campaigns</span></p>
                </div>

                <!-- Audit Log -->
                <div class="card p-6 rounded-xl">
                    <h3 class="mb-3">Recent Actions</h3>
                    <div id="audit-actions" class="text-sm space-y-2">
                        <p class="text-gray-500">No recent audit events.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateDashboard() {
            // Fetch Overview
            fetch('/api/dashboard')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('total_campaigns').textContent = d.campaigns.total_campaigns;
                    document.getElementById('budget').textContent = '$' + d.budget_remaining;
                    document.getElementById('audit_count').textContent = d.audit_log_count;
                    document.getElementById('budget_allocated').textContent = '$' + d.campaigns.total_budget_allocated;
                    document.getElementById('last-updated').textContent = 'Last updated: ' + d.last_updated;
                    
                    // Progress bar
                    const allocPct = d.campaigns.total_budget_allocated / (d.campaigns.total_budget_allocated + d.budget_remaining) * 100 || 0;
                    document.getElementById('budget-bar').style.width = allocPct.toFixed(0) + '%';
                    document.getElementById('budget-pct').textContent = allocPct.toFixed(0) + '% Used';
                });

            // Fetch Campaigns
            fetch('/api/campaigns')
                .then(r => r.json())
                .then(campaigns => {
                    const tbody = document.getElementById('campaigns_body');
                    tbody.innerHTML = '';
                    Object.entries(campaigns).forEach(([id, c]) => {
                        const statusColor = c.status === 'executing' ? 'bg-green-900 text-green-300' : 'bg-blue-900 text-blue-300';
                        tbody.innerHTML += '<tr class="border-b border-gray-800">' +
                            '<td class="py-3 text-gray-500">' + id + '</td>' +
                            '<td class="py-3 font-medium">' + c.name + '</td>' +
                            '<td class="py-3"><span class="px-2 py-1 rounded-full text-xs ' + statusColor + '">' + c.status + '</span></td>' +
                            '<td class="py-3">$' + c.budget + '</td>' +
                            '<td class="py-3 text-gray-400">' + c.target_audience + '</td>' +
                            '</tr>';
                    });
                });

            // Fetch Audit Log
            fetch('/api/audit')
                .then(r => r.json())
                .then(logs => {
                    const auditDiv = document.getElementById('audit-actions');
                    if (logs && logs.length > 0) {
                        auditDiv.innerHTML = logs.slice(0, 5).map(l =>
                            '<div class="p-2 bg-gray-900 rounded text-xs text-gray-400">' +
                            l.action + ' <span class="text-gray-600">' + new Date(l.timestamp).toLocaleTimeString() + '</span></div>'
                        ).join('');
                    }
                });
        }

        // Initial load + auto-refresh every 15s
        updateDashboard();
        setInterval(updateDashboard, 15000);
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

@app.route('/api/audit')
def get_audit():
    logs = [{'action': t['action'], 'timestamp': t['timestamp']} for t in audit_tracer.trace_log]
    return jsonify(logs)

if __name__ == '__main__':
    app.run(port=5000, debug=False)
