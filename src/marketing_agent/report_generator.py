import os
from datetime import datetime
from marketing_agent.db import get_conn

class ReportGenerator:
    def _get_campaigns(self):
        conn = get_conn()
        rows = conn.execute("SELECT name, objective, target_audience, budget, status FROM campaigns ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _get_audit(self):
        conn = get_conn()
        rows = conn.execute("SELECT action, timestamp FROM audit_logs ORDER BY id DESC LIMIT 50").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def generate_html(self):
        campaigns = self._get_campaigns()
        audit = self._get_audit()
        total_budget = sum(c['budget'] for c in campaigns) if campaigns else 0
        planned = sum(1 for c in campaigns if c['status'] == 'planned')
        executing = sum(1 for c in campaigns if c['status'] == 'executing')

        rows = ''
        for c in campaigns:
            rows += f'''<tr><td>{c['name']}</td><td>{c['objective']}</td><td><span class="status-{c['status']}">{c['status']}</span></td><td>${c['budget']}</td></tr>
'''

        audit_rows = ''
        for a in audit[:20]:
            audit_rows += f'<tr><td>{a["action"]}</td><td>{a["timestamp"][:19]}</td></tr>\n'

        html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Marketing Agent Report - {datetime.now().strftime('%Y-%m-%d')}</title>
<style>
body {{ font-family: Arial, sans-serif; background: #111; color: #eee; padding: 40px; }}
h1 {{ color: #2dd4bf; border-bottom: 2px solid #2dd4bf; padding-bottom: 10px; }}
.summary {{ display: flex; gap: 20px; margin: 20px 0; }}
.card {{ background: #1a1a1a; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
.card h3 {{ color: #9ca3af; margin: 0 0 5px; }}
.card p {{ font-size: 24px; font-weight: bold; margin: 0; }}
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
th {{ text-align: left; color: #9ca3af; text-transform: uppercase; font-size: 12px; padding: 8px; border-bottom: 1px solid #333; }}
td {{ padding: 8px; border-bottom: 1px solid #222; }}
.status-planned {{ color: #3b82f6; }}
.status-executing {{ color: #10b981; }}
.footer {{ margin-top: 30px; color: #555; font-size: 12px; text-align: center; }}
</style>
</head>
<body>
<h1>Marketing Agent Performance Report</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

<div class="summary">
<div class="card"><h3>Total Campaigns</h3><p style="color:#3b82f6">{len(campaigns)}</p></div>
<div class="card"><h3>Total Budget</h3><p style="color:#10b981">${total_budget}</p></div>
<div class="card"><h3>Planned</h3><p style="color:#f59e0b">{planned}</p></div>
<div class="card"><h3>Executing</h3><p style="color:#ef4444">{executing}</p></div>
</div>

<h2>Campaign Details</h2>
<table>
<thead><tr><th>Name</th><th>Objective</th><th>Status</th><th>Budget</th></tr></thead>
<tbody>{rows}</tbody>
</table>

<h2>Recent Audit Actions</h2>
<table>
<thead><tr><th>Action</th><th>Timestamp</th></tr></thead>
<tbody>{audit_rows}</tbody>
</table>

<div class="footer">Hermes AI Marketing Agent &mdash; CONFIDENTIAL</div>
</body>
</html>'''
        return html

    def save_html(self, output_path=None):
        html = self.generate_html()
        if not output_path:
            output_dir = 'reports'
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path

report_generator = ReportGenerator()
