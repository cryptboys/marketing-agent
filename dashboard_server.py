import sys, os
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
    <title>Hermes AI Marketing Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Tailwind CSS custom classes for dark mode */
        body { background: #0f0f0f; color: #e0e0e0; transition: background-color 0.3s, color 0.3s; }
        .sidebar { background: #1a1a1a; border-right: 1px solid #2a2a2a; transition: background-color 0.3s; }
        .card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; transition: background-color 0.3s; }
        .active-tab { border-left: 4px solid #2dd4bf; background: #262626; }
        .text-teal-400 { color: #2dd4bf; }
        .bg-gray-800 { background: #1f2937; }
        .text-green-500 { color: #4ade80; }
        .text-blue-400 { color: #60a5fa; }
        .text-yellow-400 { color: #fbbf24; }
        .text-gray-400 { color: #9ca3af; }
        .text-gray-500 { color: #6b7280; }
        .border-gray-700 { border-color: #374151; }
        .rounded-xl { border-radius: 0.75rem; }
        .bg-gray-900 { background: #111827; }
    </style>
</head>
<body class="flex h-screen">
    <!-- Sidebar -->
    <div class="sidebar w-64 p-6 flex flex-col">
        <div class="flex items-center mb-8">
            <svg class="w-8 h-8 mr-3" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 12h4v10h4v-6h4v6h4v-10h4L12 2zm0 20v-6h-4v6z" fill="#2dd4bf"/><path d="M22 12v10h-4v-6h-4v6H6v-10H2l10-10 10 10z" fill="#e0e0e0"/></svg>
            <h2 class="text-xl font-bold text-teal-400">Hermes AI</h2>
        </div>
        <nav class="space-y-4 text-gray-400 flex-1">
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Home</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Analytics</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Campaigns</div>
            <div class="active-tab p-2 text-white cursor-pointer">Hermes AI</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Security</div>
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800">Reports</div>
        </nav>
        <div class="mt-auto pt-4">
            <div class="p-2 rounded cursor-pointer hover:bg-gray-800 flex items-center"><svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.345 15.848a1.002 1.002 0 00-.366.753 1.002 1.002 0 00.366.753l3.253 2.354a1.002 1.002 0 001.345-.366l1.117-1.924a1.002 1.002 0 00-.366-1.345L14 12.733V3.5a1.002 1.002 0 00-1-1H7a1.002 1.002 0 00-1 1v9.233l-2.707 2.354a1.002 1.002 0 00-.366 1.345l3.253 2.354zM13.754 12.021l-2.707 2.354a1.002 1.002 0 01-1.345-.366L9.246 11.677a1.002 1.002 0 01.366-.753L12.308 9H7.002a1 1 0 00-1 1v5.733l3.449 2.5a1.002 1.002 0 001.345-.366l2.707-2.354a1.002 1.002 0 00.366-.753V12.021zM17 12v3.733l-2.707-2.354a1.002 1.002 0 00-1.345.366l-3.253 2.354a1.002 1.002 0 00.366 1.345l4.557 3.329a1.002 1.002 0 001.345-.366l3.253-2.354a1.002 1.002 0 00.366-1.345L17 15.733V12a1 1 0 00-1-1z"/></svg>Settings</div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 p-8 overflow-y-auto">
        <header class="flex justify-between items-center mb-8">
            <div class="flex items-center">
                <h1 class="text-2xl font-semibold">Welcome back, Sarah!</h1>
                <p class="text-gray-500 ml-4">Hermes AI Marketing Agent</p>
            </div>
            <div class="bg-gray-800 p-2 rounded flex items-center">Nov 1 - Nov 30, 2023 <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V6a2 2 0 012-2h6a2 2 0 012 2v1m-6 4h8m-8 4h8m-8 4h8"/></svg></div>
        </header>

        <!-- Main Content Area -->
        <div id="main-content-area">
            <!-- Placeholder for dynamic content based on sidebar selection -->
            <div class="grid grid-cols-4 gap-4 mb-8">
                <div class="card p-6 rounded-xl">
                    <h3 class="mb-2">Total Campaigns</h3>
                    <p class="text-3xl font-bold text-blue-400" id="total_campaigns">-</p>
                </div>
                <div class="card p-6 rounded-xl">
                    <h3 class="mb-2">Remaining Budget</h3>
                    <p class="text-3xl font-bold text-green-500" id="budget">$</p>
                </div>
                <div class="card p-6 rounded-xl">
                    <h3 class="mb-2">Audit Events</h3>
                    <p class="text-3xl font-bold text-yellow-400" id="audit_count">-</p>
                </div>
                <div class="card p-6 rounded-xl">
                    <h3 class="mb-2">Budget Allocated</h3>
                    <p class="text-3xl font-bold" id="budget_allocated">$</p>
                </div>
            </div>

            <div class="grid grid-cols-3 gap-8">
                <div class="col-span-2 card p-6 rounded-xl">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg">Performance Over Time</h3>
                        <div class="bg-gray-800 p-2 rounded flex items-center">Nov 1 - Nov 30, 2023 <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V6a2 2 0 012-2h6a2 2 0 012 2v1m-6 4h8m-8 4h8m-8 4h8"/></svg></div>
                    </div>
                    <canvas id="performanceChart"></canvas>
                </div>
                <div class="card p-6 rounded-xl">
                    <h3 class="mb-4">Hermes AI Agent Status</h3>
                    <div class="flex items-center gap-2 mb-4"><div class="w-3 h-3 rounded-full bg-green-500"></div> <span id="agent_status">ACTIVE & OPTIMIZING</span></div>
                    <p class="text-sm text-gray-500 mb-4">Current Focus: <span id="agent_focus">Q4 Holiday Ads</span></p>
                    <h4 class="text-md font-semibold mb-2">Recent Actions</h4>
                    <div id="recent-actions" class="text-sm space-y-2"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Chart Configuration
        const ctx = document.getElementById('performanceChart');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Nov 1', 'Nov 8', 'Nov 15', 'Nov 22', 'Nov 30'],
                datasets: [
                    { label: 'Impressions', data: [120, 150, 170, 200, 240], borderColor: '#60a5fa', fill: false },
                    { label: 'Clicks', data: [80, 90, 110, 130, 150], borderColor: '#2dd4bf', fill: false },
                    { label: 'Conversions', data: [5, 7, 9, 11, 13], borderColor: '#4ade80', fill: false } 
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: '#374151' } },
                    x: { grid: { color: '#374151' } }
                },
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { enabled: true }
                }
            }
        });
        
        // Populate Data
        function updateDashboard() {
            fetch('/api/dashboard').then(r => r.json()).then(d => {
                document.getElementById('total_campaigns').textContent = d.campaigns.total_campaigns;
                document.getElementById('budget').textContent = '$' + d.budget_remaining;
                document.getElementById('audit_count').textContent = d.audit_log_count;
                document.getElementById('budget_allocated').textContent = '$' + d.campaigns.total_budget_allocated;
                document.getElementById('agent_status').textContent = 'ACTIVE & OPTIMIZING'; // Static for now
                document.getElementById('agent_focus').textContent = 'Q4 Holiday Ads'; // Static for now
            });
            fetch('/api/campaigns').then(r => r.json()).then(campaigns => {
                const tbody = document.getElementById('campaigns_body');
                tbody.innerHTML = '';
                Object.entries(campaigns).forEach(([id, c]) => {
                    tbody.innerHTML += `<tr>
                        <td class="label">${id}</td>
                        <td>${c.name}</td>
                        <td><span class="status ${c.status}">${c.status}</span></td>
                        <td>$${c.budget}</td>
                        <td>${c.target_audience}</td>
                    </tr>`;
                });
            });
        }
        updateDashboard();
        setInterval(updateDashboard, 30000); // Refresh every 30 seconds
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
    app.run(port=5000, debug=False)
