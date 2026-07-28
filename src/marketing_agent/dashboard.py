from datetime import datetime
from .governance import audit_tracer, budget_manager
from .db import get_conn, init_db

class Dashboard:
    def __init__(self):
        init_db()

    def get_overview(self):
        overview = {
            "last_updated": datetime.now().isoformat(),
            "campaigns": self._get_campaign_summary(),
            "audit_log_count": len(audit_tracer.trace_log),
            "budget_remaining": budget_manager.get_remaining_budget()
        }
        return overview

    def _get_campaign_summary(self):
        campaign_summary = {
            "total_campaigns": 0,
            "planned": 0,
            "executing": 0,
            "completed": 0,
            "total_budget_allocated": 0
        }
        conn = get_conn()
        try:
            rows = conn.execute("SELECT status, budget FROM campaigns").fetchall()
            campaign_summary["total_campaigns"] = len(rows)
            for r in rows:
                campaign_summary["total_budget_allocated"] += r['budget'] or 0
                status = r['status']
                if status == 'planned':
                    campaign_summary["planned"] += 1
                elif status == 'executing':
                    campaign_summary["executing"] += 1
                elif status == 'completed':
                    campaign_summary["completed"] += 1
        except Exception as e:
            print(f"Error loading campaign data for dashboard: {e}")
        finally:
            conn.close()
        return campaign_summary

dashboard = Dashboard()